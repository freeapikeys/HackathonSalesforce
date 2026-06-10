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

The command center now adds a human-facing inspection surface:

- relationship-history cards show subject, object, assertion type, status,
  confidence, source event, and correction state;
- source participant links show which entity was attached to which source
  event and under which role;
- contradictory claims stay visible with the proposed resolution instead of
  being overwritten;
- correction controls emit a governed review intent and do not mutate records or
  execute external actions directly.
- live correction-review requests persist a governed work item, source
  evidence, recommendation, and pending approval using existing HFS records.
- approved correction-review decisions persist supersession state on the target
  relationship, including the approval, reviewer, timestamp, and reason, while
  rejected reviews leave the relationship unchanged.

C03 still has future depth available around richer replacement assertions and
graph traversal, but the MVP now preserves source claims, review work, human
decisions, and supersession state through the Salesforce service layer.
