#!/usr/bin/env python3
r"""Drift guard for the \Assumes declarations in tex/*/main.tex.

`\Assumes{<slug>}{<title>}` prints a 前提知識 entry at the top of a topic's
目次 page, linking to `pdf/<slug>.pdf` under the title given. The rule is
docs/naming-convention.md `## Inside a topic`; the macro is in
tex/preamble.tex.

**Why a test.** Both arguments name another topic, and the build of this topic
never reads that topic's sources — on purpose, so one PDF does not depend on
another. So a prerequisite that is renamed or deleted leaves a link to a 404,
and a retitled one leaves the old title in print, behind a green build. This
is the only thing that looks.

What is checked, for every `\Assumes` outside a comment:

- **The line is well-formed**: one `\Assumes{<slug>}{<title>}` on a line of its
  own. A malformed one would otherwise be skipped by the parser below and pass.
- **`tex/<slug>/main.tex` exists.**
- **`<title>` is byte-for-byte that topic's `\DocTitle`.**
- **A topic does not assume itself.**

Deliberately not checked: cycles across topics. A cycle among the owner's own
notes is a choice, not a broken artifact.

A consequence worth knowing: deleting a topic that another assumes fails this
test, and because the `scripts/` tests run in `update-readme.yml` too, the
README bot stays red until the `\Assumes` line goes. `/delete-topic` refuses
for that reason.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "tex"

# The title may itself contain braces (\texorpdfstring{代数的$K$理論}{…}), so
# it runs greedily to the last brace on the line rather than to the first.
ASSUMES = re.compile(r"^\s*\\Assumes\{([a-z0-9_]+)\}\{(.*)\}\s*$")
DOC_TITLE = re.compile(r"^\\newcommand\{\\DocTitle\}\{(.*)\}\s*$", re.M)


def assumes_lines(source: str) -> list[str]:
    r"""Every line that mentions \Assumes outside a comment."""
    return [
        line
        for line in source.splitlines()
        if "\\Assumes" in line.split("%", 1)[0]
    ]


def parse_assumes(line: str) -> tuple[str, str] | None:
    """(slug, title) for a well-formed line, None otherwise."""
    match = ASSUMES.match(line)
    return (match.group(1), match.group(2)) if match else None


def doc_title(source: str) -> str | None:
    match = DOC_TITLE.search(source)
    return match.group(1) if match else None


class TestParser(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(
            parse_assumes(r"\Assumes{category_theory}{圏論}"),
            ("category_theory", "圏論"),
        )

    def test_title_with_braces(self):
        line = r"\Assumes{algebraic_k_theory}{\texorpdfstring{代数的$K$理論}{代数的K理論}}"
        self.assertEqual(
            parse_assumes(line),
            ("algebraic_k_theory", r"\texorpdfstring{代数的$K$理論}{代数的K理論}"),
        )

    def test_malformed(self):
        self.assertIsNone(parse_assumes(r"\Assumes{category_theory}"))
        self.assertIsNone(parse_assumes(r"\Assumes{Category Theory}{圏論}"))
        self.assertIsNone(parse_assumes(r"\Assumes{a}{圏論} \tableofcontents"))

    def test_comments_are_ignored(self):
        self.assertEqual(assumes_lines(r"% \Assumes{category_theory}{圏論}"), [])
        self.assertEqual(len(assumes_lines(r"\Assumes{a}{b} % note")), 1)


class TestRepo(unittest.TestCase):
    def test_every_assumes_resolves(self):
        for main in sorted(TEX.glob("*/main.tex")):
            topic = main.parent.name
            for line in assumes_lines(main.read_text(encoding="utf-8")):
                with self.subTest(topic=topic, line=line):
                    parsed = parse_assumes(line)
                    self.assertIsNotNone(
                        parsed, "expected \\Assumes{<slug>}{<title>} alone on its line"
                    )
                    slug, title = parsed
                    self.assertNotEqual(slug, topic, "a topic cannot assume itself")
                    target = TEX / slug / "main.tex"
                    self.assertTrue(target.is_file(), f"no topic tex/{slug}/")
                    self.assertEqual(
                        title,
                        doc_title(target.read_text(encoding="utf-8")),
                        f"title differs from tex/{slug}/main.tex's \\DocTitle",
                    )


if __name__ == "__main__":
    unittest.main()
