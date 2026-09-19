#!/usr/bin/env python3
# Copyright (c) 2026 Feng Ruohang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Refresh the generated-asset checkout; publishing is handled by the workflow."""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import hashlib
from html import escape
import json
from http.client import IncompleteRead
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import yaml

import render

REPOSITORY = 'Vonng/ddia'
GROUPS = ('code', 'proposed', 'reports')
HANDLE = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}\Z')


def request(url, token='', limit=8 * 1024 * 1024):
    headers = {'User-Agent': 'ddia-repository-cards', 'Accept': 'application/vnd.github+json'}
    if urlparse(url).netloc == 'api.github.com':
        headers['X-GitHub-Api-Version'] = '2026-03-10'
        if token:
            headers['Authorization'] = f'Bearer {token}'
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=25) as response:
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError('Response exceeds the size limit')
                expected = response.headers.get('Content-Length')
                if expected is not None and len(data) != int(expected):
                    raise URLError('Incomplete response body')
                return data
        except HTTPError as exc:
            if exc.code < 500 or attempt == 2:
                raise
        except (URLError, TimeoutError, IncompleteRead):
            if attempt == 2:
                raise
        time.sleep(attempt + 1)


class GitHub:
    def __init__(self, token):
        self.token = token

    def get(self, path):
        for attempt in range(3):
            try:
                return json.loads(request('https://api.github.com/' + path, self.token))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                if attempt == 2:
                    raise ValueError(f'Incomplete or invalid GitHub JSON: {path}') from exc
                time.sleep(attempt + 1)

    def issues(self, repository):
        page = 1
        while True:
            batch = self.get(f'repos/{repository}/issues?state=all&per_page=100&page={page}&sort=created&direction=asc')
            if not isinstance(batch, list):
                raise ValueError(f'Invalid issues response for {repository}')
            yield from batch
            if len(batch) < 100:
                return
            page += 1


def curated_snapshot(data, revision):
    people = []
    for entry in data['items']:
        if not HANDLE.fullmatch(entry['github']):
            raise ValueError('Invalid GitHub contributor handle')
        people.append({
            'handle': entry['github'],
            'group': 'code' if entry.get('featured') else 'reports',
            'featured': bool(entry.get('featured')),
            'what': entry.get('role', 'Translation, corrections, proposals or reports'),
            'firstContribution': '9999-12-31',
        })
    if not people or len({p['handle'].lower() for p in people}) != len(people):
        raise ValueError('Empty or duplicate contributor roster')
    return {'revision': revision, 'repositories': [REPOSITORY],
            'excludedIssues': data.get('excluded_issues', []),
            'bots': ['Copilot', 'dependabot[bot]'], 'people': people}


def collect_people(api, curated, records=None):
    bots = {name.lower() for name in curated['bots']}
    people = {p['handle'].lower(): dict(p) for p in curated['people']
              if p['handle'].lower() not in bots | {'ghost'} and not p['handle'].lower().endswith('[bot]')}
    order = {p['handle'].lower(): index for index, p in enumerate(curated['people'])}
    for repository in curated['repositories']:
        print(f'Reading issue and PR authors: {repository}', flush=True)
        for issue in records if records is not None else api.issues(repository):
            if issue.get('number') in curated.get('excludedIssues', []):
                continue
            user = issue.get('user') or {}
            handle = user.get('login', '')
            key = handle.lower()
            if user.get('type') != 'User' or key in bots | {'ghost'} or key.endswith('[bot]'):
                continue
            if not HANDLE.fullmatch(handle):
                raise ValueError('Invalid issue author')
            pr = issue.get('pull_request')
            group = 'code' if pr and pr.get('merged_at') else 'proposed' if pr else 'reports'
            first = issue['created_at'][:10]
            date.fromisoformat(first)
            person = people.setdefault(key, {
                'handle': handle, 'group': group, 'featured': False,
                'what': 'Contributed an issue or pull request to the DDIA translation',
                'firstContribution': first,
            })
            person['avatarUrl'] = user.get('avatar_url', '')
            person['firstContribution'] = min(person['firstContribution'], first)
            if GROUPS.index(group) < GROUPS.index(person['group']):
                person['group'] = group
    if not people:
        raise ValueError('No human contributors were collected')
    return sorted(people.values(), key=lambda p: (
        GROUPS.index(p['group']), not p['featured'],
        order.get(p['handle'].lower(), len(order)), p['firstContribution'], p['handle'].lower()))


