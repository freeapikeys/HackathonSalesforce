# Apex Service Contract

## Scope

Version `1.0.0` defines the Core-lane boundary used by Lightning, Agentforce,
and integration adapters. It covers:

- permission-aware relationship/context retrieval;
- source provenance and evidence citations;
- recommendation storage;
- approval requests and human decisions;
- pending action logging;
- outcome capture.

The service remains domain-neutral. North Star maps global primitives and the
private hospital demo profile onto the same context, recommendation, approval,
action, and outcome boundary.

The contract and implementation classes are under
`force-app/main/default/classes/`. `HFS_RelationshipServiceImpl` is the
`with sharing` implementation, `HFS_ContextAssembler` builds context and
provenance responses, and `HFS_ServiceSupport` normalizes validation,
authorization, replay, and error behavior.

## Implemented Behavior

- Context reads start from a work item or subject entity and assemble the
  connected entity, relationship, agreement, SOP, evidence, recommendation,
  approval, action, outcome, evaluation, and event graph.
- Provenance reads use an explicit object allowlist and trace records back to
  citable evidence and immutable source events.
- Queries use user mode; command DML uses user mode and the service runs with
  sharing.
- Every referenced record is checked against the request tenant.
- Recommendation, approval request, action, and outcome external keys replay
  only when the persisted command content matches.
- Approval decisions and action execution require their named custom
  permissions.
- Human decisions derive the deciding user and timestamp on the server.
- Outcome capture records the outcome, marks the action executed, and completes
  terminal work in one rollback-protected transaction.

## North Star Hospital Mapping

The Apex service should be able to represent:

- patient or visitor aliases without real personal or medical data;
- departments, locations, beds, rooms, queues, pharmacy stock, equipment, and
  staff pools as global `Entity` or typed `Resource` records;
- lab, laundry, insurer, payment, food, maintenance, transport, and equipment
  partners;
- complaint, capacity, stock, partner, billing, staff, approval, action, and
  outcome evidence;
- protected actions such as service task, bed cleaning, vendor escalation,
  pharmacy restock, billing review, insurance follow-up, Slack alert, WhatsApp
  alert, and hospital outcome capture.

Clinical diagnosis, treatment, dosage, triage, and clinical priority decisions
must be refused or routed to human clinical review, not executed as Apex or
MuleSoft actions.

## Verified Failure Paths

The Apex suite executes with the deployed `HFS_Relationship_User`,
`HFS_Approver`, and `HFS_Integration_User` permission sets on minimum-access
users. It proves:

- role-appropriate success and cross-role denial;
- missing custom-permission denial;
- inaccessible source evidence fails closed with
  `SOURCE_EVIDENCE_INACCESSIBLE`;
- conflicting external or idempotency keys return `IDEMPOTENCY_CONFLICT`;
- invalid approval and action states are rejected;
- explicit clinical action types return `CLINICAL_DECISION_REFUSED` before
  recommendation or action records are inserted;
- a failure after outcome insertion rolls back the outcome, action update, and
  work update, so a single-command transaction never returns a partial commit.

Hospital-specific tests prove clinical-decision refusal and protected-action
denial before approval.

## Service Interface

`HFS_RelationshipService` exposes:

| Operation              | Request                       | Response                 |
| ---------------------- | ----------------------------- | ------------------------ |
| `READ_CONTEXT`         | `HFS_ContextRequest`          | `HFS_ContextResponse`    |
| `READ_PROVENANCE`      | `HFS_ProvenanceRequest`       | `HFS_ProvenanceResponse` |
| `STORE_RECOMMENDATION` | `HFS_RecommendationCommand`   | `HFS_CommandResult`      |
| `REQUEST_APPROVAL`     | `HFS_ApprovalRequestCommand`  | `HFS_CommandResult`      |
| `DECIDE_APPROVAL`      | `HFS_ApprovalDecisionCommand` | `HFS_CommandResult`      |
| `LOG_ACTION`           | `HFS_ActionCommand`           | `HFS_CommandResult`      |
| `CAPTURE_OUTCOME`      | `HFS_OutcomeCommand`          | `HFS_CommandResult`      |

