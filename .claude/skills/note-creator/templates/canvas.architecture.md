# Canvas Architecture Diagram Generation Template

## Purpose
Create a **high-level architecture diagram** showing system components, layer boundaries, and interaction dependencies for the requested topic.

This template is for structural topology and component relationships, not for sequential execution timing.

---

## Architecture Layering (Top-Down or Multi-Tier)

Derive 2 to 4 logical layers from the user's subject matter:

1. **Client / Entry Layer** (e.g., User, Web/Mobile App, External Caller)
2. **Gateway / Control Layer** (e.g., API Gateway, Load Balancer, Orchestrator)
3. **Core Services / Domain Layer** (e.g., Microservices, Processing Workers, Subsystems)
4. **Data / Storage Layer** (e.g., Database, Cache, Message Queue, File Storage)

---

## Suggested Layout Coordinates

- **Tier 1 (Entry)**: `y = 0`, centered or left-to-right
- **Tier 2 (Gateway/Control)**: `y = 180 ~ 220`
- **Tier 3 (Core Services)**: `y = 380 ~ 440`
- **Tier 4 (Data/Storage)**: `y = 600 ~ 660`

Node dimensions:
- Standard component node: `width = 240 ~ 300`, `height = 100 ~ 130`
- Horizontal spacing: `40 ~ 60px` between adjacent components
- Subsystem Group node (optional): wraps related components with clear boundary labels

---

## Node Design & IDs

Assign semantic, kebab-case IDs based on the actual components:
- `entry-<component-name>` (e.g., `entry-web-client`, `entry-cli`)
- `gateway-<name>` (e.g., `gateway-ingress`, `gateway-api`)
- `svc-<name>` (e.g., `svc-auth`, `svc-order-processor`)
- `data-<name>` (e.g., `data-primary-db`, `data-redis-cache`)
- `group-<name>` (optional group container)

Node text formatting:
```markdown
### [Component Name]
Brief role or tech stack (e.g. Go / gRPC)
- Key responsibility 1
- Key responsibility 2
```

---

## Edge Connections & Dependencies

- Connect callers to callees in the direction of data/control flow:
  `fromNode: "caller-id"`, `toNode: "callee-id"`
- Label edges with protocol, method, or data type (e.g., `HTTP / REST`, `gRPC`, `SQL`, `Pub/Sub`)
- Keep edges uncluttered: connect only authentic architectural dependencies evident in the topic.

---

## Canvas Constraints

- Text nodes MUST use `{"type": "text", "text": "..."}`. Never use `"label"` on text nodes.
- Edges MUST use `"fromNode"` and `"toNode"` (never `"from"` or `"to"`).
- JSON Canvas must be strictly valid JSON.
