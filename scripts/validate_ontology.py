#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import OWL, SH

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
HFS = Namespace("https://freeapikeys.github.io/HackathonSalesforce/ontology#")


def load_graph(path: Path, *, format_name: str) -> Graph:
    graph = Graph()
    graph.parse(path, format=format_name)
    return graph


def validate_fixture(
    path: Path, ontology: Graph, shapes: Graph
) -> tuple[bool, Graph, Graph, str]:
    data = load_graph(path, format_name="json-ld")
    conforms, results_graph, results_text = validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="rdfs",
        advanced=True,
        abort_on_first=False,
    )
    return bool(conforms), data, results_graph, str(results_text)


def result_messages(results_graph: Graph) -> set[str]:
    return {
        str(message)
        for result in results_graph.subjects(RDF.type, SH.ValidationResult)
        for message in results_graph.objects(result, SH.resultMessage)
    }


def contradiction_messages(data_graph: Graph) -> set[str]:
    assertions_by_scope: dict[
        tuple[object, object, object], dict[object, set[object]]
    ] = {}
    for assertion in data_graph.subjects(RDF.type, HFS.Assertion):
        subject = data_graph.value(assertion, HFS.assertionSubject)
        predicate = data_graph.value(assertion, HFS.assertionPredicate)
        valid_from = data_graph.value(assertion, HFS.validFrom)
        assertion_object = data_graph.value(assertion, HFS.assertionObject)
        if not all((subject, predicate, valid_from, assertion_object)):
            continue
        scope = (subject, predicate, valid_from)
        assertions_by_scope.setdefault(scope, {}).setdefault(
            assertion_object,
            set(),
        ).add(assertion)

    messages: set[str] = set()
    for values_by_object in assertions_by_scope.values():
        if len(values_by_object) < 2:
            continue
        scoped_assertions = {
            assertion
            for assertions in values_by_object.values()
            for assertion in assertions
        }
        has_supersession = any(
            (newer, HFS.supersedes, older) in data_graph
            for newer in scoped_assertions
            for older in scoped_assertions
            if newer != older
        )
        if not has_supersession:
            messages.add(
                "Contradictory assertions for the same effective point must use explicit supersession."
            )
    return messages


def main() -> None:
    ontology = load_graph(ONTOLOGY_DIR / "hfs-core.ttl", format_name="turtle")
    shapes = load_graph(ONTOLOGY_DIR / "shapes.ttl", format_name="turtle")

    assert (HFS.CoreOntology, RDF.type, OWL.Ontology) in ontology

    context = json.loads((ONTOLOGY_DIR / "context.jsonld").read_text())
    context_terms = context["@context"]
    for required_term in (
        "identifier",
        "assertionKind",
        "assertionObject",
        "assertionPredicate",
        "assertionSubject",
        "attributedTo",
        "canonicalConcept",
        "generatedBy",
        "localTerm",
        "recordedAt",
        "sourceRecordId",
        "sourceSystem",
        "subjectEntity",
        "objectEntity",
        "supersededAt",
        "supersedes",
        "supportedBy",
        "recommendsAction",
    ):
        assert required_term in context_terms, (
            f"JSON-LD context is missing required term: {required_term}"
        )

    valid_conforms, valid_data, _, valid_report = validate_fixture(
        ONTOLOGY_DIR / "examples" / "valid.jsonld", ontology, shapes
    )
    assert valid_conforms, f"Valid semantic fixture failed:\n{valid_report}"
    valid_custom_messages = contradiction_messages(valid_data)
    assert not valid_custom_messages, (
        "Valid semantic fixture produced custom violations: "
        + ", ".join(sorted(valid_custom_messages))
    )
    expected_supersession = (
        URIRef("https://example.org/data/assertion/relationship-status-paused"),
        HFS.supersedes,
        URIRef("https://example.org/data/assertion/relationship-status-active"),
    )
    assert expected_supersession in valid_data, (
        "Valid fixture must prove explicit assertion supersession."
    )
    supersedes_count = len(list(valid_data.triples((None, HFS.supersedes, None))))
    assert supersedes_count == 1, "Valid fixture must prove explicit supersession."
    assert (
        None,
        HFS.assertionPredicate,
        HFS.relationshipStatus,
    ) in valid_data, "Valid fixture must use the canonical HFS relationshipStatus IRI."
    assert (
        None,
        HFS.assertionKind,
        HFS.SourceClaim,
    ) in valid_data, "Valid fixture must use the canonical HFS SourceClaim IRI."

    invalid_conforms, invalid_data, invalid_results, invalid_report = validate_fixture(
        ONTOLOGY_DIR / "examples" / "invalid.jsonld", ontology, shapes
    )
    assert not invalid_conforms, "Invalid semantic fixture unexpectedly passed."

    messages = result_messages(invalid_results) | contradiction_messages(invalid_data)
    expected_messages = {
        "Every record must include its source record identifier.",
        "A relationship must identify its object entity.",
        "A relationship must declare when it became valid.",
        "A recommendation must cite at least one evidence record.",
        "A recommendation must point to the proposed action.",
        "A source activity must identify the responsible source agent.",
        "A terminology entry must map to a canonical concept.",
        "A terminology entry must belong to a source terminology scheme.",
        "An assertion must declare whether it is a source claim or derived inference.",
        "Contradictory assertions for the same effective point must use explicit supersession.",
    }
    missing_messages = expected_messages - messages
    assert not missing_messages, (
        "Invalid fixture did not produce expected violations: "
        + ", ".join(sorted(missing_messages))
        + f"\n\n{invalid_report}"
    )

    print(
        "Semantic contract is valid: positive fixture conforms and negative "
        f"fixture produced {len(messages)} named violation(s)."
    )


if __name__ == "__main__":
    main()
