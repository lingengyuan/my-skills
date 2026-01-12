#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wechat-archiver: WeChat article archiver with automatic note generation.

Orchestration workflow:
1) Call wechat2md to fetch article
2) Generate asset_id and slug
3) Create unified asset directory
4) Consolidate files (article.md + images/)
5) Check idempotency (hash_content)
6) Decide artifact_plan (auto canvas/base)
7) Prepare input for note-creator
8) Return execution summary

Usage:
  python wechat_archiver.py <url> [options]
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
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


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

def normalize_url(url: str) -> str:
    """Normalize URL by removing tracking parameters."""
    parsed = urlparse(url)
    tracking_params = {"chksm", "vid", "uin", "sid", "from"}

    # Simply return netloc + path for wechat articles
    return f"{parsed.netloc}{parsed.path}".rstrip("/")


def sanitize_title(title: str, max_len: int = 50) -> str:
    """Clean title to create valid filename."""
    illegal_chars = re.compile(r'[\\/:*?"<>|]+')
    title = illegal_chars.sub("-", title)
    title = re.sub(r'\s+', ' ', title).strip()

    # Remove special characters (keep Chinese, alphanumeric, -, _)
    title = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title)

    if len(title) > max_len:
        title = title[:max_len].rstrip()

    return title or "untitled"


def generate_asset_id(url: str) -> str:
    """Generate asset ID from URL."""
    normalized = normalize_url(url)
    return hashlib.sha1(normalized.encode()).hexdigest()


def generate_slug(title: str, asset_id: str, date: datetime = None) -> str:
    """Generate unique slug for asset directory."""
    if date is None:
        date = datetime.now()

    date_prefix = date.strftime("%Y%m%d")
    title_slug = sanitize_title(title, max_len=50)
    asset_id_short = asset_id[:6]

    return f"{date_prefix}-{title_slug}-{asset_id_short}"


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

    historical_hash = meta.get("hash_content")
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

def run_wechat2md(url: str, cwd: Path) -> Dict:
    """Call wechat2md to fetch article."""
    skill_dir = cwd / ".claude" / "skills" / "wechat2md"
    script = skill_dir / "tools" / "wechat2md.py"

    # Get outputs directory state before
    outputs_dir = cwd / "outputs"
    before_dirs = set([d for d in outputs_dir.iterdir() if d.is_dir()]) if outputs_dir.exists() else set()

    # Run wechat2md
    result = subprocess.run(
        ["python", str(script), url],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        cwd=str(cwd)
    )

    if result.returncode != 0:
        raise RuntimeError(f"wechat2md failed: {result.stderr}")

    # Find the newly created directory
    after_dirs = set([d for d in outputs_dir.iterdir() if d.is_dir()]) if outputs_dir.exists() else set()
    new_dirs = after_dirs - before_dirs

    if not new_dirs:
        # Fallback: find most recently modified directory
        all_dirs = [d for d in outputs_dir.iterdir() if d.is_dir()] if outputs_dir.exists() else []
        if not all_dirs:
            raise RuntimeError("No output directory found")
        new_dir = max(all_dirs, key=lambda p: p.stat().st_mtime)
    else:
        new_dir = list(new_dirs)[0]

    # Find the .md file in the new directory
    md_files = list(new_dir.glob("*.md"))
    if not md_files:
        raise RuntimeError(f"No .md file found in {new_dir}")

    temp_md_path = md_files[0]
    title = temp_md_path.stem
    temp_images_dir = cwd / "images" / title

    return {
        "title": title,
        "temp_md_path": temp_md_path,
        "temp_images_dir": temp_images_dir
    }


def create_asset_directory(cwd: Path, target_folder: str, slug: str) -> Path:
    """Create unified asset directory."""
    asset_dir = cwd / "outputs" / target_folder / slug
    asset_dir.mkdir(parents=True, exist_ok=True)
    return asset_dir


def consolidate_files(asset_dir: Path, temp_md_path: Path, temp_images_dir: Path) -> None:
    """Consolidate files into asset directory."""
    # Copy article.md
    shutil.copy2(temp_md_path, asset_dir / "article.md")

    # Copy images directory
    if temp_images_dir.exists():
        shutil.copytree(temp_images_dir, asset_dir / "images", dirs_exist_ok=True)

    # Cleanup temp files
    temp_output_dir = temp_md_path.parent
    if temp_output_dir != asset_dir:
        shutil.rmtree(temp_output_dir, ignore_errors=True)

    if temp_images_dir != asset_dir / "images":
        shutil.rmtree(temp_images_dir, ignore_errors=True)


