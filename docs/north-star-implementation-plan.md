# North Star Implementation Plan

## Goal

Convert the existing HFS vertical slice into a North Star universal operations
MVP with a private hospital demo profile, without weakening the governed
Salesforce, Agentforce, MuleSoft, model gateway, LWC, and harness contracts
already present in the repository.

The first task is specialization through global primitives and a hospital
profile, not reinvention. Keep the core general: profile IDs, primitive IDs,
agent names, action IDs, and skill names must be sector-neutral. Hospital terms
belong in the active profile rendering and demo data only.

## Current Starting Point

The repository already has:

- Salesforce custom objects for event, entity, relationship, agreement, work,
  evidence, recommendation, approval, action, outcome, and evaluation;
- Apex services and Agentforce invocable actions;
- MuleSoft OpenAPI and Python mock runtime;
- provider-neutral model gateway and fixtures;
- Lightning command center component and state adapter;
- deterministic seed, reset, and end-to-end harness scripts;
- Slack approved-action support on the current branch;
- Agentforce inventory and waste reasoning work from latest `origin/main`.

Preserve those assets. Generalize them where needed instead of replacing them
with a new architecture.

## Workstream 1: Global Primitive Mapping

Tasks:

1. Map private-hospital concepts onto global primitives.
2. Use existing HFS records before adding metadata.
3. Keep the model reusable for hotel, airport, banking, supermarket, and other
   profiles.
4. Use general IDs such as `profile:hospital-private-large`,
   `resource:room`, `resource:stock-item`, `resource:service-counter`,
   `action:send-internal-alert`, `action:create-service-task`, and
   `action:request-partner-followup`.

Initial mapping:

| Hospital concept                                         | Global primitive       | HFS object                        |
| -------------------------------------------------------- | ---------------------- | --------------------------------- |
| Hospital, ward, department                               | `Entity` or `Location` | `HFS_Entity__c`                   |
| Patient or visitor alias                                 | `Customer`             | `HFS_Entity__c` or evidence alias |
| Bed, room, stock item, equipment, queue slot             | `Resource`             | `HFS_Entity__c`                   |
| Complaint, queue spike, low stock, vendor delay          | `Signal`               | `HFS_Event__c`                    |
| Complaint text, queue record, stock record, vendor reply | `Evidence`             | `HFS_Evidence__c`                 |
| Lab, laundry, insurer, payment processor, supplier       | `Partner`              | `HFS_Entity__c`                   |
| Discharge cleaning, billing review, restock, alert       | `Action`               | `HFS_Action__c`                   |
| Operations manager approval                              | `Approval`             | `HFS_Approval__c`                 |
| Wait reduced, bed released, stockout avoided             | `Outcome`              | `HFS_Outcome__c`                  |

Acceptance:

- no source label assumes supermarket-only or burger-only behavior;
- hospital concepts map through global primitives;
- protected action and approval contracts remain unchanged.

## Workstream 2: Hospital Demo Seed And Event Fixtures

Tasks:

1. Convert the demo story to a private hospital morning operations surge.
2. Add or update event fixtures for:
   - `PATIENT_COMPLAINT_CLUSTER_DETECTED`;
   - `BED_CAPACITY_PRESSURE_DETECTED`;
   - `DISCHARGE_ROOM_BLOCKED`;
   - `PHARMACY_STOCK_RISK_DETECTED`;
   - `LAB_VENDOR_RESPONSE_DELAYED`;
   - `BILLING_APPROVAL_STALLED`;
   - `STAFF_QUEUE_RISK_DETECTED`;
   - `APPROVED_ACTION_EXECUTED`;
   - `HOSPITAL_OUTCOME_CAPTURED`.
3. Keep duplicate, malformed, late, out-of-order, hash, replay, and
   idempotency-conflict cases.

Acceptance:

- `npm run check:events` passes;
- `npm run check:mulesoft` passes;
- `npm run demo:seed` creates one coherent hospital operations case.

## Workstream 3: Agentforce Topics And Actions

