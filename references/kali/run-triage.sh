#!/usr/bin/env bash
set -uo pipefail
cd ~/goshenite/glass-bundles/references/kali
chmod +x check-fedora.sh
podman run --rm -v "$PWD/all-tools.txt:/all-tools.txt:ro" -v "$PWD/check-fedora.sh:/check-fedora.sh:ro" ghcr.io/ublue-os/aurora:stable bash /check-fedora.sh > fedora-availability.txt 2>/dev/null
echo "EXIT=$?"
echo "OK:   $(grep -c '^OK'   fedora-availability.txt)"
echo "MISS: $(grep -c '^MISS' fedora-availability.txt)"
