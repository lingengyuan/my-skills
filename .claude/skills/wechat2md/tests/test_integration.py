#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration tests for wechat2md - testing complete workflows."""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from config import load_config, Wechat2mdConfig
from path_builder import PathBuilder
from frontmatter import FrontmatterGenerator
from wechat2md import (
    build_md_document,
    extract_author,
    html_to_markdown,
    write_meta_json,
)


class TestDefaultMode:
    """Test v1 behavior without config file."""

    def test_default_config_loads_without_file(self):
        """Verify default config when no config.json exists."""
        with mock.patch("config.find_config_file", return_value=None):
            config = load_config()
            assert config.output.base_dir == "outputs"
            assert config.output.path_template == "{base_dir}/{title}"
            assert config.output.article_filename == "{title}.md"
            assert config.frontmatter.enabled is False
            assert config.meta.enabled is False

    def test_default_path_building(self):
        """Verify v1 path structure."""
        config = Wechat2mdConfig.from_dict({})
        builder = PathBuilder(config)

        cwd = Path("/test")
        path = builder.build_output_path("测试文章", "https://example.com", cwd=cwd)
        filename = builder.build_article_filename("测试文章")

        assert path == cwd / "outputs" / "测试文章"
        assert filename == "测试文章.md"

    def test_no_frontmatter_in_default_mode(self):
        """Verify no frontmatter generated in default mode."""
        config = Wechat2mdConfig.from_dict({})
        gen = FrontmatterGenerator(config)
        result = gen.generate(title="测试")
        assert result == ""

    def test_no_meta_json_in_default_mode(self):
        """Verify no meta.json generated in default mode."""
        config = Wechat2mdConfig.from_dict({})
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = write_meta_json(
                output_dir, "Test", "https://example.com", None,
                datetime.now(), config
            )
            assert result is None
            assert not (output_dir / "meta.json").exists()


