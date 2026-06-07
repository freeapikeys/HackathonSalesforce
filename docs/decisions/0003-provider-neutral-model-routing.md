# 0003: Use Provider-Neutral Model Profiles

Status: Accepted

## Decision

Business logic selects a logical model profile. A deterministic routing policy
maps that profile to a qualified Salesforce-managed, cloud, private-cloud, or
secured on-prem deployment.

Salesforce AI Models, BYOLLM, the Models API, and the LLM Open Connector are the
preferred Salesforce integration surfaces. Provider-specific APIs remain
behind adapters.

## Reason

Model quality, price, latency, availability, residency, and provider offerings
change quickly. Embedding provider names in agents, prompts, Apex, or SOPs would
make the product expensive to change and difficult to deploy in regulated or
on-prem environments.

## Consequences

- Model profiles, deployments, policies, invocations, and evaluations require
  versioned records.
- Agentforce agents and subagents may use different qualified models.
- Air-gapped models require an asynchronous customer-controlled integration
  boundary rather than direct Salesforce inference.
- Provider fallback never overrides security or residency policy.
- North Star must request retail reasoning through logical profiles and accessible
  evidence. Agentforce, prompts, UI state, and workflow code must not hard-code
  a provider, model, or product-specific model name.
