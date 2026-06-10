public with sharing class HFS_ContextAssembler {
  private static final Set<String> PROVENANCE_OBJECTS = new Set<String>{
    'HFS_Event__c',
    'HFS_Entity__c',
    'HFS_Relationship__c',
    'HFS_Event_Participant__c',
    'HFS_Agreement__c',
    'HFS_Work_Item__c',
    'HFS_SOP_Execution__c',
    'HFS_Evidence__c',
    'HFS_Recommendation__c',
    'HFS_Approval__c',
    'HFS_Action__c',
    'HFS_Outcome__c',
    'HFS_Evaluation__c'
  };

  public static HFS_ContextResponse getContext(HFS_ContextRequest request) {
    HFS_ServiceSupport.validateRequest(
      request == null ? null : request.contractVersion,
      request == null ? null : request.tenantKey,
      request == null ? null : request.purpose,
      request == null ? null : request.correlationId
    );
    if (
      String.isBlank(request.workItemId) &&
      String.isBlank(request.subjectEntityId)
    ) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'A work item or subject entity is required.',
        'workItemId'
      );
    }

    HFS_Work_Item__c workItem = loadWorkItem(request);
    HFS_ServiceSupport.requireTenant(
      request.tenantKey,
      workItem.Tenant_Key__c,
      'workItemId'
    );

    List<HFS_Evidence__c> evidenceRecords = evidenceForWork(workItem.Id);
    List<HFS_SOP_Execution__c> sopRecords = [
      SELECT
        Id,
        Name,
        External_Key__c,
        Tenant_Key__c,
        Work_Item__c,
        Definition_Key__c,
        Definition_Version__c,
        Current_Step_Key__c,
        Status__c,
        Started_At__c,
        Completed_At__c
      FROM HFS_SOP_Execution__c
      WHERE Work_Item__c = :workItem.Id
      WITH USER_MODE
      ORDER BY Started_At__c DESC
    ];
    List<HFS_Recommendation__c> recommendationRecords = [
      SELECT
        Id,
        Name,
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
        Model_Invocation_Id__c,
        Generated_At__c
      FROM HFS_Recommendation__c
      WHERE Work_Item__c = :workItem.Id
      WITH USER_MODE
      ORDER BY Generated_At__c DESC
    ];

    Set<Id> recommendationIds = ids(recommendationRecords);
    List<HFS_Approval__c> approvalRecords = new List<HFS_Approval__c>();
    List<HFS_Action__c> actionRecords = new List<HFS_Action__c>();
    if (!recommendationIds.isEmpty()) {
      approvalRecords = [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Recommendation__c,
          Status__c,
          Requested_At__c,
          Decision_By__c,
          Decided_At__c,
          Decision_Notes__c,
          Policy_Key__c
        FROM HFS_Approval__c
        WHERE Recommendation__c IN :recommendationIds
        WITH USER_MODE
        ORDER BY Requested_At__c DESC
      ];
      actionRecords = [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Recommendation__c,
          Approval__c,
          Target_Entity__c,
          Status__c,
          Action_Type__c,
          Requested_At__c,
          Executed_At__c,
          Correlation_Id__c,
          Idempotency_Key__c,
          External_Reference__c,
          Failure_Detail__c
        FROM HFS_Action__c
        WHERE Recommendation__c IN :recommendationIds
        WITH USER_MODE
        ORDER BY Requested_At__c DESC
      ];
    }

    Set<Id> actionIds = ids(actionRecords);
    List<HFS_Outcome__c> outcomeRecords = new List<HFS_Outcome__c>();
    if (!actionIds.isEmpty()) {
      outcomeRecords = [
        SELECT
          Id,
          Name,
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
        WHERE Action__c IN :actionIds
        WITH USER_MODE
        ORDER BY Observed_At__c DESC
      ];
    }

    Set<Id> outcomeIds = ids(outcomeRecords);
    List<HFS_Evaluation__c> evaluationRecords = new List<HFS_Evaluation__c>();
    if (!outcomeIds.isEmpty()) {
      evaluationRecords = [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Outcome__c,
          Evaluation_Type__c,
          Evaluator_Type__c,
          Evaluator_Id__c,
          Score__c,
          Verdict__c,
          Notes__c,
          Evaluated_At__c
        FROM HFS_Evaluation__c
        WHERE Outcome__c IN :outcomeIds
        WITH USER_MODE
        ORDER BY Evaluated_At__c DESC
      ];
    }

    Set<Id> sourceEventIds = new Set<Id>{ workItem.Trigger_Event__c };
    Set<Id> entityIds = new Set<Id>{ workItem.Primary_Entity__c };
    for (HFS_Evidence__c evidence : evidenceRecords) {
      sourceEventIds.add(evidence.Source_Event__c);
      if (evidence.Related_Entity__c != null) {
        entityIds.add(evidence.Related_Entity__c);
      }
    }
    for (HFS_Recommendation__c recommendation : recommendationRecords) {
      entityIds.add(recommendation.Subject_Entity__c);
    }
    for (HFS_Action__c action : actionRecords) {
      entityIds.add(action.Target_Entity__c);
    }
    for (HFS_Outcome__c outcome : outcomeRecords) {
      sourceEventIds.add(outcome.Source_Event__c);
    }

    List<HFS_Event_Participant__c> participantRecords = [
      SELECT
        Id,
        Name,
        External_Key__c,
        Tenant_Key__c,
        Event__c,
        Entity__c,
        Participant_Role__c
      FROM HFS_Event_Participant__c
      WHERE Event__c IN :sourceEventIds
      WITH USER_MODE
    ];
    for (HFS_Event_Participant__c participant : participantRecords) {
      entityIds.add(participant.Entity__c);
    }

    List<HFS_Relationship__c> relationshipRecords = [
      SELECT
        Id,
        Name,
        External_Key__c,
        Tenant_Key__c,
        Subject_Entity__c,
        Object_Entity__c,
        Relationship_Type__c,
        Source_Event__c,
        Valid_From__c,
        Valid_To__c,
        Confidence__c
      FROM HFS_Relationship__c
      WHERE Subject_Entity__c IN :entityIds OR Object_Entity__c IN :entityIds
      WITH USER_MODE
    ];
    for (HFS_Relationship__c relationship : relationshipRecords) {
      entityIds.add(relationship.Subject_Entity__c);
      entityIds.add(relationship.Object_Entity__c);
      sourceEventIds.add(relationship.Source_Event__c);
    }
    List<HFS_Agreement__c> agreementRecords = [
      SELECT
        Id,
        Name,
        External_Key__c,
        Tenant_Key__c,
        Party_One__c,
        Party_Two__c,
        Agreement_Type__c,
        Status__c,
        Terms_Summary__c,
        Source_Event__c,
        Effective_From__c,
        Effective_To__c
      FROM HFS_Agreement__c
      WHERE Party_One__c IN :entityIds OR Party_Two__c IN :entityIds
      WITH USER_MODE
    ];
    for (HFS_Agreement__c agreement : agreementRecords) {
      entityIds.add(agreement.Party_One__c);
      entityIds.add(agreement.Party_Two__c);
      sourceEventIds.add(agreement.Source_Event__c);
    }

    List<HFS_Entity__c> entityRecords = [
      SELECT
        Id,
        Name,
        External_Key__c,
        Tenant_Key__c,
        Display_Name__c,
        Entity_Type__c,
        Source_Event__c,
        Valid_From__c,
        Valid_To__c,
        Confidence__c
      FROM HFS_Entity__c
      WHERE Id IN :entityIds
      WITH USER_MODE
      ORDER BY Display_Name__c
    ];
    for (HFS_Entity__c entity : entityRecords) {
      sourceEventIds.add(entity.Source_Event__c);
    }

    List<HFS_Event__c> eventRecords = [
      SELECT
        Id,
        Name,
        Event_Id__c,
        Tenant_Key__c,
        Event_Type__c,
        Subject__c,
        Source_URI__c,
        Content_Hash__c,
        Occurred_At__c,
        Observed_At__c,
        Correlation_Id__c,
        Intake_Result__c
      FROM HFS_Event__c
      WHERE Id IN :sourceEventIds
      WITH USER_MODE
      ORDER BY Occurred_At__c DESC
    ];

    validateTenants(
      request.tenantKey,
      new List<List<SObject>>{
        toSObjects(evidenceRecords),
        toSObjects(sopRecords),
        toSObjects(recommendationRecords),
        toSObjects(approvalRecords),
        toSObjects(actionRecords),
        toSObjects(outcomeRecords),
        toSObjects(evaluationRecords),
        toSObjects(participantRecords),
        toSObjects(relationshipRecords),
        toSObjects(agreementRecords),
        toSObjects(entityRecords),
        toSObjects(eventRecords)
      }
    );

    HFS_ContextResponse response = emptyContext(request);
    response.workItem = item(workItem);
    response.entities = items(entityRecords);
    response.relationships = items(relationshipRecords);
    response.eventParticipants = items(participantRecords);
    response.agreements = items(agreementRecords);
    response.sopExecutions = items(sopRecords);
    response.evidence = citations(evidenceRecords);
    response.recommendations = items(recommendationRecords);
    response.approvals = items(approvalRecords);
    response.actions = items(actionRecords);
    response.outcomes = items(outcomeRecords);
    response.evaluations = items(evaluationRecords);

    List<HFS_ContextItem> timeline = new List<HFS_ContextItem>();
    timeline.addAll(items(eventRecords));
    timeline.addAll(items(recommendationRecords));
    timeline.addAll(items(approvalRecords));
    timeline.addAll(items(actionRecords));
    timeline.addAll(items(outcomeRecords));
    timeline.addAll(items(evaluationRecords));
    response.timeline = sortTimeline(
      timeline,
      request.timelineLimit == null ? 100 : request.timelineLimit
    );
    return response;
  }

  public static HFS_ProvenanceResponse getProvenance(
    HFS_ProvenanceRequest request
  ) {
    HFS_ServiceSupport.validateRequest(
      request == null ? null : request.contractVersion,
      request == null ? null : request.tenantKey,
      request == null ? null : request.purpose,
      request == null ? null : request.correlationId
    );
    HFS_ServiceSupport.requireText(request.objectApiName, 'objectApiName');
    Id recordId = HFS_ServiceSupport.requireId(request.recordId, 'recordId');
    if (!PROVENANCE_OBJECTS.contains(request.objectApiName)) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'The requested object is not supported for provenance.',
        'objectApiName'
      );
    }

    ProvenanceSeed seed = provenanceSeed(
      request.objectApiName,
      recordId,
      request.tenantKey
    );
    HFS_ProvenanceResponse response = new HFS_ProvenanceResponse();
    response.contractVersion = HFS_ServiceContract.VERSION;
    response.correlationId = request.correlationId;
    response.tenantKey = request.tenantKey;
    response.rootRecord = seed.root;
    response.lineage = new List<HFS_ContextItem>();
    response.citations = new List<HFS_EvidenceCitation>();
    response.errors = new List<HFS_ServiceError>();

    Integer maxDepth = request.maxDepth == null
      ? 4
      : Math.max(0, Math.min(4, request.maxDepth));
    if (maxDepth == 0) {
      return response;
    }

    if (!seed.evidenceIds.isEmpty()) {
      List<HFS_Evidence__c> evidenceRecords = evidenceByIds(seed.evidenceIds);
      for (HFS_Evidence__c evidence : evidenceRecords) {
        HFS_ServiceSupport.requireTenant(
          request.tenantKey,
          evidence.Tenant_Key__c,
          'recordId'
        );
        response.lineage.add(item(evidence));
        response.citations.add(citation(evidence));
        seed.eventIds.add(evidence.Source_Event__c);
      }
    }

    if (maxDepth > 1 && !seed.eventIds.isEmpty()) {
      List<HFS_Event__c> eventRecords = [
        SELECT
          Id,
          Name,
          Event_Id__c,
          Tenant_Key__c,
          Event_Type__c,
          Subject__c,
          Source_URI__c,
          Content_Hash__c,
          Occurred_At__c,
          Observed_At__c,
          Correlation_Id__c,
          Intake_Result__c
        FROM HFS_Event__c
        WHERE Id IN :seed.eventIds
        WITH USER_MODE
        ORDER BY Occurred_At__c DESC
      ];
      for (HFS_Event__c eventRecord : eventRecords) {
        HFS_ServiceSupport.requireTenant(
          request.tenantKey,
          eventRecord.Tenant_Key__c,
          'recordId'
        );
        if (eventRecord.Id != recordId) {
          response.lineage.add(item(eventRecord));
        }
      }
    }
    return response;
  }

  private static HFS_Work_Item__c loadWorkItem(HFS_ContextRequest request) {
    List<HFS_Work_Item__c> records;
    if (!String.isBlank(request.workItemId)) {
      Id workItemId = HFS_ServiceSupport.requireId(
        request.workItemId,
        'workItemId'
      );
      records = [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Primary_Entity__c,
          Trigger_Event__c,
          Status__c,
          Priority__c,
          Summary__c,
          Due_At__c,
          Blocked_Reason__c,
          Owner.Name,
          CreatedDate
        FROM HFS_Work_Item__c
        WHERE Id = :workItemId
        WITH USER_MODE
        LIMIT 1
      ];
    } else {
      Id subjectEntityId = HFS_ServiceSupport.requireId(
        request.subjectEntityId,
        'subjectEntityId'
      );
      records = [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Primary_Entity__c,
          Trigger_Event__c,
          Status__c,
          Priority__c,
          Summary__c,
          Due_At__c,
          Blocked_Reason__c,
          Owner.Name,
          CreatedDate
        FROM HFS_Work_Item__c
        WHERE Primary_Entity__c = :subjectEntityId
        WITH USER_MODE
        ORDER BY CreatedDate DESC
        LIMIT 1
      ];
    }
    if (records.isEmpty()) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.RECORD_NOT_FOUND,
        'No accessible work item was found.',
        'workItemId'
      );
    }
    return records[0];
  }

  private static ProvenanceSeed provenanceSeed(
    String objectApiName,
    Id recordId,
    String tenantKey
  ) {
    ProvenanceSeed seed = new ProvenanceSeed();
    switch on objectApiName {
      when 'HFS_Event__c' {
        HFS_Event__c recordValue = oneEvent(recordId);
        requireRootTenant(tenantKey, recordValue);
        seed.root = item(recordValue);
        seed.eventIds.add(recordValue.Id);
      }
      when 'HFS_Entity__c' {
        List<HFS_Entity__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Display_Name__c,
            Entity_Type__c,
            Source_Event__c,
            Valid_From__c,
            Valid_To__c,
            Confidence__c
          FROM HFS_Entity__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Source_Event__c);
      }
      when 'HFS_Relationship__c' {
        List<HFS_Relationship__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Subject_Entity__c,
            Object_Entity__c,
            Relationship_Type__c,
            Source_Event__c,
            Valid_From__c,
            Valid_To__c,
            Confidence__c
          FROM HFS_Relationship__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Source_Event__c);
      }
      when 'HFS_Event_Participant__c' {
        List<HFS_Event_Participant__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Event__c,
            Entity__c,
            Participant_Role__c
          FROM HFS_Event_Participant__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Event__c);
      }
      when 'HFS_Agreement__c' {
        List<HFS_Agreement__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Party_One__c,
            Party_Two__c,
            Agreement_Type__c,
            Status__c,
            Terms_Summary__c,
            Source_Event__c,
            Effective_From__c,
            Effective_To__c
          FROM HFS_Agreement__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Source_Event__c);
      }
      when 'HFS_Work_Item__c' {
        List<HFS_Work_Item__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Primary_Entity__c,
            Trigger_Event__c,
            Status__c,
            Priority__c,
            Summary__c,
            Due_At__c,
            Blocked_Reason__c,
            CreatedDate
          FROM HFS_Work_Item__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Trigger_Event__c);
        for (HFS_Evidence__c evidence : [
          SELECT Id
          FROM HFS_Evidence__c
          WHERE Work_Item__c = :recordId
          WITH USER_MODE
        ]) {
          seed.evidenceIds.add(evidence.Id);
        }
      }
      when 'HFS_SOP_Execution__c' {
        List<HFS_SOP_Execution__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Work_Item__c,
            Work_Item__r.Trigger_Event__c,
            Definition_Key__c,
            Definition_Version__c,
            Current_Step_Key__c,
            Status__c,
            Started_At__c,
            Completed_At__c
          FROM HFS_SOP_Execution__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Work_Item__r.Trigger_Event__c);
      }
      when 'HFS_Evidence__c' {
        HFS_Evidence__c recordValue = oneEvidence(recordId);
        requireRootTenant(tenantKey, recordValue);
        seed.root = item(recordValue);
        seed.evidenceIds.add(recordValue.Id);
      }
      when 'HFS_Recommendation__c' {
        List<HFS_Recommendation__c> records = [
          SELECT
            Id,
            Name,
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
            Model_Invocation_Id__c,
            Generated_At__c
          FROM HFS_Recommendation__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.evidenceIds.add(records[0].Primary_Evidence__c);
      }
      when 'HFS_Approval__c' {
        List<HFS_Approval__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Recommendation__c,
            Recommendation__r.Primary_Evidence__c,
            Status__c,
            Requested_At__c,
            Decision_By__c,
            Decided_At__c,
            Decision_Notes__c,
            Policy_Key__c
          FROM HFS_Approval__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.evidenceIds.add(records[0].Recommendation__r.Primary_Evidence__c);
      }
      when 'HFS_Action__c' {
        List<HFS_Action__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Recommendation__c,
            Recommendation__r.Primary_Evidence__c,
            Approval__c,
            Target_Entity__c,
            Status__c,
            Action_Type__c,
            Requested_At__c,
            Executed_At__c,
            Correlation_Id__c,
            Idempotency_Key__c,
            External_Reference__c,
            Failure_Detail__c
          FROM HFS_Action__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.evidenceIds.add(records[0].Recommendation__r.Primary_Evidence__c);
      }
      when 'HFS_Outcome__c' {
        List<HFS_Outcome__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Action__c,
            Action__r.Recommendation__r.Primary_Evidence__c,
            Source_Event__c,
            Outcome_Type__c,
            Status__c,
            Observed_At__c,
            Summary__c,
            Metric_Key__c,
            Metric_Value__c
          FROM HFS_Outcome__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.evidenceIds.add(
          records[0].Action__r.Recommendation__r.Primary_Evidence__c
        );
        seed.eventIds.add(records[0].Source_Event__c);
      }
      when 'HFS_Evaluation__c' {
        List<HFS_Evaluation__c> records = [
          SELECT
            Id,
            Name,
            External_Key__c,
            Tenant_Key__c,
            Outcome__c,
            Outcome__r.Source_Event__c,
            Outcome__r.Action__r.Recommendation__r.Primary_Evidence__c,
            Evaluation_Type__c,
            Evaluator_Type__c,
            Evaluator_Id__c,
            Score__c,
            Verdict__c,
            Notes__c,
            Evaluated_At__c
          FROM HFS_Evaluation__c
          WHERE Id = :recordId
          WITH USER_MODE
          LIMIT 1
        ];
        requireRecord(records, 'recordId');
        requireRootTenant(tenantKey, records[0]);
        seed.root = item(records[0]);
        seed.eventIds.add(records[0].Outcome__r.Source_Event__c);
        seed.evidenceIds.add(
          records[0].Outcome__r.Action__r.Recommendation__r.Primary_Evidence__c
        );
      }
    }
    return seed;
  }

  private static HFS_Event__c oneEvent(Id recordId) {
    List<HFS_Event__c> records = [
      SELECT
        Id,
        Name,
        Event_Id__c,
        Tenant_Key__c,
        Event_Type__c,
        Subject__c,
        Source_URI__c,
        Content_Hash__c,
        Occurred_At__c,
        Observed_At__c,
        Correlation_Id__c,
        Intake_Result__c
      FROM HFS_Event__c
      WHERE Id = :recordId
      WITH USER_MODE
      LIMIT 1
    ];
    requireRecord(records, 'recordId');
    return records[0];
  }

  private static HFS_Evidence__c oneEvidence(Id recordId) {
    List<HFS_Evidence__c> records;
    try {
      records = [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Work_Item__c,
          Related_Entity__c,
          Source_Event__c,
          Evidence_Type__c,
          Summary__c,
          Content_Hash__c,
          Source_URI__c,
          Captured_At__c
        FROM HFS_Evidence__c
        WHERE Id = :recordId
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

  private static List<HFS_Evidence__c> evidenceForWork(Id workItemId) {
    try {
      return [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Work_Item__c,
          Related_Entity__c,
          Source_Event__c,
          Evidence_Type__c,
          Summary__c,
          Content_Hash__c,
          Source_URI__c,
          Captured_At__c
        FROM HFS_Evidence__c
        WHERE Work_Item__c = :workItemId
        WITH USER_MODE
        ORDER BY Captured_At__c DESC
      ];
    } catch (Exception ignored) {
      inaccessibleEvidence();
      return new List<HFS_Evidence__c>();
    }
  }

  private static List<HFS_Evidence__c> evidenceByIds(Set<Id> evidenceIds) {
    try {
      return [
        SELECT
          Id,
          Name,
          External_Key__c,
          Tenant_Key__c,
          Work_Item__c,
          Related_Entity__c,
          Source_Event__c,
          Evidence_Type__c,
          Summary__c,
          Content_Hash__c,
          Source_URI__c,
          Captured_At__c
        FROM HFS_Evidence__c
        WHERE Id IN :evidenceIds
        WITH USER_MODE
      ];
    } catch (Exception ignored) {
      inaccessibleEvidence();
      return new List<HFS_Evidence__c>();
    }
  }

  private static void inaccessibleEvidence() {
    HFS_ServiceSupport.fail(
      HFS_ServiceContract.SOURCE_EVIDENCE_INACCESSIBLE,
      'The source evidence is missing or inaccessible.',
      'recordId'
    );
  }

  private static void requireRecord(List<SObject> records, String fieldName) {
    if (records.isEmpty()) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.RECORD_NOT_FOUND,
        'No accessible record was found.',
        fieldName
      );
    }
  }

  private static void requireRootTenant(String tenantKey, SObject recordValue) {
    HFS_ServiceSupport.requireTenant(
      tenantKey,
      (String) recordValue.get('Tenant_Key__c'),
      'recordId'
    );
  }

  private static HFS_ContextResponse emptyContext(HFS_ContextRequest request) {
    HFS_ContextResponse response = new HFS_ContextResponse();
    response.contractVersion = HFS_ServiceContract.VERSION;
    response.correlationId = request.correlationId;
    response.tenantKey = request.tenantKey;
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
    response.errors = new List<HFS_ServiceError>();
    return response;
  }

  private static void validateTenants(
    String tenantKey,
    List<List<SObject>> recordGroups
  ) {
    for (List<SObject> records : recordGroups) {
      for (SObject recordValue : records) {
        HFS_ServiceSupport.requireTenant(
          tenantKey,
          (String) recordValue.get('Tenant_Key__c'),
          'tenantKey'
        );
      }
    }
  }

  private static List<SObject> toSObjects(List<SObject> values) {
    return values;
  }

  private static Set<Id> ids(List<SObject> records) {
    Set<Id> result = new Set<Id>();
    for (SObject recordValue : records) {
      result.add((Id) recordValue.get('Id'));
    }
    return result;
  }

  private static List<HFS_ContextItem> items(List<SObject> records) {
    List<HFS_ContextItem> result = new List<HFS_ContextItem>();
    for (SObject recordValue : records) {
      result.add(item(recordValue));
    }
    return result;
  }

  private static HFS_ContextItem item(SObject recordValue) {
    if (recordValue instanceof HFS_Event__c) {
      HFS_Event__c value = (HFS_Event__c) recordValue;
      return contextItem(
        value,
        value.Event_Id__c,
        value.Event_Type__c,
        value.Subject__c,
        value.Intake_Result__c,
        value.Subject__c,
        value.Occurred_At__c,
        value.Id,
        null,
        null,
        null,
        null,
        null,
        value.Source_URI__c,
        value.Content_Hash__c
      );
    }
    if (recordValue instanceof HFS_Entity__c) {
      HFS_Entity__c value = (HFS_Entity__c) recordValue;
      return contextItem(
        value,
        value.External_Key__c,
        value.Entity_Type__c,
        value.Display_Name__c,
        null,
        value.Display_Name__c,
        value.Valid_From__c,
        value.Source_Event__c,
        value.Id,
        null,
        null,
        null,
        value.Confidence__c,
        null,
        null
      );
    }
    if (recordValue instanceof HFS_Relationship__c) {
      HFS_Relationship__c value = (HFS_Relationship__c) recordValue;
      return contextItem(
        value,
        value.External_Key__c,
        'RELATIONSHIP',
        value.Name,
        null,
        value.Relationship_Type__c,
        value.Valid_From__c,
        value.Source_Event__c,
        value.Subject_Entity__c,
        value.Object_Entity__c,
        value.Relationship_Type__c,
        null,
        value.Confidence__c,
        null,
        null
      );
    }
    if (recordValue instanceof HFS_Event_Participant__c) {
      HFS_Event_Participant__c value = (HFS_Event_Participant__c) recordValue;
      return contextItem(
        value,
        value.External_Key__c,
        'EVENT_PARTICIPANT',
        value.Name,
        null,
        value.Participant_Role__c,
        null,
        value.Event__c,
        value.Entity__c,
        null,
        null,
        value.Participant_Role__c,
        null,
        null,
        null
      );
    }
    if (recordValue instanceof HFS_Agreement__c) {
      HFS_Agreement__c value = (HFS_Agreement__c) recordValue;
      return contextItem(
        value,
        value.External_Key__c,
        value.Agreement_Type__c,
        value.Name,
        value.Status__c,
        value.Terms_Summary__c,
        value.Effective_From__c,
        value.Source_Event__c,
        value.Party_One__c,
        value.Party_Two__c,
        'AGREEMENT',
        null,
        null,
        null,
        null
      );
    }
    if (recordValue instanceof HFS_Work_Item__c) {
      HFS_Work_Item__c value = (HFS_Work_Item__c) recordValue;
      HFS_ContextItem result = contextItem(
        value,
        value.External_Key__c,
        value.Priority__c,
        value.Name,
        value.Status__c,
        value.Summary__c,
        value.CreatedDate,
        value.Trigger_Event__c,
        value.Primary_Entity__c,
        null,
        null,
        null,
        null,
        null,
        null
      );
      result.ownerLabel = value.Owner == null ? null : value.Owner.Name;
      result.dueAt = value.Due_At__c;
      result.blockedReason = value.Blocked_Reason__c;
      return result;
    }
    if (recordValue instanceof HFS_SOP_Execution__c) {
      HFS_SOP_Execution__c value = (HFS_SOP_Execution__c) recordValue;
      HFS_ContextItem result = contextItem(
        value,
        value.External_Key__c,
        value.Definition_Key__c,
        value.Name,
        value.Status__c,
        value.Current_Step_Key__c,
        value.Started_At__c,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      );
      result.definitionVersion = value.Definition_Version__c;
      return result;
    }
    if (recordValue instanceof HFS_Evidence__c) {
      HFS_Evidence__c value = (HFS_Evidence__c) recordValue;
      return contextItem(
        value,
        value.External_Key__c,
        value.Evidence_Type__c,
        value.Name,
        null,
        value.Summary__c,
        value.Captured_At__c,
        value.Source_Event__c,
        value.Related_Entity__c,
        null,
        null,
        null,
        null,
        value.Source_URI__c,
        value.Content_Hash__c
      );
    }
    if (recordValue instanceof HFS_Recommendation__c) {
      HFS_Recommendation__c value = (HFS_Recommendation__c) recordValue;
      HFS_ContextItem result = contextItem(
        value,
        value.External_Key__c,
        value.Recommendation_Type__c,
        value.Name,
        value.Status__c,
        value.Rationale__c,
        value.Generated_At__c,
        null,
        value.Subject_Entity__c,
        null,
        null,
        null,
        value.Confidence__c,
        null,
        null
      );
      result.proposedActionType = value.Proposed_Action_Type__c;
      result.primaryEvidenceId = value.Primary_Evidence__c;
      result.modelProfile = value.Model_Profile__c;
      result.modelInvocationId = value.Model_Invocation_Id__c;
      return result;
    }
    if (recordValue instanceof HFS_Approval__c) {
      HFS_Approval__c value = (HFS_Approval__c) recordValue;
      HFS_ContextItem result = contextItem(
        value,
        value.External_Key__c,
        value.Policy_Key__c,
        value.Name,
        value.Status__c,
        value.Decision_Notes__c,
        value.Decided_At__c == null
          ? value.Requested_At__c
          : value.Decided_At__c,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      );
      result.requestedAt = value.Requested_At__c;
      result.decidedAt = value.Decided_At__c;
      return result;
    }
    if (recordValue instanceof HFS_Action__c) {
      HFS_Action__c value = (HFS_Action__c) recordValue;
      HFS_ContextItem result = contextItem(
        value,
        value.External_Key__c,
        value.Action_Type__c,
        value.Name,
        value.Status__c,
        value.Failure_Detail__c,
        value.Executed_At__c == null
          ? value.Requested_At__c
          : value.Executed_At__c,
        null,
        value.Target_Entity__c,
        null,
        null,
        null,
        null,
        null,
        null
      );
      result.requestedAt = value.Requested_At__c;
      result.correlationId = value.Correlation_Id__c;
      result.externalReference = value.External_Reference__c;
      return result;
    }
    if (recordValue instanceof HFS_Outcome__c) {
      HFS_Outcome__c value = (HFS_Outcome__c) recordValue;
      HFS_ContextItem result = contextItem(
        value,
        value.External_Key__c,
        value.Outcome_Type__c,
        value.Name,
        value.Status__c,
        value.Summary__c,
        value.Observed_At__c,
        value.Source_Event__c,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      );
      result.metricKey = value.Metric_Key__c;
      result.metricValue = value.Metric_Value__c;
      return result;
    }
    HFS_Evaluation__c value = (HFS_Evaluation__c) recordValue;
    return contextItem(
      value,
      value.External_Key__c,
      value.Evaluation_Type__c,
      value.Name,
      value.Verdict__c,
      value.Notes__c,
      value.Evaluated_At__c,
      null,
      null,
      null,
      null,
      null,
      value.Score__c,
      null,
      null
    );
  }

  private static HFS_ContextItem contextItem(
    SObject recordValue,
    String externalKey,
    String recordType,
    String label,
    String status,
    String summary,
    Datetime occurredAt,
    Id sourceEventId,
    Id subjectEntityId,
    Id objectEntityId,
    String relationshipType,
    String participantRole,
    Decimal confidence,
    String sourceUri,
    String contentHash
  ) {
    HFS_ContextItem itemValue = new HFS_ContextItem();
    itemValue.recordId = String.valueOf(recordValue.get('Id'));
    itemValue.objectApiName = recordValue
      .getSObjectType()
      .getDescribe()
      .getName();
    itemValue.externalKey = externalKey;
    itemValue.recordType = recordType;
    itemValue.label = label;
    itemValue.status = status;
    itemValue.summary = summary;
    itemValue.occurredAt = occurredAt;
    itemValue.sourceEventId = stringId(sourceEventId);
    itemValue.subjectEntityId = stringId(subjectEntityId);
    itemValue.objectEntityId = stringId(objectEntityId);
    itemValue.relationshipType = relationshipType;
    itemValue.participantRole = participantRole;
    itemValue.confidence = confidence;
    itemValue.sourceUri = sourceUri;
    itemValue.contentHash = contentHash;
    return itemValue;
  }

  private static List<HFS_EvidenceCitation> citations(
    List<HFS_Evidence__c> records
  ) {
    List<HFS_EvidenceCitation> result = new List<HFS_EvidenceCitation>();
    for (HFS_Evidence__c recordValue : records) {
      result.add(citation(recordValue));
    }
    return result;
  }

  private static HFS_EvidenceCitation citation(HFS_Evidence__c recordValue) {
    HFS_EvidenceCitation result = new HFS_EvidenceCitation();
    result.evidenceId = String.valueOf(recordValue.Id);
    result.sourceEventId = stringId(recordValue.Source_Event__c);
    result.sourceUri = recordValue.Source_URI__c;
    result.contentHash = recordValue.Content_Hash__c;
    result.summary = recordValue.Summary__c;
    result.capturedAt = recordValue.Captured_At__c;
    return result;
  }

  private static List<HFS_ContextItem> sortTimeline(
    List<HFS_ContextItem> records,
    Integer limitValue
  ) {
    Integer safeLimit = Math.max(1, Math.min(500, limitValue));
    Map<Long, List<HFS_ContextItem>> byTime = new Map<Long, List<HFS_ContextItem>>();
    for (HFS_ContextItem recordValue : records) {
      Long key = recordValue.occurredAt == null
        ? 0
        : recordValue.occurredAt.getTime();
      if (!byTime.containsKey(key)) {
        byTime.put(key, new List<HFS_ContextItem>());
      }
      byTime.get(key).add(recordValue);
    }
    List<Long> times = new List<Long>(byTime.keySet());
    times.sort();
    List<HFS_ContextItem> result = new List<HFS_ContextItem>();
    for (Integer index = times.size() - 1; index >= 0; index--) {
      for (HFS_ContextItem recordValue : byTime.get(times[index])) {
        if (result.size() == safeLimit) {
          return result;
        }
        result.add(recordValue);
      }
    }
    return result;
  }

  private static String stringId(Id value) {
    return value == null ? null : String.valueOf(value);
  }

  private class ProvenanceSeed {
    HFS_ContextItem root;
    Set<Id> eventIds = new Set<Id>();
    Set<Id> evidenceIds = new Set<Id>();
  }
}
