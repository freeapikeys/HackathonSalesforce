import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const canonicalHospitalDataDir = path.join("data", "hospital");

const forbiddenRetailTerms = [
  /\bsupermarket\b/i,
  /\bretail\b/i,
  /\bburger\b/i,
  /\bcashier\b/i,
  /\bshelf\b/i,
  /\bstore:/i,
  /\bstore execution\b/i,
  /\bproduct context\b/i,
  /\bsupplier response\b/i
];

const activeHospitalDataFiles = [
  { canonical: "master_data.json", mirror: "master_data.json" },
  { canonical: "resources.json", mirror: "warehouse_inventory.json" },
  { canonical: "supply_positions.json", mirror: "inventory_positions.json" },
  { canonical: "supply_batches.json", mirror: "product_batches.json" },
  { canonical: "complaints.json", mirror: "complaints.json" },
  { canonical: "complaint_clusters.json", mirror: "complaint_clusters.json" },
  { canonical: "capacity_pressure.json", mirror: "queue_pressure.json" },
  { canonical: "financial_cases.json", mirror: "sales_data.json" },
  { canonical: "partner_responses.json", mirror: "supplier_responses.json" },
  { canonical: "task_templates.json", mirror: "task_templates.json" },
  { canonical: "channel_aliases.json", mirror: "channel_aliases.json" },
  {
    canonical: "recommendation_cases.json",
    mirror: "recommendation_cases.json"
  },
  { canonical: "event_stream.json", mirror: "event_stream.json" },
  {
    canonical: "service_recovery_options.json",
    mirror: "promotions.json"
  }
];

const activeLwcFiles = [
  "force-app/main/default/lwc/hfsRelationshipCommandCenter/fixtures.js",
  "force-app/main/default/lwc/hfsRelationshipCommandCenter/stateAdapter.js",
  "force-app/main/default/lwc/hfsRelationshipCommandCenter/hfsRelationshipCommandCenter.html"
];

const forbiddenLwcIdentifiers = [
  "productContext",
  "storeExecution",
  "supplierResponse",
  "cashierRecommendation",
  "shelfArea"
];

const legacyRetailEventFiles = new Set([
  "15-stockout-risk-detected.json",
  "16-warehouse-stock-checked.json",
  "17-supplier-lead-time-updated.json",
  "18-expiry-risk-detected.json",
  "19-near-expiry-markdown-recommended.json",
  "20-complaint-cluster-detected.json",
  "21-price-mismatch-reported.json",
  "22-damaged-packaging-reported.json",
  "23-supplier-response-received.json",
  "24-queue-risk-detected.json",
  "25-shelf-layout-mismatch-detected.json",
  "26-store-task-created.json",
  "27-approved-action-executed.json",
  "28-retail-outcome-captured.json"
]);

const legacyRetailAgentforceScenarios = new Set([
  "accessible-grounded-explanation",
  "grounded-recommendation",
  "no-qualified-model-refusal",
  "changed-recommendation-after-supplier-response",
  "inventory-waste-missing-expiry-caution",
  "inventory-waste-clean-stockout",
  "inventory-waste-near-expiry-markdown",
  "inventory-waste-overstock-household"
]);

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(read(relativePath));
}

function fail(message) {
  throw new Error(message);
}

function assertNoForbiddenTerms(label, text) {
  for (const pattern of forbiddenRetailTerms) {
    if (pattern.test(text)) {
      fail(`${label} contains legacy retail wording matching ${pattern}`);
    }
  }
}

function assertNoForbiddenIdentifiers(relativePath) {
  const text = read(relativePath);
  for (const identifier of forbiddenLwcIdentifiers) {
    if (text.includes(identifier)) {
      fail(`${relativePath} still uses legacy UI state key ${identifier}`);
    }
  }
}

for (const { canonical, mirror } of activeHospitalDataFiles) {
  const canonicalPath = path.join(canonicalHospitalDataDir, canonical);
  const mirrorPath = path.join("synthetic_data", mirror);
  const canonicalText = read(canonicalPath);
  const syntheticText = read(mirrorPath);
  assertNoForbiddenTerms(canonicalPath, canonicalText);
  assertNoForbiddenTerms(mirrorPath, syntheticText);
}

for (const relativePath of activeLwcFiles) {
  assertNoForbiddenIdentifiers(relativePath);
}

const eventDir = path.join(root, "integration/events/fixtures/events");
const eventFiles = fs
  .readdirSync(eventDir)
  .filter((fileName) => fileName.endsWith(".json"));

let hospitalEventCount = 0;
let legacyEventCount = 0;
for (const fileName of eventFiles) {
  const relativePath = path.join(
    "integration/events/fixtures/events",
    fileName
  );
  const event = readJson(relativePath);
  const eventText = JSON.stringify(event);
  const isHospital =
    event.source === "urn:hfs:source:hospital-operations" ||
    event.data?.attributes?.profile === "private-hospital";
  if (isHospital) {
    hospitalEventCount += 1;
    assertNoForbiddenTerms(relativePath, eventText);
    continue;
  }
  if (legacyRetailEventFiles.has(fileName)) {
    legacyEventCount += 1;
    continue;
  }
  assertNoForbiddenTerms(relativePath, eventText);
}

const agentforce = readJson(
  "intelligence/agentforce/fixtures/agentforce-scenarios-v1.json"
);
let hospitalScenarioCount = 0;
let legacyScenarioCount = 0;
for (const scenario of agentforce.scenarios) {
  const scenarioText = JSON.stringify(scenario);
  const hasHospitalReasoning = Boolean(
    scenario.response?.recommendation?.hospitalOperationsReasoning
  );
  if (hasHospitalReasoning) {
    hospitalScenarioCount += 1;
    assertNoForbiddenTerms(
      `Agentforce scenario ${scenario.name}`,
      scenarioText
    );
    continue;
  }
  if (legacyRetailAgentforceScenarios.has(scenario.name)) {
    legacyScenarioCount += 1;
    continue;
  }
  assertNoForbiddenTerms(`Agentforce scenario ${scenario.name}`, scenarioText);
}

console.log(
  "Fixture language audit passed: " +
    `${hospitalEventCount} hospital events, ` +
    `${hospitalScenarioCount} hospital Agentforce scenarios, ` +
    `${legacyEventCount} legacy retail event fixtures, ` +
    `${legacyScenarioCount} legacy retail Agentforce scenarios.`
);
