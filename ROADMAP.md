# Product Roadmap

## North Star

Build a system that can answer, with evidence and permissions:

- Who and what are involved?
- What happened, in what order, and according to which source?
- What was promised, required, or expected?
- Who owns the next action?
- Which SOP, approval, deadline, and dependency apply?
- Who will be affected if nothing changes?
- What action is recommended, and why?
- Was the action approved, completed, and effective?

The product serves relationships across the business, including customers,
employees, managers, suppliers, partners, subsidiaries, regulators, and
shareholders. It uses first-party business data and adapts to each
organization's real systems and operating rules.

## How This Roadmap Works

- Progress is organized by implemented capability, resolved problem, and passed
  checkpoint. It is not organized by days.
- Every capability maps to evidence in
  `research/mauritius-relationship-management/`.
- Beads contains the active tasks and dependencies.
- A capability is complete only when its acceptance checkpoint passes.
- The first straight path is built before broadening the product surface.

## Four-Developer Execution

The first vertical slice is implemented through four stable ownership lanes:

| Lane         | Responsibility                                                              | First claimable bead |
| ------------ | --------------------------------------------------------------------------- | -------------------- |
| Core         | Salesforce Apex context, provenance, approval, action, and outcome services | `hfs-v1-05a`         |
| Integration  | MuleSoft APIs, adapters, write-back, retries, and callbacks                 | `hfs-v1-06a`         |
| Intelligence | Provider-neutral model gateway, routing, audit, fallback, and Agentforce    | `hfs-v1-10a`         |
| Experience   | Lightning command center, seed/reset, end-to-end verification, and demo     | `hfs-v1-07a`         |

Cross-lane work is governed by four Beads checkpoints:

1. contracts frozen;
2. lanes independently verified;
3. connected governed behavior;
4. clean-clone completion.

The detailed ownership, dependency, file-collision, branch, and handoff rules
are in `docs/parallel-development.md`. Run `./scripts/team-status.sh` for the
current claimable work and checkpoint state.

## Research-Backed Problem Map

| ID  | Enterprise problem                                                    | Required system response                                                                                        |
| --- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| P01 | Work and complaints disappear during departmental handoffs            | Shared case history, explicit ownership, deadlines, escalation, and closure evidence                            |
| P02 | Employees lack useful feedback, recognition, growth, and a safe voice | Restricted employee relationship records, feedback loops, growth actions, and confidential escalation           |
| P03 | Skills exist but are poorly matched to work and future demand         | Skills evidence, role requirements, gaps, workload, development, and internal opportunity mapping               |
| P04 | Customers repeatedly chase status and retell context                  | Cross-channel history, expectation records, next-update commitments, and proactive approved communication       |
| P05 | Groups need shared governance without erasing local authority         | Common semantics and controls with business-unit-specific policies, ownership, and processes                    |
| P06 | Decision makers wait too long for assembled evidence                  | Defined metrics, source lineage, current context, exceptions, and decision-ready views                          |
| P07 | Supplier and system failures create hidden cascading effects          | Dependency relationships and impact traversal across people, work, agreements, and services                     |
| P08 | SOPs exist but execution and recommendation closure are weak          | Executable steps, required evidence, exception handling, escalation, and verification                           |
| P09 | Sensitive concerns are unsafe in ordinary management chains           | Purpose-based access, confidential cases, independent routing, and non-retaliation audit                        |
| P10 | Automation removes friction but can make service less human           | Human-controlled recommendations, language/channel preferences, and complete context for the responsible person |
| P11 | Transformation pilots stall or fail to reach operating teams          | Early user validation, visible rules, local process ownership, and measurable adoption                          |
| P12 | Privacy and security failures destroy relationship trust              | Consent, purpose, minimization, retention, segregation of duties, and incident history                          |
| P13 | Data quality and duplicate reporting undermine confidence             | Source ownership, validation, identity confidence, provenance, and correction workflows                         |
| P14 | Organizations measure activity instead of outcomes                    | Versioned metric definitions, attribution models, outcomes, and effectiveness evaluation                        |
| P15 | Organizational memory is trapped in people, documents, and chat       | Permission-aware episodic, semantic, procedural, and outcome memory with source evidence                        |

## Capability Sequence

### C00. Project Control and Recovery

**Problems prevented:** context loss, duplicate work, conflicting agent changes,
and undocumented decisions.

Features:

- Repository onboarding for humans and agents.
- Dependency-aware Beads work graph.
- Architecture decision records.
- Research claim and source register.
- Development-tool and product-runtime separation.
- Clean-session recovery instructions.

Checkpoint:

- [x] A new collaborator can clone the repository, understand the product,
      inspect the research, run `bd prime`, and identify unblocked work without
      reading prior chat.

