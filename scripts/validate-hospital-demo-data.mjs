import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const dataFiles = [
  "master_data.json",
  "warehouse_inventory.json",
  "inventory_positions.json",
  "product_batches.json",
  "complaints.json",
  "complaint_clusters.json",
  "queue_pressure.json",
  "sales_data.json",
  "supplier_responses.json",
  "task_templates.json",
  "channel_aliases.json",
  "recommendation_cases.json",
  "event_stream.json",
  "promotions.json"
];

const forbiddenKeys = [
  "address",
  "credential",
  "diagnosis",
  "dosage",
  "email",
  "medicalRecord",
  "patientName",
  "phone",
  "prescription",
  "staffName",
  "treatment"
];

function fail(message) {
  throw new Error(message);
}

function assert(condition, message) {
  if (!condition) {
    fail(message);
  }
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function countBetween(label, count, min, max) {
  assert(
    count >= min && count <= max,
    `${label} count ${count} is outside expected range ${min}-${max}`
  );
}

function walk(value, visitor, trail = []) {
  if (Array.isArray(value)) {
    value.forEach((entry, index) => walk(entry, visitor, trail.concat(index)));
    return;
  }

  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, entry]) => {
      visitor(key, entry, trail.concat(key));
      walk(entry, visitor, trail.concat(key));
    });
  }
}

function assertNoForbiddenPersonalData(fileName, value) {
  walk(value, (key, entry, trail) => {
    const normalizedKey = key.toLowerCase();
    for (const forbidden of forbiddenKeys) {
      assert(
        normalizedKey !== forbidden.toLowerCase(),
        `${fileName} contains forbidden personal or clinical key ${trail.join(
          "."
        )}`
      );
    }

    if (typeof entry === "string") {
      assert(!entry.includes("@"), `${fileName} contains an email-like value`);
      assert(
        !/\+\d{7,}/.test(entry),
        `${fileName} contains a phone-like value`
      );
    }
  });
}

const rootData = Object.fromEntries(
  dataFiles.map((fileName) => [fileName, readJson(fileName)])
);
const syntheticData = Object.fromEntries(
  dataFiles.map((fileName) => [
    fileName,
    readJson(path.join("synthetic_data", fileName))
  ])
);

for (const fileName of dataFiles) {
  assertNoForbiddenPersonalData(fileName, rootData[fileName]);
  assertNoForbiddenPersonalData(
    path.join("synthetic_data", fileName),
    syntheticData[fileName]
  );
  assert(
    JSON.stringify(rootData[fileName]) ===
      JSON.stringify(syntheticData[fileName]),
    `${fileName} and synthetic_data/${fileName} are not identical`
  );
}

const masterData = rootData["master_data.json"];
const resources = rootData["warehouse_inventory.json"].resources;
const supplyPositions = rootData["inventory_positions.json"].supplyPositions;
const complaints = rootData["complaints.json"];
const complaintClusters = rootData["complaint_clusters.json"];
const queuePressure = rootData["queue_pressure.json"];
const financialCases = rootData["sales_data.json"].financialCases;
const partnerResponses = rootData["supplier_responses.json"];
const taskTemplates = rootData["task_templates.json"];
const channelAliases = rootData["channel_aliases.json"];
const recommendationCases = rootData["recommendation_cases.json"];
const eventStream = rootData["event_stream.json"];
const requiredComplaintTypes = new Set([
  "wait_time",
  "room_readiness",
  "cleanliness",
  "food",
  "billing",
  "discharge_delay",
  "lost_item",
  "accessibility",
  "privacy",
  "safety",
  "pharmacy_delay",
  "staff_interaction"
]);
const requiredResourceTypes = new Set([
  "BED",
  "ROOM",
  "QUEUE",
  "STAFF_POOL",
  "SUPPLY",
  "EQUIPMENT",
  "SERVICE_COUNTER"
]);
const requiredPartnerTypes = new Set([
  "laboratory",
  "laundry",
  "food_service",
  "insurance",
  "payment_processor",
  "maintenance",
  "transport",
  "equipment_vendor"
]);
const requiredFinancialCaseTypes = new Set([
  "duplicate_invoice",
  "claim_pending",
  "refund_request",
  "deposit_issue",
  "voucher_request",
  "compensation_review",
  "payment_failure",
  "revenue_risk"
]);
const allowedFinancialStatuses = new Set([
  "open",
  "pending_partner",
  "approved",
  "denied",
  "resolved"
]);
const allowedAmountBands = new Set(["low", "medium", "high"]);

