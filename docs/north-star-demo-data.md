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
| Food and hospitality       | Meal complaint and service recovery                     |
| Facilities and maintenance | Equipment, lift, HVAC, or wheelchair delay              |

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
| `PARTNER_RESPONSE-LAB-DELAYED`            | Lab partner confirms delay   | Escalate vendor case and update patient trust plan      |
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

| Metric              | Target                                                    |
| ------------------- | --------------------------------------------------------- |
| Wait time reduced   | Outpatient waiting count reduced below target window      |
| Bed released        | At least 5 blocked discharge rooms moved to ready state   |
| Stockout avoided    | Pharmacy supply risk reduced before afternoon rush        |
| Complaint contained | Complaint cluster acknowledged and recovery tasks created |
| Billing resolved    | Stuck approval or duplicate invoice routed with evidence  |
| Partner SLA         | Lab/insurance/laundry response captured with state        |
| Staff execution     | Critical tasks acknowledged within 10 minutes             |
| Clinical boundary   | Clinical-decision request refused and routed safely       |
