# Closed-Loop Intelligence RM

This private local branch is recentered on the original product: a Salesforce,
Agentforce, Data 360, and MuleSoft system that turns first-party business data
into evidence-backed decisions, coordinates people and agents across business
relationships, captures outcomes, and feeds those outcomes back into the next
cycle.

The supermarket command-center work is useful as a demo vertical, but it is not
the product boundary for this branch. Treat retail as one scenario that proves
the broader relationship-management intelligence loop.

Start with [docs/closed-loop-intelligence-rm.md](docs/closed-loop-intelligence-rm.md)
for the branch doctrine and
[docs/decisions/0006-closed-loop-intelligence-rm-branch.md](docs/decisions/0006-closed-loop-intelligence-rm-branch.md)
for the branch decision.

## Start Here

1. Read [ROADMAP.md](ROADMAP.md).
2. Read [docs/closed-loop-intelligence-rm.md](docs/closed-loop-intelligence-rm.md).
3. Read [docs/architecture.md](docs/architecture.md).
4. Read [AGENTS.md](AGENTS.md).
5. Run `npm run check` when the local shell can execute the project scripts.

If Beads is installed, run `bd prime`, `bd ready`, and
`./scripts/team-status.sh` before claiming work. If Beads is not installed, use
the checklist in [ROADMAP.md](ROADMAP.md) and the lane split in
[docs/north-star-implementation-plan.md](docs/north-star-implementation-plan.md).

## Current Build Target

The first branch-level vertical slice is:

`authorized source event -> preserved evidence -> semantic mapping -> facts and
inferences -> recommendation -> human approval -> coordinated task or outreach
-> outcome -> updated relationship intelligence`

Retail fixtures can instantiate this flow with product, supplier, store, staff,
complaint, promotion, and outcome records. Shared contracts should remain
adaptable to customers, employees, suppliers, partners, subsidiaries,
regulators, shareholders, and other business relationships.

## Repository Map

- `ROADMAP.md`: branch roadmap and completion gates.
- `AGENTS.md`: rules for Codex and human contributors.
- `docs/closed-loop-intelligence-rm.md`: branch product doctrine and loop.
- `docs/research/jury-gift-dossiers-2026-06-10.md`: private OSINT-backed
  jury/company gift dossiers.
- `docs/north-star-mvp.md`: retail demo vertical brief.
- `docs/north-star-implementation-plan.md`: retail demo build plan.
- `docs/architecture.md`: system architecture and runtime flow.
- `docs/demo-harness.md`: seed, reset, verification, and demo harness behavior.
- `docs/event-contract.md`: versioned retail event intake contract.
- `docs/mulesoft-api-contract.md`: mock integration and write-back boundary.
- `docs/model-gateway-contract.md`: model routing and audit contract.
- `docs/agentforce-action-contract.md`: governed Agentforce action boundary.
- `docs/ui-state-contract.md`: Lightning command-center state contract.
- `force-app/`: Salesforce DX source.
- `mulesoft/`: API contract and mock runtime.
- `intelligence/`: Agentforce and model-gateway contracts, fixtures, and tests.
- `integration/events/`: event schemas and deterministic fixtures.
- `scripts/`: validation, seed, reset, and harness utilities.

## Demo Promise

The branch demo should show five things clearly:

1. fragmented first-party data becoming one operational picture;
2. Agentforce and models separating facts from inference;
3. new evidence changing the recommendation;
4. human approval before consequential actions;
5. Salesforce records preserving evidence, actions, and outcomes.

## Non-Goals

- Do not reduce this branch to a retail-only product.
- Do not pitch surveillance, scraping, or unauthorized data harvesting.
- Do not claim live POS, supplier, Slack, WhatsApp, or ERP integrations unless
  they are configured and demonstrated.
- Do not let Agentforce execute protected external actions directly.
- Do not hard-code the product, supplier, relationship type, or scenario.
- Do not hide uncertainty behind one unexplained score.
