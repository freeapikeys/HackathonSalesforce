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
    System.assertNotEquals(null, response.permissions.canModify);
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

  @IsTest
  static void correctionReviewPersistsGovernedReviewChainAndReplays() {
    Datetime nowValue = System.now();
    HFS_Event__c eventRecord = new HFS_Event__c(
      Event_Id__c = 'event-controller-correction',
      Tenant_Key__c = 'tenant-controller-correction',
      Source_URI__c = 'urn:test:controller:correction',
      Source_Record_Id__c = 'relationship-correction-source',
      Event_Type__c = 'RELATIONSHIP_ASSERTION_REVIEWED',
      Subject__c = 'Relationship correction requested',
      Occurred_At__c = nowValue.addMinutes(-10),
      Observed_At__c = nowValue.addMinutes(-9),
      Source_Sequence__c = 1,
      Idempotency_Key__c = 'event-controller-correction-v1',
      Correlation_Id__c = 'correlation-controller-correction',
      Schema_Version__c = '1.0.0',
      Content_Hash__c = 'sha256:controller-correction',
      Intake_Result__c = 'ACCEPTED'
    );
    insert eventRecord;

    HFS_Entity__c subject = new HFS_Entity__c(
      External_Key__c = 'entity-controller-subject',
      Tenant_Key__c = 'tenant-controller-correction',
      Entity_Type__c = 'ORGANIZATION',
      Display_Name__c = 'Controller Subject',
      Source_Event__c = eventRecord.Id,
      Valid_From__c = nowValue.addDays(-1),
      Confidence__c = 0.95
    );
    HFS_Entity__c objectValue = new HFS_Entity__c(
      External_Key__c = 'entity-controller-object',
      Tenant_Key__c = 'tenant-controller-correction',
      Entity_Type__c = 'SUPPLIER',
      Display_Name__c = 'Controller Object',
      Source_Event__c = eventRecord.Id,
      Valid_From__c = nowValue.addDays(-1),
      Confidence__c = 0.95
    );
    insert new List<HFS_Entity__c>{ subject, objectValue };

    HFS_Relationship__c relationship = new HFS_Relationship__c(
      External_Key__c = 'relationship-controller-correction',
      Tenant_Key__c = 'tenant-controller-correction',
      Subject_Entity__c = subject.Id,
      Object_Entity__c = objectValue.Id,
      Relationship_Type__c = 'SUPPLIER_OF',
      Source_Event__c = eventRecord.Id,
      Valid_From__c = nowValue.addDays(-1),
      Confidence__c = 0.91
    );
    insert relationship;

    HFS_CorrectionReviewCommand command = new HFS_CorrectionReviewCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = 'correlation-controller-correction';
    command.tenantKey = 'tenant-controller-correction';
    command.purpose = 'REVIEW_RELATIONSHIP_CORRECTION';
    command.externalKey = 'correction-controller-correction';
    command.sourceRelationshipId = relationship.Id;
    command.targetLabel = 'Supplier relationship';
    command.reason = 'Review whether this supplier assertion should be superseded.';

    Test.startTest();
    HFS_CommandResult result = HFS_RelationshipController.requestCorrectionReview(
      command
    );
    HFS_CommandResult replay = HFS_RelationshipController.requestCorrectionReview(
      command
    );
    Test.stopTest();

    System.assertEquals(true, result.success);
    System.assertEquals('REQUEST_CORRECTION_REVIEW', result.operation);
    System.assertEquals('AWAITING_APPROVAL', result.status);
    System.assertEquals(false, result.replayed);
    System.assertEquals(true, replay.replayed);
    System.assertEquals(result.recordId, replay.recordId);

    HFS_Work_Item__c workItem = [
      SELECT Status__c, Primary_Entity__c, Trigger_Event__c
      FROM HFS_Work_Item__c
      WHERE Id = :result.recordId
    ];
    System.assertEquals('AWAITING_APPROVAL', workItem.Status__c);
    System.assertEquals(subject.Id, workItem.Primary_Entity__c);
    System.assertEquals(eventRecord.Id, workItem.Trigger_Event__c);

    HFS_Recommendation__c recommendation = [
      SELECT
        Status__c,
        Recommendation_Type__c,
        Proposed_Action_Type__c,
        Primary_Evidence__c
      FROM HFS_Recommendation__c
      WHERE Work_Item__c = :workItem.Id
    ];
    System.assertEquals('PENDING_APPROVAL', recommendation.Status__c);
    System.assertEquals(
      'RELATIONSHIP_CORRECTION_REVIEW',
      recommendation.Recommendation_Type__c
    );
    System.assertEquals(
      'SUPERSEDE_RELATIONSHIP_ASSERTION',
      recommendation.Proposed_Action_Type__c
    );

    HFS_Approval__c approval = [
      SELECT Status__c, Policy_Key__c
      FROM HFS_Approval__c
      WHERE Recommendation__c = :recommendation.Id
    ];
    System.assertEquals('PENDING', approval.Status__c);
    System.assertEquals(
      'relationship-correction-review-v1',
      approval.Policy_Key__c
    );

    System.assertEquals(
      1,
      [
        SELECT COUNT()
        FROM HFS_Relationship__c
        WHERE Id = :relationship.Id
      ]
    );
  }
}
