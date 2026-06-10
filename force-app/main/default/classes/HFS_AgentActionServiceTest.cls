@IsTest
private class HFS_AgentActionServiceTest {
  private static final String TENANT = 'tenant-agent-action-test';
  private static final String CORRELATION = 'agent-action-correlation-001';
  private static final String HASH = 'sha256:56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70fdb4feada11935c10';

  @TestSetup
  static void createGroundedCase() {
    Datetime nowValue = System.now();
    HFS_Event__c sourceEvent = new HFS_Event__c(
      Event_Id__c = 'event-agent-action-test',
      Tenant_Key__c = TENANT,
      Source_URI__c = 'urn:test:crm:agent-case-001',
      Source_Record_Id__c = 'agent-case-001',
      Event_Type__c = 'CASE_STATUS_CHANGED',
      Subject__c = 'A customer is waiting for a promised status update.',
      Occurred_At__c = nowValue.addMinutes(-10),
      Observed_At__c = nowValue.addMinutes(-9),
      Source_Sequence__c = 1,
      Idempotency_Key__c = 'event-agent-action-test-v1',
      Correlation_Id__c = CORRELATION,
      Schema_Version__c = '1.0.0',
      Content_Hash__c = HASH,
      Intake_Result__c = 'ACCEPTED'
    );
    insert sourceEvent;

    HFS_Entity__c customer = new HFS_Entity__c(
      External_Key__c = 'entity-agent-action-test',
      Tenant_Key__c = TENANT,
      Entity_Type__c = 'PERSON',
      Display_Name__c = 'Agent Action Customer',
      Source_Event__c = sourceEvent.Id,
      Valid_From__c = nowValue.addDays(-30),
      Confidence__c = 0.99
    );
    insert customer;

    HFS_Work_Item__c groundedWork = new HFS_Work_Item__c(
      External_Key__c = 'work-agent-action-test',
      Tenant_Key__c = TENANT,
      Primary_Entity__c = customer.Id,
      Trigger_Event__c = sourceEvent.Id,
      Status__c = 'IN_PROGRESS',
      Priority__c = 'HIGH',
      Summary__c = 'Prepare a proactive status update.',
      Due_At__c = nowValue.addHours(2),
      Blocked_Reason__c = 'Human approval is required.'
    );
    HFS_Work_Item__c ungroundedWork = new HFS_Work_Item__c(
      External_Key__c = 'work-agent-action-no-evidence',
      Tenant_Key__c = TENANT,
      Primary_Entity__c = customer.Id,
      Trigger_Event__c = sourceEvent.Id,
      Status__c = 'IN_PROGRESS',
      Priority__c = 'MEDIUM',
      Summary__c = 'A work item without accessible evidence.'
    );
    insert new List<HFS_Work_Item__c>{ groundedWork, ungroundedWork };

    HFS_Evidence__c evidence = new HFS_Evidence__c(
      External_Key__c = 'evidence-agent-action-test',
      Tenant_Key__c = TENANT,
      Work_Item__c = groundedWork.Id,
      Related_Entity__c = customer.Id,
      Source_Event__c = sourceEvent.Id,
      Evidence_Type__c = 'SOURCE_EVENT',
      Summary__c = 'The customer is waiting for a promised status update.',
      Content_Hash__c = HASH,
      Source_URI__c = 'urn:test:crm:agent-case-001',
      Captured_At__c = nowValue.addMinutes(-8)
    );
    insert evidence;

    insert new HFS_Recommendation__c(
      External_Key__c = 'recommendation-agent-action-test',
      Tenant_Key__c = TENANT,
      Work_Item__c = groundedWork.Id,
      Subject_Entity__c = customer.Id,
      Primary_Evidence__c = evidence.Id,
      Status__c = 'DRAFT',
      Recommendation_Type__c = 'PROACTIVE_RELATIONSHIP_UPDATE',
      Proposed_Action_Type__c = 'SEND_STATUS_UPDATE',
      Rationale__c = 'Prepare an update naming the owner and next update time.',
      Confidence__c = 0.87,
      Model_Profile__c = 'recommendation_reasoning',
      Model_Invocation_Id__c = 'model-invocation-agent-test-001',
      Generated_At__c = nowValue.addMinutes(-5)
    );
  }

