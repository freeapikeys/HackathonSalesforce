#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p .beads
bd export --all --output .beads/issues.jsonl

count="$(wc -l < .beads/issues.jsonl | tr -d ' ')"
printf "Exported %s Beads records to .beads/issues.jsonl\n" "$count"
