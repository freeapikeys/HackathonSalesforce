# North Star Roadmap

This roadmap is the hackathon checklist. Keep it honest: mark an item complete
only when the code, fixture, UI, test, or demo evidence exists in the repo.

Beads is not installed in the current local environment, so this roadmap is the
active task tracker.

## North Star

Build a Salesforce, Agentforce, and MuleSoft command center that lets a business
plug in a profile and coordinate messy operational issues across evidence,
agents, approvals, protected actions, alerts, and outcomes.

The active demo profile is a large private hospital operations command center.
It solves non-clinical operations issues. It must not make diagnosis, treatment,
dosage, triage, or clinical priority decisions.

North Star must answer:

- Which signal triggered the issue?
- Which global primitives are involved: customer, resource, location, partner,
  process, policy, approval, action, outcome, and metric?
- What source evidence supports each fact?
- Which parts are claims, inference, recommendation, decision, and action?
- Which agents contributed?
- Which actions require business manager approval?
- What MuleSoft action or channel mock executed, and what happened next?

## Universal Issue Modules

These modules are the problems North Star should solve across hospital, hotel,
airport, banking, supermarket, cruise, and other profiles.

| ID    | Issue module                     | Primary agent           | Hospital demo response                                                   |
| ----- | -------------------------------- | ----------------------- | ------------------------------------------------------------------------ |
| NS-01 | Complaint and trust              | Patient Trust           | Cluster complaints, classify cause, draft approved service recovery      |
| NS-02 | Capacity and availability        | Resource and Capacity   | Check beds, rooms, queues, staff, pharmacy stock, and equipment          |
| NS-03 | Staff coordination               | Operations Execution    | Assign tasks, owners, due times, acknowledgements, and escalation        |
| NS-04 | Partner and vendor failure       | Partner and Vendor      | Escalate lab, laundry, insurer, food, payment, or maintenance delay      |
| NS-05 | Inventory and supply             | Resource and Capacity   | Detect low pharmacy/linen/food stock and recommend restock or transfer   |
| NS-06 | Billing and financial exposure   | Financial Impact        | Flag duplicate billing, claim delay, refund, voucher, or revenue risk    |
| NS-07 | Risk, safety, and compliance     | Risk and Approval       | Gate protected actions and refuse clinical decisions                     |
| NS-08 | Communication and escalation     | Communication           | Send approved Slack/WhatsApp-style alerts to role aliases                |
| NS-09 | Disruption recovery              | North Star Orchestrator | Combine complaints, capacity, vendor, billing, and staff signals         |
| NS-10 | Outcome learning                 | Outcome Learning        | Track wait-time, bed release, stockout avoidance, SLA, and task outcome  |
| NS-11 | Evidence quality and uncertainty | Evidence and Context    | Detect missing, contradictory, late, duplicate, or restricted evidence   |
| NS-12 | Policy and approval routing      | Risk and Approval       | Decide manager approval, refusal, defer, modification, or execution path |

## Private Hospital Issues We Solve

| ID     | Hospital issue                          | Primary agent         | Demo response                                                               |
| ------ | --------------------------------------- | --------------------- | --------------------------------------------------------------------------- |
| HOS-01 | Patient wait-time complaints            | Patient Trust         | Cluster complaints, cite queue evidence, draft service recovery             |
| HOS-02 | Room readiness or cleanliness complaint | Patient Trust         | Link complaint to blocked room, housekeeping task, and manager escalation   |
| HOS-03 | Discharge bed blocked                   | Resource and Capacity | Detect blocked beds, assign cleaning/porter task, estimate bed release      |
| HOS-04 | Outpatient queue spike                  | Resource and Capacity | Predict queue risk and recommend staff movement                             |
| HOS-05 | Pharmacy supply running low             | Resource and Capacity | Calculate stock days remaining and request approved restock or transfer     |
| HOS-06 | Lab vendor response delayed             | Partner and Vendor    | Escalate vendor case and update recommendation when response arrives        |
| HOS-07 | Insurance approval stuck                | Financial Impact      | Open approved insurance follow-up and estimate claim-delay exposure         |
| HOS-08 | Duplicate billing or refund complaint   | Financial Impact      | Open billing review, require approval for refund or compensation            |
| HOS-09 | Food or hospitality complaint           | Patient Trust         | Route food-service task and approved patient-safe message                   |
| HOS-10 | Accessibility support missing           | Operations Execution  | Assign wheelchair/porter/support task and track acknowledgement             |
| HOS-11 | Equipment or maintenance unavailable    | Partner and Vendor    | Check resource status, vendor SLA, and fallback options                     |
| HOS-12 | Privacy or safety-sensitive complaint   | Risk and Approval     | Escalate, preserve evidence, and prevent unsafe message/action              |
| HOS-13 | Clinical-decision request               | Risk and Approval     | Refuse diagnosis/treatment/triage decision and route to clinician           |
| HOS-14 | Multi-department morning surge          | Orchestrator          | Create one recovery plan across trust, capacity, vendor, billing, and tasks |

