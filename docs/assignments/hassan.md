# Hassan Assignment: Meta WhatsApp Customer Channel And Voice Mode

## Goal

Own the official Meta WhatsApp customer channel and the WhatsApp voice/media
evidence path for North Star's private hospital operations demo. WhatsApp is
the external customer intake surface; Slack is the internal staff and manager
surface. Voice and media become governed evidence, not autonomous clinical or
financial decisions.

The current live Meta reply is only a short receipt acknowledgement. That is
useful because it proves the webhook is alive, but it is not yet the full agent
conversation. Your job is to make the customer-facing WhatsApp layer feel real
without bypassing Salesforce evidence, Agentforce recommendation, business
approval, MuleSoft action governance, or clinical-decision boundaries.

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
assistant. Build a hackathon-realistic operations intake, acknowledgement,
approved-reply, and voice/media evidence path that fits the existing MVP.

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

## Current Reality

- Meta WhatsApp Cloud API is the active hackathon provider.
- Twilio Sandbox is legacy backup only.
- CloudHub currently receives Meta payloads through an inherited route name:
  `/twilio/whatsapp/inbound`.
- A live customer message can create Salesforce intake evidence.
- The visible WhatsApp reply is currently a simple receipt, not the full North
  Star agent response.
- Salesforce intake can store language hints for English, French, and
  Mauritian Creole, but the live Meta receipt still needs same-language wording.
- Voice, image, and document media can be represented as evidence metadata; live
  Meta media download, transcription, OCR, and extraction are still remaining
  work.
- Hassan owns this lane solo for the hackathon: multilingual WhatsApp, voice
  mode, customer-facing chat drafts, and judge-sector WhatsApp use cases.
- Hassan may use his own pretrained multilingual or voice models for language
  detection, translation, transcription, and confidence scoring.
- Hassan may use DeepSeek for customer chat drafting or short same-language
  responses, as long as it stays behind the model/adapter boundary and never
  bypasses evidence, approval, safety, or audit rules.

## Model And Chat Guardrails

Use custom models as implementation details, not as product architecture.

- Do not hard-code `DeepSeek`, a local model name, or a provider-specific model
  ID into North Star core IDs, action IDs, primitive IDs, Agentforce topics, or
  UI state.
- Use logical capabilities instead, for example `language_detection`,
  `voice_transcription`, `message_drafting`, `customer_reply_drafting`, or
  `judge_sector_use_case_mapping`.
- Keep provider credentials, model endpoints, API keys, and local model paths
  outside Git.
- Send only safe, minimized context to any external model: synthetic alias,
  source channel, language, safe summary, evidence IDs, affected primitives,
  and policy flags. Do not send raw phone numbers, raw media URLs, credentials,
  medical records, or private documents.
- Record language, transcript, extraction, and chat-draft confidence where
  available.
- If model confidence is low, ask one short follow-up instead of guessing.
- DeepSeek or pretrained-model output may draft a response, classify intent, or
  summarize evidence. It must not approve actions, send WhatsApp messages,
  decide refunds, make clinical decisions, or bypass manager approval.
- Customer-facing WhatsApp replies remain short, same-language where safe, and
  manager-approved before consequential statements are sent.

## Judge-Sector Use Cases

Hassan owns the WhatsApp/chat use-case examples for the judge sectors. These
are demo mappings, not separate architectures.

- [ ] Build a hospital WhatsApp use case for patient/visitor complaint intake.
- [ ] Build a hotel WhatsApp use case for guest complaint, room readiness,
      billing, food/service, and housekeeping coordination.
- [ ] Build an airport WhatsApp use case for passenger complaint, gate/baggage
      issue, vendor delay, staff coordination, and customer update.
- [ ] Build a banking WhatsApp use case for client complaint, duplicate charge,
      dispute/case status, compliance-safe follow-up, and manager approval.
- [ ] For each sector, map the use case to the same primitives:
      `Signal`, `Evidence`, `Customer`, `Resource`, `Partner`, `Policy`,
      `Recommendation`, `Approval`, `Action`, `Outcome`, and `Metric`.
- [ ] For each sector, show which model step is used:
      language detection, voice transcription, chat draft, evidence summary, or
      follow-up question.
- [ ] For each sector, name what must remain human-approved.
- [ ] Keep wording simple and natural. Do not create a separate bot per sector.

## WhatsApp Required Behavior

Inbound WhatsApp must create `Signal` and `Evidence`.

Outbound WhatsApp must be modeled as the protected action type
`SEND_WHATSAPP_ALERT` when it sends a customer-safe reply, internal mobile
alert, or approved follow-up.

The action may execute only after a business manager approval exists. The
hackathon demo uses official Meta WhatsApp Cloud API. If the provider token,
phone number, webhook subscription, or test recipient is incomplete, label the
result honestly.

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

