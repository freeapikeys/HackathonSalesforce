# Salesforce Core Data Model

The initial operational model implements the vertical-slice chain:

`event -> entity and relationship context -> work and SOP -> evidence ->
recommendation -> approval -> action -> outcome -> evaluation`

## Objects

| Object                     | Responsibility                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HFS_Event__c`             | Preserved event envelope, source identity, ordering, hashes, and intake result                                                                                      |
| `HFS_Entity__c`            | Person alias, organization, partner, regulator, unit, resource, or location                                                                                         |
| `HFS_Relationship__c`      | Directed, typed, time-bounded relationship between two entities                                                                                                     |
| `HFS_Event_Participant__c` | Entity participation and role in an event                                                                                                                           |
| `HFS_Agreement__c`         | Agreement, policy, SLA, promise, obligation, status, and material terms                                                                                             |
| `HFS_Work_Item__c`         | Accountable cross-functional work triggered by evidence                                                                                                             |
| `HFS_SOP_Execution__c`     | Versioned SOP execution and current step                                                                                                                            |
| `HFS_Evidence__c`          | Citable source evidence connected to work                                                                                                                           |
| `HFS_Recommendation__c`    | Grounded proposed intervention and model invocation trace                                                                                                           |
| `HFS_Approval__c`          | Human decision under an explicit policy                                                                                                                             |
| `HFS_Action__c`            | Approved outreach or operational action                                                                                                                             |
| `HFS_Outcome__c`           | Observed result of an action                                                                                                                                        |
| `HFS_Evaluation__c`        | Human, rule, model, or system assessment of an outcome                                                                                                              |
| Object                     | Responsibility                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HFS_Event__c`             | Preserved event envelope, source identity, ordering, hashes, and intake result                                                                                      |
| `HFS_Entity__c`            | Person, organization, supplier, partner, regulator, unit, or other entity                                                                                           |
| `HFS_Relationship__c`      | Directed, typed, time-bounded relationship between two entities, including explicit supersession state when a human approves a correction                           |
| `HFS_Event_Participant__c` | Entity participation and role in an event                                                                                                                           |
| `HFS_Agreement__c`         | Agreement, promise, obligation, status, and material terms                                                                                                          |
| `HFS_Work_Item__c`         | Accountable cross-functional work triggered by evidence, with optional target relationship, dependency, owner role, handoff, escalation, and verified closure state |
| `HFS_SOP_Execution__c`     | Versioned SOP execution, current step, evidence requirements, and escalation rule                                                                                   |
| `HFS_Evidence__c`          | Citable source evidence connected to work                                                                                                                           |
| `HFS_Recommendation__c`    | Grounded proposed intervention and model invocation trace                                                                                                           |
| `HFS_Approval__c`          | Human decision under an explicit policy                                                                                                                             |
| `HFS_Action__c`            | Approved outreach or operational action                                                                                                                             |
| `HFS_Outcome__c`           | Observed result of an action                                                                                                                                        |
| `HFS_Evaluation__c`        | Human, rule, model, or system assessment of an outcome                                                                                                              |

Every mapped operational record has a tenant key and stable external key.
Source-derived records link to the immutable event that produced them.

## Global Primitive Mapping

North Star should map business concepts onto global primitives before adding
new custom objects. Add fields or types only when the generic model cannot
express the demo requirement.

