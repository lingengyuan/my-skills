#!/usr/bin/env bash
# Check that a bilingual README keeps parity between its two languages.
#
# Two layouts are supported:
#   1. One file with "## English" and "## 简体中文" sections (### counts compared).
#   2. Separate files, e.g. README.md plus README.en.md in the same directory
#      (heading counts per level compared).
# With neither layout the script exits 0: a single-language README is not an
# error.
set -euo pipefail

readme_path="${1:-README.md}"

if [[ ! -f "$readme_path" ]]; then
  echo "ERROR: README file not found: $readme_path" >&2
  exit 1
fi

dir="$(dirname "$readme_path")"

# Prints "H2 H3 H4" for one file.
heading_counts() {
  awk '
    /^## /   { h2++ }
    /^### /  { h3++ }
    /^#### / { h4++ }
    END { printf "%d %d %d\n", h2 + 0, h3 + 0, h4 + 0 }
  ' "$1"
}

if grep -Fqx "## English" "$readme_path"; then
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
  exit 0
fi

shopt -s nullglob
siblings=("$dir"/README.md "$dir"/README.*.md)
shopt -u nullglob

if [[ ${#siblings[@]} -eq 0 ]]; then
  echo "No bilingual layout detected in $readme_path; skipped."
  exit 0
fi

reference="$(heading_counts "$readme_path")"
checked=0

for sibling in "${siblings[@]}"; do
  if [[ "$(basename "$sibling")" == "$(basename "$readme_path")" ]]; then
    continue
  fi
  counts="$(heading_counts "$sibling")"
  if [[ "$counts" != "$reference" ]]; then
    echo "Bilingual README heading counts differ (H2 H3 H4):" >&2
    echo "  $(basename "$readme_path"): $reference" >&2
    echo "  $(basename "$sibling"): $counts" >&2
    exit 1
  fi
  if ! grep -q "$(basename "$sibling")" "$readme_path"; then
    echo "WARN: $(basename "$readme_path") does not link to $(basename "$sibling")" >&2
  fi
  checked=$((checked + 1))
done

if [[ "$checked" -eq 0 ]]; then
  echo "No bilingual layout detected in $readme_path; skipped."
  exit 0
fi

read -r h2 h3 h4 <<<"$reference"
echo "Bilingual README parity check passed: $(basename "$readme_path") and $checked companion file(s), $h2 H2 + $h3 H3 + $h4 H4 headings each."
