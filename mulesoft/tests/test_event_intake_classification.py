from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from mock_runtime import build_default_api
from mock_runtime.intake import content_hash


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "integration" / "events" / "fixtures"
SCENARIO = json.loads((FIXTURE_ROOT / "scenario.json").read_text())
PRESERVED_RESULTS = {
    "ACCEPTED",
    "ACCEPTED_LATE",
    "ACCEPTED_OUT_OF_ORDER",
    "CONFLICT_REVIEW",
}
REJECTED_STATUS = {
    "REJECTED_SCHEMA": 422,
    "REJECTED_HASH": 422,
    "REJECTED_IDEMPOTENCY_CONFLICT": 409,
}


def headers(event):
    return {
        "X-Tenant-Id": event.get("hfstenantid", "demo-mauritius"),
        "X-Correlation-Id": event.get(
            "hfscorrelationid",
            "10000000-0000-4000-8000-000000000001",
        ),
        "X-Idempotency-Key": event.get(
            "hfsidempotencykey",
            "missing-event-key",
        ),
        "X-Callback-Url": "https://callbacks.example.test/hfs/completions",
    }


class EventIntakeClassificationTest(unittest.TestCase):
    def test_all_versioned_fixtures_use_runtime_intake_behavior(self):
        api = build_default_api(
            maximum_lateness_seconds=SCENARIO["maximumLatenessSeconds"]
        )

        for case in SCENARIO["events"]:
            with self.subTest(case=case["file"]):
                event = json.loads((FIXTURE_ROOT / case["file"]).read_text())
                response = api.request(
                    "POST",
                    "/v1/events",
                    headers(event),
                    deepcopy(event),
                )
                attempt = api.source_adapter.attempts[-1]

                self.assertEqual(case["expected"], attempt["intakeResult"])
                if case["expected"] in PRESERVED_RESULTS:
                    self.assertEqual(202, response.status)
                    self.assertEqual(
                        case["expected"],
                        response.body["intakeResult"],
                    )
                    self.assertTrue(attempt["preserved"])
                elif case["expected"] == "DUPLICATE":
                    self.assertEqual(202, response.status)
                    self.assertEqual("DUPLICATE", response.body["intakeResult"])
                    self.assertTrue(response.body["replayed"])
                    self.assertFalse(attempt["preserved"])
                else:
                    self.assertEqual(
                        REJECTED_STATUS[case["expected"]],
                        response.status,
                    )
                    self.assertEqual(
                        case["expected"],
                        response.body["errors"][0]["details"],
                    )
                    self.assertFalse(
                        response.body["errors"][0]["retryable"]
                    )
                    self.assertFalse(attempt["preserved"])

        self.assertEqual(14, len(api.source_adapter.attempts))
        self.assertEqual(10, len(api.source_adapter.events))
        ingestion_callbacks = [
            item
            for item in api.callback_transport.received
            if item["payload"]["operation"] == "INGEST_EVENT"
        ]
        self.assertEqual(10, len(ingestion_callbacks))
        self.assertEqual(
            sorted(
                case["expected"]
                for case in SCENARIO["events"]
                if case["expected"] in PRESERVED_RESULTS
            ),
            sorted(
                item["payload"]["result"]["intakeResult"]
                for item in ingestion_callbacks
            ),
        )

    def test_source_retry_uses_data_hash_not_transport_metadata(self):
        api = build_default_api()
        original = json.loads(
            (FIXTURE_ROOT / "events/05-agreement.json").read_text()
        )
        retry = json.loads(
            (FIXTURE_ROOT / "events/08-duplicate-agreement.json").read_text()
        )

        first = api.request(
            "POST",
            "/v1/events",
            headers(original),
            original,
        )
        duplicate = api.request(
            "POST",
            "/v1/events",
            headers(retry),
            retry,
        )

        self.assertEqual("ACCEPTED", first.body["intakeResult"])
        self.assertEqual("DUPLICATE", duplicate.body["intakeResult"])
        self.assertNotEqual(first.body["eventId"], duplicate.body["eventId"])
        self.assertEqual(1, len(api.source_adapter.events))

    def test_conflicting_assertions_coexist_without_overwrite(self):
        api = build_default_api()
        original = json.loads(
            (FIXTURE_ROOT / "events/05-agreement.json").read_text()
        )
        conflict = json.loads(
            (FIXTURE_ROOT / "events/11-conflicting-agreement.json").read_text()
        )

        api.request("POST", "/v1/events", headers(original), original)
        response = api.request(
            "POST",
            "/v1/events",
            headers(conflict),
            conflict,
        )

        self.assertEqual("CONFLICT_REVIEW", response.body["intakeResult"])
        self.assertIn(
            (original["hfstenantid"], original["source"], original["id"]),
            api.source_adapter.events,
        )
        self.assertIn(
            (conflict["hfstenantid"], conflict["source"], conflict["id"]),
            api.source_adapter.events,
        )
        self.assertEqual(2, len(api.source_adapter.events))

    def test_source_identity_and_idempotency_are_tenant_scoped(self):
        api = build_default_api()
        original = json.loads(
            (FIXTURE_ROOT / "events/05-agreement.json").read_text()
        )
        other_tenant = deepcopy(original)
        other_tenant["hfstenantid"] = "demo-secondary"
        other_source = deepcopy(original)
        other_source["source"] = "urn:hfs:source:contracts-secondary"

        responses = [
            api.request("POST", "/v1/events", headers(event), event)
            for event in (original, other_tenant, other_source)
        ]

        self.assertEqual(
            ["ACCEPTED", "ACCEPTED", "ACCEPTED"],
            [response.body["intakeResult"] for response in responses],
        )
        self.assertEqual(3, len(api.source_adapter.events))

    def test_event_identity_cannot_overwrite_preserved_source_data(self):
        api = build_default_api()
        original = json.loads(
            (FIXTURE_ROOT / "events/05-agreement.json").read_text()
        )
        changed = deepcopy(original)
        changed["hfsidempotencykey"] = "contracts-agreement-001-reused-id"
        changed["data"]["attributes"]["status"] = "TERMINATED"
        changed["hfscontenthash"] = content_hash(changed["data"])

        accepted = api.request(
            "POST",
            "/v1/events",
            headers(original),
            original,
        )
        rejected = api.request(
            "POST",
            "/v1/events",
            headers(changed),
            changed,
        )

        self.assertEqual("ACCEPTED", accepted.body["intakeResult"])
        self.assertEqual(409, rejected.status)
        self.assertEqual(
            "REJECTED_IDEMPOTENCY_CONFLICT",
            rejected.body["errors"][0]["details"],
        )
        self.assertEqual("id", rejected.body["errors"][0]["fieldName"])
        self.assertEqual(1, len(api.source_adapter.events))


if __name__ == "__main__":
    unittest.main()
