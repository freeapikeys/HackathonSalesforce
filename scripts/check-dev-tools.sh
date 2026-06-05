#!/usr/bin/env bash

set -u

failures=0

check_tool() {
  local name="$1"
  local command_name="$2"
  local install_url="$3"

  if command -v "$command_name" >/dev/null 2>&1; then
    printf "ok   %-12s %s\n" "$name" "$("$command_name" --version 2>/dev/null | head -n 1)"
  else
    printf "miss %-12s %s\n" "$name" "$install_url"
    failures=$((failures + 1))
  fi
}

check_tool "git" "git" "https://git-scm.com/"
check_tool "gh" "gh" "https://cli.github.com/"
check_tool "sf" "sf" "https://developer.salesforce.com/tools/salesforcecli"
check_tool "bd" "bd" "https://github.com/steveyegge/beads"
check_tool "onecontext" "onecontext" "https://github.com/human-re/aline"

if command -v overstory >/dev/null 2>&1; then
  printf "ok   %-12s %s\n" "overstory" "$(overstory --version 2>/dev/null | head -n 1)"
else
  printf "info %-12s optional: https://github.com/jayminwest/overstory\n" "overstory"
fi

if [ "$failures" -gt 0 ]; then
  printf "\n%d required tool(s) missing.\n" "$failures"
  exit 1
fi

printf "\nDevelopment tools are available. Run: bd prime && bd ready\n"
