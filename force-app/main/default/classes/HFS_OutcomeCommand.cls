public class HFS_OutcomeCommand {
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
  public String actionId { get; set; }

  @AuraEnabled
  public String sourceEventId { get; set; }

  @AuraEnabled
  public String outcomeType { get; set; }

  @AuraEnabled
  public String status { get; set; }

  @AuraEnabled
  public Datetime observedAt { get; set; }

  @AuraEnabled
  public String summary { get; set; }

  @AuraEnabled
  public String metricKey { get; set; }

  @AuraEnabled
  public Decimal metricValue { get; set; }
}
