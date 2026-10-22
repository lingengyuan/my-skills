# Canvas Sequence (Compact / Presentation)

## Purpose
Create a **clean, presentation-quality sequence diagram** showing **who talks to whom, and in what order** for high-level comprehension and public-facing notes.

Clarity, brevity, and visual balance are preferred over exhaustive implementation details.

---

## Swimlane Setup

- Derive 2 to 4 primary actors/roles from the topic (e.g. `Client`, `Gateway`, `Service`, `Database`).
- Standard Lane Spacing: `X = lane_index * 300` (e.g., `0`, `300`, `600`, `900`).
- Header Node: `width = 220`, `height = 50`, `y = 0`.
  ID: `lane-<actor-slug>`.
- Lifeline Node: `width = 16`, `height = 650`, `y = 65`, `x = lane_x + 102`.
  ID: `life-<actor-slug>`.

---

## Compact Message Rules

- Limit total messages to **4 to 6 critical interactions**.
- Each message node contains 1 concise line (≤ 15 characters).
- Node dimensions: `width = 200`, `height = 45`.
- Vertical step: `y = 100, 190, 280, 370, 460, 550`.
- Message IDs: `msg-01-<slug>`, `msg-02-<slug>`...

---

## Edge Connections

- Directed edges from sender to receiver with short semantic labels (e.g., `请求`, `验证`, `查询`, `返回`).
- Text nodes MUST use `{"type": "text", "text": "..."}`.
- All edges use `"fromNode"` and `"toNode"`.
