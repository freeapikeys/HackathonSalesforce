# Agent Instructions

## Required Context

Before starting work:

1. Read `ROADMAP.md`.
2. Read `docs/north-star-mvp.md`.
3. Read `docs/north-star-implementation-plan.md`.
4. If you are doing a teammate task, read the matching file in
   `docs/assignments/`.
5. Read the relevant contract or source files for the surface you are changing.
6. Run `bd prime` and `bd ready` if Beads is installed.
7. If Beads is not installed, use the checklist in `ROADMAP.md` and say which
   checklist item you are advancing.

The roadmap is the visible hackathon checklist. Beads is useful for dependency
tracking, but it is not required to understand the build.

## North Star Context

North Star is the active product. It is a supermarket operations command center
that coordinates inventory, expiry, complaints, supplier recovery, staff tasks,
manager approval, and outcome tracking.

Do not drift back into the old broad platform idea. Keep work tied
to the retail demo unless the user explicitly asks for longer-term architecture.

Do not hard-code the MVP to burgers. Burger patties can be the first scenario,
but object names, fixtures, labels, actions, and Agentforce instructions must
support any selected supermarket product category.

The North Star agents are:

- North Star Orchestrator Topic;
- Inventory and Waste Agent;
- Supplier and Product Trust Agent;
- Store Execution and Outreach Agent.

The Supplier and Product Trust Agent must not blindly stop all orders because
complaints exist. It should inspect batch, product, store, time, supplier
response, and available alternatives before proposing quarantine, replacement,
reorder, transfer, promotion adjustment, or escalation.

## Issue Tracking

This project can use [Beads](https://github.com/steveyegge/beads) when
available.

Useful commands:

```bash
bd prime
bd ready
./scripts/team-status.sh
bd show <id>
bd update <id> --claim
bd create "Title" --type task --priority 2
bd dep add <issue> <depends-on>
bd close <id> --reason "Acceptance checks passed"
./scripts/sync-beads.sh
```

Close a bead only after its acceptance checks pass. If you change Beads, run
`./scripts/sync-beads.sh` and commit the updated `.beads/issues.jsonl`.

## Engineering Rules

- Use plain retail operations language.
- Preserve source records and evidence.
- Distinguish facts, claims, inferences, recommendations, decisions, actions,
  and outcomes.
- Define every metric, score, formula, time window, and confidence value.
- Do not silently overwrite contradictory evidence. Supersede it explicitly.
- External actions require the configured policy and manager approval.
- Slack, WhatsApp, reorder, supplier, markdown, and store-task write-backs are
  protected external actions unless explicitly scoped as local demo mocks.
- Approval means a business manager role in the MVP, not a Salesforce admin and
  not a developer approving implementation work. A command-center button or
  Salesforce approval/status record is acceptable for the hackathon demo.
- Agents operate with the current user's permissions and purpose restrictions.
- Prefer existing Salesforce, Agentforce, MuleSoft, model-gateway, LWC, and
  harness patterns before adding new architecture.
- Add focused tests for every behavioral change.

## Workflow

1. **Scope:** identify the roadmap checkbox being advanced.
2. **Trace:** identify the source data, evidence, action, owner, and failure path.
3. **Assemble:** implement the smallest complete behavior.
4. **Verify:** run the focused checks and record what passed.
5. **Update:** keep docs and checklist status honest.

Use language models for interpretation and recommendations, not for invariants
that must always execute deterministically.

## Documentation

- Update `ROADMAP.md` when a checklist item is truly complete.
- Keep `docs/north-star-mvp.md` as the product brief.
- Keep `docs/north-star-implementation-plan.md` as the practical build plan.
- Record architecture decisions in `docs/decisions/` only when a real contract
  decision changes.
- Never commit secrets, personal memory, downloaded copyrighted source files,
  agent transcripts, or machine-local paths.
