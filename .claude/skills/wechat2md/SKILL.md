---
name: wechat2md
description: Convert WeChat Official Account article and album URLs from mp.weixin.qq.com into local Markdown with downloaded images. Use when the user asks to save, archive, download, or convert a WeChat article or collection.
---

# WeChat to Markdown

Use the scripts and dependencies bundled in this Skill.

## Setup

```bash
pip install -r "<skill-dir>/requirements.txt"
```

Optional configuration lives at `<skill-dir>/config.json`. Copy [config.example.json](config.example.json) and read [references/config.md](references/config.md). Do not require project-root configuration.

## Routing

Single article:

```bash
python "<skill-dir>/tools/wechat2md_v2.py" "<article-url>"
```

Album or collection:

```bash
python "<skill-dir>/tools/wechat2md.py" --album "<album-url>"
```

Use `wechat2md_v2.py` for single articles because it writes one stable asset directory. Use `wechat2md.py` only for album mode.

## Output

Single article:

```text
outputs/<target-folder>/<slug>/
├── article.md
├── images/
└── meta.json
```

Album:

```text
outputs/<target-folder>/<album-name>/
├── _index.md
└── 001-<article-title>/
    ├── article.md
    └── images/
```

## Rules

- Resolve output paths from the user's current working directory.
- Download正文 images and rewrite links to local relative paths.
- Preserve the original URL and article metadata.
- On an image failure, retain the original image URL and report the failure.
- Do not claim success unless the Markdown exists and local image links resolve.
- For albums, continue after individual article failures and list them in `_index.md`.
