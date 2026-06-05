public class HFS_ContextResponse {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public Datetime generatedAt { get; set; }

  @AuraEnabled
  public HFS_ContextItem workItem { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> entities { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> relationships { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> agreements { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> sopExecutions { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> timeline { get; set; }

  @AuraEnabled
  public List<HFS_EvidenceCitation> evidence { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> recommendations { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> approvals { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> actions { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> outcomes { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> evaluations { get; set; }

  @AuraEnabled
  public List<HFS_ServiceError> errors { get; set; }
}
