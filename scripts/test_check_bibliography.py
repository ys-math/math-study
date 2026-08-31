#!/usr/bin/env python3
r"""Tests for scripts/check_bibliography.py.

Two kinds of test here, and the second is the one that matters. The first kind
builds a synthetic bibliography and asserts the checker's verdict on it. The
second runs the checker against the repo's real tex/*/bibliography.tex, so that
a hand-edited entry -- which is how the divergence that prompted this script
arrived -- fails the suite rather than waiting to be noticed.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import unittest
from pathlib import Path

from check_bibliography import SPDX, check_file, check_text, entries_of

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "tex"

BOOK = """\\bibitem{bib: Rosenberg}
J. Rosenberg,
\\textit{Algebraic $K$-Theory and Its Applications},
Graduate Texts in Mathematics 147, Springer-Verlag, 1994."""

ARTICLE = """\\bibitem{bib: Milnor}
J. Milnor,
``On manifolds homeomorphic to the 7-sphere'',
\\textit{Annals of Mathematics} \\textbf{64} (1956), 399--405."""

PREPRINT = """\\bibitem{bib: Leinster}
T. Leinster,
``Basic Category Theory'',
preprint, arXiv:1612.09375 [math.CT], 2025."""

WEB = """\\bibitem{bib: nLab}
nLab,
``adjoint functor'',
\\url{https://ncatlab.org/nlab/show/adjoint+functor}, 2026-08-31."""

JAPANESE_BOOK = """\\bibitem{bib: 松本}
松本幸夫,
『多様体の基礎』,
東京大学出版会, 1988."""

JAPANESE_WEB = """\\bibitem{bib: 数学セミナー編集部}
数学セミナー編集部,
「圏論のはなし」,
\\url{https://example.jp/kenron}, 2026-08-31."""


def build(*entries: str, spdx: str = SPDX, width: str = "9") -> str:
    """A whole bibliography.tex around the given entries, in the order given."""
    body = "\n\n".join(entries)
    return (
        f"{spdx}\n"
        "% !TEX root = main.tex\n"
        "\n"
        "\\phantomsection\n"
        "\\addcontentsline{toc}{section}{参考文献}\n"
        f"\\begin{{thebibliography}}{{{width}}}\n"
        "\n"
        f"{body}\n"
        "\n"
        "\\end{thebibliography}\n"
    )


def messages(text: str) -> list[str]:
    return [problem.message for problem in check_text("t.tex", text)]


class TestEveryKindPasses(unittest.TestCase):
    """The grammar is meant to accept all four kinds in both languages.

    If one of these ever fails, the checker has grown a rule the convention does
    not have -- which is worse than no checker, because it pushes the next entry
    into a shape nothing agreed to.
    """

    def test_book(self) -> None:
        self.assertEqual(messages(build(BOOK)), [])

    def test_journal_article(self) -> None:
        self.assertEqual(messages(build(ARTICLE)), [])

    def test_arxiv_preprint(self) -> None:
        self.assertEqual(messages(build(PREPRINT)), [])

    def test_web_resource(self) -> None:
        self.assertEqual(messages(build(WEB)), [])

    def test_japanese_book(self) -> None:
        self.assertEqual(messages(build(JAPANESE_BOOK)), [])

    def test_japanese_web_resource(self) -> None:
        self.assertEqual(messages(build(JAPANESE_WEB)), [])

    def test_several_together_in_order(self) -> None:
        self.assertEqual(messages(build(PREPRINT, ARTICLE, BOOK)), [])


class TestTheLicenceHeader(unittest.TestCase):
    def test_missing_spdx_fails(self) -> None:
        text = build(BOOK, spdx="% !TEX root = main.tex")
        self.assertIn("line 1 must be", " ".join(messages(text)))

    def test_the_mit_header_fails_too(self) -> None:
        """The root LICENSE is MIT, so this is the header that reads as correct."""
        text = build(BOOK, spdx="% SPDX-License-Identifier: MIT")
        self.assertIn("line 1 must be", " ".join(messages(text)))


class TestTheKey(unittest.TestCase):
    def test_missing_prefix_fails(self) -> None:
        text = build(BOOK.replace("bib: Rosenberg", "Rosenberg"))
        self.assertIn("not 'bib: ' plus a spaceless body", " ".join(messages(text)))

    def test_missing_space_after_colon_fails(self) -> None:
        text = build(BOOK.replace("bib: Rosenberg", "bib:Rosenberg"))
        self.assertIn("not 'bib: ' plus a spaceless body", " ".join(messages(text)))

    def test_a_year_suffix_is_fine(self) -> None:
        self.assertEqual(messages(build(BOOK.replace("Rosenberg", "Weibel1994"))), [])

    def test_a_web_page_suffix_is_fine(self) -> None:
        """`bib: nLabAdjoint` is the collision form for a web resource."""
        self.assertEqual(messages(build(WEB.replace("nLab}", "nLabAdjoint}"))), [])


class TestTheThreeLineGrammar(unittest.TestCase):
    def test_a_fourth_line_fails(self) -> None:
        text = build(BOOK + "\nSecond printing, 1996.")
        self.assertIn("has 4 lines, not 3", " ".join(messages(text)))

    def test_a_two_line_entry_fails(self) -> None:
        """The shape an authorless work would take if the site did not fill line 1."""
        text = build("\n".join(WEB.splitlines()[:1] + WEB.splitlines()[2:]))
        self.assertIn("has 2 lines, not 3", " ".join(messages(text)))

    def test_author_line_without_a_comma_fails(self) -> None:
        text = build(BOOK.replace("J. Rosenberg,", "J. Rosenberg"))
        self.assertIn("author line must end in ','", " ".join(messages(text)))

    def test_locator_without_a_full_stop_fails(self) -> None:
        text = build(BOOK.replace("Springer-Verlag, 1994.", "Springer-Verlag, 1994"))
        self.assertIn("locator line must end in '.'", " ".join(messages(text)))

    def test_a_wrong_length_entry_is_not_also_punctuation_checked(self) -> None:
        """One entry, one complaint: the line roles are undefined once the count is."""
        text = build(BOOK + "\nSecond printing, 1996")
        self.assertEqual(len(messages(text)), 1)


class TestTheTitleMarkup(unittest.TestCase):
    def test_a_straight_quote_fails(self) -> None:
        r"""The bug this rule exists for.

        Under jlreq with LuaLaTeX the encoding is TU and `"` typesets as U+201D,
        so `"Title"` prints with a closing quote at both ends -- balanced in the
        source and wrong in the PDF. It shipped once; it does not ship again.
        """
        text = build(ARTICLE.replace("``On", '"On').replace("sphere''", 'sphere"'))
        self.assertIn("straight", " ".join(messages(text)))

    def test_an_unmarked_title_fails(self) -> None:
        text = build(ARTICLE.replace("``On", "On").replace("sphere''", "sphere"))
        self.assertIn("title must open with", " ".join(messages(text)))

    def test_japanese_wrapped_in_textit_fails(self) -> None:
        r"""\textit{} is inert on CJK: the PDF loses the emphasis silently.

        It clears the "opens with a sanctioned marker" branch, which is exactly
        why it needs a branch of its own -- nothing about the source looks wrong.
        """
        text = build(JAPANESE_BOOK.replace("『多様体の基礎』,", "\\textit{多様体の基礎},"))
        self.assertIn("takes 『』 or 「」", " ".join(messages(text)))

    def test_japanese_in_latin_quotes_fails(self) -> None:
        text = build(JAPANESE_WEB.replace("「圏論のはなし」,", "``圏論のはなし'',"))
        self.assertIn("takes 『』 or 「」", " ".join(messages(text)))

    def test_a_latin_title_is_not_mistaken_for_japanese(self) -> None:
        self.assertEqual(messages(build(ARTICLE)), [])


class TestTheOrder(unittest.TestCase):
    def test_out_of_order_fails(self) -> None:
        self.assertIn("sorts before", " ".join(messages(build(BOOK, ARTICLE))))

    def test_the_fold_is_case_insensitive(self) -> None:
        """`bib: nLab` before `bib: Riehl`: right alphabetically, wrong in ASCII."""
        riehl = BOOK.replace("bib: Rosenberg", "bib: Riehl")
        self.assertEqual(messages(build(WEB, riehl)), [])

    def test_the_fold_still_catches_a_real_inversion(self) -> None:
        riehl = BOOK.replace("bib: Rosenberg", "bib: Riehl")
        self.assertIn("sorts before", " ".join(messages(build(riehl, WEB))))


class TestTheLabelWidth(unittest.TestCase):
    def test_nine_is_too_narrow_for_ten_entries(self) -> None:
        entries = [BOOK.replace("Rosenberg", f"A{index:02d}") for index in range(10)]
        self.assertIn("too narrow for 10 entries", " ".join(messages(build(*entries))))

    def test_ninety_nine_is_wide_enough(self) -> None:
        entries = [BOOK.replace("Rosenberg", f"A{index:02d}") for index in range(10)]
        self.assertEqual(messages(build(*entries, width="99")), [])


class TestEntrySplitting(unittest.TestCase):
    def test_a_blank_line_ends_an_entry(self) -> None:
        entries = entries_of(build(BOOK, ARTICLE).splitlines())
        self.assertEqual([key for _, key, _ in entries], ["bib: Rosenberg", "bib: Milnor"])
        self.assertEqual([len(body) for _, _, body in entries], [3, 3])

    def test_the_end_of_the_environment_ends_the_last_entry(self) -> None:
        (_, _, body), = entries_of(build(BOOK).splitlines())
        self.assertEqual(len(body), 3)


class TestTheRepoItself(unittest.TestCase):
    """The guard that would have caught the divergence this script was written for.

    bib: Riehl arrived inside a chapter commit rather than through /bib, and no
    check looked at it. These run against the real files, so the next one fails
    here.
    """

    def test_there_are_bibliographies_to_check(self) -> None:
        self.assertGreater(len(list(TEX.glob("*/bibliography.tex"))), 0)

    def test_every_bibliography_in_the_repo_conforms(self) -> None:
        for path in sorted(TEX.glob("*/bibliography.tex")):
            with self.subTest(topic=path.parent.name):
                self.assertEqual([str(problem) for problem in check_file(path)], [])


if __name__ == "__main__":
    unittest.main()
