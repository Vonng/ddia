#!/usr/bin/env python3
"""校验 cards/src/ 下所有卡片的完整性与链接有效性。

用法：python3 check.py
退出码 0 = 全部通过；非 0 = 存在问题（逐条打印）。

校验项：
1. frontmatter 必备字段（id/type/chapter/title）齐全
2. 卡片 ID 全局唯一
3. 各类型卡片的段落完整性
4. 每张卡至少 2 道自测题；判断题答案 ∈ {对,错}；单选题恰有一个 *
5. mermaid 代码块成对出现
6. 原文关联中的 /chN/#anchor 在 content/zh/chN.md 中真实存在
7. 文件内 id 与文件名前缀一致
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD_DIR = HERE / "src"
CONTENT_DIR = HERE.parent / "content" / "zh"

REQUIRED_META = ["id", "type", "chapter", "title"]
# 每类卡片必须出现的段落（按前缀匹配，容许标题带补充说明，如「推演序列（每步先预测…）」）
SECTIONS = {
    "dilemma": ["场景", "揭示", "图", "自测", "原文关联"],
    "simulation": ["推演序列", "揭示", "自测", "原文关联"],
    "incident": ["事故经过", "自测", "原文关联"],
}

problems = []


def note(msg):
    problems.append(msg)


def parse(text):
    meta, body_start = {}, 0
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(\w+):\s*(.+)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
        elif line.strip():
            body_start = i
            break
    body = "\n".join(lines[body_start:])
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    sections = {}
    for i in range(1, len(parts), 2):
        sections[parts[i].strip()] = parts[i + 1]
    return meta, sections, body


_ch_cache = {}


def chapter_text(n):
    if n not in _ch_cache:
        f = CONTENT_DIR / f"ch{n}.md"
        _ch_cache[n] = f.read_text(encoding="utf-8") if f.exists() else ""
    return _ch_cache[n]


def main():
    files = sorted(f for f in CARD_DIR.glob("*.md") if f.name != "README.md")
    if not files:
        note("cards/src/ 下没有卡片文件")
    seen_ids = {}

    for f in files:
        text = f.read_text(encoding="utf-8")
        meta, sections, body = parse(text)
        cid = meta.get("id", "")

        for k in REQUIRED_META:
            if not meta.get(k):
                note(f"{f.name}: 缺少 frontmatter 字段 {k}")

        if cid:
            if cid in seen_ids:
                note(f"{f.name}: 卡片 ID 与 {seen_ids[cid]} 重复（会导致状态串卡）")
            seen_ids[cid] = f.name
            if not f.name.startswith(cid):
                note(f"{f.name}: 文件名前缀与 id（{cid}）不一致")

        ctype = meta.get("type", "")
        if ctype and ctype not in SECTIONS:
            note(f"{f.name}: 未知 type '{ctype}'")
        for sec in SECTIONS.get(ctype, []):
            if not any(k.startswith(sec) for k in sections):
                note(f"{f.name}: 缺少段落 ## {sec}")

        # 自测题
        quiz_block = sections.get("自测", "")
        judges = re.findall(r"^- 判断:\s*(.+?)\s*\[([^\]]*)\]\s*$", quiz_block, flags=re.M)
        choices = re.findall(r"^- 单选:\s*(.+)$", quiz_block, flags=re.M)
        if len(judges) + len(choices) < 2:
            note(f"{f.name}: 自测题少于 2 道")
        for stem, ans in judges:
            if ans not in ("对", "错"):
                note(f"{f.name}: 判断题答案必须是 [对] 或 [错]，实为 [{ans}]")
        for line in choices:
            opts = [o for o in line.split("|") if o.strip()]
            if len(opts) < 2:
                note(f"{f.name}: 单选题选项少于 2 个：{line[:30]}")
            stars = [o for o in opts if o.strip().endswith("*")]
            if len(stars) != 1:
                note(f"{f.name}: 单选题必须恰有一个 * 标记，实为 {len(stars)} 个：{line[:30]}")

        # mermaid 代码块配对
        fences = re.findall(r"^```", body, flags=re.M)
        if len(fences) % 2:
            note(f"{f.name}: 代码块 ``` 数量为奇数，可能有未闭合块")

        # 原文关联锚点
        for ch, anchor in re.findall(r"\(/ch(\d+)/#([A-Za-z0-9_-]+)\)", sections.get("原文关联", "")):
            if f"{{#{anchor}}}" not in chapter_text(ch):
                note(f"{f.name}: 锚点不存在 content/zh/ch{ch}.md {{#{anchor}}}")
        for link in re.findall(r"\(/ch\d+/#\)", sections.get("原文关联", "")):
            note(f"{f.name}: 原文关联存在空锚点链接 {link}")

    total = len(files)
    if problems:
        print(f"✗ {total} 张卡，发现 {len(problems)} 个问题：")
        for p in problems:
            print("  -", p)
        return 1

    chapters = sorted({int(re.match(r"§(\d+)", parse(f.read_text(encoding='utf-8'))[0].get('chapter', '')).group(1))
                       for f in files
                       if re.match(r"§(\d+)", parse(f.read_text(encoding='utf-8'))[0].get('chapter', ''))})
    print(f"✓ 全部通过：{total} 张卡，覆盖第 {chapters[0]}–{chapters[-1]} 章"
          f"（共 {len(chapters)} 章）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
