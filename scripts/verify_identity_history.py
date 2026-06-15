#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "integration" / "events" / "fixtures"
SCENARIO_PATH = FIXTURE_ROOT / "scenario.json"
PRESERVED_RESULTS = {
    "ACCEPTED",
    "ACCEPTED_LATE",
    "ACCEPTED_OUT_OF_ORDER",
    "CONFLICT_REVIEW",
}
DIRECT_CONFIDENCE = 1.0
INFERRED_CONFIDENCE = 0.74


@dataclass
class IdentityNode:
    key: str
    kind: str
    source_records: set[str] = field(default_factory=set)
    evidence_events: set[str] = field(default_factory=set)
    corrections: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class RelationshipEdge:
    subject: str
    predicate: str
    object: str
    confidence: float
    evidence_event: str
    source_record_id: str


def load_event(path: str) -> dict[str, Any]:
    return json.loads((FIXTURE_ROOT / path).read_text())


def identity_key(kind: str, value: str) -> str:
    return f"{kind}:{value}"


def identity_from_subject(subject: str) -> tuple[str, str]:
    kind, _, value = subject.partition(":")
    return identity_key(kind, value), kind


def attribute_identity(attribute: str, value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str) or not value:
        return None
    if attribute in {"personkey"}:
        return identity_key("person", value), "person"
    if attribute in {"organizationkey", "customerorganizationkey", "supplierorganizationkey"}:
        return identity_key("organization", value), "organization"
    if attribute in {"supplierkey", "supplierid"}:
        return identity_key("supplier", value), "supplier"
    if attribute in {"agreementkey"}:
        return identity_key("agreement", value), "agreement"
    if attribute in {"storeid"}:
        return identity_key("store", value), "store"
    if attribute in {"productid", "expectedproductid"}:
        return identity_key("product", value), "product"
    if attribute in {"batchid", "replacementbatchid"}:
        return identity_key("batch", value), "batch"
    if attribute in {"promotionid"}:
        return identity_key("promotion", value), "promotion"
    if attribute in {"companyid"}:
        return identity_key("organization", value), "organization"
    if attribute in {"approvalid"}:
        return identity_key("approval", value), "approval"
    return None


def add_identity(
    identities: dict[str, IdentityNode],
    key: str,
    kind: str,
    event: dict[str, Any],
) -> None:
    node = identities.setdefault(key, IdentityNode(key=key, kind=kind))
    node.source_records.add(event["hfssourcerecordid"])
    node.evidence_events.add(event["id"])


def add_edge(
    edges: set[RelationshipEdge],
    event: dict[str, Any],
    subject: str,
    predicate: str,
    object_key: str,
    confidence: float = DIRECT_CONFIDENCE,
) -> None:
    edges.add(
        RelationshipEdge(
            subject=subject,
            predicate=predicate,
            object=object_key,
            confidence=confidence,
            evidence_event=event["id"],
            source_record_id=event["hfssourcerecordid"],
        )
    )


def build_identity_history() -> dict[str, Any]:
    scenario = json.loads(SCENARIO_PATH.read_text())
    identities: dict[str, IdentityNode] = {}
    edges: set[RelationshipEdge] = set()
    participant_links: set[tuple[str, str, str]] = set()
    assertions: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    preserved_events: list[dict[str, Any]] = []

    for case in scenario["events"]:
        if case["expected"] not in PRESERVED_RESULTS:
            continue
        event = load_event(case["file"])
        preserved_events.append(event)
        data = event["data"]
        attributes = data.get("attributes", {})
        subject_key, subject_kind = identity_from_subject(event["subject"])
        add_identity(identities, subject_key, subject_kind, event)
        participant_links.add((event["id"], subject_key, "SUBJECT"))

        record_type = data["recordtype"]
        business_key = str(data["businesskey"])
        if record_type in {"Person", "Organization", "Supplier", "Agreement", "Issue", "SOP"}:
            business_identity = identity_key(record_type.lower(), business_key)
            add_identity(identities, business_identity, record_type.lower(), event)
            participant_links.add((event["id"], business_identity, "BUSINESS_RECORD"))

        if data["operation"] in {"UPDATE", "CLOSE"} or case["expected"] in {
            "ACCEPTED_LATE",
            "ACCEPTED_OUT_OF_ORDER",
            "CONFLICT_REVIEW",
        }:
            identities[subject_key].corrections.append(
                {
                    "operation": data["operation"],
                    "intakeResult": case["expected"],
                    "eventId": event["id"],
                    "sourceRecordId": event["hfssourcerecordid"],
                }
            )

        for attribute, value in attributes.items():
            resolved = attribute_identity(attribute, value)
            if resolved is None:
                continue
            key, kind = resolved
            add_identity(identities, key, kind, event)
            participant_links.add((event["id"], key, attribute.upper()))

        if record_type == "Employee":
            person_key = identity_key("person", attributes["personkey"])
            organization_key = identity_key("organization", attributes["organizationkey"])
            add_edge(edges, event, person_key, "EMPLOYED_BY", organization_key)

        if record_type == "Supplier":
            supplier_org = attributes.get("supplierorganizationkey")
            customer_org = attributes.get("customerorganizationkey")
            if supplier_org and customer_org:
                add_edge(
                    edges,
                    event,
                    identity_key("organization", supplier_org),
                    "SUPPLIER_OF",
                    identity_key("organization", customer_org),
                )
            supplier_record = identity_key("supplier", business_key)
            if customer_org:
                add_edge(
                    edges,
                    event,
                    supplier_record,
                    "SUPPLIER_RECORD_FOR",
                    identity_key("organization", customer_org),
                )

        if record_type == "Agreement":
            organization = attributes.get("organizationkey")
            supplier = attributes.get("supplierkey")
            if organization and supplier:
                add_edge(
                    edges,
                    event,
                    identity_key("organization", organization),
                    "HAS_AGREEMENT_WITH",
                    identity_key("supplier", supplier),
                )

        if record_type == "Issue":
            issue_key = identity_key("issue", business_key)
            for attribute, predicate in (
                ("agreementkey", "ABOUT_AGREEMENT"),
                ("supplierkey", "ABOUT_SUPPLIER"),
                ("supplierid", "ABOUT_SUPPLIER"),
                ("storeid", "AFFECTS_STORE"),
                ("productid", "AFFECTS_PRODUCT"),
                ("batchid", "AFFECTS_BATCH"),
                ("promotionid", "AFFECTS_PROMOTION"),
                ("companyid", "AFFECTS_ORGANIZATION"),
            ):
                resolved = attribute_identity(attribute, attributes.get(attribute))
                if resolved:
                    add_edge(
                        edges,
                        event,
                        issue_key,
                        predicate,
                        resolved[0],
                        INFERRED_CONFIDENCE,
                    )

        for assertion in data.get("assertions", []):
            assertions[assertion["conflictkey"]].append(
                {
                    "predicate": assertion["predicate"],
                    "value": str(assertion["value"]),
                    "eventId": event["id"],
                    "sourceRecordId": event["hfssourcerecordid"],
                }
            )

    return {
        "identities": identities,
        "edges": edges,
        "participantLinks": participant_links,
        "assertions": assertions,
        "preservedEvents": preserved_events,
    }


