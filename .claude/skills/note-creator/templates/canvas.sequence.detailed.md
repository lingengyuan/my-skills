# Canvas Sequence (Detailed / Internal)

## Purpose
Create a **detailed sequence diagram** explaining execution order
and responsibility boundaries between skills.

This diagram is for internal understanding, not for presentation.

---

## Lanes
用户 | note-creator | obsidian-markdown | json-canvas

(same coordinates and lifeline rules as compact version)

---

## Message Rules
- Message nodes represent **calls or responses**
- Internal logic may appear, but must stay abstract
- File names are allowed but should be minimal
- Node count should not exceed 10

---

## Typical Messages (Examples)
- 创建笔记请求
- 识别类型与目录
- 调用生成 Markdown
- 返回 Markdown（含 frontmatter）
- 判断是否需要可视化
- 调用 json-canvas
- 返回可视化结果
- 输出到目标目录

---

## Edges
- Horizontal preferred
- Vertical offset allowed
- Avoid crossing when possible

---

## Guidance
This diagram may trade beauty for completeness,
but must still clearly communicate:
- who initiates
- who processes
- who responds
