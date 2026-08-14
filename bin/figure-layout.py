#!/usr/bin/env python3
"""Add stable dimensions and responsive layout classes to DDIA Book figures.

The OINK migration deliberately preserves image paths and semantic numbering.
This second, site-owned pass reads the actual PNG headers so the browser can
reserve space before an image loads, then classifies each diagram by aspect
ratio for the DDIA publication stylesheet.

Dry-run is the default. Use ``--write`` to update the Simplified Chinese
authorities; the existing zh-tw generator carries the byte-stable attributes
into the Traditional Chinese variants.
"""

from __future__ import annotations

import argparse
import re
import struct
from collections import Counter
from pathlib import Path


FIG_RE = re.compile(r"\{\{<\s*fig\b(?P<attrs>.*?)\s*/>\}\}", re.DOTALL)
ATTR_RE = re.compile(r'([A-Za-z][\w-]*)="([^"]*)"')
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError(f"expected a PNG image: {path}")
    return struct.unpack(">II", header[16:24])


def layout_class(width: int, height: int) -> str:
    ratio = width / height
    if ratio >= 3:
        return "panorama"
    if ratio >= 1.65:
        return "wide"
    return "standard"


def enrich(text: str, root: Path, counters: Counter[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        attrs_text = match.group("attrs").strip()
        attrs = dict(ATTR_RE.findall(attrs_text))
        src = attrs.get("src")
        if not src:
            return match.group(0)
        if not src.startswith("/"):
            raise ValueError(f"figure source must be site-absolute: {src}")

        image_path = root / "static" / src.removeprefix("/")
        width, height = png_size(image_path)
        layout = layout_class(width, height)
        counters[layout] += 1
        counters["figures"] += 1

        additions: list[str] = []
        if "class" not in attrs:
            additions.append(f'class="ddia-figure ddia-figure--{layout}"')
        if "width" not in attrs:
            additions.append(f'width="{width}"')
        if "height" not in attrs:
            additions.append(f'height="{height}"')
        if not additions:
            return match.group(0)
        return "{{< fig " + attrs_text + " " + " ".join(additions) + " />}}"

    return FIG_RE.sub(replace, text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="DDIA repository root (defaults to the parent of bin/)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="apply the enrichment")
    mode.add_argument(
        "--check",
        action="store_true",
        help="fail when any source still needs enrichment",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    files = sorted((root / "content" / "zh").glob("*.md"))
    files += sorted((root / "content" / "v1").glob("*.md"))
    changed: list[Path] = []
    counters: Counter[str] = Counter()

    for path in files:
        original = path.read_text(encoding="utf-8")
        updated = enrich(original, root, counters)
        if updated == original:
            continue
        changed.append(path.relative_to(root))
        if args.write:
            path.write_text(updated, encoding="utf-8")

    action = "wrote" if args.write else "would change"
    print(
        f"figures={counters['figures']} standard={counters['standard']} "
        f"wide={counters['wide']} panorama={counters['panorama']}"
    )
    print(f"files_scanned={len(files)} files_{action.replace(' ', '_')}={len(changed)}")
    for path in changed:
        print(path)

    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
