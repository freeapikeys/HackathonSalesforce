# North Star Demo Narrative

## Product Pitch

North Star is a Salesforce and Agentforce command center that turns supermarket
inventory, supplier, complaint, promotion, and staffing signals into one
manager-approved recovery plan before customers feel the problem.

## Three-Minute Judge Demo

The demo opens with a weekend promotion risk at Goodlands FreshMart. The
command center shows that promoted island beef burger patties are selling faster
than planned, shelf stock is low, the warehouse can cover only part of the gap,
and a subset of batch `BATCH-FRESH-BEEF-2026-06-07-A` is near expiry.

North Star then reveals the conflict. The Inventory and Demand Agent recommends
reorder or warehouse transfer because days of cover are below the weekend
threshold. The Customer and Risk Intelligence Agent warns that recent
complaints mention smell, damaged packaging, refunds, and price mismatch on the
same batch and promotion. The Store Operations Agent forecasts a checkout queue
risk from 16:30 to 18:30 and recommends moving one aisle colleague to checkout
plus creating restock, rotation, shelf signage, and quarantine tasks.

The orchestrator combines these findings into one recovery plan. It separates
facts from inferences, avoids the unsafe shortcut of blocking all supplier
orders, and waits for a supplier response before final supplier action. When
the supplier confirms a replacement batch with a later lead time and a credit
note, North Star updates the plan: quarantine the suspicious units, transfer
safe warehouse stock, request replacement stock, mark down near-expiry safe
units, fix the shelf price, and open an extra cashier lane.

The manager approves consequential actions in the command center. MuleSoft mocks
then execute the approved supplier case, transfer, markdown, store tasks, Slack
alert, WhatsApp-style internal alert, and outcome callback. The final view shows
stockout avoided, waste reduced, complaint risk contained, queue readiness
improved, staff tasks acknowledged, and supplier SLA state preserved in the
audit trail.

## Five-Minute Extended Demo

The extended version starts by showing that North Star is product-category
neutral. The selected live story uses fresh-food patties, while the fixture set
also includes frozen desserts, dairy, beverages, household goods, and consumer
electronics. The same context model can represent product, batch, store,
supplier, promotion, shelf area, roster, evidence, approval, action, and
outcome for each category.

The presenter launches the retail risk event and pauses on the risk pulse. The
stockout, expiry, complaint, supplier, queue, price, promotion, and staff
readiness cards make the mixed incident visible without requiring the judge to
read raw logs. The evidence timeline cites POS demand, stock position, expiry
records, complaint examples, supplier lead time, shelf price audit, promotion
calendar, and roster baseline.

Next, the presenter asks Agentforce for the recommendation. The specialist
agents disagree in useful ways: inventory sees low cover, customer risk sees a
possible bad batch, and operations sees checkout pressure. The orchestrator
explains which statements are source facts, which are inferences, and which
assumptions still need supplier confirmation.

The supplier response arrives and changes the recommendation. Instead of
stopping all supplier orders, North Star narrows the action to the affected
batch, requests a replacement batch, preserves the credit-note evidence, and
keeps safe transfer stock available for the promotion. The manager approves the
protected actions, rejects or defers any unsafe customer-facing message, and
executes only the approved internal workflow.

Finally, the command center shows channel results and outcomes. Slack and
WhatsApp-style alerts are clearly marked as mock delivery unless credentials are
configured. The audit trail keeps correlation IDs, approval IDs, action IDs, and
evidence IDs so the team can explain exactly what was executed and why.

## Backup Recorded-Demo Path

If live Salesforce, Agentforce, Slack, WhatsApp, or local tunnel setup fails,
use the deterministic mock path:

1. Run `npm run demo:reset`.
2. Run `npm run demo:seed`.
3. Run `npm run demo:run`.
4. Open the command center in mock mode with the seeded North Star fixture.
5. Play the recorded screen capture showing the same trigger, conflict,
   supplier response, approval, action execution, channel results, and outcome
   panels.

The presenter must state that Slack and WhatsApp-style delivery are mock channel
results unless real credentials are configured for that rehearsal.

## Final Non-Goals

- North Star is not a generic business platform for this hackathon.
- The first story may use burger patties, but the product model is not
  burger-only.
- POS, supplier, Slack, and WhatsApp integrations are mocks unless explicitly
  configured and demonstrated live.
- Agentforce does not execute protected external actions without manager
  approval.
- Deterministic rules are described as a rules-based baseline, not as trained
  demand forecasting.
