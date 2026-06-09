# North Star Roadmap

This roadmap is the hackathon checklist. Keep it honest: mark an item complete
only when the code, fixture, UI, test, or demo evidence exists in the repo.

## North Star

Build a Salesforce and Agentforce command center that helps a supermarket
manager prevent stockouts, reduce waste, handle supplier quality issues, and
coordinate staff actions before the rush.

North Star must answer:

- What product, batch, store, supplier, promotion, shelf area, and team are
  involved?
- What source evidence triggered the risk?
- Is the issue stockout, expiry, overstock, cold chain, complaint, supplier,
  queue, shelf-layout, price, promotion, or a mix?
- Which agent found the issue and what does it recommend?
- Which facts are source evidence and which are inference?
- Which actions need manager approval?
- What action was executed, through which mock channel, and what happened next?

## Supermarket Issues We Solve

These are the issues from the multi-agent brief that North Star must cover.

| ID    | Supermarket issue                        | Primary agent                        | Demo response                                                                 |
| ----- | ---------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------- |
| NS-01 | Stock finishing soon                     | Inventory and Demand Agent           | Predict days of cover, check warehouse stock, recommend reorder or transfer   |
| NS-02 | Poor stock capacity planning             | Inventory and Demand Agent           | Compare sales velocity, promotion demand, stock-on-hand, and supplier lead    |
| NS-03 | Overstock and dead stock                 | Inventory and Demand Agent           | Detect slow-moving products and recommend markdown, transfer, or promo change |
| NS-04 | Expired food not replaced in time        | Inventory and Demand Agent           | Flag expired or near-expiry batches and create removal/replacement tasks      |
| NS-05 | Food waste risk                          | Inventory and Demand Agent           | Estimate waste risk and suggest rotation, discount, or markdown               |
| NS-06 | Seasonal or promotion demand spike       | Inventory and Demand Agent           | Use historical/promotion data to forecast demand pressure                     |
| NS-07 | Supplier delay risk                      | Inventory and Demand Agent           | Compare lead time against days of cover and suggest alternatives              |
| NS-08 | Cashier allocation problems              | Store Operations Agent               | Predict peak queue windows and recommend cashier/staff movement               |
| NS-09 | Peak-hour queue risk                     | Store Operations Agent               | Use past traffic/sales patterns and create staffing recommendations           |
| NS-10 | Misplaced items or shelf-layout mismatch | Store Operations Agent               | Create shelf-check and correction tasks                                       |
| NS-11 | Restocking work not prioritized          | Store Operations Agent               | Assign refill, rotation, quarantine, markdown, and signage tasks              |
| NS-12 | Staff task prioritization is unclear     | Store Operations Agent               | Rank tasks by risk, deadline, customer impact, and approval state             |
| NS-13 | Customer complaint clusters              | Customer and Risk Intelligence Agent | Detect repeated complaints by product, batch, store, supplier, and time       |
| NS-14 | Product quality issues                   | Customer and Risk Intelligence Agent | Connect smell, packaging, refund, or quality reports to batch/supplier        |
| NS-15 | Supplier reliability concern             | Customer and Risk Intelligence Agent | Ask for supplier response before changing reorder decision                    |
| NS-16 | Price mismatch complaints                | Customer and Risk Intelligence Agent | Link complaint, shelf price, POS price, promo, and signage task               |
| NS-17 | Repeated refunds or damaged packaging    | Customer and Risk Intelligence Agent | Escalate bad-batch or packaging-risk review                                   |
| NS-18 | Reputation or customer satisfaction risk | Customer and Risk Intelligence Agent | Draft manager-approved internal/customer-facing response                      |
| NS-19 | Promotion planning failure               | North Star Orchestrator              | Combine stock, price, queue, supplier, and complaint signals into one plan    |
| NS-20 | Cold chain failure                       | Customer and Risk Intelligence Agent | Treat as high-risk future extension requiring quarantine and manager approval |

## Agent Responsibilities

### North Star Orchestrator

- [ ] Combine inventory, supplier, customer-risk, and store-operation findings
      into one recovery plan.
- [ ] Resolve conflicts, for example "reorder now" versus "do not reorder this
      batch until supplier confirms quality."
- [ ] Decide which actions require manager approval.
- [ ] Produce one recommendation with facts, inferences, confidence, and
      expected outcome.
