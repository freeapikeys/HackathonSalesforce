#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MULESOFT_RUNTIME = ROOT / "mulesoft"
if str(MULESOFT_RUNTIME) not in sys.path:
    sys.path.insert(0, str(MULESOFT_RUNTIME))

from mock_runtime import RetryPolicy, build_default_api  # noqa: E402


FIXTURE_ROOT = ROOT / "integration" / "events" / "fixtures"
EVENTS = FIXTURE_ROOT / "events"
SCENARIO_PATH = FIXTURE_ROOT / "scenario.json"
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
CORRELATION = "10000000-0000-4000-8000-000000000099"


class VerificationFailure(RuntimeError):
    pass


class CommandRunner:
    def run_json(self, command: list[str]) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise VerificationFailure(
                f"Command returned invalid JSON: {' '.join(command[:4])}"
            ) from error
        if completed.returncode != 0 or payload.get("status") not in (None, 0):
            message = payload.get("message") or "command failed"
            raise VerificationFailure(
                f"{' '.join(command[:4])} failed: {message}"
            )
        return payload


def event_headers(event: dict[str, Any]) -> dict[str, str]:
    return {
        "X-Tenant-Id": event.get("hfstenantid", "demo-mauritius"),
        "X-Correlation-Id": event.get("hfscorrelationid", CORRELATION),
        "X-Idempotency-Key": event.get("hfsidempotencykey", "missing-key"),
        "X-Callback-Url": "https://callbacks.example.test/hfs/completions",
    }


def replay_request(
    original_attempt_id: str,
    event: dict[str, Any],
    key: str = "source-intake-replay-001",
) -> tuple[dict[str, str], dict[str, Any]]:
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


def load_event(path: str) -> dict[str, Any]:
    return json.loads((FIXTURE_ROOT / path).read_text())


def verify_fixture_runtime() -> dict[str, Any]:
    scenario = json.loads(SCENARIO_PATH.read_text())
    api = build_default_api(
        maximum_lateness_seconds=scenario["maximumLatenessSeconds"]
    )
    result_counts: Counter[str] = Counter()
    status_counts: Counter[int] = Counter()

    for case in scenario["events"]:
        event = load_event(case["file"])
        response = api.request(
            "POST",
            "/v1/events",
            event_headers(event),
            deepcopy(event),
        )
        attempt = api.source_adapter.attempts[-1]
        expected = case["expected"]
        actual = attempt["intakeResult"]
        if actual != expected:
            raise VerificationFailure(
                f"{case['file']}: expected {expected}, received {actual}"
            )
        result_counts[actual] += 1
        status_counts[response.status] += 1

        if expected in PRESERVED_RESULTS:
            if response.status != 202 or not attempt["preserved"]:
                raise VerificationFailure(
                    f"{case['file']}: preserved event was not accepted"
                )
        elif expected == "DUPLICATE":
            if response.status != 202 or not response.body["replayed"]:
                raise VerificationFailure(
                    f"{case['file']}: duplicate replay was not recognized"
                )
        else:
            if response.status != REJECTED_STATUS[expected]:
                raise VerificationFailure(
                    f"{case['file']}: rejection status mismatch"
                )
            if attempt["preserved"]:
                raise VerificationFailure(
                    f"{case['file']}: rejected attempt was preserved"
                )

    preserved_expected = sum(
        1
        for case in scenario["events"]
        if case["expected"] in PRESERVED_RESULTS
    )
    callback_count = sum(
        1
        for item in api.callback_transport.received
        if item["payload"]["operation"] == "INGEST_EVENT"
    )
    if preserved_expected != len(api.source_adapter.events):
        raise VerificationFailure("MuleSoft preserved event count mismatch.")
    if preserved_expected != callback_count:
        raise VerificationFailure("MuleSoft callback count mismatch.")

    return {
        "status": "passed",
        "fixtureCount": len(scenario["events"]),
        "attemptCount": len(api.source_adapter.attempts),
        "preservedCount": len(api.source_adapter.events),
        "callbackCount": callback_count,
        "resultCounts": dict(sorted(result_counts.items())),
        "httpStatusCounts": {
            str(key): value for key, value in sorted(status_counts.items())
        },
    }


