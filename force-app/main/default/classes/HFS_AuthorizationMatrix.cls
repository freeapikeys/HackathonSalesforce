public class HFS_AuthorizationMatrix {
  public static final String RELATIONSHIP_USER = 'HFS_Relationship_User';
  public static final String APPROVER = 'HFS_Approver';
  public static final String INTEGRATION_USER = 'HFS_Integration_User';

  public static List<HFS_AuthorizationPolicy> allPolicies() {
    List<HFS_AuthorizationPolicy> policies = new List<HFS_AuthorizationPolicy>();
    for (String operation : HFS_ServiceContract.OPERATIONS) {
      policies.add(forOperation(operation));
    }
    return policies;
  }

  public static HFS_AuthorizationPolicy forOperation(String operation) {
    HFS_AuthorizationPolicy policy = basePolicy(operation);

    switch on operation {
      when 'READ_CONTEXT' {
        policy.allowedBaselineRoles = roles(
          RELATIONSHIP_USER,
          APPROVER,
          INTEGRATION_USER
        );
        policy.readableObjects = contextObjects();
        policy.readableFields = allFields(contextObjects());
        policy.transactionBoundary = 'READ_ONLY';
      }
      when 'READ_PROVENANCE' {
        policy.allowedBaselineRoles = roles(
          RELATIONSHIP_USER,
          APPROVER,
          INTEGRATION_USER
        );
        policy.readableObjects = values(
          'ROOT_RECORD',
          'HFS_Event__c',
          'HFS_Evidence__c'
        );
        policy.readableFields = values(
          'ROOT_RECORD.*',
          'HFS_Event__c.*',
          'HFS_Evidence__c.*'
        );
        policy.transactionBoundary = 'READ_ONLY';
      }
      when 'PERSIST_EVENT' {
        policy.allowedBaselineRoles = roles(INTEGRATION_USER);
        policy.readableObjects = values('HFS_Event__c');
        policy.creatableObjects = values('HFS_Event__c');
        policy.readableFields = allFields(policy.readableObjects);
        policy.writableFields = eventFields();
        policy.transactionBoundary = 'ALL_OR_NOTHING_DML';
      }
      when 'STORE_RECOMMENDATION' {
        policy.allowedBaselineRoles = roles(
          RELATIONSHIP_USER,
          INTEGRATION_USER
        );
        policy.readableObjects = values(
          'HFS_Work_Item__c',
          'HFS_Entity__c',
          'HFS_Evidence__c'
        );
        policy.creatableObjects = values('HFS_Recommendation__c');
        policy.updatableObjects = values('HFS_Recommendation__c');
        policy.readableFields = allFields(policy.readableObjects);
        policy.writableFields = recommendationFields();
        policy.transactionBoundary = 'ALL_OR_NOTHING_DML';
      }
      when 'REQUEST_APPROVAL' {
        policy.allowedBaselineRoles = roles(APPROVER, INTEGRATION_USER);
        policy.readableObjects = values('HFS_Recommendation__c');
        policy.creatableObjects = values('HFS_Approval__c');
        policy.readableFields = allFields(policy.readableObjects);
        policy.writableFields = approvalRequestFields();
        policy.transactionBoundary = 'ALL_OR_NOTHING_DML';
      }
      when 'DECIDE_APPROVAL' {
        policy.allowedBaselineRoles = roles(APPROVER);
        policy.readableObjects = values(
          'HFS_Approval__c',
          'HFS_Recommendation__c',
          'HFS_Work_Item__c',
          'HFS_Relationship__c'
        );
        policy.updatableObjects = values(
          'HFS_Approval__c',
          'HFS_Relationship__c'
        );
        policy.readableFields = allFields(policy.readableObjects);
        policy.writableFields = approvalDecisionFields();
        policy.customPermissions = values('HFS_Approve_Recommendation');
        policy.transactionBoundary = 'ALL_OR_NOTHING_DML';
      }
      when 'LOG_ACTION' {
        policy.allowedBaselineRoles = roles(INTEGRATION_USER);
        policy.readableObjects = values(
          'HFS_Recommendation__c',
          'HFS_Approval__c',
          'HFS_Entity__c'
        );
        policy.creatableObjects = values('HFS_Action__c');
        policy.readableFields = allFields(policy.readableObjects);
        policy.writableFields = actionFields();
        policy.customPermissions = values('HFS_Execute_Action');
        policy.transactionBoundary = 'LOG_PENDING_ACTION_ONLY';
      }
      when 'CAPTURE_OUTCOME' {
        policy.allowedBaselineRoles = roles(INTEGRATION_USER);
        policy.readableObjects = values(
          'HFS_Action__c',
          'HFS_Event__c',
          'HFS_Recommendation__c'
        );
        policy.creatableObjects = values('HFS_Outcome__c');
        policy.updatableObjects = values('HFS_Action__c', 'HFS_Work_Item__c');
        policy.readableFields = allFields(policy.readableObjects);
        policy.writableFields = outcomeFields();
        policy.customPermissions = values('HFS_Execute_Action');
        policy.transactionBoundary = 'ALL_OR_NOTHING_DML';
      }
      when else {
        throw new UnknownOperationException(
          'Unknown HFS service operation: ' + operation
        );
      }
    }

    return policy;
  }

  public static Boolean baselineRoleExpectedToPass(
    String role,
    String operation
  ) {
    return forOperation(operation).allowedBaselineRoles.contains(role);
  }

  private static HFS_AuthorizationPolicy basePolicy(String operation) {
    HFS_AuthorizationPolicy policy = new HFS_AuthorizationPolicy();
    policy.operation = operation;
    policy.sharingMode = 'WITH_SHARING';
    policy.dataAccessMode = 'USER_MODE';
    policy.externalCalloutAllowed = false;
    policy.allowedBaselineRoles = new List<String>();
    policy.readableObjects = new List<String>();
    policy.creatableObjects = new List<String>();
    policy.updatableObjects = new List<String>();
    policy.readableFields = new List<String>();
    policy.writableFields = new List<String>();
    policy.customPermissions = new List<String>();
    return policy;
  }

  private static List<String> contextObjects() {
    return new List<String>{
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
  }

  private static List<String> recommendationFields() {
    return new List<String>{
      'HFS_Recommendation__c.External_Key__c',
      'HFS_Recommendation__c.Tenant_Key__c',
      'HFS_Recommendation__c.Work_Item__c',
      'HFS_Recommendation__c.Subject_Entity__c',
      'HFS_Recommendation__c.Primary_Evidence__c',
      'HFS_Recommendation__c.Status__c',
      'HFS_Recommendation__c.Recommendation_Type__c',
      'HFS_Recommendation__c.Proposed_Action_Type__c',
      'HFS_Recommendation__c.Rationale__c',
      'HFS_Recommendation__c.Confidence__c',
      'HFS_Recommendation__c.Model_Profile__c',
      'HFS_Recommendation__c.Model_Invocation_Id__c',
      'HFS_Recommendation__c.Generated_At__c'
    };
  }

  private static List<String> eventFields() {
    return new List<String>{
      'HFS_Event__c.Event_Id__c',
      'HFS_Event__c.Tenant_Key__c',
      'HFS_Event__c.Event_Type__c',
      'HFS_Event__c.Source_URI__c',
      'HFS_Event__c.Subject__c',
      'HFS_Event__c.Source_Record_Id__c',
      'HFS_Event__c.Schema_Version__c',
      'HFS_Event__c.Correlation_Id__c',
      'HFS_Event__c.Causation_Id__c',
      'HFS_Event__c.Idempotency_Key__c',
      'HFS_Event__c.Source_Sequence__c',
      'HFS_Event__c.Occurred_At__c',
      'HFS_Event__c.Observed_At__c',
      'HFS_Event__c.Content_Hash__c',
      'HFS_Event__c.Payload_JSON__c',
      'HFS_Event__c.Intake_Result__c'
    };
  }

  private static List<String> approvalRequestFields() {
    return values(
      'HFS_Approval__c.External_Key__c',
      'HFS_Approval__c.Tenant_Key__c',
      'HFS_Approval__c.Recommendation__c',
      'HFS_Approval__c.Status__c',
      'HFS_Approval__c.Requested_At__c',
      'HFS_Approval__c.Policy_Key__c'
    );
  }

  private static List<String> approvalDecisionFields() {
    return new List<String>{
      'HFS_Approval__c.Status__c',
      'HFS_Approval__c.Decision_By__c',
      'HFS_Approval__c.Decided_At__c',
      'HFS_Approval__c.Decision_Notes__c',
      'HFS_Relationship__c.Valid_To__c',
      'HFS_Relationship__c.Supersession_Approval__c',
      'HFS_Relationship__c.Superseded_By_User__c',
      'HFS_Relationship__c.Superseded_At__c',
      'HFS_Relationship__c.Supersession_Reason__c'
    };
  }

  private static List<String> actionFields() {
    return new List<String>{
      'HFS_Action__c.External_Key__c',
      'HFS_Action__c.Tenant_Key__c',
      'HFS_Action__c.Recommendation__c',
      'HFS_Action__c.Approval__c',
      'HFS_Action__c.Target_Entity__c',
      'HFS_Action__c.Status__c',
      'HFS_Action__c.Action_Type__c',
      'HFS_Action__c.Requested_At__c',
      'HFS_Action__c.Correlation_Id__c',
      'HFS_Action__c.Idempotency_Key__c'
    };
  }

  private static List<String> outcomeFields() {
    return new List<String>{
      'HFS_Outcome__c.External_Key__c',
      'HFS_Outcome__c.Tenant_Key__c',
      'HFS_Outcome__c.Action__c',
      'HFS_Outcome__c.Source_Event__c',
      'HFS_Outcome__c.Outcome_Type__c',
      'HFS_Outcome__c.Status__c',
      'HFS_Outcome__c.Observed_At__c',
      'HFS_Outcome__c.Summary__c',
      'HFS_Outcome__c.Metric_Key__c',
      'HFS_Outcome__c.Metric_Value__c',
      'HFS_Action__c.Status__c',
      'HFS_Action__c.Executed_At__c',
      'HFS_Action__c.External_Reference__c',
      'HFS_Action__c.Failure_Detail__c',
      'HFS_Work_Item__c.Status__c',
      'HFS_Work_Item__c.Handoff_State__c',
      'HFS_Work_Item__c.Closure_Verification_Status__c',
      'HFS_Work_Item__c.Closure_Verified_At__c',
      'HFS_Work_Item__c.Closure_Outcome__c'
    };
  }

  private static List<String> allFields(List<String> objectApiNames) {
    List<String> fields = new List<String>();
    for (String objectApiName : objectApiNames) {
      fields.add(objectApiName + '.*');
    }
    return fields;
  }

  private static List<String> roles(String firstRole) {
    return values(firstRole);
  }

  private static List<String> roles(String firstRole, String secondRole) {
    return values(firstRole, secondRole);
  }

  private static List<String> roles(
    String firstRole,
    String secondRole,
    String thirdRole
  ) {
    return values(firstRole, secondRole, thirdRole);
  }

  private static List<String> values(String firstValue) {
    return new List<String>{ firstValue };
  }

  private static List<String> values(String firstValue, String secondValue) {
    return new List<String>{ firstValue, secondValue };
  }

  private static List<String> values(
    String firstValue,
    String secondValue,
    String thirdValue
  ) {
    return new List<String>{ firstValue, secondValue, thirdValue };
  }

  private static List<String> values(
    String firstValue,
    String secondValue,
    String thirdValue,
    String fourthValue
  ) {
    return new List<String>{ firstValue, secondValue, thirdValue, fourthValue };
  }

  private static List<String> values(
    String firstValue,
    String secondValue,
    String thirdValue,
    String fourthValue,
    String fifthValue
  ) {
    return new List<String>{
      firstValue,
      secondValue,
      thirdValue,
      fourthValue,
      fifthValue
    };
  }

  private static List<String> values(
    String firstValue,
    String secondValue,
    String thirdValue,
    String fourthValue,
    String fifthValue,
    String sixthValue
  ) {
    return new List<String>{
      firstValue,
      secondValue,
      thirdValue,
      fourthValue,
      fifthValue,
      sixthValue
    };
  }

  public class UnknownOperationException extends Exception {
  }
}
