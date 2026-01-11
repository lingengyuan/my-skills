# Canvas Artifact Map Generation Template

## Purpose
Create an **artifact map** focusing on **inputs/outputs and produced files**.
This template is for “what gets generated and where”, not detailed execution timing.

---

## Columns (Left → Right)
Create these 3 columns:
1) 输入 (Inputs)
2) 处理 (Processing)
3) 产物 (Outputs)

### Standard Coordinates
- Column X positions:
  - 输入: x=0
  - 处理: x=420
  - 产物: x=840
- Node width=360, height=120
- y positions: 0, 150, 300, 450 ... (consistent spacing)

---

## Required Nodes (Fixed IDs)
Inputs:
- art-input-user (text): user_prompt / optional_context_files

Processing:
- art-process-classify (text): intent classification (title/folder/diagram_type/artifact_plan)
- art-process-md (text): obsidian-markdown generates note.md
- art-process-canvas (text): json-canvas generates diagram.canvas (if selected)
- art-process-base (text): obsidian-bases generates table.base (if selected)

Outputs:
- art-out-note (text): note.md
- art-out-meta (text): meta.json
- art-out-canvas (text): diagram.canvas (optional)
- art-out-base (text): table.base (optional)
- art-out-root (text): root_dir = outputs/<folder>/<title>/

Optional: wrap output nodes in a group node with label “outputs/<folder>/<title>/”.

---

## Edge Pattern (Mandatory)
- art-input-user → art-process-classify
- art-process-classify → art-process-md
- art-process-md → art-out-note
- art-process-classify → art-process-canvas (conditional)
- art-process-canvas → art-out-canvas (conditional)
- art-process-classify → art-process-base (conditional)
- art-process-base → art-out-base (conditional)
- art-out-note → art-out-meta
- art-out-meta → art-out-root
- art-out-canvas → art-out-root (conditional)
- art-out-base → art-out-root (conditional)

Use edge labels sparingly (e.g., “生成”, “写入”).

---

## Strict Constraints
- Text nodes MUST use {"type":"text","text":"..."}. No "label" for text nodes.
- IDs MUST match the fixed IDs above.
- Do not mix with swimlanes; keep columnar artifact map style.
