import importlib.util
import json
import os
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

    def test_command_runner_resolves_windows_cli_shims(self) -> None:
        original_run = e2e_harness.subprocess.run
        captured: dict[str, Any] = {}

        class Completed:
            returncode = 0
            stdout = '{"status": 0, "result": {"ok": true}}'
            stderr = ""

        def fake_which(command: str) -> str | None:
            if command == "sf":
                return r"C:\Users\test\AppData\Roaming\npm\sf.CMD"
            return None

        def fake_run(command: list[str], **kwargs: Any) -> Completed:
            captured["command"] = command
            captured["kwargs"] = kwargs
            return Completed()

        e2e_harness.shutil.which = fake_which
        e2e_harness.subprocess.run = fake_run
        try:
            result = e2e_harness.CommandRunner().run(
                ["sf", "org", "display", "--json"]
            )
        finally:
            e2e_harness.subprocess.run = original_run

        self.assertEqual({"ok": True}, result["result"])
        self.assertEqual(
            r"C:\Users\test\AppData\Roaming\npm\sf.CMD",
            captured["command"][0],
        )
        self.assertFalse(captured["kwargs"]["check"])

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
                "ensure-permissions",
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
        self.assertTrue(
            apex_scripts[0].endswith("ensure_demo_permissions.apex")
        )
        self.assertTrue(apex_scripts[1].endswith("reset_demo.apex"))
        self.assertTrue(apex_scripts[2].endswith("seed_demo.apex"))
        self.assertTrue(apex_scripts[3].endswith("verify_demo_context.apex"))
        self.assertNotIn("logs", report["steps"][3]["details"])

    def test_connected_model_and_mulesoft_paths_fail_closed_then_succeed(
        self,
    ) -> None:
        # Load fixture to get compatible test configuration
        contract = e2e_harness.ModelGatewayContract()
        fixture = contract.fixture
        fixture_config = {
            "schemaVersion": "1.0.0",
            "tenantKey": fixture["policies"][0]["tenantKey"],
            "correlationId": fixture["generateRequest"]["correlationId"],
            "expectedCounts": CONFIG["expectedCounts"],
            "identifiers": CONFIG["identifiers"],
        }
        
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
                fixture["generateRequest"]["context"]["sourceContentHashes"][0]
            ),
            "targetEntityIds": {
                "DEPT-OUTPATIENT-RECEPTION": "a01000000000002AAA",
                "PARTNER-ISLAND-DIAGNOSTICS": "a01000000000003AAA",
                "PROCESS-BILLING-INSURANCE-REVIEW": "a01000000000004AAA",
                "RESOURCE-PHARMACY-IV-KITS": "a01000000000005AAA",
                "RESOURCE-WARD-A3-DISCHARGE-ROOMS": "a01000000000006AAA",
            },
        }
        model = harness.run_model_gateway(source)
        self.assertIn("runtime-invocation-", model["invocationId"])
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
            "channelActions": [
                {
                    "channel": "slack",
                    "actionType": "SEND_SLACK_ALERT",
                    "sourceSystem": "slack",
                    "actionId": "a00000000000001AAA",
                    "actionExternalKey": "action-demo-slack-001",
                    "actionIdempotencyKey": "action-demo-slack-001-v1",
                },
                {
                    "channel": "whatsapp",
                    "actionType": "SEND_WHATSAPP_ALERT",
                    "sourceSystem": "whatsapp",
                    "actionId": "a00000000000002AAA",
                    "actionExternalKey": "action-demo-whatsapp-001",
                    "actionIdempotencyKey": "action-demo-whatsapp-001-v1",
                },
            ],
        }
        channel_env_names = [
            "SLACK_WEBHOOK_URL",
            "META_WHATSAPP_PHONE_NUMBER_ID",
            "META_WHATSAPP_ACCESS_TOKEN",
            "META_WHATSAPP_TO",
            "META_GRAPH_VERSION",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_WHATSAPP_FROM",
            "TWILIO_WHATSAPP_TO",
        ]
        original_channel_env = {
            name: os.environ.pop(name, None) for name in channel_env_names
        }
        try:
            mulesoft = harness.run_mulesoft(
                source,
                recommendation,
                action,
            )
        finally:
            for name, value in original_channel_env.items():
                if value is not None:
                    os.environ[name] = value
        self.assertEqual(403, mulesoft["blockedStatus"])
        self.assertEqual("PERMISSION_DENIED", mulesoft["blockedErrorCode"])
        self.assertEqual(202, mulesoft["executionStatus"])
        self.assertEqual(
            fixture_config["correlationId"],
            mulesoft["outcome"]["correlationId"],
        )
        self.assertEqual(2, len(mulesoft["outcomes"]))
        self.assertEqual(
            "MOCK_SENT",
            mulesoft["deliveryByActionType"]["SEND_SLACK_ALERT"]["status"],
        )
        self.assertEqual(
            "MOCK_SENT",
            mulesoft["deliveryByActionType"]["SEND_WHATSAPP_ALERT"]["status"],
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
