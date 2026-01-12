#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wechat2md v2: Improved WeChat article to Markdown converter.

Key improvements over v1:
1. Use markdownify for better HTML->MD conversion (preserves formatting)
2. Use asset_id (SHA1 of URL) for unique identification
3. Output to single asset directory (no scattered files)
4. Clean temporary files automatically
5. Better structure preservation

Usage:
  python3 wechat2md_v2.py "https://mp.weixin.qq.com/s/xxxxxxxx" [--output-dir OUTPUT_DIR]

Output contract (relative to CWD):
  outputs/<target_folder>/<slug>/
    ├── article.md           # Original article Markdown
    ├── images/              # Article images (only if any)
    │   ├── 001.jpg
    │   └── ...
    └── meta.json            # Metadata (asset_id, url, title, etc.)

Where:
  - <slug> = sanitized article title (or custom with --slug)
  - asset_id = sha1(normalized_url) for deduplication
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from markdownify import markdownify as md

# User-Agent for WeChat
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9,en;q=0.8"


@dataclass
class ArticleMetadata:
    """Metadata for the article."""
    asset_id: str           # SHA1 hash of normalized URL
    url: str               # Original URL
    title: str             # Article title
    author: str            # Author/official account name
    publish_time: str      # Publish time
    ingested_at: str       # ISO timestamp of ingestion
    images_count: int      # Number of images
    has_images: bool       # Whether article has images
    content_hash: str      # SHA1 hash of article MD content


def normalize_url(url: str) -> str:
    """Normalize URL for consistent asset_id generation."""
    # Remove common tracking parameters
    parsed = urllib.parse.urlparse(url.strip())
    # WeChat articles don't need query params for uniqueness
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def compute_asset_id(url: str) -> str:
    """Compute asset_id as SHA1 of normalized URL."""
    normalized = normalize_url(url)
    return hashlib.sha1(normalized.encode('utf-8')).hexdigest()


def fetch_html(url: str, timeout_s: int = 30) -> str:
    """Fetch article HTML using curl (better compatibility)."""
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError("curl not found in PATH; please install curl")

    cmd = [
        curl,
        "-L",
        "--compressed",
        "--max-time", str(timeout_s),
        "-H", f"User-Agent: {UA}",
        "-H", f"Accept-Language: {ACCEPT_LANGUAGE}",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        url,
    ]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )

    if proc.returncode != 0:
        raise RuntimeError(f"curl failed ({proc.returncode}): {proc.stderr.strip()}")
    if not proc.stdout.strip():
        raise RuntimeError("empty HTML fetched")
    return proc.stdout


def extract_title(soup: BeautifulSoup) -> str:
    """Extract article title."""
    # Try meta tags first
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    tw_title = soup.find("meta", attrs={"name": "twitter:title"})
    if tw_title and tw_title.get("content"):
        return tw_title["content"].strip()

    # Try <title> tag
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    # Fallback to h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)

    return "wechat_article"


def extract_author(soup: BeautifulSoup) -> str:
    """Extract author/official account name."""
    author_tag = soup.find("a", id="js_name")
    if author_tag:
        return author_tag.get_text().strip()

    # Try other common selectors
    for selector in ['#js_author_name', '.rich_media_meta_text']:
        elem = soup.select_one(selector)
        if elem:
            return elem.get_text().strip()

    return "Unknown"


def extract_publish_time(soup: BeautifulSoup) -> str:
    """Extract publish time."""
    time_tag = soup.find("em", id="publish_time")
    if time_tag:
        return time_tag.get_text().strip()

    # Try other selectors
    elem = soup.select_one('.rich_media_meta.rich_media_meta_text')
    if elem:
        return elem.get_text().strip()

    return ""


def sanitize_filename(name: str, max_len: int = 80) -> str:
    """Sanitize filename for filesystem."""
    # Remove illegal characters
    illegal = re.compile(r'[\\/:*?"<>|]')
    name = illegal.sub('-', name)
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    # Remove leading/trailing dots
    name = name.strip('.')
    # Limit length
    if len(name) > max_len:
        name = name[:max_len].rstrip()
    return name or "article"


def extract_js_content(soup: BeautifulSoup) -> BeautifulSoup:
    """Extract #js_content div."""
    content = soup.find(id="js_content")
    if not content:
        raise RuntimeError("Cannot find #js_content in article")
    return content


def download_images(
    content_div: BeautifulSoup,
    article_url: str,
    images_dir: Path,
) -> Tuple[int, str]:
    """Download images and update HTML.

    Returns:
        (images_count, image_prefix) - Number of images downloaded and prefix for MD links
    """
    images = content_div.find_all("img")
    if not images:
        return 0, ""

    images_dir.mkdir(parents=True, exist_ok=True)
    image_prefix = "images/"  # v2: unified dir structure, images relative to article.md

    for idx, img in enumerate(images, 1):
        # Get image URL (WeChat uses data-src)
        img_url = img.get('data-src') or img.get('src', '')
        if not img_url or img_url.startswith('data:'):
            continue

        # Normalize protocol-less URLs
        if img_url.startswith('//'):
            img_url = 'https:' + img_url

        # Determine extension
        ext = guess_extension(img_url)
        filename = f"{idx:03d}.{ext}"
        filepath = images_dir / filename

        # Download image
        try:
            download_image(img_url, filepath, article_url)
            # Update img tag
            img['src'] = f"{image_prefix}{filename}"
            # Remove data-src to avoid confusion
            if img.get('data-src'):
                del img['data-src']
            # Add alt if missing
            if not img.get('alt'):
                img['alt'] = f"Image {idx}"
        except Exception as e:
            print(f"Warning: Failed to download image {idx}: {e}", file=sys.stderr)
            # Keep original URL as fallback
            img['src'] = img_url

    return len(images), image_prefix


