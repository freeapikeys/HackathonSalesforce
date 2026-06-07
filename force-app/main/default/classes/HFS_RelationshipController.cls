public with sharing class HFS_RelationshipController {
  @AuraEnabled(cacheable=true)
  public static HFS_CommandCenterResponse loadCommandCenter(
    HFS_ContextRequest request
  ) {
    HFS_CommandCenterResponse response = new HFS_CommandCenterResponse();
    response.context = new HFS_RelationshipServiceImpl().getContext(request);
    response.permissions = currentPermissions();
    response.userLabel = UserInfo.getUserName();
    return response;
  }

  @AuraEnabled
  public static HFS_CommandResult decideApproval(
    HFS_ApprovalDecisionCommand command
  ) {
    return new HFS_RelationshipServiceImpl().decideApproval(command);
  }

  private static HFS_CommandCenterPermissions currentPermissions() {
    HFS_CommandCenterPermissions permissions = new HFS_CommandCenterPermissions();
    Boolean canDecideApproval =
      FeatureManagement.checkPermission('HFS_Approve_Recommendation') &&
      Schema.SObjectType.HFS_Approval__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Status__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Decision_By__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Decided_At__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Decision_Notes__c.isUpdateable();

    permissions.canApprove = canDecideApproval;
    permissions.canModify = false;
    permissions.canReject = canDecideApproval;
    permissions.canExecute =
      FeatureManagement.checkPermission('HFS_Execute_Action') &&
      Schema.SObjectType.HFS_Action__c.isCreateable();
    return permissions;
  }
}
