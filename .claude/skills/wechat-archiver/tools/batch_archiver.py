#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""batch_archiver: Batch process WeChat article URLs from inbox file.

Features:
- Extract WeChat URLs from markdown files (inbox.md)
- Support multiple link formats (markdown links, plain URLs, task lists)
- Deduplicate URLs
- Resume from interruption (checkpoint support)
- Mark processed URLs in source file

Usage:
  python batch_archiver.py --inbox inbox.md [options]
  python batch_archiver.py --inbox inbox.md --dry-run  # Preview only
"""

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ==================== Constants ====================
WECHAT_URL_PATTERN = re.compile(
    r'https?://mp\.weixin\.qq\.com/s[/?][^\s\)\]"\'<>]+',
    re.IGNORECASE
)

# Patterns for different link formats
MARKDOWN_LINK_PATTERN = re.compile(
    r'\[([^\]]*)\]\((https?://mp\.weixin\.qq\.com/s[/?][^\)]+)\)',
    re.IGNORECASE
)

TASK_LIST_PATTERN = re.compile(
    r'^(\s*-\s*\[)([ xX])(\]\s*)(.*?)$',
    re.MULTILINE
)


# ==================== URL Extraction ====================

def extract_wechat_urls(content: str) -> List[Dict]:
    """Extract all WeChat URLs from content with their context.

    Returns list of dicts with:
    - url: the WeChat URL
    - line_num: line number in file (1-indexed)
    - format: 'markdown_link' | 'plain_url' | 'task_unchecked' | 'task_checked'
    - title: optional title from markdown link
    - original_line: the full original line
    """
    results = []
    seen_urls = set()
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Check for markdown links first
        md_matches = MARKDOWN_LINK_PATTERN.findall(line)
        for title, url in md_matches:
            normalized = normalize_url(url)
            if normalized not in seen_urls:
                seen_urls.add(normalized)

                # Determine if it's in a task list
                task_match = TASK_LIST_PATTERN.match(line)
                if task_match:
                    is_checked = task_match.group(2).lower() == 'x'
                    format_type = 'task_checked' if is_checked else 'task_unchecked'
                else:
                    format_type = 'markdown_link'

                results.append({
                    'url': url.strip(),
                    'line_num': line_num,
                    'format': format_type,
                    'title': title.strip() if title else None,
                    'original_line': line,
                    'normalized_url': normalized
                })
                continue

        # Check for plain URLs (not already captured as markdown links)
        plain_matches = WECHAT_URL_PATTERN.findall(line)
        for url in plain_matches:
            # Skip if already found in markdown link
            normalized = normalize_url(url)
            if normalized in seen_urls:
                continue
            seen_urls.add(normalized)

            # Check if in task list
            task_match = TASK_LIST_PATTERN.match(line)
            if task_match:
                is_checked = task_match.group(2).lower() == 'x'
                format_type = 'task_checked' if is_checked else 'task_unchecked'
            else:
                format_type = 'plain_url'

            results.append({
                'url': url.strip(),
                'line_num': line_num,
                'format': format_type,
                'title': None,
                'original_line': line,
                'normalized_url': normalized
            })

    return results


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication."""
    parsed = urlparse(url)
    # Remove tracking parameters
    return f"{parsed.netloc}{parsed.path}".rstrip("/").lower()


# ==================== Checkpoint Management ====================

def get_checkpoint_path(inbox_path: Path) -> Path:
    """Get checkpoint file path for given inbox file."""
    return inbox_path.parent / f".batch_checkpoint_{inbox_path.stem}.json"


def load_checkpoint(checkpoint_path: Path) -> Dict:
    """Load checkpoint data."""
    if not checkpoint_path.exists():
        return {
            'processed_urls': {},  # normalized_url -> {status, timestamp, asset_dir}
            'last_run': None,
            'version': '1.0'
        }

    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_checkpoint(checkpoint_path: Path, data: Dict) -> None:
    """Save checkpoint data."""
    data['last_run'] = datetime.now().isoformat()
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==================== Source File Update ====================

