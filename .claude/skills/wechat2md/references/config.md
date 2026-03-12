# wechat2md 配置系统

配置文件位置：`.claude/skills/wechat2md/config.json`

无配置文件时使用 v1 默认行为（输出到 `outputs/<标题>/<标题>.md`）。

## 默认配置（v1 兼容）

```json
{
  "schema_version": "1.0",
  "output": {
    "base_dir": "outputs",
    "path_template": "{base_dir}/{title}",
    "article_filename": "{title}.md",
    "images_dirname": "images"
  },
  "slug": { "format": "title", "max_length": 80 },
  "frontmatter": { "enabled": false },
  "folder": { "default": null, "enforce_whitelist": false },
  "tags": { "default_tags": [] },
  "meta": { "enabled": false }
}
```

## 知识库适配配置（复制 config.example.json 为 config.json）

```json
{
  "schema_version": "1.0",
  "output": {
    "base_dir": "outputs",
    "path_template": "{base_dir}/{folder}/{slug}",
    "article_filename": "article.md"
  },
  "slug": { "format": "date-title-hash", "max_length": 80 },
  "frontmatter": {
    "enabled": true,
    "include_fields": ["title", "author", "created", "source", "tags"]
  },
  "folder": {
    "default": "20-阅读笔记",
    "whitelist": ["00-Inbox", "10-项目", "20-阅读笔记", "30-方法论",
                  "40-工具脚本", "50-运维排障", "60-数据与表", "90-归档"],
    "enforce_whitelist": true
  },
  "tags": { "default_tags": ["微信文章", "阅读笔记"], "max_count": 8 },
  "meta": { "enabled": true }
}
```

## 配置项说明

| 字段 | 说明 |
|------|------|
| `output.base_dir` | 输出根目录（默认 `outputs`） |
| `output.path_template` | 路径模板，变量：`{base_dir}` `{title}` `{slug}` `{folder}` |
| `output.article_filename` | 文章文件名，支持 `{title}` |
| `slug.format` | `title` / `date-title` / `date-title-hash`（6位URL哈希） |
| `slug.max_length` | slug 最大长度（默认 80） |
| `frontmatter.enabled` | 是否生成 YAML frontmatter |
| `frontmatter.include_fields` | 字段列表：`title` `author` `created` `source` `tags` |
| `folder.default` | 默认文件夹 |
| `folder.whitelist` | 文件夹白名单 |
| `folder.enforce_whitelist` | 是否强制白名单验证 |
| `tags.default_tags` | 默认标签列表 |
| `tags.max_count` | 最大标签数 |
| `meta.enabled` | 是否生成 meta.json |
| `album.delay_seconds` | 合集下载间隔（默认 1.0 秒） |
| `album.max_articles` | 最大下载文章数（0 = 不限） |
| `album.generate_index` | 是否生成索引文件（默认 true） |
