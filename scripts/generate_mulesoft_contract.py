#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "mulesoft" / "api"
SPEC_PATH = API_DIR / "hfs-integration-v1.openapi.json"
EXAMPLES_PATH = API_DIR / "examples" / "operation-examples-v1.json"
EVENT_FIXTURE_PATH = (
    ROOT / "integration" / "events" / "fixtures" / "events" / "07-issue.json"
)

CONTRACT_VERSION = "1.0.0"
TENANT = "demo-mauritius"
CORRELATION = "10000000-0000-4000-8000-000000000001"
CALLBACK_URL = "https://callbacks.example.test/hfs/completions"


def schema_ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/components/schemas/{name}"}


def example_ref(operation_id: str, category: str) -> dict[str, str]:
    return {
        "$ref": (
            "./examples/operation-examples-v1.json"
            f"#/operations/{operation_id}/{category}"
        )
    }


def example_pointer(operation_id: str, category: str) -> str:
    return (
        "./examples/operation-examples-v1.json"
        f"#/operations/{operation_id}/{category}"
    )


def media_type(
    schema_name: str,
    operation_id: str,
    category: str,
) -> dict[str, Any]:
    return {
        "schema": schema_ref(schema_name),
        "examples": {category: example_ref(operation_id, category)},
    }


def error_response(
    description: str,
    operation_id: str,
    category: str,
    retryable: bool = False,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "description": description,
        "content": {
            "application/json": media_type(
                "ErrorResponse",
                operation_id,
                category,
            )
        },
    }
    if retryable:
        response["headers"] = {
            "Retry-After": {
                "description": "Seconds before the caller should retry.",
                "schema": {"type": "integer", "minimum": 1},
            }
        }
    return response


def operation(
    *,
    operation_id: str,
    summary: str,
    description: str,
    request_schema: str,
    success_schema: str,
    success_code: str,
    success_description: str,
    idempotent: bool,
    tags: list[str],
) -> dict[str, Any]:
    parameters = [
        {"$ref": "#/components/parameters/TenantId"},
        {"$ref": "#/components/parameters/CorrelationId"},
        {"$ref": "#/components/parameters/CallbackUrl"},
    ]
    if idempotent:
        parameters.append({"$ref": "#/components/parameters/IdempotencyKey"})

    coverage = {
        category: example_pointer(operation_id, category)
        for category in (
            "request",
            "success",
            "denial",
            "conflict",
            "validation",
            "retryableFailure",
            "callback",
        )
    }

    return {
        "operationId": operation_id,
        "summary": summary,
        "description": description,
        "tags": tags,
        "parameters": parameters,
        "requestBody": {
            "required": True,
            "content": {
                "application/json": media_type(
                    request_schema,
                    operation_id,
                    "request",
                )
            },
        },
        "responses": {
            success_code: {
                "description": success_description,
                "content": {
                    "application/json": media_type(
                        success_schema,
                        operation_id,
                        "success",
                    )
                },
            },
            "403": error_response(
                "The current client, user, purpose, or policy is not allowed.",
                operation_id,
                "denial",
            ),
            "409": error_response(
                "The request conflicts with prior content or current state.",
                operation_id,
                "conflict",
            ),
            "422": error_response(
                "The request is well formed but fails deterministic validation.",
                operation_id,
                "validation",
            ),
            "503": error_response(
                "A required dependency is temporarily unavailable.",
                operation_id,
                "retryableFailure",
                retryable=True,
            ),
        },
        "callbacks": {
            "operationCompleted": {
                "$ref": "#/components/callbacks/OperationCompleted"
            }
        },
        "security": [
            {
                "oauth2ClientCredentials": ["hfs.integration"],
                "mutualTLS": [],
            }
        ],
        "x-hfs-example-coverage": coverage,
    }


def string_schema(
    *,
    min_length: int = 1,
    max_length: int | None = None,
    pattern: str | None = None,
    format_name: str | None = None,
) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "string", "minLength": min_length}
    if max_length is not None:
        schema["maxLength"] = max_length
    if pattern is not None:
        schema["pattern"] = pattern
    if format_name is not None:
        schema["format"] = format_name
    return schema


