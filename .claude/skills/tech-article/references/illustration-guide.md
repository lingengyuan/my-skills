# Illustration Guide

## Two-Dimension System

Every illustration is defined by **Type × Style**:

| Dimension | Controls |
|-----------|----------|
| **Type** | Information structure — what kind of visual |
| **Style** | Visual aesthetics — how it looks |

Example: `--type infographic --style vector` = flat vector data visualization

---

## Types

| Type | Best For |
|------|----------|
| `infographic` | Data, metrics, key concepts, comparisons with numbers |
| `flowchart` | Processes, workflows, step-by-step instructions |
| `comparison` | Side-by-side options, pros/cons, before/after |
| `framework` | Architecture, models, conceptual structures |
| `timeline` | History, evolution, progression |
| `scene` | Narratives, emotional hooks, personal stories |

### Auto-Select by Content Signals

| Article Content | Recommended Type | Recommended Style |
|-----------------|------------------|-------------------|
| AI, tech, code, programming | infographic | vector, sci-fi |
| Tutorial, guide, how-to | flowchart | vector, minimal-flat |
| Comparisons, tool reviews | comparison | vector, minimal-flat |
| Architecture, framework, model | framework | sci-fi, vector |
| Personal story, experience | scene | hand-drawn, scene |
| History, evolution of tech | timeline | editorial, hand-drawn |
| Metrics, data, numbers | infographic | editorial, vector |

---

## Outline Format

Save as `./drafts/<slug>/outline.md`:

```yaml
---
type: infographic
density: balanced
style: vector
image_count: 3
---

## Illustration 1

**Position**: After section "XX" / After paragraph starting with "..."
**Purpose**: Visualize the three-layer architecture described in the text
**Visual Content**: Framework diagram showing Layer A → Layer B → Layer C with data flow arrows
**Filename**: 01-framework-architecture.png

## Illustration 2
...
```

---

## Prompt File Format

Save each prompt as `./drafts/<slug>/prompts/NN-{type}-{slug}.md`:

```yaml
---
illustration_id: 01
type: infographic
style: vector
---

[Prompt content using type-specific template below]
```

---

## Prompt Templates

### Default Requirements (add to ALL prompts)

```
风格简洁，留白充足，背景简单或纯色。
主要元素居中或按内容需要布局。
文字：大而清晰，关键词为主，不堆砌。
```

> ⚠️ **Prompt 语言规则**：一律用**中文**描述内容和布局。颜色用**名称**（如：珊瑚红、薄荷绿、芥末黄、深蓝），**绝对不要**写十六进制色值（如 `#E07A5F`）——色值会被模型当作文字渲染进图片。

### Infographic

```
[标题] - 数据可视化

布局：[网格 / 放射 / 层级]

区域：
- 区域1：[具体数据点，使用文章中的真实数值]
- 区域2：[对比或指标]
- 区域3：[总结/结论]

标签：[使用文章中的真实数字、术语——不用占位符]
颜色：[语义化描述，如"珊瑚红表示强调，薄荷绿表示正向，芥末黄表示警示"]
风格：扁平矢量，粗几何形状，清晰视觉层级
比例：16:9
```

### Flowchart

```
[标题] - 流程图

布局：[左右 / 上下 / 环形]

步骤：
1. [步骤名称] — [简要说明]
2. [步骤名称] — [简要说明]
3. ...

连接：[箭头样式，是否有判断分支]
颜色：[各步骤或阶段的颜色描述]
风格：粗箭头，清晰步骤容器，高对比度
比例：16:9
```

### Comparison

```
[标题] - 对比图

左侧 — [选项A / 之前 / 旧版]：
- [要点1]
- [要点2]

右侧 — [选项B / 之后 / 新版]：
- [要点1]
- [要点2]

分隔线：[视觉分隔样式]
颜色：左侧[颜色名称]，右侧[颜色名称]，奶白背景
风格：分栏布局，粗体图标，颜色区分
比例：16:9
```

### Framework

```
[标题] - 概念框架图

结构：[层级 / 网络 / 矩阵]

节点：
- [概念1] — [角色/说明]
- [概念2] — [角色/说明]

关系：[节点如何连接，流向]
颜色：节点用[颜色名称]，连接线用[颜色名称]
风格：几何节点，粗连接线，清晰层级
比例：16:9
```

### Timeline

```
[标题] - 时间线

方向：[横向 / 纵向]

事件：
- [日期/时期1]：[里程碑描述]
- [日期/时期2]：[里程碑描述]

标记：[视觉指示器样式]
颜色：[渐进色彩方案，用名称描述]
风格：[精致 / 温暖 / 编辑风格]
比例：16:9
```

### Scene

```
[标题] - 场景图

主体：[核心视觉主体]
氛围：[光线、情绪、环境]
情感：[传达的情感]
色调：[暖色 / 冷色 / 中性]

人物（如有）：简化风格剪影，非写实。
风格：[温暖 / 水彩 / 手绘]
比例：16:9
```

---

## What to Avoid

- Vague descriptions ("a nice image about AI")
- Literal illustration of metaphors (e.g., article says "电锯切西瓜" → don't draw a chainsaw cutting watermelon; visualize the underlying concept of speed/efficiency)
- Missing concrete labels — always use actual terms and numbers from the article
- Generic decorative illustrations that don't add information value
