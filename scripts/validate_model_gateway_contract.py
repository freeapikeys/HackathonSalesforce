#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from generate_model_gateway_contract import canonical_json, content_hash

ROOT = Path(__file__).resolve().parents[1]
GATEWAY_DIR = ROOT / "intelligence" / "model-gateway"
SCHEMA_PATH = GATEWAY_DIR / "schemas" / "model-gateway-v1.schema.json"
FIXTURE_PATH = GATEWAY_DIR / "fixtures" / "gateway-scenario-v1.json"

FIXTURE_TYPES = {
    "profiles": "modelProfile",
    "deployments": "modelDeployment",
    "policies": "routingPolicy",
    "routingRequests": "routingRequest",
    "routingDecisions": "routingDecision",
    "normalizedResponses": "generateResponse",
    "invocationAudits": "invocationAudit",
}
FORBIDDEN_REQUEST_KEYS = {
    "provider",
    "providerIdentifier",
    "model",
    "modelIdentifier",
    "deploymentKey",
    "endpoint",
}
FORBIDDEN_SECRET_KEYS = {
    "apiKey",
    "accessToken",
    "clientSecret",
    "credential",
    "password",
    "secret",
}
REQUIRED_POLICY_CHECKS = {
    "TENANT",
    "BUSINESS_UNIT",
    "PURPOSE",
    "PROFILE",
    "DATA_CLASSIFICATION",
    "RESIDENCY",
    "LANGUAGE",
    "CAPABILITY",
    "CONTEXT_WINDOW",
    "QUALITY",
    "LATENCY",
    "COST",
    "STATUS",
    "AVAILABILITY",
}


def walk_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for child in value.values():
            keys.update(walk_keys(child))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for child in value:
            keys.update(walk_keys(child))
        return keys
    return set()


