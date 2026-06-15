@IsTest
private class HFS_ServiceContractTest {
  @IsTest
  static void exposesEveryVersionedOperationAndPolicy() {
    System.assertEquals('1.0.0', HFS_ServiceContract.VERSION);
    System.assert(HFS_ServiceContract.supportsVersion('1.0.0'));
    System.assert(!HFS_ServiceContract.supportsVersion('2.0.0'));

    List<HFS_AuthorizationPolicy> policies = HFS_AuthorizationMatrix.allPolicies();

    System.assertEquals(HFS_ServiceContract.OPERATIONS.size(), policies.size());
    for (HFS_AuthorizationPolicy policy : policies) {
      System.assert(HFS_ServiceContract.OPERATIONS.contains(policy.operation));
      System.assertEquals('WITH_SHARING', policy.sharingMode);
      System.assertEquals('USER_MODE', policy.dataAccessMode);
      System.assertEquals(false, policy.externalCalloutAllowed);
      System.assertNotEquals(null, policy.transactionBoundary);
    }
  }

  @IsTest
  static void baselineRoleMatrixMatchesPermissionSets() {
    Map<String, Set<String>> expectedOperationsByRole = new Map<String, Set<String>>{
      HFS_AuthorizationMatrix.RELATIONSHIP_USER => new Set<String>{
        HFS_ServiceContract.READ_CONTEXT,
        HFS_ServiceContract.READ_PROVENANCE,
        HFS_ServiceContract.STORE_RECOMMENDATION
      },
      HFS_AuthorizationMatrix.APPROVER => new Set<String>{
        HFS_ServiceContract.READ_CONTEXT,
        HFS_ServiceContract.READ_PROVENANCE,
        HFS_ServiceContract.REQUEST_APPROVAL,
        HFS_ServiceContract.DECIDE_APPROVAL
      },
      HFS_AuthorizationMatrix.INTEGRATION_USER => new Set<String>{
        HFS_ServiceContract.READ_CONTEXT,
        HFS_ServiceContract.READ_PROVENANCE,
        HFS_ServiceContract.PERSIST_EVENT,
        HFS_ServiceContract.STORE_RECOMMENDATION,
        HFS_ServiceContract.REQUEST_APPROVAL,
        HFS_ServiceContract.LOG_ACTION,
        HFS_ServiceContract.CAPTURE_OUTCOME
      }
    };

    for (String role : expectedOperationsByRole.keySet()) {
      for (String operation : HFS_ServiceContract.OPERATIONS) {
        System.assertEquals(
          expectedOperationsByRole.get(role).contains(operation),
          HFS_AuthorizationMatrix.baselineRoleExpectedToPass(role, operation),
          role + ' authorization mismatch for ' + operation
        );
      }
    }

    System.assertEquals(
      new List<String>{ 'HFS_Approve_Recommendation' },
      HFS_AuthorizationMatrix.forOperation(HFS_ServiceContract.DECIDE_APPROVAL)
        .customPermissions
    );
    System.assertEquals(
      new List<String>{ 'HFS_Execute_Action' },
      HFS_AuthorizationMatrix.forOperation(HFS_ServiceContract.LOG_ACTION)
        .customPermissions
    );
  }

