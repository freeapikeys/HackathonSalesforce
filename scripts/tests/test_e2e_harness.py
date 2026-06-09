import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any


MODULE_PATH = Path(__file__).resolve().parents[1] / "e2e_harness.py"
SPEC = importlib.util.spec_from_file_location("e2e_harness", MODULE_PATH)
e2e_harness = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(e2e_harness)


CONFIG = {
    "schemaVersion": "1.0.0",
    "tenantKey": "demo-test",
    "correlationId": "correlation-test",
    "expectedCounts": {
        "HFS_Event__c": 1,
        "HFS_Work_Item__c": 1,
        "HFS_Recommendation__c": 1,
        "HFS_Approval__c": 1,
    },
    "identifiers": {
        "workItemExternalKey": "work-test",
        "recommendationExternalKey": "recommendation-test",
        "approvalExternalKey": "approval-test",
    },
}


class FakeRunner:
    def __init__(self, counts: dict[str, int] | None = None) -> None:
        self.commands: list[list[str]] = []
        self.counts = counts or dict(CONFIG["expectedCounts"])

    def run(self, command: list[str]) -> dict[str, Any]:
        self.commands.append(command)
        if command[:3] == ["node", "-p", "process.versions.node"]:
            return {"stdout": "20.19.0"}
        if command[:3] == ["sf", "org", "display"]:
            return {"status": 0, "result": {"connectedStatus": "Connected"}}
        if command[:3] == ["sf", "data", "query"]:
            query = command[command.index("--query") + 1]
            if "COUNT(Id)" in query:
                object_api_name = query.split("FROM ", 1)[1].split()[0]
                return {
                    "status": 0,
                    "result": {
                        "records": [{"total": self.counts[object_api_name]}]
                    },
                }
            external_key = query.split("External_Key__c = '", 1)[1].split(
                "'", 1
            )[0]
            return {
                "status": 0,
                "result": {"records": [{"Id": f"id-{external_key}"}]},
            }
        return {"status": 0, "result": {}}


class DemoHarnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_which = e2e_harness.shutil.which
        e2e_harness.shutil.which = lambda command: f"/test/{command}"

    def tearDown(self) -> None:
        e2e_harness.shutil.which = self.original_which

    def test_seed_reports_repeatable_records_and_identifiers(self) -> None:
        runner = FakeRunner()
        report, exit_code = e2e_harness.run_harness(
            "seed", "test-org", runner=runner, config=CONFIG
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("passed", report["status"])
        self.assertEqual(
            [
                "tools",
                "salesforce-org",
                "reset",
                "seed",
                "verify-seed",
                "verify-context",
            ],
            [step["name"] for step in report["steps"]],
        )
        self.assertEqual(
            "id-work-test", report["details"]["identifiers"]["workItemId"]
        )
        apex_scripts = [
            command[command.index("--file") + 1]
            for command in runner.commands
            if command[:3] == ["sf", "apex", "run"]
        ]
        self.assertTrue(apex_scripts[0].endswith("reset_demo.apex"))
        self.assertTrue(apex_scripts[1].endswith("seed_demo.apex"))
        self.assertTrue(apex_scripts[2].endswith("verify_demo_context.apex"))
        self.assertNotIn("logs", report["steps"][2]["details"])

    def test_connected_model_and_mulesoft_paths_fail_closed_then_succeed(
        self,
    ) -> None:
        # Use fixture config instead of file config to ensure tenant key matches
        contract = e2e_harness.ModelGatewayContract()
        fixture_config = contract.fixture
        
        harness = e2e_harness.DemoHarness(
            "test-org",
            runner=FakeRunner(),
            config=fixture_config,
        )
        source = {
            "workItemId": "a0E000000000001AAA",
            "subjectEntityId": "a01000000000001AAA",
            "triggerEventId": "a09000000000001AAA",
            "evidenceId": "a06000000000001AAA",
            "contentHash": (
                "sha256:"
                "56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70fdb4feada11935c10"
            ),
        }
        model = harness.run_model_gateway(source)
        self.assertEqual("runtime-invocation-0001", model["invocationId"])
        self.assertEqual(
            "NO_QUALIFIED_DEPLOYMENT",
            model["restrictedDecision"],
        )
        self.assertEqual("FAILED_CLOSED", model["restrictedAuditStatus"])

        recommendation = {"recommendationId": "a0B000000000001AAA"}
        action = {
            "approvalId": "a04000000000001AAA",
            "actionId": "a00000000000001AAA",
            "actionExternalKey": "action-demo-001",
            "actionIdempotencyKey": "action-demo-001-v1",
        }
        mulesoft = harness.run_mulesoft(
            source,
            recommendation,
            action,
        )
        self.assertEqual(403, mulesoft["blockedStatus"])
        self.assertEqual("PERMISSION_DENIED", mulesoft["blockedErrorCode"])
        self.assertEqual(202, mulesoft["executionStatus"])
        self.assertEqual(
            fixture_config["correlationId"],
            mulesoft["outcome"]["correlationId"],
        )

    def test_count_mismatch_returns_machine_readable_failure(self) -> None:
        runner = FakeRunner(
            counts={
                **CONFIG["expectedCounts"],
                "HFS_Work_Item__c": 0,
            }
        )
        report, exit_code = e2e_harness.run_harness(
            "verify", "test-org", runner=runner, config=CONFIG
        )

        self.assertEqual(1, exit_code)
        self.assertEqual("failed", report["status"])
        self.assertIn("HFS_Work_Item__c", report["error"])
        json.dumps(report)


if __name__ == "__main__":
    unittest.main()
