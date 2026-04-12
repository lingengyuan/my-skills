#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUNDLED_CLI="${SKILL_DIR}/assets/portpilot/bin/portpilot.js"

if [[ -f "${BUNDLED_CLI}" ]]; then
  node "${BUNDLED_CLI}" "$@"
else
  npx -y portpilot-cli@1 "$@"
fi
