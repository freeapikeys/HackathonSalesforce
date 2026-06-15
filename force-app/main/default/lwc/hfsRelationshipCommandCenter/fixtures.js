export const UI_STATE_VERSION = "1.0.0";

export const DEFAULT_PROFILE_KEY = "logia-retail";

const PROFILE_CONFIGS = {
  "logia-retail": {
    key: "logia-retail",
    shortName: "Logia",
    eyebrow: "Logia command center",
    pageTitle: "Supermarket recovery plan",
    loadingTitle: "Loading Logia context",
    loadingMessage: "Assembling Logia retail context.",
    emptyTitle: "No Logia work is assigned",
    emptyMessage: "New supermarket risk work will appear here when assigned.",
    deniedTitle: "Logia context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this retail context.",
    errorTitle: "Logia could not load",
    errorMessage:
      "The retail command service is temporarily unavailable. Retry the request.",
    ownerLabel: "Manager owner",
    deadlineLabel: "Rush deadline",
    updateLabel: "Next decision update",
    riskKicker: "Risk pulse",
    riskHeading: "Logia retail signals",
    relationshipKicker: "Product context",
    relationshipHeading: "Product, batch, and stock",
    contextLabels: {
      primary: "Store",
      secondary: "Product",
      tertiary: "Batch",
      quaternary: "Promotion"
    },
    clusterKicker: "Customer risk",
    clusterHeading: "Complaint cluster",
    clusterLabels: {
      type: "Type",
      count: "Count",
      supplier: "Supplier",
      window: "Window"
    },
    responseKicker: "Supplier",
    responseHeading: "Supplier response",
    responseLabels: {
      leadTime: "Lead time",
      replacement: "Replacement",
      creditNote: "Credit note",
      qualityIssue: "Quality issue"
    },
    executionKicker: "Execution",
    executionHeading: "Store tasks and channel log",
    executionPlanLabel: "Cashier plan",
    recommendationKicker: "Recommendation",
    factsHeading: "Source facts",
    assumptionsHeading: "Assumptions",
    inferencesHeading: "Model inference",
    approvalKicker: "Human control",
    approvalHeading: "Approval decision",
    approvalNote:
      "Approval authorizes execution; it does not mark the external action as completed.",
    blockersKicker: "Dependencies",
    blockersHeading: "Current blockers",
    restrictedNotice:
      "You can inspect the accessible case facts. Approval controls are not available for your current role.",
    outcomeMetricLabel: "Outcome metrics"
  },
  "nexavenu-revenue": {
    key: "nexavenu-revenue",
    shortName: "Nexavenu",
    eyebrow: "Nexavenu revenue intelligence tower",
    pageTitle: "Champion nurture and discovery readiness",
    loadingTitle: "Loading Nexavenu revenue context",
    loadingMessage: "Assembling Nexavenu revenue intelligence context.",
    emptyTitle: "No Nexavenu revenue work is assigned",
    emptyMessage:
      "New prospect or retention work will appear here when assigned.",
    deniedTitle: "Nexavenu revenue context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this revenue context.",
    errorTitle: "Nexavenu context could not load",
    errorMessage:
      "The revenue command service is temporarily unavailable. Retry the request.",
    ownerLabel: "Revenue owner",
    deadlineLabel: "Discovery gate",
    updateLabel: "Next nurture touch",
    riskKicker: "Pipeline pulse",
    riskHeading: "Revenue and buyer-readiness signals",
    relationshipKicker: "Relationship context",
    relationshipHeading: "Prospect, champion, and opportunity",
    contextLabels: {
      primary: "Account",
      secondary: "Opportunity",
      tertiary: "Stage",
      quaternary: "Campaign"
    },
    clusterKicker: "Buyer education",
    clusterHeading: "Education gaps",
    clusterLabels: {
      type: "Gaps",
      count: "Count",
      supplier: "Missing owner",
      window: "Window"
    },
    responseKicker: "Readiness gate",
    responseHeading: "Discovery readiness",
    responseLabels: {
      leadTime: "Score",
      replacement: "Next asset",
      creditNote: "ROI proof",
      qualityIssue: "Constraint"
    },
    executionKicker: "Revenue execution",
    executionHeading: "Nurture actions and handoff log",
    executionPlanLabel: "Handoff gate",
    recommendationKicker: "Revenue recommendation",
    factsHeading: "Source facts",
    assumptionsHeading: "Contact-sourced assumptions",
    inferencesHeading: "Revenue inference",
    approvalKicker: "Human control",
    approvalHeading: "Revenue approval decision",
    approvalNote:
      "Approval authorizes the governed write-back; it does not send outreach without the revenue owner.",
    blockersKicker: "Deal dependencies",
    blockersHeading: "Current blockers",
    restrictedNotice:
      "You can inspect the accessible revenue facts. Approval controls are not available for your current role.",
    outcomeMetricLabel: "Revenue outcome metrics"
  },
  "air-mauritius-passenger": {
    key: "air-mauritius-passenger",
    shortName: "Air Mauritius",
    eyebrow: "Air Mauritius passenger recovery tower",
    pageTitle: "Passenger claims and disruption recovery",
    loadingTitle: "Loading airline recovery context",
    loadingMessage: "Assembling passenger recovery intelligence context.",
    emptyTitle: "No passenger recovery work is assigned",
    emptyMessage:
      "New claims, baggage, disruption, or compensation work will appear here when assigned.",
    deniedTitle: "Airline recovery context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this passenger recovery context.",
    errorTitle: "Airline recovery context could not load",
    errorMessage:
      "The passenger recovery service is temporarily unavailable. Retry the request.",
    ownerLabel: "Recovery owner",
    deadlineLabel: "Passenger SLA",
    updateLabel: "Next passenger update",
    riskKicker: "Passenger pulse",
    riskHeading: "Claims, baggage, and disruption signals",
    relationshipKicker: "Passenger context",
    relationshipHeading: "Passenger, claim, flight, and case",
    contextLabels: {
      primary: "Passenger",
      secondary: "Claim",
      tertiary: "Flight",
      quaternary: "Journey"
    },
    clusterKicker: "Service recovery",
    clusterHeading: "Passenger friction cluster",
    clusterLabels: {
      type: "Friction",
      count: "Cases",
      supplier: "Owner",
      window: "Window"
    },
    responseKicker: "Resolution gate",
    responseHeading: "Compensation and operations response",
    responseLabels: {
      leadTime: "SLA",
      replacement: "Next action",
      creditNote: "Compensation",
      qualityIssue: "Constraint"
    },
    executionKicker: "Recovery execution",
    executionHeading: "Claims actions and passenger updates",
    executionPlanLabel: "Recovery plan",
    recommendationKicker: "Passenger recommendation",
    factsHeading: "Source facts",
    assumptionsHeading: "Operational assumptions",
    inferencesHeading: "Recovery inference",
    approvalKicker: "Human control",
    approvalHeading: "Recovery approval decision",
    approvalNote:
      "Approval authorizes claims and passenger-update actions; protected communications remain governed.",
    blockersKicker: "Recovery blockers",
    blockersHeading: "Current blockers",
    restrictedNotice:
      "You can inspect accessible passenger facts. Approval controls are not available for your current role.",
    outcomeMetricLabel: "Passenger recovery metrics"
  },
  "constance-hospitality": {
    key: "constance-hospitality",
    shortName: "Constance",
    eyebrow: "Constance guest revenue and operations loop",
    pageTitle: "Guest revenue and occupancy recovery",
    loadingTitle: "Loading hospitality context",
    loadingMessage: "Assembling reservations, FX, and guest sentiment context.",
    emptyTitle: "No hospitality work is assigned",
    emptyMessage:
      "New reservations, occupancy, or guest recovery work will appear here when assigned.",
    deniedTitle: "Hospitality context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this hospitality context.",
    errorTitle: "Hospitality context could not load",
    errorMessage:
      "The hospitality command service is temporarily unavailable. Retry the request.",
    ownerLabel: "Revenue owner",
    deadlineLabel: "Booking window",
    updateLabel: "Next guest action",
    riskKicker: "Occupancy pulse",
    riskHeading: "Reservations, FX, and sentiment signals",
    relationshipKicker: "Guest context",
    relationshipHeading: "Guest, booking, stay, and revenue risk",
    contextLabels: {
      primary: "Property",
      secondary: "Booking",
      tertiary: "Stay window",
      quaternary: "Campaign"
    },
    clusterKicker: "Guest sentiment",
    clusterHeading: "Occupancy and sentiment cluster",
    clusterLabels: {
      type: "Signal",
      count: "Records",
      supplier: "Owner",
      window: "Window"
    },
    responseKicker: "Revenue response",
    responseHeading: "Reservations and ERP response",
    responseLabels: {
      leadTime: "FX status",
      replacement: "Next action",
      creditNote: "Revenue proof",
      qualityIssue: "Constraint"
    },
    executionKicker: "Hospitality execution",
    executionHeading: "Guest actions and operations log",
    executionPlanLabel: "Guest plan",
    recommendationKicker: "Hospitality recommendation",
    factsHeading: "Source facts",
    assumptionsHeading: "Revenue assumptions",
    inferencesHeading: "Guest inference",
    approvalKicker: "Human control",
    approvalHeading: "Hospitality approval decision",
    approvalNote:
      "Approval authorizes guest and operations actions; external messages remain governed.",
    blockersKicker: "Hospitality blockers",
    blockersHeading: "Current blockers",
    restrictedNotice:
      "You can inspect accessible hospitality facts. Approval controls are not available for your current role.",
    outcomeMetricLabel: "Hospitality outcome metrics"
  },
  "afrasia-private-banking": {
    key: "afrasia-private-banking",
    shortName: "AfrAsia",
    eyebrow: "AfrAsia relationship intelligence control tower",
    pageTitle: "Private banking relationship intelligence",
    loadingTitle: "Loading private banking context",
    loadingMessage: "Assembling KYC, FX, wealth, and relationship context.",
    emptyTitle: "No private banking work is assigned",
    emptyMessage:
      "New RM, KYC, cross-border, or wealth-signal work will appear here when assigned.",
    deniedTitle: "Private banking context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this banking context.",
    errorTitle: "Private banking context could not load",
    errorMessage:
      "The private banking command service is temporarily unavailable. Retry the request.",
    ownerLabel: "Relationship manager",
    deadlineLabel: "Compliance SLA",
    updateLabel: "Next RM touch",
    riskKicker: "Relationship pulse",
    riskHeading: "KYC, FX, and wealth relationship signals",
    relationshipKicker: "Client context",
    relationshipHeading: "Client, RM, product, and compliance state",
    contextLabels: {
      primary: "Client",
      secondary: "Relationship",
      tertiary: "Jurisdiction",
      quaternary: "Product"
    },
    clusterKicker: "RM intelligence",
    clusterHeading: "Client and compliance cluster",
    clusterLabels: {
      type: "Signal",
      count: "Records",
      supplier: "Owner",
      window: "Window"
    },
    responseKicker: "Compliance gate",
    responseHeading: "KYC and relationship response",
    responseLabels: {
      leadTime: "KYC status",
      replacement: "Next action",
      creditNote: "Commercial proof",
      qualityIssue: "Constraint"
    },
    executionKicker: "RM execution",
    executionHeading: "RM actions and approval log",
    executionPlanLabel: "RM plan",
    recommendationKicker: "Banking recommendation",
    factsHeading: "Source facts",
    assumptionsHeading: "RM assumptions",
    inferencesHeading: "Relationship inference",
    approvalKicker: "Human control",
    approvalHeading: "Banking approval decision",
    approvalNote:
      "Approval authorizes RM workflow actions; regulated communications and KYC changes remain governed.",
    blockersKicker: "Compliance blockers",
    blockersHeading: "Current blockers",
    restrictedNotice:
      "You can inspect accessible banking facts. Approval controls are not available for your current role.",
    outcomeMetricLabel: "Private banking metrics"
  },
  "sunlife-guest-recovery": {
    key: "sunlife-guest-recovery",
    shortName: "Sunlife",
    eyebrow: "Sunlife guest recovery and experience loop",
    pageTitle: "Guest recovery and experience intelligence",
    loadingTitle: "Loading guest recovery context",
    loadingMessage:
      "Assembling guest service, staff task, and sustainability context.",
    emptyTitle: "No guest recovery work is assigned",
    emptyMessage:
      "New guest recovery, staff task, or experience work will appear here when assigned.",
    deniedTitle: "Guest recovery context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this guest recovery context.",
    errorTitle: "Guest recovery context could not load",
    errorMessage:
      "The guest recovery service is temporarily unavailable. Retry the request.",
    ownerLabel: "Experience owner",
    deadlineLabel: "Guest SLA",
    updateLabel: "Next guest touch",
    riskKicker: "Experience pulse",
    riskHeading: "Guest recovery, staff, and service signals",
    relationshipKicker: "Guest context",
    relationshipHeading: "Guest, stay, staff, and experience risk",
    contextLabels: {
      primary: "Guest",
      secondary: "Stay",
      tertiary: "Service area",
      quaternary: "Recovery moment"
    },
    clusterKicker: "Guest recovery",
    clusterHeading: "Experience and staff coordination cluster",
    clusterLabels: {
      type: "Signal",
      count: "Records",
      supplier: "Owner",
      window: "Window"
    },
    responseKicker: "Service response",
    responseHeading: "Guest recovery response",
    responseLabels: {
      leadTime: "SLA",
      replacement: "Next action",
      creditNote: "Recovery offer",
      qualityIssue: "Constraint"
    },
    executionKicker: "Guest execution",
    executionHeading: "Guest messages and staff task log",
    executionPlanLabel: "Recovery plan",
    recommendationKicker: "Guest recovery recommendation",
    factsHeading: "Source facts",
    assumptionsHeading: "Experience assumptions",
    inferencesHeading: "Guest inference",
    approvalKicker: "Human control",
    approvalHeading: "Guest recovery approval decision",
    approvalNote:
      "Approval authorizes staff and guest-recovery actions; outbound guest messages remain governed.",
    blockersKicker: "Experience blockers",
    blockersHeading: "Current blockers",
    restrictedNotice:
      "You can inspect accessible guest facts. Approval controls are not available for your current role.",
    outcomeMetricLabel: "Guest recovery metrics"
  }
};

