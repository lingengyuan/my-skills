#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wechat-archiver v2: Improved WeChat article archiver with better structure.

Key improvements:
1. Use wechat2md_v2 (markdownify-based) for better format preservation
2. Unified asset directory structure (no scattered files)
3. Better idempotency with asset_id (SHA1 of URL)
4. Automatic cleanup of temporary files
5. Proper base scoping with filters

Workflow:
1) Call wechat2md_v2 to fetch article (returns article.md + images/ + meta.json)
2) Read metadata and check idempotency
3) Decide artifact_plan (auto canvas/base)
4) Call note-creator to generate note.md + diagram.canvas + table.base
5) Merge meta.json
6) Cleanup temporary files
7) Return execution summary

Usage:
  python wechat_archiver_v2.py <url> [options]
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# ==================== Constants ====================
FOLDER_WHITELIST = [
    "00-Inbox",
    "10-项目",
    "20-阅读笔记",
    "30-方法论",
    "40-工具脚本",
    "50-运维排障",
    "60-数据与表",
    "90-归档",
]

CANVAS_KEYWORDS = [
    "流程", "步骤", "时序", "执行顺序", "调用链", "协作", "交互",
    "sequence", "flow", "workflow", "process", "steps", "pipeline",
    "架构", "结构", "组件", "模块", "依赖", "关系",
    "architecture", "structure", "components", "modules", "dependencies",
    "原理", "机制", "实现原理", "底层原理",
    "mechanism", "implementation", "internals",
    "架构图", "流程图", "时序图", "示意图",
    "diagram", "chart", "graph"
]

BASE_KEYWORDS = [
    "对比", "比较", "优缺点", "区别", "差异", "VS", "选择",
    "comparison", "compare", "vs", "difference", "pros and cons",
    "清单", "术语表", "词汇表", "名词解释", "常用工具", "最佳实践",
    "checklist", "glossary", "vocabulary", "inventory", "best practices"
]


# ==================== Utility Functions ====================

def sanitize_title(title: str, max_len: int = 60) -> str:
    """Clean title to create valid filename."""
    illegal_chars = re.compile(r'[\\/:*?"<>|]+')
    title = illegal_chars.sub('-', title)
    title = re.sub(r'\s+', ' ', title).strip()

    if len(title) > max_len:
        title = title[:max_len].rstrip()

    return title or "untitled"


def generate_slug(title: str, asset_id: str) -> str:
    """Generate slug from title and asset_id.

    No date prefix - using title only for stability.
    """
    title_slug = sanitize_title(title, max_len=60)
    asset_id_short = asset_id[:6]

    # Use title + asset_id short for uniqueness
    return f"{title_slug}-{asset_id_short}"


def calculate_content_hash(content: str) -> str:
    """Calculate SHA256 hash of content."""
    normalized = re.sub(r'\s+', ' ', content).strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def check_idempotency(asset_dir: Path, hash_content: str, force: bool = False) -> Dict:
    """Check if regeneration is needed based on hash."""
    meta_path = asset_dir / "meta.json"

    if not meta_path.exists():
        return {"should_generate": True, "reason": "first_run"}

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    if force:
        return {"should_generate": True, "reason": "forced"}

    historical_hash = meta.get("content_hash") or meta.get("hash_content")
    if historical_hash == hash_content:
        return {"should_generate": False, "reason": "content_unchanged"}
    else:
        return {
            "should_generate": True,
            "reason": "content_changed",
            "old_hash": historical_hash,
            "new_hash": hash_content
        }


def decide_artifact_plan(content: str, canvas: str, base: str) -> Dict:
    """Decide which artifacts to generate based on content."""
    artifact_plan = ["md"]

    # Canvas decision
    if canvas == "on":
        artifact_plan.append("canvas")
    elif canvas == "auto":
        canvas_match = any(kw in content for kw in CANVAS_KEYWORDS)
        if canvas_match:
            artifact_plan.append("canvas")

    # Base decision
    if base == "on":
        artifact_plan.append("base")
    elif base == "auto":
        base_match = any(kw in content for kw in BASE_KEYWORDS)
        table_count = content.count("| --- ")

        # Check for structured lists
        list_pattern = r'## .+\n(?:- .+\n){3,}'
        structured_lists = len(re.findall(list_pattern, content))

        if base_match or table_count >= 3 or structured_lists >= 2:
            artifact_plan.append("base")

    # Determine diagram_type and base_mode
    diagram_type = None
    base_mode = None

    if "canvas" in artifact_plan:
        if any(kw in content for kw in ["时序", "sequence", "调用链", "交互"]):
            diagram_type = "sequence"
        elif any(kw in content for kw in ["流程", "flow", "steps", "步骤"]):
            diagram_type = "flowchart"
        elif any(kw in content for kw in ["架构", "architecture", "组件", "模块"]):
            diagram_type = "architecture"
        else:
            diagram_type = "artifact"

    if "base" in artifact_plan:
        if any(kw in content for kw in ["对比", "比较", "VS", "comparison"]):
            base_mode = "comparison"
        else:
            base_mode = "generic"

    return {
        "artifact_plan": artifact_plan,
        "diagram_type": diagram_type,
        "base_mode": base_mode
    }