Every request carries `contractVersion`, `tenantKey`, `correlationId`, and a
non-empty `purpose`. Write commands use stable external keys or action
idempotency keys where the Salesforce model supports them.

## Authorization Matrix

The table describes the baseline permission sets. Effective authorization must
evaluate the current user's sharing, object CRUD, field permissions, and custom
permissions. Assigning multiple permission sets may expand access, but no
implementation may authorize from a role-name string alone.

| Operation            | Relationship user | Approver | Integration user | Additional gate                                       |
| -------------------- | ----------------- | -------- | ---------------- | ----------------------------------------------------- |
| Read context         | Allow             | Allow    | Allow            | Accessible records and fields only                    |
| Read provenance      | Allow             | Allow    | Allow            | Root record and cited evidence must remain accessible |
| Store recommendation | Allow             | Deny     | Allow            | Recommendation create or update access                |
| Request approval     | Deny              | Allow    | Allow            | Approval create access                                |
| Decide approval      | Deny              | Allow    | Deny             | `HFS_Approve_Recommendation`                          |
| Log action           | Deny              | Deny     | Allow            | `HFS_Execute_Action` and approved approval            |
| Capture outcome      | Deny              | Deny     | Allow            | `HFS_Execute_Action`                                  |

`HFS_AuthorizationMatrix` is the executable policy definition. It names the
objects, fields, custom permissions, sharing mode, user-mode data access, and
transaction boundary for every operation.

## Security Invariants

- Service implementations and entry-point controllers use `with sharing`.
- Queries and DML enforce current-user CRUD and field-level security.
- Tenant keys on referenced records must match the request tenant.
- Inaccessible source evidence returns `SOURCE_EVIDENCE_INACCESSIBLE`; it is
  never silently summarized.
- Approval decisions derive `Decision_By__c` from `UserInfo.getUserId()` and
  `Decided_At__c` from the server clock.
- Recommendation generation time, approval request time, and action request
  time use the server clock.
- `LOG_ACTION` records a pending action only. It does not perform an external
  callout in the DML transaction.
- External action execution requires an approved approval linked to the same
  recommendation.
- No partial record graph is committed when a command fails.

## Transaction Boundaries

| Operation                    | Boundary                                           |
| ---------------------------- | -------------------------------------------------- |
| Context and provenance reads | Read-only user-mode transaction                    |
| Recommendation storage       | All-or-nothing DML                                 |
| Approval request             | All-or-nothing DML                                 |
| Approval decision            | All-or-nothing DML                                 |
| Action logging               | All-or-nothing pending-action DML; no callout      |
| Outcome capture              | All-or-nothing outcome, action, and work-state DML |

The implementation may return `PARTIAL_FAILURE` only for an explicitly batched
future endpoint. The version `1.0.0` single-command methods roll back on any
failure.

## Error Contract

Errors use `HFS_ServiceError` and one of the named codes in
`HFS_ServiceContract`, including:

- request and contract errors;
- permission and custom-permission denial;
- missing or inaccessible records and evidence;
- tenant and state mismatches;
- idempotency and validation conflicts;
- retryable dependency failure;
- partial or unexpected failure.

An expected denial is a normal `HFS_CommandResult` with `success = false`; it
must not expose raw exception text or inaccessible record details.

## Compatibility

Additive nullable response fields are backward-compatible within version
`1.0.0`. Renaming or removing a field, changing required input, changing an
error code, or weakening an authorization rule requires a new contract version
and review from every consuming lane.

Verify compatibility with:

```bash
sf apex run test --tests HFS_ServiceContractTest,HFS_RelationshipServiceImplTest --target-org dev-ed --wait 20 --result-format human
```
