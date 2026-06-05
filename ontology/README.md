# Semantic Contract

This directory is the executable seed of the shared enterprise vocabulary.
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
