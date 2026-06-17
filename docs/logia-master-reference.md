# Logia Master Reference

This is the single quick reference for the hackathon team. It explains what
Logia is, which agents exist, which IDs matter, how live channels are
configured, and how to run the demo.

## Product

Logia is a Salesforce, Agentforce, and MuleSoft operations command center.
It turns messy business signals into evidence-backed recommendations,
manager-approved actions, role-based alerts, and measured outcomes.

The demo profile is a large private hospital. It handles non-clinical
operations only: complaints, room readiness, queues, staff tasks, pharmacy
stock, lab/vendor delays, billing/insurance issues, alerts, approvals, and
outcomes.

Logia must not make diagnosis, treatment, dosage, triage, or clinical
priority decisions.

Logia is general first. Hospital is the flagship demo profile, not the
core product. Core names, IDs, agents, skills, actions, and primitives stay
sector-neutral; hospital words such as patient, bed, ward, pharmacy, clinician,
and lab appear only in the active profile display, demo data, or hospital
fixtures.

## Global Primitives

These are the reusable building blocks. Business-specific objects must map into
these instead of creating a new architecture.

| Primitive        | Meaning                                                                    |
| ---------------- | -------------------------------------------------------------------------- |
| `Signal`         | Event, complaint, alert, request, or anomaly that starts work              |
| `Evidence`       | Source record, message, timestamp, fixture, or system fact                 |
| `Entity`         | Organization, department, vendor, supplier, person role, or account        |
| `Resource`       | Bed, room, stock item, equipment, account, gate, batch, or slot            |
| `Location`       | Ward, room, counter, branch, terminal, store, or service area              |
| `Actor`          | User, manager, agent, vendor, staff role, or system actor                  |
| `Customer`       | Patient, visitor, guest, passenger, shopper, client, or account holder     |
| `Partner`        | Lab, laundry, insurer, payment processor, supplier, airline, or vendor     |
| `Process`        | Discharge, billing, restock, complaint, approval, or escalation flow       |
| `Risk`           | Capacity, safety, financial, service, compliance, reputation, or SLA risk  |
| `Policy`         | Approval, permission, threshold, compliance, or escalation rule            |
| `Recommendation` | Evidence-backed plan proposed by Logia                                     |
| `Approval`       | Human business approval before protected execution                         |
| `Action`         | Task, alert, vendor request, billing review, stock request, or callback    |
| `Outcome`        | Result after execution                                                     |
| `Metric`         | Wait time, stock risk, cost exposure, SLA, completion, or complaint change |

## General IDs

Use these shapes for core IDs. Do not create core IDs such as
`hospital-bed-agent` or `pharmacy-only-action` when a universal primitive or
action can describe the same work.

| Type     | Examples                                                                                                                            |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Profile  | `profile:hospital-private-large`, `profile:airport-operations`, `profile:hotel-guest-operations`, `profile:bank-service-operations` |
| Resource | `resource:room`, `resource:stock-item`, `resource:service-counter`                                                                  |
| Action   | `action:send-internal-alert`, `action:create-service-task`, `action:request-partner-followup`                                       |

## Profile Mapping

Business profiles translate sector words into primitives.

| Universal issue    | Hospital profile                | Hotel profile             | Airport profile                 | Banking profile                    |
| ------------------ | ------------------------------- | ------------------------- | ------------------------------- | ---------------------------------- |
| Room readiness     | Discharge room readiness        | Guest room readiness      | Gate readiness                  | Service case readiness             |
| Stock risk         | Pharmacy stock risk             | Linen or food stock risk  | Equipment stock risk            | Card, cash, or document stock risk |
| Duplicate charge   | Billing duplicate               | Guest overcharge          | Passenger fee dispute           | Bank dispute                       |
| Customer complaint | Patient or visitor complaint    | Guest complaint           | Passenger complaint             | Client complaint                   |
| Partner delay      | Lab, insurer, or supplier delay | Laundry or supplier delay | Airline or ground handler delay | Processor or insurer delay         |

## Agent System

Logia should feel like one coordinated product, not separate chatbots.
Agents can be Agentforce topics, prompt profiles, deterministic modules, or
action contracts.

Logia has 10 core agents in the MVP.