def create_meta_json(asset_dir: Path, metadata: Dict, hash_content: str, plan: Dict) -> None:
    """Create unified meta.json."""
    meta_path = asset_dir / "meta.json"

    # Check if meta exists
    existing_meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            existing_meta = json.load(f)

    unified_meta = {
        "asset_id": metadata["asset_id"],
        "url": metadata["url"],
        "title": metadata["title"],
        "slug": metadata["slug"],
        "hash_content": hash_content,
        "hash_algorithm": "sha256",
        "ingested_at": datetime.now().isoformat(),
        "published_at": existing_meta.get("published_at"),
        "artifact_plan": plan["artifact_plan"],
        "category": existing_meta.get("category", "article"),
        "tags": existing_meta.get("tags", ["wechat", "reading"]),
        "properties": existing_meta.get("properties", {
            "created": datetime.now().strftime("%Y-%m-%d"),
            "modified": datetime.now().strftime("%Y-%m-%d"),
            "source": "wechat_article",
            "folder": metadata.get("folder", "20-阅读笔记")
        }),
        "last_run_at": datetime.now().isoformat(),
        "last_run_status": "success",
        "last_run_reason": "first_run",
        "run_count": existing_meta.get("run_count", 0) + 1,
        "meta_version": "1.0"
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(unified_meta, f, ensure_ascii=False, indent=2)


def append_run_log(asset_dir: Path, entry: Dict) -> None:
    """Append entry to run.jsonl."""
    log_path = asset_dir / "run.jsonl"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="WeChat article archiver")
    parser.add_argument("url", help="WeChat article URL")
    parser.add_argument("--folder", default="20-阅读笔记", help="Target folder")
    parser.add_argument("--force", action="store_true", help="Force regeneration")
    parser.add_argument("--canvas", choices=["auto", "on", "off"], default="auto", help="Canvas generation")
    parser.add_argument("--base", choices=["auto", "on", "off"], default="auto", help="Base generation")
    parser.add_argument("--simple-slug", action="store_true", help="Use simple slug without asset_id suffix (format: YYYYMMDD-title)")

    args = parser.parse_args()
    start_time = datetime.now()

    try:
        cwd = Path.cwd()

        # Step 1: Call wechat2md
        print(f"[1/7] Fetching article...")
        wechat_result = run_wechat2md(args.url, cwd)
        print(f"      Title: {wechat_result['title']}")

        # Step 2: Generate asset metadata
        print(f"[2/7] Generating asset metadata...")
        asset_id = generate_asset_id(args.url)

        # Generate slug (with or without asset_id suffix)
        if args.simple_slug:
            # Simple format: YYYYMMDD-title
            date_prefix = datetime.now().strftime("%Y%m%d")
            title_slug = sanitize_title(wechat_result['title'], max_len=50)
            slug = f"{date_prefix}-{title_slug}"
        else:
            # Default format: YYYYMMDD-title-asset_id[:6]
            slug = generate_slug(wechat_result['title'], asset_id)

        print(f"      Asset ID: {asset_id[:16]}...")
        print(f"      Slug: {slug}")
        if args.simple_slug:
            print(f"      [INFO] Using simple slug (no asset_id suffix)")

        # Step 3: Create asset directory
        print(f"[3/7] Creating asset directory...")
        asset_dir = create_asset_directory(cwd, args.folder, slug)
        print(f"      Directory: {asset_dir}")

        # Step 4: Consolidate files
        print(f"[4/7] Consolidating files...")
        consolidate_files(asset_dir, wechat_result['temp_md_path'], wechat_result['temp_images_dir'])
        print(f"      Copied: article.md")

        # Step 5: Check idempotency
        print(f"[5/7] Checking idempotency...")
        with open(asset_dir / "article.md", "r", encoding="utf-8") as f:
            article_content = f.read()
        hash_content = calculate_content_hash(article_content)
        print(f"      Content hash: {hash_content[:16]}...")

        idempotency = check_idempotency(asset_dir, hash_content, args.force)
        print(f"      Decision: {idempotency['reason']}")

        # Step 6: Decide artifact plan
        print(f"[6/7] Deciding artifact plan...")
        plan = decide_artifact_plan(article_content, args.canvas, args.base)
        print(f"      Plan: {plan['artifact_plan']}")
        if plan.get('diagram_type'):
            print(f"      Diagram type: {plan['diagram_type']}")
        if plan.get('base_mode'):
            print(f"      Base mode: {plan['base_mode']}")

        # Step 7: Create metadata
        print(f"[7/7] Creating metadata...")
        metadata = {
            "asset_id": asset_id,
            "url": args.url,
            "title": wechat_result['title'],
            "slug": slug,
            "folder": args.folder
        }
        create_meta_json(asset_dir, metadata, hash_content, plan)

        # Log run
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        run_log = {
            "timestamp": datetime.now().isoformat(),
            "action": "ingest",
            "asset_id": asset_id,
            "status": "success" if idempotency['should_generate'] else "skipped",
            "reason": idempotency['reason'],
            "hash_content": hash_content,
            "artifact_plan": plan['artifact_plan'],
            "duration_ms": duration_ms
        }
        append_run_log(asset_dir, run_log)

        # Output summary
        print()
        print("=" * 60)
        print(f"SUCCESS: WeChat article archived")
        print("=" * 60)
        print(f"Directory: {asset_dir}")
        print(f"Files generated:")
        print(f"  - article.md")
        print(f"  - meta.json")
        print(f"  - run.jsonl")
        if not idempotency['should_generate']:
            print(f"\n[INFO] Note generation skipped (content unchanged)")
        else:
            print(f"\n[INFO] Ready for note-creator integration")
            print(f"      Run: Skill(note-creator) with context from {asset_dir}")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
