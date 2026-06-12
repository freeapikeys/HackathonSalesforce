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

North Star is general first. Core agents, action contracts, primitives, and IDs
must stay sector-neutral; the hospital is one profile that renders those
primitives with hospital words for the demo.

General profile and action IDs:

- `profile:hospital-private-large`
- `profile:airport-operations`
- `profile:hotel-guest-operations`
- `profile:bank-service-operations`
- `resource:room`
- `resource:stock-item`
- `resource:service-counter`
- `action:send-internal-alert`
- `action:create-service-task`
- `action:request-partner-followup`

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
| NS-01 | Complaint and trust              | Customer Trust          | Cluster complaints, classify cause, draft approved service response      |
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
| HOS-01 | Patient wait-time complaints            | Customer Trust        | Cluster complaints, cite queue evidence, draft service response           |
| HOS-02 | Room readiness or cleanliness complaint | Customer Trust        | Link complaint to blocked room, housekeeping task, and manager escalation |
| HOS-03 | Discharge bed blocked                   | Resource and Capacity | Detect blocked beds, assign cleaning/porter task, estimate bed release    |
| HOS-04 | Outpatient queue spike                  | Resource and Capacity | Predict queue risk and recommend staff movement                           |
| HOS-05 | Pharmacy supply running low             | Resource and Capacity | Calculate stock days remaining and request approved restock or transfer   |
| HOS-06 | Lab vendor response delayed             | Partner and Vendor    | Escalate vendor case and update recommendation when response arrives      |
| HOS-07 | Insurance approval stuck                | Financial Impact      | Open approved insurance follow-up and estimate claim-delay exposure       |
| HOS-08 | Duplicate billing or refund complaint   | Financial Impact      | Open billing review, require approval for refund or compensation          |
| HOS-09 | Food or hospitality complaint           | Customer Trust        | Route food-service task and approved patient-safe message                 |
| HOS-10 | Accessibility support missing           | Operations Execution  | Assign wheelchair/porter/support task and track acknowledgement           |
| HOS-11 | Equipment or maintenance unavailable    | Partner and Vendor    | Check resource status, vendor SLA, and fallback options                   |
| HOS-12 | Privacy or safety-sensitive complaint   | Risk and Approval     | Escalate, preserve evidence, and prevent unsafe message/action            |
| HOS-13 | Clinical-decision request               | Risk and Approval     | Refuse diagnosis/treatment/triage decision and route to clinician         |
| HOS-14 | Multi-department morning surge          | Orchestrator          | Create one action plan across trust, capacity, vendor, billing, and tasks |

## Agent Responsibilities

### North Star Orchestrator

- [x] Combine customer trust, resource capacity, partner/vendor, financial,
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

### Customer Trust Agent

- [x] Detect customer complaint clusters. In the hospital profile, customers
      render as patients and visitors.
- [x] Classify complaints into wait time, room readiness, cleanliness, food,
      billing, discharge delay, lost item, accessibility, privacy, safety,
      pharmacy delay, and staff interaction.
- [x] Connect complaints to location, department, resource, time window,
      partner, and evidence.
- [x] Draft approved service response or customer-facing message text.
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

- accept a customer or patient complaint through Meta WhatsApp Cloud API;
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
- [x] Core profile, resource, and action ID examples are documented as
      sector-neutral (`profile:*`, `resource:*`, `action:*`).
- [x] Hospital wording is documented as profile display/demo data, not core
      architecture.
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
- [ ] Aarav: prepare the final no-credential demo QA pack: multilingual
      complaint scripts, voice-note transcript scripts, document/image evidence
      scenarios, expected agent routing, and judge-sector mapping examples.
- [x] Fahan: preserve and hospitalize `SEND_SLACK_ALERT` behind approved
      MuleSoft action execution, with real webhook support only through
      `SLACK_WEBHOOK_URL` and honest `MOCK_SENT` fallback.
