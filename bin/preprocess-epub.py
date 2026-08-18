#!/usr/bin/env python3
"""Lower OINK Book primitives to Pandoc-friendly Markdown for EPUB output.

The website source remains the authority: numbered figures/tables and xrefs
keep their public IDs, while site-only aggregate navigation is omitted because
Pandoc generates the EPUB table of contents itself.
"""

from __future__ import annotations

import os
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import unquote


ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
FRONT_MATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(?P<meta>.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL
)
META_VALUE_RE = re.compile(r"^(?P<key>[A-Za-z][\w-]*):[ \t]*(?P<value>.*)$", re.MULTILINE)
HEADING_ID_RE = re.compile(
    r"^(?P<lead>#{1,6}[ \t]+.*?\{)#(?P<id>[^\s}]+)", re.MULTILINE
)
INDENTED_HEADING_RE = re.compile(
    r"^(?P<indent>[ \t]{4,})#{1,6}[ \t]+(?P<title>.*?)"
    r"[ \t]+\{#(?P<id>[^\s}]+)\}[ \t]*$",
    re.MULTILINE,
)
FOOTNOTE_RE = re.compile(r"\[\^(?P<id>[^\]]+)\]")
XREF_RE = re.compile(
    r"\{\{<\s*xref\b(.*?)>\}\}(.*?)\{\{<\s*/xref\s*>\}\}", re.DOTALL
)
FIG_RE = re.compile(r"\{\{<\s*fig\b(.*?)/>\}\}", re.DOTALL)
# OINK 0.5 numbered example: `{{< eg num id caption >}}` wrapping the body
# (usually one fence), closed by `{{< /eg >}}` at the same indentation.
EXAMPLE_RE = re.compile(
    r"^(?P<indent>[ \t]*)\{\{<\s*eg\b(?P<attrs>.*?)>\}\}[ \t]*\n"
    r"(?P<body>.*?)\n"
    r"(?P=indent)\{\{<\s*/eg\s*>\}\}[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
TABLE_RE = re.compile(
    r"\{\{<\s*tbl\b(.*?)>\}\}(.*?)\{\{<\s*/tbl\s*>\}\}", re.DOTALL
)
# OINK 0.5 native numbered table: the pipe table itself, followed by the
# attribute line that numbers it. Footnote references keep working in a native
# table because the cells stay part of the page document, so this is the form
# the book uses; the `tbl` shortcode remains for compound bodies.
NATIVE_TABLE_RE = re.compile(
    r"(?P<table>(?:^[ \t]*\|[^\n]*\n)+)"
    r"^[ \t]*\{(?P<attrs>[^}\n]*\bnum=\"[^\"]*\"[^}\n]*)\}[ \t]*$",
    re.MULTILINE,
)
ID_ATTR_RE = re.compile(r"#([A-Za-z][\w:.-]*)")
LEGACY_FIGURE_RE = re.compile(r"\{\{<\s*figure\b(.*?)>\}\}", re.DOTALL)
SITE_ONLY_RE = re.compile(
    r"\{\{<\s*(?:book-(?:toc|figures|tables|equations|examples)|contributors)\b.*?>\}\}",
    re.DOTALL,
)
ABS_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(/(?!static/)([^)]+)\)")
SHORTCODE_RE = re.compile(r"\{\{[<%].*?[>%]\}\}", re.DOTALL)
SITE_LINK_RE = re.compile(
    r"(?P<prefix>\]\()(?P<url>/(?:ch\d+|part-(?:i|ii|iii)|preface|"
    r"glossary|indexes|contrib|colophon|toc|tw)/?(?:#[^)\s]+)?)(?=[)\s])"
)
LOCAL_FRAGMENT_RE = re.compile(
    r"(?P<prefix>\]\()#(?P<fragment>[^)\s]+)(?=[)\s])"
)

BOOK_ORDER = (
    "_index",
    "preface",
    "part-i",
    "ch1",
    "ch2",
    "ch3",
    "ch4",
    "ch5",
    "part-ii",
    "ch6",
    "ch7",
    "ch8",
    "ch9",
    "ch10",
    "part-iii",
    "ch11",
    "ch12",
    "ch13",
    "ch14",
    "glossary",
    "indexes",
    "contrib",
    "colophon",
)


def _stem_key(stem: str) -> str:
    return "about" if stem == "_index" else stem


def _document_id(stem: str) -> str:
    return f"epub-{_stem_key(stem)}"


def _heading_id(stem: str, identifier: str) -> str:
    return f"{_document_id(stem)}-{identifier}"


def _chunk_name(stem: str) -> str:
    try:
        index = BOOK_ORDER.index(stem) + 1
    except ValueError as exc:
        raise ValueError(f"EPUB route is not in BOOK_ORDER: {stem}") from exc
    return f"ch{index:03}.xhtml"


def _chunk_link(source: str, target: str, fragment: str) -> str:
    if source == target:
        return f"#{fragment}"
    return f"{_chunk_name(target)}#{fragment}"


def _front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    metadata = {
        item.group("key"): item.group("value").strip().strip("'\"")
        for item in META_VALUE_RE.finditer(match.group("meta"))
    }
    return metadata, text[match.end() :]


