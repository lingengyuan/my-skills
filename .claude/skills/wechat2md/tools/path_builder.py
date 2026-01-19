#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Path builder for wechat2md.

Handles slug generation and path template expansion.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Optional

try:
    from .config import Wechat2mdConfig
except ImportError:
    from config import Wechat2mdConfig


_ILLEGAL_FS_CHARS = re.compile(r"[\\/:*?\"<>|]+")
_WHITESPACE = re.compile(r"\s+")


def sanitize_title(title: str, max_len: int = 80) -> str:
    """Sanitize title for filesystem use."""
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


class PathBuilder:
    """Builds output paths based on configuration."""

    def __init__(self, config: Wechat2mdConfig):
        self.config = config

    def build_slug(self, title: str, url: str, date: Optional[datetime] = None) -> str:
        """Generate slug based on configuration.

        Args:
            title: Article title (already sanitized)
            url: Article URL (used for hash)
            date: Article date (defaults to current date)

        Returns:
            Slug string based on configured format:
            - "title": Just the sanitized title
            - "date-title": YYYYMMDD-title
            - "date-title-hash": YYYYMMDD-title-abcdef
        """
        slug_format = self.config.slug.format
        max_length = self.config.slug.max_length

        sanitized = sanitize_title(title, max_len=max_length)

        if slug_format == "title":
            return sanitized

        if date is None:
            date = datetime.now()
        date_prefix = date.strftime("%Y%m%d")

        if slug_format == "date-title":
            # Reserve space for date prefix and separator
            title_max = max_length - len(date_prefix) - 1
            truncated_title = sanitize_title(title, max_len=title_max)
            return f"{date_prefix}-{truncated_title}"

        if slug_format == "date-title-hash":
            # Generate short hash from URL
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:6]
            # Reserve space for date, hash, and separators
            title_max = max_length - len(date_prefix) - len(url_hash) - 2
            truncated_title = sanitize_title(title, max_len=max(title_max, 10))
            return f"{date_prefix}-{truncated_title}-{url_hash}"

        # Fallback to title format
        return sanitized

    def build_output_path(
        self,
        title: str,
        url: str,
        date: Optional[datetime] = None,
        cwd: Optional[Path] = None
    ) -> Path:
        """Build the output directory path.

        Args:
            title: Article title (raw, will be sanitized)
            url: Article URL
            date: Article date (for date-based slugs)
            cwd: Working directory (defaults to current directory)

        Returns:
            Path to output directory.
        """
        if cwd is None:
            cwd = Path.cwd()

        slug = self.build_slug(title, url, date)
        sanitized_title = sanitize_title(title, self.config.slug.max_length)

        # Build template variables
        variables = {
            "base_dir": self.config.output.base_dir,
            "title": sanitized_title,
            "slug": slug,
            "folder": self._get_folder(),
        }

        # Expand path template
        path_template = self.config.output.path_template
        path_str = path_template.format(**variables)

        return cwd / path_str

    def build_article_filename(self, title: str) -> str:
        """Build the article filename.

        Args:
            title: Article title (raw, will be sanitized)

        Returns:
            Filename string (e.g., "article.md" or "My Article.md")
        """
        sanitized_title = sanitize_title(title, self.config.slug.max_length)
        filename_template = self.config.output.article_filename
        return filename_template.format(title=sanitized_title)

    def get_images_dirname(self) -> str:
        """Get the images subdirectory name."""
        return self.config.output.images_dirname

    def _get_folder(self) -> str:
        """Get the folder name from config.

        Returns:
            Folder name or empty string if not configured.
        """
        folder = self.config.folder.default
        if folder is None:
            return ""

        # Validate against whitelist if enforcement is enabled
        if self.config.folder.enforce_whitelist:
            if folder not in self.config.folder.whitelist:
                import sys
                print(
                    f"WARNING: Folder '{folder}' not in whitelist, using first whitelist item",
                    file=sys.stderr
                )
                return self.config.folder.whitelist[0] if self.config.folder.whitelist else ""

        return folder
