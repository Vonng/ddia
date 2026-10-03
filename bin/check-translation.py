#!/usr/bin/env python3
"""Check second-edition translation structure and shared-page links, read-only.

Run without arguments for all 14 Simplified Chinese chapters and shared pages.
This validates structural and editorial invariants, not translation semantics.
Reports go to stdout unless --json explicitly names a report file. Importing
this module does not read the repository or produce output.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ATTR = re.compile(r'([\w-]+)=(["\'])(.*?)\2', re.S)
SC = re.compile(r'\{\{<\s*(fig|eg|xref)\b(.*?)\s*/?>\}\}', re.S)
ID = re.compile(r'\{#([^\s}]+)[^}]*\}|<a\s+id=["\']([^"\']+)["\']')
HEAD = re.compile(r'^[ \t]*(#{1,6})\s+(.+?)(?:\s+\{#([^\s}]+)\})?\s*$', re.M)
MDLINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^\s)]+)(?:\s+[^)]*)?\)')
MDIMAGE = re.compile(r'!\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)')
REFERENCE_HEADING = re.compile(r'^###\s+(?:References|参考文献)(?:\s+\{#[^}]+\})?\s*$', re.M)
TABLE_SEPARATOR = re.compile(r'^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$', re.M)
ROLES = {'References': 'references', '参考文献': 'references', 'Footnotes': 'footnotes', '脚注': 'footnotes'}

# These corrections predate the translation review and were checked against
# archived sources/DOIs. Only these exact replacements are canonicalized.
BIBLIOGRAPHY_REPLACEMENTS = {
    'https://blog.christianposta.com/microservices/why-microservices-should-be-event-driven-autonomy-vs-authority/': 'https://perma.cc/E6N9-3X92',
    'https://blog.rapid7.com/2014/03/14/synchronizing-clocks-in-a-cassandra-cluster-pt-1-the-problem/': 'https://perma.cc/N3RV-5LNL',
    'https://codemesh.io/codemesh2016/mark-callaghan': 'https://www.youtube.com/watch?v=tgzkgZVXKB4',
    'https://core.ac.uk/download/pdf/158372754.pdf': 'https://doi.org/10.1145/3183713.3190657',
    'https://cse.buffalo.edu/~demirbas/publications/hlc.pdf': 'https://doi.org/10.1007/978-3-319-14472-6_2',
    'https://doi.org/10.1145/2639988.2639988': 'https://doi.org/10.1145/2639988.2655736',
    'https://doi.org/10.5555/2665671.2665726': 'https://doi.org/10.1145/2678373.2665726',
    'https://eng.uber.com/h3/': 'https://www.uber.com/blog/h3/',
    'https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying': 'https://perma.cc/2JHR-FR64',
    'https://iarapakis.github.io/papers/TOIS17.pdf': 'https://doi.org/10.1145/3106372',
    'https://pdos.csail.mit.edu/6.824/papers/bayou-conflicts.pdf': 'https://doi.org/10.1145/224056.224070',
    'https://smeiklej.com/files/aft19a.pdf': 'https://doi.org/10.1145/3318041.3355458',
    'https://towardsdatascience.com/understanding-hierarchies-in-oracle-43f85561f3d9': 'https://perma.cc/5ZLR-Q7EW',
    'https://unlimited.humio.com/rs/756-LMY-106/images/Distributed-Systems-Observability-eBook.pdf': 'https://perma.cc/M6JL-XKCM',
    'https://w6113.github.io/files/papers/btreesurvey-graefe.pdf': 'https://doi.org/10.1561/1900000028',
    'https://www.cs.purdue.edu/homes/hosking/197/canon/karp.pdf': 'https://doi.org/10.1007/978-1-4684-2001-2_9',
    'https://www.nilebits.com/blog/2024/09/sync-engines-future-web-applications/': 'https://perma.cc/5N73-5M3V',
    'https://www.pagerduty.com/blog/the-discovery-of-apache-zookeepers-poison-packet/': 'https://perma.cc/RV6L-Y5CQ',
    'https://www.thenile.dev/blog/storage-compute': 'https://perma.cc/QCV3-XJNZ',
    'https://www.taylorfrancis.com/books/mono/10.1201/9781315257396/drift-failure-sidney-dekker': 'https://doi.org/10.1201/9781315257396',
    'https://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442': 'https://web.archive.org/web/20120712231854/http://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442',
    'https://codahale.com/you-cant-sacrifice-partition-tolerance/': 'https://perma.cc/6GJU-X4G5',
    '10.1145/2639988.2639988': '10.1145/2639988.2655736',
    '10.5555/2665671.2665726': '10.1145/2678373.2665726',
}

EXCEPTIONS = [
    'Language-specific front matter, translated captions and figure layout attributes need not match EN.',
    'Example headings in EN, including the nested ch8 meeting-room example, become eg containers (or retained ch13 example labels) in ZH.',
    'EN ch9 sidebar_distributed_determinism h4 is a ZH TIP with the same preserved identifier.',
    'ZH ch8 explicitly adds the references anchor for its existing bibliography.',
    'Bibliography equality permits only the exact historical URL/DOI corrections listed in this script.',
    'Footnotes/脚注 and References/参考文献 are equivalent heading roles.',
    'Chapter-root links and descriptive labels are not forced to equal section titles.',
    'Removing a duplicate extracted figure caption does not require a fixed xref count; every remaining target is checked.',
    'Other language/edition links are outside this source check; rendered-link validation covers them separately.',
]


def clean(text: str) -> str:
    text = re.sub(r'[*_`]', '', text).strip()
    pairs = (('“', '”'), ('‘', '’'), ('"', '"'), ("'", "'"))
    while len(text) > 1 and any(text.startswith(a) and text.endswith(b) for a, b in pairs):
        text = text[1:-1].strip()
    return re.sub(r'\s+', ' ', text.replace('‘', '“').replace('’', '”'))


def without_code(text: str, *, inline: bool = True) -> str:
    """Keep offsets while masking fenced blocks and inline code."""
    output = []; fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match and fence is None:
            fence = (match[1][0], len(match[1]))
        elif match and fence and match[1][0] == fence[0] and len(match[1]) >= fence[1]:
            output.append(re.sub(r'[^\r\n]', ' ', line)); fence = None; continue
        output.append(re.sub(r'[^\r\n]', ' ', line) if fence else line)
    prose = ''.join(output)
    return re.sub(r'(`+).*?\1', lambda m: ' ' * len(m[0]), prose) if inline else prose


def attrs(body: str) -> dict[str, str]:
    return {key: value for key, _, value in ATTR.findall(body)}


def sc_records(text: str, kind: str) -> list[dict[str, str]]:
    return [attrs(body) for typ, body in SC.findall(without_code(text)) if typ == kind]


def all_ids(text: str) -> list[str]:
    prose = without_code(text)
    found = [a or b for a, b in ID.findall(prose)]
    found += [attrs(body)['id'] for kind, body in SC.findall(prose)
              if kind in ('fig', 'eg') and 'id' in attrs(body)]
    return found


def headings(text: str, chapter: int) -> list[tuple[int, str]]:
    found = []
    for hashes, title, anchor in HEAD.findall(without_code(text, inline=False)):
        if re.match(r'(?:Example\s+|例\s*)\d+-\d+', clean(title)):
            continue
        if chapter == 9 and anchor == 'sidebar_distributed_determinism':
            continue
        found.append((len(hashes), anchor or ROLES.get(clean(title), clean(title))))
    return found


def heading_titles(text: str) -> dict[str, str]:
    # Mask fenced code, but retain inline-code text in headings for their labels.
    found = {anchor or ROLES.get(clean(title), ''): clean(title)
             for _, title, anchor in HEAD.findall(without_code(text, inline=False))
             if anchor or clean(title) in ROLES}
    # The determinism sidebar retains an HTML anchor instead of a prose h4.
    for match in re.finditer(r'<a\s+id=["\']([^"\']+)["\'][^>]*></a>\s*\n\s*>\s*\[!\w+\]\s+([^\n]+)', text):
        found[match[1]] = clean(match[2])
    return found


def example_signature(text: str) -> list[tuple[str | None, str | None]]:
    prose = without_code(text, inline=False); records = []
    for match in SC.finditer(prose):
        if match[1] == 'eg':
            rec = attrs(match[2]); records.append((match.start(), rec.get('id'), rec.get('num')))
    for match in HEAD.finditer(prose):
        number = re.match(r'(?:Example\s+|例\s*)(\d+-\d+)', clean(match[2]))
        if number:
            records.append((match.start(), match[3], number[1]))
    return [(anchor, number) for _, anchor, number in sorted(records)]


def reference_regions(text: str) -> tuple[str, str | None]:
    match = REFERENCE_HEADING.search(text)
    return (text[:match.start()], text[match.end():]) if match else (text, None)


def footnote_references(text: str) -> list[str]:
    # Count the intended body citation; reject broken column-zero syntax below.
    return re.findall(r'\[\^([^\]]+)\]', without_code(reference_regions(text)[0]))


def footnote_definitions(text: str) -> list[str]:
    tail = reference_regions(text)[1]
    return re.findall(r'^\[\^([^\]]+)\]:', tail or '', re.M)


def reference_tail(text: str) -> list[str] | None:
    tail = reference_regions(text)[1]
    if tail is None:
        return None
    for old, new in BIBLIOGRAPHY_REPLACEMENTS.items():
        tail = tail.replace(old, new)
    return [line.rstrip() for line in tail.splitlines()]


def fence_signature(text: str) -> tuple[list[str], bool]:
    signature = []; fence = None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if not match:
            continue
        mark, info = match.groups()
        if fence is None:
            fence = (mark[0], len(mark)); signature.append(info.strip())
        elif mark[0] == fence[0] and len(mark) >= fence[1] and not info.strip():
            fence = None; signature.append('')
    return signature, fence is None


def normalize_target(target: str) -> str:
    return re.sub(r'^/(?:en|zh)/ch', '/ch', target).rstrip('/')


def source_links(text: str) -> list[re.Match[str]]:
    prose = without_code(text, inline=False)
    spans = [(m.start(), m.end()) for m in re.finditer(r'(`+).*?\1', prose)]
    return [m for m in MDLINK.finditer(prose)
            if not any(start <= m.start() < end for start, end in spans)]


def issue(errors: list[dict], path: str, check: str, detail, line: int | None = None) -> None:
    record = {'file': path, 'check': check, 'detail': detail}
    if line is not None:
        record['line'] = line
    errors.append(record)


def check_images(root: Path, text: str, path: str, errors: list[dict], totals: Counter) -> None:
    for match in MDIMAGE.finditer(without_code(text)):
        target = urlsplit(match[1])
        if target.scheme or target.netloc:
            continue
        totals['markdown_images'] += 1
        resource = root/'static'/unquote(target.path).lstrip('/')
        if not target.path.startswith('/') or not resource.is_file():
            issue(errors, path, 'image resource', match[1], text[:match.start()].count('\n')+1)


def check_index_terms(root: Path, errors: list[dict], totals: Counter) -> None:
    """Check only explicitly reviewed labels at corresponding index bullets."""
    config_path = root/'bin/translation-terms.json'
    if not config_path.is_file():
        return
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if config.get('scope') != 'index_labels' or not isinstance(config.get('terms'), dict):
        issue(errors, 'bin/translation-terms.json', 'index term configuration', 'expected scope=index_labels and a terms object')
        return
    def bullets(path):
        rows = []
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            if match:
                rows.append((number, len(match[1]), match[2].split(', [', 1)[0].strip()))
        return rows
    a = bullets(root/'content/en/indexes.md'); b = bullets(root/'content/zh/indexes.md')
    totals['index_bullets'] = len(b); totals['configured_index_labels'] = len(config['terms'])
    if len(a) != len(b):
        issue(errors, 'content/zh/indexes.md', 'index bullet alignment', {'en': len(a), 'zh': len(b)})
        return
    found = set()
    for (_, depth, label), (line, other_depth, translated) in zip(a, b):
        if label not in config['terms']:
            continue
        found.add(label); totals['reviewed_index_occurrences'] += 1
        expected = config['terms'][label]
        if depth != other_depth or translated != expected:
            issue(errors, 'content/zh/indexes.md', 'reviewed index label',
                  {'english': label, 'actual': translated, 'expected': expected, 'same_depth': depth == other_depth}, line)
    for label in config['terms'].keys()-found:
        issue(errors, 'bin/translation-terms.json', 'reviewed index label absent from English index', label)


def run_checks(root: Path, chapters: list[int] | None = None) -> dict:
    """Return a structured read-only report. Extension checks can append issues."""
    chapters = chapters or list(range(1, 15)); errors = []; totals = Counter(); rows = []
    en = {n: (root / f'content/en/ch{n}.md').read_text(encoding='utf-8') for n in range(1, 15)}
    zh = {n: (root / f'content/zh/ch{n}.md').read_text(encoding='utf-8') for n in range(1, 15)}
    title_en = {n: heading_titles(t) for n, t in en.items()}
    title_zh = {n: heading_titles(t) for n, t in zh.items()}
    ids = {n: set(all_ids(t)) for n, t in zh.items()}; definitions = {}
    for n, text in zh.items():
        for kind in ('fig', 'eg'):
            for rec in sc_records(text, kind):
                definitions[(n, rec.get('id'))] = (kind, rec.get('num'))
        for _, title, anchor in HEAD.findall(without_code(text)):
            match = re.match(r'(?:Example\s+|例\s*)(\d+-\d+)', clean(title))
            if match and anchor:
                definitions[(n, anchor)] = ('eg', match[1])
        for match in re.finditer(r'\{#([^\s}]+)\s+num="([^"]+)"[^}]*\}', text):
            definitions[(n, match[1])] = ('tbl', match[2])

    for n in chapters:
        a, b = en[n], zh[n]; path = f'content/zh/ch{n}.md'; checks = {}; initial = len(errors)
        def check(name, ok, detail=''):
            checks[name] = bool(ok)
            if not ok:
                issue(errors, path, name, detail)
        part = 1 if n <= 5 else 2 if n <= 10 else 3
        metadata = [r'^book_kind:\s*chapter\s*$', rf'^book_number:\s*["\']?{n}["\']?\s*$',
                    rf'^book_part:\s*["\']?{"I" * part}["\']?\s*$', rf'^weight:\s*{100 * part + n}\s*$']
        front = b.split('---', 2)[1] if b.startswith('---\n') else ''
        check('chapter metadata', all(re.search(p, front, re.M) for p in metadata))
        ea, za = Counter(all_ids(a)), Counter(all_ids(b))
        if n == 8 and 'references' not in ea:
            za.subtract({'references': 1}); za = +za
        check('anchor inventory', ea == za, {'missing': list((ea-za).elements()), 'extra': list((za-ea).elements())})
        check('no duplicate explicit ids', len(all_ids(b)) == len(set(all_ids(b))))
        check('prose heading levels and anchors', headings(a, n) == headings(b, n), {'en': headings(a, n), 'zh': headings(b, n)})
        sig = lambda records: [tuple(r.get(k) for k in ('id', 'num', 'src', 'link')) for r in records]
        fa, fb = sc_records(a, 'fig'), sc_records(b, 'fig')
        check('figure identifiers numbers paths links', sig(fa) == sig(fb))
        check('figure resources', all(r.get('src') and (root/'static'/r['src'].lstrip('/')).is_file() for r in fb))
        check('example identifiers and numbers', example_signature(a) == example_signature(b),
              {'en': example_signature(a), 'zh': example_signature(b)})
        check('footnote reference sequence', footnote_references(a) == footnote_references(b))
        check('footnote definition ids', footnote_definitions(a) == footnote_definitions(b))
        check('unique footnote definitions', len(footnote_definitions(b)) == len(set(footnote_definitions(b))))
        check('all body citations have definitions', set(footnote_references(b)) <= set(footnote_definitions(b)))
        for language, text in (('en', a), ('zh', b)):
            body = without_code(reference_regions(text)[0])
            for match in re.finditer(r'^\[\^([^\]]+)\]:', body, re.M):
                issue(errors, f'content/{language}/ch{n}.md', 'body citation mistaken for a definition',
                      f'[^'+match[1]+']: at column zero is parsed as a definition; keep the citation in its sentence',
                      body[:match.start()].count('\n')+1)
        check('bibliography preservation with listed URL corrections', reference_tail(a) == reference_tail(b))
        fence_a, fence_b = fence_signature(a), fence_signature(b)
        check('balanced fences and language sequence', fence_a[1] and fence_b[1] and fence_a[0] == fence_b[0])
        check('table count', len(TABLE_SEPARATOR.findall(without_code(a))) == len(TABLE_SEPARATOR.findall(without_code(b))))
        xrefs = sc_records(b, 'xref')
        for rec in xrefs:
            target = re.fullmatch(r'/ch(\d+)/?', rec.get('page', ''))
            kinds = [k for k in ('fig', 'eg', 'tbl') if k in rec]
            actual = definitions.get((int(target[1]), rec.get('anchor'))) if target else None
            valid = bool(target and rec.get('anchor') in ids.get(int(target[1]), set()))
            if kinds:
                valid = valid and len(kinds) == 1 and actual == (kinds[0], rec[kinds[0]])
            if not valid:
                issue(errors, path, 'xref target type and number', {'xref': rec, 'target': actual})
        checks['xref target type and number'] = not any(e['check'] == 'xref target type and number' for e in errors[initial:])
        totals.update(figures=len(fb), examples=len(sc_records(b, 'eg')), xrefs=len(xrefs), footnote_references=len(footnote_references(b)))
        rows.append({'chapter': n, 'checks': checks})
        check_images(root, a, f'content/en/ch{n}.md', errors, totals)

    # Shared pages use the same page+anchor identity as chapters. For bilingual
    # chapter links, same-target occurrence order distinguishes title links from
    # descriptive links. Explicit quotation/TOC entries classify shared titles.
    files = sorted((root/'content/zh').glob('*.md'))
    for file in files:
        chapter_match = re.fullmatch(r'ch(\d+)\.md', file.name)
        n = int(chapter_match[1]) if chapter_match else None
        if n is not None and n not in chapters:
            continue
        text = file.read_text(encoding='utf-8'); path = file.relative_to(root).as_posix()
        check_images(root, text, path, errors, totals)
        english = root/'content/en'/file.name; title_flags = defaultdict(list)
        if english.is_file():
            for match in source_links(english.read_text(encoding='utf-8')):
                target = normalize_target(match[2]); m = re.fullmatch(r'/ch(\d+)#(.+)', target)
                if m:
                    title = title_en.get(int(m[1]), {}).get(m[2], '')
                    title_flags[target].append(bool(title and clean(match[1]).casefold() == title.casefold()))
        occurrences = Counter()
        for match in source_links(text):
            label, target = match.groups(); line = text[:match.start()].count('\n') + 1
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path.startswith(('/en/', '/zh/')):
                issue(errors, path, 'language prefix in primary-page link', target, line); continue
            if parsed.path in ('/tw', '/v1', '/v1_tw') or parsed.path.startswith(('/tw/', '/v1/', '/v1_tw/')):
                continue
            target = normalize_target(target)
            m = re.fullmatch(r'/ch(\d+)(?:#(.+))?', target)
            if target.startswith('#') and n is not None:
                m = re.fullmatch(r'/ch(\d+)#(.+)', f'/ch{n}{target}')
            if not m:
                if parsed.path.startswith('/') and parsed.path and parsed.path != '/':
                    slug = parsed.path.strip('/')
                    if not (root/'content/zh'/f'{slug}.md').is_file() and not (root/'static'/slug).is_file():
                        issue(errors, path, 'internal page or resource target', target, line)
                continue
            number = int(m[1]); anchor = unquote(m[2]) if m[2] else None
            totals['chapter_links'] += 1
            if number not in ids or (anchor and anchor not in ids[number]):
                issue(errors, path, 'internal chapter target', target, line); continue
            if not anchor:
                continue
            expected = title_zh.get(number, {}).get(anchor)
            position = occurrences[target]; occurrences[target] += 1
            english_title = position < len(title_flags[target]) and title_flags[target][position]
            before = text[max(0, match.start()-2):match.start()]
            after = text[match.end():match.end()+2]
            quoted = bool(before and after and before[-1] in '“‘"\'' and after[0] in '”’"\'')
            prefix = text[text.rfind('\n', 0, match.start())+1:match.start()]
            toc_entry = bool(re.fullmatch(r'\s*(?:[-*+]\s+|#{1,6}\s+)', prefix))
            toc_page = file.stem == 'toc' or file.stem.startswith('part-')
            title_link = english_title or (n is None and (quoted or (toc_page and toc_entry)))
            if expected and title_link:
                totals['exact_heading_links'] += 1
                if n is None:
                    totals['shared_heading_links'] += 1
                if clean(label) != expected:
                    issue(errors, path, 'heading link label', {'target': target, 'actual': clean(label), 'expected': expected}, line)
        totals['source_pages'] += 1

    check_index_terms(root, errors, totals)
    return {'scope': '14 Simplified Chinese second-edition chapters and shared primary-language pages; explicitly reviewed index labels only',
            'exceptions': EXCEPTIONS, 'totals': dict(totals), 'chapters': rows, 'errors': errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chapters', nargs='*', type=int, help='source chapters to check; default all 14 (shared pages always checked)')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--json', type=Path, help='explicit optional report destination; defaults to stdout only')
    args = parser.parse_args(argv)
    if any(n < 1 or n > 14 for n in args.chapters):
        parser.error('chapter numbers must be between 1 and 14')
    try:
        result = run_checks(args.root.resolve(), args.chapters)
    except (OSError, ValueError) as error:
        print(f'FAIL translation checks: {error}'); return 1
    if args.json:
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    status = 'FAIL' if result['errors'] else 'PASS'
    print(f"{status} translation checks ({len(result['chapters'])} chapters; {len(result['errors'])} errors)")
    print(json.dumps(result['totals'], ensure_ascii=False, sort_keys=True))
    for error in result['errors']:
        print(json.dumps(error, ensure_ascii=False))
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
