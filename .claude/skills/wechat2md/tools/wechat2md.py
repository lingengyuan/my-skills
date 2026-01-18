#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wechat2md: Convert a WeChat Official Account article to Markdown with local images.

Deterministic pipeline:
1) Fetch HTML (curl)
2) Extract title + #js_content inner HTML
3) Download all images to ./images/<title>/001.<ext>...
4) Convert正文HTML to Markdown (structure-first, keep key inline styles as HTML)
5) Write Markdown to ./outputs/<title>/<title>.md

Output contract (relative to CWD):
- Markdown: ./outputs/<title>/<title>.md
- Images:   ./images/<title>/001.<ext> ... (3-digit, order in DOM)
- Create missing dirs, overwrite existing files.

Usage:
  python3 wechat2md.py "https://mp.weixin.qq.com/s/xxxxxxxx"

Notes:
- If an image download fails, Markdown keeps the original URL and a failure list is appended
  near the top.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9,en;q=0.8"


@dataclass
class ImageItem:
    idx: int
    original_url: str
    local_filename: str  # e.g. '001.jpg'
    local_rel_md: str    # e.g. '../../images/<title>/001.jpg'
    download_ok: bool
    error: Optional[str] = None


def fetch_html_with_curl(url: str, timeout_s: int = 30) -> str:
    """Fetch page HTML using curl for maximum compatibility with mp.weixin.qq.com."""
    # Prefer curl if available.
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError("curl not found in PATH; please install curl")

    cmd = [
        curl,
        "-L",
        "--compressed",
        "--max-time",
        str(timeout_s),
        "-H",
        f"User-Agent: {UA}",
        "-H",
        f"Accept-Language: {ACCEPT_LANGUAGE}",
        "-H",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        url,
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed ({proc.returncode}): {proc.stderr.strip()}")
    if not proc.stdout.strip():
        raise RuntimeError("empty HTML fetched")
    return proc.stdout


def extract_title(html: str) -> str:
    """Extract title from HTML using meta og:title first, then <title>."""
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", attrs={"property": "og:title"})
    if og and og.get("content"):
        return og["content"].strip()

    # Some pages use meta name="twitter:title"
    tw = soup.find("meta", attrs={"name": "twitter:title"})
    if tw and tw.get("content"):
        return tw["content"].strip()

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    # Fallback: first h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)

    return "wechat_article"


_ILLEGAL_FS_CHARS = re.compile(r"[\\/:*?\"<>|]+")
_WHITESPACE = re.compile(r"\s+")


def sanitize_title(title: str, max_len: int = 80) -> str:
    t = unescape(title)
    t = t.strip()
    t = _ILLEGAL_FS_CHARS.sub("-", t)
    t = _WHITESPACE.sub(" ", t).strip()
    t = t.strip(".")  # avoid weird trailing dot names
    if not t:
        t = "wechat_article"
    if len(t) > max_len:
        t = t[:max_len].rstrip()
    return t


def extract_js_content_inner_html(html: str) -> str:
    """Extract inner HTML of div#js_content.

    First try BeautifulSoup. If not found, fallback to a depth-counting extractor.
    """
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find(id="js_content")
    if div:
        # Return inner HTML (not including the wrapper div itself).
        return "".join(str(x) for x in div.contents)

    # Fallback: string search + div depth count (robust against partial parsing)
    marker = 'id="js_content"'
    start = html.find(marker)
    if start < 0:
        marker = "id='js_content'"
        start = html.find(marker)
    if start < 0:
        raise RuntimeError("cannot find #js_content")

    # find nearest opening <div ... id="js_content" ...>
    open_div = html.rfind("<div", 0, start)
    if open_div < 0:
        raise RuntimeError("cannot locate opening <div> for #js_content")

    i = open_div
    depth = 0
    in_script = False
    # We will extract the whole js_content div, then strip outer tag via BeautifulSoup.
    while i < len(html):
        if html.startswith("<script", i):
            in_script = True
        if in_script:
            end_script = html.find("</script", i)
            if end_script == -1:
                break
            i = html.find(">", end_script)
            if i == -1:
                break
            i += 1
            in_script = False
            continue

        if html.startswith("<div", i):
            depth += 1
            i = html.find(">", i)
            if i == -1:
                break
            i += 1
            continue

        if html.startswith("</div", i):
            depth -= 1
            i = html.find(">", i)
            if i == -1:
                break
            i += 1
            if depth == 0:
                js_div_html = html[open_div:i]
                tmp = BeautifulSoup(js_div_html, "html.parser")
                js = tmp.find(id="js_content")
                if not js:
                    raise RuntimeError("fallback extractor found wrapper but cannot parse #js_content")
                return "".join(str(x) for x in js.contents)
            continue

        i += 1

    raise RuntimeError("failed to extract #js_content by depth counting")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _guess_ext_from_url(url: str) -> Optional[str]:
    try:
        p = urllib.parse.urlparse(url)
        base = os.path.basename(p.path)
        if "." in base:
            ext = base.rsplit(".", 1)[-1].lower()
            if ext in {"jpg", "jpeg", "png", "gif", "webp", "bmp"}:
                return "jpg" if ext == "jpeg" else ext
    except Exception:
        return None
    return None


def _ext_from_content_type(ct: str) -> Optional[str]:
    ct = (ct or "").split(";")[0].strip().lower()
    mapping = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/bmp": "bmp",
    }
    return mapping.get(ct)


