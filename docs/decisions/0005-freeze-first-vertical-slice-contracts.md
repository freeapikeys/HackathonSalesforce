# 0005: Freeze First Vertical Slice Contracts at Version 1.0.0

Status: Accepted

## Decision

The first vertical slice uses version `1.0.0` for the Apex service, MuleSoft
API, model gateway, and Lightning UI state contracts.

Cross-lane requests preserve:

- `tenantKey` as the business tenant identifier;
- `correlationId` as the end-to-end operation identifier;
- `purpose` as the declared reason for access or action;
- named operations and error codes from the Apex service contract;
- human approval before protected external action.

The MuleSoft transport header `X-Tenant-Id` carries the same value as
`tenantKey`; it is not a second tenant identifier.

## Reason

All four lanes now have versioned examples and executable checks. Freezing the
shared names lets implementation continue independently without silently
changing identity, authorization, approval, or audit semantics.

## Compatibility Checks

| Lane         | Command                                                                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Core         | `sf apex run test --tests HFS_ServiceContractTest,HFS_RelationshipServiceImplTest --target-org dev-ed --wait 20 --result-format human`         |
| Integration  | `npm run check:mulesoft`                                                                                                                       |
| Intelligence | `npm run check:models`                                                                                                                         |
| Experience   | `npm run test:unit -- --runTestsByPath force-app/main/default/lwc/hfsRelationshipCommandCenter/__tests__/hfsRelationshipCommandCenter.test.js` |
| Repository   | `npm run check`                                                                                                                                |

## Consequences

- Incompatible changes require a new contract version, a compatibility note,
  updated examples and tests, and review from every affected lane.
- Additive optional fields remain compatible when they do not weaken
  authorization, approval, provenance, or routing policy.
- Provider, source-system, and user-interface implementation details remain
  behind these contracts.
- Logia should first specialize data, fixtures, action payloads, and UI
  state behind version `1.0.0`. Create a new contract version only if the retail
  demo requires renamed fields, new required inputs, weakened approvals, or
  changed authorization semantics.
