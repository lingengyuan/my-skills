# Claude Skills Development Framework

[English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>
## English

### Overview

A comprehensive framework for developing Claude Code Skills with integrated Obsidian ecosystem support. This project implements an orchestrator pattern where `note-creator` delegates to specialized format-specific skills.

### 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills

# Install dependencies
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt

# Archive a WeChat article
Skill(wechat-archiver, args="https://mp.weixin.qq.com/s/your-article-url")

# Generate manga-style image (requires API token, see below)
"Convert this photo to Hojo manga style"
```

#### Z-Image API Setup (Optional)

To use `zimage-api` skill, you need a Replicate API token:

1. Sign up at [Replicate](https://replicate.com/)
2. Get your API token from [Account Settings](https://replicate.com/account/api-tokens)
3. Create `.env` file in project root:
   ```env
   REPLICATE_API_TOKEN=r8_your_token_here
   ```

### 📁 Project Structure

| Directory/File | Description |
|----------------|-------------|
| `.claude/skills/` | Claude Skills definitions |
| ├── `note-creator/` | Orchestrator for structured note generation |
| ├── `obsidian-markdown/` | Markdown generation with YAML frontmatter |
| ├── `json-canvas/` | Visual diagram/canvas generation |
| ├── `obsidian-bases/` | Database-like table view generation |
| ├── `wechat-archiver/` | WeChat article archiving workflow |
| ├── `wechat2md/` | WeChat article to Markdown converter |
| ├── `sync_to_github/` | Automated git commit and push |
| ├── `portpilot-assistant/` | Natural-language local dev port management |
| ├── `zimage-api/` | Manga style image generation (Cloud API) |
| ├── `zimage-local/` | Manga style image generation (Local ComfyUI) |
| └── `zimage-core/` | Shared core module for Z-Image skills |
| `.postmortem/` | Postmortem reports for incidents and bugs |
| `CLAUDE.md` | Project development guidelines |
| `README.md` | This file |

### 🎯 Key Features

#### Note Generation System
- **Orchestrator Pattern**: `note-creator` classifies intent and delegates to format skills
- **Multi-Format Output**: Markdown, Canvas diagrams, Base tables
- **Intelligent Classification**: Auto-detects content type and generates appropriate artifacts
- **Folder Organization**: Whitelist-based folder system for structured knowledge base

#### WeChat Article Archiving
- **WeChat Article to Markdown**: Convert articles with local images
- **Structured Notes**: Auto-generate summaries, key points, and metadata
- **Batch Processing**: Process multiple URLs from inbox.md file
- **Idempotent**: Same URL won't create duplicates
- **Self-Contained Output**: Article and images in single portable directory

#### Quality Assurance
- **Postmortem Reports**: Detailed analysis of 6 resolved incidents
- **Transparent Development**: Public documentation of issues and fixes
- **Continuous Improvement**: Learning from mistakes to prevent recurrence

### 📖 Usage Examples

#### Archive WeChat Article

```bash
# Using Claude Skill - Single article
Skill(wechat-archiver, args="https://mp.weixin.qq.com/s/your-article-url")

# Output directory: outputs/20-阅读笔记/YYYYMMDD-slug-abcdef/
# - article.md       # Original article
# - note.md          # Structured notes
# - images/          # Downloaded images
# - meta.json        # Metadata

# Using Claude Skill - Album/Collection (batch download)
Skill(wechat-archiver, args="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=xxx&album_id=xxx")

# Output directory: outputs/20-阅读笔记/album-name/
# - _index.md                    # Index file with all article links
# - 001-first-article/
#   ├── article.md
#   └── images/
# - 002-second-article/
#   ├── article.md
#   └── images/
# ... (all articles numbered by publication time)
```

#### Batch Archive from inbox.md

```bash
# Create inbox.md with WeChat URLs (one per line)
# Supports formats: plain URLs, markdown links, task lists
- [ ] https://mp.weixin.qq.com/s/article1
- [x] https://mp.weixin.qq.com/s/already-processed  # Will be skipped
- [ ] https://mp.weixin.qq.com/s/article2

# Run batch archiver
Skill(wechat-archiver, args="--batch inbox.md")

# URLs are automatically marked as [x] after processing
```

#### Create Comparison Table

```bash
# Using note-creator
Skill(note-creator, "Compare Obsidian Skills: markdown, canvas, and base")

# Output: outputs/30-方法论/obsidian-skills-comparison-*/
# - note.md          # Comparison article
# - table.base       # Comparison table
# - compare/         # Individual item files
```

#### Generate Technical Diagram

```bash
# Create architecture diagram
Skill(note-creator, "Create architecture diagram for note-creator workflow")

# Output: outputs/30-方法论/*/diagram.canvas
```

#### Generate Manga-Style Image

```bash
# Let Claude Code analyze and convert an image
"Convert this photo to Hojo Tsukasa manga style"
"Turn input/photo.jpg into Urushihara Satoshi anime style"

# Or provide prompts directly
cd .claude/skills/zimage-local
python generate.py "1girl, solo, glasses, smile, portrait" hojo

# Output: outputs/zimage/zimage_hojo_local_*.png
```

### 🛠️ Skills Reference

#### Core Skills

1. **note-creator** (Orchestrator)
   - Classifies user intent
   - Delegates to format skills
   - Writes all artifacts to disk
   - Location: `.claude/skills/note-creator/SKILL.md`

2. **obsidian-markdown**
   - Generates valid Obsidian Flavored Markdown
   - Includes YAML frontmatter, tags, wikilinks
   - Location: `.claude/skills/obsidian-markdown/SKILL.md`

3. **json-canvas**
   - Creates visual diagrams in Obsidian Canvas format
   - Supports flowcharts, sequences, architectures
   - Location: `.claude/skills/json-canvas/SKILL.md`

4. **obsidian-bases**
   - Generates database-like table views
   - Supports comparison mode with auto-generated rows
   - Location: `.claude/skills/obsidian-bases/SKILL.md`

#### Utility Skills

5. **wechat-archiver** (Orchestrator)
   - Orchestrates WeChat article archiving workflow
   - Calls **wechat2md** for HTML → Markdown conversion
   - Calls **note-creator** for structured note generation
   - Batch processing from inbox.md with progress bar and ETA
   - Manages asset directories and metadata
   - Location: `.claude/skills/wechat-archiver/SKILL.md`

6. **wechat2md** (Called by wechat-archiver)
   - Converts WeChat articles to clean Markdown
   - Downloads all images to self-contained output directory
   - **Album/Collection Batch Download**: One URL downloads entire article series (8 articles in 1 command)
   - **Smart URL Detection**: Auto-detects single article vs album, maintains backward compatibility
   - **Auto-Sorting by Time**: Articles numbered by publication order (001, 002, 003...)
   - **Index Generation**: Auto-creates `_index.md` with links to all articles
   - **Knowledge Base Integration**: Configurable output paths, frontmatter, and metadata
   - Proper paragraph separation and code block formatting
   - Converts inline styles to native Markdown syntax
   - Auto-fix plain text URLs to markdown links
   - Auto-detect code language for syntax highlighting
   - **Backward Compatible**: v1 behavior without config, enhanced features with config.json
   - Location: `.claude/skills/wechat2md/SKILL.md`

7. **sync_to_github**
   - Automated git workflow
   - AI-generated commit messages
   - Optional push to remote
   - Location: `.claude/skills/sync_to_github/SKILL.md`

8. **portpilot-assistant**
   - Natural-language local dev port management via PortPilot CLI
   - Supports read actions (`scan`, `who`, `pick`, `doctor`) with direct execution
   - Requires explicit confirmation for write actions (`free`, `init --force`, `config migrate`)
   - Location: `.claude/skills/portpilot-assistant/SKILL.md`

#### Image Generation Skills

9. **zimage-api**
   - Generate manga-style images using Replicate cloud API
   - Supports Hojo Tsukasa (B&W manga) and Urushihara Satoshi (90s anime) styles
   - Claude Code analyzes images and generates prompts automatically
   - No local GPU required
   - Location: `.claude/skills/zimage-api/SKILL.md`

10. **zimage-local**
   - Generate manga-style images using local ComfyUI
   - Same style support as API version
   - **Completely free** - no API costs
   - Requires local GPU (4GB+ VRAM)
   - Location: `.claude/skills/zimage-local/SKILL.md`

### 📊 Output Structure

```
outputs/
├── 00-Inbox/           # Unclassified/temporary
├── 10-项目/            # Project-specific notes
├── 20-阅读笔记/         # Reading notes, article summaries
├── 30-方法论/          # Methods, comparisons, frameworks
├── 40-工具脚本/         # Actual executable scripts/tools
├── 50-运维排障/         # Troubleshooting, debugging
├── 60-数据与表/         # Database schemas, data models
└── 90-归档/            # Deprecated/completed
```

### 🔒 Security & Privacy

- ✅ No hardcoded credentials in repository
- ✅ `.gitignore` properly configured
- ✅ Local settings excluded (`.claude/settings.local.json`)
- ✅ Obsidian configs excluded from history
- ✅ Postmortem reports publicly shared

### 📚 Documentation

- **`CLAUDE.md`** - Project development guidelines
- **`.postmortem/README.md`** - Postmortem reports index
- **`.claude/skills/*/SKILL.md`** - Individual skill documentation
- **`.claude/skills/*/REFERENCE.md`** - Technical references

### 🐛 Known Issues

See [`.postmortem/README.md`](.postmortem/README.md) for detailed reports:
- POSTMORTEM-2026-001: Base filters failure (P0) ✅ Resolved
- POSTMORTEM-2026-002: Base path resolution (P0) ✅ Resolved
- POSTMORTEM-2026-003: Windows encoding (P1) ✅ Resolved
- POSTMORTEM-2026-004: Overbroad detection (P2) ✅ Resolved
- POSTMORTEM-2026-005: Duplicate ingestion (P2) ⏳ Partially Resolved
- POSTMORTEM-2026-006: Image path error (P1) ✅ Resolved

### 🔗 Related Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [Obsidian Plugin Docs](https://docs.obsidian.md/)
- [JSON Canvas Spec](https://github.com/obsidianmd/jsoncanvas)

### 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<a name="简体中文"></a>
## 简体中文

### 概述

Claude Code Skills 开发框架，集成了 Obsidian 生态系统支持。项目采用编排器模式，`note-creator` 负责分类意图并委托给专门的格式化技能。

### 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills

# 安装依赖
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt

# 归档微信文章
Skill(wechat-archiver, args="https://mp.weixin.qq.com/s/your-article-url")

# 生成漫画风格图像（需要配置 API Token，见下方）
"帮我把这张照片转成北条司风格"
```

#### Z-Image API 配置（可选）

使用 `zimage-api` 需要 Replicate API Token：

1. 在 [Replicate](https://replicate.com/) 注册账号
2. 从 [账户设置](https://replicate.com/account/api-tokens) 获取 API Token
3. 在项目根目录创建 `.env` 文件：
   ```env
   REPLICATE_API_TOKEN=r8_your_token_here
   ```

**注意：** `zimage-local` 使用本地 ComfyUI，完全免费，无需 API Token。

### 📁 项目结构

| 目录/文件 | 说明 |
|---------|------|
| `.claude/skills/` | Claude Skills 定义 |
| ├── `note-creator/` | 结构化笔记生成的编排器 |
| ├── `obsidian-markdown/` | Markdown 生成（含 YAML frontmatter） |
| ├── `json-canvas/` | 可视化图表/Canvas 生成 |
| ├── `obsidian-bases/` | 数据库式表格视图生成 |
| ├── `wechat-archiver/` | 微信文章归档工作流 |
| ├── `wechat2md/` | 微信文章转 Markdown 转换器 |
| ├── `sync_to_github/` | 自动提交和推送 |
| ├── `portpilot-assistant/` | 本地开发端口自然语言管理 |
| ├── `zimage-api/` | 漫画风格图像生成（云端 API） |
| ├── `zimage-local/` | 漫画风格图像生成（本地 ComfyUI） |
| └── `zimage-core/` | Z-Image 共享核心模块 |
| `.postmortem/` | 事故和 Bug 的详细分析报告 |
| `CLAUDE.md` | 项目开发指南 |
| `README.md` | 本文件 |

### 🎯 核心功能

#### 笔记生成系统
- **编排器模式**：`note-creator` 分类意图并委托给格式技能
- **多格式输出**：Markdown、Canvas 图表、Base 表格
- **智能分类**：自动检测内容类型并生成适当的产物
- **文件夹组织**：基于白名单的文件夹系统，构建结构化知识库

#### 微信文章归档
- **微信文章转 Markdown**：转换文章并下载本地图片
- **结构化笔记**：自动生成摘要、要点和元数据
- **批量处理**：从 inbox.md 文件批量处理多个 URL
- **幂等性**：相同 URL 不会创建重复内容
- **自包含输出**：文章和图片在单一可移植目录中

#### 质量保证
- **事后分析报告**：6 个已解决问题的详细分析
- **透明开发**：公开记录问题和修复过程
- **持续改进**：从错误中学习，防止再次发生

### 📖 使用示例

#### 归档微信文章

```bash
# 使用 Claude Skill - 单篇文章
Skill(wechat-archiver, args="https://mp.weixin.qq.com/s/your-article-url")

# 输出目录：outputs/20-阅读笔记/YYYYMMDD-slug-abcdef/
# - article.md       # 原始文章
# - note.md          # 结构化笔记
# - images/          # 下载的图片
# - meta.json        # 元数据

# 使用 Claude Skill - 合集/专题（批量下载）
Skill(wechat-archiver, args="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=xxx&album_id=xxx")

# 输出目录：outputs/20-阅读笔记/合集名称/
# - _index.md                    # 索引文件（包含所有文章链接）
# - 001-第一篇文章/
#   ├── article.md
#   └── images/
# - 002-第二篇文章/
#   ├── article.md
#   └── images/
# ... (所有文章按发布时间编号)
```

#### 从 inbox.md 批量归档

```bash
# 创建包含微信 URL 的 inbox.md（每行一个）
# 支持格式：纯 URL、markdown 链接、任务列表
- [ ] https://mp.weixin.qq.com/s/article1
- [x] https://mp.weixin.qq.com/s/已处理  # 将被跳过
- [ ] https://mp.weixin.qq.com/s/article2

# 运行批量归档
Skill(wechat-archiver, args="--batch inbox.md")

# 处理后 URL 会自动标记为 [x]
```

#### 创建对比表格

```bash
# 使用 note-creator
Skill(note-creator, "对比 Obsidian Skills: markdown, canvas, 和 base")

# 输出：outputs/30-方法论/obsidian-skills-comparison-*/
# - note.md          # 对比文章
# - table.base       # 对比表格
# - compare/         # 各项的独立文件
```

#### 生成技术图表

```bash
# 创建架构图
Skill(note-creator, "创建 note-creator 工作流的架构图")

# 输出：outputs/30-方法论/*/diagram.canvas
```

#### 生成漫画风格图像

```bash
# 让 Claude Code 分析并转换图片
"帮我把这张照片转成北条司风格"
"把 input/photo.jpg 转成漆原智志风格"

# 或直接提供提示词
cd .claude/skills/zimage-local
python generate.py "1girl, solo, glasses, smile, portrait" hojo

# 输出：outputs/zimage/zimage_hojo_local_*.png
```

### 🛠️ Skills 参考

#### 核心 Skills

1. **note-creator**（编排器）
   - 分类用户意图
   - 委托给格式技能
   - 将所有产物写入磁盘
   - 位置：`.claude/skills/note-creator/SKILL.md`

2. **obsidian-markdown**
   - 生成有效的 Obsidian Flavored Markdown
   - 包含 YAML frontmatter、标签、wikilinks
   - 位置：`.claude/skills/obsidian-markdown/SKILL.md`

3. **json-canvas**
   - 创建 Obsidian Canvas 格式的可视化图表
   - 支持流程图、时序图、架构图
   - 位置：`.claude/skills/json-canvas/SKILL.md`

4. **obsidian-bases**
   - 生成数据库式表格视图
   - 支持对比模式和自动生成的行
   - 位置：`.claude/skills/obsidian-bases/SKILL.md`

#### 工具 Skills

5. **wechat-archiver**（编排器）
   - 编排微信文章归档的完整工作流
   - 调用 **wechat2md** 进行 HTML → Markdown 转换
   - 调用 **note-creator** 生成结构化笔记
   - 支持从 inbox.md 批量处理，带进度条和预计剩余时间
   - 管理资产目录和元数据
   - 位置：`.claude/skills/wechat-archiver/SKILL.md`

6. **wechat2md**（被 wechat-archiver 调用）
   - 将微信文章转换为干净的 Markdown
   - 下载所有图片到自包含输出目录
   - **合集/专题批量下载**：一个 URL 下载整个系列文章（8 篇文章仅需 1 条命令）
   - **智能 URL 识别**：自动识别单篇文章或合集，保持向后兼容
   - **按时间自动排序**：文章按发布顺序编号（001, 002, 003...）
   - **索引自动生成**：自动创建 `_index.md` 包含所有文章链接
   - **知识库集成**：可配置输出路径、frontmatter 和元数据
   - 正确的段落分隔和代码块格式
   - 将内联样式转换为原生 Markdown 语法
   - 自动修复纯文本 URL 为 Markdown 链接
   - 自动检测代码语言用于语法高亮
   - **向后兼容**：无配置时保持 v1 行为，有 config.json 时启用增强功能
   - 位置：`.claude/skills/wechat2md/SKILL.md`

7. **sync_to_github**
   - 自动化 git 工作流
   - AI 生成的提交信息
   - 可选推送到远程
   - 位置：`.claude/skills/sync_to_github/SKILL.md`

8. **portpilot-assistant**
   - 通过 PortPilot CLI 用自然语言管理本地开发端口
   - 支持 `scan`、`who`、`pick`、`doctor` 等只读操作直接执行
   - 对 `free`、`init --force`、`config migrate` 等写操作要求显式确认
   - 位置：`.claude/skills/portpilot-assistant/SKILL.md`

#### 图像生成 Skills

9. **zimage-api**
   - 使用 Replicate 云端 API 生成漫画风格图像
   - 支持北条司风格（黑白漫画）和漆原智志风格（90年代动漫）
   - Claude Code 自动分析图片并生成提示词
   - 无需本地 GPU
   - 位置：`.claude/skills/zimage-api/SKILL.md`

10. **zimage-local**
   - 使用本地 ComfyUI 生成漫画风格图像
   - 与 API 版支持相同的风格
   - **完全免费** - 无 API 费用
   - 需要本地 GPU（4GB+ 显存）
   - 位置：`.claude/skills/zimage-local/SKILL.md`

### 📊 输出结构

```
outputs/
├── 00-Inbox/           # 未分类/临时
├── 10-项目/            # 项目特定笔记
├── 20-阅读笔记/         # 阅读笔记、文章摘要
├── 30-方法论/          # 方法、对比、框架
├── 40-工具脚本/         # 实际可执行的脚本/工具
├── 50-运维排障/         # 故障排查、调试
├── 60-数据与表/         # 数据库架构、数据模型
└── 90-归档/            # 已弃用/已完成
```

### 🔒 安全与隐私

- ✅ 仓库中无硬编码凭证
- ✅ `.gitignore` 正确配置
- ✅ 本地设置已排除（`.claude/settings.local.json`）
- ✅ Obsidian 配置已从历史中清除
- ✅ 事后分析报告公开分享

### 📚 文档

- **`CLAUDE.md`** - 项目开发指南
- **`.postmortem/README.md`** - 事后分析报告索引
- **`.claude/skills/*/SKILL.md`** - 各个技能的文档
- **`.claude/skills/*/REFERENCE.md`** - 技术参考

### 🐛 已知问题

详见 [`.postmortem/README.md`](.postmortem/README.md)：
- POSTMORTEM-2026-001: Base 过滤器失败（P0）✅ 已解决
- POSTMORTEM-2026-002: Base 路径解析（P0）✅ 已解决
- POSTMORTEM-2026-003: Windows 编码（P1）✅ 已解决
- POSTMORTEM-2026-004: 过度检测（P2）✅ 已解决
- POSTMORTEM-2026-005: 重复摄取（P2）⏳ 部分解决
- POSTMORTEM-2026-006: 图片路径错误（P1）✅ 已解决

### 🔗 相关资源

- [Claude Code 文档](https://code.claude.com/docs)
- [Obsidian 插件文档](https://docs.obsidian.md/)
- [JSON Canvas 规范](https://github.com/obsidianmd/jsoncanvas)

### 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

- Follow the patterns in existing skills
- Update documentation for new features
- Add postmortem reports for bugs
- Test on multiple platforms (Windows, macOS, Linux)

### Postmortem Process

When you encounter or fix a bug:
1. Document it in `.postmortem/POSTMORTEM-YYYY-NNN-title.md`
2. Follow the existing report structure
3. Update `.postmortem/README.md` statistics
4. Commit with descriptive message

---

## 📝 Changelog

### 2026-02-14
- **portpilot-assistant**: Add natural-language local dev port management skill
  - Added `.claude/skills/portpilot-assistant` to the project skill set
  - Updated README project structure and skill references (English & Chinese)

### 2026-01-29
- **wechat2md**: Add album/collection batch download feature
  - **One-command batch download**: Download entire article series with single URL (8 articles → 1 command)
  - **Smart URL detection**: Auto-detects single article vs album URLs, fully backward compatible
  - **Time-based sorting**: Articles automatically numbered by publication order (001, 002, 003...)
  - **Index generation**: Auto-creates `_index.md` with links to all articles in collection
  - **Folder isolation**: Each album uses unique folder name to prevent overwriting
  - **Error recovery**: Single article failure doesn't block other downloads
  - **26 new unit tests**: Comprehensive test coverage for URL detection, parsing, downloading, and index generation
  - **91% time savings**: 8-article series from ~12 minutes manual work to ~1 minute automated
  - **Technical article**: Created `outputs/skill-engineering-10-album-download.md` following "Skill 工程化" series style
  - **Documentation updates**:
    - Updated README.md with album usage examples (English & Chinese)
    - Enhanced wechat2md feature description
    - Added comprehensive changelog entry
    - Corrected article descriptions to reflect skill-based workflow (Claude Code interactions, not manual Python commands)

### 2026-01-19
- **wechat2md**: Add knowledge base configuration system
  - **Configurable output paths**: Custom folder structure with template variables
  - **Slug generation**: Support `title`, `date-title`, and `date-title-hash` formats
  - **YAML frontmatter**: Optional frontmatter with configurable fields (title, author, created, source, tags)
  - **Meta.json generation**: Optional metadata file for knowledge base integration
  - **Tag management**: Default tags, deduplication, and max count limits
  - **Folder whitelist**: Optional validation for knowledge base folder structure
  - **Backward compatible**: v1 behavior without config.json, enhanced features with configuration
  - **Comprehensive testing**: 107 unit, integration, and E2E tests (100% pass rate)
  - See `.claude/skills/wechat2md/TEST_REPORT.md` for detailed test results

### 2026-01-18
- **wechat-archiver**: Add batch processing from inbox.md
  - Extract URLs from markdown files (plain URLs, links, task lists)
  - Auto-mark processed URLs as `[x]` in source file
  - Checkpoint support for resuming interrupted batches
  - Progress bar with percentage and ETA display
- **wechat2md**: Major format quality improvements
  - Proper paragraph separation for nested sections
  - Code blocks with correct line breaks
  - Convert inline styles to native Markdown syntax
  - Self-contained output (images in article subdirectory)
  - Auto-fix plain text URLs to markdown links (`地址→github.com` → `[地址](https://github.com)`)
  - Auto-detect code language for syntax highlighting (Python, JS, Go, Rust, C/C++, etc.)
- **tests**: Add 40 unit tests for wechat2md (all passing)

### 2026-01-16
- Add Z-Image skills for manga-style image generation
  - `zimage-api`: Cloud-based generation via Replicate API
  - `zimage-local`: Local generation via ComfyUI
  - `zimage-core`: Shared core modules
- Support Hojo Tsukasa (B&W manga) and Urushihara Satoshi (90s anime) styles
- Claude Code directly analyzes images - no extra API costs

### 2026-01-12
- ✅ Add postmortem reports (6 incidents)
- ✅ Clean .obsidian/ from git history
- ✅ Fix image path handling in wechat2md
- ✅ Update skill documentation
- ✅ Add REFERENCE.md files for format skills

### Previous Changes
See git log for detailed history: `git log --oneline`

---

**Made with ❤️ by [lingengyuan](https://github.com/lingengyuan) and [Claude Code](https://code.claude.com)**
