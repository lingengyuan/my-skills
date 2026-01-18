#!/usr/bin/env python3
import argparse
import html
import os
import re
import sys


THEMES = {
    "autumn-warm": {
        "styles": {
            "container": "background-color:#FFFFFF;color:#494949;font-family:PingFang SC,-apple-system-font,system-ui,Helvetica Neue,Hiragino Sans GB,Microsoft YaHei UI,Microsoft YaHei,Arial,sans-serif;font-size:15px;line-height:1.75em;max-width:700px;margin:0 auto;padding:8px 0;box-sizing:border-box;word-wrap:break-word;",
            "paragraph": "margin:0 16px;text-align:justify;line-height:1.75em;text-indent:0;font-size:15px;color:#494949;letter-spacing:0;",
            "h1": "margin:24px 16px 12px;text-align:center;font-size:20px;font-weight:700;line-height:1.6em;color:#DC801F;letter-spacing:0.04em;",
            "h2": "margin:20px 16px 10px;text-align:left;font-size:17px;font-weight:700;line-height:1.6em;color:#DC801F;",
            "h3": "margin:16px 16px 8px;text-align:left;font-size:15px;font-weight:700;line-height:1.6em;color:#C94747;",
            "image": "max-width:100%;height:auto;display:block;margin:8px auto;",
            "ul": "margin:8px 16px;padding-left:20px;line-height:1.75em;color:#494949;font-size:15px;",
            "ol": "margin:8px 16px;padding-left:20px;line-height:1.75em;color:#494949;font-size:15px;",
            "li": "margin:4px 0;line-height:1.75em;text-align:justify;",
            "strong": "font-weight:700;",
            "em": "font-style:italic;",
            "code": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:0.95em;background:#F6F6F6;padding:2px 4px;border-radius:3px;",
            "pre": "background:#F6F6F6;padding:12px 16px;border-radius:4px;overflow:auto;margin:12px 16px;",
            "preCode": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:0.95em;line-height:1.6em;white-space:pre;letter-spacing:0;word-break:normal;",
            "link": "color:#DC801F;text-decoration:none;border-bottom:1px solid rgba(220,128,31,0.3);",
            "blockquote": "margin:12px 16px;padding:8px 12px;color:#494949;background:rgba(220,128,31,0.06);",
            "hr": "border:none;border-top:1px solid #f0e6df;margin:18px 0;",
        }
    },
    "spring-fresh": {
        "styles": {
            "container": "background-color:#FFFFFF;color:#494949;font-family:PingFang SC,-apple-system-font,system-ui,Helvetica Neue,Hiragino Sans GB,Microsoft YaHei UI,Microsoft YaHei,Arial,sans-serif;font-size:15px;line-height:1.75em;max-width:700px;margin:0 auto;padding:8px 0;box-sizing:border-box;word-wrap:break-word;",
            "paragraph": "margin:0 16px;text-align:justify;line-height:1.75em;text-indent:0;font-size:15px;color:#494949;letter-spacing:0;",
            "h1": "margin:24px 16px 12px;text-align:center;font-size:20px;font-weight:700;line-height:1.6em;color:#2E8B57;letter-spacing:0.04em;",
            "h2": "margin:20px 16px 10px;text-align:left;font-size:17px;font-weight:700;line-height:1.6em;color:#2E8B57;",
            "h3": "margin:16px 16px 8px;text-align:left;font-size:15px;font-weight:700;line-height:1.6em;color:#3CB371;",
            "image": "max-width:100%;height:auto;display:block;margin:8px auto;",
            "ul": "margin:8px 16px;padding-left:20px;line-height:1.75em;color:#494949;font-size:15px;",
            "ol": "margin:8px 16px;padding-left:20px;line-height:1.75em;color:#494949;font-size:15px;",
            "li": "margin:4px 0;line-height:1.75em;text-align:justify;",
            "strong": "font-weight:700;",
            "em": "font-style:italic;",
            "code": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:0.95em;background:#F0FFF0;padding:2px 4px;border-radius:3px;",
            "pre": "background:#F0FFF0;padding:12px 16px;border-radius:4px;overflow:auto;margin:12px 16px;",
            "preCode": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:0.95em;line-height:1.6em;white-space:pre;letter-spacing:0;word-break:normal;",
            "link": "color:#2E8B57;text-decoration:none;border-bottom:1px solid rgba(46,139,87,0.3);",
            "blockquote": "margin:12px 16px;padding:8px 12px;color:#494949;background:rgba(46,139,87,0.06);",
            "hr": "border:none;border-top:1px solid #d4edda;margin:18px 0;",
        }
    },
    "ocean-calm": {
        "styles": {
            "container": "background-color:#FFFFFF;color:#494949;font-family:PingFang SC,-apple-system-font,system-ui,Helvetica Neue,Hiragino Sans GB,Microsoft YaHei UI,Microsoft YaHei,Arial,sans-serif;font-size:15px;line-height:1.75em;max-width:700px;margin:0 auto;padding:8px 0;box-sizing:border-box;word-wrap:break-word;",
            "paragraph": "margin:0 16px;text-align:justify;line-height:1.75em;text-indent:0;font-size:15px;color:#494949;letter-spacing:0;",
            "h1": "margin:24px 16px 12px;text-align:center;font-size:20px;font-weight:700;line-height:1.6em;color:#1E3A5F;letter-spacing:0.04em;",
            "h2": "margin:20px 16px 10px;text-align:left;font-size:17px;font-weight:700;line-height:1.6em;color:#1E3A5F;",
            "h3": "margin:16px 16px 8px;text-align:left;font-size:15px;font-weight:700;line-height:1.6em;color:#4682B4;",
            "image": "max-width:100%;height:auto;display:block;margin:8px auto;",
            "ul": "margin:8px 16px;padding-left:20px;line-height:1.75em;color:#494949;font-size:15px;",
            "ol": "margin:8px 16px;padding-left:20px;line-height:1.75em;color:#494949;font-size:15px;",
            "li": "margin:4px 0;line-height:1.75em;text-align:justify;",
            "strong": "font-weight:700;",
            "em": "font-style:italic;",
            "code": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:0.95em;background:#F0F8FF;padding:2px 4px;border-radius:3px;",
            "pre": "background:#F0F8FF;padding:12px 16px;border-radius:4px;overflow:auto;margin:12px 16px;",
            "preCode": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:0.95em;line-height:1.6em;white-space:pre;letter-spacing:0;word-break:normal;",
            "link": "color:#1E3A5F;text-decoration:none;border-bottom:1px solid rgba(30,58,95,0.3);",
            "blockquote": "margin:12px 16px;padding:8px 12px;color:#494949;background:rgba(30,58,95,0.06);",
            "hr": "border:none;border-top:1px solid #cce5ff;margin:18px 0;",
        }
    },
}

