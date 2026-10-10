#!/usr/bin/env python3
r"""Drift guard between \Interactive links and the pages they point at.

`\Interactive{<name>}` in a chapter of `tex/<slug>/` prints a link to the page
`tex/<slug>/html/<name>.html` as GitHub Pages serves it. The rules are
docs/interactive-convention.md; the macro is in tex/preamble.tex.

**Why a test.** The PDF build never reads the page and the Pages deploy never
reads the chapter, so a typo in the name, a renamed page or a deleted one
leaves a link to a 404 behind two green builds. This is the only thing that
looks at both.

What is checked:

- **Every `\Interactive` outside a comment is well-formed**: one
  `\Interactive{<kebab-case-name>}` on a line of its own. A malformed one
  would otherwise be skipped by the parser below and pass.
- **Every link has a page**: `tex/<slug>/html/<name>.html` exists, in the
  same topic as the chapter that links to it.
- **Every page has a link.** A page no chapter points at is unreachable from
  where readers start, so it is an orphan whether or not it works.
- **Every page is shaped like one**: a kebab-case name, the CC BY-NC-ND
  header on line 1, and the engine loaded from `../../html-common/`. A page
  that inlines its own engine would drift from the others silently.

A consequence worth knowing: a page and the `\Interactive` line that links to
it have to land in the same commit, or this fails in between — and because the
`scripts/` tests run in `update-readme.yml` too, the README bot stays red until
the other half arrives.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "tex"

NAME = r"[a-z0-9]+(?:-[a-z0-9]+)*"
INTERACTIVE = re.compile(rf"^\s*\\Interactive\{{({NAME})\}}\s*$")
HEADER = "<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->"
ENGINE = '<script src="../../html-common/diagram.js"></script>'


def interactive_lines(source: str) -> list[str]:
    r"""Every line that mentions \Interactive outside a comment."""
    return [
        line
        for line in source.splitlines()
        if "\\Interactive" in line.split("%", 1)[0]
    ]


def parse_interactive(line: str) -> str | None:
    """The page name of a well-formed line, None otherwise."""
    match = INTERACTIVE.match(line)
    return match.group(1) if match else None


def links() -> dict[tuple[str, str], list[str]]:
    """(slug, name) of every well-formed link, mapped to the chapters using it."""
    found: dict[tuple[str, str], list[str]] = {}
    for chapter in sorted(TEX.glob("*/ch*.tex")):
        for line in interactive_lines(chapter.read_text(encoding="utf-8")):
            name = parse_interactive(line)
            if name:
                found.setdefault((chapter.parent.name, name), []).append(chapter.name)
    return found


def pages() -> list[Path]:
    return sorted(TEX.glob("*/html/*.html"))


class TestParser(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(parse_interactive(r"\Interactive{biproduct-sphere}"), "biproduct-sphere")

    def test_malformed(self):
        self.assertIsNone(parse_interactive(r"\Interactive{biproduct_sphere}"))
        self.assertIsNone(parse_interactive(r"\Interactive{Biproduct-Sphere}"))
        self.assertIsNone(parse_interactive(r"\Interactive{biproduct-sphere.html}"))
        self.assertIsNone(parse_interactive(r"\Interactive{a} 続き"))

    def test_comments_are_ignored(self):
        self.assertEqual(interactive_lines(r"% \Interactive{a}"), [])
        self.assertEqual(len(interactive_lines(r"\Interactive{a} % note")), 1)


class TestRepo(unittest.TestCase):
    def test_every_interactive_is_well_formed(self):
        for chapter in sorted(TEX.glob("*/ch*.tex")):
            for line in interactive_lines(chapter.read_text(encoding="utf-8")):
                with self.subTest(chapter=str(chapter.relative_to(ROOT)), line=line):
                    self.assertIsNotNone(
                        parse_interactive(line),
                        "expected \\Interactive{<kebab-case-name>} alone on its line",
                    )

    def test_every_link_has_a_page(self):
        for (slug, name), chapters in links().items():
            with self.subTest(topic=slug, name=name, chapters=chapters):
                self.assertTrue(
                    (TEX / slug / "html" / f"{name}.html").is_file(),
                    f"no page tex/{slug}/html/{name}.html",
                )

    def test_every_page_has_a_link(self):
        linked = set(links())
        for page in pages():
            with self.subTest(page=str(page.relative_to(ROOT))):
                self.assertIn(
                    (page.parent.parent.name, page.stem),
                    linked,
                    f"no chapter of tex/{page.parent.parent.name}/ has \\Interactive{{{page.stem}}}",
                )

    def test_every_page_is_shaped_like_one(self):
        for page in pages():
            source = page.read_text(encoding="utf-8")
            with self.subTest(page=str(page.relative_to(ROOT))):
                self.assertRegex(page.stem, rf"^{NAME}$", "page names are kebab-case")
                self.assertEqual(source.splitlines()[0], HEADER, "licence header on line 1")
                self.assertIn(ENGINE, source, "the page must load the shared engine")


if __name__ == "__main__":
    unittest.main()
