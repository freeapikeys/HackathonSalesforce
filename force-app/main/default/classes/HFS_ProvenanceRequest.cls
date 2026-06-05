public class HFS_ProvenanceRequest {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public String objectApiName { get; set; }

  @AuraEnabled
  public String recordId { get; set; }

  @AuraEnabled
  public String purpose { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public Integer maxDepth { get; set; }
}
