#!/usr/bin/env python3
"""Tests for quiver_macros.py, which publishes the preamble's macros to quiver.

The case that matters is the silent one: a definition quiver cannot read is
skipped with a console warning nobody opens, and the label just renders red.
So the real preamble is checked as well as fixtures — every operator it
declares must reach the file, trailing comment or not.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
import urllib.parse
from pathlib import Path

import quiver
import quiver_macros


class Extract(unittest.TestCase):
    def test_trailing_comments_are_stripped(self):
        self.assertEqual(
            quiver_macros.extract(r"\DeclareMathOperator{\Res}{Res}       % restriction"),
            [r"\DeclareMathOperator{\Res}{Res}"],
        )

    def test_starred_operators_and_renewcommand_are_kept(self):
        src = "\\DeclareMathOperator*{\\colim}{colim}  % star\n\\renewcommand{\\Im}{\\operatorname{Im}}"
        self.assertEqual(
            quiver_macros.extract(src),
            [r"\DeclareMathOperator*{\colim}{colim}", r"\renewcommand{\Im}{\operatorname{Im}}"],
        )

    def test_colours_are_kept(self):
        self.assertEqual(
            quiver_macros.extract(r"\definecolor{myblue}{HTML}{0000EE}"),
            [r"\definecolor{myblue}{HTML}{0000EE}"],
        )

    def test_document_macros_and_other_lines_are_dropped(self):
        src = "\n".join([
            r"\newcommand{\DocAuthor}{\href{\GitHub}{\DocAuthorName}}",
            r"\renewcommand{\proofname}{\bfseries 証明}",
            r"\NewDocumentCommand{\termen}{m}{%",
            r"% \newcommand{\commented}{out}",
            r"\usepackage{hyperref}",
        ])
        self.assertEqual(quiver_macros.extract(src), [])

    def test_escaped_percent_is_not_a_comment(self):
        self.assertEqual(
            quiver_macros.extract(r"\newcommand{\pct}{50\%}"),
            [r"\newcommand{\pct}{50\%}"],
        )


class Preamble(unittest.TestCase):
    def setUp(self):
        self.preamble = Path("tex/preamble.tex").read_text(encoding="utf-8")
        self.kept = quiver_macros.extract(self.preamble)

    def test_every_declared_operator_reaches_quiver(self):
        declared = re.findall(r"^\\DeclareMathOperator\*?\{(\\[a-zA-Z]+)\}", self.preamble, re.M)
        kept = set(re.findall(r"^\\DeclareMathOperator\*?\{(\\[a-zA-Z]+)\}", "\n".join(self.kept), re.M))
        self.assertEqual(sorted(set(declared) - kept), [])

    def test_the_file_starts_with_its_licence_and_holds_no_comments_after(self):
        text = quiver_macros.render(self.preamble)
        self.assertTrue(text.startswith("% SPDX-License-Identifier: MIT\n"))
        body = [line for line in text.splitlines() if not line.startswith("%")]
        self.assertEqual(body, self.kept)


class DraftUrl(unittest.TestCase):
    def test_draft_is_an_empty_diagram_quiver_py_still_decodes(self):
        url = quiver_macros.draft_url()
        self.assertEqual(quiver.parse(quiver.decode_payload(quiver.find_url(url))),
                         {"objects": [], "arrows": []})

    def test_draft_carries_the_gist_url(self):
        query = urllib.parse.parse_qs(quiver_macros.draft_url().split("#", 1)[1])
        self.assertEqual(query["macro_url"], [quiver_macros.MACRO_URL])


if __name__ == "__main__":
    unittest.main()
