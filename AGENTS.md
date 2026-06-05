# Agent Instructions

## Required Context

Before starting work:

1. Read `ROADMAP.md`.
2. Read the relevant files in `docs/`.
3. Run `bd prime`.
4. Run `bd ready` and claim one bead with `bd update <id> --claim`.
5. Search OneContext when the request refers to prior decisions, existing
   features, debugging history, or previous conversations.

The roadmap defines product direction. Beads defines executable work. A chat
plan is not a replacement for either.

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking

This project uses [Beads](https://github.com/steveyegge/beads).

- Track implementation work, bugs, research gaps, and decisions in Beads.
- Use dependencies to make sequencing explicit.
- Create newly discovered work with a `discovered-from` relationship.
- Close a bead only after its acceptance checks pass.
- Run `bd ready` instead of selecting work from memory.
- Roadmap checkboxes are capability gates, not a second task tracker.
- Run `./scripts/sync-beads.sh` after changing Beads and commit the resulting
  `.beads/issues.jsonl`.

Useful commands:

```bash
bd prime
bd ready
bd show <id>
bd update <id> --claim
bd create "Title" --type task --priority 2
bd dep add <issue> <depends-on>
bd close <id> --reason "Acceptance checks passed"
./scripts/sync-beads.sh
```
<!-- END BEADS INTEGRATION -->

## Development and Product Boundary

Beads, OneContext, Overstory, Atlas/GOTCHA files, local agent memory, and agent
worktrees belong to the development control plane.

They must not become Salesforce metadata, MuleSoft runtime dependencies,
customer data models, product prompts, or deployable packages.

Product capabilities such as memory, dependency tracking, agent handoffs, and
replay must be implemented natively using the product architecture and security
model.

## Engineering Rules

- Use plain business and technical language. Do not invent product terminology.
- Define every metric, score, formula, time window, and confidence value.
- Preserve source records and provenance. Derived facts must identify their
  inputs, rule or model version, and generation time.
- Distinguish facts, claims, inferences, recommendations, decisions, actions,
  and outcomes.
- Do not silently overwrite contradictory evidence. Supersede it explicitly.
- External actions require the configured policy and human approval.
- Agents operate with the current user's permissions and purpose restrictions.
- Prefer Salesforce, Agentforce, Data 360, and MuleSoft platform capabilities
  before introducing another runtime.
- Keep every enterprise implementation adaptable to its real terminology,
  systems, SOPs, permissions, and operating structure.
- Add focused tests for every behavioral change.

## Workflow

Use the project adaptation of Atlas:

1. **Architect:** identify the problem, user, measurable result, and constraints.
2. **Trace:** define data, sources, interfaces, ownership, and failure paths.
3. **Link:** validate credentials, APIs, permissions, and test fixtures.
4. **Assemble:** implement the smallest complete vertical behavior.
5. **Stress-test:** test errors, permissions, retries, evidence, and acceptance.

Push deterministic work into code, schemas, validation, and policies. Use
language models for interpretation and recommendations, not for invariants that
must always execute the same way.

## Documentation

- Update `ROADMAP.md` only when product scope, dependencies, or completion gates
  change.
- Record architecture decisions in `docs/decisions/`.
- Add research claims to the research archive with a source locator.
- Never commit secrets, personal memory, downloaded copyrighted source files,
  agent transcripts, or machine-local paths.
