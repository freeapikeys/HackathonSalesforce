#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
HFS = Namespace("https://freeapikeys.github.io/HackathonSalesforce/ontology#")

SUBJECT = URIRef("https://example.org/data/relationship/alice-acme")
PREDICATE = HFS.relationshipStatus


@dataclass(frozen=True)
class AssertionRow:
    uri: URIRef
    value: str
    valid_from: datetime
    valid_to: datetime | None
    recorded_at: datetime
    source_record_id: str
    generated_by: URIRef
    attributed_to: URIRef
    supersedes: frozenset[URIRef]


def parse_time(value: object) -> datetime:
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_graph(path: Path, *, format_name: str) -> Graph:
    graph = Graph()
    graph.parse(path, format=format_name)
    return graph


def validate_temporal_fixture(data: Graph, ontology: Graph, shapes: Graph) -> None:
    conforms, _, results_text = validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="rdfs",
        advanced=True,
        abort_on_first=False,
    )
    assert conforms, f"Temporal semantic fixture failed SHACL validation:\n{results_text}"


def assertion_rows(data: Graph) -> list[AssertionRow]:
    rows: list[AssertionRow] = []
    for assertion in data.subjects(RDF.type, HFS.Assertion):
        subject = data.value(assertion, HFS.assertionSubject)
        predicate = data.value(assertion, HFS.assertionPredicate)
        if subject != SUBJECT or predicate != PREDICATE:
            continue

        valid_to = data.value(assertion, HFS.validTo)
        rows.append(
            AssertionRow(
                uri=URIRef(assertion),
                value=str(data.value(assertion, HFS.assertionObject)),
                valid_from=parse_time(data.value(assertion, HFS.validFrom)),
                valid_to=parse_time(valid_to) if valid_to is not None else None,
                recorded_at=parse_time(data.value(assertion, HFS.recordedAt)),
                source_record_id=str(data.value(assertion, HFS.sourceRecordId)),
                generated_by=URIRef(data.value(assertion, HFS.generatedBy)),
                attributed_to=URIRef(data.value(assertion, HFS.attributedTo)),
                supersedes=frozenset(
                    URIRef(superseded)
                    for superseded in data.objects(assertion, HFS.supersedes)
                ),
            )
        )
    return rows


def resolve_relationship_status(
    rows: list[AssertionRow],
    *,
    business_time: datetime,
    recorded_cutoff: datetime,
) -> AssertionRow | None:
    candidates = [
        row
        for row in rows
        if row.recorded_at <= recorded_cutoff
        and row.valid_from <= business_time
        and (row.valid_to is None or business_time < row.valid_to)
    ]
    superseded = {
        superseded_uri
        for row in candidates
        for superseded_uri in row.supersedes
    }
    active_candidates = [row for row in candidates if row.uri not in superseded]
    if not active_candidates:
        return None
    return max(active_candidates, key=lambda row: (row.valid_from, row.recorded_at))


def assert_source_evidence(row: AssertionRow | None, case_name: str) -> AssertionRow:
    assert row is not None, f"{case_name}: expected an assertion result."
    assert row.source_record_id, f"{case_name}: missing source record id."
    assert row.generated_by, f"{case_name}: missing source activity."
    assert row.attributed_to, f"{case_name}: missing source agent."
    return row


def main() -> None:
    ontology = load_graph(ONTOLOGY_DIR / "hfs-core.ttl", format_name="turtle")
    shapes = load_graph(ONTOLOGY_DIR / "shapes.ttl", format_name="turtle")
    data = load_graph(ONTOLOGY_DIR / "examples" / "temporal.jsonld", format_name="json-ld")
    validate_temporal_fixture(data, ontology, shapes)
    rows = assertion_rows(data)

    cases = [
        {
            "name": "historical-belief-before-late-arrival",
            "businessTime": "2026-06-03T12:00:00Z",
            "recordedCutoff": "2026-06-04T00:00:00Z",
            "expectedValue": "ACTIVE",
            "expectedSourceRecordId": "relationship-status-001",
        },
        {
            "name": "current-state-after-late-arrival",
            "businessTime": "2026-06-03T12:00:00Z",
            "recordedCutoff": "2026-06-06T00:00:00Z",
            "expectedValue": "PAUSED",
            "expectedSourceRecordId": "relationship-status-002",
        },
        {
            "name": "historical-belief-before-restoration",
            "businessTime": "2026-06-09T12:00:00Z",
            "recordedCutoff": "2026-06-07T00:00:00Z",
            "expectedValue": "PAUSED",
            "expectedSourceRecordId": "relationship-status-002",
        },
        {
            "name": "current-state-after-restoration",
            "businessTime": "2026-06-09T12:00:00Z",
            "recordedCutoff": "2026-06-09T12:00:00Z",
            "expectedValue": "ACTIVE",
            "expectedSourceRecordId": "relationship-status-003",
        },
    ]

    for case in cases:
        result = resolve_relationship_status(
            rows,
            business_time=parse_time(case["businessTime"]),
            recorded_cutoff=parse_time(case["recordedCutoff"]),
        )
        row = assert_source_evidence(result, case["name"])
        assert row.value == case["expectedValue"], (
            f"{case['name']}: expected value {case['expectedValue']}, got {row.value}."
        )
        assert row.source_record_id == case["expectedSourceRecordId"], (
            f"{case['name']}: expected source {case['expectedSourceRecordId']}, "
            f"got {row.source_record_id}."
        )

    print(
        "Temporal semantic queries are valid: "
        f"{len(cases)} scenario(s) resolved with source evidence."
    )


if __name__ == "__main__":
    main()
