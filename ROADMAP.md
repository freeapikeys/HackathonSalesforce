# Closed-Loop Intelligence RM Roadmap

This roadmap is the branch checklist. Keep it honest: mark an item complete only
when the code, fixture, UI, test, or demo evidence exists in the repo.

## Branch Direction

Build a permissioned enterprise intelligence and relationship-management loop
on Salesforce, Agentforce, Data 360, and MuleSoft.

The product collects authorized first-party business data, preserves source
evidence, maps fragmented terminology, forms conclusions and recommendations,
coordinates humans and agents across relationships, records outcomes, and feeds
those outcomes back into the next cycle.

The supermarket command-center material is one demo vertical. It must prove the
loop, not replace the broader product direction.

See [docs/closed-loop-intelligence-rm.md](docs/closed-loop-intelligence-rm.md)
and
[docs/decisions/0006-closed-loop-intelligence-rm-branch.md](docs/decisions/0006-closed-loop-intelligence-rm-branch.md).

## Retail Demo Vertical

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

## Jury Gift Verticals

The jury gifts are tailored demo verticals that reuse the same closed-loop
evidence/action spine. They should feel specific to the company, but they must
not become five separate products.

Research source:
[docs/research/jury-gift-dossiers-2026-06-10.md](docs/research/jury-gift-dossiers-2026-06-10.md).

### Flagship Gifts

- [ ] Air Mauritius Passenger Recovery Command Center: claims, disruption,
      baggage, compensation triage, approval, passenger updates, and outcome
      feedback.
- [ ] Constance Guest Revenue and Operations Loop: reservations email
      extraction, FX-to-ERP, sentiment-to-occupancy, approved hospitality
      actions, and outcome feedback.
- [ ] Nexavenu Revenue Intelligence and Champion Nurture Tower: attribution,
      lead qualification, buyer education, champion mapping, discovery
      readiness, close plan, retention/ascension signals, and content gaps.

### Tailored Overlays

- [ ] AfrAsia Relationship Intelligence Control Tower: private banking, KYC/AML
      guardrails, cross-border RM, FX/wealth signals, approval, and outcome
      feedback.
- [ ] Sunlife Guest Recovery and Experience Intelligence Loop: WhatsApp-style
      guest recovery, staff task coordination, sustainability evidence, service
      quality, and repeat-stay risk.

### Nexavenu Business-System Notes

- [x] Contact-sourced signals captured privately: 10% close rate, 6-month
      discovery, big client churn, and dissatisfaction despite previous loyalty.
- [x] Public OSINT confluence captured: BDR hiring, qualification/nurture
      responsibilities, C-level engagement, marketing handoffs, CRM pipeline
      reporting, AI/Data 360 readiness positioning, MuleSoft modernization, and
      long-run customer success language.
- [x] Build synthetic Nexavenu revenue pipeline fixtures without presenting
      contact-sourced metrics as public fact.
- [x] Show the full business pipeline:
      `lead generation -> lead nurture -> sales -> fulfillment -> retention/ascension`.
- [x] Show the buyer journey:
      `problem -> awareness -> struggle -> education -> search -> comparison -> test -> purchase -> first impressions`.
- [x] Recommendation separates public facts, contact-sourced assumptions,
      inferences, next actions, approval requirements, and expected outcomes.

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

- [x] Closed-loop intelligence RM selected as the private branch direction.
- [x] Branch doctrine created in `docs/closed-loop-intelligence-rm.md`.
- [x] Branch decision recorded in
      `docs/decisions/0006-closed-loop-intelligence-rm-branch.md`.
- [x] Supermarket operations retained as a retail demo vertical.
- [x] Retail MVP brief retained in `docs/north-star-mvp.md`.
- [x] Retail implementation plan retained in
      `docs/north-star-implementation-plan.md`.
- [x] Supermarket issue map retained as demo scenario coverage.
- [ ] Retail roadmap items audited and mapped to reusable relationship
      intelligence capabilities.
- [ ] One-sentence branch product pitch finalized.
- [x] Three-minute retail judge demo narrative drafted.
- [x] Five-minute retail extended demo narrative drafted.
- [x] Backup recorded-demo path defined in case live integrations fail.
- [ ] Final branch non-goals reviewed before any publication.

### 2. Product Categories and Demo Data

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

### 3. Retail Event Fixtures

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
- [x] Source-intake verifier emits a machine-readable report for fixture
      classification, MuleSoft replay/quarantine behavior, and Salesforce
      check-only persistence tests.

### 4. Shared Semantics and Provenance

- [x] Extend ontology and JSON-LD context for source-local terminology,
      canonical concepts, PROV-compatible source agents, and source activities.
