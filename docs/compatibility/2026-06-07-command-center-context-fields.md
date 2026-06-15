# Command Center Context Field Extension

Date: 2026-06-07

Affected contracts: Apex service `1.0.0`, Lightning UI state `1.0.0`

## Change

`HFS_ContextItem` adds nullable fields for values already present on accessible
Salesforce records:

- work owner, deadline, and blocker;
- SOP definition version;
- recommendation action type, model profile, and invocation;
- approval request and decision times;
- action correlation and external reference;
- outcome metric key and value.

`HFS_RelationshipController` exposes the frozen context and approval service to
the Lightning command center and returns effective server-side capabilities.

## Compatibility

The change is additive. Existing consumers can ignore the new fields. Request
requirements, error codes, authorization rules, and transaction boundaries do
not change.

Logia can use these nullable context fields for product risk, supplier
status, action correlation, channel result, and outcome display as long as
required inputs and authorization semantics remain unchanged.

Verify with:

```bash
npm run check
sf project deploy start --dry-run --source-dir force-app --target-org dev-ed --test-level RunSpecifiedTests --tests HFS_ServiceContractTest --tests HFS_RelationshipServiceImplTest --tests HFS_RelationshipControllerTest --wait 20
```