def raster_data_url(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = 'image/png'
    elif data.startswith(b'\xff\xd8\xff'):
        mime = 'image/jpeg'
    elif data.startswith((b'GIF87a', b'GIF89a')):
        mime = 'image/gif'
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        mime = 'image/webp'
    else:
        raise ValueError('Avatar is not a raster image')
    return f'data:{mime};base64,' + base64.b64encode(data).decode('ascii')


def cached_avatar(person):
    value = person.get('avatarDataUrl', '')
    if not value:
        return ''
    prefix, encoded = value.split(',', 1)
    if prefix not in ('data:image/png;base64', 'data:image/jpeg;base64', 'data:image/gif;base64', 'data:image/webp;base64'):
        raise ValueError('Invalid cached avatar format')
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > 512 * 1024 or raster_data_url(raw) != value:
        raise ValueError('Invalid cached avatar')
    return value


def add_avatars(api, people, previous):
    cached = {p['handle'].lower(): cached_avatar(p) for p in previous}

    def update(person):
        person = dict(person)
        try:
            url = person.pop('avatarUrl', '') or api.get('users/' + person['handle'])['avatar_url']
            parsed = urlparse(url)
            if parsed.scheme != 'https' or parsed.netloc != 'avatars.githubusercontent.com':
                raise ValueError('Unexpected avatar host')
            data = request(url + ('&' if '?' in url else '?') + 's=96', limit=512 * 1024)
            person['avatarDataUrl'] = raster_data_url(data)
        except (HTTPError, URLError, TimeoutError, IncompleteRead, ValueError, KeyError) as exc:
            person.pop('avatarUrl', None)
            person['avatarDataUrl'] = cached.get(person['handle'].lower(), '')
            print(f'Avatar fallback for @{person["handle"]}: {type(exc).__name__}', file=sys.stderr)
        return person

    with ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(update, people))


def update_history(history, day, stars):
    date.fromisoformat(day)
    if type(stars) is not int or stars < 0:
        raise ValueError('Invalid repository star count')
    if history is None:
        history = {'repository': REPOSITORY, 'bootstrap': {'through': day, 'reconstructed': False}, 'points': []}
    if history['repository'] != REPOSITORY:
        raise ValueError('Star history belongs to a different repository')
    date.fromisoformat(history['bootstrap']['through'])
    dates = []
    for point in history['points']:
        date.fromisoformat(point['date'])
        if type(point['stars']) is not int or point['stars'] < 0:
            raise ValueError('Invalid historical star count')
        dates.append(point['date'])
    if dates != sorted(set(dates)) or any(d > day for d in dates):
        raise ValueError('History contains duplicate, unordered, or future dates')
    # Replace today's observation, preserve previous days, and allow unstars.
    points = [dict(p) for p in history['points'] if p['date'] != day]
    points.append({'date': day, 'stars': stars})
    return {**history, 'points': points}


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def bootstrap_history(api, metadata, day):
    """Reconstruct the initial curve from GitHub's aggregated weekly star data."""
    weeks = []
    for page in range(1, 101):
        batch = api.get(f'repos/{REPOSITORY}/stargazers/history?per_page=30&page={page}')
        if not isinstance(batch, list):
            raise ValueError('Invalid star-history response')
        weeks.extend(batch)
        if len(batch) < 30:
            break
    else:
        raise ValueError('Star-history pagination did not reach the end')
    totals = {}
    for week in weeks:
        timestamp, total = week['week'], week['total']
        if type(timestamp) is not int or type(total) is not int or total < 0 or timestamp in totals:
            raise ValueError('Invalid or duplicate star-history week')
        totals[timestamp] = total
    if metadata['stargazers_count'] and not totals:
        raise ValueError('GitHub returned no star history for a starred repository')
    created = metadata['created_at'][:10]
    points = {created: 0}
    running = 0
    for timestamp, total in sorted(totals.items()):
        start = datetime.fromtimestamp(timestamp, timezone.utc).date()
        running += total
        endpoint = min(day, (start + timedelta(days=6)).isoformat())
        if endpoint >= created:
            points[endpoint] = running
    result = {
        'repository': REPOSITORY,
        'bootstrap': {'through': day, 'reconstructed': True,
                      'source': 'GitHub stargazers/history weekly aggregates'},
        'points': [{'date': d, 'stars': n} for d, n in sorted(points.items())],
    }
    print(f'Bootstrapped {len(totals)} weeks of GitHub star history', flush=True)
    return result