- [ ] Update the recommendation after supplier response arrives.

### Inventory and Demand Agent

- [ ] Detect stock finishing soon using sales velocity and current stock.
- [ ] Check shelf, backroom, warehouse, and supplier stock.
- [ ] Calculate days of cover.
- [ ] Include supplier lead time in reorder recommendation.
- [ ] Detect slow-moving products, overstock, and dead stock.
- [ ] Detect expired and near-expiry batches.
- [ ] Recommend rotation, discount, markdown, reorder, or transfer.
- [ ] Estimate sales-at-risk and waste-at-risk.
- [ ] Handle seasonal and promotion demand prediction.

### Store Operations Agent

- [ ] Predict peak-hour queue risk.
- [ ] Recommend cashier allocation for the risky window.
- [ ] Recommend moving staff from aisle duty to checkout when needed.
- [ ] Create restocking tasks.
- [ ] Create shelf-layout and misplaced-item correction tasks.
- [ ] Create expiry removal and fresh-product rotation tasks.
- [ ] Prioritize staff tasks by urgency and risk.
- [ ] Track task acknowledgement and completion.

### Customer and Risk Intelligence Agent

- [ ] Detect complaint clusters.
- [ ] Classify complaints into quality, smell, damaged packaging, price
      mismatch, refund, service, expiry, and availability.
- [ ] Connect complaints to product, batch, supplier, store, and promotion.
- [ ] Detect bad-batch risk.
- [ ] Detect repeated refunds and damaged packaging reports.
- [ ] Evaluate supplier reliability and response.
- [ ] Escalate high-risk cases to manager or supplier.
- [ ] Draft approved message or alert text without sending it directly.

## Demo Story

A promoted supermarket product is at risk before a weekend rush. POS demand is
rising, stock cover is low, some units are near expiry, complaints mention
quality or price mismatch, supplier lead time is uncertain, and queue pressure
is expected later in the day.

North Star should produce one recovery plan:

- inspect or quarantine risky batch if needed;
- choose reorder, transfer, markdown, promotion adjustment, or supplier case;
- assign store tasks;
- send internal Slack and WhatsApp-style alerts;
- require manager approval for consequential actions;
- record outcome metrics.

The story may use burger patties for the first demo, but the labels, fixtures,
and UI must support any supermarket product category.

## Detailed Checklist

### 1. Product Direction and Scope

- [x] Supermarket operations selected as the hackathon scope.
- [x] Product name changed to North Star in active docs.
- [x] MVP brief created in `docs/north-star-mvp.md`.
- [x] Implementation plan created in `docs/north-star-implementation-plan.md`.
- [x] Old broad platform wording removed from active docs.
- [x] Supermarket issue map added to this roadmap.
- [x] Teammate assignment docs created in `docs/assignments/`.
- [x] One-sentence product pitch finalized.
- [x] Three-minute judge demo narrative drafted.
- [x] Five-minute extended demo narrative drafted.
- [x] Backup recorded-demo path defined in case live integrations fail.
- [x] Final non-goals reviewed by whole team.

### 2. Team Assignment Checkpoints

Each teammate has a detailed assignment file. AI agents should read the relevant
file before editing.

- [ ] Aarav: create realistic synthetic retail data, complaints, supplier
      responses, queue pressure, task templates, and channel recipient aliases.
- [ ] Fahan: implement `SEND_SLACK_ALERT` behind approved MuleSoft action
      execution, with real webhook support only through `SLACK_WEBHOOK_URL` and
      honest `MOCK_SENT` fallback.
- [ ] Hassan: implement `SEND_WHATSAPP_ALERT` behind approval and add the
      voice-mode prototype that converts operator speech/transcript into a
      governed request without bypassing approval.
- [ ] Ranveer: implement Inventory and Waste reasoning with deterministic
      stockout, expiry, waste, overstock, promotion-readiness calculations and
      evidence-backed recommendation output.
- [ ] Merge owner: keep branches aligned, review conflicts, protect `main`, and
      verify the demo still tells one North Star story.

### 3. Product Categories and Demo Data

- [x] Choose first demo product category and product.
- [x] Add at least two other product categories to prove this is not
      burger-only.
- [x] Define store, supplier, product, product batch, promotion, shelf area,
      roster, and task fixture IDs.
