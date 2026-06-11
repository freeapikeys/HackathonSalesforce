String tenantKey = 'demo-mauritius';
String correlationId = '10000000-0000-4000-8000-000000000001';
Datetime baseTime = Datetime.newInstanceGmt(2026, 6, 13, 5, 0, 0);

HFS_Event__c sourceEvent = new HFS_Event__c(
  Event_Id__c = 'event-north-star-hospital-surge-001',
  Tenant_Key__c = tenantKey,
  Source_URI__c = 'urn:hfs:source:hospital:operations-surge',
  Source_Record_Id__c = 'hospital-ops-surge-2026-06-13-morning',
  Event_Type__c = 'HOSPITAL_OPERATIONS_SURGE_DETECTED',
  Subject__c = 'North Star private hospital morning operations surge',
  Occurred_At__c = baseTime,
  Observed_At__c = baseTime.addMinutes(1),
  Source_Sequence__c = 1,
  Idempotency_Key__c = 'event-north-star-hospital-surge-001-v1',
  Correlation_Id__c = correlationId,
  Schema_Version__c = '1.0.0',
  Content_Hash__c = 'sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f',
  Payload_JSON__c = '{"eventcode":"HOSPITAL_OPERATIONS_SURGE_DETECTED","organizationid":"HOSP-NORTH-STAR-PRIVATE","window":"2026-06-13T08:45:00+04:00/2026-06-13T11:15:00+04:00"}',
  Intake_Result__c = 'ACCEPTED'
);
insert sourceEvent;

HFS_Entity__c hospital = new HFS_Entity__c(
  External_Key__c = 'HOSP-NORTH-STAR-PRIVATE',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'ORGANIZATION',
  Display_Name__c = 'North Star Private Hospital',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-365),
  Confidence__c = 1,
  Attributes_JSON__c = '{"primitive":"Organization","profile":"private-hospital","country":"Mauritius"}'
);
HFS_Entity__c outpatientReception = new HFS_Entity__c(
  External_Key__c = 'DEPT-OUTPATIENT-RECEPTION',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'LOCATION',
  Display_Name__c = 'Outpatient reception',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-365),
  Confidence__c = 1,
  Attributes_JSON__c = '{"primitive":"Location","departmentType":"outpatient","queueTargetMinutes":35}'
);
HFS_Entity__c wardRooms = new HFS_Entity__c(
  External_Key__c = 'RESOURCE-WARD-A3-DISCHARGE-ROOMS',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'RESOURCE',
  Display_Name__c = 'Ward A3 discharge rooms',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-90),
  Confidence__c = 0.99,
  Attributes_JSON__c = '{"primitive":"Resource","resourceType":"ROOM","capacity":18,"availableCapacity":6,"blockedCapacity":7}'
);
HFS_Entity__c pharmacyStock = new HFS_Entity__c(
  External_Key__c = 'RESOURCE-PHARMACY-IV-KITS',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'RESOURCE',
  Display_Name__c = 'Pharmacy IV kit stock',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-30),
  Confidence__c = 0.96,
  Attributes_JSON__c = '{"primitive":"Resource","resourceType":"SUPPLY","stockCoverHours":2.4,"thresholdHours":4}'
);
HFS_Entity__c labPartner = new HFS_Entity__c(
  External_Key__c = 'PARTNER-ISLAND-DIAGNOSTICS',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'PARTNER',
  Display_Name__c = 'Island Diagnostics Lab',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-180),
  Confidence__c = 0.95,
  Attributes_JSON__c = '{"primitive":"Partner","partnerType":"LAB","normalResponseMinutes":30,"currentDelayMinutes":42}'
);
HFS_Entity__c billingProcess = new HFS_Entity__c(
  External_Key__c = 'PROCESS-BILLING-INSURANCE-REVIEW',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'PROCESS',
  Display_Name__c = 'Billing and insurance review',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-120),
  Confidence__c = 0.94,
  Attributes_JSON__c = '{"primitive":"Process","caseType":"duplicate_invoice_and_claim_pending","approvalRequired":true}'
);
HFS_Entity__c patientAlias = new HFS_Entity__c(
  External_Key__c = 'ALIAS-PATIENT-GROUP-MORNING-001',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'CUSTOMER_ALIAS',
  Display_Name__c = 'Synthetic patient and visitor alias group',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime,
  Confidence__c = 0.9,
  Attributes_JSON__c = '{"primitive":"Customer","aliasOnly":true,"containsPersonalData":false,"complaintCount":11}'
);
insert new List<HFS_Entity__c>{
  hospital,
  outpatientReception,
  wardRooms,
  pharmacyStock,
  labPartner,
  billingProcess,
  patientAlias
};