# ==================== Main Workflow ====================

def run_wechat2md_v2(url: str, slug: str, target_folder: str, cwd: Path) -> Dict:
    """Call wechat2md_v2 to fetch article.

    Returns dict with:
        - success: bool
        - article_md_path: Path
        - images_dir: Path
        - asset_id: str
        - content_hash: str
        - images_count: int
        - meta: dict (metadata from wechat2md_v2)
    """
    skill_dir = cwd / ".claude" / "skills" / "wechat2md"
    script = skill_dir / "tools" / "wechat2md_v2.py"

    if not script.exists():
        return {
            "success": False,
            "error": f"wechat2md_v2.py not found at {script}"
        }

    cmd = [
        sys.executable,
        str(script),
        url,
        "--slug", slug,
        "--target-folder", target_folder
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=cwd
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Unknown error"
            return {
                "success": False,
                "error": f"wechat2md_v2 failed: {error_msg}"
            }

        # Parse output
        output_vars = {}
        for line in result.stdout.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                output_vars[key] = value

        article_md_path = Path(output_vars.get('ARTICLE_MD', ''))
        images_dir = Path(output_vars.get('IMAGES_DIR', ''))
        asset_id = output_vars.get('ASSET_ID', '')
        content_hash = output_vars.get('HASH', '')
        images_count = int(output_vars.get('IMAGES_COUNT', 0))

        # Read meta.json
        meta_path = article_md_path.parent / "meta.json"
        meta = {}
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

        return {
            "success": True,
            "article_md_path": article_md_path,
            "images_dir": images_dir,
            "asset_id": asset_id,
            "content_hash": content_hash,
            "images_count": images_count,
            "meta": meta
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to run wechat2md_v2: {e}"
        }


def prepare_note_creator_input(
    article_md_path: Path,
    title: str,
    folder: str,
    artifact_plan: List[str],
    diagram_type: Optional[str],
    base_mode: Optional[str]
) -> str:
    """Prepare user_prompt for note-creator."""

    # Read article content for context
    with open(article_md_path, 'r', encoding='utf-8') as f:
        article_content = f.read()

    # Extract first paragraph for summary
    lines = article_content.split('\n')
    summary_lines = []
    for line in lines[10:50]:  # Skip header, get first paragraph
        if line.strip() and not line.startswith('#') and not line.startswith('>'):
            summary_lines.append(line)
        if len(summary_lines) >= 3:
            break

    summary = ' '.join(summary_lines).strip()[:200]

    prompt = f"""Create a structured note based on this WeChat article.

Title: {title}
Summary: {summary}

The original article is at: {article_md_path}

Generate:
- A comprehensive note.md summarizing key insights
- diagram.canvas ({diagram_type}) if applicable
- table.base ({base_mode}) if applicable
"""

    return prompt


def call_note_creator(
    user_prompt: str,
    context_files: List[Path],
    cwd: Path
) -> Dict:
    """Call note-creator skill.

    For now, this is a placeholder - the actual invocation is done by Claude.
    When using the skill through Claude, it will handle this step.
    """
    # This is handled by Claude's skill system
    # We just return the prepared information
    return {
        "success": True,
        "user_prompt": user_prompt,
        "context_files": context_files
    }


def merge_meta(
    asset_dir: Path,
    wechat2md_meta: Dict,
    artifact_plan: List[str],
    diagram_type: Optional[str],
    base_mode: Optional[str]
) -> None:
    """Merge wechat2md metadata with note-creator metadata."""

    meta_path = asset_dir / "meta.json"

    # Read existing meta if note-creator already ran
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            existing_meta = json.load(f)
    else:
        existing_meta = {}

    # Merge metadata (wechat2md + note-creator)
    merged_meta = {
        **wechat2md_meta,
        **existing_meta,
        "artifact_plan": artifact_plan,
        "diagram_type": diagram_type,
        "base_mode": base_mode,
        "last_run_at": datetime.now().isoformat(),
    }

    # Write merged meta
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(merged_meta, f, ensure_ascii=False, indent=2)


def cleanup_temp_files(asset_dir: Path) -> None:
    """Clean up temporary files."""
    # wechat2md_v2 already handles this
    # But we can add additional cleanup if needed
    pass


# ==================== Main Entry Point ====================

def main():
    parser = argparse.ArgumentParser(
        description="Archive WeChat articles with automatic note generation (v2)"
    )
    parser.add_argument("url", help="WeChat article URL")
    parser.add_argument("--target-folder", default="20-阅读笔记", help="Target folder")
    parser.add_argument("--force", action="store_true", help="Force regeneration")
    parser.add_argument("--canvas", choices=["on", "off", "auto"], default="auto")
    parser.add_argument("--base", choices=["on", "off", "auto"], default="auto")

    args = parser.parse_args()

    url = args.url.strip()
    if not url:
        print("ERROR: URL is required", file=sys.stderr)
        return 2

    # Validate URL
    if "mp.weixin.qq.com" not in url:
        print("ERROR: URL must be from mp.weixin.qq.com", file=sys.stderr)
        return 2

    cwd = Path.cwd()

    try:
        # Step 1: Fetch article with wechat2md_v2
        print("=" * 60)
        print("Step 1: Fetching article...")
        print("=" * 60)

        # We don't have title yet, use a temporary placeholder
        # wechat2md_v2 will generate proper slug from title
        temp_slug = "temp_article"

        fetch_result = run_wechat2md_v2(
            url=url,
            slug=temp_slug,
            target_folder=args.target_folder,
            cwd=cwd
        )

        if not fetch_result["success"]:
            print(f"ERROR: {fetch_result['error']}", file=sys.stderr)
            return 1

        article_md_path = fetch_result["article_md_path"]
        images_dir = fetch_result["images_dir"]
        asset_id = fetch_result["asset_id"]
        content_hash = fetch_result["content_hash"]
        images_count = fetch_result["images_count"]
        wechat2md_meta = fetch_result["meta"]

        print(f"✓ Article fetched: {article_md_path}")
        print(f"✓ Images: {images_count}")
        print(f"✓ Asset ID: {asset_id}")

        # Step 2: Check idempotency
        print("\n" + "=" * 60)
        print("Step 2: Checking idempotency...")
        print("=" * 60)

        asset_dir = article_md_path.parent
        idempotency = check_idempotency(asset_dir, content_hash, args.force)

        if not idempotency["should_generate"]:
            print(f"✓ Content unchanged ({idempotency['reason']})")
            print("✓ Skipping note generation")
            return 0

        print(f"✓ Need to generate note ({idempotency['reason']})")

        # Step 3: Decide artifact plan
        print("\n" + "=" * 60)
        print("Step 3: Deciding artifact plan...")
        print("=" * 60)

        with open(article_md_path, 'r', encoding='utf-8') as f:
            article_content = f.read()

        decision = decide_artifact_plan(article_content, args.canvas, args.base)
        artifact_plan = decision["artifact_plan"]
        diagram_type = decision["diagram_type"]
        base_mode = decision["base_mode"]

        print(f"✓ Artifact plan: {', '.join(artifact_plan)}")
        if "canvas" in artifact_plan:
            print(f"  - Diagram type: {diagram_type}")
        if "base" in artifact_plan:
            print(f"  - Base mode: {base_mode}")

        # Step 4: Prepare input for note-creator
        print("\n" + "=" * 60)
        print("Step 4: Preparing note generation...")
        print("=" * 60)

        title = wechat2md_meta.get("title", "Unknown Title")
        user_prompt = prepare_note_creator_input(
            article_md_path,
            title,
            args.target_folder,
            artifact_plan,
            diagram_type,
            base_mode
        )

        print(f"✓ User prompt prepared:")
        print(f"  {user_prompt[:100]}...")

        # Step 5: Merge metadata
        print("\n" + "=" * 60)
        print("Step 5: Merging metadata...")
        print("=" * 60)

        merge_meta(
            asset_dir,
            wechat2md_meta,
            artifact_plan,
            diagram_type,
            base_mode
        )

        print(f"✓ Metadata merged: {asset_dir / 'meta.json'}")

        # Step 6: Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Asset directory: {asset_dir}")
        print(f"Article:        {article_md_path}")
        print(f"Images:         {images_dir} ({images_count} images)")
        print(f"Asset ID:       {asset_id}")
        print(f"Content hash:   {content_hash}")
        print(f"\nNext step: Invoke note-creator skill")
        print(f"  Context files: {article_md_path}")
        print(f"  User prompt:   {user_prompt[:100]}...")

        return 0

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
