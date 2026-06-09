# Agent Instructions

## Required Context

Before starting work:

1. Read `ROADMAP.md`.
2. Read `docs/closed-loop-intelligence-rm.md`.
3. Read `docs/architecture.md`.
4. Read the relevant contract or source files for the surface you are changing.
5. Run `bd prime` and `bd ready` if Beads is installed.
6. If Beads is not installed, use the checklist in `ROADMAP.md` and say which
   checklist item you are advancing.

The roadmap is the visible branch checklist. Beads is useful for dependency
tracking, but it is not required to understand the build.

## Branch Context

This private local branch is the active product direction. It is a closed-loop
enterprise intelligence and relationship-management system that coordinates
evidence, recommendations, human approval, actions, and outcomes across business
relationships.

The supermarket command-center material is a demo vertical, not the product
boundary. Keep shared contracts adaptable to customers, employees, managers,
suppliers, partners, subsidiaries, regulators, shareholders, and other business
relationships.

Do not publish this branch, push commits, open pull requests, or otherwise make
this work visible to collaborators until the owner explicitly approves it.

Do not hard-code the MVP to burgers, supermarkets, or any single relationship
type. Retail can be the first scenario, but object names, fixtures, labels,
actions, and Agentforce instructions should preserve the reusable relationship
intelligence loop.

The retail demo agents are:

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

- Use plain business and technical language.
- Preserve source records and evidence.
- Distinguish facts, claims, inferences, recommendations, decisions, actions,
  and outcomes.
- Define every metric, score, formula, time window, and confidence value.
- Do not silently overwrite contradictory evidence. Supersede it explicitly.
- External actions require the configured policy and manager approval.
- Slack, WhatsApp, email, supplier, customer, employee, partner, reorder,
  markdown, case, and task write-backs are protected external actions unless
  explicitly scoped as local demo mocks.
- Approval means the responsible business role in the MVP, not a Salesforce
  admin and not a developer approving implementation work. A command-center
  button or Salesforce approval/status record is acceptable for the demo.
- Agents operate with the current user's permissions and purpose restrictions.
- Prefer existing Salesforce, Agentforce, MuleSoft, model-gateway, LWC, and
  harness patterns before adding new architecture.
- Add focused tests for every behavioral change.

## Workflow

1. **Scope:** identify the roadmap checkbox or Beads task being advanced.
2. **Trace:** identify the source data, evidence, action, owner, and failure path.
3. **Assemble:** implement the smallest complete behavior.
4. **Verify:** run the focused checks and record what passed.
5. **Update:** keep docs and checklist status honest.

Use language models for interpretation and recommendations, not for invariants
that must always execute deterministically.

## Documentation

- Update `ROADMAP.md` when a checklist item is truly complete.
- Keep `docs/closed-loop-intelligence-rm.md` as the branch product doctrine.
- Treat `docs/north-star-mvp.md` as the retail demo vertical brief.
- Treat `docs/north-star-implementation-plan.md` as the retail demo build plan.
- Record architecture decisions in `docs/decisions/` only when a real contract
  decision changes.
- Never commit secrets, personal memory, downloaded copyrighted source files,
  agent transcripts, or machine-local paths.
