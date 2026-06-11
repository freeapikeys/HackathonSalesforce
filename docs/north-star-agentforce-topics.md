# North Star Agentforce Topics

## North Star Orchestrator

Combines patient trust, evidence, resource capacity, partner/vendor, financial,
communication, approval, and outcome findings into one action plan. It
resolves conflicts, separates source facts from inferences and assumptions,
decides which actions require manager approval, refuses clinical decisions, and
updates the recommendation after partner, capacity, billing, or stock evidence
arrives.

## Evidence And Context

Normalizes hospital operations signals into global primitives. It links
complaints, queue records, resource status, partner responses, billing cases,
approvals, actions, and outcomes to source evidence IDs. It names missing,
contradictory, restricted, duplicate, late, out-of-order, malformed, or
low-confidence evidence.

## Patient Trust

Detects complaint clusters, classifies wait-time, room readiness, cleanliness,
food, billing, discharge delay, pharmacy delay, accessibility, privacy, safety,
lost-item, and staff-interaction issues. It drafts approved service response
text and escalates high-risk complaints without making clinical decisions.

## Resource And Capacity

Calculates capacity pressure, queue load, stock days remaining, staff coverage
gap, and SLA breach risk. It checks beds, rooms, queues, pharmacy stock,
equipment, service counters, and staff pools. It recommends task, restock,
transfer, staffing, vendor, or manager-review actions that flow into approval.

## Operations Execution

Creates patient-service, bed-cleaning, porter, pharmacy, billing, insurance,
vendor-follow-up, maintenance, food-service, and manager-review tasks. It
assigns owner roles, tracks acknowledgement and completion, and escalates missed
work before the service window is lost.

## Partner And Vendor

Tracks lab, laundry, insurer, payment, food, maintenance, transport, and
equipment partner status. It requests response or escalation after approval,
preserves SLA evidence, and updates recommendations when partner evidence
changes.

## Risk And Approval

Determines approval requirement, refusal, modification, deferment, or
execute-ready status. It blocks unsafe or unsupported actions and refuses
diagnosis, treatment, dosage, triage, and clinical priority decisions.

## Financial Impact

Detects billing disputes, duplicate invoices, claim approval delays, refund
requests, voucher requests, payment failures, compensation thresholds, revenue
exposure, and SLA penalties. It estimates exposure with a formula, confidence,
and time window, routes financial actions through approval, and preserves audit
evidence without personal data.

## Communication

Drafts Slack, WhatsApp, and future email messages, then executes only the
approved ones through MuleSoft. Slack is for internal teams. WhatsApp can be
customer intake, urgent mobile alert, or approved customer acknowledgement.
Customer-facing replies must be privacy-safe and must not include clinical
advice. The agent preserves provider, status, fallback reason, evidence IDs,
approval ID, action ID, and correlation ID.

## Outcome Learning

Captures wait time reduced, bed released, stockout avoided, complaint
contained, billing issue resolved, vendor SLA state, channel delivery, and task
completion. It compares expected and actual outcomes for the next
recommendation.

## Contract Evidence

The executable Agentforce fixture in
`intelligence/agentforce/fixtures/agentforce-scenarios-v1.json` now preserves
the completed inventory/waste scenarios as compatibility coverage and adds the
global/hospital profile. The hospital scenarios separate facts from inferences
and assumptions, cite evidence, name missing evidence, define expected outcomes,
refuse protected external execution, block clinical decisions, and include
partner/capacity evidence that changes or qualifies the recommendation.
