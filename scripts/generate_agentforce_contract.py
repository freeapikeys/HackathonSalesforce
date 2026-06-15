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
HOSPITAL_PURPOSE = "RESOLVE_HOSPITAL_OPERATION_RISK"
HOSPITAL_MODEL_PROFILE = "hospital_action_reasoning"
HOSPITAL_APPROVAL_POLICY = "north-star-hospital-manager-approval-v1"


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
                    "evidenceType",
                    "sourceEventId",
                    "sourceUri",
                    "contentHash",
                    "summary",
                    "accessible",
                ],
                "properties": {
                    "evidenceId": identifier,
                    "evidenceType": string(100),
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
            "contextCategory": {
                "type": "object",
                "additionalProperties": False,
                "required": ["applies", "evidenceIds", "recordIds"],
                "properties": {
                    "applies": {"type": "boolean"},
                    "evidenceIds": evidence_id_list(min_items=0),
                    "recordIds": {
                        "type": "array",
                        "items": identifier,
                        "uniqueItems": True,
                    },
                },
            },
            "contextCoverage": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "evidenceIds",
                    "evidenceTypes",
                    "evidenceCategories",
                    "recordIdsByPrimitive",
                ],
                "properties": {
                    "evidenceIds": evidence_id_list(min_items=1),
                    "evidenceTypes": {
                        "type": "array",
                        "items": string(100),
                        "minItems": 1,
                        "uniqueItems": True,
                    },
                    "evidenceCategories": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "complaint",
                            "resource",
                            "capacity",
                            "partner",
                            "billing",
                            "stock",
                            "staffing",
                            "approval",
                            "outcome",
                        ],
                        "properties": {
                            "complaint": {"$ref": "#/$defs/contextCategory"},
                            "resource": {"$ref": "#/$defs/contextCategory"},
                            "capacity": {"$ref": "#/$defs/contextCategory"},
                            "partner": {"$ref": "#/$defs/contextCategory"},
                            "billing": {"$ref": "#/$defs/contextCategory"},
                            "stock": {"$ref": "#/$defs/contextCategory"},
                            "staffing": {"$ref": "#/$defs/contextCategory"},
                            "approval": {"$ref": "#/$defs/contextCategory"},
                            "outcome": {"$ref": "#/$defs/contextCategory"},
                        },
                    },
                    "recordIdsByPrimitive": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "customerAliases",
                            "departments",
                            "locations",
                            "resources",
                            "partners",
                            "processes",
                            "recommendations",
                            "approvals",
                            "actions",
                            "outcomes",
                            "metrics",
                        ],
                        "properties": {
                            "customerAliases": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "departments": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "locations": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "resources": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "partners": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "processes": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "recommendations": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "approvals": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "actions": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "outcomes": {
                                "type": "array",
                                "items": identifier,
                                "uniqueItems": True,
                            },
                            "metrics": {
                                "type": "array",
                                "items": key,
                                "uniqueItems": True,
                            },
                        },
                    },
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
                    "inventoryWasteReasoning": nullable(
                        "#/$defs/inventoryWasteReasoning"
                    ),
                    "hospitalOperationsReasoning": nullable(
                        "#/$defs/hospitalOperationsReasoning"
                    ),
                },
            },
            "calculation": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "metricKey",
                    "formula",
                    "value",
                    "unit",
                    "evidenceIds",
                ],
                "properties": {
                    "metricKey": key,
                    "formula": string(500),
                    "value": {"type": "number"},
                    "unit": string(100),
                    "evidenceIds": evidence_id_list(),
                },
            },
            "recommendedHospitalAction": {
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
            "blockedHospitalAction": {
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
            "clinicalBoundary": {
                "type": "object",
                "additionalProperties": False,
                "required": ["applies", "statement", "evidenceIds"],
                "properties": {
                    "applies": {"type": "boolean"},
                    "statement": string(1000),
                    "evidenceIds": evidence_id_list(min_items=0),
                },
            },
            "partnerCaution": {
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
                    "evidenceIds": evidence_id_list(min_items=0),
                },
            },
            "evidenceQualityFinding": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "findingType",
                    "summary",
                    "action",
                    "evidenceIds",
                ],
                "properties": {
                    "findingType": {
                        "enum": [
                            "MISSING",
                            "CONTRADICTORY",
                            "RESTRICTED",
                            "DUPLICATE",
                            "LATE",
                            "OUT_OF_ORDER",
                            "MALFORMED",
                            "LOW_CONFIDENCE",
                        ]
                    },
                    "summary": string(1000),
                    "action": string(1000),
                    "evidenceIds": evidence_id_list(min_items=0),
                },
            },
            "conflictResolution": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "conflictId",
                    "tension",
                    "resolution",
                    "winningPolicy",
                    "evidenceIds",
                ],
                "properties": {
                    "conflictId": key,
                    "tension": string(1000),
                    "resolution": string(1000),
                    "winningPolicy": string(500),
                    "evidenceIds": evidence_id_list(),
                },
            },
            "recommendationUpdate": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "trigger",
                    "changedByEvidenceId",
                    "before",
                    "after",
                    "decision",
                    "evidenceIds",
                ],
                "properties": {
                    "trigger": string(300),
                    "changedByEvidenceId": identifier,
                    "before": string(1000),
                    "after": string(1000),
                    "decision": string(1000),
                    "evidenceIds": evidence_id_list(),
                },
            },
            "serviceRecoveryDraft": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "draftId",
                    "audience",
                    "message",
                    "approvalRequired",
                    "approvalId",
                    "policyReason",
                    "privacySafe",
                    "evidenceIds",
                ],
                "properties": {
                    "draftId": key,
                    "audience": string(200),
                    "message": string(1200),
                    "approvalRequired": {"const": True},
                    "approvalId": identifier,
                    "policyReason": string(500),
                    "privacySafe": {"const": True},
                    "evidenceIds": evidence_id_list(),
                },
            },
            "approvalDecision": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "decisionState",
                    "approvalId",
                    "actionId",
                    "approverRole",
                    "policyReason",
                    "evidenceIds",
                ],
                "properties": {
                    "decisionState": {
                        "enum": [
                            "APPROVE",
                            "REJECT",
                            "MODIFY",
                            "DEFER",
                            "EXECUTE_READY",
                        ]
                    },
                    "approvalId": identifier,
                    "actionId": key,
                    "approverRole": string(200),
                    "policyReason": string(1000),
                    "evidenceIds": evidence_id_list(min_items=0),
                },
            },
            "financialImpactSummary": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "detectedCaseTypes",
                    "exposureFormula",
                    "exposureValue",
                    "currencyCode",
                    "timeWindow",
                    "confidence",
                    "approvalRequired",
                    "protectedActionTypes",
                    "personalDataPolicy",
                    "evidenceIds",
                ],
                "properties": {
                    "detectedCaseTypes": {
                        "type": "array",
                        "items": key,
                        "minItems": 1,
                        "uniqueItems": True,
                    },
                    "exposureFormula": string(500),
                    "exposureValue": {"type": "number"},
                    "currencyCode": string(10),
                    "timeWindow": string(200),
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "approvalRequired": {"const": True},
                    "protectedActionTypes": {
                        "type": "array",
                        "items": string(100),
                        "minItems": 1,
                        "uniqueItems": True,
                    },
                    "personalDataPolicy": string(500),
                    "evidenceIds": evidence_id_list(),
                },
            },
            "expectedHospitalOutcome": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "metricKey",
                    "target",
                    "timeWindow",
                    "evidenceIds",
                ],
                "properties": {
                    "metricKey": key,
                    "target": string(500),
                    "timeWindow": string(200),
                    "evidenceIds": evidence_id_list(min_items=0),
                },
            },
            "hospitalOperationsReasoning": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "riskType",
                    "severity",
                    "calculations",
                    "assumptions",
                    "missingEvidence",
                    "evidenceQualityFindings",
                    "conflictResolutions",
                    "recommendationUpdates",
                    "recommendedActions",
                    "blockedActions",
                    "partnerCaution",
                    "clinicalBoundary",
                    "serviceRecoveryDraft",
                    "approvalDecisions",
                    "financialImpact",
                    "expectedOutcomes",
                    "explanation",
                ],
                "properties": {
                    "riskType": {
                        "enum": [
                            "CAPACITY",
                            "QUEUE",
                            "STOCK",
                            "SLA",
                            "VENDOR",
                            "BILLING",
                            "COMPLAINT",
                            "CLINICAL_REFUSAL",
                            "MIXED",
                        ]
                    },
                    "severity": {
                        "enum": ["Low", "Medium", "High", "Critical"]
                    },
                    "calculations": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/calculation"},
                    },
                    "assumptions": {
                        "type": "array",
                        "items": string(500),
                        "uniqueItems": True,
                    },
                    "missingEvidence": {
                        "type": "array",
                        "items": string(500),
                        "uniqueItems": True,
                    },
                    "evidenceQualityFindings": {
                        "type": "array",
                        "items": {
                            "$ref": "#/$defs/evidenceQualityFinding"
                        },
                    },
                    "conflictResolutions": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/conflictResolution"},
                    },
                    "recommendationUpdates": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/recommendationUpdate"},
                    },
                    "recommendedActions": {
                        "type": "array",
                        "items": {
                            "$ref": "#/$defs/recommendedHospitalAction"
                        },
                    },
                    "blockedActions": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/blockedHospitalAction"},
                    },
                    "partnerCaution": {"$ref": "#/$defs/partnerCaution"},
                    "clinicalBoundary": {
                        "$ref": "#/$defs/clinicalBoundary"
                    },
                    "serviceRecoveryDraft": nullable(
                        "#/$defs/serviceRecoveryDraft"
                    ),
                    "approvalDecisions": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/approvalDecision"},
                    },
                    "financialImpact": nullable(
                        "#/$defs/financialImpactSummary"
                    ),
                    "expectedOutcomes": {
                        "type": "array",
                        "items": {
                            "$ref": "#/$defs/expectedHospitalOutcome"
                        },
                    },
                    "explanation": string(2000),
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
                    "assumptions",
                    "inferences",
                    "citations",
                    "contextCoverage",
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
                    "contextCoverage": nullable(
                        "#/$defs/contextCoverage"
                    ),
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
        "purpose": HOSPITAL_PURPOSE,
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
    purpose: str = HOSPITAL_PURPOSE,
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
        "contextCoverage": None,
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
    evidence_type: str = "SOURCE_EVENT",
    *,
    source_event_id: str = "a09000000000001AAA",
) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "evidenceType": evidence_type,
        "sourceEventId": source_event_id,
        "sourceUri": f"urn:hfs:source:{suffix}",
        "contentHash": content_hash,
        "summary": summary,
        "accessible": True,
    }