def verify_replay_paths() -> dict[str, Any]:
    malformed = json.loads((EVENTS / "09-malformed.json").read_text())
    corrected = deepcopy(malformed)
    corrected["hfssourcerecordid"] = "account-record-002"

    api = build_default_api()
    rejected = api.request(
        "POST",
        "/v1/events",
        event_headers(malformed),
        malformed,
    )
    original = deepcopy(api.source_adapter.attempts[-1])
    headers, body = replay_request(original["attemptId"], corrected)
    replayed = api.request("POST", "/v1/events/replays", headers, body)
    if rejected.status != 422 or original["state"] != "QUARANTINED":
        raise VerificationFailure("Malformed event was not quarantined.")
    if replayed.status != 202 or replayed.body["status"] != "COMPLETED":
        raise VerificationFailure("Corrected replay did not complete.")
    if api.source_adapter.attempts[-1]["originalAttemptId"] != original["attemptId"]:
        raise VerificationFailure("Replay attempt was not linked.")

    exhausted_event = json.loads((EVENTS / "07-issue.json").read_text())
    retry_api = build_default_api(
        source_failures=2,
        retry_policy=RetryPolicy(max_attempts=2),
    )
    exhausted = retry_api.request(
        "POST",
        "/v1/events",
        event_headers(exhausted_event),
        exhausted_event,
    )
    exhausted_attempt = retry_api.source_adapter.attempts[-1]
    headers, body = replay_request(
        exhausted_attempt["attemptId"],
        exhausted_event,
        key="source-intake-replay-exhausted",
    )
    recovered = retry_api.request("POST", "/v1/events/replays", headers, body)
    if exhausted.status != 503 or exhausted_attempt["state"] != "QUARANTINED":
        raise VerificationFailure("Exhausted source-store retry was not quarantined.")
    if recovered.status != 202 or len(retry_api.source_adapter.events) != 1:
        raise VerificationFailure("Exhausted retry replay did not recover.")

    permanent_api = build_default_api()
    original_event = json.loads((EVENTS / "01-person.json").read_text())
    conflict = json.loads((EVENTS / "13-idempotency-conflict.json").read_text())
    permanent_api.request(
        "POST",
        "/v1/events",
        event_headers(original_event),
        original_event,
    )
    permanent_api.request("POST", "/v1/events", event_headers(conflict), conflict)
    permanent_attempt = permanent_api.source_adapter.attempts[-1]
    headers, body = replay_request(
        permanent_attempt["attemptId"],
        conflict,
        key="source-intake-replay-permanent",
    )
    permanent_replay = permanent_api.request(
        "POST",
        "/v1/events/replays",
        headers,
        body,
    )
    if permanent_attempt["state"] != "REJECTED" or permanent_replay.status != 409:
        raise VerificationFailure("Permanent rejection was replayable.")

    return {
        "status": "passed",
        "malformedReplay": replayed.body["status"],
        "exhaustedRetryReplay": recovered.body["status"],
        "permanentReplayStatus": permanent_replay.status,
    }


def verify_salesforce(
    target_org: str | None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    if not target_org:
        return {
            "status": "skipped",
            "reason": "Pass --target-org to run Salesforce check-only tests.",
        }
    payload = (runner or CommandRunner()).run_json(
        [
            "sf",
            "project",
            "deploy",
            "validate",
            "--source-dir",
            "force-app/main/default",
            "--target-org",
            target_org,
            "--test-level",
            "RunLocalTests",
            "--json",
        ]
    )
    result = payload["result"]
    return {
        "status": "passed",
        "checkOnly": result.get("checkOnly"),
        "deployId": result.get("id"),
        "numberTestsCompleted": result.get("numberTestsCompleted"),
        "numberTestErrors": result.get("numberTestErrors"),
    }


def build_report(
    target_org: str | None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    report = {
        "schemaVersion": "1.0.0",
        "status": "passed",
        "fixtureRuntime": verify_fixture_runtime(),
        "replayRuntime": verify_replay_paths(),
        "salesforce": verify_salesforce(target_org, runner=runner),
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-org", help="Salesforce org alias for check-only tests.")
    parser.add_argument("--output", help="Optional JSON report path.")
    args = parser.parse_args()

    try:
        report = build_report(args.target_org)
    except Exception as error:
        report = {
            "schemaVersion": "1.0.0",
            "status": "failed",
            "error": str(error),
        }
        exit_code = 1
    else:
        exit_code = 0

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered)
    print(rendered, end="")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
