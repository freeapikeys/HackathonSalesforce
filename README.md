# North Star

North Star is a Salesforce, Agentforce, and MuleSoft operations command center
for messy cross-functional business issues. It is not a generic chatbot. It
turns one operational signal into source-backed evidence, specialist-agent
reasoning, manager-approved action, protected channel execution, and outcome
tracking.

The hackathon demo profile is a large private hospital. The architecture is
global: the same primitives can map to hotel rooms, airport gates, bank cases,
supermarket batches, cruise cabins, and hospital beds.

North Star handles non-clinical operations only. It must not diagnose, treat,
recommend dosage, triage patients, or decide clinical priority.

## Start Here

1. Read [ROADMAP.md](ROADMAP.md).
2. Read [docs/north-star-mvp.md](docs/north-star-mvp.md).
3. Read [docs/north-star-implementation-plan.md](docs/north-star-implementation-plan.md).
4. Read [AGENTS.md](AGENTS.md).
5. Run `npm run check` when the local shell can execute the project scripts.

If Beads is installed, run `bd prime`, `bd ready`, and
`./scripts/team-status.sh` before claiming work. If Beads is not installed, use
the checklist in [ROADMAP.md](ROADMAP.md).

## Current Build Target

The first North Star hospital proof is:

`customer/staff/system signal -> global primitives and evidence -> Agentforce
action recommendation -> clinical-refusal guardrail -> manager approval ->
Salesforce task action records -> MuleSoft Slack/WhatsApp actions -> Salesforce
outcomes -> updated command center`

The demo starts from rising patient complaints, blocked discharge rooms,
outpatient queue pressure, low pharmacy stock, delayed lab response, and stuck
billing or insurance approvals. North Star expands that one surge into patient
trust, capacity, partner/vendor, financial, communication, risk, and outcome
work.

## Repository Map

- `ROADMAP.md`: hackathon checklist and completion gates.
- `AGENTS.md`: rules for Codex and human contributors.
- `docs/north-star-master-reference.md`: one-stop team reference for agents,
  IDs, channels, commands, setup, and demo gates.
- `docs/north-star-mvp.md`: product brief, agent roles, demo story, and non-goals.
- `docs/north-star-implementation-plan.md`: practical build plan for the team.
- `docs/north-star-demo-narrative.md`: judge demo script and backup path.
- `docs/north-star-demo-data.md`: synthetic private-hospital demo data summary.
- `docs/architecture.md`: system architecture and runtime flow.
- `docs/demo-harness.md`: seed, reset, verification, and connected demo behavior.
- `docs/clean-clone-runbook.md`: clean-clone verification path.
- `docs/event-contract.md`: versioned event intake contract.
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

1. messy hospital operations signals becoming one coordinated action plan;
2. a credible intake story: WhatsApp/customer complaint, Salesforce fallback,
   or system event becoming evidence;
3. Agentforce separating source-backed facts from inference;
4. global primitives that judges can map to their own sectors;
5. manager approval before protected Slack, WhatsApp-style, vendor, billing,
   pharmacy, room/bed, staff-task, or patient-message actions;
6. Salesforce records preserving evidence, approvals, actions, outcomes,
   evaluations, and clinical refusal.

## Non-Goals

- Do not pitch this as zero-configuration magic. Say "global primitives plus a
  business profile."
- Do not claim diagnosis, treatment, dosage, triage, or clinical priority
  decisions.
- Do not claim real hospital, patient, insurer, Slack, WhatsApp, vendor,
  pharmacy, billing, or task integrations unless configured and demonstrated.
- Do not let Agentforce execute protected external actions directly.
- Do not commit real patient, staff, vendor, insurer, phone, email, credential,
  or medical-record data.
- Do not hide uncertainty behind one unexplained score.