def _heading_ids(text: str) -> set[str]:
    return {match.group("id") for match in HEADING_ID_RE.finditer(text)}


def _heading_index(paths: list[Path]) -> dict[str, set[str]]:
    return {
        path.stem: _heading_ids(path.read_text(encoding="utf-8")) for path in paths
    }


def _document_heading(stem: str, title: str) -> str:
    if stem == "_index":
        label = "关于本书"
    elif stem.startswith("ch") and stem[2:].isdigit():
        label = f"第 {int(stem[2:])} 章　{title}"
    elif stem.startswith("part-"):
        number = {"part-i": "第一部分", "part-ii": "第二部分", "part-iii": "第三部分"}
        label = f"{number.get(stem, '部分')}　{title}"
    else:
        label = title or stem.replace("-", " ").title()
    return f"# {label} {{#{_document_id(stem)}}}\n\n"


def _rewrite_site_url(
    url: str,
    heading_ids: dict[str, set[str]],
    source_stem: str,
) -> str:
    path, separator, raw_fragment = url.partition("#")
    route = path.strip("/")
    if route == "tw":
        return "https://ddia.vonng.com/tw/" + (f"#{raw_fragment}" if separator else "")
    if route == "toc":
        return _chunk_link(source_stem, "_index", _document_id("_index"))
    if route not in heading_ids:
        return url
    if not separator or not raw_fragment:
        return _chunk_link(source_stem, route, _document_id(route))
    fragment = unquote(raw_fragment)
    if fragment in heading_ids.get(route, set()):
        fragment = _heading_id(route, fragment)
    return _chunk_link(source_stem, route, fragment)


def _attrs(raw: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(raw))


def _escape_alt_text(text: str) -> str:
    return text.replace("]", r"\]").replace("\n", " ").strip()


def _local_image(src: str) -> str:
    return "static" + src if src.startswith("/") else src


def _xref_label(attrs: dict[str, str], inner: str) -> str:
    label = inner.strip()
    if label:
        return label
    for kind, localized in (("fig", "图"), ("tbl", "表"), ("eq", "公式"), ("eg", "示例")):
        if attrs.get(kind):
            return f"{localized} {attrs[kind]}"
    return attrs.get("anchor", "引用")


