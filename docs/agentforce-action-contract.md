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

The deployed entry points are:

| Action                              | Apex target                      |
| ----------------------------------- | -------------------------------- |
| `EXPLAIN_RELATIONSHIP_CASE`         | `HFS_AgentExplainAction`         |
| `DRAFT_RELATIONSHIP_RECOMMENDATION` | `HFS_AgentRecommendationAction`  |
| `REQUEST_HUMAN_APPROVAL`            | `HFS_AgentApprovalRequestAction` |

Each action returns typed status, citation, model-invocation, approval,
refusal, error, and external-execution fields. `responseJson` is the canonical
serialized `1.0.0` response and preserves the complete facts, inferences,
citations, recommendation, approval, refusal, error, and audit structure.

The recommendation action returns only a normalized recommendation already
persisted with a qualified provider-neutral model profile and invocation ID.
If no matching result exists, it returns `NO_QUALIFIED_MODEL`; it does not
silently substitute a provider, model, or ungrounded answer.

The approval-request action requires user confirmation in the action catalog.
It creates only a pending approval record and never calls the external action
boundary.

Permission-set access is intentionally narrower than method availability:

- relationship users can explain cases and retrieve qualified recommendations;
- approvers can explain cases and request human approval;
- integration users can invoke all three actions;
- no permission set receives an Agentforce external-execution action because
  no such Apex entry point exists.

## Compatibility

Additive optional response fields are compatible within `1.0.0`. Renaming
inputs or outputs, changing refusal meaning, weakening evidence requirements,
or expanding Agentforce authority requires a new contract version and
cross-lane review.

Verify with:

```bash
npm run check:agentforce
npm run demo:run
```

The connected demo run invokes all three actions against the Salesforce org,
checks that the model invocation ID survives the Agentforce boundary, and
proves that external execution remains blocked until a separate human approval
and MuleSoft transaction.
