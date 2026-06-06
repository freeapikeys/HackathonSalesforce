#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

"$PYTHON" "$ROOT/scripts/generate_mulesoft_contract.py" --check
"$PYTHON" "$ROOT/scripts/validate_mulesoft_contract.py"
