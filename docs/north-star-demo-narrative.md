# North Star Demo Narrative

## Product Pitch

North Star is a Salesforce and Agentforce command center that turns messy
business operations signals into one manager-approved action plan. The demo
uses a large private hospital, but the architecture is global: the same
primitives can map to hotel rooms, airport gates, bank cases, supermarket
batches, cruise cabins, and hospital beds.

## Three-Minute Judge Demo

The demo opens with a morning operations surge at a private hospital. The
signal can start from an official Meta WhatsApp patient complaint or a system
event. The Salesforce command center is the visibility, audit, and fallback
approval surface. It shows rising patient
complaints, blocked discharge rooms, a growing outpatient queue, pharmacy stock
pressure, delayed lab response, and stuck billing/insurance approvals.

North Star reveals the conflict. The Customer Trust Agent sees a complaint
cluster around waiting time, room readiness, and billing confusion. The Resource
and Capacity Agent shows blocked beds, staff coverage gaps, and low stock days
remaining for a pharmacy item. The Partner and Vendor Agent shows a delayed lab
response. The Financial Impact Agent flags billing and insurance exposure. The
Risk and Approval Agent blocks any clinical-decision request and requires
manager approval for protected operational actions.

The orchestrator combines these findings into one action plan. It separates
facts from inferences, names missing evidence, refuses diagnosis or triage, and
proposes operational action: release cleaned beds, assign porter tasks,
request pharmacy restock, open billing review, escalate the lab partner, and
prepare approved internal alerts.

The operations manager approves consequential actions through Slack approval or
the command-center fallback. The live harness executes approved Slack,
WhatsApp, and protected vendor-email MuleSoft channel actions and captures the
resulting Salesforce outcomes. The broader action
plan names the service task, bed-cleaning request, vendor escalation, billing
review, pharmacy restock, and outcome metrics that the mocked action catalog
supports. The final view shows wait time reduced, beds released, stockout
avoided, complaint risk contained, billing issue routed, vendor SLA preserved,
and staff tasks acknowledged.

## Five-Minute Extended Demo

The extended version starts by showing that North Star is profile-driven, not
hospital-only. The same global primitives model:

- hospital bed as `Resource`;
- hotel room as `Resource`;
- airport gate as `Resource`;
- bank case or account as `Resource`;
- supermarket batch as `Resource`.

The presenter launches the hospital operations surge event and pauses on the
risk pulse. The complaint, capacity, pharmacy stock, vendor, billing, approval,
and outcome cards make the mixed incident visible without requiring the judge to
read raw logs. The evidence timeline cites complaint records, queue and bed
capacity, pharmacy stock, lab response, billing approval, staffing baseline,
and prior outcome evidence.

Next, the presenter asks Agentforce for the recommendation. The specialist
agents disagree in useful ways: customer trust wants a fast response, capacity
shows blocked rooms, partner evidence shows a lab delay, and financial evidence
shows billing exposure. The orchestrator explains which statements are source
facts, which are inferences, what is missing, and what needs approval.

The partner response arrives and changes the recommendation. Instead of
blindly escalating every partner case, North Star narrows action to the affected
lab and billing issues, creates tasks for the operations team, and keeps
clinical judgment out of scope. The manager approves the protected actions,
rejects or defers unsafe actions, and executes only the approved internal
workflow.

Finally, the command center shows channel results and outcomes. Slack and
WhatsApp-style alerts are clearly marked as mock delivery unless credentials
are configured. The audit trail keeps correlation IDs, approval IDs, action
IDs, evidence IDs, and outcome IDs so the team can explain exactly what was
executed and why.

## Judge Pitch Deck Outline

Use this outline as the source for the final slides. The pitch should stay
close to the live demo instead of promising a broad platform that the prototype
does not prove.

### Slide 1: Problem

Every sector has operational issues that begin as one signal but quickly touch
complaints, capacity, partners, staff work, billing, approvals, communication,
and outcomes. A hospital morning surge makes that visible in one story:
patients are complaining, rooms are blocked, the queue is rising, pharmacy
stock is low, a lab partner is late, and billing approvals are stuck.

Judge bridge:

| Judge sector | Same pattern they will recognize                                         |
| ------------ | ------------------------------------------------------------------------ |
| Hotel        | Guest complaint expands into room readiness, housekeeping, food, billing |
| Airport      | Flight disruption expands into gates, baggage, vendors, staff, messages  |
| Banking      | Dispute or claim expands into risk, compliance, approvals, communication |
| Supermarket  | Product complaint expands into batch, stock, supplier, waste, customer   |

### Slide 2: Agent System

Do not pitch "lots of bots." Pitch one governed North Star command center:

- the Orchestrator turns one messy signal into one action plan;
- global primitives make the plan reusable across industries;
- specialist agents contribute evidence, trust, capacity, vendor, financial,
  execution, communication, risk, and outcome views;
- the output separates facts, inferences, missing evidence, recommendations,
  blocked actions, approvals, and expected outcomes.

### Slide 3: Salesforce, Agentforce, And MuleSoft

The system boundary is the strongest part of the story:

