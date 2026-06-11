HFS_Work_Item__c workItem = [
  SELECT Id
  FROM HFS_Work_Item__c
  WHERE
    Tenant_Key__c = 'demo-mauritius'
    AND External_Key__c = 'work-north-star-hospital-surge-001'
  LIMIT 1
];

HFS_ContextRequest request = new HFS_ContextRequest();
request.contractVersion = HFS_ServiceContract.VERSION;
request.tenantKey = 'demo-mauritius';
request.workItemId = workItem.Id;
request.purpose = 'RESOLVE_HOSPITAL_OPERATION_RISK';
request.correlationId = '10000000-0000-4000-8000-000000000001';
request.includeProvenance = true;
request.timelineLimit = 100;

HFS_ContextResponse context = new HFS_RelationshipServiceImpl()
  .getContext(request);
System.assertEquals(0, context.errors.size());
System.assertEquals(
  'work-north-star-hospital-surge-001',
  context.workItem.externalKey
);
System.assertEquals(7, context.entities.size());
System.assertEquals(6, context.relationships.size());
System.assertEquals(7, context.evidence.size());
System.assertEquals(1, context.recommendations.size());
System.assertEquals(1, context.approvals.size());
System.assertEquals('PENDING', context.approvals[0].status);
System.assertEquals(
  'NORTH_STAR_HOSPITAL_RECOVERY_PLAN',
  context.recommendations[0].recordType
);

Set<String> entityTypes = new Set<String>();
Set<String> entityExternalKeys = new Set<String>();
for (HFS_ContextItem item : context.entities) {
  entityTypes.add(item.recordType);
  entityExternalKeys.add(item.externalKey);
}
System.assertEquals(true, entityTypes.contains('CUSTOMER_ALIAS'));
System.assertEquals(true, entityTypes.contains('LOCATION'));
System.assertEquals(true, entityTypes.contains('RESOURCE'));
System.assertEquals(true, entityTypes.contains('PARTNER'));
System.assertEquals(true, entityTypes.contains('PROCESS'));
System.assertEquals(
  true,
  entityExternalKeys.contains('ALIAS-PATIENT-GROUP-MORNING-001')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('DEPT-OUTPATIENT-RECEPTION')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('RESOURCE-WARD-A3-DISCHARGE-ROOMS')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('RESOURCE-PHARMACY-IV-KITS')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('PARTNER-ISLAND-DIAGNOSTICS')
);
System.assertEquals(
  true,
  entityExternalKeys.contains('PROCESS-BILLING-INSURANCE-REVIEW')
);

Set<String> evidenceTypes = new Set<String>();
for (HFS_EvidenceCitation citation : context.evidence) {
  evidenceTypes.add(citation.evidenceType);
}
System.assertEquals(true, evidenceTypes.contains('PATIENT_COMPLAINT_CLUSTER'));
System.assertEquals(true, evidenceTypes.contains('RESOURCE_CAPACITY'));
System.assertEquals(true, evidenceTypes.contains('PHARMACY_STOCK_POSITION'));
System.assertEquals(true, evidenceTypes.contains('PARTNER_RESPONSE_STATUS'));
System.assertEquals(true, evidenceTypes.contains('BILLING_AND_INSURANCE_HOLD'));
System.assertEquals(true, evidenceTypes.contains('STAFF_QUEUE_RISK'));
System.assertEquals(true, evidenceTypes.contains('CLINICAL_DECISION_REFUSAL'));

System.debug('HFS_DEMO_CONTEXT_VERIFIED:' + workItem.Id);
