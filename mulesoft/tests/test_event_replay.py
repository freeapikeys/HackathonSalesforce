from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from mock_runtime import RetryPolicy, build_default_api


ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "integration" / "events" / "fixtures" / "events"
CORRELATION = "10000000-0000-4000-8000-000000000099"


def event_headers(event):
    return {
        "X-Tenant-Id": event.get("hfstenantid", "demo-mauritius"),
        "X-Correlation-Id": event.get("hfscorrelationid", CORRELATION),
        "X-Idempotency-Key": event.get("hfsidempotencykey", "missing-key"),
    }


def replay_request(original_attempt_id, event, key="replay-001"):
    body = {
        "contractVersion": "1.0.0",
        "tenantKey": event["hfstenantid"],
        "correlationId": CORRELATION,
        "idempotencyKey": key,
        "purpose": "REPLAY_QUARANTINED_EVENT",
        "originalAttemptId": original_attempt_id,
        "reason": "The source envelope was corrected and reviewed.",
        "event": event,
    }
    headers = {
        "X-Tenant-Id": body["tenantKey"],
        "X-Correlation-Id": body["correlationId"],
        "X-Idempotency-Key": body["idempotencyKey"],
    }
    return headers, body


class EventReplayTest(unittest.TestCase):
    def malformed_and_corrected(self):
        malformed = json.loads((EVENTS / "09-malformed.json").read_text())
        corrected = deepcopy(malformed)
        corrected["hfssourcerecordid"] = "account-record-002"
        return malformed, corrected

    def test_authorized_replay_links_new_attempt_without_mutating_original(self):
        api = build_default_api()
        malformed, corrected = self.malformed_and_corrected()
        rejected = api.request(
            "POST",
            "/v1/events",
            event_headers(malformed),
            malformed,
        )
        original = deepcopy(api.source_adapter.attempts[-1])
        headers, body = replay_request(original["attemptId"], corrected)

        replayed = api.request(
            "POST",
            "/v1/events/replays",
            headers,
            body,
        )

        self.assertEqual(422, rejected.status)
        self.assertEqual("QUARANTINED", original["state"])
        self.assertEqual(202, replayed.status)
        self.assertEqual("COMPLETED", replayed.body["status"])
        linked = api.source_adapter.attempts[-1]
        self.assertEqual(original["attemptId"], linked["originalAttemptId"])
        self.assertEqual("PRESERVED", linked["state"])
        self.assertEqual(
            original,
            api.source_adapter.attempt(original["attemptId"]),
        )

    def test_replay_requires_authorized_purpose(self):
        api = build_default_api()
        malformed, corrected = self.malformed_and_corrected()
        api.request("POST", "/v1/events", event_headers(malformed), malformed)
        original = api.source_adapter.attempts[-1]
        headers, body = replay_request(original["attemptId"], corrected)
        body["purpose"] = "BULK_DATA_FIX"

        denied = api.request("POST", "/v1/events/replays", headers, body)

        self.assertEqual(403, denied.status)
        self.assertEqual("PERMISSION_DENIED", denied.body["errors"][0]["code"])
        self.assertEqual(1, len(api.source_adapter.attempts))

    def test_replay_is_idempotent_and_changed_content_conflicts(self):
        api = build_default_api()
        malformed, corrected = self.malformed_and_corrected()
        api.request("POST", "/v1/events", event_headers(malformed), malformed)
        original = api.source_adapter.attempts[-1]
        headers, body = replay_request(original["attemptId"], corrected)

        first = api.request("POST", "/v1/events/replays", headers, body)
        exact = api.request(
            "POST",
            "/v1/events/replays",
            headers,
            deepcopy(body),
        )
        changed = deepcopy(body)
        changed["reason"] = "Changed after the replay key was used."
        conflict = api.request(
            "POST",
            "/v1/events/replays",
            headers,
            changed,
        )

        self.assertEqual(202, first.status)
        self.assertTrue(exact.body["replayed"])
        self.assertEqual(409, conflict.status)
        self.assertEqual(
            "IDEMPOTENCY_CONFLICT",
            conflict.body["errors"][0]["code"],
        )
        self.assertEqual(2, len(api.source_adapter.attempts))

    def test_exhausted_source_retries_quarantine_then_replay(self):
        event = json.loads((EVENTS / "07-issue.json").read_text())
        api = build_default_api(
            source_failures=2,
            retry_policy=RetryPolicy(max_attempts=2),
        )

        exhausted = api.request(
            "POST",
            "/v1/events",
            event_headers(event),
            event,
        )
        original = api.source_adapter.attempts[-1]
        headers, body = replay_request(original["attemptId"], event)
        recovered = api.request(
            "POST",
            "/v1/events/replays",
            headers,
            body,
        )

        self.assertEqual(503, exhausted.status)
        self.assertTrue(exhausted.body["errors"][0]["retryable"])
        self.assertEqual("QUARANTINED", original["state"])
        self.assertEqual(202, recovered.status)
        self.assertEqual("PRESERVED", api.source_adapter.attempts[-1]["state"])
        self.assertEqual(1, len(api.source_adapter.events))

    def test_permanent_rejection_cannot_be_replayed(self):
        api = build_default_api()
        original = json.loads((EVENTS / "01-person.json").read_text())
        conflict = json.loads(
            (EVENTS / "13-idempotency-conflict.json").read_text()
        )
        api.request("POST", "/v1/events", event_headers(original), original)
        api.request("POST", "/v1/events", event_headers(conflict), conflict)
        rejected = api.source_adapter.attempts[-1]
        headers, body = replay_request(rejected["attemptId"], conflict)

        response = api.request(
            "POST",
            "/v1/events/replays",
            headers,
            body,
        )

        self.assertEqual("REJECTED", rejected["state"])
        self.assertEqual(409, response.status)
        self.assertEqual("INVALID_STATE", response.body["errors"][0]["code"])


if __name__ == "__main__":
    unittest.main()
