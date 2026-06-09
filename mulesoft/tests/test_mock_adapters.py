from __future__ import annotations

import unittest
from copy import deepcopy

from mock_runtime import RetryPolicy, build_default_api


class MockAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.api = build_default_api()
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

    def test_retail_action_types_record_delivery_evidence(self) -> None:
        example = self.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        retail_action_types = [
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
        ]

        for index, action_type in enumerate(retail_action_types, start=1):
            body = deepcopy(example["value"])
            body["externalKey"] = f"retail-action-{index}"
            body["idempotencyKey"] = f"retail-action-{index}-v1"
            body["approvalId"] = f"retail-approval-{index}"
            body["actionId"] = f"retail-action-{index}"
            body["actionType"] = action_type
            body["payload"] = {
                "targetRole": "Duty Manager",
                "messageBody": f"North Star action {action_type}",
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
        self.assertEqual(len(retail_action_types), len(records))
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
            delivery_by_type["SEND_WHATSAPP_STYLE_ALERT"]["status"],
        )
        self.assertIn(
            "credentials",
            delivery_by_type["SEND_WHATSAPP_STYLE_ALERT"]["fallbackReason"],
        )


if __name__ == "__main__":
    unittest.main()
