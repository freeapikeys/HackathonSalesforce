# Agentforce Action Contracts

Version `1.0.0` defines three Agentforce-facing actions:

- explain an accessible relationship case;
- draft an evidence-backed recommendation;
- request a pending human approval.

The contract deliberately does not expose protected external execution as an
Agentforce action. The refusal fixture proves that an attempted execution fails
closed and returns no protected facts, evidence, or record identifiers.

Regenerate and verify:

```bash
python3 scripts/generate_agentforce_contract.py
npm run check:agentforce
```

The action catalog uses `apex://` targets and developer names compatible with
Salesforce custom actions. The implementation bead adds the corresponding
`@InvocableMethod` classes.
