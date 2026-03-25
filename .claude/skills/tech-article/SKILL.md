---
name: tech-article
description: Writes polished Chinese technical articles for WeChat or blog publication, then optionally generates matching illustrations. Use when user wants to write, draft, optimize, or illustrate a technical article. Handles the full pipeline: type selection → research → draft → fact-check → illustration.
---

# Tech Article Writing Skill

Full pipeline: **Type Selection** → **Research** → **Draft** → **Self-Check** → **Fact-Check** → **Illustration** (optional)

---

## Stage 0: Article Type Selection

**首先判断文章类型**（如果用户没有明说，根据内容推断并告知）：

| 类型 | 触发条件 | 核心目标 | 典型转发率 |
|------|----------|----------|------------|
| **工具型 (Tool)** | 用户做了工具/方法/skill 解决了某个问题 | 读者能立即动手复现 | 15–25% |
| **洞察型 (Insight)** | 用户深入研究某技术，发现了规律/反直觉结论 | 读者带走一个认知框架 | 5–12% |

两种类型用不同的结构模板（见 Stage 2）。共用同一套研究流程和行文风格。

---

## Stage 0.5: Pain Point Discovery (Optional)

如果用户还不确定写什么，提供以下引导（最多问 2 个问题）：

**痛点挖掘问卷（按可靠性排序）：**

1. **自己的重复劳动**：最近有没有手动做了 3 次以上的事？（最可靠来源）
2. **新工具的使用门槛**：有没有新发布的工具，中文踩坑教程还缺失？
3. **读者/社区的重复问题**：有没有人反复在问同一个问题？
4. **顿悟时刻**：最近有没有"我才明白 ___ ，之前我以为 ___"的时刻？
5. **"要是有个工具能做 ___ 就好了"**：最近有没有这样的念头？

发现痛点后 → 用最小成本验证（脚本/skill 能解决吗？）→ 做出来 → 回到 Stage 1。

---

## Stage 1: Research & Context

Ask at most 2 questions upfront. Assume reasonable defaults for everything else.

| Question | Default if not specified |
|----------|--------------------------|
| Topic / Subject + source URL or repo? | — (required) |
| Article type (Tool / Insight) | Inferred from content |
| Target platform | WeChat 公众号 |
| Target audience | 有一定技术基础的读者 |
| Key message / angle | Inferred from content |
| Length | Medium (~1500字) |

If user provides a GitHub repo or URL → **use WebFetch to read it before drafting**. Do not rely on training knowledge for technical specifics.

**研究阶段额外注意：**
- 找出**反直觉核心观点**——这往往是标题和开头的最佳素材
- 收集**具体数字**（token 数、工具数、性能指标等）——数字是最强的标题锚点
- 记录**踩坑细节**——真实的失败案例比成功案例更有可信度
- 记录**原始引语**（代码、原文语录）——后续直接引用，不要全部转述

---

## Stage 2: Draft

Write in **Chinese**. Use the template matching the article type.

### 通用风格规则

- 口语化、直接——像跟朋友喝酒时聊技术，不是在台上做分享
- 第一人称，说自己的真实感受，允许有粗糙的边角
- 少用列表，能用散文的地方用散文
- 加粗克制：每节最多一处
- 代码块：始终带语言标签

### 去 AI 味（强制，每篇文章必须遵守）

AI 生成的中文技术文章有明显的腔调，读者一眼能认出来。以下是具体的禁用规则：

**禁用词表——出现即改：**
- 填充收尾词：总的来说、综上所述、不得不说、毋庸置疑、值得一提的是
- 互联网黑话：赋能、抓手、打通、闭环、沉淀、链路、底层逻辑
- 伪学术腔：认知框架、可迁移的原则、维度（抽象用法）、可复用（当形容词修饰"教训/框架/认知"时）、深度（当形容词，如"深度解析"）
- 过度归纳：反直觉（偶尔可用，但一篇文章最多出现 1 次；不能当万能标签）、核心发现、关键洞察
- AI 过渡句："这让我想到一个更普遍的规律"、"这说明了一个重要的事实"、"让我们来看看"、"接下来我们将探讨"

**禁用结构模式：**
- "发现一/发现二/发现三"式机械编号——用自然的小标题代替，每个标题说具体的事而不是编号
- 开篇的论文式摘要——不要写"这篇文章讲三件事：第一……第二……第三……"
- 每节末尾的"总结升华"——节的最后一句话应该是具体的事实或观点，不是对本节的复述
- 前后呼应的排比句——"不是因为 A，而是因为 B；不是因为 C，而是因为 D"用一次可以，用两次就有味道了

