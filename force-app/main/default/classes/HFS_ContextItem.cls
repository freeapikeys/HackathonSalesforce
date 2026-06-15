public class HFS_ContextItem {
  @AuraEnabled
  public String recordId { get; set; }

  @AuraEnabled
  public String objectApiName { get; set; }

  @AuraEnabled
  public String externalKey { get; set; }

  @AuraEnabled
  public String recordType { get; set; }

  @AuraEnabled
  public String label { get; set; }

  @AuraEnabled
  public String status { get; set; }

  @AuraEnabled
  public String summary { get; set; }

  @AuraEnabled
  public Datetime occurredAt { get; set; }

  @AuraEnabled
  public String sourceEventId { get; set; }

  @AuraEnabled
  public String subjectEntityId { get; set; }

  @AuraEnabled
  public String objectEntityId { get; set; }

  @AuraEnabled
  public String relationshipType { get; set; }

  @AuraEnabled
  public String participantRole { get; set; }

  @AuraEnabled
  public Decimal confidence { get; set; }

  @AuraEnabled
  public String sourceUri { get; set; }

  @AuraEnabled
  public String contentHash { get; set; }

  @AuraEnabled
  public String ownerLabel { get; set; }

  @AuraEnabled
  public Datetime dueAt { get; set; }

  @AuraEnabled
  public String blockedReason { get; set; }

  @AuraEnabled
  public String targetRelationshipId { get; set; }

  @AuraEnabled
  public String dependsOnWorkItemId { get; set; }

  @AuraEnabled
  public String ownerRole { get; set; }

  @AuraEnabled
  public String escalationRole { get; set; }

  @AuraEnabled
  public String handoffTargetRole { get; set; }

  @AuraEnabled
  public String handoffState { get; set; }

  @AuraEnabled
  public String closureVerificationStatus { get; set; }

  @AuraEnabled
  public Datetime closureVerifiedAt { get; set; }

  @AuraEnabled
  public String closureOutcomeId { get; set; }

  @AuraEnabled
  public String supersededByRelationshipId { get; set; }

  @AuraEnabled
  public String supersessionApprovalId { get; set; }

  @AuraEnabled
  public String supersededByUserId { get; set; }

  @AuraEnabled
  public Datetime supersededAt { get; set; }

  @AuraEnabled
  public String supersessionReason { get; set; }

  @AuraEnabled
  public String definitionVersion { get; set; }

  @AuraEnabled
  public String requiredEvidence { get; set; }

  @AuraEnabled
  public String escalationRule { get; set; }

  @AuraEnabled
  public String proposedActionType { get; set; }

  @AuraEnabled
  public String primaryEvidenceId { get; set; }

  @AuraEnabled
  public String modelProfile { get; set; }

  @AuraEnabled
  public String modelInvocationId { get; set; }

  @AuraEnabled
  public Datetime requestedAt { get; set; }

  @AuraEnabled
  public Datetime decidedAt { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String externalReference { get; set; }

  @AuraEnabled
  public String metricKey { get; set; }

  @AuraEnabled
  public Decimal metricValue { get; set; }
}
