# Governed Experimentation

## Where AutoResearch Fits

Karpathy's AutoResearch demonstrates a bounded loop:

1. modify a constrained artifact;
2. run a fixed-budget experiment;
3. measure one objective result;
4. keep an improvement or discard it;
5. preserve the experiment log;
6. repeat.

We should adopt the experiment discipline, not embed that training repository
into the production product.

## Suitable Experiments

- prompt and instruction versions;
- retrieval chunking, filters, ranking, and context size;
- logical model profile routing;
- provider and model comparisons;
- classifier and escalation thresholds;
- attribution parameters such as time-decay half-life;
- summarization compression;
- local fine-tuning recipes when an organization operates its own model;
- deterministic pipeline latency or cost improvements.

North Star hospital suitable experiments:

- complaint-cluster threshold compared with service recovery outcome;
- capacity-pressure threshold compared with wait-time reduction;
- pharmacy stock-risk threshold compared with stockout avoidance;
- partner-response classification accuracy;
- billing/insurance escalation threshold compared with resolution time;
- staff-alert wording and acknowledgement rate;
- recommendation ordering when complaint, capacity, partner, billing, and queue
  risks conflict.

## Unsafe Experiments

The loop must not autonomously:

- alter production SOPs or approval requirements;
- execute production or external actions;
- train on unrestricted patient, staff, complaint, billing, or partner records;
- change permissions, consent, retention, safety, privacy, or clinical rules;
- promote its own candidates;
- use live patients, visitors, or staff as an unapproved test population;
- optimize only engagement when the relevant outcome includes harm, fairness,
  privacy, or service quality.

For North Star, the loop must not autonomously change clinical decision rules,
approval rules, privacy policy, billing policy, staff allocation policy, or
patient-facing messages. It can propose candidates for review.

## Experiment Contract

Every experiment records:

- hypothesis;
- mutable artifact and allowed change scope;
- immutable harness and evaluation version;
- authorized dataset snapshot;
- baseline;
- primary metric and direction;
- safety and regression metrics;
- compute and time budget;
- candidate lineage;
- result and confidence interval where applicable;
- keep, reject, or inconclusive decision;
- reviewer and promotion decision.

## Evaluation Dimensions

No model is promoted on one quality score alone.

- task correctness;
- citation and provenance accuracy;
- permission and data-leakage tests;
- harmful or disallowed action rate;
- fairness measures appropriate to the use case;
- calibration and abstention;
- latency;
- cost;
- robustness to prompt injection and malformed context;
- downstream business outcome where a reliable measure exists.

North Star evaluation should include wait time reduced, bed released, stockout
avoided, complaint contained, billing issue resolved, partner SLA state,
staff-task completion, alert delivery, approval accuracy, clinical-refusal
accuracy, and whether the selected action created a new operational risk.

## Promotion

The experiment loop produces candidates. A human-controlled release process
promotes an approved candidate into:

- a prompt version;
- retrieval configuration;
- model deployment;
- routing policy;
- threshold;
- metric or attribution configuration.

Promotion creates a versioned record, rollback target, effective date, and
audit trail. Production outcomes then feed future evaluation datasets only after
authorization and review.

## Reference

- Karpathy AutoResearch: https://github.com/karpathy/autoresearch