def convert_markdown(
    text: str,
    *,
    stem: str = "document",
    heading_ids: dict[str, set[str]] | None = None,
) -> str:
    """Convert one Markdown document without changing its prose."""

    heading_ids = heading_ids or {stem: _heading_ids(text)}
    metadata, text = _front_matter(text)
    local_heading_ids = heading_ids.get(stem, set())

    def replace_xref(match: re.Match[str]) -> str:
        attrs = _attrs(match.group(1))
        label = _xref_label(attrs, match.group(2))
        anchor = attrs.get("anchor")
        if not anchor:
            for kind in ("fig", "tbl", "eq", "eg"):
                if attrs.get(kind):
                    anchor = f"{kind}-{attrs[kind]}"
                    break
        page = attrs.get("page", "").strip("/")
        if anchor and page in heading_ids and anchor in heading_ids[page]:
            anchor = _heading_id(page, anchor)
        if not anchor:
            return label
        target = page if page in BOOK_ORDER else stem
        return f"[{label}]({_chunk_link(stem, target, anchor)})"

    def _book_table(number: str, caption: str, target: str, body: str) -> str:
        label = f"**表 {number}.**" if number else "**表.**"
        heading = f"{label} {caption}".rstrip()
        fenced_attrs = f" {{#{target} .book-table}}" if target else " {.book-table}"
        return f"\n:::{fenced_attrs}\n{heading}\n\n{body.strip()}\n:::\n"

    def replace_table(match: re.Match[str]) -> str:
        attrs = _attrs(match.group(1))
        number = attrs.get("num", "")
        return _book_table(
            number,
            attrs.get("caption", "").strip(),
            attrs.get("id") or (f"tbl-{number}" if number else ""),
            match.group(2),
        )

    def replace_native_table(match: re.Match[str]) -> str:
        raw = match.group("attrs")
        attrs = _attrs(raw)
        number = attrs.get("num", "")
        identifier = ID_ATTR_RE.search(raw)
        return _book_table(
            number,
            attrs.get("caption", "").strip(),
            (identifier.group(1) if identifier else "")
            or (f"tbl-{number}" if number else ""),
            match.group("table"),
        )

    def replace_figure(match: re.Match[str]) -> str:
        attrs = _attrs(match.group(1))
        src = attrs.get("src")
        if not src:
            return ""
        number = attrs.get("num", "")
        caption = (attrs.get("caption") or attrs.get("title") or "").strip()
        alt = attrs.get("alt") or caption
        visible = f"图 {number}. {caption}".strip() if number else caption
        target = attrs.get("id") or (f"fig-{number}" if number else "")
        image_attrs = [f"#{target}" if target else "", ".book-figure"]
        if attrs.get("width"):
            image_attrs.append(f'width="{attrs["width"]}"')
        if attrs.get("height"):
            image_attrs.append(f'height="{attrs["height"]}"')
        attr_block = "{" + " ".join(part for part in image_attrs if part) + "}"
        # Pandoc uses the image description as the semantic figure caption.
        description = visible or alt
        return f"![{_escape_alt_text(description)}]({_local_image(src)}){attr_block}"

    def replace_example(match: re.Match[str]) -> str:
        attrs = _attrs(match.group("attrs"))
        indent = match.group("indent")
        body = match.group("body")
        number = attrs.get("num", "").strip()
        caption = attrs.get("caption", "").strip()
        target = attrs.get("id") or (f"eg-{number}" if number else "")
        label = f"示例 {number}." if number else "示例："
        anchor = f' id="{escape(target)}"' if target else ""
        # The caption stays an anchored paragraph; the wrapped body (fences)
        # follows after a blank line so Pandoc parses it as Markdown again.
        return (
            f'{indent}<p{anchor} class="book-example-caption">'
            f"<strong>{escape(label)}</strong> {escape(caption)}</p>\n\n{body}"
        )

    def replace_legacy_figure(match: re.Match[str]) -> str:
        attrs = _attrs(match.group(1))
        src = attrs.get("src")
        if not src:
            return ""
        caption = attrs.get("caption") or attrs.get("title") or attrs.get("alt") or ""
        return f"![{_escape_alt_text(caption)}]({_local_image(src)})"

    # Pandoc otherwise merges identically named notes from separate chapters.
    text = FOOTNOTE_RE.sub(
        lambda match: f"[^{_stem_key(stem)}-{match.group('id')}]", text
    )
    text = XREF_RE.sub(replace_xref, text)
    text = SITE_LINK_RE.sub(
        lambda match: match.group("prefix")
        + _rewrite_site_url(match.group("url"), heading_ids, stem),
        text,
    )
    text = LOCAL_FRAGMENT_RE.sub(
        lambda match: match.group("prefix")
        + "#"
        + (
            _heading_id(stem, unquote(match.group("fragment")))
            if unquote(match.group("fragment")) in local_heading_ids
            else match.group("fragment")
        ),
        text,
    )
    text = TABLE_RE.sub(replace_table, text)
    text = NATIVE_TABLE_RE.sub(replace_native_table, text)
    text = FIG_RE.sub(replace_figure, text)
    text = EXAMPLE_RE.sub(replace_example, text)
    text = LEGACY_FIGURE_RE.sub(replace_legacy_figure, text)
    text = SITE_ONLY_RE.sub("", text)
    text = ABS_IMAGE_RE.sub(r"![\1](static/\2)", text)
    # A DDIA example heading is nested in a definition list. Pandoc treats
    # its four-space indentation as code, so lower it to an anchored caption
    # while preserving the surrounding definition-list structure.
    text = INDENTED_HEADING_RE.sub(
        lambda match: (
            match.group("indent")
            + f'<p id="{match.group("id")}" class="book-example-caption">'
            + f"<strong>{escape(match.group('title'))}</strong></p>"
        ),
        text,
    )
    text = HEADING_ID_RE.sub(
        lambda match: match.group("lead") + "#" + _heading_id(stem, match.group("id")),
        text,
    )
    text = _document_heading(stem, metadata.get("title", "")) + text.lstrip()

    remaining = SHORTCODE_RE.findall(text)
    if remaining:
        preview = ", ".join(repr(item[:80]) for item in remaining[:3])
        raise ValueError(f"unsupported Hugo shortcode(s) remain: {preview}")
    return text


def process_file(
    input_path: str,
    output_path: str,
    heading_ids: dict[str, set[str]],
) -> None:
    with open(input_path, "r", encoding="utf-8") as stream:
        content = stream.read()
    converted = convert_markdown(
        content,
        stem=Path(input_path).stem,
        heading_ids=heading_ids,
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as stream:
        stream.write(converted)
    print(f"Processed: {input_path} -> {output_path}")


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--print-order":
        for stem in BOOK_ORDER:
            print(f"{stem}.md")
        return 0

    if len(sys.argv) < 2:
        print("Usage: preprocess-epub.py <input_file> [output_file]")
        print("   or: preprocess-epub.py <input_dir> <output_dir>")
        return 1

    input_path = sys.argv[1]
    if os.path.isfile(input_path):
        output_path = sys.argv[2] if len(sys.argv) > 2 else input_path
        input_file = Path(input_path)
        heading_ids = _heading_index(sorted(input_file.parent.glob("*.md")))
        process_file(input_path, output_path, heading_ids)
        return 0
    if os.path.isdir(input_path):
        if len(sys.argv) < 3:
            print("Error: an output directory is required for directory input")
            return 1
        output_dir = sys.argv[2]
        md_files = sorted(Path(input_path).glob("*.md"))
        heading_ids = _heading_index(md_files)
        for md_file in md_files:
            process_file(
                str(md_file),
                os.path.join(output_dir, md_file.name),
                heading_ids,
            )
        print(f"\nTotal processed: {len(md_files)} files")
        return 0

    print(f"Error: {input_path} is not a valid file or directory")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
