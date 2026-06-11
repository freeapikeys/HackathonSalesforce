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
            "action": {"blockedErrorCode": "INVALID_STATE"},
            "mulesoft": {
                "blockedStatus": 403,
                "blockedErrorCode": "PERMISSION_DENIED",
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
                },
            },
            "outcome": {
                "actionStatus": "EXECUTED",
                "executedChannelActionCount": 2,
                "outcomeStatus": "SUCCESS",
                "taskActionCount": 5,
                "workItemStatus": "COMPLETED",
            },
            "postOutcomeAgentforce": {
                "outcomeContextCovered": True,
                "outcomeRecordCount": 2,
                "actionRecordCount": 7,
                "metricCount": 2,
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
                    "ESCALATE_LAB_VENDOR_CASE",
                    "OPEN_BILLING_REVIEW",
                    "SEND_SLACK_ALERT",
                    "SEND_WHATSAPP_ALERT",
                ],
                "outcomeTypes": [
                    "SLACK_ALERT_DELIVERY",
                    "WHATSAPP_ALERT_DELIVERY",
                ],
                "outcomeMetricKeys": [
                    "slack_alert_delivery_success",
                    "whatsapp_alert_delivery_success",
                ],
                "recommendationCount": 1,
                "approvalCount": 1,
                "actionCount": 7,
                "outcomeCount": 2,
                "evaluationCount": 2,
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
