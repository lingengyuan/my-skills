---
name: note-creator
description: Create a complete Obsidian note package containing Markdown and, only when useful, a JSON Canvas diagram or Obsidian Base. Use when users ask to create notes, save knowledge, document concepts, compare items, or persist structured material in an Obsidian vault.
---

# Note Creator

Create and validate every artifact directly. This Skill is self-contained and does not require sibling format Skills.

## Inputs

- User content or context files.
- Target vault or output directory.
- Optional requested artifacts: Markdown, Canvas, Base.

If the destination is unclear, inspect the current workspace. Ask before writing when more than one vault is plausible.

## Workflow

1. Read the source material.
2. Classify the note using [rules/classify.intent.md](rules/classify.intent.md).
3. Choose the smallest useful artifact plan:
   - always create `note.md`;
   - add `diagram.canvas` only when relationships or sequence are materially clearer visually;
   - add `table.base` only when multiple comparable records need a database-like view.
4. Choose the folder and title with [rules/folders.md](rules/folders.md) and [rules/naming.rules.md](rules/naming.rules.md).
5. Create `<target>/<folder>/<title>/`.
6. Write and validate each artifact.
7. Write `meta.json` using [rules/output.contract.md](rules/output.contract.md).
8. Re-read the files and return their final paths.

## Markdown contract

Use [templates/note.md.prompt](templates/note.md.prompt) as guidance, not as a rigid word-count template.

- Put valid YAML frontmatter first.
- Include a concise summary and only the sections supported by the source.
- Preserve uncertainty and source attribution.
- Do not invent examples or caveats to satisfy a quota.

## Canvas contract

Use [templates/canvas.prompt](templates/canvas.prompt) only for the generic Canvas field/output contract, then select one content-specific layout template from `templates/canvas.*.md`.

- Write valid JSON Canvas with `nodes` and `edges`.
- Every edge uses `fromNode` and `toNode`; never `from` or `to`.
- IDs are unique and every edge resolves to existing nodes.
- Parse the completed JSON before finishing.

## Base contract

For comparisons, create one Markdown record per item under `compare/` using [templates/compare.item.md](templates/compare.item.md), then use [templates/base.comparison.prompt](templates/base.comparison.prompt) and scope the Base to that directory. For generic views, use [templates/base.prompt](templates/base.prompt), scope the Base to the note package directory, and include Markdown files only.

Write valid YAML and verify every referenced property or formula exists.

## Metadata contract

Use [templates/meta.json.prompt](templates/meta.json.prompt) as a schema example only. Replace its sample values with values from the current run, and compute current timestamps and fingerprints before reporting completion.

## Boundaries

- Preserve existing notes unless the user asks to replace them.
- Do not create Canvas or Base merely to produce more files.
- Do not write outside the selected destination.
