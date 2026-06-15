# Event Replay Compatibility

## Change

Contract version `1.0.0` adds:

- `POST /v1/events/replays`;
- `EventReplayRequest`;
- `EventReplayResponse`;
- `REPLAY_EVENT` completion callbacks.

The operation is additive. Existing event-ingestion requests and responses are
unchanged.

## Invariants

- Only attempts in `QUARANTINED` state can be replayed.
- Purpose `REPLAY_QUARANTINED_EVENT` must be authorized.
- The request contains a complete corrected event envelope.
- A replay creates a new attempt linked by `originalAttemptId`.
- Replay idempotency is scoped separately from source-event idempotency.
- Exact replay returns the prior result without a second intake attempt.
- Reusing a replay key for changed content returns `IDEMPOTENCY_CONFLICT`.
- The original attempt is never changed.

## Verification

```bash
npm run check:events
npm run check:mulesoft
```

The contract contains five operations and 35 executable examples. Runtime
tests cover authorization, malformed-event quarantine, retry exhaustion,
linked replay, permanent rejection, exact replay, and replay-key conflict.

Logia should use this replay path for corrected retail source events, such
as malformed complaint clusters, corrected supplier responses, or late
inventory events. Replays must never overwrite the original retail intake
attempt.
