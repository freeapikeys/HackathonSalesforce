Savepoint checkpoint = Database.setSavepoint();

try {
    Datetime nowValue = System.now();
    String tenantKey = 'metadata-smoke';

    HFS_Event__c sourceEvent = new HFS_Event__c(
        Event_Id__c = '00000000-0000-4000-8000-000000009001',
        Tenant_Key__c = tenantKey,
        Event_Type__c = 'io.github.freeapikeys.hfs.issue.opened.v1',
        Source_URI__c = 'urn:hfs:source:metadata-smoke',
        Subject__c = 'issue:metadata-smoke',
        Source_Record_Id__c = 'metadata-smoke-event',
        Schema_Version__c = '1.0.0',
        Correlation_Id__c = '10000000-0000-4000-8000-000000009001',
        Idempotency_Key__c = 'metadata-smoke-event-v1',
        Source_Sequence__c = 1,
        Occurred_At__c = nowValue,
        Observed_At__c = nowValue,
        Content_Hash__c = 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        Payload_JSON__c = '{}',
        Intake_Result__c = 'ACCEPTED'
    );
    insert sourceEvent;

    HFS_Entity__c subjectEntity = new HFS_Entity__c(
        External_Key__c = 'metadata-smoke-subject',
        Tenant_Key__c = tenantKey,
        Source_Event__c = sourceEvent.Id,
        Entity_Type__c = 'PERSON',
        Display_Name__c = 'Metadata Smoke Subject'
    );
    HFS_Entity__c objectEntity = new HFS_Entity__c(
        External_Key__c = 'metadata-smoke-object',
        Tenant_Key__c = tenantKey,
        Source_Event__c = sourceEvent.Id,
        Entity_Type__c = 'ORGANIZATION',
        Display_Name__c = 'Metadata Smoke Organization'
    );
    insert new List<HFS_Entity__c>{subjectEntity, objectEntity};

    Boolean rejectedSelfRelationship = false;
    try {
        insert new HFS_Relationship__c(
            External_Key__c = 'metadata-smoke-invalid-relationship',
            Tenant_Key__c = tenantKey,
            Source_Event__c = sourceEvent.Id,
            Subject_Entity__c = subjectEntity.Id,
            Object_Entity__c = subjectEntity.Id,
            Relationship_Type__c = 'TEST',
            Valid_From__c = nowValue
        );
    } catch (DmlException exceptionValue) {
        rejectedSelfRelationship = exceptionValue.getDmlMessage(0).contains(
            'two different entity records'
        );
    }
    System.assert(
        rejectedSelfRelationship,
        'Self-relationships must be rejected.'
    );

    insert new HFS_Relationship__c(
        External_Key__c = 'metadata-smoke-valid-relationship',
        Tenant_Key__c = tenantKey,
        Source_Event__c = sourceEvent.Id,
        Subject_Entity__c = subjectEntity.Id,
        Object_Entity__c = objectEntity.Id,
        Relationship_Type__c = 'EMPLOYMENT',
        Valid_From__c = nowValue
    );

    HFS_Work_Item__c workItem = new HFS_Work_Item__c(
        External_Key__c = 'metadata-smoke-work',
        Tenant_Key__c = tenantKey,
        Primary_Entity__c = subjectEntity.Id,
        Trigger_Event__c = sourceEvent.Id,
        Status__c = 'AWAITING_APPROVAL',
        Priority__c = 'HIGH',
        Summary__c = 'Verify the core metadata chain'
    );
    insert workItem;

    insert new HFS_SOP_Execution__c(
        External_Key__c = 'metadata-smoke-sop',
        Tenant_Key__c = tenantKey,
        Work_Item__c = workItem.Id,
        Definition_Key__c = 'metadata-smoke-sop',
        Definition_Version__c = '1.0.0',
        Status__c = 'RUNNING',
        Started_At__c = nowValue
    );

    HFS_Evidence__c evidence = new HFS_Evidence__c(
        External_Key__c = 'metadata-smoke-evidence',
        Tenant_Key__c = tenantKey,
        Source_Event__c = sourceEvent.Id,
        Work_Item__c = workItem.Id,
        Related_Entity__c = subjectEntity.Id,
        Evidence_Type__c = 'SOURCE_EVENT',
        Summary__c = 'Synthetic evidence for metadata verification.',
        Captured_At__c = nowValue
    );
    insert evidence;

    HFS_Recommendation__c recommendation = new HFS_Recommendation__c(
        External_Key__c = 'metadata-smoke-recommendation',
        Tenant_Key__c = tenantKey,
        Work_Item__c = workItem.Id,
        Subject_Entity__c = subjectEntity.Id,
        Primary_Evidence__c = evidence.Id,
        Status__c = 'PENDING_APPROVAL',
        Recommendation_Type__c = 'RELATIONSHIP_INTERVENTION',
        Proposed_Action_Type__c = 'SEND_MESSAGE',
        Rationale__c = 'Synthetic rationale for metadata verification.',
        Confidence__c = 0.8,
        Model_Profile__c = 'metadata_smoke',
        Model_Invocation_Id__c = 'metadata-smoke-invocation',
        Generated_At__c = nowValue
    );
    insert recommendation;

    HFS_Approval__c approval = new HFS_Approval__c(
        External_Key__c = 'metadata-smoke-approval',
        Tenant_Key__c = tenantKey,
        Recommendation__c = recommendation.Id,
        Status__c = 'PENDING',
        Requested_At__c = nowValue,
        Policy_Key__c = 'human-approval-required'
    );
    insert approval;

    HFS_Action__c actionRecord = new HFS_Action__c(
        External_Key__c = 'metadata-smoke-action',
        Tenant_Key__c = tenantKey,
        Recommendation__c = recommendation.Id,
        Approval__c = approval.Id,
        Target_Entity__c = subjectEntity.Id,
        Status__c = 'PENDING',
        Action_Type__c = 'SEND_MESSAGE',
        Requested_At__c = nowValue,
        Correlation_Id__c = '20000000-0000-4000-8000-000000009001',
        Idempotency_Key__c = 'metadata-smoke-action-v1'
    );

    Boolean rejectedUnapprovedAction = false;
    try {
        insert actionRecord;
    } catch (DmlException exceptionValue) {
        rejectedUnapprovedAction = exceptionValue.getDmlMessage(0).contains(
            'requires an approved approval record'
        );
    }
    System.assert(
        rejectedUnapprovedAction,
        'Actions must be rejected while approval is pending.'
    );

    Boolean rejectedIncompleteDecision = false;
    approval.Status__c = 'APPROVED';
    try {
        update approval;
    } catch (DmlException exceptionValue) {
        rejectedIncompleteDecision = exceptionValue.getDmlMessage(0).contains(
            'Decision By and Decided At are required'
        );
    }
    System.assert(
        rejectedIncompleteDecision,
        'Completed decisions must identify the decision maker and time.'
    );

    approval.Decision_By__c = UserInfo.getUserId();
    approval.Decided_At__c = nowValue;
    update approval;

    insert actionRecord;

    HFS_Outcome__c outcome = new HFS_Outcome__c(
        External_Key__c = 'metadata-smoke-outcome',
        Tenant_Key__c = tenantKey,
        Source_Event__c = sourceEvent.Id,
        Action__c = actionRecord.Id,
        Outcome_Type__c = 'DELIVERY',
        Status__c = 'SUCCESS',
        Observed_At__c = nowValue,
        Summary__c = 'Synthetic successful outcome.'
    );
    insert outcome;

    HFS_Evaluation__c evaluation = new HFS_Evaluation__c(
        External_Key__c = 'metadata-smoke-evaluation',
        Tenant_Key__c = tenantKey,
        Outcome__c = outcome.Id,
        Evaluation_Type__c = 'DELIVERY_SUCCESS',
        Evaluator_Type__c = 'SYSTEM',
        Evaluator_Id__c = 'metadata-smoke',
        Score__c = 1,
        Verdict__c = 'PASS',
        Evaluated_At__c = nowValue
    );
    insert evaluation;

    System.assertNotEquals(null, evaluation.Id);
    System.debug('HFS_METADATA_SMOKE_TEST_PASSED');
} finally {
    Database.rollback(checkpoint);
}
