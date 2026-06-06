# MuleSoft API Contract

## Boundary

Version `1.0.0` is the stable MuleSoft Process API boundary between source
adapters, Salesforce Core, Agentforce consumers, and write-back adapters. The
contract is executable at
`mulesoft/api/hfs-integration-v1.openapi.json`.

| Operation                 | Path                          | Result                                                         |
| ------------------------- | ----------------------------- | -------------------------------------------------------------- |
| `INGEST_EVENT`            | `POST /v1/events`             | Deterministic intake disposition                               |
| `READ_CONTEXT`            | `POST /v1/context/queries`    | Permission-aware relationship context                          |
| `EXECUTE_APPROVED_ACTION` | `POST /v1/actions/executions` | Accepted source-system write-back correlated to human approval |
| `CAPTURE_OUTCOME`         | `POST /v1/outcomes/callbacks` | Idempotent outcome capture and action correlation              |

## Invariants

- `X-Tenant-Id` and `X-Correlation-Id` are required and must match their body
  values.
- Write operations require `X-Idempotency-Key`; reusing a key with different
  content returns `IDEMPOTENCY_CONFLICT`.
- Exact retries return the prior result with `replayed = true`.
- `403` is a policy or permission denial, `409` is a state or idempotency
  conflict, `422` is deterministic validation failure, and `503` is retryable.
- Error bodies use the Apex service error codes and never expose raw upstream
  exception text.
- Approved action execution is a separate MuleSoft transaction after
  Salesforce has logged the pending action.
- Callbacks preserve the original tenant, correlation, operation, and result.
- Callback delivery is retried independently and cannot change the original
  operation result.

## Compatibility

Additive optional fields are compatible within version `1.0.0`. Removing or
renaming fields, changing required inputs, changing an error code, changing
idempotency scope, or weakening approval and authorization rules requires a new
contract version and cross-lane review.