  @IsTest
  static void explainsAccessibleEvidenceAndSeparatesInference() {
    HFS_AgentActionResult result = HFS_AgentExplainAction.invoke(
      new List<HFS_AgentActionRequest>{
        request(HFS_AgentActionService.EXPLAIN)
      }
    )[0];

    System.assertEquals('SUCCESS', result.status);
    System.assertEquals(false, result.externalActionExecuted);
    System.assertEquals(1, result.citationEvidenceIds.size());
    Map<String, Object> body = body(result);
    System.assertEquals(1, asList(body, 'facts').size());
    System.assertEquals(1, asList(body, 'inferences').size());
    System.assertEquals(1, asList(body, 'citations').size());
    Map<String, Object> citation = asMap(asList(body, 'citations')[0]);
    System.assertEquals(true, citation.get('accessible'));
    Map<String, Object> inference = asMap(asList(body, 'inferences')[0]);
    System.assertEquals(1, asList(inference, 'basisFactIds').size());
    System.assertEquals(
      false,
      asMap(body.get('audit')).get('externalActionExecuted')
    );
  }

  @IsTest
  static void returnsQualifiedRecommendationWithModelProvenance() {
    HFS_AgentActionRequest actionRequest = request(
      HFS_AgentActionService.RECOMMEND
    );
    actionRequest.modelProfile = 'recommendation_reasoning';
    actionRequest.desiredOutcome = 'Reduce repeated status chasing.';

    HFS_AgentActionResult result = HFS_AgentRecommendationAction.invoke(
      new List<HFS_AgentActionRequest>{ actionRequest }
    )[0];

    System.assertEquals('SUCCESS', result.status);
    System.assertEquals(
      'model-invocation-agent-test-001',
      result.modelInvocationId
    );
    Map<String, Object> response = body(result);
    Map<String, Object> recommendation = asMap(response.get('recommendation'));
    System.assertEquals(true, recommendation.get('requiresHumanApproval'));
    System.assertEquals(
      'recommendation_reasoning',
      recommendation.get('modelProfile')
    );
    System.assertEquals(
      result.modelInvocationId,
      asMap(response.get('audit')).get('modelInvocationId')
    );
    System.assertEquals(false, result.externalActionExecuted);
  }

  @IsTest
  static void failsClosedWithoutEvidenceOrQualifiedModel() {
    HFS_AgentActionRequest noModel = request(HFS_AgentActionService.RECOMMEND);
    noModel.modelProfile = 'unqualified-profile';
    HFS_AgentActionResult noModelResult = HFS_AgentRecommendationAction.invoke(
      new List<HFS_AgentActionRequest>{ noModel }
    )[0];
    assertRefusal(noModelResult, 'NO_QUALIFIED_MODEL');

    HFS_AgentActionRequest noEvidence = request(HFS_AgentActionService.EXPLAIN);
    noEvidence.workItemId = [
      SELECT Id
      FROM HFS_Work_Item__c
      WHERE External_Key__c = 'work-agent-action-no-evidence'
    ]
    .Id;
    HFS_AgentActionResult noEvidenceResult = HFS_AgentExplainAction.invoke(
      new List<HFS_AgentActionRequest>{ noEvidence }
    )[0];
    assertRefusal(noEvidenceResult, 'INACCESSIBLE_EVIDENCE');
  }

  @IsTest
  static void createsOnlyPendingHumanApprovalAndReplays() {
    HFS_Recommendation__c recommendation = [
      SELECT Id
      FROM HFS_Recommendation__c
      WHERE External_Key__c = 'recommendation-agent-action-test'
    ];
    HFS_AgentActionRequest actionRequest = request(
      HFS_AgentActionService.APPROVE
    );
    actionRequest.recommendationId = recommendation.Id;
    actionRequest.approvalPolicyKey = 'external-message-v1';

    HFS_AgentActionResult created = HFS_AgentApprovalRequestAction.invoke(
      new List<HFS_AgentActionRequest>{ actionRequest }
    )[0];
    HFS_AgentActionResult replayed = HFS_AgentApprovalRequestAction.invoke(
      new List<HFS_AgentActionRequest>{ actionRequest }
    )[0];

    System.assertEquals('SUCCESS', created.status);
    System.assertEquals(created.approvalId, replayed.approvalId);
    System.assertEquals(
      'PENDING',
      [SELECT Status__c FROM HFS_Approval__c WHERE Id = :created.approvalId]
      .Status__c
    );
    System.assertEquals(0, [SELECT COUNT() FROM HFS_Action__c]);
    System.assertEquals(false, created.externalActionExecuted);
    System.assertEquals(
      false,
      asMap(body(created).get('approval')).get('externalActionExecuted')
    );
  }

