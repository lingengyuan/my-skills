---
name: tech-article
description: Research, draft, revise, fact-check, and optionally illustrate a Chinese technical article for WeChat or a blog. Use when the user asks to write or improve a technical article, turn a repository or experiment into an article, remove AI-like prose, or plan article illustrations.
---

# Technical Article

Write natural Chinese grounded in supplied experience and verified sources.

## 1. Establish the article

Determine from context:

- topic and source material,
- target reader and platform,
- intended conclusion,
- whether the article is a tutorial, project story, analysis, or opinion.

Ask only for missing information that would materially change the article. Do not invent first-person experience, failures, results, or reader metrics.

## 2. Research

When URLs, repositories, products, APIs, or current facts are involved, read and verify them before drafting. Prefer primary sources. Record commands, filenames, numbers, and quotations with their sources.

## 3. Draft

- Lead with the concrete result or tension.
- Use specific events, data, code, and decisions.
- Explain technical terms in plain language.
- Prefer prose over repetitive lists.
- Keep headings descriptive rather than mechanical.
- Do not use slogans, fabricated drama, or unsupported causal claims.

Avoid habitual AI phrases such as `总的来说`, `综上所述`, `赋能`, `抓手`, `底层逻辑`, `核心洞察`, and formulaic “发现一/二/三” structures.

Read [references/styles.md](references/styles.md) only when choosing a specific visual or editorial style.

## 4. Fact-check

Recheck every externally verifiable claim:

- CLI syntax and configuration names,
- versions and model IDs,
- measurements and comparisons,
- quoted statements,
- feature and compatibility claims.

Mark unresolved items explicitly; do not hide them in polished prose.

## 5. Output

Return the article in the requested location or in chat. When saving, use `drafts/<slug>.md` unless the user specifies another path. Keep fact-check notes separate from the publishable body.

## 6. Illustrations

Generate illustrations only when requested. Read [references/illustration-guide.md](references/illustration-guide.md), create an outline and prompt files first, then use the available image-generation capability. If none is available, return the prompts without claiming images were generated.

Verify every inserted image path and keep style consistent across the article.
