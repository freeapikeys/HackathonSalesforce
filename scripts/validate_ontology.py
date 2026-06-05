#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, RDF
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
) -> tuple[bool, Graph, str]:
    data = load_graph(path, format_name="json-ld")
    conforms, results_graph, results_text = validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="rdfs",
        advanced=True,
        abort_on_first=False,
    )
    return bool(conforms), results_graph, str(results_text)


def result_messages(results_graph: Graph) -> set[str]:
    return {
        str(message)
        for result in results_graph.subjects(RDF.type, SH.ValidationResult)
        for message in results_graph.objects(result, SH.resultMessage)
    }


def main() -> None:
    ontology = load_graph(ONTOLOGY_DIR / "hfs-core.ttl", format_name="turtle")
    shapes = load_graph(ONTOLOGY_DIR / "shapes.ttl", format_name="turtle")

    assert (HFS.CoreOntology, RDF.type, OWL.Ontology) in ontology

    context = json.loads((ONTOLOGY_DIR / "context.jsonld").read_text())
    context_terms = context["@context"]
    for required_term in (
        "identifier",
        "recordedAt",
        "sourceRecordId",
        "sourceSystem",
        "subjectEntity",
        "objectEntity",
        "supportedBy",
        "recommendsAction",
    ):
        assert required_term in context_terms, (
            f"JSON-LD context is missing required term: {required_term}"
        )

    valid_conforms, _, valid_report = validate_fixture(
        ONTOLOGY_DIR / "examples" / "valid.jsonld", ontology, shapes
    )
    assert valid_conforms, f"Valid semantic fixture failed:\n{valid_report}"

    invalid_conforms, invalid_results, invalid_report = validate_fixture(
        ONTOLOGY_DIR / "examples" / "invalid.jsonld", ontology, shapes
    )
    assert not invalid_conforms, "Invalid semantic fixture unexpectedly passed."

    messages = result_messages(invalid_results)
    expected_messages = {
        "Every record must include its source record identifier.",
        "A relationship must identify its object entity.",
        "A relationship must declare when it became valid.",
        "A recommendation must cite at least one evidence record.",
        "A recommendation must point to the proposed action.",
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
