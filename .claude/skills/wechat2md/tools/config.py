#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration loader for wechat2md.

Provides default configuration (v1 compatible behavior) and merges with
config.json if present.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# Default configuration - maintains v1 behavior when no config.json exists
DEFAULT_CONFIG: Dict[str, Any] = {
    "schema_version": "1.0",
    "output": {
        "base_dir": "outputs",
        "path_template": "{base_dir}/{title}",
        "article_filename": "{title}.md",
        "images_dirname": "images"
    },
    "slug": {
        "format": "title",  # title | date-title | date-title-hash
        "max_length": 80
    },
    "frontmatter": {
        "enabled": False,
        "include_fields": ["title", "author", "created", "source", "tags"]
    },
    "folder": {
        "default": None,
        "whitelist": [
            "00-Inbox",
            "10-项目",
            "20-阅读笔记",
            "30-方法论",
            "40-工具脚本",
            "50-运维排障",
            "60-数据与表",
            "90-归档"
        ],
        "enforce_whitelist": False
    },
    "tags": {
        "default_tags": [],
        "max_count": 8
    },
    "meta": {
        "enabled": False
    },
    "album": {
        "delay_seconds": 1.0,
        "max_articles": 0,
        "generate_index": True,
        "index_filename": "_index.md"
    }
}


@dataclass
class OutputConfig:
    base_dir: str = "outputs"
    path_template: str = "{base_dir}/{title}"
    article_filename: str = "{title}.md"
    images_dirname: str = "images"


@dataclass
class SlugConfig:
    format: str = "title"  # title | date-title | date-title-hash
    max_length: int = 80


@dataclass
class FrontmatterConfig:
    enabled: bool = False
    include_fields: List[str] = field(default_factory=lambda: ["title", "author", "created", "source", "tags"])


@dataclass
class FolderConfig:
    default: Optional[str] = None
    whitelist: List[str] = field(default_factory=lambda: [
        "00-Inbox",
        "10-项目",
        "20-阅读笔记",
        "30-方法论",
        "40-工具脚本",
        "50-运维排障",
        "60-数据与表",
        "90-归档"
    ])
    enforce_whitelist: bool = False


@dataclass
class TagsConfig:
    default_tags: List[str] = field(default_factory=list)
    max_count: int = 8


@dataclass
class MetaConfig:
    enabled: bool = False


@dataclass
class AlbumConfig:
    """Configuration for album/collection downloads."""
    delay_seconds: float = 1.0      # Delay between article downloads
    max_articles: int = 0           # 0 = no limit
    generate_index: bool = True     # Generate _index.md
    index_filename: str = "_index.md"


@dataclass
class Wechat2mdConfig:
    """Main configuration class for wechat2md."""
    schema_version: str = "1.0"
    output: OutputConfig = field(default_factory=OutputConfig)
    slug: SlugConfig = field(default_factory=SlugConfig)
    frontmatter: FrontmatterConfig = field(default_factory=FrontmatterConfig)
    folder: FolderConfig = field(default_factory=FolderConfig)
    tags: TagsConfig = field(default_factory=TagsConfig)
    meta: MetaConfig = field(default_factory=MetaConfig)
    album: AlbumConfig = field(default_factory=AlbumConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Wechat2mdConfig":
        """Create config from dictionary, using defaults for missing values."""
        return cls(
            schema_version=data.get("schema_version", "1.0"),
            output=OutputConfig(
                base_dir=data.get("output", {}).get("base_dir", "outputs"),
                path_template=data.get("output", {}).get("path_template", "{base_dir}/{title}"),
                article_filename=data.get("output", {}).get("article_filename", "{title}.md"),
                images_dirname=data.get("output", {}).get("images_dirname", "images"),
            ),
            slug=SlugConfig(
                format=data.get("slug", {}).get("format", "title"),
                max_length=data.get("slug", {}).get("max_length", 80),
            ),
            frontmatter=FrontmatterConfig(
                enabled=data.get("frontmatter", {}).get("enabled", False),
                include_fields=data.get("frontmatter", {}).get(
                    "include_fields", ["title", "author", "created", "source", "tags"]
                ),
            ),
            folder=FolderConfig(
                default=data.get("folder", {}).get("default"),
                whitelist=data.get("folder", {}).get("whitelist", [
                    "00-Inbox", "10-项目", "20-阅读笔记", "30-方法论",
                    "40-工具脚本", "50-运维排障", "60-数据与表", "90-归档"
                ]),
                enforce_whitelist=data.get("folder", {}).get("enforce_whitelist", False),
            ),
            tags=TagsConfig(
                default_tags=data.get("tags", {}).get("default_tags", []),
                max_count=data.get("tags", {}).get("max_count", 8),
            ),
            meta=MetaConfig(
                enabled=data.get("meta", {}).get("enabled", False),
            ),
            album=AlbumConfig(
                delay_seconds=data.get("album", {}).get("delay_seconds", 1.0),
                max_articles=data.get("album", {}).get("max_articles", 0),
                generate_index=data.get("album", {}).get("generate_index", True),
                index_filename=data.get("album", {}).get("index_filename", "_index.md"),
            ),
        )


def find_config_file() -> Optional[Path]:
    """Find config.json in the wechat2md skill directory.

    Searches relative to this module's location.
    """
    # config.json should be in the parent directory of tools/
    module_dir = Path(__file__).parent  # tools/
    skill_dir = module_dir.parent       # wechat2md/
    config_path = skill_dir / "config.json"

    if config_path.exists():
        return config_path
    return None


def load_config() -> Wechat2mdConfig:
    """Load configuration from config.json, falling back to defaults.

    Returns:
        Wechat2mdConfig with merged settings (config.json overrides defaults).
    """
    config_path = find_config_file()

    if config_path is None:
        # No config file - use v1 defaults
        return Wechat2mdConfig.from_dict(DEFAULT_CONFIG)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        # Config file exists but is invalid - warn and use defaults
        import sys
        print(f"WARNING: Failed to load config.json: {e}", file=sys.stderr)
        return Wechat2mdConfig.from_dict(DEFAULT_CONFIG)

    # Merge user config with defaults
    merged = _deep_merge(DEFAULT_CONFIG.copy(), user_config)
    return Wechat2mdConfig.from_dict(merged)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge override into base, returning a new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