def sync_roster(source_root, people, records, day):
    """Update the shared roster, README names, and both source contribution tables."""
    path = source_root / 'data/contributors.yaml'
    data = yaml.safe_load(path.read_text())
    entries = {item['github'].lower(): item for item in data['items']}
    for person in people:
        entries.setdefault(person['handle'].lower(), {'github': person['handle']})
    priority = {'vonng': 0, 'yingang': 1, 'afuntw': 2}
    items = sorted(entries.values(), key=lambda item: (priority.get(item['github'].lower(), 3), item['github'].lower()))
    # Keep the existing readable layout, including quoted numeric GitHub names.
    metadata = {key: value for key, value in data.items() if key != 'items'}
    lines = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).splitlines() if metadata else []
    lines.append('items:')
    for item in items:
        lines.append('  - github: ' + json.dumps(item['github']))
        metadata = {key: value for key, value in item.items() if key != 'github'}
        if metadata:
            lines.extend('    ' + line for line in yaml.safe_dump(
                metadata, allow_unicode=True, sort_keys=False).splitlines())
    path.write_text('\n'.join(lines) + '\n')

    names = [f'[@{item["github"]}](https://github.com/{item["github"]})' for item in items]
    rows = [' · '.join(names[i:i + 6]) for i in range(0, len(names), 6)]
    details = f'<details>\n<summary>{len(items)} 位贡献者</summary>\n\n' + '\n'.join(rows) + '\n\n</details>'
    readme = source_root / 'README.md'
    text, replacements = re.subn(r'<details>\n<summary>\d+ 位贡献者</summary>.*?</details>',
                                 lambda _: details, readme.read_text(), flags=re.S)
    if replacements != 1:
        raise ValueError('Expected one README contributor list')
    readme.write_text(text)

    table = ['<!-- CONTRIBUTIONS:START -->',
             f'截至 {day}（UTC），共收录 {len(items)} 位贡献者。以下记录保留实际状态，未合并的提议同样计入贡献。', '',
             '| Issue / PR | 贡献者 | 标题 | 状态 |', '|---|---|---|---|']
    for record in sorted(records, key=lambda record: record['number'], reverse=True):
        if record['number'] in data.get('excluded_issues', []):
            continue
        user = record.get('user') or {}
        handle = user.get('login', '')
        if user.get('type') != 'User' or (handle.lower() not in entries and handle.lower() != 'ghost'):
            continue
        # GitHub titles are plain text, not executable Hugo shortcodes or math.
        title = escape(' '.join(record['title'].split())).translate(
            str.maketrans({char: f'&#{ord(char)};' for char in '\\[]|*_`{}$~'}))
        pr = record.get('pull_request')
        status = ('已合并' if pr.get('merged_at') else '待处理' if record['state'] == 'open' else '未合并') if pr else ('待处理' if record['state'] == 'open' else '已关闭')
        kind = 'PR' if pr else 'Issue'
        author = '已删除账户' if handle.lower() == 'ghost' else f'[@{handle}](https://github.com/{handle})'
        table.append(f'| [{kind} #{record["number"]}]({record["html_url"]}) | {author} | {title} | {status} |')
    table.append('<!-- CONTRIBUTIONS:END -->')
    block = '\n'.join(table)
    pages = [readme, *(source_root / 'content' / language / 'contrib.md' for language in ('zh', 'v1'))]
    for path in pages:
        text = path.read_text()
        pattern = r'<!-- CONTRIBUTIONS:START -->.*?<!-- CONTRIBUTIONS:END -->' if '<!-- CONTRIBUTIONS:START -->' in text else r'^\| ISSUE & Pull Requests[^\n]*(?:\n\|[^\n]*)+'
        text, replacements = re.subn(pattern, lambda _: block, text, flags=re.S if '<!-- CONTRIBUTIONS:START -->' in text else re.M)
        if replacements != 1:
            raise ValueError(f'Expected one contribution table in {path}')
        path.write_text(text)
    print(f'Synchronized {len(items)} contributors; run make translate to refresh Traditional Chinese.', flush=True)


