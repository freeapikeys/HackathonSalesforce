#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

./scripts/check-dev-tools.sh

if ! bd where >/dev/null 2>&1; then
  if [ -d .beads/dolt/hfs ]; then
    printf "Beads data exists but cannot be opened. Run: bd doctor\n" >&2
    exit 1
  fi

  if [ -s .beads/issues.jsonl ]; then
    bd init --force --prefix hfs --from-jsonl --skip-hooks --stealth
  else
    bd init --force --prefix hfs --skip-hooks --stealth
  fi
fi

if bd hooks install >/dev/null 2>&1; then
  printf "ok   %-12s installed\n" "bd-hooks"
else
  printf "info %-12s could not install automatically\n" "bd-hooks"
fi

printf "\n"
bd status
printf "\nReady work:\n"
bd ready
