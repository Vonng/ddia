"""EPUB alerts remain readable without changing quoted content or code literals."""

import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "epub_preprocess", Path(__file__).resolve().parents[1] / "preprocess-epub.py"
)
epub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(epub)


class EpubAlertTests(unittest.TestCase):
    def test_custom_title_and_entire_quoted_body_are_preserved(self):
        body = (
            '> 第一段 [参考](https://example.org/spec#section) [^note]。\n'
            '>\n'
            '> <a id="detail"></a>\n'
            '> 第二段，包含 `int64` 和 $u_1$。\n'
            '>\n'
            '> - 列表项\n'
            '\n'
            '[^note]: 注释 [链接](#detail)。\n'
        )
        source = '> [!NOTE] 译注：[编码](https://example.org)\n' + body
        converted = epub._lower_alerts(source)
        self.assertEqual(
            converted,
            '> **译注：[编码](https://example.org)**\n>\n' + body,
        )

    def test_all_supported_markers_have_titles_without_custom_title(self):
        expected = {
            'NOTE': '注意', 'TIP': '提示', 'IMPORTANT': '重要',
            'WARNING': '警告', 'CAUTION': '当心',
        }
        for kind, title in expected.items():
            with self.subTest(kind=kind):
                self.assertEqual(
                    epub._lower_alerts(f'> [!{kind}]\n> 正文\n'),
                    f'> **{title}**\n>\n> 正文\n',
                )

    def test_nested_quote_and_crlf_keep_their_container(self):
        self.assertEqual(
            epub._lower_alerts('> > [!TIP] 自定义标题\r\n> > 正文\r\n'),
            '> > **自定义标题**\r\n> >\r\n> > 正文\r\n',
        )

    def test_fences_keep_alert_literals_and_only_close_with_matching_delimiter(self):
        for delimiter in ('````', '~~~~'):
            with self.subTest(delimiter=delimiter):
                code = (
                    f'{delimiter}markdown\n'
                    '> [!NOTE] literal title\n'
                    '```\n'
                    '> [!TIP]\n'
                    '> ```\n'
                    '> [!WARNING]\n'
                    f'- {delimiter}\n'
                    '> [!CAUTION]\n'
                    f'{delimiter}\n'
                )
                source = code + '\n> [!IMPORTANT]\n> outside\n'
                self.assertEqual(
                    epub._lower_alerts(source),
                    code + '\n> **重要**\n>\n> outside\n',
                )

    def test_quoted_and_list_fences_protect_literals(self):
        fixtures = (
            '> ```markdown\n> [!NOTE] literal\n> ```\n',
            '- ```markdown\n  > [!NOTE] literal\n  ```\n',
            '    ~~~markdown\n    > [!NOTE] literal\n    ~~~\n',
        )
        for code in fixtures:
            with self.subTest(code=code):
                self.assertEqual(
                    epub._lower_alerts(code + '\n> [!TIP] after\n> body\n'),
                    code + '\n> **after**\n>\n> body\n',
                )

    def test_quoted_fence_ends_when_its_quote_container_ends(self):
        code = '> ```markdown\n> [!NOTE] literal\n'
        self.assertEqual(
            epub._lower_alerts(code + '\n> [!CAUTION]\n> body\n'),
            code + '\n> **当心**\n>\n> body\n',
        )

    def test_list_then_quote_fence_protects_literal_alerts(self):
        code = '- > ```markdown\n  > [!NOTE] literal\n  > ```\n'
        self.assertEqual(
            epub._lower_alerts(code + '\n> [!NOTE] real\n> body\n'),
            code + '\n> **real**\n>\n> body\n',
        )

    def test_list_fence_ends_when_its_list_container_ends(self):
        code = '- ```markdown\n  > [!NOTE] literal\n'
        self.assertEqual(
            epub._lower_alerts(code + '\n> [!NOTE] real\n> body\n'),
            code + '\n> **real**\n>\n> body\n',
        )

    def test_indented_literal_fence_does_not_hide_a_later_alert(self):
        code = '    ```markdown\n    > [!NOTE] literal\n\n'
        self.assertEqual(
            epub._lower_alerts(code + '> [!NOTE] real\n> body\n'),
            code + '> **real**\n>\n> body\n',
        )

    def test_quoted_indented_code_does_not_hide_a_later_alert(self):
        code = '>     ```\n>     [!NOTE] literal\n>\n'
        self.assertEqual(
            epub._lower_alerts(code + '> [!NOTE] real\n> body\n'),
            code + '> **real**\n>\n> body\n',
        )

    def test_unknown_marker_and_indented_code_are_untouched(self):
        source = '> [!CUSTOM] label\n> body\n\n    > [!NOTE] literal\n'
        self.assertEqual(epub._lower_alerts(source), source)

    def test_document_conversion_preserves_note_content_and_normal_link_rules(self):
        source = (
            '---\ntitle: Example\n---\n\n'
            '## Detail {#detail}\n\n'
            '> [!NOTE] 译注：编码\n'
            '> <a id="note-id"></a> [本节](#detail) [他章](/ch6#other) [^n]。\n'
            '>\n'
            '> 第二段。\n\n'
            '```markdown\n> [!NOTE] literal\n```\n\n'
            '[^n]: 原注释。\n'
        )
        converted = epub.convert_markdown(
            source, stem='ch5', heading_ids={'ch5': {'detail'}, 'ch6': {'other'}}
        )
        self.assertIn('> **译注：编码**\n>\n', converted)
        self.assertIn(
            '> <a id="note-id"></a> [本节](#epub-ch5-detail) '
            '[他章](ch010.xhtml#epub-ch6-other) [^ch5-n]。\n>\n> 第二段。',
            converted,
        )
        self.assertIn('[^ch5-n]: 原注释。', converted)
        self.assertIn('```markdown\n> [!NOTE] literal\n```', converted)


if __name__ == '__main__':
    unittest.main()
