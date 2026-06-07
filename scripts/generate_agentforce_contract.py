#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "intelligence"
    / "agentforce"
    / "schemas"
    / "agentforce-actions-v1.schema.json"
)
FIXTURE_PATH = (
    ROOT
    / "intelligence"
    / "agentforce"
    / "fixtures"
    / "agentforce-scenarios-v1.json"
)
CONTRACT_VERSION = "1.0.0"
TENANT = "demo-mauritius"
CORRELATION = "30000000-0000-4000-8000-000000000001"
WORK_ITEM = "a0E000000000001AAA"


def string(max_length: int = 200, pattern: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "string",
        "minLength": 1,
        "maxLength": max_length,
    }
    if pattern:
        result["pattern"] = pattern
    return result


def nullable(reference: str) -> dict[str, Any]:
    return {"oneOf": [{"$ref": reference}, {"type": "null"}]}


def schema() -> dict[str, Any]:
    key = string(pattern="^[a-z0-9][a-z0-9._-]*$")
    identifier = string()
    evidence_ids = {
        "type": "array",
        "items": identifier,
        "uniqueItems": True,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://freeapikeys.github.io/HackathonSalesforce/agentforce/agentforce-actions-v1.schema.json",
        "title": "HFS Agentforce Action Contract v1",
        "type": "object",
        "additionalProperties": False,
        "required": ["contractVersion", "actionCatalog", "scenarios"],
        "properties": {
            "contractVersion": {"const": CONTRACT_VERSION},
            "actionCatalog": {
                "type": "array",
                "items": {"$ref": "#/$defs/actionDefinition"},
                "minItems": 3,
            },
            "scenarios": {
                "type": "array",
                "items": {"$ref": "#/$defs/scenario"},
                "minItems": 7,
            },
        },
        "$defs": {
            "actionDefinition": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "developerName",
                    "action",
                    "target",
                    "description",
                    "requireUserConfirmation",
                    "inputContract",
                    "outputContract",
                ],
                "properties": {
                    "developerName": {
                        "type": "string",
                        "pattern": "^[a-z][a-z0-9_]{0,79}$",
                    },
                    "action": {
                        "enum": [
                            "EXPLAIN_RELATIONSHIP_CASE",
                            "DRAFT_RELATIONSHIP_RECOMMENDATION",
                            "REQUEST_HUMAN_APPROVAL",
                        ]
                    },
                    "target": {
                        "type": "string",
                        "pattern": "^apex://[A-Za-z][A-Za-z0-9_]{0,79}$",
                    },
                    "description": string(1000),
                    "requireUserConfirmation": {"type": "boolean"},
                    "inputContract": {"const": "#/$defs/actionRequest"},
                    "outputContract": {"const": "#/$defs/actionResponse"},
                },
            },
            "actionRequest": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "contractVersion",
                    "action",
                    "tenantKey",
                    "correlationId",
                    "purpose",
                    "workItemId",
                ],
                "properties": {
                    "contractVersion": {"const": CONTRACT_VERSION},
                    "action": {
                        "enum": [
                            "EXPLAIN_RELATIONSHIP_CASE",
                            "DRAFT_RELATIONSHIP_RECOMMENDATION",
                            "REQUEST_HUMAN_APPROVAL",
                            "EXECUTE_EXTERNAL_ACTION",
                        ]
                    },
                    "tenantKey": key,
                    "correlationId": {"type": "string", "format": "uuid"},
                    "purpose": string(),
                    "workItemId": identifier,
                    "recommendationId": {
                        "type": ["string", "null"],
                        "maxLength": 200,
                    },
                    "approvalPolicyKey": {
                        "type": ["string", "null"],
                        "maxLength": 200,
                    },
                    "desiredOutcome": {
                        "type": ["string", "null"],
                        "maxLength": 1000,
                    },
                    "modelProfile": {
                        "type": ["string", "null"],
                        "maxLength": 200,
                    },
                },
            },
            "citation": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "evidenceId",
                    "sourceEventId",
                    "sourceUri",
                    "contentHash",
                    "summary",
                    "accessible",
                ],
                "properties": {
                    "evidenceId": identifier,
                    "sourceEventId": identifier,
                    "sourceUri": string(500),
                    "contentHash": {
                        "type": "string",
                        "pattern": "^sha256:[a-f0-9]{64}$",
                    },
                    "summary": string(2000),
                    "accessible": {"const": True},
                },
            },
            "fact": {
                "type": "object",
                "additionalProperties": False,
                "required": ["factId", "statement", "evidenceIds"],
                "properties": {
                    "factId": key,
                    "statement": string(2000),
                    "evidenceIds": {
                        **evidence_ids,
                        "minItems": 1,
                    },
                },
            },
            "inference": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "inferenceId",
                    "statement",
                    "basisFactIds",
                    "confidence",
                ],
                "properties": {
                    "inferenceId": key,
                    "statement": string(2000),
                    "basisFactIds": {
                        "type": "array",
                        "items": key,
                        "minItems": 1,
                        "uniqueItems": True,
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                },
            },
            "recommendation": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "recommendationType",
                    "proposedActionType",
                    "rationale",
                    "confidence",
                    "evidenceIds",
                    "modelProfile",
                    "modelInvocationId",
                    "requiresHumanApproval",
                ],
                "properties": {
                    "recommendationType": string(),
                    "proposedActionType": string(),
                    "rationale": string(4000),
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "evidenceIds": {
                        **evidence_ids,
                        "minItems": 1,
                    },
                    "modelProfile": key,
                    "modelInvocationId": identifier,
                    "requiresHumanApproval": {"const": True},
                },
            },
            "approval": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "approvalId",
                    "recommendationId",
                    "policyKey",
                    "status",
                    "externalActionExecuted",
                ],
                "properties": {
                    "approvalId": identifier,
                    "recommendationId": identifier,
                    "policyKey": key,
                    "status": {"const": "PENDING"},
                    "externalActionExecuted": {"const": False},
                },
            },
            "refusal": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "code",
                    "message",
                    "retryable",
                    "disclosedRecordIds",
                ],
                "properties": {
                    "code": {
                        "enum": [
                            "INACCESSIBLE_EVIDENCE",
                            "UNAUTHORIZED_ACTION",
                            "PURPOSE_DENIED",
                            "NO_QUALIFIED_MODEL",
                        ]
                    },
                    "message": string(1000),
                    "retryable": {"type": "boolean"},
                    "disclosedRecordIds": {
                        "type": "array",
                        "maxItems": 0,
                    },
                },
            },
            "serviceError": {
                "type": "object",
                "additionalProperties": False,
                "required": ["code", "message", "retryable"],
                "properties": {
                    "code": {
                        "enum": [
                            "INVALID_REQUEST",
                            "UNSUPPORTED_CONTRACT_VERSION",
                            "VALIDATION_FAILED",
                            "RETRYABLE_DEPENDENCY_FAILURE",
                            "UNEXPECTED_ERROR",
                        ]
                    },
                    "message": string(1000),
                    "retryable": {"type": "boolean"},
                },
            },
            "audit": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "actorUserId",
                    "agentKey",
                    "purpose",
                    "permissionEvaluated",
                    "modelInvocationId",
                    "humanApprovalRequired",
                    "externalActionExecuted",
                ],
                "properties": {
                    "actorUserId": identifier,
                    "agentKey": key,
                    "purpose": string(),
                    "permissionEvaluated": {"const": True},
                    "modelInvocationId": {
                        "type": ["string", "null"],
                        "maxLength": 200,
                    },
                    "humanApprovalRequired": {"type": "boolean"},
                    "externalActionExecuted": {"const": False},
                },
            },
            "actionResponse": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "contractVersion",
                    "action",
                    "tenantKey",
                    "correlationId",
                    "status",
                    "facts",
                    "inferences",
                    "citations",
                    "recommendation",
                    "approval",
                    "refusal",
                    "errors",
                    "audit",
                ],
                "properties": {
                    "contractVersion": {"const": CONTRACT_VERSION},
                    "action": {
                        "enum": [
                            "EXPLAIN_RELATIONSHIP_CASE",
                            "DRAFT_RELATIONSHIP_RECOMMENDATION",
                            "REQUEST_HUMAN_APPROVAL",
                            "EXECUTE_EXTERNAL_ACTION",
                        ]
                    },
                    "tenantKey": key,
                    "correlationId": {"type": "string", "format": "uuid"},
                    "status": {"enum": ["SUCCESS", "REFUSED", "ERROR"]},
                    "facts": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/fact"},
                    },
                    "inferences": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/inference"},
                    },
                    "citations": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/citation"},
                    },
                    "recommendation": nullable("#/$defs/recommendation"),
                    "approval": nullable("#/$defs/approval"),
                    "refusal": nullable("#/$defs/refusal"),
                    "errors": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/serviceError"},
                    },
                    "audit": {"$ref": "#/$defs/audit"},
                },
            },
            "scenario": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "request", "response"],
                "properties": {
                    "name": key,
                    "request": {"$ref": "#/$defs/actionRequest"},
                    "response": {"$ref": "#/$defs/actionResponse"},
                },
            },
        },
    }


