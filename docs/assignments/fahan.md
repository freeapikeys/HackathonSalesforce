# Fahan Assignment: Slack Integration And Approved Communication

## Goal

Own the Slack alert path for Logia's private hospital operations demo.
Slack is a protected communication action behind Salesforce approval,
Agentforce recommendation, and MuleSoft execution. It is not a standalone
chatbot and it must not carry clinical decision-making.

## What The Project Already Has

Start from the existing governed spine:

- `docs/logia-mvp.md` defines the global operating model and hospital demo.
- `docs/logia-implementation-plan.md` defines the practical build plan.
- `docs/mulesoft-api-contract.md` defines the integration boundary.
- `mulesoft/README.md` explains the mock runtime and Logia mock actions.
- `mulesoft/mock_runtime/` contains the Python reference runtime.
- `mulesoft/api/hfs-integration-v1.openapi.json` is the generated Process API
  contract.
- `mulesoft/api/examples/operation-examples-v1.json` contains generated request
  and response examples.
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/fixtures.js` holds
  UI fixture state that can show channel delivery status.
- Salesforce records already model actions and outcomes through the HFS spine.

The Slack branch already prepared `SEND_SLACK_ALERT` with real webhook support
through `SLACK_WEBHOOK_URL`, honest `MOCK_SENT` fallback, denial before
approval, malformed payload validation, and correlation/evidence preservation.
Your next work is to keep that path working while updating examples, docs, and
fixtures from retail roles to hospital operations roles.

## Files To Inspect First

- `docs/logia-mvp.md`
- `docs/logia-implementation-plan.md`
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

Slack remains the protected action type `SEND_SLACK_ALERT`.

The action may execute only after business approval exists. Approval means an
Operations Manager, Bed Manager, Pharmacy Lead, Billing Supervisor, Patient
Experience Manager, or Duty Manager approved the action in the demo flow. It
does not mean a developer approves code work.

The action request should preserve:

- `tenantId`
- `correlationId`
- `approvalId`
- `actionId`
- `actionType` equal to `SEND_SLACK_ALERT`
- `targetRole`, such as `Operations Manager`, `Bed Manager`, `Pharmacy Lead`,
  `Billing Supervisor`, or `Patient Experience Lead`
- `targetChannel`, such as `#logia-demo` or `hospital-ops-alerts`
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
- `approvalId`
- `evidenceIds`
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

A Slack alert should be short, operational, and privacy-safe:

```text
Logia alert: Bed capacity and patient wait risk
Department: Outpatient reception and discharge ward
Action: Release cleaned rooms, move porter task forward, review billing hold
Owner: Operations Manager
Due: 2026-06-13 10:30 MUT
Evidence: complaint-cluster-hos-003, bed-capacity-041, billing-approval-007
```

Do not include raw secrets, real patient names, medical records, diagnoses,
treatment details, phone numbers, or unsupported model claims.

## Implementation Checklist

- [x] Pull latest `main` into the working branch.
- [x] Read this file and the required docs.
- [x] Inspect the existing MuleSoft mock runtime before editing.
- [x] Confirm where approved action execution is represented today.
- [x] Add or finish `SEND_SLACK_ALERT` in the action examples.
- [x] Add or finish Slack handling in the mock runtime.
- [x] Add real webhook behavior only through `SLACK_WEBHOOK_URL`.
- [x] Add mock fallback behavior with `status: MOCK_SENT`.
- [x] Add denial behavior when `approvalId` is missing or not approved.
- [x] Add failure behavior for malformed Slack payloads.
- [x] Ensure every response preserves `correlationId` and `actionId`.
- [x] Add fixtures for approved real-capable Slack, mock Slack, and denied
      Slack.
- [x] Add enough result data for the LWC to display channel status.
- [x] Replace retail Slack examples with hospital operations examples.
- [x] Add hospital role aliases for Slack targets.
- [x] Confirm Slack message body is privacy-safe.
- [x] Confirm clinical decision requests are never sent as Slack instructions.
- [x] Update docs only if the action contract or fallback behavior changes.

## Testing Checklist

- [x] Run `npm run check:mulesoft`.
- [x] Run `npm run check:project` if Salesforce metadata or generated examples
      are touched.
- [x] Add or update MuleSoft tests for hospital Slack examples if the contract
      changes.
- [x] Confirm no credential values, real patient data, phone numbers, emails,
      medical records, or local machine paths appear in `git diff`.

## Demo Acceptance

The Slack work is demo-ready when:

- a recommended hospital action can request Slack alert execution;
- an unapproved Slack action is denied;
- an approved Slack action returns `SENT` or `MOCK_SENT`;
- the result can be shown in the command center;
- the message names department, action, owner role, deadline, and evidence;
- the demo remains honest if no real Slack webhook is configured;
- the Slack path never sends clinical diagnosis, treatment, dosage, or triage
  instructions.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/fahan.md, docs/mulesoft-api-contract.md, and
mulesoft/README.md. Preserve the approved SEND_SLACK_ALERT path while updating
Slack examples, fixtures, and role aliases for the private hospital operations
demo. Do not commit credentials or patient data. Keep approval gating and honest
MOCK_SENT fallback. Add or update tests and run npm run check:mulesoft.
```
