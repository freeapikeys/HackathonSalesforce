public interface HFS_RelationshipService {
  HFS_ContextResponse getContext(HFS_ContextRequest request);

  HFS_ProvenanceResponse getProvenance(HFS_ProvenanceRequest request);

  HFS_CommandResult persistEvent(HFS_EventIntakeCommand command);

  HFS_CommandResult storeRecommendation(HFS_RecommendationCommand command);

  HFS_CommandResult requestApproval(HFS_ApprovalRequestCommand command);

  HFS_CommandResult decideApproval(HFS_ApprovalDecisionCommand command);

  HFS_CommandResult logAction(HFS_ActionCommand command);

  HFS_CommandResult captureOutcome(HFS_OutcomeCommand command);
}
