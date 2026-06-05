public class HFS_ApprovalDecisionCommand {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public String purpose { get; set; }

  @AuraEnabled
  public String approvalId { get; set; }

  @AuraEnabled
  public String decisionStatus { get; set; }

  @AuraEnabled
  public String decisionNotes { get; set; }
}