| Agent                       | Role                                                                           |
| --------------------------- | ------------------------------------------------------------------------------ |
| Logia Orchestrator          | Combines all specialist findings into one manager-ready plan                   |
| Evidence and Context Agent  | Normalizes signals, links evidence, detects missing or conflicting facts       |
| Customer Trust Agent        | Classifies complaints and drafts safe manager-approved messages                |
| Resource and Capacity Agent | Checks beds, rooms, queues, staff, stock, equipment, and capacity pressure     |
| Operations Execution Agent  | Creates role-owned tasks, due times, acknowledgements, and escalations         |
| Partner and Vendor Agent    | Tracks lab, laundry, food, insurer, payment, maintenance, and transport status |
| Risk and Approval Agent     | Enforces approval, permission, purpose limits, and clinical refusal            |
| Financial Impact Agent      | Estimates billing, refund, claim, voucher, payment, and revenue exposure       |
| Communication Agent         | Sends approved Slack and WhatsApp alerts to role aliases                       |
| Outcome Learning Agent      | Records outcomes and compares expected result with actual result               |

## Agent Skills And Orchestration

The Orchestrator owns the end-to-end trace. Specialist agents do not act alone;
they return evidence-backed findings into one shared action plan.

| Agent                       | Core skills                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| Logia Orchestrator          | route issue type, merge findings, resolve conflicts, set approval path, explain plan        |
| Evidence and Context Agent  | normalize source signals, map global primitives, detect missing/late/contradictory evidence |
| Customer Trust Agent        | classify complaints, detect clusters, draft privacy-safe service response text              |
| Resource and Capacity Agent | calculate queue pressure, bed/room availability, stock days remaining, staff gap            |
| Operations Execution Agent  | create tasks, assign role owners, set due windows, track acknowledgement                    |
| Partner and Vendor Agent    | check lab/laundry/insurer/payment/food/maintenance status and SLA risk                      |
| Risk and Approval Agent     | decide approval need, enforce permission, refuse clinical decisions, preserve audit         |
| Financial Impact Agent      | estimate refund, billing, claim, voucher, payment, and revenue exposure                     |
| Communication Agent         | prepare Slack, WhatsApp, and protected email messages after approval                        |
| Outcome Learning Agent      | capture outcomes, compare expected vs actual, feed learning into next plan                  |

Optional specialist skills can sit under those agents. They are not separate
chatbots and they must not create a new architecture.

| Specialist skill       | Plugs into              | What it adds                                                        |
| ---------------------- | ----------------------- | ------------------------------------------------------------------- |
| Hospital Operations    | Operations Execution    | room readiness, discharge cleaning, porter, front desk, service SLA |
| Inventory and Capacity | Resource and Capacity   | stock days remaining, transfer option, restock urgency, queue load  |
| Billing and Insurance  | Financial Impact        | duplicate invoice, stuck claim, refund threshold, payment issue     |
| Vendor SLA             | Partner and Vendor      | lab, laundry, food, supplier, maintenance, and insurer follow-up    |
| Customer Experience    | Customer Trust          | complaint follow-up questions and privacy-safe response drafts      |
| Channel Approval UX    | Risk/Approval and Comms | Slack, WhatsApp, and email action wording after approval            |
| Cross-Sector Mapping   | Orchestrator            | maps hospital primitives to airport, hotel, banking, and retail     |

Orchestration flow:

1. Intake creates a `Signal` and linked `Evidence`.
2. Evidence and Context maps the signal to primitives.
3. The Orchestrator asks each specialist for only its slice.
4. Specialists return facts, inferences, missing evidence, risks, and proposed
   actions.
5. Risk and Approval marks which actions are protected.
6. The manager approves, modifies, rejects, or defers.
7. Communication and Operations Execution run only approved actions through
   MuleSoft/Salesforce.
8. Outcome Learning records whether the action worked.

## Universal Issue Modules

| ID      | Module                           | Primary agent         |
| ------- | -------------------------------- | --------------------- |
| `NS-01` | Complaint and trust              | Customer Trust        |
| `NS-02` | Capacity and availability        | Resource and Capacity |
| `NS-03` | Staff coordination               | Operations Execution  |
| `NS-04` | Partner and vendor failure       | Partner and Vendor    |
| `NS-05` | Inventory and supply             | Resource and Capacity |
| `NS-06` | Billing and financial exposure   | Financial Impact      |
| `NS-07` | Risk, safety, and compliance     | Risk and Approval     |
| `NS-08` | Communication and escalation     | Communication         |
| `NS-09` | Disruption handling              | Logia Orchestrator    |
| `NS-10` | Outcome learning                 | Outcome Learning      |
| `NS-11` | Evidence quality and uncertainty | Evidence and Context  |
| `NS-12` | Policy and approval routing      | Risk and Approval     |

