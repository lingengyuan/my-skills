#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for frontmatter module."""

from datetime import datetime
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from config import Wechat2mdConfig
from frontmatter import FrontmatterGenerator


class TestFrontmatterGenerator:
    """Test FrontmatterGenerator class."""

    @pytest.fixture
    def disabled_config(self):
        return Wechat2mdConfig.from_dict({"frontmatter": {"enabled": False}})

    @pytest.fixture
    def enabled_config(self):
        return Wechat2mdConfig.from_dict({
            "frontmatter": {
                "enabled": True,
                "include_fields": ["title", "author", "created", "source", "tags"],
            },
            "tags": {
                "default_tags": ["微信文章", "阅读笔记"],
                "max_count": 8,
            },
        })

    def test_generate_disabled(self, disabled_config):
        gen = FrontmatterGenerator(disabled_config)
        result = gen.generate("Test Title")
        assert result == ""

    def test_generate_enabled_basic(self, enabled_config):
        gen = FrontmatterGenerator(enabled_config)
        created = datetime(2024, 3, 15, 10, 30, 0)
        result = gen.generate(
            title="Test Title",
            author="Test Author",
            source_url="https://example.com",
            created=created,
        )
        assert result.startswith("---")
        assert "---\n" in result  # closing delimiter present
        assert "title: Test Title" in result
        assert "author: Test Author" in result
        assert "created: 2024-03-15" in result
        assert "source:" in result  # URL may be quoted
        assert "example.com" in result

    def test_generate_with_default_tags(self, enabled_config):
        gen = FrontmatterGenerator(enabled_config)
        result = gen.generate(title="Test")
        assert "tags:" in result
        assert "微信文章" in result
        assert "阅读笔记" in result

    def test_generate_with_extra_tags(self, enabled_config):
        gen = FrontmatterGenerator(enabled_config)
        result = gen.generate(title="Test", extra_tags=["自定义标签"])
        assert "自定义标签" in result
        assert "微信文章" in result

    def test_generate_tags_deduplication(self, enabled_config):
        gen = FrontmatterGenerator(enabled_config)
        result = gen.generate(title="Test", extra_tags=["微信文章", "新标签"])
        # Should not have duplicate 微信文章
        assert result.count("微信文章") == 1

    def test_generate_tags_max_count(self):
        config = Wechat2mdConfig.from_dict({
            "frontmatter": {"enabled": True, "include_fields": ["tags"]},
            "tags": {
                "default_tags": ["tag1", "tag2", "tag3"],
                "max_count": 2,
            },
        })
        gen = FrontmatterGenerator(config)
        result = gen.generate(title="Test")
        # Should only have 2 tags due to max_count
        assert "tag1" in result
        assert "tag2" in result
        assert "tag3" not in result

    def test_generate_without_optional_fields(self, enabled_config):
        gen = FrontmatterGenerator(enabled_config)
        result = gen.generate(title="Test Title")
        assert "title: Test Title" in result
        assert "author:" not in result  # author not provided

    def test_generate_partial_fields(self):
        config = Wechat2mdConfig.from_dict({
            "frontmatter": {
                "enabled": True,
                "include_fields": ["title", "created"],
            },
        })
        gen = FrontmatterGenerator(config)
        result = gen.generate(
            title="Test",
            author="Author",  # Will be ignored
            source_url="https://example.com",  # Will be ignored
        )
        assert "title: Test" in result
        assert "author:" not in result
        assert "source:" not in result


class TestYamlEscaping:
    """Test YAML string escaping."""

    @pytest.fixture
    def gen(self):
        config = Wechat2mdConfig.from_dict({
            "frontmatter": {"enabled": True, "include_fields": ["title"]},
        })
        return FrontmatterGenerator(config)

    def test_escape_colon(self, gen):
        result = gen.generate(title="Test: With Colon")
        assert '"Test: With Colon"' in result

    def test_escape_quotes(self, gen):
        result = gen.generate(title='Test "Quoted"')
        assert 'Test \\"Quoted\\"' in result

    def test_escape_special_chars(self, gen):
        result = gen.generate(title="Test #hashtag")
        assert '"Test #hashtag"' in result

    def test_no_escape_simple_string(self, gen):
        result = gen.generate(title="Simple Title")
        # Should not be quoted
        assert "title: Simple Title" in result
        assert '"Simple Title"' not in result

    def test_escape_boolean_like(self, gen):
        result = gen.generate(title="true")
        assert '"true"' in result

    def test_escape_number_like(self, gen):
        result = gen.generate(title="123")
        assert '"123"' in result


class TestEmptyFrontmatter:
    """Test edge cases for empty frontmatter."""

    def test_no_fields_enabled(self):
        config = Wechat2mdConfig.from_dict({
            "frontmatter": {
                "enabled": True,
                "include_fields": [],
            },
        })
        gen = FrontmatterGenerator(config)
        result = gen.generate(title="Test")
        assert result == ""  # No fields to include

    def test_empty_tags_list(self):
        config = Wechat2mdConfig.from_dict({
            "frontmatter": {
                "enabled": True,
                "include_fields": ["tags"],
            },
            "tags": {
                "default_tags": [],
            },
        })
        gen = FrontmatterGenerator(config)
        result = gen.generate(title="Test")
        # Empty tags should not produce tags field
        assert result == ""
