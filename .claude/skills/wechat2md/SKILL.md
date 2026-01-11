# wechat2md

将微信公众号文章（mp.weixin.qq.com）转换为本地 Markdown，并强制下载所有正文图片。

## 用法（自然语言）
用户输入示例：
- 把这篇文章转成 Markdown：https://mp.weixin.qq.com/s/xxxxxxxx

## 行为规范（强约束）
- 只要识别到 mp.weixin.qq.com/s/ 的文章链接，就执行转换。
- 图片处理为必选：必须下载正文中所有图片，并在 Markdown 中改写为本地相对路径。

## 输出契约（以运行时当前目录为根目录）
- Markdown：`./outputs/<文章名称>/<文章名称>.md`
- 图片：`./images/<文章名称>/001.<ext>`（从 001 开始，按正文出现顺序递增，三位补零）
- 若 `outputs/`、`outputs/<文章名称>/`、`images/`、`images/<文章名称>/` 不存在：必须新建。
- 若存在同名 Markdown 或同名图片文件：必须覆盖。

## 执行方式
当用户提供 URL 后，运行：

```bash
python3 .claude/skills/wechat2md/tools/wechat2md.py "<URL>"
```

脚本会根据文章标题自动生成输出目录与文件。

## 失败策略
- 若抓取失败或未能提取正文（#js_content），应返回错误原因。
- 若个别图片下载失败：
  - Markdown 中对该图片保留原始 URL（不阻断整体生成）
  - 在 Markdown 顶部生成一个 “图片下载失败列表” 区块（包含序号与 URL）
- 若 `outputs/`、`outputs/<文章名称>/`、`images/`、`images/<文章名称>/` 不存在，则创建。
- 若存在同名文件（Markdown 或图片），直接覆盖。
- Markdown 中图片引用使用相对路径：`![](../../images/<文章名称>/001.<ext>)`

## 执行
- 从用户输入中提取 URL（允许句子中混杂其它文字）。
- 运行：
  - `python3 .claude/skills/wechat2md/tools/wechat2md.py "<URL>"`
- 运行完成后：
  - 输出生成的 Markdown 路径
  - 输出图片目录路径

## 失败处理
- 如果抓取失败或无法提取正文 `#js_content`，明确报错并退出（非静默失败）。
- 如果个别图片下载失败：
  - Markdown 中该图片保留原始 URL（不阻断整篇文章生成）
  - 在 Markdown 顶部附加“下载失败图片列表”
  - 在 Markdown 顶部追加“图片下载失败列表”。
