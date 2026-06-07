public class HFS_CommandCenterPermissions {
  @AuraEnabled
  public Boolean canApprove { get; set; }

  @AuraEnabled
  public Boolean canModify { get; set; }

  @AuraEnabled
  public Boolean canReject { get; set; }

  @AuraEnabled
  public Boolean canExecute { get; set; }
}
