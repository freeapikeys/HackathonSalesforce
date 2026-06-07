# Synthetic Demo Harness

The harness validates prerequisites, resets only the `demo-mauritius` tenant,
loads one deterministic relationship case, verifies every object count and
stable external key, reads the graph through the governed Apex context service,
and emits a versioned JSON result.

## Commands

```bash
npm run demo:check
npm run demo:reset
npm run demo:seed
npm run demo:verify
npm run demo:run
```

Pass another authenticated org alias with:

```bash
python3 scripts/e2e_harness.py run --target-org hfs-dev
```

Write the same machine-readable result to an ignored artifact:

```bash
python3 scripts/e2e_harness.py run \
  --target-org hfs-dev \
  --output artifacts/demo-harness-result.json
```

`demo:seed` always resets the scoped tenant before inserting data. Running it
repeatedly therefore produces the same counts and external keys without
touching records from another tenant.

The successful report includes the Salesforce IDs for `work-demo-001`,
`recommendation-demo-001`, and `approval-demo-001`. Configure the Lightning
command center with:

- tenant key: `demo-mauritius`;
- work item ID: the report's `workItemId`;
- purpose: `RELATIONSHIP_SERVICE`;
- synthetic demo data: disabled.

## Failure Behavior

The process exits nonzero and still emits a JSON report when a required tool,
org connection, contract check, Apex fixture, count, or identifier fails. No
credentials, access tokens, org details, or local Salesforce state are written
to the report.
