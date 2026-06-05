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

## Issue Tracking

This project uses [Beads](https://github.com/steveyegge/beads).

- Track implementation work, bugs, research gaps, and decisions in Beads.
- Use dependencies to make sequencing explicit.
- Create newly discovered work with a `discovered-from` relationship.
- Close a bead only after its acceptance checks pass.
- Run `bd ready` instead of selecting work from memory.
- Roadmap checkboxes are capability gates, not a second task tracker.

Useful commands:

```bash
bd prime
bd ready
bd show <id>
bd update <id> --claim
bd create "Title" --type task --priority 2
bd dep add <issue> <depends-on>
bd close <id> --reason "Acceptance checks passed"
```

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

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs via Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push`/`bd dolt pull` for remote sync
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-- END BEADS INTEGRATION -->
