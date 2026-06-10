# Agentforce Action Contracts

Version `1.0.0` defines three Agentforce-facing actions:

- explain an accessible relationship case;
- draft an evidence-backed recommendation;
- request a pending human approval.

For North Star, these actions should be presented to Agentforce through retail
topics:

- North Star Orchestration;
- Inventory and Waste;
- Supplier and Product Trust;
- Store Execution and Outreach;
- Manager Approval and Outreach.

The same action boundary also supports private jury-gift scenarios. The
Nexavenu revenue-intelligence fixture uses the recommendation action to return
separate facts, contact-sourced assumptions, inferences, citations, a governed
close plan, and audit state for the Revenue Intelligence and Champion Nurture
Tower.

The actions remain governed. Agentforce can explain a retail case, draft an
evidence-backed recovery recommendation, and request approval. It cannot
directly send Slack, WhatsApp, reorder, markdown, supplier, or store-task
write-backs.

The contract deliberately does not expose protected external execution as an
Agentforce action. The refusal fixture proves that an attempted execution fails
closed and returns no protected facts, evidence, or record identifiers.

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
