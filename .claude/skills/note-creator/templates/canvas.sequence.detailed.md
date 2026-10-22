# Canvas Sequence (Detailed / Deep-Dive)

## Purpose
Create a **detailed sequence diagram** explaining granular call flows, state validations, branch decisions, and error-handling paths between components for internal engineering design and deep-dive notes.

---

## Swimlane Setup

- Derive 3 to 5 actors/components from the topic (e.g. `Client`, `Ingress/Gateway`, `AuthService`, `DomainWorker`, `Storage`).
- Lane Spacing: `X = lane_index * 320`.
- Header Node: `width = 240`, `height = 55`, `y = 0`. ID: `lane-<actor-slug>`.
- Lifeline Node: `width = 16`, `height = 950`, `y = 70`, `x = lane_x + 112`. ID: `life-<actor-slug>`.

---

## Detailed Message Rules

- Message nodes represent concrete calls, callbacks, or state validations.
- Include parameters or return codes where helpful (e.g. `verifyToken(jwt) -> uid`, `200 OK {status: active}`).
- Limit total message steps to 6 ~ 10 steps to maintain readability.
- Node dimensions: `width = 240`, `height = 60 ~ 70`.
- Vertical step: `y = 120, 210, 300, 390, 480, 570, 660, 750, 840`.
- Message IDs: `msg-01-<action-slug>`, `msg-02-<action-slug>`...

---

## Edge Connections

- Horizontal preferred; vertical offset allowed when showing async or delayed response.
- Label edges with request method, payload type, or outcome status.
- Text nodes MUST use `{"type": "text", "text": "..."}`.
- All edges use `"fromNode"` and `"toNode"`.
