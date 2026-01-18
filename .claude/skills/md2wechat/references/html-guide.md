# 微信公众号 HTML 规则（精简）

## 必须遵守

- 只用内联 CSS（`style` 属性）。
- `<body>` 后立刻创建主容器 `<div>`。
- 每个 `<p>` 明确 `color`。
- 图片必须使用微信 CDN URL（`mmbiz.qpic.cn`）。

## 安全标签（常用）

`section`, `p`, `span`, `strong`, `em`, `u`, `a`, `h1`-`h6`, `ul`, `ol`, `li`,
`blockquote`, `pre`, `code`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `img`, `br`, `hr`

## 禁止

`script`, `iframe`, `form`, `style`, `link`, `video`, `audio`