**应该怎么写：**
- 标题用具体的事，别用抽象概括："账对不上才是最大的敌人" > "统计一致性挑战"
- 过渡靠内容自然衔接，别靠连接词硬转——上一节讲完了一个事实，下一节从新的事实开始就行
- 允许不整齐——不是每一节都要有相同的结构，不是每个观点都要配一个例子
- 结尾可以短，一两句话把问题抛出去就行，别搞仪式感

---

### 模板 A：工具型文章（Tool Article）
> 用于：我做了某个工具/方法/skill 解决了一个具体问题

**结构（严格按此顺序）：**

```
# 标题
  · 格式：[具体动作] + [解决的问题]
  · 示例："一句话复刻公众号排版" / "三步本地部署翻译模型"
  · 避免："介绍一个 XX 工具" / "探索 XX 的可能性"

## 先给结论（必须，≤100字）
  · 解决什么（用户原来怎么做，有什么痛点）
  · 怎么做（你的方案是什么）
  · 效果是什么（可量化最好）

## 为什么需要它（痛点共鸣）
  · 描述用户原来的工作方式——麻烦在哪里
  · 不要只说"效率低"，要说具体的麻烦（"每次都要手动对齐段距"）

## 它是怎么工作的（最小可理解版本）
  · 拆成 2-4 个步骤，每步说明做什么 + 为什么这样设计
  · 关键技术决策 + 背后理由（不只是"怎么做"，还要"为什么这么做"）
  · 核心代码/命令可以展示，但只展示关键部分

## 真正解决了哪些"会反复发生的问题"
  · 列出 2-4 个具体踩坑细节（增加可信度）
  · 每个问题：是什么问题 → 怎么解决的
  · 真实失败经历比成功经历更有说服力

## 边界说明（必须）
  · 它做了什么（范围内）
  · 它不做什么（范围外，明确说）
  · 适合谁 / 不适合谁

## 行动项（必须，至少一个）
  · 下载链接 / GitHub 地址 / 可直接复制的命令 / Prompt 模板
  · 没有行动项 = 丢失 50% 转发动力
```

**工具型文章成功指标**：读者读完后有"我要发给 ___ 用" 的冲动。

---

### 模板 B：洞察型文章（Insight Article）
> 用于：做了一件事、研究了一个东西，过程中发现了一些意料之外的事

**结构指引（不是死板模板，按需调整）：**

```
# 标题
  · 用具体的事说话，不要抽象概括
  · ✅ "用 AI 写了 916 个 Zig 算法后，我发现最难的不是写代码"
  · ✅ "把 X 推荐算法做成了可视化模拟器"
  · ❌ "深度解析 XX" / "全面了解 XX" / "关于 XX 的几点思考"

## 开场（≤150字）
  · 先说让人意外的结论或事实，再交代背景
  · 不要写"这篇文章讲三件事"——读者会自己发现你讲了什么

## 主体（分 H2 节，每节讲一个具体的事）
  · 每节标题必须是具体的事，不是"发现一""发现二"
    ✅ "账对不上才是最大的敌人" / "最后 25% 花了跟前 60% 差不多的时间"
    ❌ "发现一：统计一致性问题" / "核心发现 A"
  · 每节的展开方式不需要一样——有的节靠数据说话，有的节靠故事，有的节靠代码
  · 不要在每节末尾写总结句。节讲完了就完了，读者不需要你帮他归纳
  · 重要数据或原话用 blockquote（>），比加粗更有分量

## 收获/教训（靠后但不是必须单独成节）
  · 可以融入主体的最后一两节，不用非得单独拎出来叫"可复用的 XX"
  · 用大白话说：你之后会怎么做、你觉得别人可以借鉴什么
  · 不要用"原则一/原则二"的格式——改成"两件值得记住的事"或直接融进散文里

## 结尾（必须简短）
  · 一个问题、一句话，不要超过两行
  · ✅ "下次你打算用 AI 批量生成代码的时候，时间表里给管理留了多少？"
  · ❌ "本文介绍了 XX，希望对大家有所启发。"
```

**洞察型文章成功指标**：读者读完有"我之前没这么想过"的感觉。

---

### WeChat Length Guide

| Type | Target |
|------|--------|
| Short post | 800–1200字 |
| Standard | 1200–2000字 |
| Deep dive | 2000–3500字 |

---

## Stage 3: Self-Check（写完必做）

