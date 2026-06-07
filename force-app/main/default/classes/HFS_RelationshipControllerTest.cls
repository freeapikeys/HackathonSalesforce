@IsTest
private class HFS_RelationshipControllerTest {
  @IsTest
  static void loadReturnsNormalizedServiceFailureAndCapabilities() {
    HFS_ContextRequest request = new HFS_ContextRequest();
    request.contractVersion = HFS_ServiceContract.VERSION;
    request.tenantKey = 'tenant-controller-test';
    request.workItemId = 'not-a-salesforce-id';
    request.purpose = 'RELATIONSHIP_SERVICE';
    request.correlationId = 'correlation-controller-test';

    Test.startTest();
    HFS_CommandCenterResponse response = HFS_RelationshipController.loadCommandCenter(
      request
    );
    Test.stopTest();

    System.assertEquals(
      'correlation-controller-test',
      response.context.correlationId
    );
    System.assertEquals(1, response.context.errors.size());
    System.assertEquals(
      HFS_ServiceContract.INVALID_REQUEST,
      response.context.errors[0].code
    );
    System.assertNotEquals(null, response.permissions);
    System.assertEquals(false, response.permissions.canModify);
    System.assertNotEquals(null, response.userLabel);
  }

  @IsTest
  static void decisionDelegatesToGovernedService() {
    HFS_ApprovalDecisionCommand command = new HFS_ApprovalDecisionCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = 'correlation-controller-decision';
    command.tenantKey = 'tenant-controller-test';
    command.purpose = 'RELATIONSHIP_SERVICE';
    command.approvalId = 'not-a-salesforce-id';
    command.decisionStatus = 'APPROVED';

    HFS_ServiceSupport.setPermissionOverride(
      'HFS_Approve_Recommendation',
      false
    );
    Test.startTest();
    HFS_CommandResult result = HFS_RelationshipController.decideApproval(
      command
    );
    Test.stopTest();
    HFS_ServiceSupport.clearPermissionOverrides();

    System.assertEquals(false, result.success);
    System.assertEquals(HFS_ServiceContract.DECIDE_APPROVAL, result.operation);
    System.assertEquals(
      'correlation-controller-decision',
      result.correlationId
    );
    System.assertEquals(
      HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED,
      result.errors[0].code
    );
  }
}