export function getProfile(profileKey = DEFAULT_PROFILE_KEY) {
  return PROFILE_CONFIGS[profileKey] || PROFILE_CONFIGS[DEFAULT_PROFILE_KEY];
}

function operatingLayer({ kpis, trendTitle, trend, brief, agents, channels }) {
  return {
    kpis: kpis.map((kpi) => ({
      ...kpi,
      predictionStyle: `width: ${kpi.predictionPercent || 0}%`
    })),
    trendTitle,
    trend: trend.map((point) => ({
      ...point,
      actualStyle: `height: ${point.actual || point.value || 0}%`,
      predictedStyle: `height: ${point.predicted || point.value || 0}%`
    })),
    brief,
    agents,
    channels
  };
}

const caseState = {
  id: "work-logia-retail-risk-001",
  externalKey: "CORR-LOGIA-WEEKEND-GRILL-001",
  title: "Logia weekend promotion recovery",
  summary:
    "Fresh beef patties need a manager-approved recovery plan before the weekend rush.",
  severity: "High",
  status: "Awaiting approval",
  owner: {
    name: "Duty Manager",
    role: "Store manager approval",
    since: "2026-06-06T09:35:00Z"
  },
  serviceDeadline: "2026-06-06T16:15:00Z",
  nextUpdateDue: "2026-06-06T10:00:00Z",
  relationshipContext: {
    store: "Goodlands FreshMart",
    product: "Island beef burger patties 400g",
    category: "Fresh food",
    batch: "BATCH-FRESH-BEEF-2026-06-07-A",
    supplier: "Island Proteins Ltd",
    promotion: "Weekend Grill",
    resourceArea: "SHELF-MEAT-CHILLER-A3"
  },
  stock: [
    { id: "stock-shelf", label: "Shelf", value: "18 units" },
    { id: "stock-backroom", label: "Backroom", value: "24 units" },
    { id: "stock-warehouse", label: "Warehouse", value: "72 units" },
    { id: "stock-supplier", label: "Supplier", value: "180 units" }
  ],
  riskPulses: [
    { id: "risk-stockout", label: "Stockout", status: "High" },
    { id: "risk-expiry", label: "Expiry", status: "High" },
    { id: "risk-overstock", label: "Overstock", status: "Low" },
    { id: "risk-complaint", label: "Complaint", status: "Watch" },
    { id: "risk-supplier", label: "Supplier", status: "Responded" },
    { id: "risk-queue", label: "Queue", status: "16:30 risk" },
    { id: "risk-shelf", label: "Shelf layout", status: "Mismatch" },
    { id: "risk-price", label: "Price", status: "Mismatch" },
    { id: "risk-promotion", label: "Promotion", status: "Active" },
    { id: "risk-staff", label: "Staff readiness", status: "Needs lane" }
  ],
  complaintCluster: {
    type: "Smell, damaged packaging, refund, price mismatch",
    count: 5,
    product: "Island beef burger patties 400g",
    batch: "BATCH-FRESH-BEEF-2026-06-07-A",
    supplier: "Island Proteins Ltd",
    window: "09:00-09:18"
  },
  partnerResponse: {
    status: "Replacement approved",
    leadTime: "18 hours",
    replacement: "BATCH-FRESH-BEEF-2026-06-08-B",
    creditNote: "Offered",
    qualityIssue: "Batch-specific review remains open"
  },
  operationsExecution: {
    primaryRecommendation: "Open one extra lane by 16:15",
    tasks: [
      {
        id: "task-restock",
        label: "Transfer safe warehouse stock",
        owner: "Stockroom",
        status: "Acknowledged"
      },
      {
        id: "task-rotate",
        label: "Rotate near-expiry safe units",
        owner: "Fresh Food Lead",
        status: "In progress"
      },
      {
        id: "task-shelf",
        label: "Fix shelf price and promo signage",
        owner: "Floor Supervisor",
        status: "Queued"
      },
      {
        id: "task-cashier",
        label: "Open extra cashier lane",
        owner: "Cashier Lead",
        status: "Pending"
      }
    ]
  },
  affectedRelationship: {
    label: "Retail context",
    subject: "Goodlands FreshMart",
    object: "Island beef burger patties 400g",
    type: "STOCKS_PRODUCT",
    status: "Active"
  },
  relationshipHistory: [
    {
      id: "history-store-product-001",
      type: "STOCKS_PRODUCT",
      subject: "Goodlands FreshMart",
      object: "Island beef burger patties 400g",
      status: "Active",
      confidencePercent: "98%",
      sourceEventId: "event-stockout-risk-detected",
      evidenceSummary:
        "Inventory and promotion evidence link the store, product, and weekend demand spike.",
      correctionState: "Current"
    },
    {
      id: "history-supplier-batch-001",
      type: "SUPPLIES_BATCH",
      subject: "Island Proteins Ltd",
      object: "BATCH-FRESH-BEEF-2026-06-07-A",
      status: "Under review",
      confidencePercent: "92%",
      sourceEventId: "event-supplier-response-received",
      evidenceSummary:
        "Supplier response narrows the issue to a replacement and batch review, not a full supplier stop.",
      correctionState: "Reviewable"
    }
  ],
  identityLinks: [
    {
      id: "participant-store-001",
      role: "STORE",
      entity: "Goodlands FreshMart",
      sourceEventId: "event-stockout-risk-detected",
      evidenceSummary: "Store participated in the demand and stockout signal."
    },
    {
      id: "participant-supplier-001",
      role: "SUPPLIER",
      entity: "Island Proteins Ltd",
      sourceEventId: "event-supplier-response-received",
      evidenceSummary:
        "Supplier participated in the response that changed the recommendation."
    }
  ],
  relationshipContradictions: [
    {
      id: "contradiction-batch-scope-001",
      claim:
        "Complaint cluster supports quarantining suspect Batch A units before the rush.",
      counterclaim:
        "Supplier response supports replacement and continued supplier relationship.",
      resolution:
        "Quarantine suspect batch units only; keep supplier ordering decisions evidence-scoped."
    }
  ],
  correctionActions: [
    {
      id: "correction-batch-scope-001",
      label: "Request correction review",
      target: "Batch scope",
      reason:
        "Ask a manager to supersede the batch-risk claim only if inspection evidence changes.",
      sourceEventId: "event-supplier-response-received"
    }
  ],
  connectedEntities: [
    {
      id: "STORE-GOODLANDS-FRESHMART",
      label: "Goodlands FreshMart",
      type: "Store",
      role: "Promotion store"
    },
    {
      id: "PROD-FRESH-BEEF-PATTIES-400G",
      label: "Island beef burger patties 400g",
      type: "Product",
      role: "Risk product"
    },
    {
      id: "BATCH-FRESH-BEEF-2026-06-07-A",
      label: "Batch A, use by 2026-06-08",
      type: "Product batch",
      role: "Complaint and expiry focus"
    },
    {
      id: "SUPPLIER-ISLAND-PROTEINS",
      label: "Island Proteins Ltd",
      type: "Supplier",
      role: "Replacement supplier"
    }
  ],
  blockers: [
    {
      id: "blocker-approval-001",
      label: "Manager approval for consequential actions",
      owner: "Duty Manager",
      status: "Ready for decision",
      dueAt: "2026-06-06T10:00:00Z"
    }
  ],
  timeline: [
    {
      id: "timeline-stockout",
      occurredAt: "2026-06-06T09:00:00Z",
      type: "Stockout",
      title: "Low cover detected",
      detail: "Sales velocity exceeds shelf and backroom cover.",
      source: "Retail inventory"
    },
    {
      id: "timeline-complaint",
      occurredAt: "2026-06-06T09:14:00Z",
      type: "Complaint",
      title: "Complaint cluster detected",
      detail: "Smell, packaging, refund, and price mismatch reports linked.",
      source: "Customer risk"
    },
    {
      id: "timeline-supplier",
      occurredAt: "2026-06-06T09:25:00Z",
      type: "Supplier",
      title: "Replacement batch approved",
      detail: "Supplier response changes the recommendation.",
      source: "Supplier mock"
    },
    {
      id: "timeline-queue",
      occurredAt: "2026-06-06T09:30:00Z",
      type: "Queue",
      title: "Peak queue risk forecast",
      detail: "Extra cashier lane recommended for 16:30-18:30.",
      source: "Roster forecast"
    },
    {
      id: "timeline-approval",
      occurredAt: "2026-06-06T09:36:00Z",
      type: "Approval",
      title: "Manager decision requested",
      detail: "No protected action has executed.",
      source: "Logia Orchestrator"
    }
  ],
  evidence: [
    {
      id: "evidence-inventory-logia-001",
      label: "Inventory and demand",
      summary:
        "Shelf 18, backroom 24, warehouse 72, supplier 180, sales velocity 28 units per hour.",
      sourceUri: "urn:hfs:source:retail:inventory",
      capturedAt: "2026-06-06T09:01:00Z",
      contentHash:
        "sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f"
    },
    {
      id: "evidence-complaint-logia-001",
      label: "Complaint cluster",
      summary:
        "Five complaints mention smell, damaged packaging, refunds, and price mismatch.",
      sourceUri: "urn:hfs:source:retail:complaints",
      capturedAt: "2026-06-06T09:14:00Z",
      contentHash:
        "sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb"
    },
    {
      id: "evidence-supplier-logia-001",
      label: "Supplier response",
      summary:
        "Replacement batch approved with 18-hour lead time and credit note.",
      sourceUri: "urn:hfs:source:retail:supplier",
      capturedAt: "2026-06-06T09:25:00Z",
      contentHash:
        "sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588"
    },
    {
      id: "evidence-staffing-logia-001",
      label: "Staffing forecast",
      summary:
        "Queue risk forecast from 16:30 to 18:30 with one extra lane recommended.",
      sourceUri: "urn:hfs:source:retail:roster",
      capturedAt: "2026-06-06T09:30:00Z",
      contentHash:
        "sha256:f42d186a12981c8c7a25b7be50f5f95541e4323f83f3f3c65de8e20717b5e6ea"
    }
  ],
  sop: {
    name: "Logia retail recovery",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await manager approval",
    completedSteps: 3,
    totalSteps: 6,
    progress: 50,
    requiredEvidence: "Approved action set and channel delivery results"
  },
  recommendation: {
    id: "recommendation-logia-retail-001",
    status: "Pending approval",
    title: "Approve retail recovery actions",
    recommendation:
      "Transfer safe warehouse stock, request supplier replacement, quarantine suspect batch units, mark down only safe near-expiry stock, fix shelf price, open one extra cashier lane, and send internal alerts.",
    facts: [
      "Stock cover is low against promotion demand.",
      "Batch A has near-expiry units and complaint evidence.",
      "Supplier approved replacement batch B with credit note.",
      "Queue risk is forecast from 16:30 to 18:30."
    ],
    assumptions: [],
    inferences: [
      "The complaint signal is batch-specific, not a reason to stop all supplier orders.",
      "Warehouse transfer protects the rush before supplier replacement arrives."
    ],
    confidence: 0.86,
    confidencePercent: "86%",
    modelProfile: "logia-retail-recommendation",
    modelProfileVersion: "1.0.0",
    policyVersion: "logia-retail-routing-mauritius 1.0.0",
    evidenceIds: [
      "evidence-inventory-logia-001",
      "evidence-complaint-logia-001",
      "evidence-supplier-logia-001",
      "evidence-staffing-logia-001"
    ],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-logia-retail-001",
    status: "Pending",
    policy: "Logia manager approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-06T09:36:00Z",
    requestedBy: "Logia Orchestrator",
    decisionDueAt: "2026-06-06T10:00:00Z"
  },
  actions: [
    {
      id: "action-transfer-001",
      type: "CREATE_WAREHOUSE_TRANSFER",
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
      target: "Duty Manager",
      detail: "Webhook missing; mock message recorded honestly."
    },
    {
      id: "channel-whatsapp-001",
      channel: "WhatsApp-style",
      status: "MOCK_SENT",
      target: "Fresh Food Lead",
      detail: "Provider credentials missing; internal demo alert recorded."
    }
  ],
  outcomeMetrics: [
    { id: "outcome-stockout", label: "Stockout avoided", value: "54 units" },
    { id: "outcome-waste", label: "Waste reduced", value: "18 units" },
    { id: "outcome-complaint", label: "Complaint risk", value: "Contained" },
    { id: "outcome-queue", label: "Queue readiness", value: "Extra lane" },
    { id: "outcome-staff", label: "Staff tasks", value: "Critical complete" },
    {
      id: "outcome-supplier",
      label: "Supplier SLA",
      value: "Replacement approved"
    }
  ],
  outcome: {
    status: "Awaiting approved action",
    summary:
      "Outcome metrics are projected until manager approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  },
  operatingLayer: operatingLayer({
    kpis: [
      {
        id: "kpi-retail-stockout",
        label: "Stockout exposure",
        value: "54 units",
        prediction: "Predicted stockout avoided if transfer is approved",
        predictionPercent: 86,
        confidence: "86%",
        delta: "Protected if approved",
        status: "High"
      },
      {
        id: "kpi-retail-waste",
        label: "Waste at risk",
        value: "18 units",
        prediction: "Predicted waste reduction after rotation and markdown",
        predictionPercent: 72,
        confidence: "72%",
        delta: "Markdown/rotation pending",
        status: "Watch"
      },
      {
        id: "kpi-retail-queue",
        label: "Rush readiness",
        value: "16:30",
        prediction: "Predicted queue pressure unless one lane opens",
        predictionPercent: 67,
        confidence: "79%",
        delta: "Extra lane required",
        status: "Action"
      }
    ],
    trendTitle: "Weekend recovery trend",
    trend: [
      { id: "retail-trend-1", label: "Stock", actual: 44, predicted: 86 },
      { id: "retail-trend-2", label: "Waste", actual: 58, predicted: 28 },
      { id: "retail-trend-3", label: "Queue", actual: 67, predicted: 31 },
      { id: "retail-trend-4", label: "Supplier", actual: 62, predicted: 81 }
    ],
    brief: [
      "Approve warehouse transfer and supplier replacement before the promotion rush.",
      "Keep the supplier relationship active; current evidence is batch-scoped.",
      "Send internal Slack and WhatsApp-style alerts only after manager approval."
    ],
    agents: [
      {
        id: "agent-retail-orchestrator",
        name: "Logia Orchestrator",
        status: "Waiting on approval",
        lastMessage:
          "I combined stock, complaint, supplier, and staffing signals into one recovery plan."
      },
      {
        id: "agent-retail-inventory",
        name: "Inventory and Waste Agent",
        status: "Monitoring",
        lastMessage:
          "Warehouse transfer protects the rush while markdown reduces waste."
      },
      {
        id: "agent-retail-store",
        name: "Store Execution Agent",
        status: "Coordinating",
        lastMessage:
          "Fresh Food Lead and Cashier Lead tasks are queued behind approval."
      }
    ],
    channels: [
      {
        id: "dept-retail-ops",
        name: "Store Ops",
        owner: "Duty Manager",
        unread: 3,
        lastMessage: "Cashier Lead can open one lane at 16:15 if approved."
      },
      {
        id: "dept-retail-supplier",
        name: "Supplier Desk",
        owner: "Fresh Food Lead",
        unread: 1,
        lastMessage:
          "Replacement batch is approved; batch A review remains open."
      }
    ]
  })
};

const nexavenuCaseState = {
  ...caseState,
  id: "work-nexavenu-revenue-001",
  externalKey: "CORR-NEXAVENU-REVENUE-INTELLIGENCE-001",
  title: "Nexavenu champion nurture tower",
  summary:
    "Synthetic B2B prospect needs buyer education, champion mapping, and discovery readiness before senior delivery handoff.",
  severity: "High",
  status: "Awaiting revenue approval",
  owner: {
    name: "Revenue Owner",
    role: "Revenue approval",
    since: "2026-06-10T08:40:00Z"
  },
  serviceDeadline: "2026-06-10T12:00:00Z",
  nextUpdateDue: "2026-06-10T09:30:00Z",
  relationshipContext: {
    store: "Synthetic LiftOps Manufacturing",
    product: "Agentforce and MuleSoft transformation",
    category: "B2B revenue pipeline",
    batch: "Discovery readiness: 48/100",
    supplier: "Operations champion",
    promotion: "Agentforce acceleration campaign",
    resourceArea: "Revenue workspace"
  },
  stock: [
    { id: "stage-lead", label: "Pipeline", value: "Lead nurture" },
    { id: "stage-buyer", label: "Buyer journey", value: "Education/test" },
    { id: "stage-readiness", label: "Readiness", value: "48/100" },
    { id: "stage-icp", label: "ICP score", value: "72/100" }
  ],
  riskPulses: [
    { id: "risk-lead-quality", label: "Lead quality", status: "Needs work" },
    { id: "risk-education", label: "Education gaps", status: "High" },
    { id: "risk-champion", label: "Champion", status: "Emerging" },
    { id: "risk-economic-buyer", label: "Economic buyer", status: "Missing" },
    { id: "risk-cio", label: "Technical buyer", status: "Missing" },
    { id: "risk-readiness", label: "Readiness gate", status: "Hold" },
    { id: "risk-content", label: "Content", status: "Assign" },
    { id: "risk-handoff", label: "Consultant handoff", status: "Blocked" },
    { id: "risk-retention", label: "Retention", status: "Watch" },
    { id: "risk-feedback", label: "Feedback loop", status: "Open" }
  ],
  complaintCluster: {
    type: "System inventory, decision owner, budget, success metric",
    count: 4,
    product: "Agentforce and MuleSoft transformation",
    batch: "Discovery readiness: 48/100",
    supplier: "Executive sponsor and data owner",
    window: "Pre-discovery nurture"
  },
  partnerResponse: {
    status: "Hold before handoff",
    leadTime: "48/100",
    replacement: "AI readiness checklist + MuleSoft explainer",
    creditNote: "CFO ROI proof needed",
    qualityIssue: "Do not consume senior solution-consultant time yet"
  },
  operationsExecution: {
    primaryRecommendation:
      "Hold solution-consultant handoff until readiness > 70",
    tasks: [
      {
        id: "task-nurture",
        label: "Create nurture task",
        owner: "BDR",
        status: "Queued"
      },
      {
        id: "task-email",
        label: "Draft champion email",
        owner: "Revenue Owner",
        status: "Needs approval"
      },
      {
        id: "task-content",
        label: "Assign buyer education assets",
        owner: "Marketing",
        status: "Queued"
      },
      {
        id: "task-handoff",
        label: "Create solution-consultant handoff",
        owner: "Solutions Lead",
        status: "Blocked by readiness"
      }
    ]
  },
  affectedRelationship: {
    label: "Prospect relationship",
    subject: "Nexavenu",
    object: "Synthetic LiftOps Manufacturing",
    type: "NURTURES_PROSPECT",
    status: "Active"
  },
  relationshipHistory: [
    {
      id: "history-nexavenu-prospect-001",
      type: "NURTURES_PROSPECT",
      subject: "Nexavenu",
      object: "Synthetic LiftOps Manufacturing",
      status: "Active",
      confidencePercent: "83%",
      sourceEventId: "event-nexavenu-lead-source-captured",
      evidenceSummary:
        "Lead source and ICP evidence make the account promising but not yet discovery-ready.",
      correctionState: "Current"
    },
    {
      id: "history-nexavenu-champion-001",
      type: "INFLUENCES_DEAL",
      subject: "Operations manager",
      object: "Synthetic LiftOps Manufacturing",
      status: "Emerging champion",
      confidencePercent: "76%",
      sourceEventId: "event-nexavenu-buying-committee-mapped",
      evidenceSummary:
        "Champion map identifies influence but still lacks CFO, CIO, sponsor, and data-owner confirmation.",
      correctionState: "Needs human confirmation"
    }
  ],
  identityLinks: [
    {
      id: "participant-nexavenu-account-001",
      role: "ACCOUNT",
      entity: "Synthetic LiftOps Manufacturing",
      sourceEventId: "event-nexavenu-lead-source-captured",
      evidenceSummary: "Prospect account participated in the attribution event."
    },
    {
      id: "participant-nexavenu-champion-001",
      role: "CHAMPION",
      entity: "Operations manager",
      sourceEventId: "event-nexavenu-buying-committee-mapped",
      evidenceSummary:
        "Champion role is inferred from buying-committee mapping and should be confirmed."
    }
  ],
  relationshipContradictions: [
    {
      id: "contradiction-readiness-handoff-001",
      claim: "ICP score indicates the account is worth working.",
      counterclaim:
        "Discovery readiness is 48/100, so senior solution-consultant handoff should wait.",
      resolution:
        "Keep the prospect in nurture, equip the champion, and only supersede HOLD after readiness evidence improves."
    }
  ],
  correctionActions: [
    {
      id: "correction-champion-role-001",
      label: "Request correction review",
      target: "Champion role",
      reason:
        "Ask revenue owner to confirm, correct, or supersede the inferred champion before outreach.",
      sourceEventId: "event-nexavenu-buying-committee-mapped"
    }
  ],
  connectedEntities: [
    {
      id: "ORG-NEXAVENU",
      label: "Nexavenu",
      type: "Partner business",
      role: "Revenue team"
    },
    {
      id: "PROSPECT-SYNTH-LIFTOPS",
      label: "Synthetic LiftOps Manufacturing",
      type: "Prospect",
      role: "AI/MuleSoft opportunity"
    },
    {
      id: "ROLE-OPS-CHAMPION",
      label: "Operations manager",
      type: "Champion",
      role: "Likely internal champion"
    },
    {
      id: "ROLE-CFO-CIO",
      label: "CFO and CIO",
      type: "Buying committee",
      role: "Economic and technical buyers"
    }
  ],
  blockers: [
    {
      id: "blocker-revenue-approval-001",
      label: "Revenue owner approval for external champion actions",
      owner: "Revenue Owner",
      status: "Ready for decision",
      dueAt: "2026-06-10T09:30:00Z"
    },
    {
      id: "blocker-readiness-001",
      label: "Readiness score must reach 70 before consultant handoff",
      owner: "BDR",
      status: "Blocked",
      dueAt: "2026-06-10T12:00:00Z"
    }
  ],
  timeline: [
    {
      id: "timeline-lead-source",
      occurredAt: "2026-06-10T08:00:00Z",
      type: "Lead source",
      title: "Attribution captured",
      detail:
        "Webinar, LinkedIn outbound, and MuleSoft landing-page touches linked.",
      source: "Revenue fixture"
    },
    {
      id: "timeline-education",
      occurredAt: "2026-06-10T08:10:00Z",
      type: "Education",
      title: "Buyer education gaps detected",
      detail:
        "System inventory, decision owner, budget, and success metric are missing.",
      source: "Agentforce revenue agent"
    },
    {
      id: "timeline-committee",
      occurredAt: "2026-06-10T08:20:00Z",
      type: "Champion map",
      title: "Buying committee mapped",
      detail:
        "Operations champion exists; CFO, CIO, executive sponsor, and data owner need alignment.",
      source: "Relationship intelligence"
    },
    {
      id: "timeline-readiness",
      occurredAt: "2026-06-10T08:30:00Z",
      type: "Readiness",
      title: "Discovery gate held",
      detail: "Readiness score is 48/100, below handoff threshold.",
      source: "SOP gate"
    },
    {
      id: "timeline-approval",
      occurredAt: "2026-06-10T08:40:00Z",
      type: "Approval",
      title: "Revenue actions proposed",
      detail:
        "Protected outreach and stage updates require revenue-owner approval.",
      source: "Nexavenu revenue orchestrator"
    }
  ],
  evidence: [
    {
      id: "evidence-nexavenu-lead-source-001",
      label: "Lead source and ICP",
      summary:
        "ICP score 72/100 from industry fit, integration complexity, executive intent, data readiness, and budget signal.",
      sourceUri: "urn:hfs:source:nexavenu:revenue:lead-source",
      capturedAt: "2026-06-10T08:00:00Z",
      contentHash:
        "sha256:15ec846204c98c2dcd963a904d85633b5b0ad3bb7b8d44e4b0582ac3f592f4d9"
    },
    {
      id: "evidence-nexavenu-education-gap-001",
      label: "Buyer education gaps",
      summary:
        "Missing system inventory, decision owner, budget range, and AI-to-process translation.",
      sourceUri: "urn:hfs:source:nexavenu:revenue:buyer-education",
      capturedAt: "2026-06-10T08:10:00Z",
      contentHash:
        "sha256:a79d23357b2e5c0e5f11b9a5f4ea65cffd02971e8229b107896bc55d5672ed3d"
    },
    {
      id: "evidence-nexavenu-buying-committee-001",
      label: "Champion map",
      summary:
        "Operations manager is likely champion; CFO and CIO are high-influence buyers; executive sponsor and data owner are missing.",
      sourceUri: "urn:hfs:source:nexavenu:revenue:buying-committee",
      capturedAt: "2026-06-10T08:20:00Z",
      contentHash:
        "sha256:5c81292ae1d9a73de4219c06a230a31cd3a7d08e0477095edb1b49241dcd46a5"
    },
    {
      id: "evidence-nexavenu-readiness-001",
      label: "Discovery readiness",
      summary:
        "Readiness score is 48/100 and handoff gate is HOLD until buyer gaps are resolved.",
      sourceUri: "urn:hfs:source:nexavenu:revenue:discovery-readiness",
      capturedAt: "2026-06-10T08:30:00Z",
      contentHash:
        "sha256:45ffe60a85a761be8db5fae6ca1858ad7ae8786770b100ffb4ef9121ac3bcfe5"
    }
  ],
  sop: {
    name: "Nexavenu revenue qualification",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await revenue-owner approval",
    completedSteps: 2,
    totalSteps: 5,
    progress: 40,
    requiredEvidence:
      "Approved nurture actions, champion response, and readiness score"
  },
  recommendation: {
    id: "recommendation-nexavenu-revenue-001",
    status: "Pending approval",
    title: "Approve champion nurture actions",
    recommendation:
      "Keep the lead in nurture until readiness crosses 70, send readiness and MuleSoft education content, equip the operations champion, request system inventory and success metrics, then schedule CFO/CIO alignment.",
    facts: [
      "ICP score is 72/100.",
      "Buyer education gaps remain unresolved.",
      "Operations manager is likely champion.",
      "Discovery readiness is 48/100 with handoff gate HOLD."
    ],
    assumptions: [
      "Contact-sourced signal suggests lead quality and buyer education need stronger system support.",
      "Contact-sourced signal suggests discovery should be compressed through readiness gates."
    ],
    inferences: [
      "The lead is promising but not solution-consultant-ready.",
      "Champion enablement should precede CFO/CIO alignment."
    ],
    confidence: 0.83,
    confidencePercent: "83%",
    modelProfile: "nexavenu-revenue-recommendation",
    modelProfileVersion: "1.0.0",
    policyVersion: "nexavenu-revenue-routing-mauritius 1.0.0",
    evidenceIds: [
      "evidence-nexavenu-lead-source-001",
      "evidence-nexavenu-education-gap-001",
      "evidence-nexavenu-buying-committee-001",
      "evidence-nexavenu-readiness-001"
    ],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-nexavenu-revenue-001",
    status: "Pending",
    policy: "Revenue owner approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-10T08:40:00Z",
    requestedBy: "Nexavenu Revenue Orchestrator",
    decisionDueAt: "2026-06-10T09:30:00Z"
  },
  actions: [
    {
      id: "action-nexavenu-nurture-001",
      type: "CREATE_NURTURE_TASK",
      status: "Pending approval",
      requestedAt: "2026-06-10T08:40:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft revenue mock",
      correlationId: "30000000-0000-4000-8000-000000000001"
    },
    {
      id: "action-nexavenu-email-001",
      type: "DRAFT_CHAMPION_EMAIL",
      status: "Pending approval",
      requestedAt: "2026-06-10T08:40:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft revenue mock",
      correlationId: "30000000-0000-4000-8000-000000000001"
    }
  ],
  channelLog: [
    {
      id: "channel-revenue-email-001",
      channel: "Champion email",
      status: "DRAFT_ONLY",
      target: "Operations manager",
      detail: "Draft requires revenue-owner approval before send."
    },
    {
      id: "channel-content-001",
      channel: "Content assignment",
      status: "QUEUED",
      target: "Prospect account",
      detail: "AI readiness checklist and MuleSoft explainer queued."
    }
  ],
  outcomeMetrics: [
    { id: "outcome-readiness", label: "Readiness target", value: "70+" },
    { id: "outcome-champion", label: "Champion equipped", value: "Pending" },
    { id: "outcome-cfo-cio", label: "CFO/CIO alignment", value: "Pending" },
    { id: "outcome-handoff", label: "Consultant handoff", value: "Held" },
    { id: "outcome-retention", label: "Retention review", value: "Created" },
    { id: "outcome-feedback", label: "Feedback loop", value: "Open" }
  ],
  outcome: {
    status: "Awaiting approved nurture action",
    summary:
      "Outcome metrics are projected until revenue-owner approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  },
  operatingLayer: operatingLayer({
    kpis: [
      {
        id: "kpi-nex-readiness",
        label: "Discovery readiness",
        value: "48/100",
        prediction:
          "Predicted to reach 76 after champion assets and system inventory",
        predictionPercent: 76,
        confidence: "83%",
        delta: "+28 forecast",
        status: "Hold"
      },
      {
        id: "kpi-nex-champion",
        label: "Champion strength",
        value: "Emerging",
        prediction:
          "Predicted champion strength improves after education sequence",
        predictionPercent: 69,
        confidence: "76%",
        delta: "Needs proof",
        status: "Build"
      },
      {
        id: "kpi-nex-handoff",
        label: "Consultant handoff",
        value: "Blocked",
        prediction: "Predicted handoff clears after readiness crosses 70",
        predictionPercent: 63,
        confidence: "78%",
        delta: "Gate at 70",
        status: "Blocked"
      }
    ],
    trendTitle: "Revenue qualification forecast",
    trend: [
      { id: "nex-trend-1", label: "Lead", actual: 72, predicted: 78 },
      { id: "nex-trend-2", label: "Educate", actual: 35, predicted: 74 },
      { id: "nex-trend-3", label: "Champion", actual: 48, predicted: 69 },
      { id: "nex-trend-4", label: "Close", actual: 31, predicted: 58 }
    ],
    brief: [
      "Keep the opportunity in nurture until readiness crosses the handoff threshold.",
      "Give the champion proof assets before asking for CFO/CIO alignment.",
      "Do not spend senior solution-consultant time until buyer gaps are closed."
    ],
    agents: [
      {
        id: "agent-nex-orchestrator",
        name: "Revenue Orchestrator",
        status: "Holding handoff",
        lastMessage:
          "Readiness is below threshold; I recommend nurture before consultant involvement."
      },
      {
        id: "agent-nex-champion",
        name: "Champion Mapping Agent",
        status: "Needs confirmation",
        lastMessage:
          "Operations manager looks influential, but CFO/CIO and data owner are unconfirmed."
      },
      {
        id: "agent-nex-content",
        name: "Buyer Education Agent",
        status: "Assigning assets",
        lastMessage:
          "AI readiness checklist and MuleSoft explainer are the next best assets."
      }
    ],
    channels: [
      {
        id: "dept-nex-sales",
        name: "Sales",
        owner: "Revenue Owner",
        unread: 4,
        lastMessage: "Handoff remains blocked until readiness is 70+."
      },
      {
        id: "dept-nex-marketing",
        name: "Marketing",
        owner: "Content Owner",
        unread: 2,
        lastMessage: "Education assets are queued for champion enablement."
      }
    ]
  })
};

function buildTerrainCaseState(overrides) {
  return {
    ...nexavenuCaseState,
    ...overrides,
    owner: {
      ...nexavenuCaseState.owner,
      ...(overrides.owner || {})
    },
    relationshipContext: {
      ...nexavenuCaseState.relationshipContext,
      ...(overrides.relationshipContext || {})
    }
  };
}

const airMauritiusCaseState = buildTerrainCaseState({
  id: "work-air-mauritius-passenger-001",
  externalKey: "CORR-AIR-MAURITIUS-PASSENGER-RECOVERY-001",
  title: "Air Mauritius passenger recovery tower",
  summary:
    "Synthetic disrupted passenger needs claims triage, baggage follow-up, compensation review, and governed passenger updates.",
  owner: {
    name: "Passenger Recovery Lead",
    role: "Claims and service recovery approval",
    since: "2026-06-10T08:20:00Z"
  },
  serviceDeadline: "2026-06-10T11:30:00Z",
  nextUpdateDue: "2026-06-10T09:05:00Z",
  relationshipContext: {
    store: "Passenger MRU-REC-1842",
    product: "Delayed baggage and disruption claim",
    category: "Airline passenger recovery",
    batch: "Flight MK-SYN-482",
    supplier: "Claims, ground ops, loyalty",
    promotion: "Service recovery window",
    resourceArea: "Passenger recovery desk"
  },
  stock: [
    { id: "air-claim", label: "Claim", value: "Open" },
    { id: "air-bag", label: "Baggage", value: "Tracing" },
    { id: "air-comp", label: "Compensation", value: "Review" },
    { id: "air-update", label: "Passenger update", value: "Due 09:05" }
  ],
  riskPulses: [
    { id: "air-risk-sla", label: "SLA", status: "At risk" },
    { id: "air-risk-baggage", label: "Baggage trace", status: "Open" },
    { id: "air-risk-comp", label: "Compensation", status: "Needs approval" },
    { id: "air-risk-loyalty", label: "Loyalty", status: "Protect" },
    { id: "air-risk-message", label: "Passenger message", status: "Draft" },
    { id: "air-risk-feedback", label: "Feedback loop", status: "Open" }
  ],
  complaintCluster: {
    type: "Delayed bag, missed connection, refund expectation",
    count: 3,
    product: "Delayed baggage and disruption claim",
    batch: "Flight MK-SYN-482",
    supplier: "Passenger Recovery Lead",
    window: "Post-arrival recovery"
  },
  partnerResponse: {
    status: "Claims review required",
    leadTime: "2h SLA",
    replacement: "Send grounded update and baggage tracing task",
    creditNote: "Compensation eligibility review",
    qualityIssue: "Do not promise payout before approval"
  },
  operationsExecution: {
    primaryRecommendation:
      "Coordinate claims, baggage trace, and passenger update before SLA breach.",
    tasks: [
      {
        id: "air-task-claims",
        label: "Create claims triage task",
        owner: "Claims Desk",
        status: "Queued"
      },
      {
        id: "air-task-baggage",
        label: "Request baggage trace update",
        owner: "Ground Ops",
        status: "In progress"
      },
      {
        id: "air-task-message",
        label: "Draft passenger update",
        owner: "Passenger Recovery Lead",
        status: "Needs approval"
      }
    ]
  },
  affectedRelationship: {
    label: "Passenger relationship",
    subject: "Air Mauritius",
    object: "Passenger MRU-REC-1842",
    type: "RECOVERS_PASSENGER",
    status: "Active recovery"
  },
  relationshipHistory: [
    {
      id: "air-history-passenger-001",
      type: "RECOVERS_PASSENGER",
      subject: "Air Mauritius",
      object: "Passenger MRU-REC-1842",
      status: "Active recovery",
      confidencePercent: "88%",
      sourceEventId: "event-air-disruption-linked",
      evidenceSummary:
        "Passenger, flight disruption, baggage trace, and claim records link to one recovery case.",
      correctionState: "Current"
    }
  ],
  identityLinks: [
    {
      id: "air-participant-passenger-001",
      role: "PASSENGER",
      entity: "Passenger MRU-REC-1842",
      sourceEventId: "event-air-disruption-linked",
      evidenceSummary:
        "Passenger participated in disruption, baggage, and claims records."
    }
  ],
  relationshipContradictions: [
    {
      id: "air-contradiction-compensation-001",
      claim: "Passenger expects compensation immediately.",
      counterclaim:
        "Claims policy requires baggage trace and disruption evidence before payout.",
      resolution:
        "Send empathetic status update now; hold payout until claims approval."
    }
  ],
  correctionActions: [
    {
      id: "air-correction-claim-scope-001",
      label: "Request correction review",
      target: "Claim scope",
      reason:
        "Ask recovery owner to confirm whether disruption and baggage claims should be merged.",
      sourceEventId: "event-air-disruption-linked"
    }
  ],
  connectedEntities: [
    {
      id: "AIR-PASSENGER-001",
      label: "Passenger MRU-REC-1842",
      type: "Passenger",
      role: "Recovery subject"
    },
    {
      id: "AIR-FLIGHT-001",
      label: "Flight MK-SYN-482",
      type: "Flight",
      role: "Disruption source"
    },
    {
      id: "AIR-BAG-001",
      label: "Baggage trace",
      type: "Claim artifact",
      role: "Resolution dependency"
    }
  ],
  blockers: [
    {
      id: "air-blocker-approval-001",
      label: "Recovery lead approval before passenger update",
      owner: "Passenger Recovery Lead",
      status: "Ready for decision",
      dueAt: "2026-06-10T09:05:00Z"
    }
  ],
  timeline: [
    {
      id: "air-timeline-disruption",
      occurredAt: "2026-06-10T08:00:00Z",
      type: "Disruption",
      title: "Passenger disruption linked",
      detail:
        "Flight, baggage, claim, and loyalty context merged into one recovery case.",
      source: "Airline fixture"
    },
    {
      id: "air-timeline-baggage",
      occurredAt: "2026-06-10T08:12:00Z",
      type: "Baggage",
      title: "Baggage trace still open",
      detail: "Ground ops update is needed before final passenger resolution.",
      source: "Baggage mock"
    },
    {
      id: "air-timeline-approval",
      occurredAt: "2026-06-10T08:20:00Z",
      type: "Approval",
      title: "Passenger update requested",
      detail:
        "Outbound update and compensation review require recovery-owner approval.",
      source: "Passenger recovery orchestrator"
    }
  ],
  evidence: [
    {
      id: "air-evidence-disruption-001",
      label: "Disruption record",
      summary:
        "Synthetic flight disruption, baggage trace, and claim evidence are linked by passenger and flight.",
      sourceUri: "urn:hfs:source:air-mauritius:disruption",
      capturedAt: "2026-06-10T08:00:00Z",
      contentHash:
        "sha256:58593426cb653f0971127114c0c6a529cda9a81c738ed177e1a2fabf3d8f24df"
    },
    {
      id: "air-evidence-claim-001",
      label: "Claim policy",
      summary:
        "Compensation recommendation is policy-gated until claim evidence is complete.",
      sourceUri: "urn:hfs:source:air-mauritius:claims",
      capturedAt: "2026-06-10T08:18:00Z",
      contentHash:
        "sha256:a6a9e9fffe1b57aa9079bb6a05f0703b85f73f014a010c98c3c9a204d58d9a91"
    }
  ],
  sop: {
    name: "Airline passenger recovery",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await recovery-owner approval",
    completedSteps: 2,
    totalSteps: 5,
    progress: 40,
    requiredEvidence:
      "Disruption record, baggage trace, compensation policy, and passenger update"
  },
  recommendation: {
    id: "recommendation-air-mauritius-001",
    status: "Pending approval",
    title: "Approve passenger recovery actions",
    recommendation:
      "Send a grounded passenger update, create baggage trace escalation, start claims review, and defer compensation promise until eligibility evidence is complete.",
    facts: [
      "Passenger disruption and baggage trace records are linked.",
      "Passenger update SLA is approaching.",
      "Compensation requires claims policy review."
    ],
    assumptions: [
      "Passenger churn or complaint risk rises if no proactive update is sent."
    ],
    inferences: [
      "The safest immediate action is status transparency plus claims triage.",
      "Payout language should be avoided before eligibility approval."
    ],
    confidence: 0.84,
    confidencePercent: "84%",
    modelProfile: "air-mauritius-passenger-recovery",
    modelProfileVersion: "1.0.0",
    policyVersion: "air-mauritius-recovery-routing-mauritius 1.0.0",
    evidenceIds: ["air-evidence-disruption-001", "air-evidence-claim-001"],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-air-mauritius-001",
    status: "Pending",
    policy: "Passenger recovery approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-10T08:20:00Z",
    requestedBy: "Passenger Recovery Orchestrator",
    decisionDueAt: "2026-06-10T09:05:00Z"
  },
  actions: [
    {
      id: "air-action-passenger-update-001",
      type: "DRAFT_PASSENGER_UPDATE",
      status: "Pending approval",
      requestedAt: "2026-06-10T08:20:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft airline mock",
      correlationId: "40000000-0000-4000-8000-000000000001"
    }
  ],
  channelLog: [
    {
      id: "air-channel-message-001",
      channel: "Passenger message",
      status: "DRAFT_ONLY",
      target: "Passenger MRU-REC-1842",
      detail: "Draft requires recovery-owner approval before send."
    }
  ],
  outcomeMetrics: [
    { id: "air-outcome-sla", label: "SLA protection", value: "09:05 due" },
    { id: "air-outcome-claim", label: "Claim triage", value: "Started" },
    { id: "air-outcome-bag", label: "Baggage trace", value: "Escalated" },
    { id: "air-outcome-feedback", label: "Feedback loop", value: "Open" }
  ],
  outcome: {
    status: "Awaiting approved passenger recovery",
    summary:
      "Outcome metrics are projected until recovery-owner approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  },
  operatingLayer: operatingLayer({
    kpis: [
      {
        id: "kpi-air-sla",
        label: "Passenger SLA risk",
        value: "09:05",
        prediction:
          "Predicted SLA recovery if update and baggage trace are approved",
        predictionPercent: 82,
        confidence: "84%",
        delta: "Protect now",
        status: "At risk"
      },
      {
        id: "kpi-air-claim",
        label: "Claim resolution",
        value: "Open",
        prediction: "Predicted claim cycle shortens after evidence merge",
        predictionPercent: 64,
        confidence: "77%",
        delta: "Triage",
        status: "Review"
      },
      {
        id: "kpi-air-loyalty",
        label: "Loyalty protection",
        value: "Watch",
        prediction:
          "Predicted complaint risk drops after proactive grounded update",
        predictionPercent: 71,
        confidence: "73%",
        delta: "Message due",
        status: "Protect"
      }
    ],
    trendTitle: "Passenger recovery forecast",
    trend: [
      { id: "air-trend-1", label: "SLA", actual: 38, predicted: 82 },
      { id: "air-trend-2", label: "Bags", actual: 44, predicted: 68 },
      { id: "air-trend-3", label: "Claim", actual: 35, predicted: 64 },
      { id: "air-trend-4", label: "Loyalty", actual: 51, predicted: 71 }
    ],
    brief: [
      "Send an approved passenger update before the next SLA checkpoint.",
      "Escalate baggage tracing and merge the claim evidence into one recovery case.",
      "Avoid compensation promises until eligibility evidence is approved."
    ],
    agents: [
      {
        id: "agent-air-recovery",
        name: "Passenger Recovery Agent",
        status: "Drafting update",
        lastMessage:
          "I can draft the passenger update, but compensation language must remain conditional."
      },
      {
        id: "agent-air-baggage",
        name: "Baggage Trace Agent",
        status: "Escalating",
        lastMessage:
          "Ground ops needs to confirm the latest baggage trace before final resolution."
      }
    ],
    channels: [
      {
        id: "dept-air-claims",
        name: "Claims",
        owner: "Claims Desk",
        unread: 2,
        lastMessage:
          "Eligibility review can start after baggage evidence merges."
      },
      {
        id: "dept-air-ground",
        name: "Ground Ops",
        owner: "Baggage Team",
        unread: 1,
        lastMessage: "Baggage trace update is requested before 09:05."
      }
    ]
  })
});

const constanceHospitalityCaseState = buildTerrainCaseState({
  id: "work-constance-hospitality-001",
  externalKey: "CORR-CONSTANCE-GUEST-REVENUE-OPS-001",
  title: "Constance guest revenue and operations loop",
  summary:
    "Synthetic reservations and guest sentiment signals need booking-list extraction, FX sync, occupancy forecast, and governed guest actions.",
  owner: {
    name: "Revenue Operations Lead",
    role: "Hospitality approval",
    since: "2026-06-10T08:25:00Z"
  },
  relationshipContext: {
    store: "Constance synthetic property",
    product: "Reservations and occupancy recovery",
    category: "Hospitality revenue operations",
    batch: "Stay window: next 14 days",
    supplier: "Reservations, finance, guest experience",
    promotion: "Direct booking recovery",
    resourceArea: "Revenue operations workspace"
  },
  stock: [
    { id: "con-bookings", label: "Bookings", value: "Extract pending" },
    { id: "con-fx", label: "FX", value: "ERP sync due" },
    { id: "con-sentiment", label: "Sentiment", value: "Occupancy signal" },
    { id: "con-actions", label: "Guest actions", value: "Needs approval" }
  ],
  riskPulses: [
    {
      id: "con-risk-mailbox",
      label: "Reservations inbox",
      status: "Unstructured"
    },
    { id: "con-risk-fx", label: "FX sync", status: "Due" },
    { id: "con-risk-occupancy", label: "Occupancy", status: "Forecast risk" },
    { id: "con-risk-message", label: "Guest message", status: "Draft" },
    { id: "con-risk-feedback", label: "Feedback loop", status: "Open" }
  ],
  complaintCluster: {
    type: "New booking, amend booking, availability, sentiment",
    count: 24,
    supplier: "Revenue Operations Lead",
    window: "Next 14 days"
  },
  partnerResponse: {
    status: "Revenue response required",
    leadTime: "FX pending",
    replacement: "Extract booking list and update ERP",
    creditNote: "Occupancy forecast proof",
    qualityIssue: "Sentiment model needs internal data confidence"
  },
  operationsExecution: {
    primaryRecommendation:
      "Extract reservations from mailbox, sync FX, forecast occupancy, then approve guest/revenue actions.",
    tasks: [
      {
        id: "con-task-mailbox",
        label: "Extract reservations mailbox",
        owner: "Reservations",
        status: "Queued"
      },
      {
        id: "con-task-fx",
        label: "Sync daily exchange rate to ERP",
        owner: "Finance Ops",
        status: "Queued"
      },
      {
        id: "con-task-sentiment",
        label: "Review sentiment occupancy forecast",
        owner: "Revenue Ops",
        status: "Needs approval"
      }
    ]
  },
  affectedRelationship: {
    label: "Guest revenue relationship",
    subject: "Constance synthetic property",
    object: "Reservations and occupancy recovery",
    type: "RECOVERS_GUEST_REVENUE",
    status: "Active"
  },
  relationshipHistory: [
    {
      id: "con-history-reservation-001",
      type: "RECOVERS_GUEST_REVENUE",
      subject: "Constance synthetic property",
      object: "Stay window: next 14 days",
      status: "Active",
      confidencePercent: "82%",
      sourceEventId: "event-constance-reservations-linked",
      evidenceSummary:
        "Reservations, FX, and sentiment signals are linked to the same occupancy recovery window.",
      correctionState: "Current"
    }
  ],
  identityLinks: [
    {
      id: "con-participant-property-001",
      role: "PROPERTY",
      entity: "Constance synthetic property",
      sourceEventId: "event-constance-reservations-linked",
      evidenceSummary:
        "Property participated in reservations, FX, and occupancy evidence."
    }
  ],
  relationshipContradictions: [
    {
      id: "con-contradiction-occupancy-001",
      claim: "Sentiment predicts occupancy pressure.",
      counterclaim:
        "Reservations mailbox and ERP FX state are not yet fully structured.",
      resolution:
        "Treat sentiment as forecast support, not source truth, until booking extraction and ERP sync complete."
    }
  ],
  correctionActions: [
    {
      id: "con-correction-booking-class-001",
      label: "Request correction review",
      target: "Booking classification",
      reason:
        "Ask revenue owner to review mailbox classification before ERP write-back.",
      sourceEventId: "event-constance-reservations-linked"
    }
  ],
  connectedEntities: [
    {
      id: "CON-PROPERTY-001",
      label: "Constance synthetic property",
      type: "Property",
      role: "Revenue focus"
    },
    {
      id: "CON-MAILBOX-001",
      label: "Reservations mailbox",
      type: "Source",
      role: "Unstructured booking feed"
    },
    {
      id: "CON-ERP-001",
      label: "ERP FX update",
      type: "Finance system",
      role: "Revenue dependency"
    }
  ],
  blockers: [
    {
      id: "con-blocker-approval-001",
      label: "Revenue owner approval before ERP and guest actions",
      owner: "Revenue Operations Lead",
      status: "Ready for decision",
      dueAt: "2026-06-10T10:00:00Z"
    }
  ],
  timeline: [
    {
      id: "con-timeline-mailbox",
      occurredAt: "2026-06-10T08:05:00Z",
      type: "Reservations",
      title: "Mailbox extraction requested",
      detail:
        "New booking, amendment, availability, and miscellaneous emails classified.",
      source: "Hospitality fixture"
    },
    {
      id: "con-timeline-fx",
      occurredAt: "2026-06-10T08:15:00Z",
      type: "FX",
      title: "Daily FX sync due",
      detail: "ERP update is ready after public bank rate extraction.",
      source: "FX mock"
    },
    {
      id: "con-timeline-approval",
      occurredAt: "2026-06-10T08:25:00Z",
      type: "Approval",
      title: "Revenue actions proposed",
      detail: "Guest and ERP actions require revenue-owner approval.",
      source: "Hospitality orchestrator"
    }
  ],
  evidence: [
    {
      id: "con-evidence-mailbox-001",
      label: "Reservations mailbox",
      summary:
        "Synthetic mailbox extraction produced structured booking and amendment candidates.",
      sourceUri: "urn:hfs:source:constance:reservations",
      capturedAt: "2026-06-10T08:05:00Z",
      contentHash:
        "sha256:8c51bfb7f4f12d696d096e8f7287dc8fae86cd52618a8728e4f6e917f56031e6"
    },
    {
      id: "con-evidence-fx-001",
      label: "FX extraction",
      summary:
        "Daily exchange-rate fixture is ready for ERP API load after approval.",
      sourceUri: "urn:hfs:source:constance:fx",
      capturedAt: "2026-06-10T08:15:00Z",
      contentHash:
        "sha256:6cfd20ac4b9a62fdd1fc71c248e7062666fcbf4f94192cfaa5eba592a4cf36d4"
    }
  ],
  sop: {
    name: "Hospitality revenue recovery",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await revenue-owner approval",
    completedSteps: 2,
    totalSteps: 5,
    progress: 40,
    requiredEvidence:
      "Booking extraction, FX source, sentiment confidence, and approved action"
  },
  recommendation: {
    id: "recommendation-constance-001",
    status: "Pending approval",
    title: "Approve guest revenue actions",
    recommendation:
      "Approve booking extraction review, sync daily FX into ERP, use sentiment only as forecast support, and queue guest recovery outreach for reservations at risk.",
    facts: [
      "Reservations mailbox contains new booking and amendment candidates.",
      "Daily FX update is ready for ERP write-back.",
      "Sentiment-to-occupancy forecast needs internal-data confidence."
    ],
    assumptions: [
      "Fast booking structuring reduces missed revenue and manual reservation work."
    ],
    inferences: [
      "ERP write-back should wait for human approval.",
      "Sentiment is useful for prioritization, not enough alone for occupancy truth."
    ],
    confidence: 0.81,
    confidencePercent: "81%",
    modelProfile: "constance-hospitality-revenue",
    modelProfileVersion: "1.0.0",
    policyVersion: "constance-hospitality-routing-mauritius 1.0.0",
    evidenceIds: ["con-evidence-mailbox-001", "con-evidence-fx-001"],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-constance-001",
    status: "Pending",
    policy: "Hospitality revenue approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-10T08:25:00Z",
    requestedBy: "Hospitality Revenue Orchestrator",
    decisionDueAt: "2026-06-10T10:00:00Z"
  },
  actions: [
    {
      id: "con-action-erp-fx-001",
      type: "ERP_FX_WRITEBACK",
      status: "Pending approval",
      requestedAt: "2026-06-10T08:25:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft hospitality mock",
      correlationId: "50000000-0000-4000-8000-000000000001"
    }
  ],
  channelLog: [
    {
      id: "con-channel-reservation-001",
      channel: "Reservations task",
      status: "QUEUED",
      target: "Reservations",
      detail: "Booking-review task queued; ERP write-back is approval-gated."
    }
  ],
  outcomeMetrics: [
    { id: "con-outcome-bookings", label: "Bookings structured", value: "24" },
    { id: "con-outcome-fx", label: "FX sync", value: "Pending approval" },
    { id: "con-outcome-occupancy", label: "Occupancy risk", value: "Watch" },
    { id: "con-outcome-feedback", label: "Feedback loop", value: "Open" }
  ],
  outcome: {
    status: "Awaiting approved hospitality action",
    summary:
      "Outcome metrics are projected until revenue-owner approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  },
  operatingLayer: operatingLayer({
    kpis: [
      {
        id: "kpi-con-booking",
        label: "Bookings structured",
        value: "24",
        prediction:
          "Predicted manual reservation backlog drops after extraction",
        predictionPercent: 79,
        confidence: "81%",
        delta: "Queue clear",
        status: "Action"
      },
      {
        id: "kpi-con-occupancy",
        label: "Occupancy risk",
        value: "Watch",
        prediction:
          "Predicted occupancy forecast improves after sentiment validation",
        predictionPercent: 68,
        confidence: "74%",
        delta: "Validate",
        status: "Forecast"
      },
      {
        id: "kpi-con-fx",
        label: "FX to ERP",
        value: "Due",
        prediction:
          "Predicted revenue variance reduces after approved ERP FX sync",
        predictionPercent: 73,
        confidence: "80%",
        delta: "Sync",
        status: "Pending"
      }
    ],
    trendTitle: "Guest revenue forecast",
    trend: [
      { id: "con-trend-1", label: "Bookings", actual: 46, predicted: 79 },
      { id: "con-trend-2", label: "FX", actual: 42, predicted: 73 },
      { id: "con-trend-3", label: "Sentiment", actual: 51, predicted: 68 },
      { id: "con-trend-4", label: "Occupancy", actual: 57, predicted: 75 }
    ],
    brief: [
      "Approve reservation extraction review before ERP updates are posted.",
      "Sync daily FX only after source check and revenue-owner approval.",
      "Use sentiment as a prioritization signal, not as source truth."
    ],
    agents: [
      {
        id: "agent-con-reservations",
        name: "Reservations Extraction Agent",
        status: "Classifying",
        lastMessage:
          "New, amended, availability, and miscellaneous emails are structured for review."
      },
      {
        id: "agent-con-revenue",
        name: "Revenue Forecast Agent",
        status: "Forecasting",
        lastMessage:
          "Occupancy prediction improves once reservations and FX are approved."
      }
    ],
    channels: [
      {
        id: "dept-con-reservations",
        name: "Reservations",
        owner: "Reservations Lead",
        unread: 3,
        lastMessage: "Booking classifications are ready for review."
      },
      {
        id: "dept-con-finance",
        name: "Finance Ops",
        owner: "Finance Ops",
        unread: 1,
        lastMessage: "FX sync is waiting on approval."
      }
    ]
  })
});

const afrasiaPrivateBankingCaseState = buildTerrainCaseState({
  id: "work-afrasia-private-banking-001",
  externalKey: "CORR-AFRASIA-RM-INTELLIGENCE-001",
  title: "AfrAsia relationship intelligence control tower",
  summary:
    "Synthetic private-banking relationship needs RM prioritization, KYC guardrails, FX/wealth signal review, and governed next touch.",
  owner: {
    name: "Senior Relationship Manager",
    role: "RM and compliance approval",
    since: "2026-06-10T08:35:00Z"
  },
  relationshipContext: {
    store: "Synthetic cross-border client",
    product: "Private banking RM opportunity",
    category: "Private banking relationship",
    batch: "KYC review window",
    supplier: "RM, compliance, treasury",
    promotion: "Wealth and FX advisory touch",
    resourceArea: "RM workspace"
  },
  stock: [
    { id: "afr-kyc", label: "KYC", value: "Refresh due" },
    { id: "afr-fx", label: "FX signal", value: "High intent" },
    { id: "afr-rm", label: "RM touch", value: "Needs approval" },
    { id: "afr-risk", label: "Compliance", value: "Guarded" }
  ],
  riskPulses: [
    { id: "afr-risk-kyc", label: "KYC", status: "Refresh due" },
    { id: "afr-risk-fx", label: "FX exposure", status: "Opportunity" },
    { id: "afr-risk-cross-border", label: "Cross-border", status: "Review" },
    { id: "afr-risk-message", label: "Client touch", status: "Draft" },
    { id: "afr-risk-feedback", label: "Feedback loop", status: "Open" }
  ],
  complaintCluster: {
    type: "KYC refresh, FX intent, relationship value, next best action",
    count: 4,
    supplier: "Senior Relationship Manager",
    window: "Next 7 days"
  },
  partnerResponse: {
    status: "Compliance gate required",
    leadTime: "KYC refresh due",
    replacement: "RM briefing and client touch draft",
    creditNote: "Potential FX/advisory opportunity",
    qualityIssue: "No product advice before suitability and approval"
  },
  operationsExecution: {
    primaryRecommendation:
      "Prepare RM briefing, refresh KYC, and hold client outreach until compliance-safe approval.",
    tasks: [
      {
        id: "afr-task-kyc",
        label: "Create KYC refresh task",
        owner: "Compliance",
        status: "Queued"
      },
      {
        id: "afr-task-brief",
        label: "Prepare RM relationship brief",
        owner: "Relationship Manager",
        status: "In progress"
      },
      {
        id: "afr-task-touch",
        label: "Draft client touchpoint",
        owner: "Senior Relationship Manager",
        status: "Needs approval"
      }
    ]
  },
  affectedRelationship: {
    label: "Private banking relationship",
    subject: "AfrAsia",
    object: "Synthetic cross-border client",
    type: "MANAGES_CLIENT_RELATIONSHIP",
    status: "Compliance-gated"
  },
  relationshipHistory: [
    {
      id: "afr-history-client-001",
      type: "MANAGES_CLIENT_RELATIONSHIP",
      subject: "AfrAsia",
      object: "Synthetic cross-border client",
      status: "Compliance-gated",
      confidencePercent: "85%",
      sourceEventId: "event-afrasia-relationship-signal",
      evidenceSummary:
        "KYC, FX, product interest, and RM history are linked into one relationship picture.",
      correctionState: "Current"
    }
  ],
  identityLinks: [
    {
      id: "afr-participant-client-001",
      role: "CLIENT",
      entity: "Synthetic cross-border client",
      sourceEventId: "event-afrasia-relationship-signal",
      evidenceSummary:
        "Client participated in KYC, treasury, and RM interaction evidence."
    }
  ],
  relationshipContradictions: [
    {
      id: "afr-contradiction-wealth-signal-001",
      claim: "FX and wealth signals suggest a commercial opportunity.",
      counterclaim:
        "KYC refresh and suitability guardrails block immediate product outreach.",
      resolution:
        "Prepare RM brief and compliance task first; draft client touch only after approval."
    }
  ],
  correctionActions: [
    {
      id: "afr-correction-kyc-scope-001",
      label: "Request correction review",
      target: "KYC scope",
      reason:
        "Ask RM and compliance owner to confirm whether the relationship state is fit for outreach.",
      sourceEventId: "event-afrasia-relationship-signal"
    }
  ],
  connectedEntities: [
    {
      id: "AFR-CLIENT-001",
      label: "Synthetic cross-border client",
      type: "Client",
      role: "Relationship subject"
    },
    {
      id: "AFR-RM-001",
      label: "Senior Relationship Manager",
      type: "RM",
      role: "Action owner"
    },
    {
      id: "AFR-COMPLIANCE-001",
      label: "Compliance review",
      type: "Guardrail",
      role: "Approval dependency"
    }
  ],
  blockers: [
    {
      id: "afr-blocker-compliance-001",
      label: "Compliance approval before client outreach",
      owner: "Compliance",
      status: "Ready for review",
      dueAt: "2026-06-10T11:00:00Z"
    }
  ],
  timeline: [
    {
      id: "afr-timeline-signal",
      occurredAt: "2026-06-10T08:10:00Z",
      type: "RM signal",
      title: "Relationship signal detected",
      detail:
        "KYC refresh, FX intent, and RM history linked to the same client relationship.",
      source: "Banking fixture"
    },
    {
      id: "afr-timeline-approval",
      occurredAt: "2026-06-10T08:35:00Z",
      type: "Approval",
      title: "Compliance-gated RM action proposed",
      detail: "Client touchpoint requires RM and compliance approval.",
      source: "Banking orchestrator"
    }
  ],
  evidence: [
    {
      id: "afr-evidence-relationship-001",
      label: "Relationship signal",
      summary:
        "Synthetic KYC, FX, and RM history indicate a valuable but compliance-gated client touchpoint.",
      sourceUri: "urn:hfs:source:afrasia:relationship",
      capturedAt: "2026-06-10T08:10:00Z",
      contentHash:
        "sha256:c5e620b727ade9d1f4fd13c560c5779502bd9c47fca537f9f4687a7a3eb72ad3"
    }
  ],
  sop: {
    name: "Private banking relationship review",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await RM and compliance approval",
    completedSteps: 2,
    totalSteps: 5,
    progress: 40,
    requiredEvidence:
      "KYC state, RM history, FX signal, suitability guardrail, and approved touchpoint"
  },
  recommendation: {
    id: "recommendation-afrasia-001",
    status: "Pending approval",
    title: "Approve RM relationship actions",
    recommendation:
      "Create KYC refresh task, prepare RM briefing, draft compliance-safe client touchpoint, and defer product-specific advice until suitability evidence is approved.",
    facts: [
      "KYC refresh is due.",
      "FX and wealth signals indicate relationship opportunity.",
      "Client outreach is compliance-gated."
    ],
    assumptions: [
      "RM value improves when compliance context and commercial signals are seen together."
    ],
    inferences: [
      "The next action should be RM preparation, not immediate product push.",
      "Suitability and approval boundaries protect the relationship."
    ],
    confidence: 0.8,
    confidencePercent: "80%",
    modelProfile: "afrasia-private-banking-rm",
    modelProfileVersion: "1.0.0",
    policyVersion: "afrasia-rm-routing-mauritius 1.0.0",
    evidenceIds: ["afr-evidence-relationship-001"],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-afrasia-001",
    status: "Pending",
    policy: "RM and compliance approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-10T08:35:00Z",
    requestedBy: "Banking Relationship Orchestrator",
    decisionDueAt: "2026-06-10T11:00:00Z"
  },
  actions: [
    {
      id: "afr-action-rm-touch-001",
      type: "DRAFT_RM_TOUCHPOINT",
      status: "Pending approval",
      requestedAt: "2026-06-10T08:35:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft banking mock",
      correlationId: "60000000-0000-4000-8000-000000000001"
    }
  ],
  channelLog: [
    {
      id: "afr-channel-rm-task-001",
      channel: "RM task",
      status: "QUEUED",
      target: "Senior Relationship Manager",
      detail: "RM briefing queued; client message remains approval-gated."
    }
  ],
  outcomeMetrics: [
    { id: "afr-outcome-kyc", label: "KYC refresh", value: "Queued" },
    { id: "afr-outcome-rm", label: "RM brief", value: "In progress" },
    { id: "afr-outcome-touch", label: "Client touch", value: "Draft only" },
    { id: "afr-outcome-feedback", label: "Feedback loop", value: "Open" }
  ],
  outcome: {
    status: "Awaiting approved RM action",
    summary:
      "Outcome metrics are projected until RM/compliance approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  },
  operatingLayer: operatingLayer({
    kpis: [
      {
        id: "kpi-afr-kyc",
        label: "KYC readiness",
        value: "Refresh",
        prediction: "Predicted outreach clearance after KYC refresh is opened",
        predictionPercent: 66,
        confidence: "80%",
        delta: "Guarded",
        status: "Due"
      },
      {
        id: "kpi-afr-rm",
        label: "RM opportunity",
        value: "High",
        prediction:
          "Predicted RM value improves with FX signal and relationship brief",
        predictionPercent: 78,
        confidence: "75%",
        delta: "Prepare",
        status: "Opportunity"
      },
      {
        id: "kpi-afr-compliance",
        label: "Compliance risk",
        value: "Gated",
        prediction:
          "Predicted risk stays controlled if product advice is deferred",
        predictionPercent: 84,
        confidence: "82%",
        delta: "No advice yet",
        status: "Gate"
      }
    ],
    trendTitle: "Private banking relationship forecast",
    trend: [
      { id: "afr-trend-1", label: "KYC", actual: 41, predicted: 66 },
      { id: "afr-trend-2", label: "FX", actual: 72, predicted: 78 },
      { id: "afr-trend-3", label: "RM", actual: 58, predicted: 76 },
      { id: "afr-trend-4", label: "Risk", actual: 52, predicted: 84 }
    ],
    brief: [
      "Open KYC refresh before any commercial client touchpoint.",
      "Prepare RM briefing from FX and relationship history signals.",
      "Keep product-specific advice out of drafts until suitability is approved."
    ],
    agents: [
      {
        id: "agent-afr-rm",
        name: "RM Intelligence Agent",
        status: "Preparing brief",
        lastMessage:
          "Client value is high, but outreach should be compliance-safe and advisory-neutral."
      },
      {
        id: "agent-afr-compliance",
        name: "Compliance Gate Agent",
        status: "Checking guardrails",
        lastMessage:
          "KYC refresh and suitability evidence are required before product advice."
      }
    ],
    channels: [
      {
        id: "dept-afr-rm",
        name: "Relationship Managers",
        owner: "Senior RM",
        unread: 2,
        lastMessage: "RM brief is in progress; client touch is draft-only."
      },
      {
        id: "dept-afr-compliance",
        name: "Compliance",
        owner: "Compliance",
        unread: 1,
        lastMessage: "KYC refresh is the blocking checkpoint."
      }
    ]
  })
});

const sunlifeGuestRecoveryCaseState = buildTerrainCaseState({
  id: "work-sunlife-guest-recovery-001",
  externalKey: "CORR-SUNLIFE-GUEST-RECOVERY-001",
  title: "Sunlife guest recovery and experience loop",
  summary:
    "Synthetic guest experience signal needs WhatsApp-style guest recovery, staff task coordination, and repeat-stay risk feedback.",
  owner: {
    name: "Guest Experience Lead",
    role: "Guest recovery approval",
    since: "2026-06-10T08:45:00Z"
  },
  relationshipContext: {
    store: "Synthetic Sunlife resort",
    product: "Guest recovery moment",
    category: "Hospitality guest experience",
    batch: "Stay SUN-SYN-2044",
    supplier: "Guest experience and operations",
    promotion: "Repeat-stay protection",
    resourceArea: "Guest recovery desk"
  },
  stock: [
    { id: "sun-service", label: "Service issue", value: "Open" },
    { id: "sun-staff", label: "Staff task", value: "Queued" },
    { id: "sun-message", label: "Guest message", value: "Draft" },
    { id: "sun-repeat", label: "Repeat-stay risk", value: "Watch" }
  ],
  riskPulses: [
    { id: "sun-risk-service", label: "Service quality", status: "At risk" },
    { id: "sun-risk-staff", label: "Staff coordination", status: "Queued" },
    { id: "sun-risk-message", label: "Guest message", status: "Draft" },
    {
      id: "sun-risk-sustainability",
      label: "Sustainability proof",
      status: "Attach"
    },
    { id: "sun-risk-repeat", label: "Repeat stay", status: "Watch" }
  ],
  complaintCluster: {
    type: "Service delay, room issue, recovery offer, sustainability proof",
    count: 4,
    supplier: "Guest Experience Lead",
    window: "Current stay"
  },
  partnerResponse: {
    status: "Guest recovery required",
    leadTime: "30m SLA",
    replacement: "Staff task and WhatsApp-style recovery draft",
    creditNote: "Recovery offer pending",
    qualityIssue: "Do not send guest message before approval"
  },
  operationsExecution: {
    primaryRecommendation:
      "Coordinate staff task, recovery offer, sustainability evidence, and guest message before the guest checks out.",
    tasks: [
      {
        id: "sun-task-room",
        label: "Create room/service recovery task",
        owner: "Operations",
        status: "Queued"
      },
      {
        id: "sun-task-message",
        label: "Draft WhatsApp-style guest message",
        owner: "Guest Experience",
        status: "Needs approval"
      },
      {
        id: "sun-task-proof",
        label: "Attach sustainability proof",
        owner: "Sustainability Lead",
        status: "Queued"
      }
    ]
  },
  affectedRelationship: {
    label: "Guest relationship",
    subject: "Sunlife synthetic resort",
    object: "Guest SUN-SYN-2044",
    type: "RECOVERS_GUEST_EXPERIENCE",
    status: "Active recovery"
  },
  relationshipHistory: [
    {
      id: "sun-history-guest-001",
      type: "RECOVERS_GUEST_EXPERIENCE",
      subject: "Sunlife synthetic resort",
      object: "Guest SUN-SYN-2044",
      status: "Active recovery",
      confidencePercent: "84%",
      sourceEventId: "event-sunlife-guest-signal",
      evidenceSummary:
        "Guest issue, staff task, recovery offer, and repeat-stay risk are linked to one recovery loop.",
      correctionState: "Current"
    }
  ],
  identityLinks: [
    {
      id: "sun-participant-guest-001",
      role: "GUEST",
      entity: "Guest SUN-SYN-2044",
      sourceEventId: "event-sunlife-guest-signal",
      evidenceSummary:
        "Guest participated in service, stay, and recovery evidence."
    }
  ],
  relationshipContradictions: [
    {
      id: "sun-contradiction-recovery-001",
      claim: "Immediate apology message reduces dissatisfaction.",
      counterclaim:
        "Guest promise should be tied to staff task and approved recovery offer.",
      resolution:
        "Draft message now; send only after staff task and offer approval."
    }
  ],
  correctionActions: [
    {
      id: "sun-correction-recovery-offer-001",
      label: "Request correction review",
      target: "Recovery offer",
      reason:
        "Ask experience owner to confirm the recovery offer before guest outreach.",
      sourceEventId: "event-sunlife-guest-signal"
    }
  ],
  connectedEntities: [
    {
      id: "SUN-GUEST-001",
      label: "Guest SUN-SYN-2044",
      type: "Guest",
      role: "Recovery subject"
    },
    {
      id: "SUN-OPS-001",
      label: "Operations task",
      type: "Staff task",
      role: "Resolution dependency"
    },
    {
      id: "SUN-GX-001",
      label: "Guest Experience Lead",
      type: "Approver",
      role: "Human control"
    }
  ],
  blockers: [
    {
      id: "sun-blocker-approval-001",
      label: "Guest experience approval before outbound message",
      owner: "Guest Experience Lead",
      status: "Ready for decision",
      dueAt: "2026-06-10T09:15:00Z"
    }
  ],
  timeline: [
    {
      id: "sun-timeline-signal",
      occurredAt: "2026-06-10T08:20:00Z",
      type: "Guest signal",
      title: "Experience risk detected",
      detail:
        "Service issue, staff task, recovery offer, and repeat-stay risk linked.",
      source: "Guest recovery fixture"
    },
    {
      id: "sun-timeline-approval",
      occurredAt: "2026-06-10T08:45:00Z",
      type: "Approval",
      title: "Guest recovery action proposed",
      detail: "WhatsApp-style guest message requires approval.",
      source: "Guest recovery orchestrator"
    }
  ],
  evidence: [
    {
      id: "sun-evidence-guest-001",
      label: "Guest experience signal",
      summary:
        "Synthetic service issue and repeat-stay risk evidence point to a recovery touchpoint.",
      sourceUri: "urn:hfs:source:sunlife:guest-experience",
      capturedAt: "2026-06-10T08:20:00Z",
      contentHash:
        "sha256:4d7d8d0bc6ab7b77933a060a55e69eb664deec977832f004eddb8af508c2c6ef"
    }
  ],
  sop: {
    name: "Guest experience recovery",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await guest-experience approval",
    completedSteps: 2,
    totalSteps: 5,
    progress: 40,
    requiredEvidence:
      "Guest issue, staff task, recovery offer, sustainability proof, and approved message"
  },
  recommendation: {
    id: "recommendation-sunlife-001",
    status: "Pending approval",
    title: "Approve guest recovery actions",
    recommendation:
      "Create staff recovery task, attach sustainability proof where relevant, draft a WhatsApp-style guest message, and send only after the experience owner approves the recovery offer.",
    facts: [
      "Guest experience issue is active.",
      "Staff task is needed before promise is made.",
      "Outbound guest message is approval-gated."
    ],
    assumptions: ["Fast recovery before checkout lowers repeat-stay risk."],
    inferences: [
      "The guest should receive a grounded update, not a generic apology.",
      "Staff execution evidence should feed the next recovery recommendation."
    ],
    confidence: 0.82,
    confidencePercent: "82%",
    modelProfile: "sunlife-guest-recovery",
    modelProfileVersion: "1.0.0",
    policyVersion: "sunlife-guest-routing-mauritius 1.0.0",
    evidenceIds: ["sun-evidence-guest-001"],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-sunlife-001",
    status: "Pending",
    policy: "Guest recovery approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-10T08:45:00Z",
    requestedBy: "Guest Recovery Orchestrator",
    decisionDueAt: "2026-06-10T09:15:00Z"
  },
  actions: [
    {
      id: "sun-action-guest-message-001",
      type: "DRAFT_GUEST_MESSAGE",
      status: "Pending approval",
      requestedAt: "2026-06-10T08:45:00Z",
      completedAt: null,
      sourceSystem: "MuleSoft guest mock",
      correlationId: "70000000-0000-4000-8000-000000000001"
    }
  ],
  channelLog: [
    {
      id: "sun-channel-whatsapp-001",
      channel: "WhatsApp-style guest message",
      status: "DRAFT_ONLY",
      target: "Guest SUN-SYN-2044",
      detail: "Guest message requires experience-owner approval before send."
    }
  ],
  outcomeMetrics: [
    { id: "sun-outcome-task", label: "Staff task", value: "Queued" },
    { id: "sun-outcome-message", label: "Guest message", value: "Draft only" },
    { id: "sun-outcome-repeat", label: "Repeat-stay risk", value: "Watch" },
    { id: "sun-outcome-feedback", label: "Feedback loop", value: "Open" }
  ],
  outcome: {
    status: "Awaiting approved guest recovery",
    summary:
      "Outcome metrics are projected until experience-owner approval and mock execution complete.",
    observedAt: null,
    effectiveness: "Pending"
  },
  operatingLayer: operatingLayer({
    kpis: [
      {
        id: "kpi-sun-recovery",
        label: "Recovery success",
        value: "Draft",
        prediction:
          "Predicted recovery improves if staff task closes before message",
        predictionPercent: 74,
        confidence: "82%",
        delta: "Before checkout",
        status: "Action"
      },
      {
        id: "kpi-sun-repeat",
        label: "Repeat-stay risk",
        value: "Watch",
        prediction:
          "Predicted repeat-stay risk drops after approved guest recovery",
        predictionPercent: 69,
        confidence: "73%",
        delta: "Recover",
        status: "Watch"
      },
      {
        id: "kpi-sun-staff",
        label: "Staff coordination",
        value: "Queued",
        prediction:
          "Predicted service closure improves after operations acknowledgement",
        predictionPercent: 77,
        confidence: "79%",
        delta: "Task first",
        status: "Queued"
      }
    ],
    trendTitle: "Guest experience recovery forecast",
    trend: [
      { id: "sun-trend-1", label: "Service", actual: 39, predicted: 77 },
      { id: "sun-trend-2", label: "Message", actual: 45, predicted: 74 },
      { id: "sun-trend-3", label: "Repeat", actual: 57, predicted: 69 },
      { id: "sun-trend-4", label: "Proof", actual: 48, predicted: 72 }
    ],
    brief: [
      "Close the staff task before promising the guest a recovery outcome.",
      "Attach sustainability proof only where it directly supports the guest issue.",
      "Send WhatsApp-style guest message only after experience-owner approval."
    ],
    agents: [
      {
        id: "agent-sun-guest",
        name: "Guest Recovery Agent",
        status: "Drafting message",
        lastMessage:
          "The guest update should mention the concrete staff action, not a generic apology."
      },
      {
        id: "agent-sun-staff",
        name: "Staff Coordination Agent",
        status: "Routing task",
        lastMessage:
          "Operations acknowledgement is the next evidence point before guest message send."
      }
    ],
    channels: [
      {
        id: "dept-sun-gx",
        name: "Guest Experience",
        owner: "Guest Experience Lead",
        unread: 3,
        lastMessage: "Guest message is draft-only until offer approval."
      },
      {
        id: "dept-sun-ops",
        name: "Operations",
        owner: "Operations Lead",
        unread: 2,
        lastMessage: "Room/service recovery task is queued."
      }
    ]
  })
});

const CASE_STATES_BY_PROFILE = {
  "logia-retail": caseState,
  "nexavenu-revenue": nexavenuCaseState,
  "air-mauritius-passenger": airMauritiusCaseState,
  "constance-hospitality": constanceHospitalityCaseState,
  "afrasia-private-banking": afrasiaPrivateBankingCaseState,
  "sunlife-guest-recovery": sunlifeGuestRecoveryCaseState
};

const PROFILE_RUNTIME = {
  "logia-retail": {
    correlationId: "20000000-0000-4000-8000-000000000001",
    userRole: "Duty Manager",
    purpose: "RESOLVE_RETAIL_RISK"
  },
  "nexavenu-revenue": {
    correlationId: "30000000-0000-4000-8000-000000000001",
    userRole: "Revenue Owner",
    purpose: "QUALIFY_B2B_REVENUE_PIPELINE"
  },
  "air-mauritius-passenger": {
    correlationId: "40000000-0000-4000-8000-000000000001",
    userRole: "Passenger Recovery Lead",
    purpose: "RESOLVE_PASSENGER_RECOVERY"
  },
  "constance-hospitality": {
    correlationId: "50000000-0000-4000-8000-000000000001",
    userRole: "Revenue Operations Lead",
    purpose: "RESOLVE_HOSPITALITY_REVENUE"
  },
  "afrasia-private-banking": {
    correlationId: "60000000-0000-4000-8000-000000000001",
    userRole: "Senior Relationship Manager",
    purpose: "RESOLVE_PRIVATE_BANKING_RM"
  },
  "sunlife-guest-recovery": {
    correlationId: "70000000-0000-4000-8000-000000000001",
    userRole: "Guest Experience Lead",
    purpose: "RESOLVE_GUEST_RECOVERY"
  }
};

export function getProfileOptions(selectedProfileKey = DEFAULT_PROFILE_KEY) {
  return Object.values(PROFILE_CONFIGS).map((profile) => ({
    key: profile.key,
    shortName: profile.shortName,
    pageTitle: profile.pageTitle,
    eyebrow: profile.eyebrow,
    selected: profile.key === selectedProfileKey,
    buttonVariant: profile.key === selectedProfileKey ? "brand" : "neutral"
  }));
}

const readyState = {
  stateVersion: UI_STATE_VERSION,
  stateName: "ready",
  mode: "ready",
  profile: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY],
  generatedAt: "2026-06-06T09:39:00Z",
  correlationId: "20000000-0000-4000-8000-000000000001",
  userRole: "Duty Manager",
  purpose: "RESOLVE_RETAIL_RISK",
  permissions: {
    canApprove: true,
    canModify: true,
    canReject: true,
    canExecute: false,
    canRequestCorrection: true
  },
  case: caseState
};

export const UI_STATES = {
  ready: readyState,
  restricted: {
    ...readyState,
    stateName: "restricted",
    userRole: "Retail Viewer",
    permissions: {
      canApprove: false,
      canModify: false,
      canReject: false,
      canExecute: false,
      canRequestCorrection: false
    }
  },
  loading: {
    stateVersion: UI_STATE_VERSION,
    stateName: "loading",
    mode: "loading",
    profile: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY],
    message: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].loadingMessage
  },
  empty: {
    stateVersion: UI_STATE_VERSION,
    stateName: "empty",
    mode: "empty",
    profile: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY],
    title: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].emptyTitle,
    message: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].emptyMessage
  },
  denied: {
    stateVersion: UI_STATE_VERSION,
    stateName: "denied",
    mode: "denied",
    profile: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY],
    title: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].deniedTitle,
    message: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].deniedMessage,
    correlationId: "20000000-0000-4000-8000-000000000002"
  },
  error: {
    stateVersion: UI_STATE_VERSION,
    stateName: "error",
    mode: "error",
    profile: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY],
    title: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].errorTitle,
    message: PROFILE_CONFIGS[DEFAULT_PROFILE_KEY].errorMessage,
    errorCode: "RETRYABLE_DEPENDENCY_FAILURE",
    correlationId: "20000000-0000-4000-8000-000000000003",
    retryable: true
  }
};

