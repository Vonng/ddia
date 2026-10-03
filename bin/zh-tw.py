#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys
import re
import unicodedata

EXTERNAL_URL_RE = re.compile(r'https?://[^\s<>]+')


def convert_preserving_external_urls(converter, text):
    """执行简繁转换，但保持外部 URL 的字节内容不变。"""
    urls = []

    def stash(match):
        urls.append(match.group(0))
        return f'__DDIA_EXTERNAL_URL_{len(urls) - 1}__'

    converted = converter.convert(EXTERNAL_URL_RE.sub(stash, text))
    for index, url in enumerate(urls):
        converted = converted.replace(f'__DDIA_EXTERNAL_URL_{index}__', url)
    return converted


def process_urls(text, src_folder, dst_folder):
    """处理 Markdown 中的相对 URL"""
    # 定义需要处理的页面路径（不带.md后缀）
    page_paths = [
        '/ch1', '/ch2', '/ch3', '/ch4', '/ch5', '/ch6',
        '/ch7', '/ch8', '/ch9', '/ch10', '/ch11', '/ch12', '/ch13', '/ch14',
        '/part-i', '/part-ii', '/part-iii', 
        '/preface', '/glossary', '/colophon', '/contrib', '/indexes', '/toc'
    ]
    
    # 对每个页面路径进行替换
    for page_path in page_paths:
        # 匹配 Markdown 链接格式 [text](page_path) 或 [text](page_path#anchor)
        pattern = rf'\[([^\]]*)\]\(([^)]*)({re.escape(page_path)})(#[^)]*)?\)'
        # 替换为添加 /tw 前缀的版本
        def replace_func(match):
            text_part = match.group(1)
            folder_part = match.group(2) or ''
            page_part = match.group(3)
            anchor_part = match.group(4) or ''
            if not folder_part:
                return f'[{text_part}](/{dst_folder}{page_part}{anchor_part})'  # 默认版本没有语言前缀，添加目标版本前缀
            elif folder_part[1:] == src_folder:
                return f'[{text_part}](/{dst_folder}{page_part}{anchor_part})'  # 其它中文版本，有类似 /v1 的前缀，根据输入参数进行替换
            else:
                text = f'[{text_part}]({folder_part}{page_part}{anchor_part})'
                print(f'unknown folder part in: {text}, keep it unchanged')
                return text
        text = re.sub(pattern, replace_func, text)

    # 第二版繁体页面中的第一版链接应指向第一版繁体页面。
    if src_folder == 'zh' and dst_folder == 'tw':
        text = re.sub(
            r'(\[[^\]]*\]\()/v1(?=[/#)])',
            r'\1/v1_tw',
            text,
        )
    
    return text


def make_converter(cfg):
    """Support both native OpenCC and opencc-python-reimplemented configs."""
    import opencc
    try:
        return opencc.OpenCC(cfg)
    except FileNotFoundError:
        if cfg.endswith('.json'):
            return opencc.OpenCC(cfg[:-5])
        raise

def convert_file_legacy(src_filepath, dst_filepath, src_folder, dst_folder, cfg='s2twp.json'):
    print("convert %s to %s" % (src_filepath, dst_filepath))
    converter = make_converter(cfg)
    with open(src_filepath, "r", encoding='utf-8') as src, open(dst_filepath, "w+", encoding='utf-8') as dst:
        dst.write("\n".join(
            process_urls(
                convert_preserving_external_urls(converter, line.rstrip())
                    .replace('一箇', '一個')
                    .replace('髮送', '傳送')
                    .replace('髮布', '釋出')
                    .replace('髮生', '發生')
                    .replace('髮出', '發出')
                    .replace('嚐試', '嘗試')
                    .replace('線上性一致', '在線性一致')    # 优先按"在线"解析了？
                    .replace('復雜', '複雜')
                    .replace('討論瞭', '討論了')
                    .replace('瞭解釋', '了解釋')
                    .replace('瞭如', '了如')                # 引入了如, 實現了如, 了如何, 了如果, 了如此
                    .replace('了如指掌', '瞭如指掌')        # 针对上一行的例外情况
                    .replace('明瞭', '明了')                # 闡明了, 聲明了, 指明了
                    .replace('倒黴', '倒楣')
                    .replace('區域性性', '區域性')
                    .replace('下麵條件', '下面條件')        # 优先按"面条"解析了？
                    .replace('當日志', '當日誌')            # 优先按"当日"解析了？
                    .replace('真即時間', '真實時間')        # 优先按"实时"解析了？
                    .replace('面向物件', '物件導向')
                    .replace('獨立完成', '獨力完成')
                    .replace('非規範化', '反正規化')
                    .replace('規範化', '正規化')
                    .replace('可擴充套件性', '可擴展性')  # extensibility，不是軟體套件
                    .replace('隻影響', '只影響')
                    .replace('云原生', '雲原生')
                    .replace('云服務', '雲服務'),
                src_folder, dst_folder
            )
            for line in src))

