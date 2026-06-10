#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_semantic_mappings import validate as validate_mappings  # noqa: E402

HFS = Namespace("https://freeapikeys.github.io/HackathonSalesforce/ontology#")
ONTOLOGY_DIR = ROOT / "ontology"
MAPPING_PATH = ONTOLOGY_DIR / "mappings" / "semantic-mappings-v1.json"


def run_check(name: str, script: str) -> dict[str, str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip().splitlines()
    return {
        "name": name,
        "status": "passed",
        "summary": output[-1] if output else "",
    }


def load_graph(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="json-ld")
    return graph


def count_mapping_targets(mappings: dict[str, Any]) -> int:
    return sum(
        len(record["salesforce"]["targets"])
        for record in mappings["salesforceFieldMappings"]
    )


def count_attribute_mappings(mappings: dict[str, Any]) -> int:
    return sum(len(record["attributes"]) for record in mappings["eventAttributeMappings"])


def main() -> int:
    checks = [
        run_check("ontology", "validate_ontology.py"),
        run_check("temporal", "validate_temporal_semantics.py"),
    ]

    mapping_errors = validate_mappings()
    if mapping_errors:
        for error in mapping_errors:
            print(error, file=sys.stderr)
        return 1
    checks.append(
        {
            "name": "mappings",
            "status": "passed",
            "summary": (
                "Semantic mappings are valid: event envelope, event attributes, "
                "event type patterns, and Salesforce field coverage are complete."
            ),
        }
    )

    valid_graph = load_graph(ONTOLOGY_DIR / "examples" / "valid.jsonld")
    temporal_graph = load_graph(ONTOLOGY_DIR / "examples" / "temporal.jsonld")
    mappings = json.loads(MAPPING_PATH.read_text())

    terminology_mappings = list(
        valid_graph.triples((None, HFS.canonicalConcept, HFS.CustomerRelationship))
    )
    temporal_assertions = list(temporal_graph.subjects(RDF.type, HFS.Assertion))
    supersession_edges = list(temporal_graph.triples((None, HFS.supersedes, None)))

    report = {
        "status": "passed",
        "checks": checks,
        "evidence": {
            "sourceTerminologyMappings": len(terminology_mappings),
            "temporalSourceAssertions": len(temporal_assertions),
            "temporalSupersessionEdges": len(supersession_edges),
            "salesforceFieldMappings": count_mapping_targets(mappings),
            "eventAttributeMappings": count_attribute_mappings(mappings),
            "eventTypePatterns": len(mappings["eventTypePatterns"]),
        },
    }
    assert report["evidence"]["sourceTerminologyMappings"] >= 1
    assert report["evidence"]["temporalSourceAssertions"] == 3
    assert report["evidence"]["temporalSupersessionEdges"] == 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
