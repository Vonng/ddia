#!/usr/bin/env python3
"""Check content/vi against content/zh structurally, read-only.

Every Vietnamese page must mirror its Chinese counterpart: same page set,
invariant front matter, anchors, heading levels, fig/eg/xref shortcodes,
footnotes, URLs and existing local images. Draft and finished pages are
checked the same way. Syntax definitions are reused from check-translation.py.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import sys

_spec = importlib.util.spec_from_file_location('check_translation', Path(__file__).with_name('check-translation.py'))
ct = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ct)

TRANSLATABLE = {'title', 'linkTitle', 'description', 'search_keywords'}
VI_ONLY = {'draft', 'book_status'}
# ponytail: repo/feedback links on these pages point at the fork, not Vonng/ddia.
OWN_LINKS = {'_index', 'contrib'}
# Pages that exist only in the Vietnamese edition (no zh counterpart).
VI_ONLY_PAGES = {'terms'}
FN_DEF = re.compile(r'^\[\^([^\]\s]+)\]:', re.M)
FN_REF = re.compile(r'\[\^([^\]\s]+)\](?!:)')
# Stop at CJK text and Markdown emphasis so the neighbouring language never leaks into a URL.
URL = re.compile(r'https?://[^\s<>()"\'*\u3000-\u9fff\uff00-\uffef]+[^\s<>()"\'*.,;:!?\u3000-\u9fff\uff00-\uffef]')


def split_page(text: str) -> tuple[dict[str, str], str]:
    """Front matter as {top-level key: raw block} plus the body."""
    match = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not match:
        return {}, text
    keys: dict[str, str] = {}; current = None
    for line in match[1].splitlines():
        top = re.match(r'([A-Za-z_]\w*):', line)
        if top:
            current = top[1]; keys[current] = line
        elif current:
            keys[current] += '\n' + line
    return keys, text[match.end():]


def line_of(text: str, needle: str) -> int | None:
    pos = text.find(needle)
    return text.count('\n', 0, pos) + 1 if pos >= 0 else None


def short(value) -> str:
    text = ', '.join(map(str, value)) if isinstance(value, (list, tuple, set)) else str(value)
    return text if len(text) <= 120 else text[:117] + '...'


def multiset_diff(expected, actual) -> tuple[list, list]:
    e, a = Counter(expected), Counter(actual)
    return sorted((e - a).elements(), key=str), sorted((a - e).elements(), key=str)


def page_facts(body: str) -> dict:
    prose = ct.without_code(body)
    blocks = ct.without_code(body, inline=False)
    shortcodes = [(kind, ct.attrs(raw)) for kind, raw in ct.SC.findall(prose)]
    return {
        'ids': ct.all_ids(body),
        'headings': Counter(len(h) for h, _, _ in ct.HEAD.findall(blocks)),
        'blocks': [(k, a.get('num'), a.get('id'), a.get('src')) for k, a in shortcodes if k in ('fig', 'eg')],
        'xrefs': [(k, a.get('fig') or a.get('tbl') or a.get('eg') or a.get('num'), a.get('page'), a.get('anchor'))
                  for k, a in shortcodes if k == 'xref'],
        'fn_refs': FN_REF.findall(prose),
        'fn_defs': FN_DEF.findall(blocks),
        'urls': URL.findall(prose),
        'images': ct.MDIMAGE.findall(prose) + [a['src'] for k, a in shortcodes if k == 'fig' and a.get('src')],
    }


def check_page(root: Path, slug: str, zh_text: str, vi_text: str, vi_ids: dict[str, set], issue) -> None:
    path = f'content/vi/{slug}.md'
    zh_fm, zh_body = split_page(zh_text)
    vi_fm, vi_body = split_page(vi_text)
    for key, raw in zh_fm.items():
        if key in TRANSLATABLE:
            continue
        if key not in vi_fm:
            issue(path, 'front-matter', f'key {key}', '(missing)')
        elif vi_fm[key] != raw:
            issue(path, 'front-matter', raw, vi_fm[key], line_of(vi_text, vi_fm[key].splitlines()[0]))
    for key in vi_fm.keys() - zh_fm.keys() - VI_ONLY:
        issue(path, 'front-matter', '(absent in zh)', f'key {key}')

    zh, vi = page_facts(zh_body), page_facts(vi_body)
    if zh['ids'] != vi['ids']:
        missing, extra = multiset_diff(zh['ids'], vi['ids'])
        issue(path, 'anchor', short(missing) or 'same ids', short(extra) or 'different order')
    for dup in sorted(k for k, n in Counter(vi['ids']).items() if n > 1):
        issue(path, 'duplicate-id', f'#{dup} once', f'{Counter(vi["ids"])[dup]} times', line_of(vi_text, dup))
    if zh['headings'] != vi['headings']:
        issue(path, 'heading', dict(sorted(zh['headings'].items())), dict(sorted(vi['headings'].items())))
    if zh['blocks'] != vi['blocks']:
        missing, extra = multiset_diff(zh['blocks'], vi['blocks'])
        issue(path, 'shortcode', short(missing) or 'same order', short(extra) or '(missing)')
    missing, extra = multiset_diff(zh['xrefs'], vi['xrefs'])
    if missing or extra:
        issue(path, 'shortcode', f'xref {short(missing)}', f'xref {short(extra)}')
    for kind, num, page, anchor in vi['xrefs']:
        target = (page or f'/{slug}').strip('/') or '_index'
        if anchor and anchor not in vi_ids.get(target, set()):
            issue(path, 'xref-target', f'#{anchor} in {target}', '(not found)', line_of(vi_text, f'anchor="{anchor}"'))
    missing, extra = multiset_diff(zh['fn_refs'], vi['fn_refs'])
    if missing or extra:
        issue(path, 'footnote', f'refs {short(missing)}', f'refs {short(extra)}')
    for label in sorted(set(zh['fn_defs']) | set(vi['fn_defs'])):
        if label in zh['fn_defs'] and vi['fn_defs'].count(label) != 1:
            issue(path, 'footnote', f'[^{label}] defined once', vi['fn_defs'].count(label))
        elif label not in zh['fn_defs']:
            issue(path, 'footnote', '(absent in zh)', f'[^{label}] defined')
    missing, extra = multiset_diff(zh['urls'], vi['urls'])
    if (missing or extra) and slug not in OWN_LINKS:
        issue(path, 'url', short(missing) or '(none)', short(extra) or '(missing)')
    for src in vi['images']:
        if src.startswith('/') and not (root / 'static' / src.lstrip('/')).is_file():
            issue(path, 'image', f'static{src}', '(not found)', line_of(vi_text, src))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('slugs', nargs='*', help='pages to check, e.g. ch1 glossary; default all')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--json', type=Path, help='also write issues as JSON')
    args = parser.parse_args(argv)

    zh_dir, vi_dir = args.root / 'content/zh', args.root / 'content/vi'
    for d in (zh_dir, vi_dir):
        if not d.is_dir():
            print(f'error: directory not found: {d}', file=sys.stderr)
            return 2

    issues: list[dict] = []

    def issue(file, kind, expected, actual, line=None):
        issues.append({'file': file, 'line': line, 'kind': kind, 'expected': str(expected), 'actual': str(actual)})

    zh_pages = {p.stem: p for p in zh_dir.glob('*.md')}
    vi_pages = {p.stem: p for p in vi_dir.glob('*.md')}
    if not args.slugs:
        for slug in sorted(zh_pages.keys() - vi_pages.keys()):
            issue(f'content/zh/{slug}.md', 'missing-page', 'Vietnamese page', '(missing)')
        for slug in sorted(vi_pages.keys() - zh_pages.keys() - VI_ONLY_PAGES):
            issue(f'content/vi/{slug}.md', 'extra-page', '(no zh page)', 'Vietnamese page')

    vi_texts = {slug: p.read_text(encoding='utf-8') for slug, p in vi_pages.items()}
    vi_ids = {slug: set(ct.all_ids(split_page(t)[1])) for slug, t in vi_texts.items()}
    selected = args.slugs or sorted(zh_pages.keys() & vi_pages.keys())
    drafts = 0
    for slug in selected:
        if slug not in zh_pages or slug not in vi_pages:
            issue(f'content/vi/{slug}.md', 'missing-page', 'page in zh and vi', '(missing)')
            continue
        drafts += 'draft' in split_page(vi_texts[slug])[0] and 'true' in split_page(vi_texts[slug])[0]['draft']
        check_page(args.root, slug, zh_pages[slug].read_text(encoding='utf-8'), vi_texts[slug], vi_ids, issue)

    issues.sort(key=lambda i: (i['file'], i['line'] or 0))
    for i in issues:
        loc = f"{i['file']}:{i['line']}" if i['line'] else i['file']
        print(f"{loc}: {i['kind']}: expected {i['expected']}, got {i['actual']}")
    if args.json:
        args.json.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding='utf-8')
    n = len(selected)
    if issues:
        print(f"checked {n} pages: {len(issues)} issues ({len({i['file'] for i in issues})} pages)")
        return 1
    print(f'checked {n} pages: OK ({drafts} drafts, {n - drafts} done)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
