# Canvas Flowchart Generation Template

## Purpose
Create a **procedural flowchart** showing step-by-step logic, decision branching, and state transitions for a process or algorithm.

---

## Standard Layout Coordinates

### Main Flow (Top-Down or Left-to-Right)
- Center X: `350` (for vertical flow)
- Node width: `260 ~ 300`, height: `80 ~ 110`
- Vertical gap: `60 ~ 80px` between consecutive steps

```text
1. Trigger / Start:       y = 0
2. Pre-check / Input:     y = 150
3. Decision / Branch:     y = 300
   ├── Branch A (Yes/True):   x = 100, y = 450
   └── Branch B (No/False):  x = 600, y = 450
4. Processing / Action:   y = 620
5. Terminal / Outcome:    y = 780
```

### Color Scheme (Obsidian Canvas Color Codes)
- **Start / Input**: `color: "6"` (Purple)
- **Processing Steps**: `color: "3"` (Yellow)
- **Decision / Gate**: `color: "2"` (Orange)
- **Success / Positive Outcome**: `color: "4"` (Green)
- **Failure / Abort**: `color: "1"` (Red)
- **Neutral / Informational**: `color: "5"` (Cyan)

---

## Semantic Node IDs

Name nodes according to their actual procedural role in the user's domain:
- `step-01-start`
- `step-02-<action>`
- `decision-<condition>`
- `branch-<outcome-a>`
- `branch-<outcome-b>`
- `step-final-<success/failure>`

Node text formatting:
```markdown
### [Step Title]
Short explanation of the action or check
- Detail or condition
```

---

## Edge Connection Patterns

- Vertical flow for sequential steps:
  `fromNode: "step-01"`, `toNode: "step-02"`, `fromSide: "bottom"`, `toSide: "top"`
- Decision branching:
  - Yes branch: `fromSide: "left"`, `toSide: "top"`, `label: "Yes / 符合条件"`
  - No branch: `fromSide: "right"`, `toSide: "top"`, `label: "No / 异常或跳过"`
- Reconvergence: Branch nodes connect into the downstream action or terminal node.

---

## Canvas Constraints

- Text nodes MUST use `{"type": "text", "text": "..."}`. Never use `"label"` on text nodes.
- Edges MUST use `"fromNode"` and `"toNode"` (never `"from"` or `"to"`).
- Keep layout balanced and legible without overlapping lines.