# Default theme used when custom prompt is specified
DEFAULT_THEME = "autumn-warm"


def format_inline(text, styles):
    code_chunks = []

    def repl_code(match):
        code_chunks.append(match.group(1))
        return f"\x00CODE{len(code_chunks) - 1}\x00"

    text = re.sub(r"`([^`]+)`", repl_code, text)
    for raw, val in (
        (r"\*\*", "**"),
        (r"\*", "*"),
        (r"\_", "_"),
        (r"\`", "`"),
        (r"\[", "["),
        (r"\]", "]"),
        (r"\(", "("),
        (r"\)", ")"),
        (r"\\", "\\"),
    ):
        text = text.replace(raw, val)
    text = html.escape(text)

    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<a href=\"\2\">\1</a>", text)

    for i, code in enumerate(code_chunks):
        code_html = html.escape(code)
        code_tag = (
            f"<span style=\"{styles['code']}\">{code_html}</span>"
        )
        text = text.replace(f"\x00CODE{i}\x00", code_tag)

    return text.replace("\x00BR\x00", "<br />")


def join_lines_with_breaks(lines):
    parts = []
    for line in lines:
        raw = line.rstrip("\n")
        hard_break = raw.endswith("  ")
        text = raw.strip()
        if not text:
            continue
        parts.append((text, hard_break))

    tokens = []
    for text, hard_break in parts:
        tokens.append(text)
        if hard_break:
            tokens.append("\x00BR\x00")
        else:
            tokens.append(" ")

    return "".join(tokens).strip()