- Use Meta WhatsApp Cloud API for the demo provider.
- Keep Twilio only as legacy backup/context, not as the main plan.
- Keep all credentials in environment variables.
- Replace short-lived test tokens with a permanent system-user token before the
  final rehearsal.
- Use aliases in fixtures, such as `role:bed-manager`, not real phone numbers.
- If credentials are missing, return `MOCK_SENT`.
- Never show `SENT` unless the provider actually accepted the message.
- Never execute WhatsApp before approval.

## Voice And Media Required Behavior

WhatsApp voice/media should feel useful without pretending to be a clinical
assistant.

Recommended MVP:

1. Detect Meta WhatsApp text, audio, image, and document message types.
2. For text, create a safe `Signal` and `Evidence` record.
3. For audio, download the media through Meta only at runtime, store safe
   metadata, and create transcript evidence when transcription succeeds.
4. If transcription confidence is low or unavailable, ask one short follow-up.
5. For images and documents, store safe metadata and extraction confidence.
6. Never commit raw media URLs, phone numbers, audio files, screenshots,
   documents, or customer personal data.
7. Convert transcript or extracted text into a structured operations request.
8. Send that request through the existing Agentforce/Salesforce context flow.
9. Show the transcript, interpreted intent, refusal if needed, and resulting
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
- [ ] Update the live Meta acknowledgement so English complaints receive short
      plain English receipts.
- [ ] Update the live Meta acknowledgement so French complaints receive short
      plain French receipts.
- [ ] Update the live Meta acknowledgement so Mauritian Creole complaints
      receive short plain Mauritian Creole receipts.
- [ ] Make the receipt clear that North Star received the issue and a manager
      will review it; do not promise the action is completed.
- [ ] Add approved customer-facing WhatsApp reply execution after manager
      approval. The reply must be privacy-safe and must not include diagnosis,
      treatment, dosage, triage, refund approval, or legal/financial final
      decisions.
- [ ] Add Meta audio message handling: detect `audio`, retrieve media metadata,
      avoid storing raw media in Git or Salesforce demo text fields, and create
      pending transcript evidence when transcription is unavailable.
- [ ] Add a transcription adapter path or stub that records transcript,
      language, confidence, and evidence ID.
- [ ] Add one short follow-up question when transcript confidence is low.
- [ ] Add Meta image/document handling: detect `image` and `document`, record
      safe metadata, create extraction evidence or pending extraction state,
      and ask one short follow-up when extraction is low-confidence.
- [ ] Add tests or harness proof for Meta text, French text, Mauritian Creole
      text, audio pending transcript, audio transcript success, image/document
      pending extraction, and no raw phone/media storage.
- [ ] Add an adapter boundary for Hassan's pretrained multilingual/voice
      models so language, transcript, and confidence are recorded without
      leaking model-specific IDs into core contracts.
- [ ] Add a DeepSeek-backed or DeepSeek-compatible chat-draft path for safe
      same-language WhatsApp responses, with `MOCK` or local fallback when no
      model credential is available.
- [ ] Add tests or fixtures proving model output cannot approve actions, send
      protected messages, make clinical decisions, decide refunds, or overwrite
      source evidence.
- [ ] Add judge-sector WhatsApp/chat examples for hospital, hotel, airport, and
      banking using the same universal primitives.

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

- a Meta WhatsApp customer text creates Salesforce signal/evidence;
- the customer receives a short same-language receipt;
- an approved WhatsApp alert or customer-safe response returns `SENT` or
  `MOCK_SENT`;
- an unapproved WhatsApp alert is denied;
- the command center can show WhatsApp delivery status;
- WhatsApp voice mode creates transcript evidence or pending-transcript
  evidence;
- image/document messages create extraction evidence or pending-extraction
  evidence;
- the transcript produces an Agentforce recommendation request;
- voice mode cannot bypass manager approval;
- voice mode refuses clinical decisions and routes them to human review.

## Codex Prompt Starter

Use this when starting a fresh Codex task:

```text
Read docs/assignments/hassan.md, docs/mulesoft-api-contract.md,
docs/agentforce-action-contract.md, and docs/ui-state-contract.md. Implement
the next smallest official Meta WhatsApp task for North Star: same-language
receipt, approved customer response, voice-note evidence, or image/document
evidence. Hassan may use his pretrained multilingual/voice models and DeepSeek
for chat drafting behind a safe adapter boundary. Preserve approval gating,
honest mock fallback, no raw personal/media storage, no provider secrets in Git,
no provider-specific core IDs, and clinical decision refusal. Inspect existing
files before editing, add tests, and run the focused checks.
```
