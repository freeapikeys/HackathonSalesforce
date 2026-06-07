# 0004: Keep AutoResearch-Style Loops Outside Production

Status: Accepted

## Decision

Use bounded AutoResearch-style experimentation to improve prompts, retrieval,
model routing, thresholds, attribution parameters, and approved model training.

Experiments run on versioned authorized datasets in an isolated evaluation
environment. They create candidates but cannot promote themselves or execute
production actions.

## Reason

The keep-or-discard loop is valuable when an objective metric and immutable
evaluation harness exist. Enterprise recommendations also require privacy,
safety, fairness, provenance, multiple metrics, and human release control.

## Consequences

- Evaluation data, harnesses, experiments, candidates, and promotion decisions
  become first-class records.
- Production outcomes may improve later evaluations but cannot silently change
  policies or models.
- The live Agentforce path remains deterministic around permissions, approval,
  and action execution.
- North Star outcome learning can propose improved stockout, expiry, complaint,
  supplier, and staff-alert thresholds, but it cannot silently change supplier
  blocking, food-safety, markdown, or staff-allocation policy.
