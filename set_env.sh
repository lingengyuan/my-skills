#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "Virtual environment not found: .venv/bin/activate" >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Virtual environment activated."
echo "Python:"
python --version
echo
echo "To deactivate, run: deactivate"