- [ ] Hassan: finish the official Meta WhatsApp customer channel solo:
      same-language receipts and approved replies, pretrained multilingual and
      voice-model evidence, DeepSeek-compatible chat drafts, judge-sector use
      cases, and no clinical or protected action bypass.
- [x] Ranveer: finish the internal execution proof: signed Slack approval
      harness plus command-center fallback, command-center action/outcome
      trace, protected vendor-email mock proof, and resource/capacity workflows
      that show depth.
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
- [x] Re-verified Aarav's canonical hospital data on 2026-06-12 after pulling
      `origin/main`: `npm run check:demo-data` passed with 90 resources, 60
      complaints, 15 recommendation cases, and 20 hospital events.
- [x] Re-verified the hospital fixture wording on 2026-06-12:
      `npm run check:fixture-language` passed without introducing real patient,
      staff, vendor, phone, email, credential, or clinical-decision data.

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
- [x] Define/update Customer Trust topic.
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
- [x] Document optional specialist skills that support the 10 agents without
      creating a separate architecture.
- [x] Show the agent handoff trace in the command center: which agent found
      facts, which agent inferred risk, which agent required approval, and
      which agent executed or measured the outcome.
- [x] Replace the generated 8-topic hospital labels with the universal 10-agent
      Agentforce source model.
- [x] Replace the default Studio welcome/role text with North Star operations
      language.
- [x] Agentforce source instructs "I have a problem" to ask one short follow-up.
- [x] Agentforce source keeps hospital words inside the active profile and uses
      universal primitive/action wording for the core.

### 7. MuleSoft And Channel Mocks

- [x] Mock `CREATE_PATIENT_SERVICE_TASK`.
- [x] Mock `REQUEST_BED_CLEANING`.
- [x] Mock `ESCALATE_LAB_VENDOR_CASE`.
- [x] Mock `CREATE_PHARMACY_RESTOCK_REQUEST`.
- [x] Mock `OPEN_BILLING_REVIEW`.
- [x] Mock `REQUEST_INSURANCE_FOLLOWUP`.
- [x] Mock `SEND_SLACK_ALERT`.
- [x] Mock `SEND_WHATSAPP_ALERT`.
- [x] Mock `SEND_VENDOR_EMAIL` as an approved protected vendor/supplier follow-up.
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
- [x] Support signed Slack approval interactions in the mock runtime and
      harness with `SLACK_SIGNING_SECRET` outside Git.
- [x] Slack approval keeps protected actions blocked until a valid signed
      approve decision is received.

### 7A. Signal Intake And Channel Routing

- [x] Document that inbound channels create `Signal` and `Evidence`, while
      outbound channels execute approved `Action` records.
- [x] Document WhatsApp as the preferred customer/patient complaint intake
      story.
- [x] Document Meta WhatsApp Cloud API as the active WhatsApp provider for the
      hackathon. Twilio Sandbox is legacy backup only.
- [x] Document Slack as internal worker and manager coordination.
- [x] Document WhatsApp outbound as either urgent internal mobile alert or
      approved customer acknowledgement.
- [x] Document email as a protected mock action for vendor/supplier follow-up,
      not a current live email capability.
- [x] Verify live outbound Slack delivery when `SLACK_WEBHOOK_URL` is
      configured.
- [x] Verify live outbound WhatsApp delivery when Meta WhatsApp Cloud API
      credentials are configured.
- [x] Implement or simulate a provider-neutral inbound WhatsApp webhook that
      maps customer complaint text to `INGEST_EVENT`.
- [x] Add Salesforce Apex REST intake endpoint
      `/services/apexrest/northstar/v1/twilio/whatsapp` so live MuleSoft
      intake can create a command-center case.
- [x] Add deployable Mule app `mulesoft/north-star-twilio-webhook` for official
      Meta WhatsApp Cloud API intake. The app name is inherited from the first
      Twilio bridge, but the active route accepts Meta payloads.
- [x] Keep the existing Salesforce command center as the visibility, approval,
      and fallback surface instead of adding a new complaint form.
- [x] Convert inbound complaint text into a synthetic customer alias, source
      channel, timestamp, department/resource hints, correlation ID, and
      evidence ID.
