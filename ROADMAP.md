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
| NS-01 | Complaint and trust              | Patient Trust           | Cluster complaints, classify cause, draft approved service response      |
| NS-02 | Capacity and availability        | Resource and Capacity   | Check beds, rooms, queues, staff, pharmacy stock, and equipment          |
| NS-03 | Staff coordination               | Operations Execution    | Assign tasks, owners, due times, acknowledgements, and escalation        |
| NS-04 | Partner and vendor failure       | Partner and Vendor      | Escalate lab, laundry, insurer, food, payment, or maintenance delay      |
| NS-05 | Inventory and supply             | Resource and Capacity   | Detect low pharmacy/linen/food stock and recommend restock or transfer   |
| NS-06 | Billing and financial exposure   | Financial Impact        | Flag duplicate billing, claim delay, refund, voucher, or revenue risk    |
| NS-07 | Risk, safety, and compliance     | Risk and Approval       | Gate protected actions and refuse clinical decisions                     |
| NS-08 | Communication and escalation     | Communication           | Send approved Slack/WhatsApp-style alerts to role aliases                |
| NS-09 | Disruption coordination          | North Star Orchestrator | Combine complaints, capacity, vendor, billing, and staff signals         |
| NS-10 | Outcome learning                 | Outcome Learning        | Track wait-time, bed release, stockout avoidance, SLA, and task outcome  |
| NS-11 | Evidence quality and uncertainty | Evidence and Context    | Detect missing, contradictory, late, duplicate, or restricted evidence   |
| NS-12 | Policy and approval routing      | Risk and Approval       | Decide manager approval, refusal, defer, modification, or execution path |

## Private Hospital Issues We Solve

| ID     | Hospital issue                          | Primary agent         | Demo response                                                             |
| ------ | --------------------------------------- | --------------------- | ------------------------------------------------------------------------- |
| HOS-01 | Patient wait-time complaints            | Patient Trust         | Cluster complaints, cite queue evidence, draft service response           |
| HOS-02 | Room readiness or cleanliness complaint | Patient Trust         | Link complaint to blocked room, housekeeping task, and manager escalation |
| HOS-03 | Discharge bed blocked                   | Resource and Capacity | Detect blocked beds, assign cleaning/porter task, estimate bed release    |
| HOS-04 | Outpatient queue spike                  | Resource and Capacity | Predict queue risk and recommend staff movement                           |
| HOS-05 | Pharmacy supply running low             | Resource and Capacity | Calculate stock days remaining and request approved restock or transfer   |
| HOS-06 | Lab vendor response delayed             | Partner and Vendor    | Escalate vendor case and update recommendation when response arrives      |
| HOS-07 | Insurance approval stuck                | Financial Impact      | Open approved insurance follow-up and estimate claim-delay exposure       |
| HOS-08 | Duplicate billing or refund complaint   | Financial Impact      | Open billing review, require approval for refund or compensation          |
| HOS-09 | Food or hospitality complaint           | Patient Trust         | Route food-service task and approved patient-safe message                 |
| HOS-10 | Accessibility support missing           | Operations Execution  | Assign wheelchair/porter/support task and track acknowledgement           |
| HOS-11 | Equipment or maintenance unavailable    | Partner and Vendor    | Check resource status, vendor SLA, and fallback options                   |
| HOS-12 | Privacy or safety-sensitive complaint   | Risk and Approval     | Escalate, preserve evidence, and prevent unsafe message/action            |
| HOS-13 | Clinical-decision request               | Risk and Approval     | Refuse diagnosis/treatment/triage decision and route to clinician         |
| HOS-14 | Multi-department morning surge          | Orchestrator          | Create one action plan across trust, capacity, vendor, billing, and tasks |

## Agent Responsibilities

### North Star Orchestrator

- [x] Combine patient trust, resource capacity, partner/vendor, financial,
      communication, and outcome findings into one action plan.
- [x] Resolve conflicts, for example "move patients faster" versus "room
      cleaning is not complete."
- [x] Decide which actions require manager approval.
- [x] Produce one recommendation with facts, inferences, assumptions, missing
      evidence, blocked actions, confidence, and expected outcome.
- [x] Update the recommendation after partner, capacity, billing, or stock
      evidence arrives.

### Evidence And Context Agent

- [x] Normalize hospital signals into global primitives.
- [x] Link complaints, queues, resources, partners, policies, approvals,
      actions, and outcomes to evidence IDs.
- [x] Detect missing, contradictory, restricted, duplicate, late, out-of-order,
      malformed, and low-confidence evidence.
- [x] Preserve source facts separately from claims and inferences.
- [x] Ask for missing operational evidence when needed.

### Patient Trust Agent

