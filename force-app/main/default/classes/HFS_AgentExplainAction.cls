public with sharing class HFS_AgentExplainAction {
  @InvocableMethod(
    label='Explain Relationship Case'
    description='Returns permission-aware facts, inferences, and evidence citations for a relationship work item. It never performs an external action.'
  )
  public static List<HFS_AgentActionResult> invoke(
    List<HFS_AgentActionRequest> requests
  ) {
    return HFS_AgentActionService.explain(requests);
  }
}
