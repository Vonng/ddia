#!/usr/bin/env python3
"""Validate DDIA's generated EPUB package and every internal reference."""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_STORED, BadZipFile, ZipFile


CONTAINER_NS = {"container": "urn:oasis:names:tc:opendocument:xmlns:container"}
OPF_NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf",
}
CHAPTER_RE = re.compile(r"EPUB/text/ch\d+\.xhtml\Z")


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def archive_target(source: str, path: str) -> str:
    return posixpath.normpath(
        posixpath.join(posixpath.dirname(source), unquote(path))
    )


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub", nargs="?", type=Path, default=root / "output/ddia.epub")
    parser.add_argument("--expected-chapters", type=int, default=23)
    parser.add_argument("--expected-figures", type=int, default=106)
    parser.add_argument("--expected-tables", type=int, default=3)
    parser.add_argument("--expected-title", default="设计数据密集型应用（第二版）")
    parser.add_argument("--expected-language", default="zh-CN")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        archive = ZipFile(args.epub)
    except (FileNotFoundError, BadZipFile) as exc:
        print(f"EPUB validation failed: {exc}", file=sys.stderr)
        return 1

    with archive:
        infos = archive.infolist()
        names = set(archive.namelist())
        if not infos:
            errors.append("archive is empty")
        elif infos[0].filename != "mimetype" or infos[0].compress_type != ZIP_STORED:
            errors.append("mimetype must be the first, uncompressed archive entry")
        if "mimetype" not in names or archive.read("mimetype") != b"application/epub+zip":
            errors.append("mimetype content is not application/epub+zip")

        rootfile = ""
        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile_node = container.find(".//container:rootfile", CONTAINER_NS)
            rootfile = rootfile_node.attrib.get("full-path", "") if rootfile_node is not None else ""
        except (KeyError, ET.ParseError) as exc:
            errors.append(f"invalid META-INF/container.xml: {exc}")
        if not rootfile or rootfile not in names:
            errors.append(f"package document is missing: {rootfile or '(unspecified)'}")

        if rootfile in names:
            try:
                package = ET.fromstring(archive.read(rootfile))
                title = package.findtext(".//dc:title", namespaces=OPF_NS) or ""
                language = package.findtext(".//dc:language", namespaces=OPF_NS) or ""
                if title != args.expected_title:
                    errors.append(f"unexpected title: {title!r}")
                if language != args.expected_language:
                    errors.append(f"unexpected language: {language!r}")

                manifest: dict[str, str] = {}
                package_dir = posixpath.dirname(rootfile)
                for item in package.findall(".//opf:manifest/opf:item", OPF_NS):
                    identifier = item.attrib.get("id", "")
                    href = item.attrib.get("href", "")
                    target = posixpath.normpath(posixpath.join(package_dir, unquote(href)))
                    if not identifier or identifier in manifest:
                        errors.append(f"invalid or duplicate manifest id: {identifier!r}")
                    else:
                        manifest[identifier] = target
                    if target not in names:
                        errors.append(f"manifest target is missing: {href}")
                for itemref in package.findall(".//opf:spine/opf:itemref", OPF_NS):
                    identifier = itemref.attrib.get("idref", "")
                    if identifier not in manifest:
                        errors.append(f"spine idref is not in manifest: {identifier!r}")
            except ET.ParseError as exc:
                errors.append(f"invalid package document {rootfile}: {exc}")

        xhtml_names = sorted(name for name in names if name.endswith(".xhtml"))
        roots: dict[str, ET.Element] = {}
        ids: dict[str, set[str]] = {}
        for name in xhtml_names:
            try:
                root_node = ET.fromstring(archive.read(name))
            except ET.ParseError as exc:
                errors.append(f"invalid XHTML {name}: {exc}")
                continue
            roots[name] = root_node
            all_ids = [node.attrib["id"] for node in root_node.iter() if "id" in node.attrib]
            ids[name] = set(all_ids)
            duplicates = [identifier for identifier, count in Counter(all_ids).items() if count > 1]
            if duplicates:
                errors.append(f"{name}: duplicate ids: {', '.join(duplicates[:5])}")

        for name, root_node in roots.items():
            for node in root_node.iter():
                for raw_attr, value in node.attrib.items():
                    if local_name(raw_attr) not in {"href", "src"} or not value:
                        continue
                    parsed = urlsplit(value)
                    if parsed.scheme or parsed.netloc:
                        continue
                    target = archive_target(name, parsed.path) if parsed.path else name
                    if target not in names:
                        errors.append(f"{name}: missing internal target {value!r}")
                    elif parsed.fragment and target in ids:
                        fragment = unquote(parsed.fragment)
                        if fragment not in ids[target]:
                            errors.append(f"{name}: missing fragment {value!r}")

        chapter_count = sum(bool(CHAPTER_RE.fullmatch(name)) for name in names)
        figure_count = sum(
            local_name(node.tag) == "figure"
            for root_node in roots.values()
            for node in root_node.iter()
        )
        table_count = sum(
            "book-table" in node.attrib.get("class", "").split()
            for root_node in roots.values()
            for node in root_node.iter()
        )
        if chapter_count != args.expected_chapters:
            errors.append(
                f"expected {args.expected_chapters} content chapters, found {chapter_count}"
            )
        if figure_count != args.expected_figures:
            errors.append(f"expected {args.expected_figures} figures, found {figure_count}")
        if table_count != args.expected_tables:
            errors.append(f"expected {args.expected_tables} tables, found {table_count}")

        if any(b"{{<" in archive.read(name) for name in xhtml_names):
            errors.append("unprocessed Hugo shortcode found in XHTML")

    summary = (
        f"EPUB chapters={chapter_count} figures={figure_count} tables={table_count} "
        f"xhtml={len(xhtml_names)} entries={len(names)}"
    )
    if errors:
        print(f"{summary} errors={len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{summary} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
