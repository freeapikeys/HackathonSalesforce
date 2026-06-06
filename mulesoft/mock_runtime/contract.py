from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "mulesoft" / "api" / "hfs-integration-v1.openapi.json"
EXAMPLES_PATH = (
    ROOT
    / "mulesoft"
    / "api"
    / "examples"
    / "operation-examples-v1.json"
)
EVENT_SCHEMA_PATH = (
    ROOT / "integration" / "events" / "schemas" / "event-envelope-v1.schema.json"
)


class ContractValidationError(ValueError):
    def __init__(self, schema_name: str, messages: list[str]) -> None:
        self.schema_name = schema_name
        self.messages = messages
        super().__init__(f"{schema_name}: {' | '.join(messages)}")


class IntegrationContract:
    def __init__(self) -> None:
        self.spec = json.loads(SPEC_PATH.read_text())
        self.examples = json.loads(EXAMPLES_PATH.read_text())
        event_schema = json.loads(EVENT_SCHEMA_PATH.read_text())
        self.registry = (
            Registry()
            .with_resource(
                SPEC_PATH.resolve().as_uri(),
                Resource(contents=self.spec, specification=DRAFT202012),
            )
            .with_resource(
                EVENT_SCHEMA_PATH.resolve().as_uri(),
                Resource.from_contents(event_schema),
            )
        )

    def validate(self, schema_name: str, value: dict[str, Any]) -> None:
        schema = {
            "$ref": (
                f"{SPEC_PATH.resolve().as_uri()}"
                f"#/components/schemas/{schema_name}"
            )
        }
        validator = Draft202012Validator(
            schema,
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        errors = sorted(
            validator.iter_errors(value),
            key=lambda error: list(error.absolute_path),
        )
        if not errors:
            return

        messages = []
        for error in errors:
            path = ".".join(str(part) for part in error.absolute_path)
            messages.append(f"{path}: {error.message}" if path else error.message)
        raise ContractValidationError(schema_name, messages)

    def example(self, operation_id: str, category: str) -> dict[str, Any]:
        return self.examples["operations"][operation_id][category]["value"]
