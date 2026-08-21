#!/bin/bash
# Builds SipMate.app - a standalone macOS app bundle, no Python install required
# to run it. Output goes to dist/SipMate.app (gitignored; rebuild whenever you
# want a fresh copy, e.g. after code changes).
#
# Usage:
#   pip install pyinstaller
#   ./scripts/build_app.sh
#
# Then either double-click dist/SipMate.app, or drag it into /Applications.

set -euo pipefail
cd "$(dirname "$0")/.."

pyinstaller \
  --name "SipMate" \
  --icon "assets/icon/SipMate.icns" \
  --windowed \
  --noconfirm \
  --add-data "assets:assets" \
  --add-data "characters/manifests:characters/manifests" \
  --add-data "sounds/effects:sounds/effects" \
  --collect-all rlottie_python \
  main.py

echo ""
echo "Built: dist/SipMate.app"
