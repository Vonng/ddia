#!/usr/bin/env python3
"""
预处理 Markdown 文件，将 Hugo shortcode 转换为 Pandoc 可识别的格式

处理两种 shortcode：
1. {{< figure src="/fig/xxx.png" caption="xxx" >}} → ![xxx](static/fig/xxx.png)
2. {{< figure ... >}} (无 src) → 移除（通常用于代码示例）
"""

import os
import re
import sys
from pathlib import Path

FIGURE_SHORTCODE_RE = re.compile(r"\{\{<\s*figure\b(.*?)>\}\}", re.DOTALL)
CALLOUT_SHORTCODE_RE = re.compile(r"\{\{<\s*callout\b(.*?)>\}\}(.*?)\{\{<\s*/callout\s*>\}\}", re.DOTALL)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
ABS_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(/(?!static/)([^)]+)\)')
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
TITLE_RE = re.compile(r'^title:\s*(?:"([^"]*)"|\'([^\']*)\'|(.+?))\s*$', re.MULTILINE)
LINK_HEADING_RE = re.compile(r"^(#{2,6})\s+(\[[^\]]+\]\([^)]+\))\s*$", re.MULTILINE)
HEADER_ID_RE = re.compile(r"\{#([A-Za-z0-9_:-]+)\}")
RAW_ID_RE = re.compile(r'(<a\s+[^>]*\bid=")([^"]+)(")', re.IGNORECASE)
RAW_HREF_RE = re.compile(r'(<a\s+[^>]*\bhref=")(/[^"#?)]*)(#[^"]*)?(")', re.IGNORECASE)
MD_HREF_RE = re.compile(r"(?<!!)(\[[^\]]+\]\()(/[^)#?]+)(#[^)]+)?(\))")
LOCAL_MD_HREF_RE = re.compile(r"(?<!!)(\[[^\]]+\]\()(#[A-Za-z0-9_:-]+)(\))")
FOOTNOTE_RE = re.compile(r"\[\^([^\]\s]+)\]")


def _escape_alt_text(text):
    """Escape `]` in alt text to avoid breaking Markdown image syntax."""
    return text.replace("]", r"\]")


def _slug_for_path(path):
    stem = Path(path).stem
    return "index" if stem == "_index" else stem


def _extract_front_matter(text):
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    raw_meta = match.group(1)
    title_match = TITLE_RE.search(raw_meta)
    title = None
    if title_match:
        title = next(group for group in title_match.groups() if group is not None).strip()

    return {"title": title}, text[match.end():]


def _page_anchor(slug, anchor):
    return anchor if anchor == slug or anchor.startswith(f"{slug}__") else f"{slug}__{anchor}"


def _rewrite_internal_href(slug, path, fragment, known_pages):
    target = path.strip("/")
    if target == "":
        target_slug = "index"
    else:
        target_slug = target.split("/", 1)[0]

    if target_slug not in known_pages:
        return None

    if fragment:
        return f"#{_page_anchor(target_slug, fragment[1:])}"
    return f"#{target_slug}"


def _rewrite_links(text, slug, known_pages):
    def replace_md_href(match):
        replacement = _rewrite_internal_href(slug, match.group(2), match.group(3), known_pages)
        if replacement is None:
            return match.group(0)
        return f"{match.group(1)}{replacement}{match.group(4)}"

    def replace_raw_href(match):
        replacement = _rewrite_internal_href(slug, match.group(2), match.group(3), known_pages)
        if replacement is None:
            return match.group(0)
        return f"{match.group(1)}{replacement}{match.group(4)}"

    def replace_local_href(match):
        anchor = match.group(2)[1:]
        if anchor == slug or anchor.startswith(f"{slug}__"):
            return match.group(0)
        return f"{match.group(1)}#{_page_anchor(slug, anchor)}{match.group(3)}"

    text = MD_HREF_RE.sub(replace_md_href, text)
    text = RAW_HREF_RE.sub(replace_raw_href, text)
    text = LOCAL_MD_HREF_RE.sub(replace_local_href, text)
    return text


def _rewrite_footnotes(text, slug):
    def replace(match):
        label = match.group(1)
        if label.startswith(f"{slug}__"):
            return match.group(0)
        return f"[^{slug}__{label}]"

    return FOOTNOTE_RE.sub(replace, text)


def convert_markdown(text, slug, known_pages=None):
    """
    转换 Hugo front matter、figure shortcode 和站内绝对路径引用。

    Args:
        text: Markdown 文本内容
        slug: 当前页面 slug，用于生成 EPUB 内稳定锚点

    Returns:
        转换后的文本
    """
    known_pages = known_pages or {slug}
    meta, text = _extract_front_matter(text)

    def replace_figure_shortcode(match):
        attrs_text = match.group(1)
        attrs = dict(ATTR_RE.findall(attrs_text))
        src = attrs.get("src")

        # 没有 src 的 figure 一般是代码示例占位，直接移除
        if not src:
            return ""

        # 绝对路径资源转为相对 static 路径，便于 Pandoc 打包
        if src.startswith('/'):
            src = 'static' + src

        # 优先 caption，fallback 到 title，至少保证图片可渲染
        alt = _escape_alt_text(attrs.get("caption") or attrs.get("title") or "")
        return f'![{alt}]({src})'

    def replace_callout_shortcode(match):
        body = match.group(2).strip()
        if not body:
            return ""
        quoted = "\n".join(f"> {line}" if line else ">" for line in body.splitlines())
        return f"> **注意**\n>\n{quoted}"

    text = CALLOUT_SHORTCODE_RE.sub(replace_callout_shortcode, text)
    text = FIGURE_SHORTCODE_RE.sub(replace_figure_shortcode, text)

    # 把 Markdown 里的绝对路径图片 ![](/map/ch01.png) 转为 static/map/ch01.png
    text = ABS_IMAGE_RE.sub(r'![\1](static/\2)', text)

    # 网站目录页里用二级标题承载跳转链接；EPUB 目录应指向真实章节页。
    text = LINK_HEADING_RE.sub(r"**\2**", text)

    text = HEADER_ID_RE.sub(lambda m: "{#" + _page_anchor(slug, m.group(1)) + "}", text)
    text = RAW_ID_RE.sub(lambda m: f"{m.group(1)}{_page_anchor(slug, m.group(2))}{m.group(3)}", text)
    text = _rewrite_links(text, slug, known_pages)
    text = _rewrite_footnotes(text, slug)

    title = meta.get("title")
    if title:
        text = f"# {title} {{#{slug}}}\n\n{text.lstrip()}"

    return text

def process_file(input_path, output_path, known_pages=None):
    """
    处理单个 Markdown 文件

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 转换内容
    converted_content = convert_markdown(content, _slug_for_path(input_path), known_pages)

    # 写入输出文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(converted_content)

    print(f"Processed: {input_path} -> {output_path}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: preprocess.py <input_file> [output_file]")
        print("   or: preprocess.py <input_dir> <output_dir>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        # 处理单个文件
        output_path = sys.argv[2] if len(sys.argv) > 2 else input_path
        process_file(input_path, output_path)
    elif os.path.isdir(input_path):
        # 处理目录
        output_dir = sys.argv[2]
        input_dir = Path(input_path)

        # 获取所有 .md 文件
        md_files = sorted(input_dir.glob('*.md'))
        known_pages = {_slug_for_path(path) for path in md_files}

        for md_file in md_files:
            output_file = os.path.join(output_dir, md_file.name)
            process_file(str(md_file), output_file, known_pages)

        print(f"\nTotal processed: {len(md_files)} files")
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main()
