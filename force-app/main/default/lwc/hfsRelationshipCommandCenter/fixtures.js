export const UI_STATE_VERSION = "1.0.0";

const caseState = {
  id: "work-north-star-hospital-surge-001",
  externalKey: "CORR-NORTH-STAR-HOSPITAL-MORNING-001",
  title: "North Star hospital operations surge",
  summary:
    "Patient complaints, blocked discharge rooms, low pharmacy stock, delayed lab response, and stuck billing approvals need one manager-approved action plan.",
  severity: "High",
  status: "Awaiting approval",
  owner: {
    name: "Operations Manager",
    role: "Hospital operations approval",
    since: "2026-06-06T09:35:00Z"
  },
  serviceDeadline: "2026-06-06T11:15:00Z",
  nextUpdateDue: "2026-06-06T10:00:00Z",
  profile: {
    core: "North Star universal operations",
    activeProfile: "profile:hospital-private-large",
    displayName: "Large private hospital operations",
    boundary:
      "Hospital wording is profile display only; the core agents and actions stay sector-neutral."
  },
  operationsContext: {
    organization: "North Star Private Hospital",
    resource: "Morning outpatient and discharge flow",
    category: "Hospital operations",
    operationalFocus: "BED-BLOCK-A3 / PHARM-IV-KIT-LOW",
    partner: "Island Diagnostics Lab",
    recoveryWindow: "Morning operations window",
    serviceAreas: "Outpatient reception, Ward A3, Pharmacy"
  },
  profileMappings: [
    {
      id: "mapping-room-readiness",
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
      id: "mapping-stock-risk",
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
      id: "mapping-billing-dispute",
      issue: "Duplicate charge",
      primitive: "Risk",
      hospital: "Billing duplicate",
      hotel: "Guest overcharge",
      airport: "Passenger fee dispute",
      banking: "Bank dispute",
      supermarket: "Receipt overcharge",
      cruise: "Onboard account dispute"
    },
    {
      id: "mapping-complaint",
      issue: "Customer complaint",
      primitive: "Signal",
      hospital: "Patient or visitor complaint",
      hotel: "Guest complaint",
      airport: "Passenger complaint",
      banking: "Client complaint",
      supermarket: "Shopper complaint",
      cruise: "Guest complaint"
    },
    {
      id: "mapping-partner-delay",
      issue: "Partner delay",
      primitive: "Partner",
      hospital: "Lab, insurer, or supplier delay",
      hotel: "Laundry or supplier delay",
      airport: "Airline or ground handler delay",
      banking: "Processor or insurer delay",
      supermarket: "Supplier or delivery delay",
      cruise: "Port or supplier delay"
    }
  ],
  resourcePositions: [
    { id: "resource-beds", label: "Ready beds", value: "6 of 18" },
    { id: "resource-rooms", label: "Blocked rooms", value: "7 rooms" },
    { id: "resource-queue", label: "Queue wait", value: "74 min" },
    { id: "resource-pharmacy", label: "IV kits", value: "2.4 hrs cover" }
  ],
  riskPulses: [
    { id: "risk-complaint", label: "Complaints", status: "Clustered" },
    { id: "risk-bed", label: "Bed capacity", status: "High" },
    { id: "risk-queue", label: "Queue", status: "Rising" },
    { id: "risk-pharmacy", label: "Pharmacy stock", status: "Low cover" },
    { id: "risk-lab", label: "Lab partner", status: "Delayed" },
    { id: "risk-billing", label: "Billing", status: "Stalled" },
    { id: "risk-approval", label: "Approval", status: "Required" },
    { id: "risk-clinical", label: "Clinical boundary", status: "Refuse" },
    { id: "risk-communication", label: "Communication", status: "Drafted" },
    { id: "risk-outcome", label: "Outcome", status: "Pending" }
  ],
  complaintCluster: {
    type: "Wait time, room readiness, billing, pharmacy delay",
    count: 11,
    resource: "Outpatient and discharge experience",
    operationalFocus: "Morning surge window",
    partner: "Island Diagnostics Lab",
    window: "08:45-09:18"
  },
  inboundComplaintIntake: {
    sourceChannel: "Twilio Sandbox WhatsApp",
    customerAlias: "alias-whatsapp-customer-demo",
    protectedActionState: "No protected action executed",
    summary:
      "Inbound WhatsApp complaint expands into wait time, pharmacy stock, and billing review without storing raw phone or message text.",
    followUpQuestions: [
      "Which service area were you in?",
      "When did the issue happen?",
      "Was the pharmacy delay caused by queue time, unavailable stock, or missing approval?",
      "Was the billing concern a duplicate charge, claim delay, refund, or payment issue?",
      "What outcome would make this acceptable for you?"
    ],
    rootCauseHypotheses: [
      "Queue pressure or staff coverage gap may be driving the complaint.",
      "Low stock, counter queue, or approval delay may be affecting pharmacy service.",
      "Duplicate invoice, insurer delay, or payment review may be causing financial friction."
    ],
    nextEvidenceNeeded: [
      "current queue or service-area status",
      "pharmacy stock and counter queue status",
      "billing or insurance case status",
      "manager approval requirement"
    ]
  },
  agentHandoffTrace: [
    {
      id: "handoff-orchestrator",
      agent: "North Star Orchestrator",
      contribution:
        "Expanded one WhatsApp complaint into trust, capacity, pharmacy, billing, vendor, communication, approval, and outcome work.",
      output: "One manager-ready action plan"
    },
    {
      id: "handoff-evidence-context",
      agent: "Evidence and Context",
      contribution:
        "Mapped WhatsApp complaint, queue, stock, billing, and vendor records into global primitives.",
      output: "Signal, Evidence, Customer, Resource, Partner, Risk"
    },
    {
      id: "handoff-customer-trust",
      agent: "Customer Trust",
      contribution:
        "Classified complaint themes and drafted safe follow-up questions. The hospital profile displays this as patient or visitor trust.",
      output: "Complaint type, missing evidence, privacy-safe response draft"
    },
    {
      id: "handoff-resource-capacity",
      agent: "Resource and Capacity",
      contribution:
        "Checked bed pressure, outpatient queue, pharmacy stock cover, and staff load.",
      output: "Capacity risk, stockout risk, staff gap"
    },
    {
      id: "handoff-partner-vendor",
      agent: "Partner and Vendor",
      contribution:
        "Connected the complaint to lab, supplier, insurer, and vendor SLA follow-up.",
      output: "Vendor escalation and protected mock email"
    },
    {
      id: "handoff-financial-impact",
      agent: "Financial Impact",
      contribution:
        "Flagged duplicate invoice and insurance-review exposure without using personal billing data.",
      output: "Billing review action and exposure estimate"
    },
    {
      id: "handoff-risk-approval",
      agent: "Risk and Approval",
      contribution:
        "Required manager approval and refused any clinical diagnosis, treatment, dosage, or triage decision.",
      output: "Approval requirement and clinical refusal boundary"
    },
    {
      id: "handoff-communication",
      agent: "Communication",
      contribution:
        "Prepared Slack manager approval, internal Slack alert, and Twilio WhatsApp update after approval.",
      output: "Slack approval, Slack alert, WhatsApp alert"
    },
    {
      id: "handoff-operations",
      agent: "Operations Execution",
      contribution:
        "Converted the approved plan into cleaning, porter, pharmacy, billing, and vendor tasks.",
      output: "Role-owned task records"
    },
    {
      id: "handoff-outcome-learning",
      agent: "Outcome Learning",
      contribution:
        "Measured wait reduction, bed release, stockout avoidance, complaint containment, and SLA follow-up.",
      output: "Outcome metrics and next-plan evidence"
    }
  ],
  partnerResponse: {
    status: "Lab escalation pending",
    responseDelay: "42 minutes over SLA",
    recoveryOption: "Second courier route available",
    financialImpact: "Not applicable",
    boundary: "Operational SLA delay, not clinical interpretation"
  },
  orchestrationConflicts: [
    {
      id: "conflict-patient-capacity",
      agent: "Customer Trust vs Resource and Capacity",
      conflict:
        "Customer Trust wants a quick service response, but Resource and Capacity shows rooms are still blocked.",
      resolution:
        "Approve internal updates now, then release rooms only after cleaning and porter tasks are acknowledged."
    },
    {
      id: "conflict-pharmacy-billing",
      agent: "Resource and Capacity vs Financial Impact",
      conflict:
        "Pharmacy stock needs restock or transfer while billing approvals are stuck for affected cases.",
      resolution:
        "Route pharmacy and billing actions through one manager approval instead of creating disconnected work."
    },
    {
      id: "conflict-clinical-boundary",
      agent: "Risk and Approval",
      conflict:
        "The fastest-sounding question asks who should receive treatment first.",
      resolution:
        "Refuse clinical priority decisions and keep North Star on operations coordination only."
    }
  ],
  recommendationUpdates: [
    {
      id: "update-lab-response",
      trigger: "Partner response changed the plan",
      before:
        "Before partner evidence, North Star keeps lab escalation pending and names missing response evidence.",
      after:
        "After Island Diagnostics confirms the delay and second courier route, North Star narrows the action to approved SLA escalation plus alternate courier request.",
      evidence: "evidence-partner-hospital-001"
    },
    {
      id: "update-capacity-evidence",
      trigger: "Capacity evidence qualified the plan",
      before:
        "A generic complaint workflow would send a manager message and stop.",
      after:
        "North Star ties the complaint to blocked rooms, queue pressure, staff coverage, pharmacy stock, billing, and outcome metrics.",
      evidence: "evidence-capacity-hospital-001"
    }
  ],
  operationsExecution: {
    primaryRecommendation:
      "Move one front-desk staff member to outpatient check-in, dispatch cleaning and porter tasks, and open billing review after manager approval.",
    tasks: [
      {
        id: "task-cleaning",
        label: "Clean and release Ward A3 discharge rooms",
        owner: "Housekeeping Lead",
        status: "Queued"
      },
      {
        id: "task-porter",
        label: "Move discharged patients to lounge after nurse handoff",
        owner: "Porter Coordinator",
        status: "Pending approval"
      },
      {
        id: "task-pharmacy",
        label: "Request approved IV kit restock or transfer",
        owner: "Pharmacy Lead",
        status: "Awaiting approval"
      },
      {
        id: "task-billing",
        label: "Open duplicate invoice and insurer follow-up review",
        owner: "Billing Supervisor",
        status: "Pending"
      }
    ]
  },
  affectedRelationship: {
    label: "Hospital operations context",
    subject: "North Star Private Hospital",
    object: "Morning operations surge",
    type: "HAS_OPERATIONAL_RISK",
    status: "Active"
  },
  connectedEntities: [
    {
      id: "HOSP-NORTH-STAR-PRIVATE",
      label: "North Star Private Hospital",
      type: "Organization",
      role: "Demo hospital profile"
    },
    {
      id: "DEPT-OUTPATIENT-RECEPTION",
      label: "Outpatient reception",
      type: "Location",
      role: "Queue and complaints focus"
    },
    {
      id: "RESOURCE-WARD-A3-BEDS",
      label: "Ward A3 discharge beds",
      type: "Resource",
      role: "Blocked capacity"
    },
    {
      id: "PARTNER-ISLAND-DIAGNOSTICS",
      label: "Island Diagnostics Lab",
      type: "Partner",
      role: "Delayed vendor response"
    }
  ],
  blockers: [
    {
      id: "blocker-approval-001",
      label: "Manager approval for protected operations actions",
      owner: "Operations Manager",
      status: "Ready for decision",
      dueAt: "2026-06-06T10:00:00Z"
    },
    {
      id: "blocker-clinical-001",
      label: "Clinical treatment and triage decisions are out of scope",
      owner: "Risk and Approval Agent",
      status: "Refused and routed to clinician",
      dueAt: "2026-06-06T09:40:00Z"
    }
  ],
  timeline: [
    {
      id: "timeline-complaints",
      occurredAt: "2026-06-06T08:45:00Z",
      type: "Patient trust",
      title: "Complaint cluster detected",
      detail:
        "Eleven patient and visitor complaints mention wait time, room readiness, billing, and pharmacy delay.",
      source: "Synthetic hospital complaints"
    },
    {
      id: "timeline-capacity",
      occurredAt: "2026-06-06T09:02:00Z",
      type: "Resource capacity",
      title: "Discharge rooms blocked",
      detail:
        "Seven rooms are blocked by cleaning and porter handoff tasks, reducing ready beds to six.",
      source: "Bed management fixture"
    },
    {
      id: "timeline-pharmacy",
      occurredAt: "2026-06-06T09:11:00Z",
      type: "Pharmacy stock",
      title: "Low operational stock cover",
      detail:
        "IV kit cover falls below the four-hour threshold before the afternoon rush.",
      source: "Pharmacy stock fixture"
    },
    {
      id: "timeline-partner",
      occurredAt: "2026-06-06T09:25:00Z",
      type: "Partner SLA",
      title: "Lab vendor response delayed",
      detail:
        "Island Diagnostics is forty-two minutes over the agreed response window.",
      source: "Lab partner mock"
    },
    {
      id: "timeline-approval",
      occurredAt: "2026-06-06T09:36:00Z",
      type: "Approval",
      title: "Manager decision requested",
      detail:
        "No Slack, WhatsApp, billing, pharmacy, vendor, room, or staff-task write-back has executed.",
      source: "North Star Orchestrator"
    }
  ],
  evidence: [
    {
      id: "evidence-complaint-hospital-001",
      label: "Patient complaint cluster",
      summary:
        "Eleven synthetic complaints map to customer trust, billing, pharmacy, and room readiness signals.",
      sourceUri: "urn:hfs:source:hospital:complaints",
      capturedAt: "2026-06-06T08:45:00Z",
      contentHash:
        "sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f"
    },
    {
      id: "evidence-capacity-hospital-001",
      label: "Capacity and queue facts",
      summary:
        "Ready beds are constrained, outpatient wait is seventy-four minutes, and discharge rooms are blocked.",
      sourceUri: "urn:hfs:source:hospital:capacity",
      capturedAt: "2026-06-06T09:02:00Z",
      contentHash:
        "sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb"
    },
    {
      id: "evidence-partner-hospital-001",
      label: "Partner and pharmacy evidence",
      summary:
        "Lab response is late and pharmacy stock cover is below the demo threshold.",
      sourceUri: "urn:hfs:source:hospital:partner-stock",
      capturedAt: "2026-06-06T09:25:00Z",
      contentHash:
        "sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588"
    },
    {
      id: "evidence-billing-hospital-001",
      label: "Billing and approval evidence",
      summary:
        "Three duplicate invoice reviews and two insurer follow-ups are stuck behind manager approval.",
      sourceUri: "urn:hfs:source:hospital:billing",
      capturedAt: "2026-06-06T09:30:00Z",
      contentHash:
        "sha256:f42d186a12981c8c7a25b7be50f5f95541e4323f83f3f3c65de8e20717b5e6ea"
    }
  ],
  sop: {
    name: "North Star hospital operations plan",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await manager approval",
    completedSteps: 3,
    totalSteps: 6,
    progress: 50,
    requiredEvidence: "Approved action set and channel delivery results"
  },
  recommendation: {
    id: "recommendation-north-star-hospital-001",
    status: "Pending approval",
    title: "Approve hospital operations actions",
    recommendation:
      "Approve room-cleaning and porter tasks, pharmacy restock or transfer, lab vendor escalation, billing review, insurance follow-up, and privacy-safe Slack and WhatsApp-style internal alerts. Refuse clinical diagnosis, treatment, dosage, and triage decisions.",
    facts: [
      "Complaints are clustered across wait time, room readiness, billing, and pharmacy delay.",
      "Seven discharge rooms are blocked and ready bed capacity is constrained.",
      "IV kit stock cover is below the four-hour operational threshold.",
      "Lab partner response is forty-two minutes over the demo SLA."
    ],
    inferences: [
      "The complaint is not just a complaint; it affects capacity, partner response, billing, communications, and outcome tracking.",
      "The safe next step is operational: task owners, manager approval, protected action execution, and outcome measurement."
    ],
    confidence: 0.88,
    confidencePercent: "88%",
    modelProfile: "north-star-hospital-operations",
    modelProfileVersion: "1.0.0",
    policyVersion: "north-star-hospital-routing-mauritius 1.0.0",
    evidenceIds: [
      "evidence-complaint-hospital-001",
      "evidence-capacity-hospital-001",
      "evidence-partner-hospital-001",
      "evidence-billing-hospital-001"
    ],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-north-star-hospital-001",
    status: "Pending",
    policy: "North Star operations manager approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-06T09:36:00Z",
    requestedBy: "North Star Orchestrator",
    decisionDueAt: "2026-06-06T10:00:00Z"
  },
  actions: [
    {
      id: "action-bed-cleaning-001",
      type: "REQUEST_BED_CLEANING",
      status: "Pending approval",
      requestedAt: "2026-06-06T09:36:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft mock",
      correlationId: "20000000-0000-4000-8000-000000000001"
    },
    {
      id: "action-lab-vendor-001",
      type: "ESCALATE_LAB_VENDOR_CASE",
      status: "Pending approval",
      requestedAt: "2026-06-06T09:36:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft mock",
      correlationId: "20000000-0000-4000-8000-000000000001"
    }
  ],
  channelLog: [
    {
      id: "channel-slack-001",
      channel: "Slack",
      status: "MOCK_SENT",
      target: "Operations Manager",
      detail: "Webhook missing; privacy-safe mock message recorded honestly."
    },
    {
      id: "channel-whatsapp-001",
      channel: "WhatsApp-style",
      status: "MOCK_SENT",
      target: "Pharmacy Lead",
      detail:
        "Provider credentials missing; internal demo alert recorded without personal contact data."
    }
  ],
  voiceMode: {
    status: "Manual transcript fixture",
    summary:
      "Voice mode is modeled as an operator transcript input. It can request an Agentforce recommendation, but it cannot execute protected actions.",
    requests: [
      {
        id: "voice-request-action-plan",
        transcriptSource: "manual",
        transcript:
          "Why are discharge beds blocked this morning and who needs to act before the outpatient queue gets worse?",
        interpretedIntent: "ASK_HOSPITAL_ACTION_PLAN",
        agentforceAction: "DRAFT_RELATIONSHIP_RECOMMENDATION",
        recommendationId: "recommendation-north-star-hospital-001",
        status: "Ready for Agentforce",
        protectedActionState: "No protected action executed",
        refusal: null,
        structuredFields: [
          {
            id: "voice-issue",
            label: "Issue",
            value: "Blocked discharge beds and outpatient queue risk"
          },
          {
            id: "voice-department",
            label: "Department",
            value: "DEPT-OUTPATIENT-RECEPTION"
          },
          {
            id: "voice-location",
            label: "Location",
            value: "WARD-A3-DISCHARGE"
          },
          {
            id: "voice-resources",
            label: "Resources",
            value: "BED-BLOCK-A3, QUEUE-OUTPATIENT-009"
          },
          {
            id: "voice-role",
            label: "Requested by",
            value: "Operations Manager"
          },
          {
            id: "voice-urgency",
            label: "Urgency",
            value: "High"
          },
          {
            id: "voice-evidence",
            label: "Evidence",
            value:
              "evidence-capacity-hospital-001, evidence-complaint-hospital-001"
          },
          {
            id: "voice-window",
            label: "Time window",
            value: "2026-06-06T08:00:00+04:00/2026-06-06T12:00:00+04:00"
          }
        ]
      },
      {
        id: "voice-request-clinical-refusal",
        transcriptSource: "manual",
        transcript: "Which patient should receive treatment first?",
        interpretedIntent: "CLINICAL_DECISION_REFUSAL",
        agentforceAction: "DRAFT_RELATIONSHIP_RECOMMENDATION",
        recommendationId: "recommendation-clinical-refusal-fixture",
        status: "Refused and routed",
        protectedActionState: "No clinical or protected action executed",
        refusal:
          "North Star handles hospital operations only. Treatment priority, diagnosis, dosage, and triage decisions are routed to a clinician or clinical manager.",
        structuredFields: [
          {
            id: "voice-clinical-issue",
            label: "Issue",
            value: "Clinical treatment priority request"
          },
          {
            id: "voice-clinical-route",
            label: "Route",
            value: "Clinician review"
          },
          {
            id: "voice-clinical-boundary",
            label: "Boundary",
            value: "Clinical priority decision refused"
          },
          {
            id: "voice-clinical-evidence",
            label: "Evidence",
            value: "evidence-clinical-refusal-hospital-001"
          }
        ]
      }
    ]
  },
  outcomeMetrics: [
    { id: "outcome-wait", label: "Wait time reduced", value: "Projected 22%" },
    { id: "outcome-bed", label: "Beds released", value: "4 rooms" },
    { id: "outcome-stock", label: "Stockout avoided", value: "IV kits" },
    { id: "outcome-complaint", label: "Complaint containment", value: "Open" },
    { id: "outcome-billing", label: "Billing exposure", value: "Flagged" },
    { id: "outcome-sla", label: "Partner SLA", value: "Escalated" }
  ],
  outcome: {
    status: "Awaiting approved action",
    summary:
      "Outcome metrics are projected until manager approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  }
};

const readyState = {
  stateVersion: UI_STATE_VERSION,
  stateName: "ready",
  mode: "ready",
  generatedAt: "2026-06-06T09:39:00Z",
  correlationId: "20000000-0000-4000-8000-000000000001",
  userRole: "Operations Manager",
  purpose: "RESOLVE_HOSPITAL_OPERATION_RISK",
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
    userRole: "Hospital Viewer",
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
    message: "Assembling North Star hospital operations context."
  },
  empty: {
    stateVersion: UI_STATE_VERSION,
    stateName: "empty",
    mode: "empty",
    title: "No North Star work is assigned",
    message: "New hospital operations work will appear here when assigned."
  },
  denied: {
    stateVersion: UI_STATE_VERSION,
    stateName: "denied",
    mode: "denied",
    title: "North Star context is not available",
    message:
      "Your current permissions or declared purpose do not allow access to this hospital operations context.",
    correlationId: "20000000-0000-4000-8000-000000000002"
  },
  error: {
    stateVersion: UI_STATE_VERSION,
    stateName: "error",
    mode: "error",
    title: "North Star could not load",
    message:
      "The hospital operations command service is temporarily unavailable. Retry the request.",
    errorCode: "RETRYABLE_DEPENDENCY_FAILURE",
    correlationId: "20000000-0000-4000-8000-000000000003",
    retryable: true
  }
};

export function getUiState(stateName) {
  const selected = UI_STATES[stateName] || UI_STATES.error;
  return JSON.parse(JSON.stringify(selected));
}
