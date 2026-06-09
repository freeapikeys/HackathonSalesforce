String tenantKey = 'demo-mauritius';
String correlationId = '20000000-0000-4000-8000-000000000001';
Datetime baseTime = Datetime.newInstanceGmt(2026, 6, 6, 9, 0, 0);

HFS_Event__c sourceEvent = new HFS_Event__c(
  Event_Id__c = 'event-north-star-retail-risk-001',
  Tenant_Key__c = tenantKey,
  Source_URI__c = 'urn:hfs:source:retail',
  Source_Record_Id__c = 'retail-event-stockout-001',
  Event_Type__c = 'STOCKOUT_RISK_DETECTED',
  Subject__c = 'Fresh beef patties weekend promotion risk',
  Occurred_At__c = baseTime,
  Observed_At__c = baseTime.addMinutes(1),
  Source_Sequence__c = 1,
  Idempotency_Key__c = 'event-north-star-retail-risk-001-v1',
  Correlation_Id__c = correlationId,
  Schema_Version__c = '1.0.0',
  Content_Hash__c = 'sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f',
  Payload_JSON__c = '{"eventcode":"STOCKOUT_RISK_DETECTED","productid":"PROD-FRESH-BEEF-PATTIES-400G","batchid":"BATCH-FRESH-BEEF-2026-06-07-A"}',
  Intake_Result__c = 'ACCEPTED'
);
insert sourceEvent;

HFS_Entity__c store = new HFS_Entity__c(
  External_Key__c = 'STORE-GOODLANDS-FRESHMART',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'ORGANIZATIONAL_UNIT',
  Display_Name__c = 'Goodlands FreshMart',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-60),
  Confidence__c = 1,
  Attributes_JSON__c = '{"role":"store","region":"north","country":"Mauritius"}'
);
HFS_Entity__c product = new HFS_Entity__c(
  External_Key__c = 'PROD-FRESH-BEEF-PATTIES-400G',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'PRODUCT',
  Display_Name__c = 'Island beef burger patties 400g',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-30),
  Confidence__c = 1,
  Attributes_JSON__c = '{"category":"fresh food","shelfAreaId":"SHELF-MEAT-CHILLER-A3"}'
);
HFS_Entity__c batch = new HFS_Entity__c(
  External_Key__c = 'BATCH-FRESH-BEEF-2026-06-07-A',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'PRODUCT_BATCH',
  Display_Name__c = 'Fresh beef patties batch A, use by 2026-06-08',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-2),
  Valid_To__c = Datetime.newInstanceGmt(2026, 6, 8, 23, 59, 0),
  Confidence__c = 0.99,
  Attributes_JSON__c = '{"expiryDate":"2026-06-08","nearExpiryQuantity":18}'
);
HFS_Entity__c supplier = new HFS_Entity__c(
  External_Key__c = 'SUPPLIER-ISLAND-PROTEINS',
  Tenant_Key__c = tenantKey,
  Entity_Type__c = 'SUPPLIER',
  Display_Name__c = 'Island Proteins Ltd',
  Source_Event__c = sourceEvent.Id,
  Valid_From__c = baseTime.addDays(-90),
  Confidence__c = 0.95,
  Attributes_JSON__c = '{"normalLeadTimeHours":36,"replacementLeadTimeHours":18}'
);
insert new List<HFS_Entity__c>{ store, product, batch, supplier };

insert new List<HFS_Event_Participant__c>{
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-store-north-star-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = store.Id,
    Participant_Role__c = 'STORE'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-product-north-star-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = product.Id,
    Participant_Role__c = 'PRODUCT'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-batch-north-star-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = batch.Id,
    Participant_Role__c = 'PRODUCT_BATCH'
  ),
  new HFS_Event_Participant__c(
    External_Key__c = 'participant-supplier-north-star-001',
    Tenant_Key__c = tenantKey,
    Event__c = sourceEvent.Id,
    Entity__c = supplier.Id,
    Participant_Role__c = 'SUPPLIER'
  )
};

insert new List<HFS_Relationship__c>{
  new HFS_Relationship__c(
    External_Key__c = 'relationship-store-product-north-star-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = store.Id,
    Object_Entity__c = product.Id,
    Relationship_Type__c = 'STOCKS_PRODUCT',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-30),
    Confidence__c = 1
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-product-batch-north-star-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = product.Id,
    Object_Entity__c = batch.Id,
    Relationship_Type__c = 'HAS_BATCH',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-2),
    Confidence__c = 0.99
  ),
  new HFS_Relationship__c(
    External_Key__c = 'relationship-product-supplier-north-star-001',
    Tenant_Key__c = tenantKey,
    Subject_Entity__c = product.Id,
    Object_Entity__c = supplier.Id,
    Relationship_Type__c = 'SUPPLIED_BY',
    Source_Event__c = sourceEvent.Id,
    Valid_From__c = baseTime.addDays(-90),
    Confidence__c = 0.96
  )
};

