from __future__ import annotations

import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from hfs_model_gateway import (
    AdapterUnavailable,
    DeepSeekOpenAICompatibleAdapter,
    DeterministicRouter,
    MockAlphaAdapter,
    MockBetaAdapter,
    ModelGateway,
    ModelGatewayContract,
)
from hfs_model_gateway.contract import ModelContractError, content_hash


class FixedClock:
    def __init__(self) -> None:
        self.sequence = 0

    def __call__(self) -> str:
        self.sequence += 1
        return f"2026-06-05T08:30:{self.sequence:02d}Z"


class ModelGatewayRuntimeTest(unittest.TestCase):
    def build_gateway(
        self,
        *,
        alpha_mode: str = "success",
        beta_mode: str = "success",
    ):
        contract = ModelGatewayContract()
        fixture = contract.fixture
        clock = FixedClock()
        router = DeterministicRouter(
            contract=contract,
            profile=fixture["profiles"][0],
            deployments=fixture["deployments"],
            policy=fixture["policies"][0],
            clock=clock,
        )
        output = fixture["normalizedResponses"][0]["output"]
        alpha = MockAlphaAdapter(output, mode=alpha_mode)
        beta = MockBetaAdapter(output, mode=beta_mode)
        deepseek = DeepSeekOpenAICompatibleAdapter()
        gateway = ModelGateway(
            contract=contract,
            router=router,
            adapters={
                alpha.adapter_key: alpha,
                beta.adapter_key: beta,
                deepseek.adapter_key: deepseek,
            },
            clock=clock,
        )
        return contract, gateway, alpha, beta, deepseek

    def requests(self, contract):
        route = deepcopy(contract.fixture["routingRequests"]["primary"])
        generate = deepcopy(contract.fixture["generateRequest"])
        return route, generate

    def test_primary_deployment_success_is_fully_audited(self) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway()
        route, generate = self.requests(contract)

        result = gateway.generate(route, generate)

        self.assertEqual("mock-alpha-primary", result.response["deploymentKey"])
        self.assertFalse(result.decision["fallback"])
        self.assertEqual(["SUCCEEDED"], [
            item["status"] for item in result.audit["attempts"]
        ])
        self.assertEqual("1.0.0", result.audit["profileVersion"])
        self.assertEqual("1.0.0", result.audit["policyVersion"])
        self.assertEqual(
            content_hash(generate),
            result.audit["inputHash"],
        )
        self.assertEqual(
            content_hash(result.response["output"]),
            result.audit["outputHash"],
        )
        self.assertEqual(1, alpha.calls)
        self.assertEqual(0, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_same_request_falls_back_to_second_qualified_adapter(self) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway(
            alpha_mode="unavailable"
        )
        route, generate = self.requests(contract)

        result = gateway.generate(route, generate)

        self.assertEqual("mock-beta-private", result.response["deploymentKey"])
        self.assertTrue(result.decision["fallback"])
        self.assertTrue(result.audit["fallbackUsed"])
        self.assertEqual(
            ["UNAVAILABLE", "SUCCEEDED"],
            [item["status"] for item in result.audit["attempts"]],
        )
        self.assertTrue(result.audit["attempts"][0]["retryable"])
        self.assertEqual(1, alpha.calls)
        self.assertEqual(1, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_policy_selected_fallback_is_recorded_without_calling_primary(
        self,
    ) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway()
        route, generate = self.requests(contract)
        route["unavailableDeploymentKeys"] = ["mock-alpha-primary"]

        result = gateway.generate(route, generate)

        self.assertEqual("mock-beta-private", result.response["deploymentKey"])
        self.assertTrue(result.decision["fallback"])
        self.assertTrue(result.audit["fallbackUsed"])
        self.assertEqual(
            ["SUCCEEDED"],
            [item["status"] for item in result.audit["attempts"]],
        )
        self.assertEqual(0, alpha.calls)
        self.assertEqual(1, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_invalid_primary_output_uses_qualified_fallback(self) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway(
            alpha_mode="invalid"
        )
        route, generate = self.requests(contract)

        result = gateway.generate(route, generate)

        self.assertEqual("mock-beta-private", result.response["deploymentKey"])
        self.assertEqual(
            ["INVALID_OUTPUT", "SUCCEEDED"],
            [item["status"] for item in result.audit["attempts"]],
        )
        self.assertFalse(result.audit["attempts"][0]["retryable"])
        self.assertTrue(result.audit["fallbackUsed"])
        self.assertEqual(1, alpha.calls)
        self.assertEqual(1, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_all_invalid_outputs_fail_closed(self) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway(
            alpha_mode="invalid",
            beta_mode="invalid",
        )
        route, generate = self.requests(contract)

        result = gateway.generate(route, generate)

        self.assertIsNone(result.response)
        self.assertEqual("FAILED_CLOSED", result.audit["status"])
        self.assertEqual(
            ["INVALID_OUTPUT", "INVALID_OUTPUT"],
            [item["status"] for item in result.audit["attempts"]],
        )
        self.assertIsNone(result.audit["selectedDeploymentKey"])
        self.assertIsNone(result.audit["outputHash"])
        self.assertEqual(1, alpha.calls)
        self.assertEqual(1, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_restricted_data_fails_before_any_adapter_call(self) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway()
        route, generate = self.requests(contract)
        route["dataClassification"] = "RESTRICTED"
        generate["context"]["dataClassification"] = "RESTRICTED"

        result = gateway.generate(route, generate)

        self.assertIsNone(result.response)
        self.assertEqual(
            "NO_QUALIFIED_DEPLOYMENT",
            result.decision["decision"],
        )
        self.assertEqual("FAILED_CLOSED", result.audit["status"])
        self.assertEqual(
            {"POLICY_REJECTED"},
            {item["status"] for item in result.audit["attempts"]},
        )
        self.assertEqual(0, alpha.calls)
        self.assertEqual(0, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_residency_capability_cost_and_availability_fail_closed(self) -> None:
        mutations = (
            ("residencyRegion", "eu"),
            ("requiredCapabilities", ["CHAT", "VISION"]),
            ("maximumLatencyMs", 1000),
            ("maximumCostUsd", 0.001),
            (
                "unavailableDeploymentKeys",
                ["mock-alpha-primary", "mock-beta-private"],
            ),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                contract, gateway, alpha, beta, deepseek = self.build_gateway()
                route, generate = self.requests(contract)
                route[field] = value

                result = gateway.generate(route, generate)

                self.assertIsNone(result.response)
                self.assertEqual("FAILED_CLOSED", result.audit["status"])
                self.assertEqual(0, alpha.calls)
                self.assertEqual(0, beta.calls)
                self.assertEqual(0, deepseek.calls)

    def test_request_identity_and_classification_must_match(self) -> None:
        contract, gateway, _, _, _ = self.build_gateway()
        route, generate = self.requests(contract)
        generate["purpose"] = "DIFFERENT_PURPOSE"
        with self.assertRaises(ModelContractError):
            gateway.generate(route, generate)

        route, generate = self.requests(contract)
        generate["context"]["dataClassification"] = "INTERNAL"
        with self.assertRaises(ModelContractError):
            gateway.generate(route, generate)

    def test_tenant_purpose_and_language_policy_fail_closed(self) -> None:
        scenarios = (
            ("tenantKey", "other-tenant"),
            ("purpose", "UNAPPROVED_PURPOSE"),
            ("language", "de"),
        )
        for field, value in scenarios:
            with self.subTest(field=field):
                contract, gateway, alpha, beta, deepseek = self.build_gateway()
                route, generate = self.requests(contract)
                route[field] = value
                if field in {"tenantKey", "purpose"}:
                    generate[field] = value

                result = gateway.generate(route, generate)

                self.assertIsNone(result.response)
                self.assertEqual("FAILED_CLOSED", result.audit["status"])
                self.assertEqual(0, alpha.calls)
                self.assertEqual(0, beta.calls)
                self.assertEqual(0, deepseek.calls)

    def test_deepseek_deployment_is_configured_but_disabled_by_default(self) -> None:
        contract, gateway, alpha, beta, deepseek = self.build_gateway()
        route, generate = self.requests(contract)
        route["unavailableDeploymentKeys"] = [
            "mock-alpha-primary",
            "mock-beta-private",
        ]

        result = gateway.generate(route, generate)

        self.assertIsNone(result.response)
        self.assertEqual("FAILED_CLOSED", result.audit["status"])
        self.assertIn(
            ("deepseek-cloud-disabled", "DEPLOYMENT_NOT_ACTIVE"),
            {
                (check["deploymentKey"], check["reasonCode"])
                for check in result.decision["checks"]
            },
        )
        self.assertEqual(0, alpha.calls)
        self.assertEqual(0, beta.calls)
        self.assertEqual(0, deepseek.calls)

    def test_enabled_deepseek_adapter_uses_openai_compatible_generation(
        self,
    ) -> None:
        contract = ModelGatewayContract()
        _, generate = self.requests(contract)
        expected_output = deepcopy(
            contract.fixture["normalizedResponses"][0]["output"]
        )
        posts = []

        def fake_transport(url, headers, payload):
            posts.append({"url": url, "headers": headers, "payload": payload})
            return 200, {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(expected_output),
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 111,
                    "completion_tokens": 44,
                },
            }

        with patch.dict(
            "os.environ",
            {
                "DEEPSEEK_API_KEY": "test-key",
                "DEEPSEEK_MODEL": "deepseek-chat",
            },
            clear=False,
        ):
            adapter = DeepSeekOpenAICompatibleAdapter(
                enabled=True,
                transport=fake_transport,
            )
            result = adapter.generate(generate)

        self.assertEqual(expected_output, result.output)
        self.assertEqual(111, result.input_tokens)
        self.assertEqual(44, result.output_tokens)
        self.assertEqual(0.0, result.cost_usd)
        self.assertEqual(1, len(posts))
        self.assertEqual(
            "https://api.deepseek.com/chat/completions",
            posts[0]["url"],
        )
        self.assertEqual(
            "Bearer test-key",
            posts[0]["headers"]["Authorization"],
        )
        self.assertEqual("deepseek-chat", posts[0]["payload"]["model"])
        self.assertEqual(
            {"type": "json_object"},
            posts[0]["payload"]["response_format"],
        )

    def test_enabled_deepseek_adapter_requires_api_key(self) -> None:
        contract = ModelGatewayContract()
        _, generate = self.requests(contract)
        adapter = DeepSeekOpenAICompatibleAdapter(enabled=True)

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(AdapterUnavailable):
                adapter.generate(generate)


if __name__ == "__main__":
    unittest.main()
