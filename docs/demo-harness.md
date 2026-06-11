# Synthetic Demo Harness

The harness validates prerequisites, resets only the `demo-mauritius` tenant,
loads one deterministic operations case, verifies every object count and stable
external key, and emits a versioned JSON result.

For `demo:seed` and `demo:run`, the harness first assigns the current connected
Salesforce user the `HFS_Approver` and `HFS_Integration_User` permission sets.
That keeps execute-anonymous seeding aligned with object and field-level
permissions before the seed script compiles.

For North Star, the harness should evolve from the existing foundation case into
one deterministic private hospital operations case. The seed should include
patient/visitor complaints, resource/capacity evidence, pharmacy stock, partner
responses, billing/insurance evidence, staffing evidence, and approval context.

`demo:seed` stops at the review state used by the Lightning command center.
`demo:run` continues through the complete governed vertical slice:

1. route a recommendation through the provider-neutral model gateway;
2. prove a restricted model route fails closed;
3. persist the normalized recommendation with its model invocation ID;
4. read grounded citations and the recommendation through Agentforce actions;
5. prove the Agentforce recommendation includes complaint, resource, capacity,
   partner, billing, stock, staffing, and approval context coverage;
6. create a pending human approval through Agentforce;
7. prove a clinical treatment-priority request is refused before storage;
8. prove Salesforce refuses action logging before approval;
9. record the human approval and log five pending operational task actions plus
   pending Slack and WhatsApp-style channel actions;
10. prove MuleSoft refuses an unregistered approval;
11. execute approved Slack and WhatsApp-style mock write-backs and preserve
    correlation;
12. ingest the resulting source events and capture two channel-delivery
    outcomes plus six business outcomes in Salesforce;
13. evaluate the defined outcomes;
14. refresh the Lightning controller and verify completed state;
15. re-read Agentforce recommendation context and prove outcome and metric
    coverage are now present;
16. re-read direct Apex context and prove the final graph still includes the
    customer alias, department/location, resources, partner, process, evidence,
    recommendation, approval, actions, outcomes, and outcome metrics.

North Star hospital assertions:

- the case uses global primitives, not one-off hospital-only objects;
- patient/visitor aliases contain no real personal or medical data;
- complaint evidence is evaluated with capacity, partner, billing, stock, and
  staffing evidence;
- clinical decision requests are refused;
- manager approval is required before protected write-back;
- service, bed-cleaning, pharmacy, lab, and billing task actions are mapped to
  approved Salesforce action records;
- task action results preserve owner role alias, escalation role alias,
  priority rank, urgency, risk class, approval requirement, service window, and
  missed-task escalation window;
- Slack and WhatsApp-style internal alerts are recorded after approved
  execution;
- outcome metrics include wait time reduced, complaint contained, rooms
  released, stockout avoided, billing issue routed, vendor SLA escalated, and
  channel delivery.

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
npm run demo:run -- --target-org hfs-dev
```

Write the same machine-readable result to an ignored artifact:

```bash
node scripts/run-python-task.mjs harness run \
  --target-org hfs-dev \
  --output artifacts/demo-harness-result.json
```

To verify a pushed repository ref from a new temporary clone, including
dependency bootstrap, Salesforce deployment, Apex tests, connected behavior,
and sanitized completion evidence, follow
[the clean-clone completion runbook](clean-clone-runbook.md).

`demo:seed` always resets the scoped tenant before inserting data. Running it
repeatedly therefore produces the same counts and external keys without
touching records from another tenant.

The seed report includes the Salesforce IDs for
`work-north-star-hospital-surge-001`,
`recommendation-north-star-hospital-001`, and
`approval-north-star-hospital-001`. The connected report also includes the
hospital Slack and WhatsApp-style action, outcome, and evaluation IDs, and the
final action count includes five Salesforce task action records plus two
channel action records. The report also includes the model deployment, profile,
policy, and invocation versions used by the run.

Configure the Lightning command center with:

- tenant key: `demo-mauritius`;
- work item ID: the report's `workItemId`;
- purpose: `RESOLVE_HOSPITAL_OPERATION_RISK`;
- synthetic demo data: disabled.

## Connected Invariants

The connected report must show:

- `NO_QUALIFIED_DEPLOYMENT` and `FAILED_CLOSED` for restricted model data;
- `INACCESSIBLE_EVIDENCE` for a transient work item with no evidence;
- Agentforce citations and the same model invocation ID that was persisted;
- Agentforce recommendation coverage includes complaint, resource, capacity,
  partner, billing, stock, staffing, approval, and post-outcome context;
- `CLINICAL_DECISION_REFUSED` with zero stored clinical recommendations;
- `externalActionExecuted = false` for Agentforce;
- `INVALID_STATE` before human approval in Salesforce;
- `403 PERMISSION_DENIED` for an unregistered MuleSoft approval;
- five approved task action records, two approved channel actions, eight
  correlated outcomes, and eight evaluations;
- task routing includes the required owner aliases, escalation aliases,
  deterministic priority ranks, approval requirement, service windows, and
  missed-task escalation windows before service-window loss;
- direct Apex final context includes the global primitive records, hospital
  evidence types, approved action types, Slack/WhatsApp-style delivery outcomes,
  business outcomes, and metric keys;
- final channel action statuses `EXECUTED`, task action statuses `EXECUTED`,
  and work item status `COMPLETED`;
- Lightning controller permissions and refreshed final context.

## Failure Behavior

The process exits nonzero and still emits a JSON report when a required tool,
org connection, contract check, model route, Agentforce action, approval,
MuleSoft write-back, Apex fixture, count, or identifier fails. No credentials,
access tokens, command logs, usernames, org details, local Salesforce state,
real patient data, or medical records are written to the report.
