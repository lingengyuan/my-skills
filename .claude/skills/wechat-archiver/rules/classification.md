# Classification Rules (Auto Canvas/Base Decision)

## Purpose
定义基于关键词规则的自动分类逻辑，决定是否生成 `canvas` 和 `base`。

**设计原则**：
- ✅ 简单可靠：基于关键词匹配，不使用 LLM
- ✅ 可配置：支持用户手动覆盖 (`on`/`off`)
- ✅ 可扩展：规则易于维护和更新

---

## Canvas Generation Rules

### Trigger Mode: `auto`

当 `canvas=auto` 时，如果文章内容包含以下任一关键词，则生成 `diagram.canvas`：

#### 流程/时序类
- 中文：`流程`、`步骤`、`时序`、`执行顺序`、`调用链`、`协作`、`交互`
- 英文：`sequence`、`flow`、`workflow`、`process`、`steps`、`pipeline`

#### 架构/结构类
- 中文：`架构`、`结构`、`组件`、`模块`、`依赖`、`关系`
- 英文：`architecture`、`structure`、`components`、`modules`、`dependencies`

#### 原理/机制类
- 中文：`原理`、`机制`、`实现原理`、`底层原理`
- 英文：`mechanism`、`implementation`、`internals`、`how it works`

#### 视图类型提示
- 中文：`架构图`、`流程图`、`时序图`、`示意图`
- 英文：`diagram`、`chart`、`graph`

### Canvas Type Selection

如果决定生成 canvas，根据关键词选择 `diagram_type`：

| 关键词匹配 | diagram_type | Canvas Template |
|-----------|--------------|-----------------|
| `时序`、`sequence`、`调用链`、`交互` | `sequence` | `canvas.sequence.compact.md` |
| `流程`、`flow`、`steps`、`步骤` | `flowchart` | `canvas.flowchart.md` |
| `架构`、`architecture`、`组件`、`模块` | `architecture` | `canvas.architecture.md` |
| 其他 | `artifact` | `canvas.artifact.md` |

---

## Base Generation Rules

### Trigger Mode: `auto`

当 `base=auto` 时，如果文章内容包含以下任一关键词，则生成 `table.base`：

#### 对比/比较类
- 中文：`对比`、`比较`、`优缺点`、`区别`、`差异`、`VS`、`选择`
- 英文：`comparison`、`compare`、`vs`、`difference`、`pros and cons`

#### 清单/列表类（仅适用于明确的清单类文章）
- 中文：`清单`、`术语表`、`词汇表`、`名词解释`、`常用工具`、`最佳实践`
- 英文：`checklist`、`glossary`、`vocabulary`、`inventory`、`best practices`

**注意**：普通的"列表"、"工具列表"等描述性词汇不应该触发 base

#### 术语/概念类
- 中文：`术语`、`概念`、`名词解释`、`词汇表`
- 英文：`glossary`、`terms`、`concepts`、`vocabulary`

#### 表格密集型
- 检测到 ≥3 个 Markdown 表格 (`| ... |`)

#### 多项并列型
- 检测到结构化的多级列表（≥2 个二级标题，每个下有 ≥3 个列表项）

### Base Mode Selection

如果决定生成 base，根据关键词选择 `base_mode`：

| 关键词匹配 | base_mode | 说明 |
|-----------|-----------|------|
| `对比`、`比较`、`VS`、`comparison` | `comparison` | 需提供 comparison_items |
| 其他 | `generic` | 通用 Base 表格 |

---

## Implementation Pseudo-code

