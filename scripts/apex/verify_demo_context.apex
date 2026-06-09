HFS_Work_Item__c workItem = [
  SELECT Id
  FROM HFS_Work_Item__c
  WHERE
    Tenant_Key__c = 'demo-mauritius'
    AND External_Key__c = 'work-north-star-retail-risk-001'
  LIMIT 1
];

HFS_ContextRequest request = new HFS_ContextRequest();
request.contractVersion = HFS_ServiceContract.VERSION;
request.tenantKey = 'demo-mauritius';
request.workItemId = workItem.Id;
request.purpose = 'NORTH_STAR_RETAIL_SERVICE';
request.correlationId = '20000000-0000-4000-8000-000000000001';
request.includeProvenance = true;
request.timelineLimit = 100;

HFS_ContextResponse context = new HFS_RelationshipServiceImpl().getContext(
  request
);
System.assertEquals(0, context.errors.size());
System.assertEquals(
  'work-north-star-retail-risk-001',
  context.workItem.externalKey
);
System.assertEquals(4, context.entities.size());
System.assertEquals(3, context.relationships.size());
System.assertEquals(4, context.evidence.size());
System.assertEquals(1, context.recommendations.size());
System.assertEquals(1, context.approvals.size());
System.assertEquals('PENDING', context.approvals[0].status);
System.assertEquals(
  'NORTH_STAR_RETAIL_RECOVERY_PLAN',
  context.recommendations[0].recordType
);

System.debug('HFS_DEMO_CONTEXT_VERIFIED:' + workItem.Id);
