---
name: md2wechat
description: Convert Markdown into WeChat Official Account compatible HTML with bundled themes, and optionally upload it to the WeChat draft box. Use for 公众号排版, Markdown 转微信 HTML, inline CSS rendering, image upload, or draft publishing.
---

# Markdown to WeChat

Use only files and scripts bundled in this Skill.

## Setup

No dependency installation is required. Draft publishing needs a local `<skill-dir>/.env`:

```env
WECHAT_APPID=your_app_id
WECHAT_SECRET=your_secret
```

Keep this file local; the repository ignores Skill-level `.env` files.

## Workflow

1. Read the Markdown and identify the title, structure, theme, and images.
2. Read [references/themes.md](references/themes.md) only when choosing a theme.
3. Render HTML:

```bash
python "<skill-dir>/scripts/md_ai_render.py" --md article.md --theme autumn-warm --out article.html
```

4. Inspect the generated HTML for unresolved image placeholders and unsupported styling.
5. If the user explicitly requests draft publishing, confirm the target account and publish:

```bash
python "<skill-dir>/scripts/wechat_publish.py" --env "<skill-dir>/.env" --md article.md --html article.html --draft --cover cover.jpg
```

Publishing changes external state. Rendering does not.

## Images

- Local and remote images are uploaded only during publishing.
- Generate requested illustrations with an available image-generation capability before rendering; do not leave `__generate:...` placeholders in final HTML.
- Use the first suitable image as cover only after the user accepts that choice.

Read [references/html-guide.md](references/html-guide.md), [references/image-syntax.md](references/image-syntax.md), and [references/wechat-api.md](references/wechat-api.md) only for the relevant step.

## Validation

- Output HTML exists and is non-empty.
- Styles are inline and compatible with WeChat.
- All local image paths resolve.
- Draft publishing returns a media ID before reporting success.
