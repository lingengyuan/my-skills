---
name: readme-maintainer
description: Update, rewrite, or generate a project README from current repository facts. Use for README.md maintenance, install/usage refreshes, project documentation, bilingual alignment, command verification, and keeping documentation synchronized with code.
---

# README Maintainer

Treat repository files as the source of truth. This Skill uses only its bundled scripts and the current assistant model.

## Workflow

1. Resolve the target repository and README path.
2. Read the existing README before proposing changes.
3. Collect facts:

```bash
bash "<skill-dir>/scripts/collect_repo_facts.sh" "<repo-path>"
```

4. Read only authoritative files needed to verify purpose, prerequisites, configuration, commands, tests, and structure.
5. Preserve useful user-authored sections. Remove stale claims instead of replacing them with guesses.
6. Match the existing README language. Use bilingual output only when the repository is already bilingual or the user requests it.
7. Verify every documented path and command.
8. For bilingual files, run:

```bash
bash "<skill-dir>/scripts/check_bilingual_readme.sh" README.md
```

9. Re-read the final README and report changed sections plus unresolved facts.

## Rules

- Do not invent compatibility, metrics, deployment status, or test results.
- Distinguish a command documented from a command executed successfully.
- Keep the structure proportional to the project; omit empty boilerplate sections.
- Read [references/readme-checklist.md](references/readme-checklist.md) before a full rewrite.
