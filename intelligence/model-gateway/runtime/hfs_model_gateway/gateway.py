from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable

from .adapters import AdapterUnavailable, ScriptedMockAdapter
from .contract import (
    ModelContractError,
    ModelGatewayContract,
    content_hash,
)
from .router import DeterministicRouter


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class GatewayResult:
    decision: dict[str, Any]
    response: dict[str, Any] | None
    audit: dict[str, Any]


class ModelGateway:
    def __init__(
        self,
        *,
        contract: ModelGatewayContract,
        router: DeterministicRouter,
        adapters: dict[str, ScriptedMockAdapter],
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self.contract = contract
        self.router = router
        self.adapters = adapters
        self.clock = clock
        self._invocation_sequence = 0
        for deployment in router.deployments.values():
            adapter_key = deployment["adapterKey"]
            if adapter_key not in adapters:
                raise ValueError(
                    f"No adapter is configured for {adapter_key}."
                )
            if (
                adapters[adapter_key].interface_version
                != deployment["adapterInterfaceVersion"]
            ):
                raise ValueError(
                    f"Adapter interface mismatch for {adapter_key}."
                )

    def generate(
        self,
        routing_request: dict[str, Any],
        generate_request: dict[str, Any],
    ) -> GatewayResult:
        self.contract.validate("routingRequest", routing_request)
        self.contract.validate("generateRequest", generate_request)
        self._validate_request_pair(routing_request, generate_request)

        self._invocation_sequence += 1
        invocation_id = f"runtime-invocation-{self._invocation_sequence:04d}"
        excluded: set[str] = set()
        attempts: list[dict[str, Any]] = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_latency_ms = 0
        total_cost_usd = 0.0

        while True:
            decision = self.router.route(
                routing_request,
                excluded_deployments=excluded,
            )
            if decision["decision"] == "NO_QUALIFIED_DEPLOYMENT":
                if not attempts:
                    attempts = self._policy_rejection_attempts(decision)
                audit = self._audit(
                    invocation_id=invocation_id,
                    routing_request=routing_request,
                    generate_request=generate_request,
                    decision=decision,
                    attempts=attempts,
                    response=None,
                    totals=(
                        total_input_tokens,
                        total_output_tokens,
                        total_latency_ms,
                        total_cost_usd,
                    ),
                )
                return GatewayResult(decision, None, audit)

            deployment_key = decision["selectedDeploymentKey"]
            deployment = self.router.deployments[deployment_key]
            adapter = self.adapters[deployment["adapterKey"]]
            started_at = self.clock()

            try:
                adapter_result = adapter.generate(generate_request)
            except AdapterUnavailable:
                attempts.append(
                    self._attempt(
                        sequence=len(attempts) + 1,
                        deployment=deployment,
                        started_at=started_at,
                        status="UNAVAILABLE",
                        retryable=True,
                        failure_code="DEPLOYMENT_UNAVAILABLE",
                    )
                )
                excluded.add(deployment_key)
                continue

            total_input_tokens += adapter_result.input_tokens
            total_output_tokens += adapter_result.output_tokens
            total_latency_ms += adapter_result.latency_ms
            total_cost_usd += adapter_result.cost_usd
            try:
                self.contract.validate_output(
                    generate_request["responseSchema"],
                    adapter_result.output,
                )
            except ModelContractError:
                attempts.append(
                    self._attempt(
                        sequence=len(attempts) + 1,
                        deployment=deployment,
                        started_at=started_at,
                        status="INVALID_OUTPUT",
                        retryable=False,
                        failure_code="OUTPUT_SCHEMA_INVALID",
                    )
                )
                excluded.add(deployment_key)
                continue

            attempts.append(
                self._attempt(
                    sequence=len(attempts) + 1,
                    deployment=deployment,
                    started_at=started_at,
                    status="SUCCEEDED",
                    retryable=False,
                    failure_code=None,
                )
            )
            response = {
                "contractVersion": generate_request["contractVersion"],
                "correlationId": generate_request["correlationId"],
                "invocationId": invocation_id,
                "profileKey": generate_request["profileKey"],
                "profileVersion": generate_request["profileVersion"],
                "deploymentKey": deployment_key,
                "deploymentVersion": deployment["version"],
                "adapterInterfaceVersion": adapter.interface_version,
                "output": deepcopy(adapter_result.output),
                "finishReason": "STOP",
                "outputSchemaValid": True,
                "safetyStatus": "PASSED",
            }
            self.contract.validate("generateResponse", response)
            audit = self._audit(
                invocation_id=invocation_id,
                routing_request=routing_request,
                generate_request=generate_request,
                decision=decision,
                attempts=attempts,
                response=response,
                totals=(
                    total_input_tokens,
                    total_output_tokens,
                    total_latency_ms,
                    total_cost_usd,
                ),
            )
            return GatewayResult(decision, response, audit)

    def _validate_request_pair(
        self,
        routing_request: dict[str, Any],
        generate_request: dict[str, Any],
    ) -> None:
        equal_fields = (
            "contractVersion",
            "correlationId",
            "tenantKey",
            "userId",
            "purpose",
            "agentKey",
            "profileKey",
        )
        for field in equal_fields:
            if routing_request[field] != generate_request[field]:
                raise ModelContractError(
                    f"Routing and generation requests disagree on {field}."
                )
        if (
            routing_request["dataClassification"]
            != generate_request["context"]["dataClassification"]
        ):
            raise ModelContractError(
                "Routing and generation data classifications differ."
            )

    def _attempt(
        self,
        *,
        sequence: int,
        deployment: dict[str, Any],
        started_at: str,
        status: str,
        retryable: bool,
        failure_code: str | None,
    ) -> dict[str, Any]:
        return {
            "sequence": sequence,
            "deploymentKey": deployment["deploymentKey"],
            "deploymentVersion": deployment["version"],
            "adapterKey": deployment["adapterKey"],
            "startedAt": started_at,
            "completedAt": self.clock(),
            "status": status,
            "retryable": retryable,
            "failureCode": failure_code,
        }

    def _policy_rejection_attempts(
        self,
        decision: dict[str, Any],
    ) -> list[dict[str, Any]]:
        failed_by_deployment: dict[str, str] = {}
        for check in decision["checks"]:
            if not check["passed"]:
                failed_by_deployment.setdefault(
                    check["deploymentKey"],
                    check["reasonCode"],
                )
        attempts = []
        for deployment_key in self.router.policy["candidatePriority"]:
            if deployment_key not in failed_by_deployment:
                continue
            deployment = self.router.deployments[deployment_key]
            now = self.clock()
            attempts.append(
                self._attempt(
                    sequence=len(attempts) + 1,
                    deployment=deployment,
                    started_at=now,
                    status="POLICY_REJECTED",
                    retryable=False,
                    failure_code=failed_by_deployment[deployment_key],
                )
            )
        return attempts

    def _audit(
        self,
        *,
        invocation_id: str,
        routing_request: dict[str, Any],
        generate_request: dict[str, Any],
        decision: dict[str, Any],
        attempts: list[dict[str, Any]],
        response: dict[str, Any] | None,
        totals: tuple[int, int, int, float],
    ) -> dict[str, Any]:
        input_tokens, output_tokens, latency_ms, cost_usd = totals
        succeeded = response is not None
        audit = {
            "contractVersion": generate_request["contractVersion"],
            "invocationId": invocation_id,
            "correlationId": generate_request["correlationId"],
            "tenantKey": generate_request["tenantKey"],
            "userId": generate_request["userId"],
            "purpose": generate_request["purpose"],
            "agentKey": generate_request["agentKey"],
            "profileKey": generate_request["profileKey"],
            "profileVersion": generate_request["profileVersion"],
            "policyKey": decision["policyKey"],
            "policyVersion": decision["policyVersion"],
            "selectedDeploymentKey": (
                response["deploymentKey"] if response else None
            ),
            "selectedDeploymentVersion": (
                response["deploymentVersion"] if response else None
            ),
            "promptVersion": generate_request["promptVersion"],
            "retrievalVersion": generate_request["retrievalVersion"],
            "inputHash": content_hash(generate_request),
            "outputHash": (
                content_hash(response["output"]) if response else None
            ),
            "evidenceIds": generate_request["context"]["evidenceIds"],
            "attempts": deepcopy(attempts),
            "fallbackUsed": succeeded
            and (decision["fallback"] or len(attempts) > 1),
            "inputTokens": input_tokens,
            "outputTokens": output_tokens,
            "latencyMs": latency_ms,
            "costUsd": round(cost_usd, 6),
            "safetyStatus": "PASSED" if succeeded else "NOT_RUN",
            "outputSchemaValid": succeeded,
            "retentionMode": (
                "POLICY_APPROVED_CONTENT"
                if generate_request["invocationPolicy"]["retainContent"]
                else "HASHES_ONLY"
            ),
            "status": "SUCCEEDED" if succeeded else "FAILED_CLOSED",
            "completedAt": self.clock(),
        }
        self.contract.validate("invocationAudit", audit)
        return audit
