from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import os
from typing import Any


class AdapterUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class AdapterResult:
    output: dict[str, Any]
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float


class ScriptedMockAdapter:
    interface_version = "hfs.generate.v1"

    def __init__(
        self,
        *,
        adapter_key: str,
        output: dict[str, Any],
        mode: str = "success",
        latency_ms: int,
        cost_usd: float,
    ) -> None:
        self.adapter_key = adapter_key
        self.output = deepcopy(output)
        if mode not in {"success", "unavailable", "invalid"}:
            raise ValueError(f"Unsupported mock adapter mode: {mode}")
        self.mode = mode
        self.latency_ms = latency_ms
        self.cost_usd = cost_usd
        self.calls = 0

    def generate(self, request: dict[str, Any]) -> AdapterResult:
        self.calls += 1
        if self.mode == "unavailable":
            raise AdapterUnavailable(f"{self.adapter_key} is unavailable")
        output = deepcopy(self.output)
        if self.mode == "invalid":
            output.pop("evidenceIds", None)
        return AdapterResult(
            output=output,
            input_tokens=840,
            output_tokens=156,
            latency_ms=self.latency_ms,
            cost_usd=self.cost_usd,
        )


class MockAlphaAdapter(ScriptedMockAdapter):
    def __init__(
        self,
        output: dict[str, Any],
        *,
        mode: str = "success",
    ) -> None:
        super().__init__(
            adapter_key="mock-alpha-adapter",
            output=output,
            mode=mode,
            latency_ms=2100,
            cost_usd=0.031,
        )


class MockBetaAdapter(ScriptedMockAdapter):
    def __init__(
        self,
        output: dict[str, Any],
        *,
        mode: str = "success",
    ) -> None:
        super().__init__(
            adapter_key="mock-beta-adapter",
            output=output,
            mode=mode,
            latency_ms=3200,
            cost_usd=0.039,
        )


class DeepSeekOpenAICompatibleAdapter:
    interface_version = "hfs.generate.v1"
    adapter_key = "deepseek-openai-compatible-adapter"
    api_key_env_var = "DEEPSEEK_API_KEY"
    base_url = "https://api.deepseek.com"

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled
        self.calls = 0

    def generate(self, request: dict[str, Any]) -> AdapterResult:
        self.calls += 1
        if not self.enabled:
            raise AdapterUnavailable(
                "DeepSeek adapter is disabled by default; enable it only "
                "after approved credentials, budget, and policy are configured."
            )
        if not os.environ.get(self.api_key_env_var):
            raise AdapterUnavailable(
                f"{self.api_key_env_var} is not configured."
            )
        raise AdapterUnavailable(
            "DeepSeek live invocation is intentionally not implemented in the "
            "demo runtime; use the LLM Open Connector or a governed production "
            "adapter behind the same hfs.generate.v1 interface."
        )
