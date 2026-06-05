public class HFS_ActionCommand {
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
  public String idempotencyKey { get; set; }

  @AuraEnabled
  public String recommendationId { get; set; }

  @AuraEnabled
  public String approvalId { get; set; }

  @AuraEnabled
  public String targetEntityId { get; set; }

  @AuraEnabled
  public String actionType { get; set; }
}
