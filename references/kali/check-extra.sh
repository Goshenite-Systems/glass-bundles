#!/usr/bin/env bash
set -uo pipefail
for p in gobuster netcat traceroute whois wireshark-cli; do
  if dnf5 -q info "$p" >/dev/null 2>&1; then echo "OK   $p"; else echo "MISS $p"; fi
done
