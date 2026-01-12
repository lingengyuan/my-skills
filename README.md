# WeChat Article Archiver Skills

微信公众号文章归档到知识库的完整解决方案，使用 v2 版本实现更好的格式保留和统一的目录结构。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r .claude/skills/wechat2md/requirements.txt --break-system-packages
```

### 2. 基本使用

```bash
# 使用 v2 版本抓取文章
python .claude/skills/wechat2md/tools/wechat2md_v2.py "https://mp.weixin.qq.com/s/your-article-url"
```

### 3. 查看结果

生成的文件会保存在 `outputs/<folder>/<slug>/` 目录下：
- `article.md` - 原始文章
- `images/` - 图片目录（如有）
- `meta.json` - 元数据

## 📁 项目结构

| 目录/文件 | 说明 |
|---------|------|
| `.claude/skills/wechat2md/` | 微信文章转 Markdown（v2 ✨） |
| `.claude/skills/wechat-archiver/` | 文章归档到知识库（v2 ✨） |
| `.claude/skills/note-creator/` | 生成结构化笔记 |
| `CLAUDE.md` | 项目指南 |
| `SKILLS_AUDIT.md` | Skills 审计报告 |
| `WECHAT2MD_OPTIMIZATION.md` | v2 优化总结 |

## 💡 主要功能

### wechat2md v2
- ✅ 使用 markdownify 库（95% 格式保留）
- ✅ 统一的目录结构（article.md + images/ + meta.json）
- ✅ asset_id 唯一标识（SHA1 of URL）
- ✅ 自动清理空图片目录
- ✅ 完整的元数据记录

### wechat-archiver v2
- ✅ 调用 wechat2md v2 抓取文章
- ✅ 自动生成结构化笔记
- ✅ 可选生成架构图和对比表
- ✅ 幂等性控制（相同 URL 不重复）
- ✅ 统一的资产目录管理

## 📖 使用方法

### 方法一：直接使用 wechat2md v2

```bash
# 基本用法
python .claude/skills/wechat2md/tools/wechat2md_v2.py "URL"

# 指定输出文件夹
python .claude/skills/wechat2md/tools/wechat2md_v2.py "URL" --target-folder "20-阅读笔记"

# 自定义 slug
python .claude/skills/wechat2md/tools/wechat2md_v2.py "URL" --slug "my-article"
```

**输出结构**：
```
outputs/20-阅读笔记/文章标题-abc123/
  ├── article.md      # 原始文章
  ├── images/         # 图片（如有）
  └── meta.json       # 元数据
```

### 方法二：使用 wechat-archiver v2

```bash
python .claude/skills/wechat-archiver/tools/wechat_archiver_v2.py "URL" --canvas auto --base auto
```

**输出结构**：
```
outputs/20-阅读笔记/文章标题-abc123/
  ├── article.md      # 原始文章
  ├── note.md         # 结构化笔记
  ├── diagram.canvas  # 可选：架构图
  ├── table.base      # 可选：对比表
  ├── images/         # 图片（如有）
  └── meta.json       # 统一元数据
```

### 方法三：通过 Claude Skill（推荐）

在 Claude Code 中：

```bash
# 归档文章
/wechat-archiver article_url="https://mp.weixin.qq.com/s/xxxxx"

# 生成结构化笔记
/note-creator "为这篇文章生成笔记"
```

## 📂 输出结构

```
outputs/
├── 00-Inbox/
├── 10-项目/
├── 20-阅读笔记/
│   └── 文章标题-abc123/
│       ├── article.md      # 原始文章
│       ├── note.md         # 结构化笔记（可选）
│       ├── diagram.canvas  # 架构图（可选）
│       ├── table.base      # 对比表（可选）
│       ├── images/         # 图片
│       │   ├── 001.jpg
│       │   └── 002.png
│       └── meta.json       # 元数据
├── 30-方法论/
└── 90-归档/
```

## 🎨 v2 版本改进

| 特性 | v1 | v2 |
|------|----|----|
| Markdown 转换 | 自定义解析器（70%） | markdownify（95%） |
| 目录结构 | 分散（outputs/ + images/） | 统一目录 |
| 唯一标识 | 日期前缀（重复问题） | asset_id（SHA1） |
| 元数据 | ❌ | ✅ 完整 meta.json |
| 图片路径 | `../images/<title>/` | `images/`（相对） |
| 幂等性 | ❌ | ✅ content_hash |

详细对比见：`.claude/skills/wechat2md/V2_UPGRADE.md`

## 🔧 技术栈

- **requests** - HTTP 请求
- **BeautifulSoup4** - HTML 解析
- **markdownify** - HTML 转 Markdown（v2 新增）
- **lxml** - XML/HTML 解析器

## ⚠️ 注意事项

1. **仅供个人学习和备份使用**
2. **尊重原作者版权**
3. **不用于商业用途**
4. **部分文章可能需要登录才能查看**
5. **图片可能有防盗链保护**

## 🐛 常见问题

**Q: markdownify 未安装？**
```bash
pip install markdownify lxml --break-system-packages
```

**Q: 图片路径错误？**
- v2.1 已修复图片路径问题
- 确保使用最新版本

**Q: 抓取失败？**
- 检查 URL 是否为 `mp.weixin.qq.com` 域名
- 确保是公开可访问的文章
- 检查网络连接

## 📚 更多文档

- `SKILL.md` - 技能使用指南
- `CLAUDE.md` - 项目详细指南
- `SKILLS_AUDIT.md` - Skills 审计报告
- `WECHAT2MD_OPTIMIZATION.md` - v2 优化总结
- `.claude/skills/wechat2md/V2_UPGRADE.md` - v2 升级指南

## 🔗 相关资源

- [Claude Code 文档](https://code.claude.com/docs/en/skills)
- [Markdown 语法指南](https://www.markdownguide.org/)
- [markdownify 文档](https://github.com/matthewwithanm/markdownify)

## 📄 许可证

MIT License - 仅供学习和个人使用，请遵守相关法律法规和平台规则。
