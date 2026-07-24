#!/usr/bin/env bash
# Bulk-check which Kali tools exist as Fedora RPMs (R1 triage at scale).
set -uo pipefail
while IFS= read -r p; do
  [ -z "$p" ] && continue
  if dnf5 -q info "$p" >/dev/null 2>&1; then
    echo "OK   $p"
  else
    echo "MISS $p"
  fi
done < /all-tools.txt
