@IsTest
private class HFS_TwilioIntakeResourceTest {
  @IsTest
  static void createsSafeComplaintRecordsAndApproval() {
    System.runAs(createUser('twilio', 'HFS_Integration_User')) {
      Map<String, Object> requestBody = basePayload();
      requestBody.put(
        'rawBody',
        'I waited 90 minutes, the bill looks wrong, and pharmacy says stock is late.'
      );
      requestBody.put('from', 'whatsapp:+23057175190');

      HFS_TwilioIntakeResource.IntakeResponse response = post(requestBody);

      System.assertEquals(
        true,
        response.success,
        JSON.serialize(response.error)
      );
      System.assertEquals('ACCEPTED', response.status);
      System.assertNotEquals(null, response.workItemId);
      System.assert(response.categories.contains('WAIT_TIME'));
      System.assert(response.categories.contains('BILLING'));
      System.assert(response.categories.contains('PHARMACY_STOCK'));
      System.assertEquals(false, response.replayed);

      HFS_Event__c eventRecord = [
        SELECT Payload_JSON__c, Source_Record_Id__c
        FROM HFS_Event__c
        WHERE Id = :response.eventId
        LIMIT 1
      ];
      System.assertEquals('SM-test-001', eventRecord.Source_Record_Id__c);
      System.assert(!eventRecord.Payload_JSON__c.contains('+23057175190'));
      System.assert(!eventRecord.Payload_JSON__c.contains('waited 90 minutes'));
      System.assert(
        eventRecord.Payload_JSON__c.contains('"rawPhoneStored":false')
      );
      System.assert(
        eventRecord.Payload_JSON__c.contains('"rawMessageStored":false')
      );

      HFS_Recommendation__c recommendation = [
        SELECT Recommendation_Type__c, Proposed_Action_Type__c
        FROM HFS_Recommendation__c
        WHERE Id = :response.recommendationId
        LIMIT 1
      ];
      System.assertEquals(
        'NORTH_STAR_HOSPITAL_ACTION_PLAN',
        recommendation.Recommendation_Type__c
      );
      System.assertEquals(
        'APPROVE_HOSPITAL_ACTIONS',
        recommendation.Proposed_Action_Type__c
      );

      HFS_Approval__c approval = [
        SELECT Status__c
        FROM HFS_Approval__c
        WHERE Id = :response.approvalId
        LIMIT 1
      ];
      System.assertEquals('PENDING', approval.Status__c);
    }
  }

  @IsTest
  static void replaysDuplicateTwilioMessage() {
    System.runAs(createUser('twiliod', 'HFS_Integration_User')) {
      Map<String, Object> requestBody = basePayload();
      HFS_TwilioIntakeResource.IntakeResponse firstResponse = post(requestBody);
      HFS_TwilioIntakeResource.IntakeResponse duplicateResponse = post(
        requestBody
      );

      System.assertEquals(
        true,
        firstResponse.success,
        JSON.serialize(firstResponse.error)
      );
      System.assertEquals(
        true,
        duplicateResponse.success,
        JSON.serialize(duplicateResponse.error)
      );
      System.assertEquals(true, duplicateResponse.replayed);
      System.assertEquals(firstResponse.eventId, duplicateResponse.eventId);
      System.assertEquals(
        firstResponse.workItemId,
        duplicateResponse.workItemId
      );
    }
  }

  @IsTest
  static void routesClinicalRequestsWithoutClinicalDecision() {
    System.runAs(createUser('twilioc', 'HFS_Integration_User')) {
      Map<String, Object> requestBody = basePayload();
      requestBody.put('messageSid', 'SM-test-clinical');
      requestBody.put(
        'rawBody',
        'Can the bot diagnose me and decide treatment priority?'
      );
      requestBody.put('clinicalRequest', true);

      HFS_TwilioIntakeResource.IntakeResponse response = post(requestBody);

      System.assertEquals(
        true,
        response.success,
        JSON.serialize(response.error)
      );
      System.assert(response.categories.contains('CLINICAL_REQUEST'));
      HFS_Work_Item__c workItem = [
        SELECT Blocked_Reason__c
        FROM HFS_Work_Item__c
        WHERE Id = :response.workItemId
        LIMIT 1
      ];
      System.assert(
        workItem.Blocked_Reason__c.contains('cannot make clinical decisions')
      );

      HFS_Recommendation__c recommendation = [
        SELECT Recommendation_Type__c, Proposed_Action_Type__c, Rationale__c
        FROM HFS_Recommendation__c
        WHERE Id = :response.recommendationId
        LIMIT 1
      ];
      System.assertEquals(
        'NORTH_STAR_CLINICAL_BOUNDARY_ROUTE',
        recommendation.Recommendation_Type__c
      );
      System.assertEquals(
        'ROUTE_TO_CLINICIAN_REVIEW',
        recommendation.Proposed_Action_Type__c
      );
      System.assert(recommendation.Rationale__c.contains('must not decide'));
    }
  }

  private static HFS_TwilioIntakeResource.IntakeResponse post(
    Map<String, Object> payload
  ) {
    RestRequest request = new RestRequest();
    request.requestUri = '/services/apexrest/northstar/v1/twilio/whatsapp';
    request.httpMethod = 'POST';
    request.requestBody = Blob.valueOf(JSON.serialize(payload));
    RestContext.request = request;
    RestContext.response = new RestResponse();
    return HFS_TwilioIntakeResource.ingest();
  }

  private static Map<String, Object> basePayload() {
    return new Map<String, Object>{
      'tenantKey' => 'demo-mauritius',
      'purpose' => 'RESOLVE_HOSPITAL_OPERATION_RISK',
      'messageSid' => 'SM-test-001',
      'messageSummary' => 'A WhatsApp complaint mentions waiting time, billing, and pharmacy delay.',
      'sourceChannel' => 'Twilio Sandbox WhatsApp'
    };
  }

  private static User createUser(String key, String permissionSetName) {
    Profile minimumAccess = [
      SELECT Id
      FROM Profile
      WHERE Name = 'Minimum Access - Salesforce'
      LIMIT 1
    ];
    String uniqueValue =
      String.valueOf(System.now().getTime()) +
      String.valueOf(Math.abs(Crypto.getRandomInteger()));
    User userValue = new User(
      Alias = key.left(8),
      CommunityNickname = (key + uniqueValue).left(40),
      Email = key + uniqueValue + '@hfs.example',
      EmailEncodingKey = 'UTF-8',
      LanguageLocaleKey = 'en_US',
      LastName = 'HFS ' + key,
      LocaleSidKey = 'en_US',
      ProfileId = minimumAccess.Id,
      TimeZoneSidKey = 'America/Los_Angeles',
      Username = key + uniqueValue + '@hfs.example'
    );
    insert userValue;
    PermissionSet permissionSetValue = [
      SELECT Id
      FROM PermissionSet
      WHERE Name = :permissionSetName
      LIMIT 1
    ];
    insert new PermissionSetAssignment(
      AssigneeId = userValue.Id,
      PermissionSetId = permissionSetValue.Id
    );
    return userValue;
  }
}
