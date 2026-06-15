#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_core_salesforce_metadata import expanded_fields  # noqa: E402

MAPPING_PATH = ROOT / "ontology" / "mappings" / "semantic-mappings-v1.json"
EVENT_SCHEMA_PATH = ROOT / "integration" / "events" / "schemas" / "event-envelope-v1.schema.json"
EVENT_FIXTURES_DIR = ROOT / "integration" / "events" / "fixtures" / "events"
SALESFORCE_MODEL_PATH = ROOT / "config" / "core-salesforce-model.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def require_text(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string.")


def require_quality(record: dict[str, Any], section: str, errors: list[str]) -> None:
    prefix = f"{section}.{record.get('id', '<missing-id>')}"
    require_text(record.get("id"), f"{prefix}.id", errors)
    require_text(record.get("owner"), f"{prefix}.owner", errors)
    source = record.get("source", {})
    if not isinstance(source, dict):
        errors.append(f"{prefix}.source must be an object.")
        source = {}
    require_text(source.get("localTerm"), f"{prefix}.source.localTerm", errors)
    if not any(
        key in source
        for key in (
            "locator",
            "locators",
            "locatorPrefix",
            "typePattern",
        )
    ):
        errors.append(f"{prefix}.source must include a locator, locators, locatorPrefix, or typePattern.")

    data360 = record.get("data360", {})
    if not isinstance(data360, dict):
        errors.append(f"{prefix}.data360 must be an object.")
        data360 = {}
    require_text(data360.get("object"), f"{prefix}.data360.object", errors)
    require_text(data360.get("field"), f"{prefix}.data360.field", errors)

    ontology = record.get("ontology", {})
    if not isinstance(ontology, dict):
        errors.append(f"{prefix}.ontology must be an object.")
        ontology = {}
    require_text(ontology.get("class"), f"{prefix}.ontology.class", errors)
    require_text(ontology.get("property"), f"{prefix}.ontology.property", errors)

    transformation = record.get("transformation", {})
    if not isinstance(transformation, dict):
        errors.append(f"{prefix}.transformation must be an object.")
        transformation = {}
    require_text(transformation.get("rule"), f"{prefix}.transformation.rule", errors)
    require_text(transformation.get("loss"), f"{prefix}.transformation.loss", errors)
    require_text(
        transformation.get("ambiguity"),
        f"{prefix}.transformation.ambiguity",
        errors,
    )


def schema_event_paths(schema: dict[str, Any]) -> set[str]:
    paths = {f"$.{name}" for name in schema["properties"]}
    business_record = schema["$defs"]["businessRecord"]
    paths.update(f"$.data.{name}" for name in business_record["properties"])
    assertion = schema["$defs"]["assertion"]
    paths.update(f"$.data.assertions[].{name}" for name in assertion["properties"])
    return paths


def mapped_event_paths(mappings: dict[str, Any]) -> set[str]:
    locators: list[str] = []
    for record in mappings["eventEnvelopeMappings"]:
        source = record["source"]
        if locator := source.get("locator"):
            locators.append(locator)
        locators.extend(source.get("locators", []))
    return set(locators)


def fixture_documents() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in sorted(EVENT_FIXTURES_DIR.glob("*.json")):
        documents.append(load_json(path))
    return documents


