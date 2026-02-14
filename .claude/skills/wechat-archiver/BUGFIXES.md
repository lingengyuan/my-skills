# Bug Fixes and Improvements

## Issues Reported

### Issue 1: Slug Format (数字后缀)

**问题**：文件夹名称最后带有 `-asset_id[:6]` 数字串，例如 `20260111-标题-41f7f7`

**原因**：
- 目的是避免同一天同标题文章冲突
- asset_id 的前6位用于唯一标识

**解决方案**：
- 添加 `--simple-slug` 选项
- 默认行为：包含 asset_id 后缀（更安全）
- 使用 `--simple-slug`：不包含后缀（更简洁）

**使用示例**：
```bash
# 默认：包含 asset_id
python3 wechat_archiver.py "https://mp.weixin.qq.com/s/xxx"
# 输出：20260111-文章标题-41f7f7/

# 使用 --simple-slug
python3 wechat_archiver.py "https://mp.weixin.qq.com/s/xxx" --simple-slug
# 输出：20260111-文章标题/
```

---

### Issue 2: table.base Sources 配置错误

**问题**：
- `sources.basePath: "."` 会扫描当前目录的所有 .md 文件
- 包含了不应该显示的 `article.md` 和其他文件
- 不符合 note-creator 的设计原则

**原因**：
- 对于 generic 模式，应该只显示 `note.md`
- 不应该包含 `article.md`（原始文章）

**解决方案**：
修改 `table.base` 的 sources 配置：

```yaml
# 错误的配置（会扫描所有 .md）
sources:
  - type: local
    basePath: "."
    include:
      - "*.md"
    exclude: []

# 正确的配置（只包含 note.md）
sources:
  - type: local
    basePath: "."
    include:
      - "note.md"
    exclude: []
```

**注意**：
- Generic 模式：只包含 `note.md`
- Comparison 模式：sources 指向 `compare/` 子目录，每个对比项一个 .md 文件

---

### Issue 3: note.md 缺少 YAML Frontmatter

**问题**：
- note.md 没有 YAML frontmatter
- tags 在文件末尾而不是 frontmatter 中
- Obsidian 无法正确识别标签

**解决方案**：
note.md 必须包含 YAML frontmatter：

```markdown
---
category: technology
tags:
  - Cursor
  - Agent
  - LLM
  - 动态上下文
created: 2026-01-11
modified: 2026-01-11
source: wechat_article
---

# 文章标题

内容...
```

**验证**：
- 在 Obsidian 中打开文件
- 点击属性面板应该能看到 tags
- tags 应该可点击和搜索

---

### Issue 4: diagram.canvas JSON 格式错误

**问题**：
- 在 Obsidian 中打开报错："fail to open"
- JSON 包含无效的控制字符（换行符）

**原因**：
- text 字段中的 `\n` 没有正确转义
- JSON 序列化时需要使用 `json.dump()` 而不是手动拼接

**解决方案**：
使用 Python 的 `json.dump()` 生成 JSON Canvas：

```python
import json

canvas_data = {
    "nodes": [
        {
            "id": "root",
            "type": "text",
            "text": "第一行\n第二行",  # Python 字符串中的 \n 会被正确转义
            "x": 0,
            "y": 0
        }
    ]
}

# 使用 json.dump() 而不是手动拼接
with open("diagram.canvas", "w", encoding="utf-8") as f:
    json.dump(canvas_data, f, ensure_ascii=False, indent=2)
```

**验证**：
- JSON 文件必须符合 JSON Canvas 规范
- text 节点必须包含 "type": "text" 和 "text" 字段
- 在 Obsidian 中应该能正常打开

---

## Files Modified

### 1. `.claude/skills/wechat-archiver/tools/wechat_archiver.py`

**添加的功能**：
- `--simple-slug` 命令行选项

### 2. 测试文件修复

已修复的测试文件：
- `outputs/20-阅读笔记/20260111-大道至简Cursor发表了一个长篇-悔改书--41f7f7/note.md`
- `outputs/20-阅读笔记/20260111-大道至简Cursor发表了一个长篇-悔改书--41f7f7/table.base`
- `outputs/20-阅读笔记/20260111-大道至简Cursor发表了一个长篇-悔改书--41f7f7/diagram.canvas`

---

## Usage Examples

### 默认模式（包含 asset_id）

```bash
python .claude/skills/wechat-archiver/tools/wechat_archiver.py \
  "https://mp.weixin.qq.com/s/xxx" \
  --folder "20-阅读笔记"
```

输出：
```
outputs/20-阅读笔记/20260111-文章标题-41f7f7/
├── article.md
├── note.md         # 包含 YAML frontmatter 和 tags
├── diagram.canvas  # 正确的 JSON Canvas 格式
├── table.base      # sources 只包含 note.md
├── meta.json
├── run.jsonl
└── images/
    └── 001.png
```

### 简洁模式（不包含 asset_id）

```bash
python .claude/skills/wechat-archiver/tools/wechat_archiver.py \
  "https://mp.weixin.qq.com/s/xxx" \
  --folder "20-阅读笔记" \
  --simple-slug
```

输出：
```
outputs/20-阅读笔记/20260111-文章标题/
├── article.md
├── note.md
├── diagram.canvas
├── table.base
├── meta.json
├── run.jsonl
└── images/
    └── 001.png
```

---

## Testing

### Test 1: 验证 simple-slug

```bash
cd "F:/Project/my-skills"
python .claude/skills/wechat-archiver/tools/wechat_archiver.py \
  "https://mp.weixin.qq.com/s/q-ULGOEj5SIm-uHKo7yfoQ" \
  --simple-slug
```

检查输出目录名称是否为：`20260111-我的2025年~/`

### Test 2: 验证 Obsidian 兼容性

1. 打开 Obsidian
2. 打开 vault: `F:/Project/my-skills/outputs`
3. 导航到资产目录
4. 检查：
   - note.md 的 tags 是否显示
   - diagram.canvas 是否能打开
   - table.base 是否只显示 note.md 的数据

---

## Notes

### 关于 Asset ID 冲突

如果使用 `--simple-slug`，同一天抓取同标题的文章会冲突。

**解决方案**：
- 我们chat-archiver 会检测到目录已存在
- 检查内容哈希是否相同
- 如果相同，跳过（幂等性）
- 如果不同，提示用户手动处理或使用默认模式

### 关于 note-creator 集成

当前测试中，note.md、diagram.canvas、table.base 是模拟生成的。

**真正的集成**需要：
1. 调用 `Skill(note-creator)`
2. 传递正确的上下文和参数
3. 确保 note-creator 生成符合规范的文件

这需要在后续版本中实现。

---

## Changelog

### 2026-01-11
- ✅ 添加 `--simple-slug` 选项
- ✅ 修复 table.base sources 配置
- ✅ 修复 note.md YAML frontmatter
- ✅ 修复 diagram.canvas JSON 格式
- 📝 创建此文档