## Agent Responsibilities

### North Star Orchestrator

- [ ] Combine patient trust, resource capacity, partner/vendor, financial,
      communication, and outcome findings into one recovery plan.
- [ ] Resolve conflicts, for example "move patients faster" versus "room
      cleaning is not complete."
- [ ] Decide which actions require manager approval.
- [ ] Produce one recommendation with facts, inferences, assumptions, missing
      evidence, blocked actions, confidence, and expected outcome.
- [ ] Update the recommendation after partner, capacity, billing, or stock
      evidence arrives.

### Evidence And Context Agent

- [ ] Normalize hospital signals into global primitives.
- [ ] Link complaints, queues, resources, partners, policies, approvals,
      actions, and outcomes to evidence IDs.
- [ ] Detect missing, contradictory, restricted, duplicate, late, out-of-order,
      malformed, and low-confidence evidence.
- [ ] Preserve source facts separately from claims and inferences.
- [ ] Ask for missing operational evidence when needed.

### Patient Trust Agent

- [ ] Detect patient and visitor complaint clusters.
- [ ] Classify complaints into wait time, room readiness, cleanliness, food,
      billing, discharge delay, lost item, accessibility, privacy, safety,
      pharmacy delay, and staff interaction.
- [ ] Connect complaints to location, department, resource, time window,
      partner, and evidence.
- [ ] Draft approved service-recovery or patient-facing message text.
- [ ] Escalate safety, privacy, or high-severity complaints.

### Resource And Capacity Agent

- [ ] Evaluate bed, room, queue, staff, pharmacy stock, equipment, and service
      counter capacity.
- [ ] Calculate available capacity, demand pressure, queue risk, stock days
      remaining, and SLA breach risk.
- [ ] Detect blocked discharge rooms and delayed cleaning/porter tasks.
- [ ] Recommend task, restock, transfer, staffing, or escalation actions.
- [ ] Name missing evidence when data is incomplete.

### Operations Execution Agent

- [ ] Create patient-service, room-cleaning, porter, pharmacy, billing,
      front-desk, vendor-follow-up, and manager-review tasks.
- [ ] Assign tasks to role aliases.
- [ ] Prioritize tasks by urgency, risk, approval state, and service window.
- [ ] Track acknowledgement and completion.
- [ ] Escalate missed tasks before the recovery window is lost.

### Partner And Vendor Agent

- [ ] Track lab, laundry, food, insurer, payment, maintenance, transport, and
      equipment partner status.
- [ ] Create vendor escalation or response request after approval.
- [ ] Preserve SLA evidence and partner response details.
- [ ] Update the recommendation when a partner response changes the plan.

### Risk And Approval Agent

- [ ] Enforce business manager approval before protected actions.
- [ ] Refuse diagnosis, treatment, dosage, triage, and clinical priority
      decisions.
- [ ] Decide approve, reject, modify, defer, or execute-ready state.
- [ ] Preserve policy reason, approver role, approval ID, and action ID.
- [ ] Ensure agents operate with current user permissions and purpose limits.

### Financial Impact Agent

- [ ] Detect duplicate billing, stuck claim approval, refund request, voucher
      request, compensation threshold, payment gateway issue, and revenue risk.
- [ ] Estimate financial exposure with formula, time window, and confidence.
- [ ] Route refund, compensation, or payment actions through approval.
- [ ] Preserve billing and insurance evidence without personal data.

### Communication Agent

- [x] Support approved `SEND_SLACK_ALERT` with real webhook or honest
      `MOCK_SENT` fallback.