def fixture_attribute_pairs(documents: list[dict[str, Any]]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for document in documents:
        data = document.get("data")
        if not isinstance(data, dict):
            continue
        record_type = data.get("recordtype")
        attributes = data.get("attributes", {})
        if not isinstance(record_type, str) or not isinstance(attributes, dict):
            continue
        pairs.update((record_type, attribute) for attribute in attributes)
    return pairs


def mapped_attribute_pairs(
    mappings: dict[str, Any],
    errors: list[str],
) -> set[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for record in mappings["eventAttributeMappings"]:
        record_type = record.get("recordType")
        if not isinstance(record_type, str) or not record_type.strip():
            errors.append(f"{record.get('id', '<missing-id>')}.recordType must be a non-empty string.")
            continue
        attributes = record.get("attributes")
        if not isinstance(attributes, list) or not attributes:
            errors.append(f"{record['id']}.attributes must be a non-empty list.")
            continue
        for attribute in attributes:
            if not isinstance(attribute, str) or not attribute.strip():
                errors.append(f"{record['id']}.attributes contains a non-string attribute.")
                continue
            pairs.append((record_type, attribute))

    duplicate_pairs = [pair for pair, count in Counter(pairs).items() if count > 1]
    for record_type, attribute in duplicate_pairs:
        errors.append(f"Duplicate attribute mapping for {record_type}.{attribute}.")
    return set(pairs)


def validate_event_type_patterns(
    mappings: dict[str, Any],
    documents: list[dict[str, Any]],
    errors: list[str],
) -> None:
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for record in mappings["eventTypePatterns"]:
        pattern_text = record["source"].get("typePattern")
        if not isinstance(pattern_text, str):
            errors.append(f"{record['id']}.source.typePattern must be a string.")
            continue
        try:
            patterns.append((record["id"], re.compile(pattern_text)))
        except re.error as exc:
            errors.append(f"{record['id']}.source.typePattern is invalid: {exc}.")

    event_types = {
        document["type"]
        for document in documents
        if isinstance(document.get("type"), str)
    }
    matched_by_pattern: defaultdict[str, set[str]] = defaultdict(set)
    for event_type in event_types:
        matches = [
            pattern_id
            for pattern_id, pattern in patterns
            if pattern.fullmatch(event_type)
        ]
        if len(matches) != 1:
            errors.append(
                f"Event type {event_type} must match exactly one pattern; matched {matches}."
            )
        for pattern_id in matches:
            matched_by_pattern[pattern_id].add(event_type)

    for pattern_id, _ in patterns:
        if pattern_id not in matched_by_pattern:
            errors.append(f"Event type pattern {pattern_id} did not match any fixture event.")


def expected_salesforce_targets(model: dict[str, Any]) -> set[tuple[str, str]]:
    targets: set[tuple[str, str]] = set()
    for object_definition in model["objects"]:
        object_api = object_definition["api"]
        for field in expanded_fields(object_definition):
            targets.add((object_api, field["api"]))
    return targets


def mapped_salesforce_targets(
    mappings: dict[str, Any],
    errors: list[str],
) -> set[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    for record in mappings["salesforceFieldMappings"]:
        salesforce = record.get("salesforce", {})
        if not isinstance(salesforce, dict):
            errors.append(f"{record['id']}.salesforce must be an object.")
            continue
        record_targets = salesforce.get("targets")
        if not isinstance(record_targets, list) or not record_targets:
            errors.append(f"{record['id']}.salesforce.targets must be a non-empty list.")
            continue
        for target in record_targets:
            if not isinstance(target, dict):
                errors.append(f"{record['id']}.salesforce.targets contains a non-object target.")
                continue
            object_api = target.get("object")
            field_api = target.get("field")
            if not isinstance(object_api, str) or not isinstance(field_api, str):
                errors.append(f"{record['id']}.salesforce target must include object and field strings.")
                continue
            targets.append((object_api, field_api))

    duplicate_targets = [target for target, count in Counter(targets).items() if count > 1]
    for object_api, field_api in duplicate_targets:
        errors.append(f"Duplicate Salesforce mapping target for {object_api}.{field_api}.")
    return set(targets)


def validate() -> list[str]:
    errors: list[str] = []
    mappings = load_json(MAPPING_PATH)
    schema = load_json(EVENT_SCHEMA_PATH)
    model = load_json(SALESFORCE_MODEL_PATH)
    documents = fixture_documents()

    require_text(mappings.get("version"), "version", errors)
    require_text(mappings.get("owner"), "owner", errors)

    seen_ids: Counter[str] = Counter()
    for section in (
        "eventEnvelopeMappings",
        "eventTypePatterns",
        "eventAttributeMappings",
        "salesforceFieldMappings",
    ):
        records = mappings.get(section)
        if not isinstance(records, list) or not records:
            errors.append(f"{section} must be a non-empty list.")
            continue
        for record in records:
            if not isinstance(record, dict):
                errors.append(f"{section} contains a non-object record.")
                continue
            if isinstance(record.get("id"), str):
                seen_ids[record["id"]] += 1
            require_quality(record, section, errors)

    for record_id, count in seen_ids.items():
        if count > 1:
            errors.append(f"Duplicate mapping id: {record_id}.")

    expected_paths = schema_event_paths(schema)
    actual_paths = mapped_event_paths(mappings)
    missing_paths = expected_paths - actual_paths
    extra_paths = actual_paths - expected_paths - {"$"}
    if missing_paths:
        errors.append("Missing event envelope mappings: " + ", ".join(sorted(missing_paths)))
    if extra_paths:
        errors.append("Unknown event envelope mappings: " + ", ".join(sorted(extra_paths)))

    expected_attributes = fixture_attribute_pairs(documents)
    mapped_attributes = mapped_attribute_pairs(mappings, errors)
    missing_attributes = expected_attributes - mapped_attributes
    stale_attributes = mapped_attributes - expected_attributes
    if missing_attributes:
        errors.append(
            "Missing event attribute mappings: "
            + ", ".join(f"{record}.{attribute}" for record, attribute in sorted(missing_attributes))
        )
    if stale_attributes:
        errors.append(
            "Stale event attribute mappings: "
            + ", ".join(f"{record}.{attribute}" for record, attribute in sorted(stale_attributes))
        )

    validate_event_type_patterns(mappings, documents, errors)

    expected_targets = expected_salesforce_targets(model)
    mapped_targets = mapped_salesforce_targets(mappings, errors)
    missing_targets = expected_targets - mapped_targets
    unknown_targets = mapped_targets - expected_targets
    if missing_targets:
        errors.append(
            "Missing Salesforce field mappings: "
            + ", ".join(f"{object_api}.{field_api}" for object_api, field_api in sorted(missing_targets))
        )
    if unknown_targets:
        errors.append(
            "Unknown Salesforce field mappings: "
            + ", ".join(f"{object_api}.{field_api}" for object_api, field_api in sorted(unknown_targets))
        )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(
        "Semantic mappings are valid: event envelope, event attributes, "
        "event type patterns, and Salesforce field coverage are complete."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
