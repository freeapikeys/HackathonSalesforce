#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "mulesoft" / "api"
SPEC_PATH = API_DIR / "hfs-integration-v1.openapi.json"
EXAMPLES_PATH = API_DIR / "examples" / "operation-examples-v1.json"
EVENT_SCHEMA_PATH = (
    ROOT / "integration" / "events" / "schemas" / "event-envelope-v1.schema.json"
)

REQUIRED_OPERATIONS = {
    "ingestEvent",
    "retrieveContext",
    "executeApprovedAction",
    "receiveOutcomeCallback",
}
REQUIRED_CATEGORIES = {
    "request",
    "success",
    "denial",
    "conflict",
    "validation",
    "retryableFailure",
    "callback",
}
EXPECTED_STATUS = {
    "denial": "403",
    "conflict": "409",
    "validation": "422",
    "retryableFailure": "503",
}


def resolve_pointer(document: Any, pointer: str) -> Any:
    if not pointer.startswith("#/"):
        raise AssertionError(f"Unsupported JSON pointer: {pointer}")
    current = document
    for raw_part in pointer[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current


def example_from_reference(
    reference: str,
    examples: dict[str, Any],
) -> dict[str, Any]:
    relative_path, pointer = reference.split("#", 1)
    assert relative_path == "./examples/operation-examples-v1.json", (
        f"Unexpected example document: {relative_path}"
    )
    return resolve_pointer(examples, f"#{pointer}")


def operation_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    operations: dict[str, dict[str, Any]] = {}
    for path_item in spec["paths"].values():
        for method, operation in path_item.items():
            if method.lower() not in {
                "get",
                "put",
                "post",
                "delete",
                "options",
                "head",
                "patch",
                "trace",
            }:
                continue
            operations[operation["operationId"]] = operation
    return operations


def schema_registry(
    spec: dict[str, Any],
    event_schema: dict[str, Any],
) -> Registry:
    return (
        Registry()
        .with_resource(
            SPEC_PATH.resolve().as_uri(),
            Resource(contents=spec, specification=DRAFT202012),
        )
        .with_resource(
            EVENT_SCHEMA_PATH.resolve().as_uri(),
            Resource.from_contents(event_schema),
        )
    )


def validate_example(
    example_object: dict[str, Any],
    registry: Registry,
) -> None:
    schema_name = example_object["x-hfs-schema"]
    root_schema = {
        "$ref": (
            f"{SPEC_PATH.resolve().as_uri()}"
            f"#/components/schemas/{schema_name}"
        )
    }
    validator = Draft202012Validator(
        root_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(example_object["value"]),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = " | ".join(
            (
                ".".join(str(part) for part in error.absolute_path)
                + f": {error.message}"
            )
            for error in errors
        )
        raise AssertionError(f"{schema_name} example is invalid: {details}")


def validate_header_consistency(
    operation_id: str,
    request_example: dict[str, Any],
) -> None:
    headers = request_example["x-hfs-headers"]
    body = request_example["value"]
    tenant_field = "hfstenantid" if operation_id == "ingestEvent" else "tenantKey"
    correlation_field = (
        "hfscorrelationid" if operation_id == "ingestEvent" else "correlationId"
    )

    assert headers["X-Tenant-Id"] == body[tenant_field]
    assert headers["X-Correlation-Id"] == body[correlation_field]

    if "X-Idempotency-Key" in headers:
        body_key = (
            body["hfsidempotencykey"]
            if operation_id == "ingestEvent"
            else body["idempotencyKey"]
        )
        assert headers["X-Idempotency-Key"] == body_key


def validate_operation_examples(
    spec: dict[str, Any],
    examples: dict[str, Any],
    registry: Registry,
) -> int:
    operations = operation_map(spec)
    assert set(operations) == REQUIRED_OPERATIONS, (
        "Unexpected operation set: " + ", ".join(sorted(operations))
    )
    assert set(examples["operations"]) == REQUIRED_OPERATIONS

    validated = 0
    for operation_id, operation in operations.items():
        coverage = operation["x-hfs-example-coverage"]
        assert set(coverage) == REQUIRED_CATEGORIES, (
            f"{operation_id} example coverage is incomplete"
        )
        assert "operationCompleted" in operation["callbacks"]

        operation_examples = examples["operations"][operation_id]
        assert set(operation_examples) == REQUIRED_CATEGORIES

        for category, reference in coverage.items():
            example_object = example_from_reference(reference, examples)
            assert example_object == operation_examples[category]
            validate_example(example_object, registry)
            validated += 1

        validate_header_consistency(operation_id, operation_examples["request"])

        for category, status in EXPECTED_STATUS.items():
            assert operation_examples[category]["x-hfs-status"] == status
            response = operation["responses"][status]
            response_ref = response["content"]["application/json"]["examples"][
                category
            ]["$ref"]
            assert response_ref == coverage[category]

        request_ref = operation["requestBody"]["content"]["application/json"][
            "examples"
        ]["request"]["$ref"]
        assert request_ref == coverage["request"]

        success_status = operation_examples["success"]["x-hfs-status"]
        success_ref = operation["responses"][success_status]["content"][
            "application/json"
        ]["examples"]["success"]["$ref"]
        assert success_ref == coverage["success"]

    return validated


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text())
    examples = json.loads(EXAMPLES_PATH.read_text())
    event_schema = json.loads(EVENT_SCHEMA_PATH.read_text())

    validate(spec, base_uri=SPEC_PATH.resolve().as_uri())
    registry = schema_registry(spec, event_schema)
    count = validate_operation_examples(spec, examples, registry)

    print(
        "MuleSoft OpenAPI contract is valid "
        f"({len(REQUIRED_OPERATIONS)} operations, {count} examples)."
    )


if __name__ == "__main__":
    main()
