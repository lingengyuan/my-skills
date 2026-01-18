# 批量处理指南

## 概述

`batch_archiver.py` 支持从 inbox.md 文件中批量提取微信文章链接并归档。

## 支持的链接格式

### 1. Markdown 链接

```markdown
[文章标题](https://mp.weixin.qq.com/s/xxxxx)
```

### 2. 纯 URL

```markdown
https://mp.weixin.qq.com/s/xxxxx
```

### 3. 任务列表（推荐）

```markdown
- [ ] https://mp.weixin.qq.com/s/xxxxx
- [ ] [文章标题](https://mp.weixin.qq.com/s/yyyyy)
```

处理后自动标记为已完成：

```markdown
- [x] https://mp.weixin.qq.com/s/xxxxx (已归档)
- [x] [文章标题](https://mp.weixin.qq.com/s/yyyyy)
```

## 使用方法

### 基本用法

```bash
# 预览要处理的链接（不实际执行）
python .claude/skills/wechat-archiver/tools/batch_archiver.py --inbox inbox.md --dry-run

# 批量处理
python .claude/skills/wechat-archiver/tools/batch_archiver.py --inbox inbox.md
```

### 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--inbox` | inbox.md 文件路径 | 必填 |
| `--folder` | 目标文件夹 | `20-阅读笔记` |
| `--dry-run` | 预览模式，不实际处理 | - |
| `--force` | 强制重新处理已完成的 URL | - |
| `--no-mark` | 不在源文件中标记已处理项 | - |
| `--include-checked` | 包含已勾选的任务项 | - |
| `--reset-checkpoint` | 重置检查点，从头开始 | - |

### 示例

```bash
# 预览
python batch_archiver.py --inbox ~/notes/inbox.md --dry-run

# 处理到指定文件夹
python batch_archiver.py --inbox inbox.md --folder "30-方法论"

# 强制重新处理所有
python batch_archiver.py --inbox inbox.md --force --reset-checkpoint

# 不标记源文件
python batch_archiver.py --inbox inbox.md --no-mark
```

## 断点续传

脚本会在 inbox.md 同目录下创建检查点文件 `.batch_checkpoint_inbox.json`，记录已处理的 URL。

- 如果处理中断，重新运行会自动跳过已成功处理的 URL
- 使用 `--reset-checkpoint` 可清除检查点重新开始
- 使用 `--force` 可强制重新处理所有 URL

## inbox.md 示例

```markdown
# 待读文章

## 技术

- [ ] [深入理解 async/await](https://mp.weixin.qq.com/s/abc123)
- [ ] https://mp.weixin.qq.com/s/def456

## 产品

- [ ] [产品设计方法论](https://mp.weixin.qq.com/s/ghi789)

## 已读

- [x] [已归档的文章](https://mp.weixin.qq.com/s/old123)
```

## 输出

处理完成后，每篇文章会创建独立的资产目录：

```
outputs/20-阅读笔记/
  ├── 20260118-深入理解-async-await-a1b2c3/
  │   ├── article.md
  │   ├── images/
  │   ├── meta.json
  │   └── run.jsonl
  └── 20260118-产品设计方法论-d4e5f6/
      ├── article.md
      ├── images/
      ├── meta.json
      └── run.jsonl
```

## 注意事项

1. **去重**: 相同 URL（规范化后）只会处理一次
2. **幂等性**: 重复运行不会重复处理已成功的 URL
3. **任务列表**: 默认跳过已勾选 `[x]` 的项目
4. **标记**: 处理成功后会自动将 `[ ]` 改为 `[x]`