  @IsTest
  static void dtoFixturesSerializeAndInterfaceCompiles() {
    HFS_RelationshipService service = new ContractFixtureService();

    HFS_ContextItem contextItem = contextItemFixture();
    HFS_ContextItem copiedContextItem = (HFS_ContextItem) roundTrip(
      contextItem,
      HFS_ContextItem.class
    );
    System.assertEquals(contextItem.recordId, copiedContextItem.recordId);

    HFS_EvidenceCitation citation = citationFixture();
    HFS_EvidenceCitation copiedCitation = (HFS_EvidenceCitation) roundTrip(
      citation,
      HFS_EvidenceCitation.class
    );
    System.assertEquals(citation.contentHash, copiedCitation.contentHash);
    System.assertEquals(citation.evidenceType, copiedCitation.evidenceType);

    HFS_ServiceError error = errorFixture();
    HFS_ServiceError copiedError = (HFS_ServiceError) roundTrip(
      error,
      HFS_ServiceError.class
    );
    System.assertEquals(error.code, copiedError.code);

    HFS_ContextRequest contextRequest = new HFS_ContextRequest();
    contextRequest.contractVersion = HFS_ServiceContract.VERSION;
    contextRequest.tenantKey = 'tenant-demo';
    contextRequest.workItemId = 'work-001';
    contextRequest.subjectEntityId = 'entity-001';
    contextRequest.purpose = 'RELATIONSHIP_SERVICE';
    contextRequest.correlationId = 'correlation-001';
    contextRequest.includeProvenance = true;
    contextRequest.timelineLimit = 100;

    HFS_ProvenanceRequest provenanceRequest = new HFS_ProvenanceRequest();
    provenanceRequest.contractVersion = HFS_ServiceContract.VERSION;
    provenanceRequest.tenantKey = 'tenant-demo';
    provenanceRequest.objectApiName = 'HFS_Recommendation__c';
    provenanceRequest.recordId = 'recommendation-001';
    provenanceRequest.purpose = 'EXPLAIN_RECOMMENDATION';
    provenanceRequest.correlationId = 'correlation-001';
    provenanceRequest.maxDepth = 4;

    HFS_EventIntakeCommand eventIntake = new HFS_EventIntakeCommand();
    eventIntake.contractVersion = HFS_ServiceContract.VERSION;
    eventIntake.correlationId = 'correlation-001';
    eventIntake.tenantKey = 'tenant-demo';
    eventIntake.purpose = 'INGEST_SOURCE_EVENT';
    eventIntake.eventId = '00000000-0000-4000-8000-000000000001';
    eventIntake.sourceUri = 'urn:hfs:source:crm';
    eventIntake.sourceRecordId = 'case-001';
    eventIntake.eventType = 'io.github.freeapikeys.hfs.case.updated.v1';
    eventIntake.subject = 'case:case-001';
    eventIntake.schemaVersion = '1.0.0';
    eventIntake.idempotencyKey = 'crm-case-001-v1';
    eventIntake.sourceSequence = 1;
    eventIntake.occurredAt = System.now().addMinutes(-1);
    eventIntake.observedAt = System.now();
    eventIntake.contentHash = 'sha256:fixture';
    eventIntake.payloadJson = '{"businesskey":"case-001"}';
    eventIntake.intakeResult = 'ACCEPTED';

    HFS_RecommendationCommand recommendation = new HFS_RecommendationCommand();
    recommendation.contractVersion = HFS_ServiceContract.VERSION;
    recommendation.correlationId = 'correlation-001';
    recommendation.tenantKey = 'tenant-demo';
    recommendation.purpose = 'RELATIONSHIP_SERVICE';
    recommendation.externalKey = 'recommendation-001';
    recommendation.workItemId = 'work-001';
    recommendation.subjectEntityId = 'entity-001';
    recommendation.primaryEvidenceId = 'evidence-001';
    recommendation.recommendationType = 'PROACTIVE_UPDATE';
    recommendation.proposedActionType = 'SEND_STATUS_UPDATE';
    recommendation.rationale = 'The customer is waiting for a promised update.';
    recommendation.confidence = 0.91;
    recommendation.modelProfile = 'relationship-recommendation';
    recommendation.modelInvocationId = 'invocation-001';

    HFS_ApprovalRequestCommand approvalRequest = new HFS_ApprovalRequestCommand();
    approvalRequest.contractVersion = HFS_ServiceContract.VERSION;
    approvalRequest.correlationId = 'correlation-001';
    approvalRequest.tenantKey = 'tenant-demo';
    approvalRequest.purpose = 'RELATIONSHIP_SERVICE';
    approvalRequest.externalKey = 'approval-001';
    approvalRequest.recommendationId = 'recommendation-001';
    approvalRequest.policyKey = 'external-message-v1';

    HFS_ApprovalDecisionCommand approvalDecision = new HFS_ApprovalDecisionCommand();
    approvalDecision.contractVersion = HFS_ServiceContract.VERSION;
    approvalDecision.correlationId = 'correlation-001';
    approvalDecision.tenantKey = 'tenant-demo';
    approvalDecision.purpose = 'RELATIONSHIP_SERVICE';
    approvalDecision.approvalId = 'approval-001';
    approvalDecision.decisionStatus = 'APPROVED';
    approvalDecision.decisionNotes = 'Evidence and channel are appropriate.';

    HFS_ActionCommand action = new HFS_ActionCommand();
    action.contractVersion = HFS_ServiceContract.VERSION;
    action.correlationId = 'correlation-001';
    action.tenantKey = 'tenant-demo';
    action.purpose = 'RELATIONSHIP_SERVICE';
    action.externalKey = 'action-001';
    action.idempotencyKey = 'action-001-v1';
    action.recommendationId = 'recommendation-001';
    action.approvalId = 'approval-001';
    action.targetEntityId = 'entity-001';
    action.actionType = 'SEND_STATUS_UPDATE';

    HFS_OutcomeCommand outcome = new HFS_OutcomeCommand();
    outcome.contractVersion = HFS_ServiceContract.VERSION;
    outcome.correlationId = 'correlation-001';
    outcome.tenantKey = 'tenant-demo';
    outcome.purpose = 'RELATIONSHIP_SERVICE';
    outcome.externalKey = 'outcome-001';
    outcome.actionId = 'action-001';
    outcome.sourceEventId = 'event-001';
    outcome.outcomeType = 'MESSAGE_DELIVERED';
    outcome.status = 'SUCCESS';
    outcome.observedAt = System.now();
    outcome.summary = 'The approved update was delivered.';
    outcome.metricKey = 'delivery_success';
    outcome.metricValue = 1;

    System.assertNotEquals(null, service.getContext(contextRequest));
    System.assertNotEquals(null, service.getProvenance(provenanceRequest));
    System.assertNotEquals(
      null,
      service.persistEvent(
        (HFS_EventIntakeCommand) roundTrip(
          eventIntake,
          HFS_EventIntakeCommand.class
        )
      )
    );
    System.assertNotEquals(
      null,
      service.storeRecommendation(
        (HFS_RecommendationCommand) roundTrip(
          recommendation,
          HFS_RecommendationCommand.class
        )
      )
    );
    System.assertNotEquals(
      null,
      service.requestApproval(
        (HFS_ApprovalRequestCommand) roundTrip(
          approvalRequest,
          HFS_ApprovalRequestCommand.class
        )
      )
    );
    System.assertNotEquals(
      null,
      service.decideApproval(
        (HFS_ApprovalDecisionCommand) roundTrip(
          approvalDecision,
          HFS_ApprovalDecisionCommand.class
        )
      )
    );
    System.assertNotEquals(
      null,
      service.logAction(
        (HFS_ActionCommand) roundTrip(action, HFS_ActionCommand.class)
      )
    );
    System.assertNotEquals(
      null,
      service.captureOutcome(
        (HFS_OutcomeCommand) roundTrip(outcome, HFS_OutcomeCommand.class)
      )
    );
  }

