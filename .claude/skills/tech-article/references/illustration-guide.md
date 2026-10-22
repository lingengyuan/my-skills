# Technical Illustration Guide

## 1. 总体设计原则

配图应作为技术正文的有力佐证与认知脚手架，而不是文章的点缀装饰。

- **高信息密度**：一张图必须包含真实的数据、组件名、协议名或逻辑因果，杜绝纯概念占位符。
- **优先确定性代码绘图**：优先使用 Mermaid 源码并编译为 SVG（如使用 CLI 工具 `pele` 或 `mmdc`），保证图表可维护、可版本控制、无渲染幻觉。
- **无 AI 假海报感**：杜绝生成与具体代码无关的空泛 AI 意境图。

---

## 2. 图像类型选择指南

| 图表类型 (Type) | 最佳实践 | 推荐实现方式 |
|---|---|---|
| **架构与组件拓扑 (Architecture)** | 表达系统分层（接入/网关/服务/存储）、模块间依赖与数据流向 | Mermaid `flowchart TB` 或 `graph TD` |
| **时序与调用流 (Sequence)** | 表达微服务交互、OAuth 授权流程、组件生命周期调用 | Mermaid `sequenceDiagram` |
| **状态机与生命周期 (State)** | 表达连接状态变迁、订单流转、任务调度阶段 | Mermaid `stateDiagram-v2` |
| **技术选型对比 (Comparison)** | 方案 A vs 方案 B 的多维度优缺点、适用场景与成本权衡 | Markdown 表格或结构化矢量图 |
| **性能基准图 (Benchmark)** | 吞吐量 (QPS)、响应延迟 (P99)、冷启动耗时、显存占用 | 真实实测数据柱状图/折线图 |

---

## 3. 编译 Mermaid 插图为 SVG（首选）

在技术文章撰写过程中，直接在 `drafts/<slug>/diagrams/` 目录下保存 `.mmd` 源文件，并调用编译工具（如 `pele` 或 `mmdc`）生成对应的 SVG：

```bash
# 生成亮色架构图
pele drafts/<slug>/diagrams/01-architecture.mmd drafts/<slug>/diagrams/01-architecture.svg

# 生成暗色主题（如需要）
pele drafts/<slug>/diagrams/01-architecture.mmd drafts/<slug>/diagrams/01-architecture-dark.svg --theme dark
```

在正文中引用编译产物（推荐正文保存为 `drafts/<slug>/article.md`，此时引用路径为 `diagrams/...`；若正文保存为单文件 `drafts/<slug>.md`，引用路径为 `<slug>/diagrams/...`）：
```markdown
![系统调用架构图](diagrams/01-architecture.svg)
```

---

## 4. 概念矢量生图规范（当必须使用生图模型时）

若图表包含复杂的拟物原型或非代码能表达的管道模型，输出生图 Prompt 时须遵守以下约束：

### Prompt 编写硬性规则：
1. **真实标签**：必须包含文章中出现的具体技术名词与参数（如 `gRPC`, `Redis Cluster`, `12ms`, `Kafka Partition`），严禁使用“模块A”、“参数X”等抽象占位符。
2. **纯色留白与功能色**：背景使用纯白或深色极简底色，颜色仅用于区分语义（例如：深蓝表示核心链路，薄荷绿表示通过，珊瑚红表示熔断/拦截）。
3. **颜色禁止写十六进制代码**：生图模型会把 `#FF0000` 渲染为图片上的文字，颜色一律用具体中文名称（深蓝、墨灰、翠绿）。

### 示例：数据管道流向图 Prompt
```text
【标题】：实时流计算管道架构 - 技术信息图
【布局】：水平三段式流向（左：多源日志采集 -> 中：Flink 状态计算与窗口聚合 -> 右：ClickHouse 写入与 Grafana 监控）
【核心节点与标签】：
- 左侧：Syslog / Nginx Access Log (JSON)
- 中部：Apache Flink 1.18 算子（Event-time 窗口，5s 聚合）
- 右侧：ClickHouse 宽表、Grafana Dashboard
【视觉风格】：扁平工程矢量图，深色背景，线框分明，细箭头表示数据流向，高对比度功能色标出关键瓶颈点
【比例】：16:9
```
