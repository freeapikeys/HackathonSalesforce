# Hassan Assignment: WhatsApp Integration And Voice Mode

## Goal

Build the WhatsApp alert path and a realistic voice/transcript mode for North
Star's private hospital operations demo. WhatsApp is a protected internal alert
action. Voice mode is an operator input surface that turns a transcript into a
governed recommendation request. Neither feature may bypass approval, evidence,
MuleSoft action governance, or clinical-decision boundaries.

## What The Project Already Has

Start from the existing governed spine:

- `docs/north-star-mvp.md` defines the global operating model and hospital demo.
- `docs/north-star-implementation-plan.md` defines generic build steps.
- `docs/mulesoft-api-contract.md` defines approved action execution.
- `docs/agentforce-action-contract.md` defines Agentforce-facing governed
  actions.
- `docs/ui-state-contract.md` defines command-center state expectations.
- `mulesoft/mock_runtime/` contains the local reference integration runtime.
- `mulesoft/api/hfs-integration-v1.openapi.json` contains the generated API
  contract.
- `force-app/main/default/lwc/hfsRelationshipCommandCenter/` contains the
  current Lightning command center and fixtures.

Do not build a separate WhatsApp product. Do not build a clinical voice
assistant. Build a hackathon-realistic operations input and alert path that fits
the existing MVP.

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

The action may execute only after a business manager approval exists. The
hackathon demo should use Twilio Sandbox or an honest mock result, and it must
label the result honestly. Meta Cloud API is out of scope unless business
verification and templates are already ready.

The action request should preserve:

- `tenantId`
- `correlationId`
- `approvalId`
- `actionId`
- `actionType` equal to `SEND_WHATSAPP_ALERT`
- `targetRole`, such as `Operations Manager`, `Bed Manager`, `Pharmacy Lead`,
  `Billing Supervisor`, or `Patient Experience Lead`
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
- `approvalId`
- `actionId`
- `evidenceIds`

## WhatsApp Credential Rule

Use this rule:

- Use Twilio Sandbox only when credentials are available.
- Keep all credentials in environment variables.
- Use aliases in fixtures, such as `role:bed-manager`, not real phone numbers.
- If credentials are missing, return `MOCK_SENT`.
- Never show `SENT` unless the provider actually accepted the message.
- Never execute WhatsApp before approval.

## Voice Mode Required Behavior

Voice mode should feel useful without pretending to be a clinical assistant.

Recommended MVP:

1. Add a command-center voice panel or transcript input area.
2. Support a manual transcript box first.
3. Optionally use browser speech recognition when available.
4. Convert the transcript into a structured hospital operations request.
5. Send that request through the existing Agentforce/Salesforce context flow.
6. Show the transcript, interpreted intent, refusal if needed, and resulting
   recommendation.

Example valid transcript:

```text
Why are discharge beds blocked this morning and who needs to act before the
outpatient queue gets worse?
```

Expected structured request:

- `intent`: `ASK_HOSPITAL_ACTION_PLAN`
- `departmentId`: `department-outpatient-001`
- `locationId`: `ward-discharge-002`
- `resourceIds`: `bed-block-hos-041`, `queue-outpatient-009`
- `timeWindow`: `2026-06-13T08:00:00+04:00/2026-06-13T12:00:00+04:00`
- `requestedByRole`: `Operations Manager`
- `transcriptSource`: `manual` or `browser-speech`

Example refused transcript:

```text
Which patient should receive treatment first?
```

Expected behavior:

- refuse clinical triage or treatment decision;
- explain that North Star handles operations coordination only;
- route to clinician or clinical manager review.

## Implementation Checklist

- [x] Pull latest `main`.
- [x] Read this file and the required docs.
- [x] Inspect the MuleSoft approved action path before editing.
- [x] Add or finish `SEND_WHATSAPP_ALERT` examples and mock runtime handling.
- [x] Add credential-driven provider selection for Twilio only if
      practical.
- [x] Add honest `MOCK_SENT` fallback when credentials are missing.
- [x] Add denial behavior when approval is missing or not approved.
- [x] Add WhatsApp status fields that the command center can display.
- [x] Add malformed WhatsApp payload validation.
- [x] Add WhatsApp response preservation for `tenantId`, `correlationId`,
      `approvalId`, `actionId`, evidence IDs, provider, status, and fallback
      reason.
- [x] Add a voice transcript input surface or fixture path.
- [x] Add optional browser speech recognition only if it does not destabilize
      the UI.
- [x] Map transcript to a structured hospital operations request.
- [x] Ensure voice mode can ask Agentforce for a recommendation but cannot
      execute protected actions directly.
- [x] Ensure voice mode refuses clinical diagnosis, treatment, dosage, triage,
      and clinical priority requests.
- [x] Update fixtures for manual transcript, interpreted intent, clinical
      refusal, and resulting recommendation.

## Testing Checklist

- [x] Run direct MuleSoft checks when WhatsApp action behavior changes.
- [x] Run `npm run test:unit` when LWC voice or channel UI changes.
- [x] Run `npm run check:agentforce` when Agentforce fixtures or actions
      change.
- [x] Add or update tests for approved WhatsApp execution, mock WhatsApp
      fallback, missing approval denial, and malformed payload rejection.
- [x] Add or update tests for voice transcript to structured request, voice
      protected-action refusal, and clinical-decision refusal.
- [x] Confirm no phone numbers, credentials, real patient data, medical records,
      emails, or local paths appear in `git diff`.

## Demo Acceptance

The WhatsApp and voice work is demo-ready when:

- an approved WhatsApp alert returns `SENT` or `MOCK_SENT`;
- an unapproved WhatsApp alert is denied;
- the command center can show WhatsApp delivery status;
- voice mode accepts a transcript or browser speech input;
- the transcript produces an Agentforce recommendation request;
- voice mode cannot bypass manager approval;
- voice mode refuses clinical decisions and routes them to human review.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/hassan.md, docs/mulesoft-api-contract.md,
docs/agentforce-action-contract.md, and docs/ui-state-contract.md. Implement
the next smallest WhatsApp or voice-mode task for the private hospital
operations demo. Preserve approval gating, honest mock fallback, and clinical
decision refusal. Inspect existing files before editing, add tests, and run the
focused checks.
```
