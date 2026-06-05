# Apex Service Contract

## Scope

Version `1.0.0` defines the Core-lane boundary used by Lightning, Agentforce,
and integration adapters. It covers:

- permission-aware relationship context retrieval;
- source provenance and evidence citations;
- recommendation storage;
- approval requests and human decisions;
- pending action logging;
- outcome capture.

The contract classes are under `force-app/main/default/classes/`. The service
implementation belongs to `hfs-v1-05b`.

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
- Inaccessible source evidence returns
  `SOURCE_EVIDENCE_INACCESSIBLE`; it is never silently summarized.
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
