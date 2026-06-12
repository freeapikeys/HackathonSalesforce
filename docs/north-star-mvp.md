# North Star MVP

## Product Position

North Star is an Agentforce-powered operations command center for organizations
that need to resolve messy, cross-functional issues quickly. It uses one global
operating model and one business profile at a time. The hackathon demo profile
is a large private hospital.

The product is general first. Hospital is not the architecture; it is the
flagship demo profile. Core names, IDs, primitives, agents, skills, and action
contracts stay sector-neutral. Hospital words such as patient, bed, pharmacy,
ward, and lab appear only in the hospital profile, demo data, or display labels.

North Star is not a generic chatbot. It is a governed multi-agent system that
turns one operational signal into:

1. source-backed evidence;
2. facts separated from inference;
3. multi-function impact analysis;
4. manager-approved actions;
5. Slack and WhatsApp-style coordination;
6. outcome tracking.

## Global Operating Model

The core model uses reusable primitives:

| Primitive        | Meaning                                                                    |
| ---------------- | -------------------------------------------------------------------------- |
| `Signal`         | The event, complaint, alert, request, or anomaly that starts the work      |
| `Evidence`       | Source record, message, fixture, timestamp, or system fact                 |
| `Entity`         | Organization, department, person role, supplier, vendor, or account        |
| `Resource`       | Bed, room, stock item, equipment, account, gate, batch, or service slot    |
| `Location`       | Ward, counter, branch, terminal, store, room, or service area              |
| `Actor`          | User, manager, agent, vendor, staff role, or system actor                  |
| `Customer`       | Patient, guest, passenger, shopper, client, or visitor                     |
| `Partner`        | Lab, laundry, insurer, payment processor, supplier, airline, or vendor     |
| `Process`        | Admission, discharge, billing, restock, complaint, approval, or escalation |
| `Risk`           | Capacity, safety, financial, service, compliance, reputation, or SLA risk  |
| `Policy`         | Approval, permission, threshold, compliance, or escalation rule            |
| `Recommendation` | Evidence-backed plan proposed by North Star                                |
| `Approval`       | Human business approval before protected action execution                  |
| `Action`         | Task, alert, vendor request, billing review, stock request, or callback    |
| `Outcome`        | Result after action execution                                              |
| `Metric`         | Wait time, stock risk, cost exposure, SLA, completion, or complaint change |

Business-specific details are typed values on these primitives, not separate
architecture. A hospital bed, hotel room, airport gate, bank account,
supermarket batch, and cruise cabin are all `Resource` records with different
types, policies, and actions.

Core ID examples:

| ID type  | General examples                                                                                                                    |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Profile  | `profile:hospital-private-large`, `profile:airport-operations`, `profile:hotel-guest-operations`, `profile:bank-service-operations` |
| Resource | `resource:room`, `resource:stock-item`, `resource:service-counter`                                                                  |
| Action   | `action:send-internal-alert`, `action:create-service-task`, `action:request-partner-followup`                                       |

Profile mapping examples:

| Universal issue    | Hospital profile                | Hotel profile             | Airport profile                 | Banking profile                    |
| ------------------ | ------------------------------- | ------------------------- | ------------------------------- | ---------------------------------- |
| Room readiness     | Discharge room readiness        | Guest room readiness      | Gate readiness                  | Service room or case readiness     |
| Stock risk         | Pharmacy stock risk             | Linen or food stock risk  | Equipment stock risk            | Card, cash, or document stock risk |
| Duplicate charge   | Billing duplicate               | Guest overcharge          | Passenger fee dispute           | Bank dispute                       |
| Customer complaint | Patient or visitor complaint    | Guest complaint           | Passenger complaint             | Client complaint                   |
| Partner delay      | Lab, insurer, or supplier delay | Laundry or supplier delay | Airline or ground handler delay | Processor or insurer delay         |

## Signal Intake And Channel Roles

North Star should not be pitched as "the user talks to a chatbot and the bot
magically fixes everything." The winning flow is a governed operations loop:
signals enter, evidence is stored, agents reason, managers approve, actions
execute, and outcomes are measured.

Inbound channels create `Signal` and `Evidence`:

