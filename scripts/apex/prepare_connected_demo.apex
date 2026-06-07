String tenantKey = 'demo-mauritius';

delete [SELECT Id FROM HFS_Approval__c WHERE Tenant_Key__c = :tenantKey];
delete [
  SELECT Id
  FROM HFS_Recommendation__c
  WHERE Tenant_Key__c = :tenantKey
];

System.assertEquals(
  0,
  [SELECT COUNT() FROM HFS_Recommendation__c WHERE Tenant_Key__c = :tenantKey]
);
System.assertEquals(
  0,
  [SELECT COUNT() FROM HFS_Approval__c WHERE Tenant_Key__c = :tenantKey]
);

System.debug('HFS_DEMO_CONNECTED_PREPARED:' + tenantKey);
