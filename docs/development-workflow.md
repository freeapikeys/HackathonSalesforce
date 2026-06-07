# Development Workflow

This project adapts the useful parts of the local Atlas and GOTCHA material
without making that personal framework a dependency.

## Five Checkpoints

### Architect

Define:

- the problem being resolved;
- the user or role;
- the measurable result;
- constraints and permissions;
- the roadmap capability and Beads issue.

For North Star, also define the selected product category, store role, business
risk, and whether the action is informational, operational, or protected.
Protected retail actions include reorder, supplier case, markdown, warehouse
transfer, Slack alert, WhatsApp-style alert, and staff-task write-back.

### Trace

Define:

- authoritative data sources;
- entities, relationships, events, and evidence;
- public interfaces;
- ownership and dependencies;
- expected failures and recovery.

For North Star, trace the source of each retail signal:

- POS sales or promotion history;
- inventory, shelf, backroom, warehouse, batch, and expiry record;
- customer complaint or refund evidence;
- supplier response or delivery record;
- staff roster or task state;
- channel delivery result.

### Link

Validate before broad implementation:

- credentials and environments;
- API availability and response shape;
- Salesforce permissions and licenses;
- MuleSoft connectivity;
- synthetic fixtures;
- test and deployment commands.

For North Star, validate whether Slack and WhatsApp are real configured channels
or mocked channel results. Do not write docs or demo scripts that imply a live
channel exists when the current implementation uses the mock runtime.

### Assemble

Implement the smallest complete vertical behavior. Prefer existing Salesforce
and MuleSoft capabilities and established repository patterns.

### Stress-Test

Test:

- normal behavior;
- malformed, missing, duplicate, late, and conflicting data;
- permission denial;
- retries and partial failure;
- evidence and audit history;
- user acceptance and roadmap completion gates.

For North Star, stress-test:

- complaints without supplier response;
- supplier response that resolves only one batch;
- selected product category changes;
- reorder recommendation blocked by quality evidence;
- staff alert delivery failure;
- manager rejection or modification;
- outcome that does not improve the metric.

## Reasoning and Determinism

Language models may interpret context, compare hypotheses, summarize evidence,
and propose actions.

Code, schemas, policies, formulas, authorization, approval requirements,
idempotency, and audit logging must execute deterministically.

## Improvement Loop

When a failure or better method is discovered:

1. Create or update a Beads issue.
2. Preserve the failing input or test fixture.
3. Fix the deterministic component or clarify the decision rule.
4. Add a regression test.
5. Record the architectural decision if it changes a shared contract.
6. Close the issue only after the relevant checkpoint passes.
