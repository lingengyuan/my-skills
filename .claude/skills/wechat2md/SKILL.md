# wechat2md

将微信公众号文章（mp.weixin.qq.com）转换为本地 Markdown，并强制下载所有正文图片。

支持两种模式：
1. **单篇文章**：下载单篇微信文章
2. **专题合集**：批量下载微信"专题"中的所有文章

## 用法（自然语言）
用户输入示例：
- 把这篇文章转成 Markdown：https://mp.weixin.qq.com/s/xxxxxxxx
- 下载这个合集：https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=...

## 行为规范（强约束）
- 识别到 `mp.weixin.qq.com/s/` 的文章链接时，执行单篇转换。
- 识别到 `mp.weixin.qq.com/mp/appmsgalbum` 的合集链接时，执行批量下载。
- 图片处理为必选：必须下载正文中所有图片，并在 Markdown 中改写为本地相对路径。

## 输出契约（以运行时当前目录为根目录）

### 单篇文章 - 默认输出（v1 行为，无配置文件时）
- Markdown：`./outputs/<文章名称>/<文章名称>.md`
- 图片：`./outputs/<文章名称>/images/001.<ext>`（从 001 开始，按正文出现顺序递增，三位补零）

### 单篇文章 - 配置后输出（有 config.json 时）
- Markdown：`./outputs/<folder>/<slug>/article.md`（带 YAML frontmatter）
- 图片：`./outputs/<folder>/<slug>/images/`
- 元数据：`./outputs/<folder>/<slug>/meta.json`

### 专题合集输出
```
outputs/<folder>/<album-name>/
├── _index.md            # 合集索引，包含所有文章链接
├── 001-<article-title>/
│   ├── article.md
│   └── images/
├── 002-<article-title>/
│   ├── article.md
│   └── images/
└── ...
```

索引文件（`_index.md`）格式：
```markdown
---
title: <合集名称>
created: YYYY-MM-DD
type: album
article_count: N
source: "<合集URL>"
tags: [微信文章, 合集]
---

# <合集名称>

共 N 篇文章

## 文章列表

1. [文章标题](./001-标题/article.md)
2. [文章标题](./002-标题/article.md)
...

## 下载失败

- [ ] 文章标题 - 需要登录
- [ ] 文章标题 - 网络超时
```

## 配置系统

### 配置文件位置
`.claude/skills/wechat2md/config.json`

### 默认配置（v1 兼容）
无配置文件时，使用以下默认行为：
```json
{
  "schema_version": "1.0",
  "output": {
    "base_dir": "outputs",
    "path_template": "{base_dir}/{title}",
    "article_filename": "{title}.md",
    "images_dirname": "images"
  },
  "slug": {
    "format": "title",
    "max_length": 80
  },
  "frontmatter": {
    "enabled": false
  },
  "folder": {
    "default": null,
    "enforce_whitelist": false
  },
  "tags": {
    "default_tags": []
  },
  "meta": {
    "enabled": false
  }
}
```

### 知识库适配配置（示例）
复制 `config.example.json` 为 `config.json` 以启用知识库适配：
```json
{
  "schema_version": "1.0",
  "output": {
    "base_dir": "outputs",
    "path_template": "{base_dir}/{folder}/{slug}",
    "article_filename": "article.md"
  },
  "slug": {
    "format": "date-title-hash",
    "max_length": 80
  },
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
  "tags": {
    "default_tags": ["微信文章", "阅读笔记"],
    "max_count": 8
  },
  "meta": {
    "enabled": true
  }
}
```

### 配置项说明

#### output
- `base_dir`: 输出根目录（默认 `outputs`）
- `path_template`: 路径模板，支持变量 `{base_dir}`, `{title}`, `{slug}`, `{folder}`
- `article_filename`: 文章文件名模板，支持 `{title}`
- `images_dirname`: 图片子目录名（默认 `images`）

#### slug
- `format`: slug 格式
  - `title`: 仅标题（默认）
  - `date-title`: `YYYYMMDD-标题`
  - `date-title-hash`: `YYYYMMDD-标题-abcdef`（6 位 URL 哈希）
- `max_length`: 最大长度（默认 80）

#### frontmatter
- `enabled`: 是否生成 YAML frontmatter
- `include_fields`: 包含的字段列表（`title`, `author`, `created`, `source`, `tags`）

#### folder
- `default`: 默认文件夹
- `whitelist`: 文件夹白名单
- `enforce_whitelist`: 是否强制白名单验证

#### tags
- `default_tags`: 默认标签列表
- `max_count`: 最大标签数

#### meta
- `enabled`: 是否生成 meta.json

#### album（合集配置）
- `delay_seconds`: 下载间隔时间（默认 1.0 秒）
- `max_articles`: 最大下载文章数（0 = 不限制）
- `generate_index`: 是否生成索引文件（默认 true）
- `index_filename`: 索引文件名（默认 `_index.md`）

## 执行方式
当用户提供 URL 后，运行：

```bash
# 单篇文章（自动检测）
python3 .claude/skills/wechat2md/tools/wechat2md.py "https://mp.weixin.qq.com/s/xxxxxxxx"

# 专题合集（自动检测）
python3 .claude/skills/wechat2md/tools/wechat2md.py "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..."

# 强制使用合集模式
python3 .claude/skills/wechat2md/tools/wechat2md.py --album "<URL>"
```

脚本会根据 URL 类型自动选择单篇或合集模式。

## 失败策略

### 单篇文章
- 若抓取失败或未能提取正文（#js_content），应返回错误原因。
- 若个别图片下载失败：
  - Markdown 中对该图片保留原始 URL（不阻断整体生成）
  - 在 Markdown 顶部生成一个 "图片下载失败列表" 区块（包含序号与 URL）
- 若目录不存在，则创建。
- 若存在同名文件，直接覆盖。

### 专题合集
- 若合集 API 请求失败，返回错误原因。
- 若单篇文章下载失败（需要登录、网络超时等）：
  - 跳过该文章，继续下载其他文章
  - 在索引文件的"下载失败"区块中记录
- 若触发频率限制，等待 30 秒后重试。
- 每篇文章下载完成后默认等待 1 秒（可配置）。

## 执行
- 从用户输入中提取 URL（允许句子中混杂其它文字）。
- 运行：
  - `python3 .claude/skills/wechat2md/tools/wechat2md.py "<URL>"`
- 运行完成后：
  - 输出生成的 Markdown 路径
  - 输出图片目录路径
  - 输出 meta.json 路径（如果启用）

## 失败处理
- 如果抓取失败或无法提取正文 `#js_content`，明确报错并退出（非静默失败）。
- 如果个别图片下载失败：
  - Markdown 中该图片保留原始 URL（不阻断整篇文章生成）
  - 在 Markdown 顶部追加"图片下载失败列表"。
- 如果配置文件格式错误，打印警告并使用默认配置。

## 测试
```bash
python3 -m pytest .claude/skills/wechat2md/tests/ -v
```
