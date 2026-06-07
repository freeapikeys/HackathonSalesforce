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
  public String definitionVersion { get; set; }

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