export function getUiState(stateName, profileKey = DEFAULT_PROFILE_KEY) {
  const profile = getProfile(profileKey);
  const selected = UI_STATES[stateName] || UI_STATES.error;
  const state = JSON.parse(JSON.stringify(selected));
  state.profile = JSON.parse(JSON.stringify(profile));
  state.profileOptions = getProfileOptions(profile.key);
  if (state.mode === "ready") {
    const runtime =
      PROFILE_RUNTIME[profile.key] || PROFILE_RUNTIME[DEFAULT_PROFILE_KEY];
    state.case = JSON.parse(
      JSON.stringify(CASE_STATES_BY_PROFILE[profile.key] || caseState)
    );
    state.correlationId = runtime.correlationId;
    state.userRole =
      state.stateName === "restricted"
        ? `${profile.shortName} Viewer`
        : runtime.userRole;
    state.purpose = runtime.purpose;
  }
  if (state.mode === "loading") {
    state.message = profile.loadingMessage;
  }
  if (state.mode === "empty") {
    state.title = profile.emptyTitle;
    state.message = profile.emptyMessage;
  }
  if (state.mode === "denied") {
    state.title = profile.deniedTitle;
    state.message = profile.deniedMessage;
  }
  if (state.mode === "error") {
    state.title = profile.errorTitle;
    state.message = profile.errorMessage;
  }
  return state;
}