def traversable_path(
    edges: set[RelationshipEdge],
    start: str,
    end: str,
) -> list[str]:
    graph: defaultdict[str, set[str]] = defaultdict(set)
    for edge in edges:
        graph[edge.subject].add(edge.object)
        graph[edge.object].add(edge.subject)

    queue: deque[list[str]] = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        for next_node in sorted(graph[node]):
            if next_node in visited:
                continue
            visited.add(next_node)
            queue.append([*path, next_node])
    return []


def main() -> int:
    history = build_identity_history()
    identities: dict[str, IdentityNode] = history["identities"]
    edges: set[RelationshipEdge] = history["edges"]
    participant_links: set[tuple[str, str, str]] = history["participantLinks"]
    assertions: dict[str, list[dict[str, str]]] = history["assertions"]

    required_identities = {
        "person:person-001",
        "organization:organization-001",
        "supplier:supplier-001",
        "agreement:agreement-001",
        "issue:issue-001",
        "store:STORE-GOODLANDS-FRESHMART",
        "product:PROD-FRESH-BEEF-PATTIES-400G",
        "organization:SYNTH-LIFTOPS-MANUFACTURING",
    }
    missing_identities = required_identities - set(identities)
    assert not missing_identities, (
        "Missing required identities: " + ", ".join(sorted(missing_identities))
    )

    relationship_counter = Counter(edge.predicate for edge in edges)
    for required_predicate in {
        "EMPLOYED_BY",
        "SUPPLIER_OF",
        "HAS_AGREEMENT_WITH",
        "AFFECTS_PRODUCT",
        "AFFECTS_STORE",
    }:
        assert relationship_counter[required_predicate] > 0, (
            f"Missing relationship predicate: {required_predicate}"
        )

    agreement_statuses = {
        assertion["value"]
        for assertion in assertions["agreement:agreement-001:status"]
    }
    assert agreement_statuses == {"ACTIVE", "TERMINATED"}, (
        "Agreement status conflict was not preserved."
    )

    correction_count = sum(len(node.corrections) for node in identities.values())
    assert correction_count >= 3, "Expected late/out-of-order/conflict corrections."

    path = traversable_path(
        edges,
        "person:person-001",
        "supplier:supplier-001",
    )
    assert path, "Expected traversable person-to-supplier relationship path."

    for edge in edges:
        assert edge.source_record_id, f"{edge.predicate} edge lacks source record."
        assert edge.evidence_event, f"{edge.predicate} edge lacks evidence event."
        assert 0 <= edge.confidence <= 1, f"{edge.predicate} confidence out of range."

    report = {
        "status": "passed",
        "identityCount": len(identities),
        "relationshipCount": len(edges),
        "participantLinkCount": len(participant_links),
        "correctionCount": correction_count,
        "conflictingAssertionCount": len(agreement_statuses),
        "preservedEventCount": len(history["preservedEvents"]),
        "relationshipPredicates": dict(sorted(relationship_counter.items())),
        "sampleTraversal": path,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
