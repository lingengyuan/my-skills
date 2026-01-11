# Canvas Architecture Diagram Generation Template

## Purpose
Create a **high-level architecture** diagram showing **components, boundaries, and dependencies**.
This template is not for step-by-step execution flow.

---

## Required Components (Nodes)
You MUST include these components as nodes:
- 用户 (User)
- note-creator (Orchestrator)
- obsidian-markdown
- json-canvas
- obsidian-bases
- 文件系统 (outputs/<folder>/<title>/)

---

## Layout (Two Layers)
### Top layer: Control plane
- 用户
- note-creator

### Middle layer: Worker skills
- obsidian-markdown
- json-canvas
- obsidian-bases

### Bottom layer: Storage
- 文件系统 (outputs/<folder>/<title>/)

### Suggested Coordinates
- 用户: x=0, y=0, w=280, h=110
- note-creator: x=320, y=0, w=320, h=140
- obsidian-markdown: x=0, y=200, w=280, h=110
- json-canvas: x=320, y=200, w=280, h=110
- obsidian-bases: x=640, y=200, w=280, h=110
- 文件系统: x=220, y=420, w=560, h=140

---

## Fixed Node IDs
- arch-user
- arch-orchestrator
- arch-md
- arch-canvas
- arch-base
- arch-storage

Optional: one group node for “Worker Skills”:
- arch-group-workers (type: group, label: "Worker Skills")

---

## Edge Pattern (Mandatory)
Control plane:
- arch-user → arch-orchestrator (label: "user_prompt")

Orchestrator to workers:
- arch-orchestrator → arch-md (label: "generate note.md")
- arch-orchestrator → arch-canvas (label: "generate diagram.canvas")
- arch-orchestrator → arch-base (label: "generate table.base")

Workers to storage:
- arch-md → arch-storage (label: "write")
- arch-canvas → arch-storage (label: "write")
- arch-base → arch-storage (label: "write")
- arch-orchestrator → arch-storage (label: "write meta.json")

---

## Strict Constraints
- Text nodes MUST use {"type":"text","text":"..."}. No "label" for text nodes.
- IDs MUST match the fixed IDs above.
- Keep it readable: architecture = components + dependencies, not a long flow.
