from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable

from .contract import ContractValidationError, IntegrationContract
from .intake import EventIntakeClassifier, IntakeDecision

CONTRACT_VERSION = "1.0.0"
USE_ENV_SLACK_WEBHOOK = object()


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


class ActionPayloadValidationError(ValueError):
    def __init__(self, field_name: str, message: str) -> None:
        self.field_name = field_name
        super().__init__(message)


class RetryableDependencyFailure(RuntimeError):
    pass


class SlackWebhookTransport:
    """Posts approved Slack alerts without exposing webhook secrets."""

    def post(
        self,
        webhook_url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        request = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                status_code = getattr(response, "status", response.getcode())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise RetryableDependencyFailure(
                "Slack webhook request failed."
            ) from error

        if status_code < 200 or status_code >= 300:
            raise RetryableDependencyFailure(
                f"Slack webhook returned HTTP {status_code}."
            )
        return {"statusCode": status_code, "body": response_body}


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

    def __init__(self, failures_remaining: int = 0) -> None:
        if failures_remaining < 0:
            raise ValueError("failures_remaining cannot be negative")
        self.events: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.attempts: list[dict[str, Any]] = []
        self.failures_remaining = failures_remaining
        self._attempt_events: dict[str, dict[str, Any]] = {}

    def preserve(self, event: dict[str, Any]) -> None:
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise RetryableDependencyFailure(
                "Injected temporary source-event store failure."
            )
        identity = (
            event["hfstenantid"],
            event["source"],
            event["id"],
        )
        self.events[identity] = deepcopy(event)

    def record_attempt(
        self,
        event: dict[str, Any],
        decision: IntakeDecision,
        *,
        state: str | None = None,
        original_attempt_id: str | None = None,
        error_code: str | None = None,
    ) -> dict[str, Any]:
        attempt_id = f"intake-attempt-{len(self.attempts) + 1:06d}"
        attempt = {
            "attemptId": attempt_id,
            "originalAttemptId": original_attempt_id,
            "eventId": event.get("id"),
            "tenantKey": event.get("hfstenantid"),
            "source": event.get("source"),
            "idempotencyKey": event.get("hfsidempotencykey"),
            "intakeResult": decision.result,
            "state": state
            or (
                "PRESERVED"
                if decision.preserve
                else "DUPLICATE"
                if decision.replayed
                else "REJECTED"
            ),
            "errorCode": error_code,
            "detail": decision.detail,
            "preserved": decision.preserve and state != "QUARANTINED",
            "replayed": decision.replayed,
            "lateBySeconds": decision.late_by_seconds,
            "sourceWatermark": decision.source_watermark,
        }
        self.attempts.append(attempt)
        self._attempt_events[attempt_id] = deepcopy(event)
        return deepcopy(attempt)

    def attempt(self, attempt_id: str) -> dict[str, Any] | None:
        for attempt in self.attempts:
            if attempt["attemptId"] == attempt_id:
                return deepcopy(attempt)
        return None


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

    RETAIL_ACTION_TYPES = frozenset(
        {
            "CREATE_SUPPLIER_QUALITY_CASE",
            "REQUEST_REPLACEMENT_BATCH",
            "CREATE_REORDER_REQUEST",
            "CREATE_WAREHOUSE_TRANSFER",
            "CREATE_MARKDOWN_PLAN",
            "CREATE_QUARANTINE_TASK",
            "CREATE_RESTOCK_TASK",
            "CREATE_SHELF_LAYOUT_TASK",
            "OPEN_EXTRA_CASHIER_TASK",
            "SEND_SLACK_ALERT",
            "SEND_WHATSAPP_STYLE_ALERT",
            "CAPTURE_RETAIL_OUTCOME",
        }
    )

    def __init__(
        self,
        *,
        slack_webhook_url: str | None = None,
        slack_transport: SlackWebhookTransport | None = None,
    ) -> None:
        self.approvals: dict[str, dict[str, str]] = {}
        self.source_records: dict[str, dict[str, Any]] = {}
        self._executions: dict[
            tuple[str, str], tuple[str, dict[str, Any]]
        ] = {}
        self.slack_webhook_url = slack_webhook_url
        self.slack_transport = slack_transport or SlackWebhookTransport()

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

        source_record_id = "mock-writeback-" + canonical_hash(action)[:16]
        if action["actionType"] == "SEND_SLACK_ALERT":
            source_record, outcome = self._execute_slack_alert(
                action,
                source_record_id,
            )
            self.source_records[source_record_id] = source_record
            self._executions[scope] = (action_hash, deepcopy(outcome))
            return outcome

        delivery = self._delivery_evidence(action)
        self.source_records[source_record_id] = {
            "sourceRecordId": source_record_id,
            "sourceSystem": action["sourceSystem"],
            "actionId": action["actionId"],
            "actionType": action["actionType"],
            "payload": deepcopy(action["payload"]),
            "delivery": deepcopy(delivery),
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
            "status": "SUCCESS" if delivery["status"] != "FAILED" else "PARTIAL",
            "observedAt": timestamp(),
            "summary": delivery["summary"],
            "metricKey": delivery["metricKey"],
            "metricValue": delivery["metricValue"],
        }
        self._executions[scope] = (action_hash, deepcopy(outcome))
        return outcome

    def _delivery_evidence(self, action: dict[str, Any]) -> dict[str, Any]:
        action_type = action["actionType"]
        payload = action.get("payload", {})
        if action_type == "SEND_SLACK_ALERT":
            has_webhook = bool(payload.get("webhookConfigured"))
            return {
                "channel": "SLACK",
                "targetRole": payload.get("targetRole", "Duty Manager"),
                "messageBody": payload.get("messageBody", ""),
                "status": "SENT" if has_webhook else "MOCK_SENT",
                "fallbackReason": None
                if has_webhook
                else "SLACK_WEBHOOK_URL is not configured in the demo runtime.",
                "summary": "Approved Slack alert was recorded in mock mode."
                if not has_webhook
                else "Approved Slack alert was sent.",
                "metricKey": "slack_alert_recorded",
                "metricValue": 1,
            }
        if action_type == "SEND_WHATSAPP_STYLE_ALERT":
            provider = payload.get("providerConfigured")
            return {
                "channel": "WHATSAPP_STYLE",
                "targetRole": payload.get("targetRole", "Fresh Food Lead"),
                "messageBody": payload.get("messageBody", ""),
                "status": "SENT" if provider else "MOCK_SENT",
                "fallbackReason": None
                if provider
                else "WhatsApp provider credentials are not configured in the demo runtime.",
                "summary": "Approved WhatsApp-style alert was recorded in mock mode."
                if not provider
                else "Approved WhatsApp alert was sent.",
                "metricKey": "whatsapp_style_alert_recorded",
                "metricValue": 1,
            }
        if action_type in self.RETAIL_ACTION_TYPES:
            return {
                "channel": payload.get("channel", "MULESOFT_MOCK"),
                "targetRole": payload.get("targetRole", "Store Manager"),
                "messageBody": payload.get("messageBody", ""),
                "status": "QUEUED",
                "fallbackReason": None,
                "summary": f"Approved retail mock action {action_type} was queued.",
                "metricKey": "retail_action_queued",
                "metricValue": 1,
            }
        return {
            "channel": payload.get("channel", "MULESOFT_MOCK"),
            "targetRole": payload.get("targetRole", "Operations"),
            "messageBody": payload.get("messageBody", ""),
            "status": "QUEUED",
            "fallbackReason": None,
            "summary": "The approved mock action was executed.",
            "metricKey": "action_execution_success",
            "metricValue": 1,
        }

    def _execute_slack_alert(
        self,
        action: dict[str, Any],
        source_record_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = action["payload"]
        slack_payload = self._validated_slack_payload(payload)
        text = self._slack_message_text(slack_payload)
        sent_at: str | None = None
        fallback_reason: str | None = None
        provider_message_id: str | None = None

        if self.slack_webhook_url:
            provider = "slack-webhook"
            try:
                result = self.slack_transport.post(
                    self.slack_webhook_url,
                    {"text": text},
                )
                status = "SENT"
                sent_at = timestamp()
                provider_message_id = result.get("messageId")
            except RetryableDependencyFailure as error:
                status = "FAILED"
                fallback_reason = str(error)
        else:
            provider = "mock-slack"
            status = "MOCK_SENT"
            sent_at = timestamp()
            fallback_reason = "SLACK_WEBHOOK_URL is not configured."
            provider_message_id = (
                "mock-slack-" + canonical_hash(action)[:12]
            )

        delivery = {
            "status": status,
            "provider": provider,
            "providerMessageId": provider_message_id,
            "sentAt": sent_at,
            "fallbackReason": fallback_reason,
            "targetRole": slack_payload["targetRole"],
            "targetChannel": slack_payload["targetChannel"],
            "messageTitle": slack_payload["messageTitle"],
            "messageBody": slack_payload["messageBody"],
            "evidenceIds": deepcopy(slack_payload["evidenceIds"]),
            "sourceRecommendationId": slack_payload["sourceRecommendationId"],
            "correlationId": action["correlationId"],
            "actionId": action["actionId"],
        }
        source_record = {
            "sourceRecordId": source_record_id,
            "sourceSystem": action["sourceSystem"],
            "actionId": action["actionId"],
            "actionType": action["actionType"],
            "payload": deepcopy(payload),
            "delivery": delivery,
        }
        outcome_status = "SUCCESS" if status in {"SENT", "MOCK_SENT"} else "FAILED"
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
            "outcomeType": "SLACK_ALERT_DELIVERY",
            "status": outcome_status,
            "observedAt": timestamp(),
            "summary": (
                f"Slack alert {status} for "
                f"{slack_payload['targetRole']} via {provider}."
            ),
            "metricKey": "slack_alert_delivery_success",
            "metricValue": 1 if outcome_status == "SUCCESS" else 0,
        }
        return source_record, outcome

    def _validated_slack_payload(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        required_text = [
            "targetRole",
            "targetChannel",
            "messageTitle",
            "messageBody",
            "sourceRecommendationId",
        ]
        for field in required_text:
            value = payload.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ActionPayloadValidationError(
                    f"payload.{field}",
                    f"Slack payload field {field} is required.",
                )

        evidence_ids = payload.get("evidenceIds")
        if (
            not isinstance(evidence_ids, list)
            or not evidence_ids
            or any(
                not isinstance(evidence_id, str) or not evidence_id.strip()
                for evidence_id in evidence_ids
            )
        ):
            raise ActionPayloadValidationError(
                "payload.evidenceIds",
                "Slack payload field evidenceIds must be a non-empty string array.",
            )
        return deepcopy(payload)

    def _slack_message_text(self, payload: dict[str, Any]) -> str:
        return "\n".join(
            [
                f"North Star alert: {payload['messageTitle']}",
                payload["messageBody"],
                f"Owner: {payload['targetRole']}",
                f"Channel: {payload['targetChannel']}",
                "Evidence: " + ", ".join(payload["evidenceIds"]),
            ]
        )


class MockIntegrationApi:
    PATHS = {
        "/v1/events": "ingestEvent",
        "/v1/events/replays": "replayEvent",
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
        intake_classifier: EventIntakeClassifier,
        replay_purposes: set[str] | None = None,
    ) -> None:
        self.contract = contract
        self.source_adapter = source_adapter
        self.write_back_adapter = write_back_adapter
        self.outcome_adapter = outcome_adapter
        self.callback_transport = callback_transport
        self.retry_policy = retry_policy
        self.intake_classifier = intake_classifier
        self.replay_purposes = replay_purposes or {
            "REPLAY_QUARANTINED_EVENT"
        }
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
            "replayEvent": self.replay_event,
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
        details: str | None = None,
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
                    "details": details,
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
        *,
        original_attempt_id: str | None = None,
    ) -> MockHttpResponse:
        operation = "INGEST_EVENT"
        validation = self.intake_classifier.validate(body)
        if validation is not None:
            state = (
                "QUARANTINED"
                if validation.result in {"REJECTED_SCHEMA", "REJECTED_HASH"}
                else "REJECTED"
            )
            self.source_adapter.record_attempt(
                body,
                validation,
                state=state,
                original_attempt_id=original_attempt_id,
                error_code="VALIDATION_FAILED",
            )
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="VALIDATION_FAILED",
                message=validation.detail,
                field_name=validation.field_name,
                details=validation.result,
            )
        header_error = self._validated_headers(
            operation=operation,
            headers=headers,
            body=body,
            idempotent=True,
        )
        if header_error:
            return header_error
        decision = self.intake_classifier.classify(body, commit=False)
        if decision.result == "REJECTED_IDEMPOTENCY_CONFLICT":
            self.source_adapter.record_attempt(
                body,
                decision,
                state="REJECTED",
                original_attempt_id=original_attempt_id,
                error_code="IDEMPOTENCY_CONFLICT",
            )
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="IDEMPOTENCY_CONFLICT",
                message=decision.detail,
                field_name=decision.field_name,
                details=decision.result,
            )
        if decision.preserve:
            preserved = False
            for _ in range(self.retry_policy.max_attempts):
                try:
                    self.source_adapter.preserve(body)
                    preserved = True
                    break
                except RetryableDependencyFailure:
                    continue
            if not preserved:
                self.source_adapter.record_attempt(
                    body,
                    decision,
                    state="QUARANTINED",
                    original_attempt_id=original_attempt_id,
                    error_code="RETRYABLE_DEPENDENCY_FAILURE",
                )
                return self._common_error(
                    operation=operation,
                    headers=headers,
                    body=body,
                    status=503,
                    code="RETRYABLE_DEPENDENCY_FAILURE",
                    message="Source-event preservation exhausted its retry policy.",
                    retryable=True,
                    details="QUARANTINED",
                )
            decision = self.intake_classifier.classify(body, commit=True)
        self.source_adapter.record_attempt(
            body,
            decision,
            original_attempt_id=original_attempt_id,
        )
        response_body = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": body["hfstenantid"],
            "correlationId": body["hfscorrelationid"],
            "eventId": body["id"],
            "intakeResult": decision.result,
            "replayed": decision.replayed,
            "observedAt": body["hfsobservedat"],
        }
        self.contract.validate("EventIntakeResponse", response_body)
        response = MockHttpResponse(
            202,
            response_body,
            {"X-Correlation-Id": body["hfscorrelationid"]},
        )
        if not decision.replayed:
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

    def replay_event(
        self,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> MockHttpResponse:
        operation = "REPLAY_EVENT"
        try:
            self.contract.validate("EventReplayRequest", body)
        except ContractValidationError as error:
            return self._schema_error(
                operation=operation,
                headers=headers,
                body=body,
                error=error,
            )
        required = {
            "contractVersion",
            "tenantKey",
            "correlationId",
            "idempotencyKey",
            "purpose",
            "originalAttemptId",
            "reason",
            "event",
        }
        missing = sorted(required - set(body))
        if missing:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="VALIDATION_FAILED",
                message=f"Required field {missing[0]} is missing.",
                field_name=missing[0],
            )
        header_error = self._validated_headers(
            operation=operation,
            headers=headers,
            body=body,
            idempotent=True,
        )
        if header_error:
            return header_error
        if body["purpose"] not in self.replay_purposes:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=403,
                code="PERMISSION_DENIED",
                message="The declared purpose is not authorized for event replay.",
                field_name="purpose",
            )
        replay = self._idempotency_result(
            operation=operation,
            headers=headers,
            body=body,
        )
        if replay:
            return replay

        original = self.source_adapter.attempt(body["originalAttemptId"])
        if original is None:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="RECORD_NOT_FOUND",
                message="The original intake attempt was not found.",
                field_name="originalAttemptId",
            )
        if original["tenantKey"] != body["tenantKey"]:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="TENANT_MISMATCH",
                message="The replay tenant does not match the original attempt.",
                field_name="tenantKey",
            )
        if original["state"] != "QUARANTINED":
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="INVALID_STATE",
                message="Only quarantined intake attempts can be replayed.",
                field_name="originalAttemptId",
            )

        event = body["event"]
        if not isinstance(event, dict) or event.get("hfstenantid") != body["tenantKey"]:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=409,
                code="TENANT_MISMATCH",
                message="The replay event tenant does not match the request.",
                field_name="event.hfstenantid",
            )
        event_headers = {
            "X-Tenant-Id": event.get("hfstenantid", ""),
            "X-Correlation-Id": event.get("hfscorrelationid", ""),
            "X-Idempotency-Key": event.get("hfsidempotencykey", ""),
        }
        intake_response = self._ingest_event(
            event_headers,
            event,
            original_attempt_id=original["attemptId"],
        )
        if intake_response.status != 202:
            error = intake_response.body["errors"][0]
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=intake_response.status,
                code=error["code"],
                message=error["message"],
                retryable=error["retryable"],
                field_name=error["fieldName"],
                details=error["details"],
            )

        replay_attempt = self.source_adapter.attempts[-1]
        response_body = {
            "contractVersion": CONTRACT_VERSION,
            "tenantKey": body["tenantKey"],
            "correlationId": body["correlationId"],
            "operation": operation,
            "success": True,
            "replayed": False,
            "originalAttemptId": original["attemptId"],
            "replayAttemptId": replay_attempt["attemptId"],
            "intakeResult": replay_attempt["intakeResult"],
            "status": "COMPLETED",
        }
        response = MockHttpResponse(
            202,
            response_body,
            {"X-Correlation-Id": body["correlationId"]},
        )
        self.contract.validate("EventReplayResponse", response_body)
        self._remember(
            operation=operation,
            headers=headers,
            body=body,
            response=response,
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
        except ActionPayloadValidationError as error:
            return self._common_error(
                operation=operation,
                headers=headers,
                body=body,
                status=422,
                code="VALIDATION_FAILED",
                message=str(error),
                field_name=error.field_name,
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
        delivery = self.write_back_adapter.source_records[
            outcome["sourceRecordId"]
        ].get("delivery")
        if delivery is not None:
            callback_result["delivery"] = deepcopy(delivery)
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
    source_failures: int = 0,
    retry_policy: RetryPolicy | None = None,
    maximum_lateness_seconds: int = 86_400,
    replay_purposes: set[str] | None = None,
    slack_webhook_url: str | None | object = USE_ENV_SLACK_WEBHOOK,
    slack_transport: SlackWebhookTransport | None = None,
) -> MockIntegrationApi:
    contract = IntegrationContract()
    source_adapter = MockSourceAdapter(source_failures)
    resolved_slack_webhook_url = (
        os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook_url is USE_ENV_SLACK_WEBHOOK
        else slack_webhook_url
    )
    write_back_adapter = MockWriteBackAdapter(
        slack_webhook_url=resolved_slack_webhook_url,
        slack_transport=slack_transport,
    )
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
        intake_classifier=EventIntakeClassifier(
            maximum_lateness_seconds=maximum_lateness_seconds
        ),
        replay_purposes=replay_purposes,
    )
    action = contract.example("executeApprovedAction", "request")
    write_back_adapter.register_approval(
        approval_id=action["approvalId"],
        tenant_key=action["tenantKey"],
        recommendation_id=action["recommendationId"],
        action_id=action["actionId"],
    )
    return api
