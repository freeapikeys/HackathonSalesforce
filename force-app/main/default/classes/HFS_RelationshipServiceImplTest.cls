@IsTest
private class HFS_RelationshipServiceImplTest {
  private static final String TENANT = 'tenant-service-test';
  private static final String CORRELATION = 'correlation-service-test';

  @TestSetup
  static void createRelationshipGraph() {
    Datetime nowValue = System.now();
    HFS_Event__c sourceEvent = new HFS_Event__c(
      Event_Id__c = 'event-service-test',
      Tenant_Key__c = TENANT,
      Source_URI__c = 'urn:test:crm:case-001',
      Source_Record_Id__c = 'case-001',
      Event_Type__c = 'CASE_STATUS_CHANGED',
      Subject__c = 'Customer needs a proactive status update',
      Occurred_At__c = nowValue.addMinutes(-10),
      Observed_At__c = nowValue.addMinutes(-9),
      Source_Sequence__c = 1,
      Idempotency_Key__c = 'event-service-test-v1',
      Correlation_Id__c = CORRELATION,
      Schema_Version__c = '1.0.0',
      Content_Hash__c = 'sha256:event-service-test',
      Intake_Result__c = 'ACCEPTED'
    );
    insert sourceEvent;

    HFS_Entity__c customer = new HFS_Entity__c(
      External_Key__c = 'entity-customer-test',
      Tenant_Key__c = TENANT,
      Entity_Type__c = 'PERSON',
      Display_Name__c = 'Jordan Customer',
      Source_Event__c = sourceEvent.Id,
      Valid_From__c = nowValue.addDays(-30),
      Confidence__c = 0.99
    );
    HFS_Entity__c business = new HFS_Entity__c(
      External_Key__c = 'entity-business-test',
      Tenant_Key__c = TENANT,
      Entity_Type__c = 'ORGANIZATION',
      Display_Name__c = 'Example Business',
      Source_Event__c = sourceEvent.Id,
      Valid_From__c = nowValue.addDays(-30),
      Confidence__c = 1
    );
    HFS_Entity__c supplier = new HFS_Entity__c(
      External_Key__c = 'entity-supplier-test',
      Tenant_Key__c = TENANT,
      Entity_Type__c = 'SUPPLIER',
      Display_Name__c = 'Example Supplier',
      Source_Event__c = sourceEvent.Id,
      Valid_From__c = nowValue.addDays(-30),
      Confidence__c = 0.95
    );
    insert new List<HFS_Entity__c>{ customer, business, supplier };

    insert new HFS_Event_Participant__c(
      External_Key__c = 'participant-customer-test',
      Tenant_Key__c = TENANT,
      Event__c = sourceEvent.Id,
      Entity__c = customer.Id,
      Participant_Role__c = 'SUBJECT'
    );
    insert new HFS_Relationship__c(
      External_Key__c = 'relationship-customer-test',
      Tenant_Key__c = TENANT,
      Subject_Entity__c = customer.Id,
      Object_Entity__c = business.Id,
      Relationship_Type__c = 'CUSTOMER_OF',
      Source_Event__c = sourceEvent.Id,
      Valid_From__c = nowValue.addDays(-30),
      Confidence__c = 0.98
    );
    insert new HFS_Agreement__c(
      External_Key__c = 'agreement-supplier-test',
      Tenant_Key__c = TENANT,
      Party_One__c = business.Id,
      Party_Two__c = supplier.Id,
      Agreement_Type__c = 'SERVICE_LEVEL',
      Status__c = 'ACTIVE',
      Terms_Summary__c = 'Supplier provides status within one business day.',
      Source_Event__c = sourceEvent.Id,
      Effective_From__c = nowValue.date().addDays(-30)
    );

    HFS_Work_Item__c workItem = new HFS_Work_Item__c(
      External_Key__c = 'work-service-test',
      Tenant_Key__c = TENANT,
      Primary_Entity__c = customer.Id,
      Trigger_Event__c = sourceEvent.Id,
      Status__c = 'IN_PROGRESS',
      Priority__c = 'HIGH',
      Summary__c = 'Prepare and approve a proactive customer update.'
    );
    insert workItem;
    insert new HFS_SOP_Execution__c(
      External_Key__c = 'sop-service-test',
      Tenant_Key__c = TENANT,
      Work_Item__c = workItem.Id,
      Definition_Key__c = 'proactive-update',
      Definition_Version__c = '1.0.0',
      Current_Step_Key__c = 'REVIEW_EVIDENCE',
      Status__c = 'RUNNING',
      Started_At__c = nowValue.addMinutes(-8)
    );
    insert new HFS_Evidence__c(
      External_Key__c = 'evidence-service-test',
      Tenant_Key__c = TENANT,
      Work_Item__c = workItem.Id,
      Related_Entity__c = customer.Id,
      Source_Event__c = sourceEvent.Id,
      Evidence_Type__c = 'SOURCE_EVENT',
      Summary__c = 'The customer is waiting for a promised update.',
      Content_Hash__c = 'sha256:evidence-service-test',
      Source_URI__c = 'urn:test:crm:case-001',
      Captured_At__c = nowValue.addMinutes(-7)
    );
  }