def mark_url_as_processed(content: str, url_info: Dict, asset_dir: str) -> str:
    """Mark a URL as processed in the source content.

    For task lists: change [ ] to [x]
    For other formats: append (archived) marker
    """
    lines = content.split('\n')
    line_idx = url_info['line_num'] - 1

    if line_idx >= len(lines):
        return content

    original_line = lines[line_idx]

    if url_info['format'] == 'task_unchecked':
        # Change [ ] to [x]
        new_line = TASK_LIST_PATTERN.sub(
            lambda m: f"{m.group(1)}x{m.group(3)}{m.group(4)}",
            original_line
        )
        lines[line_idx] = new_line
    elif url_info['format'] in ('markdown_link', 'plain_url'):
        # Append archived marker if not already present
        if '(archived)' not in original_line and '(已归档)' not in original_line:
            lines[line_idx] = f"{original_line} (已归档)"

    return '\n'.join(lines)


# ==================== Archive Execution ====================

def run_single_archive(url: str, cwd: Path, folder: str, force: bool = False) -> Dict:
    """Run wechat_archiver.py for a single URL."""
    script_path = cwd / ".claude" / "skills" / "wechat-archiver" / "tools" / "wechat_archiver.py"

    cmd = ["python", str(script_path), url, "--folder", folder]
    if force:
        cmd.append("--force")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        cwd=str(cwd)
    )

    # Parse output to find asset directory
    asset_dir = None
    if result.returncode == 0:
        # Look for "Directory: " in output
        for line in result.stdout.split('\n'):
            if 'Directory:' in line:
                asset_dir = line.split('Directory:')[-1].strip()
                break

    return {
        'success': result.returncode == 0,
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'asset_dir': asset_dir
    }


# ==================== Main Workflow ====================

