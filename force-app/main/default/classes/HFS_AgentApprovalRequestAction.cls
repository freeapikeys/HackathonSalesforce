public with sharing class HFS_AgentApprovalRequestAction {
  @InvocableMethod(
    label='Request Human Approval'
    description='Creates or replays a pending human approval for an existing recommendation. It never decides the approval or performs the protected external action.'
  )
  public static List<HFS_AgentActionResult> invoke(
    List<HFS_AgentActionRequest> requests
  ) {
    return HFS_AgentActionService.requestApproval(requests);
  }
}
