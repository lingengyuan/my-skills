---
name: wechat2md
description: Convert WeChat Official Account articles and topic albums (mp.weixin.qq.com) to local Markdown files with downloaded images. Use when converting WeChat articles, saving WeChat albums, downloading article content, or extracting Markdown from WeChat URLs.
---

# WeChat to Markdown Skill

Convert WeChat Official Account web articles and albums into local Markdown with downloaded images. Standard Markdown syntax is assumed knowledge.

## Setup

Python 3.8+ and `curl` in `PATH` are required. Install dependencies in the Skill directory:

```bash
pip install -r "<skill-dir>/requirements.txt"
```

## Workflows

### 1. Convert Single Article

Use `wechat2md_v2.py` for single articles. It creates an isolated asset directory with downloaded images and metadata:

```bash
python3 "<skill-dir>/tools/wechat2md_v2.py" "<article-url>"
```

Custom output paths:
```bash
python3 "<skill-dir>/tools/wechat2md_v2.py" "<article-url>" --output-dir "outputs" --target-folder "20-阅读笔记" --slug "custom-slug"
```

### 2. Convert Topic Album

Use `wechat2md.py` with `--album` to batch-download all articles in a WeChat collection:

```bash
python3 "<skill-dir>/tools/wechat2md.py" --album "<album-url>"
```

For custom album configurations (delays, slug templates, tag rules), see [references/config.md](references/config.md).

## CLI Reference

### `wechat2md_v2.py` (Single Article)

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | string (positional) | required | WeChat article URL |
| `--output-dir` | string | `outputs` | Base output directory |
| `--target-folder` | string | `20-阅读笔记` | Target folder within output directory |
| `--slug` | string | auto from title | Custom directory slug |

### `wechat2md.py` (Album Mode)

| Argument | Type | Description |
|----------|------|-------------|
| `--album` | string | WeChat album / topic URL |
| `--config` | string | Path to custom `config.json` |

## Output Package Structure

### Single Article

```text
outputs/<target-folder>/<slug>/
├── article.md          # Converted article in clean Markdown
├── images/             # Downloaded local images (if present)
└── meta.json           # Article metadata (title, author, url, asset_id)
```

### Album Collection

```text
outputs/<target-folder>/<album-name>/
├── _index.md           # Album table of contents
└── 001-<article-title>/
    ├── article.md      # Article Markdown
    └── images/         # Local images
```

## Guidelines

- **Relative paths**: Rewrite image tags in `article.md` to relative paths (`images/001.jpg`).
- **Image failure handling**: If an individual image fails to download, keep the remote URL and log a warning. Do not terminate the conversion.
- **Album continuity**: In album mode, continue downloading remaining articles if an individual article fails. Record failed items in `_index.md`.
- **Metadata preservation**: Always preserve original publishing timestamp, author name, and source URL in frontmatter or `meta.json`.

## Validation Checklist

Before completing the task, verify:

1. `article.md` exists and contains readable article text.
2. Image links in `article.md` point to local files in the `images/` directory.
3. Downloaded image files exist on disk and have non-zero size.
4. For albums, `_index.md` lists all successfully downloaded chapters and any failed URLs.
