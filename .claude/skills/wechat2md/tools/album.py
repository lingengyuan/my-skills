#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Album/collection download support for wechat2md.

Handles downloading WeChat "专题" (albums/collections) which contain multiple articles.
Detects album URLs, fetches article list via API, and downloads each article in order.

Album URL pattern:
  https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=...

Single article pattern:
  https://mp.weixin.qq.com/s/...
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .config import load_config, Wechat2mdConfig
    from .path_builder import sanitize_title
except ImportError:
    from config import load_config, Wechat2mdConfig
    from path_builder import sanitize_title


# User agent for requests
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9,en;q=0.8"


@dataclass
class AlbumInfo:
    """Information about a WeChat album/collection."""
    biz: str
    album_id: str
    name: str = ""
    article_count: int = 0


@dataclass
class ArticleInfo:
    """Information about a single article in an album."""
    title: str
    url: str
    msgid: str
    create_time: int = 0


@dataclass
class DownloadResult:
    """Result of downloading a single article."""
    article: ArticleInfo
    success: bool
    output_dir: Optional[Path] = None
    error: Optional[str] = None


@dataclass
class AlbumResult:
    """Result of downloading an entire album."""
    album: AlbumInfo
    output_dir: Path
    index_file: Optional[Path] = None
    results: List[DownloadResult] = field(default_factory=list)
    total: int = 0
    succeeded: int = 0
    failed: int = 0


def is_album_url(url: str) -> bool:
    """Check if a URL is a WeChat album URL.

    Album URLs match:
      https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=...

    Single article URLs match:
      https://mp.weixin.qq.com/s/...

    Args:
        url: URL to check

    Returns:
        True if the URL is an album URL, False otherwise.
    """
    if not url:
        return False

    parsed = urllib.parse.urlparse(url)

    # Must be WeChat domain
    if parsed.netloc not in ("mp.weixin.qq.com", "weixin.qq.com"):
        return False

    # Album path is /mp/appmsgalbum
    if "/mp/appmsgalbum" in parsed.path:
        return True

    return False


def parse_album_url(url: str) -> Optional[AlbumInfo]:
    """Parse an album URL to extract biz and album_id.

    Args:
        url: Album URL

    Returns:
        AlbumInfo with biz and album_id, or None if parsing fails.
    """
    if not is_album_url(url):
        return None

    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)

    biz = params.get("__biz", [None])[0]
    album_id = params.get("album_id", [None])[0]

    if not biz or not album_id:
        return None

    return AlbumInfo(biz=biz, album_id=album_id)


def _fetch_album_name_from_page(biz: str, album_id: str, timeout_s: int = 30) -> str:
    """Fetch album name from the album page HTML.

    The API doesn't always return the album name, so we fetch it from the page.

    Args:
        biz: Public account identifier
        album_id: Album ID
        timeout_s: Request timeout

    Returns:
        Album name or empty string if not found.
    """
    url = f"https://mp.weixin.qq.com/mp/appmsgalbum?__biz={biz}&album_id={album_id}"

    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": ACCEPT_LANGUAGE,
    }

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Try to find album name in the HTML
        # Pattern 1: <div class="album__author-name">合集名称</div>
        match = re.search(r'class="album__author-name"[^>]*>([^<]+)<', html)
        if match:
            return match.group(1).strip()

        # Pattern 2: <title>合集名称</title>
        match = re.search(r'<title>([^<]+)</title>', html)
        if match:
            title = match.group(1).strip()
            # Remove common suffixes
            for suffix in [" - 微信公众号", " - 合集"]:
                if title.endswith(suffix):
                    title = title[:-len(suffix)]
            return title

    except Exception:
        pass

    return ""


