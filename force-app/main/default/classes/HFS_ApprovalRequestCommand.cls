public class HFS_ApprovalRequestCommand {
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
  public String recommendationId { get; set; }

  @AuraEnabled
  public String policyKey { get; set; }
}
