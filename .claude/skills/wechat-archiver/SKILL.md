---
name: wechat-archiver
description: Archive a WeChat Official Account article into a self-contained knowledge asset with article Markdown, local images, a structured note, metadata, and optional Canvas or Base artifacts. Use when the user wants more than conversion and explicitly asks to archive, organize, or add a WeChat article to a knowledge base.
---

# WeChat Archiver

This Skill is standalone. It contains its own article fetcher and does not call sibling Skills.

## Setup

```bash
pip install -r "<skill-dir>/requirements.txt"
```

## Workflow

1. Confirm the target knowledge-base directory.
2. Fetch the article:

```bash
python "<skill-dir>/tools/fetch_article.py" "<article-url>" --output-dir "<target-root>/outputs" --target-folder "<folder>"
```

3. Read the generated `article.md` and `meta.json`.
4. If an existing asset has the same normalized URL and content hash, report `skipped` unless the user requested refresh.
5. Create `note.md` directly in the asset directory:
   - concise summary,
   - key arguments and evidence,
   - reusable details,
   - source link,
   - uncertainty or missing context.
6. Create `diagram.canvas` only when relationships or sequence need a visual. Use valid JSON Canvas edges with `fromNode` and `toNode`.
7. Create `table.base` only when multiple comparable Markdown records exist. Scope it to the asset directory.
8. Merge artifact paths and the final status into `meta.json`.
9. Append one JSON object to `run.jsonl`.
10. Re-read and validate all artifacts before reporting success.

## Output contract

```text
<target-root>/outputs/<folder>/<slug>/
├── article.md
├── images/
├── note.md
├── diagram.canvas      # optional
├── table.base          # optional
├── meta.json
└── run.jsonl
```

## Batch mode

Process URLs one at a time with the same workflow. Continue after an individual failure, preserve successful assets, and return a success/failure summary. Do not edit the source inbox unless the user requests it.

## Boundaries

- Do not delete existing assets during refresh.
- Do not create optional artifacts merely to increase output count.
- A fetched article is not a completed archive until `note.md`, `meta.json`, and validation are complete.