## Demo Story

A hospital morning gets messy at the same time:

- patient complaints are increasing;
- discharge rooms are blocked;
- outpatient queues are rising;
- pharmacy stock is low;
- lab response is delayed;
- billing and insurance reviews are stuck.

Logia turns this into one operations plan with evidence, approval,
protected actions, Slack and WhatsApp alerts, and outcome metrics.

## Signal Intake And Channel Roles

Logia has two different channel directions. Do not mix them in the pitch.

Inbound signal channels create `Signal` and `Evidence` records. They do not
execute actions.

Outbound action channels execute approved `Action` records. They require a
business manager approval unless the demo clearly marks them as local mocks.

| Channel                     | Best use                                                 | Current demo state                                                                                                                                                  |
| --------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| WhatsApp inbound            | Customer, patient, visitor, or client complaint intake   | Official Meta WhatsApp Cloud API is active; Twilio is legacy backup only                                                                                            |
| Salesforce command center   | Manager review, approval, command-center visibility      | Active platform surface                                                                                                                                             |
| Salesforce/manual demo form | Optional fallback for staff-entered signals              | Not a core build item for the hackathon v1                                                                                                                          |
| Slack                       | Internal staff and manager coordination                  | Live webhook and bot-token posting work; Lists are optional paid mirror                                                                                             |
| WhatsApp outbound           | Urgent mobile alert or approved customer acknowledgement | Live Meta receipt works; approved replies still need final rehearsal                                                                                                |
| Email                       | Supplier, vendor, insurer, or formal customer follow-up  | Gmail-capable protected action exists in the reference runtime; CloudHub secure properties are configured, but live CloudHub send still needs execution-route proof |

Recommended hackathon stance:

- WhatsApp should be the customer-facing intake story.
- Slack should be the internal worker and manager coordination story.
- Slack supports internal alerts, Block Kit approval cards, signed
  approve/reject/modify decisions, safe
  `/logia status <case-id|approval-id>`, `/logia queue`, and
  `/logia profile hospital|airport|hotel|bank`,
  `/logia demo hospital|airport|hotel|bank`,
  `/logia demo run hospital-surge`, `/logia report <issue>`, and protected
  `/logia order ...` checks, plus delivery/audit metadata in the local runtime.
- Slack approve/reject buttons should be the manager approval story when the
  Slack App interactivity Request URL is configured. The verified free CloudHub
  URL is:
  `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound`.
- The `/logia` slash command uses the same verified CloudHub Request URL:
  `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound`.
- Optional bot-token mode can add live `chat.postMessage`, `chat.update`,
  threaded replies, and ephemeral messages with `SLACK_BOT_TOKEN` and
  `SLACK_CHANNEL_ID`; do not claim message-update or thread features unless
  those credentials are configured and tested.
- Optional Slack Lists mode can mirror safe queue fields into
  `Logia Operations Queue` on a paid Slack workspace with `lists:write`.
  Salesforce remains the source of truth; the list is only a cockpit mirror.
- WhatsApp outbound may be used for urgent internal mobile alerts or approved
  customer-safe replies in the demo.
- Customer-facing WhatsApp replies should be approved, privacy-safe, and
  template/consent-aware.
- The current visible Meta WhatsApp response is a receipt acknowledgement only:
  it proves intake worked, but it is not yet a full agent conversation.
- Email is useful for suppliers, insurers, vendors, or formal follow-up. The
  current repo has a protected Gmail-capable vendor-email adapter. It sends
  only after approval when credentials are configured outside Git; otherwise it
  records a protected queued fallback.
- For the current CloudHub channel app, Gmail OAuth values can be stored as
  Anypoint secure properties with
  `scripts/configure-cloudhub-logia-secrets.ps1`. The live Slack route can send
  an approved supplier email through Gmail and returns a visible `gmail-api`
  message id when delivery succeeds; otherwise it keeps the email queued.

## Slack Cockpit

Slack is the internal operating layer, not the database. Use it to make the
demo feel alive for managers and staff:

- alerts: role-routed internal updates for operations owners;
- approval cards: `Approve`, `Reject`, and `Modify` Block Kit buttons;
- commands: `/logia status <case-id|approval-id>`, `/logia queue`,
  `/logia profile hospital|airport|hotel|bank`,
  `/logia demo hospital|airport|hotel|bank`,
  `/logia demo run hospital-surge`, `/logia report <issue>`, and protected
  `/logia order ...`;
