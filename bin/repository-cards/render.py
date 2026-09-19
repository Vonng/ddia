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

"""Pure, self-contained SVG rendering for DDIA's README cards."""
from datetime import date, timedelta
import base64
from html import escape
import math

themes = {
    'light': dict(bg='#ffffff', wash='#f2f7fc', edge='#d9e3ee', ink='#16222e',
                  muted='#62758a', blue='#1d588c', copper='#b4762e', grid='#e5edf5',
                  line='#2b6ca3', ring='#dce5ef', field='#f7f9fc', label='#3d4e61'),
    'dark': dict(bg='#101923', wash='#152738', edge='#2b3c50', ink='#e8eef6',
                 muted='#93a3b8', blue='#7fb8e8', copper='#e0a35c', grid='#263749',
                 line='#5da2dd', ring='#3a4e63', field='#0b1119', label='#b6c2d2'),
}

def read_emblem(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def txt(x, y, value, size=14, color=None, weight=400, anchor='start', mono=False, spacing=None):
    family = 'Menlo,Consolas,monospace' if mono else 'Arial,Helvetica,sans-serif'
    extra = f' letter-spacing="{spacing}"' if spacing is not None else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{extra}>'
            f'{escape(str(value))}</text>')


def start(height, theme, title, description, emblem_body):
    t = themes[theme]
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" '
            f'viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<defs><linearGradient id="surface" x1="0" y1="1" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["bg"]}"/>'
            f'<stop offset="1" stop-color="{t["wash"]}"/></linearGradient>'
            '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["blue"]}"/>'
            f'<stop offset="1" stop-color="{t["copper"]}"/></linearGradient>'
            '<linearGradient id="area" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{t["line"]}" stop-opacity=".22"/>'
            f'<stop offset="1" stop-color="{t["line"]}" stop-opacity=".015"/>'
            '</linearGradient></defs>',
            f'<rect x=".75" y=".75" width="998.5" height="{height-1.5}" rx="22" '
            f'fill="url(#surface)" stroke="{t["edge"]}" stroke-width="1.5"/>',
            f'<image x="39" y="20" width="32" height="32" href="{escape(emblem_body)}"/>']


def heading(parts, t, eyebrow, title, subtitle, value, value_label):
    parts.extend([
        txt(76, 43, eyebrow, 11, t['muted'], 600, mono=True, spacing=1.7),
        txt(40, 94, title, 32, t['ink'], 700),
        txt(41, 123, subtitle, 14, t['muted']),
        txt(958, 89, f'{value:,}', 45, t['ink'], 700, anchor='end'),
        txt(957, 114, value_label, 10, t['muted'], 600, anchor='end', mono=True, spacing=1.5),
        f'<path d="M40 146 H960" stroke="{t["edge"]}"/>',
    ])


def contributors(theme, people, snapshot, emblem_body):
    columns = 14
    height = 206 + 66 * math.ceil(len(people) / columns)
    t = themes[theme]
    parts = start(height, theme, f'DDIA community — {len(people)} contributors',
                  f'DDIA translators, reviewers, and human issue and pull-request authors across both editions. '
                  f'Gold rings retain the existing significant-contribution designation. Snapshot {snapshot}.', emblem_body)
    heading(parts, t, 'DDIA / COMMUNITY', 'Contributors',
            'Translation, corrections, proposals & reports across both editions', len(people), 'COMMUNITY CONTRIBUTORS')
    for row in range(math.ceil(len(people) / columns)):
        group = people[row * columns:(row + 1) * columns]
        row_width = len(group) * 65
        for col, person in enumerate(group):
            x = (1000 - row_width) / 2 + col * 65 + 32.5
            y = 194 + row * 66
            identifier = f'avatar-{row}-{col}'
            featured = bool(person.get('featured'))
            parts.append(f'<g><title>@{escape(person["handle"])} — {escape(person["what"])}</title>')
            parts.append(f'<defs><clipPath id="{identifier}"><circle cx="{x}" cy="{y}" r="24"/></clipPath></defs>')
            if featured:
                parts.append(f'<circle cx="{x}" cy="{y}" r="29" fill="{t["copper"]}" opacity=".09"/>')
            if person.get('avatarDataUrl'):
                parts.append(f'<image x="{x-24}" y="{y-24}" width="48" height="48" '
                             f'clip-path="url(#{identifier})" href="{escape(person["avatarDataUrl"])}"/>')
            else:
                parts.append(f'<circle cx="{x}" cy="{y}" r="24" fill="{t["ring"]}"/>')
                parts.append(txt(x, y + 9, person['handle'][0].upper(), 26, t['ink'], 700, 'middle'))
            parts.append(f'<circle cx="{x}" cy="{y}" r="25.5" fill="none" '
                         f'stroke="{t["copper"] if featured else t["ring"]}" stroke-width="{2 if featured else 1.25}"/></g>')
    parts.extend([
        f'<path d="M40 {height-42} H960" stroke="{t["edge"]}"/>',
        f'<circle cx="47" cy="{height-21}" r="4" fill="none" stroke="{t["copper"]}" stroke-width="1.5"/>',
        txt(61, height-17, 'Gold rings mark significant contributions', 12, t['muted']),
        txt(959, height-17, f'AS OF {snapshot}', 10, t['muted'], 500, 'end', mono=True, spacing=.6),
        '</svg>',
    ])
    return ''.join(parts)


