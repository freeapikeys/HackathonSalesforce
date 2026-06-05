#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v node >/dev/null 2>&1 || {
  printf "Node.js 20 or newer is required.\n" >&2
  exit 1
}
command -v npm >/dev/null 2>&1 || {
  printf "npm is required.\n" >&2
  exit 1
}
command -v python3 >/dev/null 2>&1 || {
  printf "Python 3.12 or newer is required.\n" >&2
  exit 1
}

node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 20 ? 0 : 1)' || {
  printf "Node.js 20 or newer is required.\n" >&2
  exit 1
}
python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 12))' || {
  printf "Python 3.12 or newer is required.\n" >&2
  exit 1
}

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -r requirements-dev.txt
npm ci

printf "\nRuntime dependencies are ready. Run: npm run check\n"
