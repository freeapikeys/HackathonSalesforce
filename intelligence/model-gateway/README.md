# Provider-Neutral Model Gateway Contract

Version `1.0.0` freezes the boundary between business workflows and model
deployments. Callers select a logical profile and declare purpose, sensitivity,
residency, capability, latency, and cost constraints. They do not select a
provider or model.

The contract defines:

- logical model profiles;
- deployment descriptors;
- deterministic routing policy inputs and decisions;
- provider-neutral generation requests and normalized responses;
- qualified fallback attempts;
- invocation audit records.

Two active mock deployments implement the same `hfs.generate.v1` adapter
interface. The scenario demonstrates primary selection, qualified fallback, and
fail-closed behavior when no deployment satisfies the data policy.

For Logia, the same gateway should route hospital action
recommendations and message drafts through logical profiles. A hospital
action request should include only accessible complaint, capacity, resource,
partner, pharmacy stock, billing, staffing, approval, and outcome evidence. It
should never select a provider or model by name from Agentforce or UI code.
A DeepSeek descriptor is also present so the router can prove that a cloud
provider can be plugged into the same contract without changing Agentforce, UI,
or prompt callers. It remains `UNAVAILABLE` in the demo fixtures until policy
enables it. The reference adapter can call DeepSeek's OpenAI-compatible
chat-completions endpoint only when explicitly enabled and `DEEPSEEK_API_KEY`
is present. Missing credentials or disabled policy fail closed instead of
silently pretending a model answered.

For Logia, the same gateway should route retail recommendations and message
drafts through logical profiles. A retail recommendation request should include
only accessible product, store, supplier, batch, complaint, inventory,
promotion, staff, and outcome evidence.

The private jury-gift path also defines a `nexavenu-revenue-recommendation`
profile. Its fixture separates revenue facts, contact-sourced assumptions,
inferences, champion-nurture recommendations, cited evidence, and human approval
requirements. Neither Agentforce nor UI code should select a provider or model
by name.

Run:

```bash
npm run check:models
```

Generated schema and fixtures are owned by
`scripts/generate_model_gateway_contract.py`. Secrets are intentionally absent;
production credentials belong in Salesforce credentials, MuleSoft secure
properties, or the customer's approved secret manager.

## Reference Runtime

`runtime/hfs_model_gateway/` implements the frozen contract with deterministic
qualification checks, two mock adapters, a guarded DeepSeek-compatible adapter,
normalized output validation, qualified fallback, failed-closed behavior, and
hashes-only invocation audit. It is a local reference and test harness;
production adapters remain behind the same interface and use customer-approved
Salesforce or integration credentials.

Slack and WhatsApp collaborators should read
[`docs/deepseek-slack-handoff.md`](../../docs/deepseek-slack-handoff.md) before
using the adapter for message drafts. The short version: call the model gateway
for advisory draft text, keep `DEEPSEEK_API_KEY` outside Git, and never let the
draft bypass manager approval or protected-action execution.