def _make_api_request(
    biz: str,
    album_id: str,
    begin_msgid: Optional[str] = None,
    count: int = 10,
    timeout_s: int = 30,
) -> Dict[str, Any]:
    """Make a request to the WeChat album API.

    Args:
        biz: Public account identifier (__biz)
        album_id: Album ID
        begin_msgid: Starting message ID for pagination (None for first page)
        count: Number of articles to fetch per request
        timeout_s: Request timeout in seconds

    Returns:
        Parsed JSON response.

    Raises:
        RuntimeError: If the request fails.
    """
    base_url = "https://mp.weixin.qq.com/mp/appmsgalbum"

    params = {
        "action": "getalbum",
        "__biz": biz,
        "album_id": album_id,
        "count": str(count),
        "is_reverse": "1",  # 正序，从第一篇开始
        "f": "json",
    }

    if begin_msgid:
        params["begin_msgid"] = begin_msgid

    query_string = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{query_string}"

    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": ACCEPT_LANGUAGE,
        "Referer": f"https://mp.weixin.qq.com/mp/appmsgalbum?__biz={biz}&album_id={album_id}",
    }

    req = urllib.request.Request(full_url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error: {e.reason}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON response: {e}")


def fetch_album_articles(
    biz: str,
    album_id: str,
    max_articles: int = 0,
    delay_seconds: float = 1.0,
    on_progress: Optional[callable] = None,
) -> Tuple[AlbumInfo, List[ArticleInfo]]:
    """Fetch all articles from a WeChat album.

    Args:
        biz: Public account identifier (__biz)
        album_id: Album ID
        max_articles: Maximum number of articles to fetch (0 = no limit)
        delay_seconds: Delay between API requests for pagination
        on_progress: Optional callback(fetched_count, total_count) for progress

    Returns:
        Tuple of (AlbumInfo with name and count, list of ArticleInfo sorted by create_time).

    Raises:
        RuntimeError: If fetching fails.
    """
    articles: List[ArticleInfo] = []
    album_info = AlbumInfo(biz=biz, album_id=album_id)
    begin_msgid: Optional[str] = None
    page = 0

    while True:
        page += 1

        try:
            resp = _make_api_request(biz, album_id, begin_msgid=begin_msgid)
        except RuntimeError as e:
            # Check for frequency control
            if "freq control" in str(e).lower() or "频繁" in str(e):
                print("Rate limited, waiting 30 seconds...", file=sys.stderr)
                time.sleep(30)
                continue
            raise

        # Parse response
        album_resp = resp.get("getalbum_resp", {})

        # Get album info from first response
        if page == 1:
            info = album_resp.get("album_info", {})
            album_info.name = info.get("album_name", "")
            album_info.article_count = info.get("article_count", 0)

            # If API doesn't return album name, fetch from page HTML
            if not album_info.name.strip():
                album_info.name = _fetch_album_name_from_page(biz, album_id)

            if on_progress:
                on_progress(0, album_info.article_count)

        # Parse article list
        article_list = album_resp.get("article_list", [])

        if not article_list:
            break

        for item in article_list:
            # Handle create_time which might be int or string
            raw_create_time = item.get("create_time", 0)
            try:
                create_time = int(raw_create_time) if raw_create_time else 0
            except (ValueError, TypeError):
                create_time = 0

            article = ArticleInfo(
                title=item.get("title", ""),
                url=item.get("url", ""),
                msgid=str(item.get("msgid", "")),
                create_time=create_time,
            )
            articles.append(article)

            if on_progress:
                on_progress(len(articles), album_info.article_count)

            # Check limit
            if max_articles > 0 and len(articles) >= max_articles:
                return album_info, articles

        # Check if there are more pages
        continue_flag = album_resp.get("continue_flag", 0)
        if not continue_flag or continue_flag == 0:
            break

        # Set up for next page
        begin_msgid = articles[-1].msgid

        # Rate limit between pages
        if delay_seconds > 0:
            time.sleep(delay_seconds)

    # Sort articles by publication time (oldest first)
    articles.sort(key=lambda a: a.create_time)

    return album_info, articles


def _download_single_article(
    article: ArticleInfo,
    output_dir: Path,
    idx: int,
    config: Wechat2mdConfig,
) -> DownloadResult:
    """Download a single article from the album.

    Args:
        article: Article to download
        output_dir: Base output directory for this article
        idx: Article index (1-based) for numbering
        config: Configuration

    Returns:
        DownloadResult with success status.
    """
    # Import here to avoid circular imports
    try:
        from .wechat2md import (
            fetch_html_with_curl,
            extract_title,
            extract_author,
            extract_js_content_inner_html,
            download_images_and_rewrite_html,
            html_to_markdown,
            build_md_document,
            ensure_dir,
        )
        from .frontmatter import FrontmatterGenerator
    except ImportError:
        from wechat2md import (
            fetch_html_with_curl,
            extract_title,
            extract_author,
            extract_js_content_inner_html,
            download_images_and_rewrite_html,
            html_to_markdown,
            build_md_document,
            ensure_dir,
        )
        from frontmatter import FrontmatterGenerator

    # Build article directory name: 001-title
    safe_title = sanitize_title(article.title, max_len=60)
    article_dirname = f"{idx:03d}-{safe_title}"
    article_dir = output_dir / article_dirname
    images_dir = article_dir / config.output.images_dirname

    try:
        # Fetch HTML
        html = fetch_html_with_curl(article.url)

        # Check for login-required pages
        if "环境异常" in html or "请在微信客户端打开" in html:
            return DownloadResult(
                article=article,
                success=False,
                error="需要登录或微信客户端打开",
            )

        # Extract content
        raw_title = extract_title(html)
        author = extract_author(html)

        try:
            js_inner_html = extract_js_content_inner_html(html)
        except RuntimeError as e:
            return DownloadResult(
                article=article,
                success=False,
                error=f"无法提取正文: {e}",
            )

        # Create directories
        ensure_dir(article_dir)
        ensure_dir(images_dir)

        # Download images
        md_image_prefix = f"./{config.output.images_dirname}/"
        rewritten_html, manifest = download_images_and_rewrite_html(
            js_inner_html=js_inner_html,
            article_url=article.url,
            images_dir=images_dir,
            md_image_prefix=md_image_prefix,
        )

        # Convert to markdown
        body_md = html_to_markdown(rewritten_html)

        # Generate frontmatter
        frontmatter_gen = FrontmatterGenerator(config)
        # Handle create_time which might be int or string
        try:
            create_ts = int(article.create_time) if article.create_time else 0
            created = datetime.fromtimestamp(create_ts) if create_ts else datetime.now()
        except (ValueError, TypeError, OSError):
            created = datetime.now()
        frontmatter = frontmatter_gen.generate(
            title=raw_title,
            author=author,
            source_url=article.url,
            created=created,
        )

        # Build document
        full_md = build_md_document(
            title=raw_title,
            body_md=body_md,
            image_manifest=manifest,
        )

        if frontmatter:
            full_md = frontmatter + full_md

        # Write markdown file
        md_path = article_dir / "article.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        return DownloadResult(
            article=article,
            success=True,
            output_dir=article_dir,
        )

    except Exception as e:
        return DownloadResult(
            article=article,
            success=False,
            error=f"{type(e).__name__}: {e}",
        )