- [x] Detect patient and visitor complaint clusters.
- [x] Classify complaints into wait time, room readiness, cleanliness, food,
      billing, discharge delay, lost item, accessibility, privacy, safety,
      pharmacy delay, and staff interaction.
- [x] Connect complaints to location, department, resource, time window,
      partner, and evidence.
- [x] Draft approved service response or patient-facing message text.
- [x] Escalate safety, privacy, or high-severity complaints.

### Resource And Capacity Agent

- [x] Evaluate bed, room, queue, staff, pharmacy stock, equipment, and service
      counter capacity.
- [x] Calculate available capacity, demand pressure, queue risk, stock days
      remaining, and SLA breach risk.
- [x] Detect blocked discharge rooms and delayed cleaning/porter tasks.
- [x] Recommend task, restock, transfer, staffing, or escalation actions.
- [x] Name missing evidence when data is incomplete.

### Operations Execution Agent

- [x] Create patient-service, room-cleaning, porter, pharmacy, billing,
      front-desk, vendor-follow-up, and manager-review tasks.
- [x] Assign tasks to role aliases.
- [x] Prioritize tasks by urgency, risk, approval state, and service window.
- [x] Track acknowledgement and completion.
- [x] Escalate missed tasks before the service window is lost.

### Partner And Vendor Agent

- [x] Track lab, laundry, food, insurer, payment, maintenance, transport, and
      equipment partner status.
- [x] Create vendor escalation or response request after approval.
- [x] Preserve SLA evidence and partner response details.
- [x] Update the recommendation when a partner response changes the plan.

### Risk And Approval Agent

- [x] Enforce business manager approval before protected actions.
- [x] Refuse diagnosis, treatment, dosage, triage, and clinical priority
      decisions.
- [x] Decide approve, reject, modify, defer, or execute-ready state.
- [x] Preserve policy reason, approver role, approval ID, and action ID.
- [x] Ensure agents operate with current user permissions and purpose limits.

### Financial Impact Agent

- [x] Detect duplicate billing, stuck claim approval, refund request, voucher
      request, compensation threshold, payment gateway issue, and revenue risk.
- [x] Estimate financial exposure with formula, time window, and confidence.
- [x] Route refund, compensation, or payment actions through approval.
- [x] Preserve billing and insurance evidence without personal data.

### Communication Agent

- [x] Support approved `SEND_SLACK_ALERT` with real webhook or honest
      `MOCK_SENT` fallback.
- [x] Support approved `SEND_WHATSAPP_ALERT` with real provider only when
      configured or honest `MOCK_SENT` fallback.
- [x] Route alerts to role aliases, not personal contact data.
- [x] Keep messages privacy-safe and operational.
- [x] Preserve provider, status, fallback reason, evidence IDs, action ID,
      approval ID, and correlation ID.

### Outcome Learning Agent

- [x] Capture wait-time reduced, bed released, stockout avoided, complaint
      contained, billing issue routed, vendor SLA state, and task completion.
- [x] Compare expected outcome with actual outcome.
- [x] Preserve correlation IDs and evidence IDs.
- [x] Feed outcome summaries into the next recommendation.

## Demo Story

A large private hospital has a morning operations surge. Patient complaints are
increasing, discharge rooms are blocked, outpatient wait time is rising, pharmacy
stock is low, a lab partner response is delayed, and billing/insurance approvals
are stuck.

North Star should produce one action plan:

- accept a customer or patient complaint through WhatsApp or a Salesforce
  intake fallback;
- identify whether the root issue is complaint, capacity, partner, billing,
  stock, staffing, or mixed;
- check hospital resources and evidence;
- refuse any clinical treatment or triage decision;
- create approved service, cleaning, restock, vendor, and billing actions;
- send Slack internal alerts and approved WhatsApp mobile/customer-safe
  messages;
- record outcome metrics and audit trail.

## Detailed Checklist

### 1. Product Direction And Scope

- [x] Product name remains North Star.
- [x] Active docs now define a global operating model with a private hospital
      demo profile.
- [x] Universal primitive list added to active docs.
- [x] Hospital non-clinical boundary documented.
- [x] Teammate assignment docs exist in `docs/assignments/`.
- [x] One-sentence hospital/global product pitch finalized.
- [x] Three-minute judge demo narrative updated.
- [x] Five-minute extended demo narrative updated.
- [x] Backup recorded-demo path updated for hospital scenario.
- [ ] Final non-goals reviewed by whole team.

### 2. Team Assignment Checkpoints

Each teammate has a detailed assignment file. AI agents should read the relevant
file before editing.

- [x] Aarav: create realistic synthetic hospital operations data, complaints,
      partner responses, capacity pressure, task templates, channel recipient
      aliases, and expected recommendation cases.
