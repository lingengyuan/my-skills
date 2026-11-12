# Analysis prompts

这些 prompt 从 Claude Code 2.1.322 的 `/insights` 实现中提取。宿主 agent 读取 `digest.md` 后，按下面的 schema 生成 `analysis.json`。

数据可能来自 Claude Code、Codex、pi 或 omp。先看 digest 的 `Agents:` 和 `Agent breakdown`，确认本次分析范围。涉及具体工具时写 agent 名称；泛指时写 "agent"，不要默认写 "Claude"。单一 agent 的报告只能写该 agent 的能力和命令。

## 输出总 schema

```json
{
  "project_areas": {
    "areas": [
      {"name": "Area name", "session_count": 0, "description": "2-3 sentences"}
    ]
  },
  "interaction_style": {
    "narrative": "2-3 paragraphs, second person",
    "key_pattern": "One sentence"
  },
  "what_works": {
    "intro": "1 sentence",
    "impressive_workflows": [
      {"title": "Short title", "description": "2-3 sentences"}
    ]
  },
  "friction_analysis": {
    "intro": "1 sentence",
    "categories": [
      {"category": "Concrete category", "description": "1-2 sentences", "examples": ["Example", "Example"]}
    ]
  },
  "suggestions": {
    "instruction_additions": [
      {"addition": "Line or block", "why": "1 sentence", "prompt_scaffold": "Where to add it"}
    ],
    "features_to_try": [
      {"feature": "Feature name", "one_liner": "What it does", "why_for_you": "Why it helps", "example_code": "Command or config"}
    ],
    "usage_patterns": [
      {"title": "Short title", "suggestion": "1-2 sentences", "detail": "3-4 sentences", "copyable_prompt": "Prompt to try"}
    ]
  },
  "on_the_horizon": {
    "intro": "1 sentence",
    "opportunities": [
      {"title": "4-8 words", "whats_possible": "2-3 sentences", "how_to_try": "1-2 sentences", "copyable_prompt": "Detailed prompt"}
    ]
  },
  "fun_ending": {
    "headline": "A memorable qualitative moment",
    "detail": "Brief context"
  },
  "at_a_glance": {
    "whats_working": "2-3 sentences",
    "whats_hindering": "2-3 sentences",
    "quick_wins": "2-3 sentences",
    "ambitious_workflows": "2-3 sentences"
  }
}
```

## 1. project_areas

```text
Analyze this coding agent usage data and identify project areas.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "areas": [
    {"name": "Area name", "session_count": N, "description": "2-3 sentences about what was worked on and how the agent was used."}
  ]
}

Include 4-5 areas. Skip internal CC operations.
```

## 2. interaction_style

```text
Analyze this coding agent usage data and describe the user's interaction style.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "narrative": "2-3 paragraphs analyzing HOW the user interacts with the agent. Use second person 'you'. Describe patterns: iterate quickly vs detailed upfront specs? Interrupt often or let the agent run? Include specific examples. Use **bold** for key insights.",
  "key_pattern": "One sentence summary of most distinctive interaction style"
}
```

## 3. what_works

```text
Analyze this coding agent usage data and identify what's working well for this user. Use second person ("you").

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "intro": "1 sentence of context",
  "impressive_workflows": [
    {"title": "Short title (3-6 words)", "description": "2-3 sentences describing the impressive workflow or approach. Use 'you' not 'the user'."}
  ]
}

Include 3 impressive workflows.
```

## 4. friction_analysis

```text
Analyze this coding agent usage data and identify friction points for this user. Use second person ("you").

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "intro": "1 sentence summarizing friction patterns",
  "categories": [
    {"category": "Concrete category name", "description": "1-2 sentences explaining this category and what could be done differently. Use 'you' not 'the user'.", "examples": ["Specific example with consequence", "Another example"]}
  ]
}

Include 3 friction categories with 2 examples each.
```

## 5. suggestions

