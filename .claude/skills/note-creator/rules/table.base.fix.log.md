# table.base 问题修复记录

## 问题描述

用户反馈 table.base 只显示了 file_name 字段，没有显示在 compare/*.md 文件中定义的其他字段（如 name, 输入, 输出, 定位, 边界, 产物）。

## 根本原因

**Obsidian Base 的 filters 必须用字符串格式（带引号）**

错误的配置：
```yaml
filters:
  and:
    - item_type == "tool"         # ❌ 缺少引号
    - file.hasTag("对比")          # ❌ 缺少引号
```

正确的配置：
```yaml
filters:
  and:
    - 'item_type == "tool"'       # ✅ 带引号
    - 'file.hasTag("对比")'        # ✅ 带引号
```

### 为什么必须用引号？

Obsidian Base 的 filters 是**表达式字符串**，需要被 YAML 解析后传递给 Obsidian Base 的表达式引擎执行。

如果不加引号：
- YAML 会尝试解析 `item_type == "tool"` 作为其他数据类型
- 可能导致解析失败或传递错误的数据类型
- 结果：**过滤失效，显示所有文件**

## 修复内容

### 1. 修复了 table.base 的 filters

**文件**: `outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/table.base`

**修改**：
```diff
filters:
  and:
-    - item_type == "tool"
-    - file.hasTag("对比")
+    - 'item_type == "tool"'
+    - 'file.hasTag("对比")'
```

### 2. 更新了 note-creator 规则文档

**文件**: `.claude/skills/note-creator/rules/base.path.guide.md`

**添加内容**：
1. ⚠️ 强调 filters 必须用引号的部分
2. ❌ 错误示例对比
3. ✅ 正确格式说明
4. 快速检查清单
5. 常见错误排查表

## 预防措施

### 未来生成 table.base 时必须检查

1. **filters 必须有引号**
   ```yaml
   filters:
     and:
       - 'field == "value"'    # ✅ 正确
   ```

2. **验证 compare/*.md 文件**
   - frontmatter 字段存在
   - item_type 正确
   - tags 包含 "对比"

3. **验证路径配置**
   - basePath 使用完整相对路径
   - data.path 使用完整相对路径

## 完整的正确示例

```yaml
version: 1
type: table
name: 工具对比
sources:
  - type: local
    basePath: outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare
    include:
      - "*.md"
data:
  - type: frontmatter
    path: outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare/*.md

views:
  - type: table
    name: 工具对比
    filters:
      and:
        - 'item_type == "tool"'       # ⚠️ 必须有引号
        - 'file.hasTag("对比")'        # ⚠️ 必须有引号
    sources:
      - type: local
        basePath: outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare
        include:
          - "*.md"
    columns:
      - id: col1
        key: name                      # 必须与 frontmatter 字段名一致
        name: 名称
        type: text
      # ... 其他列定义
```

## 相关文档

- `.claude/skills/note-creator/rules/base.path.guide.md` - 完整的 table.base 配置指南
- `.claude/skills/obsidian-bases/SKILL.md` - Obsidian Base 官方文档

## 经验教训

1. **YAML 的引号很重要**
   - 过滤条件必须是字符串
   - 嵌套引号用单引号包裹，内部用双引号

2. **Obsidian Base 的过滤器是表达式**
   - 不是简单的键值对
   - 需要被解析和执行

3. **文档化很重要**
   - 创建了详细的指南文档
   - 包含正确/错误示例
   - 添加了快速检查清单

4. **测试验证**
   - 生成后必须在 Obsidian 中打开验证
   - 检查字段是否正确显示
   - 检查过滤是否生效
