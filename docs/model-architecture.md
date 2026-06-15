# Model Architecture

## Decision

Business workflows, prompts, actions, and UI code refer to logical model
profiles, not provider model names.

Examples:

- `classification_fast`
- `case_explanation`
- `recommendation_reasoning`
- `message_drafting`
- `embedding_general`
- `sensitive_on_prem`

North Star can reuse these logical profiles and add retail-specific aliases only
when they describe a distinct capability. Candidate profiles:

- `retail_signal_classification`
- `retail_recovery_reasoning`
- `supplier_response_analysis`
- `staff_alert_drafting`
- `manager_briefing`

Do not encode provider names or product names such as burger items into a model
profile. The selected product belongs in context, not routing policy.

Each logical profile resolves to a versioned deployment and policy.

## Core Records

### Model Profile

Defines the business purpose and required capabilities:

- task type;
- input and output schema;
- minimum context length;
- tool or structured-output support;
- permitted data classifications;
- quality, latency, and cost objectives;
- fallback behavior.

### Model Deployment

Defines one callable model:

- provider and model identifier;
- Salesforce configured-model identifier;
- endpoint and hosting class;
- cloud, private-cloud, or on-prem location;
- supported capabilities;
- configuration and prompt compatibility version;
- active dates and operational status.

Secrets stay in Salesforce credentials, MuleSoft secure properties, or the
customer's secret manager. They are never stored in these records.

### Routing Policy

Selects a deployment using:

- tenant and business unit;
- use case and agent or subagent;
- data sensitivity and residency;
- language;
- capability requirements;
- quality and safety qualification;
- cost and latency limits;
- availability and fallback rules.

Policy evaluation is deterministic and auditable.

### Model Invocation

Records:

- logical profile and selected deployment;
- agent, prompt, retrieval, and policy versions;
- user, tenant, and purpose;
- input and output hashes;
- accessible evidence identifiers;
- token, latency, and cost measures;
- safety and validation results;
- outcome and user feedback links.

Sensitive prompt or output content is retained only when policy permits it.

### Evaluation Suite and Score

Defines the authorized dataset, metrics, thresholds, judge configuration,
regression cases, and test results required before a deployment or prompt
version can be promoted.

## Salesforce Connection

Salesforce currently supports:

- Salesforce-managed models;
- external models through BYOLLM;
- custom or in-house models through the LLM Open Connector;
- model access through Prompt Builder and the Models API;
- model selection at the Agentforce agent and subagent level.

The LLM Open Connector service implements Salesforce's `chat/completions`
contract. The required endpoint is standard HTTPS on port 443. A model hosted
inside a customer network therefore needs a secured endpoint reachable from
Salesforce, normally through an API gateway, private-cloud ingress, or
controlled relay with allowlisting and customer-approved authentication.

A fully air-gapped model cannot be invoked directly by Salesforce. That case
requires an architecture in which an on-prem execution service receives an
approved job through a customer-controlled integration boundary and returns a
result. It must not be described as direct Agentforce inference.

## Gateway Pattern

The initial implementation uses Salesforce AI Models as the model-management
entry point and the Einstein Trust Layer where available.

For custom providers, our LLM Open Connector adapter presents one stable
contract and translates provider-specific requests and responses. The adapter
may be fronted by MuleSoft for policy, routing, observability, and production
connectivity, but model-streaming and latency requirements must be tested
before choosing MuleSoft as the inference proxy.

Provider-specific deployment descriptors can include Salesforce-managed,
private, on-prem, or cloud models. For the current demo, DeepSeek is represented
only as a disabled cloud deployment behind the provider-neutral contract. It is
not invoked by the reference runtime and must not be used with live credentials
until the customer-approved budget, policy, secret manager, and monitoring path
are in place.

The application must also keep a narrow internal interface:

```text
generate(profile, messages, context, response_schema, invocation_policy)
embed(profile, inputs, invocation_policy)
```

This interface lets custom Apex, Flow, Agentforce actions, and future non-
Salesforce services request capabilities without encoding a provider.

For North Star, the generation context must distinguish source facts from
inferences and include only the evidence the current user and purpose can see:
product, batch, store, supplier, complaint cluster, inventory position,
promotion window, staff context, and prior outcome evidence.

## Failover

Fallback is allowed only between deployments qualified for the same profile and
data classification.

The router must not send restricted data to a cheaper or more available model
that lacks the required residency or security approval.

Every fallback is recorded as part of the model invocation.

## References

- Salesforce Agentforce model configuration:
  https://developer.salesforce.com/docs/ai/agentforce/guide/ascript-model.html
- Salesforce models and prompts:
  https://developer.salesforce.com/docs/ai/agentforce/guide/models-get-started.html
- Salesforce LLM Open Connector:
  https://github.com/salesforce/einstein-platform
