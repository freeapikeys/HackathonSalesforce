public with sharing class HFS_AgentActionService {
  public static final String EXPLAIN = 'EXPLAIN_RELATIONSHIP_CASE';
  public static final String RECOMMEND = 'DRAFT_RELATIONSHIP_RECOMMENDATION';
  public static final String APPROVE = 'REQUEST_HUMAN_APPROVAL';

  private static final String AGENT_KEY = 'relationship-management-agent';
  private static final String INACCESSIBLE_EVIDENCE = 'INACCESSIBLE_EVIDENCE';
  private static final String UNAUTHORIZED_ACTION = 'UNAUTHORIZED_ACTION';
  private static final String NO_QUALIFIED_MODEL = 'NO_QUALIFIED_MODEL';

  @TestVisible
  private static HFS_RelationshipService serviceOverride;

  public static List<HFS_AgentActionResult> explain(
    List<HFS_AgentActionRequest> requests
  ) {
    List<HFS_AgentActionResult> results = new List<HFS_AgentActionResult>();
    if (requests == null || requests.isEmpty()) {
      results.add(
        errorResult(
          null,
          EXPLAIN,
          HFS_ServiceContract.INVALID_REQUEST,
          'At least one action request is required.',
          false
        )
      );
      return results;
    }
    for (HFS_AgentActionRequest request : requests) {
      results.add(explainOne(request));
    }
    return results;
  }

  public static List<HFS_AgentActionResult> recommend(
    List<HFS_AgentActionRequest> requests
  ) {
    List<HFS_AgentActionResult> results = new List<HFS_AgentActionResult>();
    if (requests == null || requests.isEmpty()) {
      results.add(
        errorResult(
          null,
          RECOMMEND,
          HFS_ServiceContract.INVALID_REQUEST,
          'At least one action request is required.',
          false
        )
      );
      return results;
    }
    for (HFS_AgentActionRequest request : requests) {
      results.add(recommendOne(request));
    }
    return results;
  }

  public static List<HFS_AgentActionResult> requestApproval(
    List<HFS_AgentActionRequest> requests
  ) {
    List<HFS_AgentActionResult> results = new List<HFS_AgentActionResult>();
    if (requests == null || requests.isEmpty()) {
      results.add(
        errorResult(
          null,
          APPROVE,
          HFS_ServiceContract.INVALID_REQUEST,
          'At least one action request is required.',
          false
        )
      );
      return results;
    }
    for (HFS_AgentActionRequest request : requests) {
      results.add(approvalOne(request));
    }
    return results;
  }

  private static HFS_AgentActionResult explainOne(
    HFS_AgentActionRequest request
  ) {
    try {
      validateRequest(request, EXPLAIN);
      HFS_ContextResponse context = service()
        .getContext(contextRequest(request));
      HFS_AgentActionResult contextFailure = contextFailure(
        request,
        EXPLAIN,
        context
      );
      if (contextFailure != null) {
        return contextFailure;
      }

      Grounding grounding = grounding(context);
      if (grounding.citations.isEmpty()) {
        return refusalResult(
          request,
          EXPLAIN,
          INACCESSIBLE_EVIDENCE,
          'No accessible source evidence is available for this work item.',
          false,
          false
        );
      }

      Map<String, Object> response = baseResponse(request, EXPLAIN);
      response.put('facts', grounding.facts);
      response.put('citations', grounding.citations);

      HFS_ContextItem recommendation = firstQualifiedRecommendation(
        context.recommendations,
        null
      );
      List<Object> inferences = recommendationInference(
        recommendation,
        grounding
      );
      response.put('inferences', inferences);
      response.put('status', 'SUCCESS');
      return result(
        response,
        'Returned ' +
          String.valueOf(grounding.facts.size()) +
          ' grounded fact(s) and ' +
          String.valueOf(inferences.size()) +
          ' inference(s).'
      );
    } catch (Exception exceptionValue) {
      return exceptionResult(request, EXPLAIN, exceptionValue);
    }
  }

  private static HFS_AgentActionResult recommendOne(
    HFS_AgentActionRequest request
  ) {
    try {
      validateRequest(request, RECOMMEND);
      HFS_ContextResponse context = service()
        .getContext(contextRequest(request));
      HFS_AgentActionResult contextFailure = contextFailure(
        request,
        RECOMMEND,
        context
      );
      if (contextFailure != null) {
        return contextFailure;
      }

      HFS_ContextItem recommendation = firstQualifiedRecommendation(
        context.recommendations,
        request.modelProfile
      );
      if (recommendation == null) {
        return refusalResult(
          request,
          RECOMMEND,
          NO_QUALIFIED_MODEL,
          'No qualified model result is available for this request.',
          true,
          false
        );
      }

      Grounding grounding = grounding(context);
      String basisFactId = grounding.factByEvidenceId.get(
        recommendation.primaryEvidenceId
      );
      if (
        grounding.citations.isEmpty() ||
        String.isBlank(basisFactId) ||
        String.isBlank(recommendation.modelProfile) ||
        String.isBlank(recommendation.modelInvocationId)
      ) {
        return refusalResult(
          request,
          RECOMMEND,
          INACCESSIBLE_EVIDENCE,
          'The qualified recommendation cannot be returned without accessible source evidence and model provenance.',
          false,
          false
        );
      }

      Map<String, Object> response = baseResponse(request, RECOMMEND);
      response.put('facts', grounding.facts);
      response.put('citations', grounding.citations);
      response.put(
        'inferences',
        new List<Object>{
          inference(
            'inference-recommendation-rationale',
            recommendation.summary,
            new List<String>{ basisFactId },
            recommendation.confidence
          )
        }
      );
      response.put(
        'recommendation',
        new Map<String, Object>{
          'recommendationType' => recommendation.recordType,
          'proposedActionType' => recommendation.proposedActionType,
          'rationale' => recommendation.summary,
          'confidence' => recommendation.confidence,
          'evidenceIds' => new List<String>{ recommendation.primaryEvidenceId },
          'modelProfile' => recommendation.modelProfile,
          'modelInvocationId' => recommendation.modelInvocationId,
          'requiresHumanApproval' => true
        }
      );
      Map<String, Object> audit = audit(request, true);
      audit.put('modelInvocationId', recommendation.modelInvocationId);
      response.put('audit', audit);
      response.put('status', 'SUCCESS');
      return result(
        response,
        'Returned a grounded recommendation that still requires human approval.'
      );
    } catch (Exception exceptionValue) {
      return exceptionResult(request, RECOMMEND, exceptionValue);
    }
  }

  private static HFS_AgentActionResult approvalOne(
    HFS_AgentActionRequest request
  ) {
    try {
      validateRequest(request, APPROVE);
      HFS_ServiceSupport.requireText(
        request.recommendationId,
        'recommendationId'
      );
      HFS_ServiceSupport.requireText(
        request.approvalPolicyKey,
        'approvalPolicyKey'
      );

      HFS_ApprovalRequestCommand command = new HFS_ApprovalRequestCommand();
      command.contractVersion = request.contractVersion;
      command.correlationId = request.correlationId;
      command.tenantKey = request.tenantKey;
      command.purpose = request.purpose;
      command.externalKey = approvalExternalKey(request);
      command.recommendationId = request.recommendationId;
      command.policyKey = request.approvalPolicyKey;
      HFS_CommandResult commandResult = service().requestApproval(command);

      if (!commandResult.success) {
        HFS_ServiceError errorValue = firstError(commandResult.errors);
        if (
          errorValue.code == HFS_ServiceContract.PERMISSION_DENIED ||
          errorValue.code == HFS_ServiceContract.CUSTOM_PERMISSION_REQUIRED
        ) {
          return refusalResult(
            request,
            APPROVE,
            UNAUTHORIZED_ACTION,
            'The current user cannot request this approval.',
            false,
            true
          );
        }
        if (
          errorValue.code == HFS_ServiceContract.RECORD_NOT_FOUND ||
          errorValue.code == HFS_ServiceContract.SOURCE_EVIDENCE_INACCESSIBLE
        ) {
          return refusalResult(
            request,
            APPROVE,
            INACCESSIBLE_EVIDENCE,
            'The recommendation or its evidence is unavailable to the current user.',
            false,
            true
          );
        }
        return errorResult(
          request,
          APPROVE,
          normalizeErrorCode(errorValue.code),
          errorValue.message,
          errorValue.retryable
        );
      }
      if (commandResult.status != 'PENDING') {
        return errorResult(
          request,
          APPROVE,
          HFS_ServiceContract.VALIDATION_FAILED,
          'The approval request is no longer pending for a human decision.',
          false
        );
      }

      Map<String, Object> response = baseResponse(request, APPROVE);
      response.put(
        'approval',
        new Map<String, Object>{
          'approvalId' => commandResult.recordId,
          'recommendationId' => request.recommendationId,
          'policyKey' => request.approvalPolicyKey,
          'status' => 'PENDING',
          'externalActionExecuted' => false
        }
      );
      response.put('audit', audit(request, true));
      response.put('status', 'SUCCESS');
      return result(
        response,
        commandResult.replayed
          ? 'Returned the existing pending human approval request.'
          : 'Created a pending human approval request.'
      );
    } catch (Exception exceptionValue) {
      return exceptionResult(request, APPROVE, exceptionValue);
    }
  }

  private static void validateRequest(
    HFS_AgentActionRequest request,
    String expectedAction
  ) {
    HFS_ServiceSupport.validateRequest(
      request == null ? null : request.contractVersion,
      request == null ? null : request.tenantKey,
      request == null ? null : request.purpose,
      request == null ? null : request.correlationId
    );
    HFS_ServiceSupport.requireText(request.action, 'action');
    HFS_ServiceSupport.requireText(request.workItemId, 'workItemId');
    if (request.action != expectedAction) {
      HFS_ServiceSupport.fail(
        HFS_ServiceContract.INVALID_REQUEST,
        'The request action does not match the invoked Agentforce action.',
        'action'
      );
    }
  }

  private static HFS_ContextRequest contextRequest(
    HFS_AgentActionRequest request
  ) {
    HFS_ContextRequest context = new HFS_ContextRequest();
    context.contractVersion = request.contractVersion;
    context.tenantKey = request.tenantKey;
    context.workItemId = request.workItemId;
    context.purpose = request.purpose;
    context.correlationId = request.correlationId;
    context.includeProvenance = true;
    context.timelineLimit = 100;
    return context;
  }

  private static HFS_AgentActionResult contextFailure(
    HFS_AgentActionRequest request,
    String action,
    HFS_ContextResponse context
  ) {
    if (context == null) {
      return errorResult(
        request,
        action,
        HFS_ServiceContract.UNEXPECTED_ERROR,
        'The relationship context service returned no result.',
        false
      );
    }
    if (context.errors == null || context.errors.isEmpty()) {
      return null;
    }

    HFS_ServiceError errorValue = context.errors[0];
    if (
      errorValue.code == HFS_ServiceContract.PERMISSION_DENIED ||
      errorValue.code == HFS_ServiceContract.RECORD_NOT_FOUND ||
      errorValue.code == HFS_ServiceContract.SOURCE_EVIDENCE_INACCESSIBLE
    ) {
      return refusalResult(
        request,
        action,
        INACCESSIBLE_EVIDENCE,
        'The source evidence is missing or inaccessible for this user and purpose.',
        false,
        false
      );
    }
    return errorResult(
      request,
      action,
      normalizeErrorCode(errorValue.code),
      errorValue.message,
      errorValue.retryable
    );
  }

  private static Grounding grounding(HFS_ContextResponse context) {
    Grounding result = new Grounding();
    Integer sequence = 0;
    for (HFS_EvidenceCitation citationValue : context.evidence) {
      if (
        citationValue == null ||
        String.isBlank(citationValue.evidenceId) ||
        String.isBlank(citationValue.sourceEventId) ||
        String.isBlank(citationValue.sourceUri) ||
        String.isBlank(citationValue.contentHash) ||
        String.isBlank(citationValue.summary) ||
        !Pattern.matches('^sha256:[a-f0-9]{64}$', citationValue.contentHash)
      ) {
        HFS_ServiceSupport.fail(
          HFS_ServiceContract.VALIDATION_FAILED,
          'Accessible evidence is missing required provenance.',
          'evidence'
        );
      }
      sequence++;
      String factId = 'fact-' + String.valueOf(sequence);
      result.factByEvidenceId.put(citationValue.evidenceId, factId);
      result.citations.add(
        new Map<String, Object>{
          'evidenceId' => citationValue.evidenceId,
          'sourceEventId' => citationValue.sourceEventId,
          'sourceUri' => citationValue.sourceUri,
          'contentHash' => citationValue.contentHash,
          'summary' => citationValue.summary,
          'accessible' => true
        }
      );
      result.facts.add(
        new Map<String, Object>{
          'factId' => factId,
          'statement' => citationValue.summary,
          'evidenceIds' => new List<String>{ citationValue.evidenceId }
        }
      );
    }
    return result;
  }

  private static List<Object> recommendationInference(
    HFS_ContextItem recommendation,
    Grounding grounding
  ) {
    List<Object> result = new List<Object>();
    if (
      recommendation == null ||
      String.isBlank(recommendation.summary) ||
      String.isBlank(recommendation.primaryEvidenceId)
    ) {
      return result;
    }
    String basisFactId = grounding.factByEvidenceId.get(
      recommendation.primaryEvidenceId
    );
    if (String.isBlank(basisFactId)) {
      return result;
    }
    result.add(
      inference(
        'inference-existing-recommendation',
        recommendation.summary,
        new List<String>{ basisFactId },
        recommendation.confidence
      )
    );
    return result;
  }

  private static Map<String, Object> inference(
    String inferenceId,
    String statement,
    List<String> basisFactIds,
    Decimal confidence
  ) {
    return new Map<String, Object>{
      'inferenceId' => inferenceId,
      'statement' => statement,
      'basisFactIds' => basisFactIds,
      'confidence' => confidence == null ? 0.5 : confidence
    };
  }

  private static HFS_ContextItem firstQualifiedRecommendation(
    List<HFS_ContextItem> recommendations,
    String requestedProfile
  ) {
    if (recommendations == null) {
      return null;
    }
    for (HFS_ContextItem recommendation : recommendations) {
      if (
        recommendation != null &&
        !String.isBlank(recommendation.modelProfile) &&
        !String.isBlank(recommendation.modelInvocationId) &&
        !String.isBlank(recommendation.proposedActionType) &&
        !String.isBlank(recommendation.summary) &&
        (String.isBlank(requestedProfile) ||
        requestedProfile == recommendation.modelProfile)
      ) {
        return recommendation;
      }
    }
    return null;
  }

  private static String approvalExternalKey(HFS_AgentActionRequest request) {
    String material =
      request.tenantKey +
      '|' +
      request.correlationId +
      '|' +
      request.recommendationId +
      '|' +
      request.approvalPolicyKey;
    return 'agent-approval-' +
      EncodingUtil.convertToHex(
        Crypto.generateDigest('SHA-256', Blob.valueOf(material))
      );
  }

  private static HFS_AgentActionResult exceptionResult(
    HFS_AgentActionRequest request,
    String action,
    Exception exceptionValue
  ) {
    HFS_ServiceError errorValue = HFS_ServiceSupport.error(exceptionValue);
    return errorResult(
      request,
      action,
      normalizeErrorCode(errorValue.code),
      errorValue.message,
      errorValue.retryable
    );
  }

  private static HFS_AgentActionResult refusalResult(
    HFS_AgentActionRequest request,
    String action,
    String code,
    String message,
    Boolean retryable,
    Boolean humanApprovalRequired
  ) {
    Map<String, Object> response = baseResponse(request, action);
    response.put('status', 'REFUSED');
    response.put(
      'refusal',
      new Map<String, Object>{
        'code' => code,
        'message' => message,
        'retryable' => retryable,
        'disclosedRecordIds' => new List<String>()
      }
    );
    response.put('audit', audit(request, humanApprovalRequired));
    return result(response, message);
  }

  private static HFS_AgentActionResult errorResult(
    HFS_AgentActionRequest request,
    String action,
    String code,
    String message,
    Boolean retryable
  ) {
    Map<String, Object> response = baseResponse(request, action);
    response.put('status', 'ERROR');
    response.put(
      'errors',
      new List<Object>{
        new Map<String, Object>{
          'code' => normalizeErrorCode(code),
          'message' => String.isBlank(message)
            ? 'The operation could not be completed.'
            : message,
          'retryable' => retryable == true
        }
      }
    );
    return result(
      response,
      String.isBlank(message)
        ? 'The operation could not be completed.'
        : message
    );
  }

  private static Map<String, Object> baseResponse(
    HFS_AgentActionRequest request,
    String action
  ) {
    return new Map<String, Object>{
      'contractVersion' => request == null
        ? HFS_ServiceContract.VERSION
        : request.contractVersion,
      'action' => action,
      'tenantKey' => request == null ? null : request.tenantKey,
      'correlationId' => request == null ? null : request.correlationId,
      'status' => 'ERROR',
      'facts' => new List<Object>(),
      'inferences' => new List<Object>(),
      'citations' => new List<Object>(),
      'recommendation' => null,
      'approval' => null,
      'refusal' => null,
      'errors' => new List<Object>(),
      'audit' => audit(request, false)
    };
  }

  private static Map<String, Object> audit(
    HFS_AgentActionRequest request,
    Boolean humanApprovalRequired
  ) {
    return new Map<String, Object>{
      'actorUserId' => UserInfo.getUserId(),
      'agentKey' => AGENT_KEY,
      'purpose' => request == null ? 'UNSPECIFIED' : request.purpose,
      'permissionEvaluated' => true,
      'modelInvocationId' => null,
      'humanApprovalRequired' => humanApprovalRequired,
      'externalActionExecuted' => false
    };
  }

  private static HFS_AgentActionResult result(
    Map<String, Object> response,
    String summary
  ) {
    HFS_AgentActionResult result = new HFS_AgentActionResult();
    result.status = (String) response.get('status');
    result.summary = summary;
    result.responseJson = JSON.serialize(response);
    result.citationEvidenceIds = new List<String>();
    for (Object citationValue : (List<Object>) response.get('citations')) {
      Map<String, Object> citation = (Map<String, Object>) citationValue;
      result.citationEvidenceIds.add((String) citation.get('evidenceId'));
    }
    Map<String, Object> recommendation = (Map<String, Object>) response.get(
      'recommendation'
    );
    if (recommendation != null) {
      result.modelInvocationId = (String) recommendation.get(
        'modelInvocationId'
      );
    }
    Map<String, Object> approval = (Map<String, Object>) response.get(
      'approval'
    );
    if (approval != null) {
      result.approvalId = (String) approval.get('approvalId');
    }
    Map<String, Object> refusal = (Map<String, Object>) response.get('refusal');
    if (refusal != null) {
      result.refusalCode = (String) refusal.get('code');
    }
    List<Object> errors = (List<Object>) response.get('errors');
    if (!errors.isEmpty()) {
      result.errorCode = (String) ((Map<String, Object>) errors[0]).get('code');
    }
    result.externalActionExecuted = false;
    return result;
  }

  private static HFS_ServiceError firstError(List<HFS_ServiceError> errors) {
    if (errors != null && !errors.isEmpty()) {
      return errors[0];
    }
    return HFS_ServiceSupport.error(
      HFS_ServiceContract.UNEXPECTED_ERROR,
      'The operation could not be completed.',
      null,
      false,
      null
    );
  }

  private static String normalizeErrorCode(String code) {
    if (
      code == HFS_ServiceContract.INVALID_REQUEST ||
      code == HFS_ServiceContract.UNSUPPORTED_CONTRACT_VERSION ||
      code == HFS_ServiceContract.VALIDATION_FAILED ||
      code == HFS_ServiceContract.RETRYABLE_DEPENDENCY_FAILURE ||
      code == HFS_ServiceContract.UNEXPECTED_ERROR
    ) {
      return code;
    }
    if (
      code == HFS_ServiceContract.TENANT_MISMATCH ||
      code == HFS_ServiceContract.INVALID_STATE ||
      code == HFS_ServiceContract.IDEMPOTENCY_CONFLICT
    ) {
      return HFS_ServiceContract.VALIDATION_FAILED;
    }
    return HFS_ServiceContract.UNEXPECTED_ERROR;
  }

  private static HFS_RelationshipService service() {
    return serviceOverride == null
      ? new HFS_RelationshipServiceImpl()
      : serviceOverride;
  }

  private class Grounding {
    private List<Object> facts = new List<Object>();
    private List<Object> citations = new List<Object>();
    private Map<String, String> factByEvidenceId = new Map<String, String>();
  }
}