- natural intake: `@Logia` mentions, Logia DMs, `/logia order`, and the
  `Send to Logia` message shortcut can route stock/order requests into a
  protected supplier-email draft;
- threads: one case thread can hold recommendation, approval, execution, and
  outcome updates when bot-token threading is configured;
- Lists: optional paid mirror named `Logia Operations Queue`.

The Slack List mirror uses safe fields only:

| Field            | Meaning                                          |
| ---------------- | ------------------------------------------------ |
| `Case`           | Work item or correlation ID                      |
| `Profile`        | Active profile, for example `profile:airport-*`  |
| `Module`         | Universal issue module                           |
| `Priority`       | Operational priority label                       |
| `Status`         | Pending Approval, Approved, Executing, or Failed |
| `Owner Role`     | Role alias, not a personal user                  |
| `Due Time`       | Demo-safe due window                             |
| `Approval ID`    | Approval record ID                               |
| `Action ID`      | Action record ID                                 |
| `Evidence Count` | Count only, not raw evidence text                |
| `Outcome`        | Safe outcome label                               |

Slack Lists require a paid Slack workspace and `lists:write`. If the List API
fails because the workspace is unpaid, the scope is missing, or column IDs are
not configured, Logia still sends the Slack message and records the List mirror
as skipped or failed. That is acceptable for the demo if stated honestly.

For a step-by-step demo script, see
[docs/logia-demo-operator-guide.md](logia-demo-operator-guide.md).

Universal demo command examples:

```text
/logia demo hospital
/logia demo airport
/logia demo hotel
/logia demo bank
/logia profile hospital
/logia report gloves are low and the queue is not moving
/logia order hospital gloves qty 500 due 3 days supplier supplier@example.com
/logia demo run hospital-surge
```

Each command uses the same primitive flow: signal, evidence, primitive mapping,
agent action plan, approval, MuleSoft execution, Slack update, and outcome.
The `report` command is worker-safe and creates a role-routed issue without
supplier email. The `order` command is manager-initiated and demonstrates a
protected supplier email draft: Slack can show the approval card, but
Salesforce remains the approval and audit source of truth.

## End-To-End Logic

Use this as the judge explanation for "how does a complaint actually enter and
become action?"

1. A customer, patient, visitor, staff member, or system sends a signal.
   Examples: WhatsApp complaint, command-center review note, queue spike, low
   stock event, lab delay, billing issue, or room readiness issue.
2. MuleSoft or Salesforce writes the signal as source-backed evidence.
   Logia stores the message, timestamp, source channel, synthetic alias,
   affected department, resource, partner, and correlation ID.
3. Evidence and Context normalizes the signal into global primitives.
   The same model can handle a hospital bed, hotel room, airport gate, bank
   case, supermarket batch, or cruise cabin as a typed `Resource`.
4. The Orchestrator asks specialist agents for findings.
   Customer Trust classifies the complaint. Resource and Capacity checks rooms,
   queues, stock, equipment, and staff. Partner and Vendor checks external
   delays. Financial Impact checks billing, refund, claim, and payment exposure.
   Risk and Approval checks policy and clinical boundaries.
5. Logia drafts one action plan.
   The plan separates facts, inferences, missing evidence, recommendations,
   blocked clinical actions, required approvals, owners, due windows, and
   expected outcomes.
6. A business manager approves, modifies, rejects, or defers protected actions.
   The manager is an operations role in the demo, not a Salesforce admin.
7. MuleSoft executes only approved actions.
   Examples: Slack internal alert, WhatsApp alert, room-cleaning task, pharmacy
   restock request, lab vendor follow-up, billing review, insurer follow-up, or
   protected mock vendor email.
8. Outcomes return to Salesforce.
   Logia records what was attempted, what happened, which provider accepted
   the message, which tasks were acknowledged, and which metrics changed.

## Deep Resolution Pattern

This is the main competitive differentiator. Logia should not behave like
a chatbot that says "sorry" or "manager notified." It should expand one issue
into the business functions it affects.

For every complaint or operational signal, Logia should:

1. classify the issue type;
2. ask only the follow-up questions needed to fill missing evidence;
3. map the issue to global primitives;
4. identify affected resources, locations, partners, policies, approvals,
   actions, outcomes, and metrics;
5. form root-cause hypotheses without pretending they are facts;
6. request the next evidence needed to confirm or reject each hypothesis;
7. propose one manager-ready action plan;
8. block clinical or unsupported actions;
9. execute only approved actions;
10. measure whether the action actually improved the situation.

Example:

```text
Complaint: "I waited one hour, the pharmacy said there is no stock, and my invoice looks duplicated."
```

