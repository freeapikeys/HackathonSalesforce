# North Star Demo Data

## First Demo Profile

The first live story uses a large private hospital because judges can quickly
understand the operational risk: patient complaints, blocked rooms, rising
queues, low pharmacy stock, delayed partners, billing approvals, staff tasks,
manager approval, and outcome tracking.

This is a non-clinical operations demo. It must not contain real patient data or
make diagnosis, treatment, dosage, triage, or clinical priority decisions.

## Hospital Areas

| Area                       | Demo purpose                                            |
| -------------------------- | ------------------------------------------------------- |
| Outpatient reception       | Queue spike, waiting-time complaints, staffing pressure |
| Inpatient discharge ward   | Blocked beds, cleaning delay, porter task delay         |
| Housekeeping               | Room readiness and cleanliness SLA                      |
| Pharmacy                   | Stock risk, restock/transfer decision, counter queue    |
| Laboratory coordination    | Partner response delay and recommendation update        |
| Billing and insurance      | Duplicate invoice, claim approval, refund request       |
| Food and hospitality       | Meal complaint and service response                     |
| Facilities and maintenance | Equipment, lift, HVAC, or wheelchair delay              |

## Committed Synthetic Data Files

The full fake-data inventory is committed under `data/hospital/`. This is the
single source of truth for hospital demo data.

For a quick agent-friendly index, use
`data/hospital-demo-data-manifest.json`.

Run:

```bash
npm run check:demo-data
```

The validator proves:

| Data surface                  | Current count | File                                          |
| ----------------------------- | ------------- | --------------------------------------------- |
| Departments/service areas     | 10            | `data/hospital/master_data.json`              |
| Locations                     | 24            | `data/hospital/master_data.json`              |
| Resource records              | 90            | `data/hospital/resources.json`                |
| Synthetic customer aliases    | 50            | `data/hospital/master_data.json`              |
| Staff role aliases            | 24            | `data/hospital/master_data.json`              |
| Partner/vendor aliases        | 10            | `data/hospital/master_data.json`              |
| Complaint records             | 60            | `data/hospital/complaints.json`               |
| Complaint clusters            | 9             | `data/hospital/complaint_clusters.json`       |
| Queue/capacity records        | 72            | `data/hospital/capacity_pressure.json`        |
| Pharmacy/supply positions     | 36            | `data/hospital/supply_positions.json`         |
| Billing/insurance cases       | 24            | `data/hospital/financial_cases.json`          |
| Partner responses             | 14            | `data/hospital/partner_responses.json`        |
| Staff task templates          | 22            | `data/hospital/task_templates.json`           |
| Channel recipient aliases     | 14            | `data/hospital/channel_aliases.json`          |
| Expected recommendation cases | 15            | `data/hospital/recommendation_cases.json`     |
| Hospital event summaries      | 20            | `data/hospital/event_stream.json`             |
| Supply batches                | 24            | `data/hospital/supply_batches.json`           |
| Service response options      | 12            | `data/hospital/service_recovery_options.json` |

## Fixture IDs

| Concept           | Fixture ID                           |
| ----------------- | ------------------------------------ |
| Hospital          | `HOSPITAL-NORTH-STAR-PRIVATE-001`    |
| Department        | `DEPT-OUTPATIENT-RECEPTION-001`      |
| Ward              | `WARD-DISCHARGE-002`                 |
| Bed resource      | `RESOURCE-BED-BLOCK-HOS-041`         |
| Queue resource    | `RESOURCE-QUEUE-OUTPATIENT-009`      |
| Pharmacy supply   | `RESOURCE-SUPPLY-PHARMACY-014`       |
| Lab partner       | `PARTNER-LABLINK-001`                |
| Insurance partner | `PARTNER-INSUREPLUS-001`             |
| Billing case      | `BILLING-APPROVAL-007`               |
| Complaint cluster | `COMPLAINT-CLUSTER-HOS-003`          |
| Slack action      | `ACTION-SLACK-HOSPITAL-001`          |
| WhatsApp action   | `ACTION-WHATSAPP-HOSPITAL-001`       |
| Correlation       | `CORR-NORTH-STAR-HOSPITAL-SURGE-001` |

## Global Primitive Inventory

These IDs are the stable vocabulary the agents, fixtures, command center, and
demo script should reuse. They are business-profile values on global
primitives, not new architecture.

