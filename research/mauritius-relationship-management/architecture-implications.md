# Architecture Implications

| Evidence pattern                                                       | Architecture requirement                                                                                                         |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Cases cross departments and customers repeatedly request status        | One work item with a complete history, participants, owner, contributors, deadline, next update, and escalation                  |
| Feedback, employee voice, recognition, and grievance handling are weak | Employee-specific relationship records, follow-up commitments, confidential access, independent routing, and aggregate reporting |
| Qualified workers and employer demand are mismatched                   | Skills, proficiency evidence, role requirements, workload, aspirations, development, and internal opportunity relationships      |
| Conglomerates need alignment and local autonomy                        | Shared types and controls with business-unit-specific SOPs, policies, permissions, and source ownership                          |
| Supplier and entity disruption has cascading effects                   | Typed dependency relationships and impact traversal                                                                              |
| Metrics and evidence are assembled slowly                              | Versioned definitions, provenance, calculated measures, current exceptions, and decision views                                   |
| Digital pilots stall                                                   | Capability checkpoints, early user validation, adoption measures, and visible process ownership                                  |
| Complaint terms and expectations are unclear                           | Agreements, obligations, promises, material terms, and communication evidence                                                    |
| Recommendations are not consistently implemented                       | Recommendation ownership, due dates, status, required evidence, escalation, and verified closure                                 |
| Human interaction remains important                                    | Recommendations and message drafts support responsible people; consequential actions remain controlled                           |
| Privacy and cyber incidents damage trust                               | Purpose, consent, minimization, access, retention, segregation of duties, and incident response                                  |
| Organizations forget what worked                                       | Outcome-linked episodic, semantic, procedural, and outcome memory                                                                |

## Design Principles

1. Preserve source evidence before harmonization.
2. Keep identity confidence visible.
3. Store relationships and events separately.
4. Use effective dates and recorded dates.
5. Make SOPs executable and versioned.
6. Make metrics independently reproducible.
7. Make recommendations explainable and expiring.
8. Require policy and approval checks before actions.
9. Treat outcomes as evidence for future recommendations.
10. Retain contradictions and supersession history.
11. Apply permissions during retrieval, reasoning, and action.
12. Keep local operating authority while sharing semantics and governance.
