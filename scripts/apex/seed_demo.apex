String tenantKey = 'demo-mauritius';
String correlationId = '10000000-0000-4000-8000-000000000001';
Datetime baseTime = Datetime.newInstanceGmt(2026, 6, 7, 8, 30, 0);

HFS_Event__c sourceEvent = new HFS_Event__c(
  Event_Id__c = 'event-demo-001',
  Tenant_Key__c = tenantKey,
  Source_URI__c = 'urn:hfs:source:operations',
  Source_Record_Id__c = 'operations-incident-demo-001',
  Event_Type__c = 'SERVICE_INTERRUPTION_REPORTED',
  Subject__c = 'Repeated service interruption',
  Occurred_At__c = baseTime,
  Observed_At__c = baseTime.addMinutes(1),
  Source_Sequence__c = 1,
  Idempotency_Key__c = 'event-demo-001-v1',
  Correlation_Id__c = correlationId,
  Schema_Version__c = '1.0.0',
  Content_Hash__c = 'sha256:56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70fdb4feada11935c10',
  Payload_JSON__c = '{"case":"operations-incident-demo-001","status":"open"}',
  Intake_Result__c = 'ACCEPTED'
);
insert sourceEvent;

HFS_Entity__c customer = new HFS_Entity__c(
  External_Key__c = 'entity-customer-demo-001',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'PERSON',
  Display_Name__c = 'Affected person',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-30),
  Confidence__c = 0.99
);
HFS_Entity__c business = new HFS_Entity__c(
  External_Key__c = 'entity-business-demo-001',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'ORGANIZATION',
  Display_Name__c = 'Demo Mauritius organization',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-30),
  Confidence__c = 1
);
HFS_Entity__c supplier = new HFS_Entity__c(
  External_Key__c = 'entity-supplier-demo-001',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'SUPPLIER',
  Display_Name__c = 'Critical service supplier',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-30),
  Confidence__c = 0.95
);
insert new List<HFS_Entity__c>{ customer, business, supplier };

insert new List<HFS_Event_Participant__c>{
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-customer-demo-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = customer.Id,
    Participant_Role__c = 'AFFECTED_RELATIONSHIP'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-business-demo-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = business.Id,
    Participant_Role__c = 'SERVICE_OWNER'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-supplier-demo-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = supplier.Id,
    Participant_Role__c = 'UPSTREAM_DEPENDENCY'
  )
};

insert new List<HFS_Relationship__c>{
  new HFS_Relationship__c(
    External_Key__c = 'relationship-customer-demo-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = customer.Id,
    Object_Entity__c = business.Id,
    Relationship_Type__c = 'CUSTOMER_OF',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-30),
    Confidence__c = 0.98
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-supplier-demo-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = business.Id,
    Object_Entity__c = supplier.Id,
    Relationship_Type__c = 'DEPENDS_ON',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-30),
    Confidence__c = 0.96
  )
};

insert new HFS_Agreement__c(
  External_Key__c = 'agreement-demo-001',
  Tenant_Key__c = tenantKey,
  Party_One__c = business.Id,
  Party_Two__c = supplier.Id,
  Agreement_Type__c = 'SERVICE_LEVEL',
  Status__c = 'ACTIVE',
  Terms_Summary__c = 'Incident updates are required within two hours.',
  Source_Event__c = sourceEvent.Id,
  Effective_From__c = baseTime.date().addDays(-30)
);

HFS_Work_Item__c workItem = new HFS_Work_Item__c(
  External_Key__c = 'work-demo-001',
  Tenant_Key__c = tenantKey,
  Primary_Entity__c = customer.Id,
  Trigger_Event__c = sourceEvent.Id,
  Status__c = 'AWAITING_APPROVAL',
  Priority__c = 'HIGH',
  Summary__c = 'Prepare and approve a proactive relationship update.',
  Due_At__c = baseTime.addHours(2),
  Blocked_Reason__c = 'Human approval is required before external outreach.'
);
insert workItem;

insert new HFS_SOP_Execution__c(
  External_Key__c = 'sop-demo-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Definition_Key__c = 'major-incident-relationship-response',
  Definition_Version__c = '1.0.0',
  Current_Step_Key__c = 'APPROVE_FIRST_UPDATE',
  Status__c = 'RUNNING',
  Started_At__c = baseTime.addMinutes(4)
);

HFS_Evidence__c incidentEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-incident-demo-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = customer.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'SOURCE_EVENT',
  Summary__c = 'The operations source reported repeated interruption at 08:30.',
  Content_Hash__c = 'sha256:56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70fdb4feada11935c10',
  Source_URI__c = 'urn:hfs:source:operations',
  Captured_At__c = baseTime.addMinutes(1)
);
HFS_Evidence__c agreementEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-agreement-demo-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = business.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'AGREEMENT_TERM',
  Summary__c = 'The service agreement requires incident updates within two hours.',
  Content_Hash__c = 'sha256:7549cf0c63ad4a64f178d8500c1f3874d97478f6ee323e4debbab6d89b168b69',
  Source_URI__c = 'urn:hfs:source:contracts',
  Captured_At__c = baseTime.addMinutes(2)
);
insert new List<HFS_Evidence__c>{ incidentEvidence, agreementEvidence };

HFS_Recommendation__c recommendation = new HFS_Recommendation__c(
  External_Key__c = 'recommendation-demo-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Subject_Entity__c = customer.Id,
  Primary_Evidence__c = incidentEvidence.Id,
  Status__c = 'PENDING_APPROVAL',
  Recommendation_Type__c = 'PROACTIVE_RELATIONSHIP_UPDATE',
  Proposed_Action_Type__c = 'SEND_STATUS_UPDATE',
  Rationale__c = 'Send a grounded update naming the owner and next update time.',
  Confidence__c = 0.87,
  Model_Profile__c = 'recommendation_reasoning',
  Model_Invocation_Id__c = 'model-invocation-demo-001',
  Generated_At__c = baseTime.addMinutes(7)
);
insert recommendation;

insert new HFS_Approval__c(
  External_Key__c = 'approval-demo-001',
  Tenant_Key__c = tenantKey,
  Recommendation__c = recommendation.Id,
  Status__c = 'PENDING',
  Requested_At__c = baseTime.addMinutes(8),
  Policy_Key__c = 'external-relationship-communication-v1'
);

System.debug('HFS_DEMO_SEED:' + workItem.Id);
