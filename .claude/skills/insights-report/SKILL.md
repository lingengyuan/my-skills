---
name: insights-report
description: Generate a usage insights report from local Claude Code, Codex, pi, and omp session transcripts. Use when the user asks for an insights report, session analysis, usage review, "how do I work with agents", or runs /insights-report.
---

# Insights Report

从本机 Claude Code、Codex、pi、omp 的会话记录生成 `/insights` 风格的 HTML 报告。采集和渲染由脚本完成，语义分析由当前 agent 完成。

## 支持的 agent

| agent | 数据来源 | 会话格式 |
|---|---|---|
| Claude Code | `~/.claude/projects/**/*.jsonl` | `user` / `assistant` 消息 + `tool_use` / `tool_result` 块 |
| Codex | `codex app-server` 的 `thread/list` + `thread/items/list`；旧版本回退到 `~/.codex/sessions/**/rollout-*.jsonl`、`~/.codex/archived_sessions/rollout-*.jsonl` | app-server 返回规范化 item；回退路径解析 `session_meta` + `response_item` + `event_msg` |
| pi | `~/.pi/agent/sessions/**/*.jsonl` | `session` + `message` + `toolCall` / `toolResult` |
| omp | `~/.omp/agent/sessions/**/*.jsonl` | 与 pi 相同的 JSONL 布局；未安装时自动跳过 |

路径可以用环境变量覆盖：`CLAUDE_CONFIG_DIR`、`CODEX_HOME`、`PI_HOME`、`OMP_HOME`。Codex 可执行文件可以用 `CODEX_BIN` 指定。

Codex 没有内置的 insights 报告命令。内置的会话入口是 `codex agents`、`codex resume --all`、`codex migrate-rollouts --json`，以及 app-server 的 `thread/*` 方法。脚本优先走 app-server；app-server 不可用时才解析 rollout 文件。

## 流程

### 1. 采集

```bash
python3 -I /Users/hughlin/.claude/skills/insights-report/scripts/collect.py --agent auto --days 30
```

默认输出到 `/Users/hughlin/.claude/usage-data/insights-skill/`：

- `stats.json`：聚合指标和会话列表。
- `digest.md`：给 agent 阅读的紧凑摘要。

参数：

- `--agent auto|all|claude,codex,omp,pi`：要扫描的 agent，可逗号分隔。`auto` 根据当前进程判断调用方 agent；判断不出时退回 `all`。默认 `auto`。
- `--days N`：只分析最近 N 天有更新的会话，`0` 表示全部。默认 30。
- `--max-sessions N`：最多分析多少个会话。默认 500。
- `--out DIR`：输出目录。
- `--facets-dir DIR`：facet 缓存目录。默认复用 `/Users/hughlin/.claude/usage-data/facets/`。
- `--emit-facets`：为没有 facet 的会话生成 `facets-todo.json`。

### 2. 阅读摘要

读取 `digest.md`。它包含 headline 指标、agent 分布、最多 50 条会话摘要、friction 明细和用户对 agent 的重复要求。所有结论必须以这些内容为依据。

### 3. 生成 analysis.json

按 `/Users/hughlin/.claude/skills/insights-report/references/prompts.md` 中的 8 个 section 和 schema，写一个 `analysis.json`。一次写完全部 section，不要逐段输出到对话。

要求：

- 用第二人称 "你"。
- 每条结论都能在 `digest.md` 中找到证据。
- 不要编造统计数字。
- 报告范围由 `--agent` 决定。单一 agent 的报告只写该 agent；跨 agent 报告要按 `Agent breakdown` 分别归因，不要默认写成 "Claude"。
- 建议里的命令、目录、配置文件必须属于报告范围内的 agent：Codex 用 `~/.codex/`、`AGENTS.md`、`codex exec`；Claude Code 用 `.claude/`、`CLAUDE.md`、`claude -p`。
- `at_a_glance` 最后写，内容来自前面 7 个 section。

### 4. 渲染

```bash
python3 -I /Users/hughlin/.claude/skills/insights-report/scripts/render_report.py \
  --stats /Users/hughlin/.claude/usage-data/insights-skill/stats.json \
  --analysis /Users/hughlin/.claude/usage-data/insights-skill/analysis.json \
  --out /Users/hughlin/.claude/usage-data/insights-report.html
```

### 5. 交付

回复报告路径，并给出 `at_a_glance` 的简短摘要。不要贴整份 HTML。

## 可选：补全 facet

Claude Code 的 `/insights` 会在 `~/.claude/usage-data/facets/` 留下缓存，脚本默认复用。Codex 和 pi 没有这份缓存，goal、outcome、satisfaction、friction 图表会显示 "No data"。

需要这些图表时：

1. 运行 `collect.py --agent all --emit-facets`，生成 `facets-todo.json`。
2. 按 `references/prompts.md` 的 facet prompt，为每个会话生成 facet。
3. 写入 `/Users/hughlin/.claude/usage-data/facets/<session-id>.json`。
4. 重新运行 `collect.py`。

单次最多处理 50 个会话。不同 agent 的会话 id 不会冲突。

## 指标差异

- Claude Code：工具名、文件路径、语言、增删行数最完整。
- Codex：走 app-server 时能拿到 `commandExecution`、`mcpToolCall`、`fileChange`、`webSearch`、`imageView`，指标较完整。回退到 rollout 文件时，`exec` 是 JS 编排工具，内部具体命令和文件路径不会全部暴露，工具计数偏向 `exec`。
- Codex 恢复会话会产生多个共用 session id 的 rollout；采集时只保留消息最多的一份，避免同一会话重复计数。
- pi：`bash`、`edit`、`write`、`read` 能提取命令和路径，指标较完整。
- 工具错误：Claude 用 `is_error`，pi 用 `isError`，Codex 用 `exitCode` 或输出模式判断。

## 隐私

`collect.py` 只读本地文件，不联网。`digest.md` 会进入当前对话上下文，并随模型请求发送到你配置的模型服务。不要把报告目录提交到公开仓库。
