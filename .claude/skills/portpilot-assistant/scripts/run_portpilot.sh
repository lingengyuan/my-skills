#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUNDLED_CLI="${SKILL_DIR}/assets/portpilot/bin/portpilot.js"

if [[ -f "${BUNDLED_CLI}" ]]; then
  exec node "${BUNDLED_CLI}" "$@"
else
  echo "ERROR: bundled PortPilot CLI not found: ${BUNDLED_CLI}" >&2
  exit 1
fi
