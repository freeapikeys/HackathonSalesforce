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
            "assumption": {
                "type": "object",
                "additionalProperties": False,
                "required": ["assumptionId", "statement", "evidenceIds"],
                "properties": {
                    "assumptionId": key,
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
                    "assumptions",
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
                    "assumptions": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/assumption"},
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
    *,
    purpose: str = "RESOLVE_RETAIL_RISK",
    agent_key: str = "north-star-orchestrator",
) -> dict[str, Any]:
    return {
        "actorUserId": "005000000000001AAA",
        "agentKey": agent_key,
        "purpose": purpose,
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
        "assumptions": [],
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
    *,
    source_event_id: str = "a09000000000001AAA",
) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "sourceEventId": source_event_id,
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

    nexavenu_lead = citation(
        "a06000000000021AAA",
        "Synthetic LiftOps Manufacturing entered through Agentforce webinar, LinkedIn outbound, and MuleSoft landing-page touches with ICP score 72/100.",
        "nexavenu:revenue:lead-source",
        "sha256:15ec846204c98c2dcd963a904d85633b5b0ad3bb7b8d44e4b0582ac3f592f4d9",
        source_event_id="00000000-0000-4000-8000-000000000029",
    )
    nexavenu_education = citation(
        "a06000000000022AAA",
        "Buyer education gaps include missing system inventory, executive decision owner, budget range, and translation from AI ask to process, data, and integration requirements.",
        "nexavenu:revenue:buyer-education",
        "sha256:a79d23357b2e5c0e5f11b9a5f4ea65cffd02971e8229b107896bc55d5672ed3d",
        source_event_id="00000000-0000-4000-8000-000000000030",
    )
    nexavenu_committee = citation(
        "a06000000000023AAA",
        "Champion map identifies operations manager as likely champion, CFO as economic buyer, CIO as technical approver, and executive sponsor plus data owner as missing stakeholders.",
        "nexavenu:revenue:buying-committee",
        "sha256:5c81292ae1d9a73de4219c06a230a31cd3a7d08e0477095edb1b49241dcd46a5",
        source_event_id="00000000-0000-4000-8000-000000000031",
    )
    nexavenu_readiness = citation(
        "a06000000000024AAA",
        "Discovery readiness score is 48/100 and the handoff gate is HOLD until budget owner, current systems list, decision timeline, and success metric are resolved.",
        "nexavenu:revenue:discovery-readiness",
        "sha256:45ffe60a85a761be8db5fae6ca1858ad7ae8786770b100ffb4ef9121ac3bcfe5",
        source_event_id="00000000-0000-4000-8000-000000000032",
    )
    nexavenu_close_plan = citation(
        "a06000000000025AAA",
        "Close plan recommends champion briefing pack, system inventory request, CFO/CIO alignment call after readiness reaches 70, and human approval for external champion email, opportunity stage update, and solution-consultant handoff.",
        "nexavenu:revenue:close-plan",
        "sha256:cc8225815cd95c3a2ddbf4b8571503137a96ca3449d35fe6cf41e1429f05016d",
        source_event_id="00000000-0000-4000-8000-000000000033",
    )
    nexavenu_retention = citation(
        "a06000000000026AAA",
        "Existing synthetic customer risk shows previous-loyalty account with adoption friction, executive dissatisfaction, and missing expansion owner.",
        "nexavenu:revenue:retention-risk",
        "sha256:8733ad175aa9a44fdc16c22bf553e2fecfc2421145b1357e7f0a3132f83bbd67",
        source_event_id="00000000-0000-4000-8000-000000000034",
    )
    nexavenu_outcome = citation(
        "a06000000000027AAA",
        "Outcome fixture shows readiness score increased from 48 to 76, champion replied with system inventory, CFO/CIO alignment call was accepted, handoff was scheduled, and retention review was created.",
        "nexavenu:revenue:outcome",
        "sha256:82a2d3f5e30cbdeb5a48be25c05a822d85101593452e443074a91441cde34644",
        source_event_id="00000000-0000-4000-8000-000000000036",
    )

    nexavenu_request = base_request("DRAFT_RELATIONSHIP_RECOMMENDATION")
    nexavenu_request["purpose"] = "QUALIFY_B2B_REVENUE_PIPELINE"
    nexavenu_request["workItemId"] = "a0E00000000009AAA"
    nexavenu_request["desiredOutcome"] = (
        "Qualify and educate a B2B AI/MuleSoft prospect, build a champion map, protect senior discovery time, and capture retention feedback without executing external actions."
    )
    nexavenu_request["modelProfile"] = "nexavenu-revenue-recommendation"
    nexavenu_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    nexavenu_response["citations"] = [
        nexavenu_lead,
        nexavenu_education,
        nexavenu_committee,
        nexavenu_readiness,
        nexavenu_close_plan,
        nexavenu_retention,
        nexavenu_outcome,
    ]
    nexavenu_response["facts"] = [
        {
            "factId": "fact-nexavenu-icp-score",
            "statement": "Synthetic prospect has ICP score 72/100 from industry fit, integration complexity, executive intent, data readiness, and budget signal.",
            "evidenceIds": [nexavenu_lead["evidenceId"]],
        },
        {
            "factId": "fact-nexavenu-education-gaps",
            "statement": "Buyer education gaps remain around system inventory, decision owner, budget range, and translation from AI interest into process, data, and integration requirements.",
            "evidenceIds": [nexavenu_education["evidenceId"]],
        },
        {
            "factId": "fact-nexavenu-champion-map",
            "statement": "Operations manager is the likely champion; CFO and CIO are high-influence buyers; executive sponsor and data owner are missing.",
            "evidenceIds": [nexavenu_committee["evidenceId"]],
        },
        {
            "factId": "fact-nexavenu-readiness-score",
            "statement": "Discovery readiness score is 48/100 and the handoff gate is HOLD.",
            "evidenceIds": [nexavenu_readiness["evidenceId"]],
        },
        {
            "factId": "fact-nexavenu-retention-risk",
            "statement": "A synthetic existing customer shows adoption friction, executive dissatisfaction, and no named expansion owner after previous loyalty.",
            "evidenceIds": [nexavenu_retention["evidenceId"]],
        },
        {
            "factId": "fact-nexavenu-feedback-loop",
            "statement": "When nurture actions are approved, the synthetic outcome raises readiness to 76, gets champion inventory, accepts CFO/CIO alignment, schedules handoff, and creates retention review.",
            "evidenceIds": [nexavenu_outcome["evidenceId"]],
        },
    ]
    nexavenu_response["assumptions"] = [
        {
            "assumptionId": "assumption-contact-sourced-lead-quality",
            "statement": "Contact-sourced signal suggests lead quality and buyer education are major constraints; treat this as a private diagnostic assumption, not a public claim.",
            "evidenceIds": [
                nexavenu_lead["evidenceId"],
                nexavenu_education["evidenceId"],
            ],
        },
        {
            "assumptionId": "assumption-contact-sourced-discovery-compression",
            "statement": "Contact-sourced signal suggests discovery should be compressed through readiness gates before senior solution-consultant handoff.",
            "evidenceIds": [
                nexavenu_readiness["evidenceId"],
                nexavenu_close_plan["evidenceId"],
            ],
        },
    ]
    nexavenu_response["inferences"] = [
        {
            "inferenceId": "inference-nexavenu-keep-in-nurture",
            "statement": "The prospect is promising but not ready for senior delivery discovery until stakeholder, budget, system inventory, and success metric gaps are resolved.",
            "basisFactIds": [
                "fact-nexavenu-icp-score",
                "fact-nexavenu-education-gaps",
                "fact-nexavenu-champion-map",
                "fact-nexavenu-readiness-score",
            ],
            "confidence": 0.82,
        },
        {
            "inferenceId": "inference-nexavenu-champion-first",
            "statement": "Champion enablement and content sequencing should happen before a CFO/CIO alignment call, because the likely champion needs ROI and integration inventory support.",
            "basisFactIds": [
                "fact-nexavenu-education-gaps",
                "fact-nexavenu-champion-map",
                "fact-nexavenu-readiness-score",
            ],
            "confidence": 0.79,
        },
        {
            "inferenceId": "inference-nexavenu-retention-loop",
            "statement": "Revenue intelligence must cover post-sale first impressions as well as lead nurture because churn risk can appear even after loyal history.",
            "basisFactIds": [
                "fact-nexavenu-retention-risk",
                "fact-nexavenu-feedback-loop",
            ],
            "confidence": 0.78,
        },
    ]
    nexavenu_response["recommendation"] = {
        "recommendationType": "NEXAVENU_REVENUE_INTELLIGENCE_PLAN",
        "proposedActionType": "APPROVE_NEXAVENU_CHAMPION_NURTURE_ACTIONS",
        "rationale": (
            "Keep the lead in nurture until readiness crosses 70, send the AI readiness checklist, MuleSoft modernization explainer, field-service case story, and CFO ROI proof, equip the operations champion with a briefing pack, request system inventory and success metric worksheet, then schedule CFO/CIO alignment. Separately open a retention review for the existing customer signal. External champion email, opportunity stage movement, solution-consultant handoff, and retention outreach require human approval. Expected outcomes are qualified discovery, protected solution-consultant time, champion-equipped CFO/CIO alignment, and early retention recovery."
        ),
        "confidence": 0.83,
        "evidenceIds": [
            nexavenu_lead["evidenceId"],
            nexavenu_education["evidenceId"],
            nexavenu_committee["evidenceId"],
            nexavenu_readiness["evidenceId"],
            nexavenu_close_plan["evidenceId"],
            nexavenu_retention["evidenceId"],
            nexavenu_outcome["evidenceId"],
        ],
        "modelProfile": "nexavenu-revenue-recommendation",
        "modelInvocationId": "model-invocation-agentforce-nexavenu-001",
        "requiresHumanApproval": True,
    }
    nexavenu_response["audit"] = audit(
        "model-invocation-agentforce-nexavenu-001",
        True,
        purpose="QUALIFY_B2B_REVENUE_PIPELINE",
        agent_key="nexavenu-revenue-orchestrator",
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
                "name": "nexavenu-revenue-intelligence-recommendation",
                "request": nexavenu_request,
                "response": nexavenu_response,
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
