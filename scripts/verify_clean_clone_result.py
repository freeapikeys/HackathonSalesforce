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
    "human-approval-and-action-log",
    "mulesoft-writeback",
    "outcome-and-lightning-refresh",
    "verify-connected",
]
FINAL_COUNT_MINIMUMS = {
    "HFS_Action__c": 1,
    "HFS_Evaluation__c": 1,
    "HFS_Event__c": 2,
    "HFS_Outcome__c": 1,
    "HFS_Recommendation__c": 1,
    "HFS_Work_Item__c": 1,
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
    action = details.get("action") or {}
    mulesoft = details.get("mulesoft") or {}
    outcome = details.get("outcome") or {}
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
    require(
        action.get("blockedErrorCode") == "INVALID_STATE",
        "Salesforce did not block the pre-approval action",
    )
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
    require(
        outcome.get("actionStatus") == "EXECUTED"
        and outcome.get("outcomeStatus") == "SUCCESS"
        and outcome.get("workItemStatus") == "COMPLETED",
        "The final governed outcome is incomplete",
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
            "agentforceExternalActionExecuted": agentforce[
                "externalActionExecuted"
            ],
            "salesforcePreApprovalAction": action["blockedErrorCode"],
            "mulesoftPreApprovalStatus": mulesoft["blockedStatus"],
            "mulesoftPreApprovalError": mulesoft["blockedErrorCode"],
            "mulesoftApprovedStatus": mulesoft["executionStatus"],
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
