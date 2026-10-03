#!/usr/bin/env python3
r"""Drift guard for the \Assumes declarations in tex/*/main.tex.

`\Assumes{<slug>}` prints a 前提知識 entry at the top of a topic's 目次 page,
reading `<slug>.pdf` and linking to that file in `pdf/`. The rule is
docs/naming-convention.md `## Inside a topic`; the macro is in
tex/preamble.tex.

**Why a test.** The slug names another topic, and the build of this topic
never reads that topic's sources — on purpose, so one PDF does not depend on
another. So a prerequisite that is renamed or deleted leaves a link to a 404
behind a green build. This is the only thing that looks.

What is checked, for every `\Assumes` outside a comment:

- **The line is well-formed**: one `\Assumes{<slug>}` on a line of its own. A
  malformed one would otherwise be skipped by the parser below and pass — and
  a leftover second argument from the macro's old two-argument form would be
  typeset as stray text after the entry.
- **`tex/<slug>/main.tex` exists.**
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

ASSUMES = re.compile(r"^\s*\\Assumes\{([a-z0-9_]+)\}\s*$")


def assumes_lines(source: str) -> list[str]:
    r"""Every line that mentions \Assumes outside a comment."""
    return [
        line
        for line in source.splitlines()
        if "\\Assumes" in line.split("%", 1)[0]
    ]


def parse_assumes(line: str) -> str | None:
    """The slug of a well-formed line, None otherwise."""
    match = ASSUMES.match(line)
    return match.group(1) if match else None


class TestParser(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(parse_assumes(r"\Assumes{category_theory}"), "category_theory")

    def test_malformed(self):
        self.assertIsNone(parse_assumes(r"\Assumes{category_theory}{圏論}"))
        self.assertIsNone(parse_assumes(r"\Assumes{Category Theory}"))
        self.assertIsNone(parse_assumes(r"\Assumes{a} \tableofcontents"))

    def test_comments_are_ignored(self):
        self.assertEqual(assumes_lines(r"% \Assumes{category_theory}"), [])
        self.assertEqual(len(assumes_lines(r"\Assumes{a} % note")), 1)


class TestRepo(unittest.TestCase):
    def test_every_assumes_resolves(self):
        for main in sorted(TEX.glob("*/main.tex")):
            topic = main.parent.name
            for line in assumes_lines(main.read_text(encoding="utf-8")):
                with self.subTest(topic=topic, line=line):
                    slug = parse_assumes(line)
                    self.assertIsNotNone(slug, "expected \\Assumes{<slug>} alone on its line")
                    self.assertNotEqual(slug, topic, "a topic cannot assume itself")
                    self.assertTrue(
                        (TEX / slug / "main.tex").is_file(), f"no topic tex/{slug}/"
                    )


if __name__ == "__main__":
    unittest.main()
