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

### Trace

Define:

- authoritative data sources;
- entities, relationships, events, and evidence;
- public interfaces;
- ownership and dependencies;
- expected failures and recovery.

### Link

Validate before broad implementation:

- credentials and environments;
- API availability and response shape;
- Salesforce permissions and licenses;
- MuleSoft connectivity;
- synthetic fixtures;
- test and deployment commands.

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
