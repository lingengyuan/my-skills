# Output Contract (v3.1)

## Required Files
- `note.md`: Core markdown note with frontmatter.
- `meta.json`: Clean machine-readable package manifest.

## Optional Files (Generated only when explicitly valuable)
- `diagram.canvas`: JSON Canvas diagram for spatial workflows or architectures.
- `table.base`: Obsidian Base view for queryable tabular comparisons.
- `compare/`: Subdirectory containing item notes when `base_mode: comparison` is active.

---

## meta.json Schema

`meta.json` MUST include:
- `schema_version`: "3.1"
- `id`: unique note identifier (e.g. `nc_YYYYMMDD_<slug>`)
- `title`: human-readable title
- `folder`: whitelisted category folder
- `diagram_type`: "none" | "flowchart" | "sequence" | "architecture" | "artifact"
- `artifact_plan`: array containing `"md"` and any generated optional artifacts (`"canvas"`, `"base"`)
- `tags`: relevant category tags
- `created`: creation date (YYYY-MM-DD)
- `modified`: modification date (YYYY-MM-DD)
- `summary`: concise single-sentence summary of the note
- `paths`: file paths relative to the package directory itself (e.g. `"note": "note.md"`, `"canvas": "diagram.canvas"` or `null`, `"base": "table.base"` or `null`, `"meta": "meta.json"`)

Do NOT hallucinate cryptographic SHA-256 hashes, fake Git revisions, or internal agent provenance in `meta.json`. Keep metadata strictly practical and verifiable.

---

## Canvas Rules
- Text nodes MUST use:
  - `"type": "text"`
  - `"text": "<content>"`
- `"label"` MUST NOT be used for text nodes.
- Edges MUST use `"fromNode"` and `"toNode"` (never `"from"` or `"to"`).
- Canvas JSON MUST be valid for Obsidian Canvas.
- Nodes and edges must reflect the actual topic domain, never orchestrator internals.

---

## Base Rules
- `sources` and `file.inFolder()` filter MUST be scoped to the package directory relative to vault root:
  `<folder>/<title>/` or `<folder>/<title>/compare/`
- Non-markdown files (`.png`, `.json`, `.canvas`) MUST be excluded.
- Base MUST define at least one usable view with valid YAML.

---

## Consistency
- `artifact_plan` and `paths` MUST accurately match actual generated files on disk.
- Writing files to disk is mandatory; generating JSON responses without writing is invalid.
