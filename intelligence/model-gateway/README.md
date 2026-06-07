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

Two mock deployments implement the same `hfs.generate.v1` adapter interface.
The scenario demonstrates primary selection, qualified fallback, and
fail-closed behavior when no deployment satisfies the data policy.

For North Star, the same gateway should route retail recommendations and message
drafts through logical profiles. A retail recommendation request should include
only accessible product, store, supplier, batch, complaint, inventory,
promotion, staff, and outcome evidence. It should never select a provider or
model by name from Agentforce or UI code.

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
qualification checks, two mock adapters, normalized output validation,
qualified fallback, failed-closed behavior, and hashes-only invocation audit.
It is a local reference and test harness; production adapters remain behind the
same interface and use customer-approved Salesforce or integration
credentials.
