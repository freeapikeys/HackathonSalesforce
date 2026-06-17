# DeepSeek Slack Handoff

This branch exposes the minimum DeepSeek plumbing needed by the Slack
implementation without committing credentials.

## Boundary

Slack code should not call DeepSeek directly and should not know the API key.
Use the model gateway to produce an advisory draft, then pass the approved,
normalized text into the existing protected Slack action path.

Correct flow:

1. Build a model-gateway `generateRequest` from safe context:
   - synthetic case or work item alias;
   - source channel;
   - safe summary;
   - affected primitives;
   - evidence IDs;
   - approval and policy flags.
2. Call the `hfs.generate.v1` adapter through the model gateway.
3. Use the normalized output as draft text only.
4. Create or update a protected `SEND_SLACK_ALERT` action.
5. Require business manager approval before MuleSoft sends the Slack webhook.
6. Record the Slack delivery or mock result as outcome evidence.

Do not send raw phone numbers, raw customer messages, credentials, private
documents, medical records, or provider-specific secrets to Slack or DeepSeek.

## Local Environment

Copy `.env.example` to `.env` for local development, or set equivalent
environment variables through the approved secret manager for shared runtimes.
`.env` is ignored by Git.

```bash
export DEEPSEEK_ENABLED=true
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"
export DEEPSEEK_MODEL="deepseek-chat"
```

`DEEPSEEK_MODEL` is optional and defaults to `deepseek-chat`.

Do not place either value in committed files, screenshots, Slack payloads,
Salesforce fixtures, MuleSoft examples, or Beads issues.

Validate local configuration without a live provider call:

```bash
npm run check:deepseek
```

Run a real DeepSeek smoke test only when you intentionally want a paid/provider
call:

```bash
npm run check:deepseek:live
```

## Runtime Adapter

The reference adapter lives at:

```text
intelligence/model-gateway/runtime/hfs_model_gateway/adapters.py
```

Use:

```python
from hfs_model_gateway import DeepSeekOpenAICompatibleAdapter

adapter = DeepSeekOpenAICompatibleAdapter(enabled=True)
result = adapter.generate(generate_request)
```

The adapter:

- calls `https://api.deepseek.com/chat/completions`;
- uses OpenAI-compatible `messages`;
- requests JSON output with `response_format = {"type": "json_object"}`;
- normalizes the response into the existing gateway `AdapterResult`;
- fails closed if disabled, credentials are missing, HTTP fails, or output is
  not valid JSON.
- can be enabled through `DEEPSEEK_ENABLED=true` so existing gateway code does
  not need provider-specific edits.

## Slack Implementation Contract

The Slack implementation should consume model output as:

```json
{
  "recommendation": "Short operational Slack draft.",
  "confidence": 0.82,
  "evidenceIds": ["evidence-001"],
  "requiresHumanApproval": true
}
```

Then create a protected action shaped like:

```json
{
  "actionType": "SEND_SLACK_ALERT",
  "approvalId": "approval-...",
  "actionId": "action-...",
  "correlationId": "correlation-...",
  "targetRole": "Operations Manager",
  "messageTitle": "Capacity risk needs review",
  "messageBody": "Normalized gateway draft goes here.",
  "evidenceIds": ["evidence-001"]
}
```

The Slack send remains blocked until approval is present. Missing Slack
credentials should still return an honest `MOCK_SENT` or failure state, not a
fake live delivery.

## Shared Runtime Rule

For collaborator machines, each developer should set their own `.env` or shell
environment. For shared demos, put `DEEPSEEK_ENABLED`, `DEEPSEEK_API_KEY`, and
`DEEPSEEK_MODEL` in the deployment secret store:

- GitHub Actions: repository or environment secret;
- MuleSoft/CloudHub: secure properties;
- Salesforce-facing runtime: Named Credential, External Credential, or the
  gateway service environment;
- local dashboard/dev server: ignored `.env`.

The repository should only contain `.env.example`, setup docs, and code that
reads the environment.

## Verification

Run:

```bash
npm run check:deepseek
npm run check:models
```

The unit tests use a fake transport and do not call DeepSeek or require a real
API key.
