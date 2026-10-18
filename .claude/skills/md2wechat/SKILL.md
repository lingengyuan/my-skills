---
name: md2wechat
description: Convert Markdown articles into WeChat Official Account compatible inline-styled HTML and optionally publish them to the WeChat draft box. Use when formatting articles for WeChat, rendering WeChat HTML, styling Markdown with themes, uploading article images, or publishing drafts to WeChat.
---

# Markdown to WeChat Skill

Convert Markdown into WeChat Official Account compatible HTML with inline CSS styling, and optionally upload articles directly to the WeChat draft box.

## Setup

HTML rendering requires Python 3.8+ and uses only the Python standard library.

Draft publishing requires valid credentials stored in a local `.env` file within this Skill's directory:

```env
WECHAT_APPID=your_wechat_app_id
WECHAT_SECRET=your_wechat_secret
```

Keep this file local. The repository ignores Skill-level `.env` files.

## Workflows

### 1. Render WeChat HTML (Local)

Render Markdown into styled HTML with inlined CSS:

```bash
python3 "<skill-dir>/scripts/md_ai_render.py" --md article.md --theme autumn-warm --out article.html
```

Supported preset themes:
- `autumn-warm`: Warm orange tone, editorial styling
- `spring-fresh`: Fresh green tone, clean reading
- `ocean-calm`: Deep blue tone, technical and business style

For custom CSS rules and theme details, see [references/themes.md](references/themes.md).

### 2. Publish to WeChat Draft Box (Remote)

Publishing mutates external state on the WeChat platform. Execute publishing only when the user explicitly requests it:

```bash
python3 "<skill-dir>/scripts/wechat_publish.py" --env "<skill-dir>/.env" --md article.md --html article.html --draft --cover cover.jpg
```

See [references/wechat-api.md](references/wechat-api.md) for publishing API options and error codes.

## Image Handling

- **Local images**: Referenced local images are uploaded to WeChat permanent material storage during draft publishing and replaced with WeChat CDN URLs.
- **Remote images**: Downloaded and uploaded to WeChat storage during publishing.
- **Cover image**: Specify `--cover <image-path>` explicitly. If unspecified, ask the user before publishing.
- **Image placeholders**: Ensure no unexpanded `__generate:...` placeholders remain in the final HTML. See [references/image-syntax.md](references/image-syntax.md).

## WeChat HTML Compatibility Rules

- All CSS declarations must be inlined in `style` attributes.
- Wrap body content in a top-level container `<div>`.
- Explicitly specify font colors on `<p>` and heading tags to prevent WeChat dark mode overriding text colors.
- Disallowed tags: `<script>`, `<iframe>`, `<style>`, `<link>`, `<form>`. See [references/html-guide.md](references/html-guide.md).

## Verification Checklist

Before completing the task, verify:

1. Rendered HTML file exists and is non-empty.
2. All styles are properly inlined on HTML elements.
3. Local image paths in Markdown resolve to valid image files on disk.
4. If publishing draft, the API response returns a valid `media_id`.
5. Report the output HTML path and publication status to the user.
