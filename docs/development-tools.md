# Development Tools

## Purpose

The team uses several tools to preserve context and coordinate work. They form
the development control plane only.

| Tool                    | Job                                                               | Repository                              |
| ----------------------- | ----------------------------------------------------------------- | --------------------------------------- |
| Beads                   | Work items, dependencies, readiness, and completion history       | https://github.com/steveyegge/beads     |
| Aline / OneContext      | Searchable development conversation history                       | https://github.com/human-re/aline       |
| Overstory               | Optional parallel agents, worktrees, mail, and merge coordination | https://github.com/jayminwest/overstory |
| Atlas/GOTCHA adaptation | Architecture and validation workflow                              | `docs/development-workflow.md`          |

The original Atlas material is inside the private
`freeapikeys/claudes-space` repository. Collaborators do not need access to it
because the relevant project rules are reproduced here without personal memory
or unrelated workspace content.

## Supported Setup

Run:

```bash
./scripts/bootstrap-dev.sh
bd prime
bd ready
```

Recommended versions at project bootstrap:

- Beads: `1.0.4` or a compatible later release.
- Aline: `0.9.2` or a compatible later release.
- Overstory: `0.11.0` if used.

Overstory was archived upstream on May 28, 2026. It is optional and must not
become necessary to build, test, or deploy the product.

## Logia Hackathon Usage

For the hackathon, use the tools to preserve the Logia build path:

- Beads tracks tasks and dependencies when available.
- Contributors should pull latest `main`, inspect the relevant contract, make a
  focused change, run the focused check, and update docs or fixtures when
  behavior changes.
- Generated hospital operations data, partner replies, malformed event cases,
  clinical-refusal cases, expected recommendation notes, and manual validation
  must land in committed files, fixtures, or checklists.
- Tooling should support the multi-agent system: Orchestrator, Evidence and
  Context, Customer Trust, Resource and Capacity, Operations Execution, Partner
  and Vendor, Risk and Approval, Financial Impact, Communication, and Outcome
  Learning.
- Keep Slack, WhatsApp, Agentforce, MuleSoft, Salesforce, and LWC changes
  contract-compatible so they converge cleanly.

## Tool Responsibilities

Beads is authoritative for implementation work and dependencies when installed.

The live Dolt database is local unless a team Dolt remote is configured. The
repository therefore tracks `.beads/issues.jsonl` as a portable exchange and
recovery copy:

```bash
./scripts/sync-beads.sh
```

Fresh clones import that file through `bootstrap-dev.sh`. This is intentionally
separate from the product runtime.

OneContext is evidence for prior development conversations. Important
requirements and decisions must still be committed to the repository.

Overstory may execute Beads work in isolated worktrees. It does not define
product architecture.

Atlas/GOTCHA supplies process principles: separate reasoning from deterministic
execution, define the source of truth, validate connections before assembly,
and stress-test complete behavior.

## Product Boundary

Do not deploy any of the following to a customer environment:

- `.beads` runtime databases not required by repository collaboration;
- `.overstory` logs, mail, worktrees, prompts, or session state;
- OneContext databases or transcripts;
- personal memory files;
- local absolute paths;
- development agent credentials;
- Atlas workspace files.

When the product needs a similar capability, implement it using Salesforce
permissions, Salesforce records, Data 360, Agentforce, MuleSoft, and the
product's own audit and retention policies.
