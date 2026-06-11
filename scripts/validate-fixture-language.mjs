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
  "master_data.json",
  "resources.json",
  "supply_positions.json",
  "supply_batches.json",
  "complaints.json",
  "complaint_clusters.json",
  "capacity_pressure.json",
  "financial_cases.json",
  "partner_responses.json",
  "task_templates.json",
  "channel_aliases.json",
  "recommendation_cases.json",
  "event_stream.json",
  "service_recovery_options.json"
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

for (const fileName of activeHospitalDataFiles) {
  const canonicalPath = path.join(canonicalHospitalDataDir, fileName);
  const canonicalText = read(canonicalPath);
  assertNoForbiddenTerms(canonicalPath, canonicalText);
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
