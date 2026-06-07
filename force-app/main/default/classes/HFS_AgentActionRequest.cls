public class HFS_AgentActionRequest {
  @InvocableVariable(
    label='Contract Version'
    description='The HFS Agentforce action contract version. Use 1.0.0.'
    required=true
  )
  public String contractVersion;

  @InvocableVariable(
    label='Action'
    description='The requested HFS Agentforce action name.'
    required=true
  )
  public String action;

  @InvocableVariable(
    label='Tenant Key'
    description='The tenant boundary for every record read or written.'
    required=true
  )
  public String tenantKey;

  @InvocableVariable(
    label='Correlation ID'
    description='A stable correlation identifier for tracing and replay.'
    required=true
  )
  public String correlationId;

  @InvocableVariable(
    label='Purpose'
    description='The declared business purpose for this access.'
    required=true
  )
  public String purpose;

  @InvocableVariable(
    label='Work Item ID'
    description='The Salesforce ID of the relationship work item.'
    required=true
  )
  public String workItemId;

  @InvocableVariable(
    label='Recommendation ID'
    description='The existing recommendation to route for human approval.'
  )
  public String recommendationId;

  @InvocableVariable(
    label='Approval Policy Key'
    description='The named policy that governs the human approval.'
  )
  public String approvalPolicyKey;

  @InvocableVariable(
    label='Desired Outcome'
    description='The business outcome the recommendation should support.'
  )
  public String desiredOutcome;

  @InvocableVariable(
    label='Model Profile'
    description='The provider-neutral qualified model profile.'
  )
  public String modelProfile;
}
