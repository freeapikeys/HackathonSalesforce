from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[4]
GATEWAY_DIR = ROOT / "intelligence" / "model-gateway"
SCHEMA_PATH = GATEWAY_DIR / "schemas" / "model-gateway-v1.schema.json"
FIXTURE_PATH = GATEWAY_DIR / "fixtures" / "gateway-scenario-v1.json"


class ModelContractError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def content_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


class ModelGatewayContract:
    def __init__(self) -> None:
        self.schema = json.loads(SCHEMA_PATH.read_text())
        self.fixture = json.loads(FIXTURE_PATH.read_text())
        self.registry = Registry().with_resource(
            self.schema["$id"],
            Resource.from_contents(self.schema),
        )

    def validate(self, definition: str, value: dict[str, Any]) -> None:
        validator = Draft202012Validator(
            {"$ref": f"{self.schema['$id']}#/$defs/{definition}"},
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        errors = sorted(
            validator.iter_errors(value),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            details = []
            for error in errors:
                path = ".".join(str(part) for part in error.absolute_path)
                details.append(
                    f"{path}: {error.message}" if path else error.message
                )
            raise ModelContractError(
                f"{definition}: {' | '.join(details)}"
            )

    def validate_output(
        self,
        response_schema: dict[str, Any],
        output: dict[str, Any],
    ) -> None:
        validator = Draft202012Validator(
            response_schema,
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        errors = list(validator.iter_errors(output))
        if errors:
            raise ModelContractError(errors[0].message)

    def copy_fixture(self, key: str) -> Any:
        return deepcopy(self.fixture[key])
