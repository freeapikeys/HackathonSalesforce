# North Star Implementation Plan

## Goal

Convert the existing HFS vertical slice into a North Star supermarket MVP
without weakening the governed Salesforce, Agentforce, MuleSoft, and model
contracts already present in the repository.

## Current Starting Point

The repository already has:

- Salesforce custom objects for event, entity, relationship, agreement, work,
  evidence, recommendation, approval, action, outcome, and evaluation;
- Apex services and Agentforce invocable actions;
- MuleSoft OpenAPI and Python mock runtime;
- provider-neutral model gateway and fixtures;
- Lightning command center component and state adapter;
- deterministic seed, reset, and end-to-end harness scripts.

The first task is specialization, not reinvention.

## Workstream 1: Retail Domain Mapping

Tasks:

1. Map retail concepts onto existing HFS objects.
2. Add optional fields only where the current generic records cannot express
   demo needs.
3. Keep all mappings product-category neutral.

Initial mapping:

| Retail concept      | HFS object                                                        |
| ------------------- | ----------------------------------------------------------------- |
| Store               | `HFS_Entity__c` with type `ORGANIZATION` or `ORGANIZATIONAL_UNIT` |
| Product             | `HFS_Entity__c` with type `PRODUCT`                               |
| Supplier            | `HFS_Entity__c` with type `SUPPLIER`                              |
| Product batch       | `HFS_Entity__c` with type `ASSET` or `PRODUCT_BATCH` if added     |
| Promotion           | `HFS_Agreement__c` or `HFS_Event__c` depending on source          |
| Stockout risk       | `HFS_Event__c` plus `HFS_Work_Item__c`                            |
| Complaint cluster   | `HFS_Event__c` plus `HFS_Evidence__c`                             |
| Supplier resolution | `HFS_Event__c`, `HFS_Evidence__c`, and `HFS_Outcome__c`           |
| Staff/store task    | `HFS_Action__c` and optionally Salesforce Task                    |

Acceptance:

- seed data creates multiple product categories;
- no metadata or UI label assumes burgers only;
- Apex tests still pass.

## Workstream 2: North Star Demo Seed and Event Fixtures

Tasks:

1. Replace generic service-interruption seed with North Star retail scenario.
2. Add event fixtures for:
   - `STOCKOUT_RISK_DETECTED`;
   - `EXPIRY_RISK_DETECTED`;
   - `COMPLAINT_CLUSTER_DETECTED`;
   - `SUPPLIER_RESPONSE_RECEIVED`;
   - `QUEUE_RISK_DETECTED`;
   - `ACTION_OUTCOME_CAPTURED`.
3. Keep duplicate, malformed, late, out-of-order, and replay cases.

Acceptance:

- `npm run check:events` passes;
- `npm run check:mulesoft` passes;
- `npm run demo:seed` creates one coherent retail case.

## Workstream 3: Agentforce Topics and Actions

Agentforce topics:

- North Star Orchestration;
- Inventory and Waste;
- Supplier and Product Trust;
- Store Execution and Outreach;
- Manager Approval and Outreach.

Agentforce action catalog:

- explain North Star case;
- draft evidence-backed recovery plan;
- request manager approval;
- summarize supplier response;
- draft staff alerts;
- draft supplier quality message.

Protected execution remains behind Salesforce approval and MuleSoft action
execution. Agentforce can draft and request approval, but it cannot directly
send Slack, WhatsApp, reorder, supplier, or markdown actions.

Acceptance:

- recommendations cite inventory, complaint, supplier, and staffing evidence;
- supplier decision includes the "do not blindly stop orders" rule;
- restricted or missing evidence fails closed.

## Workstream 4: MuleSoft Mock Actions and Channels

Mock actions:

- `CREATE_SUPPLIER_QUALITY_CASE`;
- `REQUEST_REPLACEMENT_BATCH`;
- `CREATE_REORDER_REQUEST`;
- `CREATE_WAREHOUSE_TRANSFER`;
- `CREATE_MARKDOWN_PLAN`;
- `CREATE_STORE_TASKS`;
- `SEND_SLACK_ALERT`;
- `SEND_WHATSAPP_ALERT`;
- `CAPTURE_RETAIL_OUTCOME`.

