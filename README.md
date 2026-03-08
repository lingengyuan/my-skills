# My Skills Framework

[English](#english) | [简体中文](#简体中文)

Reusable workspace for building, maintaining, and testing local Claude/Codex skills.

<a name="english"></a>
## English

### Project Description

This repository is a skill engineering workspace centered on `.claude/skills/`.

It combines:
- orchestrator skills that route multi-step workflows,
- specialized format and utility skills backed by local scripts,
- postmortem records for regressions and fixes,
- reference docs and example assets for ongoing maintenance.

### Features

- Orchestrator pattern for higher-level workflows such as note generation and WeChat article archiving.
- Script-backed utilities for documentation maintenance, Git automation, WeChat publishing, and local port management.
- Obsidian-oriented output skills for Markdown, Canvas, and Bases artifacts.
- Image generation helpers for Replicate-backed and local ComfyUI-backed workflows.
- Repository-grounded maintenance workflow with `SKILL.md`, references, tests, and postmortems.

### Install

Prerequisites:
- Git
- Python 3.8+

Clone the repository and activate the local virtual environment:

```bash
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
python3 -m venv .venv
source set_env.sh
# Windows: set_env.bat
```

Install the base dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Install optional skill-specific dependencies when you plan to use those skills:

```bash
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt
```

### Quick Start

Examples below are assistant-session prompts, not shell commands:

```text
Archive this WeChat article: https://mp.weixin.qq.com/s/your-article-url
Create a comparison note for markdown, canvas, and bases
Update README based on current repository facts
Convert input/photo.jpg to Hojo style
```

Useful local entrypoints in this repo:

```bash
python .claude/skills/wechat2md/tools/wechat2md_v2.py --help
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py --help
python .claude/skills/sync_to_github/tools/git_sync.py --help
bash .claude/skills/portpilot-assistant/scripts/run_portpilot.sh --help
```

### Skill Catalog

| Skill | Type | Purpose | Path |
|---|---|---|---|
| `note-creator` | Orchestrator | Create structured Obsidian notes and delegate to format skills | `.claude/skills/note-creator` |
| `wechat-archiver` | Orchestrator | Archive WeChat articles and trigger note generation workflow | `.claude/skills/wechat-archiver` |
| `readme-maintainer` | Documentation | Update or rewrite README files from repository facts | `.claude/skills/readme-maintainer` |
| `obsidian-markdown` | Format | Create and edit Obsidian-flavored Markdown | `.claude/skills/obsidian-markdown` |
| `json-canvas` | Format | Create and edit Obsidian Canvas files | `.claude/skills/json-canvas` |
| `obsidian-bases` | Format | Create and edit Obsidian Bases files | `.claude/skills/obsidian-bases` |
| `wechat2md` | Utility | Convert WeChat articles to local Markdown with downloaded images | `.claude/skills/wechat2md` |
| `md2wechat` | Utility | Convert Markdown to WeChat HTML and optionally publish drafts | `.claude/skills/md2wechat` |
| `sync_to_github` | Utility | Analyze changes, generate commit messages, and commit/push | `.claude/skills/sync_to_github` |
| `portpilot-assistant` | Utility | Manage local development ports through PortPilot CLI | `.claude/skills/portpilot-assistant` |
| `zimage-api` | Image | Generate stylized images through Replicate | `.claude/skills/zimage-api` |
| `zimage-local` | Image | Generate stylized images through local ComfyUI | `.claude/skills/zimage-local` |
| `insight-collector` | Knowledge | Extract reusable insights into the CodeSnippets knowledge base | `.claude/skills/insight-collector` |

Shared module:

| Module | Purpose | Path |
|---|---|---|
| `zimage-core` | Shared logic used by `zimage-api` and `zimage-local` | `.claude/skills/zimage-core` |

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
│       ├── insight-collector/
│       └── zimage-core/
├── .postmortem/          # incident reports and fix history
├── docs/                 # project docs and images
├── outputs/              # generated artifacts at runtime
├── requirements.txt
├── set_env.sh
├── set_env.bat
└── README.md
```

### Configuration

Only some skills require extra configuration. Create a project-level `.env` file when needed:

```env
REPLICATE_API_TOKEN=r8_your_token_here
COMFYUI_SERVER=127.0.0.1:8188
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
```

Use the variables that match the skills you actually run:
- `REPLICATE_API_TOKEN`: required by `zimage-api`
- `COMFYUI_SERVER`: optional override for `zimage-local`
- `WECHAT_APPID` / `WECHAT_SECRET`: required for draft publishing in `md2wechat`

### Development and Testing

Activate the virtual environment before running local checks:

```bash
source set_env.sh
```

Verified checks in this repository:

```bash
python -m pytest .claude/skills/wechat2md/tests -q
python .claude/skills/wechat2md/tools/wechat2md_v2.py --help
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py --help
python .claude/skills/sync_to_github/tools/git_sync.py --help
bash .claude/skills/portpilot-assistant/scripts/run_portpilot.sh --help
```

### Contributing

1. Update the target skill under `.claude/skills/<skill-name>/`.
2. Keep `SKILL.md`, scripts, references, and examples consistent.
3. Add or update tests when behavior changes.
4. Update this README in both languages when externally visible workflows change.
5. Record major failures or regressions in `.postmortem/`.

### Maintenance Guide

Use the readme maintenance helpers when refreshing repository documentation:

```bash
.claude/skills/readme-maintainer/scripts/collect_repo_facts.sh .
.claude/skills/readme-maintainer/scripts/check_bilingual_readme.sh README.md
```

Recommended maintenance rules:
- Keep the skill catalog aligned with `.claude/skills/*/SKILL.md`.
- Re-verify every documented command against the repository before publishing changes.
- Treat `outputs/` as generated content rather than a source directory.
- Keep English and Simplified Chinese sections aligned section-by-section.

### License

MIT. See `LICENSE`.

<a name="简体中文"></a>
## 简体中文

### 项目说明

本仓库是一个围绕 `.claude/skills/` 组织的本地技能工程工作区。

它包含：
- 用于串联多步骤流程的编排技能，
- 由本地脚本支撑的格式技能和工具技能，
- 用于记录回归与修复的 postmortem 文档，
- 用于持续维护的参考资料与示例资源。

### 功能特性

- 使用编排模式承载更高层的工作流，例如笔记生成与微信公众号文章归档。
- 提供脚本化工具能力，覆盖 README 维护、Git 自动化、微信公众号排版发布与本地端口管理。
- 面向 Obsidian 的 Markdown、Canvas、Bases 产物生成能力。
- 同时支持 Replicate 云端和本地 ComfyUI 的图像生成辅助能力。
- 通过 `SKILL.md`、参考资料、测试和 postmortem 构成基于仓库事实的维护流程。

### 安装

前置要求：
- Git
- Python 3.8+

克隆仓库并激活本地虚拟环境：

```bash
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
python3 -m venv .venv
source set_env.sh
# Windows: set_env.bat
```

安装仓库根目录的基础依赖：

```bash
pip install -r requirements.txt
```

如果你准备使用对应技能，再安装技能级依赖：

```bash
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/zimage-core/requirements.txt
```

### 快速开始

下面示例是给助手会话使用的提示语，不是 shell 命令：

```text
归档这篇微信文章：https://mp.weixin.qq.com/s/your-article-url
创建一篇比较 markdown、canvas、bases 的笔记
基于当前仓库事实更新 README
把 input/photo.jpg 转成北条司风格
```

本仓库中常用的本地入口命令：

```bash
python .claude/skills/wechat2md/tools/wechat2md_v2.py --help
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py --help
python .claude/skills/sync_to_github/tools/git_sync.py --help
bash .claude/skills/portpilot-assistant/scripts/run_portpilot.sh --help
```

### 技能目录

| 技能 | 类型 | 主要用途 | 路径 |
|---|---|---|---|
| `note-creator` | 编排 | 生成结构化 Obsidian 笔记并调度格式技能 | `.claude/skills/note-creator` |
| `wechat-archiver` | 编排 | 归档微信公众号文章并触发笔记生成流程 | `.claude/skills/wechat-archiver` |
| `readme-maintainer` | 文档 | 基于仓库事实更新或重写 README | `.claude/skills/readme-maintainer` |
| `obsidian-markdown` | 格式 | 创建和编辑 Obsidian 风格 Markdown | `.claude/skills/obsidian-markdown` |
| `json-canvas` | 格式 | 创建和编辑 Obsidian Canvas 文件 | `.claude/skills/json-canvas` |
| `obsidian-bases` | 格式 | 创建和编辑 Obsidian Bases 文件 | `.claude/skills/obsidian-bases` |
| `wechat2md` | 工具 | 将微信文章转换为本地 Markdown 并下载图片 | `.claude/skills/wechat2md` |
| `md2wechat` | 工具 | 将 Markdown 转为微信公众号 HTML，并可选发布草稿 | `.claude/skills/md2wechat` |
| `sync_to_github` | 工具 | 分析改动、生成提交信息并执行提交/推送 | `.claude/skills/sync_to_github` |
| `portpilot-assistant` | 工具 | 通过 PortPilot CLI 管理本地开发端口 | `.claude/skills/portpilot-assistant` |
| `zimage-api` | 图像 | 通过 Replicate 生成风格化图像 | `.claude/skills/zimage-api` |
| `zimage-local` | 图像 | 通过本地 ComfyUI 生成风格化图像 | `.claude/skills/zimage-local` |
| `insight-collector` | 知识 | 将可复用洞察整理进 CodeSnippets 知识库 | `.claude/skills/insight-collector` |

共享模块：

| 模块 | 主要用途 | 路径 |
|---|---|---|
| `zimage-core` | `zimage-api` 与 `zimage-local` 共享的核心逻辑 | `.claude/skills/zimage-core` |

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
│       ├── insight-collector/
│       └── zimage-core/
├── .postmortem/          # 事故复盘与修复记录
├── docs/                 # 项目文档与示例图片
├── outputs/              # 运行时生成的产物目录
├── requirements.txt
├── set_env.sh
├── set_env.bat
└── README.md
```

### 配置

只有部分技能需要额外配置。需要时可在项目根目录创建 `.env` 文件：

```env
REPLICATE_API_TOKEN=r8_your_token_here
COMFYUI_SERVER=127.0.0.1:8188
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
```

变量用途如下：
- `REPLICATE_API_TOKEN`：`zimage-api` 必需
- `COMFYUI_SERVER`：`zimage-local` 的可选地址覆盖
- `WECHAT_APPID` / `WECHAT_SECRET`：`md2wechat` 发布草稿时必需

### 开发与测试

运行本地检查前先激活虚拟环境：

```bash
source set_env.sh
```

已在当前仓库中验证的检查命令：

```bash
python -m pytest .claude/skills/wechat2md/tests -q
python .claude/skills/wechat2md/tools/wechat2md_v2.py --help
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py --help
python .claude/skills/sync_to_github/tools/git_sync.py --help
bash .claude/skills/portpilot-assistant/scripts/run_portpilot.sh --help
```

### 贡献指南

1. 在 `.claude/skills/<skill-name>/` 下修改目标技能。
2. 保持 `SKILL.md`、脚本、参考资料和示例一致。
3. 行为变化时补充或更新测试。
4. 对外可见流程变化后，同步更新本 README 的中英文内容。
5. 重大故障或回归问题记录到 `.postmortem/`。

### 维护指南

更新仓库文档时，优先使用 README 维护辅助脚本：

```bash
.claude/skills/readme-maintainer/scripts/collect_repo_facts.sh .
.claude/skills/readme-maintainer/scripts/check_bilingual_readme.sh README.md
```

建议遵守以下维护规则：
- 让技能目录与 `.claude/skills/*/SKILL.md` 保持一致。
- 发布 README 变更前，重新核对每一条命令和路径。
- 将 `outputs/` 视为生成内容，而不是源码目录。
- 保持英文与简体中文章节逐一对应。

### 许可证

MIT，详见 `LICENSE`。
