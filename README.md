# My Skills

[English](#english) | [简体中文](#简体中文)

<a id="english"></a>

## English

Standalone Claude/Codex Skills. Each Skill owns its instructions, scripts, dependencies, and configuration.

### Skills

| Skill | Purpose |
|---|---|
| `beautiful-mermaid` | Render Mermaid as SVG or terminal text |
| `brief-output` | Produce concise, professional output |
| `insight-collector` | Archive reusable insights |
| `json-canvas` | Create and validate JSON Canvas files |
| `md2wechat` | Render Markdown for WeChat and publish drafts |
| `note-creator` | Create Obsidian note packages |
| `obsidian-bases` | Create and validate Obsidian Bases |
| `obsidian-markdown` | Create Obsidian Markdown |
| `portpilot-assistant` | Inspect and manage development ports |
| `readme-maintainer` | Maintain README files from repository facts |
| `sync-to-github` | Commit staged changes and optionally push |
| `tech-article` | Write Chinese technical articles |
| `wechat-archiver` | Archive WeChat articles as knowledge assets |
| `wechat2md` | Convert WeChat articles and albums to Markdown |

### Install

```bash
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
```

Install dependencies only for the Skill that needs them:

```bash
npm install --prefix .claude/skills/beautiful-mermaid
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/wechat-archiver/requirements.txt
```

`portpilot-assistant` requires Node.js 18 or newer and supports Windows, macOS, and Linux.

### Configuration

- `md2wechat/.env`: `WECHAT_APPID`, `WECHAT_SECRET`
- `wechat2md/config.json`: optional output rules

Local configuration and temporary tests are ignored by Git.

### Rules

- Each directory under `.claude/skills/` must work independently.
- Dependencies and configuration belong inside the relevant Skill.
- Run structural and functional tests locally; do not commit temporary tests.
- The repository root contains only `.claude/skills/`, `.gitignore`, `LICENSE`, and `README.md`.

### License

MIT. See [LICENSE](LICENSE).

---

<a id="简体中文"></a>

## 简体中文

独立的 Claude/Codex Skills。每个 Skill 自带说明、脚本、依赖和配置。

### Skill 目录

| Skill | 用途 |
|---|---|
| `beautiful-mermaid` | 将 Mermaid 渲染为 SVG 或终端文本 |
| `brief-output` | 输出精炼、专业的内容 |
| `insight-collector` | 归档可复用洞察 |
| `json-canvas` | 创建并验证 JSON Canvas 文件 |
| `md2wechat` | 排版微信公众号 HTML 并发布草稿 |
| `note-creator` | 创建 Obsidian 笔记包 |
| `obsidian-bases` | 创建并验证 Obsidian Bases |
| `obsidian-markdown` | 创建 Obsidian Markdown |
| `portpilot-assistant` | 检查和管理开发端口 |
| `readme-maintainer` | 根据仓库事实维护 README |
| `sync-to-github` | 提交已暂存改动并可选推送 |
| `tech-article` | 撰写中文技术文章 |
| `wechat-archiver` | 将微信文章归档为知识资产 |
| `wechat2md` | 将微信文章和合集转换为 Markdown |

### 安装

```bash
git clone https://github.com/lingengyuan/my-skills.git
cd my-skills
```

只为需要的 Skill 安装依赖：

```bash
npm install --prefix .claude/skills/beautiful-mermaid
pip install -r .claude/skills/wechat2md/requirements.txt
pip install -r .claude/skills/wechat-archiver/requirements.txt
```

`portpilot-assistant` 需要 Node.js 18 或更高版本，支持 Windows、macOS 和 Linux。

### 配置

- `md2wechat/.env`：`WECHAT_APPID`、`WECHAT_SECRET`
- `wechat2md/config.json`：可选输出规则

本地配置和临时测试均被 Git 忽略。

### 规则

- `.claude/skills/` 下的每个目录必须能够独立使用。
- 依赖和配置必须放在对应 Skill 内。
- 结构和功能测试只在本地运行，不提交临时测试。
- 仓库根目录只保留 `.claude/skills/`、`.gitignore`、`LICENSE` 和 `README.md`。

### 许可证

MIT，详见 [LICENSE](LICENSE)。