def refresh(output, api, source_root, sync=False):
    day = datetime.now(timezone.utc).date().isoformat()
    metadata = api.get('repos/' + REPOSITORY)
    if metadata['full_name'].lower() != REPOSITORY.lower():
        raise ValueError('Unexpected repository metadata')
    source = (source_root / 'data/contributors.yaml').read_bytes()
    curated = curated_snapshot(yaml.safe_load(source), hashlib.sha256(source).hexdigest())
    records = list(api.issues(REPOSITORY))
    people = collect_people(api, curated, records)
    if sync:
        sync_roster(source_root, people, records, day)
        source = (source_root / 'data/contributors.yaml').read_bytes()
        curated = curated_snapshot(yaml.safe_load(source), hashlib.sha256(source).hexdigest())
        people = collect_people(api, curated, records)
    history = read_json(output / 'history.json')
    if history is None:
        history = bootstrap_history(api, metadata, day)
    history = update_history(history, day, metadata['stargazers_count'])
    previous = read_json(output / 'contributors.json', {}).get('people', [])
    people = add_avatars(api, people, previous)
    emblem = render.read_emblem(source_root / 'static/logo.png')
    payloads = {}
    for theme in ('light', 'dark'):
        payloads[f'contributors-{theme}.svg'] = render.contributors(theme, people, day, emblem) + '\n'
        payloads[f'star-history-{theme}.svg'] = render.stars(theme, history, day, emblem) + '\n'
    for svg in payloads.values():
        ET.fromstring(svg)
    for name, data in {
        'history.json': history,
        'curated.json': curated,
        'contributors.json': {'repository': REPOSITORY, 'updated': day, 'people': people},
    }.items():
        payloads[name] = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    payloads['README.md'] = f'''# DDIA repository cards

Generated by [Repository Cards](https://github.com/Vonng/ddia/actions/workflows/repository-cards.yml)
at 00:00 UTC daily (08:00 Asia/Shanghai). GitHub may queue scheduled runs.

Snapshot: {day}. {metadata['stargazers_count']:,} stars; {len(people)} community contributors.

- `contributors-light.svg` / `contributors-dark.svg`: translators, reviewers, and human issue/PR authors for both DDIA editions. Open and unmerged work counts. Bots are excluded; gold rings follow the reviewed roster.
- `star-history-light.svg` / `star-history-dark.svg`: the initial curve is reconstructed from GitHub's weekly star aggregates, not a log of observed past totals. Later points are daily observed totals, including decreases. Missing daily observations are not fabricated.
- `curated.json`: reviewed contributor credit from `data/contributors.yaml` on the source branch. Newly discovered human authors are included automatically.
- `contributors.json`: generated contributor data and embedded raster avatars. Failed avatar refreshes use the previous image, or an initial when no image is available.
- `history.json`: persistent daily totals. Keep this file when regenerating images.

The SVGs are self-contained. Source and instructions live on the default branch;
this branch contains generated assets only. Do not merge it into `main`.
'''
    # Collect and validate everything before touching the publication checkout.
    output.mkdir(parents=True, exist_ok=True)
    for filename, text in payloads.items():
        (output / filename).write_text(text)
    print(f'{day}: {len(people)} contributors; {metadata["stargazers_count"]:,} stars; {len(history["points"])} history points')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sync-roster', action='store_true', help='also refresh the shared roster, README names, and contribution tables')
    args = parser.parse_args()
    configured = os.environ.get('GITHUB_REPOSITORY', REPOSITORY)
    if configured.lower() != REPOSITORY.lower():
        raise SystemExit('This workflow is scoped to Vonng/ddia')
    refresh(args.output, GitHub(os.environ.get('GH_TOKEN', '')), Path(__file__).resolve().parents[2], args.sync_roster)


if __name__ == '__main__':
    main()