| Channel                   | Primary role                                                              |
| ------------------------- | ------------------------------------------------------------------------- |
| Twilio WhatsApp inbound   | Customer, guest, passenger, patient, visitor, or client complaint intake  |
| Salesforce command center | Staff review, approval, audit, and fallback visibility                    |
| System event              | Queue spike, stock threshold, vendor delay, payment issue, or room status |
| Voice/manual transcript   | Staff or customer voice note that becomes governed evidence               |
| Document/image intake     | Uploaded proof, invoice, photo, note, or partner file as evidence         |

Outbound channels execute approved `Action` records:

| Channel           | Primary role                                                                |
| ----------------- | --------------------------------------------------------------------------- |
| Slack             | Internal worker and manager coordination                                    |
| WhatsApp outbound | Urgent mobile alert or approved customer acknowledgement                    |
| Email             | Future supplier, insurer, vendor, or formal customer follow-up adapter      |
| Salesforce tasks  | Role-owned work for cleaning, porter, pharmacy, billing, vendor, and review |

For the hospital demo, Meta WhatsApp Cloud API is the preferred customer-facing
intake story when the app, phone number, test recipient, token, and webhook are
ready. Twilio Sandbox remains the backup. Slack is the internal team
coordination and approval story. WhatsApp outbound should be used carefully:
internal urgent alerts are safe for the demo, while customer-facing replies need
approval, privacy-safe text, template/consent handling, and no clinical advice.

## Winning Demo Story

A large private hospital starts the morning with several connected problems:

- patient complaints are increasing around waiting time, billing, and room
  readiness;
- discharge rooms are blocked because cleaning and porter tasks are delayed;
- pharmacy stock for a common supply is low before the afternoon rush;
- a lab partner response is late, which affects the service response;
- insurance and billing approvals are stuck for several cases;
- the operations manager needs one coordinated action plan before queues get
  worse.

A weak assistant says "notify the manager." North Star does more:

1. detects whether complaints are isolated, clustered, capacity-driven, billing
   driven, vendor-driven, or safety-sensitive;
2. checks beds, rooms, queues, staff roles, pharmacy stock, vendor status, and
   approval state;
3. separates facts from inference and names missing evidence;
4. creates an action plan across customer trust, capacity, operations, vendor,
   billing, risk, and communications;
5. refuses diagnosis, treatment, dosage, or clinical priority decisions;
6. requires business approval before protected actions;
7. executes approved MuleSoft mock actions and records outcomes.

## Agents

North Star should feel like one coordinated product, not ten disconnected
chatbots.

### North Star Orchestrator Topic

Owns the final decision trace. It expands one issue across all affected
business functions, resolves tradeoffs, and produces one action plan.

Responsibilities:

- decide whether a case is mainly complaint, capacity, vendor, billing, risk,
  communication, inventory, or mixed;
- combine facts from specialist agents;
- identify conflicts such as "move patients faster" versus "room cleaning is
  not complete";
- define which actions need approval;
- log assumptions, confidence, missing evidence, actions, and outcomes.

### Evidence And Context Agent

Owns grounding.

Responsibilities:

- normalize messy signals from complaints, fixtures, Salesforce records, and
  MuleSoft callbacks;
- link evidence IDs to affected patients, departments, resources, vendors,
  approvals, and outcomes;
- detect missing or contradictory evidence;
- keep source facts separate from claims and inference.

### Customer Trust Agent

Owns customer trust without making sector-specific final decisions. In the
hospital profile, this displays as patient and visitor trust.

Responsibilities:

- classify complaints into waiting time, room readiness, food, billing,
  discharge delay, staff interaction, lost item, pharmacy delay, accessibility,
  safety, privacy, or service response;
- detect repeated complaint clusters;
- draft manager-approved messages;
- recommend service response actions that require approval when consequential.

### Resource And Capacity Agent

Owns availability and pressure.

Responsibilities:

- evaluate beds, rooms, pharmacy stock, staff capacity, service counters,
  equipment, queue pressure, and appointment slots;
- calculate capacity pressure, stock days remaining, and SLA risk;
- recommend task, transfer, restock, or escalation options;
- name missing evidence when data is incomplete.

### Operations Execution Agent

Owns tasking.

Responsibilities:

- create room-cleaning, porter, pharmacy, billing, front-desk, vendor-follow-up,
  and manager-review tasks;
- assign owners by role;
- track acknowledgement and completion;
- escalate missed tasks before the service window is lost.

### Partner And Vendor Agent

Owns external dependency follow-up.

Responsibilities:

- track lab, laundry, food, insurance, payment, maintenance, and transport
  partner status;
