public class HFS_AgentActionResult {
  @InvocableVariable(label='Status' description='SUCCESS, REFUSED, or ERROR.')
  public String status;

  @InvocableVariable(
    label='Summary'
    description='A permission-safe summary of the result.'
  )
  public String summary;

  @InvocableVariable(
    label='Contract Response JSON'
    description='The complete versioned Agentforce action response.'
  )
  public String responseJson;

  @InvocableVariable(
    label='Citation Evidence IDs'
    description='Accessible evidence IDs cited by the response.'
  )
  public List<String> citationEvidenceIds;

  @InvocableVariable(
    label='Model Invocation ID'
    description='The qualified model invocation that produced the recommendation.'
  )
  public String modelInvocationId;

  @InvocableVariable(
    label='Approval ID'
    description='The pending human approval record created by this action.'
  )
  public String approvalId;

  @InvocableVariable(
    label='Refusal Code'
    description='The structured refusal code when status is REFUSED.'
  )
  public String refusalCode;

  @InvocableVariable(
    label='Error Code'
    description='The structured service error code when status is ERROR.'
  )
  public String errorCode;

  @InvocableVariable(
    label='External Action Executed'
    description='Always false. Agentforce cannot execute protected external actions.'
  )
  public Boolean externalActionExecuted;
}
