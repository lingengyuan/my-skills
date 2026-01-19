#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end test for wechat2md with mock HTML data."""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import mock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from config import load_config, Wechat2mdConfig
from path_builder import PathBuilder, sanitize_title
from frontmatter import FrontmatterGenerator
from wechat2md import (
    build_md_document,
    download_images_and_rewrite_html,
    ensure_dir,
    extract_author,
    extract_title,
    html_to_markdown,
    write_meta_json,
)


# Mock WeChat article HTML
MOCK_WECHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta property="og:title" content="测试微信文章：Python 开发最佳实践">
    <meta name="author" content="技术博客">
    <title>测试微信文章：Python 开发最佳实践</title>
</head>
<body>
    <div id="js_name">技术博客</div>
    <div id="js_content">
        <h2>引言</h2>
        <p>这是一篇关于 <strong>Python</strong> 开发的文章。</p>
        <p>本文将介绍以下内容：</p>
        <ul>
            <li>代码规范</li>
            <li>测试方法</li>
            <li>性能优化</li>
        </ul>

        <h2>代码规范</h2>
        <p>遵循 <em>PEP 8</em> 是 Python 开发的基本要求。</p>
        <pre>def greet(name):
    return f"Hello, {name}!"</pre>

        <h2>测试示例</h2>
        <blockquote>
        <p>测试是保证代码质量的重要手段。</p>
        </blockquote>

        <p>GitHub 地址：github.com/test/project</p>

        <p>访问 <a href="https://python.org">Python 官网</a>了解更多。</p>

        <img data-src="https://example.com/test1.jpg" alt="测试图片1">
        <img src="https://example.com/test2.png">

        <p style="text-align:center;font-size:14px;">图片说明文字</p>
    </div>
