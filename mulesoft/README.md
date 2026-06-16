# MuleSoft Integration Boundary

The version `1.0.0` Process API contract is generated at
`api/hfs-integration-v1.openapi.json`. It freezes these operations:

- source event ingestion;
- authorized event replay;
- permission-aware context retrieval;
- approved action execution;
- outcome callback capture.

Every operation preserves tenant and correlation identifiers, uses the stable
service error envelope, and includes request, success, denial, conflict,
validation, retryable-failure, and callback examples. Protected source-system
actions require an approval identifier and are accepted for execution rather
than performed inside the Salesforce logging transaction.

OAuth 2.0 client credentials and mutual TLS are both required. The optional
`X-Callback-Url` header requests a signed completion callback; it does not
weaken the synchronous response or retry contract.

Run:

```bash
npm run check:mulesoft
```

The generator keeps the OpenAPI document and example catalog deterministic.
Edit `scripts/generate_mulesoft_contract.py`, regenerate, and commit both
generated JSON files.

## Mock Runtime

`mock_runtime/` is the replaceable local reference implementation behind the
frozen API. It preserves accepted source events, reads seeded context, executes
only registered approved actions, writes deterministic mock source records,
captures correlated outcomes, and retries optional completion callbacks.

Event ingestion shares its stateful classifier with the versioned event
fixtures. The mock therefore exposes the same accepted, duplicate, late,
out-of-order, conflict-review, schema-rejection, hash-rejection, and
idempotency-conflict behavior that Mule flows must preserve.

The generated contract also exposes `POST /v1/events/replays`. The reference
runtime records immutable intake attempts, retries temporary source-store
failures, quarantines exhausted or correctable failures, authorizes replay by
purpose, and links each replay attempt to its original audit record.

## Logia Mock Actions

The active Logia demo uses the same mock runtime to simulate private
hospital operations systems and channels:

- patient-service tasks;
- bed cleaning and discharge-room release tasks;
- lab, laundry, insurer, payment, food, maintenance, transport, and equipment
  partner escalations;
- pharmacy or supply restock requests;
- billing review and insurance follow-up;
- Slack staff alert;
- WhatsApp-style urgent staff alert;
- protected vendor or supplier email queue;
- hospital outcome callback.

Use real Slack or WhatsApp credentials only when they are available and safe to
configure. Otherwise the mock runtime should return deterministic channel
delivery records that are clearly presented as demo channel results.

The runtime deliberately keeps adapters behind Python interfaces so the same
contract tests can be applied to Mule flows and real connectors without
embedding mock behavior in production configuration. The runtime is an
integration test harness, not a substitute for an Anypoint deployment.

## Signal Intake Path

Inbound customer and operations signals must enter through event intake, not
through approved action execution.

Use `POST /v1/events` for:

- WhatsApp customer, patient, visitor, or client complaints;
- Salesforce command-center intake form submissions;
- queue, room, stock, partner, payment, billing, or equipment system events;
- staff voice or manual transcript requests that need governed reasoning.

For WhatsApp inbound, the intended production-shaped flow is:

1. Twilio Sandbox or Meta receives the customer message.
2. MuleSoft maps the webhook payload to an `INGEST_EVENT` request.
3. The event stores source channel, timestamp, safe message summary, synthetic
   customer alias, department/resource hints, tenant, correlation ID, and
   content hash.
4. Salesforce stores the signal and evidence.
5. Agentforce drafts an action plan from that evidence.
6. Any reply, Slack alert, vendor request, billing review, stock request,
   refund, or vendor email action still requires approval first.

Inbound WhatsApp must never directly send medical advice, decide clinical
priority, issue refunds, email vendors, change stock, or message staff without
the protected action boundary.

The local reference runtime now includes
`MockIntegrationApi.ingest_twilio_whatsapp(...)` for deterministic demo and
test use. It maps a Twilio-style payload into `INGEST_EVENT`, masks the customer
phone number, hashes the raw message body, adds follow-up questions, adds
root-cause hypotheses, and preserves the event through the same intake
classifier used by the Process API.