```python
def decide_artifact_plan(article_content: str, canvas: str, base: str) -> List[str]:
    """
    决定 artifact_plan
    :param article_content: article.md 内容
    :param canvas: 用户指定的 canvas 策略 (auto/on/off)
    :param base: 用户指定的 base 策略 (auto/on/off)
    :return: ["md", "canvas", "base"] 或 ["md"] 或 ["md", "canvas"] 等
    """
    artifact_plan = ["md"]

    # Canvas decision
    if canvas == "on":
        artifact_plan.append("canvas")
    elif canvas == "auto":
        canvas_keywords = [
            "流程", "步骤", "时序", "执行顺序", "调用链", "协作", "交互",
            "sequence", "flow", "workflow", "process", "steps", "pipeline",
            "架构", "结构", "组件", "模块", "依赖", "关系",
            "architecture", "structure", "components", "modules", "dependencies",
            "原理", "机制", "实现原理", "底层原理",
            "mechanism", "implementation", "internals",
            "架构图", "流程图", "时序图", "示意图",
            "diagram", "chart", "graph"
        ]
        if any(kw in article_content for kw in canvas_keywords):
            artifact_plan.append("canvas")

    # Base decision
    if base == "on":
        artifact_plan.append("base")
    elif base == "auto":
        base_keywords = [
            "对比", "比较", "优缺点", "区别", "差异", "VS", "选择",
            "comparison", "compare", "vs", "difference", "pros and cons",
            "清单", "术语表", "词汇表", "名词解释", "常用工具", "最佳实践",
            "checklist", "glossary", "vocabulary", "inventory", "best practices"
        ]

        # Check keywords
        keyword_match = any(kw in article_content for kw in base_keywords)

        # Check table density (≥3 tables)
        table_count = article_content.count("| --- ") >= 3

        # Check structured lists (heuristic)
        # Count "## " headers followed by "- " lists
        import re
        structured_lists = len(re.findall(r'## .+\n(?:- .+\n){3,}', article_content))
        list_match = structured_lists >= 2

        if keyword_match or table_count or list_match:
            artifact_plan.append("base")

    return artifact_plan


def decide_diagram_type(article_content: str) -> str:
    """
    决定 canvas 的 diagram_type
    """
    if any(kw in article_content for kw in ["时序", "sequence", "调用链", "交互"]):
        return "sequence"
    elif any(kw in article_content for kw in ["流程", "flow", "steps", "步骤"]):
        return "flowchart"
    elif any(kw in article_content for kw in ["架构", "architecture", "组件", "模块"]):
        return "architecture"
    else:
        return "artifact"


def decide_base_mode(article_content: str) -> str:
    """
    决定 base 的 base_mode
    """
    if any(kw in article_content for kw in ["对比", "比较", "VS", "comparison"]):
        return "comparison"
    else:
        return "generic"
```

---

## Testing the Rules

### Test Cases

| Article Content | Expected canvas | Expected base |
|----------------|-----------------|---------------|
| "本文介绍 React 的渲染流程和步骤" | ✅ (流程/步骤) | ❌ |
| "对比三种前端框架的优缺点" | ❌ | ✅ (对比) |
| "微服务架构的组件划分和依赖关系" | ✅ (架构/组件) | ❌ |
| "本文整理了 10 个常用的 Python 术语" | ❌ | ✅ (术语) |
| "异步编程的底层实现原理" | ✅ (原理/机制) | ❌ |
| "2024 年度技术总结和关键点" | ❌ | ✅ (总结/要点) |

---

## Extension Points

### Future Enhancements

1. **更精细的结构检测**
   - 检测代码块比例（技术文章可能需要架构图）
   - 检测图片数量（图文并茂可能不需要 canvas）

2. **学习用户偏好**
   - 记录用户手动修改的历史
   - 训练简单的分类器

3. **支持自定义规则**
   - 用户可以在 `meta.json` 中覆盖默认规则
   - 支持项目级别的规则配置文件

---

## Validation Checklist

实现时必须验证：
- [ ] `canvas=off` 和 `base=off` 时强制不生成
- [ ] `canvas=on` 和 `base=on` 时强制生成
- [ ] `auto` 模式下关键词匹配准确率 ≥80%
- [ ] 规则可以在 100ms 内完成判断（不调用 LLM）
- [ ] 规则易于扩展和维护
