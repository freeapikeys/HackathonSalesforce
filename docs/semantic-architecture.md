# Semantic, Workflow, and Memory Architecture

## Separate Structures

The product must not force every form of knowledge into one graph.

### Type Graph

OWL and SKOS define shared meaning:

- entity and relationship types;
- event and participant types;
- agreement, obligation, work, evidence, action, and outcome types;
- organization-specific terms and mappings;
- allowed type relationships.

### Assertion Graph

Assertions represent facts or claims:

`subject -> predicate -> object`

Each assertion records:

- source record and source system;
- confidence and validation status;
- sensitivity and purpose restrictions;
- valid-from and valid-to;
- recorded-at and superseded-at;
- authoring person, system, rule, or model.

Contradictory assertions can coexist. Resolution creates a new reviewed
assertion and supersession links; it does not erase history.

### Event History

Events are immutable occurrences. They record actors, participants, roles,
timestamps, source identifiers, correlation identifiers, and evidence.

### Workflow DAG

An SOP version defines steps and dependencies. A work item instantiates that
definition with owners, deadlines, evidence requirements, approvals, retries,
exceptions, and escalation.

The workflow definition should be acyclic. The organization and its
relationships are not.

### Decision Trace

A decision trace links:

`evidence -> observation -> hypothesis -> recommendation -> approval -> action
-> outcome -> evaluation -> updated belief`

The trace may loop as new outcomes arrive. Every run is versioned and retains
the information available at the time.

## Initial Core Types

- `Entity`
- `Person`
- `Organization`
- `OrganizationalUnit`
- `Team`
- `Role`
- `Supplier`
- `Partner`
- `Regulator`
- `Product`
- `Service`
- `Asset`
- `System`
- `Relationship`
- `Event`
- `EventParticipant`
- `Agreement`
- `Obligation`
- `Consent`
- `WorkItem`
- `SOPDefinition`
- `SOPStep`
- `Evidence`
- `Claim`
- `MetricDefinition`
- `MetricValue`
- `AttributionResult`
- `Recommendation`
- `Approval`
- `Action`
- `Outcome`
- `Evaluation`
- `AgentDefinition`
- `AgentRun`
- `AgentStep`
- `ToolCall`
- `Handoff`
- `MemoryItem`
- `ModelProfile`
- `ModelDeployment`
- `ModelRoutingPolicy`
- `ModelInvocation`
- `EvaluationSuite`
- `ExperimentRun`
- `ExperimentCandidate`
- `PromotionDecision`

## North Star Semantic Extension

North Star should extend the core types through controlled terms before adding a
separate graph store. Candidate retail terms:

- `Store`
- `ProductCategory`
- `ProductBatch`
- `ShelfLocation`
- `InventoryPosition`
- `PromotionWindow`
- `ComplaintCluster`
- `SupplierResponse`
- `MarkdownPlan`
- `WarehouseTransfer`
- `StaffTask`
- `ChannelAlert`
- `RetailOutcome`

These terms should preserve original source terminology. For example, one
retailer may say "lot", another "batch", and another "SKU batch"; mappings
should keep those labels while relating them to the shared concept.

## Standards

- OWL 2 for vocabulary and class relationships.
- SKOS for controlled terms and organization-specific labels.
- SHACL for graph validation and required fields.
- W3C PROV-O for entities, activities, agents, derivation, and generation.
- JSON-LD for portable semantic payloads where appropriate.

## Product Storage

Salesforce and Data 360 remain the operational stores.

- Data 360 stores ingested data, harmonized objects, identity resolution,
  history, calculated insights, and model features.
- Salesforce Core stores operational entities, work, SOP execution,
  recommendations, approvals, actions, and audit-facing records.
- MuleSoft handles source-specific integration and write-back.
- Versioned ontology files define meaning and validation.

The initial executable contract lives in `ontology/`. It includes the core OWL
vocabulary, controlled SKOS concepts, SHACL shapes, a JSON-LD context, and
positive and negative validation fixtures.

A separate graph database is not required for the initial vertical slice.
Introduce one only when measured traversal, inference, or scale requirements
cannot be satisfied by the platform architecture.

## Product Memory

Memory is permission-aware evidence, not an unrestricted transcript dump.

### Episodic Memory

Interactions, cases, decisions, actions, and outcomes.

### Semantic Memory

Reviewed facts, concepts, definitions, and relationships.

### Procedural Memory

SOPs, policies, constraints, and approval requirements.

### Outcome Memory

What was attempted, under which conditions, what happened, and how the result
was measured.

North Star outcome memory should capture which recovery option was chosen,
supplier response status, manager decision, channel delivery, staff completion,
stockout result, waste result, complaint result, and any new risk created by
the action.

### Working Context

The minimum accessible information assembled for one agent run or user task.
Working context expires and is not automatically promoted to long-term memory.

## Learning Loop

The local memory research memory system demonstrates useful patterns:

- source text, claims, rules, concepts, and evidence are separate;
- graph recall narrows relevant context;
- competing hypotheses are compared;
- decision traces preserve reasoning;
- outcomes can strengthen or downrank future rules;
- OWL is an export of structured knowledge, not the only working store.

The production product extends those patterns with:

- tenant and user isolation;
- purpose and consent checks;
- reviewed memory promotion;
- retention and deletion;
- contradiction handling;
- model and rule versioning;
- outcome evaluation;
- access-controlled citations.

The product never changes a policy or high-impact action rule solely because an
agent observed one outcome. It creates a candidate change for review.

See `model-architecture.md` and `governed-experimentation.md` for provider
portability and AutoResearch-style evaluation.
