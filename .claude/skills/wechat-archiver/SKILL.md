---
name: wechat-archiver
description: Archive WeChat Official Account articles into structured knowledge assets with local Markdown, downloaded images, structured notes, and metadata. Use when archiving, indexing, or saving WeChat articles to an Obsidian vault or knowledge base.
---

# WeChat Archiver Skill

Archive WeChat Official Account articles into self-contained knowledge asset packages with clean Markdown, local images, a structured analytical note, and verified metadata.

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
3. **Inspect extracted content**: Read generated `article.md`, `images/`, and `meta.json`.
4. **Create structured note (`note.md`)**: Write a clean analytical note directly in the asset directory:
   - **核心摘要**：1-2 句直接说明文章解决的问题与核心结论。
   - **关键技术机制与论据**：系统原理解析、核心技术决策、支持论据。
   - **可复用资产**：可直接提取的代码、配置、命令或规则。
   - **局限与边界**：原文适用的范围、未解决的问题或作者主观偏见。
   - 绝不编造泛泛而谈的寒暄、大而无当的空话或虚假深刻的升华。
5. **Update metadata**: Ensure `meta.json` accurately reflects the generated asset paths.
6. **Optional visual artifacts**: Create `diagram.canvas` or `table.base` only when the user explicitly requests it or when complex spatial/comparison relationships provide clear visual value.
7. **Verify output**: Verify that `article.md`, images, `note.md`, and `meta.json` exist and pass verification.

## Output Package Structure

```text
<target-root>/outputs/<folder>/<slug>/
├── article.md          # Faithful Markdown of original article
├── images/             # Downloaded local images (if present)
├── note.md             # Structured analytical note
├── meta.json           # Machine-readable asset metadata (title, author, url, asset_id)
├── diagram.canvas      # Optional (only when explicitly requested)
└── table.base          # Optional (only when explicitly requested)
```

## Batch Processing

When processing multiple URLs:
1. Process articles sequentially using the standard single-article workflow.
2. If an article fetch fails, record the error, preserve completed assets, and continue with remaining URLs.
3. Report a final summary listing successful paths and failed URLs.
4. Do not modify the source inbox list unless directed by the user.

## Guidelines & Boundaries

- **Faithful preservation**: Never alter the original article's technical claims or author opinions in `article.md`.
- **Minimal optional artifacts**: Never create optional `diagram.canvas` or `table.base` files without clear informational value.
- **Completion definition**: An archive is complete only when `article.md`, downloaded images, `note.md`, and `meta.json` exist and pass verification.

## Verification Checklist

Before completing the task, verify:

1. `article.md` exists and image references link to local files in `images/`.
2. Local images exist on disk with non-zero file sizes.
3. `note.md` contains verified analytical sections and source attribution without AI fluff.
4. `meta.json` contains accurate artifact paths and metadata.
5. Output reports the exact asset directory path to the user.
