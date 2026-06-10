# MuleSoft Integration Boundary

The version `1.0.0` Process API contract is generated at
`api/hfs-integration-v1.openapi.json`. It freezes these operations:

- source event ingestion;
- authorized event replay;
- permission-aware context retrieval;
- approved action execution;
- outcome callback capture.

Every operation preserves tenant and correlation identifiers, uses the stable
service error envelope, and includes request, success, denial, conflict,
validation, retryable-failure, and callback examples. Protected source-system
actions require an approval identifier and are accepted for execution rather
than performed inside the Salesforce logging transaction.

OAuth 2.0 client credentials and mutual TLS are both required. The optional
`X-Callback-Url` header requests a signed completion callback; it does not
weaken the synchronous response or retry contract.

Run:

```bash
npm run check:mulesoft
```

The generator keeps the OpenAPI document and example catalog deterministic.
Edit `scripts/generate_mulesoft_contract.py`, regenerate, and commit both
generated JSON files.

## Mock Runtime

`mock_runtime/` is the replaceable local reference implementation behind the
frozen API. It preserves accepted source events, reads seeded context, executes
only registered approved actions, writes deterministic mock source records,
captures correlated outcomes, and retries optional completion callbacks.

Event ingestion shares its stateful classifier with the versioned event
fixtures. The mock therefore exposes the same accepted, duplicate, late,
out-of-order, conflict-review, schema-rejection, hash-rejection, and
idempotency-conflict behavior that Mule flows must preserve.

The generated contract also exposes `POST /v1/events/replays`. The reference
runtime records immutable intake attempts, retries temporary source-store
failures, quarantines exhausted or correctable failures, authorizes replay by
purpose, and links each replay attempt to its original audit record.

## North Star Mock Actions

The active North Star demo uses the same mock runtime to simulate private
hospital operations systems and channels:

- patient-service tasks;
- bed cleaning and discharge-room release tasks;
- lab, laundry, insurer, payment, food, maintenance, transport, and equipment
  partner escalations;
- pharmacy or supply restock requests;
- billing review and insurance follow-up;
- Slack staff alert;
- WhatsApp-style urgent staff alert;
- hospital outcome callback.

Use real Slack or WhatsApp credentials only when they are available and safe to
configure. Otherwise the mock runtime should return deterministic channel
delivery records that are clearly presented as demo channel results.

The runtime deliberately keeps adapters behind Python interfaces so the same
contract tests can be applied to Mule flows and real connectors without
embedding mock behavior in production configuration. The runtime is an
integration test harness, not a substitute for an Anypoint deployment.

## Slack Alert Path

Slack is modeled as the protected action type `SEND_SLACK_ALERT` behind
`EXECUTE_APPROVED_ACTION`. In the local reference runtime, an approved Slack
action validates the role, target channel, message, evidence IDs, and source
recommendation before producing a channel delivery record.

Use `SLACK_WEBHOOK_URL` only as a local or Anypoint secure property. If it is
configured, the runtime posts the approved message to the webhook and records
`SENT`. If it is missing, the runtime records `MOCK_SENT` with
`provider = mock-slack` and a fallback reason. Unapproved Slack actions are
denied before payload execution, and malformed Slack payloads return
`VALIDATION_FAILED`.

For an Anypoint build, keep the same Process API boundary and implement the
Slack write-back as a Mule flow or connector-backed adapter behind
`POST /v1/actions/executions`. Store the webhook URL in Anypoint secure
configuration, never in Git.

## Clinical Boundary

The MuleSoft boundary must not expose actions for diagnosis, treatment, dosage,
triage, or clinical priority decisions. If a request attempts to execute one of
those actions, the correct result is denial or validation failure with a safe
manager/clinician routing message.
