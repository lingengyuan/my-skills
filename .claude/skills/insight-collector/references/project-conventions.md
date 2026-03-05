# CodeSnippets Project Conventions

## Project Root

`/root/projects/CodeSnippets`

## Directory Map

| Directory | Purpose | File types |
|-----------|---------|------------|
| `python/` | Python code snippets | `.py` |
| `javascript/` | JavaScript / HTML single-file tools | `.js`, `.html` |
| `html-tools/` | Standalone single-page HTML tools (combined / ready-to-use) | `.html` |
| `shell/` | Shell scripts and CLI tricks | `.sh` |
| `snippets/` | Cross-language or general snippets | any |
| `ideas/` | Project ideas and inspiration notes | `.md` |
| `analysis/` | Cross-cutting analysis and idea combination reports | `.md` |

## Code Snippet Header Template

```python
# =============================================================================
# 名称: <Name>
# 用途: <One-line purpose>
# 依赖: <pip install ... / CDN / stdlib only>
# 适用场景: <Where to use it>
# 来源: <URL or blank>
# 日期: YYYY-MM-DD
# =============================================================================
```

For HTML files use `<!-- ... -->` comment block with the same fields.

## Idea File Template

```markdown
# <Title>

**来源**: <URL or description>
**日期**: YYYY-MM-DD
**状态**: 💡灵感

## 核心内容
...

## 可提取的技术片段
...

## 延伸方向
...

## 参考链接
...
```

## README Catalog

After writing files, update both English and Chinese snippet catalog tables in `README.md`:

English table under `### Snippet Catalog`
Chinese table under `### 片段目录`

Add one row per new file. Also update the project structure tree if a new directory was created.