def batch_archive(
    inbox_path: Path,
    cwd: Path,
    folder: str = "20-阅读笔记",
    force: bool = False,
    mark_done: bool = True,
    dry_run: bool = False,
    skip_checked: bool = True
) -> Dict:
    """Process all WeChat URLs from inbox file.

    Args:
        inbox_path: Path to inbox.md file
        cwd: Working directory
        folder: Target folder for archives
        force: Force regeneration
        mark_done: Mark processed URLs in source file
        dry_run: Preview only, don't actually process
        skip_checked: Skip already checked task items

    Returns:
        Summary dict with results
    """
    # Read inbox file
    if not inbox_path.exists():
        raise FileNotFoundError(f"Inbox file not found: {inbox_path}")

    with open(inbox_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract URLs
    url_infos = extract_wechat_urls(content)

    if not url_infos:
        return {
            'total': 0,
            'processed': 0,
            'skipped': 0,
            'failed': 0,
            'results': [],
            'message': 'No WeChat URLs found in inbox file'
        }

    # Load checkpoint
    checkpoint_path = get_checkpoint_path(inbox_path)
    checkpoint = load_checkpoint(checkpoint_path)

    # Filter URLs to process
    urls_to_process = []
    for info in url_infos:
        # Skip already checked items if requested
        if skip_checked and info['format'] == 'task_checked':
            continue

        # Skip already processed (from checkpoint)
        if info['normalized_url'] in checkpoint['processed_urls']:
            prev = checkpoint['processed_urls'][info['normalized_url']]
            if prev.get('status') == 'success' and not force:
                continue

        urls_to_process.append(info)

    # Dry run - just show what would be processed
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN - Would process {len(urls_to_process)} URLs:")
        print(f"{'='*60}")
        for i, info in enumerate(urls_to_process, 1):
            title = info['title'] or '(no title)'
            print(f"  {i}. [{info['format']}] {title}")
            print(f"     {info['url'][:60]}...")
        print(f"{'='*60}")

        return {
            'total': len(url_infos),
            'to_process': len(urls_to_process),
            'dry_run': True,
            'urls': urls_to_process
        }

    # Process URLs
    results = []
    processed_count = 0
    skipped_count = 0
    failed_count = 0

    total = len(urls_to_process)
    print(f"\n{'='*60}")
    print(f"Batch Archive: Processing {total} URLs")
    print(f"{'='*60}\n")

    for i, info in enumerate(urls_to_process, 1):
        url = info['url']
        title = info['title'] or '(no title)'

        print(f"[{i}/{total}] Processing: {title[:40]}...")
        print(f"         URL: {url[:50]}...")

        try:
            result = run_single_archive(url, cwd, folder, force)

            if result['success']:
                processed_count += 1
                status = 'success'
                print(f"         Status: SUCCESS")
                if result['asset_dir']:
                    print(f"         Output: {result['asset_dir']}")

                # Update checkpoint
                checkpoint['processed_urls'][info['normalized_url']] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'asset_dir': result['asset_dir'],
                    'title': title
                }

                # Mark as done in source file
                if mark_done:
                    content = mark_url_as_processed(content, info, result['asset_dir'])
            else:
                failed_count += 1
                status = 'failed'
                print(f"         Status: FAILED")
                print(f"         Error: {result['stderr'][:100]}...")

                checkpoint['processed_urls'][info['normalized_url']] = {
                    'status': 'failed',
                    'timestamp': datetime.now().isoformat(),
                    'error': result['stderr'][:500]
                }

            results.append({
                'url': url,
                'title': title,
                'status': status,
                'asset_dir': result.get('asset_dir')
            })

        except Exception as e:
            failed_count += 1
            print(f"         Status: ERROR - {e}")

            checkpoint['processed_urls'][info['normalized_url']] = {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

            results.append({
                'url': url,
                'title': title,
                'status': 'error',
                'error': str(e)
            })

        # Save checkpoint after each URL
        save_checkpoint(checkpoint_path, checkpoint)
        print()

    # Save updated content if mark_done
    if mark_done and processed_count > 0:
        with open(inbox_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[INFO] Updated {inbox_path} with {processed_count} marked items")

    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Archive Complete")
    print(f"{'='*60}")
    print(f"  Total URLs found:    {len(url_infos)}")
    print(f"  Processed:           {processed_count}")
    print(f"  Failed:              {failed_count}")
    print(f"  Already done:        {len(url_infos) - total}")
    print(f"{'='*60}")

    return {
        'total': len(url_infos),
        'processed': processed_count,
        'skipped': skipped_count,
        'failed': failed_count,
        'results': results
    }


def main():
    parser = argparse.ArgumentParser(
        description="Batch process WeChat article URLs from inbox file"
    )
    parser.add_argument(
        "--inbox",
        required=True,
        help="Path to inbox.md file containing WeChat URLs"
    )
    parser.add_argument(
        "--folder",
        default="20-阅读笔记",
        help="Target folder for archives (default: 20-阅读笔记)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of already processed URLs"
    )
    parser.add_argument(
        "--no-mark",
        action="store_true",
        help="Don't mark processed URLs in source file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, don't actually process"
    )
    parser.add_argument(
        "--include-checked",
        action="store_true",
        help="Include already checked task items (default: skip)"
    )
    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        help="Reset checkpoint file and start fresh"
    )

    args = parser.parse_args()

    inbox_path = Path(args.inbox).resolve()
    cwd = Path.cwd()

    # Reset checkpoint if requested
    if args.reset_checkpoint:
        checkpoint_path = get_checkpoint_path(inbox_path)
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            print(f"[INFO] Checkpoint reset: {checkpoint_path}")

    try:
        result = batch_archive(
            inbox_path=inbox_path,
            cwd=cwd,
            folder=args.folder,
            force=args.force,
            mark_done=not args.no_mark,
            dry_run=args.dry_run,
            skip_checked=not args.include_checked
        )

        return 0 if result.get('failed', 0) == 0 else 1

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
