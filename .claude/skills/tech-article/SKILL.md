---
name: tech-article
description: Research, draft, revise, verify, and illustrate Chinese technical articles for WeChat Official Accounts or developer blogs. Use when writing technical articles, turning repositories or experiments into articles, removing AI prose patterns, or planning article illustrations.
---

# Technical Article Skill

Research, draft, revise, and illustrate authentic Chinese technical articles grounded in verified source code, architecture, and engineering practice.

## Workflow

1. **Define scope and angle**: Identify core topic, target audience, intended takeaway, and article format (tutorial, system design breakdown, postmortem analysis, or engineering opinion).
2. **Research and verify sources**: Read source code, configuration files, benchmark logs, and primary documentation. Record concrete commands, file names, version tags, and performance numbers with source attribution.
3. **Draft core content**:
   - Lead with the concrete result, technical tension, or engineering problem.
   - Build the narrative around specific events, real decisions, and reasoned trade-offs.
   - Keep narrative flowing in natural prose. Avoid converting the entire body into bulleted lists.
   - Use descriptive, informative section headings rather than generic mechanical labels.
4. **Eliminate AI writing patterns**:
   - Remove formulaic transitions (`总的来说`, `综上所述`, `由此可见`, `值得注意的是`, `需要明确的是`).
   - Remove hollow corporate buzzwords (`赋能`, `抓手`, `闭环`, `底层逻辑`, `核心洞察`, `组合拳`, `对齐`).
   - Remove rigid three-point templates ("发现一/二/三", "首先/其次/最后" repetitive stacking).
   - Remove unsubstantiated claims and fabricated first-person anecdotes.
5. **Verify technical details**:
   - Verify CLI commands, flags, and parameter names against source code or help outputs.
   - Verify library versions, API signatures, and configuration keys.
   - Verify all numbers, benchmark figures, and citations against original sources.
   - Explicitly flag unverified items or open questions instead of glossing over them.
6. **Plan illustrations (optional)**:
   - Generate diagrams or illustrations only when explicitly requested.
   - Select diagram types and visual styles from [references/styles.md](references/styles.md).
   - Create outline and prompt files following [references/illustration-guide.md](references/illustration-guide.md).
7. **Export draft**: Save the finished article to `drafts/<slug>.md` or output directly as requested.

## AI Writing Anti-Patterns

| AI Pattern | Issue | Plain Technical Replacement |
|------------|-------|-----------------------------|
| `总的来说` / `综上所述` | Empty filler transition | State the concrete conclusion directly |
| `赋能业务增长` | Vague corporate jargon | Name the exact capability added (e.g. `提高吞吐量 30%`) |
| `核心痛点` / `底层逻辑` | Overused abstraction | Describe the exact technical constraint or design invariant |
| `值得注意的是...` | Moralizing hedge | State the fact or rule directly in imperative mood |
| 机械排比清单 (1/2/3堆砌) | Loss of logical flow | Connect causes and effects using prose paragraphs |

## Guidelines

- **Grounding**: Base every technical explanation on verified repo facts or primary sources. Never invent fictional benchmark numbers or code snippets.
- **Style consistency**: Keep code in its source language. Write explanations in clear, natural Chinese.
- **Illustrations**: If image generation tools are unavailable, deliver verified prompt markdown files without claiming images were generated.

## Verification Checklist

Before completing the task, verify:

1. All CLI commands, options, and code blocks match source code or verified documentation.
2. All benchmark figures, performance metrics, and quotes match verified sources.
3. Prohibited AI phrases and empty buzzwords are eliminated.
4. Section headings accurately reflect their contained technical points.
5. Saved draft file path exists and is accessible.
