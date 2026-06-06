from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable

from .contract import ContractValidationError, IntegrationContract

CONTRACT_VERSION = "1.0.0"


def canonical_hash(value: dict[str, Any]) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class MockHttpResponse:
    status: int
    body: dict[str, Any]
    headers: dict[str, str]


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


class RetryableCallbackFailure(RuntimeError):
    pass


class AdapterIdempotencyConflict(RuntimeError):
    pass


class RetryableDependencyFailure(RuntimeError):
    pass


class MockCallbackTransport:
    """Replaceable callback transport with deterministic failure injection."""

    def __init__(
        self,
        contract: IntegrationContract,
        failures_by_operation: dict[str, int] | None = None,
    ) -> None:
        self.contract = contract
        self.failures_by_operation = dict(failures_by_operation or {})
        self.attempts_by_operation: dict[str, int] = {}
        self.received: list[dict[str, Any]] = []

    def post(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> None:
        self.contract.validate("OperationCallback", payload)
        operation = payload["operation"]
        self.attempts_by_operation[operation] = (
            self.attempts_by_operation.get(operation, 0) + 1
        )

        failures_remaining = self.failures_by_operation.get(operation, 0)
        if failures_remaining > 0:
            self.failures_by_operation[operation] = failures_remaining - 1
            raise RetryableCallbackFailure(
                f"Injected callback failure for {operation}"
            )

        self.received.append(
            {
                "url": url,
                "headers": deepcopy(headers),
                "payload": deepcopy(payload),
            }
        )


class MockSourceAdapter:
    """Preserves accepted source events without source-specific behavior."""

    def __init__(self) -> None:
        self.events: dict[str, dict[str, Any]] = {}

    def preserve(self, event: dict[str, Any]) -> None:
        self.events[event["id"]] = deepcopy(event)


class MockOutcomeAdapter:
    """Replaceable outcome store with deterministic retryable failures."""

    def __init__(self, failures_remaining: int = 0) -> None:
        if failures_remaining < 0:
            raise ValueError("failures_remaining cannot be negative")
        self.failures_remaining = failures_remaining
        self.outcomes: dict[str, dict[str, Any]] = {}

    def record(self, outcome: dict[str, Any]) -> None:
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise RetryableDependencyFailure(
                "Injected temporary outcome-store failure."
            )
        self.outcomes[outcome["externalKey"]] = deepcopy(outcome)


class MockWriteBackAdapter:
    """Executes only registered approved actions and emits source outcomes."""

    def __init__(self) -> None:
        self.approvals: dict[str, dict[str, str]] = {}
        self.source_records: dict[str, dict[str, Any]] = {}
        self._executions: dict[
            tuple[str, str], tuple[str, dict[str, Any]]
        ] = {}

    def register_approval(
        self,
        *,
        approval_id: str,
        tenant_key: str,
        recommendation_id: str,
        action_id: str,
        status: str = "APPROVED",
    ) -> None:
        self.approvals[approval_id] = {
            "tenantKey": tenant_key,
            "recommendationId": recommendation_id,
            "actionId": action_id,
            "status": status,
        }

    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        approval = self.approvals.get(action["approvalId"])
        if approval is None or approval["status"] != "APPROVED":
            raise PermissionError("The linked approval is not approved.")
        for field in ("tenantKey", "recommendationId", "actionId"):
            if approval[field] != action[field]:
                raise PermissionError(
                    f"The linked approval does not match {field}."
                )

        scope = (action["tenantKey"], action["idempotencyKey"])
        action_hash = canonical_hash(action)
        prior = self._executions.get(scope)
        if prior is not None:
            prior_hash, prior_outcome = prior
            if prior_hash != action_hash:
                raise AdapterIdempotencyConflict(
                    "The adapter idempotency key was reused for different content."
                )
            return deepcopy(prior_outcome)

        source_record_id = (
            "mock-writeback-" + canonical_hash(action)[:16]
        )
        self.source_records[source_record_id] = {
            "sourceRecordId": source_record_id,
            "sourceSystem": action["sourceSystem"],
            "actionId": action["actionId"],
            "actionType": action["actionType"],
            "payload": deepcopy(action["payload"]),
        }
        outcome = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": action["tenantKey"],
            "correlationId": action["correlationId"],
            "purpose": "CAPTURE_APPROVED_ACTION_OUTCOME",
            "externalKey": f"outcome-{action['externalKey']}",
            "idempotencyKey": f"outcome-{action['idempotencyKey']}",
            "actionId": action["actionId"],
            "sourceEventId": f"event-{source_record_id}",
            "sourceSystem": action["sourceSystem"],
            "sourceRecordId": source_record_id,
            "outcomeType": "ACTION_EXECUTED",
            "status": "SUCCESS",
            "observedAt": timestamp(),
            "summary": "The approved mock action was executed.",
            "metricKey": "action_execution_success",
            "metricValue": 1,
        }
        self._executions[scope] = (action_hash, deepcopy(outcome))
        return outcome


