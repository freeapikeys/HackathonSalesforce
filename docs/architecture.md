# System Architecture

## Product Mental Model

At product level, the system is two coupled loops:

```mermaid
flowchart LR
    SOURCES["First-party business data<br/>and source events"]

    subgraph INTELLIGENCE["Data and Intelligence Engine"]
        INGEST["Ingest and preserve"]
        MEANING["Aggregate, map ontology,<br/>resolve identity and provenance"]
        REASON["Attribute, detect, predict<br/>and generate grounded recommendations"]
    end

    subgraph RELATIONSHIPS["Relationship Action System"]
        REVIEW["Humans and agents review<br/>evidence and proposed action"]
        ACT["Approved outreach, work,<br/>escalation or operational change"]
        OUTCOME["Problem, intervention,<br/>outcome and evaluation"]
    end

    SOURCES --> INGEST --> MEANING --> REASON
    REASON -->|"insights and proposed actions"| REVIEW
    REVIEW --> ACT --> OUTCOME
    OUTCOME -->|"new events, evidence and relationship state"| INGEST
```

Here, data manipulation means governed transformation, aggregation, mapping,
and inference. It does not mean covert behavioral manipulation. Personalization
and predictions remain bounded by source evidence, consent, purpose, access
policy, model policy, and the configured human approval point.

## Current Intended Architecture

```mermaid
flowchart TB
    subgraph Sources["Enterprise Source Systems"]
        CRM["CRM and sales"]
        HR["HR and workforce"]
        FIN["Finance and contracts"]
        SERVICE["Service and communications"]
        OPS["Suppliers, assets, and operations"]
    end

    subgraph Integration["Integration and Action Boundary"]
        SYSAPI["MuleSoft System APIs"]
        PROCAPI["MuleSoft Process APIs"]
        MQ["Queues, retry, replay, and dead letters"]
        EXPAPI["MuleSoft Experience APIs"]
    end

    subgraph Data["Data and Meaning"]
        RAW["Preserved source records and events"]
        D360["Data 360 harmonization, identity, history, features, and metrics"]
        SEM["OWL and SKOS types, SHACL rules, mappings, and provenance"]
    end

    subgraph Operations["Operational System of Work"]
        CORE["Salesforce Core records"]
        WORK["Work items, SOP steps, ownership, deadlines, and evidence"]
        GOV["Permissions, consent, policy, approval, and audit"]
        ACTIONS["Approved actions and outcome records"]
    end

    subgraph Intelligence["Agent and Model Layer"]
        AGENT["Agentforce agents and subagents"]
        CONTEXT["Permission-aware context assembly and memory retrieval"]
        ROUTER["Logical model profiles and routing policy"]
        SF_MODELS["Salesforce AI Models and Einstein Trust Layer"]
        OPEN["LLM Open Connector adapter"]
        PROVIDERS["Cloud providers, private cloud, or secured on-prem models"]
        RECOMMEND["Recommendations, explanations, and message drafts"]
    end

    subgraph Channels["Human Interfaces"]
        LWC["Lightning command center and role views"]
        SLACK["Slack"]
        TABLEAU["Tableau"]
        API["Approved external channels"]
    end

    subgraph Lab["Governed Evaluation Lab, Outside Production"]
        EVALDATA["Versioned authorized evaluation datasets"]
        LOOP["AutoResearch-style bounded experiment loop"]
        CANDIDATE["Candidate prompt, retrieval, routing, model, or threshold"]
        SCORE["Quality, safety, latency, cost, and outcome evaluation"]
        PROMOTE["Human review and controlled promotion"]
    end

    Sources --> SYSAPI
    SYSAPI --> MQ
    MQ --> PROCAPI
    PROCAPI --> RAW
    RAW --> D360
    SEM <--> D360
    D360 --> CORE
    SEM <--> CORE
    CORE --> WORK
    WORK --> CONTEXT
    GOV --> CONTEXT
    CONTEXT --> AGENT
    AGENT --> ROUTER
    ROUTER --> SF_MODELS
    SF_MODELS --> OPEN
    OPEN --> PROVIDERS
    SF_MODELS --> RECOMMEND
    RECOMMEND --> GOV
    GOV --> ACTIONS
    ACTIONS --> EXPAPI
    EXPAPI --> PROCAPI
    PROCAPI --> SYSAPI
    ACTIONS --> CORE

    CORE --> LWC
    CORE --> SLACK
    D360 --> TABLEAU
    GOV --> API

    D360 -. approved snapshots .-> EVALDATA
    CORE -. reviewed outcomes .-> EVALDATA
    EVALDATA --> LOOP
    LOOP --> CANDIDATE
    CANDIDATE --> SCORE
    SCORE --> LOOP
    SCORE --> PROMOTE
    PROMOTE -. versioned configuration .-> ROUTER
    PROMOTE -. approved templates and rules .-> AGENT
```

## Runtime Flow

1. MuleSoft receives a source event, validates it, preserves the source
   record, and applies retry and replay controls.
2. Data 360 harmonizes the event, resolves identity, calculates defined
   measures, and retains history.
3. The semantic layer defines what records and relationships mean and validates
   required provenance.
4. Salesforce Core creates or updates the operational work item, SOP execution,
   evidence, owner, deadline, and affected relationships.
5. Agentforce receives only the context the current user and purpose are
   permitted to access.
6. A logical model profile selects an approved model deployment without
   exposing provider-specific names to business logic.
7. The model produces an explanation, recommendation, or draft. Deterministic
   code validates its shape, citations, permissions, and applicable policy.
8. A human approves, rejects, or modifies consequential actions.
9. MuleSoft writes the approved action to the authoritative source system.
10. The resulting outcome event returns through the same ingestion path and is
    attached to the decision trace.

## Storage Responsibilities

| Component       | Responsibility                                                                             |
| --------------- | ------------------------------------------------------------------------------------------ |
| Source systems  | Authoritative operational source records                                                   |
| MuleSoft        | Source-specific connectivity, validation, orchestration, retries, and write-back           |
| Data 360        | Harmonization, identity, event history, calculated insights, and model features            |
| Salesforce Core | Current operational work, SOP execution, recommendations, approvals, actions, and outcomes |
| Ontology files  | Versioned meaning, mappings, provenance requirements, and validation rules                 |
| Model providers | Inference only; they are not the system of record                                          |
| Evaluation lab  | Isolated experiments and candidate configurations, never live enterprise actions           |

## Current Repository State

The architecture and roadmap exist, but the product runtime has not yet been
scaffolded. The next executable work is the Salesforce DX skeleton, event
contracts, and initial ontology.