  @IsTest
  static void rejectsUnknownAuthorizationOperation() {
    try {
      HFS_AuthorizationMatrix.forOperation('DELETE_SOURCE_EVENT');
      System.assert(false, 'Expected unknown operation to be rejected.');
    } catch (HFS_AuthorizationMatrix.UnknownOperationException expected) {
      System.assert(expected.getMessage().contains('DELETE_SOURCE_EVENT'));
    }
  }

  private static Object roundTrip(Object value, Type targetType) {
    return JSON.deserialize(JSON.serialize(value), targetType);
  }

  private class ContractFixtureService implements HFS_RelationshipService {
    public HFS_ContextResponse getContext(HFS_ContextRequest request) {
      HFS_ContextResponse response = new HFS_ContextResponse();
      response.contractVersion = request.contractVersion;
      response.correlationId = request.correlationId;
      response.tenantKey = request.tenantKey;
      response.generatedAt = System.now();
      response.workItem = contextItemFixture();
      response.entities = new List<HFS_ContextItem>{ contextItemFixture() };
      response.relationships = new List<HFS_ContextItem>{
        contextItemFixture()
      };
      response.eventParticipants = new List<HFS_ContextItem>{
        contextItemFixture()
      };
      response.agreements = new List<HFS_ContextItem>{ contextItemFixture() };
      response.sopExecutions = new List<HFS_ContextItem>{
        contextItemFixture()
      };
      response.timeline = new List<HFS_ContextItem>{ contextItemFixture() };
      response.evidence = new List<HFS_EvidenceCitation>{ citationFixture() };
      response.recommendations = new List<HFS_ContextItem>{
        contextItemFixture()
      };
      response.approvals = new List<HFS_ContextItem>{ contextItemFixture() };
      response.actions = new List<HFS_ContextItem>{ contextItemFixture() };
      response.outcomes = new List<HFS_ContextItem>{ contextItemFixture() };
      response.evaluations = new List<HFS_ContextItem>{ contextItemFixture() };
      response.errors = new List<HFS_ServiceError>();
      return response;
    }