```text
Analyze this coding agent usage data and suggest improvements.

## AGENT FEATURES REFERENCE (pick only features of the agents that appear in the digest):
1. **MCP Servers**: Connect the agent to external tools, databases, and APIs via Model Context Protocol.
   - Claude Code: `claude mcp add <server-name> -- <command>`
   - Codex: `codex mcp add <server-name> -- <command>`
   - Good for: database queries, Slack integration, GitHub issue lookup, connecting to internal APIs

2. **Custom Skills**: Reusable prompts you define as markdown files.
   - Claude Code: create `.claude/skills/<name>/SKILL.md`, then run `/<name>`.
   - Codex: create `~/.codex/skills/<name>/SKILL.md`; invoke it by name.
   - pi / omp: create the matching skill file under the agent's own skills directory.
   - Good for: repetitive workflows - commit, review, test, deploy, PR, or multi-step checks

3. **Lifecycle Hooks**: Shell commands that run automatically at defined events.
   - Claude Code: add hooks under `hooks` in `.claude/settings.json`.
   - Codex: use the `notify` setting in `~/.codex/config.toml`; do not describe Claude hooks.
   - Good for: auto-formatting code, running type checks, enforcing conventions

4. **Headless Mode**: Run the agent non-interactively from scripts and CI/CD.
   - Claude Code: `claude -p "fix lint errors" --allowedTools "Edit,Read,Bash"`
   - Codex: `codex exec "fix lint errors"`
   - Good for: CI/CD integration, batch code fixes, automated reviews

5. **Task Agents**: The agent spawns focused subagents for complex exploration or parallel work.
   - How to use: ask the agent to delegate exploration or verification to subagents.
   - Good for: codebase exploration, understanding complex systems, parallel checks

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "instruction_additions": [
    {"addition": "A specific line or block to add to the project instruction file (AGENTS.md for Codex, CLAUDE.md for Claude Code) based on workflow patterns. E.g., 'Always run tests after modifying auth-related files'", "why": "1 sentence explaining why this would help based on actual sessions", "prompt_scaffold": "Where to add it, e.g. 'Add under ## Testing section'"}
  ],
  "features_to_try": [
    {"feature": "Feature name from AGENT FEATURES REFERENCE above", "one_liner": "What it does", "why_for_you": "Why this would help YOU based on your sessions", "example_code": "Actual command or config to copy"}
  ],
  "usage_patterns": [
    {"title": "Short title", "suggestion": "1-2 sentence summary", "detail": "3-4 sentences explaining how this applies to YOUR work", "copyable_prompt": "A specific prompt to copy and try"}
  ]
}

IMPORTANT for instruction_additions: use the instruction file of the agent(s) in scope (Codex -> AGENTS.md, Claude Code -> CLAUDE.md, mixed -> describe the location per agent). PRIORITIZE instructions that appear MULTIPLE TIMES in the user data. If the user said the same thing in 2+ sessions (e.g., 'always run tests', 'use TypeScript'), that's a PRIME candidate - they shouldn't have to repeat themselves.

IMPORTANT for features_to_try: Pick 2-3 from the AGENT FEATURES REFERENCE above. Every command, path, and config key must belong to an agent that appears in the digest. Never give Claude Code commands in a Codex-only report, or the reverse.
```

## 6. on_the_horizon

```text
Analyze this coding agent usage data and identify future opportunities.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "intro": "1 sentence about evolving AI-assisted development",
  "opportunities": [
    {"title": "Short title (4-8 words)", "whats_possible": "2-3 ambitious sentences about autonomous workflows", "how_to_try": "1-2 sentences mentioning relevant tooling", "copyable_prompt": "Detailed prompt to try"}
  ]
}

Include 3 opportunities. Think BIG - autonomous workflows, parallel agents, iterating against tests.
```

## 7. fun_ending

```text
Analyze this coding agent usage data and find a memorable moment.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "headline": "A memorable QUALITATIVE moment from the transcripts - not a statistic. Something human, funny, or surprising.",
  "detail": "Brief context about when/where this happened"
}

Find something genuinely interesting or amusing from the session summaries.
```

## 8. at_a_glance

