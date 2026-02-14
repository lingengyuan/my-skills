#!/usr/bin/env bash
set -euo pipefail

repo_path="${1:-.}"

if [[ ! -d "$repo_path" ]]; then
  echo "ERROR: repo path does not exist: $repo_path" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "ERROR: ripgrep (rg) is required." >&2
  exit 1
fi

repo_abs="$(cd "$repo_path" && pwd)"
cd "$repo_abs"

echo "## Repo"
echo "path: $repo_abs"
if [[ -d .git ]]; then
  echo "git: yes"
  echo "branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
else
  echo "git: no"
fi

echo
echo "## Top-level files"
find . -maxdepth 1 -mindepth 1 \
  -not -name ".git" \
  -printf "%P\n" | sort

echo
echo "## Project tree (depth=2)"
if command -v tree >/dev/null 2>&1; then
  tree -L 2 -a -I ".git|node_modules|dist|build|coverage|.next|.venv|venv|__pycache__|.mypy_cache|.pytest_cache"
else
  find . -maxdepth 2 \
    -not -path "./.git*" \
    -not -path "./node_modules*" \
    -not -path "./dist*" \
    -not -path "./build*" \
    -not -path "./coverage*" \
    -not -path "./.next*" \
    -not -path "./.venv*" \
    -not -path "./venv*" \
    -not -path "./__pycache__*" \
    | sed "s#^\./##" \
    | sort
fi

echo
echo "## Detected ecosystem files"
for f in \
  package.json \
  pnpm-lock.yaml \
  yarn.lock \
  pyproject.toml \
  requirements.txt \
  setup.py \
  go.mod \
  Cargo.toml \
  pom.xml \
  build.gradle \
  Makefile \
  Dockerfile \
  docker-compose.yml \
  docker-compose.yaml
do
  [[ -f "$f" ]] && echo "- $f"
done

echo
echo "## Candidate run/test commands"
if [[ -f package.json ]]; then
  echo "[package.json scripts]"
  rg -n '"(dev|start|build|test|lint|format|typecheck)"\s*:' package.json || true
fi

if [[ -f Makefile ]]; then
  echo "[Makefile targets]"
  rg -n "^[a-zA-Z0-9_.-]+:" Makefile | head -n 60 || true
fi

if [[ -f pyproject.toml ]]; then
  echo "[pyproject scripts + tool hints]"
  rg -n "^\[project\.scripts\]|^\[tool\.poetry\.scripts\]|^\[tool\.(pytest|ruff|mypy|nox)" pyproject.toml || true
fi

echo
echo "## Existing README headings"
if [[ -f README.md ]]; then
  rg -n "^#+" README.md || true
else
  echo "README.md not found"
fi

