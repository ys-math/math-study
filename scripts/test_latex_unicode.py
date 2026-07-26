#!/usr/bin/env python3
"""Tests for scripts/latex_unicode.py.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import unittest

from latex_unicode import UnsupportedLatex, render


class TestRealTitles(unittest.TestCase):
    """The \\DocTitle values actually used in this repo."""

    def test_math_in_title(self):
        self.assertEqual(render(r"代数的$K$理論"), "代数的K理論")
        self.assertEqual(render(r"$\lambda$計算"), "λ計算")

    def test_plain_titles_pass_through(self):
        for title in ("圏論", "群論", "微分幾何学", "多様体論", "位相幾何学"):
            self.assertEqual(render(title), title)


class TestScripts(unittest.TestCase):
    """^ and _ become inline HTML, which GitHub renders inside link labels."""

    def test_single_token(self):
        self.assertEqual(render(r"$C^*$代数"), "C<sup>∗</sup>代数")
        self.assertEqual(render(r"$\pi_1$"), "π<sub>1</sub>")

    def test_braced_group(self):
        self.assertEqual(render(r"$H^{12}$"), "H<sup>12</sup>")
        self.assertEqual(render(r"$K_{0}$理論"), "K<sub>0</sub>理論")

    def test_command_argument(self):
        # Unicode has no subscript ∞; the HTML form can express it.
        self.assertEqual(render(r"$A_\infty$"), "A<sub>∞</sub>")


class TestAlphabets(unittest.TestCase):
    def test_letterlike_exceptions(self):
        self.assertEqual(render(r"$\mathbb{Z}$"), "ℤ")
        self.assertEqual(render(r"$\mathfrak{H}$"), "ℌ")
        self.assertEqual(render(r"$\mathcal{L}$"), "ℒ")

    def test_mathematical_alphanumeric_block(self):
        self.assertEqual(render(r"$\mathfrak{g}$"), "𝔤")
        self.assertEqual(render(r"$\mathcal{D}$"), "𝒟")
        self.assertEqual(render(r"$\mathbb{A}$"), "𝔸")

    def test_multiple_letters(self):
        self.assertEqual(render(r"$\mathbb{RP}$"), "ℝℙ")

    def test_transparent_font_commands(self):
        self.assertEqual(render(r"$\mathrm{op}$圏"), "op圏")
        self.assertEqual(render(r"$\operatorname{Hom}$"), "Hom")


class TestSymbols(unittest.TestCase):
    def test_greek_and_operators(self):
        self.assertEqual(render(r"$\Gamma \otimes \Omega$"), "Γ ⊗ Ω")
        self.assertEqual(render(r"$X \to Y$"), "X → Y")

    def test_spacing_collapses(self):
        self.assertEqual(render(r"$K$\,理論"), "K理論")

    def test_escaped_literal(self):
        self.assertEqual(render(r"100\%"), "100%")


class TestMarkdownSafety(unittest.TestCase):
    """The output is an inline link label, so active characters must be neutral."""

    def test_html_characters_become_entities(self):
        self.assertEqual(render(r"$X < Y$"), "X &lt; Y")
        self.assertEqual(render(r"A & B"), "A &amp; B")

    def test_markdown_characters_are_escaped(self):
        self.assertEqual(render(r"a\_b"), r"a\_b")
        self.assertEqual(render(r"[x]"), r"\[x\]")

    def test_grouping_is_flattened(self):
        self.assertEqual(render(r"${\alpha}{\beta}$"), "αβ")


class TestUnsupported(unittest.TestCase):
    def test_unknown_command_raises(self):
        with self.assertRaises(UnsupportedLatex):
            render(r"$\frac{1}{2}$")
        with self.assertRaises(UnsupportedLatex):
            render(r"$\widehat{\mathfrak{g}}$の表現")

    def test_unbalanced_braces_raise(self):
        with self.assertRaises(UnsupportedLatex):
            render(r"$\mathbb{Z$")
        with self.assertRaises(UnsupportedLatex):
            render(r"a}b")

    def test_missing_argument_raises(self):
        with self.assertRaises(UnsupportedLatex):
            render(r"$\mathbb$")

    def test_unstylable_letter_raises(self):
        with self.assertRaises(UnsupportedLatex):
            render(r"$\mathfrak{理}$")

    def test_error_names_the_offender(self):
        with self.assertRaises(UnsupportedLatex) as caught:
            render(r"$\sqrt{2}$")
        self.assertIn(r"\sqrt", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