- [x] Fahan: preserve and hospitalize `SEND_SLACK_ALERT` behind approved
      MuleSoft action execution, with real webhook support only through
      `SLACK_WEBHOOK_URL` and honest `MOCK_SENT` fallback.
- [x] Hassan: implement `SEND_WHATSAPP_ALERT` behind approval and add voice
      transcript flow that creates a governed recommendation request without
      bypassing approval or making clinical decisions.
- [x] Ranveer: preserve completed Agentforce reasoning work and generalize
      inventory/waste logic into resource, capacity, stock, queue, and SLA
      reasoning for hospital operations.
- [ ] Merge owner: keep branches aligned, review conflicts, protect `main`, and
      verify the demo still tells one North Star story.

### 3. Global Primitive And Hospital Data

- [x] Define hospital organization, department, ward, location, resource,
      partner, policy, action, outcome, and metric IDs.
- [x] Define synthetic patient/visitor aliases with no personal data.
- [x] Define bed, room, pharmacy item, equipment, queue, service counter, and
      staff role resources.
- [x] Define hospital partners: lab, laundry, insurer, payment, food,
      maintenance, transport, and equipment vendor.
- [x] Define complaint examples for waiting time, room readiness, food,
      billing, discharge delay, accessibility, privacy, pharmacy delay, and
      staff interaction.
- [x] Define capacity facts for beds, blocked rooms, queue pressure, staff
      availability, pharmacy stock, and equipment availability.
- [x] Define billing and insurance facts for duplicate invoice, stuck claim,
      refund request, payment issue, and approval threshold.
- [x] Define expected outcome metrics for the demo.
- [x] Ensure every fixture uses global primitive language where possible.

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
- [x] Map tasks to action records and/or Salesforce task records.
- [x] Apex context includes customer alias, department, location, resource,
      partner, complaint, capacity, stock, billing, recommendation, approval,
      action, and outcome.
- [x] Manager approval is enforced before vendor, billing, pharmacy, Slack,
      WhatsApp, patient-message, room/bed, or staff-task write-back.
- [x] Clinical decision requests are refused.
- [x] Action and outcome records preserve correlation IDs and evidence IDs.
- [x] Apex tests cover success, denial, inaccessible evidence, approval
      mismatch, invalid state, and clinical refusal.

### 6. Agentforce And Intelligence

- [x] Define/update North Star Orchestrator topic for global primitives.
- [x] Define/update Evidence and Context topic.
- [x] Define/update Patient Trust topic.
- [x] Define/update Resource and Capacity topic.
- [x] Define/update Operations Execution topic.
- [x] Define/update Partner and Vendor topic.
- [x] Define/update Risk and Approval topic.
- [x] Define/update Financial Impact topic.
- [x] Define/update Communication topic.
- [x] Define/update Outcome Learning topic.
- [x] Recommendation request includes complaint, resource, capacity, partner,
      billing, stock, staffing, approval, and outcome evidence.
- [x] Recommendation response separates facts, inferences, assumptions, missing
      evidence, recommended actions, blocked actions, approval requirements,
      and expected outcomes.
- [x] Agentforce refuses diagnosis, treatment, dosage, triage, and clinical
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

### 7A. Signal Intake And Channel Routing

- [x] Document that inbound channels create `Signal` and `Evidence`, while
      outbound channels execute approved `Action` records.
- [x] Document WhatsApp as the preferred customer/patient complaint intake
      story.
- [x] Document Slack as internal worker and manager coordination.
- [x] Document WhatsApp outbound as either urgent internal mobile alert or
      approved customer acknowledgement.
- [x] Document email as a future protected action adapter, not a current live
      capability.
- [x] Verify live outbound Slack delivery when `SLACK_WEBHOOK_URL` is
      configured.
- [x] Verify live outbound WhatsApp delivery when Twilio Sandbox credentials are
      configured.
- [ ] Implement or simulate a Twilio inbound WhatsApp webhook that maps customer
      complaint text to `INGEST_EVENT`.
- [ ] Add a Salesforce command-center complaint/signal intake fallback for demo
      reliability.
- [ ] Convert inbound complaint text into a synthetic customer alias, source
      channel, timestamp, department/resource hints, correlation ID, and
      evidence ID.
- [ ] Trigger or request an Agentforce recommendation from the newly stored
      intake evidence.
- [ ] Show the manager approval step before Slack, WhatsApp, vendor, pharmacy,
      billing, refund, email, or customer-facing response execution.
- [ ] Add optional email/vendor notification only behind the protected action
      boundary if time remains.
- [ ] Add a demo script beat: WhatsApp complaint enters, Salesforce stores
      evidence, agents create an action plan, manager approves, Slack alerts
      staff, WhatsApp sends approved reply or internal mobile alert, outcomes
      update.

### 8. Voice Mode

