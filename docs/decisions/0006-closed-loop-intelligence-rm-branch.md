# 0006: Recenter Branch on Closed-Loop Intelligence RM

Status: Accepted

## Decision

Create a private local branch, `codex/closed-loop-intelligence-rm`, from
`main` at commit `51103a4` and recenter branch work on the original
closed-loop intelligence and relationship-management system.

The supermarket command-center material stays useful as a demo vertical and
test scenario, but it is not the product boundary for this branch.

Do not publish this branch, push commits, open pull requests, or otherwise make
the branch visible to collaborators until the owner explicitly approves it.

## Reason

Recent repository work optimized the active product story around a supermarket
retail command center. That is a valid demo scenario, but it narrows the system
away from the intended product: a permissioned enterprise intelligence loop
that integrates proprietary data, forms evidence-backed conclusions, coordinates
humans and agents across relationships, captures outcomes, and repeats.

The broader architecture is the valuable part. Retail should prove it, not
replace it.

## Consequences

- New work on this branch starts from
  `docs/closed-loop-intelligence-rm.md`.
- `docs/logia-*.md` files are treated as retail demo assets unless a later
  decision promotes them again.
- Shared contracts must stay adaptable across customers, employees, suppliers,
  partners, subsidiaries, regulators, shareholders, and other business
  relationships.
- Agentforce and LLM work must remain provider-neutral, hotswappable, and
  governed by permissions, provenance, and approval policy.
- Any future publication of this branch requires an explicit owner decision.
