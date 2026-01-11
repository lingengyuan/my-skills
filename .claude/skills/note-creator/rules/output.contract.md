# Output Contract (v3)

## Required Files
- note.md
- meta.json

## Optional Files
- diagram.canvas
- table.base

---

## meta.json Schema (v3 required fields)

meta.json MUST include:

- schema_version
- id
- stable_key
- title
- folder
- diagram_type
- artifact_plan
- tags
- properties
- paths
- revision
- update
- provenance

All paths MUST be consistent with the actual generated files.

---

## Canvas Rules
- Text nodes MUST use:
  - "type": "text"
  - "text": "<content>"
- "label" MUST NOT be used for text nodes.
- Canvas JSON MUST be valid for Obsidian Canvas.

---

## Base Rules
- sources MUST be scoped to the case directory only:
  outputs/<folder>/<title>/
- Non-markdown files (png/json/canvas/etc) MUST be excluded.
- Base MUST define at least one usable view.

---

## Consistency
- artifact_plan MUST reflect actual generated artifacts.
- Writing files is mandatory; generating-only is invalid.

