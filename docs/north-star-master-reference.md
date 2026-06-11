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

## Agent System

North Star should feel like one coordinated product, not separate chatbots.
Agents can be Agentforce topics, prompt profiles, deterministic modules, or
action contracts.

North Star has 10 core agents in the MVP.

| Agent                       | Role                                                                           |
| --------------------------- | ------------------------------------------------------------------------------ |
| North Star Orchestrator     | Combines all specialist findings into one manager-ready plan                   |
| Evidence and Context Agent  | Normalizes signals, links evidence, detects missing or conflicting facts       |
| Patient Trust Agent         | Classifies complaints and drafts safe manager-approved messages                |
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
| Patient Trust Agent         | classify complaints, detect clusters, draft privacy-safe service response text              |
| Resource and Capacity Agent | calculate queue pressure, bed/room availability, stock days remaining, staff gap            |
| Operations Execution Agent  | create tasks, assign role owners, set due windows, track acknowledgement                    |
| Partner and Vendor Agent    | check lab/laundry/insurer/payment/food/maintenance status and SLA risk                      |
| Risk and Approval Agent     | decide approval need, enforce permission, refuse clinical decisions, preserve audit         |
| Financial Impact Agent      | estimate refund, billing, claim, voucher, payment, and revenue exposure                     |
| Communication Agent         | prepare Slack, WhatsApp, and future email messages after approval                           |
| Outcome Learning Agent      | capture outcomes, compare expected vs actual, feed learning into next plan                  |

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
| `NS-01` | Complaint and trust              | Patient Trust           |
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

| Channel                     | Best use                                                        | Current demo state                                            |
| --------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------- |
| WhatsApp inbound            | Customer, patient, visitor, or client complaint intake          | Target flow; use Twilio Sandbox or seeded fixture as fallback |
| Salesforce command center   | Manager review, approval, command-center visibility             | Active platform surface                                       |
| Salesforce/manual demo form | Reliable fallback for entering a complaint or operations signal | Target fallback screen or seeded event                        |
| Slack                       | Internal staff and manager coordination                         | Live outbound delivery works when webhook is configured       |
| WhatsApp outbound           | Urgent mobile alert or approved customer acknowledgement        | Live outbound delivery works through Twilio Sandbox           |
| Email                       | Supplier, vendor, insurer, or formal customer follow-up         | Future protected action; not implemented in current MVP       |

Recommended hackathon stance:

- WhatsApp should be the customer-facing intake story.
- Slack should be the internal worker and manager coordination story.
- WhatsApp outbound may be used for urgent internal mobile alerts in the demo.
- Customer-facing WhatsApp replies should be approved, privacy-safe, and
  template/consent-aware.
- Email is useful for suppliers, insurers, vendors, or formal follow-up, but it
  should be described as the next protected action adapter unless implemented.

## End-To-End Logic

Use this as the judge explanation for "how does a complaint actually enter and
become action?"

1. A customer, patient, visitor, staff member, or system sends a signal.
   Examples: WhatsApp complaint, Salesforce intake form, queue spike, low stock
   event, lab delay, billing issue, or room readiness issue.
2. MuleSoft or Salesforce writes the signal as source-backed evidence.
   North Star stores the message, timestamp, source channel, synthetic alias,
   affected department, resource, partner, and correlation ID.
3. Evidence and Context normalizes the signal into global primitives.
   The same model can handle a hospital bed, hotel room, airport gate, bank
   case, supermarket batch, or cruise cabin as a typed `Resource`.
4. The Orchestrator asks specialist agents for findings.
   Patient Trust classifies the complaint. Resource and Capacity checks rooms,
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
   future email/vendor action.
8. Outcomes return to Salesforce.
   North Star records what was attempted, what happened, which provider accepted
   the message, which tasks were acknowledged, and which metrics changed.

## Key Demo IDs

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
$env:SLACK_WEBHOOK_URL = [Environment]::GetEnvironmentVariable("SLACK_WEBHOOK_URL", "User")
```

WhatsApp through Twilio Sandbox:

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
webhook URLs, real phone numbers, or screenshots that expose secrets.

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

## Salesforce Org

`hfs-dev` is the local Salesforce CLI alias for the connected demo org. It is
not a Salesforce product name.

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
- `workItemStatus = COMPLETED`
- `actionCount = 10`
- `outcomeCount = 11`
- `CLINICAL_DECISION_REFUSED`

This proves approved outbound delivery. It does not prove live inbound customer
complaint intake unless the Twilio inbound webhook or Salesforce intake fallback
has also been implemented and tested.

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
