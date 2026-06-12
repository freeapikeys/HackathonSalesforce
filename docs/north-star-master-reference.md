# North Star Master Reference

This is the single quick reference for the hackathon team. It explains what
North Star is, which agents exist, which IDs matter, how live channels are
configured, and how to run the demo.

## Product

North Star is a Salesforce, Agentforce, and MuleSoft operations command center.
It turns messy business signals into evidence-backed recommendations,
manager-approved actions, role-based alerts, and measured outcomes.

The demo profile is a large private hospital. It handles non-clinical
operations only: complaints, room readiness, queues, staff tasks, pharmacy
stock, lab/vendor delays, billing/insurance issues, alerts, approvals, and
outcomes.

North Star must not make diagnosis, treatment, dosage, triage, or clinical
priority decisions.

North Star is general first. Hospital is the flagship demo profile, not the
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
| `Recommendation` | Evidence-backed plan proposed by North Star                                |
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

North Star should feel like one coordinated product, not separate chatbots.
Agents can be Agentforce topics, prompt profiles, deterministic modules, or
action contracts.

North Star has 10 core agents in the MVP.

| Agent                       | Role                                                                           |
| --------------------------- | ------------------------------------------------------------------------------ |
| North Star Orchestrator     | Combines all specialist findings into one manager-ready plan                   |
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
| North Star Orchestrator     | route issue type, merge findings, resolve conflicts, set approval path, explain plan        |
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

| ID      | Module                           | Primary agent           |
| ------- | -------------------------------- | ----------------------- |
| `NS-01` | Complaint and trust              | Customer Trust          |
| `NS-02` | Capacity and availability        | Resource and Capacity   |
| `NS-03` | Staff coordination               | Operations Execution    |
| `NS-04` | Partner and vendor failure       | Partner and Vendor      |
| `NS-05` | Inventory and supply             | Resource and Capacity   |
| `NS-06` | Billing and financial exposure   | Financial Impact        |
| `NS-07` | Risk, safety, and compliance     | Risk and Approval       |
| `NS-08` | Communication and escalation     | Communication           |
| `NS-09` | Disruption handling              | North Star Orchestrator |
| `NS-10` | Outcome learning                 | Outcome Learning        |
| `NS-11` | Evidence quality and uncertainty | Evidence and Context    |
| `NS-12` | Policy and approval routing      | Risk and Approval       |

## Demo Story

A hospital morning gets messy at the same time:

- patient complaints are increasing;
- discharge rooms are blocked;
- outpatient queues are rising;
- pharmacy stock is low;
- lab response is delayed;
- billing and insurance reviews are stuck.

North Star turns this into one operations plan with evidence, approval,
protected actions, Slack and WhatsApp alerts, and outcome metrics.

## Signal Intake And Channel Roles

North Star has two different channel directions. Do not mix them in the pitch.

Inbound signal channels create `Signal` and `Evidence` records. They do not
execute actions.

Outbound action channels execute approved `Action` records. They require a
business manager approval unless the demo clearly marks them as local mocks.

| Channel                     | Best use                                                 | Current demo state                                                         |
| --------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------- |
| WhatsApp inbound            | Customer, patient, visitor, or client complaint intake   | CloudHub Mule endpoint supports Twilio Sandbox and Meta Cloud API payloads |
| Salesforce command center   | Manager review, approval, command-center visibility      | Active platform surface                                                    |
| Salesforce/manual demo form | Optional fallback for staff-entered signals              | Not a core build item for the hackathon v1                                 |
| Slack                       | Internal staff and manager coordination                  | Live outbound delivery works when webhook is configured                    |
| WhatsApp outbound           | Urgent mobile alert or approved customer acknowledgement | Live outbound delivery works through Twilio Sandbox                        |
| Email                       | Supplier, vendor, insurer, or formal customer follow-up  | Protected mock action exists; live delivery is not configured              |

Recommended hackathon stance:

- WhatsApp should be the customer-facing intake story.
- Slack should be the internal worker and manager coordination story.
- Slack approve/reject buttons should be the manager approval story when the
  Slack App interactivity Request URL is configured.
- WhatsApp outbound may be used for urgent internal mobile alerts in the demo.
- Customer-facing WhatsApp replies should be approved, privacy-safe, and
  template/consent-aware.
- Email is useful for suppliers, insurers, vendors, or formal follow-up. The
  current repo has a protected mock vendor-email action; do not claim live
  email delivery until credentials and Anypoint/SMTP delivery are configured.

## End-To-End Logic

Use this as the judge explanation for "how does a complaint actually enter and
become action?"

1. A customer, patient, visitor, staff member, or system sends a signal.
   Examples: WhatsApp complaint, command-center review note, queue spike, low
   stock event, lab delay, billing issue, or room readiness issue.
