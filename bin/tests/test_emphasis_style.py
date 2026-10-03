"""Regression cases for preserving Markdown syntax while normalizing prose."""

from pathlib import Path
import importlib.util
import unittest


spec = importlib.util.spec_from_file_location(
    "emphasis_style", Path(__file__).resolve().parents[1] / "emphasis-style.py"
)
emphasis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emphasis)


class EmphasisStyleTests(unittest.TestCase):
    def test_star_bullet_padding_survives_chinese_punctuation(self):
        for punctuation in "（《〈「『【〔〖“‘":
            with self.subTest(punctuation=punctuation):
                source = f"* {punctuation}说明）\n"
                self.assertEqual(
                    emphasis.normalize_document(source, normalize_strong=True), source
                )

    def test_quoted_nested_lists_keep_markers_and_normalize_content(self):
        source = "> >   * \t《**书名**》和*术语*说明\r\n"
        expected = "> >   * \t《*书名*》和 *术语* 说明\r\n"
        self.assertEqual(
            emphasis.normalize_document(source, normalize_strong=True), expected
        )

    def test_bullet_padding_and_inline_code_are_preserved(self):
        source = "  * \t（`a**b`）这是*术语*说明\n"
        expected = "  * \t（`a**b`）这是 *术语* 说明\n"
        self.assertEqual(
            emphasis.normalize_document(source, normalize_strong=True), expected
        )

    def test_fenced_code_and_links_keep_their_syntax(self):
        source = "```text\n* （**literal**）\n```\n* 《[*书名*](/book)》\n"
        self.assertEqual(
            emphasis.normalize_document(source, normalize_strong=True), source
        )

    def test_valid_prose_spacing_and_strong_mode_are_unchanged(self):
        self.assertEqual(
            emphasis.normalize_line("说明： *重点* ，继续", normalize_strong=True),
            "说明：*重点*，继续",
        )
        self.assertEqual(
            emphasis.normalize_line("* （**人名**）", normalize_strong=False),
            "* （**人名**）",
        )
        emphasis.validate_examples()

    def test_normalization_is_idempotent(self):
        source = "* （**术语**）和*内容*相邻\n\n正文*强调*，继续。\n"
        once = emphasis.normalize_document(source, normalize_strong=True)
        self.assertEqual(
            emphasis.normalize_document(once, normalize_strong=True), once
        )


if __name__ == "__main__":
    unittest.main()
