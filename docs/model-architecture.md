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

Logia can reuse these logical profiles and add hospital/global aliases only
when they describe a distinct capability. Candidate profiles:

- `hospital_signal_classification`
- `hospital_action_reasoning`
- `resource_capacity_reasoning`
- `partner_response_analysis`
- `financial_impact_review`
- `clinical_boundary_refusal`
- `staff_alert_drafting`
- `manager_briefing`
- `language_detection`
- `voice_transcription`
- `customer_reply_drafting`
- `judge_sector_use_case_mapping`

Do not encode provider names, patient aliases, hospital names, or one-off demo
scenario names into a model profile. The selected business profile belongs in
context, not routing policy.

Hassan may use pretrained multilingual or voice models and DeepSeek for the
WhatsApp/chat lane during the hackathon. Treat those as deployments behind the
logical profiles above, not as core architecture names. Model output may draft,
classify, translate, transcribe, summarize, or ask for missing evidence. It must
not approve actions, execute MuleSoft actions, decide refunds, make clinical
decisions, or weaken evidence and approval rules.

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

## Gateway Pattern

The initial implementation uses Salesforce AI Models as the model-management
entry point and the Einstein Trust Layer where available.

For custom providers, our LLM Open Connector adapter presents one stable
contract and translates provider-specific requests and responses. The adapter
may be fronted by MuleSoft for policy, routing, observability, and production
connectivity, but model-streaming and latency requirements must be tested before
choosing MuleSoft as the inference proxy.

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

For Logia, the generation context must distinguish source facts from
inferences and include only the evidence the current user and purpose can see:
customer alias, department, location, resource, complaint cluster, capacity
record, partner response, pharmacy stock, billing case, staffing context,
approval state, and prior outcome evidence.

The model may interpret and recommend operational next steps. It must not make
diagnosis, treatment, dosage, triage, or clinical priority decisions.

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