Slack:

- use a real incoming webhook when available;
- otherwise preserve a mock sent-message record and show it in the UI.

WhatsApp:

- use Twilio WhatsApp Sandbox or Meta Cloud API only if setup is complete;
- otherwise use a WhatsApp-style internal alert panel and a MuleSoft mock
  response that is honest about being a demo substitute.

Acceptance:

- one approved action writes back through MuleSoft;
- Slack and WhatsApp-style alert results are visible;
- unapproved action execution returns denial.

## Workstream 5: North Star Command Center

Update the Lightning command center from relationship wording to retail
operations wording.

Required panels:

- risk pulse cards: stockout, expiry, complaint, supplier, queue;
- product and batch context;
- evidence timeline;
- agent reasoning with facts and inferences;
- supplier response panel;
- approval cockpit;
- Slack and WhatsApp-style alert log;
- outcome metrics.

Acceptance:

- mock mode works without Salesforce live data;
- live mode works from `HFS_RelationshipController`;
- UI labels support any product category;
- LWC tests cover ready, restricted, denied, error, and approval states.

## Workstream 6: End-to-End Proof Path

Required beats:

1. Launch risk event.
2. Show conflicting evidence.
3. Ask Agentforce for recommendation.
4. Receive supplier response.
5. Show recommendation update.
6. Approve.
7. Execute MuleSoft action.
8. Show Slack and WhatsApp-style alerts.
9. Show outcome and audit trail.

## Implementation Guardrails

Every contributor should understand all three agents:

- Inventory and Waste Agent;
- Supplier and Product Trust Agent;
- Store Execution and Outreach Agent.

Approval here means business approval by a demo role such as Store Manager,
Duty Manager, or Operations Manager. It does not require the demo user to be a
Salesforce org admin. For the MVP, approval can be implemented as a Salesforce
record/status or command-center button that allows MuleSoft to execute a
protected action only after the manager role has approved it.

CLI workflow for each Codex user:

1. Pull latest `main`.
2. Read [north-star-mvp.md](north-star-mvp.md) and this implementation plan.
3. Pick one checklist item from the relevant workstream.
4. Ask Codex to inspect the exact files and tests before editing.
5. Make the smallest working change.
6. Run the focused check for the changed surface.
7. Update the relevant Markdown or fixture if behavior changed.
8. Push or hand off only after the focused check passes.

Rules:

- no one hard-codes burger-only labels, product IDs, supplier names, or channel
  assumptions;
- each change updates the relevant doc, fixture, or runbook when behavior
  changes;
- every protected action requires a business manager approval record/status
  before MuleSoft execution;
- Slack and WhatsApp integrations must have honest fallback modes when real
  credentials are unavailable;
- run focused checks before handing off;
- keep a backup recorded demo path if live channels fail.

Focused checks:

| Surface                  | Minimum focused checks                                                                                    |
| ------------------------ | --------------------------------------------------------------------------------------------------------- |
| Salesforce core          | `npm run check:project`, Apex tests for recommendation, approval, evidence, action, and outcome behavior  |
| Agentforce contracts     | Agentforce contract fixture checks, refusal checks, evidence citation checks                              |
| MuleSoft and channels    | `npm run check:mulesoft`, approved action execution path, denied action execution path, channel fixtures  |
| Lightning command center | LWC unit tests, UI mock fixture render, ready/restricted/denied/error/approval states                     |
| Event and data fixtures  | fixture schema validation, malformed/late/duplicate/out-of-order examples, expected recommendation review |

## Build Checklist

### Slack and Approved MuleSoft Execution

- [ ] Inspect `docs/mulesoft-api-contract.md`, `mulesoft/README.md`, and the
      existing MuleSoft mock runtime before editing.