- Salesforce stores the source-backed case, evidence, recommendation,
  approval, action, outcome, and evaluation records;
- Agentforce drafts and explains the action plan, but does not execute
  protected actions;
- MuleSoft executes only approved actions and returns delivery or mock
  evidence;
- the command center shows the approval boundary, channel results, outcome
  metrics, and clinical refusal.

### Slide 4: Live Demo Flow

Show the exact flow the repo can run:

1. start with one Meta WhatsApp/customer complaint or hospital
   operations surge event;
2. show global primitive context and conflicting evidence;
3. ask Agentforce for the action recommendation;
4. show the clinical-decision request refused;
5. approve protected operational actions as a business manager;
6. execute approved Slack internal alerts and WhatsApp mobile/customer-safe
   alerts;
7. capture outcomes and evaluations in Salesforce;
8. refresh the command center with channel, audit, and outcome evidence.

### Slide 5: Business Value

Quantify the demo with operational metrics, not vague AI language:

| Value area            | Demo proof point                                                      |
| --------------------- | --------------------------------------------------------------------- |
| Wait time             | Outpatient queue is 34 waiting, target below 18 by service window     |
| Bed capacity          | 7 discharge rooms are blocked; action plan targets room release       |
| Stockout prevention   | Pharmacy supply is below threshold before the afternoon rush          |
| Complaint containment | 11 synthetic complaints are clustered and tied to approved actions    |
| Financial risk        | Billing, insurer, voucher, payment, and revenue-risk cases are gated  |
| Partner SLA           | Lab delay is preserved, escalated, then updated when response changes |
| Staff execution       | Tasks have role owners, due windows, acknowledgement, and escalation  |

### Slide 6: Plug-And-Play Mapping

Do not claim zero-configuration. Say "global primitives plus a business
profile." The same primitive map lets a judge see their world inside the
hospital demo:

| Primitive | Hospital demo              | Hotel equivalent      | Airport equivalent      | Banking equivalent       | Supermarket equivalent |
| --------- | -------------------------- | --------------------- | ----------------------- | ------------------------ | ---------------------- |
| Signal    | Complaint or surge         | Guest issue           | Delay or disruption     | Dispute or fraud signal  | Complaint or stockout  |
| Resource  | Bed, room, queue, stock    | Room, kitchen, desk   | Gate, bag belt, crew    | Case, account, queue     | Batch, shelf, stock    |
| Partner   | Lab, insurer, laundry      | Laundry, food, vendor | Airline, ground handler | Processor, KYC provider  | Supplier, courier      |
| Policy    | Manager approval, clinical | Refund or safety rule | Safety and ops approval | Compliance approval      | Recall or reorder rule |
| Action    | Task, restock, alert       | Housekeeping, voucher | Rebook, gate update     | Case review, callback    | Quarantine, reorder    |
| Outcome   | Wait, bed, SLA, billing    | Guest response, room  | Delay response, baggage | Resolution, loss avoided | Waste, stock, trust    |

### Slide 7: Honesty And Scope

Be direct:

- mocked or partial in the hackathon: synthetic hospital data, local MuleSoft
  runtime, provider channels when credentials are absent, real hospital
  systems, full WhatsApp agent chat, WhatsApp voice transcription, WhatsApp
  document extraction, and live email unless an Anypoint or email provider is
  connected;
- production-shaped architecture: evidence records, approval gate, protected
  action execution, provider-neutral model gateway, Salesforce audit trail,
  clean-clone runbook, and deterministic refusal checks;
- out of scope: diagnosis, treatment, dosage, triage, clinical priority,
  autonomous protected actions, real patient data, and zero-config onboarding.

### Slide 8: Timing

Target timing for the final rehearsal:

| Time      | Beat                                         |
| --------- | -------------------------------------------- |
| 0:00-0:20 | Problem: one signal expands across functions |
| 0:20-0:45 | Architecture: primitives, agents, approvals  |
| 0:45-2:25 | Live demo flow                               |
| 2:25-2:50 | Business value and judge-sector mapping      |
| 2:50-3:00 | Honesty, clinical boundary, closing line     |

## Backup Recorded-Demo Path

If live Salesforce, Agentforce, Slack, WhatsApp, or local tunnel setup fails,
use the deterministic mock path:

1. Run `npm run demo:reset`.
2. Run `npm run demo:seed`.
3. Run `npm run demo:run`.
4. Open the command center in mock mode with the seeded North Star fixture.
5. Play the recorded screen capture showing the same trigger, conflict, partner
   response, approval, action execution, channel results, clinical refusal, and
   outcome panels.

The presenter must state that Slack, WhatsApp, and vendor-email delivery are
mock channel results unless real credentials or connectors are configured for
that rehearsal.

## Final Non-Goals

- North Star is not a generic chatbot.
- The demo handles hospital operations, not diagnosis, treatment, dosage,
  triage, or clinical priority decisions.
- Hospital, Slack, WhatsApp, partner, billing, and pharmacy integrations are
  mocks unless explicitly configured and demonstrated live.
- Agentforce does not execute protected external actions without manager
  approval.
- Deterministic rules are described as a rules-based baseline, not as trained
  medical or demand forecasting.
