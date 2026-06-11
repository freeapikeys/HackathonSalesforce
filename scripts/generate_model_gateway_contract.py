#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATEWAY_DIR = ROOT / "intelligence" / "model-gateway"
SCHEMA_PATH = GATEWAY_DIR / "schemas" / "model-gateway-v1.schema.json"
FIXTURE_PATH = GATEWAY_DIR / "fixtures" / "gateway-scenario-v1.json"

CONTRACT_VERSION = "1.0.0"
SCHEMA_ID = (
    "https://freeapikeys.github.io/HackathonSalesforce/"
    "models/model-gateway-v1.schema.json"
)
TENANT = "demo-mauritius"
CORRELATION = "20000000-0000-4000-8000-000000000001"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def content_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/$defs/{name}"}


def string(
    *,
    min_length: int = 1,
    max_length: int | None = None,
    pattern: str | None = None,
    format_name: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {"type": "string", "minLength": min_length}
    if max_length is not None:
        value["maxLength"] = max_length
    if pattern is not None:
        value["pattern"] = pattern
    if format_name is not None:
        value["format"] = format_name
    return value


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


def array_of(item: dict[str, Any], *, minimum: int = 0) -> dict[str, Any]:
    value: dict[str, Any] = {"type": "array", "items": item}
    if minimum:
        value["minItems"] = minimum
    return value


def contract_fields() -> dict[str, Any]:
    return {
        "contractVersion": {"const": CONTRACT_VERSION},
        "version": string(pattern="^[1-9][0-9]*\\.[0-9]+\\.[0-9]+$"),
    }


def build_schema() -> dict[str, Any]:
    identifier = string(max_length=200, pattern="^[a-z0-9][a-z0-9._-]*$")
    timestamp = string(format_name="date-time")
    data_classification = {
        "type": "string",
        "enum": ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"],
    }
    capability_name = {
        "type": "string",
        "enum": [
            "CHAT",
            "STRUCTURED_OUTPUT",
            "TOOL_USE",
            "VISION",
            "EMBEDDINGS",
        ],
    }
    status = {
        "type": "string",
        "enum": ["ACTIVE", "DEGRADED", "UNAVAILABLE", "RETIRED"],
    }

    profile = object_schema(
        {
            **contract_fields(),
            "profileKey": identifier,
            "taskType": {
                "type": "string",
                "enum": [
                    "CLASSIFICATION",
                    "EXPLANATION",
                    "RECOMMENDATION",
                    "MESSAGE_DRAFTING",
                    "EMBEDDING",
                ],
            },
            "inputSchemaRef": string(format_name="uri-reference"),
            "outputSchemaRef": string(format_name="uri-reference"),
            "requiredCapabilities": array_of(capability_name, minimum=1),
            "minimumContextTokens": {"type": "integer", "minimum": 1},
            "permittedDataClassifications": array_of(
                data_classification,
                minimum=1,
            ),
            "qualityObjective": object_schema(
                {
                    "metricKey": identifier,
                    "minimumScore": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "evaluationSuiteVersion": string(),
                },
                [
                    "metricKey",
                    "minimumScore",
                    "evaluationSuiteVersion",
                ],
            ),
            "maximumLatencyMs": {"type": "integer", "minimum": 1},
            "maximumCostUsd": {"type": "number", "minimum": 0},
            "fallbackMode": {
                "type": "string",
                "enum": ["NONE", "QUALIFIED_ONLY"],
            },
            "status": {"const": "ACTIVE"},
        },
        [
            "contractVersion",
            "version",
            "profileKey",
            "taskType",
            "inputSchemaRef",
            "outputSchemaRef",
            "requiredCapabilities",
            "minimumContextTokens",
            "permittedDataClassifications",
            "qualityObjective",
            "maximumLatencyMs",
            "maximumCostUsd",
            "fallbackMode",
            "status",
        ],
    )

    deployment = object_schema(
        {
            **contract_fields(),
            "deploymentKey": identifier,
            "adapterKey": identifier,
            "adapterInterfaceVersion": {"const": "hfs.generate.v1"},
            "providerIdentifier": string(max_length=200),
            "modelIdentifier": string(max_length=200),
            "configuredModelIdentifier": {"type": ["string", "null"]},
            "hostingClass": {
                "type": "string",
                "enum": [
                    "SALESFORCE_MANAGED",
                    "CLOUD",
                    "PRIVATE_CLOUD",
                    "ON_PREM_RELAY",
                    "MOCK",
                ],
            },
            "residencyRegions": array_of(identifier, minimum=1),
            "supportedLanguages": array_of(
                string(pattern="^[a-z]{2}(-[A-Z]{2})?$"),
                minimum=1,
            ),
            "permittedDataClassifications": array_of(
                data_classification,
                minimum=1,
            ),
            "capabilities": array_of(capability_name, minimum=1),
            "contextWindowTokens": {"type": "integer", "minimum": 1},
            "qualifiedProfiles": array_of(identifier, minimum=1),
            "qualityScores": {
                "type": "object",
                "additionalProperties": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
                "minProperties": 1,
            },
            "estimatedLatencyMs": {"type": "integer", "minimum": 1},
            "estimatedCostUsd": {"type": "number", "minimum": 0},
            "operationalStatus": status,
            "activeFrom": timestamp,
            "activeUntil": {"type": ["string", "null"], "format": "date-time"},
        },
        [
            "contractVersion",
            "version",
            "deploymentKey",
            "adapterKey",
            "adapterInterfaceVersion",
            "providerIdentifier",
            "modelIdentifier",
            "configuredModelIdentifier",
            "hostingClass",
            "residencyRegions",
            "supportedLanguages",
            "permittedDataClassifications",
            "capabilities",
            "contextWindowTokens",
            "qualifiedProfiles",
            "qualityScores",
            "estimatedLatencyMs",
            "estimatedCostUsd",
            "operationalStatus",
            "activeFrom",
            "activeUntil",
        ],
    )

    routing_policy = object_schema(
        {
            **contract_fields(),
            "policyKey": identifier,
            "tenantKey": identifier,
            "businessUnit": {"type": ["string", "null"]},
            "profileKey": identifier,
            "permittedPurposes": array_of(string(max_length=200), minimum=1),
            "candidatePriority": array_of(identifier, minimum=1),
            "requiredChecks": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {
                    "type": "string",
                    "enum": [
                        "TENANT",
                        "BUSINESS_UNIT",
                        "PURPOSE",
                        "PROFILE",
                        "DATA_CLASSIFICATION",
                        "RESIDENCY",
                        "LANGUAGE",
                        "CAPABILITY",
                        "CONTEXT_WINDOW",
                        "QUALITY",
                        "LATENCY",
                        "COST",
                        "STATUS",
                        "AVAILABILITY",
                    ],
                },
            },
            "fallbackMode": {"const": "QUALIFIED_ONLY"},
            "effectiveFrom": timestamp,
            "effectiveUntil": {"type": ["string", "null"], "format": "date-time"},
        },
        [
            "contractVersion",
            "version",
            "policyKey",
            "tenantKey",
            "businessUnit",
            "profileKey",
            "permittedPurposes",
            "candidatePriority",
            "requiredChecks",
            "fallbackMode",
            "effectiveFrom",
            "effectiveUntil",
        ],
    )

    routing_request = object_schema(
        {
            "contractVersion": {"const": CONTRACT_VERSION},
            "correlationId": string(format_name="uuid"),
            "tenantKey": identifier,
            "businessUnit": {"type": ["string", "null"]},
            "agentKey": identifier,
            "subagentKey": {"type": ["string", "null"]},
            "userId": string(max_length=200),
            "purpose": string(max_length=200),
            "profileKey": identifier,
            "dataClassification": data_classification,
            "residencyRegion": identifier,
            "language": string(pattern="^[a-z]{2}(-[A-Z]{2})?$"),
            "requiredCapabilities": array_of(capability_name, minimum=1),
            "requiredContextTokens": {"type": "integer", "minimum": 1},
            "maximumLatencyMs": {"type": "integer", "minimum": 1},
            "maximumCostUsd": {"type": "number", "minimum": 0},
            "unavailableDeploymentKeys": array_of(identifier),
        },
        [
            "contractVersion",
            "correlationId",
            "tenantKey",
            "businessUnit",
            "agentKey",
            "subagentKey",
            "userId",
            "purpose",
            "profileKey",
            "dataClassification",
            "residencyRegion",
            "language",
            "requiredCapabilities",
            "requiredContextTokens",
            "maximumLatencyMs",
            "maximumCostUsd",
            "unavailableDeploymentKeys",
        ],
    )

    qualification_check = object_schema(
        {
            "deploymentKey": identifier,
            "check": string(),
            "passed": {"type": "boolean"},
            "reasonCode": string(pattern="^[A-Z][A-Z0-9_]*$"),
        },
        ["deploymentKey", "check", "passed", "reasonCode"],
    )
    routing_decision = object_schema(
        {
            "contractVersion": {"const": CONTRACT_VERSION},
            "correlationId": string(format_name="uuid"),
            "policyKey": identifier,
            "policyVersion": string(),
            "profileKey": identifier,
            "profileVersion": string(),
            "decision": {
                "type": "string",
                "enum": ["SELECTED", "NO_QUALIFIED_DEPLOYMENT"],
            },
            "selectedDeploymentKey": {"type": ["string", "null"]},
            "selectedDeploymentVersion": {"type": ["string", "null"]},
            "fallback": {"type": "boolean"},
            "fallbackFromDeploymentKey": {"type": ["string", "null"]},
            "checks": array_of(qualification_check, minimum=1),
            "decidedAt": timestamp,
        },
        [
            "contractVersion",
            "correlationId",
            "policyKey",
            "policyVersion",
            "profileKey",
            "profileVersion",
            "decision",
            "selectedDeploymentKey",
            "selectedDeploymentVersion",
            "fallback",
            "fallbackFromDeploymentKey",
            "checks",
            "decidedAt",
        ],
    )

    generate_request = object_schema(
        {
            "contractVersion": {"const": CONTRACT_VERSION},
            "correlationId": string(format_name="uuid"),
            "tenantKey": identifier,
            "userId": string(max_length=200),
            "purpose": string(max_length=200),
            "agentKey": identifier,
            "profileKey": identifier,
            "profileVersion": string(),
            "promptVersion": string(),
            "retrievalVersion": string(),
            "messages": array_of(
                object_schema(
                    {
                        "role": {
                            "type": "string",
                            "enum": ["SYSTEM", "USER", "ASSISTANT", "TOOL"],
                        },
                        "content": string(max_length=20000),
                    },
                    ["role", "content"],
                ),
                minimum=1,
            ),
            "context": object_schema(
                {
                    "dataClassification": data_classification,
                    "evidenceIds": array_of(string(max_length=200), minimum=1),
                    "sourceContentHashes": array_of(
                        string(pattern="^sha256:[a-f0-9]{64}$"),
                        minimum=1,
                    ),
                },
                [
                    "dataClassification",
                    "evidenceIds",
                    "sourceContentHashes",
                ],
            ),
            "responseSchema": {"type": "object"},
            "invocationPolicy": object_schema(
                {
                    "maximumOutputTokens": {"type": "integer", "minimum": 1},
                    "temperature": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 2,
                    },
                    "retainContent": {"type": "boolean"},
                    "requireCitations": {"const": True},
                },
                [
                    "maximumOutputTokens",
                    "temperature",
                    "retainContent",
                    "requireCitations",
                ],
            ),
        },
        [
            "contractVersion",
            "correlationId",
            "tenantKey",
            "userId",
            "purpose",
            "agentKey",
            "profileKey",
            "profileVersion",
            "promptVersion",
            "retrievalVersion",
            "messages",
            "context",
            "responseSchema",
            "invocationPolicy",
        ],
    )

    recommendation_output = object_schema(
        {
            "facts": array_of(string(max_length=1000), minimum=1),
            "inferences": array_of(string(max_length=1000)),
            "recommendation": string(max_length=2000),
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
            "evidenceIds": array_of(string(max_length=200), minimum=1),
            "requiresHumanApproval": {"const": True},
        },
        [
            "facts",
            "inferences",
            "recommendation",
            "confidence",
            "evidenceIds",
            "requiresHumanApproval",
        ],
    )

    generate_response = object_schema(
        {
            "contractVersion": {"const": CONTRACT_VERSION},
            "correlationId": string(format_name="uuid"),
            "invocationId": identifier,
            "profileKey": identifier,
            "profileVersion": string(),
            "deploymentKey": identifier,
            "deploymentVersion": string(),
            "adapterInterfaceVersion": {"const": "hfs.generate.v1"},
            "output": ref("recommendationOutput"),
            "finishReason": {
                "type": "string",
                "enum": ["STOP", "LENGTH", "CONTENT_FILTER", "ERROR"],
            },
            "outputSchemaValid": {"type": "boolean"},
            "safetyStatus": {
                "type": "string",
                "enum": ["PASSED", "BLOCKED", "REVIEW"],
            },
        },
        [
            "contractVersion",
            "correlationId",
            "invocationId",
            "profileKey",
            "profileVersion",
            "deploymentKey",
            "deploymentVersion",
            "adapterInterfaceVersion",
            "output",
            "finishReason",
            "outputSchemaValid",
            "safetyStatus",
        ],
    )

    attempt = object_schema(
        {
            "sequence": {"type": "integer", "minimum": 1},
            "deploymentKey": identifier,
            "deploymentVersion": string(),
            "adapterKey": identifier,
            "startedAt": timestamp,
            "completedAt": timestamp,
            "status": {
                "type": "string",
                "enum": [
                    "SUCCEEDED",
                    "UNAVAILABLE",
                    "TIMEOUT",
                    "INVALID_OUTPUT",
                    "POLICY_REJECTED",
                ],
            },
            "retryable": {"type": "boolean"},
            "failureCode": {"type": ["string", "null"]},
        },
        [
            "sequence",
            "deploymentKey",
            "deploymentVersion",
            "adapterKey",
            "startedAt",
            "completedAt",
            "status",
            "retryable",
            "failureCode",
        ],
    )

    invocation_audit = object_schema(
        {
            "contractVersion": {"const": CONTRACT_VERSION},
            "invocationId": identifier,
            "correlationId": string(format_name="uuid"),
            "tenantKey": identifier,
            "userId": string(max_length=200),
            "purpose": string(max_length=200),
            "agentKey": identifier,
            "profileKey": identifier,
            "profileVersion": string(),
            "policyKey": identifier,
            "policyVersion": string(),
            "selectedDeploymentKey": {"type": ["string", "null"]},
            "selectedDeploymentVersion": {"type": ["string", "null"]},
            "promptVersion": string(),
            "retrievalVersion": string(),
            "inputHash": string(pattern="^sha256:[a-f0-9]{64}$"),
            "outputHash": {
                "type": ["string", "null"],
                "pattern": "^sha256:[a-f0-9]{64}$",
            },
            "evidenceIds": array_of(string(max_length=200), minimum=1),
            "attempts": array_of(attempt, minimum=1),
            "fallbackUsed": {"type": "boolean"},
            "inputTokens": {"type": "integer", "minimum": 0},
            "outputTokens": {"type": "integer", "minimum": 0},
            "latencyMs": {"type": "integer", "minimum": 0},
            "costUsd": {"type": "number", "minimum": 0},
            "safetyStatus": {
                "type": "string",
                "enum": ["PASSED", "BLOCKED", "NOT_RUN"],
            },
            "outputSchemaValid": {"type": "boolean"},
            "retentionMode": {
                "type": "string",
                "enum": ["HASHES_ONLY", "POLICY_APPROVED_CONTENT"],
            },
            "status": {
                "type": "string",
                "enum": ["SUCCEEDED", "FAILED_CLOSED"],
            },
            "completedAt": timestamp,
        },
        [
            "contractVersion",
            "invocationId",
            "correlationId",
            "tenantKey",
            "userId",
            "purpose",
            "agentKey",
            "profileKey",
            "profileVersion",
            "policyKey",
            "policyVersion",
            "selectedDeploymentKey",
            "selectedDeploymentVersion",
            "promptVersion",
            "retrievalVersion",
            "inputHash",
            "outputHash",
            "evidenceIds",
            "attempts",
            "fallbackUsed",
            "inputTokens",
            "outputTokens",
            "latencyMs",
            "costUsd",
            "safetyStatus",
            "outputSchemaValid",
            "retentionMode",
            "status",
            "completedAt",
        ],
    )

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "HFS Provider-Neutral Model Gateway v1",
        "$defs": {
            "modelProfile": profile,
            "modelDeployment": deployment,
            "routingPolicy": routing_policy,
            "routingRequest": routing_request,
            "routingDecision": routing_decision,
            "generateRequest": generate_request,
            "recommendationOutput": recommendation_output,
            "generateResponse": generate_response,
            "invocationAudit": invocation_audit,
        },
    }