def base_request(action: str) -> dict[str, Any]:
    return {
        "contractVersion": CONTRACT_VERSION,
        "action": action,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "purpose": "RESOLVE_SERVICE_INTERRUPTION",
        "workItemId": WORK_ITEM,
        "recommendationId": None,
        "approvalPolicyKey": None,
        "desiredOutcome": None,
        "modelProfile": None,
    }


def audit(
    model_invocation_id: str | None = None,
    human_approval_required: bool = False,
) -> dict[str, Any]:
    return {
        "actorUserId": "005000000000001AAA",
        "agentKey": "relationship-management-agent",
        "purpose": "RESOLVE_SERVICE_INTERRUPTION",
        "permissionEvaluated": True,
        "modelInvocationId": model_invocation_id,
        "humanApprovalRequired": human_approval_required,
        "externalActionExecuted": False,
    }


def response(action: str, status: str) -> dict[str, Any]:
    return {
        "contractVersion": CONTRACT_VERSION,
        "action": action,
        "tenantKey": TENANT,
        "correlationId": CORRELATION,
        "status": status,
        "facts": [],
        "inferences": [],
        "citations": [],
        "recommendation": None,
        "approval": None,
        "refusal": None,
        "errors": [],
        "audit": audit(),
    }


def citation(evidence_id: str, summary: str, suffix: str) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "sourceEventId": "a09000000000001AAA",
        "sourceUri": f"urn:hfs:source:{suffix}",
        "contentHash": (
            "sha256:"
            + (
                "56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70fdb4feada11935c10"
                if suffix == "operations"
                else "7549cf0c63ad4a64f178d8500c1f3874d97478f6ee323e4debbab6d89b168b69"
            )
        ),
        "summary": summary,
        "accessible": True,
    }


