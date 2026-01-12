# Idempotency and Asset Management Rules

## Purpose
定义幂等性控制和资产管理规则，确保同一 URL 重复抓取不会产生混乱。

---

## Asset ID Generation

### URL Normalization

```python
def normalize_url(url: str) -> str:
    """
    标准化 URL，移除追踪参数
    """
    from urllib.parse import urlparse, parse_qs, urlunparse

    parsed = urlparse(url)

    # 移除已知的追踪参数
    tracking_params = {
        "chksm",  # 微信校验和
        "vid",     # 微信访客 ID
        "uin",     # 微信用户 ID
        "sid",     # 会话 ID
        "from",    # 来源
    }

    # 过滤查询参数
    filtered_qs = {
        k: v for k, v in parse_qs(parsed.query).items()
        if k.lower() not in tracking_params
    }

    # 重建 URL（保留关键查询参数如 s/xxxxx）
    # 对于微信文章，保留 path 部分 (mp.weixin.qq.com/s/xxxxx)
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        "",  # 清空 query
        parsed.fragment
    ))

    return normalized.rstrip("/")  # 移除尾部斜杠
```

### Asset ID Calculation

```python
import hashlib

def generate_asset_id(url: str) -> str:
    """
    生成 asset_id (SHA-1 hash of normalized URL)
    """
    normalized = normalize_url(url)
    return hashlib.sha1(normalized.encode()).hexdigest()
```

**示例**：
```
URL: https://mp.weixin.qq.com/s/xxx?chksm=abc&vid=123
Normalized: https://mp.weixin.qq.com/s/xxx
Asset ID: a1b2c3d4e5f6... (40 字符)
```

---

## Slug Generation

### Slug Format

```
<date_prefix>-<title_slug>-<asset_id_short>
```

其中：
- `date_prefix`: `YYYYMMDD` (抓取日期)
- `title_slug`: 标题的 slug 形式 (max 50 字符)
- `asset_id_short`: asset_id 的前 6 位

### Slug Generation Code

```python
import re
from datetime import datetime
from html import unescape
from urllib.parse import quote

def sanitize_title(title: str, max_len: int = 50) -> str:
    """
    清理标题，生成合法的文件名
    """
    # 移除非法字符
    illegal_chars = re.compile(r'[\\/:*?"<>|]+')
    title = illegal_chars.sub('-', title)

    # 移除多余空白
    title = re.sub(r'\s+', ' ', title).strip()

    # 移除特殊字符（保留中文、字母、数字、-、_）
    title = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title)

    # 截断
    if len(title) > max_len:
        title = title[:max_len].rstrip()

    # 如果为空，使用默认值
    if not title:
        title = "untitled"

    return title


def generate_slug(title: str, asset_id: str, date: datetime = None) -> str:
    """
    生成唯一的 slug
    """
    if date is None:
        date = datetime.now()

    date_prefix = date.strftime("%Y%m%d")
    title_slug = sanitize_title(title, max_len=50)
    asset_id_short = asset_id[:6]

    return f"{date_prefix}-{title_slug}-{asset_id_short}"
```

**示例**：
```
Title: "Understanding Async Programming in Python"
Asset ID: a1b2c3d4e5f6...
Slug: 20260111-understanding-async-programming-a1b2c3
```

---

## Hash Content Calculation

### Content Hash

```python
def hash_article_content(article_path: str) -> str:
    """
    计算 article.md 的内容哈希
    """
    import hashlib

    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 归一化：移除空白差异
    normalized = re.sub(r'\s+', ' ', content).strip()

    return hashlib.sha256(normalized.encode()).hexdigest()
```

**注意**：使用 SHA-256 而非 SHA-1，避免与 asset_id 混淆。

---

## Idempotency Check

### Decision Flow

