# Aarav Assignment: Fake Data, Complaints, And Demo Scenario Grounding

## Goal

Create the realistic synthetic retail data that North Star's agents, fixtures,
command center, and demo flow will use. The data must feel like a real
supermarket operation in Mauritius, but it must not contain real customer,
staff, phone, supplier, or credential data.

This assignment is not "make random fake data." It is building the evidence
base that lets the agents reason:

- Inventory and Waste Agent needs stock, sales, promotions, expiry, and lead
  time data.
- Supplier and Product Trust Agent needs complaints, batches, supplier history,
  supplier replies, refunds, and quality signals.
- Store Execution and Outreach Agent needs staff roles, queue pressure, tasks,
  channels, acknowledgements, and deadlines.
- The Orchestrator Topic needs all of the above to produce one coordinated
  recovery plan.

## What The Project Already Has

Start from the existing project structure:

- `docs/north-star-mvp.md` defines the MVP and the three-agent system.
- `docs/north-star-implementation-plan.md` defines generic build checklists.
- `docs/event-contract.md` defines source event expectations.
- `docs/demo-harness.md` defines the demo proof path.
- `docs/ui-state-contract.md` defines command-center state expectations.
- `docs/salesforce-data-model.md` maps retail data onto HFS records.
- `integration/events/fixtures/` contains current source event fixtures.
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json` contains
  current Agentforce fixtures.
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/fixtures.js`
  contains current UI fixture state.

The current fixtures are still generic in places. Your job is to create or
prepare North Star retail data that future implementation work can consume.

## Demo Business Date

Use one consistent demo business date unless a test requires another date:

```text
2026-06-13
```

This creates a weekend-promotion story and lets expiry, staffing, and supplier
lead-time examples stay consistent.

Use Mauritius time:

```text
Indian/Mauritius, UTC+04:00
```

## Data Safety Rules

- Use synthetic names only.
- Do not use real customer names, phone numbers, emails, or addresses.
- Do not use real supplier contract terms.
- Use role aliases such as `role:duty-manager` instead of personal phone
  numbers.
- Use deterministic IDs so tests can reference records.
- Every complaint must connect to product, batch or no-batch reason, store,
  supplier, timestamp, and evidence ID.
- Include messy data. Perfect data makes the demo weaker.

## Required Data Volume

Create enough data to prove this applies to all products, not only burgers.

| Data type                         | Target count     | Why it is needed                                      |
| --------------------------------- | ---------------- | ----------------------------------------------------- |
| Stores                            | 3                | Compare different store conditions                    |
| Suppliers                         | 6                | Show supplier choice, lead time, and reliability      |
| Product categories                | 8                | Prove category-neutral architecture                   |
| Products                          | 30               | Enough variety for demo and fallback scenarios        |
| Product batches                   | 45 to 60         | Needed for expiry and batch-specific complaints       |
| Inventory positions               | 90 store records | 3 stores x 30 products                                |
| Warehouse inventory records       | 30               | One warehouse position per product                    |
| Daily sales summaries             | 1,260            | 3 stores x 30 products x 14 days                      |
| Promotions                        | 8                | Demand spike, price mismatch, and signage examples    |
| Complaint records                 | 50 to 70         | Isolated complaints plus meaningful clusters          |
| Complaint clusters                | 8                | Direct input to Supplier/Product Trust reasoning      |
| Refund records                    | 20 to 30         | Helps distinguish complaints from actual loss         |
| Supplier responses                | 10               | Shows recommendation changing after supplier evidence |
| Roster and queue pressure records | 84               | 3 stores x 7 days x 4 time bands                      |
| Staff task templates              | 20               | Store execution actions                               |
| Channel recipient aliases         | 12               | Slack/WhatsApp role targets without personal data     |
| Expected recommendation cases     | 12               | Evaluation notes for Agentforce and demo QA           |
| Retail event fixtures             | 18 to 24         | Intake, duplicate, late, malformed, and outcome paths |

Do not create all of this as huge transaction-level data unless the repo needs
it. Daily summaries are enough for the hackathon.

## Required Product Categories

Use these categories and include at least the minimum number of products:

