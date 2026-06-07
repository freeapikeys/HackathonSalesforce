# System Architecture

## Product Mental Model

North Star turns scattered supermarket signals into approved operational
actions.

```mermaid
flowchart LR
    SOURCES["Retail source signals<br/>POS, inventory, expiry, complaints,<br/>supplier, promotion, roster"]
    CONTEXT["Evidence and context<br/>product, batch, store, supplier,<br/>promotion, staff, complaint cluster"]
    AGENTS["Agentforce analysis<br/>inventory/waste,<br/>supplier/product trust,<br/>store execution/outreach"]
    REVIEW["Manager review<br/>facts, inference, recommendation,<br/>approval"]
    ACTIONS["Mocked actions<br/>supplier case, reorder, transfer,<br/>markdown, task, Slack, WhatsApp-style alert"]
    OUTCOME["Outcome<br/>stockout avoided, waste reduced,<br/>complaint risk, staff readiness"]

    SOURCES --> CONTEXT --> AGENTS --> REVIEW --> ACTIONS --> OUTCOME
    OUTCOME -->|"new evidence"| CONTEXT
```

The key rule is simple: agents can recommend, explain, draft, and request
approval. Consequential external actions require manager approval and an
auditable action boundary.

## North Star Flow

1. A retail event arrives from a synthetic POS, inventory, expiry, complaint,
   supplier, promotion, or staffing source.
2. The event contract validates the envelope, hash, idempotency key, sequence,
   and correlation ID.
3. The source payload maps into Salesforce context records for product, batch,
   store, supplier, promotion, complaint evidence, staff readiness, work item,
   recommendation, approval, action, and outcome.
4. Agentforce receives only the context the current user and purpose can access.
5. Three specialist agents analyze inventory/waste, supplier/product trust, and
   store execution/outreach.
6. The orchestrator produces one evidence-backed recovery plan.
7. The manager approves, rejects, modifies, or defers protected actions.
8. MuleSoft mocks execute approved write-backs and channel alerts.
9. Outcome events return through the same intake path and refresh the command
   center.

## Runtime Components

```mermaid
flowchart TB
    subgraph RetailSources["Retail Sources"]
        POS["POS sales"]
        INV["Inventory and batches"]
        EXP["Expiry and markdown"]
        COMP["Complaints and refunds"]
        SUP["Supplier response"]
        ROSTER["Roster and queue signals"]
    end

    subgraph Integration["Integration Boundary"]
        EVENTS["Event contract"]
        MULE["MuleSoft mock APIs"]
        CHANNELS["Slack and WhatsApp-style mocks"]
    end

    subgraph Salesforce["Salesforce Core"]
        RECORDS["HFS records used as internal spine"]
        WORK["Retail work item and SOP step"]
        APPROVAL["Manager approval"]
        AUDIT["Action, outcome, and audit history"]
    end

    subgraph Intelligence["Agentforce and Model Gateway"]
        CONTEXT["Permission-aware context"]
        ROUTER["Logical model routing"]
        AGENT["North Star agents"]
        REC["Recovery recommendation"]
    end

    subgraph UI["Human Surface"]
        LWC["North Star command center"]
        ALERTS["Alert log"]
        METRICS["Outcome metrics"]
    end

    RetailSources --> EVENTS --> MULE --> RECORDS
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
| Source fixtures | Synthetic retail records and event payloads                                      |
| MuleSoft mocks  | Intake, validation, write-back simulation, channel results, retry behavior       |
| Salesforce Core | Work item, evidence, recommendation, approval, action, outcome, and audit record |
| Model gateway   | Logical model profile, routing, validation, fallback, and invocation audit       |
| Agentforce      | Explanation, recommendation drafting, approval request, and governed refusal     |
| Lightning       | Command center, evidence timeline, approval cockpit, alert log, outcome view     |

## Current Repository State

The repo already contains a reusable governed spine: Salesforce metadata,
service contracts, event schemas, MuleSoft mocks, model-gateway fixtures,
Agentforce contracts, a Lightning command center, and harness scripts.

The next work is North Star specialization: retail fixtures, retail labels,
North Star Agentforce topics, approved mock write-backs, Slack and
WhatsApp-style alert results, and a polished command-center demo.