def convert_legacy(zh_folder, tw_folder):
    home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '..'))
    zh_dirpath = os.path.join(home, 'content', zh_folder)
    tw_dirpath = os.path.join(home, 'content', tw_folder)
    for file in os.listdir(zh_dirpath):
        if file.endswith('.md'):
            zh_filepath = os.path.join(zh_dirpath, file)
            tw_filepath = os.path.join(tw_dirpath, file)
            convert_file_legacy(zh_filepath, tw_filepath, zh_folder, tw_folder)


# Only the second edition uses these repairs. The first-edition path above is
# deliberately unchanged so its archived output can still be reproduced.
LEGACY_FIXES = (
    ('一箇', '一個'), ('髮送', '傳送'), ('髮布', '釋出'),
    ('髮生', '發生'), ('髮出', '發出'), ('嚐試', '嘗試'),
    ('線上性一致', '在線性一致'), ('復雜', '複雜'),
    ('討論瞭', '討論了'), ('瞭解釋', '了解釋'), ('瞭如', '了如'),
    ('了如指掌', '瞭如指掌'), ('明瞭', '明了'), ('倒黴', '倒楣'),
    ('區域性性', '區域性'), ('下麵條件', '下面條件'),
    ('當日志', '當日誌'), ('真即時間', '真實時間'),
    ('面向物件', '物件導向'), ('獨立完成', '獨力完成'),
    ('非規範化', '反正規化'), ('規範化', '正規化'),
    ('可擴充套件性', '可擴展性'), ('隻影響', '只影響'),
    ('云原生', '雲原生'), ('云服務', '雲服務'),
)
V2_FIXES = LEGACY_FIXES + (
    ('跳錶', '跳表'), ('覆制', '複製'), ('復制', '複製'),
    ('隻讀', '只讀'), ('隻需', '只需'), ('隻字', '只字'),
    ('影片遊戲', '電子遊戲'),
)
SHORTCODE_RE = re.compile(r'\{\{[<%].*?[>%]\}\}')
CAPTION_RE = re.compile(r'(\bcaption\s*=\s*)("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')')
INLINE_CODE_RE = re.compile(r'(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)', re.DOTALL)
HTML_RE = re.compile(r'<!--.*?-->|</?[A-Za-z][^>]*>', re.DOTALL)
ANCHOR_RE = re.compile(r'\{#[^}]+\}')
PAGE_NAMES = {*(f'ch{n}' for n in range(1, 15)), 'part-i', 'part-ii',
              'part-iii', 'preface', 'glossary', 'colophon', 'contrib',
              'indexes', 'toc'}


def process_url_v2(url):
    """Rewrite only a known local page; keep the suffix and external bytes."""
    if re.match(r'^/v1(?=[/#?]|$)', url):
        return '/v1_tw' + url[3:]
    match = re.fullmatch(r'/(?:zh/)?([^/#?]+)(/?(?:[?#].*)?)', url)
    if match and match[1] in PAGE_NAMES:
        return '/tw/' + match[1] + match[2]
    return url