- [ ] Support approved `SEND_WHATSAPP_ALERT` with real provider only when
      configured or honest `MOCK_SENT` fallback.
- [ ] Route alerts to role aliases, not personal contact data.
- [ ] Keep messages privacy-safe and operational.
- [ ] Preserve provider, status, fallback reason, evidence IDs, action ID,
      approval ID, and correlation ID.

### Outcome Learning Agent

- [ ] Capture wait-time reduced, bed released, stockout avoided, complaint
      contained, billing issue resolved, vendor SLA state, and task completion.
- [ ] Compare expected outcome with actual outcome.
- [ ] Preserve correlation IDs and evidence IDs.
- [ ] Feed outcome summaries into the next recommendation.

## Demo Story

A large private hospital has a morning operations surge. Patient complaints are
increasing, discharge rooms are blocked, outpatient wait time is rising, pharmacy
stock is low, a lab partner response is delayed, and billing/insurance approvals
are stuck.

North Star should produce one recovery plan:

- identify whether the root issue is complaint, capacity, partner, billing,
  stock, staffing, or mixed;
- check hospital resources and evidence;
- refuse any clinical treatment or triage decision;
- create approved service, cleaning, restock, vendor, and billing actions;
- send internal Slack and WhatsApp-style alerts;
- record outcome metrics and audit trail.

## Detailed Checklist

### 1. Product Direction And Scope

- [x] Product name remains North Star.
- [x] Active docs now define a global operating model with a private hospital
      demo profile.
- [x] Universal primitive list added to active docs.
- [x] Hospital non-clinical boundary documented.
- [x] Teammate assignment docs exist in `docs/assignments/`.
- [ ] One-sentence hospital/global product pitch finalized.
- [ ] Three-minute judge demo narrative updated.
- [ ] Five-minute extended demo narrative updated.
- [ ] Backup recorded-demo path updated for hospital scenario.
- [ ] Final non-goals reviewed by whole team.

### 2. Team Assignment Checkpoints

Each teammate has a detailed assignment file. AI agents should read the relevant
file before editing.

- [ ] Aarav: create realistic synthetic hospital operations data, complaints,
      partner responses, capacity pressure, task templates, channel recipient
      aliases, and expected recommendation cases.
- [x] Fahan: preserve and hospitalize `SEND_SLACK_ALERT` behind approved
      MuleSoft action execution, with real webhook support only through
      `SLACK_WEBHOOK_URL` and honest `MOCK_SENT` fallback.
- [ ] Hassan: implement `SEND_WHATSAPP_ALERT` behind approval and add voice
      transcript flow that creates a governed recommendation request without
      bypassing approval or making clinical decisions.
- [ ] Ranveer: preserve completed Agentforce reasoning work and generalize
      inventory/waste logic into resource, capacity, stock, queue, and SLA
      reasoning for hospital operations.
- [ ] Merge owner: keep branches aligned, review conflicts, protect `main`, and
      verify the demo still tells one North Star story.

### 3. Global Primitive And Hospital Data

- [ ] Define hospital organization, department, ward, location, resource,
      partner, policy, action, outcome, and metric IDs.
- [ ] Define synthetic patient/visitor aliases with no personal data.
- [ ] Define bed, room, pharmacy item, equipment, queue, service counter, and
      staff role resources.
- [ ] Define hospital partners: lab, laundry, insurer, payment, food,
      maintenance, transport, and equipment vendor.
- [ ] Define complaint examples for waiting time, room readiness, food,
      billing, discharge delay, accessibility, privacy, pharmacy delay, and
      staff interaction.
- [ ] Define capacity facts for beds, blocked rooms, queue pressure, staff
      availability, pharmacy stock, and equipment availability.
- [ ] Define billing and insurance facts for duplicate invoice, stuck claim,
      refund request, payment issue, and approval threshold.
- [ ] Define expected outcome metrics for the demo.
- [ ] Ensure every fixture uses global primitive language where possible.

### 4. Hospital Event Fixtures

