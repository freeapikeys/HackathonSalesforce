# Model Gateway Contract

## Boundary

Business workflows call a logical capability:

```text
generate(profile, messages, context, responseSchema, invocationPolicy)
```

The routing layer selects a qualified deployment after evaluating tenant,
purpose, data classification, residency, language, capabilities, context size,
quality qualification, latency, cost, status, and availability.

Provider and model identifiers are deployment configuration. They do not appear
in recommendation requests, prompts, Agentforce workflow logic, or UI state.

North Star callers should request logical capabilities such as
`hospital_action_reasoning`, `resource_capacity_reasoning`,
`clinical_boundary_refusal`, `language_detection`, `voice_transcription`,
`customer_reply_drafting`, `judge_sector_use_case_mapping`, or the existing
`recommendation_reasoning` profile. They must not request a provider, a model
name, or a scenario-specific profile.

For the hackathon WhatsApp lane, Hassan may route these logical capabilities to
his pretrained multilingual/voice models or DeepSeek through configuration. The
gateway contract stays the same: provider output is advisory, audited, and
policy-bound. It must not approve protected actions, execute external actions,
make clinical decisions, decide refunds, or bypass evidence retention.
North Star callers should request logical profiles such as
`north-star-retail-recommendation`. Jury-gift callers can request similarly
logical profiles such as `nexavenu-revenue-recommendation`. They must not
request a provider, a model name, or a product-specific profile such as a
burger-only model.

## Deterministic Routing

Version `1.0.0` evaluates candidates in the policy's explicit priority order.
Every candidate receives named pass or fail checks. Fallback is permitted only
when the next candidate satisfies the same profile and request constraints.
When none qualify, the decision is `NO_QUALIFIED_DEPLOYMENT`; data policy is
never weakened to obtain a response.

## Invocation Audit

Every invocation records:

- tenant, user, purpose, agent, and correlation identifiers;
- profile, policy, deployment, prompt, retrieval, and adapter versions;
- input and normalized output hashes;
- accessible evidence identifiers;
- every attempted deployment and failure classification;
- fallback status;
- token, latency, and cost measures;
- safety and output-schema validation;
- retention mode and completion status.

Sensitive prompt or response content is not required in the audit record.

North Star invocation audit should also record stable keys or hashes for the
department, location, resource, partner, complaint cluster, capacity record,
billing case, recommendation type, and action type when present in accessible
Normalized recommendation outputs separate facts, assumptions, inferences,
recommendation text, confidence, cited evidence, and human-approval
requirements. This is required for private diagnostic signal: a contact-sourced
assumption can inform a recommendation without being promoted into source truth.

North Star invocation audit should also record the selected product external key,
product category, store key, supplier key, source evidence identifiers,
recommendation type, and action type when these are present in accessible
context. Record identifiers should be stable business keys or hashes where
policy requires minimization.

The audit must preserve clinical-boundary refusals when a request asks for
diagnosis, treatment, dosage, triage, or clinical priority decisions.

## Compatibility

Additive optional fields are compatible within `1.0.0`. Renaming a field,
changing required routing input, weakening a qualification check, changing the
adapter interface, or changing audit semantics requires a new contract version
and affected-lane review.

Verify compatibility with:

```bash
npm run check:models
```
