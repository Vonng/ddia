"""Tests for bin/check-vi.py: every issue kind is detected, a matching tree passes."""

import importlib.util
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('check_vi', Path(__file__).resolve().parents[1] / 'check-vi.py')
check_vi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_vi)

ZH = '''---
translationKey: ddia-v2-ch1
title: 数据系统
book_kind: chapter
book_number: "1"
weight: 101
---

<a id="ch_x"></a>

## 第一节 {#sec_a}

见{{< xref fig="1-1" page="/ch1" anchor="fig_a" >}}图 1-1{{< /xref >}}与参考 [^1]。

{{< fig num="1-1" id="fig_a" src="/fig/a.png" caption="中文" />}}

![地图](/map/m.png)

```
## not a heading {#not_an_id}
```

### 参考文献

[^1]: Someone. [Paper](https://example.com/p).
'''

VI = (ZH.replace('title: 数据系统', 'title: Hệ thống dữ liệu\ndraft: true')
        .replace('第一节', 'Mục một').replace('图 1-1', 'Hình 1-1')
        .replace('caption="中文"', 'caption="Tiếng Việt"').replace('参考文献', 'Tài liệu tham khảo'))


class CheckVi(unittest.TestCase):
    def run_check(self, vi=VI, *, extra_vi=None, zh_pages=None, images=('fig/a.png', 'map/m.png'), args=()):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in images:
                (root / 'static' / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / 'static' / rel).write_bytes(b'')
            for lang, pages in (('zh', zh_pages or {'ch1.md': ZH}), ('vi', {'ch1.md': vi, **(extra_vi or {})})):
                (root / 'content' / lang).mkdir(parents=True)
                for name, text in pages.items():
                    if text is not None:
                        (root / 'content' / lang / name).write_text(text, encoding='utf-8')
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = check_vi.main(['--root', str(root), *args])
            return code, out.getvalue() + err.getvalue()

    def assert_issue(self, kind, **kwargs):
        code, out = self.run_check(**kwargs)
        self.assertEqual(code, 1, out)
        self.assertIn(f': {kind}:', out)

    def test_matching_tree_passes(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn('checked 1 pages: OK (1 drafts, 0 done)', out)

    def test_missing_page(self):
        self.assert_issue('missing-page', zh_pages={'ch1.md': ZH, 'ch2.md': ZH})

    def test_extra_page(self):
        self.assert_issue('extra-page', extra_vi={'ch9.md': VI})

    def test_front_matter_invariant(self):
        self.assert_issue('front-matter', vi=VI.replace('weight: 101', 'weight: 102'))

    def test_front_matter_missing_key(self):
        self.assert_issue('front-matter', vi=VI.replace('book_kind: chapter\n', ''))

    def test_anchor(self):
        self.assert_issue('anchor', vi=VI.replace('{#sec_a}', '{#sec_b}'))

    def test_heading(self):
        self.assert_issue('heading', vi=VI.replace('### Tài liệu', '#### Tài liệu'))

    def test_shortcode(self):
        self.assert_issue('shortcode', vi=VI.replace('src="/fig/a.png"', 'src="/fig/b.png"'), images=('fig/a.png', 'fig/b.png', 'map/m.png'))

    def test_xref_target(self):
        self.assert_issue('xref-target', vi=VI.replace('id="fig_a"', 'id="fig_z"'))

    def test_footnote(self):
        self.assert_issue('footnote', vi=VI.replace('[^1]: ', '[^2]: '))

    def test_url(self):
        self.assert_issue('url', vi=VI.replace('https://example.com/p', 'https://example.com/q'))

    def test_image(self):
        self.assert_issue('image', images=('fig/a.png',))

    def test_duplicate_id(self):
        self.assert_issue('duplicate-id', vi=VI.replace('<a id="ch_x"></a>', '<a id="ch_x"></a>\n<a id="ch_x"></a>'))

    def test_code_fence_ignored(self):
        code, out = self.run_check(vi=VI.replace('{#not_an_id}', '{#changed}'))
        self.assertEqual(code, 0, out)

    def test_missing_reference_dir(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(io.StringIO()):
            self.assertEqual(check_vi.main(['--root', tmp]), 2)


if __name__ == '__main__':
    unittest.main()