def object_schema(
    properties: dict[str, Any],
    required: list[str],
) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }


def schemas() -> dict[str, Any]:
    identifier = string_schema(max_length=200)
    tenant = string_schema(pattern="^[a-z0-9][a-z0-9-]{2,63}$")
    correlation = string_schema(format_name="uuid")
    timestamp = string_schema(format_name="date-time")

    service_error = object_schema(
        {
            "code": {
                "type": "string",
                "enum": [
                    "INVALID_REQUEST",
                    "UNSUPPORTED_CONTRACT_VERSION",
                    "PERMISSION_DENIED",
                    "CUSTOM_PERMISSION_REQUIRED",
                    "RECORD_NOT_FOUND",
                    "SOURCE_EVIDENCE_INACCESSIBLE",
                    "TENANT_MISMATCH",
                    "INVALID_STATE",
                    "IDEMPOTENCY_CONFLICT",
                    "VALIDATION_FAILED",
                    "RETRYABLE_DEPENDENCY_FAILURE",
                    "PARTIAL_FAILURE",
                    "UNEXPECTED_ERROR",
                ],
            },
            "message": string_schema(max_length=500),
            "fieldName": {"type": ["string", "null"]},
            "retryable": {"type": "boolean"},
            "details": {"type": ["string", "null"]},
        },
        ["code", "message", "retryable"],
    )

    context_item = object_schema(
        {
            "recordId": identifier,
            "objectApiName": identifier,
            "externalKey": {"type": ["string", "null"]},
            "recordType": {"type": ["string", "null"]},
            "label": {"type": ["string", "null"]},
            "status": {"type": ["string", "null"]},
            "summary": {"type": ["string", "null"]},
            "occurredAt": {"type": ["string", "null"], "format": "date-time"},
            "sourceEventId": {"type": ["string", "null"]},
            "subjectEntityId": {"type": ["string", "null"]},
            "objectEntityId": {"type": ["string", "null"]},
            "relationshipType": {"type": ["string", "null"]},
            "participantRole": {"type": ["string", "null"]},
            "confidence": {
                "type": ["number", "null"],
                "minimum": 0,
                "maximum": 1,
            },
            "sourceUri": {"type": ["string", "null"], "format": "uri-reference"},
            "contentHash": {
                "type": ["string", "null"],
                "pattern": "^sha256:[a-f0-9]{64}$",
            },
        },
        ["recordId", "objectApiName"],
    )

    evidence_citation = object_schema(
        {
            "evidenceId": identifier,
            "sourceEventId": identifier,
            "sourceUri": string_schema(format_name="uri-reference"),
            "contentHash": string_schema(
                pattern="^sha256:[a-f0-9]{64}$",
            ),
            "summary": string_schema(max_length=1000),
            "capturedAt": timestamp,
        },
        [
            "evidenceId",
            "sourceEventId",
            "sourceUri",
            "contentHash",
            "summary",
            "capturedAt",
        ],
    )

    return {
        "EventEnvelope": {
            "$ref": "../../integration/events/schemas/event-envelope-v1.schema.json"
        },
        "ServiceError": service_error,
        "ErrorResponse": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "operation": string_schema(),
                "success": {"const": False},
                "errors": {
                    "type": "array",
                    "minItems": 1,
                    "items": schema_ref("ServiceError"),
                },
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "operation",
                "success",
                "errors",
            ],
        ),
        "EventIntakeResponse": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "eventId": string_schema(format_name="uuid"),
                "intakeResult": {
                    "type": "string",
                    "enum": [
                        "ACCEPTED",
                        "DUPLICATE",
                        "ACCEPTED_LATE",
                        "ACCEPTED_OUT_OF_ORDER",
                        "CONFLICT_REVIEW",
                    ],
                },
                "replayed": {"type": "boolean"},
                "observedAt": timestamp,
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "eventId",
                "intakeResult",
                "replayed",
                "observedAt",
            ],
        ),
        "EventReplayRequest": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "idempotencyKey": identifier,
                "purpose": string_schema(max_length=200),
                "originalAttemptId": identifier,
                "reason": string_schema(max_length=1000),
                "event": schema_ref("EventEnvelope"),
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "idempotencyKey",
                "purpose",
                "originalAttemptId",
                "reason",
                "event",
            ],
        ),
        "EventReplayResponse": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "operation": {"const": "REPLAY_EVENT"},
                "success": {"const": True},
                "replayed": {"type": "boolean"},
                "originalAttemptId": identifier,
                "replayAttemptId": identifier,
                "intakeResult": {
                    "type": "string",
                    "enum": [
                        "ACCEPTED",
                        "DUPLICATE",
                        "ACCEPTED_LATE",
                        "ACCEPTED_OUT_OF_ORDER",
                        "CONFLICT_REVIEW",
                    ],
                },
                "status": {"const": "COMPLETED"},
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "operation",
                "success",
                "replayed",
                "originalAttemptId",
                "replayAttemptId",
                "intakeResult",
                "status",
            ],
        ),
        "ContextRequest": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "workItemId": {"type": ["string", "null"]},
                "subjectEntityId": {"type": ["string", "null"]},
                "purpose": string_schema(max_length=200),
                "includeProvenance": {"type": "boolean", "default": True},
                "timelineLimit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                },
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "purpose",
                "includeProvenance",
                "timelineLimit",
            ],
            # oneOf is attached below to keep object_schema small.
        )
        | {
            "oneOf": [
                {
                    "required": ["workItemId"],
                    "properties": {"workItemId": {"type": "string"}},
                },
                {
                    "required": ["subjectEntityId"],
                    "properties": {"subjectEntityId": {"type": "string"}},
                },
            ]
        },
        "ContextItem": context_item,
        "EvidenceCitation": evidence_citation,
        "ContextResponse": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "generatedAt": timestamp,
                "workItem": {
                    "oneOf": [schema_ref("ContextItem"), {"type": "null"}]
                },
                "entities": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "relationships": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "agreements": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "sopExecutions": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "timeline": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "evidence": {
                    "type": "array",
                    "items": schema_ref("EvidenceCitation"),
                },
                "recommendations": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "approvals": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "actions": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "outcomes": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "evaluations": {
                    "type": "array",
                    "items": schema_ref("ContextItem"),
                },
                "errors": {
                    "type": "array",
                    "items": schema_ref("ServiceError"),
                },
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "generatedAt",
                "workItem",
                "entities",
                "relationships",
                "agreements",
                "sopExecutions",
                "timeline",
                "evidence",
                "recommendations",
                "approvals",
                "actions",
                "outcomes",
                "evaluations",
                "errors",
            ],
        ),
        "ActionExecutionRequest": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "purpose": string_schema(max_length=200),
                "externalKey": identifier,
                "idempotencyKey": identifier,
                "recommendationId": identifier,
                "approvalId": identifier,
                "actionId": identifier,
                "targetEntityId": identifier,
                "actionType": identifier,
                "sourceSystem": identifier,
                "payload": {"type": "object"},
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "purpose",
                "externalKey",
                "idempotencyKey",
                "recommendationId",
                "approvalId",
                "actionId",
                "targetEntityId",
                "actionType",
                "sourceSystem",
                "payload",
            ],
        ),
        "ActionExecutionResponse": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "operation": {"const": "EXECUTE_APPROVED_ACTION"},
                "success": {"const": True},
                "replayed": {"type": "boolean"},
                "actionId": identifier,
                "sourceSystem": identifier,
                "status": {
                    "type": "string",
                    "enum": ["QUEUED", "EXECUTING", "EXECUTED"],
                },
                "acceptedAt": timestamp,
                "errors": {"type": "array", "maxItems": 0},
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "operation",
                "success",
                "replayed",
                "actionId",
                "sourceSystem",
                "status",
                "acceptedAt",
                "errors",
            ],
        ),
        "OutcomeCallbackRequest": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "purpose": string_schema(max_length=200),
                "externalKey": identifier,
                "idempotencyKey": identifier,
                "actionId": identifier,
                "sourceEventId": identifier,
                "sourceSystem": identifier,
                "sourceRecordId": identifier,
                "outcomeType": identifier,
                "status": {
                    "type": "string",
                    "enum": ["SUCCESS", "FAILED", "PARTIAL", "REVERSED"],
                },
                "observedAt": timestamp,
                "summary": string_schema(max_length=2000),
                "metricKey": {"type": ["string", "null"]},
                "metricValue": {"type": ["number", "null"]},
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "purpose",
                "externalKey",
                "idempotencyKey",
                "actionId",
                "sourceEventId",
                "sourceSystem",
                "sourceRecordId",
                "outcomeType",
                "status",
                "observedAt",
                "summary",
                "metricKey",
                "metricValue",
            ],
        ),
        "OutcomeCallbackResponse": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "operation": {"const": "CAPTURE_OUTCOME"},
                "success": {"const": True},
                "replayed": {"type": "boolean"},
                "outcomeId": identifier,
                "actionId": identifier,
                "status": {"const": "RECORDED"},
                "recordedAt": timestamp,
                "errors": {"type": "array", "maxItems": 0},
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "operation",
                "success",
                "replayed",
                "outcomeId",
                "actionId",
                "status",
                "recordedAt",
                "errors",
            ],
        ),
        "OperationCallback": object_schema(
            {
                "contractVersion": {"const": CONTRACT_VERSION},
                "tenantKey": tenant,
                "correlationId": correlation,
                "operation": {
                    "type": "string",
                    "enum": [
                        "INGEST_EVENT",
                        "REPLAY_EVENT",
                        "READ_CONTEXT",
                        "EXECUTE_APPROVED_ACTION",
                        "CAPTURE_OUTCOME",
                    ],
                },
                "status": {
                    "type": "string",
                    "enum": ["COMPLETED", "REJECTED", "FAILED"],
                },
                "completedAt": timestamp,
                "retryable": {"type": "boolean"},
                "result": {"type": "object"},
                "errors": {
                    "type": "array",
                    "items": schema_ref("ServiceError"),
                },
            },
            [
                "contractVersion",
                "tenantKey",
                "correlationId",
                "operation",
                "status",
                "completedAt",
                "retryable",
                "result",
                "errors",
            ],
        ),
    }