Logia should not only send a message. It should connect:

- Customer Trust: wait-time and billing frustration;
- Resource and Capacity: outpatient queue and pharmacy stock;
- Financial Impact: possible duplicate invoice or insurer delay;
- Risk and Approval: no refund or customer reply without approval;
- Communication: Slack internal alert and approved WhatsApp response;
- Outcome Learning: wait reduced, stockout avoided, billing review opened.

The current repo includes two intake paths for this pattern:

- local harness/runtime proof through `MockIntegrationApi.ingest_twilio_whatsapp`;
- deployable Mule app `mulesoft/logia-twilio-webhook` that receives
  Meta WhatsApp Cloud API payloads or legacy Twilio Sandbox form posts and
  calls Salesforce Apex REST endpoint
  `/services/apexrest/logia/v1/twilio/whatsapp`.

The Salesforce endpoint creates a synthetic customer alias, safe evidence,
work item, recommendation, and pending approval. It does not store raw phone
numbers or raw message text.

The live public webhook is proven when the Mule app is deployed to CloudHub and
a WhatsApp provider points its inbound callback to that public URL. The current
CloudHub endpoint has been tested with both Meta-style JSON and Twilio-style
form posts, and it created Salesforce event, evidence, recommendation, and
approval records.

Current deployed demo webhook:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

Use this same URL for Meta WhatsApp Cloud API webhook verification and message
delivery. The name is inherited from the first Twilio bridge, but the deployed
Mule route is provider-neutral. The friendly `/meta/whatsapp/inbound` listener
exists in the Mule app for future CloudHub routing targets; the active public
demo route is the URL above.

Twilio-specific error `63038` is historical context only now. It meant Twilio
blocked a reply because the account reached a rolling daily message limit or an
account-level sending restriction. The active demo path should use official
Meta WhatsApp Cloud API instead.

Voice notes, images, and documents arrive from Meta as typed message payloads.
Logia stores only safe media metadata and a media hash. Transcript,
OCR, or document extraction remains pending evidence until a trusted
transcription or extraction path is available.

## Hospital Profile Demo IDs

These are profile/demo records used by the current hospital story. They are not
the universal core naming pattern. New reusable contracts should prefer the
general ID shapes above.

| Concept           | ID                                   |
| ----------------- | ------------------------------------ |
| Hospital          | `HOSPITAL-LOGIA-PRIVATE-001`         |
| Organization      | `HOSP-LOGIA-PRIVATE`                 |
| Department        | `DEPT-OUTPATIENT-RECEPTION`          |
| Ward              | `WARD-DISCHARGE-002`                 |
| Bed resource      | `RESOURCE-WARD-A3-DISCHARGE-ROOMS`   |
| Queue resource    | `RESOURCE-QUEUE-OUTPATIENT-009`      |
| Pharmacy supply   | `RESOURCE-PHARMACY-IV-KITS`          |
| Lab partner       | `PARTNER-ISLAND-DIAGNOSTICS`         |
| Insurance partner | `PARTNER-INSUREPLUS-001`             |
| Billing process   | `PROCESS-BILLING-INSURANCE-REVIEW`   |
| Complaint cluster | `COMPLAINT-CLUSTER-HOS-003`          |
| Approval          | `approval-logia-hospital-001`        |
| Slack action      | `action-logia-hospital-slack-001`    |
| WhatsApp action   | `action-logia-hospital-whatsapp-001` |
| Correlation       | `CORR-LOGIA-HOSPITAL-SURGE-001`      |

## Protected Actions

These actions require business manager approval before execution:

- `SEND_SLACK_ALERT`
- `SEND_WHATSAPP_ALERT`
- `SEND_VENDOR_EMAIL`
- `CREATE_PATIENT_SERVICE_TASK`
- `REQUEST_BED_CLEANING`
- `CREATE_PHARMACY_RESTOCK_REQUEST`
- `ESCALATE_LAB_VENDOR_CASE`
- `OPEN_BILLING_REVIEW`
- `REQUEST_INSURANCE_FOLLOWUP`
- room, bed, staff-task, pharmacy, supplier, vendor, billing, refund, and
  patient-message write-backs

Agentforce may explain, draft, and request approval. It must not directly
execute protected actions.

## Live Channel Setup

Keep credentials outside Git. Use Windows user environment variables or
Anypoint secure properties. Do not create `.env` files for secrets.

Slack:

```powershell
[Environment]::SetEnvironmentVariable("SLACK_WEBHOOK_URL", "<slack-webhook-url>", "User")
[Environment]::SetEnvironmentVariable("SLACK_SIGNING_SECRET", "<slack-signing-secret>", "User")
[Environment]::SetEnvironmentVariable("SLACK_BOT_TOKEN", "<optional-bot-token>", "User")
[Environment]::SetEnvironmentVariable("SLACK_CHANNEL_ID", "<optional-channel-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_ID_OPERATIONS", "<optional-list-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_CASE", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_PROFILE", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_MODULE", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_PRIORITY", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_STATUS", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_OWNER", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_DUE", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_APPROVAL", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_ACTION", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_EVIDENCE_COUNT", "<optional-column-id>", "User")
[Environment]::SetEnvironmentVariable("SLACK_LIST_COLUMN_OUTCOME", "<optional-column-id>", "User")
$env:SLACK_WEBHOOK_URL = [Environment]::GetEnvironmentVariable("SLACK_WEBHOOK_URL", "User")
$env:SLACK_SIGNING_SECRET = [Environment]::GetEnvironmentVariable("SLACK_SIGNING_SECRET", "User")
$env:SLACK_BOT_TOKEN = [Environment]::GetEnvironmentVariable("SLACK_BOT_TOKEN", "User")
$env:SLACK_CHANNEL_ID = [Environment]::GetEnvironmentVariable("SLACK_CHANNEL_ID", "User")
$env:SLACK_LIST_ID_OPERATIONS = [Environment]::GetEnvironmentVariable("SLACK_LIST_ID_OPERATIONS", "User")
```

`SLACK_WEBHOOK_URL` is enough for approved outbound alerts.
`SLACK_SIGNING_SECRET` is required for real approval buttons and `/logia`
status commands. `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` are optional
enhancements for message updates, threads, and ephemeral replies.
`SLACK_LIST_ID_OPERATIONS` and the `SLACK_LIST_COLUMN_*` values are optional
paid Slack Lists enhancers. If no list ID exists, the runtime can attempt to
create `Logia Operations Queue` and use returned column IDs for that process,
but for a stable rehearsal you should save the list and column IDs outside Git.

Bot-token mode also requires Slack channel access. If `chat.postMessage` returns
`channel_not_found`, invite the app/bot to the channel or reinstall the app with
the required channel scopes. The incoming webhook path is the simpler live demo
path and has already proven outbound delivery.

Slack app URLs to paste:

```text
Interactivity & Shortcuts Request URL:
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound

Slash command /logia Request URL:
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

This is the free route: it uses the deployed CloudHub Mule app. Do not use
Slack Lists as the task database; keep tasks and approvals in Salesforce and
use Lists only as a paid mirror.

Gmail supplier email:

```powershell
[Environment]::SetEnvironmentVariable("GMAIL_CLIENT_ID", "<google-client-id>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_CLIENT_SECRET", "<google-client-secret>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_REFRESH_TOKEN", "<google-refresh-token>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_SENDER_EMAIL", "<manager-demo@gmail.com>", "User")
[Environment]::SetEnvironmentVariable("GMAIL_SUPPLIER_EMAIL", "<supplier-demo@gmail.com>", "User")
.\scripts\configure-cloudhub-logia-secrets.ps1 -TargetOrg hfs-dev
```

The sender Gmail must be the account that authorized the refresh token. If the
manager changes, reconnect Gmail and replace the refresh token. Do not reuse an
old manager's refresh token with a new sender email. Full setup:
[docs/gmail-oauth-cloudhub-runbook.md](gmail-oauth-cloudhub-runbook.md).

WhatsApp through Meta Cloud API:

```powershell
[Environment]::SetEnvironmentVariable("META_WHATSAPP_PHONE_NUMBER_ID", "<phone-number-id>", "User")
[Environment]::SetEnvironmentVariable("META_WHATSAPP_ACCESS_TOKEN", "<access-token>", "User")
[Environment]::SetEnvironmentVariable("META_WHATSAPP_TO", "+<recipient-phone>", "User")
[Environment]::SetEnvironmentVariable("META_GRAPH_VERSION", "v25.0", "User")