Agentforce topics:

- North Star Orchestration;
- Evidence and Context;
- Customer Trust;
- Resource and Capacity;
- Operations Execution;
- Partner and Vendor;
- Risk and Approval;
- Financial Impact;
- Communication;
- Outcome Learning.

Profile labels may adapt the same role for demo clarity. For example, Customer
Trust renders as patient or visitor trust in the hospital profile, guest trust
in a hotel profile, passenger trust in an airport profile, and client trust in a
banking profile.

Agentforce action catalog:

- explain North Star case;
- draft evidence-backed action plan;
- request manager approval;
- summarize partner or capacity response;
- draft internal staff alerts;
- draft patient-safe service message;
- refuse clinical decision requests.

Protected execution remains behind Salesforce approval and MuleSoft action
execution. Agentforce can draft and request approval, but it cannot directly
send Slack, WhatsApp, vendor, billing, pharmacy, staff-task, refund, or patient
message actions.

Acceptance:

- recommendations cite complaint, resource, capacity, vendor, billing, staff,
  stock, approval, and post-write-back outcome context through structured
  `contextCoverage`;
- facts, inference, assumptions, missing evidence, recommended actions,
  blocked clinical actions, approval requirements, and expected outcomes are
  separated;
- restricted or missing evidence fails closed.

Recovery note:

- If the live Agentforce Studio preview drifts back to generic Salesforce
  responses, use `docs/agentforce-publish-recovery.md` to validate, publish,
  activate, retrieve, and smoke test the latest
  `North_Star_Hospital_Operations` authoring bundle on Windows.

## Workstream 4: MuleSoft Mock Actions And Channels

Keep the existing Process API operations:

- `INGEST_EVENT` at `POST /v1/events`;
- `REPLAY_EVENT` at `POST /v1/events/replays`;
- `READ_CONTEXT` at `POST /v1/context/queries`;
- `EXECUTE_APPROVED_ACTION` at `POST /v1/actions/executions`;
- `CAPTURE_OUTCOME` at `POST /v1/outcomes/callbacks`.

Hospital mock actions behind `EXECUTE_APPROVED_ACTION`:

- `CREATE_PATIENT_SERVICE_TASK`;
- `REQUEST_BED_CLEANING`;
- `ESCALATE_LAB_VENDOR_CASE`;
- `CREATE_PHARMACY_RESTOCK_REQUEST`;
- `OPEN_BILLING_REVIEW`;
- `REQUEST_INSURANCE_FOLLOWUP`;
- `SEND_SLACK_ALERT`;
- `SEND_WHATSAPP_ALERT`;
- `SEND_VENDOR_EMAIL`;
- `CAPTURE_HOSPITAL_OUTCOME`.

Slack:

- use a real incoming webhook when `SLACK_WEBHOOK_URL` exists;
- otherwise preserve an honest `MOCK_SENT` result.

WhatsApp:

- use Meta WhatsApp Cloud API as the active hackathon demo provider;
- keep Twilio Sandbox as legacy backup only;
- the current CloudHub public callback URL is
  `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound`;
  despite the inherited path name, it accepts Meta JSON and Twilio form payloads;
- the current visible Meta WhatsApp reply is a receipt acknowledgement, not the
  full agent conversation;
- outbound WhatsApp may be used for urgent internal mobile alerts or approved
  customer acknowledgements;
- inbound WhatsApp should be modeled as signal intake through `INGEST_EVENT`,
  not as an approved action execution;
- otherwise use an honest WhatsApp-style internal alert mock.

Email:

- model vendor email as protected action `SEND_VENDOR_EMAIL`;
- the current MVP can queue a protected mock vendor/supplier email after
  approval;
- do not claim live email delivery until an Anypoint, SMTP, or provider-backed
  adapter exists and passes tests.

Slack approval:

- use `SLACK_WEBHOOK_URL` for outbound internal alerts;
- use `SLACK_SIGNING_SECRET` and Slack App Interactivity for true approve/reject
  buttons;