| Category       | Minimum products | Required risks                                      |
| -------------- | ---------------- | --------------------------------------------------- |
| Fresh food     | 5                | expiry, quality complaint, demand spike             |
| Frozen food    | 4                | stockout, freezer/batch concern, supplier lead time |
| Bakery         | 4                | same-day waste, markdown, promotion readiness       |
| Dairy          | 4                | expiry, cold-chain complaint, replacement batch     |
| Beverages      | 4                | seasonal demand, overstock, transfer                |
| Household      | 3                | price mismatch, promotion signage, slow movement    |
| Pharmacy shelf | 3                | expiry, compliance, manager approval                |
| Electronics    | 3                | high-value stockout, supplier delay                 |

Example products:

- fresh tomatoes;
- salad packs;
- frozen beef patties;
- frozen vegetables;
- baguettes;
- croissants;
- fresh milk;
- yogurt multipack;
- bottled water;
- juice cartons;
- detergent;
- paper towels;
- pain relief tablets;
- batteries;
- phone chargers.

## Required Stores

Use three synthetic stores:

| Store ID               | Store name            | Demo role                                     |
| ---------------------- | --------------------- | --------------------------------------------- |
| `store-grand-baie-001` | Grand Baie Market     | tourism/weekend rush and promotion pressure   |
| `store-curepipe-001`   | Curepipe Central      | mixed stock, expiry, and staff pressure       |
| `store-port-louis-001` | Port Louis Waterfront | high traffic, queue pressure, supplier timing |

Each store should have:

- opening hours;
- role aliases;
- shelf areas;
- inventory positions;
- queue-pressure records;
- at least one active risk event.

## Required Suppliers

Use six synthetic suppliers:

| Supplier ID                 | Supplier type              | Risks to represent                          |
| --------------------------- | -------------------------- | ------------------------------------------- |
| `supplier-island-fresh-001` | fresh produce              | variable quality, fast replacement          |
| `supplier-coldchain-001`    | frozen and dairy logistics | cold-chain concern, delivery delay          |
| `supplier-bakeryline-001`   | bakery                     | same-day supply and waste                   |
| `supplier-bevco-001`        | beverages                  | seasonal bulk delivery                      |
| `supplier-homecare-001`     | household                  | slow-moving stock and promo price mismatch  |
| `supplier-techshelf-001`    | electronics/pharmacy shelf | high-value delay and controlled replacement |

Each supplier should have:

- normal lead time in days;
- emergency lead time in days;
- reliability score or qualitative status;
- contact alias, not a real email or phone;
- at least one response example.

## Data Objects To Create

### Product

Required fields:

- `productId`
- `sku`
- `name`
- `category`
- `storageType`: `ambient`, `chilled`, `frozen`, `controlled`, or `locked`
- `unit`
- `supplierId`
- `shelfArea`
- `isPerishable`
- `normalShelfLifeDays`
- `reorderPoint`
- `safetyStock`

### Product Batch

Required fields:

- `batchId`
- `productId`
- `supplierId`
- `receivedAt`
- `expiryDate`
- `quantityReceived`
- `quantityRemaining`
- `storeId` or `warehouseId`
- `qualityStatus`: `clear`, `watch`, `suspect`, `quarantined`, or `expired`
- `evidenceIds`

Only perishable, controlled, or quality-sensitive products need batches.

### Inventory Position

Required fields:

- `inventoryPositionId`
- `storeId`
- `productId`
- `shelfStock`
- `backroomStock`
- `reservedStock`
- `lastCountedAt`
- `countConfidence`: `high`, `medium`, or `low`
- `evidenceId`

### Warehouse Inventory

Required fields:

- `warehousePositionId`
- `productId`
- `availableStock`
- `reservedStock`
- `nextDispatchWindow`
- `evidenceId`

### Daily Sales Summary

Required fields:

- `salesSummaryId`
- `storeId`
- `productId`
- `businessDate`
- `unitsSold`
- `refundUnits`
- `averageUnitPrice`
- `promotionId` if applicable
- `evidenceId`

Use 14 days of summaries before the demo business date.

### Promotion

Required fields:

- `promotionId`
- `name`
- `storeIds`
- `productIds`
- `startsAt`
- `endsAt`
- `expectedUpliftMultiplier`
- `signageRequired`
- `priceOverride`
- `evidenceId`

### Complaint

Required fields:

- `complaintId`
- `storeId`
- `productId`
- `batchId` or `batchUnknownReason`
- `supplierId`
- `reportedAt`
- `complaintType`: `quality`, `smell`, `packaging`, `expiry`, `price`,
  `availability`, `refund`, `service`, or `cold_chain`
