#!/usr/bin/env python3
"""Normalize emphasis in the second-edition Chinese Markdown sources.

The English manuscript uses emphasis (``*text*``) for introduced terms,
variables, titles, and rhetorical stress.  The Chinese translation follows
that semantic distinction: ``**text**`` is reserved for genuinely strong
content rather than used as a visual substitute for italics.

For reliable Markdown parsing, an emphasis delimiter next to a Unicode word
character gets one outside ASCII space.  Punctuation, brackets, link syntax,
function notation, fenced code, and inline code are left compact.

Simplified Chinese is the authority.  After ``--write``, regenerate
``content/tw`` with ``bin/zh-tw.py`` (or ``make translate``).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROSE_FILES = [
    *(f"ch{number}.md" for number in range(1, 15)),
    "part-i.md",
    "part-ii.md",
    "part-iii.md",
    "preface.md",
    "glossary.md",
]

# Colophon names and translator credits contain intentional strong emphasis.
SPACING_FILES = [*PROSE_FILES, "colophon.md"]

FENCE_RE = re.compile(r"^\s{0,3}(?P<fence>`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(?P<ticks>`+).*?(?P=ticks)")
STRONG_RE = re.compile(
    r"(?<![\\*])\*\*(?!\*)"
    r"(?P<body>[^\s*](?:[^*\n]*?[^\s*])?)"
    r"\*\*(?!\*)"
)
EMPHASIS_RE = re.compile(
    r"(?<![\\*])(?P<mark>\*{1,3})(?!\*)"
    r"(?P<body>[^\s*](?:[^*\n]*?[^\s*])?)"
    r"(?P=mark)(?!\*)"
)
CJK_PUNCTUATION = "，。；：！？、（）《》〈〉「」『』【】〔〕〖〗“”‘’…"
CJK_PUNCTUATION_CLASS = re.escape(CJK_PUNCTUATION)


def word_character(character: str) -> bool:
    """Return whether Markdown emphasis needs a separator by this character."""

    return bool(character) and (character.isalnum() or character == "_")


def normalize_segment(text: str, *, normalize_strong: bool) -> str:
    """Normalize one non-code segment of a Markdown line."""

    if normalize_strong:
        text = STRONG_RE.sub(lambda match: f"*{match.group('body')}*", text)

    def add_outside_spacing(match: re.Match[str]) -> str:
        before = text[match.start() - 1] if match.start() else ""
        after = text[match.end()] if match.end() < len(text) else ""
        prefix = " " if word_character(before) else ""
        suffix = " " if word_character(after) else ""
        return f"{prefix}{match.group(0)}{suffix}"

    text = EMPHASIS_RE.sub(add_outside_spacing, text)
    # Full-width Chinese punctuation stays flush with emphasized text.  This
    # also cleans up old forms such as ``*术语* ，`` without touching the
    # intentional separator before a following word.
    text = re.sub(
        rf"(?<=[{CJK_PUNCTUATION_CLASS}])[ \t]+"
        rf"(?=\*{{1,3}}(?!\*)[\u3400-\u9fff])",
        "",
        text,
    )
    text = re.sub(
        rf"(?<=\*)[ \t]+(?=[{CJK_PUNCTUATION_CLASS}])",
        "",
        text,
    )
    return text


def normalize_line(line: str, *, normalize_strong: bool) -> str:
    """Normalize prose while preserving every inline-code span byte-for-byte."""

    output: list[str] = []
    cursor = 0
    for match in INLINE_CODE_RE.finditer(line):
        output.append(
            normalize_segment(line[cursor : match.start()], normalize_strong=normalize_strong)
        )
        output.append(match.group(0))
        cursor = match.end()
    output.append(normalize_segment(line[cursor:], normalize_strong=normalize_strong))
    return "".join(output)


def normalize_document(text: str, *, normalize_strong: bool) -> str:
    """Normalize a document without entering fenced code blocks."""

    output: list[str] = []
    fence_character = ""
    for line in text.splitlines(keepends=True):
        fence = FENCE_RE.match(line)
        if fence:
            character = fence.group("fence")[0]
            if not fence_character:
                fence_character = character
            elif character == fence_character:
                fence_character = ""
            output.append(line)
            continue
        if fence_character:
            output.append(line)
        else:
            output.append(normalize_line(line, normalize_strong=normalize_strong))
    return "".join(output)


def validate_examples() -> None:
    examples = {
        "这是*重点*内容": "这是 *重点* 内容",
        "*read*(*x*)": "*read*(*x*)",
        "《*Book Title*》": "《*Book Title*》",
        "* 使用*术语*说明": "* 使用 *术语* 说明",
        "`a**b` 与**术语**相邻": "`a**b` 与 *术语* 相邻",
        "令牌 *t**x* 保持原样": "令牌 *t**x* 保持原样",
        "说明： *重点* ，继续": "说明：*重点*，继续",
        "Reference.” *example.org*": "Reference.” *example.org*",
    }
    for source, expected in examples.items():
        actual = normalize_line(source, normalize_strong=True)
        if actual != expected:
            raise AssertionError(f"emphasis normalizer: {source!r} -> {actual!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (defaults to the parent of bin/)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="apply normalization")
    mode.add_argument("--check", action="store_true", help="fail if files need changes")
    args = parser.parse_args()

    validate_examples()
    root = args.root.resolve()
    source = root / "content" / "zh"
    changed: list[Path] = []

    for filename in SPACING_FILES:
        path = source / filename
        original = path.read_text(encoding="utf-8")
        updated = normalize_document(
            original,
            normalize_strong=filename in PROSE_FILES,
        )
        if updated == original:
            continue
        changed.append(path.relative_to(root))
        if args.write:
            path.write_text(updated, encoding="utf-8")

    action = "wrote" if args.write else "would_change"
    print(f"files_scanned={len(SPACING_FILES)} files_{action}={len(changed)}")
    for path in changed:
        print(path)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