- [x] Add deterministic follow-up questions, root-cause hypotheses,
      next-evidence needs, and affected primitives for inbound complaints.
- [x] Ensure inbound WhatsApp mapping does not store raw phone number or raw
      complaint text in the preserved demo event.
- [x] Add harness evidence that newly stored intake can request an Agentforce
      recommendation without executing protected actions.
- [x] Show the manager approval step before Slack, WhatsApp, vendor, pharmacy,
      billing, refund, email, or customer-facing response execution.
- [x] Add protected mock email/vendor notification behind the protected action
      boundary.
- [ ] Add live email/vendor delivery only if Anypoint/SMTP credentials are
      configured safely outside Git.
- [x] Add signed Slack approval buttons in the mock runtime and harness.
- [ ] Configure a public Slack App interactivity Request URL for live button
      clicks during final rehearsal.
- [x] Package/deploy the WhatsApp webhook Mule app to CloudHub and verify the
      public endpoint creates Salesforce event, evidence, recommendation, and
      approval records.
- [x] Verify the CloudHub WhatsApp endpoint also accepts Meta WhatsApp Cloud API
      JSON, returns Meta webhook challenge text for a valid verify token, and
      creates Salesforce intake records.
- [x] Add Meta Cloud API outbound acknowledgement path after Salesforce intake,
      gated by CloudHub secure `meta.whatsappAccessToken` and
      `meta.whatsappPhoneNumberId`.
- [x] Agentforce and docs define English, French, and Mauritian Creole as safe
      same-language reply targets for short operational responses.
- [x] Extend the live WhatsApp inbound mapper to persist detected language and
      reply-language preference for English, French, and Mauritian Creole.
- [x] Extend WhatsApp intake records for voice, image, and document media
      metadata without storing raw media URLs; transcript or extraction
      confidence remains pending evidence before protected action.
- [x] Point Meta WhatsApp Cloud API callback URL to the public CloudHub webhook
      URL in Meta App Dashboard and subscribe the `messages` webhook field. Use
      verify token `north-star-meta-verify`.
- [ ] Replace the short-lived Meta WhatsApp access token with a permanent
      system-user token before final rehearsal.
- [ ] Replace the temporary Salesforce session token in CloudHub with a
      Connected App/JWT path or refresh the secure property immediately before
      final rehearsal.
- [x] Stop using Twilio as the primary WhatsApp demo path; keep it only as
      legacy backup/context because the Mule app and Apex route still have
      inherited Twilio names.
- [ ] Hassan: convert the visible Meta WhatsApp acknowledgement from a fixed
      receipt into a short same-language response for English, French, and
      Mauritian Creole.
- [ ] Hassan: add Meta WhatsApp voice-note download/transcription evidence, or
      mark the voice note as pending transcript with one short follow-up.
- [ ] Hassan: add Meta WhatsApp image/document evidence extraction or
      low-confidence follow-up handling.
- [ ] Hassan: integrate his pretrained multilingual/voice models behind an
      adapter that records language, transcript, extraction, confidence, and
      evidence IDs without committing model endpoints, local paths, or secrets.
- [ ] Hassan: add a DeepSeek-backed or DeepSeek-compatible chat-draft path for
      safe WhatsApp replies. It may draft language, but it must not approve,
      execute, make clinical decisions, decide refunds, or bypass evidence.
- [ ] Hassan: build WhatsApp/chat use-case mappings for hospital, hotel,
      airport, and banking judges using the same global primitives rather than
      separate architectures.
- [x] Ranveer: rehearse live Slack approve/reject/modify buttons with a public
      Slack App interactivity Request URL, or document the command-center
      fallback used in the demo.
- [x] Ranveer: make the command center visibly show that one WhatsApp complaint
      expanded into customer trust, resource/capacity, stock, billing,
      communication, approval, action, and outcome work.
- [ ] Add WhatsApp approval templates only if approved templates are available;
      otherwise keep WhatsApp as intake/outbound alert, not approval surface.