  @IsTest
  static void completesGovernedVerticalSliceAndReadsContext() {
    HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
    HFS_Work_Item__c workItem = workItem();
    HFS_Entity__c customer = customer();
    HFS_Evidence__c evidence = evidence();
    HFS_Event__c sourceEvent = sourceEvent();

    HFS_CommandResult recommendationResult = service.storeRecommendation(
      recommendationCommand(workItem.Id, customer.Id, evidence.Id)
    );
    System.assertEquals(true, recommendationResult.success);
    System.assertEquals('DRAFT', recommendationResult.status);

    HFS_CommandResult replayedRecommendation = service.storeRecommendation(
      recommendationCommand(workItem.Id, customer.Id, evidence.Id)
    );
    System.assertEquals(true, replayedRecommendation.success);
    System.assertEquals(true, replayedRecommendation.replayed);
    System.assertEquals(
      recommendationResult.recordId,
      replayedRecommendation.recordId
    );

    HFS_CommandResult approvalResult = service.requestApproval(
      approvalRequest(recommendationResult.recordId)
    );
    System.assertEquals(true, approvalResult.success);
    System.assertEquals('PENDING', approvalResult.status);
    HFS_CommandResult replayedApproval = service.requestApproval(
      approvalRequest(recommendationResult.recordId)
    );
    System.assertEquals(true, replayedApproval.replayed);
    System.assertEquals(approvalResult.recordId, replayedApproval.recordId);

    HFS_ServiceSupport.setPermissionOverride(
      'HFS_Approve_Recommendation',
      true
    );
    HFS_CommandResult decisionResult = service.decideApproval(
      approvalDecision(approvalResult.recordId, 'APPROVED')
    );
    System.assertEquals(true, decisionResult.success);
    System.assertEquals('APPROVED', decisionResult.status);
    HFS_CommandResult replayedDecision = service.decideApproval(
      approvalDecision(approvalResult.recordId, 'APPROVED')
    );
    System.assertEquals(true, replayedDecision.replayed);

    HFS_ServiceSupport.setPermissionOverride('HFS_Execute_Action', true);
    HFS_ActionCommand actionCommandValue = actionCommand(
      recommendationResult.recordId,
      approvalResult.recordId,
      customer.Id
    );
    HFS_CommandResult actionResult = service.logAction(actionCommandValue);
    System.assertEquals(true, actionResult.success);
    System.assertEquals('PENDING', actionResult.status);
    HFS_CommandResult replayedAction = service.logAction(actionCommandValue);
    System.assertEquals(true, replayedAction.replayed);

    HFS_OutcomeCommand outcomeCommandValue = outcomeCommand(
      actionResult.recordId,
      sourceEvent.Id
    );
    HFS_CommandResult outcomeResult = service.captureOutcome(
      outcomeCommandValue
    );
    System.assertEquals(true, outcomeResult.success);
    System.assertEquals('SUCCESS', outcomeResult.status);
    HFS_CommandResult replayedOutcome = service.captureOutcome(
      outcomeCommandValue
    );
    System.assertEquals(true, replayedOutcome.replayed);

    HFS_ContextRequest contextRequest = new HFS_ContextRequest();
    contextRequest.contractVersion = HFS_ServiceContract.VERSION;
    contextRequest.tenantKey = TENANT;
    contextRequest.workItemId = workItem.Id;
    contextRequest.purpose = 'TEST_RELATIONSHIP_CONTEXT';
    contextRequest.correlationId = CORRELATION;
    contextRequest.includeProvenance = true;
    contextRequest.timelineLimit = 25;

    HFS_ContextResponse context = service.getContext(contextRequest);
    System.assertEquals(0, context.errors.size());
    System.assertEquals(workItem.Id, context.workItem.recordId);
    System.assert(context.entities.size() >= 3);
    System.assertEquals(1, context.relationships.size());
    System.assertEquals(1, context.agreements.size());
    System.assertEquals(1, context.sopExecutions.size());
    System.assertEquals(1, context.evidence.size());
    System.assertEquals(1, context.recommendations.size());
    System.assertEquals(1, context.approvals.size());
    System.assertEquals(1, context.actions.size());
    System.assertEquals(1, context.outcomes.size());
    System.assert(context.timeline.size() >= 5);

    HFS_ProvenanceRequest provenanceRequest = new HFS_ProvenanceRequest();
    provenanceRequest.contractVersion = HFS_ServiceContract.VERSION;
    provenanceRequest.tenantKey = TENANT;
    provenanceRequest.objectApiName = 'HFS_Recommendation__c';
    provenanceRequest.recordId = recommendationResult.recordId;
    provenanceRequest.purpose = 'EXPLAIN_RECOMMENDATION';
    provenanceRequest.correlationId = CORRELATION;
    provenanceRequest.maxDepth = 4;

    HFS_ProvenanceResponse provenance = service.getProvenance(
      provenanceRequest
    );
    System.assertEquals(0, provenance.errors.size());
    System.assertEquals(
      recommendationResult.recordId,
      provenance.rootRecord.recordId
    );
    System.assertEquals(1, provenance.citations.size());
    System.assert(provenance.lineage.size() >= 2);

    HFS_Action__c storedAction = [
      SELECT Status__c, Executed_At__c
      FROM HFS_Action__c
      WHERE Id = :actionResult.recordId
    ];
    System.assertEquals('EXECUTED', storedAction.Status__c);
    System.assertNotEquals(null, storedAction.Executed_At__c);
    System.assertEquals(
      'COMPLETED',
      [SELECT Status__c FROM HFS_Work_Item__c WHERE Id = :workItem.Id].Status__c
    );
  }

