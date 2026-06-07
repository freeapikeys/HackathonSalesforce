# North Star MVP

## Product Position

North Star is an Agentforce-powered retail operations command center for
supermarkets and multi-store retailers. It coordinates inventory, expiry,
supplier recovery, complaints, promotions, and staff execution across all
product categories.

The MVP is not a generic chatbot and not a burger-only demo. Burger patties can
be used as the first story because the scenario is easy to understand, but every
object, prompt, action, and UI label should work for any product: fresh produce,
frozen items, bakery, dairy, beverages, household goods, pharmacy items,
electronics, school supplies, seasonal products, or high-value locked products.

## Winning Demo Story

A supermarket is preparing a weekend promotion. One promoted product is at risk:

- point-of-sale data shows demand will exceed shelf and warehouse stock;
- batch and expiry records show some units should be sold or removed soon;
- complaints mention smell, packaging damage, refund requests, or price
  mismatch;
- supplier lead time and supplier reliability are uncertain;
- store staffing data shows peak queue pressure;
- the store manager needs one coordinated recovery plan before the rush.

A weak agent simply says "order more." North Star does more:

1. separates source facts from inference;
2. checks whether the issue is product-wide, batch-specific, store-specific, or
   supplier-specific;
3. asks the supplier for a resolution before recommending a final supplier
   decision;
4. compares options: reorder, replacement batch, warehouse transfer, alternate
   supplier, markdown, promotion adjustment, quarantine, or manager escalation;
5. creates approved tasks and outreach through Salesforce and MuleSoft;
6. alerts staff through Slack and WhatsApp-style channels;
7. records outcomes so the next recommendation can learn from what happened.

## Three-Agent System

North Star should feel like one coordinated product, not four disconnected
chatbots. The MVP therefore has three specialist agents plus a lightweight
orchestrator topic that combines their outputs into one recommendation.

### North Star Orchestrator Topic

The orchestrator topic owns the final decision trace. It receives the unified
retail context, asks the three specialist agents for analysis, resolves
tradeoffs, and produces one action plan with required approvals.

Responsibilities:

- decide whether a situation is a stockout, waste, supplier, complaint, price,
  promotion, or staffing incident;
- combine facts from all specialist agents;
- create one recommendation instead of separate disconnected suggestions;
- define which actions are autonomous and which require manager approval;
- log the decision trace, assumptions, confidence, and evidence.

### Inventory and Waste Agent

Main job: protect availability while reducing waste.

Responsibilities:

- calculate days of cover from sales velocity and on-hand stock;
- detect stockout risk for any product;
- detect overstock and dead-stock risk;
- inspect expiry batches and near-expiry quantities;
- recommend transfer, reorder, markdown, quarantine, or promotion adjustment;
- distinguish shelf stock, backroom stock, warehouse stock, and supplier stock;
- estimate waste avoided and sales-at-risk.

Evidence examples:

- POS sales history;
- inventory position;
- shelf/backroom/warehouse stock;
- product batch and expiry date;
- promotion calendar;
- supplier lead time.

### Supplier and Product Trust Agent

Main job: protect product trust without making bad supplier decisions.

Responsibilities:

- detect complaint clusters by product, batch, supplier, store, and time;
- determine whether complaints are batch-specific or supplier-wide;
- classify complaints into quality, price mismatch, packaging, expiry, service,
  refund, and availability issues;
- distinguish isolated complaints from statistically meaningful clusters;
- open supplier quality cases;
- request supplier response, credit note, replacement batch, delivery
  confirmation, or proof of corrective action;
- evaluate supplier response before blocking future orders;
- recommend safe alternatives: replacement batch, partial reorder, alternate
  supplier, warehouse transfer, or manager approval;
- trigger manager escalation for food safety, allergen, expiry, or high-volume
  complaints;
- recommend customer-facing messages only from approved templates;
- preserve evidence so supplier conversations are auditable.

Important rule:

North Star must not automatically stop all supplier orders just because
complaints exist. It can quarantine a suspicious batch, request supplier
resolution, and require manager approval for consequential supplier changes.

### Store Execution and Outreach Agent

Main job: make the plan happen inside the store.

Responsibilities:

- create restocking, shelf-check, quarantine, markdown, and signage tasks;
- assign tasks to store roles such as floor supervisor, stockroom, cashier lead,
  fresh-food lead, and duty manager;
- detect peak queue risk from historical sales and promotion windows;
- recommend cashier allocation and staff movement;
- track acknowledgements through Salesforce, Slack, and WhatsApp-style alerts;
- produce internal alert drafts for Slack and WhatsApp-style channels;
- escalate missed tasks before the promotion or rush window.

## Demo Phases

1. **Trigger:** launch a retail risk event for a selected product category.
2. **Context:** show product, store, batch, complaint, supplier, promotion, and
   staffing evidence.
3. **Conflict:** inventory wants reorder, complaints warn of quality risk, and
   store execution predicts a queue spike.
4. **Supplier response:** supplier confirms a replacement batch, credit note,
   delayed delivery, or unresolved quality issue.
5. **Recommendation:** Agentforce proposes a recovery plan with cited facts and
   inferences.
6. **Approval:** manager approves consequential actions.
7. **Action:** MuleSoft mock executes Salesforce task creation, supplier case,
   reorder or transfer request, Slack alert, WhatsApp-style alert, and outcome
   callback.
8. **Outcome:** command center updates with avoided stockout, waste reduced,
   complaint containment, staff readiness, and supplier SLA state.

## Demo Data

Use several product categories so the system does not look burger-only:

| Category       | Example risk                                        |
| -------------- | --------------------------------------------------- |
| Fresh food     | Expiry, quality complaint, demand spike             |
| Frozen food    | Stockout, freezer batch concern, supplier lead time |
| Bakery         | Same-day waste, promotion readiness                 |
| Dairy          | Expiry and cold-chain complaint                     |
| Beverages      | Overstock and seasonal demand                       |
| Household      | Price mismatch and promotion signage                |
| Electronics    | High-value stockout and supplier delay              |
| Pharmacy shelf | expiry, compliance, and manager approval            |

## Non-Goals

- Do not claim real POS, supplier, WhatsApp, or Slack production integrations
  unless they are configured and demonstrated.
- Do not claim machine-learning forecasting if the prototype uses deterministic
  rules. Say "rules-based baseline with model-ready architecture."
- Do not let Agentforce execute protected external actions directly.
- Do not hard-code one product or one supplier into architecture.
- Do not hide uncertainty behind one unexplained score.

## Success Criteria

The demo succeeds when judges see:

- messy retail signals becoming a single operational plan;
- Agentforce changing its recommendation after supplier evidence arrives;
- manager approval gating consequential changes;
- Slack and WhatsApp-style alerts reaching internal staff;
- Salesforce records preserving evidence, tasks, approvals, actions, and
  outcomes;
- architecture that can be adapted to hotels, telecom shops, airport retail,
  smart districts, or any inventory-heavy business.
