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

The Salesforce service layer now projects part of that history back through the
governed API:

- `HFS_ContextResponse.eventParticipants` exposes event-to-entity participant
  links beside entities and relationships.
- `READ_PROVENANCE` accepts `HFS_Event_Participant__c` roots and traces those
  participant links back to their immutable source event.

This is not yet the full C03 product surface. The next C03 slice should add UI
inspection and correction affordances so humans can review and amend
relationship history without losing source evidence.