def _download_binary(url: str, referer: str, timeout_s: int = 30, retries: int = 2) -> Tuple[bytes, Optional[str]]:
    headers = {
        "User-Agent": UA,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": ACCEPT_LANGUAGE,
        "Referer": referer,
    }
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                data = resp.read()
                ct = resp.headers.get("Content-Type")
                return data, ct
        except Exception as e:
            last_err = e
            # brief backoff
            time.sleep(0.6 * (attempt + 1))
    raise last_err  # type: ignore


def download_images_and_rewrite_html(
    js_inner_html: str,
    article_url: str,
    images_dir: Path,
    md_image_prefix: str,
) -> Tuple[str, List[ImageItem]]:
    """Download all images found in正文 HTML and rewrite <img> tags into placeholders.

    Returns (rewritten_html, image_manifest).
    """
    soup = BeautifulSoup(js_inner_html, "html.parser")
    imgs = soup.find_all("img")

    ensure_dir(images_dir)

    manifest: List[ImageItem] = []

    for i, img in enumerate(imgs, start=1):
        original_url = (
            img.get("data-src")
            or img.get("data-original")
            or img.get("src")
            or ""
        ).strip()

        idx_str = f"{i:03d}"

        if not original_url:
            # Remove empty image tags (rare)
            img.replace_with("" )
            manifest.append(
                ImageItem(
                    idx=i,
                    original_url="",
                    local_filename=f"{idx_str}.bin",
                    local_rel_md=f"{md_image_prefix}{idx_str}.bin",
                    download_ok=False,
                    error="missing image url",
                )
            )
            continue

        # Normalize protocol-less URLs
        if original_url.startswith("//"):
            original_url = "https:" + original_url

        ext = _guess_ext_from_url(original_url)
        local_filename = f"{idx_str}.{ext or 'jpg'}"
        local_path = images_dir / local_filename

        ok = True
        err = None

        try:
            data, ct = _download_binary(original_url, referer=article_url)
            # If ext unknown, infer from content-type
            inferred = _ext_from_content_type(ct or "")
            if ext is None and inferred is not None:
                local_filename = f"{idx_str}.{inferred}"
                local_path = images_dir / local_filename

            # Write (overwrite)
            with open(local_path, "wb") as f:
                f.write(data)
        except Exception as e:
            ok = False
            err = f"{type(e).__name__}: {e}"

        local_rel_md = f"{md_image_prefix}{local_filename}"
        manifest.append(
            ImageItem(
                idx=i,
                original_url=original_url,
                local_filename=local_filename,
                local_rel_md=local_rel_md,
                download_ok=ok,
                error=err,
            )
        )

        # Rewrite the tag in HTML:
        # Use a custom placeholder tag so later conversion is deterministic.
        if ok:
            placeholder = soup.new_tag("wechat2md-img")
            placeholder["src"] = local_rel_md
            # keep alt if any
            alt = (img.get("alt") or "").strip()
            if alt:
                placeholder["alt"] = alt
            img.replace_with(placeholder)
        else:
            # Keep original URL in placeholder so md keeps it as remote image
            placeholder = soup.new_tag("wechat2md-img")
            placeholder["src"] = original_url
            alt = (img.get("alt") or "").strip()
            if alt:
                placeholder["alt"] = alt
            img.replace_with(placeholder)

    return str(soup), manifest


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _text_of(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    return node.get_text(" ", strip=False)


def _style_keep(style: str) -> str:
    """Keep only a small set of style props to avoid dumping huge inline styles."""
    if not style:
        return ""
    allowed = {
        "color",
        "background",
        "background-color",
        "font-weight",
        "font-style",
        "text-decoration",
        "text-align",
        "font-size",
        "line-height",
    }
    parts = []
    for seg in style.split(";"):
        seg = seg.strip()
        if not seg or ":" not in seg:
            continue
        k, v = seg.split(":", 1)
        k = k.strip().lower()
        v = v.strip()
        if k in allowed and v:
            parts.append(f"{k}:{v}")
    return "; ".join(parts)


def _is_caption_p(tag: Tag) -> bool:
    if tag.name not in {"p", "section"}:
        return False

    text = _collapse_ws(tag.get_text(" ", strip=True))
    if not text:
        return False

    # Rough heuristics: short text + centered or smaller font.
    if len(text) > 80:
        return False

    style = (tag.get("style") or "")
    style_l = style.lower()
    if "text-align" in style_l and "center" in style_l:
        return True

    # Sometimes caption is in nested span with style
    span = tag.find("span")
    if span:
        s = (span.get("style") or "").lower()
        if "text-align" in s and "center" in s:
            return True
        if "font-size" in s:
            return True

    # Common class name
    cls = " ".join(tag.get("class") or [])
    if "caption" in cls.lower():
        return True

    return False


def html_to_markdown(js_html: str) -> str:
    """Convert正文 HTML (already rewritten image placeholders) to Markdown."""
    soup = BeautifulSoup(js_html, "html.parser")

    lines: List[str] = []

    def emit(line: str = ""):
        # Avoid trailing spaces
        lines.append(line.rstrip())

    def convert_inline(node) -> str:
        if isinstance(node, NavigableString):
            return str(node)

        if not isinstance(node, Tag):
            return ""

        name = node.name.lower()

        if name == "br":
            return "\n"

        if name in {"strong", "b"}:
            inner = "".join(convert_inline(c) for c in node.children)
            inner = inner.strip()
            return f"**{inner}**" if inner else ""

        if name in {"em", "i"}:
            inner = "".join(convert_inline(c) for c in node.children)
            inner = inner.strip()
            return f"*{inner}*" if inner else ""

        if name == "code":
            inner = "".join(convert_inline(c) for c in node.children)
            inner = inner.strip("\n")
            inner = inner.replace("`", "\\`")
            return f"`{inner}`" if inner else ""

        if name == "a":
            href = (node.get("href") or "").strip()
            text = _collapse_ws("".join(convert_inline(c) for c in node.children))
            if not text:
                text = href
            if href:
                return f"[{text}]({href})"
            return text

        if name == "span":
            style = node.get("style") or ""
            inner = "".join(convert_inline(c) for c in node.children)
            # Check for bold/italic in style
            style_lower = style.lower()
            if "font-weight" in style_lower and ("bold" in style_lower or "700" in style_lower or "800" in style_lower or "900" in style_lower):
                inner = inner.strip()
                if inner:
                    return f"**{inner}**"
            if "font-style" in style_lower and "italic" in style_lower:
                inner = inner.strip()
                if inner:
                    return f"*{inner}*"
            # For other styles, just return the text (don't keep HTML)
            return inner

        if name == "wechat2md-img":
            src = (node.get("src") or "").strip()
            alt = (node.get("alt") or "").strip()
            if alt:
                return f"\n\n![{alt}]({src})\n\n"
            return f"\n\n![]({src})\n\n"

        # default: inline flatten
        return "".join(convert_inline(c) for c in node.children)

    def convert_block(node, list_prefix: str = ""):
        if isinstance(node, NavigableString):
            txt = str(node)
            if _collapse_ws(txt):
                # Inline stray text inside container
                emit(_collapse_ws(txt))
                emit()
            return

        if not isinstance(node, Tag):
            return

        name = node.name.lower()

        if name in {"h1", "h2", "h3"}:
            lvl = {"h1": "#", "h2": "##", "h3": "###"}[name]
            text = _collapse_ws("".join(convert_inline(c) for c in node.children))
            if text:
                emit(f"{lvl} {text}")
                emit()
            return

        if name == "hr":
            emit("---")
            emit()
            return

        if name == "blockquote":
            # Convert each line with >
            inner_text = "".join(convert_inline(c) for c in node.children)
            inner_lines = [l.rstrip() for l in inner_text.splitlines() if l.strip()]
            if inner_lines:
                for l in inner_lines:
                    emit(f"> {l}")
                emit()
            return

        if name in {"ul", "ol"}:
            ordered = name == "ol"
            idx = 1
            for li in node.find_all("li", recursive=False):
                prefix = f"{idx}. " if ordered else "- "
                convert_block(li, list_prefix=prefix)
                idx += 1
            emit()
            return

        if name == "li":
            # List item may contain nested blocks
            # Build first-line text from immediate children that are inline
            parts: List[str] = []
            for c in node.contents:
                if isinstance(c, Tag) and c.name.lower() in {"ul", "ol", "p", "div", "section", "pre", "blockquote"}:
                    continue
                parts.append(convert_inline(c))
            first = _collapse_ws("".join(parts))
            if first:
                emit(f"{list_prefix}{first}")
            # Now nested blocks
            for c in node.contents:
                if isinstance(c, Tag) and c.name.lower() in {"ul", "ol"}:
                    # nested list indented by two spaces
                    sub_lines_before = len(lines)
                    convert_block(c)
                    # indent the nested list output
                    for j in range(sub_lines_before, len(lines)):
                        if lines[j].strip():
                            lines[j] = "  " + lines[j]
            return

        if name == "pre":
            # Extract code text, converting <br> tags to newlines
            def extract_code_text(n) -> str:
                if isinstance(n, NavigableString):
                    return str(n)
                if not isinstance(n, Tag):
                    return ""
                if n.name.lower() == "br":
                    return "\n"
                return "".join(extract_code_text(c) for c in n.children)

            code = extract_code_text(node)
            # Normalize line endings
            code = code.replace('\r\n', '\n').replace('\r', '\n')
            code = code.strip("\n")
            if code:
                # Detect code language for syntax highlighting
                lang = detect_code_language(code)
                emit(f"```{lang}")
                for line in code.split("\n"):
                    emit(line)
                emit("```")
                emit()
            return

        if name in {"p", "div", "section"}:
            # Check if this block contains only an image
            children = [c for c in node.children if not (isinstance(c, NavigableString) and not str(c).strip())]
            if len(children) == 1:
                child = children[0]
                if isinstance(child, Tag) and child.name.lower() == "wechat2md-img":
                    # Standalone image in block
                    md = convert_inline(child)
                    if md:
                        emit(md)
                        emit()
                    return

            # Caption heuristic
            if _is_caption_p(node):
                text = _collapse_ws("".join(convert_inline(c) for c in node.children))
                if text:
                    # Use italic for captions instead of HTML
                    emit(f"*{text}*")
                    emit()
                return

            # Check if this block contains nested block elements
            # If so, process children as blocks instead of inline
            block_tags = {"p", "div", "section", "ul", "ol", "pre", "blockquote", "h1", "h2", "h3", "hr", "wechat2md-img"}
            has_block_children = any(
                isinstance(c, Tag) and c.name.lower() in block_tags
                for c in node.children
            )

            if has_block_children:
                # Process mixed content: inline content before/between/after block elements
                inline_buffer = []
                for c in node.children:
                    if isinstance(c, Tag) and c.name.lower() in block_tags:
                        # Flush any accumulated inline content
                        if inline_buffer:
                            inline_text = "".join(inline_buffer)
                            inline_text = inline_text.replace("\xa0", " ")
                            inline_text = re.sub(r"[ \t]+", " ", inline_text)
                            inline_lines = [l.strip() for l in inline_text.split("\n")]
                            inline_lines = [l for l in inline_lines if l]
                            if inline_lines:
                                emit("\n".join(inline_lines))
                                emit()
                            inline_buffer = []
                        # Process the block child
                        convert_block(c)
                    else:
                        # Accumulate inline content
                        inline_buffer.append(convert_inline(c))
                # Flush remaining inline content
                if inline_buffer:
                    inline_text = "".join(inline_buffer)
                    inline_text = inline_text.replace("\xa0", " ")
                    inline_text = re.sub(r"[ \t]+", " ", inline_text)
                    inline_lines = [l.strip() for l in inline_text.split("\n")]
                    inline_lines = [l for l in inline_lines if l]
                    if inline_lines:
                        emit("\n".join(inline_lines))
                        emit()
                return

            # Regular paragraph-like block (no nested block elements)
            inner = "".join(convert_inline(c) for c in node.children)
            # Normalize NBSP and whitespace
            inner = inner.replace("\xa0", " ")
            inner = re.sub(r"[ \t]+", " ", inner)
            # Preserve intentional line breaks from <br>
            inner_lines = [l.strip() for l in inner.split("\n")]
            inner_lines = [l for l in inner_lines if l != ""]
            if inner_lines:
                emit("\n".join(inner_lines))
                emit()
            return

        if name == "wechat2md-img":
            # Standalone image
            md = convert_inline(node)
            if md:
                emit(md)
                emit()
            return

        # Fallback: walk children
        for c in node.children:
            if isinstance(c, Tag) and c.name.lower() in {"ul", "ol", "pre", "blockquote", "p", "div", "section", "h1", "h2", "h3", "hr", "wechat2md-img"}:
                convert_block(c)
            else:
                # Inline in a block context
                txt = _collapse_ws(convert_inline(c))
                if txt:
                    emit(txt)
                    emit()

    # Walk top-level nodes
    for child in soup.contents:
        convert_block(child)

    # Cleanup: collapse multiple blank lines
    cleaned: List[str] = []
    blank = 0
    for l in lines:
        if l.strip() == "":
            blank += 1
            if blank <= 1:
                cleaned.append("")
        else:
            blank = 0
            cleaned.append(l.rstrip())

    return "\n".join(cleaned).strip() + "\n"


def fix_plain_text_urls(text: str) -> str:
    """Convert plain text URLs to proper markdown links.

    Patterns handled:
    - "地址：github.com/xxx" → "[地址](https://github.com/xxx)"
    - "GitHub 地址→github.com/xxx" → "[GitHub 地址](https://github.com/xxx)"
    - Plain URLs like "github.com/xxx" → "[github.com/xxx](https://github.com/xxx)"
    """
    import re

    # Pattern 1: "XXX地址→URL" or "XXX地址：URL" (Chinese colon or arrow)
    def replace_labeled_url(match):
        label = match.group(1).strip()
        url = match.group(2).strip()
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return f"[{label}]({url})"

    # Match: label (including spaces, ending with 地址) followed by → or ： and then a URL
    # Use word boundary or start of line/space before the label
    text = re.sub(
        r'((?:[\w\s]*?)地址)\s*[→：:]\s*((?:https?://)?(?:github\.com|gitee\.com|gitlab\.com|bitbucket\.org)[^\s\)）\]<]*)',
        replace_labeled_url,
        text
    )

    # Pattern 2: Standalone URLs without protocol at line start or after space
    def add_protocol(match):
        prefix = match.group(1)
        url = match.group(2)
        return f"{prefix}[{url}](https://{url})"

    # Match standalone domain URLs (not already in markdown link format)
    text = re.sub(
        r'(^|(?<=[>\s]))((github\.com|gitee\.com|gitlab\.com|bitbucket\.org)/[^\s\)）\]<]+)',
        add_protocol,
        text,
        flags=re.MULTILINE
    )

    return text


def detect_code_language(code: str) -> str:
    """Detect programming language from code content.

    Returns language identifier for markdown code fence, or empty string if unknown.
    """
    code_lower = code.lower().strip()
    lines = code.split('\n')
    first_line = lines[0].strip() if lines else ""

    # Shell/Bash indicators
    if first_line.startswith('$') or first_line.startswith('#!'):
        return "bash"
    if any(cmd in code for cmd in ['apt-get', 'npm install', 'pip install', 'git clone', 'docker ', 'kubectl ']):
        return "bash"

    # Python indicators
    if 'import ' in code or 'def ' in code or 'print(' in code:
        if 'from __future__' in code or 'import numpy' in code or 'import pandas' in code:
            return "python"
        if re.search(r'\bdef\s+\w+\s*\(', code):
            return "python"

    # Rust indicators (check before JavaScript because both use 'let')
    if 'fn main()' in code or 'let mut ' in code or '-> Result<' in code or 'println!' in code:
        return "rust"

    # Go indicators
    if 'package main' in code or 'func ' in code or 'import "' in code:
        return "go"

    # Java indicators
    if 'public class' in code or 'public static void main' in code:
        return "java"

    # JavaScript/TypeScript indicators
    if 'const ' in code or 'let ' in code or 'function ' in code or '=>' in code:
        if 'interface ' in code or ': string' in code or ': number' in code:
            return "typescript"
        return "javascript"

    # C/C++ indicators
    if '#include' in code:
        if '<iostream>' in code or 'std::' in code or '::' in code:
            return "cpp"
        return "c"

    # SQL indicators
    if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE TABLE)\b', code, re.IGNORECASE):
        return "sql"

    # JSON indicators
    if code_lower.startswith('{') and code_lower.rstrip().endswith('}'):
        if '"' in code and ':' in code:
            return "json"

    # YAML indicators
    if re.search(r'^\w+:\s*\n', code) or re.search(r'^\s*-\s+\w+:', code, re.MULTILINE):
        return "yaml"

    # HTML/XML indicators
    if re.search(r'<\w+[^>]*>', code) and re.search(r'</\w+>', code):
        return "html"

    # CSS indicators
    if re.search(r'[.#]\w+\s*\{', code) or re.search(r'@media\s', code):
        return "css"

    return ""