  @IsTest
  static void enforcesPermissionTenantAndApprovalState() {
    HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
    HFS_Work_Item__c workItem = workItem();
    HFS_Entity__c customer = customer();
    HFS_Evidence__c evidence = evidence();

    HFS_RecommendationCommand wrongTenant = recommendationCommand(
      workItem.Id,
      customer.Id,
      evidence.Id
    );
    wrongTenant.externalKey = 'recommendation-wrong-tenant-test';
    wrongTenant.tenantKey = 'tenant-other';
    HFS_CommandResult tenantResult = service.storeRecommendation(wrongTenant);
    assertError(tenantResult, HFS_ServiceContract.TENANT_MISMATCH);

    HFS_CommandResult recommendationResult = service.storeRecommendation(
      recommendationCommand(workItem.Id, customer.Id, evidence.Id)
    );
    HFS_CommandResult approvalResult = service.requestApproval(
      approvalRequest(recommendationResult.recordId)
    );

    HFS_ServiceSupport.setPermissionOverride(
      'HFS_Approve_Recommendation',
      false
    );
    HFS_CommandResult deniedDecision = service.decideApproval(
      approvalDecision(approvalResult.recordId, 'APPROVED')
    );
    assertError(deniedDecision, HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED);

    HFS_ServiceSupport.setPermissionOverride('HFS_Execute_Action', true);
    HFS_CommandResult invalidAction = service.logAction(
      actionCommand(
        recommendationResult.recordId,
        approvalResult.recordId,
        customer.Id
      )
    );
    assertError(invalidAction, HFS_ServiceContract.INVALID_STATE);
    System.assertEquals(0, [SELECT COUNT() FROM HFS_Action__c]);
  }

