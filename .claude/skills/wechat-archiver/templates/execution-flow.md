# Execution Flow Template

## Overview

此模板定义 `wechat-archiver` skill 的完整执行流程。实现时严格按此顺序执行。

---

## Step 0: Input Validation

**Input**: `article_url`, `target_folder`, `force`, `canvas`, `base`

### 0.1 Validate URL

```python
def validate_wechat_url(url: str) -> bool:
    """
    验证是否为有效的微信公众号 URL
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)

    # 检查域名
    if parsed.netloc not in ["mp.weixin.qq.com", "weixin.qq.com"]:
        raise ValueError(f"Invalid WeChat URL domain: {parsed.netloc}")

    # 检查路径格式 (通常为 /s/<xxxxx>)
    if not parsed.path.startswith("/s/"):
        raise ValueError(f"Invalid WeChat URL path: {parsed.path}")

    return True
```

**Error**: 如果验证失败，立即返回错误，不执行后续步骤。

### 0.2 Set Default Values

```python
# Default values
if target_folder is None:
    target_folder = "20-阅读笔记"

if force is None:
    force = False

if canvas is None:
    canvas = "auto"

if base is None:
    base = "auto"
```

---

## Step 1: Call wechat2md

**Command**:
```bash
python3 .claude/skills/wechat2md/tools/wechat2md.py "<article_url>"
```

### 1.1 Capture Output

```python
import subprocess
from pathlib import Path

def run_wechat2md(url: str) -> dict:
    """
    调用 wechat2md 并返回输出路径
    """
    skill_dir = Path(".claude/skills/wechat2md")
    script = skill_dir / "tools" / "wechat2md.py"

    result = subprocess.run(
        ["python3", str(script), url],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )

    if result.returncode != 0:
        raise RuntimeError(f"wechat2md failed: {result.stderr}")

    # Parse output (last line should be the md path)
    output_lines = result.stdout.strip().split("\n")
    md_path = output_lines[-1] if output_lines else None

    # Infer paths
    md_path = Path(md_path)
    title = md_path.stem  # filename without extension
    temp_md_path = md_path
    temp_images_dir = Path.cwd() / "images" / title

    return {
        "title": title,
        "temp_md_path": temp_md_path,
        "temp_images_dir": temp_images_dir
    }
```

### 1.2 Handle Errors

- If `wechat2md` fails → 记录错误到 `run.jsonl`，返回失败状态
- Do NOT create asset directory

---

## Step 2: Generate Asset ID and Slug

```python
import hashlib
from datetime import datetime
from .rules.idempotency import normalize_url, generate_asset_id, sanitize_title, generate_slug

def generate_asset_metadata(article_url: str, article_title: str) -> dict:
    """
    生成资产的唯一标识
    """
    asset_id = generate_asset_id(article_url)
    slug = generate_slug(article_title, asset_id)

    return {
        "asset_id": asset_id,
        "slug": slug,
        "url": article_url,
        "title": article_title
    }
```

---

## Step 3: Create Asset Directory

```python
from pathlib import Path

def create_asset_directory(cwd: Path, target_folder: str, slug: str) -> Path:
    """
    创建统一的资产目录
    """
    asset_dir = cwd / "outputs" / target_folder / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    return asset_dir
```

**Path**: `<cwd>/outputs/<target_folder>/<slug>/`

---

## Step 4: Consolidate Files

```python
import shutil

def consolidate_files(
    asset_dir: Path,
    temp_md_path: Path,
    temp_images_dir: Path
) -> None:
    """
    统一文件到资产目录
    """
    # Copy article.md
    shutil.copy2(temp_md_path, asset_dir / "article.md")

    # Copy images directory
    if temp_images_dir.exists():
        shutil.copytree(temp_images_dir, asset_dir / "images", dirs_exist_ok=True)

    # Cleanup: remove wechat2md temp output
    # Note: be careful to only remove temp files, not the asset_dir
    temp_output_dir = temp_md_path.parent
    if temp_output_dir != asset_dir:
        shutil.rmtree(temp_output_dir, ignore_errors=True)

    # Cleanup temp images
    if temp_images_dir != asset_dir / "images":
        shutil.rmtree(temp_images_dir, ignore_errors=True)
```

---

## Step 5: Calculate Hash and Check Idempotency

```python
from .rules.idempotency import hash_article_content, check_idempotency

def check_should_generate(asset_dir: Path, force: bool) -> dict:
    """
    检查是否需要生成笔记
    """
    # Calculate hash
    article_path = asset_dir / "article.md"
    hash_content = hash_article_content(str(article_path))

    # Check idempotency
    decision = check_idempotency(str(asset_dir), hash_content, force)

    return {
        "hash_content": hash_content,
        "should_generate": decision["should_generate"],
        "reason": decision["reason"]
    }
```

**Decision**:
- If `should_generate == False` → 跳到 Step 9 (记录日志并返回)
- If `should_generate == True` → 继续 Step 6

