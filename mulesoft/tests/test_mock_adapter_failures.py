from __future__ import annotations

import unittest
from copy import deepcopy

from mock_runtime import RetryPolicy, build_default_api


class MockAdapterFailureTest(unittest.TestCase):
    def request_example(self, api, operation_id: str, path: str):
        example = api.contract.examples["operations"][operation_id]["request"]
        return api.request(
            "POST",
            path,
            deepcopy(example["x-hfs-headers"]),
            deepcopy(example["value"]),
        )

    def test_malformed_event_is_non_retryable_validation_failure(self) -> None:
        api = build_default_api()
        example = api.contract.examples["operations"]["ingestEvent"]["request"]
        body = deepcopy(example["value"])
        del body["source"]

        response = api.request(
            "POST",
            "/v1/events",
            deepcopy(example["x-hfs-headers"]),
            body,
        )
        self.assertEqual(422, response.status)
        self.assertEqual("VALIDATION_FAILED", response.body["errors"][0]["code"])
        self.assertFalse(response.body["errors"][0]["retryable"])
        self.assertEqual(0, len(api.source_adapter.events))

    def test_changed_content_under_same_key_is_conflict(self) -> None:
        api = build_default_api()
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        headers = deepcopy(example["x-hfs-headers"])
        body = deepcopy(example["value"])

        first = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            body,
        )
        changed = deepcopy(body)
        changed["payload"]["language"] = "fr"
        conflict = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            changed,
        )

        self.assertEqual(202, first.status)
        self.assertEqual(409, conflict.status)
        self.assertEqual(
            "IDEMPOTENCY_CONFLICT",
            conflict.body["errors"][0]["code"],
        )
        self.assertFalse(conflict.body["errors"][0]["retryable"])
        self.assertEqual(1, len(api.write_back_adapter.source_records))
        self.assertEqual(1, len(api.outcomes))

    def test_retryable_outcome_failure_recovers_without_second_write(self) -> None:
        api = build_default_api(outcome_failures=1)

        first = self.request_example(
            api,
            "executeApprovedAction",
            "/v1/actions/executions",
        )
        second = self.request_example(
            api,
            "executeApprovedAction",
            "/v1/actions/executions",
        )

        self.assertEqual(503, first.status)
        self.assertEqual(
            "RETRYABLE_DEPENDENCY_FAILURE",
            first.body["errors"][0]["code"],
        )
        self.assertTrue(first.body["errors"][0]["retryable"])
        self.assertEqual("1", first.headers["Retry-After"])
        self.assertEqual(202, second.status)
        self.assertFalse(second.body["replayed"])
        self.assertEqual(1, len(api.write_back_adapter.source_records))
        self.assertEqual(1, len(api.outcomes))

    def test_exhausted_callback_is_queued_then_replayed(self) -> None:
        api = build_default_api(
            failures_by_operation={"EXECUTE_APPROVED_ACTION": 3},
            retry_policy=RetryPolicy(max_attempts=2),
        )
        response = self.request_example(
            api,
            "executeApprovedAction",
            "/v1/actions/executions",
        )

        self.assertEqual(202, response.status)
        self.assertEqual(1, len(api.pending_callbacks))
        self.assertEqual(
            2,
            api.callback_transport.attempts_by_operation[
                "EXECUTE_APPROVED_ACTION"
            ],
        )

        remaining = api.flush_callbacks()
        self.assertEqual(0, remaining)
        self.assertEqual(
            4,
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
            response.body["correlationId"],
            callback["payload"]["correlationId"],
        )

    def test_outcome_callback_replay_does_not_duplicate_storage(self) -> None:
        api = build_default_api()
        first = self.request_example(
            api,
            "receiveOutcomeCallback",
            "/v1/outcomes/callbacks",
        )
        replay = self.request_example(
            api,
            "receiveOutcomeCallback",
            "/v1/outcomes/callbacks",
        )

        self.assertEqual(200, first.status)
        self.assertFalse(first.body["replayed"])
        self.assertEqual(200, replay.status)
        self.assertTrue(replay.body["replayed"])
        self.assertEqual(1, len(api.outcomes))
        callback_count = sum(
            item["payload"]["operation"] == "CAPTURE_OUTCOME"
            for item in api.callback_transport.received
        )
        self.assertEqual(1, callback_count)

    def test_tenant_mismatch_fails_before_side_effects(self) -> None:
        api = build_default_api()
        example = api.contract.examples["operations"][
            "executeApprovedAction"
        ]["request"]
        headers = deepcopy(example["x-hfs-headers"])
        headers["X-Tenant-Id"] = "different-tenant"

        response = api.request(
            "POST",
            "/v1/actions/executions",
            headers,
            deepcopy(example["value"]),
        )

        self.assertEqual(409, response.status)
        self.assertEqual("TENANT_MISMATCH", response.body["errors"][0]["code"])
        self.assertFalse(response.body["errors"][0]["retryable"])
        self.assertEqual(0, len(api.write_back_adapter.source_records))
        self.assertEqual(0, len(api.outcomes))


if __name__ == "__main__":
    unittest.main()
