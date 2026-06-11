public class HFS_EvidenceCitation {
  @AuraEnabled
  public String evidenceId { get; set; }

  @AuraEnabled
  public String evidenceType { get; set; }

  @AuraEnabled
  public String sourceEventId { get; set; }

  @AuraEnabled
  public String sourceUri { get; set; }

  @AuraEnabled
  public String contentHash { get; set; }

  @AuraEnabled
  public String summary { get; set; }

  @AuraEnabled
  public Datetime capturedAt { get; set; }
}