---

## Step 6: Decide Artifact Plan

```python
from .rules.classification import decide_artifact_plan, decide_diagram_type, decide_base_mode

def decide_plan(article_path: Path, canvas: str, base: str) -> dict:
    """
    决定生成哪些产物
    """
    # Read article content
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Decide artifact plan
    artifact_plan = decide_artifact_plan(content, canvas, base)

    # Decide specific types
    if "canvas" in artifact_plan:
        diagram_type = decide_diagram_type(content)
    else:
        diagram_type = None

    if "base" in artifact_plan:
        base_mode = decide_base_mode(content)
    else:
        base_mode = None

    return {
        "artifact_plan": artifact_plan,
        "diagram_type": diagram_type,
        "base_mode": base_mode
    }
```

---

## Step 7: Call note-creator

**Input Preparation**:

```python
def prepare_note_creator_input(
    asset_dir: Path,
    article_metadata: dict,
    plan: dict
) -> dict:
    """
    准备调用 note-creator 的输入
    """
    # Generate summary prompt from article
    article_path = asset_dir / "article.md"
    with open(article_path, "r", encoding="utf-8") as f:
        article_content = f.read()

    # Extract first paragraph as summary
    first_para = article_content.split("\n\n")[0][:200]

    user_prompt = f"""
    请为以下微信文章生成结构化笔记：

    标题：{article_metadata['title']}
    来源：微信公众号
    摘要：{first_para}

    文章内容：见 article.md

    要求：
    1. 生成 note.md（结构化笔记）
    2. {"生成 diagram.canvas（" + plan['diagram_type'] + "类型图）" if 'canvas' in plan['artifact_plan'] else "不生成 canvas"}
    3. {"生成 table.base（" + plan['base_mode'] + "模式）" if 'base' in plan['artifact_plan'] else "不生成 base"}

    输出到同一目录：{asset_dir}
    """

    return {
        "user_prompt": user_prompt.strip(),
        "optional_context_files": [str(article_path)],
        "runtime_context": {
            "title": article_metadata['title'],
            "folder": Path(asset_dir).parent.name,  # e.g., "20-阅读笔记"
            "artifact_plan": plan['artifact_plan'],
            "diagram_type": plan['diagram_type'],
            "base_mode": plan['base_mode'],
            "output_to_same_dir": True,
            "target_dir": str(asset_dir)
        }
    }
```

**Invocation**: (通过 Claude Code Skill 机制调用)

```
Skill(note-creator) with prepared input
```

