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
- the roadmap capability and Beads issue when Beads is available.

For North Star, also define the global primitives involved, the active business
profile, the hospital operations risk, and whether the action is informational,
operational, protected, or refused. Protected hospital actions include vendor
case, pharmacy restock, billing review, insurance follow-up, bed/room task,
Slack alert, WhatsApp-style alert, and staff-task write-back.

### Trace

Define:

- authoritative data sources;
- entities, relationships, events, and evidence;
- public interfaces;
- ownership and dependencies;
- expected failures and recovery.

For North Star, trace the source of each hospital operations signal:

- complaint or service response evidence;
- bed, room, queue, staff, equipment, or capacity record;
- pharmacy or supply position;
- lab, laundry, insurer, payment, food, maintenance, or transport partner
  response;
- billing, refund, claim, or payment review evidence;
- approval, action, channel delivery, and outcome state.

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

- complaint clusters with missing capacity evidence;
- partner response that resolves only one operational dependency;
- pharmacy stock risk with incomplete stock evidence;
- billing approval blocked by missing insurer response;
- staff alert delivery failure;
- manager rejection or modification;
- clinical diagnosis, treatment, dosage, triage, or priority request;
- outcome that does not improve the metric.

## Reasoning And Determinism

Language models may interpret context, compare hypotheses, summarize evidence,
and propose actions.

Code, schemas, policies, formulas, authorization, approval requirements,
idempotency, and audit logging must execute deterministically.

## Improvement Loop

When a failure or better method is discovered:

1. Create or update a Beads issue when Beads is available, otherwise update
   `ROADMAP.md`.
2. Preserve the failing input or test fixture.
3. Fix the deterministic component or clarify the decision rule.
4. Add a regression test.
5. Record the architectural decision if it changes a shared contract.
6. Close the issue only after the relevant checkpoint passes.
