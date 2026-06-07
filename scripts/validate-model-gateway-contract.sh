#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

"$PYTHON" "$ROOT/scripts/generate_model_gateway_contract.py" --check
"$PYTHON" "$ROOT/scripts/validate_model_gateway_contract.py"
PYTHONPATH="$ROOT/intelligence/model-gateway/runtime" \
  "$PYTHON" -m unittest discover \
  -s "$ROOT/intelligence/model-gateway/tests" \
  -p "test_*.py"
