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

## North Star Hospital Actions

North Star should keep hospital actions behind the existing
`EXECUTE_APPROVED_ACTION` operation unless a real integration requires a new
contract version.

Approved mock write-backs for the private hospital demo should include:

- `CREATE_PATIENT_SERVICE_TASK`
- `REQUEST_BED_CLEANING`
- `ESCALATE_LAB_VENDOR_CASE`
- `CREATE_PHARMACY_RESTOCK_REQUEST`
- `OPEN_BILLING_REVIEW`
- `REQUEST_INSURANCE_FOLLOWUP`
- `SEND_SLACK_ALERT`
- `SEND_WHATSAPP_ALERT`
- `CAPTURE_HOSPITAL_OUTCOME`

The same action boundary can later support hotel, airport, banking,
supermarket, cruise, or other profiles by changing action types and payloads,
not by adding a new endpoint.

## Protected Action Rules

- All external actions require business manager approval unless explicitly
  scoped as local demo mocks.
- Channel results must be honest: `SENT` only means the external provider
  accepted the message; `MOCK_SENT` means no real provider was used.
- Action and channel responses must preserve tenant, correlation, approval ID,
  action ID, evidence IDs, provider/status if applicable, fallback reason if
  applicable, and callback/outcome reference when available.
- Slack can use `SLACK_WEBHOOK_URL`. WhatsApp can use Twilio Sandbox or a
  WhatsApp-enabled Twilio sender through `TWILIO_ACCOUNT_SID`,
  `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, and `TWILIO_WHATSAPP_TO`.
- Clinical diagnosis, treatment, dosage, triage, and clinical priority actions
  are not valid MuleSoft actions for the demo.

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

The connected demo registers only Salesforce-approved actions with the mock
write-back adapter. It first submits an unregistered approval and requires a
`403 PERMISSION_DENIED` with no outcome, then executes approved Slack and
WhatsApp-style actions, captures the callbacks, and writes correlated outcomes
back to Salesforce.
