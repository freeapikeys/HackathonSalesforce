public class HFS_ContextItem {
  @AuraEnabled
  public String recordId { get; set; }

  @AuraEnabled
  public String objectApiName { get; set; }

  @AuraEnabled
  public String externalKey { get; set; }

  @AuraEnabled
  public String recordType { get; set; }

  @AuraEnabled
  public String label { get; set; }

  @AuraEnabled
  public String status { get; set; }

  @AuraEnabled
  public String summary { get; set; }

  @AuraEnabled
  public Datetime occurredAt { get; set; }

  @AuraEnabled
  public String sourceEventId { get; set; }

  @AuraEnabled
  public String subjectEntityId { get; set; }

  @AuraEnabled
  public String objectEntityId { get; set; }

  @AuraEnabled
  public String relationshipType { get; set; }

  @AuraEnabled
  public String participantRole { get; set; }

  @AuraEnabled
  public Decimal confidence { get; set; }

  @AuraEnabled
  public String sourceUri { get; set; }

  @AuraEnabled
  public String contentHash { get; set; }
}
