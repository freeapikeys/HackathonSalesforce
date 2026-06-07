# MuleSoft Integration Boundary

The version `1.0.0` Process API contract is generated at
`api/hfs-integration-v1.openapi.json`. It freezes four operations:

- source event ingestion;
- permission-aware relationship context retrieval;
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

The North Star demo should use the same mock runtime to simulate retail source
systems and channels:

- POS and inventory reads;
- expiry and batch records;
- supplier quality case and replacement-batch response;
- reorder, warehouse transfer, markdown, and store-task write-backs;
- Slack staff alert;
- WhatsApp-style urgent staff alert;
- outcome callback.

Use real Slack or WhatsApp credentials only when they are available and safe to
configure. Otherwise the mock runtime should return deterministic channel
delivery records that are clearly presented as demo channel results.

It deliberately keeps adapters behind Python interfaces so the same contract
tests can be applied to Mule flows and real connectors without embedding mock
behavior in production configuration. The runtime is an integration test
harness, not a substitute for an Anypoint deployment.