- the local mock runtime and harness validate Slack signatures and keep
  protected actions blocked until a signed approve decision is processed;
- Salesforce command-center approval remains the fallback when no public Slack
  Request URL is available.

Acceptance:

- unapproved action execution returns denial;
- approved action execution returns queued, success, or honest mock status with
  correlation IDs;
- channel results are visible in the command center.

## Workstream 4A: Customer And Staff Signal Intake

This is the missing "front door" for the demo. North Star needs a credible path
for complaints and operational signals to enter the system before agents can
reason over them.

Preferred intake paths:

1. WhatsApp inbound through Meta WhatsApp Cloud API for customer, patient,
   visitor, or client complaints.
2. Existing Salesforce command center for visibility, approval, and fallback
   review. A new intake form is not required for hackathon v1.
3. System event fixtures for queue spike, low stock, vendor delay, billing
   issue, room readiness, or equipment issue.
4. Manual or voice transcript request for staff asking what to do next.

Inbound WhatsApp flow:

1. Customer sends a WhatsApp message to the configured WhatsApp number.
2. Meta WhatsApp Cloud API posts the webhook payload to the public CloudHub
   webhook URL:
   `https://<cloudhub-host>/twilio/whatsapp/inbound`.
3. Mule maps the message to the Salesforce Apex REST intake endpoint at
   `/services/apexrest/northstar/v1/twilio/whatsapp`.
4. Salesforce stores the signal, synthetic customer alias, evidence, work item,
   recommendation, and pending approval. No diagnosis, treatment, dosage,
   triage, clinical priority, personal medical record, raw phone number, or raw
   message text is stored in demo records.
5. Agentforce drafts an action plan from the new evidence.
6. A manager approves protected actions.
7. MuleSoft sends approved Slack, WhatsApp, vendor, billing, stock, task, or
   protected mock vendor-email actions.
8. Outcomes return to Salesforce and update the command center.

Language, voice, and document handling:

- English, French, and Mauritian Creole messages use the same universal intake
  contract and should reply in the same language when the reply is safe.
- Current Salesforce intake stores language hints for English, French, and
  Mauritian Creole. The live Meta receipt still needs same-language response
  wording before it should be pitched as multilingual customer chat.
- Hassan owns the multilingual and voice-model lane. He may use his own
  pretrained multilingual or voice models for language detection, translation,
  transcription, and confidence scoring, provided they stay behind a safe
  adapter boundary and do not introduce secrets, raw personal data, raw media,
  or provider-specific core IDs into the repo.
- Hassan may use DeepSeek for customer chat drafts or same-language response
  drafting. DeepSeek output is advisory draft text only; it must not approve
  actions, execute MuleSoft actions, decide refunds, make clinical decisions,
  or overwrite evidence.
- Voice notes currently become media metadata and pending evidence. A real
  Meta media download and transcription step is still required before voice
  mode can be pitched as live WhatsApp voice understanding.
- Documents and images currently become evidence metadata. OCR or document
  extraction is still required before they can be pitched as live document
  understanding. Extraction is only evidence support; clinical, legal, or
  financial final decisions still require human approval.

Implemented bridge:

- Salesforce endpoint:
  `/services/apexrest/northstar/v1/twilio/whatsapp`.
- Mule app: `mulesoft/north-star-twilio-webhook`.
- Current deployed CloudHub webhook:
  `https://north-star-twilio-webhook-fahan-fp4vdx.5sc6y6-2.usa-e2.cloudhub.io/twilio/whatsapp/inbound`.
- Use the same URL as the Meta WhatsApp Cloud API callback URL with verify token
  `north-star-meta-verify`.
- Public hosting requires packaging/deploying the Mule app to CloudHub and
  setting the active WhatsApp provider inbound Request URL to the public webhook
  URL.

Acceptance:

- inbound complaint text can become a `Signal` and `Evidence` record;
- source channel and correlation ID are preserved;
- personal contact data and raw text are masked or represented by hashes,
  synthetic aliases, and safe summaries;
