# Hassan Assignment: WhatsApp Integration And Voice Mode

## Goal

Build the WhatsApp alert path and a realistic voice-mode prototype for North
Star. WhatsApp is a protected internal alert action. Voice mode is an operator
input surface that creates or submits a transcript into the existing
Agentforce/Salesforce flow. Neither feature should bypass approval, evidence,
or MuleSoft action governance.

## What The Project Already Has

Start from the existing governed spine:

- `docs/north-star-mvp.md` defines the supermarket MVP and three-agent system.
- `docs/north-star-implementation-plan.md` defines generic build steps.
- `docs/mulesoft-api-contract.md` defines approved action execution.
- `docs/agentforce-action-contract.md` defines Agentforce-facing governed
  actions.
- `docs/ui-state-contract.md` defines what the Lightning command center should
  show.
- `mulesoft/mock_runtime/` contains the local reference integration runtime.
- `mulesoft/api/hfs-integration-v1.openapi.json` contains the generated API
  contract.
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/` contains the
  current Lightning command center and fixtures.

Do not build a separate WhatsApp product. Do not build a full call-center
system. Build a hackathon-realistic path that fits the existing MVP.

## Files To Inspect First

- `docs/north-star-mvp.md`
- `docs/north-star-implementation-plan.md`
- `docs/mulesoft-api-contract.md`
- `docs/agentforce-action-contract.md`
- `docs/ui-state-contract.md`
- `mulesoft/README.md`
- `mulesoft/mock_runtime/api.py`
- `mulesoft/mock_runtime/contract.py`
- `mulesoft/tests/test_mock_adapters.py`
- `mulesoft/tests/test_mock_adapter_failures.py`
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/`
- `intelligence/agentforce/fixtures/agentforce-scenarios-v1.json`

## WhatsApp Required Behavior

WhatsApp must be modeled as the protected action type `SEND_WHATSAPP_ALERT`.

The action may execute only after a business manager approval exists. The demo
can use Twilio Sandbox, Meta Cloud API, or a mock result, but it must label the
result honestly.

The action request should preserve:

- `tenantId`
- `correlationId`
- `approvalId`
- `actionId`
- `actionType` equal to `SEND_WHATSAPP_ALERT`
- `targetRole`, such as `Duty Manager` or `Fresh Food Lead`
- `targetPhoneAlias`, never a real personal number in committed fixtures
- `messageTitle`
- `messageBody`
- `evidenceIds`
- `sourceRecommendationId`

The action response should preserve:

- `status`: `PENDING`, `SENT`, `FAILED`, `MOCK_SENT`, or `DENIED`
- `provider`: `twilio-whatsapp`, `meta-whatsapp-cloud`, or `mock-whatsapp`
- `providerMessageId` when available
- `sentAt` when sent
- `fallbackReason` when using mock mode
- `correlationId`
- `actionId`

## WhatsApp Credential Rule

Use this rule:

- Use Twilio Sandbox or Meta Cloud API only when credentials are available.
- Keep all credentials in environment variables.
- Use aliases in fixtures, such as `role:fresh-food-lead`, not real phone
  numbers.
- If credentials are missing, return `MOCK_SENT`.
- Never show `SENT` unless the provider actually accepted the message.
- Never execute WhatsApp before approval.

## Voice Mode Required Behavior

Voice mode should feel useful without pretending to be a production call-center
system.

Recommended MVP:

1. Add a command-center voice panel or input area.
2. Support a manual transcript box first.
3. Optionally use browser speech recognition when available.
4. Convert the transcript into a structured operator request.
5. Send that request through the existing Agentforce/Salesforce context flow.
6. Show the transcript, interpreted intent, and resulting recommendation.

Example voice transcript:

```text
What should I do about the frozen patties risk at Grand Baie before the
Saturday promotion?
```

Expected structured request:

- `intent`: `ASK_RETAIL_RECOVERY_PLAN`
- `productId`: `product-frozen-beef-patties-001`
- `storeId`: `store-grand-baie-001`
- `timeWindow`: `2026-06-13T08:00:00+04:00/2026-06-13T14:00:00+04:00`
- `requestedByRole`: `Duty Manager`
- `transcriptSource`: `manual` or `browser-speech`

Voice mode should not directly execute Slack, WhatsApp, reorder, supplier, or
markdown actions. It can ask for a recommendation and prepare an approval
request.

## Implementation Checklist

- [ ] Pull latest `main`.
- [ ] Read this file and the required docs.
- [ ] Inspect the MuleSoft approved action path before editing.
- [ ] Add or finish `SEND_WHATSAPP_ALERT` examples and mock runtime handling.
- [ ] Add credential-driven provider selection for Twilio or Meta only if
      practical.
- [ ] Add honest `MOCK_SENT` fallback when credentials are missing.
- [ ] Add denial behavior when approval is missing or not approved.
- [ ] Add WhatsApp status fields that the command center can display.
- [ ] Add a voice transcript input surface or fixture path.
- [ ] Add optional browser speech recognition only if it does not destabilize
      the UI.
- [ ] Map transcript to a structured operator request.
- [ ] Ensure voice mode can ask Agentforce for a recommendation but cannot
      execute protected actions directly.
- [ ] Update fixtures for manual transcript, interpreted intent, and resulting
      recommendation.

## Testing Checklist

- [ ] Run `npm run check:mulesoft` when WhatsApp action behavior changes.
- [ ] Run `npm run test:unit` when LWC voice or channel UI changes.
- [ ] Run `npm run check:agentforce` when Agentforce fixtures or actions
      change.
- [ ] Add or update tests for: - approved WhatsApp execution; - mock WhatsApp fallback; - missing approval denial; - voice transcript to structured request; - voice request refusing protected execution.
- [ ] Confirm no phone numbers or credentials appear in `git diff`.

## Demo Acceptance

The WhatsApp and voice work is demo-ready when:

- an approved WhatsApp alert returns `SENT` or `MOCK_SENT`;
- an unapproved WhatsApp alert is denied;
- the command center can show WhatsApp delivery status;
- voice mode accepts a transcript or browser speech input;
- the transcript produces an Agentforce recommendation request;
- voice mode cannot bypass manager approval.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/hassan.md, docs/mulesoft-api-contract.md,
docs/agentforce-action-contract.md, and docs/ui-state-contract.md. Implement
the next smallest WhatsApp or voice-mode task for North Star. Preserve approval
gating and honest mock fallback. Inspect existing files before editing, add
tests, and run the focused checks.
```
