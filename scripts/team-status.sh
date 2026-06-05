#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

lanes=(core integration intelligence experience)

printf "Claimable work by lane\n"
printf "======================\n"

for lane in "${lanes[@]}"; do
  printf "\n%s\n" "$lane"
  printf "%s\n" "----------------------"
  bd ready --label "lane-$lane" --plain --limit 20
done

printf "\nCheckpoint status\n"
printf "=================\n"
bd list --all --flat --no-pager --label checkpoint