- [x] Define stock quantities for shelf, backroom, warehouse, and supplier.
- [x] Define sales velocity and forecast window.
- [x] Define supplier lead time and supplier response options.
- [x] Define complaint examples for smell, packaging, price mismatch, refund,
      and availability.
- [x] Define expiry dates and near-expiry quantities.
- [x] Define queue-risk window and staffing baseline.
- [x] Define expected outcome metrics for the demo.

### 4. Retail Event Fixtures

- [x] Add `STOCKOUT_RISK_DETECTED` fixture.
- [x] Add `WAREHOUSE_STOCK_CHECKED` fixture.
- [x] Add `SUPPLIER_LEAD_TIME_UPDATED` fixture.
- [x] Add `EXPIRY_RISK_DETECTED` fixture.
- [x] Add `NEAR_EXPIRY_MARKDOWN_RECOMMENDED` fixture.
- [x] Add `COMPLAINT_CLUSTER_DETECTED` fixture.
- [x] Add `PRICE_MISMATCH_REPORTED` fixture.
- [x] Add `DAMAGED_PACKAGING_REPORTED` fixture.
- [x] Add `SUPPLIER_RESPONSE_RECEIVED` fixture.
- [x] Add `QUEUE_RISK_DETECTED` fixture.
- [x] Add `SHELF_LAYOUT_MISMATCH_DETECTED` fixture.
- [x] Add `STORE_TASK_CREATED` fixture.
- [x] Add `APPROVED_ACTION_EXECUTED` fixture.
- [x] Add `RETAIL_OUTCOME_CAPTURED` fixture.
- [x] Keep duplicate, malformed, late, out-of-order, replay, hash, and
      idempotency-conflict cases passing.

### 5. Salesforce Core

- [x] Map store to existing Salesforce entity record.
- [x] Map product to existing Salesforce entity record.
- [x] Map product batch to existing Salesforce entity or add the smallest
      needed field/type.
- [x] Map supplier to existing Salesforce entity record.
- [x] Map promotion to event, agreement, or work context.
- [x] Map complaints to evidence records.
- [ ] Map store tasks to action records and/or Salesforce task records.
- [x] Add optional metadata only when current records cannot express demo needs.
- [ ] Apex context includes product, batch, store, supplier, promotion,
      complaint, stock, staffing, recommendation, approval, action, and outcome.
- [ ] Manager approval is enforced before reorder, supplier case, markdown,
      quarantine, staff alert, or customer-facing message.
- [ ] Action and outcome records preserve correlation IDs and evidence IDs.
- [ ] Apex tests cover success, denial, inaccessible evidence, approval
      mismatch, and invalid state.

### 6. Agentforce and Intelligence

- [x] Define North Star Orchestrator topic.
- [x] Define Inventory and Demand topic.
- [x] Define Store Operations topic.
- [x] Define Customer and Risk Intelligence topic.
- [x] Recommendation request includes inventory, expiry, supplier, complaint,
      promotion, and staffing evidence.
- [ ] Recommendation response separates facts, inferences, assumptions,
      recommended actions, approval requirements, and expected outcomes.
- [x] Supplier decision follows the rule: do not blindly stop all supplier
      orders because complaints exist.
- [x] Agentforce updates recommendation after supplier response arrives.
- [x] Agentforce refuses restricted or missing evidence.
- [x] Model gateway uses retail profile names, not product-specific names.
- [x] Agentforce fixtures include a denied-action scenario.
- [x] Agentforce fixtures include a changed-recommendation scenario.

### 7. MuleSoft and Channel Mocks

- [x] Mock `CREATE_SUPPLIER_QUALITY_CASE`.
- [x] Mock `REQUEST_REPLACEMENT_BATCH`.
- [x] Mock `CREATE_REORDER_REQUEST`.
- [x] Mock `CREATE_WAREHOUSE_TRANSFER`.
- [x] Mock `CREATE_MARKDOWN_PLAN`.
- [x] Mock `CREATE_QUARANTINE_TASK`.
- [x] Mock `CREATE_RESTOCK_TASK`.
- [x] Mock `CREATE_SHELF_LAYOUT_TASK`.
- [x] Mock `OPEN_EXTRA_CASHIER_TASK`.
- [x] Mock `SEND_SLACK_ALERT`.
- [x] Mock `SEND_WHATSAPP_STYLE_ALERT`.
- [x] Mock `CAPTURE_RETAIL_OUTCOME`.
- [x] Unapproved execution returns denial.
- [x] Approved execution returns queued or success response with correlation.
- [x] If `SLACK_WEBHOOK_URL` exists, send real Slack webhook message.
- [x] If `SLACK_WEBHOOK_URL` is missing, return honest `MOCK_SENT`.
- [x] Malformed Slack payloads return validation errors.
- [ ] Malformed WhatsApp payloads return validation errors.
- [x] Slack channel responses preserve `tenantId`, `correlationId`,
      `approvalId`, `actionId`, evidence IDs, provider, status, and fallback
      reason.