The repo also includes `mulesoft/logia-twilio-webhook`, a deployable Mule
app for live WhatsApp inbound messages. The current CloudHub public route is
the inherited endpoint
`https://<cloudhub-host>/twilio/whatsapp/inbound`; despite the path name, it is
provider-neutral. Twilio Sandbox form posts return TwiML, and Meta WhatsApp
Cloud API JSON posts return JSON. Both shapes map into a safe JSON payload and
call the existing Salesforce Apex REST endpoint
`/services/apexrest/logia/v1/twilio/whatsapp`. Salesforce then creates the
event, synthetic customer alias, evidence, work item, recommendation, and
pending approval.

Current deployed demo webhook:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

Use that same URL as the Meta WhatsApp Cloud API callback URL. The verify token
configured in Anypoint is `north-star-meta-verify`. A healthy Meta verification
request returns HTTP `200` with the raw `hub.challenge` body; an incorrect token
returns HTTP `403`.

Meta does not display the webhook HTTP response in the WhatsApp chat. A visible
customer acknowledgement requires an outbound Messages API call. The deployable
webhook app sends the neutral acknowledgement only when CloudHub has valid
`meta.whatsappPhoneNumberId` and secure `meta.whatsappAccessToken` runtime
properties. If the token expires, inbound evidence still stores safely in
Salesforce, but the customer will not see a WhatsApp reply until the secure
property is refreshed.

Verify with:

```bash
npm run check:mulesoft
```

## Slack Alert Path

Slack is modeled as the protected action type `SEND_SLACK_ALERT` behind
`EXECUTE_APPROVED_ACTION`. In the local reference runtime, an approved Slack
action validates the role, target channel, message, evidence IDs, and source
recommendation before producing a channel delivery record.

Slack has four MVP roles:

1. internal alert delivery through `SLACK_WEBHOOK_URL`;
2. Block Kit approval cards with `Approve`, `Reject`, and `Modify`;
3. signed interactivity handling through `SLACK_SIGNING_SECRET`;
4. `/logia status <case-id|approval-id>`, `/logia queue`, and
   `/logia demo hospital|airport|hotel|bank` slash-command checks.

It now also has a natural manager/staff UX in the reference runtime:

- `/logia order <item> qty <amount> due <days> supplier <email>` drafts a
  protected supplier email and approval card;
- `/logia order` with missing details returns the order modal/form payload;
- `@Logia ...` app mentions and Logia DMs route stock/order wording into the
  same protected workflow;
- the `Send to Logia` message shortcut can prefill the order modal from an
  existing Slack message;
- complete stock orders register a pending protected action and can mirror a
  safe row into `Logia Operations Queue`.

Use `SLACK_WEBHOOK_URL` only as a local or Anypoint secure property. If it is
configured, the runtime posts the approved message to the webhook and records
`SENT`. If it is missing, the runtime records `MOCK_SENT` with
`provider = mock-slack` and a fallback reason. Unapproved Slack actions are
denied before payload execution, and malformed Slack payloads return
`VALIDATION_FAILED`.

True Slack approval is separate from the incoming webhook. It requires a Slack
App with Interactivity enabled, a public Request URL, and
`SLACK_SIGNING_SECRET` stored outside Git. The local reference runtime validates
Slack request signatures, rejects replayed interactions, supports Approve and
Reject decisions, and keeps protected actions blocked until a signed approval
decision is accepted. The Modify button returns an ephemeral instruction to
revise the recommendation in Salesforce because Salesforce currently supports
only `APPROVED` and `REJECTED` approval decisions.

For the free CloudHub route, use the same deployed Mule app. No paid Slack plan,
ngrok, or tunnel is required for Slack messages, buttons, or slash-command
acknowledgements after the app is deployed. Slack Lists are different: they are
optional paid-plan mirrors and require `lists:write`.

Slack App **Interactivity & Shortcuts** Request URL:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

