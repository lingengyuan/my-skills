#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for wechat2md functionality."""

import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from wechat2md import (
    fix_plain_text_urls,
    detect_code_language,
    html_to_markdown,
    sanitize_title,
)


class TestFixPlainTextUrls(unittest.TestCase):
    """Test cases for fix_plain_text_urls function."""

    def test_github_address_arrow(self):
        """Test converting 'GitHub 地址→github.com/xxx' format."""
        text = "GitHub 地址→github.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertEqual(result, "[GitHub 地址](https://github.com/user/repo)")

    def test_address_colon_chinese(self):
        """Test converting '地址：github.com/xxx' format."""
        text = "地址：github.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertEqual(result, "[地址](https://github.com/user/repo)")

    def test_address_colon_english(self):
        """Test converting '地址:github.com/xxx' format."""
        text = "地址:github.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertEqual(result, "[地址](https://github.com/user/repo)")

    def test_standalone_github_url(self):
        """Test converting standalone github.com/xxx URLs."""
        text = "> github.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertIn("[github.com/user/repo](https://github.com/user/repo)", result)

    def test_url_with_https(self):
        """Test URLs that already have https:// are not doubled."""
        text = "地址→https://github.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertEqual(result, "[地址](https://github.com/user/repo)")
        self.assertNotIn("https://https://", result)

    def test_gitee_url(self):
        """Test gitee.com URLs are also handled."""
        text = "地址→gitee.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertEqual(result, "[地址](https://gitee.com/user/repo)")

    def test_preserves_existing_markdown_links(self):
        """Test that existing markdown links are preserved."""
        text = "[My Link](https://github.com/user/repo)"
        result = fix_plain_text_urls(text)
        self.assertEqual(result, text)

    def test_multiple_urls_in_text(self):
        """Test handling multiple URLs in the same text."""
        text = """地址：github.com/user/repo1
地址：github.com/user/repo2"""
        result = fix_plain_text_urls(text)
        self.assertIn("[地址](https://github.com/user/repo1)", result)
        self.assertIn("[地址](https://github.com/user/repo2)", result)

    def test_url_in_blockquote(self):
        """Test URL in blockquote is converted."""
        text = "> GitHub 地址→github.com/user/repo"
        result = fix_plain_text_urls(text)
        self.assertIn("[GitHub 地址](https://github.com/user/repo)", result)


class TestDetectCodeLanguage(unittest.TestCase):
    """Test cases for detect_code_language function."""

    def test_detect_python(self):
        """Test Python code detection."""
        code = """import numpy as np
def calculate(x):
    return x * 2
"""
        self.assertEqual(detect_code_language(code), "python")

    def test_detect_javascript(self):
        """Test JavaScript code detection."""
        code = """const foo = () => {
    let x = 1;
    return x;
};"""
        self.assertEqual(detect_code_language(code), "javascript")

    def test_detect_typescript(self):
        """Test TypeScript code detection."""
        code = """interface User {
    name: string;
    age: number;
}
const user: User = { name: 'test', age: 20 };"""
        self.assertEqual(detect_code_language(code), "typescript")

    def test_detect_bash(self):
        """Test Bash/shell code detection."""
        code = """$ npm install package
$ git clone https://github.com/user/repo"""
        self.assertEqual(detect_code_language(code), "bash")

    def test_detect_bash_commands(self):
        """Test Bash detection via common commands."""
        code = "pip install numpy"
        self.assertEqual(detect_code_language(code), "bash")

    def test_detect_c(self):
        """Test C code detection."""
        code = """#include <stdio.h>
int main() {
    printf("Hello");
    return 0;
}"""
        self.assertEqual(detect_code_language(code), "c")

    def test_detect_cpp(self):
        """Test C++ code detection."""
        code = """#include <iostream>
int main() {
    std::cout << "Hello";
    return 0;
}"""
        self.assertEqual(detect_code_language(code), "cpp")

    def test_detect_go(self):
        """Test Go code detection."""
        code = """package main

import "fmt"

func main() {
    fmt.Println("Hello")
}"""
        self.assertEqual(detect_code_language(code), "go")

    def test_detect_rust(self):
        """Test Rust code detection."""
        code = """fn main() {
    let mut x = 5;
    println!("{}", x);
}"""
        self.assertEqual(detect_code_language(code), "rust")

    def test_detect_java(self):
        """Test Java code detection."""
        code = """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}"""
        self.assertEqual(detect_code_language(code), "java")

    def test_detect_sql(self):
        """Test SQL code detection."""
        code = "SELECT * FROM users WHERE id = 1"
        self.assertEqual(detect_code_language(code), "sql")

    def test_detect_json(self):
        """Test JSON code detection."""
        code = '{"name": "test", "value": 123}'
        self.assertEqual(detect_code_language(code), "json")

    def test_detect_yaml(self):
        """Test YAML code detection."""
        code = """name: test
version: 1.0
items:
  - name: item1"""
        self.assertEqual(detect_code_language(code), "yaml")

    def test_unknown_returns_empty(self):
        """Test that unknown code returns empty string."""
        code = "some random text that is not code"
        self.assertEqual(detect_code_language(code), "")


class TestSanitizeTitle(unittest.TestCase):
    """Test cases for sanitize_title function."""

    def test_removes_illegal_chars(self):
        """Test that illegal filesystem characters are removed."""
        title = "Test: File/Name*With?Illegal<Chars>"
        result = sanitize_title(title)
        self.assertNotIn(":", result)
        self.assertNotIn("/", result)
        self.assertNotIn("*", result)
        self.assertNotIn("?", result)
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)

    def test_truncates_long_titles(self):
        """Test that long titles are truncated."""
        title = "A" * 100
        result = sanitize_title(title)
        self.assertLessEqual(len(result), 80)

    def test_empty_title_fallback(self):
        """Test fallback for empty titles."""
        result = sanitize_title("")
        self.assertEqual(result, "wechat_article")

    def test_whitespace_normalization(self):
        """Test that whitespace is normalized."""
        title = "Test   Multiple   Spaces"
        result = sanitize_title(title)
        self.assertNotIn("   ", result)


class TestHtmlToMarkdown(unittest.TestCase):
    """Test cases for html_to_markdown function."""

    def test_paragraph_conversion(self):
        """Test basic paragraph conversion."""
        html = "<p>Hello World</p>"
        result = html_to_markdown(html)
        self.assertIn("Hello World", result)

    def test_heading_conversion(self):
        """Test heading conversion."""
        html = "<h1>Title</h1><h2>Subtitle</h2>"
        result = html_to_markdown(html)
        self.assertIn("# Title", result)
        self.assertIn("## Subtitle", result)

    def test_bold_conversion(self):
        """Test bold text conversion."""
        html = "<p><strong>Bold Text</strong></p>"
        result = html_to_markdown(html)
        self.assertIn("**Bold Text**", result)

    def test_italic_conversion(self):
        """Test italic text conversion."""
        html = "<p><em>Italic Text</em></p>"
        result = html_to_markdown(html)
        self.assertIn("*Italic Text*", result)

    def test_link_conversion(self):
        """Test link conversion."""
        html = '<p><a href="https://example.com">Link Text</a></p>'
        result = html_to_markdown(html)
        self.assertIn("[Link Text](https://example.com)", result)

    def test_code_block_conversion(self):
        """Test code block conversion."""
        html = "<pre>print('hello')</pre>"
        result = html_to_markdown(html)
        self.assertIn("```", result)
        self.assertIn("print('hello')", result)

    def test_blockquote_conversion(self):
        """Test blockquote conversion."""
        html = "<blockquote>Quote text</blockquote>"
        result = html_to_markdown(html)
        self.assertIn("> Quote text", result)

    def test_list_conversion(self):
        """Test unordered list conversion."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = html_to_markdown(html)
        self.assertIn("- Item 1", result)
        self.assertIn("- Item 2", result)

    def test_ordered_list_conversion(self):
        """Test ordered list conversion."""
        html = "<ol><li>First</li><li>Second</li></ol>"
        result = html_to_markdown(html)
        self.assertIn("1. First", result)
        self.assertIn("2. Second", result)

    def test_image_placeholder(self):
        """Test image placeholder conversion."""
        html = '<wechat2md-img src="./images/001.png" alt="test"></wechat2md-img>'
        result = html_to_markdown(html)
        self.assertIn("![test](./images/001.png)", result)

    def test_span_bold_style_conversion(self):
        """Test span with bold style is converted to markdown."""
        html = '<p><span style="font-weight:bold">Bold via style</span></p>'
        result = html_to_markdown(html)
        self.assertIn("**Bold via style**", result)

    def test_nested_sections_separation(self):
        """Test that nested sections create separate paragraphs."""
        html = """<section>
            <section><p>Paragraph 1</p></section>
            <section><p>Paragraph 2</p></section>
        </section>"""
        result = html_to_markdown(html)
        # Both paragraphs should be present and separated
        self.assertIn("Paragraph 1", result)
        self.assertIn("Paragraph 2", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete conversion pipeline."""

    def test_full_article_structure(self):
        """Test that a complete article structure is properly converted."""
        html = """
        <section>
            <h2>Section Title</h2>
            <p>Introduction paragraph with <strong>bold</strong> text.</p>
            <wechat2md-img src="./images/001.png"></wechat2md-img>
            <p>Description after image.</p>
            <pre>print("hello")</pre>
        </section>
        """
        result = html_to_markdown(html)

        # Check structure
        self.assertIn("## Section Title", result)
        self.assertIn("**bold**", result)
        self.assertIn("![](./images/001.png)", result)
        self.assertIn("```", result)
        self.assertIn('print("hello")', result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