def guess_extension(url: str) -> str:
    """Guess image extension from URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        basename = os.path.basename(parsed.path)
        if '.' in basename:
            ext = basename.rsplit('.', 1)[-1].lower()
            if ext in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}:
                return 'jpg' if ext == 'jpeg' else ext
    except Exception:
        pass
    return 'jpg'  # Default


def download_image(url: str, filepath: Path, referer: str, timeout: int = 30) -> None:
    """Download single image."""
    headers = {
        "User-Agent": UA,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": ACCEPT_LANGUAGE,
        "Referer": referer,
    }

    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()

    # Write to file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(data)


def clean_content(content_div: BeautifulSoup) -> BeautifulSoup:
    """Remove unwanted elements."""
    # Remove scripts and styles
    for tag in content_div.find_all(['script', 'style', 'iframe', 'noscript']):
        tag.decompose()
    return content_div


def html_to_markdown_improved(
    soup: BeautifulSoup,
    title: str,
    author: str,
    publish_time: str,
) -> str:
    """Convert HTML to Markdown using markdownify.

    This is the key improvement over v1 - markdownify does a much better job
    preserving WeChat article structure and formatting.
    """
    # Convert using markdownify with optimal settings for WeChat
    markdown_content = md(
        str(soup),
        heading_style="ATX",        # Use # for headings
        bullets="-",                # Use - for lists
        strip=['script', 'style'],  # Strip these tags
        convert_as_inline=False     # Preserve block structure
    )

    # Clean up excessive blank lines
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

    # Add article header
    header = f"""# {title}

> **作者**: {author}
> **发布时间**: {publish_time}
> **来源**: [微信公众号文章]({soup.get('url', '')})

---

"""

    full_content = header + markdown_content.strip() + '\n'
    return full_content


def compute_content_hash(content: str) -> str:
    """Compute SHA1 hash of content."""
    return hashlib.sha1(content.encode('utf-8')).hexdigest()


def save_metadata(
    output_dir: Path,
    metadata: ArticleMetadata,
) -> None:
    """Save metadata to meta.json."""
    meta_path = output_dir / "meta.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert WeChat article to Markdown (improved v2)"
    )
    parser.add_argument("url", help="WeChat article URL (mp.weixin.qq.com)")
    parser.add_argument("--output-dir", default="outputs", help="Output directory (default: outputs)")
    parser.add_argument("--target-folder", default="20-阅读笔记", help="Target folder name (default: 20-阅读笔记)")
    parser.add_argument("--slug", help="Custom slug (default: auto from title)")

    args = parser.parse_args()

    url = args.url.strip()
    if not url:
        print("ERROR: empty URL", file=sys.stderr)
        return 2

    try:
        # Parse HTML
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        # Extract metadata
        raw_title = extract_title(soup)
        title = sanitize_filename(raw_title)
        author = extract_author(soup)
        publish_time = extract_publish_time(soup)

        # Compute asset_id
        asset_id = compute_asset_id(url)

        # Determine output paths
        slug = args.slug or title
        output_dir = Path(args.output_dir) / args.target_folder / slug
        article_path = output_dir / "article.md"
        images_dir = output_dir / "images"

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract and process content
        content_div = extract_js_content(soup)
        content_div = clean_content(content_div)

        # Download images
        images_count, image_prefix = download_images(
            content_div,
            url,
            images_dir,
        )

        # Convert to Markdown
        markdown_content = html_to_markdown_improved(
            content_div,
            title=raw_title,  # Use original title for display
            author=author,
            publish_time=publish_time,
        )

        # Save article.md
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Compute content hash
        content_hash = compute_content_hash(markdown_content)

        # Save metadata
        from datetime import datetime
        metadata = ArticleMetadata(
            asset_id=asset_id,
            url=url,
            title=raw_title,
            author=author,
            publish_time=publish_time,
            ingested_at=datetime.now().isoformat(),
            images_count=images_count,
            has_images=images_count > 0,
            content_hash=content_hash,
        )
        save_metadata(output_dir, metadata)

        # Clean up empty images directory
        if images_count == 0 and images_dir.exists():
            shutil.rmtree(images_dir)

        # Output paths (for script integration)
        print(f"ARTICLE_MD={article_path}")
        print(f"IMAGES_DIR={images_dir}")
        print(f"ASSET_ID={asset_id}")
        print(f"HASH={content_hash}")
        print(f"IMAGES_COUNT={images_count}")

        return 0

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