- [x] Add `PATIENT_COMPLAINT_CLUSTER_DETECTED` fixture.
- [x] Add `BED_CAPACITY_PRESSURE_DETECTED` fixture.
- [x] Add `DISCHARGE_ROOM_BLOCKED` fixture.
- [x] Add `PHARMACY_STOCK_RISK_DETECTED` fixture.
- [x] Add `LAB_VENDOR_RESPONSE_DELAYED` fixture.
- [x] Add `BILLING_APPROVAL_STALLED` fixture.
- [x] Add `STAFF_QUEUE_RISK_DETECTED` fixture.
- [x] Add `CLINICAL_DECISION_REQUEST_REFUSED` fixture.
- [x] Add `APPROVED_ACTION_EXECUTED` hospital fixture.
- [x] Add `HOSPITAL_OUTCOME_CAPTURED` fixture.
- [x] Keep duplicate, malformed, late, out-of-order, replay, hash, and
      idempotency-conflict cases passing.

### 5. Salesforce Core

- [x] Map hospital and departments to existing Salesforce entity records.
- [x] Map resources such as bed, room, pharmacy stock, queue, service counter,
      and equipment to existing entity/resource patterns.
- [x] Map patient and visitor aliases without personal data.
- [x] Map hospital partners to entity records.
- [x] Map complaints to evidence records.
- [ ] Map tasks to action records and/or Salesforce task records.
- [ ] Apex context includes customer alias, department, location, resource,
      partner, complaint, capacity, stock, billing, recommendation, approval,
      action, and outcome.
- [x] Manager approval is enforced before vendor, billing, pharmacy, Slack,
      WhatsApp, patient-message, room/bed, or staff-task write-back.
- [ ] Clinical decision requests are refused.
- [x] Action and outcome records preserve correlation IDs and evidence IDs.
- [ ] Apex tests cover success, denial, inaccessible evidence, approval
      mismatch, invalid state, and clinical refusal.

### 6. Agentforce And Intelligence

- [ ] Define/update North Star Orchestrator topic for global primitives.
- [ ] Define/update Evidence and Context topic.
- [ ] Define/update Patient Trust topic.
- [ ] Define/update Resource and Capacity topic.
- [ ] Define/update Operations Execution topic.
- [ ] Define/update Partner and Vendor topic.
- [ ] Define/update Risk and Approval topic.
- [ ] Define/update Financial Impact topic.
- [ ] Define/update Communication topic.
- [ ] Define/update Outcome Learning topic.
- [ ] Recommendation request includes complaint, resource, capacity, partner,
      billing, stock, staffing, approval, and outcome evidence.
- [ ] Recommendation response separates facts, inferences, assumptions, missing
      evidence, recommended actions, blocked actions, approval requirements,
      and expected outcomes.
- [ ] Agentforce refuses diagnosis, treatment, dosage, triage, and clinical
      priority decisions.
- [x] Agentforce fixtures include evidence-backed reasoning from latest
      inventory/waste work.
- [x] Agentforce fixtures include a denied-action scenario.
- [x] Agentforce fixtures include a changed-recommendation scenario.
- [x] Model gateway uses global/hospital profile names, not retail-only names.

### 7. MuleSoft And Channel Mocks

- [x] Mock `CREATE_PATIENT_SERVICE_TASK`.
- [x] Mock `REQUEST_BED_CLEANING`.
- [x] Mock `ESCALATE_LAB_VENDOR_CASE`.
- [x] Mock `CREATE_PHARMACY_RESTOCK_REQUEST`.
- [x] Mock `OPEN_BILLING_REVIEW`.
- [x] Mock `REQUEST_INSURANCE_FOLLOWUP`.
- [x] Mock `SEND_SLACK_ALERT`.
- [x] Mock `SEND_WHATSAPP_ALERT`.
- [x] Mock `CAPTURE_HOSPITAL_OUTCOME`.
- [x] Unapproved execution returns denial.
- [x] Approved execution returns queued or success response with correlation.
- [x] If `SLACK_WEBHOOK_URL` exists, send real Slack webhook message.
- [x] If `SLACK_WEBHOOK_URL` is missing, return honest `MOCK_SENT`.
- [x] Malformed Slack payloads return validation errors.
- [x] Malformed WhatsApp payloads return validation errors.
- [x] Slack channel responses preserve `tenantId`, `correlationId`,
      `approvalId`, `actionId`, evidence IDs, provider, status, and fallback
      reason.
- [x] WhatsApp channel responses preserve `tenantId`, `correlationId`,
      `approvalId`, `actionId`, evidence IDs, provider, status, and fallback
      reason.
