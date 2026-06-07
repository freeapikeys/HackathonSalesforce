#!/usr/bin/env python3

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    fixtures = json.loads(FIXTURE_PATH.read_text())
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(fixtures)

    action_names = {
        definition["action"] for definition in fixtures["actionCatalog"]
    }
    require(
        action_names
        == {
            "EXPLAIN_RELATIONSHIP_CASE",
            "DRAFT_RELATIONSHIP_RECOMMENDATION",
            "REQUEST_HUMAN_APPROVAL",
        },
        "The executable action catalog changed.",
    )

    scenario_names = set()
    for scenario in fixtures["scenarios"]:
        name = scenario["name"]
        request = scenario["request"]
        response = scenario["response"]
        require(name not in scenario_names, f"Duplicate scenario: {name}")
        scenario_names.add(name)
        require(
            response["action"] == request["action"],
            f"{name}: response action does not match request.",
        )
        for identifier in ("contractVersion", "tenantKey", "correlationId"):
            require(
                response[identifier] == request[identifier],
                f"{name}: {identifier} was not preserved.",
            )
        require(
            response["audit"]["purpose"] == request["purpose"],
            f"{name}: purpose was not preserved in audit.",
        )
        require(
            response["audit"]["externalActionExecuted"] is False,
            f"{name}: an Agentforce action claimed external execution.",
        )

        citation_ids = {
            citation["evidenceId"] for citation in response["citations"]
        }
        fact_ids = {fact["factId"] for fact in response["facts"]}
        for fact in response["facts"]:
            require(
                set(fact["evidenceIds"]) <= citation_ids,
                f"{name}: fact cites evidence not returned to the user.",
            )
        for inference in response["inferences"]:
            require(
                set(inference["basisFactIds"]) <= fact_ids,
                f"{name}: inference is not grounded in returned facts.",
            )

        recommendation = response["recommendation"]
        if recommendation:
            require(
                set(recommendation["evidenceIds"]) <= citation_ids,
                f"{name}: recommendation cites inaccessible evidence.",
            )
            require(
                recommendation["requiresHumanApproval"] is True,
                f"{name}: recommendation bypasses human approval.",
            )
            require(
                response["audit"]["modelInvocationId"]
                == recommendation["modelInvocationId"],
                f"{name}: model invocation provenance was not preserved.",
            )

        if response["status"] == "SUCCESS":
            require(response["refusal"] is None, f"{name}: success has refusal.")
            require(not response["errors"], f"{name}: success has errors.")
        elif response["status"] == "REFUSED":
            require(response["refusal"] is not None, f"{name}: refusal missing.")
            require(
                not response["facts"]
                and not response["inferences"]
                and not response["citations"]
                and response["recommendation"] is None
                and response["approval"] is None,
                f"{name}: refusal disclosed protected action content.",
            )
        else:
            require(response["errors"], f"{name}: error details missing.")

        if request["action"] == "REQUEST_HUMAN_APPROVAL" and response[
            "status"
        ] == "SUCCESS":
            require(
                response["approval"]["status"] == "PENDING",
                f"{name}: approval was not left pending for a human.",
            )
        if request["action"] == "EXECUTE_EXTERNAL_ACTION":
            require(
                response["status"] == "REFUSED"
                and response["refusal"]["code"] == "UNAUTHORIZED_ACTION",
                f"{name}: protected external execution did not fail closed.",
            )

    required_scenarios = {
        "accessible-grounded-explanation",
        "grounded-recommendation",
        "pending-human-approval",
        "inaccessible-evidence-refusal",
        "unauthorized-external-action-refusal",
        "no-qualified-model-refusal",
        "invalid-approval-request-error",
    }
    require(
        required_scenarios <= scenario_names,
        "A material Agentforce contract scenario is missing.",
    )
    print(
        "Agentforce action contract is valid "
        f"({len(fixtures['actionCatalog'])} actions, "
        f"{len(fixtures['scenarios'])} scenarios)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
