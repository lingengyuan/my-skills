#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for config module."""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from config import (
    DEFAULT_CONFIG,
    Wechat2mdConfig,
    load_config,
    find_config_file,
    _deep_merge,
)


class TestDefaultConfig:
    """Test default configuration values."""

    def test_default_config_has_required_keys(self):
        assert "schema_version" in DEFAULT_CONFIG
        assert "output" in DEFAULT_CONFIG
        assert "slug" in DEFAULT_CONFIG
        assert "frontmatter" in DEFAULT_CONFIG
        assert "folder" in DEFAULT_CONFIG
        assert "tags" in DEFAULT_CONFIG
        assert "meta" in DEFAULT_CONFIG

    def test_default_output_config(self):
        output = DEFAULT_CONFIG["output"]
        assert output["base_dir"] == "outputs"
        assert output["path_template"] == "{base_dir}/{title}"
        assert output["article_filename"] == "{title}.md"
        assert output["images_dirname"] == "images"

    def test_default_frontmatter_disabled(self):
        assert DEFAULT_CONFIG["frontmatter"]["enabled"] is False

    def test_default_meta_disabled(self):
        assert DEFAULT_CONFIG["meta"]["enabled"] is False


class TestWechat2mdConfig:
    """Test Wechat2mdConfig dataclass."""

    def test_from_dict_with_defaults(self):
        config = Wechat2mdConfig.from_dict({})
        assert config.schema_version == "1.0"
        assert config.output.base_dir == "outputs"
        assert config.frontmatter.enabled is False

    def test_from_dict_with_custom_values(self):
        data = {
            "schema_version": "1.0",
            "output": {
                "base_dir": "custom_outputs",
                "path_template": "{base_dir}/{folder}/{slug}",
            },
            "frontmatter": {
                "enabled": True,
            },
        }
        config = Wechat2mdConfig.from_dict(data)
        assert config.output.base_dir == "custom_outputs"
        assert config.output.path_template == "{base_dir}/{folder}/{slug}"
        assert config.frontmatter.enabled is True
        # Defaults for unspecified
        assert config.output.images_dirname == "images"

    def test_from_dict_with_full_config(self):
        data = {
            "schema_version": "1.0",
            "output": {
                "base_dir": "outputs",
                "path_template": "{base_dir}/{folder}/{slug}",
                "article_filename": "article.md",
                "images_dirname": "images",
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
                "whitelist": ["00-Inbox", "20-阅读笔记"],
                "enforce_whitelist": True,
            },
            "tags": {
                "default_tags": ["微信文章"],
                "max_count": 8,
            },
            "meta": {
                "enabled": True,
            },
        }
        config = Wechat2mdConfig.from_dict(data)
        assert config.slug.format == "date-title-hash"
        assert config.folder.default == "20-阅读笔记"
        assert config.folder.enforce_whitelist is True
        assert "微信文章" in config.tags.default_tags
        assert config.meta.enabled is True


class TestDeepMerge:
    """Test deep merge functionality."""

    def test_simple_merge(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"y": 10, "z": 20}}
        result = _deep_merge(base, override)
        assert result == {"a": {"x": 1, "y": 10, "z": 20}, "b": 3}

    def test_override_non_dict_with_dict(self):
        base = {"a": 1}
        override = {"a": {"x": 2}}
        result = _deep_merge(base, override)
        assert result == {"a": {"x": 2}}

    def test_does_not_modify_original(self):
        base = {"a": 1}
        override = {"b": 2}
        result = _deep_merge(base, override)
        assert "b" not in base


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_config_without_file(self):
        with mock.patch("config.find_config_file", return_value=None):
            config = load_config()
            assert config.frontmatter.enabled is False
            assert config.output.base_dir == "outputs"

    def test_load_config_with_file(self):
        config_data = {
            "frontmatter": {"enabled": True},
            "folder": {"default": "20-阅读笔记"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            config_path = Path(f.name)

        try:
            with mock.patch("config.find_config_file", return_value=config_path):
                config = load_config()
                assert config.frontmatter.enabled is True
                assert config.folder.default == "20-阅读笔记"
                # Default values still present
                assert config.output.base_dir == "outputs"
        finally:
            config_path.unlink()

    def test_load_config_with_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json {")
            f.flush()
            config_path = Path(f.name)

        try:
            with mock.patch("config.find_config_file", return_value=config_path):
                # Should fall back to defaults
                config = load_config()
                assert config.frontmatter.enabled is False
        finally:
            config_path.unlink()
