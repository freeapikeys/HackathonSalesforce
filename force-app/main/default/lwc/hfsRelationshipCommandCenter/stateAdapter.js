import { UI_STATE_VERSION } from "./fixtures";

const DENIED_CODES = new Set([
  "PERMISSION_DENIED",
  "CUSTOM_PERMISSION_REQUIRED",
  "SOURCE_EVIDENCE_INACCESSIBLE",
  "TENANT_MISMATCH"
]);
const CHANNEL_ACTION_TYPES = new Set([
  "SEND_SLACK_ALERT",
  "SEND_WHATSAPP_ALERT",
  "SEND_VENDOR_EMAIL"
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
    title: denied ? "Logia context is not available" : "Logia could not load",
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
    action.recordType === "SEND_WHATSAPP_ALERT"
      ? "WhatsApp-style"
      : action.recordType === "SEND_VENDOR_EMAIL"
        ? "Vendor email"
        : "Slack";
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

function outcomeMetric(outcome, index) {
  const value =
    outcome.metricValue === null || outcome.metricValue === undefined
      ? humanize(outcome.status, "Recorded")
      : String(outcome.metricValue);
  return {
    id: outcome.recordId || `outcome-metric-${index}`,
    label: humanize(outcome.metricKey || outcome.recordType, "Outcome"),
    value
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
    supersessionApprovalId:
      relationship.supersessionApprovalId || "Not superseded",
    supersededByUserId: relationship.supersededByUserId || "Not superseded",
    supersededAt: relationship.supersededAt,
    supersessionReason:
      relationship.supersessionReason || "No supersession recorded.",
    evidenceSummary:
      relationship.supersessionReason ||
      relationship.summary ||
      "Relationship assertion preserved from accessible Salesforce context.",
    correctionState: relationship.supersededAt ? "Superseded" : "Reviewable"
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

function workBlockers(workItem) {
  const blockers = [];
  if (workItem.blockedReason) {
    blockers.push({
      id: `${workItem.recordId}-blocker`,
      label: workItem.blockedReason,
      owner: workItem.ownerRole || workItem.ownerLabel || "Work owner",
      status: "Blocked",
      dueAt: workItem.dueAt
    });
  }
  if (workItem.dependsOnWorkItemId) {
    blockers.push({
      id: `${workItem.recordId}-dependency`,
      label: `Depends on ${workItem.dependsOnWorkItemId}`,
      owner: workItem.handoffTargetRole || workItem.ownerRole || "Work owner",
      status: "Dependency",
      dueAt: workItem.dueAt
    });
  }
  if (
    workItem.handoffState &&
    !["NOT_REQUIRED", "COMPLETED"].includes(workItem.handoffState)
  ) {
    blockers.push({
      id: `${workItem.recordId}-handoff`,
      label: `Handoff ${humanize(workItem.handoffState)}`,
      owner: workItem.handoffTargetRole || "Handoff owner",
      status: humanize(workItem.handoffState),
      dueAt: workItem.dueAt
    });
  }
  if (workItem.escalationRole) {
    blockers.push({
      id: `${workItem.recordId}-escalation`,
      label: "Escalation path",
      owner: workItem.escalationRole,
      status: "Available",
      dueAt: workItem.dueAt
    });
  }
  return blockers;
}

export function mapCommandCenterPayload(payload, purpose) {
  const context = payload?.context;
  if (!context) {
    return serviceState(
      {
        code: "INVALID_RESPONSE",
        message: "The Logia service returned no context.",
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
      title: "No Logia work is assigned",
      message:
        "No accessible operations work item matched this command center request."
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
  const outcomes = context.outcomes || [];
  const outcome = first(outcomes) || {};
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
        role: workItem.ownerRole || "Salesforce record owner",
        since: workItem.occurredAt
      },
      serviceDeadline: workItem.dueAt,
      nextUpdateDue: workItem.dueAt,
      operationsContext: {
        organization: entityLabel(
          entityById,
          relationship.subjectEntityId,
          "Accessible organization"
        ),
        resource: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Accessible resource"
        ),
        category: "Operations",
        operationalFocus: "Not recorded",
        partner: entityLabel(
          entityById,
          relationship.objectEntityId,
          "Accessible partner"
        ),
        recoveryWindow: "Not recorded",
        serviceAreas: "Not recorded"
      },
      relationshipContext: {
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
        batch: workItem.externalKey || "Not recorded",
        supplier: entityLabel(
          entityById,
          relationship.objectEntityId,
          "Accessible partner"
        ),
        promotion: workItem.status ? humanize(workItem.status) : "Not recorded",
        resourceArea: relationship.relationshipType || "Not recorded"
      },
      profile: {
        core: "Logia universal operations",
        activeProfile: "profile:hospital-private-large",
        displayName: "Active business profile",
        boundary:
          "Profile wording may change by sector; primitive and action contracts stay universal."
      },
      profileMappings: [
        {
          id: "mapping-room-readiness-live",
          issue: "Room readiness",
          primitive: "Resource",
          hospital: "Discharge room readiness",
          hotel: "Guest room readiness",
          airport: "Gate readiness",
          banking: "Service case readiness",
          supermarket: "Checkout or shelf readiness",
          cruise: "Cabin readiness"
        },
        {
          id: "mapping-stock-risk-live",
          issue: "Stock risk",
          primitive: "Resource",
          hospital: "Pharmacy stock risk",
          hotel: "Linen or food stock risk",
          airport: "Equipment stock risk",
          banking: "Card, cash, or document stock risk",
          supermarket: "Shelf or cold-chain stock risk",
          cruise: "Galley or cabin-supply stock risk"
        },
        {
          id: "mapping-complaint-live",
          issue: "Customer complaint",
          primitive: "Signal",
          hospital: "Patient or visitor complaint",
          hotel: "Guest complaint",
          airport: "Passenger complaint",
          banking: "Client complaint",
          supermarket: "Shopper complaint",
          cruise: "Guest complaint"
        }
      ],
      resourcePositions: [],
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
        resource: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Accessible resource"
        ),
        operationalFocus: "Not recorded",
        partner: "Not recorded",
        window: "Not recorded"
      },
      inboundComplaintIntake: {
        sourceChannel: "Salesforce or Twilio intake evidence",
        customerAlias: entityLabel(
          entityById,
          workItem.subjectEntityId,
          "Synthetic customer alias"
        ),
        protectedActionState: "No protected action executes before approval",
        summary:
          "Accessible intake evidence is converted into a governed recommendation request with raw personal contact data kept out of the command center.",
        followUpQuestions: [
          "Which service area was affected?",
          "When did the issue happen?",
          "Which operational evidence confirms the root cause?"
        ],
        rootCauseHypotheses: [
          "Complaint pressure may connect to capacity, partner, billing, stock, or staffing evidence.",
          "Logia treats hypotheses as inference until source evidence confirms them."
        ],
        nextEvidenceNeeded: [
          "current queue or room status",
          "stock or partner status",
          "approval requirement"
        ]
      },
      partnerResponse: {
        status: "Not recorded",
        leadTime: "Not recorded",
        replacement: "Not recorded",
        creditNote: "Not recorded",
        qualityIssue: "Not recorded",
        responseDelay: "Not recorded",
        recoveryOption: "Not recorded",
        financialImpact: "Not recorded",
        boundary: "Not recorded"
      },
      operationsExecution: {
        primaryRecommendation: taskActions.length
          ? "Approved Salesforce action records map the action plan into role-owned operations tasks."
          : "No operations task action records have been logged yet.",
        tasks: taskActions.map((action, index) =>
          taskAction(action, index, entityById)
        )
      },
      agentHandoffTrace: [
        {
          id: "handoff-orchestrator-live",
          agent: "Logia Orchestrator",
          contribution:
            "Combines accessible evidence into one manager-ready action plan.",
          output: "Recommendation and approval path"
        },
        {
          id: "handoff-evidence-live",
          agent: "Evidence and Context",
          contribution:
            "Maps source records into global primitives and flags missing facts.",
          output: "Signal and evidence coverage"
        },
        {
          id: "handoff-customer-trust-live",
          agent: "Customer Trust",
          contribution:
            "Classifies complaint evidence and drafts safe follow-up needs. The active profile controls whether this displays as patient, guest, passenger, or client trust.",
          output: "Complaint impact"
        },
        {
          id: "handoff-resource-live",
          agent: "Resource and Capacity",
          contribution:
            "Checks resource, queue, stock, staff, and room availability.",
          output: "Capacity and inventory risk"
        },
        {
          id: "handoff-operations-live",
          agent: "Operations Execution",
          contribution:
            "Turns approved recommendations into role-owned task records.",
          output: "Task actions"
        },
        {
          id: "handoff-partner-live",
          agent: "Partner and Vendor",
          contribution:
            "Tracks vendor, supplier, insurer, and partner follow-up.",
          output: "Vendor actions"
        },
        {
          id: "handoff-risk-live",
          agent: "Risk and Approval",
          contribution:
            "Requires human approval and blocks clinical or unsupported actions.",
          output: "Approval boundary"
        },
        {
          id: "handoff-finance-live",
          agent: "Financial Impact",
          contribution:
            "Connects billing, refund, claim, and payment evidence to the plan.",
          output: "Financial exposure"
        },
        {
          id: "handoff-comms-live",
          agent: "Communication",
          contribution:
            "Prepares approved Slack, WhatsApp, and vendor-email communication.",
          output: "Channel actions"
        },
        {
          id: "handoff-outcome-live",
          agent: "Outcome Learning",
          contribution:
            "Compares expected outcomes with completed actions and metrics.",
          output: "Outcome evidence"
        }
      ],
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
      blockers: workBlockers(workItem),
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
        requiredEvidence:
          sop.requiredEvidence ||
          "Evidence requirements are defined by the active SOP.",
        escalationRule: sop.escalationRule
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
        requestedBy: "Governed Logia workflow",
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
      outcomeMetrics: outcomes.map(outcomeMetric),
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
    "The Logia service could not be reached.";
  return serviceState(
    {
      code: "RETRYABLE_DEPENDENCY_FAILURE",
      message,
      retryable: true
    },
    correlationId
  );
}
