import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any


MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_source_intake.py"
SPEC = importlib.util.spec_from_file_location("verify_source_intake", MODULE_PATH)
verify_source_intake = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(verify_source_intake)


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run_json(self, command: list[str]) -> dict[str, Any]:
        self.commands.append(command)
        return {
            "status": 0,
            "result": {
                "checkOnly": True,
                "id": "0Af-source-intake",
                "numberTestsCompleted": 42,
                "numberTestErrors": 0,
            },
        }


class SourceIntakeVerifierTest(unittest.TestCase):
    def test_fixture_runtime_reports_all_deterministic_intake_results(self) -> None:
        report = verify_source_intake.verify_fixture_runtime()

        self.assertEqual("passed", report["status"])
        self.assertEqual(46, report["fixtureCount"])
        self.assertEqual(46, report["attemptCount"])
        self.assertEqual(
            {
                "ACCEPTED",
                "ACCEPTED_LATE",
                "ACCEPTED_OUT_OF_ORDER",
                "CONFLICT_REVIEW",
                "DUPLICATE",
                "REJECTED_HASH",
                "REJECTED_IDEMPOTENCY_CONFLICT",
                "REJECTED_SCHEMA",
            },
            set(report["resultCounts"].keys()),
        )
        self.assertEqual(report["preservedCount"], report["callbackCount"])

    def test_replay_runtime_proves_quarantine_replay_and_permanent_rejection(
        self,
    ) -> None:
        report = verify_source_intake.verify_replay_paths()

        self.assertEqual("passed", report["status"])
        self.assertEqual("COMPLETED", report["malformedReplay"])
        self.assertEqual("COMPLETED", report["exhaustedRetryReplay"])
        self.assertEqual(409, report["permanentReplayStatus"])

    def test_salesforce_verification_is_explicitly_skipped_without_target(self) -> None:
        report = verify_source_intake.verify_salesforce(None)

        self.assertEqual("skipped", report["status"])
        self.assertIn("--target-org", report["reason"])

    def test_salesforce_verification_uses_check_only_local_tests(self) -> None:
        runner = FakeRunner()
        report = verify_source_intake.verify_salesforce(
            "dev-ed",
            runner=runner,
        )

        self.assertEqual("passed", report["status"])
        self.assertEqual(True, report["checkOnly"])
        self.assertEqual("0Af-source-intake", report["deployId"])
        self.assertEqual(
            [
                "sf",
                "project",
                "deploy",
                "validate",
                "--source-dir",
                "force-app/main/default",
                "--target-org",
                "dev-ed",
                "--test-level",
                "RunLocalTests",
                "--json",
            ],
            runner.commands[0],
        )

    def test_report_is_machine_readable(self) -> None:
        report = verify_source_intake.build_report(None)

        self.assertEqual("passed", report["status"])
        self.assertEqual("skipped", report["salesforce"]["status"])
        json.dumps(report)


if __name__ == "__main__":
    unittest.main()
