export const UI_STATE_VERSION = "1.0.0";

const caseState = {
  id: "work-issue-001",
  externalKey: "issue-001",
  title: "Repeated service interruption",
  summary:
    "A contracted service has failed repeatedly and the affected relationship is waiting for a committed update.",
  severity: "High",
  status: "Open",
  owner: {
    name: "Operations Response Team",
    role: "Accountable owner",
    since: "2026-06-05T08:35:00Z"
  },
  serviceDeadline: "2026-06-05T12:30:00Z",
  nextUpdateDue: "2026-06-05T10:30:00Z",
  affectedRelationship: {
    label: "Customer service relationship",
    subject: "Affected person",
    object: "Demo Mauritius organization",
    type: "CUSTOMER_OF",
    status: "Active"
  },
  connectedEntities: [
    {
      id: "entity-person-001",
      label: "Affected person",
      type: "Person",
      role: "Service recipient"
    },
    {
      id: "entity-organization-001",
      label: "Demo Mauritius organization",
      type: "Organization",
      role: "Service owner"
    },
    {
      id: "entity-supplier-001",
      label: "Critical service supplier",
      type: "Supplier",
      role: "Upstream dependency"
    }
  ],
  blockers: [
    {
      id: "blocker-supplier-001",
      label: "Supplier root-cause confirmation",
      owner: "Supplier Operations",
      status: "Waiting",
      dueAt: "2026-06-05T09:45:00Z"
    },
    {
      id: "blocker-approval-001",
      label: "Customer update approval",
      owner: "Duty Manager",
      status: "Ready for decision",
      dueAt: "2026-06-05T10:00:00Z"
    }
  ],
  timeline: [
    {
      id: "timeline-event-001",
      occurredAt: "2026-06-05T08:30:00Z",
      type: "Source event",
      title: "Repeated interruption reported",
      detail: "Operations opened a high-severity issue.",
      source: "Operations system"
    },
    {
      id: "timeline-evidence-001",
      occurredAt: "2026-06-05T08:31:00Z",
      type: "Evidence",
      title: "Contract and service history attached",
      detail: "Agreement, supplier, and recent incident evidence were linked.",
      source: "Relationship service"
    },
    {
      id: "timeline-sop-001",
      occurredAt: "2026-06-05T08:34:00Z",
      type: "SOP",
      title: "Major incident response started",
      detail:
        "Ownership transferred to the response team without losing context.",
      source: "Salesforce Core"
    },
    {
      id: "timeline-recommendation-001",
      occurredAt: "2026-06-05T08:37:00Z",
      type: "Recommendation",
      title: "Proactive status update proposed",
      detail: "A grounded draft was prepared from accessible evidence.",
      source: "recommendation_reasoning 1.0.0"
    },
    {
      id: "timeline-approval-001",
      occurredAt: "2026-06-05T08:38:00Z",
      type: "Approval",
      title: "Human decision requested",
      detail: "No external message has been sent.",
      source: "Approval policy 1.0.0"
    }
  ],
  evidence: [
    {
      id: "evidence-issue-001",
      label: "Source interruption report",
      summary: "The operations source reported repeated interruption at 08:30.",
      sourceUri: "urn:hfs:source:operations",
      capturedAt: "2026-06-05T08:30:03Z",
      contentHash:
        "sha256:56a6f426aa5f34eb9f59d250d587ce835ab7394cc009b70fdb4feada11935c10"
    },
    {
      id: "evidence-agreement-001",
      label: "Service agreement",
      summary:
        "The current agreement requires incident updates within two hours.",
      sourceUri: "urn:hfs:source:contracts",
      capturedAt: "2026-06-05T08:31:10Z",
      contentHash:
        "sha256:7549cf0c63ad4a64f178d8500c1f3874d97478f6ee323e4debbab6d89b168b69"
    }
  ],
  sop: {
    name: "Major incident relationship response",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Approve and send the first relationship update",
    completedSteps: 2,
    totalSteps: 5,
    progress: 40,
    requiredEvidence: "Approved message and source-system delivery result"
  },
  recommendation: {
    id: "recommendation-status-update-001",
    status: "Pending approval",
    title: "Send a proactive service status update",
    recommendation:
      "Use the approved service template to explain the interruption, name the accountable owner, and commit to the next update time.",
    facts: [
      "The source system reports repeated service interruption.",
      "The agreement requires an update within two hours.",
      "No customer update has been recorded for this incident."
    ],
    inferences: [
      "A proactive update is likely to reduce repeated status chasing."
    ],
    confidence: 0.87,
    confidencePercent: "87%",
    modelProfile: "recommendation_reasoning",
    modelProfileVersion: "1.0.0",
    policyVersion: "recommendation-routing-mauritius 1.0.0",
    evidenceIds: ["evidence-issue-001", "evidence-agreement-001"],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-status-update-001",
    status: "Pending",
    policy: "External relationship communication",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-05T08:38:00Z",
    requestedBy: "Relationship Recommendation Agent",
    decisionDueAt: "2026-06-05T10:00:00Z"
  },
  actions: [
    {
      id: "action-investigate-001",
      type: "Supplier escalation",
      status: "In progress",
      requestedAt: "2026-06-05T08:36:00Z",
      completedAt: null,
      sourceSystem: "Supplier operations",
      correlationId: "10000000-0000-4000-8000-000000000001"
    }
  ],
  outcome: {
    status: "Awaiting approved action",
    summary:
      "No communication outcome exists because the proposed message is not approved.",
    observedAt: null,
    effectiveness: "Not evaluated"
  }
};

const readyState = {
  stateVersion: UI_STATE_VERSION,
  stateName: "ready",
  mode: "ready",
  generatedAt: "2026-06-05T08:39:00Z",
  correlationId: "10000000-0000-4000-8000-000000000001",
  userRole: "Duty Manager",
  purpose: "RESOLVE_SERVICE_INTERRUPTION",
  permissions: {
    canApprove: true,
    canModify: true,
    canReject: true,
    canExecute: false
  },
  case: caseState
};

export const UI_STATES = {
  ready: readyState,
  restricted: {
    ...readyState,
    stateName: "restricted",
    userRole: "Relationship Viewer",
    permissions: {
      canApprove: false,
      canModify: false,
      canReject: false,
      canExecute: false
    }
  },
  loading: {
    stateVersion: UI_STATE_VERSION,
    stateName: "loading",
    mode: "loading",
    message: "Assembling permission-aware relationship context."
  },
  empty: {
    stateVersion: UI_STATE_VERSION,
    stateName: "empty",
    mode: "empty",
    title: "No relationship work is assigned",
    message: "New work will appear here when it is assigned to your queue."
  },
  denied: {
    stateVersion: UI_STATE_VERSION,
    stateName: "denied",
    mode: "denied",
    title: "Context is not available",
    message:
      "Your current permissions or declared purpose do not allow access to this relationship context.",
    correlationId: "10000000-0000-4000-8000-000000000002"
  },
  error: {
    stateVersion: UI_STATE_VERSION,
    stateName: "error",
    mode: "error",
    title: "The command center could not load",
    message:
      "The relationship service is temporarily unavailable. Retry the request.",
    errorCode: "RETRYABLE_DEPENDENCY_FAILURE",
    correlationId: "10000000-0000-4000-8000-000000000003",
    retryable: true
  }
};

export function getUiState(stateName) {
  const selected = UI_STATES[stateName] || UI_STATES.error;
  return JSON.parse(JSON.stringify(selected));
}
