import { existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

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
  console.error("Unable to find a Python runtime for Agentforce validation.");
  process.exit(1);
}

for (const args of [
  ["scripts/generate_agentforce_contract.py", "--check"],
  ["scripts/validate_agentforce_contract.py"]
]) {
  const result = spawnSync(python, args, {
    cwd: root,
    stdio: "inherit",
    shell: false
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}
