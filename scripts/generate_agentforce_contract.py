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


def evidence_id_list(min_items: int = 1) -> dict[str, Any]:
    return {
        "type": "array",
        "items": string(),
        "uniqueItems": True,
        "minItems": min_items,
    }


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
                    "inventoryWasteReasoning": nullable(
                        "#/$defs/inventoryWasteReasoning"
                    ),
                },
            },
            "recommendedInventoryAction": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "actionId",
                    "actionType",
                    "statement",
                    "evidenceIds",
                    "requiresHumanApproval",
                ],
                "properties": {
                    "actionId": key,
                    "actionType": string(),
                    "statement": string(1000),
                    "evidenceIds": evidence_id_list(),
                    "requiresHumanApproval": {"const": True},
                },
            },
            "blockedInventoryAction": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "actionType",
                    "reason",
                    "evidenceIds",
                ],
                "properties": {
                    "actionType": string(),
                    "reason": string(1000),
                    "evidenceIds": evidence_id_list(),
                },
            },
            "supplierCaution": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "applies",
                    "statement",
                    "evidenceIds",
                ],
                "properties": {
                    "applies": {"type": "boolean"},
                    "statement": string(1000),
                    "evidenceIds": evidence_id_list(),
                },
            },
            "inventoryWasteReasoning": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "riskType",
                    "severity",
                    "missingEvidence",
                    "recommendedActions",
                    "blockedActions",
                    "supplierCaution",
                    "explanation",
                ],
                "properties": {
                    "riskType": {
                        "enum": [
                            "STOCKOUT",
                            "EXPIRY",
                            "WASTE",
                            "OVERSTOCK",
                            "PROMOTION_READINESS",
                            "MIXED",
                        ]
                    },
                    "severity": {
                        "enum": ["Low", "Medium", "High", "Critical"]
                    },
                    "missingEvidence": {
                        "type": "array",
                        "items": string(500),
                        "uniqueItems": True,
                    },
                    "recommendedActions": {
                        "type": "array",
                        "items": {
                            "$ref": "#/$defs/recommendedInventoryAction"
                        },
                        "minItems": 1,
                    },
                    "blockedActions": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/blockedInventoryAction"},
                    },
                    "supplierCaution": {
                        "$ref": "#/$defs/supplierCaution"
                    },
                    "explanation": string(2000),
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

    missing_expiry_inventory = citation(
        "a06000000000007AAA",
        "Fresh yogurt 500 g at Flacq Hypermarket has 12 shelf units, 6 backroom units, no warehouse units, 24 incoming units reserved for tomorrow, supplier lead time of 3 days, daily sales velocity of 18 units, and a promotion uplift multiplier of 1.5.",
        "retail:inventory",
        "sha256:e7001d9e919341eaba989a6c0a17a4e1f5db506cfe108a83dd22fe31adeb868a",
    )
    missing_expiry = citation(
        "a06000000000008AAA",
        "Expiry batch dates are missing for the current fresh dairy stock, so near-expiry units and expected sales before expiry cannot be calculated.",
        "retail:expiry",
        "sha256:f1e55a20be4552200825805f52383889e7f469ff717965ca279b52c572564b84",
    )
    pending_complaint = citation(
        "a06000000000009AAA",
        "Two freshness complaints mention sour smell for the same product this morning, but no confirmed batch identifier has been linked to the complaints.",
        "retail:complaints",
        "sha256:1d5ded791652aeb621acfc5b739a86ff74b40e00d65e5b8d5229dda54f0dd2ca",
    )
    pending_supplier = citation(
        "a06000000000010AAA",
        "Supplier response is pending for the freshness complaints and no replacement batch has been confirmed.",
        "retail:supplier",
        "sha256:8157415f9c79fbf265e414509a2d2cec7980c1eaab6e50368652a329e4c6b41b",
    )
    missing_expiry_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    missing_expiry_request["desiredOutcome"] = (
        "Assess promotion readiness when stock pressure exists but expiry and supplier response evidence are incomplete."
    )
    missing_expiry_request["modelProfile"] = (
        "north-star-retail-recommendation"
    )
    missing_expiry_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    missing_expiry_response["citations"] = [
        missing_expiry_inventory,
        missing_expiry,
        pending_complaint,
        pending_supplier,
    ]
    missing_expiry_response["facts"] = [
        {
            "factId": "fact-missing-expiry-inventory",
            "statement": missing_expiry_inventory["summary"],
            "evidenceIds": [missing_expiry_inventory["evidenceId"]],
        },
        {
            "factId": "fact-missing-expiry-data",
            "statement": missing_expiry["summary"],
            "evidenceIds": [missing_expiry["evidenceId"]],
        },
        {
            "factId": "fact-pending-complaints",
            "statement": pending_complaint["summary"],
            "evidenceIds": [pending_complaint["evidenceId"]],
        },
        {
            "factId": "fact-pending-supplier-response",
            "statement": pending_supplier["summary"],
            "evidenceIds": [pending_supplier["evidenceId"]],
        },
    ]
    missing_expiry_response["inferences"] = [
        {
            "inferenceId": "inference-stockout-cover",
            "statement": "Available stock is 42 units, adjusted demand is 27 units per day, days of cover is 1.56 days, and sales at risk over the 3-day lead time is 39 units.",
            "basisFactIds": ["fact-missing-expiry-inventory"],
            "confidence": 0.9,
        },
        {
            "inferenceId": "inference-missing-expiry-caution",
            "statement": "Waste and expiry pressure cannot be quantified until batch expiry evidence is supplied, so the plan should favor reversible replenishment and manager-approved quality checks.",
            "basisFactIds": [
                "fact-missing-expiry-data",
                "fact-pending-complaints",
                "fact-pending-supplier-response",
            ],
            "confidence": 0.74,
        },
    ]
    missing_expiry_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_INVENTORY_WASTE_REASONING",
        "proposedActionType": "APPROVE_CAUTIONED_INVENTORY_ACTIONS",
        "rationale": (
            "Treat this as high stockout risk because promotion-adjusted cover is 1.56 days and lead-time demand exceeds available stock by 39 units. Do not place a blind supplier reorder while freshness complaints and supplier response are unresolved; request expiry evidence, transfer safe available stock if approved, and hold supplier escalation decisions until the response arrives."
        ),
        "confidence": 0.78,
        "evidenceIds": [
            missing_expiry_inventory["evidenceId"],
            missing_expiry["evidenceId"],
            pending_complaint["evidenceId"],
            pending_supplier["evidenceId"],
        ],
        "modelProfile": "north-star-retail-recommendation",
        "modelInvocationId": "model-invocation-agentforce-003",
        "requiresHumanApproval": True,
        "inventoryWasteReasoning": {
            "riskType": "MIXED",
            "severity": "High",
            "missingEvidence": [
                "Current batch expiry dates and quantities",
                "Supplier response or confirmed replacement batch",
                "Complaint batch linkage",
            ],
            "recommendedActions": [
                {
                    "actionId": "action-transfer-safe-stock",
                    "actionType": "WAREHOUSE_TRANSFER_REVIEW",
                    "statement": "Request manager approval to transfer safe stock from a trusted source before the promotion peak.",
                    "evidenceIds": [
                        missing_expiry_inventory["evidenceId"],
                        pending_complaint["evidenceId"],
                    ],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-request-expiry-evidence",
                    "actionType": "REQUEST_EXPIRY_BATCH_EVIDENCE",
                    "statement": "Ask store execution to capture batch expiry dates before markdown, removal, or waste calculations are approved.",
                    "evidenceIds": [missing_expiry["evidenceId"]],
                    "requiresHumanApproval": True,
                },
            ],
            "blockedActions": [
                {
                    "actionType": "BLIND_SUPPLIER_REORDER",
                    "reason": "Freshness complaints and a pending supplier response make an automatic reorder unsafe without manager approval and additional supplier evidence.",
                    "evidenceIds": [
                        pending_complaint["evidenceId"],
                        pending_supplier["evidenceId"],
                    ],
                },
                {
                    "actionType": "MARKDOWN_OR_REMOVE_STOCK",
                    "reason": "Expiry dates and batch quantities are missing, so waste risk units cannot be calculated yet.",
                    "evidenceIds": [missing_expiry["evidenceId"]],
                },
            ],
            "supplierCaution": {
                "applies": True,
                "statement": "Supplier caution applies to blind reorder and supplier-wide decisions because complaints exist and the supplier response is pending.",
                "evidenceIds": [
                    pending_complaint["evidenceId"],
                    pending_supplier["evidenceId"],
                ],
            },
            "explanation": "Promotion-adjusted demand leaves less than two days of cover, but expiry and supplier response evidence are incomplete. The safe path is to seek approval for reversible stock movement, collect expiry details, and block blind supplier reorder or markdown decisions until the missing evidence arrives.",
        },
    }
    missing_expiry_response["audit"] = audit(
        "model-invocation-agentforce-003", True
    )

    clean_stockout_inventory = citation(
        "a06000000000011AAA",
        "Rice 5 kg at Rose Hill Market has 4 shelf units, 4 backroom units, 8 warehouse units, no incoming reservations, supplier lead time of 2 days, daily sales velocity of 18 units, and a promotion uplift multiplier of 1.5.",
        "retail:inventory",
        "sha256:23aadc88bcfab1ecb40f0fcee22877c6b64ddf88507d5062b26cd42cdd7b50f1",
    )
    clean_stockout_supplier = citation(
        "a06000000000012AAA",
        "Supplier history is clean for the rice product with no active complaints, no open quality cases, and on-time replacement support in the last review window.",
        "retail:supplier",
        "sha256:6f77a1e864a7ca662ac99665e3a455d86f60b1ed8aba0f2c25f9ccb157c0ea19",
    )
    clean_stockout_complaints = citation(
        "a06000000000013AAA",
        "No current complaint cluster is linked to the rice product, store, supplier, or promotion window.",
        "retail:complaints",
        "sha256:b14d6c426e221865ce89856fb2a242118e66784260b451e1b64d3948ae3e063c",
    )
    clean_stockout_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    clean_stockout_request["desiredOutcome"] = (
        "Assess stockout risk when supplier and complaint evidence are clean."
    )
    clean_stockout_request["modelProfile"] = (
        "north-star-retail-recommendation"
    )
    clean_stockout_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    clean_stockout_response["citations"] = [
        clean_stockout_inventory,
        clean_stockout_supplier,
        clean_stockout_complaints,
    ]
    clean_stockout_response["facts"] = [
        {
            "factId": "fact-clean-stockout-inventory",
            "statement": clean_stockout_inventory["summary"],
            "evidenceIds": [clean_stockout_inventory["evidenceId"]],
        },
        {
            "factId": "fact-clean-stockout-supplier",
            "statement": clean_stockout_supplier["summary"],
            "evidenceIds": [clean_stockout_supplier["evidenceId"]],
        },
        {
            "factId": "fact-clean-stockout-complaints",
            "statement": clean_stockout_complaints["summary"],
            "evidenceIds": [clean_stockout_complaints["evidenceId"]],
        },
    ]
    clean_stockout_response["inferences"] = [
        {
            "inferenceId": "inference-clean-stockout-cover",
            "statement": "Available stock is 16 units, adjusted demand is 27 units per day, days of cover is 0.59 days, and sales at risk over the 2-day lead time is 38 units.",
            "basisFactIds": ["fact-clean-stockout-inventory"],
            "confidence": 0.91,
        },
        {
            "inferenceId": "inference-clean-stockout-action",
            "statement": "Because supplier and complaint evidence are clean, the safest recommendation is manager-approved reorder or transfer rather than quarantine.",
            "basisFactIds": [
                "fact-clean-stockout-inventory",
                "fact-clean-stockout-supplier",
                "fact-clean-stockout-complaints",
            ],
            "confidence": 0.86,
        },
    ]
    clean_stockout_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_INVENTORY_WASTE_REASONING",
        "proposedActionType": "APPROVE_STOCKOUT_RECOVERY_ACTIONS",
        "rationale": (
            "Treat this as critical stockout risk because promotion-adjusted cover is 0.59 days and lead-time demand exceeds available stock by 38 units. Clean supplier and complaint evidence support manager-approved reorder or transfer, with no supplier caution beyond normal approval."
        ),
        "confidence": 0.86,
        "evidenceIds": [
            clean_stockout_inventory["evidenceId"],
            clean_stockout_supplier["evidenceId"],
            clean_stockout_complaints["evidenceId"],
        ],
        "modelProfile": "north-star-retail-recommendation",
        "modelInvocationId": "model-invocation-agentforce-004",
        "requiresHumanApproval": True,
        "inventoryWasteReasoning": {
            "riskType": "STOCKOUT",
            "severity": "Critical",
            "missingEvidence": [],
            "recommendedActions": [
                {
                    "actionId": "action-clean-reorder-review",
                    "actionType": "REORDER_OR_TRANSFER_REVIEW",
                    "statement": "Request manager approval for a reorder or warehouse transfer to cover the promotion gap.",
                    "evidenceIds": [
                        clean_stockout_inventory["evidenceId"],
                        clean_stockout_supplier["evidenceId"],
                    ],
                    "requiresHumanApproval": True,
                }
            ],
            "blockedActions": [],
            "supplierCaution": {
                "applies": False,
                "statement": "No supplier caution applies because supplier history is clean and no complaint cluster is active.",
                "evidenceIds": [
                    clean_stockout_supplier["evidenceId"],
                    clean_stockout_complaints["evidenceId"],
                ],
            },
            "explanation": "Promotion demand creates less than one day of cover. Since supplier and complaint evidence are clean, the recommendation can focus on approved replenishment or transfer rather than quarantine or supplier escalation.",
        },
    }
    clean_stockout_response["audit"] = audit(
        "model-invocation-agentforce-004", True
    )

    expiry_markdown_inventory = citation(
        "a06000000000017AAA",
        "Bakery rolls 6 pack at Port Louis Market has 30 shelf units, 10 backroom units, no warehouse units, no incoming reservations, supplier lead time of 1 day, daily sales velocity of 8 units, and no promotion uplift.",
        "retail:inventory",
        "sha256:04fd86dbfb57c682e85088792cf719069ac7e45c145ae321a4b077a826996377",
    )
    expiry_markdown_batch = citation(
        "a06000000000018AAA",
        "Batch BR-0612 has 34 near-expiry units and expires on 2026-06-12, two days after the 2026-06-10 business date.",
        "retail:expiry",
        "sha256:5466d16857f7d66c57e643b788066d89a2895cd42a7c8f5d02ef0febfda3c26a",
    )
    expiry_markdown_complaints = citation(
        "a06000000000019AAA",
        "No active complaint cluster is linked to the bakery rolls batch, product, store, or supplier.",
        "retail:complaints",
        "sha256:9456a7e0eac8b63f9abb1ed32c3f07a14f0b5b1b84f3ae72737305dcaf33e3cb",
    )
    expiry_markdown_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    expiry_markdown_request["desiredOutcome"] = (
        "Assess near-expiry waste pressure and propose a safe markdown plan."
    )
    expiry_markdown_request["modelProfile"] = (
        "north-star-retail-recommendation"
    )
    expiry_markdown_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    expiry_markdown_response["citations"] = [
        expiry_markdown_inventory,
        expiry_markdown_batch,
        expiry_markdown_complaints,
    ]
    expiry_markdown_response["facts"] = [
        {
            "factId": "fact-expiry-markdown-inventory",
            "statement": expiry_markdown_inventory["summary"],
            "evidenceIds": [expiry_markdown_inventory["evidenceId"]],
        },
        {
            "factId": "fact-expiry-markdown-batch",
            "statement": expiry_markdown_batch["summary"],
            "evidenceIds": [expiry_markdown_batch["evidenceId"]],
        },
        {
            "factId": "fact-expiry-markdown-complaints",
            "statement": expiry_markdown_complaints["summary"],
            "evidenceIds": [expiry_markdown_complaints["evidenceId"]],
        },
    ]
    expiry_markdown_response["inferences"] = [
        {
            "inferenceId": "inference-expiry-markdown-waste",
            "statement": "Available stock is 40 units, adjusted demand is 8 units per day, days of cover is 5 days, expiry days remaining is 2, expected sales before expiry is 16 units, and waste risk is 18 units.",
            "basisFactIds": [
                "fact-expiry-markdown-inventory",
                "fact-expiry-markdown-batch",
            ],
            "confidence": 0.88,
        },
        {
            "inferenceId": "inference-expiry-markdown-action",
            "statement": "High expiry pressure with no complaint cluster supports manager-approved rotation and markdown for safe units, not blind discard.",
            "basisFactIds": [
                "fact-expiry-markdown-batch",
                "fact-expiry-markdown-complaints",
            ],
            "confidence": 0.83,
        },
    ]
    expiry_markdown_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_INVENTORY_WASTE_REASONING",
        "proposedActionType": "APPROVE_MARKDOWN_AND_ROTATION_ACTIONS",
        "rationale": (
            "Treat this as high expiry and waste risk because the batch expires in 2 days and 18 units are unlikely to sell before expiry at current velocity. Recommend manager-approved rotation and markdown for safe units, while blocking unsupported disposal of all stock."
        ),
        "confidence": 0.83,
        "evidenceIds": [
            expiry_markdown_inventory["evidenceId"],
            expiry_markdown_batch["evidenceId"],
            expiry_markdown_complaints["evidenceId"],
        ],
        "modelProfile": "north-star-retail-recommendation",
        "modelInvocationId": "model-invocation-agentforce-006",
        "requiresHumanApproval": True,
        "inventoryWasteReasoning": {
            "riskType": "WASTE",
            "severity": "High",
            "missingEvidence": [],
            "recommendedActions": [
                {
                    "actionId": "action-expiry-markdown",
                    "actionType": "MARKDOWN_AND_ROTATION_REVIEW",
                    "statement": "Request manager approval to rotate and mark down safe near-expiry units before the batch expires.",
                    "evidenceIds": [
                        expiry_markdown_inventory["evidenceId"],
                        expiry_markdown_batch["evidenceId"],
                    ],
                    "requiresHumanApproval": True,
                }
            ],
            "blockedActions": [
                {
                    "actionType": "DISCARD_ALL_STOCK",
                    "reason": "No complaint cluster or safety evidence supports discarding every unit; only expiry-driven markdown or removal at expiry is supported.",
                    "evidenceIds": [
                        expiry_markdown_batch["evidenceId"],
                        expiry_markdown_complaints["evidenceId"],
                    ],
                }
            ],
            "supplierCaution": {
                "applies": False,
                "statement": "Supplier caution does not change the plan because the evidence is expiry pressure without an active complaint cluster.",
                "evidenceIds": [expiry_markdown_complaints["evidenceId"]],
            },
            "explanation": "The batch has two days remaining and expected sales leave 18 units at waste risk. The safe recommendation is approved rotation and markdown for saleable units, while unsupported disposal of all stock is blocked.",
        },
    }
    expiry_markdown_response["audit"] = audit(
        "model-invocation-agentforce-006", True
    )

    overstock_inventory = citation(
        "a06000000000014AAA",
        "Laundry detergent 2 L at Curepipe Market has 96 shelf units, 144 backroom units, 180 warehouse units, no incoming reservations, supplier lead time of 5 days, daily sales velocity of 6 units, and no promotion uplift.",
        "retail:inventory",
        "sha256:f4176a674dc5aaa8b4058f9f586e8041917b49e2aea6a4a30648db852efcc885",
    )
    overstock_space = citation(
        "a06000000000015AAA",
        "The household shelf area is over capacity for laundry detergent, with endcap space requested by another promotion next week.",
        "retail:shelf-space",
        "sha256:a1c0efa24bb52b277547ec3644dd68c78d28a13460b41b264604c2be1a1de7af",
    )
    overstock_supplier = citation(
        "a06000000000016AAA",
        "Supplier history is clean for the household item with no active complaint or quality-risk evidence.",
        "retail:supplier",
        "sha256:9e0aa4519910c535a12fa1a193c33b6134f5643ca3fd33339c56e5aa053317c8",
    )
    overstock_request = base_request("DRAFT_RELATIONSHIP_RECOMMENDATION")
    overstock_request["desiredOutcome"] = (
        "Assess overstock risk for a household product and avoid unnecessary replenishment."
    )
    overstock_request["modelProfile"] = "north-star-retail-recommendation"
    overstock_response = response("DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS")
    overstock_response["citations"] = [
        overstock_inventory,
        overstock_space,
        overstock_supplier,
    ]
    overstock_response["facts"] = [
        {
            "factId": "fact-overstock-inventory",
            "statement": overstock_inventory["summary"],
            "evidenceIds": [overstock_inventory["evidenceId"]],
        },
        {
            "factId": "fact-overstock-space",
            "statement": overstock_space["summary"],
            "evidenceIds": [overstock_space["evidenceId"]],
        },
        {
            "factId": "fact-overstock-supplier",
            "statement": overstock_supplier["summary"],
            "evidenceIds": [overstock_supplier["evidenceId"]],
        },
    ]
    overstock_response["inferences"] = [
        {
            "inferenceId": "inference-overstock-cover",
            "statement": "Available stock is 420 units, adjusted demand is 6 units per day, days of cover is 70 days, and sales at risk over the 5-day lead time is 0 units.",
            "basisFactIds": ["fact-overstock-inventory"],
            "confidence": 0.9,
        },
        {
            "inferenceId": "inference-overstock-action",
            "statement": "The excess cover and shelf pressure support manager-approved transfer or promotion adjustment, not additional reorder.",
            "basisFactIds": [
                "fact-overstock-inventory",
                "fact-overstock-space",
                "fact-overstock-supplier",
            ],
            "confidence": 0.84,
        },
    ]
    overstock_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_INVENTORY_WASTE_REASONING",
        "proposedActionType": "APPROVE_OVERSTOCK_REBALANCING_ACTIONS",
        "rationale": (
            "Treat this as overstock risk because days of cover is 70 days and shelf space is under pressure. Recommend manager-approved transfer to a lower-stock store or promotion adjustment, and block additional reorder until cover falls."
        ),
        "confidence": 0.84,
        "evidenceIds": [
            overstock_inventory["evidenceId"],
            overstock_space["evidenceId"],
            overstock_supplier["evidenceId"],
        ],
        "modelProfile": "north-star-retail-recommendation",
        "modelInvocationId": "model-invocation-agentforce-005",
        "requiresHumanApproval": True,
        "inventoryWasteReasoning": {
            "riskType": "OVERSTOCK",
            "severity": "Medium",
            "missingEvidence": [],
            "recommendedActions": [
                {
                    "actionId": "action-overstock-transfer",
                    "actionType": "TRANSFER_OR_PROMOTION_ADJUSTMENT_REVIEW",
                    "statement": "Request manager approval to transfer excess units or adjust promotion placement before the next endcap change.",
                    "evidenceIds": [
                        overstock_inventory["evidenceId"],
                        overstock_space["evidenceId"],
                    ],
                    "requiresHumanApproval": True,
                }
            ],
            "blockedActions": [
                {
                    "actionType": "ADDITIONAL_REORDER",
                    "reason": "The product already has 70 days of cover, so additional replenishment is unsupported.",
                    "evidenceIds": [overstock_inventory["evidenceId"]],
                }
            ],
            "supplierCaution": {
                "applies": False,
                "statement": "Supplier caution does not change the plan because no active complaint or quality-risk evidence is present.",
                "evidenceIds": [overstock_supplier["evidenceId"]],
            },
            "explanation": "The household item has far more cover than near-term demand requires and shelf space is needed for another promotion. The safe action is an approved transfer or promotion adjustment, while additional reorder is blocked.",
        },
    }
    overstock_response["audit"] = audit(
        "model-invocation-agentforce-005", True
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
            {
                "name": "inventory-waste-missing-expiry-caution",
                "request": missing_expiry_request,
                "response": missing_expiry_response,
            },
            {
                "name": "inventory-waste-clean-stockout",
                "request": clean_stockout_request,
                "response": clean_stockout_response,
            },
            {
                "name": "inventory-waste-near-expiry-markdown",
                "request": expiry_markdown_request,
                "response": expiry_markdown_response,
            },
            {
                "name": "inventory-waste-overstock-household",
                "request": overstock_request,
                "response": overstock_response,
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