def build_spec() -> dict[str, Any]:
    callback_examples = {
        operation_id: example_ref(operation_id, "callback")
        for operation_id in (
            "ingestEvent",
            "replayEvent",
            "retrieveContext",
            "executeApprovedAction",
            "receiveOutcomeCallback",
        )
    }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "HFS MuleSoft Integration Process API",
            "version": CONTRACT_VERSION,
            "description": (
                "Governed event intake, context retrieval, approved action "
                "execution, and outcome callbacks."
            ),
        },
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "servers": [
            {
                "url": "https://{environment}.api.example.com/hfs",
                "variables": {
                    "environment": {
                        "default": "sandbox",
                        "enum": ["sandbox", "production"],
                    }
                },
            }
        ],
        "tags": [
            {"name": "Events"},
            {"name": "Context"},
            {"name": "Actions"},
            {"name": "Outcomes"},
        ],
        "paths": {
            "/v1/events": {
                "post": operation(
                    operation_id="ingestEvent",
                    summary="Ingest a preserved source event",
                    description=(
                        "Validates the versioned event envelope and returns a "
                        "deterministic intake disposition."
                    ),
                    request_schema="EventEnvelope",
                    success_schema="EventIntakeResponse",
                    success_code="202",
                    success_description="The event was accepted or replayed.",
                    idempotent=True,
                    tags=["Events"],
                )
            },
            "/v1/events/replays": {
                "post": operation(
                    operation_id="replayEvent",
                    summary="Replay a quarantined source event",
                    description=(
                        "Creates a linked intake attempt for a corrected "
                        "quarantined event under an authorized purpose."
                    ),
                    request_schema="EventReplayRequest",
                    success_schema="EventReplayResponse",
                    success_code="202",
                    success_description="The quarantined event was replayed.",
                    idempotent=True,
                    tags=["Events"],
                )
            },
            "/v1/context/queries": {
                "post": operation(
                    operation_id="retrieveContext",
                    summary="Retrieve permission-aware operations context",
                    description=(
                        "Reads context through the current client and user "
                        "permissions for the declared purpose."
                    ),
                    request_schema="ContextRequest",
                    success_schema="ContextResponse",
                    success_code="200",
                    success_description="Authorized context was assembled.",
                    idempotent=False,
                    tags=["Context"],
                )
            },
            "/v1/actions/executions": {
                "post": operation(
                    operation_id="executeApprovedAction",
                    summary="Execute an approved external action",
                    description=(
                        "Accepts a previously approved and logged action for "
                        "source-system write-back."
                    ),
                    request_schema="ActionExecutionRequest",
                    success_schema="ActionExecutionResponse",
                    success_code="202",
                    success_description="The approved action was queued.",
                    idempotent=True,
                    tags=["Actions"],
                )
            },
            "/v1/outcomes/callbacks": {
                "post": operation(
                    operation_id="receiveOutcomeCallback",
                    summary="Capture an external action outcome",
                    description=(
                        "Records the source-system result and correlates it to "
                        "the approved action and source event."
                    ),
                    request_schema="OutcomeCallbackRequest",
                    success_schema="OutcomeCallbackResponse",
                    success_code="200",
                    success_description="The outcome was recorded or replayed.",
                    idempotent=True,
                    tags=["Outcomes"],
                )
            },
        },
        "components": {
            "securitySchemes": {
                "oauth2ClientCredentials": {
                    "type": "oauth2",
                    "flows": {
                        "clientCredentials": {
                            "tokenUrl": "https://identity.example.com/oauth2/token",
                            "scopes": {
                                "hfs.integration": (
                                    "Invoke governed HFS integration operations."
                                )
                            },
                        }
                    },
                },
                "mutualTLS": {"type": "mutualTLS"},
            },
            "parameters": {
                "TenantId": {
                    "name": "X-Tenant-Id",
                    "in": "header",
                    "required": True,
                    "description": "Tenant isolation key; must match the body.",
                    "schema": {
                        "type": "string",
                        "pattern": "^[a-z0-9][a-z0-9-]{2,63}$",
                    },
                },
                "CorrelationId": {
                    "name": "X-Correlation-Id",
                    "in": "header",
                    "required": True,
                    "description": (
                        "End-to-end trace identifier; must match the body."
                    ),
                    "schema": {"type": "string", "format": "uuid"},
                },
                "IdempotencyKey": {
                    "name": "X-Idempotency-Key",
                    "in": "header",
                    "required": True,
                    "description": (
                        "Stable retry key scoped to tenant and operation; must "
                        "match the body when the body contains one."
                    ),
                    "schema": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                    },
                },
                "CallbackUrl": {
                    "name": "X-Callback-Url",
                    "in": "header",
                    "required": False,
                    "description": (
                        "HTTPS endpoint for an optional signed completion "
                        "callback."
                    ),
                    "schema": {
                        "type": "string",
                        "format": "uri",
                        "pattern": "^https://",
                    },
                },
            },
            "callbacks": {
                "OperationCompleted": {
                    "{$request.header.X-Callback-Url}": {
                        "post": {
                            "operationId": "receiveOperationCompletion",
                            "summary": "Receive the requested completion callback",
                            "parameters": [
                                {"$ref": "#/components/parameters/TenantId"},
                                {
                                    "$ref": (
                                        "#/components/parameters/CorrelationId"
                                    )
                                },
                            ],
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": schema_ref(
                                            "OperationCallback"
                                        ),
                                        "examples": callback_examples,
                                    }
                                },
                            },
                            "responses": {
                                "204": {
                                    "description": (
                                        "The callback was durably accepted."
                                    )
                                }
                            },
                            "security": [
                                {
                                    "oauth2ClientCredentials": [
                                        "hfs.integration"
                                    ],
                                    "mutualTLS": [],
                                }
                            ],
                        }
                    }
                }
            },
            "schemas": schemas(),
        },
    }


