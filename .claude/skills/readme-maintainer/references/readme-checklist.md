# README Checklist

Use this checklist before writing `README.md`.

## Grounding

- Verify every command exists in repo files (`package.json`, `Makefile`, `pyproject.toml`, scripts).
- Verify referenced paths/files exist.
- Keep versions/tool names consistent with source files.

## Core sections

- `# ProjectName` and one-sentence summary
- Features or capabilities
- Installation
- Usage / quick start
- Configuration (if env vars or config files exist)
- Development + test commands
- Contributing
- Project structure (short tree)
- License

## Bilingual parity (default)

- Include both `## English` and `## 简体中文` for user-facing project README files.
- Keep mirrored sections aligned in meaning and scope.
- If you add/remove a section in one language, mirror the same change in the other language.
- Validate headings with `scripts/check_bilingual_readme.sh README.md`.

## Writing rules

- Prefer concise, executable instructions.
- Show copy-pasteable commands.
- State prerequisites explicitly.
- Keep marketing language minimal; favor concrete behavior.

## Do not do

- Do not invent benchmarks, adoption numbers, or compatibility claims.
- Do not include commands that are not verifiable from the repo.
- Do not add sections with empty placeholders unless user asks for template-style README.
