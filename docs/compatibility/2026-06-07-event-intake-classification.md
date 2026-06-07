# Event Intake Classification Compatibility

## Change

The MuleSoft reference runtime now uses the same stateful classifier as the
versioned event fixture validator.

This is an implementation correction within contract version `1.0.0`; no
OpenAPI field, required input, error code, or idempotency scope changed.

## Client Impact

Clients must continue to handle every `EventIntakeResponse.intakeResult`
already declared by the contract:

- `ACCEPTED`;
- `DUPLICATE`;
- `ACCEPTED_LATE`;
- `ACCEPTED_OUT_OF_ORDER`;
- `CONFLICT_REVIEW`.

Schema, hash, and idempotency rejections continue to use the existing `422`
and `409` error responses. Their optional `ServiceError.details` value now
contains the exact deterministic intake disposition.

Exact source replay compares canonical event `data` under the documented
tenant, source, and idempotency-key scope. Transport metadata such as a new
CloudEvents occurrence ID or observation timestamp does not turn an otherwise
identical source retry into a conflict.

## Verification

```bash
npm run check:events
npm run check:mulesoft
```

The shared matrix executes all 14 versioned fixtures through the classifier
and MuleSoft reference path.
