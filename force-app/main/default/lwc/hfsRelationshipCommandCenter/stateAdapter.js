import { UI_STATE_VERSION } from "./fixtures";

const DENIED_CODES = new Set([
  "PERMISSION_DENIED",
  "CUSTOM_PERMISSION_REQUIRED",
  "SOURCE_EVIDENCE_INACCESSIBLE",
  "TENANT_MISMATCH"
]);

function first(values) {
  return Array.isArray(values) && values.length ? values[0] : null;
}

function humanize(value, fallback = "Not available") {
  if (!value) {
    return fallback;
  }
  return value
    .replace(/^HFS_/, "")
    .replace(/__c$/, "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function serviceState(error, correlationId) {
  const denied = DENIED_CODES.has(error.code);
  return {
    stateVersion: UI_STATE_VERSION,
    stateName: denied ? "denied" : "error",
    mode: denied ? "denied" : "error",
    title: denied
      ? "North Star context is not available"
      : "North Star could not load",
    message: error.message || "The retail command service returned an error.",
    errorCode: error.code,
    correlationId,
    retryable: Boolean(error.retryable)
  };
}

function entityLabel(entityById, entityId, fallback) {
  return entityById.get(entityId)?.label || fallback;
}

function confidencePercent(confidence) {
  return confidence === null || confidence === undefined
    ? "Not scored"
    : `${Math.round(Number(confidence) * 100)}%`;
}

function timelineItem(item, index) {
  return {
    id: item.recordId || `timeline-${index}`,
    occurredAt: item.occurredAt,
    type: humanize(item.objectApiName, "Context"),
    title: item.label || humanize(item.recordType),
    detail: item.summary || item.status || "No additional detail recorded.",
    source: item.sourceUri || "Salesforce retail context"
  };
}

function relationshipHistoryItem(entityById, relationship, index) {
  return {
    id: relationship.recordId || `relationship-history-${index}`,
    type: relationship.relationshipType || humanize(relationship.recordType),
    subject: entityLabel(
      entityById,
      relationship.subjectEntityId,
      "Accessible subject"
    ),
    object: entityLabel(
      entityById,
      relationship.objectEntityId,
      "Accessible object"
    ),
    status: humanize(relationship.status, "Current"),
    confidencePercent: confidencePercent(relationship.confidence),
    sourceEventId: relationship.sourceEventId || "Source event not recorded",
    evidenceSummary:
      relationship.summary ||
      "Relationship assertion preserved from accessible Salesforce context.",
    correctionState: "Reviewable"
  };
}

function participantLinkItem(entityById, participant, index) {
  return {
    id: participant.recordId || `participant-link-${index}`,
    role: participant.participantRole || humanize(participant.recordType),
    entity: entityLabel(
      entityById,
      participant.subjectEntityId,
      "Accessible participant"
    ),
    sourceEventId: participant.sourceEventId || "Source event not recorded",
    evidenceSummary:
      participant.summary ||
      "Source event participant link preserved for identity history."
  };
}

function agreementContradictions(agreements, entityById) {
  const byRelationship = new Map();
  for (const agreement of agreements) {
    const key = [
      agreement.relationshipType || agreement.recordType,
      agreement.subjectEntityId,
      agreement.objectEntityId
    ].join("|");
    if (!byRelationship.has(key)) {
      byRelationship.set(key, []);
    }
    byRelationship.get(key).push(agreement);
  }

  const contradictions = [];
  for (const claims of byRelationship.values()) {
    const statuses = new Set(
      claims.map((claim) => claim.status).filter(Boolean)
    );
    if (statuses.size < 2) {
      continue;
    }
    const firstClaim = claims[0];
    contradictions.push({
      id: `contradiction-${firstClaim.recordId}`,
      claim: `${entityLabel(
        entityById,
        firstClaim.subjectEntityId,
        "Accessible party"
      )} and ${entityLabel(
        entityById,
        firstClaim.objectEntityId,
        "accessible party"
      )} have competing ${humanize(firstClaim.recordType)} statuses.`,
      counterclaim: Array.from(statuses).map(humanize).join(" vs "),
      resolution:
        "Keep both claims visible until a human supersedes one with source evidence."
    });
  }
  return contradictions;
}

function correctionActionForRelationship(relationship, index) {
  return {
    id: relationship.recordId || `relationship-correction-${index}`,
    label: "Request correction review",
    target: relationship.relationshipType || humanize(relationship.recordType),
    reason:
      "Open a governed review instead of overwriting relationship history silently.",
    sourceEventId: relationship.sourceEventId,
    sourceRelationshipId: relationship.recordId
  };
}

export function mapCommandCenterPayload(payload, purpose) {
  const context = payload?.context;
  if (!context) {
    return serviceState(
      {
        code: "INVALID_RESPONSE",
        message: "The North Star service returned no context.",
        retryable: true
      },
      null
    );
  }

  const error = first(context.errors);
  if (error) {
    return serviceState(error, context.correlationId);
  }

  if (!context.workItem) {
    return {
      stateVersion: UI_STATE_VERSION,
      stateName: "empty",
      mode: "empty",
      title: "No North Star work is assigned",
      message:
        "No accessible retail work item matched this command center request."
    };
  }

  const entities = context.entities || [];
  const entityById = new Map(
    entities.map((entity) => [entity.recordId, entity])
  );
  const relationship = first(context.relationships) || {};
  const relationships = context.relationships || [];
  const eventParticipants = context.eventParticipants || [];
  const agreements = context.agreements || [];
  const sop = first(context.sopExecutions) || {};
  const recommendation = first(context.recommendations) || {};
  const approval = first(context.approvals) || {};
  const outcome = first(context.outcomes) || {};
  const evaluation = first(context.evaluations) || {};
  const workItem = context.workItem;
  const approvalIsPending = approval.status === "PENDING";
  const rawPermissions = payload.permissions || {};
  const confidence = recommendation.confidence;

  return {
    stateVersion: UI_STATE_VERSION,
    stateName: "ready",
    mode: "ready",
    generatedAt: context.generatedAt,
    correlationId: context.correlationId,
    userRole: payload.userLabel || "Salesforce user",
    purpose,
    permissions: {
      canApprove: Boolean(rawPermissions.canApprove && approvalIsPending),
      canModify: Boolean(rawPermissions.canModify && approvalIsPending),
      canReject: Boolean(rawPermissions.canReject && approvalIsPending),
      canExecute: Boolean(rawPermissions.canExecute),
      canRequestCorrection: Boolean(rawPermissions.canModify)
    },
    case: {
      id: workItem.recordId,
      externalKey: workItem.externalKey,
      title: workItem.label || humanize(workItem.externalKey),
      summary: workItem.summary || "No work summary was recorded.",
      severity: humanize(workItem.recordType),
      status: humanize(workItem.status),
      owner: {
        name: workItem.ownerLabel || "Unassigned",
        role: "Salesforce record owner",
        since: workItem.occurredAt
      },
      serviceDeadline: workItem.dueAt,
      nextUpdateDue: workItem.dueAt,
      productContext: {
        store: entityLabel(
          entityById,
          relationship.subjectEntityId,
          "Accessible store"
        ),
        product: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Accessible product"
        ),
        category: "Retail",
        batch: "Not recorded",
        supplier: entityLabel(
          entityById,
          relationship.objectEntityId,
          "Accessible supplier"
        ),
        promotion: "Not recorded",
        shelfArea: "Not recorded"
      },
      stock: [],
      riskPulses: [
        { id: "risk-stockout", label: "Stockout", status: "Review" },
        { id: "risk-expiry", label: "Expiry", status: "Review" },
        { id: "risk-overstock", label: "Overstock", status: "Review" },
        { id: "risk-complaint", label: "Complaint", status: "Review" },
        { id: "risk-supplier", label: "Supplier", status: "Review" },
        { id: "risk-queue", label: "Queue", status: "Review" },
        { id: "risk-shelf", label: "Shelf layout", status: "Review" },
        { id: "risk-price", label: "Price", status: "Review" },
        { id: "risk-promotion", label: "Promotion", status: "Review" },
        { id: "risk-staff", label: "Staff readiness", status: "Review" }
      ],
      complaintCluster: {
        type: "Not recorded",
        count: 0,
        product: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Accessible product"
        ),
        batch: "Not recorded",
        supplier: "Not recorded",
        window: "Not recorded"
      },
      supplierResponse: {
        status: "Not recorded",
        leadTime: "Not recorded",
        replacement: "Not recorded",
        creditNote: "Not recorded",
        qualityIssue: "Not recorded"
      },
      storeExecution: {
        cashierRecommendation: "No cashier recommendation recorded.",
        tasks: []
      },
      affectedRelationship: {
        label: relationship.label || "Connected relationship",
        subject: entityLabel(
          entityById,
          relationship.subjectEntityId,
          "Accessible subject"
        ),
        object: entityLabel(
          entityById,
          relationship.objectEntityId,
          "Accessible object"
        ),
        type: relationship.relationshipType || "RELATED_TO",
        status: humanize(relationship.status, "Current")
      },
      relationshipHistory: relationships.map((item, index) =>
        relationshipHistoryItem(entityById, item, index)
      ),
      identityLinks: eventParticipants.map((item, index) =>
        participantLinkItem(entityById, item, index)
      ),
      relationshipContradictions: agreementContradictions(
        agreements,
        entityById
      ),
      correctionActions: relationships.map((item, index) =>
        correctionActionForRelationship(item, index)
      ),
      connectedEntities: entities.map((entity) => ({
        id: entity.recordId,
        label: entity.label,
        type: humanize(entity.recordType),
        role:
          entity.recordId === workItem.subjectEntityId
            ? "Primary relationship"
            : "Connected entity"
      })),
      blockers: workItem.blockedReason
        ? [
            {
              id: `${workItem.recordId}-blocker`,
              label: workItem.blockedReason,
              owner: workItem.ownerLabel || "Work owner",
              status: "Blocked",
              dueAt: workItem.dueAt
            }
          ]
        : [],
      timeline: (context.timeline || []).map(timelineItem),
      evidence: (context.evidence || []).map((evidence, index) => ({
        id: evidence.evidenceId,
        label: `Evidence ${index + 1}`,
        summary: evidence.summary,
        sourceUri: evidence.sourceUri,
        capturedAt: evidence.capturedAt,
        contentHash: evidence.contentHash
      })),
      sop: {
        name: humanize(sop.recordType, "No active SOP"),
        version: sop.definitionVersion || "Not recorded",
        status: humanize(sop.status),
        currentStep: humanize(sop.summary, "No current step"),
        completedSteps: sop.status === "COMPLETED" ? 1 : 0,
        totalSteps: 1,
        progress: sop.status === "COMPLETED" ? 100 : 0,
        requiredEvidence: "Evidence requirements are defined by the active SOP."
      },
      recommendation: {
        id: recommendation.recordId,
        status: humanize(recommendation.status, "No recommendation"),
        title: humanize(
          recommendation.proposedActionType || recommendation.recordType,
          "No current recommendation"
        ),
        recommendation:
          recommendation.summary ||
          "No recommendation is currently available for this work item.",
        facts: (context.evidence || [])
          .map((evidence) => evidence.summary)
          .filter(Boolean),
        inferences: recommendation.summary ? [recommendation.summary] : [],
        confidence,
        confidencePercent:
          confidence === null || confidence === undefined
            ? "Not scored"
            : `${Math.round(Number(confidence) * 100)}%`,
        modelProfile: recommendation.modelProfile || "Not recorded",
        modelProfileVersion: context.contractVersion,
        policyVersion:
          recommendation.modelInvocationId || "Invocation not recorded",
        evidenceIds: (context.evidence || []).map(
          (evidence) => evidence.evidenceId
        ),
        requiresHumanApproval: Boolean(approval.recordId)
      },
      approval: {
        id: approval.recordId,
        status: humanize(approval.status, "Not requested"),
        policy: humanize(approval.recordType, "No approval policy"),
        policyVersion: context.contractVersion,
        requestedAt: approval.requestedAt || approval.occurredAt,
        requestedBy: "Governed North Star workflow",
        decisionDueAt: workItem.dueAt
      },
      actions: (context.actions || []).map((action) => ({
        id: action.recordId,
        type: humanize(action.recordType),
        status: humanize(action.status),
        requestedAt: action.requestedAt || action.occurredAt,
        completedAt: action.occurredAt,
        sourceSystem:
          action.externalReference || "Salesforce and MuleSoft action service",
        correlationId: action.correlationId || context.correlationId
      })),
      channelLog: [],
      outcomeMetrics: [],
      outcome: {
        status: humanize(outcome.status, "Awaiting outcome"),
        summary:
          outcome.summary ||
          "No observed outcome has been recorded for the current action.",
        observedAt: outcome.occurredAt,
        effectiveness:
          evaluation.status ||
          (evaluation.confidence === null || evaluation.confidence === undefined
            ? "Not evaluated"
            : `${Math.round(Number(evaluation.confidence) * 100)}%`)
      }
    }
  };
}

export function mapTransportError(error, correlationId) {
  const message =
    error?.body?.message ||
    error?.message ||
    "The North Star service could not be reached.";
  return serviceState(
    {
      code: "RETRYABLE_DEPENDENCY_FAILURE",
      message,
      retryable: true
    },
    correlationId
  );
}
