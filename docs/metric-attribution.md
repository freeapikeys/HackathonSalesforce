# Metric Attribution

C05 starts with a versioned metric catalog and deterministic verifier:

```bash
npm run check:metrics
```

The verifier reads `analytics/metrics/metric-definitions-v1.json`, loads the
named source-event fixtures, recalculates each example value, and emits the
source event ID, correlation ID, source record ID, content hash, displayed
value, and metric value.

Every metric definition must name:

- metric key, label, description, value type, unit, and direction;
- formula and calculation type;
- time window;
- attribution method, source event type, source event code, rule, and known
  limitations;
- at least one fixture-backed example with an expected value.

The first metric examples prove two patterns:

- direct numeric outcome attribution from typed source attributes;
- derived outcome attribution from structured fixture text.

This is still an MVP measurement layer. Production-grade reporting should move
every derived metric input into typed source attributes or reconciled ledgers
before using it for regulated financial, HR, or customer reporting.