Slack slash command Request URL for `/logia`:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

Use the same verified CloudHub ingress URL for both Slack settings. The Mule
app also has friendly `/slack/interactions` and `/slack/commands` listeners, but
the current shared CloudHub target rewrites public ingress paths to `/` and live
tests return `404` on the friendly paths. The active inherited ingress route is
therefore the reliable free demo URL for Slack.

The CloudHub Slack route returns fast, privacy-safe ephemeral acknowledgements
so Slack button clicks and commands do not time out. The governed Salesforce
approval record remains the system of record for action execution. The signed
local runtime is still the strongest proof of approval semantics until the
CloudHub flow is extended to preserve Slack's exact raw form body and write the
decision back to Salesforce.

The runtime now records `slackFeatures` in delivery evidence, for example
`incoming_webhook`, `mock_delivery`, `block_kit_approval`,
`signed_interactivity`, `approve_reject_modify`, and `thread_ready`. These are
presentation-safe capabilities, not proof that Slack has executed protected
business work without approval.

The `/logia` slash commands use the same signed request validation as button
interactions and return only safe approval/action readiness details. They do
not expose raw complaint text, phone numbers, patient details, or secrets.

- `/logia status <case-id|approval-id>` checks safe approval or delivery state.
- `/logia queue` summarizes active approvals and queue state.
- `/logia profile hospital|airport|hotel|bank` sets the channel demo profile
  for manager orders and role-task wording.
- `/logia demo hospital|airport|hotel|bank` previews the same universal pack
  under a judge-readable profile.
- `/logia demo run hospital-surge` posts the 5-7 minute scripted showcase
  sequence: WhatsApp signal, evidence, agents, manager approval, protected
  action, and outcome.
- `/logia report gloves are low at pharmacy` captures a worker-safe issue,
  creates role tasks, and routes protected actions to the Operations Manager.
- `/logia order hospital gloves qty 500 due 3 days supplier supplier@example.com`
  drafts a supplier email, task mirror, and approval card. Approval is required
  before Gmail or queued fallback execution.
- Worker-like users should report issues; manager-like users draft protected
  supplier email. The reference runtime routes unauthorized worker order
  attempts to a manager review report instead of creating a supplier email.

Optional Slack Lists support mirrors queue work into `Logia Operations Queue`.
Salesforce remains the source of truth. The Slack app needs `lists:write` to
create/update the mirror; `lists:read` is useful when inspecting existing list
and column IDs. The mirror writes safe fields only:
case, profile, module, priority, status, owner role, due time, approval ID,
action ID, evidence count, and outcome. Configure it outside Git with:

- `SLACK_BOT_TOKEN`
- `SLACK_LIST_ID_OPERATIONS`, optional if the runtime should attempt list
  creation
- `SLACK_LIST_COLUMN_CASE`
- `SLACK_LIST_COLUMN_PROFILE`
- `SLACK_LIST_COLUMN_MODULE`
- `SLACK_LIST_COLUMN_PRIORITY`
- `SLACK_LIST_COLUMN_STATUS`
- `SLACK_LIST_COLUMN_OWNER`
- `SLACK_LIST_COLUMN_DUE`
- `SLACK_LIST_COLUMN_APPROVAL`
- `SLACK_LIST_COLUMN_ACTION`
- `SLACK_LIST_COLUMN_EVIDENCE_COUNT`
- `SLACK_LIST_COLUMN_OUTCOME`

If the workspace is unpaid, `lists:write` is missing, or column IDs are absent,
the approved Slack alert still sends and the delivery record marks the List
mirror as skipped or failed.

For an Anypoint build, keep the same Process API boundary and implement the
Slack write-back as a Mule flow or connector-backed adapter behind
`POST /v1/actions/executions`. Store the webhook URL in Anypoint secure
configuration, never in Git. Optional future bot-token mode can use
`SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` for `chat.postMessage`,
`chat.update`, threaded replies, and ephemeral status messages; until those are
configured, the webhook plus signed local harness remains the safe demo path.
If bot-token `chat.postMessage` returns `channel_not_found`, invite the app to
the target channel or reinstall it with the required channel scopes. The
incoming webhook path is still the simplest live Slack delivery path.

