#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YAML frontmatter generator for wechat2md.

Generates YAML frontmatter for Obsidian-style markdown notes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from .config import Wechat2mdConfig
except ImportError:
    from config import Wechat2mdConfig


class FrontmatterGenerator:
    """Generates YAML frontmatter for markdown articles."""

    def __init__(self, config: Wechat2mdConfig):
        self.config = config

    def generate(
        self,
        title: str,
        author: Optional[str] = None,
        source_url: Optional[str] = None,
        created: Optional[datetime] = None,
        extra_tags: Optional[List[str]] = None,
    ) -> str:
        """Generate YAML frontmatter string.

        Args:
            title: Article title
            author: Article author (optional)
            source_url: Source URL (optional)
            created: Creation date (defaults to now)
            extra_tags: Additional tags to merge with default_tags

        Returns:
            YAML frontmatter string (including --- delimiters) or empty string if disabled.
        """
        if not self.config.frontmatter.enabled:
            return ""

        if created is None:
            created = datetime.now()

        # Build the frontmatter data
        data: Dict[str, Any] = {}
        include_fields = self.config.frontmatter.include_fields

        if "title" in include_fields:
            data["title"] = title

        if "author" in include_fields and author:
            data["author"] = author

        if "created" in include_fields:
            data["created"] = created.strftime("%Y-%m-%d")

        if "source" in include_fields and source_url:
            data["source"] = source_url

        if "tags" in include_fields:
            tags = self._build_tags(extra_tags)
            if tags:
                data["tags"] = tags

        if not data:
            return ""

        # Generate YAML
        yaml_lines = ["---"]
        for key, value in data.items():
            yaml_lines.append(self._format_yaml_field(key, value))
        yaml_lines.append("---")
        yaml_lines.append("")  # Trailing newline

        return "\n".join(yaml_lines)

    def _build_tags(self, extra_tags: Optional[List[str]] = None) -> List[str]:
        """Build the final tags list, respecting max_count."""
        tags: List[str] = []

        # Add default tags first
        tags.extend(self.config.tags.default_tags)

        # Add extra tags
        if extra_tags:
            for tag in extra_tags:
                if tag not in tags:
                    tags.append(tag)

        # Enforce max count
        max_count = self.config.tags.max_count
        if max_count > 0 and len(tags) > max_count:
            tags = tags[:max_count]

        return tags

    def _format_yaml_field(self, key: str, value: Any) -> str:
        """Format a single YAML field."""
        if isinstance(value, list):
            if not value:
                return f"{key}: []"
            # Format as YAML list
            items = ", ".join(self._escape_yaml_string(str(v)) for v in value)
            return f"{key}: [{items}]"
        elif isinstance(value, str):
            return f"{key}: {self._escape_yaml_string(value)}"
        elif isinstance(value, bool):
            return f"{key}: {'true' if value else 'false'}"
        elif value is None:
            return f"{key}: null"
        else:
            return f"{key}: {value}"

    def _escape_yaml_string(self, s: str) -> str:
        """Escape a string for YAML if needed."""
        # Check if quoting is needed
        needs_quotes = False

        # Empty string needs quotes
        if not s:
            return '""'

        # Check for special characters
        special_chars = [':', '#', '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', "'", '"', '%', '@', '`']
        if any(c in s for c in special_chars):
            needs_quotes = True

        # Check for leading/trailing whitespace
        if s != s.strip():
            needs_quotes = True

        # Check for newlines
        if '\n' in s or '\r' in s:
            needs_quotes = True

        # Check if it looks like a number or boolean
        if s.lower() in ('true', 'false', 'yes', 'no', 'null', 'on', 'off'):
            needs_quotes = True

        try:
            float(s)
            needs_quotes = True
        except ValueError:
            pass

        if needs_quotes:
            # Use double quotes and escape internal quotes
            escaped = s.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'

        return s