class TestKnowledgeBaseMode:
    """Test knowledge base integration with config."""

    @pytest.fixture
    def kb_config(self):
        return Wechat2mdConfig.from_dict({
            "output": {
                "base_dir": "outputs",
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
                "enforce_whitelist": True,
            },
            "tags": {
                "default_tags": ["微信文章", "阅读笔记"],
                "max_count": 8,
            },
            "meta": {
                "enabled": True,
            },
        })

    def test_kb_path_building(self, kb_config):
        """Verify knowledge base path structure."""
        builder = PathBuilder(kb_config)
        cwd = Path("/test")
        date = datetime(2024, 3, 15)

        path = builder.build_output_path("测试文章", "https://example.com/123", date, cwd)
        filename = builder.build_article_filename("测试文章")

        assert "20-阅读笔记" in str(path)
        assert "20240315" in str(path)
        assert len(str(path).split("-")[-1]) == 6  # hash
        assert filename == "article.md"

    def test_kb_frontmatter_generation(self, kb_config):
        """Verify frontmatter generation in KB mode."""
        gen = FrontmatterGenerator(kb_config)
        created = datetime(2024, 3, 15, 10, 30)

        result = gen.generate(
            title="测试文章",
            author="作者",
            source_url="https://mp.weixin.qq.com/s/123",
            created=created,
        )

        assert result.startswith("---")
        assert "title: 测试文章" in result
        assert "author: 作者" in result
        assert "created: 2024-03-15" in result
        assert "source:" in result
        assert "微信文章" in result
        assert "阅读笔记" in result

    def test_kb_meta_json_generation(self, kb_config):
        """Verify meta.json generation in KB mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            created = datetime(2024, 3, 15, 10, 30)

            meta_path = write_meta_json(
                output_dir, "测试文章", "https://example.com",
                "作者", created, kb_config
            )

            assert meta_path is not None
            assert meta_path.exists()

            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            assert meta["title"] == "测试文章"
            assert meta["source_url"] == "https://example.com"
            assert meta["folder"] == "20-阅读笔记"
            assert meta["author"] == "作者"
            assert "微信文章" in meta["tags"]


class TestMarkdownOutputFormat:
    """Test markdown document output format."""

    def test_basic_document_structure(self):
        """Verify basic markdown document structure."""
        body_md = "This is a test paragraph.\n\n**Bold text** and *italic text*."
        result = build_md_document("Test Title", body_md, [])

        assert "# Test Title" in result
        assert "This is a test paragraph" in result
        assert "**Bold text**" in result
        assert "*italic text*" in result

    def test_document_with_image_failures(self):
        """Verify image failure list in document."""
        from wechat2md import ImageItem

        manifest = [
            ImageItem(1, "https://example.com/1.jpg", "001.jpg", "./images/001.jpg", True),
            ImageItem(2, "https://example.com/2.jpg", "002.jpg", "./images/002.jpg", False, "timeout"),
            ImageItem(3, "https://example.com/3.jpg", "003.jpg", "./images/003.jpg", False, "404 Not Found"),
        ]

        result = build_md_document("Test", "Body content", manifest)

        assert "图片下载失败列表" in result
        assert "002: https://example.com/2.jpg" in result
        assert "003: https://example.com/3.jpg" in result
        assert "timeout" in result
        assert "404 Not Found" in result

    def test_html_conversion_preserves_structure(self):
        """Verify HTML to Markdown conversion preserves structure."""
        html = """
        <h2>Section Title</h2>
        <p>First paragraph with <strong>bold</strong> text.</p>
        <p>Second paragraph with <em>italic</em> text.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        """

        result = html_to_markdown(html)

        assert "## Section Title" in result
        assert "**bold**" in result
        assert "*italic*" in result
        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_code_block_conversion(self):
        """Verify code blocks are properly converted."""
        html = """
        <pre>function test() {
    console.log("Hello");
}</pre>
        """

        result = html_to_markdown(html)

        assert "```javascript" in result
        assert "function test()" in result
        assert "console.log" in result
        assert "```" in result

    def test_author_extraction(self):
        """Verify author extraction from HTML."""
        html_with_author = """
        <html>
        <head>
            <meta name="author" content="测试作者">
        </head>
        <body>
            <div id="js_name">公众号名称</div>
        </body>
        </html>
        """

        author = extract_author(html_with_author)
        assert author == "测试作者"

    def test_author_extraction_fallback(self):
        """Verify author extraction falls back to js_name."""
        html_fallback = """
        <html>
        <body>
            <div id="js_name">公众号名称</div>
        </body>
        </html>
        """

        author = extract_author(html_fallback)
        assert author == "公众号名称"


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    def test_default_workflow(self):
        """Simulate complete default workflow."""
        config = Wechat2mdConfig.from_dict({})
        builder = PathBuilder(config)
        fm_gen = FrontmatterGenerator(config)

        # Simulate article data
        title = "测试文章标题"
        url = "https://mp.weixin.qq.com/s/abc123"
        body_md = "文章正文内容\n\n**粗体**和*斜体*。"

        # Build paths
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            output_dir = builder.build_output_path(title, url, cwd=cwd)
            article_filename = builder.build_article_filename(title)

            # Verify path structure
            assert output_dir == cwd / "outputs" / title
            assert article_filename == f"{title}.md"

            # Generate frontmatter (should be empty)
            fm = fm_gen.generate(title=title, source_url=url)
            assert fm == ""

            # Build document
            doc = build_md_document(title, body_md, [])
            assert f"# {title}" in doc
            assert "文章正文内容" in doc

    def test_kb_workflow(self):
        """Simulate complete knowledge base workflow."""
        config = Wechat2mdConfig.from_dict({
            "output": {
                "path_template": "{base_dir}/{folder}/{slug}",
                "article_filename": "article.md",
            },
            "slug": {"format": "date-title-hash"},
            "frontmatter": {"enabled": True, "include_fields": ["title", "source", "tags"]},
            "folder": {"default": "20-阅读笔记"},
            "tags": {"default_tags": ["微信文章"]},
            "meta": {"enabled": True},
        })

        builder = PathBuilder(config)
        fm_gen = FrontmatterGenerator(config)

        # Simulate article data
        title = "知识库测试文章"
        url = "https://mp.weixin.qq.com/s/xyz789"
        created = datetime(2024, 3, 15)
        body_md = "知识库文章内容"

        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)

            # Build paths
            output_dir = builder.build_output_path(title, url, created, cwd)
            article_filename = builder.build_article_filename(title)

            # Verify KB path structure
            assert "20-阅读笔记" in str(output_dir)
            assert "20240315" in str(output_dir)
            assert article_filename == "article.md"

            # Generate frontmatter
            fm = fm_gen.generate(title=title, source_url=url, created=created)
            assert "---" in fm
            assert "title:" in fm
            assert "微信文章" in fm

            # Create output directory and write meta.json
            output_dir.mkdir(parents=True, exist_ok=True)
            meta_path = write_meta_json(output_dir, title, url, None, created, config)
            assert meta_path.exists()

            # Build complete document
            doc = build_md_document(title, body_md, [])
            full_doc = fm + doc

            # Verify complete document
            assert full_doc.startswith("---")
            assert f"# {title}" in full_doc
            assert "知识库文章内容" in full_doc
