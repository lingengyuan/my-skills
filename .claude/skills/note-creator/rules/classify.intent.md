# Intent Classification Rules (STRICT)

You are classifying a user's note request for the `note-creator` orchestrator.

## Output JSON Schema (STRICT)
Return ONLY valid JSON.

Base schema (always required):
{
  "title": string,
  "folder": string,
  "diagram_type": "sequence" | "flowchart" | "artifact" | "architecture" | "none",
  "artifact_plan": ["md" | "canvas" | "base"],
  "tags": [string, ...],        // length 3–8
  "properties": {
    "category": string,
    "created": "YYYY-MM-DD",
    "modified": "YYYY-MM-DD",
    "source": "user_prompt" | "file_input"
  }

  // Optional comparison extension (ONLY when comparison + base)
  // "base_mode": "comparison",
  // "comparison_items": [
  //   { "slug": string, "display_name": string }
  // ]
}

## Global Defaults (IMPORTANT)
- `artifact_plan` MUST always include "md".
- Default behavior is SIMPLE: only "md" unless there is a strong reason to add "canvas" and/or "base".
- Prefer NOT to generate optional artifacts unless the user asks, or they materially improve understanding.

---

## diagram_type Selection (choose ONE)

Choose the diagram_type that best matches the user's intent:

### sequence
Use when the user wants **execution order / collaboration / calls between components/skills**.
Keywords:
时序, sequence, 泳道, swimlane, 谁调用谁, 调用链, 协作流程, 执行顺序, interaction

### flowchart
Use when the user wants a **step-by-step process**, decision flow, or procedure.
Keywords:
流程图, flowchart, 步骤, 处理流程, 判断, if/else, 逻辑流程

### artifact
Use when the user wants a **deliverables / outputs / files relationship** view.
Keywords:
产物, 输出文件, 文件结构, outputs, note.md, meta.json, diagram.canvas, table.base

### architecture
Use when the user wants **system/component structure** and dependencies.
Keywords:
架构, architecture, 组件, 模块, 边界, 依赖, system design

### none
Use when no diagram is requested or helpful.

---

## artifact_plan Selection (DEFAULT = ["md"])

Start with:
- artifact_plan = ["md"]

Add optional artifacts ONLY when triggered:

### Add "canvas" (Obsidian Canvas)
Add "canvas" ONLY if:
- The user explicitly asks for a diagram / flowchart / canvas / visualization; OR
- `diagram_type` is not "none" AND the user intent is explanatory documentation (e.g., "说明/使用说明/分享/展示"); OR
- The request describes a complex interaction/process (4+ steps or 3+ actors) where a diagram would materially improve understanding.

Otherwise, do NOT add "canvas".

### Add "base" (Obsidian Base)
Add "base" ONLY if:
- The user explicitly asks for a table/base/database/list view; OR
- The request is clearly a structured list that benefits from querying/filtering
  (e.g., checklist, inventory, comparisons, glossary, resources list).

Otherwise, do NOT add "base".

### Ordering
- Keep the array ordered as: ["md", "canvas", "base"] if both optional items are present.

---

## Comparison Detection (IMPORTANT)
If the user request is a comparison (对比/比较/评测/选型/VS/优缺点/差异/横向比较)
AND you decided to include "base" in artifact_plan:

You MUST add:
- "base_mode": "comparison"
- "comparison_items": [...]

Do NOT generate a generic base for comparison intents.
If required comparison fields are missing, classification is INVALID.

Rules for comparison_items:
- Each item MUST have:
  - slug: lowercase-kebab-case (e.g., "obsidian-markdown")
  - display_name: short name shown to the user
- If the user explicitly listed items (A vs B vs C), use those.
- If the user said "三件套" or clearly implies the known Obsidian Skills trio, default to:
  - obsidian-markdown
  - json-canvas
  - obsidian-bases

Example:
"comparison_items": [
  { "slug": "obsidian-markdown", "display_name": "obsidian-markdown" },
  { "slug": "json-canvas", "display_name": "json-canvas" },
  { "slug": "obsidian-bases", "display_name": "obsidian-bases" }
]

---

## folder Rules (pick ONE)

**CRITICAL**: You MUST choose from the folder whitelist (see rules/folders.md).
Available folders:
- 00-Inbox
- 10-项目
- 20-阅读笔记
- 30-方法论
- 40-工具脚本
- 50-运维排障
- 60-数据与表
- 90-归档

**Classification Guidelines**:

### 30-方法论 (Preferred for comparisons, frameworks, best practices)
Use when:
- Content is about **methods, approaches, frameworks, or patterns**
- **Comparisons** (对比/比较) of tools, technologies, or approaches
- Best practices, guidelines, standards
- How-to guides, tutorials, workflows
- Templates, checklists, methodologies
- Architecture decisions, design patterns
- Skills documentation and comparisons

Examples:
- "工具对比" → 30-方法论
- "设计模式" → 30-方法论
- "最佳实践" → 30-方法论
- "开发规范" → 30-方法论
- "Obsidian Skills 三件套对比" → 30-方法论

### 40-工具脚本 (Only for actual scripts/tools)
Use when:
- Content is **actual executable code or scripts**
- Automation scripts, utilities, tools
- Configuration files
- Shell scripts, batch files, Python scripts
- Actual tool implementations

NOT for:
- Documentation about tools (use 30-方法论)
- Comparisons of tools (use 30-方法论)

### 10-项目
Use when:
- Project-specific notes and documentation
- Project plans, roadmaps, status updates
- Project-specific decisions and meeting notes

### 20-阅读笔记
Use when:
- Book notes, article summaries
- Reading highlights and annotations
- Literature reviews
- Research notes

### 50-运维排障
Use when:
- Troubleshooting guides
- Incident reports
- Debugging notes
- System maintenance logs

### 60-数据与表
Use when:
- Database schemas
- Data models
- Data dictionaries
- Statistical reports

### 90-归档
Use when:
- Deprecated content
- Completed projects
- Historical records

### 00-Inbox
Fallback for unclassified or temporary content.

**Default Rule**: When in doubt, prefer "30-方法论" for knowledge content, "40-工具脚本" only for actual executable scripts.

---

## Tag Rules
- 3–8 tags.
- Include at least one domain tag (e.g., 工程化/方法论/Obsidian/AI/开发).
- Short, non-redundant.

---

## properties Rules
- created/modified MUST be today's date: 2026-01-10
- source: "user_prompt" unless the request indicates file input.
