public class HFS_EventIntakeCommand {
  @AuraEnabled
  public String contractVersion { get; set; }

  @AuraEnabled
  public String correlationId { get; set; }

  @AuraEnabled
  public String tenantKey { get; set; }

  @AuraEnabled
  public String purpose { get; set; }

  @AuraEnabled
  public String eventId { get; set; }

  @AuraEnabled
  public String sourceUri { get; set; }

  @AuraEnabled
  public String sourceRecordId { get; set; }

  @AuraEnabled
  public String eventType { get; set; }

  @AuraEnabled
  public String subject { get; set; }

  @AuraEnabled
  public String schemaVersion { get; set; }

  @AuraEnabled
  public String idempotencyKey { get; set; }

  @AuraEnabled
  public Decimal sourceSequence { get; set; }

  @AuraEnabled
  public Datetime occurredAt { get; set; }

  @AuraEnabled
  public Datetime observedAt { get; set; }

  @AuraEnabled
  public String contentHash { get; set; }

  @AuraEnabled
  public String payloadJson { get; set; }

  @AuraEnabled
  public String intakeResult { get; set; }

  @AuraEnabled
  public String causationId { get; set; }
}
