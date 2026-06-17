#!/usr/bin/env python3
"""Verify local DeepSeek runtime configuration without exposing secrets."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "intelligence" / "model-gateway" / "runtime"
PLACEHOLDER_VALUES = {
    "",
    "<set-locally-or-in-secret-manager>",
    "changeme",
    "change-me",
    "test-key",
}


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def masked(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def configured() -> tuple[bool, list[str]]:
    failures: list[str] = []
    enabled = os.getenv("DEEPSEEK_ENABLED", "").strip().lower()
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    if enabled not in {"1", "true", "yes", "on"}:
        failures.append("DEEPSEEK_ENABLED must be true/1/yes/on.")
    if api_key.lower() in PLACEHOLDER_VALUES or not api_key:
        failures.append("DEEPSEEK_API_KEY must be set outside Git.")
    if not model:
        failures.append("DEEPSEEK_MODEL must be set, usually deepseek-chat.")
    return not failures, failures


def live_smoke() -> None:
    sys.path.insert(0, str(RUNTIME))
    from hfs_model_gateway import DeepSeekOpenAICompatibleAdapter

    adapter = DeepSeekOpenAICompatibleAdapter(enabled=True)
    request = {
        "messages": [
            {
                "role": "SYSTEM",
                "content": (
                    "Return JSON only with facts, assumptions, inferences, "
                    "recommendation, confidence, evidenceIds, and "
                    "requiresHumanApproval."
                ),
            },
            {
                "role": "USER",
                "content": (
                    "Draft a short internal Slack alert for a manager. "
                    "Use evidence ID evidence-config-check-001. Do not execute "
                    "or approve any action."
                ),
            },
        ],
        "invocationPolicy": {
            "temperature": 0.1,
            "maximumOutputTokens": 300,
        },
    }
    result = adapter.generate(request)
    output = result.output
    required = {
        "facts",
        "assumptions",
        "inferences",
        "recommendation",
        "confidence",
        "evidenceIds",
        "requiresHumanApproval",
    }
    missing = sorted(required - set(output))
    if missing:
        raise SystemExit(f"DeepSeek live output missing keys: {missing}")
    print(
        json.dumps(
            {
                "status": "READY",
                "provider": "deepseek",
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "inputTokens": result.input_tokens,
                "outputTokens": result.output_tokens,
                "recommendationPreview": str(output["recommendation"])[:160],
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="Make a real DeepSeek call after local configuration passes.",
    )
    args = parser.parse_args()

    load_local_env()
    ok, failures = configured()
    if not ok:
        print("DeepSeek is not ready:")
        for failure in failures:
            print(f"- {failure}")
        print("\nCopy .env.example to .env or configure the same variables in your secret manager.")
        raise SystemExit(1)

    api_key = os.environ["DEEPSEEK_API_KEY"]
    print(
        json.dumps(
            {
                "status": "CONFIGURED",
                "apiKey": masked(api_key),
                "enabled": True,
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "liveSmoke": args.live,
            },
            indent=2,
            sort_keys=True,
        )
    )
    if args.live:
        live_smoke()


if __name__ == "__main__":
    main()
