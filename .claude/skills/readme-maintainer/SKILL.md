---
name: readme-maintainer
description: Maintain, update, and rewrite concise, publication-ready repository README files grounded in codebase facts. Use when updating README.md, refreshing installation and usage guides, verifying CLI commands, or aligning bilingual documentation.
---

# README Maintainer

1. **Collect & Verify Facts**: Inspect manifests (`package.json`, `Cargo.toml`, `pyproject.toml`), CLI help, and configs (or run `bash "<skill-dir>/scripts/collect_repo_facts.sh" "<repo-path>"`). Never invent compatibility, benchmarks, or features; delete stale claims.
2. **Keep It Concise**: Cover only what a user needs to start—Overview (one sentence), Prerequisites & Installation, minimal Quick Start, essential Configuration, and links to deeper docs instead of duplicating them. Remove meta-discourse and duplicate definitions.
3. **Align Bilingual READMEs**: Keep identical section structure across languages and verify parity with:
   ```bash
   bash "<skill-dir>/scripts/check_bilingual_readme.sh" README.md
   ```
   (Accepts `## English` / `## 简体中文` in one file or `README.md` + `README.<lang>.md`; single-language README exits 0.)
4. **Verify**: Confirm install/run commands match build tools, CLI flags match code, and all relative links resolve.