- Agentforce uses the new evidence in its recommendation;
- customer-facing replies are not sent without approval;
- clinical requests are refused or routed to a clinician;
- the command center shows the intake source, evidence, approval, action, and
  outcome.
- the CloudHub Salesforce credential is refreshed before rehearsal or replaced
  with a Connected App/JWT credential path.

## Workstream 5: North Star Command Center

Update the Lightning command center from retail operations wording to universal
core wording with a hospital profile rendering.

Required panels:

- risk pulse cards: complaint, bed capacity, pharmacy stock, vendor delay,
  queue, billing, approval, and outcome;
- patient/visitor alias, department, location, and resource context;
- evidence timeline;
- agent reasoning with facts and inferences;
- partner/vendor response panel;
- approval cockpit;
- Slack and WhatsApp-style alert log;
- outcome metrics.
- cross-sector mapping cards proving the same universal issue can render as
  hospital, hotel, airport, banking, supermarket, or cruise wording.

Acceptance:

- mock mode works without live Salesforce data;
- live mode works from `HFS_RelationshipController`;
- UI labels use global/hospital language, not supermarket-only language;
- LWC tests cover ready, restricted, denied, error, approval, action, and
  outcome states.

## Workstream 6: End-To-End Proof Path

Required beats:

1. Launch hospital operations surge event.
2. Show conflicting evidence.
3. Ask Agentforce for recommendation.
4. Receive partner/capacity response.
5. Show recommendation update.
6. Approve.
7. Log eight approved Salesforce task action records with owner role aliases,
   escalation role aliases, priority ranks, approval requirement, service
   windows, and missed-task escalation windows.
8. Execute approved Slack and WhatsApp-style MuleSoft channel actions.
9. Show outcome and audit trail.

## Implementation Guardrails

Every contributor should understand the universal model and the hospital demo
profile.

Approval here means business approval by a demo role such as Operations
Manager, Bed Manager, Pharmacy Lead, Billing Supervisor, Patient Experience
Manager, or Duty Manager. It does not require the demo user to be a Salesforce
org admin.

Rules:

- do not make diagnosis, treatment, dosage, triage, or clinical priority
  decisions;
- do not use real patient names, medical records, phone numbers, emails,
  insurer records, or hospital credentials;
- every protected action requires a business manager approval record/status
  before MuleSoft execution;
- Slack and WhatsApp integrations must have honest fallback modes when real
  credentials are unavailable;
- run focused checks before handing off;
- keep a backup recorded demo path if live channels fail.

Focused checks:

| Surface                  | Minimum focused checks                                                                                                                                                 |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Salesforce core          | `npm run check:project`, Apex tests for recommendation, approval, evidence, action, and outcome behavior                                                               |
| Agentforce contracts     | `npm run check:agentforce`, refusal checks, evidence citation checks                                                                                                   |
| MuleSoft and channels    | `npm run check:mulesoft`, approved action execution path, denied path, channel fixtures                                                                                |
| Lightning command center | LWC unit tests, UI mock fixture render, ready/restricted/denied/error/approval states                                                                                  |
| Event and data fixtures  | `npm run check:demo-data`, `npm run check:fixture-language`, fixture schema validation, malformed/late/duplicate/out-of-order examples, expected recommendation review |

## Build Checklist

### Customer Complaint And Signal Intake

- [x] Document channel direction: inbound creates `Signal` and `Evidence`;
      outbound executes approved `Action` records.
- [x] Document WhatsApp as the preferred customer/patient complaint intake
      channel.
- [x] Document Meta WhatsApp Cloud API as the active WhatsApp provider and
      Twilio Sandbox as legacy backup only.
- [x] Document Slack as internal worker and manager coordination.
- [x] Document WhatsApp outbound as urgent internal mobile alert or approved
      customer acknowledgement.
- [x] Document email as a protected mock vendor/supplier action, not a current
      live delivery capability.
- [x] Add or simulate a provider-neutral inbound WhatsApp webhook that maps
      customer complaint text to `INGEST_EVENT`.