def generate_index_file(
    album: AlbumInfo,
    results: List[DownloadResult],
    output_dir: Path,
    album_url: str,
    config: Wechat2mdConfig,
) -> Path:
    """Generate the album index file (_index.md).

    Args:
        album: Album information
        results: List of download results
        output_dir: Album output directory
        album_url: Original album URL
        config: Configuration

    Returns:
        Path to the generated index file.
    """
    index_filename = config.album.index_filename
    index_path = output_dir / index_filename

    # Use album name or fallback to directory name
    album_title = album.name.strip() if album.name else output_dir.name

    lines: List[str] = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f"title: {album_title}")
    lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("type: album")
    lines.append(f"article_count: {len(results)}")
    lines.append(f'source: "{album_url}"')
    lines.append("tags: [微信文章, 合集]")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# {album_title}")
    lines.append("")
    lines.append(f"共 {len(results)} 篇文章")
    lines.append("")

    # Successful articles
    successful = [r for r in results if r.success]
    if successful:
        lines.append("## 文章列表")
        lines.append("")
        for i, result in enumerate(successful, 1):
            # Build relative link
            safe_title = sanitize_title(result.article.title, max_len=60)
            dirname = f"{results.index(result) + 1:03d}-{safe_title}"
            link = f"./{dirname}/article.md"
            lines.append(f"{i}. [{result.article.title}]({link})")
        lines.append("")

    # Failed articles
    failed = [r for r in results if not r.success]
    if failed:
        lines.append("## 下载失败")
        lines.append("")
        for result in failed:
            error_msg = result.error or "未知错误"
            lines.append(f"- [ ] {result.article.title} - {error_msg}")
        lines.append("")

    # Write file
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return index_path


