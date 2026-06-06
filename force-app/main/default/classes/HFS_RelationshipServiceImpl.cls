public with sharing class HFS_RelationshipServiceImpl implements HFS_RelationshipService {
  private static final Set<String> APPROVAL_DECISIONS = new Set<String>{
    'APPROVED',
    'REJECTED',
    'REVOKED'
  };
  private static final Set<String> OUTCOME_STATUSES = new Set<String>{
    'OBSERVED',
    'SUCCESS',
    'PARTIAL',
    'NO_EFFECT',
    'NEGATIVE',
    'UNKNOWN'
  };
  private static final Set<String> TERMINAL_OUTCOME_STATUSES = new Set<String>{
    'SUCCESS',
    'PARTIAL',
    'NO_EFFECT',
    'NEGATIVE'
  };

  public HFS_ContextResponse getContext(HFS_ContextRequest request) {
    try {
      return HFS_ContextAssembler.getContext(request);
    } catch (Exception exceptionValue) {
      HFS_ContextResponse response = new HFS_ContextResponse();
      response.contractVersion = HFS_ServiceContract.VERSION;
      response.correlationId = request == null ? null : request.correlationId;
      response.tenantKey = request == null ? null : request.tenantKey;
      response.generatedAt = System.now();
      response.entities = new List<HFS_ContextItem>();
      response.relationships = new List<HFS_ContextItem>();
      response.agreements = new List<HFS_ContextItem>();
      response.sopExecutions = new List<HFS_ContextItem>();
      response.timeline = new List<HFS_ContextItem>();
      response.evidence = new List<HFS_EvidenceCitation>();
      response.recommendations = new List<HFS_ContextItem>();
      response.approvals = new List<HFS_ContextItem>();
      response.actions = new List<HFS_ContextItem>();
      response.outcomes = new List<HFS_ContextItem>();
      response.evaluations = new List<HFS_ContextItem>();
      response.errors = new List<HFS_ServiceError>{
        HFS_ServiceSupport.error(exceptionValue)
      };
      return response;
    }
  }

  public HFS_ProvenanceResponse getProvenance(HFS_ProvenanceRequest request) {
    try {
      return HFS_ContextAssembler.getProvenance(request);
    } catch (Exception exceptionValue) {
      HFS_ProvenanceResponse response = new HFS_ProvenanceResponse();
      response.contractVersion = HFS_ServiceContract.VERSION;
      response.correlationId = request == null ? null : request.correlationId;
      response.tenantKey = request == null ? null : request.tenantKey;
      response.lineage = new List<HFS_ContextItem>();
      response.citations = new List<HFS_EvidenceCitation>();
      response.errors = new List<HFS_ServiceError>{
        HFS_ServiceSupport.error(exceptionValue)
      };
      return response;
    }
  }

  public HFS_CommandResult storeRecommendation(
    HFS_RecommendationCommand command
  ) {
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requireText(command.externalKey, 'externalKey');
      HFS_ServiceSupport.requireText(
        command.recommendationType,
        'recommendationType'
      );
      HFS_ServiceSupport.requireText(
        command.proposedActionType,
        'proposedActionType'
      );
      HFS_ServiceSupport.requireText(command.rationale, 'rationale');
      HFS_ServiceSupport.requireText(command.modelProfile, 'modelProfile');
      HFS_ServiceSupport.requireText(
        command.modelInvocationId,
        'modelInvocationId'
      );
      if (
        command.confidence != null &&
        (command.confidence < 0 ||
        command.confidence > 1)
      ) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.VALIDATION_FAILED,
          'Confidence must be between zero and one.',
          'confidence'
        );
      }

      List<HFS_Recommendation__c> existingRecords = [
        SELECT
          Id,
          External_Key__c,
          Tenant_Key__c,
          Work_Item__c,
          Subject_Entity__c,
          Primary_Evidence__c,
          Status__c,
          Recommendation_Type__c,
          Proposed_Action_Type__c,
          Rationale__c,
          Confidence__c,
          Model_Profile__c,
          Model_Invocation_Id__c
        FROM HFS_Recommendation__c
        WHERE External_Key__c = :command.externalKey
        WITH USER_MODE
        LIMIT 1
      ];
      if (!existingRecords.isEmpty()) {
        HFS_Recommendation__c existing = existingRecords[0];
        HFS_ServiceSupport.requireTenant(
          command.tenantKey,
          existing.Tenant_Key__c,
          'externalKey'
        );
        if (recommendationMatches(existing, command)) {
          return HFS_ServiceSupport.success(
            HFS_ServiceContract.STORE_RECOMMENDATION,
            command.correlationId,
            existing,
            existing.Status__c,
            true
          );
        }
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.IDEMPOTENCY_CONFLICT,
          'The recommendation key was already used for different content.',
          'externalKey'
        );
      }

      HFS_Work_Item__c workItem = workItem(command.workItemId);
      HFS_Entity__c subjectEntity = entity(command.subjectEntityId);
      HFS_Evidence__c primaryEvidence = evidence(command.primaryEvidenceId);
      requireTenant(command.tenantKey, workItem, 'workItemId');
      requireTenant(command.tenantKey, subjectEntity, 'subjectEntityId');
      requireTenant(command.tenantKey, primaryEvidence, 'primaryEvidenceId');
      if (primaryEvidence.Work_Item__c != workItem.Id) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.VALIDATION_FAILED,
          'Primary evidence must belong to the recommendation work item.',
          'primaryEvidenceId'
        );
      }

      HFS_Recommendation__c recommendation = new HFS_Recommendation__c(
        External_Key__c = command.externalKey,
        Tenant_Key__c = command.tenantKey,
        Work_Item__c = workItem.Id,
        Subject_Entity__c = subjectEntity.Id,
        Primary_Evidence__c = primaryEvidence.Id,
        Status__c = 'DRAFT',
        Recommendation_Type__c = command.recommendationType,
        Proposed_Action_Type__c = command.proposedActionType,
        Rationale__c = command.rationale,
        Confidence__c = command.confidence,
        Model_Profile__c = command.modelProfile,
        Model_Invocation_Id__c = command.modelInvocationId,
        Generated_At__c = System.now()
      );
      insert as user recommendation;
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.STORE_RECOMMENDATION,
        command.correlationId,
        recommendation,
        recommendation.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      return HFS_ServiceSupport.failure(
        HFS_ServiceContract.STORE_RECOMMENDATION,
        command == null ? null : command.correlationId,
        exceptionValue
      );
    }
  }

  public HFS_CommandResult requestApproval(HFS_ApprovalRequestCommand command) {
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requireText(command.externalKey, 'externalKey');
      HFS_ServiceSupport.requireText(command.policyKey, 'policyKey');

      List<HFS_Approval__c> existingRecords = [
        SELECT
          Id,
          External_Key__c,
          Tenant_Key__c,
          Recommendation__c,
          Status__c,
          Policy_Key__c
        FROM HFS_Approval__c
        WHERE External_Key__c = :command.externalKey
        WITH USER_MODE
        LIMIT 1
      ];
      if (!existingRecords.isEmpty()) {
        HFS_Approval__c existing = existingRecords[0];
        HFS_ServiceSupport.requireTenant(
          command.tenantKey,
          existing.Tenant_Key__c,
          'externalKey'
        );
        if (
          HFS_ServiceSupport.same(
            existing.Recommendation__c,
            command.recommendationId
          ) && existing.Policy_Key__c == command.policyKey
        ) {
          return HFS_ServiceSupport.success(
            HFS_ServiceContract.REQUEST_APPROVAL,
            command.correlationId,
            existing,
            existing.Status__c,
            true
          );
        }
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.IDEMPOTENCY_CONFLICT,
          'The approval key was already used for a different request.',
          'externalKey'
        );
      }

      HFS_Recommendation__c recommendation = recommendation(
        command.recommendationId
      );
      requireTenant(command.tenantKey, recommendation, 'recommendationId');
      if (
        recommendation.Status__c == 'REJECTED' ||
        recommendation.Status__c == 'EXPIRED'
      ) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.INVALID_STATE,
          'The recommendation cannot enter approval from its current state.',
          'recommendationId'
        );
      }

      HFS_Approval__c approval = new HFS_Approval__c(
        External_Key__c = command.externalKey,
        Tenant_Key__c = command.tenantKey,
        Recommendation__c = recommendation.Id,
        Status__c = 'PENDING',
        Requested_At__c = System.now(),
        Policy_Key__c = command.policyKey
      );
      insert as user approval;
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.REQUEST_APPROVAL,
        command.correlationId,
        approval,
        approval.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      return HFS_ServiceSupport.failure(
        HFS_ServiceContract.REQUEST_APPROVAL,
        command == null ? null : command.correlationId,
        exceptionValue
      );
    }
  }

  public HFS_CommandResult decideApproval(HFS_ApprovalDecisionCommand command) {
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requirePermission('HFS_Approve_Recommendation');
      HFS_ServiceSupport.requireText(command.decisionStatus, 'decisionStatus');
      if (!APPROVAL_DECISIONS.contains(command.decisionStatus)) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.VALIDATION_FAILED,
          'The approval decision is not supported.',
          'decisionStatus'
        );
      }

      HFS_Approval__c approval = approval(command.approvalId);
      requireTenant(command.tenantKey, approval, 'approvalId');
      if (approval.Status__c != 'PENDING') {
        if (
          approval.Status__c == command.decisionStatus &&
          approval.Decision_Notes__c == command.decisionNotes
        ) {
          return HFS_ServiceSupport.success(
            HFS_ServiceContract.DECIDE_APPROVAL,
            command.correlationId,
            approval,
            approval.Status__c,
            true
          );
        }
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.INVALID_STATE,
          'Only a pending approval can be decided.',
          'approvalId'
        );
      }

      approval.Status__c = command.decisionStatus;
      approval.Decision_By__c = UserInfo.getUserId();
      approval.Decided_At__c = System.now();
      approval.Decision_Notes__c = command.decisionNotes;
      update as user approval;
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.DECIDE_APPROVAL,
        command.correlationId,
        approval,
        approval.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      return HFS_ServiceSupport.failure(
        HFS_ServiceContract.DECIDE_APPROVAL,
        command == null ? null : command.correlationId,
        exceptionValue
      );
    }
  }

  public HFS_CommandResult logAction(HFS_ActionCommand command) {
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requirePermission('HFS_Execute_Action');
      HFS_ServiceSupport.requireText(command.externalKey, 'externalKey');
      HFS_ServiceSupport.requireText(command.idempotencyKey, 'idempotencyKey');
      HFS_ServiceSupport.requireText(command.actionType, 'actionType');

      List<HFS_Action__c> existingRecords = [
        SELECT
          Id,
          External_Key__c,
          Tenant_Key__c,
          Recommendation__c,
          Approval__c,
          Target_Entity__c,
          Status__c,
          Action_Type__c,
          Correlation_Id__c,
          Idempotency_Key__c
        FROM HFS_Action__c
        WHERE
          External_Key__c = :command.externalKey
          OR Idempotency_Key__c = :command.idempotencyKey
        WITH USER_MODE
        LIMIT 1
      ];
      if (!existingRecords.isEmpty()) {
        HFS_Action__c existing = existingRecords[0];
        HFS_ServiceSupport.requireTenant(
          command.tenantKey,
          existing.Tenant_Key__c,
          'idempotencyKey'
        );
        if (actionMatches(existing, command)) {
          return HFS_ServiceSupport.success(
            HFS_ServiceContract.LOG_ACTION,
            command.correlationId,
            existing,
            existing.Status__c,
            true
          );
        }
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.IDEMPOTENCY_CONFLICT,
          'The action key was already used for different content.',
          'idempotencyKey'
        );
      }

      HFS_Recommendation__c recommendation = recommendation(
        command.recommendationId
      );
      HFS_Approval__c approval = approval(command.approvalId);
      HFS_Entity__c targetEntity = entity(command.targetEntityId);
      requireTenant(command.tenantKey, recommendation, 'recommendationId');
      requireTenant(command.tenantKey, approval, 'approvalId');
      requireTenant(command.tenantKey, targetEntity, 'targetEntityId');
      if (
        approval.Recommendation__c != recommendation.Id ||
        approval.Status__c != 'APPROVED'
      ) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.INVALID_STATE,
          'An approved approval for the same recommendation is required.',
          'approvalId'
        );
      }

      HFS_Action__c action = new HFS_Action__c(
        External_Key__c = command.externalKey,
        Tenant_Key__c = command.tenantKey,
        Recommendation__c = recommendation.Id,
        Approval__c = approval.Id,
        Target_Entity__c = targetEntity.Id,
        Status__c = 'PENDING',
        Action_Type__c = command.actionType,
        Requested_At__c = System.now(),
        Correlation_Id__c = command.correlationId,
        Idempotency_Key__c = command.idempotencyKey
      );
      insert as user action;
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.LOG_ACTION,
        command.correlationId,
        action,
        action.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      return HFS_ServiceSupport.failure(
        HFS_ServiceContract.LOG_ACTION,
        command == null ? null : command.correlationId,
        exceptionValue
      );
    }
  }

  public HFS_CommandResult captureOutcome(HFS_OutcomeCommand command) {
    Savepoint transactionStart;
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requirePermission('HFS_Execute_Action');
      HFS_ServiceSupport.requireText(command.externalKey, 'externalKey');
      HFS_ServiceSupport.requireText(command.outcomeType, 'outcomeType');
      HFS_ServiceSupport.requireText(command.status, 'status');
      if (!OUTCOME_STATUSES.contains(command.status)) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.VALIDATION_FAILED,
          'The outcome status is not supported.',
          'status'
        );
      }

      List<HFS_Outcome__c> existingRecords = [
        SELECT
          Id,
          External_Key__c,
          Tenant_Key__c,
          Action__c,
          Source_Event__c,
          Outcome_Type__c,
          Status__c,
          Observed_At__c,
          Summary__c,
          Metric_Key__c,
          Metric_Value__c
        FROM HFS_Outcome__c
        WHERE External_Key__c = :command.externalKey
        WITH USER_MODE
        LIMIT 1
      ];
      if (!existingRecords.isEmpty()) {
        HFS_Outcome__c existing = existingRecords[0];
        HFS_ServiceSupport.requireTenant(
          command.tenantKey,
          existing.Tenant_Key__c,
          'externalKey'
        );
        if (outcomeMatches(existing, command)) {
          return HFS_ServiceSupport.success(
            HFS_ServiceContract.CAPTURE_OUTCOME,
            command.correlationId,
            existing,
            existing.Status__c,
            true
          );
        }
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.IDEMPOTENCY_CONFLICT,
          'The outcome key was already used for different content.',
          'externalKey'
        );
      }

      HFS_Action__c action = action(command.actionId);
      HFS_Event__c sourceEvent = eventRecord(command.sourceEventId);
      requireTenant(command.tenantKey, action, 'actionId');
      requireTenant(command.tenantKey, sourceEvent, 'sourceEventId');
      if (action.Status__c == 'FAILED' || action.Status__c == 'CANCELLED') {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.INVALID_STATE,
          'An outcome cannot be captured for this action state.',
          'actionId'
        );
      }

      transactionStart = Database.setSavepoint();
      Datetime observedAt = command.observedAt == null
        ? System.now()
        : command.observedAt;
      HFS_Outcome__c outcome = new HFS_Outcome__c(
        External_Key__c = command.externalKey,
        Tenant_Key__c = command.tenantKey,
        Action__c = action.Id,
        Source_Event__c = sourceEvent.Id,
        Outcome_Type__c = command.outcomeType,
        Status__c = command.status,
        Observed_At__c = observedAt,
        Summary__c = command.summary,
        Metric_Key__c = command.metricKey,
        Metric_Value__c = command.metricValue
      );
      insert as user outcome;

      action.Status__c = 'EXECUTED';
      action.Executed_At__c = observedAt;
      update as user action;

      if (TERMINAL_OUTCOME_STATUSES.contains(command.status)) {
        HFS_Recommendation__c recommendation = recommendation(
          String.valueOf(action.Recommendation__c)
        );
        HFS_Work_Item__c workItem = workItem(
          String.valueOf(recommendation.Work_Item__c)
        );
        requireTenant(command.tenantKey, recommendation, 'actionId');
        requireTenant(command.tenantKey, workItem, 'actionId');
        workItem.Status__c = 'COMPLETED';
        update as user workItem;
      }
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.CAPTURE_OUTCOME,
        command.correlationId,
        outcome,
        outcome.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      if (transactionStart != null) {
        Database.rollback(transactionStart);
      }
      return HFS_ServiceSupport.failure(
        HFS_ServiceContract.CAPTURE_OUTCOME,
        command == null ? null : command.correlationId,
        exceptionValue
      );
    }
  }

  private static void validateCommand(
    String contractVersion,
    String tenantKey,
    String purpose,
    String correlationId
  ) {
    HFS_ServiceSupport.validateRequest(
      contractVersion,
      tenantKey,
      purpose,
      correlationId
    );
  }

  private static HFS_Work_Item__c workItem(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'workItemId');
    List<HFS_Work_Item__c> records = [
      SELECT Id, Tenant_Key__c, Status__c, Primary_Entity__c, Trigger_Event__c
      FROM HFS_Work_Item__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'workItemId');
    return records[0];
  }

  private static HFS_Entity__c entity(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'subjectEntityId');
    List<HFS_Entity__c> records = [
      SELECT Id, Tenant_Key__c
      FROM HFS_Entity__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'subjectEntityId');
    return records[0];
  }

  private static HFS_Evidence__c evidence(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'primaryEvidenceId');
    List<HFS_Evidence__c> records = [
      SELECT Id, Tenant_Key__c, Work_Item__c
      FROM HFS_Evidence__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'primaryEvidenceId');
    return records[0];
  }

  private static HFS_Recommendation__c recommendation(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'recommendationId');
    List<HFS_Recommendation__c> records = [
      SELECT Id, Tenant_Key__c, Work_Item__c, Status__c
      FROM HFS_Recommendation__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'recommendationId');
    return records[0];
  }

  private static HFS_Approval__c approval(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'approvalId');
    List<HFS_Approval__c> records = [
      SELECT Id, Tenant_Key__c, Recommendation__c, Status__c, Decision_Notes__c
      FROM HFS_Approval__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'approvalId');
    return records[0];
  }

  private static HFS_Action__c action(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'actionId');
    List<HFS_Action__c> records = [
      SELECT Id, Tenant_Key__c, Recommendation__c, Status__c, Executed_At__c
      FROM HFS_Action__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'actionId');
    return records[0];
  }

  private static HFS_Event__c eventRecord(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'sourceEventId');
    List<HFS_Event__c> records = [
      SELECT Id, Tenant_Key__c
      FROM HFS_Event__c
      WHERE Id = :value
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'sourceEventId');
    return records[0];
  }

  private static void requireRecord(List<SObject> records, String fieldName) {
    if (records.isEmpty()) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.RECORD_NOT_FOUND,
        'No accessible referenced record was found.',
        fieldName
      );
    }
  }

  private static void requireTenant(
    String tenantKey,
    SObject recordValue,
    String fieldName
  ) {
    HFS_ServiceSupport.requireTenant(
      tenantKey,
      (String) recordValue.get('Tenant_Key__c'),
      fieldName
    );
  }

  private static Boolean recommendationMatches(
    HFS_Recommendation__c existing,
    HFS_RecommendationCommand command
  ) {
    return existing.Tenant_Key__c == command.tenantKey &&
      HFS_ServiceSupport.same(existing.Work_Item__c, command.workItemId) &&
      HFS_ServiceSupport.same(
        existing.Subject_Entity__c,
        command.subjectEntityId
      ) &&
      HFS_ServiceSupport.same(
        existing.Primary_Evidence__c,
        command.primaryEvidenceId
      ) &&
      existing.Recommendation_Type__c == command.recommendationType &&
      existing.Proposed_Action_Type__c == command.proposedActionType &&
      existing.Rationale__c == command.rationale &&
      HFS_ServiceSupport.same(existing.Confidence__c, command.confidence) &&
      existing.Model_Profile__c == command.modelProfile &&
      existing.Model_Invocation_Id__c == command.modelInvocationId;
  }

  private static Boolean actionMatches(
    HFS_Action__c existing,
    HFS_ActionCommand command
  ) {
    return existing.External_Key__c == command.externalKey &&
      existing.Idempotency_Key__c == command.idempotencyKey &&
      existing.Tenant_Key__c == command.tenantKey &&
      HFS_ServiceSupport.same(
        existing.Recommendation__c,
        command.recommendationId
      ) &&
      HFS_ServiceSupport.same(existing.Approval__c, command.approvalId) &&
      HFS_ServiceSupport.same(
        existing.Target_Entity__c,
        command.targetEntityId
      ) &&
      existing.Action_Type__c == command.actionType &&
      existing.Correlation_Id__c == command.correlationId;
  }

  private static Boolean outcomeMatches(
    HFS_Outcome__c existing,
    HFS_OutcomeCommand command
  ) {
    return existing.Tenant_Key__c == command.tenantKey &&
      HFS_ServiceSupport.same(existing.Action__c, command.actionId) &&
      HFS_ServiceSupport.same(
        existing.Source_Event__c,
        command.sourceEventId
      ) &&
      existing.Outcome_Type__c == command.outcomeType &&
      existing.Status__c == command.status &&
      (command.observedAt == null ||
      HFS_ServiceSupport.same(existing.Observed_At__c, command.observedAt)) &&
      existing.Summary__c == command.summary &&
      existing.Metric_Key__c == command.metricKey &&
      HFS_ServiceSupport.same(existing.Metric_Value__c, command.metricValue);
  }
}
