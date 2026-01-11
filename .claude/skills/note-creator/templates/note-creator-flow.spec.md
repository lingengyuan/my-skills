# Note-Creator Flow Canvas 规范

## 布局参数（固定值）

### 主流程节点
```
中心 X 坐标: 350
节点宽度: 300
```

### Y 坐标
```
输入节点:        y = 0
分类节点:        y = 180  (间距 180)
路径计算节点:    y = 400  (间距 220)
文件生成组:      y = 600  (间距 200)
输出节点:        y = 950  (间距 350)
```

### 文件生成组内部
```
Group 边界: x=100, y=600, width=800, height=300

左列 (必需文件):
- note.md:    x=130, y=640
- meta.json:  x=130, y=780

右列 (可选文件 + 路由):
- canvas:     x=390, y=640
- base:       x=650, y=640
- routing:    x=390, y=780
```

### 节点尺寸
```
标准节点:  300x120 或 300x140
文件节点:  220x100 或 220x90
路由节点:  480x90
输出节点:  300x100
```

## 颜色方案

```yaml
输入阶段:    color: "6"  (紫色)
处理阶段:    color: "3"  (黄色)
关键节点:    color: "1"  (红色 - CWD)
必需输出:    color: "4"  (绿色)
可选输出:    color: "2"  (橙色) 或 "3" (黄色)
最终输出:    color: "5"  (青色)
```

## 节点内容模板

```markdown
## [标题]

- **重点项** (状态)
- 普通项

说明文字
```

## 节点 ID（固定）

```
input
classification
paths
generation-group
note-md
meta-json
canvas-file
base-file
routing
output
```

## 边连接规则

```
input → classification → paths → routing
routing → note-md (always)
routing → canvas-file (conditional)
routing → base-file (conditional)
note-md → meta-json
meta-json → output
base-file → output
```

## 复现检查清单

生成 canvas 时必须：

- [ ] 使用上述固定坐标
- [ ] 使用上述节点 ID
- [ ] 使用上述颜色编码
- [ ] 所有文字使用中文
- [ ] 技术术语可保留英文
- [ ] Group 包含文件生成阶段
- [ ] 边连接符合上述规则

## 示例提示词

```
创建 note-creator skill 流程图 canvas，严格遵循：
.claude/skills/note-creator/templates/note-creator-flow.spec.md 规范

全中文，固定坐标，固定颜色，固定布局
```
