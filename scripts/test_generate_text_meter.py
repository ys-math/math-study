#!/usr/bin/env python3
"""Tests for scripts/generate_text_meter.py.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

The meter makes three claims a reader will trust without checking, and each one
is a place where a plausible-looking implementation is silently wrong:

- **An empty bar means nothing is written.** A topic holding one real sentence
  is 0.2% of the repo, which rounds to zero cells and zero eighths. The floor is
  what keeps it visible, and nothing about a missing floor looks wrong from the
  outside -- the row is still there, still carrying its true percentage.
- **The columns line up.** They only do so because the total row's rule is
  derived from the same widths as the data rows. A hand-counted indent survives
  every test that does not compare the two.
- **The percentages sum to the total.** Which they do only if the denominator is
  the sum over exactly the files the meter counted.

What is deliberately not tested: the specific numbers on disk. They change every
time the owner writes a sentence, and a test asserting them would fail on the
commit it was meant to protect.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from generate_text_meter import (
    BAR_WIDTH,
    EMPTY,
    FULL,
    TOTAL_LABEL,
    bar,
    build_body,
    count_characters,
)


class TestCountCharacters(unittest.TestCase):
    """What a chapter file contributes."""

    def count(self, text: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ch01.tex"
            path.write_text(text, encoding="utf-8")
            return count_characters(path)

    def test_counts_content_characters(self):
        self.assertEqual(self.count("abcde\n"), 5)

    def test_skips_comment_lines(self):
        header = "% SPDX-License-Identifier: CC-BY-NC-ND-4.0\n% !TEX root = main.tex\n"
        self.assertEqual(self.count(header), 0)

    def test_skips_indented_comment_lines(self):
        self.assertEqual(self.count("    % a note\nabc\n"), 3)

    def test_strips_indentation_and_trailing_space(self):
        # A nested itemize must not make a topic look bigger than it is.
        self.assertEqual(self.count("        abc   \n"), 3)

    def test_blank_lines_count_nothing(self):
        self.assertEqual(self.count("\n\n\nabc\n"), 3)

    def test_counts_codepoints_not_bytes(self):
        # Japanese prose is three bytes a character in UTF-8; the meter measures
        # what was written, not how it is encoded.
        self.assertEqual(self.count("圏論\n"), 2)

    def test_does_not_strip_latex_markup(self):
        # Deliberate, per the module docstring: here the mathematics is markup.
        self.assertEqual(self.count(r"$\cod(f)$" + "\n"), len(r"$\cod(f)$"))

    def test_a_percent_mid_line_is_not_a_comment(self):
        # Only a line that *starts* with % is dropped; the rest of the line is
        # content regardless of what a real LaTeX tokenizer would say.
        self.assertEqual(self.count("abc % tail\n"), len("abc % tail"))


class TestBar(unittest.TestCase):
    """The rendering rule, including the floor that Question 5 turned on."""

    def test_zero_is_entirely_empty(self):
        self.assertEqual(bar(0.0), EMPTY * BAR_WIDTH)

    def test_full_is_entirely_filled(self):
        self.assertEqual(bar(1.0), FULL * BAR_WIDTH)

    def test_every_bar_is_exactly_the_declared_width(self):
        for permille in range(0, 1001):
            with self.subTest(permille=permille):
                self.assertEqual(len(bar(permille / 1000)), BAR_WIDTH)

    def test_half_fills_half_the_cells(self):
        self.assertEqual(bar(0.5), FULL * 10 + EMPTY * 10)

    def test_nonzero_never_renders_as_empty(self):
        # The claim the whole meter rests on: an empty bar means nothing written.
        tiny = 1 / 1_000_000
        self.assertNotEqual(bar(tiny), EMPTY * BAR_WIDTH)
        self.assertTrue(bar(tiny).startswith("▏"))

    def test_partial_cell_resolves_to_an_eighth(self):
        # 1/8 of one cell out of 20 == 1/160 of the bar.
        self.assertTrue(bar(1 / 160).startswith("▏"))
        self.assertTrue(bar(4 / 160).startswith("▌"))

    def test_a_fraction_over_one_is_clamped(self):
        # Cannot arise from a share, but a bar longer than its own width would
        # break every column to its right rather than merely looking wrong.
        self.assertEqual(len(bar(1.5)), BAR_WIDTH)


class TestBuildBody(unittest.TestCase):
    """The block as a whole."""

    SIZES = {"alpha": 300, "beta": 100, "gamma": 0}

    def body_lines(self, sizes=None) -> list[str]:
        return build_body(self.SIZES if sizes is None else sizes).splitlines()

    def test_is_a_fenced_code_block(self):
        lines = self.body_lines()
        self.assertEqual(lines[0], "```")
        self.assertEqual(lines[-1], "```")

    def test_rows_are_sorted_by_size_descending(self):
        labels = [line.split()[0] for line in self.body_lines()[1:-1]]
        self.assertEqual(labels[:3], ["alpha", "beta", "gamma"])

    def test_ties_are_broken_alphabetically(self):
        lines = self.body_lines({"zulu": 5, "alpha": 5})
        labels = [line.split()[0] for line in lines[1:-1]]
        self.assertEqual(labels[:2], ["alpha", "zulu"])

    def test_total_row_is_last_and_below_the_sort(self):
        # gamma is 0 and alpha is the largest; the total must outrank neither.
        lines = self.body_lines()
        self.assertTrue(lines[-2].startswith(TOTAL_LABEL))
        self.assertIn("400", lines[-2])

    def test_shares_are_percentages_of_the_total(self):
        lines = self.body_lines()
        self.assertIn("75.0%", lines[1])
        self.assertIn("25.0%", lines[2])
        self.assertIn("0.0%", lines[3])

    def test_counts_are_thousands_separated(self):
        self.assertIn("1,234", build_body({"alpha": 1234}))

    def test_the_rule_aligns_with_the_count_column(self):
        # The alignment claim, checked by construction rather than by eye: the
        # dashes must sit exactly under the digits of the row above them.
        lines = self.body_lines({"alpha": 1234, "beta": 56})
        rule = lines[-3]
        self.assertEqual(set(rule.strip()), {"-"})
        self.assertEqual(rule.index("-"), lines[1].index("1,234"))
        self.assertEqual(len(rule.strip()), len("1,290"))

    def test_total_count_aligns_with_the_rule(self):
        lines = self.body_lines({"alpha": 1234, "beta": 56})
        rule, total_row = lines[-3], lines[-2]
        self.assertEqual(total_row.index("1,290"), rule.index("-"))

    def test_all_topics_empty_does_not_divide_by_zero(self):
        # The state of a brand-new repo, and of any repo whose topics are all
        # stubs. Every share is 0.0% and the meter still renders.
        lines = self.body_lines({"alpha": 0, "beta": 0})
        self.assertEqual(lines[1].count("0.0%"), 1)
        self.assertTrue(lines[-2].startswith(TOTAL_LABEL))

    def test_a_single_topic_holds_the_whole_share(self):
        self.assertIn("100.0%", build_body({"alpha": 7}))

    def test_every_row_is_the_same_width(self):
        lines = self.body_lines({"alpha": 1234, "beta": 56, "gamma": 0})
        widths = {len(line) for line in lines[1:4]}
        self.assertEqual(len(widths), 1)


if __name__ == "__main__":
    unittest.main()
