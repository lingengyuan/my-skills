# Canvas Sequence (Swimlane) Generation Template

## Purpose
Create a **sequence / swimlane diagram** that communicates **execution order** and **interaction flow** between system actors, services, or components for the requested topic.

This is a **sequence diagram** (interaction messages over time). Do NOT turn it into a static architecture map or file manifest.

---

## Swimlane Structure

Derive 2 to 5 participant lanes based on the core actors in the topic (e.g. `Client / Caller`, `Service A / Gateway`, `Service B / Worker`, `Data Store / Third-Party API`).

Lanes are arranged left-to-right in order of initiation.

Each lane consists of:
1. **Header Node**: Actor / component title
2. **Lifeline Node**: Vertical dashed or subtle line placeholder extending downwards

### Standard Lane Geometry
- Lane spacing: `X = lane_index * 320` (e.g. Lane 0: `x=0`, Lane 1: `x=320`, Lane 2: `x=640`, Lane 3: `x=960`)
- Header Node: `width = 240 ~ 280`, `height = 50 ~ 60`, `y = 0`
- Lifeline Node: `width = 16 ~ 20`, `height = 700 ~ 1000`, `y = 70`, `x = lane_x + 110`

### Lane IDs
Use semantic, predictable IDs:
- Header: `lane-<actor-slug>` (e.g., `lane-client`, `lane-gateway`, `lane-auth`, `lane-db`)
- Lifeline: `life-<actor-slug>` (e.g., `life-client`, `life-gateway`, `life-auth`, `life-db`)

---

## Interaction Messages (Nodes & Edges)

Represent each meaningful interaction step with a message node placed near the sender lane, connected via directed edges to the receiver.

### Message Node Geometry
- `width = 200 ~ 260`, `height = 50 ~ 70`
- Top-down Y progression: `y = 120, 220, 320, 420, 520, 620...` (maintain 80~120px vertical step per message)
- Position `x`: Align with the sender lane or place centered between sender and receiver lanes.

### Semantic Message Node IDs
Name messages by sequence step and intent:
- `msg-01-<action-slug>` (e.g., `msg-01-login-request`)
- `msg-02-<action-slug>` (e.g., `msg-02-verify-token`)
- `msg-03-<action-slug>` (e.g., `msg-03-fetch-profile`)
- `msg-04-<action-slug>` (e.g., `msg-04-return-response`)

Message node content:
```markdown
**[Action Name]**
Short description or payload summary
```

---

## Edge Pattern & Flow Rules

1. Connect message nodes in chronological order:
   - Call edge: sender lane / message node → target lane message node (`fromSide: "right"`, `toSide: "left"`)
   - Return edge: callee message node → caller lane (`fromSide: "left"`, `toSide: "right"`)
2. Edge Labels:
   - Use concise semantic labels (e.g., `POST /auth/token`, `Token Validated`, `Query Profile`, `200 OK`).
   - Do NOT clutter edges with excessive payload details.
3. Keep sequential order top-to-bottom so the time dimension is immediately intuitive.

---

## Canvas Constraints

- Text nodes MUST use `{"type": "text", "text": "..."}`. Never use `"label"` on text nodes.
- Edges MUST use `"fromNode"` and `"toNode"` (never `"from"` or `"to"`).
- Keep layout clean: no overlapping nodes or crossed lifelines.