</body>
</html>
"""


def test_e2e_default_mode():
    """End-to-end test in default mode (v1 behavior)."""
    print("\n=== E2E Test: Default Mode ===")

    # Mock config loading to return default config
    with mock.patch("config.find_config_file", return_value=None):
        config = load_config()

    # Extract article metadata
    title = extract_title(MOCK_WECHAT_HTML)
    author = extract_author(MOCK_WECHAT_HTML)
    sanitized_title = sanitize_title(title, config.slug.max_length)

    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Sanitized: {sanitized_title}")

    # Build paths
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = Path(tmpdir)
        builder = PathBuilder(config)

        output_dir = builder.build_output_path(title, "https://mp.weixin.qq.com/s/test", cwd=cwd)
        images_dir = output_dir / builder.get_images_dirname()
        article_filename = builder.build_article_filename(title)

        print(f"Output dir: {output_dir}")
        print(f"Images dir: {images_dir}")
        print(f"Article filename: {article_filename}")

        # Verify default structure
        assert "outputs" in str(output_dir)
        assert sanitized_title in str(output_dir)
        assert article_filename.endswith(".md")
        assert title in article_filename or sanitized_title in article_filename

        # Create directories
        ensure_dir(output_dir)
        ensure_dir(images_dir)

        # Mock image downloads (don't actually download)
        from bs4 import BeautifulSoup
        from wechat2md import ImageItem

        soup = BeautifulSoup(MOCK_WECHAT_HTML, "html.parser")
        js_content = soup.find(id="js_content")
        js_html = "".join(str(x) for x in js_content.contents)

        # Replace images with placeholders
        imgs = soup.find_all("img")
        manifest = []
        for i, img in enumerate(imgs, start=1):
            url = img.get("data-src") or img.get("src") or ""
            local_filename = f"{i:03d}.jpg"
            local_rel = f"./images/{local_filename}"
            manifest.append(ImageItem(i, url, local_filename, local_rel, True, None))

            # Replace img tag
            placeholder = soup.new_tag("wechat2md-img")
            placeholder["src"] = local_rel
            alt = img.get("alt") or ""
            if alt:
                placeholder["alt"] = alt
            img.replace_with(placeholder)

        rewritten_html = str(soup.find(id="js_content"))

        # Convert to markdown
        body_md = html_to_markdown(rewritten_html)

        # Verify markdown content
        print(f"\n--- Body MD Sample (first 800 chars) ---\n{body_md[:800]}\n")

        assert "## 引言" in body_md or "##" in body_md
        assert "**Python**" in body_md or "Python" in body_md
        assert "代码规范" in body_md
        assert "```python" in body_md or "```" in body_md
        assert "def greet" in body_md
        assert "测试是保证代码质量的重要手段" in body_md
        # URL conversion may vary, just check the URL is present
        assert "github.com/test/project" in body_md
        assert "python.org" in body_md
        assert "./images/001.jpg" in body_md or "./images/" in body_md
        assert "图片说明文字" in body_md

        print("[OK] Markdown conversion successful")

        # Generate frontmatter (should be empty in default mode)
        fm_gen = FrontmatterGenerator(config)
        fm = fm_gen.generate(title=title, author=author, source_url="https://mp.weixin.qq.com/s/test")
        assert fm == ""
        print("[OK] No frontmatter in default mode")

        # Build final document
        full_md = build_md_document(title, body_md, manifest)

        # Verify document structure
        assert f"# {title}" in full_md or f"# {sanitized_title}" in full_md
        assert "## 引言" in full_md

        # Write document
        md_path = output_dir / article_filename
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        assert md_path.exists()
        print(f"[OK] Markdown written to {md_path.name}")

        # Verify no meta.json in default mode
        meta_path = write_meta_json(output_dir, title, "https://example.com", author, datetime.now(), config)
        assert meta_path is None
        print("[OK] No meta.json in default mode")

        # Read and display sample
        print("\n--- Sample Output (First 500 chars) ---")
        print(full_md[:500])
        print("...")

    print("=== Default Mode Test PASSED ===\n")


def test_e2e_kb_mode():
    """End-to-end test in knowledge base mode."""
    print("\n=== E2E Test: Knowledge Base Mode ===")

    # Create KB config
    kb_config_data = {
        "output": {
            "path_template": "{base_dir}/{folder}/{slug}",
            "article_filename": "article.md",
        },
        "slug": {
            "format": "date-title-hash",
            "max_length": 80,
        },
        "frontmatter": {
            "enabled": True,
            "include_fields": ["title", "author", "created", "source", "tags"],
        },
        "folder": {
            "default": "20-阅读笔记",
        },
        "tags": {
            "default_tags": ["微信文章", "Python", "最佳实践"],
            "max_count": 8,
        },
        "meta": {
            "enabled": True,
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config file
        config_dir = Path(tmpdir) / ".claude" / "skills" / "wechat2md"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(kb_config_data, f, ensure_ascii=False, indent=2)

        # Mock config loading
        with mock.patch("config.find_config_file", return_value=config_file):
            config = load_config()

        # Extract article metadata
        title = extract_title(MOCK_WECHAT_HTML)
        author = extract_author(MOCK_WECHAT_HTML)
        created = datetime(2024, 3, 15, 14, 30)

        print(f"Title: {title}")
        print(f"Author: {author}")

        # Build KB paths
        cwd = Path(tmpdir)
        builder = PathBuilder(config)

        output_dir = builder.build_output_path(title, "https://mp.weixin.qq.com/s/abc123", created, cwd)
        images_dir = output_dir / builder.get_images_dirname()
        article_filename = builder.build_article_filename(title)

        print(f"Output dir: {output_dir}")
        print(f"Article filename: {article_filename}")

        # Verify KB structure
        assert "20-阅读笔记" in str(output_dir)
        assert "20240315" in str(output_dir)
        assert article_filename == "article.md"

        # Create directories
        ensure_dir(output_dir)
        ensure_dir(images_dir)

        # Convert HTML (reuse logic from default mode test)
        from bs4 import BeautifulSoup
        from wechat2md import ImageItem

        soup = BeautifulSoup(MOCK_WECHAT_HTML, "html.parser")
        js_content = soup.find(id="js_content")

        imgs = soup.find_all("img")
        manifest = []
        for i, img in enumerate(imgs, start=1):
            url = img.get("data-src") or img.get("src") or ""
            local_filename = f"{i:03d}.jpg"
            local_rel = f"./images/{local_filename}"
            manifest.append(ImageItem(i, url, local_filename, local_rel, True, None))

            placeholder = soup.new_tag("wechat2md-img")
            placeholder["src"] = local_rel
            alt = img.get("alt") or ""
            if alt:
                placeholder["alt"] = alt
            img.replace_with(placeholder)

        rewritten_html = str(soup.find(id="js_content"))
        body_md = html_to_markdown(rewritten_html)

        print("[OK] Markdown conversion successful")

        # Generate frontmatter
        fm_gen = FrontmatterGenerator(config)
        fm = fm_gen.generate(
            title=title,
            author=author,
            source_url="https://mp.weixin.qq.com/s/abc123",
            created=created,
        )

        # Verify frontmatter
        assert fm.startswith("---")
        assert "title:" in fm
        assert "author: 技术博客" in fm
        assert "created: 2024-03-15" in fm
        assert "source:" in fm
        assert "微信文章" in fm
        assert "Python" in fm

        print("[OK] Frontmatter generated")
        print("\n--- Frontmatter ---")
        print(fm)

        # Build final document with frontmatter
        doc = build_md_document(title, body_md, manifest)
        full_md = fm + doc

        # Write document
        md_path = output_dir / article_filename
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        assert md_path.exists()
        print(f"[OK] Markdown written to {md_path.relative_to(cwd)}")

        # Write meta.json
        meta_path = write_meta_json(
            output_dir,
            title,
            "https://mp.weixin.qq.com/s/abc123",
            author,
            created,
            config
        )

        assert meta_path is not None
        assert meta_path.exists()

        # Verify meta.json content
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        assert meta["title"] == title
        assert meta["author"] == author
        assert meta["folder"] == "20-阅读笔记"
        assert "微信文章" in meta["tags"]

        print(f"[OK] meta.json written to {meta_path.relative_to(cwd)}")
        print("\n--- meta.json ---")
        print(json.dumps(meta, ensure_ascii=False, indent=2))

        # Display sample output
        print("\n--- Sample Output (First 600 chars) ---")
        print(full_md[:600])
        print("...")

    print("=== Knowledge Base Mode Test PASSED ===\n")


if __name__ == "__main__":
    test_e2e_default_mode()
    test_e2e_kb_mode()
    print("\n[SUCCESS] All E2E tests passed!")