def headers(idempotency_key: str | None = None) -> dict[str, str]:
    values = {
        "X-Tenant-Id": TENANT,
        "X-Correlation-Id": CORRELATION,
        "X-Callback-Url": CALLBACK_URL,
    }
    if idempotency_key is not None:
        values["X-Idempotency-Key"] = idempotency_key
    return values


def example(
    *,
    summary: str,
    schema_name: str,
    value: dict[str, Any],
    status: str | None = None,
    request_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "summary": summary,
        "value": value,
        "x-hfs-schema": schema_name,
    }
    if status is not None:
        item["x-hfs-status"] = status
    if request_headers is not None:
        item["x-hfs-headers"] = request_headers
    return item


def error_value(
    operation_name: str,
    code: str,
    message: str,
    *,
    retryable: bool,
    field_name: str | None = None,
) -> dict[str, Any]:
    return {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "operation": operation_name,
        "success": False,
        "errors": [
            {
                "code": code,
                "message": message,
                "fieldName": field_name,
                "retryable": retryable,
                "details": None,
            }
        ],
    }


def callback_value(
    operation_name: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "operation": operation_name,
        "status": "COMPLETED",
        "completedAt": "2026-06-05T08:31:10Z",
        "retryable": False,
        "result": result,
        "errors": [],
    }