  @IsTest
  static void rejectsUnsupportedReadRequestsWithoutThrowing() {
    HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
    HFS_ContextRequest contextRequest = new HFS_ContextRequest();
    contextRequest.contractVersion = '9.0.0';
    contextRequest.tenantKey = TENANT;
    contextRequest.workItemId = workItem().Id;
    contextRequest.purpose = 'TEST';
    contextRequest.correlationId = CORRELATION;

    HFS_ContextResponse context = service.getContext(contextRequest);
    System.assertEquals(1, context.errors.size());
    System.assertEquals(
      HFS_ServiceContract.UNSUPPORTED_CONTRACT_VERSION,
      context.errors[0].code
    );

    HFS_ProvenanceRequest provenanceRequest = new HFS_ProvenanceRequest();
    provenanceRequest.contractVersion = HFS_ServiceContract.VERSION;
    provenanceRequest.tenantKey = TENANT;
    provenanceRequest.objectApiName = 'Account';
    provenanceRequest.recordId = UserInfo.getUserId();
    provenanceRequest.purpose = 'TEST';
    provenanceRequest.correlationId = CORRELATION;

    HFS_ProvenanceResponse provenance = service.getProvenance(
      provenanceRequest
    );
    System.assertEquals(1, provenance.errors.size());
    System.assertEquals(
      HFS_ServiceContract.INVALID_REQUEST,
      provenance.errors[0].code
    );
  }

  @IsTest
  static void normalizesValidationQueryDmlAndUnexpectedErrors() {
    try {
      HFS_ServiceSupport.requireText(null, 'missingField');
      System.assert(false, 'Expected a missing value failure.');
    } catch (HFS_ServiceException expected) {
      HFS_ServiceError errorValue = HFS_ServiceSupport.error(expected);
      System.assertEquals(HFS_ServiceContract.INVALID_REQUEST, errorValue.code);
      System.assertEquals('missingField', errorValue.fieldName);
    }

    try {
      HFS_ServiceSupport.requireId('not-a-salesforce-id', 'recordId');
      System.assert(false, 'Expected an invalid ID failure.');
    } catch (HFS_ServiceException expected) {
      System.assertEquals(
        HFS_ServiceContract.INVALID_REQUEST,
        HFS_ServiceSupport.error(expected).code
      );
    }

    try {
      Account missingRecord = [
        SELECT Id
        FROM Account
        WHERE Id = NULL
        LIMIT 1
      ];
      System.assertNotEquals(null, missingRecord);
    } catch (QueryException expected) {
      System.assertEquals(
        HFS_ServiceContract.PERMISSION_DENIED,
        HFS_ServiceSupport.error(expected).code
      );
    }

    try {
      insert new HFS_Work_Item__c();
      System.assert(false, 'Expected required-field DML to fail.');
    } catch (DmlException expected) {
      System.assertEquals(
        HFS_ServiceContract.VALIDATION_FAILED,
        HFS_ServiceSupport.error(expected).code
      );
    }

    System.assertEquals(
      HFS_ServiceContract.UNEXPECTED_ERROR,
      HFS_ServiceSupport.error(new SyntheticException('synthetic')).code
    );
    System.assertEquals(true, HFS_ServiceSupport.same(null, null));
    HFS_ServiceSupport.clearPermissionOverrides();
    try {
      HFS_ServiceSupport.requirePermission('HFS_Unknown_Permission');
      System.assert(false, 'Expected an unassigned permission failure.');
    } catch (HFS_ServiceException expected) {
      System.assertEquals(
        HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED,
        HFS_ServiceSupport.error(expected).code
      );
    }
  }

