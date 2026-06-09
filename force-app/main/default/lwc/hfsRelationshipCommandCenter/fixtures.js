export const UI_STATE_VERSION = "1.0.0";

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

const readyState = {
  stateVersion: UI_STATE_VERSION,
  stateName: "ready",
  mode: "ready",
  generatedAt: "2026-06-06T09:39:00Z",
  correlationId: "20000000-0000-4000-8000-000000000001",
  userRole: "Duty Manager",
  purpose: "RESOLVE_RETAIL_RISK",
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
    userRole: "Retail Viewer",
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
    message: "Assembling North Star retail context."
  },
  empty: {
    stateVersion: UI_STATE_VERSION,
    stateName: "empty",
    mode: "empty",
    title: "No North Star work is assigned",
    message: "New supermarket risk work will appear here when assigned."
  },
  denied: {
    stateVersion: UI_STATE_VERSION,
    stateName: "denied",
    mode: "denied",
    title: "North Star context is not available",
    message:
      "Your current permissions or declared purpose do not allow access to this retail context.",
    correlationId: "20000000-0000-4000-8000-000000000002"
  },
  error: {
    stateVersion: UI_STATE_VERSION,
    stateName: "error",
    mode: "error",
    title: "North Star could not load",
    message:
      "The retail command service is temporarily unavailable. Retry the request.",
    errorCode: "RETRYABLE_DEPENDENCY_FAILURE",
    correlationId: "20000000-0000-4000-8000-000000000003",
    retryable: true
  }
};

export function getUiState(stateName) {
  const selected = UI_STATES[stateName] || UI_STATES.error;
  return JSON.parse(JSON.stringify(selected));
}
