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
        "purpose": "RESOLVE_RETAIL_RISK",
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
        "agentKey": "north-star-orchestrator",
        "purpose": "RESOLVE_RETAIL_RISK",
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


def citation(
    evidence_id: str,
    summary: str,
    suffix: str,
    content_hash: str,
) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "sourceEventId": "a09000000000001AAA",
        "sourceUri": f"urn:hfs:source:{suffix}",
        "contentHash": content_hash,
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
    inventory = citation(
        "a06000000000001AAA",
        "Shelf has 18 units, backroom has 24 units, warehouse has 72 units, supplier has 180 units, and promotion sales velocity is 28 units per hour.",
        "retail:inventory",
        "sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f",
    )
    complaint = citation(
        "a06000000000002AAA",
        "Five complaints mention smell, damaged packaging, refunds, and price mismatch for the same product, batch, store, and promotion window.",
        "retail:complaints",
        "sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb",
    )
    supplier = citation(
        "a06000000000003AAA",
        "Supplier approved replacement batch B with 18-hour lead time and a credit note; quality issue is not supplier-wide.",
        "retail:supplier",
        "sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588",
    )
    staffing = citation(
        "a06000000000004AAA",
        "Queue risk is forecast from 16:30 to 18:30 with three baseline cashiers and four recommended cashiers.",
        "retail:roster",
        "sha256:f42d186a12981c8c7a25b7be50f5f95541e4323f83f3f3c65de8e20717b5e6ea",
    )
    expiry = citation(
        "a06000000000005AAA",
        "Batch A expires on 2026-06-08 and has 18 near-expiry units that need rotation, markdown, or quarantine.",
        "retail:expiry",
        "sha256:9b7c6068af1620f1bc46f5ba418dc983d1d73f2b1f9892718b58a9708a924c4a",
    )
    promotion = citation(
        "a06000000000006AAA",
        "Weekend Grill promotion is active and shelf price is MUR 159 while POS price is MUR 189.",
        "retail:promotion",
        "sha256:b832255db1ee6b95f3a5ba91d39da05a0839c32bc7b1cfb7d7c32868a5ead507",
    )

    explain_request = base_request("EXPLAIN_RELATIONSHIP_CASE")
    explain_response = response("EXPLAIN_RELATIONSHIP_CASE", "SUCCESS")
    explain_response["citations"] = [
        inventory,
        complaint,
        supplier,
        staffing,
        expiry,
        promotion,
    ]
    explain_response["facts"] = [
        {
            "factId": "fact-inventory-cover",
            "statement": inventory["summary"],
            "evidenceIds": [inventory["evidenceId"]],
        },
        {
            "factId": "fact-complaint-cluster",
            "statement": complaint["summary"],
            "evidenceIds": [complaint["evidenceId"]],
        },
        {
            "factId": "fact-supplier-response",
            "statement": supplier["summary"],
            "evidenceIds": [supplier["evidenceId"]],
        },
        {
            "factId": "fact-staffing-risk",
            "statement": staffing["summary"],
            "evidenceIds": [staffing["evidenceId"]],
        },
        {
            "factId": "fact-expiry-risk",
            "statement": expiry["summary"],
            "evidenceIds": [expiry["evidenceId"]],
        },
        {
            "factId": "fact-promotion-price",
            "statement": promotion["summary"],
            "evidenceIds": [promotion["evidenceId"]],
        },
    ]
    explain_response["inferences"] = [
        {
            "inferenceId": "inference-recovery-plan",
            "statement": "North Star should transfer safe stock, quarantine suspect batch units, preserve supplier evidence, and open one extra cashier lane.",
            "basisFactIds": [
                "fact-inventory-cover",
                "fact-complaint-cluster",
                "fact-supplier-response",
                "fact-staffing-risk",
                "fact-expiry-risk",
                "fact-promotion-price",
            ],
            "confidence": 0.86,
        }
    ]

    recommendation_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    recommendation_request["desiredOutcome"] = (
        "Avoid a weekend stockout, reduce waste, contain complaint risk, and keep checkout ready without executing unapproved actions."
    )
    recommendation_request["modelProfile"] = "north-star-retail-recommendation"
    recommendation_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    recommendation_response["citations"] = explain_response["citations"]
    recommendation_response["facts"] = explain_response["facts"]
    recommendation_response["inferences"] = explain_response["inferences"]
    recommendation_response["recommendation"] = {
        "recommendationType": "PROACTIVE_RELATIONSHIP_UPDATE",
        "proposedActionType": "APPROVE_RETAIL_RECOVERY_ACTIONS",
        "rationale": (
            "Use warehouse transfer and supplier replacement for safe availability, quarantine suspect batch units, mark down only safe near-expiry units, fix shelf price, and open one extra cashier lane. Complaints require investigation and supplier response first, not an automatic block on all supplier orders."
        ),
        "confidence": 0.87,
        "evidenceIds": [
            inventory["evidenceId"],
            complaint["evidenceId"],
            supplier["evidenceId"],
            staffing["evidenceId"],
            expiry["evidenceId"],
            promotion["evidenceId"],
        ],
        "modelProfile": "north-star-retail-recommendation",
        "modelInvocationId": "model-invocation-agentforce-001",
        "requiresHumanApproval": True,
    }
    recommendation_response["audit"] = audit(
        "model-invocation-agentforce-001", True
    )

    approval_request = base_request("REQUEST_HUMAN_APPROVAL")
    approval_request["recommendationId"] = "a07000000000001AAA"
    approval_request["approvalPolicyKey"] = "north-star-manager-approval-v1"
    approval_response = response("REQUEST_HUMAN_APPROVAL", "SUCCESS")
    approval_response["approval"] = {
        "approvalId": "a08000000000001AAA",
        "recommendationId": "a07000000000001AAA",
        "policyKey": "north-star-manager-approval-v1",
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
    model_request["modelProfile"] = "north-star-retail-recommendation"
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

    changed_request = base_request("DRAFT_RELATIONSHIP_RECOMMENDATION")
    changed_request["desiredOutcome"] = (
        "Update the plan after supplier response confirms replacement batch availability."
    )
    changed_request["modelProfile"] = "north-star-retail-recommendation"
    changed_response = response("DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS")
    changed_response["citations"] = explain_response["citations"]
    changed_response["facts"] = explain_response["facts"]
    changed_response["inferences"] = [
        {
            "inferenceId": "inference-changed-recommendation",
            "statement": "Supplier response changes the plan from blind reorder to replacement plus warehouse transfer and batch-specific quarantine.",
            "basisFactIds": [
                "fact-inventory-cover",
                "fact-complaint-cluster",
                "fact-supplier-response",
                "fact-expiry-risk",
                "fact-promotion-price",
            ],
            "confidence": 0.88,
        }
    ]
    changed_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_RETAIL_RECOVERY_PLAN_UPDATED",
        "proposedActionType": "APPROVE_RETAIL_RECOVERY_ACTIONS",
        "rationale": (
            "After supplier response, approve replacement batch request and warehouse transfer, quarantine only suspect batch A units, and avoid stopping all Island Proteins orders because evidence is batch-specific rather than supplier-wide."
        ),
        "confidence": 0.88,
        "evidenceIds": [
            inventory["evidenceId"],
            complaint["evidenceId"],
            supplier["evidenceId"],
            staffing["evidenceId"],
            expiry["evidenceId"],
            promotion["evidenceId"],
        ],
        "modelProfile": "north-star-retail-recommendation",
        "modelInvocationId": "model-invocation-agentforce-002",
        "requiresHumanApproval": True,
    }
    changed_response["audit"] = audit(
        "model-invocation-agentforce-002", True
    )

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
            {
                "name": "changed-recommendation-after-supplier-response",
                "request": changed_request,
                "response": changed_response,
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