  @IsTest
  static void enforcesDeployedPermissionSetsAcrossRealUsers() {
    User relationshipUser = createUser('relation', 'HFS_Relationship_User');
    User approverUser = createUser('approver', 'HFS_Approver');
    User integrationUser = createUser('integrat', 'HFS_Integration_User');
    User unprivilegedUser = createUser('noaccess', null);
    HFS_ServiceSupport.clearPermissionOverrides();

    HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
    HFS_Work_Item__c workItem = workItem();
    HFS_Entity__c customer = customer();
    HFS_Evidence__c evidence = evidence();
    HFS_Event__c sourceEvent = sourceEvent();
    HFS_CommandResult recommendationResult;
    HFS_CommandResult approvalResult;
    HFS_CommandResult actionResult;

    System.runAs(relationshipUser) {
      recommendationResult = service.storeRecommendation(
        recommendationCommand(workItem.Id, customer.Id, evidence.Id)
      );
      System.assertEquals(true, recommendationResult.success);

      HFS_CommandResult deniedApproval = service.requestApproval(
        approvalRequest(recommendationResult.recordId)
      );
      assertError(deniedApproval, HFS_ServiceContract.PERMISSION_DENIED);

      HFS_ContextRequest contextRequest = contextRequest(workItem.Id);
      System.assertEquals(0, service.getContext(contextRequest).errors.size());
    }

    System.runAs(approverUser) {
      HFS_RecommendationCommand deniedRecommendation = recommendationCommand(
        workItem.Id,
        customer.Id,
        evidence.Id
      );
      deniedRecommendation.externalKey = 'recommendation-approver-denied';
      assertError(
        service.storeRecommendation(deniedRecommendation),
        HFS_ServiceContract.PERMISSION_DENIED
      );

      approvalResult = service.requestApproval(
        approvalRequest(recommendationResult.recordId)
      );
      System.assertEquals(true, approvalResult.success);
      System.assertEquals(
        true,
        service
          .decideApproval(approvalDecision(approvalResult.recordId, 'APPROVED'))
          .success
      );

      assertError(
        service.logAction(
          actionCommand(
            recommendationResult.recordId,
            approvalResult.recordId,
            customer.Id
          )
        ),
        HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED
      );
    }

    System.runAs(integrationUser) {
      assertError(
        service.decideApproval(
          approvalDecision(approvalResult.recordId, 'APPROVED')
        ),
        HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED
      );

      actionResult = service.logAction(
        actionCommand(
          recommendationResult.recordId,
          approvalResult.recordId,
          customer.Id
        )
      );
      System.assertEquals(true, actionResult.success);
      System.assertEquals(
        true,
        service
          .captureOutcome(outcomeCommand(actionResult.recordId, sourceEvent.Id))
          .success
      );
    }

    System.runAs(unprivilegedUser) {
      HFS_ProvenanceRequest request = new HFS_ProvenanceRequest();
      request.contractVersion = HFS_ServiceContract.VERSION;
      request.tenantKey = TENANT;
      request.objectApiName = 'HFS_Evidence__c';
      request.recordId = evidence.Id;
      request.purpose = 'TEST_INACCESSIBLE_EVIDENCE';
      request.correlationId = CORRELATION;
      request.maxDepth = 2;

      HFS_ProvenanceResponse response = service.getProvenance(request);
      System.assertEquals(1, response.errors.size());
      System.assertEquals(
        HFS_ServiceContract.SOURCE_EVIDENCE_INACCESSIBLE,
        response.errors[0].code
      );
    }
  }

  @IsTest
  static void rejectsConflictingDuplicateCommands() {
    HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
    HFS_Work_Item__c workItem = workItem();
    HFS_Entity__c customer = customer();
    HFS_Evidence__c evidence = evidence();
    HFS_Event__c sourceEvent = sourceEvent();

    HFS_RecommendationCommand recommendation = recommendationCommand(
      workItem.Id,
      customer.Id,
      evidence.Id
    );
    HFS_CommandResult recommendationResult = service.storeRecommendation(
      recommendation
    );
    recommendation.rationale = 'Different recommendation content.';
    assertError(
      service.storeRecommendation(recommendation),
      HFS_ServiceContract.IDEMPOTENCY_CONFLICT
    );

    HFS_ApprovalRequestCommand approval = approvalRequest(
      recommendationResult.recordId
    );
    HFS_CommandResult approvalResult = service.requestApproval(approval);
    approval.policyKey = 'different-policy';
    assertError(
      service.requestApproval(approval),
      HFS_ServiceContract.IDEMPOTENCY_CONFLICT
    );

    HFS_ServiceSupport.setPermissionOverride(
      'HFS_Approve_Recommendation',
      true
    );
    service.decideApproval(
      approvalDecision(approvalResult.recordId, 'APPROVED')
    );
    HFS_ServiceSupport.setPermissionOverride('HFS_Execute_Action', true);

    HFS_ActionCommand action = actionCommand(
      recommendationResult.recordId,
      approvalResult.recordId,
      customer.Id
    );
    HFS_CommandResult actionResult = service.logAction(action);
    action.actionType = 'DIFFERENT_ACTION';
    assertError(
      service.logAction(action),
      HFS_ServiceContract.IDEMPOTENCY_CONFLICT
    );

    HFS_OutcomeCommand outcome = outcomeCommand(
      actionResult.recordId,
      sourceEvent.Id
    );
    service.captureOutcome(outcome);
    outcome.summary = 'Different outcome content.';
    assertError(
      service.captureOutcome(outcome),
      HFS_ServiceContract.IDEMPOTENCY_CONFLICT
    );
  }

