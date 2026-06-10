# Lightning Command Center UI State Contract

Version `1.0.0` defines the mock-backed state consumed by
`c-hfs-relationship-command-center`. The contract keeps rendering independent
from transport so the same component can use fixtures now and governed Apex
services later.

The North Star command center may reuse this component contract while changing
labels and fixtures. The state should describe universal private hospital
operations work for the active demo, not a generic service interruption and not
retail-only work.

## Material States

| State        | Required behavior                                                   |
| ------------ | ------------------------------------------------------------------- |
| `ready`      | Complete synthetic case with permitted approval controls            |
| `restricted` | Same underlying facts with controls removed for the current role    |
| `loading`    | Busy status without stale case content                              |
| `empty`      | No assigned work with a clear next step                             |
| `denied`     | Purpose or permission denial without inaccessible record disclosure |
| `error`      | Recoverable service error with correlation identifier               |

## Ready State

The ready state contains:

- case identity, severity, status, owner, service deadline, and next update;
- affected customer alias, department, location, resources, partners, and
  connected entities;
- blockers and cross-functional ownership;
- chronological source-backed timeline;
- evidence citations and content hashes;
- SOP version, current step, progress, and required evidence;
- recommendation facts, inferences, confidence, and model profile;
- approval policy, current status, and permitted decisions;
- action history and source-system correlation;
- observed outcome and effectiveness state.

North Star hospital ready state should additionally expose:

- patient or visitor alias, never real patient data;
- department and location context;
- bed, room, queue, pharmacy stock, staff, equipment, vendor, and billing risk
  summaries;
- partner response status;
- clinical-decision refusal state when relevant;
- Slack and WhatsApp-style channel delivery status;
- voice/transcript request examples that show interpreted intent, structured
  operations fields, Agentforce recommendation action, protected-action
  blocking, and clinical-decision refusal;
- outcome metrics for wait time, bed release, stockout avoidance, complaint
  containment, billing resolution, vendor SLA, and task completion.

The UI distinguishes source facts from model inference. Consequential controls
emit intent events only; the component never treats a click as completed
external action.

## Live Transport

Live mode calls `HFS_RelationshipController`, which delegates context reads and
approval decisions to `HFS_RelationshipServiceImpl`. The component maps the
frozen Apex DTOs into this UI state and refreshes after a successful decision.
It renders controls only when the server reports the matching capability.

Synthetic fixture mode remains available for deterministic tests and demos.
Live mode is the default.

## Compatibility

Additive optional fields are compatible within `1.0.0`. Renaming required
fields, changing state meanings, or weakening permission-based control
visibility requires a new state version and updated fixture tests.

Verify compatibility with:

```bash
npm run test:unit -- --runTestsByPath force-app/main/default/lwc/hfsRelationshipCommandCenter/__tests__/hfsRelationshipCommandCenter.test.js
```
