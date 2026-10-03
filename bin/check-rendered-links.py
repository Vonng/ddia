#!/usr/bin/env python3
"""Check internal links, fragments and media in built Hugo pages, read-only.

By default check the primary Simplified Chinese pages; --all includes every
rendered language and generated page. --second-edition includes all HTML source
pages except v1/v1_tw and still checks every local destination. Cross-edition
links are excluded only from the default scope. This script requires an existing
build and never runs Hugo.
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


LANGUAGES = ('zh', 'tw', 'v1', 'v1_tw', 'en')
EXCLUDED_PREFIXES = ('/tw/', '/v1/', '/v1_tw/')
SKIPPED_SCHEMES = {'data', 'javascript', 'mailto', 'tel'}


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets = []; self.anchors = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key in ('id', 'name'):
            if values.get(key):
                self.anchors.add(values[key])
        for key in ('href', 'src'):
            if values.get(key):
                self.targets.append(values[key])
        for candidate in (values.get('srcset') or '').split(','):
            parts = candidate.strip().split(maxsplit=1)
            if parts:
                self.targets.append(parts[0])


def output_path(public: Path, url_path: str) -> Path | None:
    relative = unquote(url_path).lstrip('/'); direct = public/relative
    candidates = [direct]
    if url_path.endswith('/') or not direct.suffix:
        candidates.insert(0, direct/'index.html')
    if not direct.suffix:
        candidates.append(public/f'{relative}.html')
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def run_checks(root: Path, public: Path, *, language: str = 'zh', all_pages: bool = False,
               second_edition: bool = False,
               origin: str = 'https://ddia.vonng.com') -> dict:
    public = public.resolve(); errors = []; pages = {}; sources = []
    if all_pages and second_edition:
        raise ValueError('--all and --second-edition are mutually exclusive')
    if all_pages or second_edition:
        sources = sorted(path for path in public.rglob('*.html')
                         if not second_edition or path.relative_to(public).parts[0] not in ('v1', 'v1_tw'))
        excluded = ()
        if not sources:
            errors.append({'check': 'missing rendered pages', 'target': str(public)})
    else:
        prefix = '' if language == 'zh' else language
        sources = [public/prefix/'index.html']
        sources += [public/prefix/source.stem/'index.html'
                    for source in sorted((root/'content'/language).glob('*.md')) if source.stem != '_index']
        excluded = EXCLUDED_PREFIXES if language == 'zh' else ()

    def parse(path):
        resolved = path.resolve()
        if resolved not in pages:
            parser = References(); parser.feed(path.read_text(encoding='utf-8')); pages[resolved] = parser
        return pages[resolved]

    for path in sources:
        if not path.is_file():
            errors.append({'check': 'missing rendered page', 'target': str(path)})
        else:
            parse(path)
    checked = 0; hostname = urlsplit(origin).netloc
    # Destination parsing may add cached pages; iterate only the source list.
    for source in sources:
        if not source.is_file():
            continue
        source_rel = source.relative_to(public).as_posix()
        source_url = '/' if source_rel == 'index.html' else f'/{source_rel.removesuffix("index.html")}'
        for raw in parse(source).targets:
            try:
                target = urlsplit(urljoin(origin+source_url, raw))
            except ValueError:
                errors.append({'source': source_url, 'check': 'invalid URL', 'target': raw}); continue
            if target.scheme in SKIPPED_SCHEMES or target.netloc not in ('', hostname):
                continue
            if any(target.path.startswith(prefix) or target.path == prefix.rstrip('/') for prefix in excluded):
                continue
            checked += 1; destination = output_path(public, target.path)
            if destination is None:
                errors.append({'source': source_url, 'check': 'missing rendered target', 'target': raw})
            elif target.fragment and destination.suffix == '.html':
                if unquote(target.fragment) not in parse(destination).anchors:
                    errors.append({'source': source_url, 'check': 'missing rendered fragment', 'target': raw})
    scope = ('all rendered pages' if all_pages else 'rendered HTML outside v1/v1_tw' if second_edition
             else f'rendered {language} content pages')
    return {'scope': scope,
            'totals': {'source_pages': len(sources), 'parsed_pages': len(pages), 'internal_targets': checked},
            'errors': errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--public', type=Path, help='existing Hugo output directory; default ROOT/public')
    parser.add_argument('--language', choices=LANGUAGES, default='zh')
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument('--all', action='store_true', help='check all rendered pages and languages')
    scope.add_argument('--second-edition', action='store_true',
                       help='check all HTML sources except v1/v1_tw; check destinations in every edition')
    parser.add_argument('--origin', default='https://ddia.vonng.com', help='site origin for absolute same-site URLs')
    parser.add_argument('--json', type=Path, help='explicit optional report destination')
    args = parser.parse_args(argv); root = args.root.resolve()
    try:
        result = run_checks(root, args.public or root/'public', language=args.language, all_pages=args.all,
                            second_edition=args.second_edition, origin=args.origin.rstrip('/'))
    except (OSError, ValueError) as error:
        print(f'FAIL rendered links: {error}'); return 1
    if args.json:
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f"{'FAIL' if result['errors'] else 'PASS'} rendered links ({len(result['errors'])} errors)")
    print(json.dumps(result['totals'], sort_keys=True))
    for error in result['errors']:
        print(json.dumps(error, ensure_ascii=False))
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
