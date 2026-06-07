# Semantic Contract

This directory is the executable seed of the shared retail operations
vocabulary.
Salesforce and Data 360 remain the operational stores; these files define the
portable meaning and validation rules used at integration boundaries.

## Files

- `hfs-core.ttl`: OWL classes, properties, and initial SKOS concepts.
- `shapes.ttl`: SHACL requirements for provenance, relationships, assertions,
  events, recommendations, and actions.
- `context.jsonld`: portable JSON-LD names and datatype coercions.
- `examples/valid.jsonld`: a conforming relationship and recommendation trace.
- `examples/invalid.jsonld`: deliberate business-level contract violations.

## Validate

From the repository root:

```bash
./scripts/bootstrap-runtime.sh
npm run check:ontology
```

The validator must prove both sides of the contract:

- the valid fixture conforms;
- the invalid fixture does not conform;
- the invalid report includes the expected human-readable violation messages.

Ontology changes require matching updates to shapes, context, examples, and
downstream Salesforce or MuleSoft mappings when their contract changes.

## North Star Extension Plan

North Star should extend the semantic contract only when implementation needs
retail concepts that the current ontology cannot express. Candidate additions
include store, product category, product batch, shelf location, inventory
position, promotion window, complaint cluster, supplier response, markdown
plan, warehouse transfer, staff task, channel alert, and retail outcome.

When these are added, update:

- `hfs-core.ttl`;
- `shapes.ttl`;
- `context.jsonld`;
- valid and invalid JSON-LD examples;
- Salesforce, MuleSoft, and Data 360 mapping docs.
