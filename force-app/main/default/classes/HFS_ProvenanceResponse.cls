public class HFS_ProvenanceResponse {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public HFS_ContextItem rootRecord { get; set; }

  @AuraEnabled
  public List<HFS_ContextItem> lineage { get; set; }

  @AuraEnabled
  public List<HFS_EvidenceCitation> citations { get; set; }

  @AuraEnabled
  public List<HFS_ServiceError> errors { get; set; }
}
