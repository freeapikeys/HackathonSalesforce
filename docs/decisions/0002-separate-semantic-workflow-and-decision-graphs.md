# 0002: Separate Semantic, Workflow, Event, and Decision Structures

Status: Accepted

## Decision

Use connected but distinct structures:

- OWL/SKOS type graph;
- provenance-bearing assertion graph;
- immutable event history;
- acyclic workflow definitions and executions;
- versioned, potentially cyclic decision traces.

## Reason

Retail operations context and feedback are naturally cyclic, while executable
SOP dependencies need deterministic ordering. Combining them into one generic
DAG would either lose real relationships or make workflow execution ambiguous.

## Consequences

- Stable identifiers connect structures.
- Every derived result retains provenance.
- OWL files define meaning and validation but do not replace Salesforce and
  Data 360 operational storage.
- A separate graph database is deferred until measurements justify it.
- Logia retail concepts such as product, batch, supplier response, staff
  task, channel alert, and outcome should map into these structures rather than
  becoming one untyped demo blob.
