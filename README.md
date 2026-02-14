# My Skills Framework

[English](#english) | [简体中文](#简体中文)

Reusable skill engineering workspace for Claude/Codex.

<a name="english"></a>
## English

### Project Description

This repository standardizes how we build, operate, and improve local coding skills.

- Keep skills in one place under `.claude/skills/`.
- Prefer deterministic scripts for repeatable execution.
- Capture failures in `.postmortem/` and feed fixes back into skills.

### Features

- Orchestrator + specialized skill composition (for example `note-creator` + format skills).
- Script-first execution for high-repeatability tasks.
- Skill-level documentation contracts (`SKILL.md`) for consistent triggering and behavior.
- Postmortem-driven maintenance workflow for quality and reliability.

### Quick Start

1. Clone repository.

```bash
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
```

2. Create and activate virtual environment.

```bash
python3 -m venv .venv
source set_env.sh
# Windows: set_env.bat
```

3. Install skill dependencies.

```bash
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt
```

4. Example skill calls (in a skill-enabled session).

```bash
Skill(wechat-archiver, args="https://mp.weixin.qq.com/s/your-article-url")
Skill(note-creator, "Create a comparison note for markdown/canvas/base")
Skill(readme-maintainer, "Update README based on current repository facts")
```

### Skill Catalog

| Skill | Type | Purpose | Path |
|---|---|---|---|
| `note-creator` | Orchestrator | Build structured notes and delegate markdown/canvas/base generation | `.claude/skills/note-creator` |
| `wechat-archiver` | Orchestrator | Archive WeChat articles and drive note creation workflow | `.claude/skills/wechat-archiver` |
| `readme-maintainer` | Documentation | Update/rewrite README from repository facts | `.claude/skills/readme-maintainer` |
| `obsidian-markdown` | Format | Generate Obsidian flavored Markdown artifacts | `.claude/skills/obsidian-markdown` |
| `json-canvas` | Format | Generate/edit `.canvas` visual artifacts | `.claude/skills/json-canvas` |
| `obsidian-bases` | Format | Generate/edit `.base` views, filters, formulas | `.claude/skills/obsidian-bases` |
| `wechat2md` | Utility | Convert WeChat article HTML to Markdown with local images | `.claude/skills/wechat2md` |
| `md2wechat` | Utility | Convert Markdown to WeChat HTML and optionally publish draft | `.claude/skills/md2wechat` |
| `sync_to_github` | Utility | Analyze changes and create/push commits | `.claude/skills/sync_to_github` |
| `portpilot-assistant` | Utility | Natural-language local port management | `.claude/skills/portpilot-assistant` |
| `zimage-api` | Image | Generate manga-style images with Replicate API | `.claude/skills/zimage-api` |
| `zimage-local` | Image | Generate manga-style images with local ComfyUI | `.claude/skills/zimage-local` |

Shared module (not a standalone skill):

| Module | Purpose | Path |
|---|---|---|
| `zimage-core` | Shared core logic for `zimage-api` and `zimage-local` | `.claude/skills/zimage-core` |

### Project Structure

```text
.
├── .claude/
│   └── skills/
│       ├── note-creator/
│       ├── wechat-archiver/
│       ├── readme-maintainer/
│       ├── obsidian-markdown/
│       ├── json-canvas/
│       ├── obsidian-bases/
│       ├── wechat2md/
│       ├── md2wechat/
│       ├── sync_to_github/
│       ├── portpilot-assistant/
│       ├── zimage-api/
│       ├── zimage-local/
│       └── zimage-core/
├── .postmortem/
├── docs/
├── requirements.txt
├── set_env.sh
├── set_env.bat
└── README.md
```

### Configuration

Optional environment variables (needed only for `zimage-api`):

```bash
cat > .env <<'ENV'
REPLICATE_API_TOKEN=r8_your_token_here
ENV
```

### Development and Testing

Install required packages first, then run focused checks.

```bash
# Ensure dependencies are available in the current environment
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt

# Unit tests currently maintained for wechat2md
python -m pytest .claude/skills/wechat2md/tests -q

# Smoke checks for key CLI tools
python .claude/skills/wechat2md/tools/wechat2md_v2.py --help
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py --help
python .claude/skills/sync_to_github/tools/git_sync.py --help
```

### Contributing

1. Update the target skill under `.claude/skills/<skill-name>/`.
2. Keep `SKILL.md` and scripts/references consistent.
3. If behavior changes, update this README section(s) in both English and Chinese.
4. Add or update postmortem records for major incidents.

### Maintenance Guide

- Always back up README before major rewrites.
- Run repository fact collection before editing documentation.
- Keep bilingual sections aligned section-by-section.
- Keep skill catalog synced with `.claude/skills/*/SKILL.md`.
- Sync local skills to `~/.codex/skills` when required.

```bash
cp README.md README.backup-$(date +%Y%m%d-%H%M%S).md
~/.codex/skills/readme-maintainer/scripts/collect_repo_facts.sh .
```

### License

MIT. See `LICENSE`.

<a name="简体中文"></a>
## 简体中文

### 项目说明

本仓库用于统一建设、运行和迭代本地 Claude/Codex 技能。

- 技能统一放在 `.claude/skills/`。
- 高频流程优先脚本化，保证可重复执行。
- 故障通过 `.postmortem/` 复盘，并反哺技能改进。

### 功能特性

- 编排技能 + 专用技能组合（例如 `note-creator` 调度格式技能）。
- 脚本优先的执行方式，减少重复手工操作。
- 通过 `SKILL.md` 约束触发条件与执行契约。
- 通过 postmortem 持续治理质量与稳定性。

### 快速开始

1. 克隆仓库。

```bash
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
```

2. 创建并激活虚拟环境。

```bash
python3 -m venv .venv
source set_env.sh
# Windows: set_env.bat
```

3. 安装技能依赖。

```bash
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt
```

4. 常见技能调用示例（在支持 Skill 的会话中）。

```bash
Skill(wechat-archiver, args="https://mp.weixin.qq.com/s/your-article-url")
Skill(note-creator, "生成 markdown/canvas/base 对比笔记")
Skill(readme-maintainer, "基于当前仓库事实更新 README")
```

### 技能目录

| 技能 | 类型 | 主要用途 | 路径 |
|---|---|---|---|
| `note-creator` | 编排 | 生成结构化笔记并调度 markdown/canvas/base | `.claude/skills/note-creator` |
| `wechat-archiver` | 编排 | 微信文章归档并串联笔记生成流程 | `.claude/skills/wechat-archiver` |
| `readme-maintainer` | 文档 | 基于仓库事实更新/重写 README | `.claude/skills/readme-maintainer` |
| `obsidian-markdown` | 格式 | 生成 Obsidian 风格 Markdown | `.claude/skills/obsidian-markdown` |
| `json-canvas` | 格式 | 生成/编辑 `.canvas` 可视化图 | `.claude/skills/json-canvas` |
| `obsidian-bases` | 格式 | 生成/编辑 `.base` 视图、筛选、公式 | `.claude/skills/obsidian-bases` |
| `wechat2md` | 工具 | 微信文章 HTML 转 Markdown 并下载图片 | `.claude/skills/wechat2md` |
| `md2wechat` | 工具 | Markdown 转微信公众号 HTML，可选发布草稿 | `.claude/skills/md2wechat` |
| `sync_to_github` | 工具 | 分析改动并生成/推送提交 | `.claude/skills/sync_to_github` |
| `portpilot-assistant` | 工具 | 自然语言本地端口管理 | `.claude/skills/portpilot-assistant` |
| `zimage-api` | 图像 | 通过 Replicate API 生成漫画风图像 | `.claude/skills/zimage-api` |
| `zimage-local` | 图像 | 通过本地 ComfyUI 生成漫画风图像 | `.claude/skills/zimage-local` |

共享模块（非独立 skill）：

| 模块 | 用途 | 路径 |
|---|---|---|
| `zimage-core` | `zimage-api` 与 `zimage-local` 的共享核心逻辑 | `.claude/skills/zimage-core` |

### 项目结构

```text
.
├── .claude/
│   └── skills/
│       ├── note-creator/
│       ├── wechat-archiver/
│       ├── readme-maintainer/
│       ├── obsidian-markdown/
│       ├── json-canvas/
│       ├── obsidian-bases/
│       ├── wechat2md/
│       ├── md2wechat/
│       ├── sync_to_github/
│       ├── portpilot-assistant/
│       ├── zimage-api/
│       ├── zimage-local/
│       └── zimage-core/
├── .postmortem/
├── docs/
├── requirements.txt
├── set_env.sh
├── set_env.bat
└── README.md
```

### 配置

可选环境变量（仅 `zimage-api` 需要）：

```bash
cat > .env <<'ENV'
REPLICATE_API_TOKEN=r8_your_token_here
ENV
```

### 开发与测试

请先安装依赖，再执行聚焦检查。

```bash
# 先确保当前环境已安装依赖
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt

# 当前维护了 wechat2md 的单元测试
python -m pytest .claude/skills/wechat2md/tests -q

# 关键 CLI 工具冒烟检查
python .claude/skills/wechat2md/tools/wechat2md_v2.py --help
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py --help
python .claude/skills/sync_to_github/tools/git_sync.py --help
```

### 贡献指南

1. 在 `.claude/skills/<skill-name>/` 下修改目标技能。
2. 保持 `SKILL.md` 与 scripts/references 一致。
3. 若行为变化，同时更新 README 的英文与中文对应章节。
4. 重大故障需新增或更新 postmortem 记录。

### 维护指南

- 重大改写前先备份 README。
- 改文档前先跑仓库事实采集。
- 中英文章节必须一一对齐维护。
- 技能目录必须与 `.claude/skills/*/SKILL.md` 同步。
- 必要时把本地技能同步到 `~/.codex/skills`。

```bash
cp README.md README.backup-$(date +%Y%m%d-%H%M%S).md
~/.codex/skills/readme-maintainer/scripts/collect_repo_facts.sh .
```

### 许可证

MIT，详见 `LICENSE`。