def is_hr(line):
    line = line.strip()
    return line in ("---", "***") or (len(line) >= 3 and all(ch == "-" for ch in line))


def parse_markdown(md):
    lines = md.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue

        img_match = re.match(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", line.strip())
        if img_match:
            blocks.append(("img", img_match.group(1)))
            i += 1
            continue

        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code_lines)))
            continue

        if is_hr(line):
            blocks.append(("hr", ""))
            i += 1
            continue

        if line.lstrip().startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote_lines.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            blocks.append(("quote", "\n".join(quote_lines)))
            continue

        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines):
                if lines[i].strip() == "":
                    i += 1
                    continue
                if not re.match(r"^\s*[-*]\s+", lines[i]):
                    break
                item = re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()
                i += 1
                cont = []
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip() == "":
                        i += 1
                        continue
                    if (
                        re.match(r"^\s*[-*]\s+", next_line)
                        or re.match(r"^\s*\d+\.\s+", next_line)
                        or re.match(r"^#{1,6}\s+", next_line)
                        or next_line.lstrip().startswith(">")
                        or next_line.strip().startswith("```")
                        or is_hr(next_line)
                    ):
                        break
                    if next_line.startswith("  ") or next_line.startswith("\t"):
                        cont.append(next_line.strip())
                        i += 1
                        continue
                    break
                if cont:
                    item = item + " " + " ".join(cont)
                if item:
                    items.append(item)
            blocks.append(("ul", items))
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines):
                if lines[i].strip() == "":
                    i += 1
                    continue
                if not re.match(r"^\s*\d+\.\s+", lines[i]):
                    break
                item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                i += 1
                sub_lines = []
                while i < len(lines):
                    next_line = lines[i]
                    if re.match(r"^\s*\d+\.\s+", next_line):
                        break
                    if re.match(r"^#{1,6}\s+", next_line) or is_hr(next_line):
                        break
                    sub_lines.append(next_line)
                    i += 1
                items.append({"text": item_text, "sub": "\n".join(sub_lines).strip("\n")})
            blocks.append(("ol", items))
            continue

        if re.match(r"^#{1,6}\s+", line):
            level = len(line.split(" ")[0])
            text = line[level:].strip()
            blocks.append((f"h{level}", text))
            i += 1
            continue

        para_lines = [line]
        i += 1
        while i < len(lines):
            if lines[i].strip() == "":
                break
            if re.match(r"^#{1,6}\s+", lines[i]) or re.match(r"^\s*[-*]\s+", lines[i]):
                break
            if re.match(r"^\s*\d+\.\s+", lines[i]) or lines[i].lstrip().startswith(">"):
                break
            if lines[i].strip().startswith("```") or is_hr(lines[i]):
                break
            para_lines.append(lines[i])
            i += 1
        blocks.append(("p", join_lines_with_breaks(para_lines)))

    return blocks


