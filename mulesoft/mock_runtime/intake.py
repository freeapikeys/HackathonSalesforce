from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
EVENT_SCHEMA_PATH = (
    ROOT / "integration" / "events" / "schemas" / "event-envelope-v1.schema.json"
)
DEFAULT_MAXIMUM_LATENESS_SECONDS = 86_400
PRESERVED_RESULTS = frozenset(
    {
        "ACCEPTED",
        "ACCEPTED_LATE",
        "ACCEPTED_OUT_OF_ORDER",
        "CONFLICT_REVIEW",
    }
)


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


def build_event_validator() -> Draft202012Validator:
    schema = json.loads(EVENT_SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


@dataclass(frozen=True)
class IntakeDecision:
    result: str
    detail: str
    preserve: bool
    replayed: bool = False
    field_name: str | None = None
    late_by_seconds: int | None = None
    source_watermark: int | None = None

    @property
    def rejected(self) -> bool:
        return self.result.startswith("REJECTED_")


class EventIntakeClassifier:
    """Stateful deterministic classifier shared by contracts and adapters."""

    def __init__(
        self,
        *,
        maximum_lateness_seconds: int = DEFAULT_MAXIMUM_LATENESS_SECONDS,
        validator: Draft202012Validator | None = None,
    ) -> None:
        if maximum_lateness_seconds < 0:
            raise ValueError("maximum_lateness_seconds cannot be negative")
        self.maximum_lateness_seconds = maximum_lateness_seconds
        self.validator = validator or build_event_validator()
        self._idempotency: dict[tuple[str, str, str], str] = {}
        self._event_identities: dict[tuple[str, str, str], str] = {}
        self._source_watermarks: dict[tuple[str, str], int] = {}
        self._assertions: dict[tuple[str, str, str], set[str]] = {}

    def validate(self, event: dict[str, Any]) -> IntakeDecision | None:
        errors = sorted(
            self.validator.iter_errors(event),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            first_path = list(errors[0].absolute_path)
            return IntakeDecision(
                result="REJECTED_SCHEMA",
                detail=" | ".join(schema_error_text(error) for error in errors),
                preserve=False,
                field_name=str(first_path[0]) if first_path else None,
            )

        if event["hfscontenthash"] != content_hash(event["data"]):
            return IntakeDecision(
                result="REJECTED_HASH",
                detail="Declared content hash does not match canonical data.",
                preserve=False,
                field_name="hfscontenthash",
            )
        return None

    def classify(
        self,
        event: dict[str, Any],
        *,
        commit: bool = True,
    ) -> IntakeDecision:
        validation = self.validate(event)
        if validation is not None:
            return validation

        idempotency_scope = (
            event["hfstenantid"],
            event["source"],
            event["hfsidempotencykey"],
        )
        previous_hash = self._idempotency.get(idempotency_scope)
        if previous_hash == event["hfscontenthash"]:
            return IntakeDecision(
                result="DUPLICATE",
                detail="Exact source-data replay in the same tenant and source scope.",
                preserve=False,
                replayed=True,
            )
        if previous_hash is not None:
            return IntakeDecision(
                result="REJECTED_IDEMPOTENCY_CONFLICT",
                detail="Idempotency key was reused for different source data.",
                preserve=False,
                field_name="hfsidempotencykey",
            )

        event_identity = (
            event["hfstenantid"],
            event["source"],
            event["id"],
        )
        previous_event_hash = self._event_identities.get(event_identity)
        if previous_event_hash == event["hfscontenthash"]:
            return IntakeDecision(
                result="DUPLICATE",
                detail="Exact source-data replay for the same event identity.",
                preserve=False,
                replayed=True,
            )
        if previous_event_hash is not None:
            return IntakeDecision(
                result="REJECTED_IDEMPOTENCY_CONFLICT",
                detail="Event identity was reused for different source data.",
                preserve=False,
                field_name="id",
            )

        effective_at = event["data"]["effectiveat"]
        assertion_values: list[tuple[tuple[str, str, str], str]] = []
        has_conflict = False
        for assertion in event["data"].get("assertions", []):
            assertion_scope = (
                event["hfstenantid"],
                assertion["conflictkey"],
                effective_at,
            )
            assertion_value = canonical_json(assertion["value"])
            previous_values = self._assertions.get(assertion_scope, set())
            if previous_values and assertion_value not in previous_values:
                has_conflict = True
            assertion_values.append((assertion_scope, assertion_value))

        source_scope = (event["hfstenantid"], event["source"])
        sequence = event["hfssourcesequence"]
        watermark = self._source_watermarks.get(source_scope)
        out_of_order = watermark is not None and sequence < watermark
        next_watermark = max(watermark or 0, sequence)
        late_by_seconds = int(
            (
                parse_datetime(event["hfsobservedat"])
                - parse_datetime(event["time"])
            ).total_seconds()
        )

        if has_conflict:
            result = "CONFLICT_REVIEW"
            detail = "Contradictory assertion preserved for review."
        elif late_by_seconds > self.maximum_lateness_seconds:
            result = "ACCEPTED_LATE"
            detail = f"Event arrived {late_by_seconds} seconds late."
        elif out_of_order:
            result = "ACCEPTED_OUT_OF_ORDER"
            detail = "Source sequence is behind the current watermark."
        else:
            result = "ACCEPTED"
            detail = "Valid new event."

        if commit:
            self._idempotency[idempotency_scope] = event["hfscontenthash"]
            self._event_identities[event_identity] = event["hfscontenthash"]
            self._source_watermarks[source_scope] = next_watermark
            for assertion_scope, assertion_value in assertion_values:
                self._assertions.setdefault(assertion_scope, set()).add(
                    assertion_value
                )

        return IntakeDecision(
            result=result,
            detail=detail,
            preserve=result in PRESERVED_RESULTS,
            late_by_seconds=late_by_seconds,
            source_watermark=next_watermark,
        )