- [x] Model source assertions and derived inferences with valid time, recorded
      time, attribution, generation provenance, and explicit supersession.
- [x] Valid fixture proves source terminology, provenance, assertion kind, valid
      time, recorded time, and supersession.
- [x] Invalid fixture proves missing provenance, missing terminology mapping,
      missing assertion kind, missing relationship validity, missing
      recommendation support, and unsuperseded contradictions are rejected.
- [x] Map event, Salesforce, and Data 360 semantics with versioned ownership,
      transformation rules, and ambiguity notes.
- [x] Add deterministic current-state and historical-belief queries over
      versioned assertions.
- [x] Add a shared semantics verification harness that proves ontology,
      mappings, temporal queries, source terminology, supersession, and source
      evidence together.
- [x] Add versioned metric definitions and deterministic outcome-attribution
      verification from source fixtures.

### 5. Identity Relationships and History

- [x] Add an identity-history verifier over preserved source fixtures.
- [x] Resolve source identities from subjects, business keys, and relationship
      attributes without dropping source record IDs.
- [x] Build relationship edges with visible confidence and source evidence.
- [x] Preserve participant links for events and source-derived entities.
- [x] Preserve late, out-of-order, update, and conflicting correction history.
- [x] Keep contradictory agreement status assertions visible instead of
      overwriting them.
- [x] Prove a traversable person-to-organization-to-supplier path.
- [x] Expose event participant identity links in Salesforce context and
      provenance responses.
- [x] Add user-facing relationship inspection and correction affordances.
- [x] Persist correction-review work items, source evidence, recommendations,
      and pending approvals.
- [x] Persist approved supersession decisions onto relationship/assertion
      history.

### 6. Salesforce Core

- [x] Map store to existing Salesforce entity record.
- [x] Map product to existing Salesforce entity record.
- [x] Map product batch to existing Salesforce entity or add the smallest
      needed field/type.
- [x] Map supplier to existing Salesforce entity record.
- [x] Map promotion to event, agreement, or work context.
- [x] Map complaints to evidence records.
- [x] Persist accepted and review-required intake results to immutable
      `HFS_Event__c` records with scoped idempotency and source payload
      preservation.
- [ ] Map store tasks to action records and/or Salesforce task records.
- [x] Add optional metadata only when current records cannot express demo needs.
- [x] Work items preserve owner role, dependency, handoff, escalation, and
      outcome-verified closure state.
- [ ] Apex context includes product, batch, store, supplier, promotion,
      complaint, stock, staffing, recommendation, approval, action, and outcome.
- [ ] Manager approval is enforced before reorder, supplier case, markdown,
      quarantine, staff alert, or customer-facing message.
- [ ] Action and outcome records preserve correlation IDs and evidence IDs.
- [ ] Apex tests cover success, denial, inaccessible evidence, approval
      mismatch, and invalid state.

### 7. Agentforce and Intelligence

- [x] Define North Star Orchestrator topic.
- [x] Define Inventory and Demand topic.
- [x] Define Store Operations topic.
- [x] Define Customer and Risk Intelligence topic.
- [x] Recommendation request includes inventory, expiry, supplier, complaint,
      promotion, and staffing evidence.
- [x] Recommendation response separates facts, inferences, assumptions,
      recommended actions, approval requirements, and expected outcomes.
- [x] Supplier decision follows the rule: do not blindly stop all supplier
      orders because complaints exist.
- [x] Agentforce updates recommendation after supplier response arrives.
- [x] Agentforce refuses restricted or missing evidence.
- [x] Model gateway uses logical profile names, not provider-specific or
      product-specific names.
- [x] Agentforce fixtures include a denied-action scenario.
- [x] Agentforce fixtures include a changed-recommendation scenario.
- [x] Agentforce fixtures include a Nexavenu revenue-intelligence scenario.

### 8. MuleSoft and Channel Mocks

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
- [x] Mock Nexavenu revenue actions: `CREATE_NURTURE_TASK`,
      `DRAFT_CHAMPION_EMAIL`, `UPDATE_OPPORTUNITY_STAGE`,
      `ASSIGN_CONTENT_ASSET`, `CREATE_SOLUTION_CONSULTANT_HANDOFF`, and
      `CAPTURE_RETENTION_ASCENSION_OUTCOME`.
- [x] Unapproved execution returns denial.
- [x] Approved execution returns queued or success response with correlation.
- [x] Mock channel results are visible in the command center.

### 9. Lightning Command Center

- [x] UI title and labels use North Star.
- [x] Profile key switches visible titles, domain labels, recommendation copy,
      approval copy, and outcome labels between North Star retail and Nexavenu
      gift profiles.
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
