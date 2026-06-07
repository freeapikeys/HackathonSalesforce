public class HFS_CommandCenterResponse {
  @AuraEnabled
  public HFS_ContextResponse context { get; set; }

  @AuraEnabled
  public HFS_CommandCenterPermissions permissions { get; set; }

  @AuraEnabled
  public String userLabel { get; set; }
}