def refusal(code: str, message: str, retryable: bool = False) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "retryable": retryable,
        "disclosedRecordIds": [],
    }


def fixtures() -> dict[str, Any]:
    incident = citation(
        "a06000000000001AAA",
        "The operations source reported repeated service interruption.",
        "operations",
    )
    agreement = citation(
        "a06000000000002AAA",
        "The agreement requires an update within two hours.",
        "contracts",
    )

    explain_request = base_request("EXPLAIN_RELATIONSHIP_CASE")
    explain_response = response("EXPLAIN_RELATIONSHIP_CASE", "SUCCESS")
    explain_response["citations"] = [incident, agreement]
    explain_response["facts"] = [
        {
            "factId": "fact-interruption",
            "statement": incident["summary"],
            "evidenceIds": [incident["evidenceId"]],
        },
        {
            "factId": "fact-update-obligation",
            "statement": agreement["summary"],
            "evidenceIds": [agreement["evidenceId"]],
        },
    ]
    explain_response["inferences"] = [
        {
            "inferenceId": "inference-update-risk",
            "statement": "A delayed update is likely to increase status chasing.",
            "basisFactIds": [
                "fact-interruption",
                "fact-update-obligation",
            ],
            "confidence": 0.82,
        }
    ]

    recommendation_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    recommendation_request["desiredOutcome"] = (
        "Reduce repeated status chasing without sending an unapproved message."
    )
    recommendation_request["modelProfile"] = "recommendation_reasoning"
    recommendation_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    recommendation_response["citations"] = [incident, agreement]
    recommendation_response["facts"] = explain_response["facts"]
    recommendation_response["inferences"] = explain_response["inferences"]
    recommendation_response["recommendation"] = {
        "recommendationType": "PROACTIVE_RELATIONSHIP_UPDATE",
        "proposedActionType": "SEND_STATUS_UPDATE",
        "rationale": (
            "Prepare a grounded update naming the owner and next update time, "
            "then route it for human approval."
        ),
        "confidence": 0.87,
        "evidenceIds": [
            incident["evidenceId"],
            agreement["evidenceId"],
        ],
        "modelProfile": "recommendation_reasoning",
        "modelInvocationId": "model-invocation-agentforce-001",
        "requiresHumanApproval": True,
    }
    recommendation_response["audit"] = audit(
        "model-invocation-agentforce-001", True
    )

    approval_request = base_request("REQUEST_HUMAN_APPROVAL")
    approval_request["recommendationId"] = "a07000000000001AAA"
    approval_request["approvalPolicyKey"] = (
        "external-relationship-communication-v1"
    )
    approval_response = response("REQUEST_HUMAN_APPROVAL", "SUCCESS")
    approval_response["approval"] = {
        "approvalId": "a08000000000001AAA",
        "recommendationId": "a07000000000001AAA",
        "policyKey": "external-relationship-communication-v1",
        "status": "PENDING",
        "externalActionExecuted": False,
    }
    approval_response["audit"] = audit(None, True)

    inaccessible_request = base_request("EXPLAIN_RELATIONSHIP_CASE")
    inaccessible_response = response("EXPLAIN_RELATIONSHIP_CASE", "REFUSED")
    inaccessible_response["refusal"] = refusal(
        "INACCESSIBLE_EVIDENCE",
        "The source evidence is missing or inaccessible for this user and purpose.",
    )

    execution_request = base_request("EXECUTE_EXTERNAL_ACTION")
    execution_request["recommendationId"] = "a07000000000001AAA"
    execution_response = response("EXECUTE_EXTERNAL_ACTION", "REFUSED")
    execution_response["refusal"] = refusal(
        "UNAUTHORIZED_ACTION",
        "Agentforce cannot execute the protected external action. Human approval and the governed execution service are required.",
    )
    execution_response["audit"] = audit(None, True)

    model_request = base_request("DRAFT_RELATIONSHIP_RECOMMENDATION")
    model_request["modelProfile"] = "recommendation_reasoning"
    model_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "REFUSED"
    )
    model_response["refusal"] = refusal(
        "NO_QUALIFIED_MODEL",
        "No model deployment satisfies the configured policy.",
        True,
    )

    invalid_request = base_request("REQUEST_HUMAN_APPROVAL")
    invalid_response = response("REQUEST_HUMAN_APPROVAL", "ERROR")
    invalid_response["errors"] = [
        {
            "code": "INVALID_REQUEST",
            "message": "A recommendation identifier and approval policy are required.",
            "retryable": False,
        }
    ]

    return {
        "contractVersion": CONTRACT_VERSION,
        "actionCatalog": [
            {
                "developerName": "explain_relationship_case",
                "action": "EXPLAIN_RELATIONSHIP_CASE",
                "target": "apex://HFS_AgentExplainAction",
                "description": (
                    "Read permission-aware relationship context, separate "
                    "facts from inference, and return accessible citations."
                ),
                "requireUserConfirmation": False,
                "inputContract": "#/$defs/actionRequest",
                "outputContract": "#/$defs/actionResponse",
            },
            {
                "developerName": "draft_relationship_recommendation",
                "action": "DRAFT_RELATIONSHIP_RECOMMENDATION",
                "target": "apex://HFS_AgentRecommendationAction",
                "description": (
                    "Draft an evidence-backed recommendation through the "
                    "qualified model gateway without executing an action."
                ),
                "requireUserConfirmation": False,
                "inputContract": "#/$defs/actionRequest",
                "outputContract": "#/$defs/actionResponse",
            },
            {
                "developerName": "request_human_approval",
                "action": "REQUEST_HUMAN_APPROVAL",
                "target": "apex://HFS_AgentApprovalRequestAction",
                "description": (
                    "Create a pending human approval request for an existing "
                    "recommendation. Never execute the protected action."
                ),
                "requireUserConfirmation": True,
                "inputContract": "#/$defs/actionRequest",
                "outputContract": "#/$defs/actionResponse",
            },
        ],
        "scenarios": [
            {
                "name": "accessible-grounded-explanation",
                "request": explain_request,
                "response": explain_response,
            },
            {
                "name": "grounded-recommendation",
                "request": recommendation_request,
                "response": recommendation_response,
            },
            {
                "name": "pending-human-approval",
                "request": approval_request,
                "response": approval_response,
            },
            {
                "name": "inaccessible-evidence-refusal",
                "request": inaccessible_request,
                "response": inaccessible_response,
            },
            {
                "name": "unauthorized-external-action-refusal",
                "request": execution_request,
                "response": execution_response,
            },
            {
                "name": "no-qualified-model-refusal",
                "request": model_request,
                "response": model_response,
            },
            {
                "name": "invalid-approval-request-error",
                "request": invalid_request,
                "response": invalid_response,
            },
        ],
    }


def serialized(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = {
        SCHEMA_PATH: serialized(schema()),
        FIXTURE_PATH: serialized(fixtures()),
    }
    if args.check:
        changed = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.exists() or path.read_text() != content
        ]
        if changed:
            for path in changed:
                print(f"changed: {path}", file=sys.stderr)
            return 1
        print("Agentforce contract artifacts match generator.")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print("Generated Agentforce action contract 1.0.0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
