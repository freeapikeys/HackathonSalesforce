# Aarav Assignment: Synthetic Hospital Data And Demo Grounding

## Goal

Create realistic synthetic private hospital operations data for North Star's
agents, fixtures, command center, and demo flow. The data must feel like a
large hospital operation in Mauritius, but it must not contain real patient,
staff, phone, supplier, insurer, credential, or medical-record data.

This assignment is not "make random fake data." It is building the evidence
base that lets the agents reason:

- Patient Trust Agent needs patient/visitor complaints, complaint clusters,
  service recovery context, and safe message drafts.
- Resource and Capacity Agent needs beds, rooms, queues, staff, pharmacy stock,
  equipment, and service counters.
- Partner and Vendor Agent needs lab, laundry, insurer, payment, food,
  maintenance, transport, and equipment partner status.
- Financial Impact Agent needs billing issues, insurance approvals, refund
  requests, compensation thresholds, and payment failures.
- Operations Execution Agent needs staff roles, task templates, channel
  aliases, acknowledgements, due times, and escalation paths.
- The Orchestrator Topic needs all of the above to produce one coordinated
  recovery plan.

## What The Project Already Has

Start from the existing project structure:

- `docs/north-star-mvp.md` defines the global operating model and hospital demo.
- `docs/north-star-implementation-plan.md` defines generic build checklists.
- `docs/event-contract.md` defines source event expectations.
- `docs/demo-harness.md` defines the demo proof path.
- `docs/ui-state-contract.md` defines command-center state expectations.
- `docs/salesforce-data-model.md` maps data onto HFS records.
- `integration/events/fixtures/` contains current source event fixtures.
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json` contains
  current Agentforce fixtures.
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/fixtures.js`
  contains current UI fixture state.

The current fixtures are still retail-oriented in places. Your job is to create
or prepare hospital operations data that future implementation work can consume.

## Demo Business Date

Use one consistent demo business date unless a test requires another date:

```text
2026-06-13
```

Use Mauritius time:

```text
Indian/Mauritius, UTC+04:00
```

## Data Safety Rules

- Use synthetic aliases only.
- Do not use real patient names, staff names, phone numbers, emails, addresses,
  insurer records, medical records, diagnoses, treatments, prescriptions, or
  clinical notes.
- Use role aliases such as `role:bed-manager` instead of personal contact data.
- Use deterministic IDs so tests can reference records.
- Every complaint must connect to department, location, resource if relevant,
  timestamp, and evidence ID.
- Include messy data. Perfect data makes the demo weaker.
- Include clinical-decision requests only as refusal scenarios, not as
  actionable medical instructions.

## Required Data Volume

Create enough data to prove this is a global operations system, not a single
hospital ticket demo.

| Data type                     | Target count | Why it is needed                                  |
| ----------------------------- | ------------ | ------------------------------------------------- |
| Hospital campus               | 1            | One coherent flagship demo environment            |
| Departments/service areas     | 8 to 10      | Show cross-functional operations                  |
| Locations                     | 20 to 30     | Wards, counters, rooms, pharmacy, lab, billing    |
| Resource types                | 8 to 12      | Beds, rooms, queues, stock, equipment, counters   |
| Resource records              | 80 to 120    | Enough capacity and availability evidence         |
| Synthetic customer aliases    | 40 to 60     | Patient/visitor complaint and service recovery    |
| Staff role aliases            | 20 to 30     | Task routing without personal data                |
| Partner/vendor aliases        | 8 to 12      | Lab, laundry, insurer, payment, food, maintenance |
| Complaint records             | 50 to 70     | Isolated complaints plus meaningful clusters      |
| Complaint clusters            | 8 to 10      | Direct input to Patient Trust reasoning           |
| Queue/capacity records        | 60 to 100    | Time-band capacity pressure                       |
| Pharmacy/supply records       | 30 to 50     | Stock risk, transfer, restock decisions           |
| Billing/insurance cases       | 20 to 30     | Financial exposure and approval routing           |
| Partner responses             | 12 to 16     | Recommendation changes after new evidence         |
| Staff task templates          | 20 to 25     | Operations execution actions                      |
| Channel recipient aliases     | 12 to 16     | Slack/WhatsApp role targets without personal data |
| Expected recommendation cases | 12 to 15     | Evaluation notes for Agentforce and demo QA       |
| Hospital event fixtures       | 18 to 24     | Intake, duplicate, late, malformed, outcome paths |

Do not create huge transaction-level data unless the repo needs it. Time-band
summaries are enough for the hackathon.

