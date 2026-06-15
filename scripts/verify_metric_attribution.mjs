#!/usr/bin/env node

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const catalogPath = path.join(
  root,
  "analytics",
  "metrics",
  "metric-definitions-v1.json"
);

function readJson(relativePath) {
  return JSON.parse(readFileSync(path.join(root, relativePath), "utf8"));
}

function getPath(value, pathExpression) {
  return pathExpression.split(".").reduce((current, segment) => {
    if (current === null || current === undefined) {
      return undefined;
    }
    return current[segment];
  }, value);
}

function numeric(value, label) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    throw new Error(`${label} must resolve to a number.`);
  }
  return value;
}

function computeMetric(metric, event) {
  const calculation = metric.calculation;
  if (calculation.type === "attributeNumber") {
    return numeric(getPath(event, calculation.path), metric.key);
  }

  if (calculation.type === "regexDelta") {
    const source = getPath(event, calculation.path);
    const lines = Array.isArray(source) ? source : [source];
    const pattern = new RegExp(calculation.pattern, "i");
    for (const line of lines.filter(Boolean)) {
      const match = String(line).match(pattern);
      if (!match) {
        continue;
      }
      const fromValue = Number(match[calculation.fromGroup]);
      const toValue = Number(match[calculation.toGroup]);
      return numeric(toValue - fromValue, metric.key);
    }
    throw new Error(`${metric.key} did not match ${calculation.pattern}.`);
  }

  throw new Error(`Unsupported metric calculation type: ${calculation.type}`);
}

function requireText(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${label} is required.`);
  }
}

function validateMetric(metric, keys) {
  requireText(metric.key, "metric.key");
  if (keys.has(metric.key)) {
    throw new Error(`Duplicate metric key: ${metric.key}`);
  }
  keys.add(metric.key);

  for (const field of [
    "label",
    "description",
    "valueType",
    "unit",
    "direction",
    "formula",
    "timeWindow"
  ]) {
    requireText(metric[field], `${metric.key}.${field}`);
  }

  if (!metric.attribution) {
    throw new Error(`${metric.key}.attribution is required.`);
  }
  for (const field of [
    "method",
    "sourceEventType",
    "sourceEventCode",
    "rule"
  ]) {
    requireText(
      metric.attribution[field],
      `${metric.key}.attribution.${field}`
    );
  }

  if (!Array.isArray(metric.examples) || metric.examples.length === 0) {
    throw new Error(
      `${metric.key}.examples must contain at least one example.`
    );
  }
}

const catalog = JSON.parse(readFileSync(catalogPath, "utf8"));
const keys = new Set();
const recalculations = [];

for (const metric of catalog.metrics || []) {
  validateMetric(metric, keys);
  for (const example of metric.examples) {
    const event = readJson(example.fixture);
    if (event.type !== metric.attribution.sourceEventType) {
      throw new Error(
        `${metric.key} expected ${metric.attribution.sourceEventType} but ${example.fixture} has ${event.type}.`
      );
    }
    const eventCode = getPath(event, "data.attributes.eventcode");
    if (eventCode !== metric.attribution.sourceEventCode) {
      throw new Error(
        `${metric.key} expected ${metric.attribution.sourceEventCode} but ${example.fixture} has ${eventCode}.`
      );
    }

    const value = computeMetric(metric, event);
    if (value !== example.expectedValue) {
      throw new Error(
        `${metric.key} expected ${example.expectedValue} but recalculated ${value}.`
      );
    }

    recalculations.push({
      metricKey: metric.key,
      value,
      unit: metric.unit,
      sourceEventId: event.id,
      correlationId: event.hfscorrelationid,
      sourceRecordId: event.hfssourcerecordid,
      contentHash: event.hfscontenthash,
      displayedValue: example.displayedValue
    });
  }
}

console.log(
  JSON.stringify(
    {
      status: "passed",
      version: catalog.version,
      metricCount: keys.size,
      recalculationCount: recalculations.length,
      recalculations
    },
    null,
    2
  )
);
