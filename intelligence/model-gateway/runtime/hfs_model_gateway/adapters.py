from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Callable


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
    model_env_var = "DEEPSEEK_MODEL"
    base_url = "https://api.deepseek.com"

    def __init__(
        self,
        *,
        enabled: bool = False,
        transport: Callable[
            [str, dict[str, str], dict[str, Any]],
            tuple[int, dict[str, Any]],
        ]
        | None = None,
    ) -> None:
        self.enabled = enabled
        self.transport = transport or self._post_json
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
        started = time.monotonic()
        payload = self._chat_payload(request)
        status, response = self.transport(
            self._chat_completions_url(),
            {
                "Authorization": f"Bearer {os.environ[self.api_key_env_var]}",
                "Content-Type": "application/json",
            },
            payload,
        )
        if status < 200 or status >= 300:
            raise AdapterUnavailable(f"DeepSeek returned HTTP {status}.")

        output = self._normalized_output(response)
        usage = response.get("usage") if isinstance(response, dict) else {}
        return AdapterResult(
            output=output,
            input_tokens=int((usage or {}).get("prompt_tokens") or 0),
            output_tokens=int((usage or {}).get("completion_tokens") or 0),
            latency_ms=max(1, int((time.monotonic() - started) * 1000)),
            cost_usd=0.0,
        )

    def _chat_payload(self, request: dict[str, Any]) -> dict[str, Any]:
        messages = [
            {
                "role": str(message["role"]).lower(),
                "content": message["content"],
            }
            for message in request["messages"]
        ]
        messages.append(
            {
                "role": "system",
                "content": (
                    "Return only a JSON object matching the requested schema. "
                    "Do not approve or execute protected actions."
                ),
            }
        )
        return {
            "model": os.environ.get(self.model_env_var, "deepseek-chat"),
            "messages": messages,
            "temperature": request["invocationPolicy"]["temperature"],
            "max_tokens": request["invocationPolicy"]["maximumOutputTokens"],
            "response_format": {"type": "json_object"},
        }

    def _normalized_output(self, response: dict[str, Any]) -> dict[str, Any]:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise AdapterUnavailable("DeepSeek response did not include choices.")
        message = choices[0].get("message") if isinstance(choices[0], dict) else {}
        content = (message or {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise AdapterUnavailable("DeepSeek response did not include content.")
        try:
            parsed = json.loads(self._json_object_text(content))
        except json.JSONDecodeError as error:
            raise AdapterUnavailable(
                "DeepSeek response content was not valid JSON."
            ) from error
        if not isinstance(parsed, dict):
            raise AdapterUnavailable("DeepSeek response content was not an object.")
        return parsed

    def _chat_completions_url(self) -> str:
        return self.base_url.rstrip("/") + "/chat/completions"

    @staticmethod
    def _json_object_text(content: str) -> str:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`").strip()
            if stripped.lower().startswith("json"):
                stripped = stripped[4:].strip()
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end < start:
            return stripped
        return stripped[start : end + 1]

    @staticmethod
    def _post_json(
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8", errors="replace")
                status = getattr(response, "status", response.getcode())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise AdapterUnavailable("DeepSeek request failed.") from error
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as error:
            raise AdapterUnavailable("DeepSeek returned invalid JSON.") from error
        return status, parsed
