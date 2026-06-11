import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "verify_clean_clone_result.py"
)
SPEC = importlib.util.spec_from_file_location(
    "verify_clean_clone_result", MODULE_PATH
)
verify = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(verify)


def passing_deployment():
    return {
        "status": 0,
        "result": {
            "status": "Succeeded",
            "numberComponentsDeployed": 80,
            "numberComponentsTotal": 80,
            "numberTestsCompleted": 19,
            "numberTestsTotal": 19,
            "numberTestErrors": 0,
        },
    }


def passing_demo():
    return {
        "schemaVersion": "1.0.0",
        "command": "run",
        "status": "passed",
        "startedAt": "2026-06-07T10:00:00Z",
        "completedAt": "2026-06-07T10:03:00Z",
        "tenantKey": "demo-mauritius",
        "steps": [
            {"name": name, "status": "passed"}
            for name in verify.REQUIRED_STEPS
        ],
        "details": {
            "twilioIntake": {
                "status": "ACCEPTED",
                "sourceChannel": "whatsapp-inbound",
                "messageBodyStored": False,
                "protectedActionState": "NO_ACTION_EXECUTED",
                "followUpQuestionCount": 5,
                "rootCauseHypothesisCount": 3,
                "expandedFunctions": [
                    "patient trust",
                    "resource and capacity",
                    "pharmacy inventory",
                    "billing",
                    "communication",
                    "outcome learning",
                ],
            },
            "model": {
                "invocationId": "runtime-invocation-0001",
                "restrictedDecision": "NO_QUALIFIED_DEPLOYMENT",
                "restrictedAuditStatus": "FAILED_CLOSED",
            },
            "agentforce": {
                "citationEvidenceIds": ["evidence-001"],
                "coveredCategories": [
                    "complaint",
                    "resource",
                    "capacity",
                    "partner",
                    "billing",
                    "stock",
                    "staffing",
                    "approval",
                ],
                "recommendationEvidenceCount": 7,
                "externalActionExecuted": False,
                "inaccessibleStatus": "REFUSED",
                "inaccessibleRefusalCode": "INACCESSIBLE_EVIDENCE",
                "modelInvocationId": "runtime-invocation-0001",
            },
            "clinicalRefusal": {
                "status": "REFUSED",
                "errorCode": "CLINICAL_DECISION_REFUSED",
                "storedRecommendationCount": 0,
            },
            "action": {
                "blockedErrorCode": "INVALID_STATE",
                "taskActions": [
                    {
                        "actionType": "CREATE_PATIENT_SERVICE_TASK",
                        "ownerRoleAlias": "role:patient-experience-lead",
                        "escalationRoleAlias": "role:operations-manager",
                        "priorityRank": 1,
                        "urgency": "HIGH",
                        "riskClass": "PATIENT_TRUST",
                        "serviceWindowMinutes": 20,
                        "missedEscalationMinutes": 10,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "REQUEST_BED_CLEANING",
                        "ownerRoleAlias": "role:bed-manager",
                        "escalationRoleAlias": "role:operations-manager",
                        "priorityRank": 2,
                        "urgency": "HIGH",
                        "riskClass": "CAPACITY",
                        "serviceWindowMinutes": 30,
                        "missedEscalationMinutes": 15,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "CREATE_PHARMACY_RESTOCK_REQUEST",
                        "ownerRoleAlias": "role:pharmacy-lead",
                        "escalationRoleAlias": "role:duty-manager",
                        "priorityRank": 5,
                        "urgency": "MEDIUM_HIGH",
                        "riskClass": "STOCK",
                        "serviceWindowMinutes": 45,
                        "missedEscalationMinutes": 25,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "REQUEST_PORTER_SUPPORT_TASK",
                        "ownerRoleAlias": "role:porter-lead",
                        "escalationRoleAlias": "role:bed-manager",
                        "priorityRank": 3,
                        "urgency": "HIGH",
                        "riskClass": "CAPACITY",
                        "serviceWindowMinutes": 25,
                        "missedEscalationMinutes": 12,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "OPEN_FRONT_DESK_QUEUE_TASK",
                        "ownerRoleAlias": "role:front-desk-lead",
                        "escalationRoleAlias": "role:operations-manager",
                        "priorityRank": 4,
                        "urgency": "HIGH",
                        "riskClass": "QUEUE",
                        "serviceWindowMinutes": 20,
                        "missedEscalationMinutes": 8,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "ESCALATE_LAB_VENDOR_CASE",
                        "ownerRoleAlias": "role:lab-coordination-lead",
                        "escalationRoleAlias": "role:partner-manager",
                        "priorityRank": 6,
                        "urgency": "MEDIUM_HIGH",
                        "riskClass": "PARTNER_SLA",
                        "serviceWindowMinutes": 20,
                        "missedEscalationMinutes": 10,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "OPEN_BILLING_REVIEW",
                        "ownerRoleAlias": "role:billing-supervisor",
                        "escalationRoleAlias": "role:finance-manager",
                        "priorityRank": 7,
                        "urgency": "MEDIUM",
                        "riskClass": "FINANCIAL_EXPOSURE",
                        "serviceWindowMinutes": 60,
                        "missedEscalationMinutes": 30,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                    {
                        "actionType": "CREATE_MANAGER_REVIEW_TASK",
                        "ownerRoleAlias": "role:operations-manager",
                        "escalationRoleAlias": "role:duty-executive",
                        "priorityRank": 8,
                        "urgency": "MEDIUM",
                        "riskClass": "GOVERNANCE",
                        "serviceWindowMinutes": 90,
                        "missedEscalationMinutes": 45,
                        "approvalRequired": True,
                        "escalatesBeforeWindowLoss": True,
                    },
                ],
            },
            "mulesoft": {
                "blockedStatus": 403,
                "blockedErrorCode": "PERMISSION_DENIED",
                "pendingApprovalBlockedStatus": 403,
                "pendingApprovalBlockedError": "PERMISSION_DENIED",
                "slackApproval": {
                    "decisionStatus": "APPROVED",
                },
                "executionStatus": 202,
                "executionState": "QUEUED",
                "deliveryByActionType": {
                    "SEND_SLACK_ALERT": {
                        "status": "MOCK_SENT",
                        "provider": "mock-slack",
                    },
                    "SEND_WHATSAPP_ALERT": {
                        "status": "MOCK_SENT",
                        "provider": "mock-whatsapp",
                    },
                    "SEND_VENDOR_EMAIL": {
                        "status": "QUEUED",
                        "metricKey": "vendor_email_queued",
                    },
                },
            },
            "outcome": {
                "actionStatus": "EXECUTED",
                "businessOutcomeCount": 9,
                "executedChannelActionCount": 3,
                "executedTaskActionCount": 8,
                "evaluationCount": 12,
                "outcomeCount": 12,
                "outcomeStatus": "SUCCESS",
                "taskActionCount": 8,
                "workItemStatus": "COMPLETED",
            },
            "postOutcomeAgentforce": {
                "outcomeContextCovered": True,
                "outcomeRecordCount": 12,
                "actionRecordCount": 11,
                "metricCount": 12,
            },
            "apexFinalContext": {
                "workItemStatus": "COMPLETED",
                "entityTypes": [
                    "CUSTOMER_ALIAS",
                    "LOCATION",
                    "RESOURCE",
                    "PARTNER",
                    "PROCESS",
                ],
                "entityExternalKeys": [
                    "ALIAS-PATIENT-GROUP-MORNING-001",
                    "DEPT-OUTPATIENT-RECEPTION",
                    "RESOURCE-WARD-A3-DISCHARGE-ROOMS",
                    "RESOURCE-PHARMACY-IV-KITS",
                    "PARTNER-ISLAND-DIAGNOSTICS",
                    "PROCESS-BILLING-INSURANCE-REVIEW",
                ],
                "evidenceTypes": [
                    "PATIENT_COMPLAINT_CLUSTER",
                    "RESOURCE_CAPACITY",
                    "PHARMACY_STOCK_POSITION",
                    "PARTNER_RESPONSE_STATUS",
                    "BILLING_AND_INSURANCE_HOLD",
                    "STAFF_QUEUE_RISK",
                    "CLINICAL_DECISION_REFUSAL",
                ],
                "actionTypes": [
                    "CREATE_PATIENT_SERVICE_TASK",
                    "REQUEST_BED_CLEANING",
                    "CREATE_PHARMACY_RESTOCK_REQUEST",
                    "REQUEST_PORTER_SUPPORT_TASK",
                    "OPEN_FRONT_DESK_QUEUE_TASK",
                    "ESCALATE_LAB_VENDOR_CASE",
                    "OPEN_BILLING_REVIEW",
                    "CREATE_MANAGER_REVIEW_TASK",
                    "SEND_SLACK_ALERT",
                    "SEND_WHATSAPP_ALERT",
                    "SEND_VENDOR_EMAIL",
                ],
                "outcomeTypes": [
                    "ACTION_EXECUTED",
                    "BILLING_REVIEW_OPENED",
                    "COMPLAINT_CONTAINED",
                    "DISCHARGE_ROOMS_RELEASED",
                    "FRONT_DESK_QUEUE_SUPPORT_OPENED",
                    "LAB_PARTNER_SLA_ESCALATED",
                    "MANAGER_REVIEW_OPENED",
                    "PHARMACY_STOCKOUT_AVOIDED",
                    "PORTER_SUPPORT_DISPATCHED",
                    "SLACK_ALERT_DELIVERY",
                    "WAIT_TIME_REDUCED",
                    "WHATSAPP_ALERT_DELIVERY",
                ],
                "outcomeMetricKeys": [
                    "billing_issue_routed",
                    "complaint_contained",
                    "front_desk_support_opened",
                    "manager_review_opened",
                    "outpatient_wait_time_reduced_minutes",
                    "partner_sla_escalated",
                    "porter_support_dispatched",
                    "rooms_released",
                    "slack_alert_delivery_success",
                    "stockout_avoided",
                    "vendor_email_queued",
                    "whatsapp_alert_delivery_success",
                ],
                "recommendationCount": 1,
                "approvalCount": 1,
                "actionCount": 11,
                "outcomeCount": 12,
                "evaluationCount": 12,
            },
            "connected": {
                "counts": dict(verify.FINAL_COUNT_MINIMUMS),
            },
        },
    }


class CleanCloneResultTest(unittest.TestCase):
    def test_builds_sanitized_completion_evidence(self):
        deployment = verify.validate_deployment(passing_deployment())
        demo = verify.validate_demo(passing_demo())
        evidence = verify.build_evidence(
            deployment,
            demo,
            "https://token@example.com/freeapikeys/HackathonSalesforce.git",
            "main",
            "a" * 40,
        )

        self.assertEqual("passed", evidence["status"])
        self.assertEqual(
            "https://example.com/freeapikeys/HackathonSalesforce",
            evidence["source"]["repository"],
        )
        self.assertEqual(19, evidence["deployment"]["testsRun"])
        self.assertEqual(
            "COMPLETED",
            evidence["demo"]["invariants"]["finalWorkItemStatus"],
        )
        self.assertIn(
            "CUSTOMER_ALIAS",
            evidence["demo"]["invariants"]["apexFinalEntityTypes"],
        )

    def test_rejects_a_missing_governed_failure_step(self):
        report = passing_demo()
        report["details"]["action"]["blockedErrorCode"] = "SUCCESS"

        with self.assertRaisesRegex(
            verify.VerificationError,
            "pre-approval action",
        ):
            verify.validate_demo(report)

    def test_rejects_wrong_task_owner_alias(self):
        report = passing_demo()
        report["details"]["action"]["taskActions"][0][
            "ownerRoleAlias"
        ] = "role:wrong-owner"

        with self.assertRaisesRegex(
            verify.VerificationError,
            "wrong owner role alias",
        ):
            verify.validate_demo(report)

    def test_rejects_sensitive_command_output(self):
        report = passing_demo()
        report["logs"] = "local command output"

        with self.assertRaisesRegex(verify.VerificationError, "sensitive key"):
            verify.validate_demo(report)

    def test_rejects_missing_final_apex_primitive(self):
        report = passing_demo()
        report["details"]["apexFinalContext"]["entityTypes"].remove(
            "CUSTOMER_ALIAS"
        )

        with self.assertRaisesRegex(
            verify.VerificationError,
            "Final Apex entity types",
        ):
            verify.validate_demo(report)

    def test_rejects_deployment_test_failures(self):
        deployment = passing_deployment()
        deployment["result"]["numberTestErrors"] = 1

        with self.assertRaisesRegex(verify.VerificationError, "test failures"):
            verify.validate_deployment(deployment)


if __name__ == "__main__":
    unittest.main()
