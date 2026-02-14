#!/usr/bin/env bash
set -euo pipefail

readme_path="${1:-README.md}"

if [[ ! -f "$readme_path" ]]; then
  echo "ERROR: README file not found: $readme_path" >&2
  exit 1
fi

required_en=(
  "## English"
  "### Project Description"
  "### Features"
  "### Quick Start"
  "### Skill Catalog"
  "### Project Structure"
  "### Configuration"
  "### Development and Testing"
  "### Contributing"
  "### Maintenance Guide"
  "### License"
)

required_zh=(
  "## 简体中文"
  "### 项目说明"
  "### 功能特性"
  "### 快速开始"
  "### 技能目录"
  "### 项目结构"
  "### 配置"
  "### 开发与测试"
  "### 贡献指南"
  "### 维护指南"
  "### 许可证"
)

missing=0

for heading in "${required_en[@]}"; do
  if ! grep -Fqx "$heading" "$readme_path"; then
    echo "MISSING (EN): $heading" >&2
    missing=1
  fi
done

for heading in "${required_zh[@]}"; do
  if ! grep -Fqx "$heading" "$readme_path"; then
    echo "MISSING (ZH): $heading" >&2
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Bilingual README parity check failed." >&2
  exit 1
fi

echo "Bilingual README parity check passed."