2. MuleSoft or Salesforce writes the signal as source-backed evidence.
   North Star stores the message, timestamp, source channel, synthetic alias,
   affected department, resource, partner, and correlation ID.
3. Evidence and Context normalizes the signal into global primitives.
   The same model can handle a hospital bed, hotel room, airport gate, bank
   case, supermarket batch, or cruise cabin as a typed `Resource`.
4. The Orchestrator asks specialist agents for findings.
   Customer Trust classifies the complaint. Resource and Capacity checks rooms,
   queues, stock, equipment, and staff. Partner and Vendor checks external
   delays. Financial Impact checks billing, refund, claim, and payment exposure.
   Risk and Approval checks policy and clinical boundaries.
5. North Star drafts one action plan.
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
   North Star records what was attempted, what happened, which provider accepted
   the message, which tasks were acknowledged, and which metrics changed.

## Deep Resolution Pattern

This is the main competitive differentiator. North Star should not behave like
a chatbot that says "sorry" or "manager notified." It should expand one issue
into the business functions it affects.

For every complaint or operational signal, North Star should:

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

North Star should not only send a message. It should connect:

- Customer Trust: wait-time and billing frustration;
- Resource and Capacity: outpatient queue and pharmacy stock;
- Financial Impact: possible duplicate invoice or insurer delay;
- Risk and Approval: no refund or customer reply without approval;
- Communication: Slack internal alert and approved WhatsApp response;
- Outcome Learning: wait reduced, stockout avoided, billing review opened.

The current repo includes two intake paths for this pattern:

- local harness/runtime proof through `MockIntegrationApi.ingest_twilio_whatsapp`;
- deployable Mule app `mulesoft/north-star-twilio-webhook` that receives
  Twilio Sandbox form posts and calls Salesforce Apex REST endpoint
  `/services/apexrest/northstar/v1/twilio/whatsapp`.

The Salesforce endpoint creates a synthetic customer alias, safe evidence,
work item, recommendation, and pending approval. It does not store raw phone
numbers or raw message text.

The live public webhook is proven when the Mule app is deployed to CloudHub and
Twilio Sandbox points "When a message comes in" to that public URL. The current
CloudHub endpoint has been tested with a synthetic Twilio-style form post and
created Salesforce event, evidence, recommendation, and approval records.

Current deployed demo webhook:

```text
https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound
```

If Twilio receives the inbound message but the WhatsApp user sees no reply,
check the latest Twilio outbound-reply status. Error `63038` means Twilio
blocked the reply because the account reached a rolling daily message limit or
an account-level sending restriction. That is an account/provider limit, not a
North Star webhook failure.

Voice notes, images, and documents arrive from Twilio as media fields such as
`MediaUrl0` and `MediaContentType0`. North Star stores only safe media metadata
and a media URL hash. Transcript or document extraction remains pending
evidence until a trusted transcription or extraction path is available.

## Hospital Profile Demo IDs

These are profile/demo records used by the current hospital story. They are not
the universal core naming pattern. New reusable contracts should prefer the
general ID shapes above.

| Concept           | ID                                        |
| ----------------- | ----------------------------------------- |
| Hospital          | `HOSPITAL-NORTH-STAR-PRIVATE-001`         |
| Organization      | `HOSP-NORTH-STAR-PRIVATE`                 |
| Department        | `DEPT-OUTPATIENT-RECEPTION`               |
| Ward              | `WARD-DISCHARGE-002`                      |
| Bed resource      | `RESOURCE-WARD-A3-DISCHARGE-ROOMS`        |
| Queue resource    | `RESOURCE-QUEUE-OUTPATIENT-009`           |
| Pharmacy supply   | `RESOURCE-PHARMACY-IV-KITS`               |
| Lab partner       | `PARTNER-ISLAND-DIAGNOSTICS`              |
| Insurance partner | `PARTNER-INSUREPLUS-001`                  |
| Billing process   | `PROCESS-BILLING-INSURANCE-REVIEW`        |
| Complaint cluster | `COMPLAINT-CLUSTER-HOS-003`               |
| Approval          | `approval-north-star-hospital-001`        |
| Slack action      | `action-north-star-hospital-slack-001`    |
| WhatsApp action   | `action-north-star-hospital-whatsapp-001` |
| Correlation       | `CORR-NORTH-STAR-HOSPITAL-SURGE-001`      |

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
$env:SLACK_WEBHOOK_URL = [Environment]::GetEnvironmentVariable("SLACK_WEBHOOK_URL", "User")
$env:SLACK_SIGNING_SECRET = [Environment]::GetEnvironmentVariable("SLACK_SIGNING_SECRET", "User")
```

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

## Live Alert Text

Use simple, non-dramatic wording.

Slack title:

```text
Hospital operations update
```

Slack body:

```text
Please check room cleaning, pharmacy stock, lab delay, and billing review. North Star has linked the evidence.
```

WhatsApp title:

```text
Hospital operations update
```

WhatsApp body:

```text
Please check room readiness, pharmacy stock, lab response, and billing review. North Star has linked the evidence.
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
$env:TWILIO_ACCOUNT_SID = [Environment]::GetEnvironmentVariable("TWILIO_ACCOUNT_SID", "User")
$env:TWILIO_AUTH_TOKEN = [Environment]::GetEnvironmentVariable("TWILIO_AUTH_TOKEN", "User")
$env:TWILIO_WHATSAPP_FROM = [Environment]::GetEnvironmentVariable("TWILIO_WHATSAPP_FROM", "User")
$env:TWILIO_WHATSAPP_TO = [Environment]::GetEnvironmentVariable("TWILIO_WHATSAPP_TO", "User")