```
┌─────────────────────────┐
│ 调用 wechat2md          │
│ 获得 article.md         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 计算 asset_id           │
│ 计算 hash_content       │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 资产目录是否存在？      │
└──────────┬──────────────┘
           │
     ┌─────┴─────┐
     │           │
    NO          YES
     │           │
     ▼           ▼
┌──────────┐ ┌──────────────────┐
│ 创建目录  │ │ 读取 meta.json   │
└─────┬────┘ └────────┬─────────┘
      │               │
      │               ▼
      │      ┌────────────────────┐
      │      │ hash_content 相同？ │
      │      └────────┬───────────┘
      │           ┌───┴───┐
      │          YES     NO
      │           │       │
      │           ▼       ▼
      │    ┌──────────┐ ┌──────────────┐
      │    │ 跳过生成  │ │ 调用         │
      │    │ (force?)  │ │ note-creator │
      │    └─────┬────┘ └──────┬───────┘
      │          │              │
      │          ▼              │
      │     ┌────────────────────┘
      │     │
      ▼     ▼
└────────────────────┐
│ 合并 meta.json      │
│ 记录 run.jsonl      │
└────────────────────┘
```

### Implementation

```python
import json
import os
from datetime import datetime
from pathlib import Path

def check_idempotency(asset_dir: str, hash_content: str, force: bool = False) -> dict:
    """
    检查幂等性，返回决策结果
    :return: {"should_generate": bool, "reason": str}
    """
    meta_path = os.path.join(asset_dir, "meta.json")

    # 目录不存在，首次运行
    if not os.path.exists(meta_path):
        return {
            "should_generate": True,
            "reason": "first_run"
        }

    # 读取历史 meta
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 强制重新生成
    if force:
        return {
            "should_generate": True,
            "reason": "forced"
        }

    # 内容哈希比较
    historical_hash = meta.get("hash_content")
    if historical_hash == hash_content:
        return {
            "should_generate": False,
            "reason": "content_unchanged"
        }
    else:
        return {
            "should_generate": True,
            "reason": "content_changed",
            "old_hash": historical_hash,
            "new_hash": hash_content
        }
```

---

## Meta.json Schema

### Version 1.0 (Initial)

```json
{
  // Asset identification (MUST)
  "asset_id": "a1b2c3d4e5f6...",
  "url": "https://mp.weixin.qq.com/s/xxx",
  "title": "Article Title",
  "slug": "20260111-article-title-a1b2c3",

  // Hash (MUST)
  "hash_content": "sha256 hash of article.md",
  "hash_algorithm": "sha256",

  // Timestamps (MUST)
  "ingested_at": "2026-01-11T10:30:00",
  "published_at": "2026-01-10"  // extracted from article, null if not found,

  // Artifact plan
  "artifact_plan": ["md", "canvas", "base"],

  // Note-creator metadata (merged)
  "category": "article",
  "tags": ["技术", "Python", "异步编程"],
  "properties": {
    "created": "2026-01-11",
    "modified": "2026-01-11",
    "source": "wechat_article",
    "folder": "20-阅读笔记"
  },

  // Run history
  "last_run_at": "2026-01-11T10:30:00",
  "last_run_status": "success",  // success | failed | skipped
  "last_run_reason": "first_run",  // first_run | content_changed | forced | content_unchanged
  "run_count": 1,

  // Version
  "meta_version": "1.0"
}
```

### Meta Merge Logic

```python
def merge_meta(wrapper_meta: dict, note_meta: dict) -> dict:
    """
    合并 wrapper 和 note-creator 的元数据
    """
    # 保留原有字段
    merged = wrapper_meta.copy()

    # Increment run count
    merged["run_count"] = merged.get("run_count", 0) + 1

    # Merge note-creator fields
    if "category" in note_meta:
        merged["category"] = note_meta["category"]
    if "tags" in note_meta:
        merged["tags"] = note_meta["tags"]
    if "properties" in note_meta:
        merged["properties"].update(note_meta["properties"])

    # Update timestamps
    merged["last_run_at"] = datetime.now().isoformat()

    return merged
```

---

## Run.jsonl Format

### Log Entry Schema

每行一个 JSON 对象：

```json
{
  "timestamp": "2026-01-11T10:30:00.123Z",
  "action": "ingest",  // ingest | update | skip | fail
  "asset_id": "a1b2c3...",
  "status": "success",  // success | failed | skipped
  "reason": "first_run",
  "hash_content": "...",
  "artifact_plan": ["md", "canvas"],
  "duration_ms": 1234,
  "error": null  // or error message
}
```

