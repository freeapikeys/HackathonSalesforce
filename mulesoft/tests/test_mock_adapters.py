from __future__ import annotations

import json
import unittest
import urllib.parse
from copy import deepcopy
from unittest.mock import patch

from mock_runtime import (
    RetryPolicy,
    SlackApprovalInteractionHandler,
    SlackStatusCommandHandler,
    WhatsAppProviderConfig,
    build_default_api,
)


class FakeSlackTransport:
    def __init__(self) -> None:
        self.posts = []

    def post(self, webhook_url, payload):
        self.posts.append({"webhookUrl": webhook_url, "payload": payload})
        return {"messageId": "slack-message-001"}


class FakeWhatsAppTransport:
    def __init__(self) -> None:
        self.posts = []

    def post(self, config, payload):
        self.posts.append({"config": config, "payload": payload})
        return {"messageId": "whatsapp-message-001"}


class MockAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.api = build_default_api(
            slack_webhook_url="",
            whatsapp_provider_config=None,
        )
        self.contract = self.api.contract

    def request(
        self,
        operation_id: str,
        path: str,
    ):
        example = self.contract.examples["operations"][operation_id]["request"]
        return self.api.request(
            "POST",
            path,
            deepcopy(example["x-hfs-headers"]),
            deepcopy(example["value"]),
        )

    def signed_slack_request(
        self,
        *,
        signing_secret: str,
        payload: dict,
        timestamp: str = "1710000000",
    ) -> tuple[dict[str, str], str]:
        raw_body = urllib.parse.urlencode(
            {"payload": json.dumps(payload, separators=(",", ":"))}
        )
        return (
            {
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": SlackApprovalInteractionHandler.signature(
                    signing_secret=signing_secret,
                    timestamp_value=timestamp,
                    raw_body=raw_body,
                ),
            },
            raw_body,
        )

    def signed_slack_form_request(
        self,
        *,
        signing_secret: str,
        form: dict[str, str],
        timestamp: str = "1710000000",
    ) -> tuple[dict[str, str], str]:
        raw_body = urllib.parse.urlencode(form)
        return (
            {
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": SlackApprovalInteractionHandler.signature(
                    signing_secret=signing_secret,
                    timestamp_value=timestamp,
                    raw_body=raw_body,
                ),
            },
            raw_body,
        )

    def test_synthetic_event_and_approved_action_produce_outcome(self) -> None:
        event_response = self.request("ingestEvent", "/v1/events")
        self.assertEqual(202, event_response.status)
        self.assertEqual("ACCEPTED", event_response.body["intakeResult"])

        action_response = self.request(
            "executeApprovedAction",
            "/v1/actions/executions",
        )
        self.assertEqual(202, action_response.status)
        self.assertEqual("QUEUED", action_response.body["status"])

        self.assertEqual(1, len(self.api.source_adapter.events))
        self.assertEqual(1, len(self.api.write_back_adapter.source_records))
        self.assertEqual(1, len(self.api.outcomes))

        outcome = next(iter(self.api.outcomes.values()))
        self.assertEqual(
            action_response.body["correlationId"],
            outcome["correlationId"],
        )
        self.assertEqual(action_response.body["actionId"], outcome["actionId"])
        self.assertEqual("SUCCESS", outcome["status"])
        record = next(iter(self.api.write_back_adapter.source_records.values()))
        self.assertEqual("SEND_SLACK_ALERT", record["actionType"])
        self.assertEqual("MOCK_SENT", record["delivery"]["status"])
        self.assertEqual("mock-slack", record["delivery"]["provider"])

        action_callbacks = [
            item
            for item in self.api.callback_transport.received
            if item["payload"]["operation"] == "EXECUTE_APPROVED_ACTION"
        ]
        self.assertEqual(1, len(action_callbacks))
        self.assertEqual(
            outcome["correlationId"],
            action_callbacks[0]["payload"]["correlationId"],
        )
        self.assertEqual(
            outcome["sourceRecordId"],
            action_callbacks[0]["payload"]["result"]["sourceRecordId"],
        )
        self.assertEqual(
            "MOCK_SENT",
            action_callbacks[0]["payload"]["result"]["delivery"]["status"],
        )

    def test_exact_replays_do_not_repeat_side_effects(self) -> None:
        first_event = self.request("ingestEvent", "/v1/events")
        replayed_event = self.request("ingestEvent", "/v1/events")
        self.assertFalse(first_event.body["replayed"])
        self.assertTrue(replayed_event.body["replayed"])
        self.assertEqual("DUPLICATE", replayed_event.body["intakeResult"])
        self.assertEqual(1, len(self.api.source_adapter.events))

        first_action = self.request(
            "executeApprovedAction",
            "/v1/actions/executions",
        )
        replayed_action = self.request(
            "executeApprovedAction",
            "/v1/actions/executions",
        )
        self.assertFalse(first_action.body["replayed"])
        self.assertTrue(replayed_action.body["replayed"])
        self.assertEqual(1, len(self.api.write_back_adapter.source_records))
        self.assertEqual(1, len(self.api.outcomes))

    def test_callback_retries_preserve_correlation(self) -> None:
        api = build_default_api(
            failures_by_operation={"EXECUTE_APPROVED_ACTION": 1},
            retry_policy=RetryPolicy(max_attempts=3),
            slack_webhook_url="",
        )
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        response = api.request(
            "POST",
            "/v1/actions/executions",
            deepcopy(example["x-hfs-headers"]),
            deepcopy(example["value"]),
        )

        self.assertEqual(202, response.status)
        self.assertEqual(
            2,
            api.callback_transport.attempts_by_operation[
                "EXECUTE_APPROVED_ACTION"
            ],
        )
        callback = next(
            item
            for item in api.callback_transport.received
            if item["payload"]["operation"] == "EXECUTE_APPROVED_ACTION"
        )
        self.assertEqual(
            example["value"]["correlationId"],
            callback["payload"]["correlationId"],
        )
        self.assertEqual([], api.pending_callbacks)

    def test_context_is_served_behind_the_frozen_contract(self) -> None:
        response = self.request("retrieveContext", "/v1/context/queries")
        self.assertEqual(200, response.status)
        self.assertEqual(
            "work-issue-001",
            response.body["workItem"]["recordId"],
        )
        self.assertEqual(1, len(response.body["evidence"]))

    def test_twilio_whatsapp_complaint_maps_to_safe_event_intake(self) -> None:
        response = self.api.ingest_twilio_whatsapp(
            {
                "MessageSid": "SM00000000000000000000000000000001",
                "From": "whatsapp:+23055550123",
                "To": "whatsapp:+14155238886",
                "Body": (
                    "I waited one hour, the pharmacy said there is no stock, "
                    "and my invoice looks duplicated."
                ),
            },
            observed_at="2026-06-13T08:45:00Z",
        )

        self.assertEqual(202, response.status)
        self.assertEqual("ACCEPTED", response.body["intakeResult"])
        event = next(iter(self.api.source_adapter.events.values()))
        attributes = event["data"]["attributes"]
        self.assertEqual("urn:hfs:source:twilio-whatsapp", event["source"])
        self.assertEqual("whatsapp-inbound", attributes["sourceChannel"])
        self.assertEqual("NO_ACTION_EXECUTED", attributes["protectedActionState"])
        self.assertEqual(False, attributes["messageBodyStored"])
        self.assertIn("wait_time", attributes["complaintTypes"])
        self.assertIn("pharmacy_delay", attributes["complaintTypes"])
        self.assertIn("billing", attributes["complaintTypes"])
        self.assertGreaterEqual(len(attributes["followUpQuestions"]), 5)
        self.assertGreaterEqual(len(attributes["rootCauseHypotheses"]), 3)
        self.assertIn("Recommendation", attributes["affectedPrimitives"])
        serialized_event = str(event)
        self.assertNotIn("+23055550123", serialized_event)
        self.assertNotIn("I waited one hour", serialized_event)

    def test_twilio_whatsapp_complaint_requires_body(self) -> None:
        response = self.api.ingest_twilio_whatsapp(
            {
                "MessageSid": "SM00000000000000000000000000000002",
                "From": "whatsapp:+23055550123",
                "Body": "",
            }
        )

        self.assertEqual(422, response.status)
        self.assertEqual(
            "VALIDATION_FAILED",
            response.body["errors"][0]["code"],
        )
        self.assertEqual("Body", response.body["errors"][0]["fieldName"])
        self.assertEqual(0, len(self.api.source_adapter.events))

    def test_event_content_hash_is_enforced_before_preservation(self) -> None:
        example = self.contract.examples["operations"]["ingestEvent"]["request"]
        body = deepcopy(example["value"])
        body["data"]["attributes"]["summary"] = "Tampered after hashing"

        response = self.api.request(
            "POST",
            "/v1/events",
            deepcopy(example["x-hfs-headers"]),
            body,
        )
        self.assertEqual(422, response.status)
        self.assertEqual(
            "VALIDATION_FAILED",
            response.body["errors"][0]["code"],
        )
        self.assertEqual("hfscontenthash", response.body["errors"][0]["fieldName"])
        self.assertEqual(0, len(self.api.source_adapter.events))

    def test_unapproved_action_fails_closed(self) -> None:
        example = self.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        body["approvalId"] = "approval-not-approved"
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Idempotency-Key"] = "action-unapproved-v1"
        body["idempotencyKey"] = "action-unapproved-v1"

        response = self.api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )
        self.assertEqual(403, response.status)
        self.assertEqual(
            "PERMISSION_DENIED",
            response.body["errors"][0]["code"],
        )
        self.assertEqual(0, len(self.api.write_back_adapter.source_records))
        self.assertEqual(0, len(self.api.outcomes))

    def test_slack_webhook_is_used_when_configured(self) -> None:
        transport = FakeSlackTransport()
        api = build_default_api(
            slack_webhook_url="https://hooks.slack.test/services/demo",
            slack_transport=transport,
        )
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]

        response = api.request(
            "POST",
            "/v1/actions/executions",
            deepcopy(example["x-hfs-headers"]),
            deepcopy(example["value"]),
        )

        self.assertEqual(202, response.status)
        self.assertEqual(1, len(transport.posts))
        self.assertIn(
            "Logia alert",
            transport.posts[0]["payload"]["text"],
        )
        record = next(iter(api.write_back_adapter.source_records.values()))
        self.assertEqual("SENT", record["delivery"]["status"])
        self.assertEqual("slack-webhook", record["delivery"]["provider"])
        self.assertEqual(
            ["incoming_webhook", "role_routed_alert"],
            record["delivery"]["slackFeatures"],
        )
        self.assertEqual(
            "slack-message-001",
            record["delivery"]["providerMessageId"],
        )

    def test_slack_approval_message_can_include_block_kit_buttons(self) -> None:
        transport = FakeSlackTransport()
        api = build_default_api(
            slack_webhook_url="https://hooks.slack.test/services/demo",
            slack_transport=transport,
        )
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        body["payload"]["approvalRequest"] = True

        response = api.request(
            "POST",
            "/v1/actions/executions",
            deepcopy(example["x-hfs-headers"]),
            body,
        )

        self.assertEqual(202, response.status)
        posted = transport.posts[0]["payload"]
        self.assertIn("blocks", posted)
        action_block = posted["blocks"][-1]
        self.assertEqual("actions", action_block["type"])
        action_ids = {
            element["action_id"] for element in action_block["elements"]
        }
        self.assertEqual(
            {
                "logia_approve",
                "logia_reject",
                "logia_modify",
            },
            action_ids,
        )
        record = next(iter(api.write_back_adapter.source_records.values()))
        self.assertIn(
            "block_kit_approval",
            record["delivery"]["slackFeatures"],
        )
        self.assertEqual(
            "SLACK_INTERACTIVITY",
            record["delivery"]["approvalMode"],
        )

    def test_slack_interaction_approves_pending_action_before_execution(self) -> None:
        signing_secret = "test-slack-signing-secret"
        api = build_default_api(
            slack_webhook_url="",
            whatsapp_provider_config=None,
        )
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        body["externalKey"] = "action-slack-interactive-approval"
        body["idempotencyKey"] = "action-slack-interactive-approval-v1"
        body["approvalId"] = "approval-slack-interactive-001"
        body["actionId"] = "action-slack-interactive-001"
        body["payload"] = {
            "targetRole": "Operations Manager",
            "targetChannel": "#logia-demo",
            "messageTitle": "Hospital operations approval",
            "messageBody": "Approve protected Logia operations actions.",
            "evidenceIds": ["evidence-hospital-001"],
            "sourceRecommendationId": body["recommendationId"],
            "approvalRequest": True,
        }
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Idempotency-Key"] = body["idempotencyKey"]
        api.write_back_adapter.register_approval(
            approval_id=body["approvalId"],
            tenant_key=body["tenantKey"],
            recommendation_id=body["recommendationId"],
            action_id=body["actionId"],
            status="PENDING",
        )

        blocked = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )
        self.assertEqual(403, blocked.status)
        self.assertEqual(0, len(api.outcomes))

        button_value = json.loads(
            api.write_back_adapter.slack_approval_blocks(
                tenant_key=body["tenantKey"],
                correlation_id=body["correlationId"],
                recommendation_id=body["recommendationId"],
                approval_id=body["approvalId"],
                action_ids=[body["actionId"]],
                title="Hospital operations approval",
                body="Approve protected Logia operations actions.",
            )[-1]["elements"][0]["value"]
        )
        slack_payload = {
            "type": "block_actions",
            "user": {"username": "ops-manager"},
            "actions": [
                {
                    "action_id": "logia_approve",
                    "value": json.dumps(button_value),
                }
            ],
        }
        signed_headers, raw_body = self.signed_slack_request(
            signing_secret=signing_secret,
            payload=slack_payload,
        )
        handler = SlackApprovalInteractionHandler(
            signing_secret=signing_secret,
            write_back_adapter=api.write_back_adapter,
            now_seconds=lambda: 1710000000,
        )
        decision = handler.handle(signed_headers, raw_body)
        self.assertEqual(200, decision.status)
        self.assertEqual("APPROVED", decision.body["decisionStatus"])
        self.assertTrue(decision.body["replace_original"])
        self.assertIn("Logia approval approved", decision.body["text"])

        approved = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )
        self.assertEqual(202, approved.status)
        self.assertEqual(1, len(api.outcomes))

        replay = handler.handle(signed_headers, raw_body)
        self.assertEqual(409, replay.status)
        self.assertEqual("SLACK_INTERACTION_REPLAYED", replay.body["code"])

    def test_slack_interaction_rejects_invalid_signature(self) -> None:
        signing_secret = "test-slack-signing-secret"
        api = build_default_api(slack_webhook_url="")
        handler = SlackApprovalInteractionHandler(
            signing_secret=signing_secret,
            write_back_adapter=api.write_back_adapter,
            now_seconds=lambda: 1710000000,
        )
        headers, raw_body = self.signed_slack_request(
            signing_secret=signing_secret,
            payload={"actions": []},
        )
        headers["X-Slack-Signature"] = "v0=invalid"

        response = handler.handle(headers, raw_body)

        self.assertEqual(401, response.status)
        self.assertEqual("SLACK_SIGNATURE_INVALID", response.body["code"])

    def test_slack_status_command_reports_approval_state(self) -> None:
        signing_secret = "test-slack-signing-secret"
        api = build_default_api(slack_webhook_url="")
        api.write_back_adapter.register_approval(
            approval_id="approval-logia-command-001",
            tenant_key="tenant-hfs-demo",
            recommendation_id="recommendation-logia-command-001",
            action_id="action-logia-command-001",
            status="PENDING",
        )
        headers, raw_body = self.signed_slack_form_request(
            signing_secret=signing_secret,
            form={
                "command": "/logia",
                "text": "status approval-logia-command-001",
                "user_name": "ops-manager",
            },
        )
        handler = SlackStatusCommandHandler(
            signing_secret=signing_secret,
            write_back_adapter=api.write_back_adapter,
            now_seconds=lambda: 1710000000,
        )

        response = handler.handle(headers, raw_body)

        self.assertEqual(200, response.status)
        self.assertEqual("ephemeral", response.body["response_type"])
        self.assertEqual("PENDING", response.body["decisionStatus"])
        self.assertIn("approval-logia-command-001", response.body["text"])

    def test_slack_status_command_rejects_invalid_signature(self) -> None:
        signing_secret = "test-slack-signing-secret"
        api = build_default_api(slack_webhook_url="")
        handler = SlackStatusCommandHandler(
            signing_secret=signing_secret,
            write_back_adapter=api.write_back_adapter,
            now_seconds=lambda: 1710000000,
        )
        headers, raw_body = self.signed_slack_form_request(
            signing_secret=signing_secret,
            form={"command": "/logia", "text": "status approval-demo"},
        )
        headers["X-Slack-Signature"] = "v0=invalid"

        response = handler.handle(headers, raw_body)

        self.assertEqual(401, response.status)
        self.assertEqual("SLACK_SIGNATURE_INVALID", response.body["code"])

    def test_malformed_slack_payload_is_rejected(self) -> None:
        example = self.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        del body["payload"]["messageBody"]
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Idempotency-Key"] = "action-slack-alert-malformed-v1"
        body["idempotencyKey"] = "action-slack-alert-malformed-v1"

        response = self.api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )

        self.assertEqual(422, response.status)
        self.assertEqual(
            "VALIDATION_FAILED",
            response.body["errors"][0]["code"],
        )
        self.assertEqual(
            "payload.messageBody",
            response.body["errors"][0]["fieldName"],
        )
        self.assertEqual(0, len(self.api.write_back_adapter.source_records))
        self.assertEqual(0, len(self.api.outcomes))

    def test_malformed_whatsapp_payload_is_rejected(self) -> None:
        example = self.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        body["actionType"] = "SEND_WHATSAPP_ALERT"
        body["sourceSystem"] = "whatsapp"
        body["externalKey"] = "action-whatsapp-alert-malformed"
        body["idempotencyKey"] = "action-whatsapp-alert-malformed-v1"
        body["approvalId"] = "approval-whatsapp-alert-malformed"
        body["actionId"] = "action-whatsapp-alert-malformed"
        del body["payload"]["messageBody"]
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Idempotency-Key"] = body["idempotencyKey"]
        self.api.write_back_adapter.register_approval(
            approval_id=body["approvalId"],
            tenant_key=body["tenantKey"],
            recommendation_id=body["recommendationId"],
            action_id=body["actionId"],
        )

        response = self.api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )

        self.assertEqual(422, response.status)
        self.assertEqual(
            "VALIDATION_FAILED",
            response.body["errors"][0]["code"],
        )
        self.assertEqual(
            "payload.messageBody",
            response.body["errors"][0]["fieldName"],
        )
        self.assertEqual(0, len(self.api.write_back_adapter.source_records))
        self.assertEqual(0, len(self.api.outcomes))

    def test_whatsapp_twilio_provider_is_used_when_configured(self) -> None:
        transport = FakeWhatsAppTransport()
        api = build_default_api(
            slack_webhook_url="",
            whatsapp_provider_config=WhatsAppProviderConfig(
                provider="twilio-whatsapp",
                account_sid="AC00000000000000000000000000000000",
                auth_token="test-token",
                from_number="whatsapp:+14155238886",
                to_number="whatsapp:+23055550123",
            ),
            whatsapp_transport=transport,
        )
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        body["actionType"] = "SEND_WHATSAPP_ALERT"
        body["sourceSystem"] = "whatsapp"
        body["externalKey"] = "action-whatsapp-alert-real-capable"
        body["idempotencyKey"] = "action-whatsapp-alert-real-capable-v1"
        body["approvalId"] = "approval-whatsapp-alert-real-capable"
        body["actionId"] = "action-whatsapp-alert-real-capable"
        body["payload"] = {
            "targetRole": "Patient Experience Lead",
            "targetChannel": "wa-role-patient-experience-lead",
            "messageTitle": "Logia hospital action",
            "messageBody": "Coordinate approved internal hospital update.",
            "evidenceIds": ["evidence-hospital-001"],
            "sourceRecommendationId": body["recommendationId"],
        }
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Idempotency-Key"] = body["idempotencyKey"]
        api.write_back_adapter.register_approval(
            approval_id=body["approvalId"],
            tenant_key=body["tenantKey"],
            recommendation_id=body["recommendationId"],
            action_id=body["actionId"],
        )

        response = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )

        self.assertEqual(202, response.status)
        self.assertEqual(1, len(transport.posts))
        record = next(iter(api.write_back_adapter.source_records.values()))
        self.assertEqual("SENT", record["delivery"]["status"])
        self.assertEqual("twilio-whatsapp", record["delivery"]["provider"])
        self.assertEqual(
            "whatsapp-message-001",
            record["delivery"]["providerMessageId"],
        )

    def test_whatsapp_meta_provider_is_used_when_configured(self) -> None:
        transport = FakeWhatsAppTransport()
        api = build_default_api(
            slack_webhook_url="",
            whatsapp_provider_config=WhatsAppProviderConfig(
                provider="meta-whatsapp-cloud",
                phone_number_id="1234567890123456",
                access_token="test-meta-token",
                to_number="+23055550123",
                graph_version="v25.0",
            ),
            whatsapp_transport=transport,
        )
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        body = deepcopy(example["value"])
        body["actionType"] = "SEND_WHATSAPP_ALERT"
        body["sourceSystem"] = "whatsapp"
        body["externalKey"] = "action-whatsapp-alert-meta"
        body["idempotencyKey"] = "action-whatsapp-alert-meta-v1"
        body["approvalId"] = "approval-whatsapp-alert-meta"
        body["actionId"] = "action-whatsapp-alert-meta"
        body["payload"] = {
            "targetRole": "Operations Manager",
            "targetChannel": "wa-role-operations-manager",
            "messageTitle": "Logia action",
            "messageBody": "Please check the approved stock request.",
            "evidenceIds": ["evidence-hospital-001"],
            "sourceRecommendationId": body["recommendationId"],
        }
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Idempotency-Key"] = body["idempotencyKey"]
        api.write_back_adapter.register_approval(
            approval_id=body["approvalId"],
            tenant_key=body["tenantKey"],
            recommendation_id=body["recommendationId"],
            action_id=body["actionId"],
        )

        response = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )

        self.assertEqual(202, response.status)
        self.assertEqual(1, len(transport.posts))
        self.assertEqual(
            "meta-whatsapp-cloud",
            transport.posts[0]["config"].provider,
        )
        record = next(iter(api.write_back_adapter.source_records.values()))
        self.assertEqual("SENT", record["delivery"]["status"])
        self.assertEqual(
            "meta-whatsapp-cloud",
            record["delivery"]["provider"],
        )

    def test_whatsapp_provider_env_prefers_meta_cloud_api(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "META_WHATSAPP_PHONE_NUMBER_ID": "1234567890123456",
                "META_WHATSAPP_ACCESS_TOKEN": "test-meta-token",
                "META_WHATSAPP_TO": "+23055550123",
                "TWILIO_ACCOUNT_SID": "AC00000000000000000000000000000000",
                "TWILIO_AUTH_TOKEN": "test-token",
                "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
                "TWILIO_WHATSAPP_TO": "whatsapp:+23055550123",
            },
            clear=False,
        ):
            api = build_default_api(
                slack_webhook_url="",
                whatsapp_transport=FakeWhatsAppTransport(),
            )

        self.assertEqual(
            "meta-whatsapp-cloud",
            api.write_back_adapter.whatsapp_provider_config.provider,
        )

    def test_hospital_action_types_record_delivery_evidence(self) -> None:
        example = self.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        hospital_action_types = [
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
        ]

        for index, action_type in enumerate(hospital_action_types, start=1):
            body = deepcopy(example["value"])
            body["externalKey"] = f"hospital-action-{index}"
            body["idempotencyKey"] = f"hospital-action-{index}-v1"
            body["approvalId"] = f"hospital-approval-{index}"
            body["actionId"] = f"hospital-action-{index}"
            body["actionType"] = action_type
            if action_type == "SEND_SLACK_ALERT":
                body["payload"] = {
                    "targetRole": "Operations Manager",
                    "targetChannel": "#logia-demo",
                    "messageTitle": "Logia hospital action",
                    "messageBody": f"Logia hospital action {action_type}",
                    "evidenceIds": ["evidence-hospital-001"],
                    "sourceRecommendationId": body["recommendationId"],
                }
            elif action_type == "SEND_WHATSAPP_ALERT":
                body["sourceSystem"] = "whatsapp"
                body["payload"] = {
                    "targetRole": "Pharmacy Lead",
                    "targetChannel": "wa-role-pharmacy-lead",
                    "messageTitle": "Logia pharmacy restock",
                    "messageBody": f"Logia hospital action {action_type}",
                    "evidenceIds": ["evidence-hospital-001"],
                    "sourceRecommendationId": body["recommendationId"],
                }
            elif action_type == "SEND_VENDOR_EMAIL":
                body["sourceSystem"] = "email"
                body["payload"] = {
                    "targetRole": "Vendor Coordinator",
                    "targetChannel": "email-role-vendor-coordinator",
                    "messageTitle": "Hospital stock follow-up",
                    "messageBody": f"Logia hospital action {action_type}",
                    "supplierAlias": "partner-pharmacy-supplier",
                    "evidenceIds": ["evidence-hospital-001"],
                    "sourceRecommendationId": body["recommendationId"],
                }
            else:
                body["payload"] = {
                    "targetRole": "Operations Manager",
                    "messageBody": f"Logia hospital action {action_type}",
                }
            headers = deepcopy(example["x-hfs-headers"])
            headers["X-Idempotency-Key"] = body["idempotencyKey"]
            self.api.write_back_adapter.register_approval(
                approval_id=body["approvalId"],
                tenant_key=body["tenantKey"],
                recommendation_id=body["recommendationId"],
                action_id=body["actionId"],
            )

            response = self.api.request(
                "POST",
                "/v1/actions/executions",
                headers,
                body,
            )
            self.assertEqual(202, response.status, action_type)

        records = list(self.api.write_back_adapter.source_records.values())
        self.assertEqual(len(hospital_action_types), len(records))
        delivery_by_type = {
            record["actionType"]: record["delivery"] for record in records
        }
        self.assertEqual(
            "MOCK_SENT",
            delivery_by_type["SEND_SLACK_ALERT"]["status"],
        )
        self.assertIn(
            "SLACK_WEBHOOK_URL",
            delivery_by_type["SEND_SLACK_ALERT"]["fallbackReason"],
        )
        self.assertEqual(
            "MOCK_SENT",
            delivery_by_type["SEND_WHATSAPP_ALERT"]["status"],
        )
        self.assertIn(
            "credentials",
            delivery_by_type["SEND_WHATSAPP_ALERT"]["fallbackReason"],
        )
        self.assertEqual(
            "QUEUED",
            delivery_by_type["REQUEST_BED_CLEANING"]["status"],
        )
        self.assertEqual(
            "QUEUED",
            delivery_by_type["SEND_VENDOR_EMAIL"]["status"],
        )
        self.assertEqual(
            "vendor_email_queued",
            delivery_by_type["SEND_VENDOR_EMAIL"]["metricKey"],
        )
        self.assertEqual(
            "hospital_action_queued",
            delivery_by_type["REQUEST_BED_CLEANING"]["metricKey"],
        )

    def test_nexavenu_revenue_action_types_record_delivery_evidence(
        self,
    ) -> None:
        example = self.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        revenue_action_types = [
            "CREATE_NURTURE_TASK",
            "DRAFT_CHAMPION_EMAIL",
            "UPDATE_OPPORTUNITY_STAGE",
            "ASSIGN_CONTENT_ASSET",
            "CREATE_SOLUTION_CONSULTANT_HANDOFF",
            "CAPTURE_RETENTION_ASCENSION_OUTCOME",
        ]

        for index, action_type in enumerate(revenue_action_types, start=1):
            body = deepcopy(example["value"])
            body["purpose"] = "EXECUTE_APPROVED_REVENUE_ACTION"
            body["externalKey"] = f"nexavenu-revenue-action-{index}"
            body["idempotencyKey"] = f"nexavenu-revenue-action-{index}-v1"
            body["recommendationId"] = "recommendation-nexavenu-revenue-001"
            body["approvalId"] = f"nexavenu-approval-{index}"
            body["actionId"] = f"nexavenu-revenue-action-{index}"
            body["targetEntityId"] = "prospect-synth-liftops"
            body["actionType"] = action_type
            body["sourceSystem"] = "salesforce-revenue-cloud"
            body["payload"] = {
                "channel": "SALESFORCE_REVENUE_MOCK",
                "targetRole": "Revenue Owner",
                "messageBody": f"Nexavenu revenue action {action_type}",
            }
            headers = deepcopy(example["x-hfs-headers"])
            headers["X-Idempotency-Key"] = body["idempotencyKey"]
            self.api.write_back_adapter.register_approval(
                approval_id=body["approvalId"],
                tenant_key=body["tenantKey"],
                recommendation_id=body["recommendationId"],
                action_id=body["actionId"],
            )

            response = self.api.request(
                "POST",
                "/v1/actions/executions",
                headers,
                body,
            )
            self.assertEqual(202, response.status, action_type)
            self.assertEqual(body["correlationId"], response.body["correlationId"])

        records = list(self.api.write_back_adapter.source_records.values())
        self.assertEqual(len(revenue_action_types), len(records))
        delivery_by_type = {
            record["actionType"]: record["delivery"] for record in records
        }
        self.assertEqual(
            "nexavenu_champion_email_drafted",
            delivery_by_type["DRAFT_CHAMPION_EMAIL"]["metricKey"],
        )
        self.assertEqual(
            "nexavenu_solution_consultant_handoff_created",
            delivery_by_type["CREATE_SOLUTION_CONSULTANT_HANDOFF"][
                "metricKey"
            ],
        )
        self.assertEqual(len(revenue_action_types), len(self.api.outcomes))
        self.assertTrue(
            all(
                outcome["correlationId"] == example["value"]["correlationId"]
                for outcome in self.api.outcomes.values()
            )
        )


if __name__ == "__main__":
    unittest.main()