- `severity`: `low`, `medium`, `high`, or `critical`
- `summary`
- `refundRequested`
- `refundApproved`
- `evidenceId`

### Complaint Cluster

Required fields:

- `clusterId`
- `productId`
- `batchId` if known
- `storeIds`
- `supplierId`
- `firstReportedAt`
- `lastReportedAt`
- `complaintCount`
- `dominantTypes`
- `riskInterpretation`: `isolated`, `batch_specific`, `store_specific`,
  `supplier_suspected`, or `price_signage`
- `recommendedCaution`
- `evidenceIds`

### Supplier Response

Required fields:

- `supplierResponseId`
- `supplierId`
- `relatedClusterId`
- `receivedAt`
- `responseType`: `replacement_batch`, `credit_note`, `delivery_confirmed`,
  `delayed_delivery`, `insufficient_evidence`, `quality_denied`, or
  `corrective_action`
- `summary`
- `replacementBatchId` if applicable
- `expectedDeliveryAt` if applicable
- `changesRecommendation`: true or false
- `evidenceId`

### Roster And Queue Pressure

Required fields:

- `queueRecordId`
- `storeId`
- `businessDate`
- `timeBand`: `morning`, `midday`, `afternoon`, or `evening`
- `expectedFootfall`
- `expectedBasketCount`
- `cashiersScheduled`
- `floorStaffScheduled`
- `queueRisk`: `low`, `medium`, `high`, or `critical`
- `evidenceId`

### Staff Task Template

Required fields:

- `taskTemplateId`
- `taskType`: `restock`, `shelf_check`, `quarantine`, `markdown`, `signage`,
  `cashier_move`, `supplier_call`, `manager_review`, or `customer_notice`
- `defaultOwnerRole`
- `defaultDueMinutes`
- `requiresApproval`
- `messageTemplate`

### Channel Recipient Alias

Required fields:

- `recipientAliasId`
- `role`
- `storeId`
- `slackTarget`
- `whatsappTargetAlias`
- `canReceiveUrgentAlerts`

Use aliases only. Example: `role:grand-baie-duty-manager`.

## Required Complaint Scenarios

Create these exact scenario types:

1. Isolated low-severity complaint with no action beyond monitoring.
2. Batch-specific quality cluster for a fresh/frozen product.
3. Store-specific packaging complaints caused by shelf handling.
4. Supplier-suspected cold-chain complaint requiring supplier response.
5. Price mismatch complaints caused by promotion signage.
6. Expiry complaint where batch data confirms risk.
7. Refund pattern that looks high but is not linked to product quality.
8. High-severity food safety concern requiring manager escalation.

Each scenario should include:

- source complaints;
- cluster summary;
- related inventory/batch facts;
- supplier status if relevant;
- expected recommendation note.

## Required Expected Recommendation Cases

Create 12 expected recommendation notes:

| Case ID | Situation                       | Expected behavior                                         |
| ------- | ------------------------------- | --------------------------------------------------------- |
| ER-01   | clean stockout risk             | reorder or warehouse transfer                             |
| ER-02   | stockout plus complaint cluster | do not blindly reorder same batch; ask supplier/manager   |
| ER-03   | replacement batch confirmed     | update plan to replacement plus staff task                |
| ER-04   | near-expiry fresh food          | markdown, rotate, remove expired units                    |
| ER-05   | overstock beverages             | transfer or promotion adjustment                          |
| ER-06   | bakery same-day waste           | markdown and production adjustment                        |
| ER-07   | price mismatch                  | signage task and customer service note                    |
| ER-08   | queue risk during promotion     | move staff or open cashier                                |
| ER-09   | missing batch data              | cautious recommendation and missing evidence              |
| ER-10   | supplier denies quality issue   | preserve evidence, do not close without manager review    |
| ER-11   | malformed duplicate event       | intake should reject or dedupe without corrupting context |
| ER-12   | late supplier response          | recommendation should update and keep audit history       |

Each note should say:

- what the agent should recommend;
- what the agent should refuse to do;
- which evidence IDs matter;
- whether manager approval is needed;
- which Slack or WhatsApp alert would be appropriate after approval.

## Required Retail Event Fixtures

Prepare 18 to 24 retail event fixtures using the existing event-envelope style.
Include:

- stockout risk detected;
- expiry risk detected;
- complaint cluster detected;
- supplier response received;
- queue risk detected;
- action outcome captured;
- duplicate event;
- malformed event;
- late event;
- out-of-order event;
- idempotency conflict;
- invalid content hash.

