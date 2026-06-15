# Ranveer Assignment: Internal Execution Proof And Resource Reasoning

## Goal

Preserve the completed Agentforce inventory/waste reasoning work from latest
`main`, then own the internal proof that Logia does more than send a fake
WhatsApp receipt. Your lane is the manager/team side: resource and capacity
reasoning, live Slack approval rehearsal, command-center action/outcome trace,
protected vendor-email mock proof, and clear evidence that one customer issue
expands into several business functions.

The agent should turn hospital operations evidence into grounded
recommendations: bed pressure, queue risk, stock risk, SLA risk, staff pressure,
vendor dependency, billing exposure, approval requirement, and safe next
actions. It must cite facts, separate inference, name missing evidence, respect
approval boundaries, and refuse clinical decisions.

## What The Project Already Has

Start from the existing governed spine:

- `docs/logia-mvp.md` defines the global operating model and hospital demo.
- `docs/agentforce-action-contract.md` defines Agentforce-facing actions.
- `docs/apex-service-contract.md` defines the Apex service boundary.
- `docs/model-gateway-contract.md` and `docs/model-architecture.md` define
  logical model routing and grounding expectations.
- `docs/salesforce-data-model.md` maps concepts to HFS records.
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json` contains
  current Agentforce fixtures.
- `force-app/main/default/classes/` contains Apex service and invocable classes.
- `integration/events/fixtures/` contains source event fixtures.
- `scripts/generate_agentforce_contract.py` and
  `scripts/validate_agentforce_contract.py` include the latest reasoning
  contract work.

Do not make a generic Q&A bot. The output must be an evidence-backed operations
recommendation.

## Files To Inspect First

- `docs/logia-mvp.md`
- `docs/logia-implementation-plan.md`
- `docs/agentforce-action-contract.md`
- `docs/apex-service-contract.md`
- `docs/model-gateway-contract.md`
- `docs/model-architecture.md`
- `docs/salesforce-data-model.md`
- `intelligence/agentforce/README.md`
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json`
- `intelligence/agentforce/schemas/agentforce-actions-v1.schema.json`
- `force-app/main/default/classes/`
- `scripts/generate_agentforce_contract.py`
- `scripts/validate_agentforce_contract.py`

## Required Reasoning Inputs

The Resource and Capacity Agent should expect these inputs from Salesforce,
fixtures, or Data Cloud style mock data:

- department ID, name, and service area;
- location ID, such as ward, reception, pharmacy, lab counter, or billing desk;
- resource IDs and types, such as bed, room, queue, supply item, equipment, or
  service counter;
- current capacity, available capacity, blocked capacity, reserved capacity, and
  incoming capacity;
- queue count, arrival rate, service rate, and wait-time target;
- pharmacy or supply stock, average usage, incoming stock, and supplier lead
  time;
- staff scheduled, staff available, staff missing, and role coverage;
- partner status, such as lab, laundry, insurer, payment, or maintenance;
- complaint or customer trust summary;
- billing or insurance approval status;
- evidence IDs and source timestamps.

## Required Reasoning Outputs

The agent should return:

- `riskType`: `CAPACITY`, `QUEUE`, `STOCK`, `SLA`, `VENDOR`, `BILLING`,
  `COMPLAINT`, `CLINICAL_REFUSAL`, or `MIXED`
- `severity`: `Low`, `Medium`, `High`, or `Critical`
- `facts`: source-backed statements with evidence IDs
- `inferences`: calculated or model-assisted conclusions
- `missingEvidence`: data needed before a stronger decision can be made
- `recommendedActions`: proposed actions, each with approval requirement
- `blockedActions`: unsafe, clinical, unapproved, unsupported, or deferred
  actions
- `supplierOrPartnerCaution`: whether partner evidence changes the plan
- `confidence`: 0 to 1
- `explanation`: manager-readable summary

## Baseline Calculations

Use deterministic calculations before model wording:

```text
availableCapacity = totalCapacity - blockedCapacity - reservedCapacity
demandPressure = expectedDemand / max(1, availableCapacity)
queueLoad = waitingCount / max(1, serviceRatePerHour)
stockDaysRemaining = availableStock / max(1, averageDailyUsage)
slaBreachRisk = minutesUntilDeadline < estimatedMinutesToResolve
coverageGap = requiredStaffByRole - availableStaffByRole
```

Suggested thresholds:

- `demandPressure > 1.25`: High capacity risk
- `demandPressure > 1.75`: Critical capacity risk
- `queueLoad > 1`: High queue risk
- `stockDaysRemaining < 1`: Critical stock risk
- `stockDaysRemaining < 2`: High stock risk
- `slaBreachRisk = true`: require escalation or manager attention
- active complaint cluster on same department/resource: qualify the plan and
  include customer trust implications

These thresholds can be changed, but the formula and reason must be documented.

## Clinical Boundary Rule

Do not recommend diagnosis, treatment, dosage, clinical triage, or clinical
priority decisions.

Correct behavior:

- If the issue is operational capacity, recommend tasking, staff movement,
  resource release, vendor escalation, or manager review.
- If the issue asks which patient should be treated first, refuse and route to
  a clinician or clinical manager.
- If clinical evidence is missing or restricted, name the restriction and do not
  infer clinical action.
- If a partner response changes operational capacity, update the
  recommendation.

## Implementation Checklist

