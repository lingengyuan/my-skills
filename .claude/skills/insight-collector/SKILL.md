---
name: insight-collector
description: Analyze URLs, source code, images, technical documents, or notes, and archive reusable insights, code snippets, and architecture patterns into a knowledge base. Use when collecting knowledge, archiving technical articles, saving reusable code, or recording insights (收录, 记录一下).
---

# Insight Collector Skill

Extract actionable engineering insights, reusable code snippets, and system design patterns from raw material and archive them into structured knowledge assets.

## Inputs

- **Source Material**: URL, code repository, image, screenshot, PDF, or text notes.
- **Target Knowledge Base**: Target directory for archiving.

If the target directory is not specified, inspect the workspace for existing catalogs (e.g. `README.md`, `INDEX.md`, `READING_LIST.md`). If multiple plausible destinations exist, ask the user to select the location before writing.

## Workflow

1. **Inspect existing catalog**: Inspect the target directory to understand existing taxonomy and prevent duplicate notes.
2. **Analyze source material**: Read the source thoroughly to understand core arguments, architecture decisions, and boundary conditions.
3. **Extract high-signal items**:
   - **Reusable code**: Self-contained functions, scripts, and configuration blocks with explicit dependency requirements.
   - **System design patterns**: Concrete architecture choices, component boundaries, and data flows.
   - **Trade-offs and failure modes**: Real-world constraints, performance bottlenecks, and edge cases.
   - **Actionable implications**: Concrete follow-up ideas or spike experiments.
4. **Structure the document**:
   - Select an appropriate document template from [references/doc-templates.md](references/doc-templates.md):
     - In-depth technical analysis (`analysis/<topic>.md`)
     - Project inspiration note (`ideas/<topic>.md`)
     - Standalone snippet (`python/`, `javascript/`, `shell/`)
   - Keep source facts and analytical inferences strictly distinguished.
   - Include original source URL or file path and capture date.
5. **Categorize and save**: Save the file in the matching category folder. Follow [references/project-conventions.md](references/project-conventions.md) when the target project adheres to those conventions.
6. **Update index catalog**: If the knowledge base maintains an index table in `README.md`, add a row referencing the new asset.
7. **Verify and report**: Verify that all files exist and links resolve. Present the key takeaways and saved paths concisely.

## Guidelines & Boundaries

- **Language consistency**: Write analytical notes in clear Chinese unless the target project specifies English. Keep code and technical identifiers in their original programming language.
- **Fact preservation**: Never fabricate claims, fake benchmark results, or code that was not present in or derived from the source.
- **No pseudo-profundity**: Do not force artificial "mental models", pretentious philosophizing, or fabricated knowledge-base links onto straightforward technical material. Keep notes pragmatic.
- **Minimal experiments**: Proposed follow-up spikes must state source motivation, expected value, and minimal verification criteria.
- **Directory isolation**: Never write outside the target knowledge base directory.

## Verification Checklist

Before completing the task, verify:

1. The generated markdown file exists and contains valid frontmatter or headers.
2. Source link and capture date are accurately recorded.
3. Code blocks specify language identifiers and required dependencies.
4. Existing catalog or index file is updated if applicable.
5. Output summary reports file paths and key findings directly.
