---
name: readme-maintainer
description: Update, rewrite, or generate concise, publication-ready project READMEs from current repository facts. Use for README maintenance, install and usage refreshes, command verification, and existing bilingual alignment.
---

# README Maintainer

Treat repository files as the source of truth. Write a standalone entry point that tells readers what the project does and how to install, configure, and use it.

## Workflow

1. Resolve the repository and README path; read the existing README.
2. Collect only the facts needed for the change. For broad updates, use:

```bash
bash "<skill-dir>/scripts/collect_repo_facts.sh" "<repo-path>"
```

3. Verify purpose, prerequisites, examples, configuration, and commands against authoritative files. Preserve useful user-authored content; remove stale claims rather than guessing.
4. Match the existing language. Use bilingual output only when already present or requested.
5. Keep the main installation path, a working usage example, common operations, and essential constraints. Link detailed configuration, architecture, exhaustive options, and development procedures to existing documentation instead of duplicating them. Verify that each destination actually covers the referenced topic.
6. Apply the publication pass below, then verify paths, command syntax, and semantic preservation. Execute commands only when appropriate to the task; distinguish source verification from successful execution.
7. For bilingual files, check semantic parity and run:

```bash
bash "<skill-dir>/scripts/check_bilingual_readme.sh" README.md
```

8. Report the completed change and material unresolved facts briefly, outside the README.

Read [references/readme-checklist.md](references/readme-checklist.md) before a full rewrite.

## Publication pass

- Delete before rewriting: remove a sentence if its absence does not impair understanding, setup, operation, or verification.
- Describe the product and its current behavior directly. Remove author reasoning, review history, temporary work status, defensive explanations, rhetorical transitions, and repeated claims.
- Express responsibilities through their owners and operational warnings as concrete rules. Preserve real prohibitions, safety constraints, compatibility conditions, and recovery limits.
- Keep each fact in one authoritative place. Prefer a short paragraph, runnable example, or compact table over repeated explanations.
- Use only sections the reader needs; a README is not a complete manual. Do not impose a fixed word count, reduction percentage, section template, or mandatory project tree.
- Preserve enough context for a new reader to act. Correctness, necessary completeness, and usability take priority over brevity.

## Evidence rules

- Do not invent compatibility, metrics, deployment status, or test results.
- Keep internal checks and editing history out of the final document. Include validation commands or supported behavior only when useful to project readers.
- A full rewrite must retain essential setup steps, technical contracts, and operational constraints, either directly or through verified documentation links.
