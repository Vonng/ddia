"""Behavioral regressions for second-edition TW generation and archive isolation."""

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('tw_conversion', Path(__file__).resolve().parents[1] / 'zh-tw.py')
tw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tw)
try:
    import opencc
except ImportError:
    opencc = None


def rule(match, before, after, *, filename='test.md', scope=None, expected=1):
    result = {'id': 'reviewed-context', 'file': filename, 'match': match,
              'replacements': [{'before': before, 'after': after}],
              'expected_replacements': expected}
    if scope:
        result['scope'] = scope
    return result


class EditionSelectionTests(unittest.TestCase):
    def test_default_and_explicit_v2_never_invoke_archive_generation(self):
        report = {'files': 24, 'override_rules': 1, 'override_replacements': 1}
        with patch.object(tw, 'convert_v2', return_value=report) as current, \
                patch.object(tw, 'convert_legacy') as archive, redirect_stdout(io.StringIO()):
            tw.main([])
            tw.main(['--edition', 'v2', '--check'])
        self.assertEqual(current.call_args_list[0].kwargs, {'check': False})
        self.assertEqual(current.call_args_list[1].kwargs, {'check': True})
        archive.assert_not_called()

    def test_v1_only_uses_legacy_path(self):
        with patch.object(tw, 'convert_v2') as current, patch.object(tw, 'convert_legacy') as archive:
            tw.main(['--edition', 'v1'])
        archive.assert_called_once_with('v1', 'v1_tw')
        current.assert_not_called()