def stars(theme, history, snapshot, emblem_body):
    points = history['points']
    star_count = points[-1]['stars']
    t = themes[theme]
    provenance = ('Initial history reconstructed · Daily totals since ' + history['bootstrap']['through'] + ' · UTC'
                  if history['bootstrap']['reconstructed'] else 'Observed daily star totals · UTC')
    parts = start(558, theme, f'DDIA star history — {star_count:,} stars',
                  f'GitHub repository Vonng/ddia. {star_count:,} stars as of {snapshot}. ' +
                  provenance, emblem_body)
    heading(parts, t, 'DDIA / GITHUB', 'Star History', 'Vonng/ddia', star_count, 'GITHUB STARS')
    left, right, top, bottom = 76, 958, 177, 440
    begin = date.fromisoformat(points[0]['date'])
    end = date.fromisoformat(points[-1]['date'])
    days = max(1, (end - begin).days)
    maximum = max(500, math.ceil(max(p['stars'] for p in points) / 500) * 500)
    tick_step = 10 ** max(0, int(math.log10(maximum)))
    xy = lambda day, n: (left + (right-left)*(date.fromisoformat(day)-begin).days / days,
                         bottom-(bottom-top)*n/maximum)
    for value in range(0, maximum+1, tick_step):
        y = xy(points[0]['date'], value)[1]
        parts.append(f'<path d="M{left} {y:.2f} H{right}" stroke="{t["grid"]}" stroke-dasharray="4 6"/>')
        parts.append(txt(left-16, round(y+4, 2), f'{value / 1000:g}k' if value >= 1000 else str(value), 12, t['muted'], anchor='end'))
    dates = sorted({begin + timedelta(days=round((end-begin).days*i/5)) for i in range(6)})
    ticks = [(d.isoformat(), d.strftime('%b %Y') if days > 90 else d.strftime('%b %d')) for d in dates]
    for day, label in ticks:
        x = xy(day, 0)[0]
        parts.append(f'<path d="M{x:.2f} {top} V{bottom}" stroke="{t["grid"]}" stroke-opacity=".65"/>')
        anchor = 'start' if day == points[0]['date'] else 'end' if day == snapshot else 'middle'
        parts.append(txt(round(x, 2), 466, label, 12, t['muted'], anchor=anchor))
    coords = [xy(p['date'], p['stars']) for p in points]
    line = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in coords)
    area = line + f' L{coords[-1][0]:.2f} {bottom} L{left} {bottom} Z'
    parts.extend([
        f'<path d="{area}" fill="url(#area)"/>',
        f'<path d="{line}" fill="none" stroke="url(#accent)" stroke-width="3" '
        'stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path d="M{left} {bottom} H{right}" stroke="{t["edge"]}"/>',
    ])
    x, y = coords[-1]
    parts.extend([
        f'<circle cx="{x}" cy="{y}" r="10" fill="{t["copper"]}" opacity=".12"/>',
        f'<circle cx="{x}" cy="{y}" r="5" fill="{t["copper"]}" stroke="{t["bg"]}" stroke-width="2"/>',
        f'<path d="M40 491 H960" stroke="{t["edge"]}"/>',
        txt(40, 516, f'{begin:%b %Y} — {end:%b %Y}'.upper(), 10, t['muted'], 500, mono=True, spacing=.7),
        txt(959, 516, f'SNAPSHOT {snapshot}', 10, t['muted'], 500, 'end', mono=True, spacing=.6),
        txt(40, 539, provenance, 11, t['muted']),
        '</svg>',
    ])
    return ''.join(parts)