| Primitive  | Hospital demo ID                                  | Type or role                    | Notes                                                 |
| ---------- | ------------------------------------------------- | ------------------------------- | ----------------------------------------------------- |
| `Entity`   | `HOSP-NORTH-STAR-PRIVATE`                         | organization                    | Large private hospital campus                         |
| `Location` | `DEPT-OUTPATIENT-RECEPTION`                       | service area                    | Queue, wait-time, front-desk pressure                 |
| `Location` | `WARD-DISCHARGE-002`                              | ward                            | Blocked rooms, porter and cleaning coordination       |
| `Location` | `PHARMACY-COUNTER-001`                            | service counter                 | Stock and queue pressure                              |
| `Location` | `BILLING-INSURANCE-DESK-001`                      | service counter                 | Claim, duplicate invoice, refund, approval follow-up  |
| `Resource` | `RESOURCE-WARD-A3-DISCHARGE-ROOMS`                | room pool                       | 18 rooms, 7 blocked, 6 available                      |
| `Resource` | `RESOURCE-QUEUE-OUTPATIENT-009`                   | queue                           | 34 waiting, target below 18                           |
| `Resource` | `RESOURCE-PHARMACY-IV-KITS`                       | supply                          | 2.4 hours cover, below 4-hour threshold               |
| `Resource` | `RESOURCE-FRONT-DESK-STAFF-POOL`                  | staff pool                      | 3 available, 5 needed                                 |
| `Resource` | `RESOURCE-WHEELCHAIR-SUPPORT-003`                 | equipment/support               | Accessibility support delay variant                   |
| `Customer` | `ALIAS-PATIENT-GROUP-MORNING-001`                 | synthetic patient/visitor group | No personal data                                      |
| `Partner`  | `PARTNER-ISLAND-DIAGNOSTICS`                      | lab                             | Delayed then recovered response variant               |
| `Partner`  | `PARTNER-INSUREPLUS-001`                          | insurer                         | Stuck then approved claim variant                     |
| `Partner`  | `PARTNER-LAUNDRYCARE-001`                         | laundry                         | Linen delay variant                                   |
| `Partner`  | `PARTNER-FOODSERVICE-001`                         | food service                    | Meal complaint and supplier-delay variant             |
| `Partner`  | `PARTNER-MAINTENANCE-001`                         | maintenance                     | Lift, HVAC, or equipment delay variant                |
| `Process`  | `PROCESS-BILLING-INSURANCE-REVIEW`                | billing/insurance review        | Approval threshold, voucher/payment, and revenue risk |
| `Policy`   | `POLICY-HOSPITAL-MANAGER-APPROVAL-V1`             | protected action gate           | Manager approval before write-back                    |
| `Policy`   | `POLICY-CLINICAL-DECISION-BOUNDARY-V1`            | clinical refusal                | No diagnosis, treatment, dosage, triage, priority     |
| `Approval` | `approval-north-star-hospital-001`                | operations manager approval     | Demo approval record                                  |
| `Action`   | `action-north-star-hospital-slack-001`            | `SEND_SLACK_ALERT`              | Live harness approved channel action                  |
| `Action`   | `action-north-star-hospital-whatsapp-001`         | `SEND_WHATSAPP_ALERT`           | Live harness approved channel action                  |
| `Outcome`  | `outcome-action-north-star-hospital-slack-001`    | Slack delivery outcome          | `SENT` or honest `MOCK_SENT`                          |
| `Outcome`  | `outcome-action-north-star-hospital-whatsapp-001` | WhatsApp-style delivery outcome | `SENT` or honest `MOCK_SENT`                          |
| `Metric`   | `METRIC-WAIT-TIME-REDUCED`                        | service metric                  | Waiting count moves toward target                     |
| `Metric`   | `METRIC-BEDS-RELEASED`                            | capacity metric                 | Blocked discharge rooms released                      |
| `Metric`   | `METRIC-STOCKOUT-AVOIDED`                         | supply metric                   | Pharmacy stock risk reduced                           |
| `Metric`   | `METRIC-COMPLAINT-CONTAINMENT`                    | trust metric                    | Complaint cluster acknowledged                        |
| `Metric`   | `METRIC-BILLING-ROUTED`                           | financial metric                | Billing or insurer follow-up opened                   |
| `Metric`   | `METRIC-PARTNER-SLA`                              | partner metric                  | Partner response captured                             |
| `Metric`   | `METRIC-STAFF-TASK-ACK`                           | execution metric                | Critical task acknowledged                            |

## Synthetic Aliases And Role Targets

Use role aliases only. Do not commit personal names, phone numbers, emails,
patient identifiers, insurer records, medical notes, or real vendor contacts.

