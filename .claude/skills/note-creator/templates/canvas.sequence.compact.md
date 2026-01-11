# Canvas Sequence (Compact / Presentation)

## Purpose
Create a **clean, presentation-quality sequence diagram** that shows
**who talks to whom, and in what order**.

This diagram is for:
- documentation
- sharing
- explanation
- public-facing materials

Clarity and visual balance are more important than completeness.

---

## Lanes (Fixed)
Create EXACTLY these 4 lanes, left-to-right:
1) 用户
2) note-creator
3) obsidian-markdown
4) json-canvas

Each lane MUST have:
- a header text node
- a single lifeline text node

### Coordinates
- Lane X:
  - 用户: 0
  - note-creator: 320
  - obsidian-markdown: 640
  - json-canvas: 960
- Header: width=240, height=56, y=0
- Lifeline: width=16, height=900, y=70, x = lane_x + 112

---

## Message Nodes (Very Limited)

### Strict Rules
- Max **6 message nodes total**
- Each node:
  - one short sentence only
  - no parameters
  - no bullet points
  - no file names
- Recommended: ≤ 10 Chinese characters

### Geometry
- width = 240
- height = 56
- y positions: 120, 220, 320, 420, 520, 620

---

## Required Messages (IDs fixed)

1) msg-request  
用户  
Text: “创建笔记请求”

2) msg-md-call  
note-creator  
Text: “请求生成 Markdown”

3) msg-md-return  
obsidian-markdown  
Text: “返回 Markdown”

4) msg-canvas-call  
note-creator  
Text: “请求生成可视化”

5) msg-canvas-return  
json-canvas  
Text: “返回可视化结果”

6) msg-done  
note-creator  
Text: “完成”

---

## Edges (Mandatory)

All edges MUST be:
- straight
- horizontal
- left-to-right or right-to-left only

### Order

1) msg-request → msg-md-call  
label: “请求”

2) msg-md-call → msg-md-return  
label: “调用”

3) msg-md-return → msg-done  
label: “返回”

4) msg-canvas-call → msg-canvas-return  
label: “调用（可选）”

5) msg-canvas-return → msg-done  
label: “返回”

Optional:
- msg-done → lane-user  
label: “完成”

---

## Absolute Prohibitions
- No filenames
- No implementation details
- No routing / planning / saving steps
- No diagonal or curved edges
- No node height variation

This diagram must look **simple, calm, and balanced**.