## WhatsApp Alert Path

WhatsApp is modeled as the protected action type `SEND_WHATSAPP_ALERT` behind
`EXECUTE_APPROVED_ACTION`. In the local reference runtime, an approved WhatsApp
action validates the role alias, target alias, message, evidence IDs, and
source recommendation before producing a channel delivery record.

For the hackathon demo, use Meta Cloud API when the app, phone number, webhook,
and access token are ready. Keep Twilio Sandbox as the backup path. The runtime
prefers Meta Cloud API when all of these environment variables are configured:

- `META_WHATSAPP_PHONE_NUMBER_ID`
- `META_WHATSAPP_ACCESS_TOKEN`
- `META_WHATSAPP_TO`
- `META_GRAPH_VERSION`, optional, default `v25.0`

If Meta is not configured, the runtime can send through Twilio Sandbox or a
WhatsApp-enabled Twilio sender when all of these environment variables are
configured:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `TWILIO_WHATSAPP_TO`

Use the Twilio WhatsApp address format, for example `whatsapp:+14155238886`, for
Twilio. Use a normal E.164 recipient such as `+23055550123` for Meta. If no
provider variable set is complete, the runtime records `MOCK_SENT` with
`provider = mock-whatsapp` and a fallback reason. If the configured provider
rejects or times out, the runtime records `FAILED`; it never claims `SENT`
unless the provider accepts the message.

Use outbound WhatsApp for urgent internal mobile alerts or approved
customer-facing acknowledgements. For hackathon safety, customer-facing replies
must be privacy-safe, approval-gated, and free of diagnosis, treatment, dosage,
triage, or clinical-priority wording.

For an Anypoint build, keep the same Process API boundary and implement the
WhatsApp write-back as a Mule flow or connector-backed adapter behind
`POST /v1/actions/executions`. For the hackathon, store Meta Cloud API or
Twilio Sandbox credentials in Anypoint secure configuration or process
environment, never in Git. Meta is preferred when the app, phone number, test
recipient, token, and webhook are ready; Twilio stays the backup.

## Gmail Supplier Email Path

Vendor email is modeled as the protected action type `SEND_VENDOR_EMAIL` behind
`EXECUTE_APPROVED_ACTION`. In the local reference runtime, a manager-created
stock order registers a pending `SEND_VENDOR_EMAIL` action. A Slack approval can
approve it, and the adapter executes it only after the approval is valid.

When these variables are configured outside Git, the runtime sends through the
Gmail API using the narrow `gmail.send` scope:

- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- `GMAIL_SENDER_EMAIL`
- `GMAIL_SUPPLIER_EMAIL`, optional fallback recipient

If Gmail credentials are missing, the supplier recipient is missing, or Gmail
returns a retryable failure, Logia records `QUEUED` with an honest fallback
reason. Do not claim live email delivery unless a visible Gmail message ID is
recorded after approval.

## Clinical Boundary

The MuleSoft boundary must not expose actions for diagnosis, treatment, dosage,
triage, or clinical priority decisions. If a request attempts to execute one of
those actions, the correct result is denial or validation failure with a safe
manager/clinician routing message.

## Nexavenu Revenue Mock Actions

The Nexavenu jury-gift scenario uses the same approved-action execution path for
revenue operations:

- create nurture task;
- draft champion email;
- update opportunity stage;
- assign content asset;
- create solution-consultant handoff;
- capture retention/ascension outcome.

Each action is still a protected write-back. The runtime records only actions
with a matching approved action ID and returns correlated source-record and
outcome evidence for the command center.

It deliberately keeps adapters behind Python interfaces so the same contract
tests can be applied to Mule flows and real connectors without embedding mock
behavior in production configuration. The runtime is an integration test
harness, not a substitute for an Anypoint deployment.
