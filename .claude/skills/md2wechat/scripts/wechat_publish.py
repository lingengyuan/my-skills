#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
import uuid


def load_env(path):
    if not path:
        return
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            if name and name not in os.environ:
                os.environ[name] = value


def http_json(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def get_access_token(appid, secret):
    params = urllib.parse.urlencode(
        {"grant_type": "client_credential", "appid": appid, "secret": secret}
    )
    url = f"https://api.weixin.qq.com/cgi-bin/token?{params}"
    res = http_json(url)
    token = res.get("access_token")
    if not token:
        raise RuntimeError(f"access_token error: {res}")
    return token


def download_url(url):
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read()
    name = os.path.basename(urllib.parse.urlparse(url).path) or "image"
    return name, data


def build_multipart(field_name, filename, data):
    boundary = "----md2wechat" + uuid.uuid4().hex
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    lines = []
    lines.append(f"--{boundary}".encode("utf-8"))
    lines.append(
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{filename}"'
        ).encode("utf-8")
    )
    lines.append(f"Content-Type: {content_type}".encode("utf-8"))
    lines.append(b"")
    lines.append(data)
    lines.append(f"--{boundary}--".encode("utf-8"))
    body = b"\r\n".join(lines)
    return boundary, body


def upload_image(access_token, filename, data):
    url = (
        "https://api.weixin.qq.com/cgi-bin/material/add_material"
        f"?type=image&access_token={access_token}"
    )
    boundary, body = build_multipart("media", filename, data)
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    res = http_json(url, method="POST", data=body, headers=headers)
    if "media_id" not in res:
        raise RuntimeError(f"upload error: {res}")
    return res["media_id"], res.get("url", "")


def parse_markdown_images(markdown):
    pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    images = []
    for match in pattern.findall(markdown):
        src = match.strip()
        if src.startswith("__generate:") or "__generate:" in src:
            continue
        images.append(src)
    return images


def replace_placeholders(html, image_urls):
    for idx, url in enumerate(image_urls):
        placeholder = f"<!-- IMG:{idx} -->"
        img_tag = (
            f'<img src="{url}" '
            'style="max-width:100%;height:auto;display:block;margin:20px auto;" />'
        )
        html = html.replace(placeholder, img_tag)
    return html


def derive_title(md_path):
    name = os.path.basename(md_path)
    if name.lower().endswith(".md"):
        name = name[:-3]
    return name.strip()


def extract_title_and_digest(markdown, md_path=None, title_override=None):
    title_from_file = False
    if title_override:
        title = title_override
    elif md_path:
        title = derive_title(md_path)
        title_from_file = True
    else:
        title = "Untitled"
    digest = ""
    lines = markdown.splitlines()
    if not title_from_file and not title_override:
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
            if line:
                title = line
                break
    paragraph = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            if paragraph:
                break
            continue
        paragraph.append(line)
    if paragraph:
        digest = " ".join(paragraph)
    return title[:64], digest[:120]


def create_draft(access_token, html, title, digest, cover_media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    payload = {
        "articles": [
            {
                "title": title,
                "digest": digest,
                "content": html,
                "thumb_media_id": cover_media_id,
                "show_cover_pic": 1,
            }
        ]
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    res = http_json(url, method="POST", data=data, headers={"Content-Type": "application/json"})
    if "media_id" not in res:
        raise RuntimeError(f"draft error: {res}")
    return res["media_id"]


def get_draft(access_token, media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={access_token}"
    payload = {"media_id": media_id}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    res = http_json(url, method="POST", data=data, headers={"Content-Type": "application/json"})
    if "news_item" not in res:
        raise RuntimeError(f"draft get error: {res}")
    return res


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", required=True, help="Markdown file")
    parser.add_argument("--html", required=True, help="HTML file")
    parser.add_argument("--env", default=".env", help="Env file path")
    parser.add_argument("--cover", help="Cover image path")
    parser.add_argument("--output-html", help="Write HTML with WeChat URLs")
    parser.add_argument("--draft", action="store_true", help="Create WeChat draft")
    parser.add_argument("--fetch-draft", help="Write WeChat-sanitized HTML to file")
    parser.add_argument("--title", help="Override article title")
    args = parser.parse_args()

    load_env(args.env)
    appid = os.getenv("WECHAT_APPID") or os.getenv("AppID")
    secret = os.getenv("WECHAT_SECRET") or os.getenv("AppSecret")
    if not appid or not secret:
        raise RuntimeError("WECHAT_APPID/WECHAT_SECRET not set in env")

    markdown = read_file(args.md)
    html = read_file(args.html)

    images = parse_markdown_images(markdown)
    access_token = get_access_token(appid, secret)

    uploaded = []
    md_dir = os.path.dirname(os.path.abspath(args.md))
    for src in images:
        if src.startswith("http://") or src.startswith("https://"):
            name, data = download_url(src)
        else:
            local_path = src
            if not os.path.isabs(local_path):
                local_path = os.path.join(md_dir, local_path)
            name = os.path.basename(local_path)
            with open(local_path, "rb") as f:
                data = f.read()
        media_id, url = upload_image(access_token, name, data)
        uploaded.append({"media_id": media_id, "url": url})

    html = replace_placeholders(html, [u["url"] for u in uploaded])

    if args.output_html:
        with open(args.output_html, "w", encoding="utf-8") as f:
            f.write(html)

    cover_media_id = None
    if args.cover:
        with open(args.cover, "rb") as f:
            data = f.read()
        cover_media_id, _ = upload_image(access_token, os.path.basename(args.cover), data)
    elif uploaded:
        cover_media_id = uploaded[0]["media_id"]

    result = {"success": True, "image_count": len(uploaded)}
    if args.draft:
        if not cover_media_id:
            raise RuntimeError("cover image required for draft upload")
        title, digest = extract_title_and_digest(markdown, args.md, args.title)
        media_id = create_draft(access_token, html, title, digest, cover_media_id)
        result["draft_media_id"] = media_id
        if args.fetch_draft:
            draft = get_draft(access_token, media_id)
            items = draft.get("news_item", [])
            if items:
                item = items[0]
                content = item.get("content", "")
                with open(args.fetch_draft, "w", encoding="utf-8") as f:
                    f.write(content)
                result["draft_title"] = item.get("title", "")

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