def coverage_category(
    evidence_ids: list[str] | None = None,
    record_ids: list[str] | None = None,
) -> dict[str, Any]:
    safe_evidence_ids = evidence_ids or []
    safe_record_ids = record_ids or []
    return {
        "applies": bool(safe_evidence_ids or safe_record_ids),
        "evidenceIds": safe_evidence_ids,
        "recordIds": safe_record_ids,
    }


def context_coverage(
    citations: list[dict[str, Any]],
    evidence_categories: dict[str, list[str]],
    records_by_primitive: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    records = {
        "customerAliases": [],
        "departments": [],
        "locations": [],
        "resources": [],
        "partners": [],
        "processes": [],
        "recommendations": [],
        "approvals": [],
        "actions": [],
        "outcomes": [],
        "metrics": [],
        **(records_by_primitive or {}),
    }
    categories = {
        "complaint": coverage_category(evidence_categories.get("complaint")),
        "resource": coverage_category(
            evidence_categories.get("resource"), records["resources"]
        ),
        "capacity": coverage_category(
            evidence_categories.get("capacity"), records["resources"]
        ),
        "partner": coverage_category(
            evidence_categories.get("partner"), records["partners"]
        ),
        "billing": coverage_category(
            evidence_categories.get("billing"), records["processes"]
        ),
        "stock": coverage_category(
            evidence_categories.get("stock"), records["resources"]
        ),
        "staffing": coverage_category(evidence_categories.get("staffing")),
        "approval": coverage_category(
            evidence_categories.get("approval"), records["approvals"]
        ),
        "outcome": coverage_category(record_ids=records["outcomes"]),
    }
    return {
        "evidenceIds": [value["evidenceId"] for value in citations],
        "evidenceTypes": sorted(
            {value["evidenceType"] for value in citations}
        ),
        "evidenceCategories": categories,
        "recordIdsByPrimitive": records,
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
            "inferenceId": "inference-action-plan",
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

    hospital_complaint = citation(
        "a06000000000021AAA",
        "Eleven synthetic patient and visitor complaints mention wait time, room readiness, billing delay, and pharmacy delay in the morning surge window.",
        "hospital:complaints",
        "sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f",
        "PATIENT_COMPLAINT_CLUSTER",
    )
    hospital_capacity = citation(
        "a06000000000022AAA",
        "Ward A3 has eighteen discharge rooms, six ready rooms, seven blocked rooms, a seventy-four minute outpatient queue wait against a thirty-five minute target, and four of six front-desk support staff available.",
        "hospital:capacity",
        "sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb",
        "RESOURCE_CAPACITY",
    )
    hospital_pharmacy = citation(
        "a06000000000023AAA",
        "Pharmacy IV kit cover is 2.4 hours against a four-hour operational threshold before the afternoon demand window.",
        "hospital:pharmacy",
        "sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588",
        "PHARMACY_STOCK_POSITION",
    )
    hospital_partner = citation(
        "a06000000000024AAA",
        "Island Diagnostics is forty-two minutes over the routine acknowledgement SLA; a second courier route is available after approval.",
        "hospital:partner",
        "sha256:f42d186a12981c8c7a25b7be50f5f95541e4323f83f3f3c65de8e20717b5e6ea",
        "PARTNER_RESPONSE_STATUS",
    )
    hospital_billing = citation(
        "a06000000000025AAA",
        "Three duplicate invoice reviews, two insurer follow-ups, one refund request, one voucher request, one payment gateway issue, and one revenue-risk hold need manager approval.",
        "hospital:billing",
        "sha256:1b7c5f38159d8e86f0a1e9e00f27acfc4f9657cdcfb30fc4a7c383563e826355",
        "BILLING_AND_INSURANCE_HOLD",
    )
    hospital_staffing = citation(
        "a06000000000026AAA",
        "Two front-desk staff are unavailable, porter coverage is delayed, and the outpatient queue needs role-owned task coordination.",
        "hospital:staffing",
        "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "STAFF_QUEUE_RISK",
    )
    hospital_clinical = citation(
        "a06000000000027AAA",
        "A request asking which patient should receive treatment first is refused by North Star and routed to clinician review.",
        "hospital:clinical-boundary",
        "sha256:a4da995bc39a2a89d45bc28398c12edc8af4f895449fffc8f54195baee4b9d5e",
        "CLINICAL_DECISION_REFUSAL",
    )

    hospital_request = base_request("DRAFT_RELATIONSHIP_RECOMMENDATION")
    hospital_request["desiredOutcome"] = (
        "Coordinate a non-clinical hospital operations action plan for the "
        "morning surge without bypassing manager approval."
    )
    hospital_request["modelProfile"] = HOSPITAL_MODEL_PROFILE
    hospital_response = response("DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS")
    hospital_response["citations"] = [
        hospital_complaint,
        hospital_capacity,
        hospital_pharmacy,
        hospital_partner,
        hospital_billing,
        hospital_staffing,
        hospital_clinical,
    ]
    hospital_response["facts"] = [
        {
            "factId": "fact-hospital-complaints",
            "statement": hospital_complaint["summary"],
            "evidenceIds": [hospital_complaint["evidenceId"]],
        },
        {
            "factId": "fact-hospital-capacity",
            "statement": hospital_capacity["summary"],
            "evidenceIds": [hospital_capacity["evidenceId"]],
        },
        {
            "factId": "fact-hospital-pharmacy",
            "statement": hospital_pharmacy["summary"],
            "evidenceIds": [hospital_pharmacy["evidenceId"]],
        },
        {
            "factId": "fact-hospital-partner",
            "statement": hospital_partner["summary"],
            "evidenceIds": [hospital_partner["evidenceId"]],
        },
        {
            "factId": "fact-hospital-billing",
            "statement": hospital_billing["summary"],
            "evidenceIds": [hospital_billing["evidenceId"]],
        },
        {
            "factId": "fact-hospital-staffing",
            "statement": hospital_staffing["summary"],
            "evidenceIds": [hospital_staffing["evidenceId"]],
        },
        {
            "factId": "fact-hospital-clinical-refusal",
            "statement": hospital_clinical["summary"],
            "evidenceIds": [hospital_clinical["evidenceId"]],
        },
    ]
    hospital_response["inferences"] = [
        {
            "inferenceId": "inference-hospital-capacity-pressure",
            "statement": "Available discharge-room capacity is six rooms, demand pressure is 3.0, queue load is 2.11 against target, and the lab partner delay creates SLA risk.",
            "basisFactIds": [
                "fact-hospital-capacity",
                "fact-hospital-partner",
            ],
            "confidence": 0.89,
        },
        {
            "inferenceId": "inference-hospital-cross-functional-plan",
            "statement": "The complaint cluster affects customer trust, bed release, pharmacy stock, partner escalation, billing, communications, and outcome tracking; it should become one approved operations plan.",
            "basisFactIds": [
                "fact-hospital-complaints",
                "fact-hospital-capacity",
                "fact-hospital-pharmacy",
                "fact-hospital-partner",
                "fact-hospital-billing",
                "fact-hospital-staffing",
            ],
            "confidence": 0.88,
        },
    ]
    hospital_response["contextCoverage"] = context_coverage(
        hospital_response["citations"],
        {
            "complaint": [hospital_complaint["evidenceId"]],
            "resource": [hospital_capacity["evidenceId"]],
            "capacity": [hospital_capacity["evidenceId"]],
            "partner": [hospital_partner["evidenceId"]],
            "billing": [hospital_billing["evidenceId"]],
            "stock": [hospital_pharmacy["evidenceId"]],
            "staffing": [hospital_staffing["evidenceId"]],
            "approval": [
                hospital_partner["evidenceId"],
                hospital_billing["evidenceId"],
            ],
        },
        {
            "customerAliases": ["a01000000000007AAA"],
            "departments": ["a01000000000002AAA"],
            "locations": ["a01000000000002AAA"],
            "resources": ["a01000000000003AAA", "a01000000000004AAA"],
            "partners": ["a01000000000005AAA"],
            "processes": ["a01000000000006AAA"],
            "recommendations": ["a07000000000021AAA"],
            "approvals": ["a08000000000021AAA"],
        },
    )
    hospital_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_HOSPITAL_ACTION_PLAN",
        "proposedActionType": "APPROVE_HOSPITAL_ACTIONS",
        "rationale": (
            "Approve room-cleaning and porter tasks, pharmacy restock or "
            "transfer, lab vendor escalation, billing and insurance review, "
            "privacy-safe Slack/WhatsApp internal alerts, and outcome capture. "
            "Refuse diagnosis, treatment, dosage, triage, and clinical "
            "priority decisions."
        ),
        "confidence": 0.88,
        "evidenceIds": [
            hospital_complaint["evidenceId"],
            hospital_capacity["evidenceId"],
            hospital_pharmacy["evidenceId"],
            hospital_partner["evidenceId"],
            hospital_billing["evidenceId"],
            hospital_staffing["evidenceId"],
            hospital_clinical["evidenceId"],
        ],
        "modelProfile": HOSPITAL_MODEL_PROFILE,
        "modelInvocationId": "model-invocation-agentforce-hospital-001",
        "requiresHumanApproval": True,
        "hospitalOperationsReasoning": {
            "riskType": "MIXED",
            "severity": "High",
            "calculations": [
                {
                    "metricKey": "available_room_capacity",
                    "formula": "totalRooms - blockedRooms - reservedRooms",
                    "value": 6,
                    "unit": "rooms",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "metricKey": "demand_pressure",
                    "formula": "expectedDemand / max(1, availableCapacity)",
                    "value": 3.0,
                    "unit": "ratio",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "metricKey": "queue_load_against_target",
                    "formula": "currentWaitMinutes / max(1, targetWaitMinutes)",
                    "value": 2.11,
                    "unit": "ratio",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "metricKey": "stock_cover_hours",
                    "formula": "availableStock / max(1, averageHourlyUsage)",
                    "value": 2.4,
                    "unit": "hours",
                    "evidenceIds": [hospital_pharmacy["evidenceId"]],
                },
                {
                    "metricKey": "partner_sla_delay_minutes",
                    "formula": "observedDelayMinutes - allowedDelayMinutes",
                    "value": 42,
                    "unit": "minutes",
                    "evidenceIds": [hospital_partner["evidenceId"]],
                },
                {
                    "metricKey": "staff_coverage_gap",
                    "formula": "requiredStaff - availableStaff",
                    "value": 2,
                    "unit": "staff",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "metricKey": "financial_exposure_estimate",
                    "formula": "duplicateInvoiceCases*2500 + claimPendingCases*10000 + refundCompensationVoucherCases*25000 + paymentGatewayIssues*10000 + revenueRiskCases*30000",
                    "value": 142500,
                    "unit": "MUR",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                },
            ],
            "assumptions": [
                "Manager approval is required before external alerts, vendor escalation, pharmacy restock, billing review, or staff tasks execute.",
                "The plan coordinates only non-clinical operations and does not prioritize treatment.",
                "Synthetic hospital fixtures contain no patient personal data.",
            ],
            "missingEvidence": [],
            "evidenceQualityFindings": [
                {
                    "findingType": "MISSING",
                    "summary": "Outcome evidence is not available until approved actions execute.",
                    "action": "Track outcome callbacks after manager approval and do not claim final impact early.",
                    "evidenceIds": [],
                },
                {
                    "findingType": "CONTRADICTORY",
                    "summary": "Patient trust asks for a quick service response while capacity evidence shows discharge rooms are still blocked.",
                    "action": "Send only approved internal updates now and delay room-release claims until cleaning and porter acknowledgements arrive.",
                    "evidenceIds": [
                        hospital_complaint["evidenceId"],
                        hospital_capacity["evidenceId"],
                    ],
                },
                {
                    "findingType": "RESTRICTED",
                    "summary": "Clinical priority evidence is restricted to clinicians and cannot be used for automated treatment decisions.",
                    "action": "Refuse clinical decisions and route the matter to clinician review.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                },
                {
                    "findingType": "DUPLICATE",
                    "summary": "Duplicate invoice reviews are present in billing evidence and must be reviewed before refunds or compensation.",
                    "action": "Open billing review instead of issuing automatic refund or voucher decisions.",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                },
                {
                    "findingType": "LATE",
                    "summary": "The lab partner acknowledgement is forty-two minutes late against the operational SLA.",
                    "action": "Escalate the partner case only through an approved vendor follow-up.",
                    "evidenceIds": [hospital_partner["evidenceId"]],
                },
                {
                    "findingType": "OUT_OF_ORDER",
                    "summary": "Capacity and partner responses may arrive after the first recommendation.",
                    "action": "Recompute the recommendation when late capacity or partner evidence changes the safe action set.",
                    "evidenceIds": [
                        hospital_capacity["evidenceId"],
                        hospital_partner["evidenceId"],
                    ],
                },
                {
                    "findingType": "MALFORMED",
                    "summary": "Malformed event fixtures are rejected before they can become recommendation facts.",
                    "action": "Keep malformed evidence out of facts and preserve the validation failure in the intake audit.",
                    "evidenceIds": [],
                },
                {
                    "findingType": "LOW_CONFIDENCE",
                    "summary": "Staff coverage is lower confidence until role-owner acknowledgements return.",
                    "action": "Create role-owned tasks with acknowledgement tracking instead of claiming staffing is fixed.",
                    "evidenceIds": [hospital_staffing["evidenceId"]],
                },
            ],
            "conflictResolutions": [
                {
                    "conflictId": "conflict-patient-trust-capacity",
                    "tension": "Customer Trust wants a quick service response, but Resource and Capacity shows rooms are still blocked.",
                    "resolution": "Approve privacy-safe updates and service tasks now; release rooms only after housekeeping and porter acknowledgements.",
                    "winningPolicy": "Operational safety and evidence-backed capacity claims override speed-only messaging.",
                    "evidenceIds": [
                        hospital_complaint["evidenceId"],
                        hospital_capacity["evidenceId"],
                    ],
                },
                {
                    "conflictId": "conflict-finance-stock-action-plan",
                    "tension": "Pharmacy restock, refund, voucher, and billing work all compete for manager attention during the surge.",
                    "resolution": "Bundle stock, billing, insurer, voucher, and payment actions under one approval so the manager sees the full exposure.",
                    "winningPolicy": "Protected financial and inventory actions require manager approval before execution.",
                    "evidenceIds": [
                        hospital_pharmacy["evidenceId"],
                        hospital_billing["evidenceId"],
                    ],
                },
                {
                    "conflictId": "conflict-clinical-boundary",
                    "tension": "The fastest-sounding request asks which patient should receive treatment first.",
                    "resolution": "Refuse clinical priority decisions and route them to clinicians while North Star continues non-clinical operations coordination.",
                    "winningPolicy": "Clinical safety boundary overrides operational optimization.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                },
            ],
            "recommendationUpdates": [
                {
                    "trigger": "Partner response arrived after the first recommendation.",
                    "changedByEvidenceId": hospital_partner["evidenceId"],
                    "before": "Keep lab escalation pending and name missing partner response evidence.",
                    "after": "Escalate the SLA and request the second courier route only after approval.",
                    "decision": "Partner evidence narrows the plan from generic follow-up to approved SLA escalation.",
                    "evidenceIds": [hospital_partner["evidenceId"]],
                },
                {
                    "trigger": "Capacity evidence qualified the complaint cluster.",
                    "changedByEvidenceId": hospital_capacity["evidenceId"],
                    "before": "Treat complaints as patient-trust messages only.",
                    "after": "Tie complaints to blocked rooms, queue pressure, staff tasks, pharmacy cover, billing exposure, and outcomes.",
                    "decision": "Capacity evidence expands one complaint cluster into a cross-functional action plan.",
                    "evidenceIds": [
                        hospital_complaint["evidenceId"],
                        hospital_capacity["evidenceId"],
                    ],
                },
                {
                    "trigger": "Billing and payment evidence changed the financial risk.",
                    "changedByEvidenceId": hospital_billing["evidenceId"],
                    "before": "Open a simple billing review.",
                    "after": "Estimate exposure and route refund, voucher, compensation, payment, and insurer follow-up through approval.",
                    "decision": "Financial evidence prevents automatic compensation and makes the exposure visible.",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                },
            ],
            "recommendedActions": [
                {
                    "actionId": "action-room-cleaning",
                    "actionType": "REQUEST_BED_CLEANING",
                    "statement": "Request manager approval to release blocked discharge rooms through housekeeping and porter tasks.",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-porter-support",
                    "actionType": "REQUEST_PORTER_SUPPORT_TASK",
                    "statement": "Dispatch porter support so cleaned discharge rooms can actually return to capacity.",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-staff-support",
                    "actionType": "CREATE_PATIENT_SERVICE_TASK",
                    "statement": "Create an approved front-desk support task to reduce the outpatient queue without making clinical triage decisions.",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-front-desk-queue",
                    "actionType": "OPEN_FRONT_DESK_QUEUE_TASK",
                    "statement": "Open a front-desk queue support task for reception load balancing and patient-safe updates.",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-pharmacy-restock",
                    "actionType": "CREATE_PHARMACY_RESTOCK_REQUEST",
                    "statement": "Request approved restock or transfer for IV kit cover before the afternoon demand window.",
                    "evidenceIds": [hospital_pharmacy["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-lab-escalation",
                    "actionType": "ESCALATE_LAB_VENDOR_CASE",
                    "statement": "Escalate Island Diagnostics response delay and request the available second courier route.",
                    "evidenceIds": [hospital_partner["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-billing-review",
                    "actionType": "OPEN_BILLING_REVIEW",
                    "statement": "Open duplicate invoice and insurer follow-up review before refund or compensation decisions.",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-insurance-followup",
                    "actionType": "REQUEST_INSURANCE_FOLLOWUP",
                    "statement": "Request insurer follow-up for stuck claim approvals before revenue-risk or refund decisions.",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-service-response-message",
                    "actionType": "CREATE_PATIENT_SERVICE_TASK",
                    "statement": "Draft a privacy-safe service response message for manager approval, without clinical advice or personal data.",
                    "evidenceIds": [
                        hospital_complaint["evidenceId"],
                        hospital_billing["evidenceId"],
                    ],
                    "requiresHumanApproval": True,
                },
                {
                    "actionId": "action-manager-review",
                    "actionType": "CREATE_MANAGER_REVIEW_TASK",
                    "statement": "Create the operations manager review task that keeps the action plan approved, auditable, and time-boxed.",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                    "requiresHumanApproval": True,
                },
            ],
            "blockedActions": [
                {
                    "actionType": "CLINICAL_TRIAGE_DECISION",
                    "reason": "North Star cannot decide diagnosis, treatment, dosage, triage, or clinical priority.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                }
            ],
            "partnerCaution": {
                "applies": True,
                "statement": "The lab partner delay changes the plan: North Star should escalate the SLA and request the second courier route only after approval.",
                "evidenceIds": [hospital_partner["evidenceId"]],
            },
            "clinicalBoundary": {
                "applies": True,
                "statement": "Clinical decisions are refused and routed to clinician review; only operations coordination is recommended.",
                "evidenceIds": [hospital_clinical["evidenceId"]],
            },
            "serviceRecoveryDraft": {
                "draftId": "draft-service-response-hospital-surge",
                "audience": "Patient and visitor service desk",
                "message": "We are coordinating outpatient queue support, room-readiness work, pharmacy stock support, and billing follow-up. A hospital operations manager is reviewing the protected actions, and clinical questions will be handled by clinical staff.",
                "approvalRequired": True,
                "approvalId": "a08000000000021AAA",
                "policyReason": "Patient-facing service messages are protected because they may affect trust, refunds, billing, and clinical-boundary wording.",
                "privacySafe": True,
                "evidenceIds": [
                    hospital_complaint["evidenceId"],
                    hospital_billing["evidenceId"],
                    hospital_clinical["evidenceId"],
                ],
            },
            "approvalDecisions": [
                {
                    "decisionState": "APPROVE",
                    "approvalId": "a08000000000021AAA",
                    "actionId": "action-room-cleaning",
                    "approverRole": "Operations Manager",
                    "policyReason": "Room-release tasks are protected write-backs and need manager approval before execution.",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "decisionState": "REJECT",
                    "approvalId": "a08000000000021AAA",
                    "actionId": "action-clinical-triage",
                    "approverRole": "Clinical Manager",
                    "policyReason": "North Star must not approve diagnosis, treatment, dosage, triage, or clinical-priority decisions.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                },
                {
                    "decisionState": "MODIFY",
                    "approvalId": "a08000000000021AAA",
                    "actionId": "action-service-response-message",
                    "approverRole": "Patient Experience Manager",
                    "policyReason": "Patient-facing wording must remain privacy-safe and avoid clinical advice before it can be sent.",
                    "evidenceIds": [
                        hospital_complaint["evidenceId"],
                        hospital_clinical["evidenceId"],
                    ],
                },
                {
                    "decisionState": "DEFER",
                    "approvalId": "a08000000000021AAA",
                    "actionId": "action-refund-voucher-compensation",
                    "approverRole": "Billing Supervisor",
                    "policyReason": "Refund, voucher, and compensation decisions wait for billing and insurer evidence.",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                },
                {
                    "decisionState": "EXECUTE_READY",
                    "approvalId": "a08000000000021AAA",
                    "actionId": "action-lab-escalation",
                    "approverRole": "Operations Manager",
                    "policyReason": "Vendor escalation is ready only after approval preserves the SLA evidence and action ID.",
                    "evidenceIds": [hospital_partner["evidenceId"]],
                },
            ],
            "financialImpact": {
                "detectedCaseTypes": [
                    "duplicate_invoice",
                    "claim_pending",
                    "refund_request",
                    "voucher_request",
                    "compensation_review",
                    "payment_failure",
                    "revenue_risk",
                ],
                "exposureFormula": "duplicateInvoiceCases*2500 + claimPendingCases*10000 + refundCompensationVoucherCases*25000 + paymentGatewayIssues*10000 + revenueRiskCases*30000",
                "exposureValue": 142500,
                "currencyCode": "MUR",
                "timeWindow": "Morning surge through same-day billing cutoff",
                "confidence": 0.82,
                "approvalRequired": True,
                "protectedActionTypes": [
                    "OPEN_BILLING_REVIEW",
                    "REQUEST_INSURANCE_FOLLOWUP",
                    "REFUND_OR_VOUCHER_DECISION",
                    "PAYMENT_GATEWAY_REVIEW",
                    "REVENUE_RISK_ESCALATION",
                ],
                "personalDataPolicy": "Use synthetic aliases and evidence IDs only; no patient, insurer, payment-card, phone, email, or medical-record data.",
                "evidenceIds": [hospital_billing["evidenceId"]],
            },
            "expectedOutcomes": [
                {
                    "metricKey": "outpatient_wait_time_minutes",
                    "target": "Reduce queue wait from 74 minutes toward the 35 minute target.",
                    "timeWindow": "Within the current morning surge window",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "metricKey": "rooms_released",
                    "target": "Release at least three blocked discharge rooms.",
                    "timeWindow": "Within 90 minutes after manager approval",
                    "evidenceIds": [hospital_capacity["evidenceId"]],
                },
                {
                    "metricKey": "pharmacy_stock_cover_hours",
                    "target": "Restore IV kit cover to at least four operational hours.",
                    "timeWindow": "Before the afternoon demand window",
                    "evidenceIds": [hospital_pharmacy["evidenceId"]],
                },
                {
                    "metricKey": "lab_partner_acknowledgement",
                    "target": "Receive lab partner acknowledgement or approved alternate courier response.",
                    "timeWindow": "Within 20 minutes of escalation",
                    "evidenceIds": [hospital_partner["evidenceId"]],
                },
                {
                    "metricKey": "financial_exposure_contained",
                    "target": "Route refund, voucher, compensation, payment, insurer, and revenue-risk decisions through approval.",
                    "timeWindow": "Before same-day billing cutoff",
                    "evidenceIds": [hospital_billing["evidenceId"]],
                },
            ],
            "explanation": "The hospital surge is cross-functional: complaints are rising, rooms are blocked, stock cover is low, a partner SLA is late, and billing approvals are stuck. The safe next step is one manager-approved operations action plan with clinical decisions refused.",
        },
    }
    hospital_response["audit"] = audit(
        "model-invocation-agentforce-hospital-001", True
    )

    missing_capacity_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    missing_capacity_request["desiredOutcome"] = (
        "Assess outpatient queue risk when capacity evidence is missing."
    )
    missing_capacity_request["modelProfile"] = HOSPITAL_MODEL_PROFILE
    missing_capacity_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    missing_capacity_response["citations"] = [
        hospital_complaint,
        hospital_pharmacy,
    ]
    missing_capacity_response["facts"] = [
        {
            "factId": "fact-missing-capacity-complaints",
            "statement": hospital_complaint["summary"],
            "evidenceIds": [hospital_complaint["evidenceId"]],
        },
        {
            "factId": "fact-missing-capacity-pharmacy",
            "statement": hospital_pharmacy["summary"],
            "evidenceIds": [hospital_pharmacy["evidenceId"]],
        },
    ]
    missing_capacity_response["inferences"] = [
        {
            "inferenceId": "inference-missing-capacity-caution",
            "statement": "North Star can identify customer trust and stock risk, but should not claim bed-release or staffing impact without current capacity evidence.",
            "basisFactIds": [
                "fact-missing-capacity-complaints",
                "fact-missing-capacity-pharmacy",
            ],
            "confidence": 0.68,
        }
    ]
    missing_capacity_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_HOSPITAL_CAUTIONED_PLAN",
        "proposedActionType": "REQUEST_MISSING_CAPACITY_EVIDENCE",
        "rationale": (
            "Ask for current bed, room, queue, and staffing evidence before "
            "claiming a capacity action plan. Continue pharmacy restock "
            "review and customer trust monitoring behind approval."
        ),
        "confidence": 0.68,
        "evidenceIds": [
            hospital_complaint["evidenceId"],
            hospital_pharmacy["evidenceId"],
        ],
        "modelProfile": HOSPITAL_MODEL_PROFILE,
        "modelInvocationId": "model-invocation-agentforce-hospital-002",
        "requiresHumanApproval": True,
        "hospitalOperationsReasoning": {
            "riskType": "MIXED",
            "severity": "Medium",
            "calculations": [
                {
                    "metricKey": "stock_cover_hours",
                    "formula": "availableStock / max(1, averageHourlyUsage)",
                    "value": 2.4,
                    "unit": "hours",
                    "evidenceIds": [hospital_pharmacy["evidenceId"]],
                }
            ],
            "assumptions": [
                "Pharmacy usage evidence is current enough for a cautious stock-risk statement.",
                "Capacity impact cannot be quantified until current room, queue, and staffing evidence arrives.",
            ],
            "missingEvidence": [
                "Current ready rooms",
                "Blocked discharge rooms",
                "Outpatient waiting count",
                "Available staff by role",
            ],
            "evidenceQualityFindings": [
                {
                    "findingType": "MISSING",
                    "summary": "Current capacity, queue, and staffing evidence is missing.",
                    "action": "Request operational evidence before claiming bed-release or staffing impact.",
                    "evidenceIds": [hospital_complaint["evidenceId"]],
                }
            ],
            "conflictResolutions": [],
            "recommendationUpdates": [],
            "recommendedActions": [
                {
                    "actionId": "action-request-capacity-evidence",
                    "actionType": "REQUEST_CAPACITY_EVIDENCE",
                    "statement": "Ask bed management and outpatient reception for current capacity and staffing evidence.",
                    "evidenceIds": [hospital_complaint["evidenceId"]],
                    "requiresHumanApproval": True,
                }
            ],
            "blockedActions": [
                {
                    "actionType": "CLAIM_BED_RELEASE_IMPACT",
                    "reason": "Current capacity evidence is missing, so North Star cannot quantify bed-release impact.",
                    "evidenceIds": [hospital_complaint["evidenceId"]],
                }
            ],
            "partnerCaution": {
                "applies": False,
                "statement": "No partner SLA evidence was provided for this cautious scenario.",
                "evidenceIds": [],
            },
            "clinicalBoundary": {
                "applies": False,
                "statement": "No clinical decision was requested in this missing-evidence scenario.",
                "evidenceIds": [],
            },
            "serviceRecoveryDraft": None,
            "approvalDecisions": [],
            "financialImpact": None,
            "expectedOutcomes": [
                {
                    "metricKey": "capacity_evidence_received",
                    "target": "Receive current room, queue, and staffing evidence before claiming bed-release impact.",
                    "timeWindow": "Within 15 minutes",
                    "evidenceIds": [hospital_complaint["evidenceId"]],
                }
            ],
            "explanation": "The cautious path names missing capacity evidence instead of inventing it, while still preserving complaint and pharmacy facts.",
        },
    }
    missing_capacity_response["audit"] = audit(
        "model-invocation-agentforce-hospital-002", True
    )

    clinical_refusal_request = base_request(
        "DRAFT_RELATIONSHIP_RECOMMENDATION"
    )
    clinical_refusal_request["desiredOutcome"] = (
        "Answer which patient should receive treatment first."
    )
    clinical_refusal_request["modelProfile"] = HOSPITAL_MODEL_PROFILE
    clinical_refusal_response = response(
        "DRAFT_RELATIONSHIP_RECOMMENDATION", "SUCCESS"
    )
    clinical_refusal_response["citations"] = [hospital_clinical]
    clinical_refusal_response["facts"] = [
        {
            "factId": "fact-clinical-refusal",
            "statement": hospital_clinical["summary"],
            "evidenceIds": [hospital_clinical["evidenceId"]],
        }
    ]
    clinical_refusal_response["inferences"] = [
        {
            "inferenceId": "inference-clinical-refusal",
            "statement": "The request asks for clinical priority, so North Star must refuse the decision and route to clinician review.",
            "basisFactIds": ["fact-clinical-refusal"],
            "confidence": 0.99,
        }
    ]
    clinical_refusal_response["recommendation"] = {
        "recommendationType": "NORTH_STAR_CLINICAL_DECISION_REFUSAL",
        "proposedActionType": "ROUTE_TO_CLINICIAN_REVIEW",
        "rationale": (
            "Refuse the clinical priority decision. North Star may coordinate "
            "non-clinical queue, room, staff, and communication tasks, but "
            "must route treatment priority to a clinician."
        ),
        "confidence": 0.99,
        "evidenceIds": [hospital_clinical["evidenceId"]],
        "modelProfile": HOSPITAL_MODEL_PROFILE,
        "modelInvocationId": "model-invocation-agentforce-hospital-003",
        "requiresHumanApproval": True,
        "hospitalOperationsReasoning": {
            "riskType": "CLINICAL_REFUSAL",
            "severity": "Critical",
            "calculations": [],
            "assumptions": [
                "The user request asks for clinical treatment priority, which is outside North Star's authority.",
            ],
            "missingEvidence": [],
            "evidenceQualityFindings": [
                {
                    "findingType": "RESTRICTED",
                    "summary": "Clinical priority evidence is restricted to clinicians and cannot be used for automated decisions.",
                    "action": "Refuse the clinical decision and route the request to clinician review.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                }
            ],
            "conflictResolutions": [
                {
                    "conflictId": "conflict-clinical-priority-request",
                    "tension": "The user asks North Star to optimize treatment priority.",
                    "resolution": "North Star refuses the clinical decision and keeps only non-clinical operations support in scope.",
                    "winningPolicy": "Clinical safety boundary overrides operational speed.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                }
            ],
            "recommendationUpdates": [],
            "recommendedActions": [
                {
                    "actionId": "action-route-clinician-review",
                    "actionType": "ROUTE_TO_CLINICIAN_REVIEW",
                    "statement": "Route the clinical-priority request to a clinician or clinical manager.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                    "requiresHumanApproval": True,
                }
            ],
            "blockedActions": [
                {
                    "actionType": "DECIDE_TREATMENT_PRIORITY",
                    "reason": "Automated diagnosis, treatment, dosage, triage, or clinical-priority decisions are out of scope.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                }
            ],
            "partnerCaution": {
                "applies": False,
                "statement": "Partner evidence is not relevant because the requested decision is clinical.",
                "evidenceIds": [],
            },
            "clinicalBoundary": {
                "applies": True,
                "statement": "North Star refuses clinical priority decisions and routes to human clinical review.",
                "evidenceIds": [hospital_clinical["evidenceId"]],
            },
            "serviceRecoveryDraft": None,
            "approvalDecisions": [
                {
                    "decisionState": "REJECT",
                    "approvalId": "a08000000000022AAA",
                    "actionId": "action-decide-treatment-priority",
                    "approverRole": "Clinical Manager",
                    "policyReason": "Automated clinical-priority decisions are outside North Star scope.",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                }
            ],
            "financialImpact": None,
            "expectedOutcomes": [
                {
                    "metricKey": "clinical_review_routed",
                    "target": "Route the clinical-priority request to a clinician without automated treatment prioritization.",
                    "timeWindow": "Immediately",
                    "evidenceIds": [hospital_clinical["evidenceId"]],
                }
            ],
            "explanation": "This scenario proves the boundary: the agent can coordinate operations but cannot decide who receives treatment first.",
        },
    }
    clinical_refusal_response["audit"] = audit(
        "model-invocation-agentforce-hospital-003", True
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
                    "Read permission-aware North Star operations context, "
                    "separate facts from inference, and return accessible "
                    "citations."
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
                    "Draft an evidence-backed operations recommendation "
                    "through the qualified model gateway without executing an "
                    "action."
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
                    "North Star recommendation. Never execute the protected "
                    "action."
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
            {
                "name": "hospital-operations-action-plan",
                "request": hospital_request,
                "response": hospital_response,
            },
            {
                "name": "hospital-missing-capacity-evidence",
                "request": missing_capacity_request,
                "response": missing_capacity_response,
            },
            {
                "name": "hospital-clinical-refusal",
                "request": clinical_refusal_request,
                "response": clinical_refusal_response,
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
