#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "demo" / "harness-config-v1.json"
RESET_SCRIPT = ROOT / "scripts" / "apex" / "reset_demo.apex"
SEED_SCRIPT = ROOT / "scripts" / "apex" / "seed_demo.apex"
VERIFY_CONTEXT_SCRIPT = ROOT / "scripts" / "apex" / "verify_demo_context.apex"


class HarnessFailure(RuntimeError):
    pass


class CommandRunner:
    def run(self, command: list[str]) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise HarnessFailure(
                f"Command failed ({' '.join(command[:3])}) "
                f"with exit code {completed.returncode}."
            )
        if "--json" not in command:
            return {"stdout": completed.stdout.strip()}
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise HarnessFailure(
                f"Command returned invalid JSON ({' '.join(command)})."
            ) from error
        if payload.get("status") not in (None, 0):
            raise HarnessFailure(
                f"Command reported failure ({' '.join(command)})."
            )
        return payload


class DemoHarness:
    def __init__(
        self,
        target_org: str,
        runner: CommandRunner | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.target_org = target_org
        self.runner = runner or CommandRunner()
        self.config = config or json.loads(CONFIG_PATH.read_text())
        self.steps: list[dict[str, Any]] = []

    def step(self, name: str, operation: Callable[[], Any]) -> Any:
        started = time.monotonic()
        try:
            details = operation()
        except Exception as error:
            self.steps.append(
                {
                    "name": name,
                    "status": "failed",
                    "durationMs": round((time.monotonic() - started) * 1000),
                    "error": str(error),
                }
            )
            raise
        self.steps.append(
            {
                "name": name,
                "status": "passed",
                "durationMs": round((time.monotonic() - started) * 1000),
                "details": details,
            }
        )
        return details

    def validate_tools(self) -> dict[str, str]:
        required = ("node", "npm", "python3", "sf")
        missing = [tool for tool in required if shutil.which(tool) is None]
        if missing:
            raise HarnessFailure(
                f"Missing required command(s): {', '.join(missing)}"
            )
        node_version = self.runner.run(
            ["node", "-p", "process.versions.node"]
        )["stdout"]
        if int(node_version.split(".", 1)[0]) < 20:
            raise HarnessFailure("Node.js 20 or newer is required.")
        if sys.version_info < (3, 12):
            raise HarnessFailure("Python 3.12 or newer is required.")
        return {"node": node_version, "python": sys.version.split()[0]}

    def validate_org(self) -> dict[str, Any]:
        payload = self.runner.run(
            ["sf", "org", "display", "--target-org", self.target_org, "--json"]
        )
        if not payload.get("result"):
            raise HarnessFailure("Salesforce org display returned no result.")
        return {"targetOrg": self.target_org, "connected": True}

    def validate_local_contracts(self) -> dict[str, int]:
        commands = (
            ["npm", "run", "check:project"],
            ["npm", "run", "check:ontology"],
            ["npm", "run", "check:events"],
            ["npm", "run", "check:metadata"],
            ["npm", "run", "check:harness"],
        )
        for command in commands:
            self.runner.run(list(command))
        return {"checks": len(commands)}

    def run_apex(self, script: Path) -> dict[str, str]:
        self.runner.run(
            [
                "sf",
                "apex",
                "run",
                "--file",
                str(script),
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        return {"script": str(script.relative_to(ROOT))}

    def query_count(self, object_api_name: str) -> int:
        tenant_key = self.config["tenantKey"].replace("'", "\\'")
        query = (
            f"SELECT COUNT(Id) total FROM {object_api_name} "
            f"WHERE Tenant_Key__c = '{tenant_key}'"
        )
        payload = self.runner.run(
            [
                "sf",
                "data",
                "query",
                "--query",
                query,
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        records = payload.get("result", {}).get("records", [])
        if not records or "total" not in records[0]:
            raise HarnessFailure(
                f"Count query returned no total for {object_api_name}."
            )
        return int(records[0]["total"])

    def query_identifier(self, object_api_name: str, external_key: str) -> str:
        safe_key = external_key.replace("'", "\\'")
        query = (
            f"SELECT Id FROM {object_api_name} "
            f"WHERE External_Key__c = '{safe_key}' LIMIT 1"
        )
        payload = self.runner.run(
            [
                "sf",
                "data",
                "query",
                "--query",
                query,
                "--target-org",
                self.target_org,
                "--json",
            ]
        )
        records = payload.get("result", {}).get("records", [])
        if len(records) != 1 or not records[0].get("Id"):
            raise HarnessFailure(
                f"Expected one {object_api_name} record for {external_key}."
            )
        return str(records[0]["Id"])

    def verify_counts(self, expected: dict[str, int]) -> dict[str, int]:
        actual = {
            object_api_name: self.query_count(object_api_name)
            for object_api_name in expected
        }
        mismatches = {
            object_api_name: {
                "expected": expected[object_api_name],
                "actual": actual[object_api_name],
            }
            for object_api_name in expected
            if actual[object_api_name] != expected[object_api_name]
        }
        if mismatches:
            raise HarnessFailure(
                f"Fixture counts did not match: {json.dumps(mismatches, sort_keys=True)}"
            )
        return actual

    def verify_seed(self) -> dict[str, Any]:
        identifiers = self.config["identifiers"]
        return {
            "counts": self.verify_counts(self.config["expectedCounts"]),
            "identifiers": {
                "workItemId": self.query_identifier(
                    "HFS_Work_Item__c",
                    identifiers["workItemExternalKey"],
                ),
                "recommendationId": self.query_identifier(
                    "HFS_Recommendation__c",
                    identifiers["recommendationExternalKey"],
                ),
                "approvalId": self.query_identifier(
                    "HFS_Approval__c",
                    identifiers["approvalExternalKey"],
                ),
            },
        }

    def verify_reset(self) -> dict[str, int]:
        expected = {
            object_api_name: 0
            for object_api_name in self.config["expectedCounts"]
        }
        return self.verify_counts(expected)

    def execute(self, command: str) -> dict[str, Any]:
        self.step("tools", self.validate_tools)
        self.step("salesforce-org", self.validate_org)
        if command in ("check", "run"):
            self.step("local-contracts", self.validate_local_contracts)
        if command in ("reset", "seed", "run"):
            self.step("reset", lambda: self.run_apex(RESET_SCRIPT))
        if command == "reset":
            self.step("verify-reset", self.verify_reset)
        if command in ("seed", "run"):
            self.step("seed", lambda: self.run_apex(SEED_SCRIPT))
            details = self.step("verify-seed", self.verify_seed)
            self.step(
                "verify-context",
                lambda: self.run_apex(VERIFY_CONTEXT_SCRIPT),
            )
            return details
        if command == "verify":
            details = self.step("verify-seed", self.verify_seed)
            self.step(
                "verify-context",
                lambda: self.run_apex(VERIFY_CONTEXT_SCRIPT),
            )
            return details
        return {}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_harness(
    command: str,
    target_org: str,
    runner: CommandRunner | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int]:
    started_at = timestamp()
    harness = DemoHarness(target_org, runner=runner, config=config)
    status = "passed"
    error_message = None
    details: dict[str, Any] = {}
    exit_code = 0
    try:
        details = harness.execute(command)
    except Exception as error:
        status = "failed"
        error_message = str(error)
        exit_code = 1
    report = {
        "schemaVersion": harness.config["schemaVersion"],
        "command": command,
        "status": status,
        "startedAt": started_at,
        "completedAt": timestamp(),
        "targetOrg": target_org,
        "tenantKey": harness.config["tenantKey"],
        "steps": harness.steps,
        "details": details,
    }
    if error_message:
        report["error"] = error_message
    return report, exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("check", "seed", "reset", "verify", "run"),
    )
    parser.add_argument("--target-org", default="dev-ed")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report, exit_code = run_harness(args.command, args.target_org)
    serialized = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n")
    print(serialized)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
