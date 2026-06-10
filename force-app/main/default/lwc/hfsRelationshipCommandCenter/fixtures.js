export const UI_STATE_VERSION = "1.0.0";

export const DEFAULT_PROFILE_KEY = "north-star-retail";

const PROFILE_CONFIGS = {
  "north-star-retail": {
    key: "north-star-retail",
    shortName: "North Star",
    eyebrow: "North Star command center",
    pageTitle: "Supermarket recovery plan",
    loadingTitle: "Loading North Star context",
    loadingMessage: "Assembling North Star retail context.",
    emptyTitle: "No North Star work is assigned",
    emptyMessage: "New supermarket risk work will appear here when assigned.",
    deniedTitle: "North Star context is not available",
    deniedMessage:
      "Your current permissions or declared purpose do not allow access to this retail context.",
    errorTitle: "North Star could not load",
    errorMessage:
      "The retail command service is temporarily unavailable. Retry the request.",
    ownerLabel: "Manager owner",
    deadlineLabel: "Rush deadline",
    updateLabel: "Next decision update",
    riskKicker: "Risk pulse",
    riskHeading: "North Star retail signals",
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
  }
};

export function getProfile(profileKey = DEFAULT_PROFILE_KEY) {
  return PROFILE_CONFIGS[profileKey] || PROFILE_CONFIGS[DEFAULT_PROFILE_KEY];
}

const caseState = {
  id: "work-north-star-retail-risk-001",
  externalKey: "CORR-NORTH-STAR-WEEKEND-GRILL-001",
  title: "North Star weekend promotion recovery",
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
  productContext: {
    store: "Goodlands FreshMart",
    product: "Island beef burger patties 400g",
    category: "Fresh food",
    batch: "BATCH-FRESH-BEEF-2026-06-07-A",
    supplier: "Island Proteins Ltd",
    promotion: "Weekend Grill",
    shelfArea: "SHELF-MEAT-CHILLER-A3"
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
  supplierResponse: {
    status: "Replacement approved",
    leadTime: "18 hours",
    replacement: "BATCH-FRESH-BEEF-2026-06-08-B",
    creditNote: "Offered",
    qualityIssue: "Batch-specific review remains open"
  },
  storeExecution: {
    cashierRecommendation: "Open one extra lane by 16:15",
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
      source: "North Star Orchestrator"
    }
  ],
  evidence: [
    {
      id: "evidence-inventory-north-star-001",
      label: "Inventory and demand",
      summary:
        "Shelf 18, backroom 24, warehouse 72, supplier 180, sales velocity 28 units per hour.",
      sourceUri: "urn:hfs:source:retail:inventory",
      capturedAt: "2026-06-06T09:01:00Z",
      contentHash:
        "sha256:86a1b1848320a798ea3df9b248f12b86976b8d6c4d86c31bbef5d2a26e49df5f"
    },
    {
      id: "evidence-complaint-north-star-001",
      label: "Complaint cluster",
      summary:
        "Five complaints mention smell, damaged packaging, refunds, and price mismatch.",
      sourceUri: "urn:hfs:source:retail:complaints",
      capturedAt: "2026-06-06T09:14:00Z",
      contentHash:
        "sha256:b3d620f198f2db5cb1dd78751ba54fcd45ba040f4da22722b0fb508f840496cb"
    },
    {
      id: "evidence-supplier-north-star-001",
      label: "Supplier response",
      summary:
        "Replacement batch approved with 18-hour lead time and credit note.",
      sourceUri: "urn:hfs:source:retail:supplier",
      capturedAt: "2026-06-06T09:25:00Z",
      contentHash:
        "sha256:3ec509577dfb0232926b50bbf7bc7b047f77c48665d1d15a067a7c548f17d588"
    },
    {
      id: "evidence-staffing-north-star-001",
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
    name: "North Star retail recovery",
    version: "1.0.0",
    status: "In progress",
    currentStep: "Await manager approval",
    completedSteps: 3,
    totalSteps: 6,
    progress: 50,
    requiredEvidence: "Approved action set and channel delivery results"
  },
  recommendation: {
    id: "recommendation-north-star-retail-001",
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
    modelProfile: "north-star-retail-recommendation",
    modelProfileVersion: "1.0.0",
    policyVersion: "north-star-retail-routing-mauritius 1.0.0",
    evidenceIds: [
      "evidence-inventory-north-star-001",
      "evidence-complaint-north-star-001",
      "evidence-supplier-north-star-001",
      "evidence-staffing-north-star-001"
    ],
    requiresHumanApproval: true
  },
  approval: {
    id: "approval-north-star-retail-001",
    status: "Pending",
    policy: "North Star manager approval",
    policyVersion: "1.0.0",
    requestedAt: "2026-06-06T09:36:00Z",
    requestedBy: "North Star Orchestrator",
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
  }
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
  productContext: {
    store: "Synthetic LiftOps Manufacturing",
    product: "Agentforce and MuleSoft transformation",
    category: "B2B revenue pipeline",
    batch: "Discovery readiness: 48/100",
    supplier: "Operations champion",
    promotion: "Agentforce acceleration campaign",
    shelfArea: "Revenue workspace"
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
  supplierResponse: {
    status: "Hold before handoff",
    leadTime: "48/100",
    replacement: "AI readiness checklist + MuleSoft explainer",
    creditNote: "CFO ROI proof needed",
    qualityIssue: "Do not consume senior solution-consultant time yet"
  },
  storeExecution: {
    cashierRecommendation:
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
  }
};

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
  if (state.mode === "ready" && profile.key === "nexavenu-revenue") {
    state.case = JSON.parse(JSON.stringify(nexavenuCaseState));
    state.correlationId = "30000000-0000-4000-8000-000000000001";
    state.userRole = "Revenue Owner";
    state.purpose = "QUALIFY_B2B_REVENUE_PIPELINE";
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