def common_failures(operation_name: str) -> dict[str, dict[str, Any]]:
    return {
        "denial": example(
            summary="Purpose or permission denial",
            schema_name="ErrorResponse",
            status="403",
            value=error_value(
                operation_name,
                "PERMISSION_DENIED",
                "The operation is not allowed for the current purpose.",
                retryable=False,
            ),
        ),
        "conflict": example(
            summary="Idempotency or state conflict",
            schema_name="ErrorResponse",
            status="409",
            value=error_value(
                operation_name,
                "IDEMPOTENCY_CONFLICT",
                "The request key was already used for different content.",
                retryable=False,
                field_name="X-Idempotency-Key",
            ),
        ),
        "validation": example(
            summary="Deterministic validation failure",
            schema_name="ErrorResponse",
            status="422",
            value=error_value(
                operation_name,
                "VALIDATION_FAILED",
                "A required field or invariant is invalid.",
                retryable=False,
            ),
        ),
        "retryableFailure": example(
            summary="Retryable dependency failure",
            schema_name="ErrorResponse",
            status="503",
            value=error_value(
                operation_name,
                "RETRYABLE_DEPENDENCY_FAILURE",
                "A required dependency is temporarily unavailable.",
                retryable=True,
            ),
        ),
    }


def context_item(
    record_id: str,
    object_api_name: str,
    label: str,
    status: str,
) -> dict[str, Any]:
    return {
        "recordId": record_id,
        "objectApiName": object_api_name,
        "externalKey": record_id,
        "recordType": object_api_name.removeprefix("HFS_").removesuffix("__c"),
        "label": label,
        "status": status,
        "summary": None,
        "occurredAt": "2026-06-05T08:30:00Z",
        "sourceEventId": "event-issue-001",
        "subjectEntityId": "entity-person-001",
        "objectEntityId": None,
        "relationshipType": None,
        "participantRole": None,
        "confidence": 1.0,
        "sourceUri": "urn:hfs:source:operations",
        "contentHash": (
            "sha256:56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70f"
            "db4feada11935c10"
        ),
    }


