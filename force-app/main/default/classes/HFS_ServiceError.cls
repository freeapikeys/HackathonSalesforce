public class HFS_ServiceError {
  @AuraEnabled
  public String code { get; set; }

  @AuraEnabled
  public String message { get; set; }

  @AuraEnabled
  public String fieldName { get; set; }

  @AuraEnabled
  public Boolean retryable { get; set; }

  @AuraEnabled
  public String details { get; set; }
}
