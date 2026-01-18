# WeChat Draft Upload (Minimal)

## Required env vars

WECHAT_APPID
WECHAT_SECRET

## Behavior

- Images are uploaded to WeChat material and replaced with WeChat CDN URLs.
- Draft creation requires a cover image media_id.

## Commands

```bash
python scripts/wechat_publish.py --md article.md --html article.html --draft --cover cover.jpg
```

## Common errors

- Invalid AppID/Secret
- No draft permission
- IP not in whitelist
