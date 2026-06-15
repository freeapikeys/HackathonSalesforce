from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable

from .contract import ContractValidationError, IntegrationContract
from .intake import EventIntakeClassifier, IntakeDecision, content_hash

CONTRACT_VERSION = "1.0.0"
USE_ENV_SLACK_WEBHOOK = object()
USE_ENV_WHATSAPP_PROVIDER = object()


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
class WhatsAppProviderConfig:
    provider: str
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = ""
    to_number: str = ""
    phone_number_id: str = ""
    access_token: str = ""
    graph_version: str = "v25.0"


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


class SlackInteractionValidationError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int = 400,
    ) -> None:
        self.code = code
        self.status = status
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


class TwilioWhatsAppTransport:
    """Posts approved WhatsApp alerts through the configured WhatsApp provider."""

    def post(
        self,
        config: WhatsAppProviderConfig,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if config.provider == "meta-whatsapp-cloud":
            return self._post_meta(config, payload)
        return self._post_twilio(config, payload)

    def _post_twilio(
        self,
        config: WhatsAppProviderConfig,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        endpoint = (
            "https://api.twilio.com/2010-04-01/Accounts/"
            f"{urllib.parse.quote(config.account_sid, safe='')}/Messages.json"
        )
        message = "\n".join(
            [
                payload["messageTitle"].strip(),
                payload["messageBody"].strip(),
            ]
        )
        form = urllib.parse.urlencode(
            {
                "From": self._whatsapp_address(config.from_number),
                "To": self._whatsapp_address(config.to_number),
                "Body": message,
            }
        ).encode("utf-8")
        token = base64.b64encode(
            f"{config.account_sid}:{config.auth_token}".encode("utf-8")
        ).decode("ascii")
        request = urllib.request.Request(
            endpoint,
            data=form,
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                status_code = getattr(response, "status", response.getcode())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise RetryableDependencyFailure(
                "Twilio WhatsApp request failed."
            ) from error

        if status_code < 200 or status_code >= 300:
            raise RetryableDependencyFailure(
                f"Twilio WhatsApp returned HTTP {status_code}."
            )
        try:
            parsed = json.loads(response_body)
        except json.JSONDecodeError:
            parsed = {}
        return {
            "statusCode": status_code,
            "messageId": parsed.get("sid"),
            "body": response_body,
        }

    def _post_meta(
        self,
        config: WhatsAppProviderConfig,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        endpoint = (
            "https://graph.facebook.com/"
            f"{urllib.parse.quote(config.graph_version, safe='')}/"
            f"{urllib.parse.quote(config.phone_number_id, safe='')}/messages"
        )
        message = "\n".join(
            [
                payload["messageTitle"].strip(),
                payload["messageBody"].strip(),
            ]
        )
        body = {
            "messaging_product": "whatsapp",
            "to": self._meta_phone_number(config.to_number),
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message[:4096],
            },
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                status_code = getattr(response, "status", response.getcode())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise RetryableDependencyFailure(
                "Meta WhatsApp Cloud API request failed."
            ) from error

        if status_code < 200 or status_code >= 300:
            raise RetryableDependencyFailure(
                f"Meta WhatsApp Cloud API returned HTTP {status_code}."
            )
        try:
            parsed = json.loads(response_body)
        except json.JSONDecodeError:
            parsed = {}
        messages = parsed.get("messages") or [{}]
        return {
            "statusCode": status_code,
            "messageId": messages[0].get("id"),
            "body": response_body,
        }

    @staticmethod
    def _whatsapp_address(value: str) -> str:
        return value if value.startswith("whatsapp:") else f"whatsapp:{value}"

    @staticmethod
    def _meta_phone_number(value: str) -> str:
        return value.removeprefix("whatsapp:").replace(" ", "").lstrip("+")


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

    HOSPITAL_ACTION_TYPES = frozenset(
        {
            "CREATE_PATIENT_SERVICE_TASK",
            "REQUEST_BED_CLEANING",
            "ESCALATE_LAB_VENDOR_CASE",
            "CREATE_PHARMACY_RESTOCK_REQUEST",
            "OPEN_BILLING_REVIEW",
            "REQUEST_INSURANCE_FOLLOWUP",
            "SEND_SLACK_ALERT",
            "SEND_WHATSAPP_ALERT",
            "SEND_VENDOR_EMAIL",
            "CAPTURE_HOSPITAL_OUTCOME",
        }
    )
    LEGACY_RETAIL_ACTION_TYPES = frozenset(
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
    NEXAVENU_REVENUE_ACTION_TYPES = frozenset(
        {
            "CREATE_NURTURE_TASK",
            "DRAFT_CHAMPION_EMAIL",
            "UPDATE_OPPORTUNITY_STAGE",
            "ASSIGN_CONTENT_ASSET",
            "CREATE_SOLUTION_CONSULTANT_HANDOFF",
            "CAPTURE_RETENTION_ASCENSION_OUTCOME",
        }
    )
    NEXAVENU_REVENUE_METRICS = {
        "CREATE_NURTURE_TASK": "nexavenu_nurture_task_created",
        "DRAFT_CHAMPION_EMAIL": "nexavenu_champion_email_drafted",
        "UPDATE_OPPORTUNITY_STAGE": "nexavenu_opportunity_stage_updated",
        "ASSIGN_CONTENT_ASSET": "nexavenu_content_asset_assigned",
        "CREATE_SOLUTION_CONSULTANT_HANDOFF": (
            "nexavenu_solution_consultant_handoff_created"
        ),
        "CAPTURE_RETENTION_ASCENSION_OUTCOME": (
            "nexavenu_retention_ascension_outcome_captured"
        ),
    }
    SUPPORTED_ACTION_TYPES = (
        HOSPITAL_ACTION_TYPES
        | LEGACY_RETAIL_ACTION_TYPES
        | NEXAVENU_REVENUE_ACTION_TYPES
    )

    def __init__(
        self,
        *,
        slack_webhook_url: str | None = None,
        slack_transport: SlackWebhookTransport | None = None,
        whatsapp_provider_config: WhatsAppProviderConfig | None = None,
        whatsapp_transport: TwilioWhatsAppTransport | None = None,
    ) -> None:
        self.approvals: dict[str, dict[str, str]] = {}
        self.source_records: dict[str, dict[str, Any]] = {}
        self._executions: dict[
            tuple[str, str], tuple[str, dict[str, Any]]
        ] = {}
        self.slack_webhook_url = slack_webhook_url
        self.slack_transport = slack_transport or SlackWebhookTransport()
        self.whatsapp_provider_config = whatsapp_provider_config
        self.whatsapp_transport = (
            whatsapp_transport or TwilioWhatsAppTransport()
        )

    def register_approval(
        self,
        *,
        approval_id: str,
        tenant_key: str,
        recommendation_id: str,
        action_id: str,
        action_ids: list[str] | None = None,
        status: str = "APPROVED",
    ) -> None:
        approved_action_ids = action_ids or [action_id]
        self.approvals[approval_id] = {
            "tenantKey": tenant_key,
            "recommendationId": recommendation_id,
            "actionId": action_id,
            "actionIds": list(approved_action_ids),
            "status": status,
        }

    def decide_approval(
        self,
        *,
        approval_id: str,
        tenant_key: str,
        recommendation_id: str,
        decision_status: str,
        decision_notes: str,
    ) -> dict[str, Any]:
        if decision_status not in {"APPROVED", "REJECTED"}:
            raise PermissionError("Only APPROVED or REJECTED decisions are supported.")
        approval = self.approvals.get(approval_id)
        if approval is None:
            raise PermissionError("The approval was not registered.")
        if approval["tenantKey"] != tenant_key:
            raise PermissionError("The approval tenant does not match.")
        if approval["recommendationId"] != recommendation_id:
            raise PermissionError("The approval recommendation does not match.")
        if approval["status"] != "PENDING":
            raise PermissionError("Only a pending approval can be decided.")
        approval["status"] = decision_status
        approval["decisionNotes"] = decision_notes
        approval["decidedAt"] = timestamp()
        return deepcopy(approval)

    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        approval = self.approvals.get(action["approvalId"])
        if approval is None or approval["status"] != "APPROVED":
            raise PermissionError("The linked approval is not approved.")
        for field in ("tenantKey", "recommendationId"):
            if approval[field] != action[field]:
                raise PermissionError(
                    f"The linked approval does not match {field}."
                )
        if action["actionId"] not in approval.get("actionIds", []):
            raise PermissionError("The linked approval does not include this action.")

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
        if action["actionType"] in {
            "SEND_WHATSAPP_ALERT",
            "SEND_WHATSAPP_STYLE_ALERT",
        }:
            source_record, outcome = self._execute_whatsapp_alert(
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
        if action_type in {"SEND_WHATSAPP_ALERT", "SEND_WHATSAPP_STYLE_ALERT"}:
            provider = payload.get("providerConfigured")
            return {
                "channel": "WHATSAPP",
                "targetRole": payload.get("targetRole", "Pharmacy Lead"),
                "messageBody": payload.get("messageBody", ""),
                "status": "SENT" if provider else "MOCK_SENT",
                "fallbackReason": None
                if provider
                else "WhatsApp provider credentials are not configured in the demo runtime.",
                "summary": "Approved WhatsApp alert was recorded in mock mode."
                if not provider
                else "Approved WhatsApp alert was sent.",
                "metricKey": "whatsapp_alert_recorded",
                "metricValue": 1,
            }
        if action_type == "SEND_VENDOR_EMAIL":
            return {
                "channel": "EMAIL_MOCK",
                "targetRole": payload.get("targetRole", "Vendor Coordinator"),
                "messageBody": payload.get("messageBody", ""),
                "status": "QUEUED",
                "fallbackReason": None,
                "summary": "Approved vendor email was queued in protected mock mode.",
                "metricKey": "vendor_email_queued",
                "metricValue": 1,
            }
        if action_type in self.HOSPITAL_ACTION_TYPES:
            return {
                "channel": payload.get("channel", "MULESOFT_HOSPITAL_MOCK"),
                "targetRole": payload.get("targetRole", "Operations Manager"),
                "messageBody": payload.get("messageBody", ""),
                "status": "QUEUED",
                "fallbackReason": None,
                "summary": f"Approved hospital mock action {action_type} was queued.",
                "metricKey": "hospital_action_queued",
                "metricValue": 1,
            }
        if action_type in self.LEGACY_RETAIL_ACTION_TYPES:
            return {
                "channel": payload.get("channel", "MULESOFT_MOCK"),
                "targetRole": payload.get("targetRole", "Store Manager"),
                "messageBody": payload.get("messageBody", ""),
                "status": "QUEUED",
                "fallbackReason": None,
                "summary": f"Approved legacy mock action {action_type} was queued.",
                "metricKey": "legacy_action_queued",
                "metricValue": 1,
            }
        if action_type in self.NEXAVENU_REVENUE_ACTION_TYPES:
            return {
                "channel": payload.get(
                    "channel", "SALESFORCE_REVENUE_MOCK"
                ),
                "targetRole": payload.get("targetRole", "Revenue Owner"),
                "messageBody": payload.get("messageBody", ""),
                "status": "QUEUED",
                "fallbackReason": None,
                "summary": (
                    "Approved Nexavenu revenue mock action "
                    f"{action_type} was queued."
                ),
                "metricKey": self.NEXAVENU_REVENUE_METRICS[action_type],
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

    def _execute_whatsapp_alert(
        self,
        action: dict[str, Any],
        source_record_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = action["payload"]
        whatsapp_payload = self._validated_channel_payload(
            payload,
            channel_label="WhatsApp",
        )
        sent_at: str | None = None
        fallback_reason: str | None = None
        provider_message_id: str | None = None
        if self.whatsapp_provider_config:
            provider = self.whatsapp_provider_config.provider
            try:
                result = self.whatsapp_transport.post(
                    self.whatsapp_provider_config,
                    whatsapp_payload,
                )
                status = "SENT"
                sent_at = timestamp()
                provider_message_id = result.get("messageId")
            except RetryableDependencyFailure as error:
                status = "FAILED"
                fallback_reason = str(error)
        else:
            provider = "mock-whatsapp"
            status = "MOCK_SENT"
            sent_at = timestamp()
            fallback_reason = "WhatsApp provider credentials are not configured."
            provider_message_id = (
                "mock-whatsapp-" + canonical_hash(action)[:12]
            )

        delivery = {
            "status": status,
            "provider": provider,
            "providerMessageId": provider_message_id,
            "sentAt": sent_at,
            "fallbackReason": fallback_reason,
            "targetRole": whatsapp_payload["targetRole"],
            "targetChannel": whatsapp_payload["targetChannel"],
            "messageTitle": whatsapp_payload["messageTitle"],
            "messageBody": whatsapp_payload["messageBody"],
            "evidenceIds": deepcopy(whatsapp_payload["evidenceIds"]),
            "sourceRecommendationId": whatsapp_payload[
                "sourceRecommendationId"
            ],
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
            "outcomeType": "WHATSAPP_ALERT_DELIVERY",
            "status": outcome_status,
            "observedAt": timestamp(),
            "summary": (
                f"WhatsApp alert {status} for "
                f"{whatsapp_payload['targetRole']} via {provider}."
            ),
            "metricKey": "whatsapp_alert_delivery_success",
            "metricValue": 1 if outcome_status == "SUCCESS" else 0,
        }
        return source_record, outcome

    def _execute_slack_alert(
        self,
        action: dict[str, Any],
        source_record_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = action["payload"]
        slack_payload = self._validated_channel_payload(
            payload,
            channel_label="Slack",
        )
        text = self._slack_message_text(slack_payload)
        sent_at: str | None = None
        fallback_reason: str | None = None
        provider_message_id: str | None = None

        if self.slack_webhook_url:
            provider = "slack-webhook"
            try:
                result = self.slack_transport.post(
                    self.slack_webhook_url,
                    self.slack_message_payload(slack_payload, action),
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

    def _validated_channel_payload(
        self,
        payload: dict[str, Any],
        *,
        channel_label: str,
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
                    f"{channel_label} payload field {field} is required.",
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
                f"{channel_label} payload field evidenceIds must be a non-empty string array.",
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

    def slack_message_payload(
        self,
        payload: dict[str, Any],
        action: dict[str, Any],
    ) -> dict[str, Any]:
        text = self._slack_message_text(payload)
        message = {"text": text}
        if payload.get("approvalRequest"):
            message["blocks"] = self.slack_approval_blocks(
                tenant_key=action["tenantKey"],
                correlation_id=action["correlationId"],
                recommendation_id=action["recommendationId"],
                approval_id=action["approvalId"],
                action_ids=[action["actionId"]],
                title=payload["messageTitle"],
                body=payload["messageBody"],
            )
        return message

    @staticmethod
    def slack_approval_blocks(
        *,
        tenant_key: str,
        correlation_id: str,
        recommendation_id: str,
        approval_id: str,
        action_ids: list[str],
        title: str,
        body: str,
    ) -> list[dict[str, Any]]:
        def button_value(decision_status: str) -> str:
            return json.dumps(
                {
                    "tenantKey": tenant_key,
                    "correlationId": correlation_id,
                    "recommendationId": recommendation_id,
                    "approvalId": approval_id,
                    "actionIds": action_ids,
                    "decisionStatus": decision_status,
                },
                separators=(",", ":"),
                sort_keys=True,
            )

        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title[:150],
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": body[:3000],
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"Approval `{approval_id}` for recommendation "
                            f"`{recommendation_id}`."
                        ),
                    }
                ],
            },
            {
                "type": "actions",
                "block_id": "north_star_approval_actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "action_id": "north_star_approve",
                        "value": button_value("APPROVED"),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "action_id": "north_star_reject",
                        "value": button_value("REJECTED"),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Modify"},
                        "action_id": "north_star_modify",
                        "value": button_value("MODIFY"),
                    },
                ],
            },
        ]


class SlackApprovalInteractionHandler:
    """Validates Slack button interactions and records approval decisions."""

    def __init__(
        self,
        *,
        signing_secret: str,
        write_back_adapter: MockWriteBackAdapter,
        now_seconds: Callable[[], int] | None = None,
        maximum_age_seconds: int = 300,
    ) -> None:
        if not signing_secret:
            raise ValueError("signing_secret is required")
        self.signing_secret = signing_secret
        self.write_back_adapter = write_back_adapter
        self.now_seconds = now_seconds or (lambda: int(time.time()))
        self.maximum_age_seconds = maximum_age_seconds
        self._seen_signatures: set[str] = set()

    @staticmethod
    def signature(
        *,
        signing_secret: str,
        timestamp_value: str,
        raw_body: str,
    ) -> str:
        base = f"v0:{timestamp_value}:{raw_body}".encode("utf-8")
        digest = hmac.new(
            signing_secret.encode("utf-8"),
            base,
            hashlib.sha256,
        ).hexdigest()
        return f"v0={digest}"

    def handle(
        self,
        headers: dict[str, str],
        raw_body: str,
    ) -> MockHttpResponse:
        try:
            return self._handle(headers, raw_body)
        except SlackInteractionValidationError as error:
            return MockHttpResponse(
                error.status,
                {
                    "ok": False,
                    "code": error.code,
                    "message": str(error),
                },
                {},
            )

    def _handle(
        self,
        headers: dict[str, str],
        raw_body: str,
    ) -> MockHttpResponse:
        normalized_headers = {key.lower(): value for key, value in headers.items()}
        timestamp_value = normalized_headers.get("x-slack-request-timestamp", "")
        signature_value = normalized_headers.get("x-slack-signature", "")
        if not timestamp_value or not signature_value:
            raise SlackInteractionValidationError(
                "SLACK_SIGNATURE_MISSING",
                "Slack signature headers are required.",
                status=401,
            )
        try:
            request_time = int(timestamp_value)
        except ValueError as error:
            raise SlackInteractionValidationError(
                "SLACK_TIMESTAMP_INVALID",
                "Slack request timestamp must be an integer.",
                status=401,
            ) from error
        if abs(self.now_seconds() - request_time) > self.maximum_age_seconds:
            raise SlackInteractionValidationError(
                "SLACK_TIMESTAMP_EXPIRED",
                "Slack request timestamp is outside the allowed window.",
                status=401,
            )
        expected_signature = self.signature(
            signing_secret=self.signing_secret,
            timestamp_value=timestamp_value,
            raw_body=raw_body,
        )
        if not hmac.compare_digest(expected_signature, signature_value):
            raise SlackInteractionValidationError(
                "SLACK_SIGNATURE_INVALID",
                "Slack request signature did not match.",
                status=401,
            )
        if signature_value in self._seen_signatures:
            raise SlackInteractionValidationError(
                "SLACK_INTERACTION_REPLAYED",
                "Slack interaction was already processed.",
                status=409,
            )

        form = urllib.parse.parse_qs(raw_body, keep_blank_values=True)
        payload_values = form.get("payload")
        if not payload_values:
            raise SlackInteractionValidationError(
                "SLACK_PAYLOAD_MISSING",
                "Slack interaction payload is required.",
            )
        try:
            payload = json.loads(payload_values[0])
        except json.JSONDecodeError as error:
            raise SlackInteractionValidationError(
                "SLACK_PAYLOAD_INVALID",
                "Slack interaction payload must be JSON.",
            ) from error
        action = (payload.get("actions") or [{}])[0]
        action_id = action.get("action_id")
        try:
            value = json.loads(action.get("value") or "{}")
        except json.JSONDecodeError as error:
            raise SlackInteractionValidationError(
                "SLACK_ACTION_VALUE_INVALID",
                "Slack action value must be JSON.",
            ) from error

        decision_status = value.get("decisionStatus")
        if action_id == "north_star_modify" or decision_status == "MODIFY":
            self._seen_signatures.add(signature_value)
            return MockHttpResponse(
                200,
                {
                    "ok": True,
                    "decisionStatus": "MODIFY_REQUESTED",
                    "approvalId": value.get("approvalId"),
                    "message": (
                        "Open the Salesforce command center to modify this "
                        "recommendation before approval."
                    ),
                },
                {},
            )
        if action_id == "north_star_approve":
            decision_status = "APPROVED"
        elif action_id == "north_star_reject":
            decision_status = "REJECTED"
        if decision_status not in {"APPROVED", "REJECTED"}:
            raise SlackInteractionValidationError(
                "SLACK_DECISION_UNSUPPORTED",
                "Slack approval decision must be APPROVED or REJECTED.",
            )
        try:
            decision = self.write_back_adapter.decide_approval(
                approval_id=value["approvalId"],
                tenant_key=value["tenantKey"],
                recommendation_id=value["recommendationId"],
                decision_status=decision_status,
                decision_notes=(
                    f"Slack button {action_id} by "
                    f"{payload.get('user', {}).get('username', 'manager')}"
                ),
            )
        except KeyError as error:
            raise SlackInteractionValidationError(
                "SLACK_ACTION_VALUE_MISSING",
                "Slack action value is missing approval identifiers.",
            ) from error
        except PermissionError as error:
            raise SlackInteractionValidationError(
                "SLACK_APPROVAL_DENIED",
                str(error),
                status=403,
            ) from error

        self._seen_signatures.add(signature_value)
        return MockHttpResponse(
            200,
            {
                "ok": True,
                "decisionStatus": decision_status,
                "approvalId": value["approvalId"],
                "recommendationId": value["recommendationId"],
                "tenantKey": value["tenantKey"],
                "correlationId": value.get("correlationId"),
                "actionIds": decision.get("actionIds", []),
            },
            {},
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

    def ingest_twilio_whatsapp(
        self,
        twilio_payload: dict[str, Any],
        *,
        tenant_key: str = "demo-mauritius",
        observed_at: str | None = None,
        source_sequence: int = 10_000,
    ) -> MockHttpResponse:
        """Map an inbound Twilio WhatsApp webhook into governed event intake.

        The demo stores only a synthetic customer alias and a body hash, not
        the customer's phone number or raw message text.
        """

        observed = observed_at or timestamp()
        message_sid = str(
            twilio_payload.get("MessageSid")
            or twilio_payload.get("SmsMessageSid")
            or ""
        ).strip()
        body = str(twilio_payload.get("Body") or "").strip()
        from_number = str(twilio_payload.get("From") or "").strip()

        correlation_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"north-star:twilio-whatsapp:{tenant_key}:{message_sid or body}",
            )
        )
        headers = {
            "X-Tenant-Id": tenant_key,
            "X-Correlation-Id": correlation_id,
            "X-Idempotency-Key": f"twilio-whatsapp-{message_sid or 'missing'}-v1",
        }
        error_body = {
            "hfstenantid": tenant_key,
            "hfscorrelationid": correlation_id,
            "hfsidempotencykey": headers["X-Idempotency-Key"],
        }

        if not message_sid:
            return self._common_error(
                operation="INGEST_EVENT",
                headers=headers,
                body=error_body,
                status=422,
                code="VALIDATION_FAILED",
                message="Twilio inbound WhatsApp payload is missing MessageSid.",
                field_name="MessageSid",
            )
        if not body:
            return self._common_error(
                operation="INGEST_EVENT",
                headers=headers,
                body=error_body,
                status=422,
                code="VALIDATION_FAILED",
                message="Twilio inbound WhatsApp payload is missing Body.",
                field_name="Body",
            )

        customer_alias = self._customer_alias(from_number or message_sid)
        analysis = self._analyze_inbound_complaint(body)
        event_data = {
            "recordtype": "Issue",
            "operation": "OPEN",
            "businesskey": f"whatsapp-complaint-{message_sid.lower()}",
            "effectiveat": observed,
            "attributes": {
                "profile": "private-hospital",
                "primitive": "Signal",
                "module": "Complaint and trust",
                "sourceChannel": "whatsapp-inbound",
                "sourceSystem": "twilio-whatsapp",
                "sourceRecordId": message_sid,
                "customerAlias": customer_alias,
                "messageBodyStored": False,
                "messageBodyHash": "sha256:"
                + hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "messageLength": len(body),
                "departmentHint": analysis["departmentHint"],
                "resourceHint": analysis["resourceHint"],
                "complaintTypes": analysis["complaintTypes"],
                "severity": analysis["severity"],
                "safeSummary": analysis["safeSummary"],
                "followUpQuestions": analysis["followUpQuestions"],
                "rootCauseHypotheses": analysis["rootCauseHypotheses"],
                "nextEvidenceNeeded": analysis["nextEvidenceNeeded"],
                "affectedPrimitives": analysis["affectedPrimitives"],
                "requiresManagerApprovalBeforeCustomerReply": True,
                "protectedActionState": "NO_ACTION_EXECUTED",
            },
            "assertions": [
                {
                    "conflictkey": f"complaint:{customer_alias}",
                    "predicate": "customer_complaint_received",
                    "value": True,
                }
            ],
        }
        event = {
            "specversion": "1.0",
            "id": str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"north-star:event:twilio-whatsapp:{tenant_key}:{message_sid}",
                )
            ),
            "source": "urn:hfs:source:twilio-whatsapp",
            "type": (
                "io.github.freeapikeys.hfs.hospital."
                "patientcomplaint.received.v1"
            ),
            "subject": f"customer:{customer_alias}",
            "time": observed,
            "datacontenttype": "application/json",
            "dataschema": (
                "https://freeapikeys.github.io/HackathonSalesforce/events/"
                "event-envelope-v1.schema.json"
            ),
            "hfstenantid": tenant_key,
            "hfsschemaversion": CONTRACT_VERSION,
            "hfscorrelationid": correlation_id,
            "hfsidempotencykey": headers["X-Idempotency-Key"],
            "hfssourcerecordid": message_sid,
            "hfssourcesequence": source_sequence,
            "hfsobservedat": observed,
            "hfscontenthash": content_hash(event_data),
            "data": event_data,
        }
        return self._ingest_event(headers, event)

    @staticmethod
    def _customer_alias(value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
        return f"alias-whatsapp-customer-{digest}"

    @staticmethod
    def _analyze_inbound_complaint(message: str) -> dict[str, Any]:
        text = message.lower()
        complaint_types: list[str] = []
        if any(term in text for term in ("wait", "queue", "late", "hour")):
            complaint_types.append("wait_time")
        if any(term in text for term in ("room", "bed", "clean", "dirty")):
            complaint_types.append("room_readiness")
        if any(term in text for term in ("bill", "invoice", "charge", "pay")):
            complaint_types.append("billing")
        if any(term in text for term in ("pharmacy", "medicine", "stock", "kit")):
            complaint_types.append("pharmacy_delay")
        if any(term in text for term in ("food", "meal", "allergy")):
            complaint_types.append("food")
        if any(term in text for term in ("wheelchair", "lift", "access")):
            complaint_types.append("accessibility")
        if any(term in text for term in ("privacy", "private", "personal")):
            complaint_types.append("privacy")
        if any(term in text for term in ("unsafe", "danger", "hurt", "fall")):
            complaint_types.append("safety")
        if not complaint_types:
            complaint_types.append("general_service")

        if "safety" in complaint_types or "privacy" in complaint_types:
            severity = "HIGH"
        elif len(complaint_types) >= 3:
            severity = "HIGH"
        elif len(complaint_types) == 2:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        department_hint = "Patient experience desk"
        resource_hint = "Customer service case"
        if "wait_time" in complaint_types:
            department_hint = "Outpatient reception"
            resource_hint = "Outpatient queue"
        if "room_readiness" in complaint_types:
            department_hint = "Inpatient discharge ward"
            resource_hint = "Room or bed readiness"
        if "pharmacy_delay" in complaint_types:
            department_hint = "Pharmacy"
            resource_hint = "Pharmacy stock or counter queue"
        if "billing" in complaint_types:
            department_hint = "Billing and insurance"
            resource_hint = "Billing review case"

        follow_up_questions = [
            "Which service area were you in?",
            "When did the issue happen?",
            "What outcome would make this acceptable for you?",
        ]
        if "room_readiness" in complaint_types:
            follow_up_questions.append("Was the issue cleanliness, room availability, or discharge timing?")
        if "billing" in complaint_types:
            follow_up_questions.append("Was the concern a duplicate charge, claim delay, refund, or payment issue?")
        if "pharmacy_delay" in complaint_types:
            follow_up_questions.append("Was the delay caused by queue time, unavailable stock, or missing approval?")

        root_causes = []
        if "wait_time" in complaint_types:
            root_causes.append("Queue pressure or staff coverage gap may be driving the complaint.")
        if "room_readiness" in complaint_types:
            root_causes.append("Blocked room, cleaning, or porter delay may be affecting readiness.")
        if "pharmacy_delay" in complaint_types:
            root_causes.append("Low stock, counter queue, or approval delay may be affecting pharmacy service.")
        if "billing" in complaint_types:
            root_causes.append("Duplicate invoice, insurer delay, or payment review may be causing financial friction.")
        if not root_causes:
            root_causes.append("More evidence is needed before assigning the root cause.")

        evidence_needed = [
            "current queue or service-area status",
            "related resource status",
            "recent similar complaints",
            "manager approval requirement",
        ]
        if "billing" in complaint_types:
            evidence_needed.append("billing or insurance case status")
        if "pharmacy_delay" in complaint_types:
            evidence_needed.append("pharmacy stock and counter queue status")

        return {
            "complaintTypes": complaint_types,
            "severity": severity,
            "departmentHint": department_hint,
            "resourceHint": resource_hint,
            "safeSummary": (
                "Inbound WhatsApp complaint classified as "
                + ", ".join(complaint_types)
                + ". Raw message text is not stored in the demo event."
            ),
            "followUpQuestions": follow_up_questions,
            "rootCauseHypotheses": root_causes,
            "nextEvidenceNeeded": evidence_needed,
            "affectedPrimitives": [
                "Signal",
                "Evidence",
                "Customer",
                "Location",
                "Resource",
                "Risk",
                "Policy",
                "Recommendation",
                "Approval",
                "Action",
                "Outcome",
            ],
        }

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


def whatsapp_provider_config_from_env() -> WhatsAppProviderConfig | None:
    meta_values = {
        "phone_number_id": os.getenv("META_WHATSAPP_PHONE_NUMBER_ID"),
        "access_token": os.getenv("META_WHATSAPP_ACCESS_TOKEN"),
        "to_number": os.getenv("META_WHATSAPP_TO"),
    }
    if all(meta_values.values()):
        return WhatsAppProviderConfig(
            provider="meta-whatsapp-cloud",
            phone_number_id=str(meta_values["phone_number_id"]),
            access_token=str(meta_values["access_token"]),
            to_number=str(meta_values["to_number"]),
            graph_version=os.getenv("META_GRAPH_VERSION", "v25.0"),
        )

    twilio_values = {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
        "from_number": os.getenv("TWILIO_WHATSAPP_FROM"),
        "to_number": os.getenv("TWILIO_WHATSAPP_TO"),
    }
    if not all(twilio_values.values()):
        return None
    return WhatsAppProviderConfig(
        provider="twilio-whatsapp",
        account_sid=str(twilio_values["account_sid"]),
        auth_token=str(twilio_values["auth_token"]),
        from_number=str(twilio_values["from_number"]),
        to_number=str(twilio_values["to_number"]),
    )


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
    whatsapp_provider_config: (
        WhatsAppProviderConfig | None | object
    ) = USE_ENV_WHATSAPP_PROVIDER,
    whatsapp_transport: TwilioWhatsAppTransport | None = None,
) -> MockIntegrationApi:
    contract = IntegrationContract()
    source_adapter = MockSourceAdapter(source_failures)
    resolved_slack_webhook_url = (
        os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook_url is USE_ENV_SLACK_WEBHOOK
        else slack_webhook_url
    )
    resolved_whatsapp_provider_config = (
        whatsapp_provider_config_from_env()
        if whatsapp_provider_config is USE_ENV_WHATSAPP_PROVIDER
        else whatsapp_provider_config
    )
    write_back_adapter = MockWriteBackAdapter(
        slack_webhook_url=resolved_slack_webhook_url,
        slack_transport=slack_transport,
        whatsapp_provider_config=resolved_whatsapp_provider_config,
        whatsapp_transport=whatsapp_transport,
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