## Required Departments And Risks

| Department/service area    | Required risks                                                  |
| -------------------------- | --------------------------------------------------------------- |
| Outpatient reception       | queue spike, wait complaint, front-desk staff pressure          |
| Emergency intake desk      | non-clinical congestion, escalation, safety-sensitive flag      |
| Inpatient discharge ward   | bed blocked, cleaning delay, porter task delay                  |
| Housekeeping               | room readiness, cleanliness complaint, SLA breach               |
| Pharmacy                   | stock risk, substitute/transfer request, counter queue          |
| Laboratory coordination    | partner response delay, status uncertainty, SLA evidence        |
| Billing and insurance      | duplicate invoice, claim approval stuck, refund request         |
| Food and hospitality       | meal complaint, allergy-safe service escalation, supplier delay |
| Facilities and maintenance | wheelchair, lift, HVAC, equipment, or cleaning issue            |
| Patient experience desk    | complaint cluster, service recovery, approved message           |

## Required Partners

Use synthetic partner aliases:

| Partner ID                | Partner type                     | Risks to represent                   |
| ------------------------- | -------------------------------- | ------------------------------------ |
| `partner-lablink-001`     | laboratory coordination          | delayed response, recovered response |
| `partner-laundrycare-001` | laundry and linen                | linen shortage, SLA breach           |
| `partner-insureplus-001`  | insurance/pre-authorization      | pending approval, approved follow-up |
| `partner-payflow-001`     | payment processing               | duplicate charge, gateway issue      |
| `partner-medstock-001`    | pharmacy/supply distributor      | restock lead time, partial supply    |
| `partner-foodservice-001` | food and meal operations         | meal complaint, supplier delay       |
| `partner-maintenance-001` | facilities maintenance           | lift, HVAC, equipment delay          |
| `partner-transport-001`   | patient transport/porter support | wheelchair/porter delay              |

Each partner should have:

- normal response time;
- emergency response time;
- reliability status or score;
- contact alias, not real email or phone;
- at least one response example.

## Data Objects To Create

### Hospital Resource

Required fields:

- `resourceId`
- `resourceType`: `BED`, `ROOM`, `QUEUE`, `SUPPLY`, `EQUIPMENT`,
  `SERVICE_COUNTER`, `STAFF_POOL`, or `PARTNER_SLOT`
- `name`
- `departmentId`
- `locationId`
- `status`: `available`, `busy`, `blocked`, `reserved`, `low_stock`,
  `delayed`, `maintenance`, or `unknown`
- `capacity`
- `availableCapacity`
- `blockedCapacity`
- `evidenceId`

### Complaint

Required fields:

- `complaintId`
- `customerAliasId`
- `departmentId`
- `locationId`
- `resourceId` or `resourceUnknownReason`
- `reportedAt`
- `complaintType`: `wait_time`, `room_readiness`, `cleanliness`, `food`,
  `billing`, `discharge_delay`, `pharmacy_delay`, `lost_item`,
  `accessibility`, `privacy`, `safety`, or `staff_interaction`
- `severity`: `low`, `medium`, `high`, or `critical`
- `summary`
- `serviceRecoveryRequested`
- `evidenceId`

### Complaint Cluster

Required fields:

- `clusterId`
- `departmentId`
- `locationIds`
- `resourceIds`
- `firstReportedAt`
- `lastReportedAt`
- `complaintCount`
- `dominantTypes`
- `riskInterpretation`: `isolated`, `capacity_driven`, `partner_driven`,
  `billing_driven`, `service_recovery`, `privacy_sensitive`, or
  `safety_sensitive`
- `recommendedCaution`
- `evidenceIds`

### Capacity Record

Required fields:

- `capacityRecordId`
- `departmentId`
- `locationId`
- `businessDate`
- `timeBand`: `morning`, `midday`, `afternoon`, or `evening`
- `expectedDemand`
- `availableCapacity`
- `blockedCapacity`
- `staffAvailable`
- `staffRequired`
- `queueRisk`: `low`, `medium`, `high`, or `critical`
- `evidenceId`

### Pharmacy Or Supply Position

Required fields:

- `supplyPositionId`
- `departmentId`
- `resourceId`
- `itemAlias`
- `availableStock`
- `reservedStock`
- `averageDailyUsage`
- `incomingStock`
- `supplierLeadTimeHours`
- `stockConfidence`: `high`, `medium`, or `low`
- `evidenceId`

### Billing Or Insurance Case

Required fields:

- `caseId`
- `customerAliasId`
- `departmentId`
- `caseType`: `duplicate_invoice`, `claim_pending`, `refund_request`,
  `deposit_issue`, `payment_failure`, or `compensation_review`
- `amountBand`: `low`, `medium`, or `high`
- `approvalRequired`
- `status`: `open`, `pending_partner`, `approved`, `denied`, or `resolved`
- `evidenceId`

### Partner Response

Required fields:

- `partnerResponseId`
- `partnerId`
- `relatedIssueId`
- `receivedAt`
- `responseType`: `delayed`, `recovered`, `approved`, `denied`,
  `insufficient_evidence`, `partial_resolution`, or `corrective_action`
- `summary`
- `expectedResolutionAt` if applicable
- `changesRecommendation`: true or false
- `evidenceId`

### Staff Task Template

Required fields:

- `taskTemplateId`
- `taskType`: `patient_service`, `bed_cleaning`, `porter_dispatch`,
  `pharmacy_restock`, `billing_review`, `insurance_followup`,
  `vendor_escalation`, `maintenance_check`, `food_service_review`,
  `manager_review`, or `clinical_route`
- `defaultOwnerRole`
- `defaultDueMinutes`
- `requiresApproval`
- `messageTemplate`

### Channel Recipient Alias

Required fields:

- `recipientAliasId`
- `role`
- `departmentId`
- `slackTarget`
- `whatsappTargetAlias`
- `canReceiveUrgentAlerts`

Use aliases only. Example: `role:outpatient-operations-manager`.

## Required Hospital Scenarios

Create these exact scenario types:

1. Isolated low-severity wait complaint with monitoring only.
2. Complaint cluster caused by outpatient queue pressure.
3. Room readiness complaint linked to blocked discharge cleaning.
4. Pharmacy stock risk requiring approved restock or transfer.
5. Lab partner delay that changes the recommendation after response.
6. Billing or insurance approval stuck and needing financial approval.
7. Food or hospitality complaint requiring service recovery.
8. Accessibility support delay requiring task assignment.
9. Privacy or safety-sensitive complaint requiring escalation.
10. Clinical triage/treatment request that North Star refuses.
11. Missing resource evidence causing a cautious recommendation.
12. Late partner response updating the plan without overwriting audit history.

Each scenario should include:

- source complaints or signals;
- cluster summary if relevant;
- related capacity/resource/partner/billing facts;
- expected recommendation note;
- what the system must refuse to do;
- which approval is required;
- which Slack or WhatsApp alert would be appropriate after approval.

## Required Expected Recommendation Cases

Create 12 to 15 expected recommendation notes:

| Case ID | Situation                           | Expected behavior                                             |
| ------- | ----------------------------------- | ------------------------------------------------------------- |
| ER-H01  | clean queue pressure                | move staff or open service counter after approval if needed   |
| ER-H02  | complaint cluster plus blocked beds | create cleaning/porter tasks and patient trust recovery       |
| ER-H03  | partner response received           | update plan and preserve previous recommendation history      |
| ER-H04  | pharmacy stock risk                 | restock, transfer, or substitute operationally after approval |
| ER-H05  | billing approval stalled            | open billing/insurance review and estimate exposure           |
| ER-H06  | food complaint                      | route service task and approved message draft                 |
| ER-H07  | accessibility delay                 | assign support task and track acknowledgement                 |
| ER-H08  | maintenance delay                   | vendor escalation and fallback resource check                 |
| ER-H09  | missing capacity data               | cautious recommendation and missing evidence                  |
| ER-H10  | duplicate event                     | intake should dedupe without corrupting context               |
| ER-H11  | clinical triage request             | refuse clinical decision and route to clinician               |
| ER-H12  | late outcome callback               | update outcome and keep correlation history                   |

Each note should say:

- what North Star should recommend;
- what North Star should refuse to do;
- which evidence IDs matter;
- whether manager approval is needed;
- which Slack or WhatsApp alert would be appropriate after approval.

## Required Hospital Event Fixtures

Prepare 18 to 24 hospital event fixtures using the existing event-envelope
style. Include:

- patient complaint cluster detected;
- bed capacity pressure detected;
- discharge room blocked;
- pharmacy stock risk detected;
- lab vendor response delayed;
- billing approval stalled;
- staff queue risk detected;
- clinical decision request refused;
- approved action executed;
- hospital outcome captured;
- duplicate event;
- malformed event;
- late event;
- out-of-order event;
- idempotency conflict;
- invalid content hash.