def check(
    deployment_key: str,
    name: str,
    passed: bool,
    reason: str,
) -> dict[str, Any]:
    return {
        "deploymentKey": deployment_key,
        "check": name,
        "passed": passed,
        "reasonCode": reason,
    }


def build_fixture() -> dict[str, Any]:
    profile_key = "hospital_action_reasoning"
    primary_key = "mock-alpha-primary"
    fallback_key = "mock-beta-private"
    evidence_hash = (
        "sha256:56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70f"
        "db4feada11935c10"
    )
    response_schema = {
        "$ref": f"{SCHEMA_ID}#/$defs/recommendationOutput"
    }

    profile = {
        "contractVersion": CONTRACT_VERSION,
        "version": "1.0.0",
        "profileKey": profile_key,
        "taskType": "RECOMMENDATION",
        "inputSchemaRef": f"{SCHEMA_ID}#/$defs/generateRequest",
        "outputSchemaRef": f"{SCHEMA_ID}#/$defs/recommendationOutput",
        "requiredCapabilities": ["CHAT", "STRUCTURED_OUTPUT"],
        "minimumContextTokens": 4096,
        "permittedDataClassifications": [
            "INTERNAL",
            "CONFIDENTIAL",
        ],
        "qualityObjective": {
            "metricKey": "grounded_recommendation_score",
            "minimumScore": 0.85,
            "evaluationSuiteVersion": "recommendation-eval-1.0.0",
        },
        "maximumLatencyMs": 8000,
        "maximumCostUsd": 0.08,
        "fallbackMode": "QUALIFIED_ONLY",
        "status": "ACTIVE",
    }
    deployments = [
        {
            "contractVersion": CONTRACT_VERSION,
            "version": "1.2.0",
            "deploymentKey": primary_key,
            "adapterKey": "mock-alpha-adapter",
            "adapterInterfaceVersion": "hfs.generate.v1",
            "providerIdentifier": "mock-provider-alpha",
            "modelIdentifier": "alpha-reasoner",
            "configuredModelIdentifier": None,
            "hostingClass": "MOCK",
            "residencyRegions": ["mu", "global"],
            "supportedLanguages": ["en", "fr"],
            "permittedDataClassifications": [
                "INTERNAL",
                "CONFIDENTIAL",
            ],
            "capabilities": ["CHAT", "STRUCTURED_OUTPUT", "TOOL_USE"],
            "contextWindowTokens": 32768,
            "qualifiedProfiles": [profile_key],
            "qualityScores": {"grounded_recommendation_score": 0.91},
            "estimatedLatencyMs": 2200,
            "estimatedCostUsd": 0.035,
            "operationalStatus": "ACTIVE",
            "activeFrom": "2026-06-01T00:00:00Z",
            "activeUntil": None,
        },
        {
            "contractVersion": CONTRACT_VERSION,
            "version": "2.0.0",
            "deploymentKey": fallback_key,
            "adapterKey": "mock-beta-adapter",
            "adapterInterfaceVersion": "hfs.generate.v1",
            "providerIdentifier": "mock-provider-beta",
            "modelIdentifier": "beta-private-reasoner",
            "configuredModelIdentifier": None,
            "hostingClass": "MOCK",
            "residencyRegions": ["mu"],
            "supportedLanguages": ["en", "fr"],
            "permittedDataClassifications": [
                "INTERNAL",
                "CONFIDENTIAL",
            ],
            "capabilities": ["CHAT", "STRUCTURED_OUTPUT"],
            "contextWindowTokens": 16384,
            "qualifiedProfiles": [profile_key],
            "qualityScores": {"grounded_recommendation_score": 0.88},
            "estimatedLatencyMs": 3100,
            "estimatedCostUsd": 0.041,
            "operationalStatus": "ACTIVE",
            "activeFrom": "2026-06-01T00:00:00Z",
            "activeUntil": None,
        },
    ]
    policy = {
        "contractVersion": CONTRACT_VERSION,
        "version": "1.0.0",
        "policyKey": "north-star-hospital-routing-mauritius",
        "tenantKey": TENANT,
        "businessUnit": None,
        "profileKey": profile_key,
        "permittedPurposes": ["RESOLVE_HOSPITAL_OPERATION_RISK"],
        "candidatePriority": [primary_key, fallback_key],
        "requiredChecks": [
            "TENANT",
            "BUSINESS_UNIT",
            "PURPOSE",
            "PROFILE",
            "DATA_CLASSIFICATION",
            "RESIDENCY",
            "LANGUAGE",
            "CAPABILITY",
            "CONTEXT_WINDOW",
            "QUALITY",
            "LATENCY",
            "COST",
            "STATUS",
            "AVAILABILITY",
        ],
        "fallbackMode": "QUALIFIED_ONLY",
        "effectiveFrom": "2026-06-01T00:00:00Z",
        "effectiveUntil": None,
    }
    request = {
        "contractVersion": CONTRACT_VERSION,
        "correlationId": CORRELATION,
        "tenantKey": TENANT,
        "businessUnit": None,
        "agentKey": "north-star-orchestrator",
        "subagentKey": "hospital-action-analysis",
        "userId": "integration-user-001",
        "purpose": "RESOLVE_HOSPITAL_OPERATION_RISK",
        "profileKey": profile_key,
        "dataClassification": "CONFIDENTIAL",
        "residencyRegion": "mu",
        "language": "en",
        "requiredCapabilities": ["CHAT", "STRUCTURED_OUTPUT"],
        "requiredContextTokens": 6000,
        "maximumLatencyMs": 8000,
        "maximumCostUsd": 0.08,
        "unavailableDeploymentKeys": [],
    }
    fallback_request = {
        **request,
        "unavailableDeploymentKeys": [primary_key],
    }
    restricted_request = {
        **request,
        "dataClassification": "RESTRICTED",
    }

    pass_checks = [
        check(primary_key, name, True, "QUALIFIED")
        for name in policy["requiredChecks"]
    ]
    fallback_checks = [
        check(primary_key, "AVAILABILITY", False, "DEPLOYMENT_UNAVAILABLE"),
        *[
            check(fallback_key, name, True, "QUALIFIED")
            for name in policy["requiredChecks"]
        ],
    ]
    restricted_checks = [
        check(
            deployment_key,
            "DATA_CLASSIFICATION",
            False,
            "DATA_CLASSIFICATION_NOT_PERMITTED",
        )
        for deployment_key in (primary_key, fallback_key)
    ]
    decisions = [
        {
            "contractVersion": CONTRACT_VERSION,
            "correlationId": CORRELATION,
            "policyKey": policy["policyKey"],
            "policyVersion": policy["version"],
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "decision": "SELECTED",
            "selectedDeploymentKey": primary_key,
            "selectedDeploymentVersion": deployments[0]["version"],
            "fallback": False,
            "fallbackFromDeploymentKey": None,
            "checks": pass_checks,
            "decidedAt": "2026-06-05T08:30:11Z",
        },
        {
            "contractVersion": CONTRACT_VERSION,
            "correlationId": CORRELATION,
            "policyKey": policy["policyKey"],
            "policyVersion": policy["version"],
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "decision": "SELECTED",
            "selectedDeploymentKey": fallback_key,
            "selectedDeploymentVersion": deployments[1]["version"],
            "fallback": True,
            "fallbackFromDeploymentKey": primary_key,
            "checks": fallback_checks,
            "decidedAt": "2026-06-05T08:30:11Z",
        },
        {
            "contractVersion": CONTRACT_VERSION,
            "correlationId": CORRELATION,
            "policyKey": policy["policyKey"],
            "policyVersion": policy["version"],
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "decision": "NO_QUALIFIED_DEPLOYMENT",
            "selectedDeploymentKey": None,
            "selectedDeploymentVersion": None,
            "fallback": False,
            "fallbackFromDeploymentKey": None,
            "checks": restricted_checks,
            "decidedAt": "2026-06-05T08:30:11Z",
        },
    ]
    generate_request = {
        "contractVersion": CONTRACT_VERSION,
        "correlationId": CORRELATION,
        "tenantKey": TENANT,
        "userId": "integration-user-001",
        "purpose": "RESOLVE_HOSPITAL_OPERATION_RISK",
        "agentKey": "north-star-orchestrator",
        "profileKey": profile_key,
        "profileVersion": profile["version"],
        "promptVersion": "north-star-hospital-action-prompt-1.0.0",
        "retrievalVersion": "north-star-hospital-context-1.0.0",
        "messages": [
            {
                "role": "SYSTEM",
                "content": (
                    "Separate hospital operations facts, inferences, "
                    "assumptions, and recommendations. Cite complaint, "
                    "capacity, pharmacy stock, partner, billing, staffing, "
                    "approval, and outcome evidence. Refuse diagnosis, "
                    "treatment, dosage, triage, and clinical priority "
                    "decisions; require human approval for protected actions."
                ),
            },
            {
                "role": "USER",
                "content": (
                    "Recommend the next action for the North Star private "
                    "hospital morning operations surge."
                ),
            },
        ],
        "context": {
            "dataClassification": "CONFIDENTIAL",
            "evidenceIds": [
                "evidence-complaint-hospital-001",
                "evidence-capacity-hospital-001",
                "evidence-pharmacy-hospital-001",
                "evidence-partner-hospital-001",
                "evidence-billing-hospital-001",
            ],
            "sourceContentHashes": [evidence_hash],
        },
        "responseSchema": response_schema,
        "invocationPolicy": {
            "maximumOutputTokens": 1200,
            "temperature": 0.1,
            "retainContent": False,
            "requireCitations": True,
        },
    }
    output = {
        "facts": [
            "Patient complaints, blocked discharge rooms, low pharmacy stock, delayed lab acknowledgement, and billing holds are all active in the same morning surge window."
        ],
        "inferences": [
            "The safest next step is an operations action plan, not a clinical decision: coordinate rooms, porter work, pharmacy restock or transfer, partner escalation, billing review, and internal alerts after manager approval."
        ],
        "recommendation": (
            "Route a hospital operations action plan for manager approval: release cleaned discharge rooms, move porter work forward, request pharmacy restock or transfer, escalate the lab partner response, open billing and insurance review, send privacy-safe internal Slack/WhatsApp alerts, and capture wait-time, bed-release, stockout, billing, vendor, and task outcomes."
        ),
        "confidence": 0.87,
        "evidenceIds": [
            "evidence-complaint-hospital-001",
            "evidence-capacity-hospital-001",
            "evidence-pharmacy-hospital-001",
            "evidence-partner-hospital-001",
            "evidence-billing-hospital-001",
        ],
        "requiresHumanApproval": True,
    }
    responses = [
        {
            "contractVersion": CONTRACT_VERSION,
            "correlationId": CORRELATION,
            "invocationId": "invocation-alpha-001",
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "deploymentKey": primary_key,
            "deploymentVersion": deployments[0]["version"],
            "adapterInterfaceVersion": "hfs.generate.v1",
            "output": output,
            "finishReason": "STOP",
            "outputSchemaValid": True,
            "safetyStatus": "PASSED",
        },
        {
            "contractVersion": CONTRACT_VERSION,
            "correlationId": CORRELATION,
            "invocationId": "invocation-beta-001",
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "deploymentKey": fallback_key,
            "deploymentVersion": deployments[1]["version"],
            "adapterInterfaceVersion": "hfs.generate.v1",
            "output": output,
            "finishReason": "STOP",
            "outputSchemaValid": True,
            "safetyStatus": "PASSED",
        },
    ]
    input_hash = content_hash(generate_request)
    audits = [
        {
            "contractVersion": CONTRACT_VERSION,
            "invocationId": "invocation-alpha-001",
            "correlationId": CORRELATION,
            "tenantKey": TENANT,
            "userId": generate_request["userId"],
            "purpose": generate_request["purpose"],
            "agentKey": generate_request["agentKey"],
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "policyKey": policy["policyKey"],
            "policyVersion": policy["version"],
            "selectedDeploymentKey": primary_key,
            "selectedDeploymentVersion": deployments[0]["version"],
            "promptVersion": generate_request["promptVersion"],
            "retrievalVersion": generate_request["retrievalVersion"],
            "inputHash": input_hash,
            "outputHash": content_hash(output),
            "evidenceIds": generate_request["context"]["evidenceIds"],
            "attempts": [
                {
                    "sequence": 1,
                    "deploymentKey": primary_key,
                    "deploymentVersion": deployments[0]["version"],
                    "adapterKey": deployments[0]["adapterKey"],
                    "startedAt": "2026-06-05T08:30:12Z",
                    "completedAt": "2026-06-05T08:30:14Z",
                    "status": "SUCCEEDED",
                    "retryable": False,
                    "failureCode": None,
                }
            ],
            "fallbackUsed": False,
            "inputTokens": 840,
            "outputTokens": 156,
            "latencyMs": 2100,
            "costUsd": 0.031,
            "safetyStatus": "PASSED",
            "outputSchemaValid": True,
            "retentionMode": "HASHES_ONLY",
            "status": "SUCCEEDED",
            "completedAt": "2026-06-05T08:30:14Z",
        },
        {
            "contractVersion": CONTRACT_VERSION,
            "invocationId": "invocation-beta-001",
            "correlationId": CORRELATION,
            "tenantKey": TENANT,
            "userId": generate_request["userId"],
            "purpose": generate_request["purpose"],
            "agentKey": generate_request["agentKey"],
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "policyKey": policy["policyKey"],
            "policyVersion": policy["version"],
            "selectedDeploymentKey": fallback_key,
            "selectedDeploymentVersion": deployments[1]["version"],
            "promptVersion": generate_request["promptVersion"],
            "retrievalVersion": generate_request["retrievalVersion"],
            "inputHash": input_hash,
            "outputHash": content_hash(output),
            "evidenceIds": generate_request["context"]["evidenceIds"],
            "attempts": [
                {
                    "sequence": 1,
                    "deploymentKey": primary_key,
                    "deploymentVersion": deployments[0]["version"],
                    "adapterKey": deployments[0]["adapterKey"],
                    "startedAt": "2026-06-05T08:30:12Z",
                    "completedAt": "2026-06-05T08:30:12Z",
                    "status": "UNAVAILABLE",
                    "retryable": True,
                    "failureCode": "DEPLOYMENT_UNAVAILABLE",
                },
                {
                    "sequence": 2,
                    "deploymentKey": fallback_key,
                    "deploymentVersion": deployments[1]["version"],
                    "adapterKey": deployments[1]["adapterKey"],
                    "startedAt": "2026-06-05T08:30:12Z",
                    "completedAt": "2026-06-05T08:30:15Z",
                    "status": "SUCCEEDED",
                    "retryable": False,
                    "failureCode": None,
                },
            ],
            "fallbackUsed": True,
            "inputTokens": 840,
            "outputTokens": 156,
            "latencyMs": 3200,
            "costUsd": 0.039,
            "safetyStatus": "PASSED",
            "outputSchemaValid": True,
            "retentionMode": "HASHES_ONLY",
            "status": "SUCCEEDED",
            "completedAt": "2026-06-05T08:30:15Z",
        },
        {
            "contractVersion": CONTRACT_VERSION,
            "invocationId": "invocation-no-qualified-001",
            "correlationId": CORRELATION,
            "tenantKey": TENANT,
            "userId": generate_request["userId"],
            "purpose": generate_request["purpose"],
            "agentKey": generate_request["agentKey"],
            "profileKey": profile_key,
            "profileVersion": profile["version"],
            "policyKey": policy["policyKey"],
            "policyVersion": policy["version"],
            "selectedDeploymentKey": None,
            "selectedDeploymentVersion": None,
            "promptVersion": generate_request["promptVersion"],
            "retrievalVersion": generate_request["retrievalVersion"],
            "inputHash": content_hash(restricted_request),
            "outputHash": None,
            "evidenceIds": generate_request["context"]["evidenceIds"],
            "attempts": [
                {
                    "sequence": index,
                    "deploymentKey": deployment["deploymentKey"],
                    "deploymentVersion": deployment["version"],
                    "adapterKey": deployment["adapterKey"],
                    "startedAt": "2026-06-05T08:30:12Z",
                    "completedAt": "2026-06-05T08:30:12Z",
                    "status": "POLICY_REJECTED",
                    "retryable": False,
                    "failureCode": "DATA_CLASSIFICATION_NOT_PERMITTED",
                }
                for index, deployment in enumerate(deployments, start=1)
            ],
            "fallbackUsed": False,
            "inputTokens": 0,
            "outputTokens": 0,
            "latencyMs": 0,
            "costUsd": 0,
            "safetyStatus": "NOT_RUN",
            "outputSchemaValid": False,
            "retentionMode": "HASHES_ONLY",
            "status": "FAILED_CLOSED",
            "completedAt": "2026-06-05T08:30:12Z",
        },
    ]

    return {
        "contractVersion": CONTRACT_VERSION,
        "profiles": [profile],
        "deployments": deployments,
        "policies": [policy],
        "routingRequests": {
            "primary": request,
            "fallback": fallback_request,
            "noQualifiedDeployment": restricted_request,
        },
        "routingDecisions": {
            "primary": decisions[0],
            "fallback": decisions[1],
            "noQualifiedDeployment": decisions[2],
        },
        "generateRequest": generate_request,
        "normalizedResponses": responses,
        "invocationAudits": audits,
    }


def rendered(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2) + "\n"


def write_or_check(path: Path, content: str, check_mode: bool) -> None:
    if check_mode:
        actual = path.read_text() if path.exists() else ""
        if actual != content:
            raise SystemExit(
                f"{path.relative_to(ROOT)} is stale; run "
                "python3 scripts/generate_model_gateway_contract.py"
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    write_or_check(SCHEMA_PATH, rendered(build_schema()), args.check)
    write_or_check(FIXTURE_PATH, rendered(build_fixture()), args.check)
    verb = "verified" if args.check else "generated"
    print(f"Model gateway schema {verb}: {SCHEMA_PATH.relative_to(ROOT)}")
    print(f"Model gateway fixtures {verb}: {FIXTURE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