- [x] Keep existing Salesforce command center as the visibility, approval, and
      fallback review surface instead of adding a new intake screen.
- [x] Convert inbound text into synthetic customer alias, source channel,
      timestamp, department/resource hints, correlation ID, and evidence ID.
- [x] Add root-cause hypotheses, follow-up questions, next-evidence needs, and
      affected primitives for inbound complaint intake.
- [x] Ensure raw phone number and raw message text are not preserved in the demo
      event.
- [x] Ensure the new intake evidence can trigger or request an Agentforce
      recommendation in the harness proof.
- [x] Block customer-facing replies until manager approval and privacy-safe
      wording checks pass.
- [x] Add tests or harness evidence for WhatsApp complaint intake through
      recommendation, approval, Slack alert, WhatsApp response, and outcome.
- [x] Add protected mock email/vendor adapter behind the approval boundary.
- [ ] Add live email/vendor delivery only if credentials and provider routing
      can stay outside Git.

### Slack And Approved MuleSoft Execution

- [x] Inspect `docs/mulesoft-api-contract.md`, `mulesoft/README.md`, and the
      existing MuleSoft mock runtime.
- [x] Ensure `EXECUTE_APPROVED_ACTION` supports `SEND_SLACK_ALERT` with
      correlation ID, approval ID, action ID, channel, target role, message
      body, delivery status, and fallback reason.
- [x] Add a Slack configuration path that can use `SLACK_WEBHOOK_URL` when it
      exists and returns honest `MOCK_SENT` when it is missing.
- [x] Make unapproved Slack execution fail closed.
- [x] Store or return enough delivery evidence for Salesforce and the command
      center to show `PENDING`, `SENT`, `FAILED`, or `MOCK_SENT`.
- [x] Add or update fixtures for approved Slack success, missing-webhook mock
      mode, and unapproved denial.
- [x] Update Slack examples and labels from retail roles to hospital roles.
- [x] Run MuleSoft contract generation, contract validation, and mock runtime
      tests after hospital action changes.
- [x] Add signed Slack approval interaction handling with replay and invalid
      signature tests.
- [x] Add harness proof that pending approval blocks execution until Slack
      approve is processed.
- [ ] Configure Slack App Interactivity Request URL for final live button
      rehearsal.

### Salesforce Core And Agentforce Recommendation

- [x] Inspect `docs/salesforce-data-model.md`,
      `docs/agentforce-action-contract.md`, `docs/apex-service-contract.md`, and
      the Apex service classes before editing.
- [x] Confirm the Salesforce records can represent patient alias, department,
      resource, partner, complaint evidence, approval, action, and outcome.
- [x] Add or update seed data for hospital departments and reusable global
      resources.
- [x] Wire Agentforce-facing outputs so recommendations cite facts, separate
      inferences, and name missing evidence.
- [x] Ensure the orchestrator recommendation includes customer trust, resource
      capacity, partner/vendor, financial, and operations execution
      implications.
- [x] Preserve clinical refusal and manager approval boundaries.
- [x] Run `npm run check:project` plus the relevant Apex/Agentforce checks.

### WhatsApp And Command Center Experience

- [x] Inspect `docs/ui-state-contract.md`, `docs/mulesoft-api-contract.md`, the
      LWC command center, and existing UI fixtures before editing.
- [x] Ensure `EXECUTE_APPROVED_ACTION` supports `SEND_WHATSAPP_ALERT` with the
      same approval, correlation, target role, message, delivery status, and
      fallback fields as Slack.
- [x] Add a WhatsApp configuration path that can use Meta Cloud API when
      credentials are configured, otherwise returns
      `MOCK_SENT` honestly.
- [ ] Add same-language Meta WhatsApp receipt and approved-response wording for
      English, French, and Mauritian Creole.
- [ ] Add Meta WhatsApp voice-note download/transcription evidence or a clear
      pending-transcript follow-up path.
