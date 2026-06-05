public class HFS_CommandResult {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String operation { get; set; }

  @AuraEnabled
  public Boolean success { get; set; }

  @AuraEnabled
  public Boolean replayed { get; set; }

  @AuraEnabled
  public String recordId { get; set; }

  @AuraEnabled
  public String recordType { get; set; }

  @AuraEnabled
  public String status { get; set; }

  @AuraEnabled
  public List<HFS_ServiceError> errors { get; set; }
}