$env:META_WHATSAPP_PHONE_NUMBER_ID = [Environment]::GetEnvironmentVariable("META_WHATSAPP_PHONE_NUMBER_ID", "User")
$env:META_WHATSAPP_ACCESS_TOKEN = [Environment]::GetEnvironmentVariable("META_WHATSAPP_ACCESS_TOKEN", "User")
$env:META_WHATSAPP_TO = [Environment]::GetEnvironmentVariable("META_WHATSAPP_TO", "User")
$env:META_GRAPH_VERSION = [Environment]::GetEnvironmentVariable("META_GRAPH_VERSION", "User")
```

WhatsApp through Twilio Sandbox backup:

```powershell
[Environment]::SetEnvironmentVariable("TWILIO_ACCOUNT_SID", "<account-sid>", "User")
[Environment]::SetEnvironmentVariable("TWILIO_AUTH_TOKEN", "<auth-token>", "User")
[Environment]::SetEnvironmentVariable("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886", "User")
[Environment]::SetEnvironmentVariable("TWILIO_WHATSAPP_TO", "whatsapp:<joined-sandbox-number>", "User")

$env:TWILIO_ACCOUNT_SID = [Environment]::GetEnvironmentVariable("TWILIO_ACCOUNT_SID", "User")
$env:TWILIO_AUTH_TOKEN = [Environment]::GetEnvironmentVariable("TWILIO_AUTH_TOKEN", "User")
$env:TWILIO_WHATSAPP_FROM = [Environment]::GetEnvironmentVariable("TWILIO_WHATSAPP_FROM", "User")
$env:TWILIO_WHATSAPP_TO = [Environment]::GetEnvironmentVariable("TWILIO_WHATSAPP_TO", "User")
```

Never commit Twilio recovery codes, Account SID plus Auth Token pairs, Slack
webhook URLs, Slack signing secrets, real phone numbers, or screenshots that
expose secrets.

Use the Twilio section only for historical fallback. The hackathon demo should
use official Meta WhatsApp Cloud API.

## Live Alert Text

Use simple, non-dramatic wording.

Slack title:

```text
Hospital operations update
```

Slack body:

```text
Please check room cleaning, pharmacy stock, lab delay, and billing review. Logia has linked the evidence.
```

WhatsApp title:

```text
Hospital operations update
```

WhatsApp body:

```text
Please check room readiness, pharmacy stock, lab response, and billing review. Logia has linked the evidence.
```

## Channel Test Commands

Use these before demo rehearsal:

```powershell
$env:SLACK_WEBHOOK_URL = [Environment]::GetEnvironmentVariable("SLACK_WEBHOOK_URL", "User")
$env:SLACK_SIGNING_SECRET = [Environment]::GetEnvironmentVariable("SLACK_SIGNING_SECRET", "User")
$env:META_WHATSAPP_PHONE_NUMBER_ID = [Environment]::GetEnvironmentVariable("META_WHATSAPP_PHONE_NUMBER_ID", "User")
$env:META_WHATSAPP_ACCESS_TOKEN = [Environment]::GetEnvironmentVariable("META_WHATSAPP_ACCESS_TOKEN", "User")
$env:META_WHATSAPP_TO = [Environment]::GetEnvironmentVariable("META_WHATSAPP_TO", "User")
$env:META_GRAPH_VERSION = [Environment]::GetEnvironmentVariable("META_GRAPH_VERSION", "User")
npm run check:mulesoft
npm run demo:run -- --target-org hfs-dev --output artifacts\demo-harness-result-live-channels.json
```

What this proves:

- `npm run check:mulesoft` proves the event intake, approved action execution,
  Slack/WhatsApp mocks, signed Slack approval handling, live-provider adapter
  paths, protected vendor email queue, and inbound WhatsApp mapper tests.
- `npm run demo:run` proves the connected Salesforce path, manager approval,
  WhatsApp intake harness proof, Slack approval-gate proof, outbound Slack,
  outbound WhatsApp, protected vendor email queue, actions, outcomes, and
  clinical refusal.

What it does not prove yet:

- full live WhatsApp agent chat; the current Meta response is a receipt
  acknowledgement while the deeper recommendation and approval work is visible
  in Salesforce and Agentforce;
- live WhatsApp voice transcription or document extraction;
- an in-command-center form where a judge types a fresh complaint;
- live Slack button clicks unless the Slack App Interactivity Request URL is
  configured to reach the runtime endpoint.
- live Slack Lists rendering unless the paid workspace, `lists:write` scope,
  list ID, and column IDs are configured.

## Salesforce Org

`hfs-dev` is the local Salesforce CLI alias for the connected demo org. It is
not a Salesforce product name.

The live Agentforce Studio recovery and publish notes are in
`docs/agentforce-publish-recovery.md`. Use that runbook if Builder falls back to
generic Salesforce replies or if `sf agent publish authoring-bundle` fails on
Windows.

The Lightning dashboard is the `Logia` app with the `Logia Command Center` tab.
The direct Lightning path is:

```text
/lightning/n/Logia_Command_Center
```

Useful commands:

```powershell
sf org display --target-org hfs-dev
sf project deploy start --source-dir force-app --target-org hfs-dev --wait 30
sf org assign permset --name HFS_Approver --target-org hfs-dev
sf org open --target-org hfs-dev --path /lightning/n/Logia_Command_Center
npm run demo:reset -- --target-org hfs-dev
npm run demo:seed -- --target-org hfs-dev
npm run demo:run -- --target-org hfs-dev --output artifacts\demo-harness-result-live-channels.json
```

## Success Evidence

The live channel demo is ready when the harness output shows:

- `SEND_SLACK_ALERT.status = SENT`
- `SEND_SLACK_ALERT.provider = slack-webhook`
- `SEND_WHATSAPP_ALERT.status = SENT`
- `SEND_WHATSAPP_ALERT.provider = meta-whatsapp-cloud`
- `SEND_VENDOR_EMAIL.status = SENT` with `provider = gmail-api` when the
  reference runtime sends through Gmail after approval, or
  `SEND_VENDOR_EMAIL.status = QUEUED` with an honest fallback reason when
  credentials or live execution routing are absent
- `workItemStatus = COMPLETED`
- `actionCount >= 11`
- `outcomeCount >= 12`
- `CLINICAL_DECISION_REFUSED`

This proves approved outbound delivery plus local signed approval and WhatsApp
intake harness proof. It does not prove full live WhatsApp agent chat, voice
transcription, or document extraction unless those paths are explicitly tested.

## Remaining Build Tasks

Highest-value tasks still open:

1. Keep the Meta WhatsApp Cloud API webhook callback URL pointed to the active
   CloudHub webhook URL:
   `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound`.
2. Finish same-language Meta WhatsApp receipts and approved replies for
   English, French, and Mauritian Creole.
3. Hassan may use his pretrained multilingual/voice models and DeepSeek for
   WhatsApp language handling, voice transcription, and chat drafting, but only
   behind logical model capabilities and with no secrets, raw media, or
   provider-specific core IDs committed.
4. Add Meta WhatsApp voice-note transcription evidence or a clear
   pending-transcript follow-up path.
5. Add Meta WhatsApp image/document evidence extraction or low-confidence
   follow-up handling.
6. Hassan should build judge-sector WhatsApp/chat use cases for hospital,
   hotel, airport, and banking using the same global primitives.
7. Configure Slack App Interactivity and the `/logia` slash command with the
   verified public Request URL if the live demo should use real Slack clicks:
   `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound`.
8. Rename the live Slack app/bot/channel to `Logia` and `#logia-demo` in the
   Slack UI before the final pitch.