@unittest.skipIf(opencc is None, 'Real OpenCC regressions require the pinned translate/test environment')
class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.converter = tw.make_converter('s2twp.json')

    def convert(self, source, rules=(), filename='test.md'):
        return tw.convert_document_v2(source, filename, self.converter, rules)[0]

    def test_markdown_url_does_not_freeze_the_following_chinese(self):
        source = '[规范](https://example.com/规范#unions)已改为采用联合类型。'
        result = self.convert(source)
        self.assertIn('(https://example.com/规范#unions)', result)
        self.assertTrue(result.endswith('已改為採用聯合型別。'))

    def test_balanced_url_parentheses_and_autolinks_remain_literal(self):
        source = '[规范](https://example.com/规范_(v2))采用规范。 <https://example.com/规范>'
        result = self.convert(source)
        self.assertIn('(https://example.com/规范_(v2))', result)
        self.assertIn('<https://example.com/规范>', result)
        self.assertIn('採用規範。', result)

    def test_local_routes_keep_trailing_slashes_and_external_paths(self):
        source = '[序言](/preface/) [目录](/zh/toc/#目录) [第一版](/v1/ch1#复制) [外部](https://example.com/ch1/)'
        result = self.convert(source)
        for destination in ('/tw/preface/', '/tw/toc/#目录', '/v1_tw/ch1#复制', 'https://example.com/ch1/'):
            self.assertIn('](' + destination + ')', result)

    def test_reference_destination_and_title_are_separate(self):
        source = '[参考]: https://example.com/规范 "采用规范"'
        result = self.convert(source)
        self.assertIn('https://example.com/规范 "採用規範"', result)

    def test_code_and_identifiers_preserve_original_bytes(self):
        source = "`连接` 和 ``SELECT `项目` FROM t``\n\n```sql\n-- 连接\nSELECT '简体云';\n```\n\n    $变量 = '连接'\n\n    - 项目管理软件\n\n    异步复制仍然运行。"
        result = self.convert(source)
        self.assertIn('`连接` 和 ``SELECT `项目` FROM t``', result)
        self.assertIn("```sql\n-- 连接\nSELECT '简体云';\n```", result)
        self.assertIn("    $变量 = '连接'", result)
        self.assertIn('    - 專案管理軟體', result)
        self.assertIn('    非同步複製仍然執行。', result)

    def test_multiple_backtick_code_can_contain_shorter_backticks(self):
        source = '采用 ``连接 ` 字符以及项目`` 规范。'
        self.assertEqual(self.convert(source), '採用 ``连接 ` 字符以及项目`` 規範。')

    def test_definition_list_prose_can_begin_with_a_latin_acronym(self):
        source = '术语\n\n: 定义\n\n    CAP 定理中的一致性指线性一致性，这是实现及时性的一种强保证。'
        result = self.convert(source)
        self.assertIn('    CAP 定理中的一致性指線性一致性，這是實現及時性的一種強保證。', result)
        self.assertFalse(tw.indented_code_line(source.splitlines()[-1]))
        self.assertTrue(tw.indented_code_line("    $变量 = '连接'"))

    def test_shortcode_only_translates_caption_not_parameter_identity(self):
        source = '{{< fig num="1-1" id="原样-id" src="/图/原样.png" caption="两表连接" class="原样" />}}'
        fixes = [rule(source, '連線', '聯結')]
        result = self.convert(source, fixes)
        self.assertEqual(result, source.replace('两表连接', '兩表聯結'))

    def test_table_attributes_only_translate_the_visible_caption(self):
        source = '{#表-id num="1-1" caption="两表连接" class="原样"}'
        result = self.convert(source, [rule(source, '連線', '聯結')])
        self.assertEqual(result, source.replace('两表连接', '兩表聯結'))

    def test_database_join_does_not_change_network_or_graph_connections(self):
        source = '两表连接\n连接到服务器\n用边连接两个顶点'
        result = self.convert(source, [rule('两表连接', '連線', '聯結')])
        self.assertEqual(result, '兩表聯結\n連線到伺服器\n用邊連線兩個頂點')

    def test_item_override_does_not_change_software_project(self):
        source = '嵌套项目\n开源项目'
        result = self.convert(source, [rule('嵌套项目', '專案', '項目')])
        self.assertEqual(result, '巢狀項目\n開源專案')

    def test_scale_extension_does_not_change_real_software_extension(self):
        source = '扩展到多台机器\npg_jsonschema 扩展'
        result = self.convert(source, [rule('扩展到多台机器', '擴充套件', '擴展')])
        self.assertEqual(result, '擴展到多臺機器\npg_jsonschema 擴充套件')

    def test_operator_is_distinct_from_operand_and_kubernetes_operator(self):
        source = '查询算子\noperand（操作数）\nKubernetes Operator'
        result = self.convert(source, [rule('查询算子', '運算元', '運算子')])
        self.assertTrue(result.startswith('查詢運算子\n'))
        self.assertIn('operand（運算元）', result)
        self.assertTrue(result.endswith('Kubernetes Operator'))

    def test_historical_pr_titles_preserve_wrong_and_correct_spellings(self):
        source = '| [PR #335](https://github.com/Vonng/ddia/pull/335) | [@user](https://github.com/user) | fix: 日志 to 日誌，呼叫-&gt;调用 | 已合并 |'
        result = self.convert(source, filename='contrib.md')
        self.assertIn('| fix: 日志 to 日誌，呼叫-&gt;调用 |', result)
        self.assertTrue(result.endswith('| 已合併 |'))

    def test_old_automatic_heading_alias_and_chinese_explicit_ids_survive(self):
        source = '<a id="法定票数quorum"></a>\n<a id="ascii-id"></a>\n\n### 连接（join）'
        result = self.convert(source, [rule('### 连接（join）', '連線', '聯結')])
        self.assertIn('<a id="法定票數quorum"></a>', result)
        self.assertIn('<a id="ascii-id"></a>', result)
        self.assertIn('<a id="聯結join"></a>\n\n### 聯結（join） {#連線join}', result)
        self.assertNotIn('<a id="連線join"></a>', result)

    def test_fragment_override_changes_only_the_reviewed_component(self):
        source = '- 网络连接, [连接](/ch12#sec_stream_joins)'
        fixes = [rule('[连接](/ch12#sec_stream_joins)', '連線', '聯結', scope='fragment')]
        result = self.convert(source, fixes)
        self.assertEqual(result, '- 網路連線, [聯結](/tw/ch12#sec_stream_joins)')

    def test_expired_and_conflicting_overrides_are_rejected(self):
        for fixes in ([rule('旧段落', '連線', '聯結')],
                      [rule('两表连接', '連線', '聯結', expected=2)]):
            with self.assertRaisesRegex(ValueError, 'missing or changed TW override'):
                self.convert('两表连接', fixes)
        first = rule('两表连接', '連線', '聯結')
        second = rule('两表连接', '連線', '聯接')
        second['id'] = 'competing-context'
        with self.assertRaisesRegex(ValueError, 'conflicting TW overrides'):
            self.convert('两表连接', [first, second])

    def test_component_counts_cannot_hide_a_missing_repair(self):
        fixes = [rule('连接连接算子', '連線', '聯結', expected=2)]
        fixes[0]['replacements'] = [
            {'before': '連線', 'after': '聯結', 'expected_count': 1},
            {'before': '不存在', 'after': '修正', 'expected_count': 1},
        ]
        with self.assertRaisesRegex(ValueError, 'missing or changed TW override'):
            self.convert('连接连接算子', fixes)

    def test_v1_legacy_keeps_its_old_url_and_postprocessing_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.md'
            target = Path(directory) / 'target.md'
            source.write_text('[规范](https://example.com/x)已改为采用规范。  \n复雜 面向对象 可扩展性\n')
            with redirect_stdout(io.StringIO()):
                tw.convert_file_legacy(source, target, 'v1', 'v1_tw')
            self.assertEqual(target.read_text(), '[規範](https://example.com/x)已改为采用规范。\n複雜 物件導向 可擴展性')

    def test_check_is_read_only_and_detects_stale_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for edition in ('zh', 'tw', 'v1', 'v1_tw'):
                (root / 'content' / edition).mkdir(parents=True)
            (root / 'content/zh/test.md').write_text('采用规范')
            (root / 'content/tw/test.md').write_text('採用規範')
            archive = root / 'content/v1_tw/ch1.md'
            archive.write_bytes(b'archived original\n')
            before = {p: p.read_bytes() for p in (root / 'content').glob('*/*.md')}
            with patch.object(tw, 'load_overrides', return_value=[]):
                report = tw.convert_v2(root, check=True)
                self.assertEqual(report['files'], 1)
                (root / 'content/tw/test.md').write_text('stale')
                with self.assertRaisesRegex(ValueError, 'differs from its reviewed generator output'):
                    tw.convert_v2(root, check=True)
            self.assertEqual(archive.read_bytes(), before[archive])
            self.assertEqual((root / 'content/zh/test.md').read_bytes(), before[root / 'content/zh/test.md'])
            self.assertEqual((root / 'content/tw/test.md').read_text(), 'stale')


if __name__ == '__main__':
    unittest.main()