### Examples

```
{"timestamp": "2026-01-11T10:30:00", "action": "ingest", "asset_id": "a1b2c3...", "status": "success", "reason": "first_run", "hash_content": "abc123", "artifact_plan": ["md", "canvas"], "duration_ms": 5234}
{"timestamp": "2026-01-11T11:00:00", "action": "update", "asset_id": "a1b2c3...", "status": "success", "reason": "content_changed", "hash_content": "def456", "artifact_plan": ["md", "canvas", "base"], "duration_ms": 3122}
{"timestamp": "2026-01-11T12:00:00", "action": "skip", "asset_id": "a1b2c3...", "status": "skipped", "reason": "content_unchanged", "hash_content": "def456", "duration_ms": 234}
{"timestamp": "2026-01-11T13:00:00", "action": "fail", "asset_id": "d4e5f6...", "status": "failed", "reason": "wechat2md_error", "error": "Failed to fetch URL", "duration_ms": 5000}
```

---

## Asset Directory Structure Validation

### Validation Function

```python
def validate_asset_directory(asset_dir: str) -> dict:
    """
    验证资产目录的完整性
    """
    required_files = ["article.md", "meta.json"]
    required_dirs = ["images/"]

    results = {
        "valid": True,
        "missing_files": [],
        "missing_dirs": [],
        "warnings": []
    }

    # Check required files
    for file in required_files:
        path = os.path.join(asset_dir, file)
        if not os.path.exists(path):
            results["missing_files"].append(file)
            results["valid"] = False

    # Check required directories
    for dir in required_dirs:
        path = os.path.join(asset_dir, dir)
        if not os.path.exists(path):
            results["missing_dirs"].append(dir)
            results["valid"] = False

    # Check optional files
    optional_files = ["note.md", "diagram.canvas", "table.base", "run.jsonl"]
    for file in optional_files:
        path = os.path.join(asset_dir, file)
        if os.path.exists(path):
            results[file] = "present"
        else:
            results[file] = "optional_not_generated"

    return results
```

---

## Conflict Resolution

### Scenario 1: Directory Exists, meta.json Missing

**决策**：询问用户

```
⚠️  资产目录已存在但 meta.json 缺失或损坏
目录：outputs/20-阅读笔记/20260111-example-a1b2c3/

选项：
[1] 覆盖：重新生成所有文件（原文会保留）
[2] 跳过：保留现有文件，不进行任何操作
[3] 恢复：尝试从现有文件重建 meta.json

请选择 (1/2/3):
```

### Scenario 2: Content Hash Changed

**决策**：自动更新，但保留历史

```python
# 在 meta.json 中保留历史哈希
if "hash_history" not in meta:
    meta["hash_history"] = []

meta["hash_history"].append({
    "hash": old_hash,
    "timestamp": meta["last_run_at"],
    "run_count": meta["run_count"]
})

# 限制历史记录数量（最多保留 10 条）
if len(meta["hash_history"]) > 10:
    meta["hash_history"] = meta["hash_history"][-10:]
```

---

## Cleanup Strategy

### Temporary File Cleanup

```python
def cleanup_temp_files(cwd: str, target_slug: str) -> None:
    """
    清理 wechat2md 的临时输出
    """
    # wechat2md 会创建 outputs/<title>/ 和 images/<title>/
    # 这些在复制到资产目录后应该删除

    temp_patterns = [
        os.path.join(cwd, "outputs", "*", "*.md"),  # 不在资产目录的临时 md
        # 注意：不要删除 images/<title>/ 因为已经移到资产目录内
    ]

    # 安全检查：只删除明确的临时文件
    # 实现时应该更精确，避免误删
```

---

## Testing Checklist

实现时必须测试：
- [ ] 相同 URL 生成相同的 asset_id
- [ ] 相同内容跳过 note-creator 生成
- [ ] `--force` 强制重新生成
- [ ] 内容变化时正确更新
- [ ] meta.json 正确合并
- [ ] run.jsonl 正确追加
- [ ] 临时文件正确清理
- [ ] 并发抓取不同文章不冲突
