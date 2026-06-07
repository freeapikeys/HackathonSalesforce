# Agentforce Explanation and Action Contract

## Boundary

Agentforce can ask the product to:

1. explain the current accessible relationship case;
2. draft a grounded recommendation through a qualified model profile;
3. create a pending human approval request.

Agentforce cannot decide the approval or execute a protected external action.
Those operations remain behind the current user's permissions, the Apex
service contract, human approval, and the MuleSoft execution boundary.

## Grounding

Version `1.0.0` returns separate collections for facts and inferences.

- Every fact cites one or more returned accessible evidence identifiers.
- Every inference names its basis facts and confidence from zero to one.
- Every recommendation cites returned evidence, records the logical model
  profile and invocation identifier, and sets `requiresHumanApproval = true`.
- Citations preserve source event, source URI, content hash, and summary.

The action response also preserves tenant, correlation, purpose, actor, agent,
permission evaluation, model invocation, and external-execution audit values.

## Refusal

Refusals are normal structured results, not prompt text.

| Code                    | Meaning                                                      |
| ----------------------- | ------------------------------------------------------------ |
| `INACCESSIBLE_EVIDENCE` | Required source evidence is unavailable to this user/purpose |
| `UNAUTHORIZED_ACTION`   | The requested action is outside Agentforce authority         |
| `PURPOSE_DENIED`        | The declared purpose does not permit the requested access    |
| `NO_QUALIFIED_MODEL`    | No deployment satisfies model routing and data policy        |

Refusal responses contain no facts, inferences, citations, recommendation,
approval, or disclosed record identifiers.

## Salesforce Action Shape

The catalog uses Apex custom-action targets and snake-case developer names.
Implementation classes use one `@InvocableMethod` per action and explicit
`@InvocableVariable` inputs and outputs. Descriptions tell Agentforce when to
invoke the action and what the action does not authorize.

The approval-request action requires user confirmation in the action catalog.
It creates only a pending approval record and never calls the external action
boundary.

## Compatibility

Additive optional response fields are compatible within `1.0.0`. Renaming
inputs or outputs, changing refusal meaning, weakening evidence requirements,
or expanding Agentforce authority requires a new contract version and
cross-lane review.

Verify with:

```bash
npm run check:agentforce
```
