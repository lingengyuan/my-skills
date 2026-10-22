---
name: note-creator
description: Create structured Obsidian note packages containing Markdown notes, metadata, and optional JSON Canvas or Obsidian Base files. Use when taking notes, saving knowledge, documenting concepts, building comparison matrices, or organizing research into an Obsidian vault.
---

# Note Creator Skill

Generate structured Obsidian note packages with clean Markdown, metadata, and optional spatial Canvas diagrams or Base database views. Obsidian Markdown, JSON Canvas, and Obsidian Bases conventions are assumed knowledge.

## Package Structure

```text
<vault-root>/<folder>/<title>/
├── note.md             # Core Markdown note with YAML frontmatter
├── meta.json           # Package metadata and artifact manifest
├── diagram.canvas      # Optional JSON Canvas diagram
├── table.base          # Optional Obsidian Base table view
└── compare/            # Optional item notes (for comparison mode)
    ├── item-1.md
    └── item-2.md
```

## Workflow

1. **Analyze input**: Read user prompt, source files, or reference links. Identify core concepts and target vault location.
2. **Classify intent**: Select target folder and artifact plan using [rules/classify.intent.md](rules/classify.intent.md).
3. **Choose artifact plan**:
   - Always create `note.md`.
   - Add `diagram.canvas` only when spatial relationships, timelines, or sequence flows provide clear visual value.
   - Add `table.base` only when multiple structured items need querying, filtering, or sorting.
4. **Resolve directory & title**: Sanitize the title and select an authorized folder using [rules/folders.md](rules/folders.md) and [rules/naming.rules.md](rules/naming.rules.md). Target directory format: `<vault>/<folder>/<title>/`.
5. **Generate artifacts**:
   - **Markdown (`note.md`)**: Start with valid YAML frontmatter. Structure sections based on evidence in the source material. Follow [templates/note.md.prompt](templates/note.md.prompt).
   - **Canvas (`diagram.canvas`)**: Generate valid JSON Canvas with unique node IDs grounded in user domain entities. Follow the matching template in `templates/canvas.<type>.md`. Use `fromNode` and `toNode` for all edges. Never use `from` or `to`.
   - **Base (`table.base`)**: Generate valid YAML with scoped filters. For comparisons, create items in `compare/` using [templates/compare.item.md](templates/compare.item.md) and scope the Base to that subfolder.
6. **Write metadata (`meta.json`)**: Generate a clean, verifiable manifest containing title, folder, tags, timestamps, summary, and relative file paths per [rules/output.contract.md](rules/output.contract.md). Do not include hallucinated SHA-256 hashes, fake Git revisions, or internal agent provenance.
7. **Verify package**: Re-read all generated files. Verify JSON and YAML syntax, verify file references, and report file paths.

## Guidelines & Boundaries

- **Preserve existing files**: Never overwrite an existing note package unless explicitly directed. Inspect existing folder contents before writing.
- **Minimal artifacts**: Do not create Canvas or Base files merely to generate more files. Every artifact must provide clear informational value.
- **Scoped destinations**: Write only within the designated vault or output directory.

## Verification Checklist

Before completing the task, verify:

1. `note.md` has valid YAML frontmatter and structured content.
2. Any `.canvas` file parses as valid JSON with valid node IDs and matching edge connections.
3. Any `.base` file parses as valid YAML and defines at least one working view.
4. `meta.json` exists, parses as valid JSON, and contains accurate relative paths to all generated files.
5. No temporary files or incomplete scaffolds remain in the package directory.
