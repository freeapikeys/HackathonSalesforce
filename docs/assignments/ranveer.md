# Ranveer Assignment: Agentforce Inventory And Waste Reasoning

## Goal

Build the Inventory and Waste reasoning path for North Star. The agent should
turn retail evidence into a grounded recommendation: stockout risk, expiry
risk, waste risk, promotion pressure, and safe next actions. It must cite facts,
separate inferences, and respect supplier/product trust evidence.

## What The Project Already Has

Start from the existing governed spine:

- `docs/north-star-mvp.md` defines the North Star three-agent system.
- `docs/agentforce-action-contract.md` defines Agentforce-facing actions.
- `docs/apex-service-contract.md` defines the Apex service boundary.
- `docs/model-gateway-contract.md` and `docs/model-architecture.md` define
  logical model routing and grounding expectations.
- `docs/salesforce-data-model.md` maps retail concepts to HFS records.
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json` contains
  current Agentforce fixtures.
- `force-app/main/default/classes/` contains Apex service and invocable classes.
- `integration/events/fixtures/` contains source event fixtures.

Do not make a generic Q&A bot. The output must be an evidence-backed retail
operations recommendation.

## Files To Inspect First

- `docs/north-star-mvp.md`
- `docs/north-star-implementation-plan.md`
- `docs/agentforce-action-contract.md`
- `docs/apex-service-contract.md`
- `docs/model-gateway-contract.md`
- `docs/model-architecture.md`
- `docs/salesforce-data-model.md`
- `intelligence/agentforce/README.md`
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json`
- `force-app/main/default/classes/`
- `scripts/generate_agentforce_contract.py`

## Required Reasoning Inputs

The Inventory and Waste Agent should expect these inputs from Salesforce,
fixtures, or Data Cloud style mock data:

- product ID, name, category, storage type, and unit size;
- store ID, store name, and shelf area;
- current shelf stock;
- backroom stock;
- warehouse stock;
- reserved or incoming stock;
- supplier lead time;
- daily sales velocity;
- promotion uplift estimate;
- expiry batch quantities and expiry dates;
- complaint or quality risk summary;
- supplier response status;
- staffing or queue pressure summary;
- evidence IDs and source timestamps.

## Required Reasoning Outputs

The agent should return:

- `riskType`: `STOCKOUT`, `EXPIRY`, `WASTE`, `OVERSTOCK`,
  `PROMOTION_READINESS`, or `MIXED`
- `severity`: `Low`, `Medium`, `High`, or `Critical`
- `facts`: source-backed statements with evidence IDs
- `inferences`: calculated or model-assisted conclusions
- `missingEvidence`: data needed before a stronger decision can be made
- `recommendedActions`: proposed actions, each with approval requirement
- `blockedActions`: actions the agent refuses or defers
- `supplierCaution`: whether supplier/product trust evidence changes the plan
- `confidence`: 0 to 1
- `explanation`: manager-readable summary

## Baseline Calculations

Use deterministic calculations before any model wording:

```text
availableStock = shelfStock + backroomStock + warehouseStock + incomingStock
adjustedDemand = dailySalesVelocity * promotionUpliftMultiplier
daysOfCover = availableStock / adjustedDemand
expiryDaysRemaining = expiryDate - businessDate
wasteRiskUnits = nearExpiryUnits - expectedSalesBeforeExpiry
salesAtRiskUnits = max(0, adjustedDemand * leadTimeDays - availableStock)
```

Suggested thresholds:

- `daysOfCover < 1`: Critical stockout risk
- `daysOfCover < 2`: High stockout risk
- `expiryDaysRemaining <= 1`: Critical expiry risk
- `expiryDaysRemaining <= 3`: High expiry risk for fresh/dairy/bakery
- `wasteRiskUnits > 0`: recommend rotation, markdown, transfer, or removal
- active complaint cluster on same batch: pause blind reorder and ask for
  supplier response or replacement batch

These thresholds can be changed, but the formula and reason must be documented.

## Important Supplier Rule

Do not recommend "order more" blindly when complaints or supplier risk exist.

Correct behavior:

- If the issue is only stock pressure, recommend reorder or transfer.
- If the issue is stock pressure plus batch complaints, recommend quarantine of
  suspect batch, supplier response, replacement batch, or alternate source.
- If supplier response confirms replacement, update the recommendation.
- If supplier response is missing, name the uncertainty and request manager
  approval for consequential actions.

## Implementation Checklist

- [x] Pull latest `main`.
- [x] Read this file and the required docs.
- [x] Inspect existing Agentforce fixtures and generated contract scripts.
- [x] Identify the current recommendation action shape.
- [x] Add or update Inventory/Waste fixture scenarios.
- [x] Add deterministic calculations for days of cover, sales at risk, and
      waste risk where appropriate.
- [x] Ensure every recommendation cites inventory, expiry, promotion, complaint,
      supplier, and staffing evidence when available.
- [x] Ensure facts and inferences are separate.
- [x] Add `missingEvidence` when data is absent.
- [x] Add `blockedActions` for unsafe direct actions or unsupported claims.
- [x] Ensure recommendations feed the approval/action path rather than execute
      actions directly.
- [x] Keep labels product-category neutral.

## Scenario Checklist

- [x] Stockout risk with clean supplier history.
- [x] Stockout risk with active complaint cluster.
- [x] Near-expiry fresh food with markdown recommendation.
- [x] Overstock household item with transfer or promotion adjustment.
- [x] Promotion demand spike with insufficient shelf stock.
- [x] Supplier replacement batch changes the recommendation.
- [x] Missing expiry data causes a cautious recommendation.
- [x] Missing supplier response blocks supplier-wide decision.

## Testing Checklist

- [x] Run `npm run check:agentforce`.
- [x] Run `npm run check:models` if model gateway fixtures change. Not
      applicable: model gateway fixtures did not change.
- [x] Run `npm run check:project` if Apex metadata or classes change. Not
      applicable: Apex metadata and classes did not change.
- [x] Add or update tests for: - evidence citation; - fact versus inference separation; - supplier complaint caution; - missing evidence; - refusal to execute protected actions directly.

## Demo Acceptance

The Inventory and Waste reasoning work is demo-ready when:

- Agentforce can explain why a product is at risk;
- it calculates or cites days of cover and expiry/waste pressure;
- it changes or qualifies the plan when complaint/supplier evidence exists;
- it proposes actions that flow into approval;
- it does not send Slack, WhatsApp, reorder, markdown, or supplier actions
  directly;
- a manager can understand the reasoning in less than one minute.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/ranveer.md, docs/agentforce-action-contract.md,
docs/apex-service-contract.md, and intelligence/agentforce fixtures. Implement
the next smallest Inventory and Waste reasoning task. Preserve evidence
citations, fact/inference separation, supplier caution, and approval gating.
Run npm run check:agentforce and any focused checks for changed files.
```
