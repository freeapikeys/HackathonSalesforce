#!/usr/bin/env bash

set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_ORG="${HFS_TARGET_ORG:-dev-ed}"
REPOSITORY="${HFS_REPOSITORY:-$(git -C "$ROOT" config --get remote.origin.url)}"
SOURCE_REF="${HFS_REF:-$(git -C "$ROOT" branch --show-current)}"
OUTPUT="${HFS_CLEAN_CLONE_OUTPUT:-$ROOT/artifacts/clean-clone-result.json}"
KEEP_WORKDIR=false
CURRENT_STAGE="prerequisites"
SOURCE_COMMIT=""
WORK_ROOT=""

usage() {
  cat <<'EOF'
Usage: ./scripts/verify-clean-clone.sh [options]

Options:
  --target-org ALIAS    Authenticated Salesforce org alias (default: dev-ed)
  --repository URL      Git repository to clone (default: origin URL)
  --ref REF             Branch or tag to verify (default: current branch)
  --output PATH         Sanitized evidence output path
  --keep-workdir        Keep the temporary clone for diagnosis
  --help                Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-org)
      TARGET_ORG="$2"
      shift 2
      ;;
    --repository)
      REPOSITORY="$2"
      shift 2
      ;;
    --ref)
      SOURCE_REF="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --keep-workdir)
      KEEP_WORKDIR=true
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      printf "Unknown option: %s\n" "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n "$REPOSITORY" ]] || {
  printf "A repository URL is required.\n" >&2
  exit 2
}
[[ -n "$SOURCE_REF" ]] || {
  printf "A branch or tag is required.\n" >&2
  exit 2
}

mkdir -p "$(dirname "$OUTPUT")"
OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"

cleanup() {
  cd "$ROOT" 2>/dev/null || true
  if [[ -n "$WORK_ROOT" && -d "$WORK_ROOT" ]]; then
    if [[ "$KEEP_WORKDIR" == true ]]; then
      printf "Temporary clean clone kept at %s\n" "$WORK_ROOT"
    else
      rm -rf "$WORK_ROOT"
    fi
  fi
}

write_failure_evidence() {
  local exit_code=$?
  trap - ERR
  python3 - "$OUTPUT" "$CURRENT_STAGE" "$SOURCE_REF" "$SOURCE_COMMIT" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

output, stage, source_ref, source_commit = sys.argv[1:]
evidence = {
    "schemaVersion": "1.0.0",
    "status": "failed",
    "verifiedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "source": {
        "ref": source_ref,
        "commit": source_commit or None,
    },
    "failedStage": stage,
}
path = Path(output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
PY
  printf "Clean-clone verification failed during %s. Evidence: %s\n" \
    "$CURRENT_STAGE" "$OUTPUT" >&2
  exit "$exit_code"
}

trap cleanup EXIT
trap write_failure_evidence ERR

for command in git node npm python3 sf; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf "%s is required.\n" "$command" >&2
    false
  fi
done

CURRENT_STAGE="salesforce-authentication"
sf org display --target-org "$TARGET_ORG" --json >/dev/null

CURRENT_STAGE="clone"
WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/hfs-clean-clone.XXXXXX")"
CLONE_DIR="$WORK_ROOT/repository"
printf "Cloning %s at %s into a temporary workspace...\n" \
  "$REPOSITORY" "$SOURCE_REF"
git clone --quiet --single-branch --branch "$SOURCE_REF" \
  "$REPOSITORY" "$CLONE_DIR"
SOURCE_COMMIT="$(git -C "$CLONE_DIR" rev-parse HEAD)"
cd "$CLONE_DIR"

CURRENT_STAGE="bootstrap"
printf "Bootstrapping runtime dependencies...\n"
./scripts/bootstrap-runtime.sh

CURRENT_STAGE="repository-checks"
printf "Running repository checks...\n"
npm run check

CURRENT_STAGE="salesforce-deployment"
DEPLOYMENT_RESULT="$WORK_ROOT/deployment-result.json"
printf "Deploying Salesforce metadata and running Apex tests...\n"
sf project deploy start \
  --source-dir force-app \
  --target-org "$TARGET_ORG" \
  --test-level RunSpecifiedTests \
  --tests HFS_ServiceContractTest \
  --tests HFS_RelationshipServiceImplTest \
  --tests HFS_RelationshipControllerTest \
  --tests HFS_AgentActionServiceTest \
  --wait 30 \
  --json >"$DEPLOYMENT_RESULT"

CURRENT_STAGE="connected-demo"
DEMO_RESULT="$WORK_ROOT/demo-result.json"
printf "Running the connected governed vertical slice...\n"
npm run demo:run -- \
  --target-org "$TARGET_ORG" \
  --output "$DEMO_RESULT"

CURRENT_STAGE="evidence-validation"
python3 scripts/verify_clean_clone_result.py \
  --deployment-result "$DEPLOYMENT_RESULT" \
  --demo-result "$DEMO_RESULT" \
  --repository "$REPOSITORY" \
  --source-ref "$SOURCE_REF" \
  --source-commit "$SOURCE_COMMIT" \
  --output "$OUTPUT"

trap - ERR
printf "Clean-clone verification passed for %s at %s.\n" \
  "$SOURCE_REF" "$SOURCE_COMMIT"