npm run check:mulesoft
npm run demo:run -- --target-org hfs-dev --output artifacts\demo-harness-result-live-channels.json
```

What this proves:

- `npm run check:mulesoft` proves the event intake, approved action execution,
  Slack/WhatsApp mocks, signed Slack approval handling, live-provider adapter
  paths, protected vendor email queue, and inbound WhatsApp mapper tests.
- `npm run demo:run` proves the connected Salesforce path, manager approval,
  Twilio intake harness proof, Slack approval-gate proof, outbound Slack,
  outbound WhatsApp, protected vendor email queue, actions, outcomes, and
  clinical refusal.

What it does not prove yet:

- a live WhatsApp customer message reaching Salesforce through Twilio, unless
  Twilio Sandbox has been pointed to the deployed CloudHub webhook URL;
- an in-command-center form where a judge types a fresh complaint;
- live Slack button clicks unless the Slack App Interactivity Request URL is
  configured to reach the runtime endpoint.

## Salesforce Org

`hfs-dev` is the local Salesforce CLI alias for the connected demo org. It is
not a Salesforce product name.

The live Agentforce Studio recovery and publish notes are in
`docs/agentforce-publish-recovery.md`. Use that runbook if Builder falls back to
generic Salesforce replies or if `sf agent publish authoring-bundle` fails on
Windows.

Useful commands:

```powershell
sf org display --target-org hfs-dev
sf project deploy start --source-dir force-app --target-org hfs-dev --wait 30
npm run demo:reset -- --target-org hfs-dev
npm run demo:seed -- --target-org hfs-dev
npm run demo:run -- --target-org hfs-dev --output artifacts\demo-harness-result-live-channels.json
```

## Success Evidence

The live channel demo is ready when the harness output shows:

- `SEND_SLACK_ALERT.status = SENT`
- `SEND_SLACK_ALERT.provider = slack-webhook`
- `SEND_WHATSAPP_ALERT.status = SENT`
- `SEND_WHATSAPP_ALERT.provider = twilio-whatsapp`
- `SEND_VENDOR_EMAIL.status = QUEUED`
- `workItemStatus = COMPLETED`
- `actionCount >= 11`
- `outcomeCount >= 12`
- `CLINICAL_DECISION_REFUSED`

This proves approved outbound delivery plus local signed approval and Twilio
intake harness proof. It does not prove a public Twilio webhook receiving live
customer messages unless that Request URL has also been hosted and tested.

## Remaining Build Tasks

Highest-value tasks still open:

1. Point Meta WhatsApp Cloud API webhook callback URL to the CloudHub webhook
   URL:
   `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/meta/whatsapp/inbound`.
2. Configure Slack App Interactivity with a public Request URL if the live demo
   should use real Slack button clicks; otherwise use the signed harness proof
   and Salesforce command-center approval fallback.
3. Add live email/vendor delivery only if credentials and Anypoint/SMTP routing
   are configured safely; the repo currently has protected mock vendor email.
4. Add cross-sector cards showing how the same global primitives map to
   airport, hotel, banking, supermarket, and cruise operations.

## Team Ownership

| Person  | Main area                                          |
| ------- | -------------------------------------------------- |
| Fahan   | Slack, channel setup, demo run, final coordination |
| Hassan  | WhatsApp and voice mode                            |
| Aarav   | Synthetic hospital data                            |
| Ranveer | Agentforce/resource/capacity reasoning             |

## Final Warnings

- Do not pitch North Star as a generic chatbot.
- Do not pitch zero-configuration magic. Say: global primitives plus a business
  profile.
- Do not claim clinical decisions.
- Do not claim a channel is live unless the demo output says `SENT`.
- Do not let Agentforce execute protected actions without manager approval.
- Rotate any exposed secret after the demo or immediately if it was shared in
  chat, screenshots, livestreams, or a repository.