def render_blocks(blocks, styles):
    out = []
    img_index = 0

    for kind, content in blocks:
        if len(kind) == 2 and kind[0] == "h" and kind[1].isdigit():
            level = int(kind[1])
            html_text = format_inline(content, styles)
            style_key = "h3" if level >= 3 else "h2" if level == 2 else "h1"
            out.append(f"<h{level} style=\"{styles[style_key]}\">{html_text}</h{level}>")
        elif kind == "p":
            html_text = format_inline(content, styles)
            out.append(f"<p style=\"{styles['paragraph']}\">{html_text}</p>")
        elif kind == "ul":
            items = "".join(
                f"<li style=\"{styles['li']}\"><span style=\"display:inline;\">{format_inline(i, styles)}</span></li>"
                for i in content
            )
            out.append(f"<ul style=\"{styles['ul']}\">{items}</ul>")
        elif kind == "ol":
            item_html = []
            for item in content:
                if isinstance(item, dict):
                    inner = f"<span style=\"display:inline;\">{format_inline(item.get('text', ''), styles)}</span>"
                    sub = item.get("sub", "").strip()
                    if sub:
                        inner += render_blocks(parse_markdown(sub), styles)
                    item_html.append(f"<li style=\"{styles['li']}\">{inner}</li>")
                else:
                    item_html.append(
                        f"<li style=\"{styles['li']}\"><span style=\"display:inline;\">"
                        f"{format_inline(item, styles)}</span></li>"
                    )
            out.append(f"<ol style=\"{styles['ol']}\">{''.join(item_html)}</ol>")
        elif kind == "quote":
            html_text = format_inline(content, styles).replace("\n", "<br />")
            out.append(f"<blockquote style=\"{styles['blockquote']}\">{html_text}</blockquote>")
        elif kind == "img":
            out.append(f"<!-- IMG:{img_index} -->")
            img_index += 1
        elif kind == "code":
            lines = content.splitlines() or [""]
            escaped_lines = []
            for line in lines:
                if line == "":
                    escaped_lines.append("")
                    continue
                lead = len(line) - len(line.lstrip(" "))
                escaped = html.escape(line.lstrip(" "))
                if lead:
                    escaped = "&nbsp;" * lead + escaped
                escaped_lines.append(escaped)
            html_text = "<br />".join(escaped_lines)
            out.append(
                f"<section style=\"{styles['pre']}\">"
                f"<span style=\"{styles['preCode']}\">{html_text}</span></section>"
            )
        elif kind == "hr":
            hr_style = styles.get("hr", "border:none;border-top:1px solid #f0e6df;margin:18px 0;")
            out.append(f"<hr style=\"{hr_style}\" />")

    return "\n".join(out)


def build_html(body, styles):
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n  <meta charset=\"utf-8\" />\n</head>\n"
        "<body>\n"
        f"  <section style=\"{styles['container']}\">\n"
        f"{body}\n"
        "  </section>\n"
        "</body>\n</html>\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to WeChat-compatible HTML with themed styling."
    )
    parser.add_argument("--md", required=True, help="Markdown file path")
    parser.add_argument("--out", required=True, help="Output HTML file path")
    parser.add_argument(
        "--theme",
        default="autumn-warm",
        choices=list(THEMES.keys()),
        help=f"Theme name. Available: {', '.join(THEMES.keys())}",
    )
    parser.add_argument("--title", help="Optional H1 title inserted into body")
    args = parser.parse_args()

    # Validate input file exists
    if not os.path.isfile(args.md):
        print(f"Error: Markdown file not found: {args.md}", file=sys.stderr)
        sys.exit(1)

    # Read markdown file
    try:
        with open(args.md, "r", encoding="utf-8") as f:
            md = f.read()
    except IOError as e:
        print(f"Error reading file {args.md}: {e}", file=sys.stderr)
        sys.exit(1)

    # Get theme styles
    theme = THEMES.get(args.theme)
    if not theme:
        print(
            f"Error: Unknown theme '{args.theme}'. "
            f"Available themes: {', '.join(THEMES.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)
    styles = theme["styles"]

    # Parse and render
    blocks = parse_markdown(md)
    if args.title:
        blocks.insert(0, ("h1", args.title))
    body = render_blocks(blocks, styles)
    html_doc = build_html(body, styles)

    # Write output file
    try:
        out_dir = os.path.dirname(args.out)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(html_doc)
        print(f"Successfully converted to {args.out}")
    except IOError as e:
        print(f"Error writing file {args.out}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
