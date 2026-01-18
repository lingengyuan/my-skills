# 微信公众号 AI 主题指南

仅保留 AI 模式主题。

## 主题一览

| 主题 | 参数 | 风格 | 适用场景 |
|---|---|---|---|
| **autumn-warm** | `--theme autumn-warm` | 温暖橙色调、文艺感 | 情感故事、生活随笔 |
| **spring-fresh** | `--theme spring-fresh` | 清新绿色调、自然感 | 旅行日记、自然主题 |
| **ocean-calm** | `--theme ocean-calm` | 深蓝色调、专业感 | 技术文章、商业分析 |

## 自定义主题（AI 模式）

用户可以通过自然语言描述自定义样式，Claude 将直接生成符合要求的 HTML。

## AI 生成要求（所有主题）

- 只输出微信公众号可用的 HTML。
- 所有 CSS 必须内联（`style` 属性）。
- 使用安全标签（见 `references/html-guide.md`）。
- 图片使用占位符：`<!-- IMG:0 -->`。
- `<body>` 后立刻创建主容器 `<div>`。
- 每个 `<p>` 明确指定 `color`。

## 自定义提示词示例

```text
请将以下 Markdown 转换为微信公众号 HTML：
- 主色：#4a7c9b
- 背景：#f0f4f8
- 所有 CSS 必须内联
- 使用图片占位符 <!-- IMG:index -->
```
