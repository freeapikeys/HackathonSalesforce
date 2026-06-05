# HackathonSalesforce

An enterprise relationship and action system built on Salesforce, Agentforce,
Data 360, MuleSoft, Lightning, Slack, and Tableau.

The system connects first-party business data across customers, employees,
suppliers, partners, business units, regulators, and other relationships. It
preserves source evidence, identifies ownership and dependencies, recommends
next actions, requires the configured human approvals, and records outcomes so
future recommendations can improve.

## Start Here

1. Read [ROADMAP.md](ROADMAP.md).
2. Read [AGENTS.md](AGENTS.md).
3. Run `./scripts/bootstrap-dev.sh`.
4. Run `./scripts/bootstrap-runtime.sh`.
5. Run `npm run check`.
6. Run `bd prime`, then `bd ready`.
7. Run `./scripts/team-status.sh`.
8. Claim a lane leaf bead before changing product code.

## Repository Map

- `ROADMAP.md`: product problems, capabilities, dependencies, and completion gates.
- `docs/architecture.md`: current end-to-end architecture and Mermaid diagram.
- `docs/parallel-development.md`: four-developer ownership lanes and checkpoints.
- `docs/`: supporting architecture and engineering decisions.
- `research/`: Mauritius-focused evidence and source register.
- `ontology/`: versioned OWL, SHACL, mappings, and examples.
- `integration/events/`: versioned event schemas and deterministic fixtures.
- `force-app/`: Salesforce DX source.
- `mulesoft/`: API contracts and MuleSoft applications.
- `scripts/`: development and research utilities.

Salesforce org setup and validation commands live in
[docs/salesforce-development.md](docs/salesforce-development.md).
The operational objects, relationships, and permission model are documented in
[docs/salesforce-data-model.md](docs/salesforce-data-model.md).
The executable semantic contract is documented in
[ontology/README.md](ontology/README.md).
The versioned source-event envelope and deterministic fixtures are documented
in [docs/event-contract.md](docs/event-contract.md).

The repository tracks `.beads/issues.jsonl` as the portable team copy of the
work graph. `bootstrap-dev.sh` imports it for a fresh clone. Run
`./scripts/sync-beads.sh` after changing Beads so collaborators receive the
updated graph through Git.

## Development Tools

These tools coordinate the team while building. They are not product runtime
dependencies.

- [Beads](https://github.com/steveyegge/beads): dependency-aware work tracking.
- [Aline / OneContext](https://github.com/human-re/aline): recoverable conversation history.
- [Overstory](https://github.com/jayminwest/overstory): optional parallel-agent orchestration.
- Atlas/GOTCHA principles: architecture, connection validation, deterministic
  tools, explicit context, and stress testing. The original workspace is
  private, so the project-specific adaptation lives in
  [docs/development-workflow.md](docs/development-workflow.md).

See [docs/development-tools.md](docs/development-tools.md) for setup and the
strict boundary between development infrastructure and product infrastructure.

## Current Build Target

The first vertical slice is:

`source event -> mapped entities and relationships -> cross-functional work item
-> evidence-backed recommendation -> human approval -> mocked MuleSoft action
-> outcome event -> updated user interface`

The first case remains industry-neutral so the architecture can later be mapped
to the selected organization without rebuilding the foundation.