### C01. Source Intake and Event Contracts

**Problems resolved:** P01, P04, P06, P13.

Features:

- MuleSoft System API boundary for each source.
- Versioned event envelope and schema registry.
- Streaming and bulk ingestion paths.
- Idempotency, deduplication, retries, dead-letter handling, and replay.
- Source-record preservation and content hashes.
- Synthetic CRM, HR, finance, service, communication, and supplier feeds.

Checkpoint:

- [ ] Valid, duplicate, malformed, late, missing, and out-of-order events
      produce deterministic and observable results.

### C02. Shared Semantics and Provenance

**Problems resolved:** P05, P06, P13, P15.

Features:

- Versioned OWL vocabulary for business entities, relationships, events,
  agreements, work, evidence, actions, and outcomes.
- SKOS concept schemes for organization-specific terminology.
- SHACL validation for graph shape and required provenance.
- W3C PROV-compatible source, activity, and agent metadata.
- Mapping records between source schemas, Data 360 objects, Salesforce
  objects, and semantic concepts.
- Valid-time and recorded-time support.

Checkpoint:

- [ ] Example records validate, preserve original terminology, and answer both
      "what is true now?" and "what was known at that time?"

### C03. Identity, Relationships, and History

**Problems resolved:** P04, P05, P07, P13, P15.

Features:

- Deterministic and probabilistic identity matching.
- Visible match confidence and contributing identifiers.
- Human merge, split, and correction workflows.
- Typed, directed, time-bounded relationships.
- Event participants and roles.
- Relationship and event traversal with source evidence.
- No silent profile merging.

Checkpoint:

- [ ] A user can inspect one entity across source systems, understand every
      match, correct ambiguity, and traverse its complete relationship history.

### C04. Cross-Functional Work and SOP Execution

**Problems resolved:** P01, P04, P07, P08, P11.

Features:

- Work items for requests, complaints, incidents, grievances, opportunities,
  approvals, and remediation.
- Explicit owner, contributors, affected parties, blockers, and dependencies.
- Versioned SOP definitions and executable steps.
- Deadline rules, service levels, required evidence, and escalations.
- Handoffs that transfer ownership without losing context.
- Closure confirmation from the affected relationship.

Checkpoint:

- [ ] A domain-neutral case crosses teams, a supplier, an agreement, an SOP,
      and an approval without losing ownership, evidence, or status.

### C05. Metrics and Attribution

**Problems resolved:** P06, P11, P14.

Features:

- Metric definitions with formula, inputs, unit, grain, owner, window, and
  version.
- First-touch, last-touch, linear, position-based, and normalized time-decay
  attribution.
- Attribution to any defined outcome, not only revenue.
- Long-window and repeated-outcome tracking.
- Cohort and path analysis.
- Data quality and confidence indicators.

Checkpoint:

- [ ] Independent recalculation from source events reproduces every displayed
      metric and attribution result.

### C06. Recommendations and Predictive Signals

**Problems resolved:** P02, P03, P04, P06, P07, P10, P14.

Features:

- Transparent rule-based baselines.
- Einstein Studio predictive models where they outperform baselines.
- Provider-neutral model profiles and deterministic routing policies.
- Salesforce-managed, BYOLLM, LLM Open Connector, private-cloud, and secured
  on-prem deployment options.
- Per-agent and per-subagent model selection.
- Capability, sensitivity, residency, quality, latency, cost, and availability
  constraints.
- Qualified fallback without weakening data policy.
- Feature snapshots, model versions, confidence, top factors, and expiry.
- Recommendations linked to affected relationships, evidence, SOPs, and
  expected outcomes.
- Competing hypotheses and falsification questions for uncertain cases.
- Agentforce explanations that distinguish facts from inference.

Checkpoint:

- [ ] Every recommendation can be explained from accessible source evidence and
      can be rejected without changing source facts. Switching a qualified model
      deployment does not require changes to the business workflow.

### C07. Human Approval, Actions, and Outreach

**Problems resolved:** P01, P04, P08, P09, P10, P12.

Features:

- Policy-based approval requirements.
- Approve, reject, modify, defer, expire, execute, fail, and reverse states.
- Agentforce actions backed by Flow, Apex, or MuleSoft APIs.
- Consent, purpose, channel, language, and frequency enforcement.
- Approved message templates with grounded personalization.
- Complete action log and write-back correlation.

Checkpoint:

- [ ] No protected external action occurs without the required identity,
      permission, policy, and approval checks.

### C08. User Surfaces

**Problems resolved:** P01, P02, P04, P06, P10, P11.

Features:

- Company command center.
- Operator work queue.
- Relationship and dependency explorer.
- Chronological evidence view.
- Recommendation and approval panel.
- Manager, data steward, compliance, and executive views.
- Slack alerts, collaboration, approvals, and Agentforce access.
- Tableau analytical views using the same metric definitions.

Checkpoint:

- [ ] Different roles see consistent underlying facts while permissions and
      purpose restrictions change what each role can access or do.

### C09. Workforce Relationships

**Problems resolved:** P02, P03, P09, P11, P15.

Features:

- Skills and evidence of proficiency.
- Role and work capability requirements.
- Feedback commitments and follow-up actions.
- Development goals, training, mentorship, and internal opportunities.
- Workload, availability, and support context.
- Restricted grievance and sensitive-case handling.
- Aggregate fairness and progression measures without exposing protected cases.

Checkpoint:

- [ ] The system can propose a development or staffing action with evidence
      while preventing unauthorized access to sensitive employee information.

### C10. Dependency and Operational Impact

**Problems resolved:** P05, P06, P07, P08.

Features:

- Supplier, system, asset, service, contract, and organizational dependencies.
- Current and potential impact traversal.
- Affected customer, employee, obligation, and work-item identification.
- Incident coordination and remediation ownership.
- Scenario comparison with explicit assumptions.

Checkpoint:

- [ ] A failed dependency identifies affected relationships and commitments,
      assigns work, and tracks remediation to verified closure.

### C11. Product Memory and Outcome Learning

**Problems resolved:** P11, P14, P15.

Features:

- Episodic memory: interactions, cases, decisions, and outcomes.
- Semantic memory: approved facts, concepts, relationships, and definitions.
- Procedural memory: versioned SOPs, policies, and action constraints.
- Outcome memory: what was tried, under which conditions, and what happened.
- Retrieval constrained by tenant, user, purpose, sensitivity, and retention.
- Candidate memories and rules require validation before promotion.
- Outcome evaluation updates recommendation performance without rewriting
  historical evidence.
- Contradictions and superseded beliefs remain traceable.
- Versioned evaluation datasets, harnesses, experiments, candidates, and
  promotion decisions.
- Bounded AutoResearch-style loops for prompts, retrieval, routing, thresholds,
  attribution parameters, and approved model-training recipes.
- Multiple promotion gates covering quality, provenance, safety, fairness,
  latency, cost, and robustness.

Checkpoint:

- [ ] A later recommendation can use a relevant prior outcome, cite it, respect
      current permissions, and show why it applies. Experiment candidates cannot
      promote themselves or execute production actions.

### C12. Security, Governance, and Enterprise Readiness

**Problems resolved:** P05, P09, P12, P13.

Features:

- Tenant isolation and Salesforce sharing enforcement.
- Record, field, relationship, evidence, and action authorization.
- Purpose and consent checks.
- Data minimization, retention, legal hold, and deletion workflows.
- Segregation of duties and dual approval.
- Prompt injection and untrusted-content handling.
- Agent and model audit records.
- Model invocation, evaluation, fallback, and promotion audit records.
- Observability, reconciliation, recovery, and operational runbooks.
- Replaceable synthetic connectors through stable MuleSoft contracts.

Checkpoint:

- [ ] Security, privacy, failure recovery, and real-source replacement tests
      pass without weakening audit history.

## First Straight Path

This is the first complete behavior to implement before expanding sideways:

1. Load a synthetic source event.
2. Validate and preserve the source record.
3. Map its entities, relationships, participants, and agreement.
4. Create or update a cross-functional work item.
5. Determine the applicable SOP and next required step.
6. Generate an evidence-backed recommendation.
7. Present the history, owner, dependencies, evidence, and recommendation.
8. Require a human approval.
9. Execute a mocked MuleSoft write-back.
10. Ingest the resulting outcome event.
11. Update the work item, action log, and user view.
12. Evaluate whether the action achieved the defined outcome.

Completion gate:

- [ ] The whole path runs from a clean clone with automated tests and no manual
      database edits.

## Definition of Done

A feature is not done because a screen renders or an agent produces text. It is
done when:

- inputs and outputs are versioned;
- permissions are enforced;
- source evidence and provenance are visible;
- failures and retries are handled;
- metrics and confidence are defined;
- actions are auditable;
- tests cover the intended behavior and material failure paths;
- documentation and Beads status are updated;
- the result advances a roadmap checkpoint.

## Explicit Non-Goals

- Replacing source systems as their authoritative store.
- Hiding uncertainty behind one unexplained score.
- Letting agents make unrestricted enterprise changes.
- Forcing every subsidiary or department into one identical process.
- Importing developer orchestration tools into the product runtime.
