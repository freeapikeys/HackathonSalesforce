public class HFS_ContextRequest {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public String workItemId { get; set; }

  @AuraEnabled
  public String subjectEntityId { get; set; }

  @AuraEnabled
  public String purpose { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public Boolean includeProvenance { get; set; }

  @AuraEnabled
  public Integer timelineLimit { get; set; }
}
