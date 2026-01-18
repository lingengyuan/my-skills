# Image Syntax (Minimal)

## AI Image in Markdown

```markdown
![alt text](__generate:prompt__)
```

- `__generate:` is the fixed prefix.
- Generated images are uploaded to WeChat and replaced with WeChat URLs.

## Image Types

- Local: `![alt](./path/image.png)` -> upload
- Remote: `![alt](https://example.com/image.jpg)` -> download then upload

## Placeholder

```html
<!-- IMG:0 -->
```

## Commands

Image upload happens during publish via:

```bash
python scripts/wechat_publish.py --md article.md --html article.html --draft --cover cover.jpg
```
