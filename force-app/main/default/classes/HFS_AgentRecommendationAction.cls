public with sharing class HFS_AgentRecommendationAction {
  @InvocableMethod(
    label='Draft Relationship Recommendation'
    description='Returns an evidence-backed recommendation from a qualified provider-neutral model profile. It fails closed when no qualified result is available and never executes the recommendation.'
  )
  public static List<HFS_AgentActionResult> invoke(
    List<HFS_AgentActionRequest> requests
  ) {
    return HFS_AgentActionService.recommend(requests);
  }
}
