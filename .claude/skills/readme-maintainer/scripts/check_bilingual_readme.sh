#!/usr/bin/env bash
set -euo pipefail

readme_path="${1:-README.md}"

if [[ ! -f "$readme_path" ]]; then
  echo "ERROR: README file not found: $readme_path" >&2
  exit 1
fi

if ! grep -Fqx "## English" "$readme_path"; then
  echo "MISSING: ## English" >&2
  exit 1
fi

if ! grep -Fqx "## 简体中文" "$readme_path"; then
  echo "MISSING: ## 简体中文" >&2
  exit 1
fi

en_count="$(awk '
  /^## English$/ { section="en"; next }
  /^## 简体中文$/ { section="zh"; next }
  section == "en" && /^### / { count++ }
  END { print count + 0 }
' "$readme_path")"

zh_count="$(awk '
  /^## English$/ { section="en"; next }
  /^## 简体中文$/ { section="zh"; next }
  section == "zh" && /^### / { count++ }
  END { print count + 0 }
' "$readme_path")"

if [[ "$en_count" -eq 0 || "$zh_count" -eq 0 || "$en_count" -ne "$zh_count" ]]; then
  echo "Bilingual README section counts differ: English=$en_count Chinese=$zh_count" >&2
  exit 1
fi

echo "Bilingual README parity check passed: $en_count sections per language."
