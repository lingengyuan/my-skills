---
name: json-canvas
description: Create, edit, and validate JSON Canvas .canvas files used by Obsidian and other compatible applications. Use for visual canvases, mind maps, architecture diagrams, flowcharts, node layouts, groups, and connections.
---

# JSON Canvas

Create valid JSON Canvas 1.0 files. Read [REFERENCE.md](REFERENCE.md) for the full schema and examples when needed. Read [templates/flowchart.prompt](templates/flowchart.prompt) only when the user requests its standard vertical flowchart layout.

## Workflow

1. Read an existing canvas before editing it.
2. Preserve unrelated nodes, edges, positions, and IDs.
3. Use unique string IDs for every node and edge.
4. Avoid unintended overlaps and leave enough spacing for readable layout.
5. Write valid JSON with top-level `nodes` and `edges` arrays.
6. Parse the completed file and validate all edge references.

## Required schema

Every node contains `id`, `type`, `x`, `y`, `width`, and `height`.

- Text node: `type: "text"` and `text`
- File node: `type: "file"` and `file`
- Link node: `type: "link"` and `url`
- Group node: `type: "group"`; `label` is optional

Every edge contains `id`, `fromNode`, and `toNode`. Never use `from` or `to`.

```json
{
  "nodes": [
    {"id":"a1","type":"text","x":0,"y":0,"width":300,"height":120,"text":"Start"},
    {"id":"b1","type":"text","x":400,"y":0,"width":300,"height":120,"text":"End"}
  ],
  "edges": [
    {"id":"e1","fromNode":"a1","toNode":"b1","toEnd":"arrow"}
  ]
}
```

## Validation

- JSON parses successfully.
- IDs are unique.
- Every `fromNode` and `toNode` resolves to an existing node.
- Node-specific required fields exist.
- Coordinates and dimensions are integers.