**Expected Output**:
- `note.md` in asset_dir
- `diagram.canvas` (if in artifact_plan)
- `table.base` (if in artifact_plan)
- `meta.json` (note-creator's metadata)

### 7.1 Handle note-creator Errors

```python
# If note-creator fails:
# 1. Preserve article.md and images/
# 2. Log error to run.jsonl
# 3. Mark meta.json with "failed" status
# 4. Return partial success to user
```

---

## Step 8: Merge meta.json

```python
import json
from datetime import datetime

def merge_meta_files(
    asset_dir: Path,
    article_metadata: dict,
    hash_content: str,
    plan: dict,
    decision: dict
) -> None:
    """
    合并元数据
    """
    meta_path = asset_dir / "meta.json"

    # Read note-creator's meta (if exists)
    note_meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            note_meta = json.load(f)

    # Build unified meta
    unified_meta = {
        # Asset identification
        "asset_id": article_metadata['asset_id'],
        "url": article_metadata['url'],
        "title": article_metadata['title'],
        "slug": article_metadata['slug'],

        # Hash
        "hash_content": hash_content,
        "hash_algorithm": "sha256",

        # Timestamps
        "ingested_at": datetime.now().isoformat(),
        "published_at": note_meta.get("published_at"),  # extracted by note-creator

        # Artifact plan
        "artifact_plan": plan['artifact_plan'],

        # Note-creator metadata (merge)
        "category": note_meta.get("category", "article"),
        "tags": note_meta.get("tags", []),
        "properties": note_meta.get("properties", {}),

        # Run info
        "last_run_at": datetime.now().isoformat(),
        "last_run_status": "success",
        "last_run_reason": decision['reason'],
        "run_count": note_meta.get("run_count", 0) + 1,

        # Version
        "meta_version": "1.0"
    }

    # Preserve hash history if updating
    if "hash_history" in note_meta:
        unified_meta["hash_history"] = note_meta["hash_history"]

    # Write unified meta
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(unified_meta, f, ensure_ascii=False, indent=2)
```

---

## Step 9: Record run.jsonl

```python
import json
import time

def append_run_log(
    asset_dir: Path,
    asset_id: str,
    action: str,
    status: str,
    reason: str,
    hash_content: str,
    artifact_plan: list,
    duration_ms: int,
    error: str = None
) -> None:
    """
    追加运行日志
    """
    log_path = asset_dir / "run.jsonl"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,  # ingest | update | skip | fail
        "asset_id": asset_id,
        "status": status,  # success | failed | skipped
        "reason": reason,
        "hash_content": hash_content,
        "artifact_plan": artifact_plan,
        "duration_ms": duration_ms,
        "error": error
    }

    # Append to file (create if not exists)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
```

---

## Step 10: Return Summary

```python
def format_success_summary(asset_dir: Path, plan: dict, status: str) -> str:
    """
    格式化执行摘要
    """
    lines = [
        "",
        "=" * 50,
        "✅ 微信文章归档成功",
        "=" * 50,
        f"📁 资产目录: {asset_dir}",
        f"📊 状态: {status}",
        ""
    ]

    # List generated files
    files = []
    for file in ["article.md", "note.md", "diagram.canvas", "table.base", "meta.json", "run.jsonl"]:
        file_path = asset_dir / file
        if file_path.exists():
            files.append(f"  ✓ {file}")

    lines.append("📄 生成的文件:")
    lines.extend(files)
    lines.append("")

    # Hints for optional artifacts
    if "canvas" in plan['artifact_plan']:
        lines.append("💡 提示: 已生成 diagram.canvas，可在 Obsidian 中打开查看")
    if "base" in plan['artifact_plan']:
        lines.append("💡 提示: 已生成 table.base，可在 Obsidian 中以表格形式查看")

    lines.append("=" * 50)
    lines.append("")

    return "\n".join(lines)
```

---

## Complete Execution Flow (Pseudo-code)

```python
def wechat_archiver_main(
    article_url: str,
    target_folder: str = None,
    force: bool = False,
    canvas: str = "auto",
    base: str = "auto"
) -> dict:
    """
    Main execution flow
    """
    start_time = time.time()
    asset_id = None
    action = "ingest"

    try:
        # Step 0: Validate input
        validate_wechat_url(article_url)
        target_folder = target_folder or "20-阅读笔记"

        # Step 1: Call wechat2md
        wechat_result = run_wechat2md(article_url)

        # Step 2: Generate asset metadata
        asset_meta = generate_asset_metadata(article_url, wechat_result['title'])
        asset_id = asset_meta['asset_id']

        # Step 3: Create asset directory
        cwd = Path.cwd()
        asset_dir = create_asset_directory(cwd, target_folder, asset_meta['slug'])

        # Step 4: Consolidate files
        consolidate_files(asset_dir, wechat_result['temp_md_path'], wechat_result['temp_images_dir'])

        # Step 5: Check idempotency
        hash_check = check_should_generate(asset_dir, force)
        hash_content = hash_check['hash_content']

        if not hash_check['should_generate']:
            # Skip note-creator
            action = "skip"
            duration_ms = int((time.time() - start_time) * 1000)
            append_run_log(
                asset_dir, asset_id, action, "skipped",
                hash_check['reason'], hash_content, [], duration_ms
            )
            return {
                "status": "skipped",
                "asset_dir": str(asset_dir),
                "reason": hash_check['reason']
            }

        # Step 6: Decide artifact plan
        plan = decide_plan(asset_dir / "article.md", canvas, base)

        # Step 7: Call note-creator
        note_creator_input = prepare_note_creator_input(asset_dir, asset_meta, plan)
        # Actual invocation via Skill(note-creator)
        invoke_note_creator(note_creator_input)

        # Step 8: Merge meta.json
        merge_meta_files(asset_dir, asset_meta, hash_content, plan, hash_check)

        # Step 9: Record run.jsonl
        duration_ms = int((time.time() - start_time) * 1000)
        append_run_log(
            asset_dir, asset_id, action, "success",
            hash_check['reason'], hash_content, plan['artifact_plan'], duration_ms
        )

        # Step 10: Return summary
        return {
            "status": "success",
            "asset_dir": str(asset_dir),
            "artifact_plan": plan['artifact_plan'],
            "reason": hash_check['reason']
        }

    except Exception as e:
        # Handle error
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"{type(e).__name__}: {e}"

        # Log error if asset_dir exists
        if asset_dir and asset_dir.exists():
            append_run_log(
                asset_dir, asset_id, action, "failed",
                "error", "", [], duration_ms, error_msg
            )

        return {
            "status": "failed",
            "error": error_msg
        }
```

---

## Summary

**Execution Order** (MUST follow):
1. ✅ Validate URL
2. ✅ Call wechat2md
3. ✅ Generate asset_id + slug
4. ✅ Create asset directory
5. ✅ Consolidate files (article.md + images/)
6. ✅ Calculate hash + check idempotency
7. ✅ Decide artifact plan (auto canvas/base)
8. ✅ Call note-creator (if needed)
9. ✅ Merge meta.json
10. ✅ Record run.jsonl
11. ✅ Return summary

**Critical Invariants**:
- All files in one directory
- Idempotency MUST be respected
- Original article MUST be preserved
- Logs MUST be appended (not overwritten)
