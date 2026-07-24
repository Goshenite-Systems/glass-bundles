#!/usr/bin/env bash
set -uo pipefail
cd ~/goshenite/glass-bundles/references/kali
podman run --rm -v "$PWD/check-extra.sh:/check-extra.sh:ro" ghcr.io/ublue-os/aurora:stable bash /check-extra.sh
