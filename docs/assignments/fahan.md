# Fahan Assignment: Slack Integration

## Goal

Build the Slack alert path for North Star so approved retail actions can notify
internal staff through Slack or an honest mock result. This is not a standalone
chatbot. It is one protected channel action behind Salesforce approval,
Agentforce recommendation, and MuleSoft execution.

## What The Project Already Has

Start from the existing governed spine:

- `docs/north-star-mvp.md` defines the supermarket MVP and three-agent system.
- `docs/north-star-implementation-plan.md` defines the generic build checklist.
- `docs/mulesoft-api-contract.md` defines the integration boundary.
- `mulesoft/README.md` explains the mock runtime and North Star mock actions.
- `mulesoft/mock_runtime/` contains the local Python reference runtime.
- `mulesoft/api/hfs-integration-v1.openapi.json` is the generated Process API
  contract.
- `mulesoft/api/examples/operation-examples-v1.json` contains generated request
  and response examples.
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/fixtures.js`
  currently holds UI fixture state that can later show Slack delivery status.
- Salesforce records already model actions and outcomes through the HFS spine.

Do not build a separate Slack app UI. The Slack path should be an action result
that the command center can display.

## Files To Inspect First

- `docs/north-star-mvp.md`
- `docs/north-star-implementation-plan.md`
- `docs/mulesoft-api-contract.md`
- `docs/ui-state-contract.md`
- `mulesoft/README.md`
- `mulesoft/mock_runtime/api.py`
- `mulesoft/mock_runtime/contract.py`
- `mulesoft/tests/test_mock_adapters.py`
- `mulesoft/tests/test_mock_adapter_failures.py`
- `mulesoft/api/examples/operation-examples-v1.json`
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/fixtures.js`

## Required Behavior

Slack must be modeled as the protected action type `SEND_SLACK_ALERT`.

The action may execute only after a business approval exists. Approval means a
Store Manager, Duty Manager, or Operations Manager approved the action in the
demo flow. It does not mean a developer approves code work.

The action request should preserve:

- `tenantId`
- `correlationId`
- `approvalId`
- `actionId`
- `actionType` equal to `SEND_SLACK_ALERT`
- `targetRole`, such as `Duty Manager`, `Cashier Lead`, or `Stockroom Lead`
- `targetChannel`, such as `#north-star-demo` or `retail-ops-alerts`
- `messageTitle`
- `messageBody`
- `evidenceIds`
- `sourceRecommendationId`

The action response should preserve:

- `status`: `PENDING`, `SENT`, `FAILED`, `MOCK_SENT`, or `DENIED`
- `provider`: `slack-webhook` or `mock-slack`
- `providerMessageId` when available
- `sentAt` when sent
- `fallbackReason` when using mock mode
- `correlationId`
- `actionId`
- `outcomeEventId` or callback reference when available

## Real Slack Versus Mock Slack

Use this rule:

- If `SLACK_WEBHOOK_URL` is configured, send a real Slack webhook message.
- If `SLACK_WEBHOOK_URL` is missing, return `MOCK_SENT`.
- Never commit Slack credentials.
- Never show `SENT` when the message was not actually sent.
- Never execute Slack before approval.

The demo is allowed to use mock mode. It must be honest on screen.

## Message Content

A Slack alert should be short and operational:

```text
North Star alert: Fresh Food stockout and quality risk
Product: Frozen beef patties, batch BEEF-2026-06-A
Store: Grand Baie
Action: Check shelf stock, quarantine suspect batch, prepare transfer request
Owner: Stockroom Lead
Due: 2026-06-13 10:30 MUT
Evidence: complaint-cluster-003, inventory-position-041, supplier-response-002
```

Do not put raw secrets, full customer personal data, or unsupported model claims
inside the Slack message.

## Implementation Checklist

- [ ] Pull latest `main`.
- [ ] Read this file and the required docs.
- [ ] Inspect the existing MuleSoft mock runtime before editing.
- [ ] Confirm where approved action execution is represented today.
- [ ] Add or finish `SEND_SLACK_ALERT` in the action examples.
- [ ] Add or finish Slack handling in the mock runtime.
- [ ] Add real webhook behavior only through `SLACK_WEBHOOK_URL`.
- [ ] Add mock fallback behavior with `status: MOCK_SENT`.
- [ ] Add denial behavior when `approvalId` is missing or not approved.
- [ ] Add failure behavior for malformed Slack payloads.
- [ ] Ensure every response preserves `correlationId` and `actionId`.
- [ ] Add fixtures for approved real-capable Slack, mock Slack, and denied
      Slack.
- [ ] Add enough result data for the LWC to display channel status.
- [ ] Update docs only if the action contract or fallback behavior changes.

## Testing Checklist

- [ ] Run `npm run check:mulesoft`.
- [ ] Run `npm run check:project` if Salesforce metadata or generated examples
      are touched.
- [ ] Add or update MuleSoft tests for: - approved Slack execution; - missing webhook mock mode; - missing approval denial; - malformed payload rejection; - correlation ID preservation.
- [ ] Confirm no credential values appear in `git diff`.

## Demo Acceptance

The Slack work is demo-ready when:

- a recommended action can request Slack alert execution;
- an unapproved Slack action is denied;
- an approved Slack action returns `SENT` or `MOCK_SENT`;
- the result can be shown in the command center;
- the message names product, store, task, owner role, deadline, and evidence;
- the demo remains honest if no real Slack webhook is configured.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/fahan.md, docs/mulesoft-api-contract.md, and
mulesoft/README.md. Implement the next smallest Slack integration task for
SEND_SLACK_ALERT behind approved MuleSoft action execution. Inspect existing
mock runtime files before editing. Do not commit credentials. Add or update
tests and run npm run check:mulesoft.
```