- [x] Add voice transcript request panel or fixture path.
- [x] Add optional browser speech capture when the browser supports it; the
      manual transcript fixture remains the reliable fallback.
- [x] Convert transcript into structured hospital operations request fields:
      issue, department, location, resource, urgency, requester role, and
      evidence.
- [x] Voice mode can ask Agentforce for a recommendation.
- [x] Voice mode cannot execute Slack, WhatsApp, vendor, pharmacy, billing,
      room/bed, staff-task, or patient-message actions directly.
- [x] Voice mode refuses clinical decision requests.
- [x] LWC or fixture tests cover transcript-to-request, protected-action
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
- [x] Voice transcript or voice request panel is visible if voice mode is in
      the demo.
- [x] Outcome panel shows wait time reduced, bed released, stockout avoided,
      complaint containment, vendor SLA, billing resolution, and task
      completion.
- [x] LWC tests cover ready, loading, empty, denied, error, restricted,
      approval, action, outcome, voice, and clinical-refusal states.

### 10. End-To-End Demo

- [x] `npm run check` passes in the intended demo environment.
- [x] `npm run demo:reset` works.
- [x] `npm run demo:seed` creates the hospital operations case.
- [x] `npm run demo:run` completes trigger through outcome.
- [x] Clean-clone runbook reflects the hospital/global flow.
- [x] Demo starts from one clear hospital operations surge event.
- [x] Demo shows conflicting recommendations before orchestration.
- [x] Demo shows partner or capacity response changing the recommendation.
- [x] Demo shows manager approval before action execution.
- [x] Demo shows Slack and WhatsApp-style internal alerts.
- [x] Demo shows clinical-decision refusal.
- [x] Demo shows outcome metrics and audit trail.
- [ ] Final rehearsal completed with the whole team.

### 11. Pitch And Presentation

- [x] Problem slide explains universal issue modules and the hospital demo.
- [x] Agent slide explains the orchestrator, global primitives, and specialist
      agents.
- [x] Salesforce slide explains Agentforce, Salesforce records, MuleSoft mocks,
      and approval boundary.
- [x] Demo slide shows the exact live flow.
- [x] Business value slide quantifies wait time reduced, bed released, stockout
      avoided, billing risk contained, vendor SLA, and complaint containment.
- [x] Plug-and-play slide maps hospital resources to hotel, airport, banking,
      and supermarket equivalents.
- [x] Honesty slide states what is mocked, what is production-ready
      architecture, and what clinical decisions are out of scope.
- [ ] Timing has been rehearsed.

## Final Manual Gates

These items remain intentionally unchecked until Fahan, Hassan, Aarav, and
Ranveer have actually done them together. Do not check them just because the
repo has code for the demo.

- Final non-goals review: the whole team must agree to say that North Star is
  not a generic chatbot, does not make clinical decisions, does not use real
  patient data, and uses mock hospital/channel integrations unless credentials
  are configured live.
- Merge owner gate: one person must pull latest, confirm `origin/main` contains
  the final demo commit, protect or freeze `main`, resolve any teammate branch
  conflicts, and run `npm run check` after the final merge.
- Salesforce/Agentforce gate: one connected org alias, normally `hfs-dev`, must
  deploy the metadata, assign the demo permission sets, seed the hospital case,
  and pass `npm run demo:run -- --target-org hfs-dev`.
- Current connected evidence: on 2026-06-11, `hfs-dev` deployed `force-app`
  with `HFS_ServiceContractTest`, `HFS_RelationshipServiceImplTest`,
  `HFS_AgentActionServiceTest`, and `HFS_RelationshipControllerTest` passing;
  `npm run demo:reset`, `npm run demo:seed`, and the connected demo run passed;
  the live-channel run wrote
  `artifacts/demo-harness-result-live-channels-simple-language.json`. The
  connected run completed the work item with 10 actions, 11 outcomes, 11
  evaluations, `CLINICAL_DECISION_REFUSED`, `SEND_SLACK_ALERT.status = SENT`,
  and `SEND_WHATSAPP_ALERT.status = SENT`. This proves approved outbound
  channels, not live inbound WhatsApp customer intake.
- Channel credential gate: Slack uses `SLACK_WEBHOOK_URL` only if the team wants
  a real Slack webhook; WhatsApp-style delivery uses Twilio or Meta credentials
  only if they are configured outside Git. Missing credentials are acceptable
  only when the presenter clearly says the result is `MOCK_SENT`.
- Final rehearsal gate: the whole team must run the three-minute pitch at least
  twice, use the timing table in `docs/north-star-demo-narrative.md`, confirm the
  backup recorded/mock path, and assign who speaks for Salesforce, Agentforce,
  MuleSoft, LWC, data, and business value.

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