9. Configure live Slack Lists only if the paid workspace, `lists:write` scope,
   list ID, and column IDs are ready. Otherwise use Slack messages/threads plus
   Salesforce command-center tasks.
10. During rehearsal, confirm the live CloudHub approval route returns a
    `gmail-api` message id before claiming supplier email delivery to judges.
11. Use `docs/no-credential-demo-qa-pack.md` during final rehearsal for
    multilingual complaint scripts, fake voice-note transcripts, document/image
    evidence scenarios, expected agent routing, judge-sector mappings, and
    strongest/backup pitch picks.
12. Keep the cross-sector cards aligned with the same global primitives across
    airport, hotel, banking, supermarket, and cruise operations.

## Team Ownership

| Person  | Main area                                                                                                                   |
| ------- | --------------------------------------------------------------------------------------------------------------------------- |
| Fahan   | Final testing and coordination only; no new implementation task in this split                                               |
| Hassan  | Official Meta WhatsApp customer channel, pretrained multilingual/voice models, DeepSeek chat drafts, judge-sector use cases |
| Aarav   | Synthetic data review, no-credential QA scripts, voice/document scenarios, judge mapping                                    |
| Ranveer | Slack approval proof, command-center action trace, resource/capacity/billing workflows                                      |

## Final Warnings

- Do not pitch Logia as a generic chatbot.
- Do not pitch zero-configuration magic. Say: global primitives plus a business
  profile.
- Do not claim clinical decisions.
- Do not claim a channel is live unless the demo output says `SENT`.
- Do not let Agentforce execute protected actions without manager approval.
- Rotate any exposed secret after the demo or immediately if it was shared in
  chat, screenshots, livestreams, or a repository.