  @IsTest
  static void rollsBackOutcomeWhenDerivedActionUpdateFails() {
    HFS_RelationshipService service = new HFS_RelationshipServiceImpl();
    HFS_Work_Item__c workItem = workItem();
    HFS_Entity__c customer = customer();
    HFS_Evidence__c evidence = evidence();
    HFS_Event__c sourceEvent = sourceEvent();
    HFS_CommandResult recommendationResult = service.storeRecommendation(
      recommendationCommand(workItem.Id, customer.Id, evidence.Id)
    );
    HFS_CommandResult approvalResult = service.requestApproval(
      approvalRequest(recommendationResult.recordId)
    );
    HFS_ServiceSupport.setPermissionOverride(
      'HFS_Approve_Recommendation',
      true
    );
    service.decideApproval(
      approvalDecision(approvalResult.recordId, 'APPROVED')
    );
    HFS_ServiceSupport.setPermissionOverride('HFS_Execute_Action', true);
    HFS_CommandResult actionResult = service.logAction(
      actionCommand(
        recommendationResult.recordId,
        approvalResult.recordId,
        customer.Id
      )
    );

    HFS_OutcomeCommand outcome = outcomeCommand(
      actionResult.recordId,
      sourceEvent.Id
    );
    outcome.externalKey = 'outcome-rollback-test';
    outcome.observedAt = System.now().addDays(-1);
    HFS_CommandResult result = service.captureOutcome(outcome);

    assertError(result, HFS_ServiceContract.VALIDATION_FAILED);
    System.assertEquals(
      0,
      [
        SELECT COUNT()
        FROM HFS_Outcome__c
        WHERE External_Key__c = 'outcome-rollback-test'
      ]
    );
    System.assertEquals(
      'PENDING',
      [
        SELECT Status__c
        FROM HFS_Action__c
        WHERE Id = :actionResult.recordId
      ]
      .Status__c
    );
    System.assertEquals(
      'IN_PROGRESS',
      [SELECT Status__c FROM HFS_Work_Item__c WHERE Id = :workItem.Id].Status__c
    );
  }

  private static HFS_RecommendationCommand recommendationCommand(
    Id workItemId,
    Id subjectEntityId,
    Id evidenceId
  ) {
    HFS_RecommendationCommand command = new HFS_RecommendationCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = CORRELATION;
    command.tenantKey = TENANT;
    command.purpose = 'TEST_RELATIONSHIP_SERVICE';
    command.externalKey = 'recommendation-service-test';
    command.workItemId = workItemId;
    command.subjectEntityId = subjectEntityId;
    command.primaryEvidenceId = evidenceId;
    command.recommendationType = 'PROACTIVE_UPDATE';
    command.proposedActionType = 'SEND_STATUS_UPDATE';
    command.rationale = 'Send the promised status update now.';
    command.confidence = 0.91;
    command.modelProfile = 'relationship-recommendation';
    command.modelInvocationId = 'model-invocation-service-test';
    return command;
  }

  private static HFS_ContextRequest contextRequest(Id workItemId) {
    HFS_ContextRequest request = new HFS_ContextRequest();
    request.contractVersion = HFS_ServiceContract.VERSION;
    request.tenantKey = TENANT;
    request.workItemId = workItemId;
    request.purpose = 'TEST_RELATIONSHIP_CONTEXT';
    request.correlationId = CORRELATION;
    request.includeProvenance = true;
    request.timelineLimit = 25;
    return request;
  }

  private static HFS_ApprovalRequestCommand approvalRequest(
    String recommendationId
  ) {
    HFS_ApprovalRequestCommand command = new HFS_ApprovalRequestCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = CORRELATION;
    command.tenantKey = TENANT;
    command.purpose = 'TEST_RELATIONSHIP_SERVICE';
    command.externalKey = 'approval-service-test';
    command.recommendationId = recommendationId;
    command.policyKey = 'external-message-v1';
    return command;
  }