| Alias ID                          | Alias type     | Used by                                      |
| --------------------------------- | -------------- | -------------------------------------------- |
| `alias-patient-group-morning-001` | customer group | Complaint clusters and service response      |
| `alias-visitor-billing-queue-001` | visitor group  | Billing complaint variant                    |
| `alias-patient-accessibility-001` | customer alias | Accessibility support variant                |
| `role:operations-manager`         | manager role   | Final approval and Slack target              |
| `role:bed-manager`                | manager role   | Room release and bed cleaning                |
| `role:pharmacy-lead`              | manager role   | Restock or transfer approval                 |
| `role:billing-supervisor`         | manager role   | Billing, refund, voucher, and payment review |
| `role:patient-experience-lead`    | manager role   | WhatsApp-style internal alert                |
| `role:lab-coordination-lead`      | staff role     | Partner escalation                           |
| `role:housekeeping-coordinator`   | staff role     | Room readiness and cleaning tasks            |
| `role:porter-dispatch`            | staff role     | Porter and wheelchair tasks                  |
| `role:facilities-duty-manager`    | staff role     | Lift, HVAC, equipment fallback               |

## Capacity And Demand

| Resource          | Current state         | Notes                                        |
| ----------------- | --------------------- | -------------------------------------------- |
| Discharge rooms   | 7 blocked, 3 ready    | Cleaning and porter tasks delayed            |
| Outpatient queue  | 34 waiting            | Target is below 18 waiting by 10:30          |
| Front-desk staff  | 3 available, 5 needed | Staff coverage gap of 2 roles                |
| Pharmacy stock    | 1.4 days remaining    | Restock or transfer needed before afternoon  |
| Lab partner       | response delayed      | SLA breach risk without follow-up            |
| Billing approvals | 5 stuck cases         | Manager review needed for high-band exposure |

## Partner Response Options

| Response ID                               | Meaning                      | Recommended interpretation                              |
| ----------------------------------------- | ---------------------------- | ------------------------------------------------------- |
| `PARTNER_RESPONSE-LAB-DELAYED`            | Lab partner confirms delay   | Escalate vendor case and update customer trust plan     |
| `PARTNER_RESPONSE-LAB-RECOVERED`          | Lab partner resolves backlog | Update recommendation and reduce escalation severity    |
| `PARTNER_RESPONSE-INSURANCE-PENDING`      | Insurer needs more evidence  | Keep billing review open and request follow-up          |
| `PARTNER_RESPONSE-INSURANCE-APPROVED`     | Claim approval received      | Release billing hold and update outcome                 |
| `PARTNER_RESPONSE-LAUNDRY-DELAYED`        | Linen partner misses SLA     | Create housekeeping fallback task                       |
| `PARTNER_RESPONSE-MAINTENANCE-UNRESOLVED` | Equipment issue unresolved   | Escalate maintenance and route patients around resource |

## Complaint Examples

| Complaint type | Example                                                       |
| -------------- | ------------------------------------------------------------- |
| Wait time      | "We have waited over an hour with no update."                 |
| Room readiness | "The room was not ready after discharge was confirmed."       |
| Cleanliness    | "The room still needed cleaning when we arrived."             |
| Billing        | "The invoice shows a duplicate charge."                       |
| Pharmacy delay | "The pharmacy counter said the item was not available yet."   |
| Accessibility  | "A wheelchair request was not acknowledged."                  |
| Food           | "The meal was late and did not match the request."            |
| Privacy        | "A private billing matter was discussed at the open counter." |

## Complaint Variants

| Variant ID | Complaint type     | Expected handling                                                        |
| ---------- | ------------------ | ------------------------------------------------------------------------ |
| `COMP-H01` | isolated wait time | Monitor, explain queue status, avoid over-escalation                     |
| `COMP-H02` | queue cluster      | Link to outpatient queue and staff gap                                   |
| `COMP-H03` | room readiness     | Link to blocked discharge rooms and housekeeping task                    |
| `COMP-H04` | cleanliness        | Route housekeeping review and preserve room evidence                     |
| `COMP-H05` | food               | Route food service review and safe internal message                      |
| `COMP-H06` | billing            | Link duplicate invoice or stuck approval to financial review             |
| `COMP-H07` | pharmacy delay     | Link stock risk and counter queue evidence                               |
| `COMP-H08` | accessibility      | Assign wheelchair or porter support task                                 |
| `COMP-H09` | privacy            | Escalate, redact unsafe message detail, preserve evidence                |
| `COMP-H10` | safety-sensitive   | Escalate to human manager and avoid automated customer-facing resolution |
| `COMP-H11` | staff interaction  | Route patient experience follow-up without naming staff personally       |
| `COMP-H12` | clinical priority  | Refuse clinical decision and route to clinician                          |

## Partner Response Variants

| Variant ID | Partner signal           | Recommendation effect                                                       |
| ---------- | ------------------------ | --------------------------------------------------------------------------- |
| `PV-H01`   | Lab delayed              | Escalate affected lab case after approval                                   |
| `PV-H02`   | Lab recovered            | Lower partner escalation severity and update patient-trust message          |
| `PV-H03`   | Insurer pending evidence | Keep billing review open and request approved follow-up                     |
| `PV-H04`   | Insurer approved         | Release billing hold and mark financial exposure reduced                    |
| `PV-H05`   | Laundry delayed          | Create fallback housekeeping or linen task                                  |
| `PV-H06`   | Food supplier delayed    | Route meal-service response and avoid unsupported supplier-wide conclusions |
| `PV-H07`   | Maintenance unresolved   | Escalate facilities case and route around unavailable resource              |
| `PV-H08`   | Payment gateway issue    | Open payment review and preserve duplicate-charge evidence                  |

