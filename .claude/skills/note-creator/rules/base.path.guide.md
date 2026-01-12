# table.base 路径配置规则

## 问题

Obsidian Base 的 `basePath` 是相对于 **vault 根目录**，而不是相对于 .base 文件所在目录。

## 错误示例

❌ **错误**：使用相对路径
```yaml
sources:
  - type: local
    basePath: compare        # 这会从 vault 根目录查找 compare 文件夹
    include:
      - "*.md"
```

这会导致扫描到 vault 根目录下所有名为 `compare` 的文件夹，而不是当前文章的 compare 文件夹。

## 正确示例

✅ **正确**：使用完整相对路径
```yaml
sources:
  - type: local
    basePath: outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare
    include:
      - "*.md"
```

这样只会扫描指定路径下的文件。

## 生成规则

### 步骤 1：计算完整路径

在 note-creator 执行时：

```python
import os
from pathlib import Path

# 获取当前工作目录
cwd = os.getcwd()  # 例如：/f/Project/my-skills

# 构建完整路径
asset_dir = Path(cwd) / "outputs" / folder / title
compare_dir = asset_dir / "compare"

# 相对于 vault 根目录的路径
relative_path = compare_dir.relative_to(cwd)
# 结果：outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare
```

### 步骤 2：添加过滤条件（⚠️ 关键：必须用引号）

为了确保只显示对比项，添加 filters：

**⚠️ 最重要的规则：filters 必须用字符串格式（带引号）**

```yaml
filters:
  and:
    - 'item_type == "tool"'      # ✅ 正确：带引号
    - 'file.hasTag("对比")'       # ✅ 正确：带引号
```

**❌ 错误示例**（会导致过滤失效，显示所有文件）：

```yaml
filters:
  and:
    - item_type == "tool"         # ❌ 错误：缺少引号
    - file.hasTag("对比")          # ❌ 错误：缺少引号
```

**为什么必须用引号？**

Obsidian Base 的 filters 是**表达式字符串**，需要被解析和执行。如果不用引号，YAML 会将它们解析为其他数据类型（如布尔值、数字等），导致过滤失效。

**正确的格式**：
- 每个过滤条件必须是一个**字符串**（用单引号或双引号包裹）
- 字符串内部比较值用双引号
- 例如：`'item_type == "tool"'` 或 `"item_type == 'tool'"`

### 步骤 3：完整的 table.base 配置

```yaml
version: 1
type: table
name: {title} 对比
sources:
  - type: local
    basePath: {full_relative_path_to_compare}  # 完整路径
    include:
      - "*.md"
    exclude: []
data:
  -
    type: frontmatter
    path: {full_relative_path_to_compare}/*.md

views:
  - type: table
    name: 对比视图
    filters:
      and:
        - 'item_type == "{item_type}"'
        - 'file.hasTag("对比")'
    sort: []
    sources:
      - type: local
        basePath: {full_relative_path_to_compare}
        include:
          - "*.md"
    state:
      # ... column definitions
    columns:
      # ... column definitions
    formatting: []
```

## 对比项目文件要求

每个 compare/*.md 文件必须包含：

```yaml
---
item_type: tool              # 或其他合适的类型
name: SpecKit
输入: 想法、需求
输出: 系统规格
定位: 设计工具
边界: 0→1 项目
产物: 完整结构设计
tags:
  - SDD
  - 设计工具
  - 对比                    # 必须包含 "对比" tag
source: wechat_article
created: 2026-01-12
modified: 2026-01-12
category: methodology
---
```

## 调试技巧

如果 table.base 显示了错误的数据：

1. **检查路径**：确认 `basePath` 是从 vault 根目录开始的完整相对路径
2. **检查过滤**：确认 filters 中的 item_type 和 tags 与 compare/*.md 文件中的 frontmatter 匹配
3. **检查文件**：确认 compare/*.md 文件存在且包含正确的 frontmatter

## 示例对比

### 普通文章（非对比）

```yaml
sources:
  - type: local
    basePath: .
    include:
      - "note.md"
```

### 对比文章

```yaml
sources:
  - type: local
    basePath: outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare
    include:
      - "*.md"

filters:
  and:
    - 'item_type == "tool"'
    - 'file.hasTag("对比")'
```

## 关键要点

1. ✅ `basePath` 必须使用**从 vault 根目录开始的完整相对路径**
2. ✅ 对比模式**必须**添加 filters 限定 item_type 和 tags
3. ✅ compare/*.md 文件**必须**包含 "对比" tag
4. ✅ data.path 也要使用完整路径
5. ⚠️ **filters 的每个条件必须用字符串（带引号）** - 这是最容易出错的地方！

## 快速检查清单

生成 table.base 后，必须检查：

- [ ] `basePath` 使用完整相对路径（从 vault 根目录）
- [ ] `data.path` 使用完整相对路径
- [ ] `filters` 存在且每个条件都有引号
- [ ] `filters` 中检查了 `item_type` 或 `file.hasTag()`
- [ ] compare/*.md 文件存在
- [ ] compare/*.md 文件的 frontmatter 包含正确的 `item_type` 和 `tags`
- [ ] tags 中包含 "对比"
- [ ] columns 的 key 与 frontmatter 字段名匹配

## 常见错误排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 显示所有文件 | filters 缺少引号 | 添加引号：`'item_type == "tool"'` |
| 显示所有文件 | filters 不存在 | 添加 filters 部分 |
| 只显示 file_name | frontmatter 字段不存在 | 检查 compare/*.md 的 frontmatter |
| 某些字段为空 | columns.key 与 frontmatter 不匹配 | 确保 key 与 frontmatter 字段名一致 |
| 找不到文件 | basePath 路径错误 | 使用完整相对路径从 vault 根目录 |
