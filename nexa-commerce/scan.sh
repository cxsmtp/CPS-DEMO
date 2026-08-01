#!/usr/bin/env bash
# Nexa Commerce - Checkmarx One scan.
#
# Run from the repository root with the cx CLI already configured
# (cx configure show / cx auth validate).
set -euo pipefail

PROJECT_NAME="${1:-Nexa-Commerce}"
BRANCH="${2:-main}"

echo "[scan] project=${PROJECT_NAME} branch=${BRANCH}"
cx scan create \
  --project-name "${PROJECT_NAME}" \
  --branch "${BRANCH}" \
  -s . \
  --scan-types "sast,sca,iac-security,containers,apisec" \
  --file-filter '!**/node_modules/**,!**/target/**,!**/.git/**' \
  --scan-info-format json

echo
echo "[scan] when it completes, export and verify:"
echo "  cx results show --scan-id <SCAN_ID> --report-format json --output-name nexa-results"
echo "  python verify_chains.py nexa-results.json"
