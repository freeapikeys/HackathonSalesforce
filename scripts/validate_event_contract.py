#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MULESOFT_RUNTIME = ROOT / "mulesoft"
if str(MULESOFT_RUNTIME) not in sys.path:
    sys.path.insert(0, str(MULESOFT_RUNTIME))

from mock_runtime.intake import (  # noqa: E402
    EventIntakeClassifier,
    content_hash,
)

EVENTS_DIR = ROOT / "integration" / "events"
SCHEMA_PATH = EVENTS_DIR / "schemas" / "event-envelope-v1.schema.json"
SCENARIO_PATH = EVENTS_DIR / "fixtures" / "scenario.json"


def update_fixture_hashes(scenario: dict[str, Any]) -> None:
    fixture_root = SCENARIO_PATH.parent
    for case in scenario["events"]:
        path = fixture_root / case["file"]
        event = json.loads(path.read_text())
        if not case.get("preserveHash"):
            event["hfscontenthash"] = content_hash(event["data"])
        path.write_text(json.dumps(event, indent=2) + "\n")


def classify_scenario(
    scenario: dict[str, Any],
    validator: Draft202012Validator,
) -> list[dict[str, str]]:
    fixture_root = SCENARIO_PATH.parent
    classifier = EventIntakeClassifier(
        maximum_lateness_seconds=scenario["maximumLatenessSeconds"],
        validator=validator,
    )
    results: list[dict[str, str]] = []
    record_types: set[str] = set()

    for case in scenario["events"]:
        path = fixture_root / case["file"]
        event = json.loads(path.read_text())
        decision = classifier.classify(event)
        disposition = decision.result
        detail = decision.detail
        if disposition != "REJECTED_SCHEMA":
            record_types.add(event["data"]["recordtype"])

        assert disposition == case["expected"], (
            f"{case['file']}: expected {case['expected']}, "
            f"received {disposition}: {detail}"
        )
        if expected_error := case.get("expectedError"):
            assert expected_error in detail, (
                f"{case['file']}: expected error text {expected_error!r}, "
                f"received {detail!r}"
            )

        results.append(
            {
                "file": case["file"],
                "result": disposition,
                "detail": detail,
            }
        )

    required_record_types = {
        "Person",
        "Organization",
        "Employee",
        "Supplier",
        "Agreement",
        "SOP",
        "Issue",
    }
    assert required_record_types <= record_types, (
        "Synthetic case is missing record types: "
        + ", ".join(sorted(required_record_types - record_types))
    )

    required_results = {
        "ACCEPTED",
        "DUPLICATE",
        "REJECTED_SCHEMA",
        "ACCEPTED_LATE",
        "CONFLICT_REVIEW",
        "ACCEPTED_OUT_OF_ORDER",
        "REJECTED_HASH",
        "REJECTED_IDEMPOTENCY_CONFLICT",
    }
    actual_results = {result["result"] for result in results}
    assert required_results <= actual_results, (
        "Synthetic case is missing intake results: "
        + ", ".join(sorted(required_results - actual_results))
    )

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update-hashes",
        action="store_true",
        help="Rewrite fixture content hashes from canonical event data.",
    )
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    scenario = json.loads(SCENARIO_PATH.read_text())

    if args.update_hashes:
        update_fixture_hashes(scenario)

    results = classify_scenario(scenario, validator)
    for result in results:
        print(f"{result['result']:<24} {result['file']}")
    print(f"\nEvent contract is valid ({len(results)} deterministic fixtures).")


if __name__ == "__main__":
    main()
