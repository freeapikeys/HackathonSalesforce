from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Callable

from .contract import ModelGatewayContract


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class DeterministicRouter:
    def __init__(
        self,
        *,
        contract: ModelGatewayContract,
        profile: dict[str, Any],
        deployments: list[dict[str, Any]],
        policy: dict[str, Any],
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self.contract = contract
        contract.validate("modelProfile", profile)
        contract.validate("routingPolicy", policy)
        for deployment in deployments:
            contract.validate("modelDeployment", deployment)
        self.profile = deepcopy(profile)
        self.deployments = {
            item["deploymentKey"]: deepcopy(item) for item in deployments
        }
        self.policy = deepcopy(policy)
        self.clock = clock
        if self.policy["profileKey"] != self.profile["profileKey"]:
            raise ValueError("Routing policy and model profile do not match.")
        missing = set(self.policy["candidatePriority"]) - set(self.deployments)
        if missing:
            raise ValueError(
                "Routing policy references missing deployments: "
                + ", ".join(sorted(missing))
            )

    def route(
        self,
        request: dict[str, Any],
        *,
        excluded_deployments: set[str] | None = None,
    ) -> dict[str, Any]:
        self.contract.validate("routingRequest", request)
        excluded = set(request["unavailableDeploymentKeys"])
        excluded.update(excluded_deployments or set())
        all_checks: list[dict[str, Any]] = []
        selected: dict[str, Any] | None = None
        selected_index = -1

        for index, deployment_key in enumerate(
            self.policy["candidatePriority"]
        ):
            deployment = self.deployments[deployment_key]
            checks = self._checks(request, deployment, excluded)
            all_checks.extend(checks)
            if all(item["passed"] for item in checks):
                selected = deployment
                selected_index = index
                break

        decision = {
            "contractVersion": request["contractVersion"],
            "correlationId": request["correlationId"],
            "policyKey": self.policy["policyKey"],
            "policyVersion": self.policy["version"],
            "profileKey": self.profile["profileKey"],
            "profileVersion": self.profile["version"],
            "decision": (
                "SELECTED"
                if selected is not None
                else "NO_QUALIFIED_DEPLOYMENT"
            ),
            "selectedDeploymentKey": (
                selected["deploymentKey"] if selected else None
            ),
            "selectedDeploymentVersion": (
                selected["version"] if selected else None
            ),
            "fallback": selected_index > 0,
            "fallbackFromDeploymentKey": (
                self.policy["candidatePriority"][0]
                if selected_index > 0
                else None
            ),
            "checks": all_checks,
            "decidedAt": self.clock(),
        }
        self.contract.validate("routingDecision", decision)
        return decision

    def _checks(
        self,
        request: dict[str, Any],
        deployment: dict[str, Any],
        excluded: set[str],
    ) -> list[dict[str, Any]]:
        metric_key = self.profile["qualityObjective"]["metricKey"]
        values = {
            "TENANT": (
                request["tenantKey"] == self.policy["tenantKey"],
                "TENANT_PERMITTED",
                "TENANT_NOT_PERMITTED",
            ),
            "BUSINESS_UNIT": (
                self.policy["businessUnit"] is None
                or request["businessUnit"] == self.policy["businessUnit"],
                "BUSINESS_UNIT_PERMITTED",
                "BUSINESS_UNIT_NOT_PERMITTED",
            ),
            "PURPOSE": (
                request["purpose"] in self.policy["permittedPurposes"],
                "PURPOSE_PERMITTED",
                "PURPOSE_NOT_PERMITTED",
            ),
            "PROFILE": (
                request["profileKey"] == self.profile["profileKey"]
                and request["profileKey"] in deployment["qualifiedProfiles"],
                "PROFILE_QUALIFIED",
                "PROFILE_NOT_QUALIFIED",
            ),
            "DATA_CLASSIFICATION": (
                request["dataClassification"]
                in self.profile["permittedDataClassifications"]
                and request["dataClassification"]
                in deployment["permittedDataClassifications"],
                "DATA_CLASSIFICATION_PERMITTED",
                "DATA_CLASSIFICATION_NOT_PERMITTED",
            ),
            "RESIDENCY": (
                request["residencyRegion"] in deployment["residencyRegions"],
                "RESIDENCY_PERMITTED",
                "RESIDENCY_NOT_PERMITTED",
            ),
            "LANGUAGE": (
                request["language"] in deployment["supportedLanguages"],
                "LANGUAGE_SUPPORTED",
                "LANGUAGE_NOT_SUPPORTED",
            ),
            "CAPABILITY": (
                set(request["requiredCapabilities"])
                <= set(deployment["capabilities"]),
                "CAPABILITIES_SUPPORTED",
                "CAPABILITIES_NOT_SUPPORTED",
            ),
            "CONTEXT_WINDOW": (
                deployment["contextWindowTokens"]
                >= max(
                    request["requiredContextTokens"],
                    self.profile["minimumContextTokens"],
                ),
                "CONTEXT_WINDOW_SUFFICIENT",
                "CONTEXT_WINDOW_INSUFFICIENT",
            ),
            "QUALITY": (
                deployment["qualityScores"].get(metric_key, 0)
                >= self.profile["qualityObjective"]["minimumScore"],
                "QUALITY_QUALIFIED",
                "QUALITY_NOT_QUALIFIED",
            ),
            "LATENCY": (
                deployment["estimatedLatencyMs"]
                <= min(
                    request["maximumLatencyMs"],
                    self.profile["maximumLatencyMs"],
                ),
                "LATENCY_WITHIN_LIMIT",
                "LATENCY_LIMIT_EXCEEDED",
            ),
            "COST": (
                deployment["estimatedCostUsd"]
                <= min(
                    request["maximumCostUsd"],
                    self.profile["maximumCostUsd"],
                ),
                "COST_WITHIN_LIMIT",
                "COST_LIMIT_EXCEEDED",
            ),
            "STATUS": (
                deployment["operationalStatus"] == "ACTIVE",
                "DEPLOYMENT_ACTIVE",
                "DEPLOYMENT_NOT_ACTIVE",
            ),
            "AVAILABILITY": (
                deployment["deploymentKey"] not in excluded,
                "DEPLOYMENT_AVAILABLE",
                "DEPLOYMENT_UNAVAILABLE",
            ),
        }
        checks = []
        for check_name in self.policy["requiredChecks"]:
            passed, pass_code, fail_code = values[check_name]
            checks.append(
                {
                    "deploymentKey": deployment["deploymentKey"],
                    "check": check_name,
                    "passed": passed,
                    "reasonCode": pass_code if passed else fail_code,
                }
            )
        return checks
