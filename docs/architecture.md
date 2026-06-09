# System Architecture

## Product Mental Model

This branch turns authorized first-party business data into evidence-backed
decisions, coordinated relationship actions, and outcome feedback.

```mermaid
flowchart LR
    SOURCES["Business source signals<br/>CRM, ERP, POS, HR, service,<br/>finance, operations, documents"]
    CONTEXT["Evidence and context<br/>source records, identity, ontology,<br/>permissions, relationship graph"]
    AGENTS["Agentforce and model analysis<br/>facts, claims, inferences,<br/>predictions, recommendations"]
    REVIEW["Human review<br/>tradeoffs, confidence,<br/>approval policy, decision"]
    ACTIONS["Coordinated actions<br/>tasks, outreach, cases,<br/>MuleSoft write-backs, channel alerts"]
    OUTCOME["Outcome evidence<br/>responses, completions,<br/>exceptions, business metrics"]

    SOURCES --> CONTEXT --> AGENTS --> REVIEW --> ACTIONS --> OUTCOME
    OUTCOME -->|"new evidence"| CONTEXT
```

The key rule is simple: agents can recommend, explain, draft, and request
approval. Consequential external actions require the configured approval policy
and an auditable action boundary.

## Closed-Loop Flow

1. A source event arrives from an authorized business system or fixture.
2. The event contract validates the envelope, hash, idempotency key, sequence,
   and correlation ID.
3. The source payload maps into Salesforce context records for entities,
   relationships, evidence, work items, recommendations, approvals, actions, and
   outcomes.
4. Agentforce receives only the context the current user and purpose can access.
5. Specialist agents analyze the relevant relationship, operational, financial,
   service, supplier, staff, or customer context.
6. The orchestrator produces one evidence-backed recommendation or plan.
7. The responsible human approves, rejects, modifies, or defers protected
   actions.
8. MuleSoft mocks execute approved write-backs and channel alerts.
9. Outcome events return through the same intake path and refresh the command
   center and relationship state.

## Runtime Components

```mermaid
flowchart TB
    subgraph Sources["Authorized Sources"]
        CRM["CRM and service"]
        OPS["Operations and POS"]
        ERP["ERP and finance"]
        HR["HR and roster"]
        DOCS["Documents and messages"]
        EXT["Approved partner systems"]
    end

    subgraph Integration["Integration Boundary"]
        EVENTS["Event contract"]
        MULE["MuleSoft mock APIs"]
        CHANNELS["Slack and WhatsApp-style mocks"]
    end

    subgraph Salesforce["Salesforce Core"]
        RECORDS["HFS records used as internal spine"]
        WORK["Relationship work item and SOP step"]
        APPROVAL["Human approval"]
        AUDIT["Action, outcome, and audit history"]
    end

    subgraph Intelligence["Agentforce and Model Gateway"]
        CONTEXT["Permission-aware context"]
        ROUTER["Logical model routing"]
        AGENT["Specialist agents"]
        REC["Evidence-backed recommendation"]
    end

    subgraph UI["Human Surface"]
        LWC["Command center"]
        ALERTS["Alert log"]
        METRICS["Outcome metrics"]
    end

    Sources --> EVENTS --> MULE --> RECORDS
    RECORDS --> WORK --> CONTEXT --> AGENT
    AGENT --> ROUTER --> REC --> APPROVAL
    APPROVAL --> AUDIT
    AUDIT --> MULE --> CHANNELS
    AUDIT --> RECORDS
    RECORDS --> LWC
    CHANNELS --> ALERTS
    AUDIT --> METRICS
```

## Storage Responsibilities

| Component       | Responsibility                                                                   |
| --------------- | -------------------------------------------------------------------------------- |
| Source fixtures | Synthetic business records and event payloads                                    |
| MuleSoft mocks  | Intake, validation, write-back simulation, channel results, retry behavior       |
| Salesforce Core | Work item, evidence, recommendation, approval, action, outcome, and audit record |
| Model gateway   | Logical model profile, routing, validation, fallback, and invocation audit       |
| Agentforce      | Explanation, recommendation drafting, approval request, and governed refusal     |
| Lightning       | Command center, evidence timeline, approval cockpit, alert log, outcome view     |

## Current Repository State

The repo already contains a reusable governed spine: Salesforce metadata,
service contracts, event schemas, MuleSoft mocks, model-gateway fixtures,
Agentforce contracts, a Lightning command center, and harness scripts.

The next work is to keep that spine broad enough for relationship-management
intelligence while using the retail demo as one concrete vertical slice.
