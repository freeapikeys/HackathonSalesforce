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

    def test_rejects_deployment_test_failures(self):
        deployment = passing_deployment()
        deployment["result"]["numberTestErrors"] = 1

        with self.assertRaisesRegex(verify.VerificationError, "test failures"):
            verify.validate_deployment(deployment)


if __name__ == "__main__":
    unittest.main()