def fixture_values(fixture: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = fixture[key]
    return list(value.values()) if isinstance(value, dict) else value


def validate_value(
    schema: dict[str, Any],
    registry: Registry,
    definition: str,
    value: dict[str, Any],
) -> None:
    validator = Draft202012Validator(
        {"$ref": f"{schema['$id']}#/$defs/{definition}"},
        registry=registry,
        format_checker=FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = " | ".join(
            (
                ".".join(str(part) for part in error.absolute_path)
                + f": {error.message}"
            )
            for error in errors
        )
        raise AssertionError(f"{definition} fixture is invalid: {details}")


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    registry = Registry().with_resource(
        schema["$id"],
        Resource.from_contents(schema),
    )

    validated = 0
    for fixture_key, definition in FIXTURE_TYPES.items():
        for value in fixture_values(fixture, fixture_key):
            validate_value(schema, registry, definition, value)
            validated += 1
    validate_value(
        schema,
        registry,
        "generateRequest",
        fixture["generateRequest"],
    )
    validated += 1
    extra_generate_requests = fixture.get("generateRequests", {})
    for request in extra_generate_requests.values():
        validate_value(schema, registry, "generateRequest", request)
        validated += 1

    deployments = fixture["deployments"]
    assert len(deployments) == 3
    assert len({item["providerIdentifier"] for item in deployments}) == 3
    assert len({item["adapterKey"] for item in deployments}) == 3
    assert {
        item["adapterInterfaceVersion"] for item in deployments
    } == {"hfs.generate.v1"}
    assert all(
        fixture["profiles"][0]["profileKey"] in item["qualifiedProfiles"]
        for item in deployments
    )
    deepseek_deployments = [
        item for item in deployments if item["providerIdentifier"] == "deepseek"
    ]
    assert len(deepseek_deployments) == 1
    assert deepseek_deployments[0]["operationalStatus"] == "UNAVAILABLE"

    request_keys: set[str] = set()
    for request in [
        fixture["generateRequest"],
        *extra_generate_requests.values(),
    ]:
        request_keys.update(walk_keys(request))
    assert not (request_keys & FORBIDDEN_REQUEST_KEYS), (
        "Provider-specific keys leaked into generate request: "
        + ", ".join(sorted(request_keys & FORBIDDEN_REQUEST_KEYS))
    )
    all_keys = walk_keys(fixture)
    assert not (all_keys & FORBIDDEN_SECRET_KEYS), (
        "Secret-like fields are forbidden in model gateway fixtures."
    )

    policy = fixture["policies"][0]
    assert set(policy["requiredChecks"]) == REQUIRED_POLICY_CHECKS
    assert fixture["routingRequests"]["primary"]["purpose"] in policy[
        "permittedPurposes"
    ]
    assert policy["candidatePriority"] == [
        item["deploymentKey"] for item in deployments
    ]
    decisions = fixture["routingDecisions"]
    assert decisions["primary"]["selectedDeploymentKey"] == (
        deployments[0]["deploymentKey"]
    )
    assert not decisions["primary"]["fallback"]
    assert decisions["fallback"]["selectedDeploymentKey"] == (
        deployments[1]["deploymentKey"]
    )
    assert decisions["fallback"]["fallback"]
    assert decisions["fallback"]["fallbackFromDeploymentKey"] == (
        deployments[0]["deploymentKey"]
    )
    assert decisions["noQualifiedDeployment"]["decision"] == (
        "NO_QUALIFIED_DEPLOYMENT"
    )
    assert decisions["noQualifiedDeployment"]["selectedDeploymentKey"] is None

    response_schema = fixture["generateRequest"]["responseSchema"]
    output_validator = Draft202012Validator(
        response_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )
    responses_by_id = {}
    for response in fixture["normalizedResponses"]:
        output_validator.validate(response["output"])
        responses_by_id[response["invocationId"]] = response
        assert response["correlationId"] == fixture["generateRequest"][
            "correlationId"
        ]

    generate_requests = [
        fixture["generateRequest"],
        *extra_generate_requests.values(),
    ]
    requests_by_profile = {
        request["profileKey"]: request for request in generate_requests
    }
    input_hashes_by_profile = {
        profile: content_hash(request)
        for profile, request in requests_by_profile.items()
    }
    failed_closed_input_hash = content_hash(
        fixture["routingRequests"]["noQualifiedDeployment"]
    )
    deployments_by_key = {
        item["deploymentKey"]: item for item in deployments
    }
    for audit in fixture["invocationAudits"]:
        expected_audit_input_hash = (
            failed_closed_input_hash
            if audit["status"] == "FAILED_CLOSED"
            else input_hashes_by_profile[audit["profileKey"]]
        )
        assert audit["inputHash"] == expected_audit_input_hash
        assert audit["policyVersion"] == policy["version"]
        expected_request = requests_by_profile.get(
            audit["profileKey"],
            fixture["generateRequest"],
        )
        assert audit["evidenceIds"] == expected_request["context"][
            "evidenceIds"
        ]
        for attempt in audit["attempts"]:
            deployment = deployments_by_key[attempt["deploymentKey"]]
            assert attempt["adapterKey"] == deployment["adapterKey"]
            assert attempt["deploymentVersion"] == deployment["version"]

        if audit["status"] == "SUCCEEDED":
            response = responses_by_id[audit["invocationId"]]
            assert audit["outputHash"] == content_hash(response["output"])
            assert audit["selectedDeploymentKey"] == response["deploymentKey"]
            assert audit["selectedDeploymentVersion"] == response[
                "deploymentVersion"
            ]
            assert audit["profileVersion"] == response["profileVersion"]
            assert audit["attempts"][-1]["status"] == "SUCCEEDED"
        else:
            assert audit["invocationId"] not in responses_by_id
            assert audit["selectedDeploymentKey"] is None
            assert audit["selectedDeploymentVersion"] is None
            assert audit["outputHash"] is None

    primary_audit = fixture["invocationAudits"][0]
    fallback_audit = fixture["invocationAudits"][1]
    failed_closed_audit = next(
        audit
        for audit in fixture["invocationAudits"]
        if audit["status"] == "FAILED_CLOSED"
    )
    assert not primary_audit["fallbackUsed"]
    assert len(primary_audit["attempts"]) == 1
    assert fallback_audit["fallbackUsed"]
    assert [item["status"] for item in fallback_audit["attempts"]] == [
        "UNAVAILABLE",
        "SUCCEEDED",
    ]
    assert fallback_audit["attempts"][0]["retryable"]
    assert failed_closed_audit["status"] == "FAILED_CLOSED"
    assert not failed_closed_audit["fallbackUsed"]
    assert {
        item["status"] for item in failed_closed_audit["attempts"]
    } == {"POLICY_REJECTED"}
    assert not any(
        item["retryable"] for item in failed_closed_audit["attempts"]
    )
    nexavenu_response = next(
        response
        for response in fixture["normalizedResponses"]
        if response["profileKey"] == "nexavenu-revenue-recommendation"
    )
    assert nexavenu_response["output"]["assumptions"]
    assert nexavenu_response["output"]["requiresHumanApproval"]
    assert fixture["contractVersion"] == "1.0.0"
    assert canonical_json(fixture)

    print(
        "Model gateway contract is valid "
        f"({validated} typed fixtures, 2 active mock deployments, "
        "1 disabled DeepSeek deployment)."
    )


if __name__ == "__main__":
    main()
