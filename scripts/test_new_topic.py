#!/usr/bin/env python3
"""Tests for scripts/new_topic.py.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import unittest
from pathlib import Path

from latex_unicode import UnsupportedLatex
from new_topic import InvalidTopic, render_main, validate_title, validate_topic

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "tex"


def topic_names() -> list[str]:
    return sorted(path.parent.name for path in TEX.glob("*/main.tex"))


class TestTemplateMatchesRepo(unittest.TestCase):
    r"""The template must reproduce the main.tex files already in the repo.

    This is the drift guard: if the shared conventions change (\input lines, the
    preamble path, the colophon), a hand-edited topic and a generated one would
    silently diverge, and these are the tests that say so.

    lambda_calculus is deliberately not covered — it \input{}s three chapters,
    which is what a topic grows into, not what it is created as.
    """

    def assert_reproduces(self, topic: str, title: str) -> None:
        expected = (TEX / topic / "main.tex").read_text(encoding="utf-8")
        self.assertEqual(render_main(topic, title), expected)

    def test_plain_title(self):
        self.assert_reproduces("topology", "位相幾何学")
        self.assert_reproduces("category_theory", "圏論")
        self.assert_reproduces("manifold", "多様体論")

    def test_title_containing_math(self):
        self.assert_reproduces(
            "algebraic_k_theory", r"\texorpdfstring{代数的$K$理論}{代数的K理論}"
        )

    def test_no_trailing_newline(self):
        # Matching the repo byte-for-byte includes its lack of a final newline.
        self.assertTrue(render_main("sheaf_theory", "層論").endswith(r"\end{document}"))

    def test_topic_only_reaches_the_url(self):
        source = render_main("sheaf_theory", "層論")
        self.assertIn(
            r"\newcommand{\TexRepo}{https://github.com/ys-math/math-study"
            r"/tree/main/tex/sheaf_theory}",
            source,
        )
        self.assertIn(r"\newcommand{\DocTitle}{層論}", source)


class TestValidateTopic(unittest.TestCase):
    def test_existing_topics_are_all_valid_names(self):
        # Guards the rule being stricter than the convention it describes.
        for topic in topic_names():
            with self.subTest(topic=topic):
                validate_topic(topic)

    def test_accepts_plausible_new_names(self):
        for topic in ("sheaf_theory", "k3", "a"):
            with self.subTest(topic=topic):
                validate_topic(topic)

    def test_rejects_unusable_names(self):
        for topic in (
            "",
            "Sheaf",  # uppercase
            "sheaf theory",  # space
            "sheaf-theory",  # hyphen
            "sheaf.theory",  # would be a wildcard in build-pdf.yml's regex
            "2categories",  # leading digit
            "_scratch",  # leading underscore
            "層論",  # not a safe filename or URL segment
            "a/b",  # path separator
        ):
            with self.subTest(topic=topic):
                with self.assertRaises(InvalidTopic):
                    validate_topic(topic)

    def test_rejects_reserved_names(self):
        for topic in ("pdf", "scripts", "latex_out"):
            with self.subTest(topic=topic):
                with self.assertRaises(InvalidTopic):
                    validate_topic(topic)

    def test_rejects_taken_names(self):
        with self.assertRaises(InvalidTopic):
            validate_topic("topology", topic_names())


class TestValidateTitle(unittest.TestCase):
    def test_returns_the_readme_label(self):
        self.assertEqual(validate_title("層論"), "層論")
        self.assertEqual(validate_title(r"代数的$K$理論"), "代数的K理論")
        self.assertEqual(
            validate_title(r"\texorpdfstring{代数的$K$理論}{代数的K理論}"), "代数的K理論"
        )

    def test_rejects_unsupported_latex(self):
        # Anything latex_unicode refuses would break generate_pdf_links.py in CI.
        with self.assertRaises(UnsupportedLatex):
            validate_title(r"$\A^1$ホモトピー論")

    def test_rejects_an_empty_label(self):
        for title in ("", "   ", r"\,"):
            with self.subTest(title=title):
                with self.assertRaises(UnsupportedLatex):
                    validate_title(title)


if __name__ == "__main__":
    unittest.main()
