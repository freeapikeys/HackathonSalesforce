public class HFS_CorrectionReviewCommand {
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
  public String sourceRelationshipId { get; set; }

  @AuraEnabled
  public String sourceParticipantId { get; set; }

  @AuraEnabled
  public String targetLabel { get; set; }

  @AuraEnabled
  public String reason { get; set; }
}
