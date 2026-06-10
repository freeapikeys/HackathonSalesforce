import { UI_STATE_VERSION } from "./fixtures";

const DENIED_CODES = new Set([
  "PERMISSION_DENIED",
  "CUSTOM_PERMISSION_REQUIRED",
  "SOURCE_EVIDENCE_INACCESSIBLE",
  "TENANT_MISMATCH"
]);
const CHANNEL_ACTION_TYPES = new Set([
  "SEND_SLACK_ALERT",
  "SEND_WHATSAPP_ALERT"
]);

function first(values) {
  return Array.isArray(values) && values.length ? values[0] : null;
}

function humanize(value, fallback = "Not available") {
  if (!value) {
    return fallback;
  }
  const words = value
    .replace(/^HFS_/, "")
    .replace(/__c$/, "")
    .replaceAll("_", " ");
  const normalized =
    words === words.toUpperCase() ? words.toLowerCase() : words;
  return normalized.replace(/\b\w/g, (character) => character.toUpperCase());
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
    message:
      error.message || "The operations command service returned an error.",
    errorCode: error.code,
    correlationId,
    retryable: Boolean(error.retryable)
  };
}

function entityLabel(entityById, entityId, fallback) {
  return entityById.get(entityId)?.label || fallback;
}

function timelineItem(item, index) {
  return {
    id: item.recordId || `timeline-${index}`,
    occurredAt: item.occurredAt,
    type: humanize(item.objectApiName, "Context"),
    title: item.label || humanize(item.recordType),
    detail: item.summary || item.status || "No additional detail recorded.",
    source: item.sourceUri || "Salesforce operations context"
  };
}

function isChannelAction(action) {
  return CHANNEL_ACTION_TYPES.has(action.recordType);
}

function taskAction(action, index, entityById) {
  return {
    id: action.recordId || `task-action-${index}`,
    label: humanize(action.recordType, "Operations task"),
    owner: entityLabel(entityById, action.subjectEntityId, "Target role"),
    status: humanize(action.status)
  };
}

function channelAction(action, index) {
  const channel =
    action.recordType === "SEND_WHATSAPP_ALERT" ? "WhatsApp-style" : "Slack";
  return {
    id: action.recordId || `channel-action-${index}`,
    channel,
    detail:
      action.externalReference ||
      action.correlationId ||
      "Approved channel action record",
    status: humanize(action.status)
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
        "No accessible operations work item matched this command center request."
    };
  }

  const entities = context.entities || [];
  const entityById = new Map(
    entities.map((entity) => [entity.recordId, entity])
  );
  const relationship = first(context.relationships) || {};
  const sop = first(context.sopExecutions) || {};
  const recommendation = first(context.recommendations) || {};
  const approval = first(context.approvals) || {};
  const outcome = first(context.outcomes) || {};
  const evaluation = first(context.evaluations) || {};
  const workItem = context.workItem;
  const actions = context.actions || [];
  const taskActions = actions.filter((action) => !isChannelAction(action));
  const channelActions = actions.filter(isChannelAction);
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
      canExecute: Boolean(rawPermissions.canExecute)
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
          "Accessible organization"
        ),
        product: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Accessible resource"
        ),
        category: "Operations",
        batch: "Not recorded",
        supplier: entityLabel(
          entityById,
          relationship.objectEntityId,
          "Accessible partner"
        ),
        promotion: "Not recorded",
        shelfArea: "Not recorded"
      },
      stock: [],
      riskPulses: [
        { id: "risk-complaint", label: "Complaint", status: "Review" },
        { id: "risk-capacity", label: "Capacity", status: "Review" },
        { id: "risk-queue", label: "Queue", status: "Review" },
        { id: "risk-stock", label: "Stock", status: "Review" },
        { id: "risk-partner", label: "Partner", status: "Review" },
        { id: "risk-billing", label: "Billing", status: "Review" },
        { id: "risk-approval", label: "Approval", status: "Review" },
        { id: "risk-staff", label: "Staff readiness", status: "Review" },
        { id: "risk-outcome", label: "Outcome", status: "Review" }
      ],
      complaintCluster: {
        type: "Not recorded",
        count: 0,
        product: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Accessible resource"
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
        cashierRecommendation: taskActions.length
          ? "Approved Salesforce action records map the recovery plan into role-owned operations tasks."
          : "No operations task action records have been logged yet.",
        tasks: taskActions.map((action, index) =>
          taskAction(action, index, entityById)
        )
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
      actions: actions.map((action) => ({
        id: action.recordId,
        type: humanize(action.recordType),
        status: humanize(action.status),
        requestedAt: action.requestedAt || action.occurredAt,
        completedAt: action.occurredAt,
        sourceSystem:
          action.externalReference || "Salesforce and MuleSoft action service",
        correlationId: action.correlationId || context.correlationId
      })),
      channelLog: channelActions.map(channelAction),
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