  @IsTest
  static void refusesPermissionFailuresWithoutDisclosingRecords() {
    HFS_AgentActionService.serviceOverride = new DeniedService();
    try {
      HFS_AgentActionResult explainResult = HFS_AgentExplainAction.invoke(
        new List<HFS_AgentActionRequest>{
          request(HFS_AgentActionService.EXPLAIN)
        }
      )[0];
      assertRefusal(explainResult, 'INACCESSIBLE_EVIDENCE');

      HFS_AgentActionRequest approvalRequest = request(
        HFS_AgentActionService.APPROVE
      );
      approvalRequest.recommendationId = 'a0B000000000001AAA';
      approvalRequest.approvalPolicyKey = 'external-message-v1';
      HFS_AgentActionResult approvalResult = HFS_AgentApprovalRequestAction.invoke(
        new List<HFS_AgentActionRequest>{ approvalRequest }
      )[0];
      assertRefusal(approvalResult, 'UNAUTHORIZED_ACTION');
    } finally {
      HFS_AgentActionService.serviceOverride = null;
    }
  }

  @IsTest
  static void rejectsActionMismatchAsStructuredError() {
    HFS_AgentActionRequest actionRequest = request(
      HFS_AgentActionService.RECOMMEND
    );
    HFS_AgentActionResult result = HFS_AgentExplainAction.invoke(
      new List<HFS_AgentActionRequest>{ actionRequest }
    )[0];

    System.assertEquals('ERROR', result.status);
    System.assertEquals(HFS_ServiceContract.INVALID_REQUEST, result.errorCode);
    System.assertEquals(false, result.externalActionExecuted);
  }

  private static HFS_AgentActionRequest request(String action) {
    HFS_AgentActionRequest result = new HFS_AgentActionRequest();
    result.contractVersion = HFS_ServiceContract.VERSION;
    result.action = action;
    result.tenantKey = TENANT;
    result.correlationId = CORRELATION;
    result.purpose = 'RESOLVE_SERVICE_INTERRUPTION';
    result.workItemId = [
      SELECT Id
      FROM HFS_Work_Item__c
      WHERE External_Key__c = 'work-agent-action-test'
    ]
    .Id;
    return result;
  }

  private static void assertRefusal(HFS_AgentActionResult result, String code) {
    System.assertEquals('REFUSED', result.status);
    System.assertEquals(code, result.refusalCode);
    System.assertEquals(false, result.externalActionExecuted);
    Map<String, Object> response = body(result);
    System.assertEquals(0, asList(response, 'facts').size());
    System.assertEquals(0, asList(response, 'inferences').size());
    System.assertEquals(0, asList(response, 'citations').size());
    System.assertEquals(null, response.get('recommendation'));
    System.assertEquals(null, response.get('approval'));
    System.assertEquals(
      0,
      asList(asMap(response.get('refusal')), 'disclosedRecordIds').size()
    );
  }

  private static Map<String, Object> body(HFS_AgentActionResult result) {
    return (Map<String, Object>) JSON.deserializeUntyped(result.responseJson);
  }

  private static Map<String, Object> asMap(Object value) {
    return (Map<String, Object>) value;
  }

  private static List<Object> asList(Map<String, Object> value, String key) {
    return (List<Object>) value.get(key);
  }

  private class DeniedService implements HFS_RelationshipService {
    public HFS_ContextResponse getContext(HFS_ContextRequest requestValue) {
      HFS_ContextResponse response = new HFS_ContextResponse();
      response.contractVersion = HFS_ServiceContract.VERSION;
      response.correlationId = requestValue.correlationId;
      response.tenantKey = requestValue.tenantKey;
      response.errors = new List<HFS_ServiceError>{
        HFS_ServiceSupport.error(
          HFS_ServiceContract.PERMISSION_DENIED,
          'The current user cannot access the required data.',
          null,
          false,
          null
        )
      };
      return response;
    }

    public HFS_CommandResult requestApproval(
      HFS_ApprovalRequestCommand command
    ) {
      HFS_CommandResult result = new HFS_CommandResult();
      result.success = false;
      result.errors = new List<HFS_ServiceError>{
        HFS_ServiceSupport.error(
          HFS_ServiceContract.PERMISSION_DENIED,
          'The current user cannot create the approval.',
          null,
          false,
          null
        )
      };
      return result;
    }

    public HFS_ProvenanceResponse getProvenance(
      HFS_ProvenanceRequest requestValue
    ) {
      return null;
    }

    public HFS_CommandResult persistEvent(HFS_EventIntakeCommand command) {
      return null;
    }

    public HFS_CommandResult storeRecommendation(
      HFS_RecommendationCommand command
    ) {
      return null;
    }

    public HFS_CommandResult decideApproval(
      HFS_ApprovalDecisionCommand command
    ) {
      return null;
    }

    public HFS_CommandResult logAction(HFS_ActionCommand command) {
      return null;
    }

    public HFS_CommandResult captureOutcome(HFS_OutcomeCommand command) {
      return null;
    }
  }
}
