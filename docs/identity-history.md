# Identity Relationship History

C03 starts with an executable source-fixture verifier:

```bash
npm run verify:identity-history
```

The verifier reads the deterministic event scenario, keeps only preserved source
events, and builds an identity graph from source keys, subjects, relationship
attributes, assertions, and participant links.

It proves the first identity-history slice can:

- preserve source identities and source record IDs;
- expose direct and inferred relationship edges with confidence values;
- retain participant links for source events;
- preserve late, out-of-order, and conflicting correction history;
- keep contradictory agreement status assertions visible instead of overwriting
  them;
- traverse a person-to-organization-to-supplier relationship path with evidence.

This is not yet the full C03 product surface. The next C03 slices should connect
the same behavior to Salesforce records, API responses, and UI inspection.
