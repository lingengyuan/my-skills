#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for path_builder module."""

from datetime import datetime
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from config import Wechat2mdConfig
from path_builder import PathBuilder, sanitize_title


class TestSanitizeTitle:
    """Test title sanitization."""

    def test_basic_title(self):
        assert sanitize_title("Hello World") == "Hello World"

    def test_illegal_characters(self):
        result = sanitize_title("Test: A/B\\C*D?E\"F<G>H|I")
        assert ":" not in result
        assert "/" not in result
        assert "\\" not in result
        assert "*" not in result
        assert "?" not in result
        assert '"' not in result
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result

    def test_max_length(self):
        long_title = "A" * 100
        result = sanitize_title(long_title, max_len=80)
        assert len(result) <= 80

    def test_empty_title(self):
        assert sanitize_title("") == "wechat_article"

    def test_whitespace_only(self):
        assert sanitize_title("   ") == "wechat_article"

    def test_trailing_dots(self):
        result = sanitize_title("Hello...")
        assert not result.endswith(".")

    def test_multiple_whitespace(self):
        result = sanitize_title("Hello    World")
        assert result == "Hello World"

    def test_html_entities(self):
        result = sanitize_title("Test &amp; Result")
        assert result == "Test & Result"


class TestPathBuilder:
    """Test PathBuilder class."""

    @pytest.fixture
    def default_config(self):
        return Wechat2mdConfig.from_dict({})

    @pytest.fixture
    def knowledge_base_config(self):
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
            "folder": {
                "default": "20-阅读笔记",
                "enforce_whitelist": True,
            },
        })

    def test_build_slug_title_format(self, default_config):
        builder = PathBuilder(default_config)
        slug = builder.build_slug("Test Article", "https://example.com")
        assert slug == "Test Article"

    def test_build_slug_date_title_format(self):
        config = Wechat2mdConfig.from_dict({"slug": {"format": "date-title"}})
        builder = PathBuilder(config)
        date = datetime(2024, 3, 15)
        slug = builder.build_slug("Test Article", "https://example.com", date)
        assert slug == "20240315-Test Article"

    def test_build_slug_date_title_hash_format(self):
        config = Wechat2mdConfig.from_dict({"slug": {"format": "date-title-hash"}})
        builder = PathBuilder(config)
        date = datetime(2024, 3, 15)
        slug = builder.build_slug("Test Article", "https://example.com", date)
        assert slug.startswith("20240315-")
        assert len(slug.split("-")[-1]) == 6  # hash is 6 chars

    def test_build_slug_deterministic_hash(self):
        config = Wechat2mdConfig.from_dict({"slug": {"format": "date-title-hash"}})
        builder = PathBuilder(config)
        date = datetime(2024, 3, 15)
        slug1 = builder.build_slug("Test", "https://example.com/1", date)
        slug2 = builder.build_slug("Test", "https://example.com/1", date)
        slug3 = builder.build_slug("Test", "https://example.com/2", date)
        assert slug1 == slug2  # Same URL = same hash
        assert slug1 != slug3  # Different URL = different hash

    def test_build_output_path_default(self, default_config):
        builder = PathBuilder(default_config)
        cwd = Path("/test/cwd")
        path = builder.build_output_path("Test Article", "https://example.com", cwd=cwd)
        assert path == cwd / "outputs" / "Test Article"

    def test_build_output_path_with_folder(self, knowledge_base_config):
        builder = PathBuilder(knowledge_base_config)
        cwd = Path("/test/cwd")
        date = datetime(2024, 3, 15)
        path = builder.build_output_path("Test Article", "https://example.com", date, cwd)
        # Should include folder in path
        assert "20-阅读笔记" in str(path)
        assert "20240315" in str(path)

    def test_build_article_filename_default(self, default_config):
        builder = PathBuilder(default_config)
        filename = builder.build_article_filename("Test Article")
        assert filename == "Test Article.md"

    def test_build_article_filename_static(self, knowledge_base_config):
        builder = PathBuilder(knowledge_base_config)
        filename = builder.build_article_filename("Test Article")
        assert filename == "article.md"

    def test_get_images_dirname(self, default_config):
        builder = PathBuilder(default_config)
        assert builder.get_images_dirname() == "images"


class TestPathBuilderFolderValidation:
    """Test folder whitelist validation."""

    def test_folder_not_in_whitelist_warning(self, capsys):
        config = Wechat2mdConfig.from_dict({
            "output": {"path_template": "{base_dir}/{folder}/{title}"},
            "folder": {
                "default": "99-Invalid",
                "whitelist": ["00-Inbox", "20-阅读笔记"],
                "enforce_whitelist": True,
            },
        })
        builder = PathBuilder(config)
        folder = builder._get_folder()
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert folder == "00-Inbox"  # Falls back to first whitelist item

    def test_folder_valid_in_whitelist(self):
        config = Wechat2mdConfig.from_dict({
            "folder": {
                "default": "20-阅读笔记",
                "whitelist": ["00-Inbox", "20-阅读笔记"],
                "enforce_whitelist": True,
            },
        })
        builder = PathBuilder(config)
        folder = builder._get_folder()
        assert folder == "20-阅读笔记"

    def test_folder_whitelist_not_enforced(self):
        config = Wechat2mdConfig.from_dict({
            "folder": {
                "default": "99-Custom",
                "whitelist": ["00-Inbox"],
                "enforce_whitelist": False,
            },
        })
        builder = PathBuilder(config)
        folder = builder._get_folder()
        assert folder == "99-Custom"  # No validation when not enforced