- request vendor response or corrective action;
- preserve SLA evidence;
- update recommendations when partner evidence changes.

### Risk And Approval Agent

Owns boundaries.

Responsibilities:

- require manager approval for protected actions;
- refuse clinical decisions and unsafe actions;
- enforce permission and purpose restrictions;
- preserve audit trail.

### Financial Impact Agent

Owns cost and revenue exposure.

Responsibilities:

- estimate refund, claim, voucher, billing, SLA, and revenue-risk impact;
- flag duplicate billing, stuck insurance approval, or compensation threshold;
- route financial actions through approval.

### Communication Agent

Owns approved outreach.

Responsibilities:

- draft internal Slack and WhatsApp-style alerts;
- route messages to role aliases, not personal contact data;
- keep message content operational and privacy-safe;
- return honest `SENT`, `FAILED`, `DENIED`, or `MOCK_SENT` status.

### Outcome Learning Agent

Owns closure.

Responsibilities:

- record wait time reduced, bed released, stockout avoided, complaint
  contained, vendor SLA updated, billing issue resolved, and task completion;
- compare expected outcome against actual outcome;
- preserve correlation IDs and evidence IDs.

## Demo Phases

1. **Trigger:** a hospital operations surge starts from complaints and capacity
   signals.
2. **Context:** show department, resource, complaint, vendor, queue, billing,
   approval, and stock evidence.
3. **Conflict:** customer trust wants a fast response, capacity shows blocked
   rooms, pharmacy stock is low, and billing approvals are stuck.
4. **Partner response:** lab, insurance, laundry, or pharmacy partner evidence
   changes the recommendation.
5. **Recommendation:** Agentforce proposes one action plan with cited facts,
   inferences, missing evidence, blocked clinical actions, and approval needs.
6. **Approval:** operations manager approves protected actions.
7. **Action:** MuleSoft mock executes approved tasks, vendor follow-up, Slack
   alert, WhatsApp-style alert, and outcome callback.
8. **Outcome:** command center updates with wait-time, bed, stock, complaint,
   billing, vendor, and task metrics.

## Demo Data

Use synthetic data only. No real patient names, phone numbers, emails, medical
records, diagnoses, or treatment details.

| Area                 | Example risk                                                |
| -------------------- | ----------------------------------------------------------- |
| Outpatient reception | queue spike, long wait complaints, staffing gap             |
| Inpatient rooms      | bed blocked, discharge cleaning delay, room complaint       |
| Pharmacy             | supply running low, stock transfer or restock needed        |
| Laboratory           | vendor response delay, result-status communication issue    |
| Billing              | duplicate invoice, insurance approval stuck, refund request |
| Food and hospitality | meal complaint, allergy-safe service escalation             |
| Facilities           | wheelchair, lift, HVAC, cleaning, or maintenance delay      |
| Partner operations   | laundry, lab, insurer, payment, food, or maintenance SLA    |

## Non-Goals

- Do not claim diagnosis, treatment, dosage, or clinical triage capability.
- Do not claim real hospital, patient, insurer, WhatsApp, Slack, or vendor
  production integrations unless configured and demonstrated.
- Do not claim live WhatsApp customer intake until the Mule webhook app is
  deployed, Twilio points to it, and a real sandbox message creates Salesforce
  records. Do not claim live email delivery until an email adapter exists and
  has been tested.
- Do not claim machine-learning forecasting if the prototype uses deterministic
  rules. Say "rules-based baseline with model-ready architecture."
- Do not let Agentforce execute protected external actions directly.
- Do not hard-code one department, one supply item, one vendor, or one patient
  scenario into the architecture.
- Do not hide uncertainty behind one unexplained score.

## Success Criteria

The demo succeeds when judges see:

- messy hospital operations signals becoming one coordinated plan;
- universal primitives that can map to hotel, airport, banking, retail, and
  hospital operations;
- Agentforce changing its recommendation after partner or capacity evidence
  arrives;
- clinical decision requests refused or routed to human clinicians;
- manager approval gating consequential changes;
- a customer complaint entering through Twilio Sandbox WhatsApp, then becoming
  evidence and an action plan visible in Salesforce;
- Slack alerts reaching internal roles, plus WhatsApp alerts or honest mock
  channel evidence;
- Salesforce records preserving evidence, tasks, approvals, actions, and
  outcomes.
