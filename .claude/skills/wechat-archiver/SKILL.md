---
name: wechat-archiver
description: Archive WeChat Official Account articles into structured knowledge assets with local Markdown, downloaded images, structured notes, metadata, and optional Canvas or Base files. Use when archiving, indexing, or saving WeChat articles to an Obsidian vault or knowledge base.
---

# WeChat Archiver Skill

Archive WeChat Official Account articles into self-contained knowledge asset packages. Standard Markdown and Obsidian conventions are assumed knowledge.

## Setup

Python 3.8+ and `curl` in `PATH` are required. Install dependencies in the Skill directory:

```bash
pip install -r "<skill-dir>/requirements.txt"
```

## Workflow

1. **Determine destination**: Verify the target knowledge base directory. Default to `outputs/<folder>/<slug>/`.
2. **Fetch article**: Run the bundled fetcher tool:
   ```bash
   python "<skill-dir>/tools/fetch_article.py" "<article-url>" --output-dir "<target-root>/outputs" --target-folder "<folder>"
   ```
   If the fetcher returns `STATUS=skipped`, the URL and article hash match an existing asset. Verify the existing asset and do not recreate it. Add `--refresh` only when the user explicitly requests an update.
3. **Inspect extracted content**: Read generated `article.md` and `meta.json`.
4. **Create structured note (`note.md`)**: Write a structured analytical note in the asset directory:
   - Concise summary (core takeaway in 2-3 sentences)
   - Key arguments with supporting evidence
   - Reusable patterns, tools, or code snippets
   - Original source URL and author metadata
   - Unresolved questions or contextual limitations
5. **Generate optional visual artifacts**:
   - **Canvas (`diagram.canvas`)**: Create only when workflows, architecture, or entity relationships benefit from a spatial diagram. Use valid JSON Canvas syntax with `fromNode` and `toNode`.
   - **Base (`table.base`)**: Create only when multiple comparable items exist within the asset. Scope filters to the asset directory.
6. **Update metadata & run log**:
   - Record all artifact paths and completion status in `meta.json`.
   - Append the execution record as one JSON line to `run.jsonl`.
7. **Verify output**: Re-read generated files and verify links before finishing.

## Output Package Structure

```text
<target-root>/outputs/<folder>/<slug>/
├── article.md          # Clean Markdown of original article
├── images/             # Downloaded local images
├── note.md             # Structured analytical note
├── diagram.canvas      # Optional JSON Canvas diagram
├── table.base          # Optional Obsidian Base table
├── meta.json           # Machine-readable asset metadata
└── run.jsonl           # Execution audit trail
```

## Batch Processing

When processing multiple URLs:
1. Process articles sequentially using the standard single-article workflow.
2. If an article fetch fails, record the error, preserve completed assets, and continue with remaining URLs.
3. Report a final summary listing successful paths and failed URLs.
4. Do not modify the source inbox list unless directed by the user.

## Guidelines & Boundaries

- **Preserve existing assets**: Never overwrite or delete existing notes unless `--refresh` is explicitly requested.
- **Minimal artifacts**: Never create optional `diagram.canvas` or `table.base` files without clear information value.
- **Completion definition**: An archive is complete only when `article.md`, downloaded images, `note.md`, and `meta.json` exist and pass verification.

## Verification Checklist

Before completing the task, verify:

1. `article.md` exists and image references link to local files in `images/`.
2. `note.md` contains verified analytical sections and source attribution.
3. Any created `.canvas` file contains valid JSON with valid node and edge connections.
4. Any created `.base` file contains valid YAML with existing property mappings.
5. `meta.json` contains accurate artifact paths and timestamps.
6. `run.jsonl` contains the append-only run entry.
