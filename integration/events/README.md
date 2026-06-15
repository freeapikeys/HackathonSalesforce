# Event Intake Contract

- `schemas/event-envelope-v1.schema.json` is the executable envelope and
  normalized source-record schema.
- `fixtures/scenario.json` defines ordered inputs and expected intake results.
- `fixtures/events/` contains source-event examples.

Validate from the repository root with `npm run check:events`.

## Logia Fixtures

Logia should add retail source events under the same envelope instead of
creating a separate intake path. Candidate examples:

- stockout risk detected;
- expiry risk detected;
- complaint cluster detected;
- supplier response received;
- queue risk detected;
- approved retail action outcome captured.

Each fixture should preserve product category, selected product, store,
supplier, batch where applicable, and source evidence. Include duplicate,
malformed, late, out-of-order, and replay cases so the retail demo retains the
same governance guarantees as the generic slice.
