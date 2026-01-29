#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for album module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from album import (
    is_album_url,
    parse_album_url,
    AlbumInfo,
    ArticleInfo,
    DownloadResult,
    generate_index_file,
)
from config import Wechat2mdConfig, AlbumConfig


class TestIsAlbumUrl:
    """Test album URL detection."""

    def test_album_url_with_full_params(self):
        url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzYzNzQ4MTA5NA==&album_id=4350717435684012033"
        assert is_album_url(url) is True

    def test_album_url_with_extra_params(self):
        url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzYzNzQ4MTA5NA==&action=getalbum&album_id=4350717435684012033&count=3"
        assert is_album_url(url) is True

    def test_single_article_url(self):
        url = "https://mp.weixin.qq.com/s/xxxxxxxxxxxxxxxx"
        assert is_album_url(url) is False

    def test_single_article_url_with_query(self):
        url = "https://mp.weixin.qq.com/s?__biz=MzYzNzQ4MTA5NA==&mid=123&idx=1"
        assert is_album_url(url) is False

    def test_empty_url(self):
        assert is_album_url("") is False

    def test_non_wechat_url(self):
        url = "https://example.com/mp/appmsgalbum?album_id=123"
        assert is_album_url(url) is False

    def test_http_url(self):
        url = "http://mp.weixin.qq.com/mp/appmsgalbum?__biz=abc&album_id=123"
        assert is_album_url(url) is True

    def test_weixin_qq_com_domain(self):
        url = "https://weixin.qq.com/mp/appmsgalbum?__biz=abc&album_id=123"
        assert is_album_url(url) is True


class TestParseAlbumUrl:
    """Test album URL parsing."""

    def test_parse_full_url(self):
        url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzYzNzQ4MTA5NA==&album_id=4350717435684012033"
        result = parse_album_url(url)
        assert result is not None
        assert result.biz == "MzYzNzQ4MTA5NA=="
        assert result.album_id == "4350717435684012033"

    def test_parse_url_with_extra_params(self):
        url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzA1ODQ3MjQ0NA==&action=getalbum&album_id=1234567890&count=10"
        result = parse_album_url(url)
        assert result is not None
        assert result.biz == "MzA1ODQ3MjQ0NA=="
        assert result.album_id == "1234567890"

    def test_parse_missing_biz(self):
        url = "https://mp.weixin.qq.com/mp/appmsgalbum?album_id=123"
        result = parse_album_url(url)
        assert result is None

    def test_parse_missing_album_id(self):
        url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=abc"
        result = parse_album_url(url)
        assert result is None

    def test_parse_single_article_url(self):
        url = "https://mp.weixin.qq.com/s/xxxxxxxx"
        result = parse_album_url(url)
        assert result is None


class TestAlbumInfo:
    """Test AlbumInfo dataclass."""

    def test_basic_creation(self):
        info = AlbumInfo(biz="abc", album_id="123")
        assert info.biz == "abc"
        assert info.album_id == "123"
        assert info.name == ""
        assert info.article_count == 0

    def test_full_creation(self):
        info = AlbumInfo(
            biz="abc",
            album_id="123",
            name="Test Album",
            article_count=10,
        )
        assert info.name == "Test Album"
        assert info.article_count == 10


class TestArticleInfo:
    """Test ArticleInfo dataclass."""

    def test_basic_creation(self):
        info = ArticleInfo(
            title="Test Article",
            url="https://mp.weixin.qq.com/s/xxx",
            msgid="12345",
        )
        assert info.title == "Test Article"
        assert info.url == "https://mp.weixin.qq.com/s/xxx"
        assert info.msgid == "12345"
        assert info.create_time == 0

    def test_full_creation(self):
        info = ArticleInfo(
            title="Test Article",
            url="https://mp.weixin.qq.com/s/xxx",
            msgid="12345",
            create_time=1704067200,
        )
        assert info.create_time == 1704067200


class TestDownloadResult:
    """Test DownloadResult dataclass."""

    def test_success_result(self):
        article = ArticleInfo(title="Test", url="http://test", msgid="1")
        result = DownloadResult(
            article=article,
            success=True,
            output_dir=Path("/tmp/test"),
        )
        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        article = ArticleInfo(title="Test", url="http://test", msgid="1")
        result = DownloadResult(
            article=article,
            success=False,
            error="需要登录",
        )
        assert result.success is False
        assert result.error == "需要登录"