- [ ] Ensure `EXECUTE_APPROVED_ACTION` supports `SEND_SLACK_ALERT` with a clear
      request/response shape, correlation ID, approval ID, action ID, channel,
      target role, message body, delivery status, and fallback reason.
- [ ] Add a Slack configuration path that can use `SLACK_WEBHOOK_URL` when it is
      present and returns an honest mock result when it is missing.
- [ ] Make unapproved Slack execution fail closed with a useful error and no
      fake success.
- [ ] Store or return enough delivery evidence for Salesforce and the command
      center to show `PENDING`, `SENT`, `FAILED`, or `MOCK_SENT`.
- [ ] Add or update fixtures for approved Slack success, missing-webhook mock
      mode, and unapproved denial.
- [ ] Run `npm run check:mulesoft` before handoff.

### Salesforce Core and Agentforce Recommendation

- [ ] Inspect `docs/salesforce-data-model.md`,
      `docs/agentforce-action-contract.md`, `docs/apex-service-contract.md`, and
      the Apex service classes before editing.
- [ ] Confirm the Salesforce records can represent product, batch, store,
      supplier, promotion, complaint evidence, approval, action, and outcome for
      any product category.
- [ ] Add or update seed data for at least three categories, not only the first
      burger-style scenario.
- [ ] Wire Agentforce-facing outputs for Inventory/Waste so recommendations cite
      facts, separate inferences, and name the missing evidence when uncertain.
- [ ] Ensure the orchestrator recommendation includes supplier/product trust and
      store execution implications.
- [ ] Preserve the rule that complaints trigger investigation and supplier
      response first, not automatic supplier blocking.
- [ ] Run `npm run check:project` plus the relevant Apex/Agentforce contract
      checks before handoff.

### WhatsApp and Command Center Experience

- [ ] Inspect `docs/ui-state-contract.md`, `docs/mulesoft-api-contract.md`, the
      LWC command center, and existing UI fixtures before editing.
- [ ] Ensure `EXECUTE_APPROVED_ACTION` supports `SEND_WHATSAPP_ALERT` with the
      same approval, correlation, target role, message, delivery status, and
      fallback fields as Slack.
- [ ] Add a WhatsApp configuration path that can use Twilio Sandbox or Meta
      Cloud API only when credentials are configured, otherwise returns
      `MOCK_SENT` honestly.
- [ ] Update the command center to show risk pulse, evidence timeline, supplier
      response, approval cockpit, Slack result, WhatsApp result, and store-task
      acknowledgement without product-specific labels.
- [ ] Add UI mock states for ready, restricted, denied, channel failed, channel
      mock sent, and action approved.
- [ ] Run LWC tests and `npm run check:mulesoft` when the WhatsApp contract
      changes.

### Data, Edge Cases, and Recommendation Validation

- [ ] Build a small product catalog across fresh food, frozen food, dairy,
      beverages, household, and one higher-value category.
- [ ] Create realistic complaint clusters that test isolated complaints,
      batch-specific issues, supplier-wide suspicion, price mismatch, expiry,
      packaging damage, and refund patterns.
- [ ] Create supplier response examples: replacement batch approved, credit note
      offered, delayed delivery, insufficient evidence, and unresolved quality
      issue.
- [ ] Create late, malformed, duplicate, and out-of-order event examples so the
      integration path proves it handles messy data.
- [ ] Write expected recommendation notes for each scenario: what the agent
      should recommend, what it should refuse to do, what needs approval, and
      what evidence is missing.
- [ ] Validate manually that the final system never treats every supplier
      complaint as a reason to stop all orders.

## Minimum Checks

Run before final demo rehearsal:

```bash
npm run check:project
npm run check:events
npm run check:mulesoft
npm run check:models
npm run check:agentforce
npm run test:unit
```

Run after Salesforce org setup:

```bash
npm run demo:reset -- --target-org hfs-dev
npm run demo:seed -- --target-org hfs-dev
npm run demo:run -- --target-org hfs-dev
```
