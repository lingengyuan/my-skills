# Canvas Artifact Map Generation Template

## Purpose
Create an **artifact and data pipeline map** focusing on **inputs, transformation engines, and output deliverables** for data pipelines, build systems, or compiler tools.

---

## 3-Column Layout (Left → Right)

Organize nodes into three logical columns:
1. **Inputs / Raw Data Sources** (`x = 0`)
2. **Processing / Pipeline Engines** (`x = 420`)
3. **Outputs / Generated Deliverables** (`x = 840`)

### Dimensions & Spacing
- Node width: `300 ~ 340`, height: `90 ~ 130`
- Vertical gap: `40 ~ 60px` (`y = 0, 160, 320, 480...`)
- Group node (optional): Wrap output nodes in a container representing target storage or output package.

---

## Semantic Node IDs

Name nodes based on the real entities in the user's pipeline:
- Inputs: `input-<source-slug>` (e.g., `input-raw-logs`, `input-user-config`)
- Processing: `process-<engine-slug>` (e.g., `process-parser`, `process-transformer`, `process-renderer`)
- Outputs: `output-<asset-slug>` (e.g., `output-html-report`, `output-sqlite-db`, `output-json-manifest`)

Node text formatting:
```markdown
### [Artifact / Engine Name]
Format or role (e.g. `.parquet` / Spark ETL)
- Key attributes or path
```

---

## Edge Connection Patterns

Connect flow from inputs through transformers to outputs:
- `input-*` → `process-*` (label: `read / ingest`)
- `process-*` → `output-*` (label: `emit / write`)
- Keep edges horizontal (`fromSide: "right"`, `toSide: "left"`) whenever possible.

---

## Canvas Constraints

- Text nodes MUST use `{"type": "text", "text": "..."}`. Never use `"label"` on text nodes.
- Edges MUST use `"fromNode"` and `"toNode"` (never `"from"` or `"to"`).
- JSON Canvas must be strictly valid JSON.