    public HFS_ProvenanceResponse getProvenance(HFS_ProvenanceRequest request) {
      HFS_ProvenanceResponse response = new HFS_ProvenanceResponse();
      response.contractVersion = request.contractVersion;
      response.correlationId = request.correlationId;
      response.tenantKey = request.tenantKey;
      response.rootRecord = contextItemFixture();
      response.lineage = new List<HFS_ContextItem>{ contextItemFixture() };
      response.citations = new List<HFS_EvidenceCitation>{ citationFixture() };
      response.errors = new List<HFS_ServiceError>();
      return response;
    }

    public HFS_CommandResult persistEvent(HFS_EventIntakeCommand command) {
      return result(HFS_ServiceContract.PERSIST_EVENT, command.correlationId);
    }

    public HFS_CommandResult storeRecommendation(
      HFS_RecommendationCommand command
    ) {
      return result(
        HFS_ServiceContract.STORE_RECOMMENDATION,
        command.correlationId
      );
    }

    public HFS_CommandResult requestApproval(
      HFS_ApprovalRequestCommand command
    ) {
      return result(
        HFS_ServiceContract.REQUEST_APPROVAL,
        command.correlationId
      );
    }

    public HFS_CommandResult decideApproval(
      HFS_ApprovalDecisionCommand command
    ) {
      return result(HFS_ServiceContract.DECIDE_APPROVAL, command.correlationId);
    }

    public HFS_CommandResult logAction(HFS_ActionCommand command) {
      return result(HFS_ServiceContract.LOG_ACTION, command.correlationId);
    }

    public HFS_CommandResult captureOutcome(HFS_OutcomeCommand command) {
      return result(HFS_ServiceContract.CAPTURE_OUTCOME, command.correlationId);
    }

    private HFS_CommandResult result(String operation, String correlationId) {
      HFS_CommandResult response = new HFS_CommandResult();
      response.contractVersion = HFS_ServiceContract.VERSION;
      response.correlationId = correlationId;
      response.operation = operation;
      response.success = true;
      response.replayed = false;
      response.recordId = 'record-001';
      response.recordType = 'HFS_Record__c';
      response.status = 'ACCEPTED';
      response.errors = new List<HFS_ServiceError>();
      return response;
    }
  }

  private static HFS_ContextItem contextItemFixture() {
    HFS_ContextItem item = new HFS_ContextItem();
    item.recordId = 'record-001';
    item.objectApiName = 'HFS_Work_Item__c';
    item.externalKey = 'work-001';
    item.recordType = 'WORK_ITEM';
    item.label = 'Customer update';
    item.status = 'IN_PROGRESS';
    item.summary = 'Prepare and approve the next customer update.';
    item.occurredAt = System.now();
    item.sourceEventId = 'event-001';
    item.subjectEntityId = 'entity-001';
    item.objectEntityId = 'entity-002';
    item.relationshipType = 'CUSTOMER_OF';
    item.participantRole = 'SUBJECT';
    item.confidence = 0.98;
    item.sourceUri = 'urn:hfs:source:crm';
    item.contentHash = 'sha256:fixture';
    return item;
  }

  private static HFS_EvidenceCitation citationFixture() {
    HFS_EvidenceCitation citation = new HFS_EvidenceCitation();
    citation.evidenceId = 'evidence-001';
    citation.evidenceType = 'SOURCE_EVENT';
    citation.sourceEventId = 'event-001';
    citation.sourceUri = 'urn:hfs:source:crm';
    citation.contentHash = 'sha256:fixture';
    citation.summary = 'The customer was promised an update.';
    citation.capturedAt = System.now();
    return citation;
  }

  private static HFS_ServiceError errorFixture() {
    HFS_ServiceError error = new HFS_ServiceError();
    error.code = HFS_ServiceContract.PERMISSION_DENIED;
    error.message = 'The current user cannot perform this operation.';
    error.fieldName = 'HFS_Approval__c.Status__c';
    error.retryable = false;
    error.details = 'Required custom permission is missing.';
    return error;
  }
}