insert new HFS_Agreement__c(
  External_Key__c = 'PROMO-WEEKEND-GRILL-2026-W23',
  Tenant_Key__c = tenantKey,
  Party_One__c = store.Id,
  Party_Two__c = supplier.Id,
  Agreement_Type__c = 'RETAIL_PROMOTION',
  Status__c = 'ACTIVE',
  Terms_Summary__c = 'Weekend Grill promotion needs safe stock, correct shelf price, and supplier response before rush.',
  Material_Terms_JSON__c = '{"promotionId":"PROMO-WEEKEND-GRILL-2026-W23","shelfPrice":159,"posPrice":189,"currency":"MUR"}',
  Source_Event__c = sourceEvent.Id,
  Effective_From__c = baseTime.date(),
  Effective_To__c = baseTime.date().addDays(1)
);

HFS_Work_Item__c workItem = new HFS_Work_Item__c(
  External_Key__c = 'work-north-star-retail-risk-001',
  Tenant_Key__c = tenantKey,
  Primary_Entity__c = product.Id,
  Trigger_Event__c = sourceEvent.Id,
  Status__c = 'AWAITING_APPROVAL',
  Priority__c = 'HIGH',
  Summary__c = 'Resolve weekend promotion stockout, expiry, complaint, supplier, and queue risks.',
  Due_At__c = baseTime.addHours(4),
  Blocked_Reason__c = 'Manager approval is required before reorder, markdown, quarantine, staff alert, or customer-facing message.'
);
insert workItem;

insert new HFS_SOP_Execution__c(
  External_Key__c = 'sop-north-star-retail-risk-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Definition_Key__c = 'north-star-retail-recovery',
  Definition_Version__c = '1.0.0',
  Current_Step_Key__c = 'AWAIT_MANAGER_APPROVAL',
  Status__c = 'RUNNING',
  Started_At__c = baseTime.addMinutes(4)
);

HFS_Evidence__c inventoryEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-inventory-north-star-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = product.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'INVENTORY_POSITION',
  Summary__c = 'Shelf has 18 units, backroom has 24 units, warehouse has 72 units, supplier has 180 units, and promotion sales velocity is 28 units per hour.',
  Content_Hash__c = 'sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f',
  Source_URI__c = 'urn:hfs:source:retail:inventory',
  Captured_At__c = baseTime.addMinutes(1)
);
HFS_Evidence__c complaintEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-complaint-north-star-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = batch.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'COMPLAINT_CLUSTER',
  Summary__c = 'Five complaints mention smell, damaged packaging, refunds, and price mismatch for the same product, batch, store, and promotion window.',
  Content_Hash__c = 'sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb',
  Source_URI__c = 'urn:hfs:source:retail:complaints',
  Captured_At__c = baseTime.addMinutes(14)
);
HFS_Evidence__c supplierEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-supplier-north-star-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = supplier.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'SUPPLIER_RESPONSE',
  Summary__c = 'Supplier approved replacement batch B with 18-hour lead time and a credit note; quality issue is not supplier-wide.',
  Content_Hash__c = 'sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588',
  Source_URI__c = 'urn:hfs:source:retail:supplier',
  Captured_At__c = baseTime.addMinutes(25)
);
HFS_Evidence__c staffingEvidence = new HFS_Evidence__c(
  External_Key__c = 'evidence-staffing-north-star-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Related_Entity__c = store.Id,
  Source_Event__c = sourceEvent.Id,
  Evidence_Type__c = 'STAFFING_FORECAST',
  Summary__c = 'Queue risk is forecast from 16:30 to 18:30 with three baseline cashiers and four recommended cashiers.',
  Content_Hash__c = 'sha256:f42d186a12981c8c7a25b7be50f5f95541e4323f83f3f3c65de8e20717b5e6ea',
  Source_URI__c = 'urn:hfs:source:retail:roster',
  Captured_At__c = baseTime.addMinutes(30)
);
insert new List<HFS_Evidence__c>{
  inventoryEvidence,
  complaintEvidence,
  supplierEvidence,
  staffingEvidence
};

HFS_Recommendation__c recommendation = new HFS_Recommendation__c(
  External_Key__c = 'recommendation-north-star-retail-001',
  Tenant_Key__c = tenantKey,
  Work_Item__c = workItem.Id,
  Subject_Entity__c = product.Id,
  Primary_Evidence__c = inventoryEvidence.Id,
  Status__c = 'PENDING_APPROVAL',
  Recommendation_Type__c = 'NORTH_STAR_RETAIL_RECOVERY_PLAN',
  Proposed_Action_Type__c = 'APPROVE_RETAIL_RECOVERY_ACTIONS',
  Rationale__c = 'Facts: stock cover is low, batch A has near-expiry and complaint evidence, supplier approved replacement batch B, and queue risk is forecast later today. Inference: use warehouse transfer and replacement batch for availability, quarantine suspect units, mark down only safe near-expiry units, fix shelf price, and open one extra cashier lane. Manager approval is required before reorder, markdown, quarantine, staff alert, or customer-facing message.',
  Confidence__c = 0.86,
  Model_Profile__c = 'north-star-retail-recommendation',
  Model_Invocation_Id__c = 'model-invocation-north-star-001',
  Generated_At__c = baseTime.addMinutes(35)
);
insert recommendation;

insert new HFS_Approval__c(
  External_Key__c = 'approval-north-star-retail-001',
  Tenant_Key__c = tenantKey,
  Recommendation__c = recommendation.Id,
  Status__c = 'PENDING',
  Requested_At__c = baseTime.addMinutes(36),
  Policy_Key__c = 'north-star-manager-approval-v1'
);

System.debug('HFS_DEMO_SEED:' + workItem.Id);