## How The Agents Will Use The Data

### Patient Trust Agent

Consumes:

- complaints;
- complaint clusters;
- customer aliases;
- department and location context;
- safety/privacy flags;
- service recovery status.

Produces:

- isolated versus meaningful cluster classification;
- patient trust risk;
- approved message draft;
- escalation or monitoring recommendation;
- missing evidence list.

### Resource And Capacity Agent

Consumes:

- hospital resources;
- capacity records;
- pharmacy/supply positions;
- queue data;
- staff role coverage;
- partner status.

Produces:

- capacity pressure;
- queue risk;
- stock days remaining;
- SLA breach risk;
- task, restock, transfer, or escalation recommendation.

### Partner And Vendor Agent

Consumes:

- partner responses;
- SLA history;
- billing/insurance partner status;
- lab/laundry/maintenance/food/transport issues.

Produces:

- partner delay classification;
- response request;
- escalation;
- recommendation change when new evidence arrives.

### Financial Impact Agent

Consumes:

- billing cases;
- insurance approvals;
- refund requests;
- compensation thresholds;
- payment failures.

Produces:

- financial exposure;
- approval requirement;
- billing review or insurance follow-up action.

### Operations Execution Agent

Consumes:

- task templates;
- staff roles;
- resource pressure;
- channel recipient aliases;
- approved action plan.

Produces:

- task queue;
- owner role;
- due time;
- acknowledgement expectation;
- escalation path.

### Orchestrator Topic

Consumes all agent outputs and expected recommendation notes.

Produces one final plan:

- facts;
- inferences;
- assumptions;
- missing evidence;
- blocked clinical actions;
- recommendation;
- required approvals;
- protected actions;
- channel alerts;
- outcome metrics.

## Implementation Checklist

- [ ] Pull latest `main`.
- [ ] Read this file and the required docs.
- [ ] Create the hospital data inventory table before writing large JSON files.
- [ ] Draft hospital campus, departments, locations, and resource types.
- [ ] Draft synthetic customer aliases and staff role aliases.
- [ ] Draft partner/vendor aliases and response examples.
- [ ] Draft hospital resources across beds, rooms, queues, supplies, equipment,
      counters, and staff pools.
- [ ] Draft complaint records and complaint clusters.
- [ ] Draft capacity and queue pressure records.
- [ ] Draft pharmacy/supply positions.
- [ ] Draft billing and insurance cases.
- [ ] Draft staff task templates and channel recipient aliases.
- [ ] Draft expected recommendation notes.
- [ ] Draft hospital event fixtures.
- [ ] Include duplicate, malformed, late, out-of-order, idempotency-conflict,
      invalid-hash, and clinical-refusal cases.
- [ ] Check that every scenario has evidence IDs.
- [ ] Check that no scenario contains real patient/staff/vendor data.
- [ ] Check that clinical decision requests are refusal-only.

## Validation Checklist

- [ ] Every resource has a type, department, location, status, and evidence ID.
- [ ] Every complaint links to customer alias, department, location, and
      evidence.
- [ ] Every complaint cluster has source complaint IDs.
- [ ] Every partner response links to a related issue.
- [ ] Every expected recommendation names evidence IDs.
- [ ] Every protected action says whether approval is needed.
- [ ] Every channel recipient is an alias, not personal contact data.
- [ ] Every messy event has a clear expected intake result.
- [ ] The final demo story has a trigger, conflict, partner/capacity response,
      approval, action, alert, and outcome.

## Demo Acceptance

The data work is demo-ready when:

- the demo can start from one hospital operations surge event;
- evidence includes complaint, capacity, resource, partner, stock, billing,
  staff, approval, and outcome context;
- the agent recommendation changes after partner or capacity evidence arrives;
- there are multiple hospital departments visible;
- there is at least one clean operations story and one high-risk complaint
  story;
- clinical decision requests are refused;
- fake data is realistic but clearly synthetic;
- another teammate can use the data without asking what each ID means.

## Codex Or Local LLM Prompt Starter

Use this when starting a fresh task:

```text
Read docs/assignments/aarav.md, docs/north-star-mvp.md,
docs/event-contract.md, docs/salesforce-data-model.md, and docs/demo-harness.md.
Create or refine synthetic private hospital operations data. Use deterministic
IDs, global primitives, complaint clusters, resource/capacity records, partner
responses, billing cases, messy event cases, expected recommendation notes, and
clinical-refusal examples. Do not use real personal, patient, medical, vendor,
phone, email, or credential data.
```
