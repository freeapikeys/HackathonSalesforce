import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(scriptDirectory, "..");

const requiredPaths = [
  ".forceignore",
  "config/project-scratch-def.json",
  "force-app/main/default",
  "manifest/package.xml",
  "sfdx-project.json"
];

for (const relativePath of requiredPaths) {
  assert(
    existsSync(join(projectRoot, relativePath)),
    `Missing required Salesforce project path: ${relativePath}`
  );
}

const project = JSON.parse(
  readFileSync(join(projectRoot, "sfdx-project.json"), "utf8")
);
const scratchDefinition = JSON.parse(
  readFileSync(join(projectRoot, "config/project-scratch-def.json"), "utf8")
);
const manifest = readFileSync(
  join(projectRoot, "manifest/package.xml"),
  "utf8"
);

assert.equal(project.name, "hackathon-salesforce");
assert.equal(project.packageDirectories?.length, 1);
assert.equal(project.packageDirectories[0].path, "force-app");
assert.equal(project.packageDirectories[0].default, true);
assert.match(project.sourceApiVersion, /^\d+\.\d+$/);
assert.equal(scratchDefinition.edition, "Developer");
assert(
  manifest.includes(`<version>${project.sourceApiVersion}</version>`),
  "manifest/package.xml must use the same API version as sfdx-project.json"
);

console.log(
  `Salesforce DX project is valid (API ${project.sourceApiVersion}, package force-app).`
);
