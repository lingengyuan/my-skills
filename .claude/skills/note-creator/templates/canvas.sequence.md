# Canvas Sequence (Swimlane) Generation Template

## Purpose
Create a **sequence / swimlane** diagram that communicates **execution order** and **cross-skill collaboration**.

Hard rule: This is a **sequence diagram** (messages). Do NOT turn it into a step-by-step flowchart or an artifact/dataflow diagram.

---

## Lanes (Fixed Columns)
Create EXACTLY these 4 lanes, left-to-right:
1) 用户
2) note-creator
3) obsidian-markdown
4) json-canvas

Each lane MUST have:
- A **header** text node (lane title)
- A **lifeline** text node (a thin vertical line placeholder)

### Standard Coordinates
- Lane X positions:
  - 用户: x=0
  - note-creator: x=320
  - obsidian-markdown: x=640
  - json-canvas: x=960
- Header node: width=260, height=60, y=0
- Lifeline node: width=20, height=980, y=70, x = lane_x + 120

### Lane Node IDs (Fixed)
Headers:
- lane-user
- lane-note-creator
- lane-obsidian-markdown
- lane-json-canvas

Lifelines:
- life-user
- life-note-creator
- life-obsidian-markdown
- life-json-canvas

---

## Message Nodes (Must be "messages", not "steps")
Represent each interaction with a **text node** near the sender lane, then connect it to the receiver lane using an edge.

### Standard Message Node Geometry
- width=260, height=70
- y positions (top-down): 120, 240, 360, 480, 600

### Required Message Nodes (IDs + Intended Meaning)
You MUST create these message nodes (Chinese preferred, short text):

1) msg-req
- Lane: 用户 (x=0)
- Text: “创建笔记请求”

2) msg-classify
- Lane: note-creator (x=320)
- Text: “识别类型 & 确定目录”

3) msg-md-call
- Lane: note-creator (x=320)
- Text: “调用生成 Markdown”

4) msg-md-done
- Lane: obsidian-markdown (x=640)
- Text: “返回 Markdown 结果”

5) msg-canvas-call
- Lane: note-creator (x=320)
- Text: “调用生成可视化（可选）”

6) msg-canvas-done
- Lane: json-canvas (x=960)
- Text: “返回可视化结果”

7) msg-done
- Lane: note-creator (x=320)
- Text: “完成并输出到目标目录”

---

## Edge Connection Pattern (Mandatory)
Create cross-lane edges in this order (labels recommended, keep them semantic-level):

1) msg-req  → msg-classify
- fromSide=right, toSide=left
- label: “请求”

2) msg-md-call → msg-md-done
- fromSide=right, toSide=left
- label: “调用”

3) msg-md-done → msg-done
- fromSide=right, toSide=left
- label: “返回结果”

4) msg-canvas-call → msg-canvas-done
- fromSide=right, toSide=left
- label: “调用（可选）”

5) msg-canvas-done → msg-done
- fromSide=left, toSide=right
- label: “返回结果”

Optional but allowed (keep minimal):
- msg-classify → msg-md-call (label: “继续”)
- msg-classify → msg-canvas-call (label: “需要可视化则调用”)
- msg-done → lane-user (or msg-req) (label: “完成”)

### Strict prohibitions for edges/labels
- Do NOT mention filenames or artifacts in labels:
  - forbidden: "note.md", "meta.json", "diagram.canvas", "table.base"
- Do NOT add "生成计划/判断路由/格式化组织" as separate edges; keep internal details out of the sequence diagram.

---

## Minimum Node/Edge Count
- Nodes: at least 15 (4 headers + 4 lifelines + 7 messages)
- Edges: at least 7 (5 cross-lane + up to 2 optional)

---

## Strict Constraints
- Text nodes MUST use {"type":"text","text":"..."}.
- IDs MUST match the fixed IDs above (do not invent random IDs).
- Keep the layout readable (no overlapping nodes).
