public class HFS_AuthorizationPolicy {
  @AuraEnabled
  public String operation { get; set; }

  @AuraEnabled
  public String sharingMode { get; set; }

  @AuraEnabled
  public String dataAccessMode { get; set; }

  @AuraEnabled
  public String transactionBoundary { get; set; }

  @AuraEnabled
  public Boolean externalCalloutAllowed { get; set; }

  @AuraEnabled
  public List<String> allowedBaselineRoles { get; set; }

  @AuraEnabled
  public List<String> readableObjects { get; set; }

  @AuraEnabled
  public List<String> creatableObjects { get; set; }

  @AuraEnabled
  public List<String> updatableObjects { get; set; }

  @AuraEnabled
  public List<String> readableFields { get; set; }

  @AuraEnabled
  public List<String> writableFields { get; set; }

  @AuraEnabled
  public List<String> customPermissions { get; set; }
}
