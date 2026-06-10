import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { delimiter, join } from "node:path";

const root = join(import.meta.dirname, "..");
const candidates = [
  process.env.PYTHON,
  join(root, ".venv", "Scripts", "python.exe"),
  join(root, ".venv", "bin", "python"),
  "python3",
  "python"
].filter(Boolean);

function canRun(command) {
  if (command.includes("\\") || command.includes("/")) {
    return existsSync(command);
  }
  const result = spawnSync(command, ["--version"], {
    cwd: root,
    stdio: "ignore",
    shell: false
  });
  return result.status === 0;
}

const python = candidates.find(canRun);

if (!python) {
  console.error("Unable to find a Python runtime for North Star scripts.");
  process.exit(1);
}

function withPythonPath(pathValue) {
  return {
    PYTHONPATH: [join(root, pathValue), process.env.PYTHONPATH]
      .filter(Boolean)
      .join(delimiter)
  };
}

const task = process.argv[2];
const rest = process.argv.slice(3);

const tasks = {
  agentforce: [
    ["scripts/generate_agentforce_contract.py", "--check"],
    ["scripts/validate_agentforce_contract.py"]
  ],
  events: [["scripts/validate_event_contract.py"]],
  harness: [["scripts/e2e_harness.py", ...rest]],
  "harness-tests": [
    ["-m", "unittest", "discover", "-s", "scripts/tests", "-p", "test_*.py"]
  ],
  metadata: [["scripts/generate_core_salesforce_metadata.py", "--check"]],
  models: [
    ["scripts/generate_model_gateway_contract.py", "--check"],
    ["scripts/validate_model_gateway_contract.py"],
    [
      "-m",
      "unittest",
      "discover",
      "-s",
      "intelligence/model-gateway/tests",
      "-p",
      "test_*.py",
      { env: withPythonPath("intelligence/model-gateway/runtime") }
    ]
  ],
  mulesoft: [
    ["scripts/generate_mulesoft_contract.py", "--check"],
    ["scripts/validate_mulesoft_contract.py"],
    [
      "-m",
      "unittest",
      "discover",
      "-s",
      "mulesoft/tests",
      "-p",
      "test_*.py",
      { env: withPythonPath("mulesoft") }
    ]
  ],
  ontology: [["scripts/validate_ontology.py"]]
};

if (!tasks[task]) {
  console.error(`Unknown Python task: ${task ?? "(missing)"}`);
  console.error(`Known tasks: ${Object.keys(tasks).sort().join(", ")}`);
  process.exit(1);
}

for (const command of tasks[task]) {
  const maybeOptions = command[command.length - 1];
  const hasOptions =
    typeof maybeOptions === "object" && !Array.isArray(maybeOptions);
  const args = hasOptions ? command.slice(0, -1) : command;
  const result = spawnSync(python, args, {
    cwd: root,
    env: {
      ...process.env,
      ...(hasOptions ? maybeOptions.env : {})
    },
    stdio: "inherit",
    shell: false
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}
