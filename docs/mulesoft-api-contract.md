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

## Logia Hospital Actions

Logia should keep hospital actions behind the existing
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
- `SEND_VENDOR_EMAIL`
- `CAPTURE_HOSPITAL_OUTCOME`

The same action boundary can later support hotel, airport, banking,
supermarket, cruise, or other profiles by changing action types and payloads,
not by adding a new endpoint.

## Logia Signal Intake

Inbound complaint and operations channels are not action executions. They are
source signals and should enter through `INGEST_EVENT`.

Preferred intake examples:

- WhatsApp inbound customer complaint from Meta WhatsApp Cloud API;
- Salesforce command-center complaint or signal form;
- system threshold event such as low pharmacy stock, queue spike, room blocked,
  lab delay, payment issue, or billing approval stalled;
- staff voice/manual transcript converted into a governed request.

Inbound WhatsApp mapping:

1. Meta WhatsApp Cloud API receives the customer or patient message.
2. Meta posts to a MuleSoft/source adapter endpoint.
3. The adapter maps the message to the `INGEST_EVENT` request shape with:
   source channel, synthetic customer alias, timestamp, safe message summary,
   department/resource hints, tenant ID, correlation ID, and content hash.
4. Salesforce stores the signal and evidence.
5. Agentforce may draft a recommendation from the new evidence.
6. Any customer reply, Slack alert, vendor request, stock request, billing
   review, refund, or vendor email action must then go through approval and
   `EXECUTE_APPROVED_ACTION`.

Inbound WhatsApp must not directly create a refund, send a vendor email, change
stock, reply with medical advice, or decide clinical priority.

The local mock runtime includes a deterministic
`MockIntegrationApi.ingest_twilio_whatsapp(...)` adapter for the hackathon demo.
The method name is historical. The active CloudHub route accepts Meta WhatsApp
Cloud API payloads and the legacy Twilio-style payload shape. It maps inbound
messages into `INGEST_EVENT`, masks the phone number, stores a synthetic alias,
hashes the raw message body, adds complaint classification, follow-up
questions, root-cause hypotheses, next-evidence needs, and affected primitives.

## Protected Action Rules

- All external actions require business manager approval unless explicitly
  scoped as local demo mocks.
- Channel results must be honest: `SENT` only means the external provider
  accepted the message; `MOCK_SENT` means no real provider was used.
- Action and channel responses must preserve tenant, correlation, approval ID,
  action ID, evidence IDs, provider/status if applicable, fallback reason if
  applicable, and callback/outcome reference when available.
- Slack can use `SLACK_WEBHOOK_URL`. WhatsApp should use official Meta
  WhatsApp Cloud API for the hackathon demo. Twilio environment variables are
  legacy backup only.
- Slack approval buttons are a separate interaction path from the incoming
  webhook. Signed interactions require `SLACK_SIGNING_SECRET`, timestamp and
  signature validation, replay rejection, and a pending approval before the
  decision can be recorded.
- Slack delivery evidence must say which Slack capabilities were used:
  webhook or mock delivery, Block Kit approval, signed interactivity,
  approve/reject/modify buttons, slash-command status, or thread-ready
  metadata.
- `/logia status <approval-id>` is an internal Slack status command. It may
  report approval state and action readiness, but it must not expose raw
  complaint text, contact data, patient details, secrets, or execute actions.
- Vendor email notification is implemented as protected mock action
  `SEND_VENDOR_EMAIL`; do not claim live email delivery unless an Anypoint,
  SMTP, or email-provider connector is configured and tested.
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
`403 PERMISSION_DENIED` with no outcome, then executes the approved action,
captures the callback, and writes the correlated outcome back to Salesforce.

For Logia, approved mock write-backs should include retail action types such
as supplier quality case, replacement-batch request, reorder request, warehouse
transfer, markdown plan, store tasks, Slack alert, WhatsApp-style alert, and
retail outcome capture. These can remain action payloads behind the existing
`EXECUTE_APPROVED_ACTION` operation unless a real integration requires a new
contract version.

For the Nexavenu revenue-intelligence gift, the same approved-action operation
supports synthetic revenue actions: nurture task creation, champion email draft,
opportunity stage update, content asset assignment, solution-consultant handoff,
and retention/ascension outcome capture. These remain protected external actions
and require a matching approved Salesforce action before the MuleSoft mock
write-back records source evidence or outcome metrics.
