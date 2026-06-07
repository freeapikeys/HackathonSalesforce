# MuleSoft API Contract

## Boundary

Version `1.0.0` is the stable MuleSoft Process API boundary between source
adapters, Salesforce Core, Agentforce consumers, and write-back adapters. The
contract is executable at
`mulesoft/api/hfs-integration-v1.openapi.json`.

| Operation                 | Path                          | Result                                                         |
| ------------------------- | ----------------------------- | -------------------------------------------------------------- |
| `INGEST_EVENT`            | `POST /v1/events`             | Deterministic intake disposition                               |
| `REPLAY_EVENT`            | `POST /v1/events/replays`     | Authorized linked replay of a quarantined intake attempt       |
| `READ_CONTEXT`            | `POST /v1/context/queries`    | Permission-aware relationship context                          |
| `EXECUTE_APPROVED_ACTION` | `POST /v1/actions/executions` | Accepted source-system write-back correlated to human approval |
| `CAPTURE_OUTCOME`         | `POST /v1/outcomes/callbacks` | Idempotent outcome capture and action correlation              |

## Invariants

- `X-Tenant-Id` and `X-Correlation-Id` are required and must match their body
  values.
- Write operations require `X-Idempotency-Key`; reusing a key with different
  content returns `IDEMPOTENCY_CONFLICT`.
- Exact retries return the prior result with `replayed = true`.
- Event replay requires purpose `REPLAY_QUARANTINED_EVENT`, accepts only an
  original attempt in `QUARANTINED` state, and creates a linked attempt.
- Replay idempotency is independent from source-event idempotency; neither an
  exact replay nor a corrected event can mutate the original attempt.
- Schema/hash failures and exhausted source-store retries are quarantined.
  Idempotency and invalid-state conflicts are permanent rejections.
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

Verify compatibility with:

```bash
npm run check:mulesoft
npm run demo:run
```

The connected demo registers only the Salesforce-approved action with the mock
write-back adapter. It first submits an unregistered approval and requires a
`403 PERMISSION_DENIED` with no outcome, then executes the approved action,
captures the callback, and writes the correlated outcome back to Salesforce.
