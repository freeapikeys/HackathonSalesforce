public class HFS_RecommendationCommand {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public String purpose { get; set; }

  @AuraEnabled
  public String externalKey { get; set; }

  @AuraEnabled
  public String workItemId { get; set; }

  @AuraEnabled
  public String subjectEntityId { get; set; }

  @AuraEnabled
  public String primaryEvidenceId { get; set; }

  @AuraEnabled
  public String recommendationType { get; set; }

  @AuraEnabled
  public String proposedActionType { get; set; }

  @AuraEnabled
  public String rationale { get; set; }

  @AuraEnabled
  public Decimal confidence { get; set; }

  @AuraEnabled
  public String modelProfile { get; set; }

  @AuraEnabled
  public String modelInvocationId { get; set; }
}