class MockIntegrationApi:
    PATHS = {
        "/v1/events": "ingestEvent",
        "/v1/context/queries": "retrieveContext",
        "/v1/actions/executions": "executeApprovedAction",
        "/v1/outcomes/callbacks": "receiveOutcomeCallback",
    }

    def __init__(
        self,
        *,
        contract: IntegrationContract,
        source_adapter: MockSourceAdapter,
        write_back_adapter: MockWriteBackAdapter,
        outcome_adapter: MockOutcomeAdapter,
        callback_transport: MockCallbackTransport,
        retry_policy: RetryPolicy,
    ) -> None:
        self.contract = contract
        self.source_adapter = source_adapter
        self.write_back_adapter = write_back_adapter
        self.outcome_adapter = outcome_adapter
        self.callback_transport = callback_transport
        self.retry_policy = retry_policy
        self.pending_callbacks: list[dict[str, Any]] = []
        self._idempotency: dict[
            tuple[str, str, str], tuple[str, MockHttpResponse]
        ] = {}

    @property
    def outcomes(self) -> dict[str, dict[str, Any]]:
        return self.outcome_adapter.outcomes

    def request(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse:
        if method.upper() != "POST" or path not in self.PATHS:
            return MockHttpResponse(
                404,
                {"message": "Mock route not found."},
                {},
            )

        handlers: dict[
            str,
            Callable[[dict[str, str], dict[str, Any]], MockHttpResponse],
        ] = {
            "ingestEvent": self._ingest_event,
            "retrieveContext": self._retrieve_context,
            "executeApprovedAction": self._execute_action,
            "receiveOutcomeCallback": self._receive_outcome,
        }
        return handlers[self.PATHS[path]](headers, body)

    def _common_error(
        self,
        *,
        operation: str,
        headers: dict[str, str],
        body: dict[str, Any],
        status: int,
        code: str,
        message: str,
        retryable: bool = False,
        field_name: str | None = None,
    ) -> MockHttpResponse:
        tenant_key = headers.get("X-Tenant-Id") or body.get("tenantKey")
        tenant_key = tenant_key or body.get("hfstenantid") or "unknown-tenant"
        correlation_id = (
            headers.get("X-Correlation-Id")
            or body.get("correlationId")
            or body.get("hfscorrelationid")
            or "00000000-0000-4000-8000-000000000000"
        )
        response = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": tenant_key,
            "correlationId": correlation_id,
            "operation": operation,
            "success": False,
            "errors": [
                {
                    "code": code,
                    "message": message,
                    "fieldName": field_name,
                    "retryable": retryable,
                    "details": None,
                }
            ],
        }
        self.contract.validate("ErrorResponse", response)
        response_headers = {"X-Correlation-Id": correlation_id}
        if retryable:
            response_headers["Retry-After"] = "1"
        return MockHttpResponse(status, response, response_headers)

    def _validated_headers(
        self,
        *,
        operation: str,
        headers: dict[str, str],
        body: dict[str, Any],
        idempotent: bool,
    ) -> MockHttpResponse | None:
        tenant_field = (
            "hfstenantid" if operation == "INGEST_EVENT" else "tenantKey"
        )
        correlation_field = (
            "hfscorrelationid"
            if operation == "INGEST_EVENT"
            else "correlationId"
        )
        required_headers = ["X-Tenant-Id", "X-Correlation-Id"]
        if idempotent:
            required_headers.append("X-Idempotency-Key")

        missing = [name for name in required_headers if not headers.get(name)]
        if missing:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="VALIDATION_FAILED",
                message=f"Required header {missing[0]} is missing.",
                field_name=missing[0],
            )
        if headers["X-Tenant-Id"] != body.get(tenant_field):
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="TENANT_MISMATCH",
                message="The tenant header does not match the request body.",
                field_name="X-Tenant-Id",
            )
        if headers["X-Correlation-Id"] != body.get(correlation_field):
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="VALIDATION_FAILED",
                message=(
                    "The correlation header does not match the request body."
                ),
                field_name="X-Correlation-Id",
            )
        if idempotent:
            body_key = (
                body.get("hfsidempotencykey")
                if operation == "INGEST_EVENT"
                else body.get("idempotencyKey")
            )
            if headers["X-Idempotency-Key"] != body_key:
                return self._common_error(
                    operation=operation,
                    headers=headers,
                    body=body,
                    status=409,
                    code="IDEMPOTENCY_CONFLICT",
                    message=(
                        "The idempotency header does not match the request body."
                    ),
                    field_name="X-Idempotency-Key",
                )
        return None

    def _schema_error(
        self,
        *,
        operation: str,
        headers: dict[str, str],
        body: dict[str, Any],
        error: ContractValidationError,
    ) -> MockHttpResponse:
        return self._common_error(
            operation=operation,
            headers=headers,
            body=body,
            status=422,
            code="VALIDATION_FAILED",
            message=error.messages[0],
        )

    def _idempotency_result(
        self,
        *,
        operation: str,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse | None:
        scope = (
            headers["X-Tenant-Id"],
            operation,
            headers["X-Idempotency-Key"],
        )
        prior = self._idempotency.get(scope)
        if prior is None:
            return None
        prior_hash, prior_response = prior
        if prior_hash != canonical_hash(body):
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="IDEMPOTENCY_CONFLICT",
                message=(
                    "The idempotency key was already used for different content."
                ),
                field_name="X-Idempotency-Key",
            )

        replay = deepcopy(prior_response.body)
        replay["replayed"] = True
        if operation == "INGEST_EVENT":
            replay["intakeResult"] = "DUPLICATE"
        return MockHttpResponse(
            prior_response.status,
            replay,
            deepcopy(prior_response.headers),
        )

    def _remember(
        self,
        *,
        operation: str,
        headers: dict[str, str],
        body: dict[str, Any],
        response: MockHttpResponse,
    ) -> None:
        scope = (
            headers["X-Tenant-Id"],
            operation,
            headers["X-Idempotency-Key"],
        )
        self._idempotency[scope] = (canonical_hash(body), deepcopy(response))

    def _ingest_event(
        self,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse:
        operation = "INGEST_EVENT"
        try:
            self.contract.validate("EventEnvelope", body)
        except ContractValidationError as error:
            return self._schema_error(
                operation=operation,
                headers=headers,
                body=body,
                error=error,
            )
        actual_content_hash = f"sha256:{canonical_hash(body['data'])}"
        if body["hfscontenthash"] != actual_content_hash:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="VALIDATION_FAILED",
                message="The declared content hash does not match event data.",
                field_name="hfscontenthash",
            )
        header_error = self._validated_headers(
            operation=operation,
            headers=headers,
            body=body,
            idempotent=True,
        )
        if header_error:
            return header_error
        replay = self._idempotency_result(
            operation=operation,
            headers=headers,
            body=body,
        )
        if replay:
            return replay

        self.source_adapter.preserve(body)
        response_body = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": body["hfstenantid"],
            "correlationId": body["hfscorrelationid"],
            "eventId": body["id"],
            "intakeResult": "ACCEPTED",
            "replayed": False,
            "observedAt": body["hfsobservedat"],
        }
        self.contract.validate("EventIntakeResponse", response_body)
        response = MockHttpResponse(
            202,
            response_body,
            {"X-Correlation-Id": body["hfscorrelationid"]},
        )
        self._remember(
            operation=operation,
            headers=headers,
            body=body,
            response=response,
        )
        self._request_callback(headers, operation, response_body)
        return response

    def _retrieve_context(
        self,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse:
        operation = "READ_CONTEXT"
        try:
            self.contract.validate("ContextRequest", body)
        except ContractValidationError as error:
            return self._schema_error(
                operation=operation,
                headers=headers,
                body=body,
                error=error,
            )
        header_error = self._validated_headers(
            operation=operation,
            headers=headers,
            body=body,
            idempotent=False,
        )
        if header_error:
            return header_error

        response_body = deepcopy(
            self.contract.example("retrieveContext", "success")
        )
        response_body["tenantKey"] = body["tenantKey"]
        response_body["correlationId"] = body["correlationId"]
        self.contract.validate("ContextResponse", response_body)
        response = MockHttpResponse(
            200,
            response_body,
            {"X-Correlation-Id": body["correlationId"]},
        )
        self._request_callback(headers, operation, response_body)
        return response

    def _execute_action(
        self,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse:
        operation = "EXECUTE_APPROVED_ACTION"
        try:
            self.contract.validate("ActionExecutionRequest", body)
        except ContractValidationError as error:
            return self._schema_error(
                operation=operation,
                headers=headers,
                body=body,
                error=error,
            )
        header_error = self._validated_headers(
            operation=operation,
            headers=headers,
            body=body,
            idempotent=True,
        )
        if header_error:
            return header_error
        replay = self._idempotency_result(
            operation=operation,
            headers=headers,
            body=body,
        )
        if replay:
            return replay

        try:
            outcome = self.write_back_adapter.execute(body)
        except PermissionError as error:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=403,
                code="PERMISSION_DENIED",
                message=str(error),
            )
        except AdapterIdempotencyConflict as error:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="IDEMPOTENCY_CONFLICT",
                message=str(error),
                field_name="X-Idempotency-Key",
            )

        outcome_headers = {
            "X-Tenant-Id": outcome["tenantKey"],
            "X-Correlation-Id": outcome["correlationId"],
            "X-Idempotency-Key": outcome["idempotencyKey"],
        }
        outcome_response = self.request(
            "POST",
            "/v1/outcomes/callbacks",
            outcome_headers,
            outcome,
        )
        if outcome_response.status != 200:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=503,
                code="RETRYABLE_DEPENDENCY_FAILURE",
                message="The generated outcome callback could not be recorded.",
                retryable=True,
            )

        response_body = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": body["tenantKey"],
            "correlationId": body["correlationId"],
            "operation": operation,
            "success": True,
            "replayed": False,
            "actionId": body["actionId"],
            "sourceSystem": body["sourceSystem"],
            "status": "QUEUED",
            "acceptedAt": timestamp(),
            "errors": [],
        }
        self.contract.validate("ActionExecutionResponse", response_body)
        response = MockHttpResponse(
            202,
            response_body,
            {"X-Correlation-Id": body["correlationId"]},
        )
        self._remember(
            operation=operation,
            headers=headers,
            body=body,
            response=response,
        )
        callback_result = {
            "actionId": body["actionId"],
            "sourceSystem": body["sourceSystem"],
            "sourceRecordId": outcome["sourceRecordId"],
            "outcomeId": outcome_response.body["outcomeId"],
            "status": "EXECUTED",
        }
        self._request_callback(headers, operation, callback_result)
        return response

    def _receive_outcome(
        self,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse:
        operation = "CAPTURE_OUTCOME"
        try:
            self.contract.validate("OutcomeCallbackRequest", body)
        except ContractValidationError as error:
            return self._schema_error(
                operation=operation,
                headers=headers,
                body=body,
                error=error,
            )
        header_error = self._validated_headers(
            operation=operation,
            headers=headers,
            body=body,
            idempotent=True,
        )
        if header_error:
            return header_error
        replay = self._idempotency_result(
            operation=operation,
            headers=headers,
            body=body,
        )
        if replay:
            return replay

        outcome_id = body["externalKey"]
        try:
            self.outcome_adapter.record(body)
        except RetryableDependencyFailure as error:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=503,
                code="RETRYABLE_DEPENDENCY_FAILURE",
                message=str(error),
                retryable=True,
            )
        response_body = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": body["tenantKey"],
            "correlationId": body["correlationId"],
            "operation": operation,
            "success": True,
            "replayed": False,
            "outcomeId": outcome_id,
            "actionId": body["actionId"],
            "status": "RECORDED",
            "recordedAt": timestamp(),
            "errors": [],
        }
        self.contract.validate("OutcomeCallbackResponse", response_body)
        response = MockHttpResponse(
            200,
            response_body,
            {"X-Correlation-Id": body["correlationId"]},
        )
        self._remember(
            operation=operation,
            headers=headers,
            body=body,
            response=response,
        )
        self._request_callback(headers, operation, response_body)
        return response

    def _request_callback(
        self,
        headers: dict[str, str],
        operation: str,
        result: dict[str, Any],
    ) -> None:
        callback_url = headers.get("X-Callback-Url")
        if not callback_url:
            return
        payload = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": headers["X-Tenant-Id"],
            "correlationId": headers["X-Correlation-Id"],
            "operation": operation,
            "status": "COMPLETED",
            "completedAt": timestamp(),
            "retryable": False,
            "result": deepcopy(result),
            "errors": [],
        }
        callback = {
            "url": callback_url,
            "headers": {
                "X-Tenant-Id": headers["X-Tenant-Id"],
                "X-Correlation-Id": headers["X-Correlation-Id"],
            },
            "payload": payload,
        }
        if not self._deliver_callback(callback):
            self.pending_callbacks.append(callback)

    def _deliver_callback(self, callback: dict[str, Any]) -> bool:
        for _ in range(self.retry_policy.max_attempts):
            try:
                self.callback_transport.post(
                    callback["url"],
                    callback["headers"],
                    callback["payload"],
                )
                return True
            except RetryableCallbackFailure:
                continue
        return False

    def flush_callbacks(self) -> int:
        pending = self.pending_callbacks
        self.pending_callbacks = []
        for callback in pending:
            if not self._deliver_callback(callback):
                self.pending_callbacks.append(callback)
        return len(self.pending_callbacks)


def build_default_api(
    *,
    failures_by_operation: dict[str, int] | None = None,
    outcome_failures: int = 0,
    retry_policy: RetryPolicy | None = None,
) -> MockIntegrationApi:
    contract = IntegrationContract()
    source_adapter = MockSourceAdapter()
    write_back_adapter = MockWriteBackAdapter()
    outcome_adapter = MockOutcomeAdapter(outcome_failures)
    callback_transport = MockCallbackTransport(
        contract,
        failures_by_operation=failures_by_operation,
    )
    api = MockIntegrationApi(
        contract=contract,
        source_adapter=source_adapter,
        write_back_adapter=write_back_adapter,
        outcome_adapter=outcome_adapter,
        callback_transport=callback_transport,
        retry_policy=retry_policy or RetryPolicy(),
    )
    action = contract.example("executeApprovedAction", "request")
    write_back_adapter.register_approval(
        approval_id=action["approvalId"],
        tenant_key=action["tenantKey"],
        recommendation_id=action["recommendationId"],
        action_id=action["actionId"],
    )
    return api
