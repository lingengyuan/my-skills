---
name: tech-article
description: Research, draft, revise, verify, and illustrate authentic Chinese technical articles for WeChat Official Accounts or developer blogs. Use when writing technical articles, turning repositories or experiments into articles, removing AI prose patterns, or planning article illustrations.
---

# Technical Article Skill

Research, draft, revise, and illustrate authentic Chinese technical articles grounded in verified source code, architecture, and engineering practice.

## Core Workflows & Scopes

Select an article structure matching user intent and provided source material:
- **工具与方案（Tool & Solution）**：解决具体开发痛点，提供即刻可用的命令、代码或配置方案。
- **深度剖析（System Deep Dive）**：深入分析开源架构、推荐算法、模型机制或协议原理。
- **实战教程（Tutorial & Guide）**：可复现的部署、搭建与配置指南，注重步骤前置条件与最小可用闭环。
- **复盘与思考（Postmortem & Opinion）**：技术选型思考、事故排障复盘或架构演进总结。

---

## Workflow

### 1. 确定立意与边界
- 明确目标读者、核心论点与预期收获。
- 拒绝宽泛空洞的主题，开门见山说明文章解决什么具体问题。

### 2. 查验代码事实与第一手素材
- 优先阅读源码、配置文件、错误日志与压测基准。
- 收集真实命令、参数名、版本号与性能数据。
- **事实第一原则**：素材中没有的信息绝不强行编造。若无实测数据或未踩坑，不虚构故障情节或虚假数据。

### 3. 正文组织规则

- **结论与开场**：开门见山，前两段直接给出核心结论、技术张力或解决的具体问题。若有反直觉实测数据可优先抛出；若无则平实陈述核心价值，不强行制造惊悚反常识。
- **机制与流程**：用自然叙事段落解析系统工作机制和技术决策背后的因果关系，避免整篇文章机械堆叠纯项目列表。
- **踩坑与真实细节（条件触发）**：
  - 若实践中有真实报错、参数冲突、版本陷阱或设计转折，**必须详细如实记录**（这是提升真实度与可信度的关键）。
  - 若为纯特性介绍或无踩坑素材，**坚决不编造虚假故障**，重点说明设计边界与注意事项。
- **适用边界**：明确适合场景、不适合场景以及系统的能力边界，不写全知全能的完美假方案。
- **可带走的价值**：根据类型提供可复现的行动项（代码/命令/配置），或读者可复用的技术思考维度。
- **收尾**：以关键技术权衡或一个具体的延伸技术问题收尾，**坚决杜绝“希望本文对大家有所帮助”等客套废话**。

### 4. 彻底消除 AI 写作痕迹
- **禁止词汇**：禁用 `总的来说`、`综上所述`、`由此可见`、`值得注意的是`、`需要明确的是`、`赋能`、`抓手`、`闭环`、`底层逻辑`、`核心痛点`、`组合拳`。
- **禁止结构**：禁用机械排比（如纯“第一...第二...第三...”无因果堆砌）。
- **真实语态**：保持工程师实事求是的叙事语气，保留真实的犹豫与权衡，不写大模型泛泛而谈的公文体。

### 5. 校验技术细节
- 逐一核实 CLI 命令、API 参数与配置项。
- 保证代码块语言标记明确，依赖清晰。
- 未经验证的推测必须显式注明“待验证”，不掩盖不确定性。

### 6. 规划插图（可选）
- 仅在用户明确需要或能显著降低认知成本时规划插图。
- **首选确定性图表**：优先使用标准 Mermaid 源码（架构拓扑、时序调用、状态流转）并编译为清晰矢量 SVG（如使用 CLI 工具 `pele` 或 `mmdc`）。
- **工程视觉优先**：对比矩阵、数据管道流向或终端调用轨迹；拒绝与正文无关的空泛 AI 装饰图，拒绝将技术比喻做字面直画。
- 参考 [references/styles.md](references/styles.md) 与 [references/illustration-guide.md](references/illustration-guide.md)。

### 7. 导出稿件
- 保存文章至 `drafts/<slug>/article.md`（含配图资源时，配图位于 `drafts/<slug>/diagrams/`）或 `drafts/<slug>.md`（单文件纯文本时），并进行最终核查。

---

## AI 写作反模式对照表

| AI 坏味道 | 典型表现 | 真实技术写作改写方式 |
|---|---|---|
| 虚泛总结 | “总的来说”、“综上所述，本文分析了...” | 删除废话，结尾以深刻的技术问题或行动指引收尾 |
| 商业黑话 | “赋能业务稳健增长”、“形成生态闭环” | 换成真实技术指标（如“将冷启动时间从 1.2s 降至 300ms”） |
| 空洞抽象 | “其底层逻辑在于心智模型的重构” | 描述具体的架构约束与状态机变化 |
| 道德说教 | “值得注意的是，我们必须充分认识到...” | 直接以祈使句说明操作规则（“生产环境需显式配置连接池上限”） |
| 伪完美叙事 | 一路畅通无阻，从头到尾没有遇到任何问题 | 补充真实排查细节；若无踩坑则如实陈述最佳实践与边界 |

---

## 交付前检查清单

1. 核心结论是否开门见山在前两段交代清楚？
2. 是否消除了所有禁止词汇与客套收尾套话？
3. 所有命令、代码、配置与数据是否与第一手素材严格一致，无凭空捏造？
4. 是否包含了清晰的适用场景与边界局限？
5. 如包含真实踩坑经验，是否如实记录了排查原因与解决方法？