def protected_line(text, convert_prose, *, historical_title=False, convert_identifier=None,
                   reviewed_fragments=()):
    """Protect the literal forms used by this repository's Markdown sources."""
    literals = []

    def stash(value):
        token = f'\ue000{len(literals)}\ue001'
        literals.append(value)
        return token

    # Contribution titles are historical data, including quoted incorrect
    # spellings and before/after examples. Translate the table's other cells.
    if historical_title:
        cells = text.split('|')
        if len(cells) == 6:
            cells[3] = stash(cells[3])
            text = '|'.join(cells)
    text = INLINE_CODE_RE.sub(lambda m: stash(m[0]), text)
    for source, target in reviewed_fragments:
        if source not in text:
            raise ValueError('A reviewed TW fragment overlaps protected code or another override')
        text = text.replace(source, stash(target))

    def caption(m):
        quoted = m[2]
        return m[1] + quoted[0] + convert_prose(quoted[1:-1]) + quoted[-1]

    def shortcode(match):
        return stash(CAPTION_RE.sub(caption, match[0]))

    text = SHORTCODE_RE.sub(shortcode, text)
    def html(match):
        value = match[0]
        # Old TW pages have translated Chinese ID aliases. Preserve those
        # established IDs while keeping ASCII IDs/attributes literal.
        if convert_identifier:
            value = re.sub(r'(\bid\s*=\s*)(["\'])(.*?)(\2)',
                           lambda m: m[1] + m[2] + convert_identifier(m[3]) + m[4], value)
        return stash(value)

    text = HTML_RE.sub(html, text)
    text = ANCHOR_RE.sub(lambda m: stash(CAPTION_RE.sub(caption, m[0])), text)

    # A Markdown destination ends at its closing parenthesis, not at the next
    # whitespace. This fixes the Avro note's previously frozen following prose.
    # Balanced parentheses are accepted inside a destination (common in URLs).
    def destination(match):
        start = match.end()
        depth = 0
        end = start
        while end < len(text):
            char = text[end]
            if char == '\\' and end + 1 < len(text):
                end += 2
                continue
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
            if char.isspace() and depth == 0:
                break
            end += 1
        return start, end

    spans = [destination(m) for m in re.finditer(r'\]\(', text)]
    for start, end in reversed(spans):
        text = text[:start] + stash(process_url_v2(text[start:end])) + text[end:]
    # Reference destinations and bare/autolink URLs also remain literal. Asian
    # prose punctuation cannot extend an ASCII URL into the following sentence.
    text = re.sub(r'(^\s*\[[^\]]+\]:\s*)(\S+)',
                  lambda m: m[1] + stash(process_url_v2(m[2])), text)
    text = re.sub(r'https?://[^\s<>\[\]{}()"\'，。；、！？（）]+',
                  lambda m: stash(m[0]), text)
    text = convert_prose(text)
    # Shortcode captions can contain inline literals stashed before the entire
    # shortcode. Restore in reverse order so those nested tokens are expanded.
    for index in reversed(range(len(literals))):
        text = text.replace(f'\ue000{index}\ue001', literals[index])
    return text


def heading_slug(line):
    """The GitHub-style IDs used by this repository's Goldmark configuration."""
    match = re.match(r'^\s{0,3}#{1,6}\s+(.+?)\s*#*$', line)
    if not match or ANCHOR_RE.search(match[1]):
        return None
    title = re.sub(r'<[^>]*>|[*_`]', '', match[1]).lower()
    return ''.join('-' if char.isspace() else char for char in title
                   if char.isspace() or char in '-_'
                   or unicodedata.category(char)[0] in 'LN')


