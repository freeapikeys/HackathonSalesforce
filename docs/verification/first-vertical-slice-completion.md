# First Vertical Slice Completion Evidence

## Verification Record

- Date: June 7, 2026
- Source ref: `main`
- Source commit: `2d9891485f4d6ea4125d7537ecffe583bfdd216e`
- Contract version: `1.0.0`
- Salesforce API version: `66.0`
- Tenant fixture: `demo-mauritius`

The completion gate ran with:

```bash
./scripts/verify-clean-clone.sh \
  --target-org dev-ed \
  --ref main \
  --output artifacts/main-clean-clone-result.json
```

The target-org alias identifies local authenticated state and is not a
deployable credential. The generated artifact is ignored by Git; this document
is the durable, identifier-free summary.

## Automated Evidence

The verifier cloned the private repository into a new temporary directory and
performed every setup and execution step without manual Salesforce record
edits.

| Gate                                | Result                         |
| ----------------------------------- | ------------------------------ |
| Locked runtime bootstrap            | Passed                         |
| Repository contract and unit checks | Passed                         |
| Deterministic source-event fixtures | 14 expected outcomes validated |
| MuleSoft contract tests             | 12 passed                      |
| Model gateway tests                 | 9 passed                       |
| End-to-end harness tests            | 7 passed                       |
| Lightning tests                     | 15 passed                      |
| Salesforce metadata deployment      | 199 of 199 components          |
| Apex tests                          | 19 passed, 0 failed            |
| Connected demo                      | 17 of 17 steps                 |

## Governed Failure Evidence

The run proved these material failure paths:

- restricted model data produced `NO_QUALIFIED_DEPLOYMENT` and
  `FAILED_CLOSED`;
- inaccessible evidence produced `INACCESSIBLE_EVIDENCE`;
- Agentforce produced no external action;
- Salesforce rejected action logging before approval with `INVALID_STATE`;
- MuleSoft rejected an unregistered approval with
  `403 PERMISSION_DENIED`.

## Completed Behavior

After human approval, the mock MuleSoft write-back returned `202 QUEUED`. The
resulting source event was ingested and correlated to one action, one outcome,
and one evaluation. Final state was:

- action: `EXECUTED`;
- outcome: `SUCCESS`;
- work item: `COMPLETED`.

Final tenant-scoped counts were:

| Object            | Count |
| ----------------- | ----: |
| Event             |     2 |
| Entity            |     3 |
| Event participant |     3 |
| Relationship      |     2 |
| Agreement         |     1 |
| Work item         |     1 |
| SOP execution     |     1 |
| Evidence          |     2 |
| Recommendation    |     1 |
| Approval          |     1 |
| Action            |     1 |
| Outcome           |     1 |
| Evaluation        |     1 |

This checkpoint proves the first synthetic vertical slice and its governance
boundaries. It does not claim production readiness, real-source certification,
or completion of the wider capability roadmap.

## North Star Follow-Up

This document remains historical evidence for the generic HFS foundation. The
North Star demo requires a separate verification record after the retail
vertical slice passes. That record should include product-category-neutral
seed data, supplier-response behavior, Slack and WhatsApp-style channel
results, and retail outcome metrics.