def build_examples() -> dict[str, Any]:
    event_request = json.loads(EVENT_FIXTURE_PATH.read_text())
    action_key = "action-slack-alert-001-v1"
    outcome_key = "outcome-slack-alert-001-v1"

    event_success = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "eventId": event_request["id"],
        "intakeResult": "ACCEPTED",
        "replayed": False,
        "observedAt": "2026-06-05T08:30:03Z",
    }
    replay_request = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "idempotencyKey": "replay-intake-attempt-000001-v1",
        "purpose": "REPLAY_QUARANTINED_EVENT",
        "originalAttemptId": "intake-attempt-000001",
        "reason": "The source envelope was corrected and reviewed.",
        "event": event_request,
    }
    replay_success = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "operation": "REPLAY_EVENT",
        "success": True,
        "replayed": False,
        "originalAttemptId": "intake-attempt-000001",
        "replayAttemptId": "intake-attempt-000002",
        "intakeResult": "ACCEPTED",
        "status": "COMPLETED",
    }
    context_request = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "workItemId": "work-issue-001",
        "subjectEntityId": None,
        "purpose": "RESOLVE_HOSPITAL_OPERATION_RISK",
        "includeProvenance": True,
        "timelineLimit": 50,
    }
    work_item = context_item(
        "work-issue-001",
        "HFS_Work_Item__c",
        "Hospital operations surge",
        "OPEN",
    )
    context_success = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "generatedAt": "2026-06-05T08:30:10Z",
        "workItem": work_item,
        "entities": [
            context_item(
                "entity-person-001",
                "HFS_Entity__c",
                "Patient alias group",
                "ACTIVE",
            )
        ],
        "relationships": [],
        "agreements": [],
        "sopExecutions": [],
        "timeline": [work_item],
        "evidence": [
            {
                "evidenceId": "evidence-issue-001",
                "sourceEventId": "event-issue-001",
                "sourceUri": "urn:hfs:source:operations",
                "contentHash": event_request["hfscontenthash"],
                "summary": "Synthetic hospital operations signals reported a morning surge.",
                "capturedAt": "2026-06-05T08:30:03Z",
            }
        ],
        "recommendations": [],
        "approvals": [],
        "actions": [],
        "outcomes": [],
        "evaluations": [],
        "errors": [],
    }
    action_request = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "purpose": "EXECUTE_APPROVED_HOSPITAL_ACTION",
        "externalKey": "action-slack-alert-001",
        "idempotencyKey": action_key,
        "recommendationId": "recommendation-logia-001",
        "approvalId": "approval-logia-slack-001",
        "actionId": "action-slack-alert-001",
        "targetEntityId": "hospital-operations-command-001",
        "actionType": "SEND_SLACK_ALERT",
        "sourceSystem": "slack",
        "payload": {
            "targetRole": "Operations Manager",
            "targetChannel": "#logia-demo",
            "messageTitle": "Hospital operations update",
            "messageBody": (
                "Please check room cleaning, pharmacy stock, lab delay, and "
                "billing review. Logia has linked the evidence."
            ),
            "evidenceIds": [
                "hospital-complaint-cluster-001",
                "hospital-capacity-pressure-001",
                "hospital-lab-delay-001",
            ],
            "sourceRecommendationId": "recommendation-logia-001",
        },
    }
    action_success = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "operation": "EXECUTE_APPROVED_ACTION",
        "success": True,
        "replayed": False,
        "actionId": "action-slack-alert-001",
        "sourceSystem": "slack",
        "status": "QUEUED",
        "acceptedAt": "2026-06-05T08:31:00Z",
        "errors": [],
    }
    outcome_request = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "purpose": "CAPTURE_APPROVED_ACTION_OUTCOME",
        "externalKey": "outcome-slack-alert-001",
        "idempotencyKey": outcome_key,
        "actionId": "action-slack-alert-001",
        "sourceEventId": "event-slack-alert-001",
        "sourceSystem": "slack",
        "sourceRecordId": "slack-alert-delivery-001",
        "outcomeType": "SLACK_ALERT_DELIVERY",
        "status": "SUCCESS",
        "observedAt": "2026-06-05T08:31:07Z",
        "summary": "The approved Slack alert was delivered or honestly mocked.",
        "metricKey": "slack_alert_delivery_success",
        "metricValue": 1,
    }
    outcome_success = {
        "contractVersion": CONTRACT_VERSION,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "operation": "CAPTURE_OUTCOME",
        "success": True,
        "replayed": False,
        "outcomeId": "outcome-slack-alert-001",
        "actionId": "action-slack-alert-001",
        "status": "RECORDED",
        "recordedAt": "2026-06-05T08:31:08Z",
        "errors": [],
    }

    operations = {
        "ingestEvent": {
            "request": example(
                summary="Valid preserved source event",
                schema_name="EventEnvelope",
                value=event_request,
                request_headers=headers(event_request["hfsidempotencykey"]),
            ),
            "success": example(
                summary="New event accepted",
                schema_name="EventIntakeResponse",
                status="202",
                value=event_success,
            ),
            "callback": example(
                summary="Event intake completion callback",
                schema_name="OperationCallback",
                value=callback_value(
                    "INGEST_EVENT",
                    {
                        "eventId": event_request["id"],
                        "intakeResult": "ACCEPTED",
                    },
                ),
            ),
        }
        | common_failures("INGEST_EVENT"),
        "replayEvent": {
            "request": example(
                summary="Authorized replay of a corrected quarantined event",
                schema_name="EventReplayRequest",
                value=replay_request,
                request_headers=headers(replay_request["idempotencyKey"]),
            ),
            "success": example(
                summary="Linked replay completed",
                schema_name="EventReplayResponse",
                status="202",
                value=replay_success,
            ),
            "callback": example(
                summary="Event replay completion callback",
                schema_name="OperationCallback",
                value=callback_value("REPLAY_EVENT", replay_success),
            ),
        }
        | common_failures("REPLAY_EVENT"),
        "retrieveContext": {
            "request": example(
                summary="Context query by work item",
                schema_name="ContextRequest",
                value=context_request,
                request_headers=headers(),
            ),
            "success": example(
                summary="Authorized context with provenance",
                schema_name="ContextResponse",
                status="200",
                value=context_success,
            ),
            "callback": example(
                summary="Context query completion callback",
                schema_name="OperationCallback",
                value=callback_value(
                    "READ_CONTEXT",
                    {
                        "workItemId": "work-issue-001",
                        "generatedAt": "2026-06-05T08:30:10Z",
                    },
                ),
            ),
        }
        | common_failures("READ_CONTEXT"),
        "executeApprovedAction": {
            "request": example(
                summary="Approved Slack alert action",
                schema_name="ActionExecutionRequest",
                value=action_request,
                request_headers=headers(action_key),
            ),
            "success": example(
                summary="Approved action queued",
                schema_name="ActionExecutionResponse",
                status="202",
                value=action_success,
            ),
            "callback": example(
                summary="Approved action completion callback",
                schema_name="OperationCallback",
                value=callback_value(
                    "EXECUTE_APPROVED_ACTION",
                    {
                        "actionId": "action-slack-alert-001",
                        "sourceSystem": "slack",
                        "sourceRecordId": "slack-alert-delivery-001",
                        "status": "EXECUTED",
                        "delivery": {
                            "status": "MOCK_SENT",
                            "provider": "mock-slack",
                            "targetRole": "Operations Manager",
                            "targetChannel": "#logia-demo",
                        },
                    },
                ),
            ),
        }
        | common_failures("EXECUTE_APPROVED_ACTION"),
        "receiveOutcomeCallback": {
            "request": example(
                summary="Slack alert delivery outcome",
                schema_name="OutcomeCallbackRequest",
                value=outcome_request,
                request_headers=headers(outcome_key),
            ),
            "success": example(
                summary="Outcome recorded",
                schema_name="OutcomeCallbackResponse",
                status="200",
                value=outcome_success,
            ),
            "callback": example(
                summary="Outcome capture completion callback",
                schema_name="OperationCallback",
                value=callback_value(
                    "CAPTURE_OUTCOME",
                    {
                        "outcomeId": "outcome-slack-alert-001",
                        "actionId": "action-slack-alert-001",
                        "status": "RECORDED",
                    },
                ),
            ),
        }
        | common_failures("CAPTURE_OUTCOME"),
    }

    return {
        "contractVersion": CONTRACT_VERSION,
        "description": (
            "Executable examples for every request, success, denial, conflict, "
            "validation, retryable failure, and callback."
        ),
        "operations": operations,
    }


def rendered(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=False) + "\n"


def write_or_check(path: Path, content: str, check: bool) -> None:
    if check:
        actual = path.read_text() if path.exists() else ""
        if actual != content:
            raise SystemExit(
                f"{path.relative_to(ROOT)} is stale; run "
                "python3 scripts/generate_mulesoft_contract.py"
            )
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when generated contract files are stale.",
    )
    args = parser.parse_args()

    write_or_check(SPEC_PATH, rendered(build_spec()), args.check)
    write_or_check(EXAMPLES_PATH, rendered(build_examples()), args.check)

    verb = "verified" if args.check else "generated"
    print(f"MuleSoft OpenAPI contract {verb}: {SPEC_PATH.relative_to(ROOT)}")
    print(f"MuleSoft examples {verb}: {EXAMPLES_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
