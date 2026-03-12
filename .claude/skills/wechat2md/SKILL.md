---
name: wechat2md
description: Convert WeChat Official Account articles (mp.weixin.qq.com) to local Markdown with all images downloaded. Use when user provides a WeChat article URL (mp.weixin.qq.com/s/...) or a WeChat album/collection URL (mp.weixin.qq.com/mp/appmsgalbum...) and wants to save or convert it. Supports single articles and bulk album downloads.
---

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

配置文件：`.claude/skills/wechat2md/config.json`（可选）。详见 [references/config.md](references/config.md)。

简要：无配置文件时使用 v1 默认行为；复制 `config.example.json` 为 `config.json` 可启用知识库适配模式（frontmatter、slug 哈希、文件夹白名单等）。

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

## 测试
```bash
python3 -m pytest .claude/skills/wechat2md/tests/ -v
```
