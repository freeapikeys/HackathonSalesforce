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
  private static final Set<String> CLINICAL_ACTION_TYPES = new Set<String>{
    'CLINICAL_TRIAGE_DECISION',
    'CLINICAL_PRIORITY_DECISION',
    'DECIDE_TREATMENT_PRIORITY',
    'DIAGNOSE_PATIENT',
    'RECOMMEND_TREATMENT',
    'PRESCRIBE_TREATMENT',
    'SET_DOSAGE'
  };
  private static final Set<String> PRESERVED_EVENT_RESULTS = new Set<String>{
    'ACCEPTED',
    'ACCEPTED_LATE',
    'ACCEPTED_OUT_OF_ORDER',
    'CONFLICT_REVIEW'
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
      response.eventParticipants = new List<HFS_ContextItem>();
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

  public HFS_CommandResult persistEvent(HFS_EventIntakeCommand command) {
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Event__c,
        'HFS_Event__c'
      );
      HFS_ServiceSupport.requireText(command.eventId, 'eventId');
      HFS_ServiceSupport.requireText(command.sourceUri, 'sourceUri');
      HFS_ServiceSupport.requireText(command.sourceRecordId, 'sourceRecordId');
      HFS_ServiceSupport.requireText(command.eventType, 'eventType');
      HFS_ServiceSupport.requireText(command.subject, 'subject');
      HFS_ServiceSupport.requireText(command.schemaVersion, 'schemaVersion');
      HFS_ServiceSupport.requireText(command.idempotencyKey, 'idempotencyKey');
      requirePresent(command.sourceSequence, 'sourceSequence');
      requirePresent(command.occurredAt, 'occurredAt');
      requirePresent(command.observedAt, 'observedAt');
      HFS_ServiceSupport.requireText(command.contentHash, 'contentHash');
      HFS_ServiceSupport.requireText(command.payloadJson, 'payloadJson');
      HFS_ServiceSupport.requireText(command.intakeResult, 'intakeResult');
      if (!PRESERVED_EVENT_RESULTS.contains(command.intakeResult)) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.INVALID_STATE,
          'Only accepted or review-required intake results are persisted as source events.',
          'intakeResult'
        );
      }

      HFS_Event__c replayedByIdempotency = replayableEventByIdempotency(
        command
      );
      if (replayedByIdempotency != null) {
        return HFS_ServiceSupport.success(
          HFS_ServiceContract.PERSIST_EVENT,
          command.correlationId,
          replayedByIdempotency,
          replayedByIdempotency.Intake_Result__c,
          true
        );
      }

      HFS_Event__c replayedByIdentity = replayableEventByIdentity(command);
      if (replayedByIdentity != null) {
        return HFS_ServiceSupport.success(
          HFS_ServiceContract.PERSIST_EVENT,
          command.correlationId,
          replayedByIdentity,
          replayedByIdentity.Intake_Result__c,
          true
        );
      }

      HFS_Event__c sourceEvent = new HFS_Event__c(
        Event_Id__c = command.eventId,
        Tenant_Key__c = command.tenantKey,
        Event_Type__c = command.eventType,
        Source_URI__c = command.sourceUri,
        Subject__c = command.subject,
        Source_Record_Id__c = command.sourceRecordId,
        Schema_Version__c = command.schemaVersion,
        Correlation_Id__c = command.correlationId,
        Causation_Id__c = command.causationId,
        Idempotency_Key__c = command.idempotencyKey,
        Source_Sequence__c = command.sourceSequence,
        Occurred_At__c = command.occurredAt,
        Observed_At__c = command.observedAt,
        Content_Hash__c = command.contentHash,
        Payload_JSON__c = command.payloadJson,
        Intake_Result__c = command.intakeResult
      );
      insert as user sourceEvent;
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.PERSIST_EVENT,
        command.correlationId,
        sourceEvent,
        sourceEvent.Intake_Result__c,
        false
      );
    } catch (Exception exceptionValue) {
      return HFS_ServiceSupport.failure(
        HFS_ServiceContract.PERSIST_EVENT,
        command == null ? null : command.correlationId,
        exceptionValue
      );
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
      requireNonClinicalActionType(
        command.proposedActionType,
        'proposedActionType'
      );
      HFS_ServiceSupport.requireText(command.rationale, 'rationale');
      HFS_ServiceSupport.requireText(command.modelProfile, 'modelProfile');
      HFS_ServiceSupport.requireText(
        command.modelInvocationId,
        'modelInvocationId'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Recommendation__c,
        'HFS_Recommendation__c'
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
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Approval__c,
        'HFS_Approval__c'
      );

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
    Savepoint transactionStart;
    try {
      validateCommand(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requirePermission('HFS_Approve_Recommendation');
      HFS_ServiceSupport.requireUpdate(
        Schema.SObjectType.HFS_Approval__c,
        'HFS_Approval__c'
      );
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
      Boolean correctionSupersession = isCorrectionSupersessionApproval(
        approval
      );
      if (approval.Status__c != 'PENDING') {
        if (
          approval.Status__c == command.decisionStatus &&
          approval.Decision_Notes__c == command.decisionNotes
        ) {
          if (command.decisionStatus == 'APPROVED' && correctionSupersession) {
            persistApprovedSupersession(command, approval);
          }
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

      if (command.decisionStatus == 'APPROVED' && correctionSupersession) {
        HFS_ServiceSupport.requireUpdate(
          Schema.SObjectType.HFS_Relationship__c,
          'HFS_Relationship__c'
        );
      }

      transactionStart = Database.setSavepoint();
      approval.Status__c = command.decisionStatus;
      approval.Decision_By__c = UserInfo.getUserId();
      approval.Decided_At__c = System.now();
      approval.Decision_Notes__c = command.decisionNotes;
      update as user approval;

      if (command.decisionStatus == 'APPROVED' && correctionSupersession) {
        persistApprovedSupersession(command, approval);
      }
      return HFS_ServiceSupport.success(
        HFS_ServiceContract.DECIDE_APPROVAL,
        command.correlationId,
        approval,
        approval.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      if (transactionStart != null) {
        Database.rollback(transactionStart);
      }
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
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Action__c,
        'HFS_Action__c'
      );
      HFS_ServiceSupport.requireText(command.externalKey, 'externalKey');
      HFS_ServiceSupport.requireText(command.idempotencyKey, 'idempotencyKey');
      HFS_ServiceSupport.requireText(command.actionType, 'actionType');
      requireNonClinicalActionType(command.actionType, 'actionType');

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
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Outcome__c,
        'HFS_Outcome__c'
      );
      HFS_ServiceSupport.requireUpdate(
        Schema.SObjectType.HFS_Action__c,
        'HFS_Action__c'
      );
      HFS_ServiceSupport.requireUpdate(
        Schema.SObjectType.HFS_Work_Item__c,
        'HFS_Work_Item__c'
      );
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
          markTerminalWorkClosure(command.tenantKey, existing);
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
        markTerminalWorkClosure(command.tenantKey, outcome);
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

  private static void requireNonClinicalActionType(
    String actionType,
    String fieldName
  ) {
    if (CLINICAL_ACTION_TYPES.contains(actionType)) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.CLINICAL_DECISION_REFUSED,
        'Logia cannot store or execute diagnosis, treatment, dosage, triage, or clinical priority decisions.',
        fieldName
      );
    }
  }

  private static void requirePresent(Object value, String fieldName) {
    if (value == null) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'A required value is missing.',
        fieldName
      );
    }
  }

  private static HFS_Event__c replayableEventByIdempotency(
    HFS_EventIntakeCommand command
  ) {
    List<HFS_Event__c> records = [
      SELECT Id, Tenant_Key__c, Content_Hash__c, Intake_Result__c
      FROM HFS_Event__c
      WHERE
        Tenant_Key__c = :command.tenantKey
        AND Source_URI__c = :command.sourceUri
        AND Idempotency_Key__c = :command.idempotencyKey
      WITH USER_MODE
      LIMIT 1
    ];
    if (records.isEmpty()) {
      return null;
    }
    HFS_Event__c existing = records[0];
    if (existing.Content_Hash__c == command.contentHash) {
      return existing;
    }
    HFS_ServiceSupport.fail(
      HFS_ServiceContract.IDEMPOTENCY_CONFLICT,
      'The idempotency key was already used for different source data.',
      'idempotencyKey'
    );
    return null;
  }

  private static HFS_Event__c replayableEventByIdentity(
    HFS_EventIntakeCommand command
  ) {
    List<HFS_Event__c> records = [
      SELECT Id, Tenant_Key__c, Content_Hash__c, Intake_Result__c
      FROM HFS_Event__c
      WHERE
        Tenant_Key__c = :command.tenantKey
        AND Source_URI__c = :command.sourceUri
        AND Event_Id__c = :command.eventId
      WITH USER_MODE
      LIMIT 1
    ];
    if (records.isEmpty()) {
      return null;
    }
    HFS_Event__c existing = records[0];
    if (existing.Content_Hash__c == command.contentHash) {
      return existing;
    }
    HFS_ServiceSupport.fail(
      HFS_ServiceContract.IDEMPOTENCY_CONFLICT,
      'The event identity was already used for different source data.',
      'eventId'
    );
    return null;
  }

  private static HFS_Work_Item__c workItem(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'workItemId');
    List<HFS_Work_Item__c> records = [
      SELECT
        Id,
        Tenant_Key__c,
        Status__c,
        Primary_Entity__c,
        Trigger_Event__c,
        Target_Relationship__c,
        Handoff_State__c,
        Closure_Verification_Status__c,
        Closure_Verified_At__c,
        Closure_Outcome__c
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
    List<HFS_Evidence__c> records;
    try {
      records = [
        SELECT Id, Tenant_Key__c, Work_Item__c
        FROM HFS_Evidence__c
        WHERE Id = :value
        WITH USER_MODE
        LIMIT 1
      ];
    } catch (Exception ignored) {
      inaccessibleEvidence();
      return null;
    }
    if (records.isEmpty()) {
      inaccessibleEvidence();
    }
    return records[0];
  }

  private static Boolean isCorrectionSupersessionApproval(
    HFS_Approval__c approval
  ) {
    return approval.Recommendation__r != null &&
      approval.Recommendation__r.Recommendation_Type__c ==
      'RELATIONSHIP_CORRECTION_REVIEW' &&
      approval.Recommendation__r.Proposed_Action_Type__c ==
      'SUPERSEDE_RELATIONSHIP_ASSERTION';
  }

  private static void persistApprovedSupersession(
    HFS_ApprovalDecisionCommand command,
    HFS_Approval__c approval
  ) {
    Id relationshipId = approval
      .Recommendation__r
      .Work_Item__r
      .Target_Relationship__c;
    if (relationshipId == null) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_STATE,
        'A correction review approval requires a target relationship.',
        'approvalId'
      );
    }

    List<HFS_Relationship__c> relationships = [
      SELECT
        Id,
        Tenant_Key__c,
        Valid_From__c,
        Valid_To__c,
        Supersession_Approval__c,
        Superseded_By_User__c,
        Superseded_At__c,
        Supersession_Reason__c
      FROM HFS_Relationship__c
      WHERE Id = :relationshipId
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(relationships, 'approvalId');
    HFS_Relationship__c relationship = relationships[0];
    requireTenant(command.tenantKey, relationship, 'approvalId');
    if (
      relationship.Supersession_Approval__c != null &&
      relationship.Supersession_Approval__c != approval.Id
    ) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_STATE,
        'The relationship has already been superseded by another approval.',
        'approvalId'
      );
    }

    Datetime supersededAt = approval.Decided_At__c == null
      ? System.now()
      : approval.Decided_At__c;
    relationship.Valid_To__c = relationship.Valid_From__c != null &&
      supersededAt < relationship.Valid_From__c
      ? relationship.Valid_From__c
      : supersededAt;
    relationship.Supersession_Approval__c = approval.Id;
    relationship.Superseded_By_User__c = approval.Decision_By__c == null
      ? UserInfo.getUserId()
      : approval.Decision_By__c;
    relationship.Superseded_At__c = supersededAt;
    relationship.Supersession_Reason__c = String.isBlank(command.decisionNotes)
      ? 'Approved relationship correction review.'
      : command.decisionNotes;
    update as user relationship;
  }

  private static void markTerminalWorkClosure(
    String tenantKey,
    HFS_Outcome__c outcome
  ) {
    if (!TERMINAL_OUTCOME_STATUSES.contains(outcome.Status__c)) {
      return;
    }

    HFS_Action__c action = action(String.valueOf(outcome.Action__c));
    HFS_Recommendation__c recommendation = recommendation(
      String.valueOf(action.Recommendation__c)
    );
    HFS_Work_Item__c workItem = workItem(
      String.valueOf(recommendation.Work_Item__c)
    );
    requireTenant(tenantKey, action, 'actionId');
    requireTenant(tenantKey, recommendation, 'actionId');
    requireTenant(tenantKey, workItem, 'actionId');

    workItem.Status__c = 'COMPLETED';
    workItem.Handoff_State__c = 'COMPLETED';
    workItem.Closure_Verification_Status__c = 'VERIFIED';
    workItem.Closure_Verified_At__c = outcome.Observed_At__c == null
      ? System.now()
      : outcome.Observed_At__c;
    workItem.Closure_Outcome__c = outcome.Id;
    update as user workItem;
  }

  private static void inaccessibleEvidence() {
    HFS_ServiceSupport.fail(
      HFS_ServiceContract.SOURCE_EVIDENCE_INACCESSIBLE,
      'The source evidence is missing or inaccessible.',
      'primaryEvidenceId'
    );
  }

  private static HFS_Recommendation__c recommendation(String recordId) {
    Id value = HFS_ServiceSupport.requireId(recordId, 'recommendationId');
    List<HFS_Recommendation__c> records = [
      SELECT
        Id,
        Tenant_Key__c,
        Work_Item__c,
        Work_Item__r.Target_Relationship__c,
        Status__c,
        Recommendation_Type__c,
        Proposed_Action_Type__c
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
      SELECT
        Id,
        Tenant_Key__c,
        Recommendation__c,
        Recommendation__r.Work_Item__c,
        Recommendation__r.Work_Item__r.Target_Relationship__c,
        Recommendation__r.Recommendation_Type__c,
        Recommendation__r.Proposed_Action_Type__c,
        Status__c,
        Decision_By__c,
        Decided_At__c,
        Decision_Notes__c
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