class TestAlbumConfig:
    """Test AlbumConfig dataclass and configuration loading."""

    def test_default_values(self):
        config = AlbumConfig()
        assert config.delay_seconds == 1.0
        assert config.max_articles == 0
        assert config.generate_index is True
        assert config.index_filename == "_index.md"

    def test_custom_values(self):
        config = AlbumConfig(
            delay_seconds=2.0,
            max_articles=10,
            generate_index=False,
            index_filename="index.md",
        )
        assert config.delay_seconds == 2.0
        assert config.max_articles == 10
        assert config.generate_index is False
        assert config.index_filename == "index.md"

    def test_config_from_dict(self):
        data = {
            "album": {
                "delay_seconds": 0.5,
                "max_articles": 5,
                "generate_index": True,
                "index_filename": "_index.md",
            }
        }
        config = Wechat2mdConfig.from_dict(data)
        assert config.album.delay_seconds == 0.5
        assert config.album.max_articles == 5

    def test_config_default_album(self):
        config = Wechat2mdConfig.from_dict({})
        assert config.album.delay_seconds == 1.0
        assert config.album.max_articles == 0


class TestGenerateIndexFile:
    """Test index file generation."""

    def test_generate_index_with_all_success(self):
        album = AlbumInfo(
            biz="abc",
            album_id="123",
            name="Test Album",
            article_count=2,
        )

        results = [
            DownloadResult(
                article=ArticleInfo(title="Article 1", url="http://1", msgid="1"),
                success=True,
                output_dir=Path("/tmp/001-Article 1"),
            ),
            DownloadResult(
                article=ArticleInfo(title="Article 2", url="http://2", msgid="2"),
                success=True,
                output_dir=Path("/tmp/002-Article 2"),
            ),
        ]

        config = Wechat2mdConfig.from_dict({})

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            index_path = generate_index_file(
                album=album,
                results=results,
                output_dir=output_dir,
                album_url="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=abc&album_id=123",
                config=config,
            )

            assert index_path.exists()
            content = index_path.read_text(encoding="utf-8")

            # Check frontmatter
            assert "title: Test Album" in content
            assert "type: album" in content
            assert "article_count: 2" in content

            # Check article list
            assert "## 文章列表" in content
            assert "[Article 1]" in content
            assert "[Article 2]" in content

            # No failure section
            assert "## 下载失败" not in content

    def test_generate_index_with_failures(self):
        album = AlbumInfo(
            biz="abc",
            album_id="123",
            name="Test Album",
            article_count=3,
        )

        results = [
            DownloadResult(
                article=ArticleInfo(title="Article 1", url="http://1", msgid="1"),
                success=True,
                output_dir=Path("/tmp/001-Article 1"),
            ),
            DownloadResult(
                article=ArticleInfo(title="Article 2", url="http://2", msgid="2"),
                success=False,
                error="需要登录",
            ),
            DownloadResult(
                article=ArticleInfo(title="Article 3", url="http://3", msgid="3"),
                success=False,
                error="网络超时",
            ),
        ]

        config = Wechat2mdConfig.from_dict({})

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            index_path = generate_index_file(
                album=album,
                results=results,
                output_dir=output_dir,
                album_url="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=abc&album_id=123",
                config=config,
            )

            content = index_path.read_text(encoding="utf-8")

            # Check both sections exist
            assert "## 文章列表" in content
            assert "## 下载失败" in content

            # Check failure entries
            assert "Article 2 - 需要登录" in content
            assert "Article 3 - 网络超时" in content

    def test_custom_index_filename(self):
        album = AlbumInfo(biz="abc", album_id="123", name="Test")
        results = []
        config = Wechat2mdConfig.from_dict({
            "album": {"index_filename": "README.md"}
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            index_path = generate_index_file(
                album=album,
                results=results,
                output_dir=output_dir,
                album_url="http://test",
                config=config,
            )

            assert index_path.name == "README.md"
