# 0001: Separate Development Tools from Product Runtime

Status: Accepted

## Decision

Beads, OneContext, Overstory, and the private Atlas workspace are development
tools only. Product capabilities inspired by them must be implemented natively
within the Salesforce, Agentforce, Data 360, and MuleSoft architecture.

## Reason

The development tools have different tenants, permissions, retention,
availability, deployment, and audit assumptions from the production product.
Mixing them would create hidden dependencies, leak development context, and
make customer deployments irreproducible.

## Consequences

- The repository can be built and deployed without OneContext or Overstory.
- Beads may coordinate repository work but is not a customer-facing database.
- Product agent memory and orchestration require explicit product schemas,
  permissions, audit records, and retention rules.
- CI will later check deployable packages for forbidden development artifacts.
- North Star pitch notes, local-model drafts, Codex transcripts, demo rehearsal
  notes, and personal task coordination must not become runtime data unless
  they are intentionally converted into product records, fixtures, or docs.
