"""Tests for bin/glossary-vi.py: table rules, chapter pair matching, --release gate."""

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('glossary_vi', Path(__file__).resolve().parents[1] / 'glossary-vi.py')
gv = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gv)

TABLE = '''[[term]]
en = "cache"
vi = "cache"
keep = true
note = "quen dùng nguyên gốc"

[[term]]
en = "replication"
vi = "sao chép"
'''
CH = '---\ntitle: C\n{draft}---\n\nTa dùng *sao chép* (*replication*) và *cache* (*cache*).\n'


def run(table, chapter=None, draft=False, release=False, book='### cache\n\n### replication\n', extra=''):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for sub in ('data/glossary', 'content/en', 'content/vi'):
            (root / sub).mkdir(parents=True)
        (root / 'data/glossary/vi.toml').write_text(table, encoding='utf-8')
        (root / 'content/en/glossary.md').write_text(book, encoding='utf-8')
        if chapter is not None:
            fm = 'draft: true\n' if draft else ''
            (root / 'content/vi/ch1.md').write_text(CH.format(draft=fm).replace('sao chép', chapter) + extra, encoding='utf-8')
        out = io.StringIO()
        with redirect_stdout(out):
            code = gv.check(root, release)
        return code, out.getvalue()


class GlossaryTest(unittest.TestCase):
    def test_valid(self):
        code, out = run(TABLE, 'sao chép')
        self.assertEqual(code, 0, out)
        self.assertIn('2 khớp / 2 cặp', out)

    def test_duplicate_without_ctx(self):
        code, out = run(TABLE + '\n[[term]]\nen = "Replication"\nvi = "nhân bản"\n')
        self.assertEqual(code, 1)
        self.assertIn('missing-ctx', out)

    def test_two_senses_with_ctx_ok(self):
        extra = '\n[[term]]\nen = "lock"\nvi = "khóa"\nctx = "a"\n\n[[term]]\nen = "lock"\nvi = "khoá"\nctx = "b"\n'
        self.assertEqual(run(TABLE + extra)[0], 0)

    def test_keep_needs_note(self):
        code, out = run('[[term]]\nen = "cache"\nvi = "cache"\nkeep = true\n')
        self.assertIn('missing-note', out)

    def test_chapter_mismatch(self):
        code, out = run(TABLE, 'nhân bản')
        self.assertEqual(code, 1)
        self.assertIn('mismatch', out)

    def test_release_todo_and_coverage(self):
        todo = TABLE + '\n[[term]]\nen = "lag"\nvi = ""\nstatus = "todo"\n'
        self.assertEqual(run(todo, 'sao chép', release=False)[0], 0)
        self.assertEqual(run(todo, release=True, book='### cache\n### replication\n### lag\n')[0], 1)
        code, out = run(TABLE, release=True, book='### cache\n### replication\n### quorum\n')
        self.assertIn('coverage', out)

    def test_release_todo_used_in_published_chapter(self):
        todo = TABLE + '\n[[term]]\nen = "lag"\nvi = ""\nstatus = "todo"\n'
        use = '\nVà *độ trễ* (*lag*).\n'
        self.assertEqual(run(todo, 'sao chép', release=True, extra=use)[0], 1)
        self.assertEqual(run(todo, 'sao chép', draft=True, release=True, extra=use)[0], 0)

    def test_todo_in_draft_chapter_not_blocked(self):
        todo = TABLE + '\n[[term]]\nen = "lag"\nvi = ""\nstatus = "todo"\n'
        self.assertEqual(run(todo, 'sao chép', draft=True, release=True)[0], 0)


if __name__ == '__main__':
    unittest.main()
