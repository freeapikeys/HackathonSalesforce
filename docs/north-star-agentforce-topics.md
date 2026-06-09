# North Star Agentforce Topics

## North Star Orchestrator

Combines inventory, expiry, supplier, complaint, promotion, and staffing
evidence into one recovery plan. It resolves conflicts, separates source facts
from inferences and assumptions, decides which actions require manager approval,
and updates the recommendation after supplier response arrives.

## Inventory and Demand

Calculates days of cover from stock and sales velocity, checks shelf, backroom,
warehouse, and supplier stock, detects stockout, overstock, dead stock, expiry,
near-expiry, waste, seasonal, and promotion demand risk, and recommends
transfer, reorder, rotation, discount, or markdown.

## Store Operations

Predicts peak-hour queue risk, recommends cashier allocation and staff movement,
creates restock, shelf-layout, expiry-removal, rotation, quarantine, markdown,
and signage tasks, and prioritizes work by urgency, customer impact, risk, and
approval state.

## Customer and Risk Intelligence

Detects complaint clusters, classifies quality, smell, damaged packaging, price
mismatch, refund, service, expiry, and availability issues, connects complaints
to product, batch, supplier, store, and promotion, evaluates supplier
reliability and response, escalates high-risk cases, and drafts approved alert
text without sending it directly.

## Contract Evidence

The executable Agentforce fixture in
`intelligence/agentforce/fixtures/agentforce-scenarios-v1.json` uses the
`north-star-retail-recommendation` model profile, separates facts from
inferences, cites inventory, complaint, supplier, and staffing evidence, refuses
restricted or missing evidence, refuses protected external execution, and
includes a changed-recommendation scenario after supplier response.