countBetween("department", masterData.departments.length, 8, 10);
countBetween("location", masterData.locations.length, 20, 30);
countBetween(
  "resource type",
  new Set(resources.map((r) => r.resourceType)).size,
  8,
  12
);
countBetween("resource", resources.length, 80, 120);
countBetween("customer alias", masterData.customerAliases.length, 40, 60);
countBetween("staff role alias", masterData.staffRoleAliases.length, 20, 30);
countBetween("partner", masterData.partners.length, 8, 12);
countBetween("complaint", complaints.length, 50, 70);
countBetween("complaint cluster", complaintClusters.length, 8, 10);
countBetween("queue/capacity", queuePressure.length, 60, 100);
countBetween("pharmacy/supply", supplyPositions.length, 30, 50);
countBetween("billing/insurance", financialCases.length, 20, 30);
countBetween("partner response", partnerResponses.length, 12, 16);
countBetween("staff task template", taskTemplates.length, 20, 25);
countBetween("channel recipient alias", channelAliases.length, 12, 16);
countBetween("expected recommendation", recommendationCases.length, 12, 15);
countBetween("hospital event fixture", eventStream.length, 18, 24);

const resourceTypes = new Set(resources.map((resource) => resource.resourceType));
for (const resourceType of requiredResourceTypes) {
  assert(resourceTypes.has(resourceType), `Missing resource type ${resourceType}`);
}

const partnerTypes = new Set(
  masterData.partners.map((partner) => partner.partnerType)
);
for (const partnerType of requiredPartnerTypes) {
  assert(partnerTypes.has(partnerType), `Missing partner type ${partnerType}`);
}

const complaintTypes = new Set(
  complaints.map((complaint) => complaint.complaintType)
);
for (const complaintType of requiredComplaintTypes) {
  assert(
    complaintTypes.has(complaintType),
    `Missing complaint type ${complaintType}`
  );
}

const financialCaseTypes = new Set(
  financialCases.map((financialCase) => financialCase.caseType)
);
for (const caseType of requiredFinancialCaseTypes) {
  assert(financialCaseTypes.has(caseType), `Missing financial case ${caseType}`);
}

const departmentIds = new Set(
  masterData.departments.map((d) => d.departmentId)
);
const locationIds = new Set(masterData.locations.map((l) => l.locationId));
const resourceIds = new Set(resources.map((r) => r.resourceId));
const partnerIds = new Set(masterData.partners.map((partner) => partner.partnerId));
const customerAliasIds = new Set(
  masterData.customerAliases.map((alias) => alias.customerAliasId)
);
const complaintIds = new Set(
  complaints.map((complaint) => complaint.complaintId)
);
const issueIds = new Set([
  ...complaintClusters.map((cluster) => cluster.clusterId),
  ...financialCases.map((financialCase) => financialCase.caseId),
  ...rootData["product_batches.json"].supplyBatches.map(
    (batch) => batch.batchId
  )
]);

for (const resource of resources) {
  assert(
    resource.globalPrimitive === "Resource",
    `${resource.resourceId} is not a Resource primitive`
  );
  assert(
    departmentIds.has(resource.departmentId),
    `${resource.resourceId} has unknown department`
  );
  assert(
    locationIds.has(resource.locationId),
    `${resource.resourceId} has unknown location`
  );
  assert(resource.status, `${resource.resourceId} is missing status`);
  assert(resource.evidenceId, `${resource.resourceId} is missing evidenceId`);
}

for (const complaint of complaints) {
  assert(
    complaint.globalPrimitive === "Signal",
    `${complaint.complaintId} is not a Signal primitive`
  );
  assert(
    requiredComplaintTypes.has(complaint.complaintType),
    `${complaint.complaintId} has unknown complaint type ${complaint.complaintType}`
  );
  assert(
    customerAliasIds.has(complaint.customerAliasId),
    `${complaint.complaintId} has unknown customer alias`
  );
  assert(
    departmentIds.has(complaint.departmentId),
    `${complaint.complaintId} has unknown department`
  );
  assert(
    locationIds.has(complaint.locationId),
    `${complaint.complaintId} has unknown location`
  );
  assert(
    (complaint.resourceId && resourceIds.has(complaint.resourceId)) ||
      complaint.resourceUnknownReason,
    `${complaint.complaintId} needs a known resource or unknown-resource reason`
  );
  assert(
    complaint.evidenceId,
    `${complaint.complaintId} is missing evidenceId`
  );
  if (["privacy", "safety"].includes(complaint.complaintType)) {
    assert(
      complaint.approvalRequiredForOutboundMessage === true,
      `${complaint.complaintId} must require approval for sensitive outbound messages`
    );
  }
}

