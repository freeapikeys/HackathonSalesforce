from __future__ import annotations

import unittest
from copy import deepcopy

from mock_runtime import (
    RetryPolicy,
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
            "North Star alert",
            transport.posts[0]["payload"]["text"],
        )
        record = next(iter(api.write_back_adapter.source_records.values()))
        self.assertEqual("SENT", record["delivery"]["status"])
        self.assertEqual("slack-webhook", record["delivery"]["provider"])
        self.assertEqual(
            "slack-message-001",
            record["delivery"]["providerMessageId"],
        )

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
            "messageTitle": "North Star hospital action",
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
                    "targetChannel": "#north-star-demo",
                    "messageTitle": "North Star hospital action",
                    "messageBody": f"North Star hospital action {action_type}",
                    "evidenceIds": ["evidence-hospital-001"],
                    "sourceRecommendationId": body["recommendationId"],
                }
            elif action_type == "SEND_WHATSAPP_ALERT":
                body["sourceSystem"] = "whatsapp"
                body["payload"] = {
                    "targetRole": "Pharmacy Lead",
                    "targetChannel": "wa-role-pharmacy-lead",
                    "messageTitle": "North Star pharmacy restock",
                    "messageBody": f"North Star hospital action {action_type}",
                    "evidenceIds": ["evidence-hospital-001"],
                    "sourceRecommendationId": body["recommendationId"],
                }
            elif action_type == "SEND_VENDOR_EMAIL":
                body["sourceSystem"] = "email"
                body["payload"] = {
                    "targetRole": "Vendor Coordinator",
                    "targetChannel": "email-role-vendor-coordinator",
                    "messageTitle": "Hospital stock follow-up",
                    "messageBody": f"North Star hospital action {action_type}",
                    "supplierAlias": "partner-pharmacy-supplier",
                    "evidenceIds": ["evidence-hospital-001"],
                    "sourceRecommendationId": body["recommendationId"],
                }
            else:
                body["payload"] = {
                    "targetRole": "Operations Manager",
                    "messageBody": f"North Star hospital action {action_type}",
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


if __name__ == "__main__":
    unittest.main()
