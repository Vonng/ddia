#!/usr/bin/env python3
"""English–Vietnamese glossary: seed the term list and check consistency, read-only check.

  seed   add missing terms (book glossary headings, first *zh* (*en*) pair per chapter) as status="todo"
  check  validate data/glossary/vi.toml and the first `*vi* (*en*)` pair per chapter in content/vi
         --release also fails on todo terms that are in the book glossary or used in a non-draft chapter,
         and on book-glossary terms missing from the table
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import tomllib

HERE = Path(__file__).resolve().parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ct = _load('check_translation', 'check-translation.py')
cv = _load('check_vi', 'check-vi.py')

TABLE = 'data/glossary/vi.toml'
STATUSES = {'ok', 'todo'}
# ponytail: en chapters write terms as plain *term*; only zh/vi carry the (*english*) pair, so seed reads zh.
ZH_PAIR = re.compile(r'\*([^*\n]+)\*[（(]\*([A-Za-z][^*\n]*)\*[）)]')
VI_PAIR = re.compile(r'\*([^*\n]+)\*\s\(\*([A-Za-z][^*\n]*)\*\)')
HEADING = re.compile(r'^###\s+(.+?)\s*$', re.M)


def norm(term: str) -> str:
    return re.sub(r'\s+', ' ', term.replace('-', ' ')).strip().lower()


def load_table(root: Path) -> list[dict]:
    """Terms with their 1-based `[[term]]` line numbers in `_line`."""
    path = root / TABLE
    text = path.read_text(encoding='utf-8')
    lines = [i for i, l in enumerate(text.splitlines(), 1) if l.strip() == '[[term]]']
    terms = tomllib.loads(text).get('term', [])
    for term, line in zip(terms, lines):
        term['_line'] = line
    return terms


def book_terms(root: Path) -> list[str]:
    return HEADING.findall((root / 'content/en/glossary.md').read_text(encoding='utf-8'))


def first_pairs(text: str, pattern: re.Pattern) -> dict[str, tuple[str, str]]:
    """{norm(en): (vi-or-zh text, en)} for the first occurrence of each pair, code removed."""
    found: dict[str, tuple[str, str]] = {}
    for local, en in pattern.findall(ct.without_code(cv.split_page(text)[1])):
        found.setdefault(norm(en), (local.strip(), en.strip()))
    return found


def toml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def seed(root: Path) -> int:
    have = {norm(t['en']) for t in load_table(root)}
    wanted: dict[str, str] = {}
    for en in book_terms(root):
        wanted.setdefault(norm(en), en)
    for path in sorted((root / 'content/zh').glob('ch*.md'), key=lambda p: int(re.sub(r'\D', '', p.stem))):
        for key, (_, en) in first_pairs(path.read_text(encoding='utf-8'), ZH_PAIR).items():
            wanted.setdefault(key, en)
    new = [en for key, en in wanted.items() if key not in have]
    with (root / TABLE).open('a', encoding='utf-8') as f:
        for en in new:
            f.write(f'\n[[term]]\nen = {toml_str(en)}\nvi = ""\nstatus = "todo"\n')
    print(f'seed: {len(new)} terms added, {len(have)} kept')
    return 0


def check(root: Path, release: bool = False) -> int:
    issues: list[str] = []
    warns: list[str] = []

    def issue(file, line, kind, expected, actual):
        issues.append(f'{file}:{line}: {kind}: expected {expected}, got {actual}')

    terms = load_table(root)
    groups: dict[str, list[dict]] = {}
    for t in terms:
        groups.setdefault(norm(t.get('en', '')), []).append(t)
    for key, group in groups.items():
        seen: set[str] = set()
        for t in group:
            ctx = t.get('ctx')
            if len(group) > 1 and not ctx:
                issue(TABLE, t['_line'], 'missing-ctx', f'ctx for repeated term "{key}"', '(none)')
            elif len(group) > 1 and ctx in seen:
                issue(TABLE, t['_line'], 'duplicate', f'one entry per ("{key}", ctx)', f'ctx "{ctx}" twice')
            seen.add(ctx or '')
    for t in terms:
        status = t.get('status', 'ok')
        if status not in STATUSES:
            issue(TABLE, t['_line'], 'status', 'ok or todo', status)
        if not t.get('vi') and status != 'todo':
            issue(TABLE, t['_line'], 'empty-vi', f'vi for "{t.get("en")}"', '(empty)')
        if t.get('keep') and not t.get('note'):
            issue(TABLE, t['_line'], 'missing-note', f'note for kept term "{t.get("en")}"', '(none)')

    by_en = {k: g for k, g in groups.items()}
    book = {norm(e) for e in book_terms(root)}
    used: set[str] = set()
    ok = total = 0
    for path in sorted((root / 'content/vi').glob('ch*.md')):
        text = path.read_text(encoding='utf-8')
        fm = cv.split_page(text)[0]
        draft = 'true' in fm.get('draft', '')
        rel = f'content/vi/{path.name}'
        for key, (vi, en) in first_pairs(text, VI_PAIR).items():
            if key not in by_en:
                warns.append(f'{rel}: unknown-term: "{en}" not in table')
                continue
            if not draft:
                used.add(key)
            known = {norm(t['vi']) for t in by_en[key] if t.get('vi')}
            if not known:
                continue
            total += 1
            if norm(vi) in known:
                ok += 1
            else:
                issue(rel, cv.line_of(text, f'*{vi}*') or 0, 'mismatch', f'"{en}" → {sorted(known)}', f'"{vi}"')

    if release:
        for key in sorted(book - by_en.keys()):
            issue(TABLE, 0, 'coverage', f'term "{key}" from content/en/glossary.md', '(missing)')
        for key, group in by_en.items():
            for t in group:
                if t.get('status', 'ok') == 'todo' and (key in book or key in used):
                    issue(TABLE, t['_line'], 'todo', f'translation for "{t["en"]}"', 'status = "todo"')

    for line in warns + issues:
        print(line)
    print(f'pairs: {ok} khớp / {total} cặp')
    print(f'glossary: {len(terms)} terms, {len(issues)} issues, {len(warns)} warnings')
    return 1 if issues else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('command', choices=['seed', 'check'])
    parser.add_argument('--release', action='store_true')
    parser.add_argument('--root', type=Path, default=HERE.parent)
    args = parser.parse_args(argv)
    return seed(args.root) if args.command == 'seed' else check(args.root, args.release)


if __name__ == '__main__':
    sys.exit(main())