for (const cluster of complaintClusters) {
  assert(
    cluster.sourceComplaintIds.length > 0,
    `${cluster.clusterId} has no source complaints`
  );
  for (const complaintId of cluster.sourceComplaintIds) {
    assert(
      complaintIds.has(complaintId),
      `${cluster.clusterId} references unknown complaint ${complaintId}`
    );
  }
  for (const dominantType of cluster.dominantTypes) {
    assert(
      requiredComplaintTypes.has(dominantType),
      `${cluster.clusterId} has unknown dominant complaint type ${dominantType}`
    );
  }
  assert(
    cluster.evidenceIds.length > 0,
    `${cluster.clusterId} has no evidence IDs`
  );
}

for (const financialCase of financialCases) {
  assert(
    financialCase.globalPrimitive === "Process",
    `${financialCase.caseId} is not a Process primitive`
  );
  assert(
    customerAliasIds.has(financialCase.customerAliasId),
    `${financialCase.caseId} has unknown customer alias`
  );
  assert(
    departmentIds.has(financialCase.departmentId),
    `${financialCase.caseId} has unknown department`
  );
  assert(
    requiredFinancialCaseTypes.has(financialCase.caseType),
    `${financialCase.caseId} has unknown case type ${financialCase.caseType}`
  );
  assert(
    allowedAmountBands.has(financialCase.amountBand),
    `${financialCase.caseId} has unknown amount band ${financialCase.amountBand}`
  );
  assert(
    financialCase.approvalRequired === true,
    `${financialCase.caseId} must require approval`
  );
  assert(
    allowedFinancialStatuses.has(financialCase.status),
    `${financialCase.caseId} has unknown status ${financialCase.status}`
  );
  assert(
    partnerIds.has(financialCase.relatedPartnerId),
    `${financialCase.caseId} has unknown related partner`
  );
  assert(financialCase.evidenceId, `${financialCase.caseId} is missing evidenceId`);
}

for (const response of partnerResponses) {
  assert(
    response.globalPrimitive === "Evidence",
    `${response.partnerResponseId} is not Evidence primitive`
  );
  assert(
    issueIds.has(response.relatedIssueId),
    `${response.partnerResponseId} references unknown issue`
  );
  assert(
    response.evidenceId,
    `${response.partnerResponseId} is missing evidenceId`
  );
  assert(
    typeof response.changesRecommendation === "boolean",
    `${response.partnerResponseId} does not state recommendation impact`
  );
}

for (const recommendationCase of recommendationCases) {
  assert(
    recommendationCase.evidenceIds.length > 0,
    `${recommendationCase.caseId} has no evidence IDs`
  );
  assert(
    typeof recommendationCase.managerApprovalRequired === "boolean",
    `${recommendationCase.caseId} does not define manager approval`
  );
  assert(
    recommendationCase.expectedRefusal,
    `${recommendationCase.caseId} is missing refusal boundary`
  );
}

for (const template of taskTemplates) {
  assert(
    typeof template.requiresApproval === "boolean",
    `${template.taskTemplateId} does not define approval requirement`
  );
}

for (const alias of channelAliases) {
  assert(
    alias.role.startsWith("role:"),
    `${alias.recipientAliasId} does not use a role alias`
  );
  assert(
    alias.slackTarget.startsWith("SLACK-ROLE-"),
    `${alias.recipientAliasId} has unsafe Slack target`
  );
  assert(
    alias.whatsappTargetAlias.startsWith("WA-ROLE-"),
    `${alias.recipientAliasId} has unsafe WhatsApp target`
  );
}

const intakeResults = new Set(eventStream.map((event) => event.intakeResult));
const eventTypes = new Set(eventStream.map((event) => event.eventType));

for (const requiredResult of [
  "DUPLICATE",
  "REJECTED_SCHEMA",
  "ACCEPTED_LATE",
  "ACCEPTED_OUT_OF_ORDER",
  "REJECTED_IDEMPOTENCY_CONFLICT",
  "REJECTED_HASH"
]) {
  assert(
    intakeResults.has(requiredResult),
    `Missing event intake result ${requiredResult}`
  );
}

assert(
  eventTypes.has("CLINICAL_DECISION_REQUEST_REFUSED"),
  "Missing clinical refusal event fixture"
);
assert(
  eventStream.every(
    (event) => event.expectedIntakeResult && event.evidenceIds.length > 0
  ),
  "Every event needs an expected intake result and evidence IDs"
);

console.log(
  `Hospital demo data is valid: ${resources.length} resources, ${complaints.length} complaints, ${recommendationCases.length} recommendation cases, ${eventStream.length} events.`
);
