---
name: insight-collector
description: Analyze URLs, code, images, documents, screenshots, or raw text and archive reusable technical insights, code, and project ideas into a user-selected knowledge-base directory. Use when the user asks to collect, archive, analyze and save, 收录, 记录一下, or add material to a snippets/knowledge project.
---

# Insight Collector

Turn source material into traceable, reusable knowledge without assuming a personal directory layout.

## Inputs

- Source material: URL, file, image, code, or text.
- Target knowledge-base directory.

If the target is not stated, inspect the current workspace for an existing catalog such as `README.md` or `READING_LIST.md`. Ask before writing if more than one destination is plausible.

## Workflow

1. Read the existing catalog and nearby entries to avoid duplicates.
2. Read the source completely enough to identify its claims and boundaries.
3. Extract only applicable items:
   - reusable code,
   - technical patterns,
   - tools and dependencies,
   - tradeoffs,
   - failure modes,
   - non-obvious conclusions,
   - open questions,
   - concrete follow-up ideas.
4. Separate source facts from your inference. Attach the source URL or file path to every archived item.
5. Search the web only when freshness matters or when claiming that an idea is novel. Prefer primary sources.
6. Write into an existing category. Create a new category only when none fits.
7. Update the local catalog and reading list only if those files already exist or the user explicitly requests them.
8. Re-read every changed file and report paths plus the most useful conclusions.

## Output rules

- Use Chinese for analysis documents unless the target project uses another language.
- Keep code in its natural language and do not invent code that was absent from the source.
- A proposed experiment must state its source, expected value, minimum validation, and known alternatives.
- Do not write outside the selected knowledge-base directory.

Read [references/doc-templates.md](references/doc-templates.md) for document shapes and [references/project-conventions.md](references/project-conventions.md) only when the target project follows those conventions.
