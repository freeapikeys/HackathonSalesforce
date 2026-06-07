String tenantKey = 'demo-mauritius';

delete [SELECT Id FROM HFS_Evaluation__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Outcome__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Action__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Approval__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Recommendation__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Evidence__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_SOP_Execution__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Work_Item__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Agreement__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Relationship__c WHERE Tenant_Key__c = :tenantKey];
delete [
  SELECT Id
  FROM HFS_Event_Participant__c
  WHERE Tenant_Key__c = :tenantKey
];
delete [SELECT Id FROM HFS_Entity__c WHERE Tenant_Key__c = :tenantKey];
delete [SELECT Id FROM HFS_Event__c WHERE Tenant_Key__c = :tenantKey];

System.debug('HFS_DEMO_RESET:' + tenantKey);