insert new List<HFS_Event_Participant__c>{
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-hospital-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = hospital.Id,
    Participant_Role__c = 'ORGANIZATION'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-outpatient-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = outpatientReception.Id,
    Participant_Role__c = 'LOCATION'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-rooms-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = wardRooms.Id,
    Participant_Role__c = 'RESOURCE'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-pharmacy-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = pharmacyStock.Id,
    Participant_Role__c = 'RESOURCE'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-lab-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = labPartner.Id,
    Participant_Role__c = 'PARTNER'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-billing-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = billingProcess.Id,
    Participant_Role__c = 'PROCESS'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-patient-alias-hospital-surge-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = patientAlias.Id,
    Participant_Role__c = 'CUSTOMER_ALIAS'
  )
};

insert new List<HFS_Relationship__c>{
  new HFS_Relationship__c(
    External_Key__c = 'relationship-hospital-outpatient-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = hospital.Id,
    Object_Entity__c = outpatientReception.Id,
    Relationship_Type__c = 'HAS_SERVICE_AREA',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-365),
    Confidence__c = 1
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-hospital-ward-rooms-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = hospital.Id,
    Object_Entity__c = wardRooms.Id,
    Relationship_Type__c = 'HAS_RESOURCE',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-90),
    Confidence__c = 0.99
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-hospital-pharmacy-stock-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = hospital.Id,
    Object_Entity__c = pharmacyStock.Id,
    Relationship_Type__c = 'HAS_RESOURCE',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-30),
    Confidence__c = 0.96
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-hospital-lab-partner-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = hospital.Id,
    Object_Entity__c = labPartner.Id,
    Relationship_Type__c = 'DEPENDS_ON_PARTNER',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-180),
    Confidence__c = 0.95
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-hospital-billing-process-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = hospital.Id,
    Object_Entity__c = billingProcess.Id,
    Relationship_Type__c = 'OWNS_PROCESS',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-120),
    Confidence__c = 0.94
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-outpatient-patient-alias-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = outpatientReception.Id,
    Object_Entity__c = patientAlias.Id,
    Relationship_Type__c = 'HAS_CUSTOMER_SIGNAL',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime,
    Confidence__c = 0.9
  )
};

insert new HFS_Agreement__c(
  External_Key__c = 'SLA-ISLAND-DIAGNOSTICS-LAB-2026',
  Tenant_Key__c = tenantKey,
  Party_One__c = hospital.Id,
  Party_Two__c = labPartner.Id,
  Agreement_Type__c = 'LAB_RESPONSE_SLA',
  Status__c = 'ACTIVE',
  Terms_Summary__c = 'Island Diagnostics should acknowledge routine operational escalation within thirty minutes and urgent operations escalations within fifteen minutes.',
  Material_Terms_JSON__c = '{"primitive":"Policy","normalResponseMinutes":30,"urgentResponseMinutes":15,"demoOnly":true}',
  Source_Event__c = sourceEvent.Id,
  Effective_From__c = baseTime.date().addDays(-180),
  Effective_To__c = baseTime.date().addDays(180)
);

HFS_Work_Item__c workItem = new HFS_Work_Item__c(
  External_Key__c = 'work-north-star-hospital-surge-001',
  Tenant_Key__c = tenantKey,
  Primary_Entity__c = hospital.Id,
  Trigger_Event__c = sourceEvent.Id,
  Status__c = 'AWAITING_APPROVAL',
  Priority__c = 'HIGH',
  Summary__c = 'Resolve patient trust, bed capacity, pharmacy stock, lab partner, billing, and task coordination risks for the morning hospital operations surge.',
  Due_At__c = baseTime.addHours(2).addMinutes(15),
  Blocked_Reason__c = 'Business manager approval is required before Slack, WhatsApp, room, pharmacy, vendor, billing, staff-task, or patient-message write-back.'
);
insert workItem;

insert new HFS_SOP_Execution__c(
  External_Key__c = 'sop-north-star-hospital-surge-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Definition_Key__c = 'north-star-hospital-operations-recovery',
  Definition_Version__c = '1.0.0',
  Current_Step_Key__c = 'AWAIT_MANAGER_APPROVAL',
  Status__c = 'RUNNING',
  Started_At__c = baseTime.addMinutes(4)
);

