"""Reject damaged current Book structures without freezing historical counts."""

from pathlib import Path
import importlib.util
import json
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'translation_checks', Path(__file__).resolve().parents[1]/'check-translation.py'
)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class TranslationChecksTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for lang in ('en', 'zh'):
            (self.root/f'content/{lang}').mkdir(parents=True)
        for n in range(1, 15):
            part = 1 if n <= 5 else 2 if n <= 10 else 3
            en = f'---\ntitle: Chapter {n}\n---\n\n<a id="ch_{n}"></a>\n\n## Overview {{#section_{n}}}\n\nContent [^1].\n\n### References {{#references}}\n\n[^1]: Author. Reference.\n'
            zh = f'---\ntitle: 第{n}章\nbook_kind: chapter\nbook_number: "{n}"\nbook_part: {"I"*part}\nweight: {100*part+n}\n---\n\n<a id="ch_{n}"></a>\n\n## 概述 {{#section_{n}}}\n\n内容 [^1].\n\n### 参考文献 {{#references}}\n\n[^1]: Author. Reference.\n'
            (self.root/f'content/en/ch{n}.md').write_text(en)
            (self.root/f'content/zh/ch{n}.md').write_text(zh)

    def insert(self, lang, n, body):
        path = self.root/f'content/{lang}/ch{n}.md'
        title = '### References' if lang == 'en' else '### 参考文献'
        path.write_text(path.read_text().replace(title, body+'\n\n'+title))

    def errors(self):
        return qa.run_checks(self.root)['errors']

    def test_complete_current_metadata_passes_all_fourteen_chapters(self):
        report = qa.run_checks(self.root)
        self.assertEqual(report['errors'], [])
        self.assertEqual(len(report['chapters']), 14)
        self.assertEqual(report['totals']['source_pages'], 14)

    def test_missing_xref_target_and_wrong_type_or_number_fail(self):
        source = '{{< fig id="diagram" num="1-1" src="/diagram.png" />}}'
        (self.root/'static').mkdir(); (self.root/'static/diagram.png').write_bytes(b'image fixture')
        self.insert('en', 1, source); self.insert('zh', 1, source)
        for attrs in ('fig="1-1" anchor="missing"', 'eg="1-1" anchor="diagram"', 'fig="1-2" anchor="diagram"'):
            with self.subTest(attrs=attrs):
                path = self.root/'content/zh/ch2.md'; original = path.read_text()
                self.insert('zh', 2, '{{< xref page="/ch1" '+attrs+' >}}图{{< /xref >}}')
                self.assertTrue(any(e['check'] == 'xref target type and number' for e in self.errors()))
                path.write_text(original)

    def test_generic_xref_resolves_without_a_fixed_count(self):
        self.insert('zh', 1, '{{< xref page="/ch2" anchor="section_2" >}}见第二章{{< /xref >}}')
        self.assertEqual(self.errors(), [])
        self.assertEqual(qa.run_checks(self.root)['totals']['xrefs'], 1)

    def test_corrupt_example_number_is_rejected(self):
        self.insert('en', 1, '#### Example 1-1. Code {#sample}\n\n```sql\nSELECT 1;\n```')
        self.insert('zh', 1, '{{< eg id="sample" num="1-2" caption="代码" >}}\n\n```sql\nSELECT 1;\n```\n\n{{< /eg >}}')
        self.assertTrue(any(e['check'] == 'example identifiers and numbers' for e in self.errors()))

    def test_nested_example_heading_matches_a_numbered_container(self):
        self.insert('en', 1, '    #### Example 1-1. Nested example {#sample}\n\n    ```sql\n    SELECT 1;\n    ```')
        self.insert('zh', 1, '    {{< eg id="sample" num="1-1" caption="嵌套示例" >}}\n\n    ```sql\n    SELECT 1;\n    ```\n\n    {{< /eg >}}')
        self.assertEqual(self.errors(), [])

    def test_line_leading_reference_fails_without_hiding_intended_citation(self):
        self.insert('en', 1, 'Quotation\n[^1]:\n\n> Words.')
        self.insert('zh', 1, '引文 [^1]：\n\n> 引文。')
        self.assertTrue(any(e['check'] == 'body citation mistaken for a definition' for e in self.errors()))
        en = (self.root/'content/en/ch1.md').read_text()
        self.assertEqual(qa.footnote_definitions(en), ['1'])
        self.assertEqual(qa.footnote_references(en), ['1', '1'])

    def test_inline_colon_citation_and_tail_definition_are_valid(self):
        self.insert('en', 1, 'Quotation [^1]:\n\n> Words.')
        self.insert('zh', 1, '引文 [^1]：\n\n> 引文。')
        self.assertEqual(self.errors(), [])

    def test_shared_title_links_are_checked_but_description_is_preserved(self):
        shared = self.root/'content/zh/glossary.md'
        shared.write_text('参见“[过时标题](/ch1#section_1)”。\n')
        self.assertTrue(any(e['check'] == 'heading link label' for e in self.errors()))
        shared.write_text('参见“[概述](/ch1#section_1)”。也可[阅读说明](/ch1#section_1)。\n')
        self.assertEqual(self.errors(), [])
        shared.write_text('- [阅读说明](/ch1#section_1)\n')
        self.assertEqual(self.errors(), [])

    def test_same_target_descriptive_chapter_label_is_not_forced_to_title(self):
        self.insert('en', 1, '[Overview](/en/ch2#section_2), or [read more](/en/ch2#section_2).')
        self.insert('zh', 1, '[概述](/ch2#section_2)，或[阅读说明](/ch2#section_2)。')
        self.assertEqual(self.errors(), [])

    def test_invalid_internal_link_and_missing_image_are_rejected(self):
        self.insert('zh', 1, '[链接](/ch2#missing)\n\n![图](/missing.png)')
        checks = {e['check'] for e in self.errors()}
        self.assertIn('internal chapter target', checks)
        self.assertIn('image resource', checks)

    def test_other_language_root_is_a_legal_entry(self):
        (self.root/'content/zh/contrib.md').write_text('[繁體](/tw)\n')
        self.assertEqual(self.errors(), [])

    def test_fenced_and_inline_literal_links_are_not_targets(self):
        body = '```md\n[not a link](/ch99#missing)\n```\n\n`[also literal](/ch99#missing)`'
        self.insert('en', 1, body); self.insert('zh', 1, body)
        self.assertEqual(self.errors(), [])

    def test_bibliography_corruption_is_not_hidden_by_url_exceptions(self):
        path = self.root/'content/zh/ch1.md'
        path.write_text(path.read_text().replace('Author. Reference.', 'Other author. Reference.'))
        self.assertTrue(any(e['check'] == 'bibliography preservation with listed URL corrections' for e in self.errors()))

    def test_reviewed_index_labels_align_by_bullet_not_file_line(self):
        (self.root/'bin').mkdir()
        (self.root/'bin/translation-terms.json').write_text(json.dumps({'scope': 'index_labels', 'terms': {'race conditions': '竞态条件'}}))
        (self.root/'content/en/indexes.md').write_text('### R\n\n- race conditions, [Overview](/en/ch1#section_1)\n- unreviewed label\n')
        target = self.root/'content/zh/indexes.md'
        target.write_text('额外元数据与说明\n\n### R\n\n- 竞态条件, [概述](/ch1#section_1)\n- 未审译法保持原样\n')
        self.assertEqual(self.errors(), [])
        target.write_text(target.read_text().replace('竞态条件', '种族条件'))
        self.assertTrue(any(e['check'] == 'reviewed index label' for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