def download_album(
    url: str,
    config: Optional[Wechat2mdConfig] = None,
    cwd: Optional[Path] = None,
) -> AlbumResult:
    """Download all articles from a WeChat album.

    Args:
        url: Album URL
        config: Configuration (loads default if None)
        cwd: Working directory (defaults to current directory)

    Returns:
        AlbumResult with download results.

    Raises:
        ValueError: If URL is not a valid album URL.
        RuntimeError: If fetching album info fails.
    """
    if config is None:
        config = load_config()

    if cwd is None:
        cwd = Path.cwd()

    # Parse album URL
    album_info = parse_album_url(url)
    if not album_info:
        raise ValueError(f"Invalid album URL: {url}")

    # Progress callback
    def show_progress(fetched: int, total: int):
        if total > 0:
            print(f"\rFetching article list: {fetched}/{total}", end="", file=sys.stderr)

    # Fetch article list
    print(f"Fetching album info...", file=sys.stderr)
    album, articles = fetch_album_articles(
        biz=album_info.biz,
        album_id=album_info.album_id,
        max_articles=config.album.max_articles,
        delay_seconds=config.album.delay_seconds,
        on_progress=show_progress,
    )
    print(file=sys.stderr)  # New line after progress

    if not articles:
        raise RuntimeError("No articles found in album")

    print(f"Album: {album.name}", file=sys.stderr)
    print(f"Found {len(articles)} articles", file=sys.stderr)
    print(file=sys.stderr)

    # Build output directory
    # Use album name if available, otherwise use album_id as fallback
    album_name = album.name.strip() if album.name else f"album-{album_info.album_id[:8]}"
    safe_album_name = sanitize_title(album_name, max_len=60)
    folder = config.folder.default or "20-阅读笔记"
    output_dir = cwd / config.output.base_dir / folder / safe_album_name

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download each article
    results: List[DownloadResult] = []
    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] Downloading: {article.title} ... ", end="", file=sys.stderr)
        sys.stderr.flush()

        result = _download_single_article(article, output_dir, i, config)
        results.append(result)

        if result.success:
            print("done", file=sys.stderr)
        else:
            print(f"failed ({result.error})", file=sys.stderr)

        # Rate limit between downloads
        if i < len(articles) and config.album.delay_seconds > 0:
            time.sleep(config.album.delay_seconds)

    # Generate index file
    index_path: Optional[Path] = None
    if config.album.generate_index:
        index_path = generate_index_file(album, results, output_dir, url, config)

    # Build result
    succeeded = sum(1 for r in results if r.success)
    failed = len(results) - succeeded

    print(file=sys.stderr)
    print(f"Album download complete: {succeeded}/{len(results)} succeeded", file=sys.stderr)
    if index_path:
        print(f"Output: {index_path}", file=sys.stderr)

    return AlbumResult(
        album=album,
        output_dir=output_dir,
        index_file=index_path,
        results=results,
        total=len(results),
        succeeded=succeeded,
        failed=failed,
    )


def download_album_main(url: str) -> int:
    """Main entry point for album download.

    Args:
        url: Album URL

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        config = load_config()
        result = download_album(url, config)

        # Output paths for caller
        if result.index_file:
            print(str(result.index_file))
        print(str(result.output_dir))

        return 0 if result.failed == 0 else 0  # Return 0 even with partial failures

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python album.py <album_url>", file=sys.stderr)
        sys.exit(2)

    url = sys.argv[1].strip()
    sys.exit(download_album_main(url))