- [x] Add a demo script beat: WhatsApp complaint enters MuleSoft intake,
      evidence is preserved, agents create an action plan, manager approves,
      Slack alerts staff, WhatsApp sends approved reply or internal mobile
      alert, outcomes update.

### 7B. Deep Resolution Differentiator

This is how North Star should beat a normal assistant that only apologizes or
notifies a manager.

- [x] Define the deeper investigation pattern: classify, ask follow-up
      questions, find affected resources, estimate risk, require approval,
      execute, and measure outcome.
- [x] Add deterministic root-cause hypotheses to inbound complaint intake.
- [x] Add next-evidence needs so agents ask for the missing operational facts
      instead of guessing.
- [x] Display follow-up questions and missing evidence in the command center
      when an inbound complaint starts the case.
- [x] Add a demo scenario where one complaint expands into at least four
      affected functions: customer trust, capacity, inventory, billing, and
      communication.
- [x] Add an outcome comparison showing what changed after the actions, not
      just that messages were sent.
- [x] Add cross-sector explanation cards mapping the same issue to airport,
      hotel, banking, supermarket, and cruise equivalents.
- [x] Add a "why this is deeper than a chatbot" pitch beat with evidence,
      approval, protected actions, and outcome learning.

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
- [ ] Add document/image intake evidence fixtures with low-confidence
      extraction follow-up.
- [ ] Aarav: write fake voice-note transcripts and document/image scenario
      descriptions that Hassan can use to test Meta WhatsApp media handling
      without needing live customer media, real files, or API secrets.

### 9. Lightning Command Center

- [x] UI title and labels use North Star global/hospital operations language.
- [x] UI shows universal primitive/profile mapping before the active hospital
      rendering.
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
- [x] Demo harness shows WhatsApp complaint intake before Agentforce
      recommendation and Slack approval.
- [x] Demo harness shows protected mock vendor email after approval.
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
- [ ] Aarav: add the final judge-demo script pack with at least 12 safe
      complaint prompts across English, French, and Mauritian Creole, expected
      follow-up questions, affected agents, protected actions, and outcomes.
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
- Current connected evidence: on 2026-06-11, `force-app` deployed to `hfs-dev`
  with 20 specified Apex tests passing, then `hfs-dev` ran
  `npm run demo:run -- --target-org hfs-dev --output
artifacts/demo-harness-result-current.json` successfully. The connected run
  proved Twilio Sandbox complaint intake mapping, Agentforce recommendation,
  clinical refusal, manager approval, signed Slack approval proof,
  pre-approval MuleSoft denial, and approved Slack, WhatsApp, vendor-email, and
  task outcomes. It completed the work item with 11 actions, 12 outcomes, 12
  evaluations, 13 events, `CLINICAL_DECISION_REFUSED`,
  `SEND_SLACK_ALERT.status = MOCK_SENT`,
  `SEND_WHATSAPP_ALERT.status = MOCK_SENT`, and
  `SEND_VENDOR_EMAIL.status = QUEUED`. This proves the governed end-to-end path;
  real outbound channel delivery still depends on credentials being visible to
  the running process.
- Agentforce Studio gate: the universal 10-agent metadata is deployed and
  activated as `North_Star_Hospital_Operations` version 2 in `hfs-dev`. The live
  preview now responds to "I have a problem" with "What happened?" and mixed
  issues produce the North Star primitive trace, agent handoff, approval gate,
  proposed actions, and outcome metric. The Windows recovery path is documented
  in `docs/agentforce-publish-recovery.md`.
- Channel credential gate: Slack uses `SLACK_WEBHOOK_URL` for outbound alerts
  and `SLACK_SIGNING_SECRET` plus a public Slack App interactivity URL for live
  approve/reject buttons. WhatsApp uses official Meta WhatsApp Cloud API for
  the hackathon demo. Twilio Sandbox is legacy backup only. Missing credentials
  are acceptable only when the presenter clearly says the result is `MOCK_SENT`
  or a signed local harness proof.
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