def load_overrides(path=None):
    path = path or Path(__file__).with_name('translation-tw-overrides.json')
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('edition') != 'v2':
        raise ValueError('TW overrides must be explicitly scoped to v2')
    ids = [rule['id'] for rule in data['rules']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate TW override ID')
    return data['rules']


def indented_code_line(line):
    """Recognize this book's bare log examples without hiding CJK prose."""
    if not re.match(r'^(?: {4}|\t)', line):
        return False
    if re.match(r'^\s*(?:[-+*]|\d+[.)])\s', line) or SHORTCODE_RE.search(line):
        return False
    if not re.search(r'[\u3400-\u9fff]', line):
        return True
    # Chinese can occur in a command, assignment, call or code comment. A
    # paragraph beginning with an acronym (e.g. CAP) is still ordinary prose.
    return bool(re.match(r'^\s*(?:[$#]|//|--(?:\s|$)|[\w.$]+\s*(?:=(?!=)|\())', line))


def convert_document_v2(text, filename, converter, rules=()):
    """Convert prose with reviewed, source-anchored semantic overrides."""
    rules = [rule for rule in rules if rule['file'] == filename]
    if len({rule['id'] for rule in rules}) != len(rules):
        raise ValueError(f'{filename}: conflicting TW override IDs')
    counts = {rule['id']: 0 for rule in rules}
    replacement_counts = {rule['id']: [0] * len(rule['replacements']) for rule in rules}
    output = []
    fence = None

    def base(value, fixes=V2_FIXES):
        value = converter.convert(value)
        for before, after in fixes:
            value = value.replace(before, after)
        return value

    def old_base(value):
        return base(value, LEGACY_FIXES)

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        # Fences can be nested in a quotation or list. The repository's bare
        # indented examples are ASCII log/shell output; indented Chinese prose,
        # index bullets and source example captions still need translation.
        fence_match = re.match(r'^\s*(?:>\s*)?(`{3,}|~{3,})', line)
        if fence or fence_match:
            output.append(line)
            if fence_match:
                marker = fence_match[1]
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
            continue
        if indented_code_line(line):
            output.append(line)
            continue
        active = [rule for rule in rules if rule['match'] in line
                  and (rule.get('position') != 'line_start' or line.startswith(rule['match']))
                  and (rule.get('position') != 'whole_line' or line == rule['match'])]
        claimed = {}
        for rule in active:
            for change in rule['replacements']:
                key = (rule.get('scope', 'line'), rule['match'], change['before'])
                if key in claimed:
                    raise ValueError(f'{filename}: conflicting TW overrides {claimed[key]} and {rule["id"]}')
                claimed[key] = rule['id']
        line_rules = [rule for rule in active if rule.get('scope') != 'fragment']

        def apply(value, selected):
            value = base(value)
            for rule in selected:
                for index, change in enumerate(rule['replacements']):
                    found = value.count(change['before'])
                    if found:
                        counts[rule['id']] += found
                        replacement_counts[rule['id']][index] += found
                        value = value.replace(change['before'], change['after'])
            return value

        def prose(value):
            return apply(value, line_rules)

        fragments = []
        for rule in active:
            if rule.get('scope') == 'fragment':
                occurrences = line.count(rule['match'])
                before_count = counts[rule['id']]
                before_components = replacement_counts[rule['id']][:]
                result = protected_line(rule['match'], lambda value: apply(value, [rule]),
                                        convert_identifier=old_base)
                counts[rule['id']] = before_count + (counts[rule['id']] - before_count) * occurrences
                replacement_counts[rule['id']] = [
                    previous + (current - previous) * occurrences
                    for previous, current in zip(before_components, replacement_counts[rule['id']])]
                fragments.append((rule['match'], result))

        historical = filename == 'contrib.md' and bool(re.match(r'^\| \[(?:PR|Issue) #\d+\]', line))
        converted = protected_line(line, prose, historical_title=historical,
                                   convert_identifier=old_base, reviewed_fragments=fragments)
        old_slug = heading_slug(protected_line(line, old_base, historical_title=historical, convert_identifier=old_base))
        new_slug = heading_slug(converted)
        if old_slug and new_slug and old_slug != new_slug:
            # OINK's print view namespaces heading IDs, but not bare aliases.
            # Keep the established ID on the heading so both page and print
            # links survive; expose the new spelling as the page alias.
            output.append(f'<a id="{new_slug}"></a>')
            output.append('')
            converted += f' {{#{old_slug}}}'
        output.append(converted)
    missing = [rule['id'] for rule in rules
               if counts[rule['id']] != rule['expected_replacements']
               or any(actual != change.get('expected_count', rule['expected_replacements'])
                      for actual, change in zip(replacement_counts[rule['id']], rule['replacements']))]
    if missing:
        raise ValueError(f'{filename}: missing or changed TW override matches: {missing}')
    return '\n'.join(output), counts


def convert_v2(repo_root=None, *, check=False, cfg='s2twp.json', verify_current=True):
    root = Path(repo_root or Path(__file__).resolve().parent.parent)
    converter = make_converter(cfg)
    rules = load_overrides()
    sources = sorted((root / 'content/zh').glob('*.md'))
    unknown = {rule['file'] for rule in rules} - {path.name for path in sources}
    if unknown:
        raise ValueError(f'TW overrides refer to missing files: {sorted(unknown)}')
    converted = []
    counts = {}
    # Validate the entire edition before any write, so a stale override cannot
    # leave partially regenerated content behind.
    for source in sources:
        result, hits = convert_document_v2(source.read_text(encoding='utf-8'), source.name, converter, rules)
        converted.append((root / 'content/tw' / source.name, result))
        counts.update(hits)
    if check and verify_current:
        stale = [str(target.relative_to(root)) for target, result in converted
                 if not target.is_file() or target.read_text(encoding='utf-8') != result]
        stale.extend(str(path.relative_to(root)) for path in sorted((root / 'content/tw').glob('*.md'))
                     if path.name not in {source.name for source in sources})
        if stale:
            raise ValueError(f'TW v2 differs from its reviewed generator output: {stale}')
    if not check:
        for target, result in converted:
            target.write_text(result, encoding='utf-8')
            print(f'convert content/zh/{target.name} to content/tw/{target.name}')
    return {'edition': 'v2', 'files': len(converted), 'override_rules': len(counts),
            'override_replacements': sum(counts.values()), 'hits': counts,
            'check_only': check}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Generate TW; second edition by default, archived v1 explicitly.')
    parser.add_argument('--edition', choices=('v2', 'v1'), default='v2')
    parser.add_argument('--check', action='store_true', help='Validate v2 conversion without writing content')
    args = parser.parse_args(argv)
    if args.edition == 'v1':
        if args.check:
            parser.error('--check is available for v2 only')
        convert_legacy('v1', 'v1_tw')
    else:
        report = convert_v2(check=args.check)
        print(f"TW v2: {report['files']} pages, {report['override_rules']} reviewed overrides, "
              f"{report['override_replacements']} replacements; all expected matches found")


if __name__ == '__main__':
    main()
