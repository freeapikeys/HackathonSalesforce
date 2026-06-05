#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = ROOT / "integration" / "events"
SCHEMA_PATH = EVENTS_DIR / "schemas" / "event-envelope-v1.schema.json"
SCENARIO_PATH = EVENTS_DIR / "fixtures" / "scenario.json"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def content_hash(data: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_error_text(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    return f"{path}: {error.message}" if path else error.message


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
    idempotency: dict[tuple[str, str, str], str] = {}
    source_watermarks: dict[tuple[str, str], int] = {}
    assertions: dict[tuple[str, str, str], str] = {}
    results: list[dict[str, str]] = []
    record_types: set[str] = set()
    maximum_lateness = scenario["maximumLatenessSeconds"]

    for case in scenario["events"]:
        path = fixture_root / case["file"]
        event = json.loads(path.read_text())
        errors = sorted(
            validator.iter_errors(event),
            key=lambda error: list(error.absolute_path),
        )

        if errors:
            disposition = "REJECTED_SCHEMA"
            detail = " | ".join(schema_error_text(error) for error in errors)
        elif event["hfscontenthash"] != content_hash(event["data"]):
            disposition = "REJECTED_HASH"
            detail = "Declared content hash does not match canonical data."
        else:
            record_types.add(event["data"]["recordtype"])
            idempotency_scope = (
                event["hfstenantid"],
                event["source"],
                event["hfsidempotencykey"],
            )
            previous_hash = idempotency.get(idempotency_scope)

            if previous_hash == event["hfscontenthash"]:
                disposition = "DUPLICATE"
                detail = "Exact replay in the same tenant and source scope."
            elif previous_hash is not None:
                disposition = "REJECTED_IDEMPOTENCY_CONFLICT"
                detail = "Idempotency key was reused for different content."
            else:
                idempotency[idempotency_scope] = event["hfscontenthash"]
                effective_at = event["data"]["effectiveat"]
                has_conflict = False

                for assertion in event["data"].get("assertions", []):
                    assertion_scope = (
                        event["hfstenantid"],
                        assertion["conflictkey"],
                        effective_at,
                    )
                    assertion_value = canonical_json(assertion["value"])
                    previous_value = assertions.get(assertion_scope)
                    if (
                        previous_value is not None
                        and previous_value != assertion_value
                    ):
                        has_conflict = True
                    else:
                        assertions[assertion_scope] = assertion_value

                source_scope = (event["hfstenantid"], event["source"])
                sequence = event["hfssourcesequence"]
                watermark = source_watermarks.get(source_scope)
                out_of_order = watermark is not None and sequence < watermark
                source_watermarks[source_scope] = max(watermark or 0, sequence)

                late_by = (
                    parse_datetime(event["hfsobservedat"])
                    - parse_datetime(event["time"])
                ).total_seconds()

                if has_conflict:
                    disposition = "CONFLICT_REVIEW"
                    detail = "Contradictory assertion preserved for review."
                elif late_by > maximum_lateness:
                    disposition = "ACCEPTED_LATE"
                    detail = f"Event arrived {int(late_by)} seconds late."
                elif out_of_order:
                    disposition = "ACCEPTED_OUT_OF_ORDER"
                    detail = "Source sequence is behind the current watermark."
                else:
                    disposition = "ACCEPTED"
                    detail = "Valid new event."

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
