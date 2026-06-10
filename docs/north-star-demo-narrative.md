# North Star Demo Narrative

## Product Pitch

North Star is a Salesforce and Agentforce command center that turns messy
business operations signals into one manager-approved recovery plan. The demo
uses a large private hospital, but the architecture is global: the same
primitives can map to hotel rooms, airport gates, bank cases, supermarket
batches, cruise cabins, and hospital beds.

## Three-Minute Judge Demo

The demo opens with a morning operations surge at a private hospital. The
command center shows rising patient complaints, blocked discharge rooms, a
growing outpatient queue, pharmacy stock pressure, delayed lab response, and
stuck billing/insurance approvals.

North Star reveals the conflict. The Patient Trust Agent sees a complaint
cluster around waiting time, room readiness, and billing confusion. The Resource
and Capacity Agent shows blocked beds, staff coverage gaps, and low stock days
remaining for a pharmacy item. The Partner and Vendor Agent shows a delayed lab
response. The Financial Impact Agent flags billing and insurance exposure. The
Risk and Approval Agent blocks any clinical-decision request and requires
manager approval for protected operational actions.

The orchestrator combines these findings into one recovery plan. It separates
facts from inferences, names missing evidence, refuses diagnosis or triage, and
proposes operational recovery: release cleaned beds, assign porter tasks,
request pharmacy restock, open billing review, escalate the lab partner, and
prepare approved internal alerts.

The operations manager approves consequential actions in the command center.
MuleSoft mocks then execute the approved service task, bed-cleaning request,
vendor escalation, billing review, Slack alert, WhatsApp-style internal alert,
and outcome callback. The final view shows wait time reduced, beds released,
stockout avoided, complaint risk contained, billing issue routed, vendor SLA
preserved, and staff tasks acknowledged.

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
agents disagree in useful ways: patient trust wants fast recovery, capacity
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

The presenter must state that Slack and WhatsApp-style delivery are mock channel
results unless real credentials are configured for that rehearsal.

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