### 工具型文章检查清单
- [ ] 开篇 100 字内给出了明确结论（解决什么、怎么做、效果是什么）
- [ ] 有边界说明（适合/不适合，以及它不做什么）
- [ ] 有至少一个可复制的行动项（链接/命令/模板）
- [ ] 踩坑细节真实具体（不是泛泛说"会有问题"，而是说具体是什么问题）
- [ ] 没有以"总的来说"/"综上所述"收尾

### 洞察型文章检查清单
- [ ] 有至少一个让读者感到意外的事实或结论
- [ ] 读者能带走点什么——一个做法、一个判断标准、一个以后可以套用的思路
- [ ] 结尾是一个短问题，不是对全文的复述
- [ ] 技术细节有原始数据或代码支撑（不是泛泛描述）
- [ ] 没有以"希望本文对大家有所帮助"结尾
- [ ] **去 AI 味检查**：全文搜索禁用词表中的词，逐个替换或删除；检查是否有"发现一/二/三"式编号结构

---

## Stage 4: Fact-Check & Output

### Fact-Check（当提供了来源 URL/仓库时必做）

草稿完成后，对照来源重新核验：
- 配置文件名、环境变量名、CLI 语法
- 功能行为描述
- 安装步骤和前置条件

### Output

Save to `./drafts/<slug>.md`

```markdown
# [Article Title]

> **平台**: WeChat / Blog | **字数**: ~XXX字 | **类型**: 工具型/洞察型 | **状态**: Draft

---

[Article content]

---

## ⚠️ 核查记录
| 内容 | 来源 | 状态 |
|------|------|------|
| config filename: foo.yml | source repo | ✅ |
```

---

## Stage 5: Article Illustration (optional)

After the draft is complete, offer to generate illustrations.

> "要不要为这篇文章配图？我可以分析文章结构，推荐插图位置，并生成风格一致的配图。"

Full illustration workflow: [references/illustration-guide.md](references/illustration-guide.md)
Style options & compatibility: [references/styles.md](references/styles.md)

### Quick Summary

**Step 1 — Analyze**: Identify 3-5 positions where illustrations add value (core arguments, abstract concepts, processes, data comparisons). Never illustrate metaphors literally — visualize the underlying concept.

**Step 2 — Confirm settings** (one AskUserQuestion, max 3 questions):
- Illustration type: `infographic` / `flowchart` / `comparison` / `framework` / `timeline` / `scene` / mixed
- Density: minimal (1-2) / balanced (3-5) / per-section
- Style: `vector` / `minimal-flat` / `sci-fi` / `hand-drawn` / `editorial` / `scene`

**Step 3 — Save outline**: Write `./drafts/<slug>/outline.md` with position, purpose, visual content, and filename for each illustration.

**Step 4 — Save prompt files**: For each illustration, save `./drafts/<slug>/prompts/NN-{type}-{slug}.md` using the templates in [references/illustration-guide.md](references/illustration-guide.md). Do NOT generate images before all prompt files are saved.

**Step 5 — Generate**: 使用以下方案生成图片（按优先级）：

**方案 A：qwen-image-plus（推荐，文字渲染最佳）**

需要 `DASHSCOPE_API_KEY`，读取 `.env` 获取。用 Python 脚本调用：

```python
import os, re, urllib.request, dashscope
from dashscope import MultiModalConversation

dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

def gen_image(prompt_file, out_path):
    with open(prompt_file) as f:
        prompt = re.sub(r'^---\n.*?\n---\n', '', f.read(), flags=re.DOTALL).strip()
    resp = MultiModalConversation.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model="qwen-image-plus-2026-01-09",
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        result_format='message', stream=False,
        watermark=False, prompt_extend=True, size='1920*1080'
    )
    if resp.status_code == 200:
        url = resp.output.choices[0].message.content[0]['image']
        urllib.request.urlretrieve(url, out_path)
        return True
    return False
```

> ⚠️ DashScope 默认模型（z-image-turbo）**不适合**文字渲染，必须指定 `qwen-image-plus-2026-01-09`。

每张生成后输出：`已生成 X/N`。失败时自动重试一次，仍失败则跳过并记录。

**Step 6 — Insert**: Add `![description](path)` after the corresponding paragraph in the article.

### Output Directory

```
drafts/<slug>/
├── <slug>.md          # Article
├── outline.md         # Illustration plan
├── prompts/           # Prompt files
│   └── 01-infographic-concept.md
└── 01-infographic-concept.png
```
