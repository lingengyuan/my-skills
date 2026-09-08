# My Skills

[English](#english) | [简体中文](#简体中文)

## English

Independent Claude/Codex Skills for technical writing, knowledge management, and development. Each directory under `.claude/skills/` includes its instructions and supporting resources.

### Skills

| Skill | Purpose |
|---|---|
| [beautiful-mermaid](.claude/skills/beautiful-mermaid/SKILL.md) | Render Mermaid as SVG or terminal text |
| [brief-output](.claude/skills/brief-output/SKILL.md) | Write concise, professional content |
| [insight-collector](.claude/skills/insight-collector/SKILL.md) | Archive reusable insights |
| [json-canvas](.claude/skills/json-canvas/SKILL.md) | Create and edit JSON Canvas files |
| [md2wechat](.claude/skills/md2wechat/SKILL.md) | Format WeChat articles and publish drafts |
| [note-creator](.claude/skills/note-creator/SKILL.md) | Create Obsidian note packages |
| [obsidian-bases](.claude/skills/obsidian-bases/SKILL.md) | Create and edit Obsidian Bases |
| [obsidian-markdown](.claude/skills/obsidian-markdown/SKILL.md) | Write Obsidian Markdown |
| [portpilot-assistant](.claude/skills/portpilot-assistant/SKILL.md) | Inspect and manage development ports |
| [publication-ready-docs](.claude/skills/publication-ready-docs/SKILL.md) | Prepare technical documents for publication |
| [readme-maintainer](.claude/skills/readme-maintainer/SKILL.md) | Maintain concise READMEs from repository facts |
| [sync-to-github](.claude/skills/sync-to-github/SKILL.md) | Commit and push within the requested scope |
| [tech-article](.claude/skills/tech-article/SKILL.md) | Write Chinese technical articles |
| [wechat-archiver](.claude/skills/wechat-archiver/SKILL.md) | Archive WeChat articles as knowledge assets |
| [wechat2md](.claude/skills/wechat2md/SKILL.md) | Convert WeChat articles and albums to Markdown |

### Setup and use

```sh
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
```

Open the repository in Claude Code, or copy the entire selected Skill directory into your Agent’s skills directory. Follow its `SKILL.md` for dependencies, configuration, and usage; install dependencies only for the Skills you use.

`portpilot-assistant` requires Node.js 18+. Keep credentials in local configuration: `md2wechat/.env` uses `WECHAT_APPID` and `WECHAT_SECRET`; `wechat2md/config.json` holds optional output rules. These paths are relative to `.claude/skills/` and ignored by Git.

## 简体中文

用于技术写作、知识管理和开发的独立 Claude/Codex Skills。每个 Skill 的说明与配套资源位于 `.claude/skills/`。

### Skill 目录

| Skill | 用途 |
|---|---|
| [beautiful-mermaid](.claude/skills/beautiful-mermaid/SKILL.md) | 将 Mermaid 渲染为 SVG 或终端文本 |
| [brief-output](.claude/skills/brief-output/SKILL.md) | 精炼专业表达 |
| [insight-collector](.claude/skills/insight-collector/SKILL.md) | 归档可复用洞察 |
| [json-canvas](.claude/skills/json-canvas/SKILL.md) | 创建和编辑 JSON Canvas |
| [md2wechat](.claude/skills/md2wechat/SKILL.md) | 排版微信文章并发布草稿 |
| [note-creator](.claude/skills/note-creator/SKILL.md) | 创建 Obsidian 笔记包 |
| [obsidian-bases](.claude/skills/obsidian-bases/SKILL.md) | 创建和编辑 Obsidian Bases |
| [obsidian-markdown](.claude/skills/obsidian-markdown/SKILL.md) | 编写 Obsidian Markdown |
| [portpilot-assistant](.claude/skills/portpilot-assistant/SKILL.md) | 检查和管理开发端口 |
| [publication-ready-docs](.claude/skills/publication-ready-docs/SKILL.md) | 整理可交付的正式技术文档 |
| [readme-maintainer](.claude/skills/readme-maintainer/SKILL.md) | 基于仓库事实维护精简 README |
| [sync-to-github](.claude/skills/sync-to-github/SKILL.md) | 按授权范围提交和推送 |
| [tech-article](.claude/skills/tech-article/SKILL.md) | 撰写中文技术文章 |
| [wechat-archiver](.claude/skills/wechat-archiver/SKILL.md) | 将微信文章归档为知识资产 |
| [wechat2md](.claude/skills/wechat2md/SKILL.md) | 将微信文章和合集转换为 Markdown |

### 安装与使用

```sh
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
```

在 Claude Code 中打开仓库，或将所选 Skill 的完整目录复制到 Agent 的 skills 目录。按对应 `SKILL.md` 安装依赖、配置和使用；依赖按需安装。

`portpilot-assistant` 需要 Node.js 18+。凭据保存在本地配置：`md2wechat/.env` 使用 `WECHAT_APPID` 和 `WECHAT_SECRET`；`wechat2md/config.json` 保存可选输出规则。路径均相对于 `.claude/skills/`，这些配置文件由 Git 忽略。

[MIT License](LICENSE)
