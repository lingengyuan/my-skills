# WeChat Article Archiver Skills

微信公众号文章归档技能集合，使用 v2 版本实现更好的格式保留和统一的目录结构。

## 功能概述

这个项目提供了完整的微信公众号文章处理和知识库归档流程：

1. **wechat2md** - 将微信文章转换为 Markdown（v2 版本，使用 markdownify）
2. **wechat-archiver** - 一键归档文章到知识库并生成结构化笔记
3. **note-creator** - 生成结构化笔记、图表和对比表

## 使用前准备

### 1. 安装依赖

```bash
pip install -r .claude/skills/wechat2md/requirements.txt --break-system-packages
```

或者单独安装：

```bash
pip install requests beautifulsoup4 markdownify lxml --break-system-packages
```

## 使用方式

### 方式一：直接使用 wechat2md v2

```bash
# 基本用法
python .claude/skills/wechat2md/tools/wechat2md_v2.py "https://mp.weixin.qq.com/s/xxxxx"

# 指定输出文件夹
python .claude/skills/wechat2md/tools/wechat2md_v2.py "URL" --target-folder "20-阅读笔记"

# 自定义 slug
python .claude/skills/wechat2md/tools/wechat2md_v2.py "URL" --slug "my-article"
```

**输出结构**：
```
outputs/<folder>/<slug>/
  ├── article.md      # 原始文章
  ├── images/         # 图片（如有）
  └── meta.json       # 元数据
```

### 方式二：使用 wechat-archiver v2（推荐）

```bash
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py "URL" --canvas auto --base auto
```

**输出结构**：
```
outputs/<folder>/<slug>/
  ├── article.md      # 原始文章
  ├── note.md         # 结构化笔记
  ├── diagram.canvas  # 可选：架构图
  ├── table.base      # 可选：对比表
  ├── images/         # 图片（如有）
  └── meta.json       # 统一元数据
```

### 方式三：通过 Claude Skill（推荐）

在 Claude Code 中：

```bash
# 归档文章
/wechat-archiver article_url="https://mp.weixin.qq.com/s/xxxxx"

# 生成结构化笔记
/note-creator "为这篇文章生成笔记"
```

## v2 版本改进

| 特性 | v1 | v2 |
|------|----|----|
| Markdown 转换 | 自定义解析器（70%） | markdownify（95%） |
| 目录结构 | 分散（outputs/ + images/） | 统一目录 |
| 唯一标识 | 日期前缀（重复问题） | asset_id（SHA1） |
| 元数据 | ❌ | ✅ 完整 meta.json |
| 图片路径 | `../images/<title>/` | `images/`（相对） |

详细对比见：`.claude/skills/wechat2md/V2_UPGRADE.md`

## 输出契约

- **article.md**: 原始文章（保留微信排版）
- **images/**: 图片目录（仅当有图片时创建）
- **meta.json**: 包含 asset_id, url, title, author, content_hash 等
- **note.md**: 结构化笔记（note-creator 生成）
- **diagram.canvas**: 可视化架构图（可选）
- **table.base**: 对比表格（可选）

## 常见问题处理

### 1. 抓取失败

**可能原因**：
- URL 格式不正确
- 文章需要登录才能查看
- 文章已被删除
- 网络连接问题

**解决方案**：
- 检查 URL 是否为 `mp.weixin.qq.com` 域名
- 确保是公开文章
- 检查网络连接

### 2. 图片下载失败

**处理方式**：
- 图片下载失败不影响文章生成
- 失败的图片会保留原始 URL
- 检查 `meta.json` 中的 `images_count`

### 3. markdownify 未安装

```bash
ERROR: No module named 'markdownify'
```

**解决**：
```bash
pip install markdownify lxml --break-system-packages
```

## 技术细节

### 图片路径修复（v2.1）

v2 最初版本有图片路径问题（`../images/images/xxx`），已在 v2.1 修复：

```python
# 修复前（错误）
image_prefix = f"../images/{images_dir.name}/"  # → "../images/images/"

# 修复后（正确）
image_prefix = "images/"  # v2: unified dir structure, images relative to article.md
```

### asset_id 算法

```python
def compute_asset_id(url: str) -> str:
    """计算 asset_id (SHA1 of normalized URL)"""
    parsed = urllib.parse.urlparse(url.strip())
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return hashlib.sha1(normalized.encode('utf-8')).hexdigest()
```

**特点**：
- 同一 URL 永远生成相同的 asset_id
- 移除查询参数（追踪参数等）
- 实现幂等性（同一文章不会重复生成目录）

### 幂等性控制

通过 `content_hash` 实现：

```python
# 计算 article.md 内容哈希
hash_content = hashlib.sha256(content.encode()).hexdigest()

# 检查历史 meta.json
if meta.get("content_hash") == hash_content and not force:
    return "skipped"  # 内容未变化，跳过
```

## 文档结构

```
.claude/skills/
├── wechat2md/
│   ├── SKILL.md                    # v1 技能说明（保留向后兼容）
│   ├── V2_UPGRADE.md               # v2 升级指南
│   ├── requirements.txt            # 依赖列表
│   └── tools/
│       ├── wechat2md.py            # v1（保留）
│       └── wechat2md_v2.py         # v2（推荐）✨
├── wechat-archiver/
│   ├── SKILL.md                    # 技能说明
│   ├── BUGFIXES.md                 # Bug 修复记录
│   └── tools/
│       ├── wechat_archiver.py      # v1（保留）
│       └── wechat_archiver_v2.py   # v2（推荐）✨
└── note-creator/
    ├── SKILL.md                    # 技能说明
    ├── rules/                      # 分类规则
    ├── templates/                  # 提示词模板
    └── examples/                   # 使用示例
```

## 最佳实践

1. **使用 v2 版本**：`wechat2md_v2.py` 和 `wechat_archiver_v2.py`
2. **统一的目录结构**：所有文件在同一资产目录下
3. **幂等性控制**：相同 URL 不会重复生成
4. **完整元数据**：使用 meta.json 追踪文章来源和修改历史
5. **结构化笔记**：使用 note-creator 生成高质量笔记

## 扩展功能建议

可以考虑添加：
- [ ] 批量抓取（多 URLs）
- [ ] 视频下载支持
- [ ] PDF 导出
- [ ] 全文搜索索引
- [ ] Web UI 界面

## 许可和使用限制

- 仅供个人学习和备份使用
- 尊重原作者版权
- 不用于商业用途
- 遵守微信公众平台规则

## 相关文档

- [SKILLS_AUDIT.md](SKILLS_AUDIT.md) - Skills 审计报告
- [WECHAT2MD_OPTIMIZATION.md](WECHAT2MD_OPTIMIZATION.md) - v2 优化总结
- [CLAUDE.md](CLAUDE.md) - 项目指南