- [x] Mock channel results are visible in the hospital command center.

### 8. Voice Mode

- [ ] Add voice transcript input or browser speech input path.
- [ ] Convert transcript into structured hospital operations request fields:
      issue, department, location, resource, urgency, requester role, and
      evidence.
- [ ] Voice mode can ask Agentforce for a recommendation.
- [ ] Voice mode cannot execute Slack, WhatsApp, vendor, pharmacy, billing,
      room/bed, staff-task, or patient-message actions directly.
- [ ] Voice mode refuses clinical decision requests.
- [ ] LWC or fixture tests cover transcript-to-request, protected-action
      refusal, and clinical-decision refusal.

### 9. Lightning Command Center

- [x] UI title and labels use North Star global/hospital operations language.
- [x] Risk pulse cards show complaint, bed capacity, queue, pharmacy stock,
      vendor delay, billing, approval, and outcome readiness.
- [x] Patient/visitor alias, department, location, and resource context are
      visible.
- [x] Complaint cluster panel shows complaint type, count, department,
      location, resource, partner, and time window.
- [x] Partner response panel shows lab, laundry, insurer, payment, food,
      maintenance, or transport status.
- [x] Operations panel shows task queue, owner role, acknowledgement, and due
      time.
- [x] Evidence timeline cites source records.
- [x] Agent reasoning panel separates facts from inference.
- [x] Approval cockpit supports approve, reject, modify, defer, and executed
      states.
- [x] Channel log shows Slack and WhatsApp-style alert results.
- [x] Clinical-refusal state is visible when relevant.
- [ ] Voice transcript or voice request panel is visible if voice mode is in
      the demo.
- [x] Outcome panel shows wait time reduced, bed released, stockout avoided,
      complaint containment, vendor SLA, billing resolution, and task
      completion.
- [ ] LWC tests cover ready, loading, empty, denied, error, restricted,
      approval, action, outcome, voice, and clinical-refusal states.

### 10. End-To-End Demo

- [ ] `npm run check` passes in the intended demo environment.
- [ ] `npm run demo:reset` works.
- [ ] `npm run demo:seed` creates the hospital operations case.
- [ ] `npm run demo:run` completes trigger through outcome.
- [ ] Clean-clone runbook reflects the hospital/global flow.
- [ ] Demo starts from one clear hospital operations surge event.
- [ ] Demo shows conflicting recommendations before orchestration.
- [ ] Demo shows partner or capacity response changing the recommendation.
- [ ] Demo shows manager approval before action execution.
- [ ] Demo shows Slack and WhatsApp-style internal alerts.
- [ ] Demo shows clinical-decision refusal.
- [ ] Demo shows outcome metrics and audit trail.
- [ ] Final rehearsal completed with the whole team.

### 11. Pitch And Presentation

- [ ] Problem slide explains universal issue modules and the hospital demo.
- [ ] Agent slide explains the orchestrator, global primitives, and specialist
      agents.
- [ ] Salesforce slide explains Agentforce, Salesforce records, MuleSoft mocks,
      and approval boundary.
- [ ] Demo slide shows the exact live flow.
- [ ] Business value slide quantifies wait time reduced, bed released, stockout
      avoided, billing risk contained, vendor SLA, and complaint containment.
- [ ] Plug-and-play slide maps hospital resources to hotel, airport, banking,
      and supermarket equivalents.
- [ ] Honesty slide states what is mocked, what is production-ready
      architecture, and what clinical decisions are out of scope.
- [ ] Timing has been rehearsed.

## Done Means

A task is done only when:

- the implementation or fixture exists;
- the relevant check passes;
- the demo state is visible to a judge;
- failure, denial, refusal, or fallback behavior is handled;
- docs are updated without drifting back to a narrow supermarket-only story.

## Non-Goals

- Do not build a generic chatbot.
- Do not claim zero-configuration plug-and-play. Say "global primitives plus a
  business profile."
- Do not claim diagnosis, treatment, dosage, triage, or clinical priority
  decisions.
- Do not claim live integrations that are actually mocks.
- Do not let agents execute protected external actions without manager
  approval.
- Do not commit real patient, staff, vendor, insurer, phone, email, credential,
  or medical-record data.