Recommended future path:

```text
integration/events/fixtures/retail/
```

If implementation has not created that folder yet, write the data plan and JSON
drafts clearly so another Codex session can wire them into the validator.

## How The Agents Will Use The Data

### Inventory and Waste Agent

Consumes:

- product catalog;
- inventory positions;
- warehouse inventory;
- daily sales summaries;
- promotions;
- product batches;
- supplier lead time.

Produces:

- days of cover;
- sales at risk;
- waste risk units;
- markdown, transfer, reorder, or quarantine recommendation;
- missing evidence list.

### Supplier and Product Trust Agent

Consumes:

- complaints;
- complaint clusters;
- refund records;
- batch quality status;
- supplier response;
- supplier reliability.

Produces:

- isolated versus meaningful cluster classification;
- batch-specific versus supplier-wide caution;
- supplier response request;
- replacement batch, credit note, quarantine, escalation, or customer-message
  recommendation.

### Store Execution and Outreach Agent

Consumes:

- task templates;
- queue pressure;
- store roles;
- channel recipient aliases;
- approved action plan.

Produces:

- restock task;
- shelf check;
- quarantine task;
- signage task;
- cashier movement;
- Slack/WhatsApp target role;
- acknowledgement expectation.

### Orchestrator Topic

Consumes all agent outputs and expected recommendation notes.

Produces one final plan:

- facts;
- inferences;
- recommendation;
- required approvals;
- protected actions;
- channel alerts;
- outcome metrics.

## Implementation Checklist

- [ ] Pull latest `main`.
- [ ] Read this file and the required docs.
- [ ] Create the data inventory table before writing large JSON files.
- [ ] Draft product catalog with 30 products across 8 categories.
- [ ] Draft 3 stores and 6 suppliers.
- [ ] Draft 45 to 60 product batches.
- [ ] Draft inventory positions for all products in all stores.
- [ ] Draft warehouse inventory for all products.
- [ ] Draft 14 days of daily sales summaries.
- [ ] Draft 8 promotions.
- [ ] Draft 50 to 70 complaints.
- [ ] Draft 8 complaint clusters.
- [ ] Draft 10 supplier responses.
- [ ] Draft queue and roster pressure records.
- [ ] Draft staff task templates and channel recipient aliases.
- [ ] Draft 12 expected recommendation notes.
- [ ] Draft 18 to 24 retail event fixtures.
- [ ] Include duplicate, malformed, late, out-of-order, idempotency-conflict,
      and invalid-hash cases.
- [ ] Check that every scenario has evidence IDs.
- [ ] Check that no scenario is burger-only.
- [ ] Check that supplier complaints never automatically stop all supplier
      orders.

## Validation Checklist

- [ ] Every product has a category, supplier, and shelf area.
- [ ] Every perishable product has at least one batch.
- [ ] Every complaint links to product, store, supplier, and evidence.
- [ ] Every complaint cluster has source complaint IDs.
- [ ] Every supplier response links to a cluster.
- [ ] Every expected recommendation names evidence IDs.
- [ ] Every protected action says whether approval is needed.
- [ ] Every channel recipient is an alias, not personal contact data.
- [ ] Every messy event has a clear expected intake result.
- [ ] The final demo story has a trigger, conflict, supplier response, approval,
      action, alert, and outcome.

## Demo Acceptance

The data work is demo-ready when:

- the demo can start from one retail risk event;
- evidence includes inventory, expiry, complaint, supplier, promotion, and queue
  context;
- the agent recommendation changes after supplier response;
- there are multiple product categories visible;
- there is at least one clean stockout story and one complaint-sensitive story;
- fake data is realistic but clearly synthetic;
- another teammate can use the data without asking what each ID means.

## Codex Or Local LLM Prompt Starter

Use this when starting a fresh task:

```text
Read docs/assignments/aarav.md, docs/north-star-mvp.md,
docs/event-contract.md, docs/salesforce-data-model.md, and docs/demo-harness.md.
Create or refine synthetic North Star retail data. Use deterministic IDs,
multiple product categories, complaint clusters, supplier responses, messy event
cases, and expected recommendation notes. Do not use real personal data. Keep
the output usable by the Inventory/Waste, Supplier/Product Trust, Store
Execution/Outreach, and Orchestrator agents.
```