- [ ] WhatsApp channel responses preserve `tenantId`, `correlationId`,
      `approvalId`, `actionId`, evidence IDs, provider, status, and fallback
      reason.
- [x] Mock channel results are visible in the command center.

### 8. Voice Mode

- [ ] Add voice transcript input or browser speech input path.
- [ ] Convert transcript into structured product, issue, store, urgency, and
      evidence fields.
- [ ] Voice mode can ask Agentforce for a recommendation.
- [ ] Voice mode cannot execute Slack, WhatsApp, reorder, markdown, supplier,
      or task actions directly.
- [ ] Voice mode refusal is visible when the user asks it to bypass manager
      approval.
- [ ] LWC or fixture tests cover transcript-to-request and protected-action
      refusal.

### 9. Lightning Command Center

- [x] UI title and labels use North Star.
- [x] Risk pulse cards show stockout, expiry, overstock, complaint, supplier,
      queue, shelf-layout, price, promotion, and staff readiness.
- [x] Product and batch context is visible.
- [x] Shelf, backroom, warehouse, and supplier stock are visible.
- [x] Complaint cluster panel shows complaint type, count, product, batch,
      supplier, and time window.
- [x] Supplier response panel shows status, lead time, replacement, credit note,
      or unresolved quality issue.
- [x] Store execution panel shows cashier recommendation and task queue.
- [x] Evidence timeline cites source records.
- [x] Agent reasoning panel separates facts from inference.
- [ ] Approval cockpit supports approve, reject, modify, defer, and executed
      states.
- [x] Channel log shows Slack and WhatsApp-style alert results.
- [ ] Voice transcript or voice request panel is visible if voice mode is in
      the demo.
- [x] Outcome panel shows stockout avoided, waste reduced, complaint risk,
      queue readiness, staff task completion, and supplier SLA state.
- [x] LWC tests cover ready, loading, empty, denied, error, restricted,
      approval, action, and outcome states.

### 10. End-to-End Demo

- [ ] `npm run check` passes in the intended demo environment.
- [ ] `npm run demo:reset` works.
- [ ] `npm run demo:seed` creates the retail case.
- [ ] `npm run demo:run` completes trigger through outcome.
- [ ] Clean-clone runbook reflects the North Star flow.
- [ ] Demo starts from one clear supermarket risk event.
- [ ] Demo shows conflicting recommendations before orchestration.
- [ ] Demo shows supplier response changing the recommendation.
- [ ] Demo shows manager approval before action execution.
- [ ] Demo shows Slack and WhatsApp-style internal alerts.
- [ ] Demo shows voice mode only if it is stable and honest.
- [ ] Demo shows outcome metrics and audit trail.
- [ ] Final rehearsal completed with the whole team.

### 11. Pitch and Presentation

- [ ] Problem slide explains the supermarket issues from this roadmap.
- [ ] Agent slide explains the three specialist agents and orchestrator.
- [ ] Salesforce slide explains Agentforce, Salesforce records, MuleSoft mocks,
      and approval boundary.
- [ ] Demo slide shows the exact live flow.
- [ ] Business value slide quantifies stockout avoided, waste reduced, queue
      readiness, supplier response, and complaint containment.
- [ ] Honesty slide states what is mocked and what is production-ready
      architecture.
- [ ] Timing has been rehearsed.

## Done Means

A task is done only when:

- the implementation or fixture exists;
- the relevant check passes;
- the demo state is visible to a judge;
- failure or denial behavior is handled;
- docs are updated without broad platform wording.

## Non-Goals

- Do not build a general business platform for this hackathon.
- Do not build a burger-only demo.
- Do not claim live integrations that are actually mocks.
- Do not let agents execute protected external actions without manager
  approval.
- Do not add new architecture unless it directly improves the North Star demo.
