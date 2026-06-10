# North Star Implementation Plan

## Goal

Convert the existing HFS vertical slice into a North Star universal operations
MVP with a private hospital demo profile, without weakening the governed
Salesforce, Agentforce, MuleSoft, model gateway, LWC, and harness contracts
already present in the repository.

The first task is specialization through global primitives and a hospital
profile, not reinvention.

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
- Patient Trust;
- Resource and Capacity;
- Operations Execution;
- Partner and Vendor;
- Risk and Approval;
- Financial Impact;
- Communication;
- Outcome Learning.

Agentforce action catalog:

- explain North Star case;
- draft evidence-backed recovery plan;
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

- recommendations cite complaint, capacity, vendor, billing, staff, stock, and
  outcome evidence;
- facts, inference, assumptions, missing evidence, recommended actions,
  blocked clinical actions, approval requirements, and expected outcomes are
  separated;
- restricted or missing evidence fails closed.

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
- `CAPTURE_HOSPITAL_OUTCOME`.

Slack:

- use a real incoming webhook when `SLACK_WEBHOOK_URL` exists;
- otherwise preserve an honest `MOCK_SENT` result.

WhatsApp:

- use Twilio Sandbox or Meta Cloud API only if setup is complete;
- otherwise use an honest WhatsApp-style internal alert mock.

Acceptance:

- unapproved action execution returns denial;
- approved action execution returns queued, success, or honest mock status with
  correlation IDs;
- channel results are visible in the command center.

## Workstream 5: North Star Command Center

Update the Lightning command center from retail operations wording to universal
hospital operations wording.

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
7. Execute MuleSoft action.
8. Show Slack and WhatsApp-style alerts.
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

| Surface                  | Minimum focused checks                                                                                    |
| ------------------------ | --------------------------------------------------------------------------------------------------------- |
| Salesforce core          | `npm run check:project`, Apex tests for recommendation, approval, evidence, action, and outcome behavior  |
| Agentforce contracts     | `npm run check:agentforce`, refusal checks, evidence citation checks                                      |
| MuleSoft and channels    | `npm run check:mulesoft`, approved action execution path, denied path, channel fixtures                   |
| Lightning command center | LWC unit tests, UI mock fixture render, ready/restricted/denied/error/approval states                     |
| Event and data fixtures  | fixture schema validation, malformed/late/duplicate/out-of-order examples, expected recommendation review |

## Build Checklist

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
- [x] Ensure the orchestrator recommendation includes patient trust, resource
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
- [ ] Add a WhatsApp configuration path that can use Twilio Sandbox or Meta
      Cloud API only when credentials are configured, otherwise returns
      `MOCK_SENT` honestly.
- [x] Update the command center to show hospital risk pulse, evidence timeline,
      vendor response, approval cockpit, Slack result, WhatsApp result, and task
      acknowledgement.
- [x] Add UI mock states for ready, restricted, denied, channel failed, channel
      mock sent, voice request, clinical refusal, and action approved.
- [x] Run LWC tests and direct MuleSoft checks when the WhatsApp contract
      changes.

### Data, Edge Cases, And Recommendation Validation

- [x] Build synthetic hospital data for departments, resources, partners,
      complaints, queues, stock, billing, insurance, tasks, channel aliases, and
      outcomes.
- [x] Create an initial realistic complaint cluster for wait time, room
      readiness, billing, pharmacy delay, and service recovery.
- [x] Add complaint variants for isolated complaints, food, accessibility,
      privacy, and staff interaction.
- [x] Create initial partner response examples for lab delay and
      billing/insurance follow-up.
- [x] Add partner recovery variants: lab recovered, insurance approved,
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