| Global primitive | Initial model mapping                                      |
| ---------------- | ---------------------------------------------------------- |
| `Signal`         | `HFS_Event__c`                                             |
| `Evidence`       | `HFS_Evidence__c`                                          |
| `Entity`         | `HFS_Entity__c`                                            |
| `Resource`       | `HFS_Entity__c` with a resource type or evidence attribute |
| `Location`       | `HFS_Entity__c` or event/evidence location attribute       |
| `Actor`          | user, role alias, or `HFS_Entity__c`                       |
| `Customer`       | alias entity or evidence alias                             |
| `Partner`        | `HFS_Entity__c`                                            |
| `Process`        | `HFS_Work_Item__c` or `HFS_SOP_Execution__c`               |
| `Risk`           | event, evidence, recommendation, or evaluation attribute   |
| `Policy`         | `HFS_Agreement__c` or approval policy field                |
| `Recommendation` | `HFS_Recommendation__c`                                    |
| `Approval`       | `HFS_Approval__c`                                          |
| `Action`         | `HFS_Action__c`                                            |
| `Outcome`        | `HFS_Outcome__c`                                           |
| `Metric`         | `HFS_Evaluation__c`, outcome field, or evidence metric     |

## Private Hospital Mapping

| Hospital concept                                                     | Initial model mapping                                    |
| -------------------------------------------------------------------- | -------------------------------------------------------- |
| Hospital, department, ward, service desk                             | `HFS_Entity__c`                                          |
| Patient or visitor alias                                             | `HFS_Entity__c` or evidence alias, no real personal data |
| Bed, room, queue, pharmacy item, equipment, staff pool               | `HFS_Entity__c` as typed resource                        |
| Lab, laundry, insurer, payment, food, maintenance partner            | `HFS_Entity__c`                                          |
| Complaint, queue spike, stock risk, vendor delay, billing issue      | `HFS_Event__c`                                           |
| Source proof                                                         | `HFS_Evidence__c`                                        |
| Action plan                                                          | `HFS_Recommendation__c`                                  |
| Operations manager decision                                          | `HFS_Approval__c`                                        |
| Service task, bed cleaning, vendor escalation, billing review, alert | `HFS_Action__c`                                          |
| Result                                                               | `HFS_Outcome__c` and `HFS_Evaluation__c`                 |

## Enforced Relationships

- relationships require distinct subject and object entities;
- agreements require distinct parties;
- work items require a primary entity and trigger event;
- correction-review work items may point at the relationship assertion being
  reviewed;
- SOP executions require a work item;
- verified work closure requires a closure timestamp and outcome record;
- evidence requires a work item and source event;
- recommendations require work, subject, and primary evidence;
- approvals require a recommendation;
- actions require both the recommendation and an approved approval record;
- outcomes require an action and source event;
- evaluations require an outcome.

Validation rules also enforce confidence ranges and chronological ordering.
Salesforce does not support metadata-level `required` on long-text-area fields.
Narrative and JSON bodies are therefore enforced by the Apex command services,
while their relationship, identity, timestamp, and hash fields are enforced by
metadata.

## Access Model

- `HFS_Relationship_User` reads all context and edits work, SOP execution,
  evidence, and recommendations.
- `HFS_Approver` reads all context, edits approvals, may update relationship
  supersession fields when approving a correction, and receives the
  `HFS_Approve_Recommendation` custom permission.
- `HFS_Integration_User` reconciles all records and receives the
  `HFS_Execute_Action` custom permission.

The initial objects use read/write organization sharing for the single-org MVP.
Permission sets define functional access. Tenant enforcement, restriction
rules, and private sharing are production-hardening work and must be completed
before multi-tenant or regulated deployment.

## Clinical Boundary

The Salesforce model may preserve evidence that a user asked for a clinical
decision, but the recommendation/action chain must refuse diagnosis, treatment,
dosage, triage, and clinical priority decisions. Such requests should route to
a clinician or clinical manager review path, not an automated action.

## Generation And Validation

`config/core-salesforce-model.json` is the versioned model definition.
Regenerate metadata after changing it:

```bash
python3 scripts/generate_core_salesforce_metadata.py
npm run check:metadata
```

The generated Salesforce DX source remains checked into `force-app`.

After deployment to a development org, run the rollback-based smoke test:

```bash
sf apex run \
  --file scripts/apex/verify_core_metadata.apex \
  --target-org dev-ed
```

It creates the complete chain inside a savepoint, verifies rejected relationship
and action states, then rolls the transaction back.
