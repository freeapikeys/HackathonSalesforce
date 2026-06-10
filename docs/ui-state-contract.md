# Lightning Command Center UI State Contract

Version `1.0.0` defines the mock-backed state consumed by
`c-hfs-relationship-command-center`. The contract keeps rendering independent
from transport so the same component can use fixtures now and governed Apex
services later.

The North Star command center may reuse this component contract while changing
labels and fixtures. The state should describe retail operations work, not a
generic service interruption, when the active demo is North Star.

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
- affected relationship and connected entities;
- blockers, dependencies, handoff state, escalation role, and cross-functional
  ownership;
- chronological source-backed timeline;
- evidence citations and content hashes;
- SOP version, current step, progress, required evidence, and escalation rule;
- recommendation facts, inferences, confidence, and model profile;
- approval policy, current status, and permitted decisions;
- relationship history, participant links, contradictory claims, correction
  state, supersession approval metadata, superseding reviewer, and
  correction-review controls;
- verified closure state when an outcome completes the accountable work item;
- action history and source-system correlation;
- observed outcome and effectiveness state.

North Star ready state should additionally expose:

- selected product and product category;
- store and supplier context;
- inventory, expiry, complaint, supplier, promotion, and queue risk summaries;
- supplier response status;
- Slack and WhatsApp-style channel delivery status;
- outcome metrics for stockout, waste, customer trust, and staff readiness.

The UI distinguishes source facts from model inference. Consequential controls
emit intent events only; the component never treats a click as completed
external action.

## Live Transport

Live mode calls `HFS_RelationshipController`, which delegates context reads and
approval decisions to `HFS_RelationshipServiceImpl`. The controller also accepts
relationship correction-review intents and persists them as governed review work
with pending approval. Approved correction decisions can return relationship
history cards marked as superseded with the approval and reviewer surfaced in
the state. The component maps the frozen Apex DTOs into this UI state and
refreshes after a successful decision or correction-review request. It renders
controls only when the server reports the matching capability.

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