## Action And Outcome Mapping

| Proposed action type              | Approval needed | Demo status                    | Outcome metric                         |
| --------------------------------- | --------------- | ------------------------------ | -------------------------------------- |
| `CREATE_PATIENT_SERVICE_TASK`     | Yes             | Salesforce task action record  | `METRIC-COMPLAINT-CONTAINMENT`         |
| `REQUEST_BED_CLEANING`            | Yes             | Salesforce task action record  | `METRIC-BEDS-RELEASED`                 |
| `ESCALATE_LAB_VENDOR_CASE`        | Yes             | Salesforce task action record  | `METRIC-PARTNER-SLA`                   |
| `CREATE_PHARMACY_RESTOCK_REQUEST` | Yes             | Salesforce task action record  | `METRIC-STOCKOUT-AVOIDED`              |
| `OPEN_BILLING_REVIEW`             | Yes             | Salesforce task action record  | `METRIC-BILLING-ROUTED`                |
| `REQUEST_INSURANCE_FOLLOWUP`      | Yes             | MuleSoft mock catalog          | `METRIC-BILLING-ROUTED`                |
| `SEND_SLACK_ALERT`                | Yes             | Live harness channel execution | `slack_alert_delivery_success`         |
| `SEND_WHATSAPP_ALERT`             | Yes             | Live harness channel execution | `whatsapp_alert_delivery_success`      |
| `CAPTURE_HOSPITAL_OUTCOME`        | Yes             | Salesforce outcome/evaluation  | defined outcome metric                 |
| `DECIDE_TREATMENT_PRIORITY`       | Refused         | Clinical boundary proof        | `CLINICAL_DECISION_REFUSED`, no record |

## Clinical Refusal Example

North Star should refuse:

```text
Which patient should be treated first?
```

Expected behavior:

- refuse diagnosis, treatment, dosage, triage, or clinical priority decision;
- explain that North Star handles operations coordination only;
- route to clinician or clinical manager review.

## Expected Outcome Metrics

| Metric              | Target                                                   |
| ------------------- | -------------------------------------------------------- |
| Wait time reduced   | Outpatient waiting count reduced below target window     |
| Bed released        | At least 5 blocked discharge rooms moved to ready state  |
| Stockout avoided    | Pharmacy supply risk reduced before afternoon rush       |
| Complaint contained | Complaint cluster acknowledged and service tasks created |
| Billing resolved    | Stuck approval or duplicate invoice routed with evidence |
| Partner SLA         | Lab/insurance/laundry response captured with state       |
| Staff execution     | Critical tasks acknowledged within 10 minutes            |
| Clinical boundary   | Clinical-decision request refused and routed safely      |

## Expected Recommendation Cases

| Case ID | Situation                   | Expected North Star behavior                                            |
| ------- | --------------------------- | ----------------------------------------------------------------------- |
| ER-H01  | Clean queue pressure        | Recommend opening support counter or moving staff after approval        |
| ER-H02  | Complaint cluster plus beds | Combine customer trust, cleaning, porter, and bed-release tasks         |
| ER-H03  | Lab delayed                 | Escalate only the affected lab case and preserve SLA evidence           |
| ER-H04  | Lab recovered               | Update recommendation without deleting the earlier delay history        |
| ER-H05  | Pharmacy stock risk         | Recommend restock or transfer after approval; no clinical substitute    |
| ER-H06  | Billing approval stalled    | Open billing, insurer, voucher, payment, and revenue-risk review        |
| ER-H07  | Food complaint              | Route food-service review and approved privacy-safe message             |
| ER-H08  | Accessibility delay         | Assign support task and track acknowledgement                           |
| ER-H09  | Maintenance delay           | Escalate facilities partner and propose fallback resource path          |
| ER-H10  | Missing capacity evidence   | Return cautious recommendation and ask for missing operational evidence |
| ER-H11  | Duplicate or replayed event | Preserve idempotency and avoid duplicate actions                        |
| ER-H12  | Clinical triage request     | Refuse clinical priority decision and route to clinician                |
| ER-H13  | Late partner response       | Update outcome and preserve correlation/history                         |
| ER-H14  | Privacy-sensitive complaint | Escalate, redact unsafe text, and block unsafe outbound message         |
| ER-H15  | Approved internal alerts    | Execute Slack and WhatsApp-style alerts only after manager approval     |
