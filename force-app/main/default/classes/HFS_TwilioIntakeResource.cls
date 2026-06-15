@RestResource(urlMapping='/logia/v1/twilio/whatsapp')
global with sharing class HFS_TwilioIntakeResource {
  private static final String DEFAULT_TENANT = 'demo-mauritius';
  private static final String DEFAULT_PURPOSE = 'RESOLVE_HOSPITAL_OPERATION_RISK';
  private static final String DEFAULT_SOURCE_CHANNEL = 'Twilio Sandbox WhatsApp';

  global class IntakeResponse {
    public Boolean success;
    public Boolean replayed;
    public String status;
    public String message;
    public String tenantKey;
    public String correlationId;
    public String eventId;
    public String workItemId;
    public String evidenceId;
    public String recommendationId;
    public String approvalId;
    public List<String> categories;
    public List<String> affectedPrimitives;
    public List<String> followUpQuestions;
    public List<String> rootCauseHypotheses;
    public List<String> missingEvidence;
    public String languageCode;
    public String replyLanguage;
    public String commandCenterHint;
    public HFS_ServiceError error;
  }

  @HttpPost
  global static IntakeResponse ingest() {
    IntakeResponse response = new IntakeResponse();
    response.success = false;
    response.replayed = false;
    response.status = 'ERROR';
    try {
      Map<String, Object> payload = requestPayload();
      String tenantKey = text(payload, 'tenantKey', DEFAULT_TENANT);
      String purpose = text(payload, 'purpose', DEFAULT_PURPOSE);
      String sourceRecordId = firstText(
        payload,
        new List<String>{ 'messageSid', 'sourceRecordId', 'MessageSid' },
        null
      );
      HFS_ServiceSupport.requireText(sourceRecordId, 'messageSid');

      String rawBody = firstText(
        payload,
        new List<String>{ 'rawBody', 'body', 'Body' },
        ''
      );
      String providedSummary = firstText(
        payload,
        new List<String>{ 'messageSummary', 'bodySummary', 'summary' },
        ''
      );
      String summary = String.isBlank(providedSummary)
        ? summarize(rawBody)
        : clean(providedSummary, 500);
      HFS_ServiceSupport.requireText(summary, 'messageSummary');
      String languageCode = detectedLanguage(payload, rawBody + ' ' + summary);
      String replyLanguage = languageName(languageCode);
      Map<String, Object> mediaInfo = mediaInfo(payload);
      String sourceChannel = sourceChannel(payload);
      String sourceUri = sourceUri(sourceChannel);

      String correlationId = text(
        payload,
        'correlationId',
        pseudoUuid('correlation:' + tenantKey + ':' + sourceRecordId)
      );
      HFS_ServiceSupport.validateRequest(
        HFS_ServiceContract.VERSION,
        tenantKey,
        purpose,
        correlationId
      );

      ExistingIntake existing = existingIntake(tenantKey, sourceRecordId);
      if (existing != null) {
        response.success = true;
        response.replayed = true;
        response.status = 'DUPLICATE';
        response.message = 'We already received this WhatsApp complaint.';
        response.tenantKey = tenantKey;
        response.correlationId = correlationId;
        response.eventId = existing.eventId;
        response.workItemId = existing.workItemId;
        response.evidenceId = existing.evidenceId;
        response.recommendationId = existing.recommendationId;
        response.approvalId = existing.approvalId;
        response.commandCenterHint = commandCenterHint(existing.workItemId);
        RestContext.response.statusCode = 202;
        return response;
      }

      List<String> categories = categories(payload, rawBody + ' ' + summary);
      Boolean clinicalRequest =
        boolValue(payload, 'clinicalRequest') ||
        categories.contains('CLINICAL_REQUEST');
      List<String> affectedPrimitives = affectedPrimitives(categories);
      List<String> followUpQuestions = followUpQuestions(categories);
      List<String> hypotheses = hypotheses(categories, clinicalRequest);
      List<String> missingEvidence = missingEvidence(categories);
      String bodyHash = hashText(rawBody);
      String fromHash = firstText(
        payload,
        new List<String>{ 'fromHash', 'customerHash' },
        ''
      );
      if (String.isBlank(fromHash)) {
        fromHash = hashText(
          firstText(payload, new List<String>{ 'from', 'From' }, '')
        );
      }
      String aliasKey = 'ALIAS-WHATSAPP-' + shortHash(fromHash);
      Datetime observedAt = System.now();

      Map<String, Object> safePayload = new Map<String, Object>{
        'sourceChannel' => sourceChannel,
        'messageSid' => sourceRecordId,
        'customerAlias' => aliasKey,
        'fromHash' => fromHash,
        'bodyHash' => bodyHash,
        'messageSummary' => summary,
        'media' => mediaInfo,
        'languageCode' => languageCode,
        'replyLanguage' => replyLanguage,
        'categories' => categories,
        'affectedPrimitives' => affectedPrimitives,
        'followUpQuestions' => followUpQuestions,
        'rootCauseHypotheses' => hypotheses,
        'missingEvidence' => missingEvidence,
        'clinicalRequest' => clinicalRequest,
        'rawPhoneStored' => false,
        'rawMessageStored' => false
      };
      String safeJson = JSON.serialize(safePayload);
      String safeHash = hashText(safeJson);

      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Event__c,
        'HFS_Event__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Entity__c,
        'HFS_Entity__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Event_Participant__c,
        'HFS_Event_Participant__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Work_Item__c,
        'HFS_Work_Item__c'
      );
      HFS_ServiceSupport.requireCreate(
        Schema.SObjectType.HFS_Evidence__c,
        'HFS_Evidence__c'
      );

      HFS_Event__c eventRecord = new HFS_Event__c(
        Event_Id__c = pseudoUuid('event:' + tenantKey + ':' + sourceRecordId),
        Tenant_Key__c = tenantKey,
        Source_URI__c = sourceUri,
        Source_Record_Id__c = sourceRecordId,
        Event_Type__c = clinicalRequest
          ? 'WHATSAPP_CLINICAL_REQUEST_ROUTED'
          : 'WHATSAPP_COMPLAINT_RECEIVED',
        Subject__c = clinicalRequest
          ? 'WhatsApp request routed to clinician or manager'
          : 'WhatsApp customer complaint received',
        Occurred_At__c = observedAt,
        Observed_At__c = observedAt,
        Source_Sequence__c = 1,
        Idempotency_Key__c = 'whatsapp-intake-' + sourceRecordId,
        Correlation_Id__c = correlationId,
        Schema_Version__c = HFS_ServiceContract.VERSION,
        Content_Hash__c = safeHash,
        Payload_JSON__c = safeJson,
        Intake_Result__c = 'ACCEPTED'
      );
      insert eventRecord;

      HFS_Entity__c customerAlias = upsertAlias(
        tenantKey,
        aliasKey,
        eventRecord.Id,
        observedAt,
        fromHash,
        sourceChannel
      );

      insert new HFS_Event_Participant__c(
        External_Key__c = 'participant-' + shortHash(sourceRecordId),
        Tenant_Key__c = tenantKey,
        Event__c = eventRecord.Id,
        Entity__c = customerAlias.Id,
        Participant_Role__c = 'CUSTOMER_ALIAS'
      );

      HFS_Work_Item__c workItem = new HFS_Work_Item__c(
        External_Key__c = 'work-whatsapp-' + shortHash(sourceRecordId),
        Tenant_Key__c = tenantKey,
        Primary_Entity__c = customerAlias.Id,
        Trigger_Event__c = eventRecord.Id,
        Status__c = clinicalRequest ? 'IN_PROGRESS' : 'AWAITING_APPROVAL',
        Priority__c = clinicalRequest ? 'CRITICAL' : priority(categories),
        Summary__c = workSummary(categories, clinicalRequest),
        Due_At__c = observedAt.addHours(clinicalRequest ? 1 : 2),
        Blocked_Reason__c = clinicalRequest
          ? 'Logia cannot make clinical decisions. Route this to a clinician or manager.'
          : 'Manager approval is required before Slack, WhatsApp, billing, pharmacy, vendor, room, staff-task, or patient-message write-back.'
      );
      insert workItem;

      HFS_Evidence__c evidence = new HFS_Evidence__c(
        External_Key__c = 'evidence-whatsapp-' + shortHash(sourceRecordId),
        Tenant_Key__c = tenantKey,
        Work_Item__c = workItem.Id,
        Related_Entity__c = customerAlias.Id,
        Source_Event__c = eventRecord.Id,
        Evidence_Type__c = clinicalRequest
          ? 'CLINICAL_DECISION_REFUSAL'
          : 'WHATSAPP_COMPLAINT_INTAKE',
        Summary__c = evidenceSummary(
          summary,
          categories,
          clinicalRequest,
          languageCode,
          replyLanguage,
          mediaInfo
        ),
        Content_Hash__c = safeHash,
        Source_URI__c = sourceUri,
        Captured_At__c = observedAt
      );
      insert evidence;

      HFS_CommandResult recommendation = storeRecommendation(
        tenantKey,
        purpose,
        correlationId,
        sourceRecordId,
        workItem.Id,
        customerAlias.Id,
        evidence.Id,
        categories,
        hypotheses,
        missingEvidence,
        clinicalRequest
      );
      if (!recommendation.success) {
        throw new HFS_ServiceException(
          'VALIDATION_FAILED|||recommendation|||Recommendation could not be stored.'
        );
      }

      HFS_CommandResult approval = requestApproval(
        tenantKey,
        purpose,
        correlationId,
        sourceRecordId,
        recommendation.recordId,
        clinicalRequest
      );
      if (!approval.success) {
        throw new HFS_ServiceException(
          'VALIDATION_FAILED|||approval|||Approval could not be requested.'
        );
      }

      response.success = true;
      response.status = 'ACCEPTED';
      response.message = responseMessage(clinicalRequest, languageCode);
      response.tenantKey = tenantKey;
      response.correlationId = correlationId;
      response.eventId = eventRecord.Id;
      response.workItemId = workItem.Id;
      response.evidenceId = evidence.Id;
      response.recommendationId = recommendation.recordId;
      response.approvalId = approval.recordId;
      response.categories = categories;
      response.affectedPrimitives = affectedPrimitives;
      response.followUpQuestions = followUpQuestions;
      response.rootCauseHypotheses = hypotheses;
      response.missingEvidence = missingEvidence;
      response.languageCode = languageCode;
      response.replyLanguage = replyLanguage;
      response.commandCenterHint = commandCenterHint(workItem.Id);
      RestContext.response.statusCode = 202;
      return response;
    } catch (Exception exceptionValue) {
      HFS_ServiceError errorValue = HFS_ServiceSupport.error(exceptionValue);
      if (Test.isRunningTest()) {
        errorValue.details =
          exceptionValue.getTypeName() +
          ': ' +
          exceptionValue.getMessage() +
          ' at ' +
          exceptionValue.getStackTraceString();
      }
      response.status = errorValue.code;
      response.message = errorValue.message;
      response.error = errorValue;
      RestContext.response.statusCode = errorValue.code ==
        HFS_ServiceContract.INVALID_REQUEST
        ? 400
        : 500;
      return response;
    }
  }

  private static Map<String, Object> requestPayload() {
    if (
      RestContext.request == null ||
      RestContext.request.requestBody == null ||
      String.isBlank(RestContext.request.requestBody.toString())
    ) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'A JSON request body is required.',
        'body'
      );
    }
    Object parsed = JSON.deserializeUntyped(
      RestContext.request.requestBody.toString()
    );
    if (!(parsed instanceof Map<String, Object>)) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'The request body must be a JSON object.',
        'body'
      );
    }
    return (Map<String, Object>) parsed;
  }

  private static ExistingIntake existingIntake(
    String tenantKey,
    String sourceRecordId
  ) {
    List<HFS_Event__c> events = [
      SELECT Id
      FROM HFS_Event__c
      WHERE Tenant_Key__c = :tenantKey AND Source_Record_Id__c = :sourceRecordId
      LIMIT 1
    ];
    if (events.isEmpty()) {
      return null;
    }
    ExistingIntake existing = new ExistingIntake();
    existing.eventId = String.valueOf(events[0].Id);
    List<HFS_Work_Item__c> workItems = [
      SELECT Id
      FROM HFS_Work_Item__c
      WHERE Tenant_Key__c = :tenantKey AND Trigger_Event__c = :events[0].Id
      LIMIT 1
    ];
    if (!workItems.isEmpty()) {
      existing.workItemId = String.valueOf(workItems[0].Id);
      List<HFS_Evidence__c> evidence = [
        SELECT Id
        FROM HFS_Evidence__c
        WHERE Tenant_Key__c = :tenantKey AND Work_Item__c = :workItems[0].Id
        LIMIT 1
      ];
      if (!evidence.isEmpty()) {
        existing.evidenceId = String.valueOf(evidence[0].Id);
      }
      List<HFS_Recommendation__c> recommendations = [
        SELECT Id
        FROM HFS_Recommendation__c
        WHERE Tenant_Key__c = :tenantKey AND Work_Item__c = :workItems[0].Id
        LIMIT 1
      ];
      if (!recommendations.isEmpty()) {
        existing.recommendationId = String.valueOf(recommendations[0].Id);
        List<HFS_Approval__c> approvals = [
          SELECT Id
          FROM HFS_Approval__c
          WHERE
            Tenant_Key__c = :tenantKey
            AND Recommendation__c = :recommendations[0].Id
          LIMIT 1
        ];
        if (!approvals.isEmpty()) {
          existing.approvalId = String.valueOf(approvals[0].Id);
        }
      }
    }
    return existing;
  }

  private static HFS_Entity__c upsertAlias(
    String tenantKey,
    String aliasKey,
    Id sourceEventId,
    Datetime observedAt,
    String fromHash,
    String sourceChannel
  ) {
    List<HFS_Entity__c> aliases = [
      SELECT Id
      FROM HFS_Entity__c
      WHERE Tenant_Key__c = :tenantKey AND External_Key__c = :aliasKey
      LIMIT 1
    ];
    if (!aliases.isEmpty()) {
      return aliases[0];
    }
    HFS_Entity__c aliasRecord = new HFS_Entity__c(
      External_Key__c = aliasKey,
      Tenant_Key__c = tenantKey,
      Entity_Type__c = 'CUSTOMER_ALIAS',
      Display_Name__c = 'WhatsApp customer alias',
      Source_Event__c = sourceEventId,
      Valid_From__c = observedAt,
      Confidence__c = 0.86,
      Attributes_JSON__c = JSON.serialize(
        new Map<String, Object>{
          'primitive' => 'Customer',
          'sourceChannel' => sourceChannel,
          'fromHash' => fromHash,
          'rawPhoneStored' => false
        }
      )
    );
    insert aliasRecord;
    return aliasRecord;
  }

  private static HFS_CommandResult storeRecommendation(
    String tenantKey,
    String purpose,
    String correlationId,
    String sourceRecordId,
    Id workItemId,
    Id customerAliasId,
    Id evidenceId,
    List<String> categories,
    List<String> hypotheses,
    List<String> missingEvidence,
    Boolean clinicalRequest
  ) {
    HFS_RecommendationCommand command = new HFS_RecommendationCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = correlationId;
    command.tenantKey = tenantKey;
    command.purpose = purpose;
    command.externalKey =
      'recommendation-whatsapp-' + shortHash(sourceRecordId);
    command.workItemId = String.valueOf(workItemId);
    command.subjectEntityId = String.valueOf(customerAliasId);
    command.primaryEvidenceId = String.valueOf(evidenceId);
    command.recommendationType = clinicalRequest
      ? 'LOGIA_CLINICAL_BOUNDARY_ROUTE'
      : 'LOGIA_HOSPITAL_ACTION_PLAN';
    command.proposedActionType = clinicalRequest
      ? 'ROUTE_TO_CLINICIAN_REVIEW'
      : 'APPROVE_HOSPITAL_ACTIONS';
    command.rationale = recommendationRationale(
      categories,
      hypotheses,
      missingEvidence,
      clinicalRequest
    );
    command.confidence = clinicalRequest ? 0.92 : 0.84;
    command.modelProfile = 'logia-hospital-operations';
    command.modelInvocationId =
      'twilio-live-intake-' + shortHash(sourceRecordId);
    return new HFS_RelationshipServiceImpl().storeRecommendation(command);
  }

  private static HFS_CommandResult requestApproval(
    String tenantKey,
    String purpose,
    String correlationId,
    String sourceRecordId,
    String recommendationId,
    Boolean clinicalRequest
  ) {
    HFS_ApprovalRequestCommand command = new HFS_ApprovalRequestCommand();
    command.contractVersion = HFS_ServiceContract.VERSION;
    command.correlationId = correlationId;
    command.tenantKey = tenantKey;
    command.purpose = purpose;
    command.externalKey = 'approval-whatsapp-' + shortHash(sourceRecordId);
    command.recommendationId = recommendationId;
    command.policyKey = clinicalRequest
      ? 'logia-clinician-route-v1'
      : 'logia-hospital-manager-approval-v1';
    return new HFS_RelationshipServiceImpl().requestApproval(command);
  }

  private static String recommendationRationale(
    List<String> categories,
    List<String> hypotheses,
    List<String> missingEvidence,
    Boolean clinicalRequest
  ) {
    if (clinicalRequest) {
      return 'Facts: a WhatsApp message asks for a clinical decision or may contain clinical urgency. Inference: Logia must not decide diagnosis, treatment, dosage, triage, or clinical priority. Recommended next step: route to a clinician or duty manager and keep the operations audit trail.';
    }
    return 'Facts: a WhatsApp complaint was received and mapped to safe evidence. Categories: ' +
      String.join(categories, ', ') +
      '. Root-cause hypotheses: ' +
      String.join(hypotheses, '; ') +
      '. Missing evidence: ' +
      String.join(missingEvidence, '; ') +
      '. Recommended next step: manager reviews one action plan across customer trust, capacity, pharmacy or inventory, billing, communication, and outcome tracking before any protected action runs.';
  }

  private static String evidenceSummary(
    String summary,
    List<String> categories,
    Boolean clinicalRequest,
    String languageCode,
    String replyLanguage,
    Map<String, Object> mediaInfo
  ) {
    String mediaNote = mediaNote(mediaInfo);
    if (clinicalRequest) {
      return 'WhatsApp message may need clinical judgement. Logia stored only a safe summary and routed the case to clinician or manager review. Language: ' +
        replyLanguage +
        ' (' +
        languageCode +
        ').' +
        mediaNote;
    }
    return clean(
      'WhatsApp complaint summary: ' +
        summary +
        ' Categories: ' +
        String.join(categories, ', ') +
        '. Language: ' +
        replyLanguage +
        ' (' +
        languageCode +
        ')' +
        mediaNote +
        '. Raw phone and raw message text were not stored.',
      32000
    );
  }

  private static String responseMessage(
    Boolean clinicalRequest,
    String languageCode
  ) {
    if (clinicalRequest) {
      if (languageCode == 'fr') {
        return 'Recu. Logia a envoye cela a un clinicien ou manager.';
      }
      if (languageCode == 'mfe') {
        return 'Resi. Logia inn avoy sa ar enn clinician ouswa manager.';
      }
      return 'Received. Logia routed this to a clinician or manager.';
    }
    if (languageCode == 'fr') {
      return 'Recu. Logia a cree un dossier operations pour revue manager.';
    }
    if (languageCode == 'mfe') {
      return 'Resi. Logia inn kree enn case operasyon pou manager verifye.';
    }
    return 'Received. Logia created an operations case for manager review.';
  }

  private static String workSummary(
    List<String> categories,
    Boolean clinicalRequest
  ) {
    if (clinicalRequest) {
      return 'Route WhatsApp clinical request to clinician or manager';
    }
    return clean(
      'Review WhatsApp complaint across ' + String.join(categories, ', '),
      255
    );
  }

  private static String priority(List<String> categories) {
    if (
      categories.contains('PRIVACY_SAFETY') ||
      categories.contains('PHARMACY_STOCK') ||
      categories.contains('BILLING')
    ) {
      return 'HIGH';
    }
    return 'MEDIUM';
  }

  private static String detectedLanguage(
    Map<String, Object> payload,
    String textValue
  ) {
    String explicitLanguage = firstText(
      payload,
      new List<String>{
        'languageCode',
        'language',
        'detectedLanguage',
        'customerLanguage',
        'EndUserLanguage'
      },
      ''
    );
    String normalizedExplicit = normalizeLanguage(explicitLanguage);
    if (!String.isBlank(normalizedExplicit)) {
      return normalizedExplicit;
    }
    String normalized = String.valueOf(textValue).toLowerCase();
    if (
      containsAny(
        normalized,
        new List<String>{
          'mo ',
          'mo pe',
          'mo finn',
          'pena',
          'enn ',
          'pa pe',
          'kouma',
          'mersi',
          'kapav'
        }
      )
    ) {
      return 'mfe';
    }
    if (
      containsAny(
        normalized,
        new List<String>{
          'bonjour',
          'merci',
          'facture',
          'retard',
          'attente',
          'chambre',
          'probleme',
          'pharmacie'
        }
      )
    ) {
      return 'fr';
    }
    return 'en';
  }

  private static String normalizeLanguage(String value) {
    String normalized = String.valueOf(value).trim().toLowerCase();
    if (String.isBlank(normalized) || normalized == 'null') {
      return null;
    }
    if (normalized.startsWith('fr')) {
      return 'fr';
    }
    if (
      normalized == 'mfe' ||
      normalized.contains('creole') ||
      normalized.contains('kreol') ||
      normalized.contains('mauritian')
    ) {
      return 'mfe';
    }
    if (normalized.startsWith('en')) {
      return 'en';
    }
    return null;
  }

  private static String languageName(String languageCode) {
    if (languageCode == 'fr') {
      return 'French';
    }
    if (languageCode == 'mfe') {
      return 'Mauritian Creole';
    }
    return 'English';
  }

  private static List<String> categories(
    Map<String, Object> payload,
    String textValue
  ) {
    List<String> values = new List<String>();
    Object explicitValue = payload.get('categories');
    if (explicitValue instanceof List<Object>) {
      for (Object item : (List<Object>) explicitValue) {
        add(values, clean(String.valueOf(item), 60).toUpperCase());
      }
    }
    if (intValue(payload, 'mediaCount') > 0) {
      add(values, 'VOICE_OR_MEDIA');
    }
    String normalized = String.valueOf(textValue).toLowerCase();
    if (containsAny(normalized, new List<String>{ 'wait', 'queue', 'delay' })) {
      add(values, 'WAIT_TIME');
    }
    if (containsAny(normalized, new List<String>{ 'room', 'clean', 'bed' })) {
      add(values, 'ROOM_READINESS');
    }
    if (
      containsAny(
        normalized,
        new List<String>{ 'bill', 'invoice', 'refund', 'insurance', 'payment' }
      )
    ) {
      add(values, 'BILLING');
    }
    if (
      containsAny(
        normalized,
        new List<String>{ 'pharmacy', 'medicine late', 'stock', 'supply' }
      )
    ) {
      add(values, 'PHARMACY_STOCK');
    }
    if (containsAny(normalized, new List<String>{ 'lab', 'test result' })) {
      add(values, 'LAB_VENDOR');
    }
    if (containsAny(normalized, new List<String>{ 'food', 'meal' })) {
      add(values, 'FOOD_SERVICE');
    }
    if (containsAny(normalized, new List<String>{ 'rude', 'staff' })) {
      add(values, 'STAFF_INTERACTION');
    }
    if (containsAny(normalized, new List<String>{ 'privacy', 'unsafe' })) {
      add(values, 'PRIVACY_SAFETY');
    }
    if (
      containsAny(
        normalized,
        new List<String>{
          'diagnose',
          'dosage',
          'treatment',
          'triage',
          'chest pain',
          'emergency'
        }
      )
    ) {
      add(values, 'CLINICAL_REQUEST');
    }
    if (values.isEmpty()) {
      add(values, 'GENERAL_SERVICE');
    }
    return values;
  }

  private static List<String> affectedPrimitives(List<String> categories) {
    List<String> primitives = new List<String>{
      'Signal',
      'Evidence',
      'Customer',
      'Process',
      'Recommendation',
      'Approval'
    };
    if (
      categories.contains('WAIT_TIME') ||
      categories.contains('ROOM_READINESS') ||
      categories.contains('PHARMACY_STOCK') ||
      categories.contains('VOICE_OR_MEDIA')
    ) {
      add(primitives, 'Resource');
      add(primitives, 'Metric');
    }
    if (categories.contains('LAB_VENDOR')) {
      add(primitives, 'Partner');
      add(primitives, 'Risk');
    }
    if (categories.contains('BILLING')) {
      add(primitives, 'Risk');
      add(primitives, 'Outcome');
    }
    add(primitives, 'Action');
    return primitives;
  }

  private static List<String> followUpQuestions(List<String> categories) {
    List<String> questions = new List<String>();
    if (categories.contains('WAIT_TIME')) {
      questions.add('Which department or counter is affected?');
    }
    if (categories.contains('ROOM_READINESS')) {
      questions.add('Which room or ward needs checking?');
    }
    if (categories.contains('BILLING')) {
      questions.add('Is this about invoice, payment, refund, or insurance?');
    }
    if (categories.contains('PHARMACY_STOCK')) {
      questions.add('Which item or prescription pickup is delayed?');
    }
    if (categories.contains('VOICE_OR_MEDIA')) {
      questions.add(
        'Can you send one short text summary if the voice note or document is unclear?'
      );
    }
    if (questions.isEmpty()) {
      questions.add('Which service area should the manager review first?');
    }
    return questions;
  }

  private static List<String> hypotheses(
    List<String> categories,
    Boolean clinicalRequest
  ) {
    if (clinicalRequest) {
      return new List<String>{
        'The message needs human clinical judgement, not automated action.'
      };
    }
    List<String> values = new List<String>();
    if (categories.contains('WAIT_TIME')) {
      values.add(
        'Queue pressure or staff coverage may be driving the complaint.'
      );
    }
    if (categories.contains('ROOM_READINESS')) {
      values.add(
        'Room cleaning, porter handoff, or bed release may be blocked.'
      );
    }
    if (categories.contains('BILLING')) {
      values.add(
        'Billing review, insurer response, or payment status may be delayed.'
      );
    }
    if (categories.contains('PHARMACY_STOCK')) {
      values.add(
        'Pharmacy stock cover or pickup workflow may need manager review.'
      );
    }
    if (categories.contains('LAB_VENDOR')) {
      values.add('A lab partner response may be affecting the service update.');
    }
    if (categories.contains('VOICE_OR_MEDIA')) {
      values.add(
        'The media needs transcript or document extraction before protected action.'
      );
    }
    if (values.isEmpty()) {
      values.add(
        'The complaint needs evidence from the affected service area.'
      );
    }
    return values;
  }

  private static List<String> missingEvidence(List<String> categories) {
    List<String> values = new List<String>{ 'latest complaint timestamp' };
    if (categories.contains('WAIT_TIME')) {
      values.add('current queue wait and staffing count');
    }
    if (categories.contains('ROOM_READINESS')) {
      values.add('room status and cleaning task acknowledgement');
    }
    if (categories.contains('BILLING')) {
      values.add('billing or insurance case status');
    }
    if (categories.contains('PHARMACY_STOCK')) {
      values.add('pharmacy stock cover and pickup backlog');
    }
    if (categories.contains('LAB_VENDOR')) {
      values.add('partner SLA acknowledgement');
    }
    if (categories.contains('VOICE_OR_MEDIA')) {
      values.add('media transcript or document extraction confidence');
    }
    return values;
  }

  private static String summarize(String rawBody) {
    String normalized = String.valueOf(rawBody).toLowerCase();
    List<String> parts = new List<String>();
    if (containsAny(normalized, new List<String>{ 'wait', 'queue', 'delay' })) {
      parts.add('waiting time');
    }
    if (containsAny(normalized, new List<String>{ 'room', 'clean', 'bed' })) {
      parts.add('room readiness');
    }
    if (
      containsAny(
        normalized,
        new List<String>{ 'bill', 'invoice', 'refund', 'insurance', 'payment' }
      )
    ) {
      parts.add('billing or payment');
    }
    if (containsAny(normalized, new List<String>{ 'pharmacy', 'stock' })) {
      parts.add('pharmacy or supply');
    }
    if (parts.isEmpty()) {
      return 'A WhatsApp complaint needs service review.';
    }
    return 'A WhatsApp complaint mentions ' + String.join(parts, ', ') + '.';
  }

  private static String commandCenterHint(String workItemId) {
    return 'Open Logia Command Center with tenantKey=demo-mauritius, purpose=RESOLVE_HOSPITAL_OPERATION_RISK, workItemId=' +
      String.valueOf(workItemId) +
      ', mockMode=false.';
  }

  private static String sourceChannel(Map<String, Object> payload) {
    String value = firstText(
      payload,
      new List<String>{ 'sourceChannel', 'channelProvider', 'provider' },
      DEFAULT_SOURCE_CHANNEL
    );
    if (String.isBlank(value)) {
      return DEFAULT_SOURCE_CHANNEL;
    }
    return clean(value, 120);
  }

  private static String sourceUri(String sourceChannel) {
    String normalized = String.valueOf(sourceChannel).toLowerCase();
    if (normalized.contains('meta')) {
      return 'urn:logia:meta:whatsapp:cloud-api';
    }
    if (normalized.contains('twilio')) {
      return 'urn:logia:twilio:whatsapp:sandbox';
    }
    return 'urn:logia:whatsapp:intake';
  }

  private static String text(
    Map<String, Object> payload,
    String key,
    String fallback
  ) {
    String value = String.valueOf(payload.get(key));
    return String.isBlank(value) || value == 'null'
      ? fallback
      : clean(value, 500);
  }

  private static String firstText(
    Map<String, Object> payload,
    List<String> keys,
    String fallback
  ) {
    for (String key : keys) {
      if (payload.containsKey(key)) {
        String value = String.valueOf(payload.get(key));
        if (!String.isBlank(value) && value != 'null') {
          return clean(value, 5000);
        }
      }
    }
    return fallback;
  }

  private static Boolean boolValue(Map<String, Object> payload, String key) {
    Object value = payload.get(key);
    if (value == null) {
      return false;
    }
    if (value instanceof Boolean) {
      return (Boolean) value;
    }
    return String.valueOf(value).toLowerCase() == 'true';
  }

  private static Integer intValue(Map<String, Object> payload, String key) {
    Object value = payload.get(key);
    if (value == null) {
      return 0;
    }
    try {
      return Integer.valueOf(String.valueOf(value));
    } catch (Exception ignored) {
      return 0;
    }
  }

  private static Map<String, Object> mediaInfo(Map<String, Object> payload) {
    Integer mediaCount = intValue(payload, 'mediaCount');
    String mediaType = firstText(
      payload,
      new List<String>{ 'firstMediaType', 'MediaContentType0' },
      ''
    );
    String mediaKind = firstText(
      payload,
      new List<String>{ 'firstMediaKind', 'mediaKind' },
      ''
    );
    String mediaUrl = firstText(
      payload,
      new List<String>{ 'mediaUrl0', 'MediaUrl0' },
      ''
    );
    if (String.isBlank(mediaKind) && !String.isBlank(mediaType)) {
      String normalizedType = mediaType.toLowerCase();
      if (normalizedType.startsWith('audio/')) {
        mediaKind = 'voice note';
      } else if (normalizedType.startsWith('image/')) {
        mediaKind = 'image';
      } else if (normalizedType == 'application/pdf') {
        mediaKind = 'document';
      } else {
        mediaKind = 'media file';
      }
    }
    return new Map<String, Object>{
      'hasMedia' => mediaCount > 0,
      'mediaCount' => mediaCount,
      'firstMediaType' => clean(mediaType, 80),
      'firstMediaKind' => clean(mediaKind, 80),
      'mediaUrlHash' => hashText(mediaUrl),
      'rawMediaUrlStored' => false,
      'transcriptStatus' => mediaCount > 0 ? 'PENDING_OR_MANUAL' : 'NONE'
    };
  }

  private static String mediaNote(Map<String, Object> mediaInfo) {
    if (mediaInfo == null || mediaInfo.get('hasMedia') != true) {
      return '';
    }
    return ' Media: ' +
      String.valueOf(mediaInfo.get('firstMediaKind')) +
      ' received; transcript or extraction is required before protected action.';
  }

  private static Boolean containsAny(String haystack, List<String> needles) {
    for (String needle : needles) {
      if (haystack.contains(needle)) {
        return true;
      }
    }
    return false;
  }

  private static void add(List<String> values, String value) {
    if (!values.contains(value)) {
      values.add(value);
    }
  }

  private static String clean(String value, Integer maxLength) {
    String normalized = String.valueOf(value).replaceAll('[\\r\\n\\t]+', ' ');
    normalized = normalized.trim();
    return normalized.length() > maxLength
      ? normalized.substring(0, maxLength)
      : normalized;
  }

  private static String hashText(String value) {
    Blob digest = Crypto.generateDigest(
      'SHA-256',
      Blob.valueOf(String.valueOf(value))
    );
    return 'sha256:' + EncodingUtil.convertToHex(digest).toLowerCase();
  }

  private static String shortHash(String value) {
    String hashValue = hashText(String.valueOf(value));
    return hashValue.substring(7, 19);
  }

  private static String pseudoUuid(String seed) {
    String hashValue = hashText(seed).substring(7, 39);
    return hashValue.substring(0, 8) +
      '-' +
      hashValue.substring(8, 12) +
      '-' +
      hashValue.substring(12, 16) +
      '-' +
      hashValue.substring(16, 20) +
      '-' +
      hashValue.substring(20, 32);
  }

  private class ExistingIntake {
    String eventId;
    String workItemId;
    String evidenceId;
    String recommendationId;
    String approvalId;
  }
}