- [ ] Add Meta WhatsApp image/document evidence extraction or low-confidence
      follow-up handling.
- [ ] Add Hassan's pretrained multilingual/voice models through logical
      capabilities such as `language_detection`, `voice_transcription`,
      `message_drafting`, and `customer_reply_drafting`; do not hard-code
      provider names into core architecture.
- [ ] Add a DeepSeek-backed or DeepSeek-compatible chat-draft path with mock or
      local fallback, confidence/audit metadata, and tests proving protected
      actions remain manager-approved.
- [ ] Add Hassan-owned judge-sector WhatsApp/chat use cases for hospital,
      hotel, airport, and banking, all mapped through the same primitives.
- [x] Update the command center to show hospital risk pulse, evidence timeline,
      vendor response, approval cockpit, Slack result, WhatsApp result, and task
      acknowledgement.
- [x] Add UI mock states for ready, restricted, denied, channel failed, channel
      mock sent, voice request, clinical refusal, and action approved.
- [x] Add optional browser speech capture for supported browsers while keeping
      manual transcript fixtures as the stable demo fallback.
- [x] Run LWC tests and direct MuleSoft checks when the WhatsApp contract
      changes.

### Data, Edge Cases, And Recommendation Validation

- [x] Build synthetic hospital data for departments, resources, partners,
      complaints, queues, stock, billing, insurance, tasks, channel aliases, and
      outcomes.
- [x] Create an initial realistic complaint cluster for wait time, room
      readiness, billing, pharmacy delay, and service response.
- [x] Add complaint variants for isolated complaints, food, accessibility,
      privacy, and staff interaction.
- [x] Create initial partner response examples for lab delay and
      billing/insurance follow-up.
- [x] Add partner response variants: lab recovered, insurance approved,
      laundry delayed, food supplier delayed, and maintenance unresolved.
- [x] Create late, malformed, duplicate, out-of-order, idempotency-conflict, and
      invalid-hash event examples.
- [x] Write expected recommendation notes for each scenario: what North Star
      should recommend, what it should refuse to do, what needs approval, and
      what evidence is missing.
- [x] Validate manually that the final system never makes diagnosis, treatment,
      dosage, or clinical priority decisions.

## Minimum Checks

Run before final demo rehearsal:

```bash
npm run check:project
npm run check:events
npm run check:demo-data
npm run check:fixture-language
npm run check:mulesoft
npm run check:models
npm run check:agentforce
npm run test:unit
```

Run after Salesforce org setup:

```bash
npm run demo:reset -- --target-org hfs-dev
npm run demo:seed -- --target-org hfs-dev
npm run demo:run -- --target-org hfs-dev
```

## Manual Setup Before The Final Rehearsal

The repo is allowed to run without real channel credentials. The presenter must
be explicit about which path is active.

1. Connect one Salesforce org alias:

   ```bash
   sf org login web --alias hfs-dev --set-default
   sf org display --target-org hfs-dev
   ```

2. Deploy and verify the Salesforce metadata from
   `docs/salesforce-development.md`, then run the demo reset, seed, and run
   commands above.
3. For real Slack delivery, configure `SLACK_WEBHOOK_URL` outside Git. Without
   it, the MuleSoft mock must return honest `MOCK_SENT`.
4. For real WhatsApp delivery in the hackathon, configure Meta Cloud API
   credentials outside Git. Twilio Sandbox is legacy backup only. Without a
   complete provider config, the MuleSoft mock must return honest `MOCK_SENT`.
5. Review the final non-goals as a team: no diagnosis, treatment, dosage,
   triage, clinical priority, real patient records, or autonomous protected
   actions.
6. Freeze or protect `main` after the final merge owner confirms the branch,
   runs `npm run check`, and verifies the demo still tells one North Star story.
7. Rehearse the three-minute path from
   `docs/north-star-demo-narrative.md`: trigger, evidence, Agentforce
   recommendation, clinical refusal, manager approval, MuleSoft channel results,
   outcome metrics, judge-sector mapping, and honesty close.
