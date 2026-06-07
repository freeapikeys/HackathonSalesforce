# North Star

North Star is a Salesforce and Agentforce supermarket operations MVP for the
hackathon. It helps a store manager spot product risk early, understand the
evidence, approve the right recovery plan, and coordinate store, supplier, and
staff actions.

The demo is focused on retail operations, not a broad all-purpose business
platform. The product watches first-party supermarket signals:

- POS sales and demand velocity;
- shelf, backroom, warehouse, and supplier stock;
- expiry batches and waste risk;
- customer complaints and refund signals;
- supplier response and delivery lead time;
- promotion readiness and price mismatch;
- staffing, queue risk, and store task execution.

The current repo still contains `HFS_` object and service names because the
foundation was built first as a governed evidence/action spine. For the
hackathon, treat that foundation as internal plumbing. The product story is
North Star.

## Start Here

1. Read [ROADMAP.md](ROADMAP.md).
2. Read [docs/north-star-mvp.md](docs/north-star-mvp.md).
3. Read [docs/north-star-implementation-plan.md](docs/north-star-implementation-plan.md).
4. Read [AGENTS.md](AGENTS.md).
5. Run `npm run check` when the local shell can execute the project scripts.

If Beads is installed, run `bd prime`, `bd ready`, and
`./scripts/team-status.sh` before claiming work. If Beads is not installed, use
the checklist in [ROADMAP.md](ROADMAP.md) and the lane split in
[docs/north-star-implementation-plan.md](docs/north-star-implementation-plan.md).

## Current Build Target

The first North Star vertical slice is:

`retail risk event -> product, supplier, store, batch, complaint, promotion, and
staff context -> evidence-backed recommendation -> manager approval -> MuleSoft
mock actions -> Slack and WhatsApp-style alerts -> outcome -> updated command
center`

The first demo may use burger patties because it is easy to understand, but the
implementation must stay product-category neutral. The same flow should work
for dairy, bakery, frozen food, fresh produce, household goods, electronics, or
pharmacy shelves.

## Repository Map

- `ROADMAP.md`: North Star task checklist and completion gates.
- `AGENTS.md`: rules for Codex and human contributors.
- `docs/north-star-mvp.md`: product brief, agent roles, demo story, and non-goals.
- `docs/north-star-implementation-plan.md`: practical build plan for the team.
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

North Star should show five things clearly:

1. messy retail signals becoming one operational picture;
2. Agentforce separating facts from inference;
3. supplier evidence changing the recommendation;
4. manager approval before consequential actions;
5. Salesforce records preserving evidence, actions, and outcomes.

## Non-Goals

- Do not pitch this as a generic all-purpose platform.
- Do not claim live POS, supplier, Slack, WhatsApp, or ERP integrations unless
  they are configured and demonstrated.
- Do not let Agentforce execute protected external actions directly.
- Do not hard-code the product, supplier, or scenario to burgers.
- Do not hide uncertainty behind one unexplained score.