def build_md_document(
    title: str,
    body_md: str,
    image_manifest: List[ImageItem],
) -> str:
    # Fix plain text URLs before building document
    body_md = fix_plain_text_urls(body_md)

    parts: List[str] = []
    parts.append(f"# {title}")
    parts.append("")

    failures = [it for it in image_manifest if not it.download_ok]
    if failures:
        parts.append("## 图片下载失败列表")
        for it in failures:
            if it.original_url:
                parts.append(f"- {it.idx:03d}: {it.original_url} ({it.error or 'download failed'})")
            else:
                parts.append(f"- {it.idx:03d}: (missing url) ({it.error or 'download failed'})")
        parts.append("")

    parts.append(body_md.strip())
    parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert WeChat article to Markdown with local images")
    parser.add_argument("url", help="WeChat article URL (mp.weixin.qq.com)")
    args = parser.parse_args()

    url = args.url.strip()
    if not url:
        print("ERROR: empty URL", file=sys.stderr)
        return 2

    try:
        html = fetch_html_with_curl(url)
        raw_title = extract_title(html)
        title = sanitize_title(raw_title)
        js_inner_html = extract_js_content_inner_html(html)

        cwd = Path.cwd()
        outputs_root = cwd / "outputs" / title
        images_dir = outputs_root / "images"

        ensure_dir(outputs_root)
        ensure_dir(images_dir)

        # Images are stored in ./images/ subdirectory of the output folder
        # This makes the article self-contained and portable
        md_image_prefix = "./images/"

        rewritten_html, manifest = download_images_and_rewrite_html(
            js_inner_html=js_inner_html,
            article_url=url,
            images_dir=images_dir,
            md_image_prefix=md_image_prefix,
        )

        body_md = html_to_markdown(rewritten_html)
        full_md = build_md_document(title=title, body_md=body_md, image_manifest=manifest)

        md_path = outputs_root / f"{title}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        print(str(md_path))
        print(str(images_dir))
        return 0

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
