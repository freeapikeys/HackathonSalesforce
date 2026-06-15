public with sharing class HFS_RelationshipController {
  private static final String REQUEST_CORRECTION_REVIEW = 'REQUEST_CORRECTION_REVIEW';

  @AuraEnabled(cacheable=true)
  public static HFS_CommandCenterResponse loadCommandCenter(
    HFS_ContextRequest request
  ) {
    HFS_CommandCenterResponse response = new HFS_CommandCenterResponse();
    response.context = new HFS_RelationshipServiceImpl().getContext(request);
    response.permissions = currentPermissions();
    response.userLabel = UserInfo.getUserName();
    return response;
  }

  @AuraEnabled
  public static HFS_CommandResult decideApproval(
    HFS_ApprovalDecisionCommand command
  ) {
    return new HFS_RelationshipServiceImpl().decideApproval(command);
  }

  @AuraEnabled
  public static HFS_CommandResult requestCorrectionReview(
    HFS_CorrectionReviewCommand command
  ) {
    try {
      HFS_ServiceSupport.validateRequest(
        command == null ? null : command.contractVersion,
        command == null ? null : command.tenantKey,
        command == null ? null : command.purpose,
        command == null ? null : command.correlationId
      );
      HFS_ServiceSupport.requireText(command.externalKey, 'externalKey');
      HFS_ServiceSupport.requireText(command.targetLabel, 'targetLabel');
      HFS_ServiceSupport.requireText(command.reason, 'reason');
      if (
        String.isBlank(command.sourceRelationshipId) &&
        String.isBlank(command.sourceParticipantId)
      ) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.INVALID_REQUEST,
          'A source relationship or participant is required.',
          'sourceRelationshipId'
        );
      }

      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Work_Item__c,
        'HFS_Work_Item__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Evidence__c,
        'HFS_Evidence__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Recommendation__c,
        'HFS_Recommendation__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Approval__c,
        'HFS_Approval__c'
      );

      List<HFS_Work_Item__c> existingWork = [
        SELECT Id, Status__c
        FROM HFS_Work_Item__c
        WHERE
          Tenant_Key__c = :command.tenantKey
          AND External_Key__c = :command.externalKey
        WITH USER_MODE
        LIMIT 1
      ];
      if (!existingWork.isEmpty()) {
        return HFS_ServiceSupport.success(
          REQUEST_CORRECTION_REVIEW,
          command.correlationId,
          existingWork[0],
          existingWork[0].Status__c,
          true
        );
      }

      CorrectionSource source = correctionSource(command);
      HFS_ServiceSupport.requireTenant(
        command.tenantKey,
        source.tenantKey,
        'tenantKey'
      );

      Datetime nowValue = System.now();
      HFS_Work_Item__c workItem = new HFS_Work_Item__c(
        External_Key__c = command.externalKey,
        Tenant_Key__c = command.tenantKey,
        Primary_Entity__c = source.primaryEntityId,
        Trigger_Event__c = source.sourceEventId,
        Target_Relationship__c = source.relationshipId,
        Status__c = 'AWAITING_APPROVAL',
        Priority__c = 'MEDIUM',
        Summary__c = clipped(
          'Review relationship correction: ' + command.targetLabel,
          255
        ),
        Due_At__c = nowValue.addDays(1),
        Blocked_Reason__c = 'Supersession requires responsible-role approval.'
      );
      insert as user workItem;

      HFS_Evidence__c evidence = new HFS_Evidence__c(
        External_Key__c = command.externalKey + '-evidence',
        Tenant_Key__c = command.tenantKey,
        Work_Item__c = workItem.Id,
        Related_Entity__c = source.primaryEntityId,
        Source_Event__c = source.sourceEventId,
        Evidence_Type__c = 'RELATIONSHIP_CORRECTION_REVIEW',
        Summary__c = command.reason,
        Content_Hash__c = hashFor(command),
        Source_URI__c = source.sourceUri,
        Captured_At__c = nowValue
      );
      insert as user evidence;

      HFS_Recommendation__c recommendation = new HFS_Recommendation__c(
        External_Key__c = command.externalKey + '-recommendation',
        Tenant_Key__c = command.tenantKey,
        Work_Item__c = workItem.Id,
        Subject_Entity__c = source.primaryEntityId,
        Primary_Evidence__c = evidence.Id,
        Status__c = 'PENDING_APPROVAL',
        Recommendation_Type__c = 'RELATIONSHIP_CORRECTION_REVIEW',
        Proposed_Action_Type__c = 'SUPERSEDE_RELATIONSHIP_ASSERTION',
        Rationale__c = command.reason,
        Confidence__c = null,
        Model_Profile__c = 'governed-correction-review',
        Model_Invocation_Id__c = command.correlationId,
        Generated_At__c = nowValue
      );
      insert as user recommendation;

      HFS_Approval__c approval = new HFS_Approval__c(
        External_Key__c = command.externalKey + '-approval',
        Tenant_Key__c = command.tenantKey,
        Recommendation__c = recommendation.Id,
        Status__c = 'PENDING',
        Requested_At__c = nowValue,
        Policy_Key__c = 'relationship-correction-review-v1'
      );
      insert as user approval;

      return HFS_ServiceSupport.success(
        REQUEST_CORRECTION_REVIEW,
        command.correlationId,
        workItem,
        workItem.Status__c,
        false
      );
    } catch (Exception exceptionValue) {
      return HFS_ServiceSupport.failure(
        REQUEST_CORRECTION_REVIEW,
        command == null ? null : command.correlationId,
        exceptionValue
      );
    }
  }

  private static HFS_CommandCenterPermissions currentPermissions() {
    HFS_CommandCenterPermissions permissions = new HFS_CommandCenterPermissions();
    Boolean canDecideApproval =
      FeatureManagement.checkPermission('HFS_Approve_Recommendation') &&
      Schema.SObjectType.HFS_Approval__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Status__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Decision_By__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Decided_At__c.isUpdateable() &&
      Schema.SObjectType.HFS_Approval__c.fields.Decision_Notes__c.isUpdateable();

    permissions.canApprove = canDecideApproval;
    permissions.canModify = canCreateCorrectionReview();
    permissions.canReject = canDecideApproval;
    permissions.canExecute =
      FeatureManagement.checkPermission('HFS_Execute_Action') &&
      Schema.SObjectType.HFS_Action__c.isCreateable();
    return permissions;
  }

  private static Boolean canCreateCorrectionReview() {
    return Schema.SObjectType.HFS_Work_Item__c.isCreateable() &&
      Schema.SObjectType.HFS_Evidence__c.isCreateable() &&
      Schema.SObjectType.HFS_Recommendation__c.isCreateable() &&
      Schema.SObjectType.HFS_Approval__c.isCreateable();
  }

  private static CorrectionSource correctionSource(
    HFS_CorrectionReviewCommand command
  ) {
    if (!String.isBlank(command.sourceRelationshipId)) {
      Id relationshipId = HFS_ServiceSupport.requireId(
        command.sourceRelationshipId,
        'sourceRelationshipId'
      );
      List<HFS_Relationship__c> relationships = [
        SELECT
          Id,
          Tenant_Key__c,
          Subject_Entity__c,
          Object_Entity__c,
          Source_Event__c,
          Source_Event__r.Source_URI__c
        FROM HFS_Relationship__c
        WHERE Id = :relationshipId
        WITH USER_MODE
        LIMIT 1
      ];
      if (relationships.isEmpty()) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.RECORD_NOT_FOUND,
          'No accessible source relationship was found.',
          'sourceRelationshipId'
        );
      }
      HFS_Relationship__c relationship = relationships[0];
      return new CorrectionSource(
        relationship.Tenant_Key__c,
        relationship.Id,
        relationship.Subject_Entity__c,
        relationship.Source_Event__c,
        relationship.Source_Event__r.Source_URI__c
      );
    }

    Id participantId = HFS_ServiceSupport.requireId(
      command.sourceParticipantId,
      'sourceParticipantId'
    );
    List<HFS_Event_Participant__c> participants = [
      SELECT Id, Tenant_Key__c, Entity__c, Event__c, Event__r.Source_URI__c
      FROM HFS_Event_Participant__c
      WHERE Id = :participantId
      WITH USER_MODE
      LIMIT 1
    ];
    if (participants.isEmpty()) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.RECORD_NOT_FOUND,
        'No accessible source participant was found.',
        'sourceParticipantId'
      );
    }
    HFS_Event_Participant__c participant = participants[0];
    return new CorrectionSource(
      participant.Tenant_Key__c,
      null,
      participant.Entity__c,
      participant.Event__c,
      participant.Event__r.Source_URI__c
    );
  }

  private static String clipped(String value, Integer maxLength) {
    return value.length() <= maxLength ? value : value.substring(0, maxLength);
  }

  private static String hashFor(HFS_CorrectionReviewCommand command) {
    Blob payload = Blob.valueOf(
      String.join(
        new List<String>{
          command.tenantKey,
          command.externalKey,
          command.sourceRelationshipId,
          command.sourceParticipantId,
          command.targetLabel,
          command.reason
        },
        '|'
      )
    );
    return 'sha256:' +
      EncodingUtil.convertToHex(Crypto.generateDigest('SHA-256', payload));
  }

  private class CorrectionSource {
    String tenantKey;
    Id relationshipId;
    Id primaryEntityId;
    Id sourceEventId;
    String sourceUri;

    CorrectionSource(
      String tenantKey,
      Id relationshipId,
      Id primaryEntityId,
      Id sourceEventId,
      String sourceUri
    ) {
      this.tenantKey = tenantKey;
      this.relationshipId = relationshipId;
      this.primaryEntityId = primaryEntityId;
      this.sourceEventId = sourceEventId;
      this.sourceUri = sourceUri;
    }
  }
}