HFS_Evidence__c complaintEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-complaint-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = patientAlias.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'PATIENT_COMPLAINT_CLUSTER',
  Summary__c = 'Eleven synthetic patient and visitor complaints mention wait time, room readiness, billing delay, and pharmacy delay in the morning surge window.',
  Content_Hash__c = 'sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f',
  Source_URI__c = 'urn:hfs:source:hospital:complaints',
  Captured_At__c = baseTime.addMinutes(1)
);
HFS_Evidence__c capacityEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-capacity-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = wardRooms.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'RESOURCE_CAPACITY',
  Summary__c = 'Ward A3 has six ready rooms, seven blocked discharge rooms, and a seventy-four minute outpatient queue wait against a thirty-five minute target.',
  Content_Hash__c = 'sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb',
  Source_URI__c = 'urn:hfs:source:hospital:capacity',
  Captured_At__c = baseTime.addMinutes(2)
);
HFS_Evidence__c pharmacyEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-pharmacy-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = pharmacyStock.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'PHARMACY_STOCK_POSITION',
  Summary__c = 'Pharmacy IV kit cover is 2.4 hours against a four-hour operational threshold before the afternoon demand window.',
  Content_Hash__c = 'sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588',
  Source_URI__c = 'urn:hfs:source:hospital:pharmacy',
  Captured_At__c = baseTime.addMinutes(11)
);
HFS_Evidence__c partnerEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-partner-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = labPartner.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'PARTNER_RESPONSE_STATUS',
  Summary__c = 'Island Diagnostics is forty-two minutes over the routine acknowledgement SLA; a second courier route is available after approval.',
  Content_Hash__c = 'sha256:f42d186a12981c8c7a25b7be50f5f95541e4323f83f3f3c65de8e20717b5e6ea',
  Source_URI__c = 'urn:hfs:source:hospital:partner',
  Captured_At__c = baseTime.addMinutes(25)
);
HFS_Evidence__c billingEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-billing-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = billingProcess.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'BILLING_AND_INSURANCE_HOLD',
  Summary__c = 'Three duplicate invoice reviews and two insurer follow-ups are open; refunds or compensation need manager approval.',
  Content_Hash__c = 'sha256:1b7c5f38159d8e86f0a1e9e00f27acfc4f9657cdcfb30fc4a7c383563e826355',
  Source_URI__c = 'urn:hfs:source:hospital:billing',
  Captured_At__c = baseTime.addMinutes(30)
);
HFS_Evidence__c staffingEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-staffing-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = outpatientReception.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'STAFF_QUEUE_RISK',
  Summary__c = 'Two front-desk staff are unavailable, porter coverage is delayed, and the outpatient queue needs role-owned task coordination.',
  Content_Hash__c = 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
  Source_URI__c = 'urn:hfs:source:hospital:staffing',
  Captured_At__c = baseTime.addMinutes(32)
);
HFS_Evidence__c clinicalBoundaryEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-clinical-refusal-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = hospital.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'CLINICAL_DECISION_REFUSAL',
  Summary__c = 'A request asking which patient should receive treatment first is refused by North Star and routed to clinician review.',
  Content_Hash__c = 'sha256:a4da995bc39a2a89d45bc28398c12edc8af4f895449fffc8f54195baee4b9d5e',
  Source_URI__c = 'urn:hfs:source:hospital:clinical-boundary',
  Captured_At__c = baseTime.addMinutes(35)
);
insert new List<HFS_Evidence__c>{
  complaintEvidence,
  capacityEvidence,
  pharmacyEvidence,
  partnerEvidence,
  billingEvidence,
  staffingEvidence,
  clinicalBoundaryEvidence
};

HFS_Recommendation__c recommendation = new HFS_Recommendation__c(
  External_Key__c = 'recommendation-north-star-hospital-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Subject_Entity__c = hospital.Id,
  Primary_Evidence__c = complaintEvidence.Id,
  Status__c = 'PENDING_APPROVAL',
  Recommendation_Type__c = 'NORTH_STAR_HOSPITAL_RECOVERY_PLAN',
  Proposed_Action_Type__c = 'APPROVE_HOSPITAL_RECOVERY_ACTIONS',
  Rationale__c = 'Facts: patient complaints are clustered, discharge rooms are blocked, pharmacy stock cover is below threshold, lab acknowledgement is late, billing/insurance reviews are stalled, and staffing coverage is short. Inference: one approved operations recovery plan should coordinate room cleaning, porter movement, pharmacy restock or transfer, lab escalation, billing review, internal Slack and WhatsApp alerts, and outcome tracking. North Star refuses clinical diagnosis, treatment, dosage, triage, or clinical priority decisions.',
  Confidence__c = 0.88,
  Model_Profile__c = 'north-star-hospital-operations',
  Model_Invocation_Id__c = 'model-invocation-north-star-hospital-001',
  Generated_At__c = baseTime.addMinutes(36)
);
insert recommendation;

insert new HFS_Approval__c(
  External_Key__c = 'approval-north-star-hospital-001',
  Tenant_Key__c = tenantKey,
  Recommendation__c = recommendation.Id,
  Status__c = 'PENDING',
  Requested_At__c = baseTime.addMinutes(37),
  Policy_Key__c = 'north-star-hospital-manager-approval-v1'
);

System.debug('HFS_DEMO_SEED:' + workItem.Id);
