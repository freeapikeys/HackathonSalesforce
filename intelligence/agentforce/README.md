# Agentforce Action Contracts

Version `1.0.0` defines three Agentforce-facing actions:

- explain an accessible North Star operations case;
- draft an evidence-backed operations recommendation;
- request a pending human approval.

For North Star, these actions should be presented to Agentforce through the
global operating model and the private hospital demo topics:

- North Star Orchestration;
- Evidence and Context;
- Patient Trust;
- Resource and Capacity;
- Operations Execution;
- Partner and Vendor;
- Risk and Approval;
- Financial Impact;
- Communication;
- Outcome Learning.

The actions remain governed. Agentforce can explain a hospital operations case,
draft an evidence-backed action recommendation, and request approval. It
cannot directly send Slack, WhatsApp-style alerts, pharmacy restock, lab/vendor,
billing, room/bed, staff-task, patient-message, or outcome write-backs.

The contract deliberately does not expose protected external execution as an
Agentforce action. The refusal fixture proves that an attempted execution fails
closed and returns no protected facts, evidence, or record identifiers.

The fixture set preserves the completed inventory/waste reasoning scenarios as
compatibility coverage, then adds the active hospital demo path:

- `hospital-operations-action-plan` combines complaints, bed capacity,
  outpatient queue pressure, staff coverage, pharmacy stock, lab partner delay,
  billing exposure, expected outcomes, and clinical-decision blocking;
- `hospital-missing-capacity-evidence` proves the agent names missing room,
  queue, and staffing evidence instead of inventing bed-release impact;
- `hospital-clinical-refusal` proves treatment-priority requests are routed to
  clinician review and not answered by Agentforce.

Regenerate and verify:

```bash
python3 scripts/generate_agentforce_contract.py
npm run check:agentforce
```

The action catalog uses `apex://` targets and developer names compatible with
Salesforce custom actions. The corresponding `@InvocableMethod` classes are
under `force-app/main/default/classes/`. They delegate to the governed Apex
service, return only accessible citations, preserve model invocation
provenance, and can create only a pending human approval.