- [x] Pull latest `main`.
- [x] Read this file and the required docs.
- [x] Inspect existing Agentforce fixtures and generated contract scripts.
- [x] Identify the current recommendation action shape.
- [x] Add or update Inventory/Waste fixture scenarios.
- [x] Add deterministic calculations for days of cover, sales at risk, and
      waste risk where appropriate.
- [x] Ensure every recommendation cites inventory, expiry, promotion, complaint,
      supplier, and staffing evidence when available.
- [x] Ensure facts and inferences are separate.
- [x] Add `missingEvidence` when data is absent.
- [x] Add `blockedActions` for unsafe direct actions or unsupported claims.
- [x] Ensure recommendations feed the approval/action path rather than execute
      actions directly.
- [x] Keep labels product-category neutral.
- [x] Generalize all active scenario labels from retail to global/hospital
      operations. The new hospital scenarios use global/hospital labels, while
      older inventory/waste scenario names remain as compatibility coverage and
      are excluded from the active hospital fixture-language audit.
- [x] Add Resource and Capacity hospital scenarios.
- [x] Add capacity, queue, stock, SLA, staff, and partner calculations where
      appropriate.
- [x] Add `CLINICAL_REFUSAL` or equivalent blocked-action scenario.
- [x] Ensure recommendations feed the hospital approval/action path.
- [ ] Rehearse live Slack approve, reject, and modify buttons with a public
      Slack App interactivity Request URL and `SLACK_SIGNING_SECRET` outside
      Git.
- [x] If live Slack interactivity is not reachable, document the exact
      command-center fallback used for manager approval.
- [x] Prove protected actions stay blocked before approval and execute only
      after approval.
- [x] Show a visible command-center trace from one Meta WhatsApp complaint to
      evidence, recommendation, approval, Slack/internal alert, vendor-email
      mock queue, task action, and outcome.
- [x] Make the stock flow judge-readable: low stock is detected, manager sees
      restock/transfer recommendation, protected supplier/vendor email remains
      queued mock unless live email credentials exist, and outcome is recorded.
- [x] Make the billing flow judge-readable: duplicate or stuck billing issue
      creates a financial-impact finding, requires approval, opens review, and
      records outcome without making a final refund/financial decision.
- [x] Make the capacity flow judge-readable: blocked room/queue pressure creates
      task actions with owner roles, due windows, acknowledgement, escalation,
      and outcome metrics.
- [x] Ensure Slack messages are short, operational, privacy-safe, and role
      targeted.
- [x] Ensure the demo never says vendor email is live unless an email provider
      is configured and tested.

## Scenario Checklist

- [x] Stockout risk with clean supplier history.
- [x] Stockout risk with active complaint cluster.
- [x] Near-expiry fresh food with markdown recommendation.
- [x] Overstock household item with transfer or promotion adjustment.
- [x] Promotion demand spike with insufficient shelf stock.
- [x] Supplier replacement batch changes the recommendation.
- [x] Missing expiry data causes a cautious recommendation.
- [x] Missing supplier response blocks supplier-wide decision.
- [x] Bed capacity pressure with blocked discharge rooms.
- [x] Outpatient queue risk with staff coverage gap.
- [x] Pharmacy stock risk with approved restock or transfer recommendation.
- [x] Lab partner delay that changes the recommendation.
- [x] Billing approval delay that requires financial approval.
- [x] Missing capacity evidence that causes a cautious recommendation.
- [x] Clinical triage request that is refused and routed to clinician review.

## Testing Checklist

- [x] Run `npm run check:agentforce`.
- [x] Run `npm run check:models` if model gateway fixtures change.
- [x] Run `npm run check:project` if Apex metadata or classes change.
- [x] Add or update tests for evidence citation, fact versus inference
      separation, partner caution, missing evidence, refusal to execute
      protected actions directly, and clinical-decision refusal.
- [x] Run `npm run check:harness` after changing approval, action execution, or
      command-center proof data.
- [x] Run `npm run check:mulesoft` after changing Slack approval, protected
      vendor email, or action execution contracts.
- [x] Capture one rehearsal note: what was live, what was mock, and what the
      judge will see in the command center.

## Demo Acceptance

The Resource and Capacity reasoning work is demo-ready when:

- Agentforce can explain why a hospital operation is at risk;
- it calculates or cites capacity pressure, queue load, stock days remaining,
  SLA risk, or staff coverage gap;
- it changes or qualifies the plan when complaint, partner, billing, or stock
  evidence exists;
- it proposes actions that flow into approval;
- it does not send Slack, WhatsApp, vendor, billing, pharmacy, room/bed, or
  staff-task actions directly;
- it refuses diagnosis, treatment, dosage, triage, and clinical priority
  decisions;
- Slack approval or command-center approval clearly gates protected actions;
- protected vendor email is visibly queued as a mock, not claimed as live;
- the command center shows action results and outcome metrics after approval;
- a manager can understand the reasoning in less than one minute.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/ranveer.md, docs/agentforce-action-contract.md,
docs/apex-service-contract.md, docs/mulesoft-api-contract.md, and
intelligence/agentforce fixtures. Implement the next smallest internal proof
task: live Slack approval rehearsal, command-center action/outcome trace,
protected vendor-email mock proof, stock/capacity/billing workflow clarity, or
Resource and Capacity reasoning. Preserve evidence citations, fact/inference
separation, partner caution, approval gating, and clinical-decision refusal.
Run the focused checks for changed files.
```