```text
You're writing an "At a Glance" summary for a coding agent usage insights report for coding agent users. The goal is to help them understand their usage and improve how they can use agents better, especially as models improve.

Use this 4-part structure:

1. **What's working** - What is the user's unique style of interacting with the agent and what are some impactful things they've done? You can include one or two details, but keep it high level since things might not be fresh in the user's memory. Don't be fluffy or overly complimentary. Also, don't focus on the tool calls they use.

2. **What's hindering you** - Split into (a) the agent's fault (misunderstandings, wrong approaches, bugs) and (b) user-side friction (not providing enough context, environment issues -- ideally more general than just one project). Be honest but constructive.

3. **Quick wins to try** - Specific agent features they could try from the examples below, or a workflow technique if you think it's really compelling. (Avoid stuff like "Ask the agent to confirm before taking actions" or "Type out more context up front" which are less compelling.)

4. **Ambitious workflows for better models** - As we move to much more capable models over the next 3-6 months, what should they prepare for? What workflows that seem impossible now will become possible? Draw from the appropriate section below.

Keep each section to 2-3 not-too-long sentences. Don't overwhelm the user. Don't mention specific numerical stats or underlined_categories from the session data below. Use a coaching tone.

RESPOND WITH ONLY A VALID JSON OBJECT:
{
  "whats_working": "(refer to instructions above)",
  "whats_hindering": "(refer to instructions above)",
  "quick_wins": "(refer to instructions above)",
  "ambitious_workflows": "(refer to instructions above)"
}
```

## 可选：单会话 facet 提取

只有在需要 goal/outcome/satisfaction/friction 图表，且 `~/.claude/usage-data/facets/` 中没有对应缓存时才执行。对 `facets-todo.json` 中的每个会话，把 transcript 摘要填到 `SESSION:` 之后。

```text
Analyze this coding agent session and extract structured facets.

CRITICAL GUIDELINES:

1. **goal_categories**: Count ONLY what the USER explicitly asked for.
   - DO NOT count the agent's autonomous codebase exploration
   - DO NOT count work the agent decided to do on its own
   - ONLY count when user says "can you...", "please...", "I need...", "let's..."

2. **user_satisfaction_counts**: Base ONLY on explicit user signals.
   - "Yay!", "great!", "perfect!" -> happy
   - "thanks", "looks good", "that works" -> satisfied
   - "ok, now let's..." (continuing without complaint) -> likely_satisfied
   - "that's not right", "try again" -> dissatisfied
   - "this is broken", "I give up" -> frustrated

3. **friction_counts**: Be specific about what went wrong.
   - misunderstood_request: the agent interpreted incorrectly
   - wrong_approach: Right goal, wrong solution method
   - buggy_code: Code didn't work correctly
   - user_rejected_action: User said no/stop to a tool call
   - excessive_changes: Over-engineered or changed too much

4. If very short or just warmup, use warmup_minimal for goal_category

SESSION:

RESPOND WITH ONLY A VALID JSON OBJECT matching this schema:
{
  "underlying_goal": "What the user fundamentally wanted to achieve",
  "goal_categories": {"category_name": count},
  "outcome": "fully_achieved|mostly_achieved|partially_achieved|not_achieved|unclear_from_transcript",
  "user_satisfaction_counts": {"level": count},
  "claude_helpfulness": "unhelpful|slightly_helpful|moderately_helpful|very_helpful|essential",
  "session_type": "single_task|multi_task|iterative_refinement|exploration|quick_question",
  "friction_counts": {"friction_type": count},
  "friction_detail": "One sentence describing friction or empty",
  "primary_success": "none|fast_accurate_search|correct_code_edits|good_explanations|proactive_help|multi_file_changes|good_debugging",
  "brief_summary": "One sentence: what user wanted and whether they got it"
}
```

## 可选：长 transcript 分块摘要

单个会话超过 30,000 字符时，按 25,000 字符切块，每块先摘要，再拼回 facet prompt。

```text
Summarize this portion of a coding agent session transcript. Focus on:
1. What the user asked for
2. What the agent did (tools used, files modified)
3. Any friction or issues
4. The outcome

Keep it concise - 3-5 sentences. Preserve specific details like file names, error messages, and user feedback.

TRANSCRIPT CHUNK:
```