  private static HFS_ApprovalDecisionCommand approvalDecision(
    String approvalId,
    String status
  ) {
    HFS_ApprovalDecisionCommand command = new HFS_ApprovalDecisionCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = CORRELATION;
    command.tenantKey = TENANT;
    command.purpose = 'TEST_RELATIONSHIP_SERVICE';
    command.approvalId = approvalId;
    command.decisionStatus = status;
    command.decisionNotes = 'Evidence and channel are appropriate.';
    return command;
  }

  private static HFS_ActionCommand actionCommand(
    String recommendationId,
    String approvalId,
    Id targetEntityId
  ) {
    HFS_ActionCommand command = new HFS_ActionCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = CORRELATION;
    command.tenantKey = TENANT;
    command.purpose = 'TEST_RELATIONSHIP_SERVICE';
    command.externalKey = 'action-service-test';
    command.idempotencyKey = 'action-service-test-v1';
    command.recommendationId = recommendationId;
    command.approvalId = approvalId;
    command.targetEntityId = targetEntityId;
    command.actionType = 'SEND_STATUS_UPDATE';
    return command;
  }

  private static HFS_OutcomeCommand outcomeCommand(
    String actionId,
    Id sourceEventId
  ) {
    HFS_OutcomeCommand command = new HFS_OutcomeCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = CORRELATION;
    command.tenantKey = TENANT;
    command.purpose = 'TEST_RELATIONSHIP_SERVICE';
    command.externalKey = 'outcome-service-test';
    command.actionId = actionId;
    command.sourceEventId = sourceEventId;
    command.outcomeType = 'MESSAGE_DELIVERED';
    command.status = 'SUCCESS';
    command.observedAt = System.now();
    command.summary = 'The approved update was delivered.';
    command.metricKey = 'delivery_success';
    command.metricValue = 1;
    return command;
  }

  private static void assertError(HFS_CommandResult result, String code) {
    System.assertEquals(false, result.success);
    System.assertEquals(1, result.errors.size());
    System.assertEquals(code, result.errors[0].code);
  }

  private static HFS_Work_Item__c workItem() {
    return [
      SELECT Id
      FROM HFS_Work_Item__c
      WHERE External_Key__c = 'work-service-test'
      LIMIT 1
    ];
  }

  private static HFS_Entity__c customer() {
    return [
      SELECT Id
      FROM HFS_Entity__c
      WHERE External_Key__c = 'entity-customer-test'
      LIMIT 1
    ];
  }

  private static HFS_Evidence__c evidence() {
    return [
      SELECT Id
      FROM HFS_Evidence__c
      WHERE External_Key__c = 'evidence-service-test'
      LIMIT 1
    ];
  }

  private static HFS_Event__c sourceEvent() {
    return [
      SELECT Id
      FROM HFS_Event__c
      WHERE Event_Id__c = 'event-service-test'
      LIMIT 1
    ];
  }

  private static User createUser(String key, String permissionSetName) {
    Profile minimumAccess = [
      SELECT Id
      FROM Profile
      WHERE Name = 'Minimum Access - Salesforce'
      LIMIT 1
    ];
    String uniqueValue =
      String.valueOf(System.now().getTime()) +
      String.valueOf(Math.abs(Crypto.getRandomInteger()));
    User userValue = new User(
      Alias = key.left(8),
      CommunityNickname = (key + uniqueValue).left(40),
      Email = key + uniqueValue + '@hfs.example',
      EmailEncodingKey = 'UTF-8',
      LanguageLocaleKey = 'en_US',
      LastName = 'HFS ' + key,
      LocaleSidKey = 'en_US',
      ProfileId = minimumAccess.Id,
      TimeZoneSidKey = 'America/Los_Angeles',
      Username = key + uniqueValue + '@hfs.example'
    );
    insert userValue;
    if (permissionSetName != null) {
      PermissionSet permissionSetValue = [
        SELECT Id
        FROM PermissionSet
        WHERE Name = :permissionSetName
        LIMIT 1
      ];
      insert new PermissionSetAssignment(
        AssigneeId = userValue.Id,
        PermissionSetId = permissionSetValue.Id
      );
    }
    return userValue;
  }

  private class SyntheticException extends Exception {
  }
}
