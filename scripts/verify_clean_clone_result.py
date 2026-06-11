#!/usr/bin/env python3

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


SCHEMA_VERSION = "1.0.0"
REQUIRED_STEPS = [
    "tools",
    "salesforce-org",
    "local-contracts",
    "reset",
    "seed",
    "verify-seed",
    "verify-context",
    "ensure-permissions",
    "prepare-connected",
    "connected-source",
    "model-gateway",
    "persist-recommendation",
    "agentforce",
    "clinical-refusal",
    "human-approval-and-action-log",
    "mulesoft-writeback",
    "outcome-and-lightning-refresh",
    "agentforce-outcome-context",
    "apex-final-context",
    "verify-connected",
]
FINAL_COUNT_MINIMUMS = {
    "HFS_Action__c": 7,
    "HFS_Evidence__c": 7,
    "HFS_Evaluation__c": 8,
    "HFS_Event__c": 9,
    "HFS_Outcome__c": 8,
    "HFS_Recommendation__c": 1,
    "HFS_Work_Item__c": 1,
}
REQUIRED_FINAL_ENTITY_TYPES = {
    "CUSTOMER_ALIAS",
    "LOCATION",
    "RESOURCE",
    "PARTNER",
    "PROCESS",
}
REQUIRED_FINAL_ENTITY_KEYS = {
    "ALIAS-PATIENT-GROUP-MORNING-001",
    "DEPT-OUTPATIENT-RECEPTION",
    "RESOURCE-WARD-A3-DISCHARGE-ROOMS",
    "RESOURCE-PHARMACY-IV-KITS",
    "PARTNER-ISLAND-DIAGNOSTICS",
    "PROCESS-BILLING-INSURANCE-REVIEW",
}
REQUIRED_FINAL_EVIDENCE_TYPES = {
    "PATIENT_COMPLAINT_CLUSTER",
    "RESOURCE_CAPACITY",
    "PHARMACY_STOCK_POSITION",
    "PARTNER_RESPONSE_STATUS",
    "BILLING_AND_INSURANCE_HOLD",
    "STAFF_QUEUE_RISK",
    "CLINICAL_DECISION_REFUSAL",
}
REQUIRED_FINAL_ACTION_TYPES = {
    "CREATE_PATIENT_SERVICE_TASK",
    "REQUEST_BED_CLEANING",
    "CREATE_PHARMACY_RESTOCK_REQUEST",
    "ESCALATE_LAB_VENDOR_CASE",
    "OPEN_BILLING_REVIEW",
    "SEND_SLACK_ALERT",
    "SEND_WHATSAPP_ALERT",
}
REQUIRED_TASK_ROUTING = {
    "CREATE_PATIENT_SERVICE_TASK": {
        "ownerRoleAlias": "role:patient-experience-lead",
        "escalationRoleAlias": "role:operations-manager",
    },
    "REQUEST_BED_CLEANING": {
        "ownerRoleAlias": "role:bed-manager",
        "escalationRoleAlias": "role:operations-manager",
    },
    "CREATE_PHARMACY_RESTOCK_REQUEST": {
        "ownerRoleAlias": "role:pharmacy-lead",
        "escalationRoleAlias": "role:duty-manager",
    },
    "ESCALATE_LAB_VENDOR_CASE": {
        "ownerRoleAlias": "role:lab-coordination-lead",
        "escalationRoleAlias": "role:partner-manager",
    },
    "OPEN_BILLING_REVIEW": {
        "ownerRoleAlias": "role:billing-supervisor",
        "escalationRoleAlias": "role:finance-manager",
    },
}
REQUIRED_FINAL_OUTCOME_TYPES = {
    "BILLING_REVIEW_OPENED",
    "COMPLAINT_CONTAINED",
    "DISCHARGE_ROOMS_RELEASED",
    "LAB_PARTNER_SLA_ESCALATED",
    "PHARMACY_STOCKOUT_AVOIDED",
    "SLACK_ALERT_DELIVERY",
    "WAIT_TIME_REDUCED",
    "WHATSAPP_ALERT_DELIVERY",
}
REQUIRED_FINAL_OUTCOME_METRICS = {
    "billing_issue_routed",
    "complaint_contained",
    "outpatient_wait_time_reduced_minutes",
    "partner_sla_escalated",
    "rooms_released",
    "slack_alert_delivery_success",
    "stockout_avoided",
    "whatsapp_alert_delivery_success",
}
SENSITIVE_KEYS = {
    "accessToken",
    "instanceUrl",
    "logs",
    "password",
    "refreshToken",
    "username",
}


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def integer(value: Any, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise VerificationError(f"{name} must be an integer") from error


def require_subset(value: Any, required: set[str], name: str) -> set[str]:
    require(isinstance(value, list), f"{name} must be a list")
    actual = {str(item) for item in value}
    missing = sorted(required - actual)
    require(not missing, f"{name} is missing: {', '.join(missing)}")
    return actual


def validate_task_routing(actions: dict[str, Any]) -> dict[str, int]:
    task_actions = actions.get("taskActions")
    require(isinstance(task_actions, list), "Task actions must be a list")
    by_type = {
        str(action.get("actionType")): action
        for action in task_actions
        if isinstance(action, dict)
    }
    missing = sorted(set(REQUIRED_TASK_ROUTING) - set(by_type))
    require(not missing, f"Task routing is missing: {', '.join(missing)}")

    priority_ranks: list[int] = []
    for action_type, expected in REQUIRED_TASK_ROUTING.items():
        action = by_type[action_type]
        require(
            action.get("ownerRoleAlias") == expected["ownerRoleAlias"],
            f"{action_type} has the wrong owner role alias",
        )
        require(
            action.get("escalationRoleAlias")
            == expected["escalationRoleAlias"],
            f"{action_type} has the wrong escalation role alias",
        )
        priority_rank = integer(
            action.get("priorityRank"),
            f"{action_type} priority rank",
        )
        service_window = integer(
            action.get("serviceWindowMinutes"),
            f"{action_type} service window",
        )
        escalation_window = integer(
            action.get("missedEscalationMinutes"),
            f"{action_type} missed escalation window",
        )
        require(
            priority_rank > 0,
            f"{action_type} priority rank must be positive",
        )
        require(
            0 < escalation_window < service_window,
            f"{action_type} must escalate before the service window is lost",
        )
        require(
            action.get("approvalRequired") is True
            and action.get("escalatesBeforeWindowLoss") is True
            and bool(action.get("urgency"))
            and bool(action.get("riskClass")),
            f"{action_type} is missing governed routing metadata",
        )
        priority_ranks.append(priority_rank)

    require(
        sorted(priority_ranks) == list(range(1, len(REQUIRED_TASK_ROUTING) + 1)),
        "Task priority ranks must be deterministic and complete",
    )
    return {
        "taskRoutingCount": len(REQUIRED_TASK_ROUTING),
        "highestPriorityRank": min(priority_ranks),
        "lowestPriorityRank": max(priority_ranks),
    }


def normalize_repository(repository: str) -> str:
    if repository.startswith("git@"):
        match = re.fullmatch(r"git@([^:]+):(.+?)(?:\.git)?", repository)
        return (
            f"{match.group(1)}/{match.group(2)}"
            if match
            else "remote-repository"
        )

    parsed = urlsplit(repository)
    if parsed.scheme in {"http", "https", "ssh"} and parsed.hostname:
        path = parsed.path.removesuffix(".git")
        return urlunsplit((parsed.scheme, parsed.hostname, path, "", ""))

    return "local-repository"


def assert_no_sensitive_keys(value: Any, path: str = "report") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(key not in SENSITIVE_KEYS, f"{path} contains sensitive key {key}")
            assert_no_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_sensitive_keys(child, f"{path}[{index}]")


def validate_deployment(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("status") == 0, "Salesforce deployment command failed")
    result = payload.get("result")
    require(isinstance(result, dict), "Salesforce deployment result is missing")
    require(result.get("status") == "Succeeded", "Salesforce deployment did not succeed")

    details = result.get("details") or {}
    run_tests = details.get("runTestResult") or {}
    tests_run = integer(
        result.get("numberTestsCompleted", run_tests.get("numTestsRun", 0)),
        "Salesforce tests run",
    )
    test_failures = integer(
        result.get("numberTestErrors", run_tests.get("numFailures", 0)),
        "Salesforce test failures",
    )
    components_deployed = integer(
        result.get("numberComponentsDeployed", 0),
        "Salesforce components deployed",
    )
    components_total = integer(
        result.get("numberComponentsTotal", components_deployed),
        "Salesforce components total",
    )

    require(tests_run > 0, "Salesforce deployment ran no Apex tests")
    require(test_failures == 0, "Salesforce deployment has Apex test failures")
    require(
        components_deployed == components_total,
        "Salesforce deployment did not deploy every component",
    )

    return {
        "status": "Succeeded",
        "componentsDeployed": components_deployed,
        "componentsTotal": components_total,
        "testsRun": tests_run,
        "testFailures": test_failures,
    }


def validate_demo(report: dict[str, Any]) -> dict[str, Any]:
    assert_no_sensitive_keys(report)
    require(report.get("schemaVersion") == SCHEMA_VERSION, "Demo schema is not 1.0.0")
    require(report.get("command") == "run", "Demo did not execute the run command")
    require(report.get("status") == "passed", "Connected demo did not pass")

    steps = report.get("steps")
    require(isinstance(steps, list), "Demo steps are missing")
    step_statuses = {
        step.get("name"): step.get("status")
        for step in steps
        if isinstance(step, dict)
    }
    missing_steps = [name for name in REQUIRED_STEPS if name not in step_statuses]
    require(not missing_steps, f"Demo is missing steps: {', '.join(missing_steps)}")
    failed_steps = [
        name for name in REQUIRED_STEPS if step_statuses.get(name) != "passed"
    ]
    require(not failed_steps, f"Demo has failed steps: {', '.join(failed_steps)}")

    details = report.get("details")
    require(isinstance(details, dict), "Demo details are missing")
    model = details.get("model") or {}
    agentforce = details.get("agentforce") or {}
    clinical_refusal = details.get("clinicalRefusal") or {}
    action = details.get("action") or {}
    mulesoft = details.get("mulesoft") or {}
    delivery_by_type = mulesoft.get("deliveryByActionType") or {}
    outcome = details.get("outcome") or {}
    post_outcome_agentforce = details.get("postOutcomeAgentforce") or {}
    apex_final_context = details.get("apexFinalContext") or {}
    connected = details.get("connected") or {}
    counts = connected.get("counts") or {}

    require(
        model.get("restrictedDecision") == "NO_QUALIFIED_DEPLOYMENT",
        "Restricted model route did not reject the deployment",
    )
    require(
        model.get("restrictedAuditStatus") == "FAILED_CLOSED",
        "Restricted model route did not fail closed",
    )
    require(
        agentforce.get("inaccessibleStatus") == "REFUSED"
        and agentforce.get("inaccessibleRefusalCode") == "INACCESSIBLE_EVIDENCE",
        "Agentforce did not refuse inaccessible evidence",
    )
    require(
        agentforce.get("externalActionExecuted") is False,
        "Agentforce executed an external action",
    )
    require(
        agentforce.get("modelInvocationId") == model.get("invocationId"),
        "Agentforce recommendation lost model invocation provenance",
    )
    require(
        isinstance(agentforce.get("citationEvidenceIds"), list)
        and len(agentforce["citationEvidenceIds"]) > 0,
        "Agentforce explanation has no evidence citations",
    )
    covered_categories = set(agentforce.get("coveredCategories") or [])
    require(
        {
            "complaint",
            "resource",
            "capacity",
            "partner",
            "billing",
            "stock",
            "staffing",
            "approval",
        }
        <= covered_categories
        and integer(
            agentforce.get("recommendationEvidenceCount", 0),
            "Agentforce recommendation evidence count",
        )
        >= 7,
        "Agentforce recommendation is missing required hospital context coverage",
    )
    require(
        clinical_refusal.get("status") == "REFUSED"
        and clinical_refusal.get("errorCode") == "CLINICAL_DECISION_REFUSED"
        and clinical_refusal.get("storedRecommendationCount") == 0,
        "Clinical decision request did not fail closed",
    )
    require(
        action.get("blockedErrorCode") == "INVALID_STATE",
        "Salesforce did not block the pre-approval action",
    )
    task_routing = validate_task_routing(action)
    require(
        mulesoft.get("blockedStatus") == 403
        and mulesoft.get("blockedErrorCode") == "PERMISSION_DENIED",
        "MuleSoft did not block the unregistered approval",
    )
    require(
        mulesoft.get("executionStatus") == 202
        and mulesoft.get("executionState") == "QUEUED",
        "MuleSoft did not accept the approved write-back",
    )
    for action_type in ("SEND_SLACK_ALERT", "SEND_WHATSAPP_ALERT"):
        delivery = delivery_by_type.get(action_type) or {}
        require(
            delivery.get("status") in {"SENT", "MOCK_SENT"},
            f"MuleSoft did not record approved {action_type} delivery",
        )
        require(
            delivery.get("provider"),
            f"MuleSoft {action_type} delivery has no provider evidence",
        )
    require(
        outcome.get("actionStatus") == "EXECUTED"
        and outcome.get("outcomeStatus") == "SUCCESS"
        and outcome.get("workItemStatus") == "COMPLETED",
        "The final governed outcome is incomplete",
    )
    require(
        integer(outcome.get("taskActionCount", 0), "task action count") >= 5
        and integer(
            outcome.get("executedChannelActionCount", 0),
            "executed channel action count",
        )
        >= 2,
        "The final governed context is missing task or channel actions",
    )
    require(
        integer(
            outcome.get("executedTaskActionCount", 0),
            "executed task action count",
        )
        >= 5
        and integer(
            outcome.get("businessOutcomeCount", 0),
            "business outcome count",
        )
        >= 6
        and integer(outcome.get("outcomeCount", 0), "outcome count") >= 8
        and integer(
            outcome.get("evaluationCount", 0),
            "evaluation count",
        )
        >= 8,
        "The final governed context is missing business outcomes or evaluations",
    )
    require(
        post_outcome_agentforce.get("outcomeContextCovered") is True
        and integer(
            post_outcome_agentforce.get("outcomeRecordCount", 0),
            "Agentforce outcome record count",
        )
        >= 8
        and integer(
            post_outcome_agentforce.get("metricCount", 0),
            "Agentforce metric count",
        )
        >= 8,
        "Agentforce did not include outcome and metric context after write-back",
    )
    require(
        apex_final_context.get("workItemStatus") == "COMPLETED",
        "Final Apex context did not return the completed work item",
    )
    final_entity_types = require_subset(
        apex_final_context.get("entityTypes"),
        REQUIRED_FINAL_ENTITY_TYPES,
        "Final Apex entity types",
    )
    require_subset(
        apex_final_context.get("entityExternalKeys"),
        REQUIRED_FINAL_ENTITY_KEYS,
        "Final Apex entity external keys",
    )
    final_evidence_types = require_subset(
        apex_final_context.get("evidenceTypes"),
        REQUIRED_FINAL_EVIDENCE_TYPES,
        "Final Apex evidence types",
    )
    final_action_types = require_subset(
        apex_final_context.get("actionTypes"),
        REQUIRED_FINAL_ACTION_TYPES,
        "Final Apex action types",
    )
    final_outcome_types = require_subset(
        apex_final_context.get("outcomeTypes"),
        REQUIRED_FINAL_OUTCOME_TYPES,
        "Final Apex outcome types",
    )
    require_subset(
        apex_final_context.get("outcomeMetricKeys"),
        REQUIRED_FINAL_OUTCOME_METRICS,
        "Final Apex outcome metric keys",
    )
    require(
        integer(
            apex_final_context.get("recommendationCount", 0),
            "Final Apex recommendation count",
        )
        >= 1
        and integer(
            apex_final_context.get("approvalCount", 0),
            "Final Apex approval count",
        )
        >= 1
        and integer(
            apex_final_context.get("actionCount", 0),
            "Final Apex action count",
        )
        >= 7
        and integer(
            apex_final_context.get("outcomeCount", 0),
            "Final Apex outcome count",
        )
        >= 8
        and integer(
            apex_final_context.get("evaluationCount", 0),
            "Final Apex evaluation count",
        )
        >= 8,
        "Final Apex context is missing recommendation, approval, action, "
        "outcome, or evaluation records",
    )

    for object_name, minimum in FINAL_COUNT_MINIMUMS.items():
        require(
            integer(counts.get(object_name, 0), f"{object_name} count") >= minimum,
            f"{object_name} did not reach its required final count",
        )

    return {
        "schemaVersion": report["schemaVersion"],
        "status": report["status"],
        "startedAt": report.get("startedAt"),
        "completedAt": report.get("completedAt"),
        "tenantKey": report.get("tenantKey"),
        "steps": [
            {
                "name": name,
                "status": step_statuses[name],
            }
            for name in REQUIRED_STEPS
        ],
        "invariants": {
            "restrictedModelDecision": model["restrictedDecision"],
            "restrictedModelAuditStatus": model["restrictedAuditStatus"],
            "inaccessibleEvidence": agentforce["inaccessibleRefusalCode"],
            "agentforceCoveredCategories": sorted(covered_categories),
            "agentforceRecommendationEvidenceCount": agentforce[
                "recommendationEvidenceCount"
            ],
            "clinicalDecisionRefusal": clinical_refusal["errorCode"],
            "agentforceExternalActionExecuted": agentforce[
                "externalActionExecuted"
            ],
            "salesforcePreApprovalAction": action["blockedErrorCode"],
            "mulesoftPreApprovalStatus": mulesoft["blockedStatus"],
            "mulesoftPreApprovalError": mulesoft["blockedErrorCode"],
            "mulesoftApprovedStatus": mulesoft["executionStatus"],
            "slackDeliveryStatus": delivery_by_type["SEND_SLACK_ALERT"]["status"],
            "whatsappDeliveryStatus": delivery_by_type["SEND_WHATSAPP_ALERT"][
                "status"
            ],
            "taskActionCount": outcome["taskActionCount"],
            "executedChannelActionCount": outcome[
                "executedChannelActionCount"
            ],
            "executedTaskActionCount": outcome["executedTaskActionCount"],
            "businessOutcomeCount": outcome["businessOutcomeCount"],
            **task_routing,
            "postOutcomeAgentforce": post_outcome_agentforce[
                "outcomeContextCovered"
            ],
            "apexFinalEntityTypes": sorted(final_entity_types),
            "apexFinalEvidenceTypes": sorted(final_evidence_types),
            "apexFinalActionTypes": sorted(final_action_types),
            "apexFinalOutcomeTypes": sorted(final_outcome_types),
            "finalActionStatus": outcome["actionStatus"],
            "finalOutcomeStatus": outcome["outcomeStatus"],
            "finalWorkItemStatus": outcome["workItemStatus"],
        },
        "finalCounts": counts,
    }


def build_evidence(
    deployment: dict[str, Any],
    demo: dict[str, Any],
    repository: str,
    source_ref: str,
    source_commit: str,
) -> dict[str, Any]:
    require(
        re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
        "Source commit must be a full Git SHA",
    )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "passed",
        "verifiedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "repository": normalize_repository(repository),
            "ref": source_ref,
            "commit": source_commit,
        },
        "deployment": deployment,
        "demo": demo,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and summarize clean-clone completion evidence."
    )
    parser.add_argument("--deployment-result", required=True, type=Path)
    parser.add_argument("--demo-result", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    require(isinstance(payload, dict), f"{path.name} must contain a JSON object")
    return payload


def main() -> int:
    args = parse_args()
    try:
        deployment = validate_deployment(load_json(args.deployment_result))
        demo = validate_demo(load_json(args.demo_result))
        evidence = build_evidence(
            deployment,
            demo,
            args.repository,
            args.source_ref,
            args.source_commit,
        )
    except (OSError, json.JSONDecodeError, VerificationError) as error:
        print(f"Clean-clone evidence validation failed: {error}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(f"Clean-clone evidence written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
