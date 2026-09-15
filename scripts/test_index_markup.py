#!/usr/bin/env python3
r"""Drift guard for the index markup in tex/*/ch0N.tex.

Every defined term in the notes is written with \term, \termja or \termen, and
those three are what put it in the 索引. The rules they answer to are
docs/index-convention.md; this file checks the two of them that are mechanical.

**Why a test and not a hook.** `.claude/hooks/guard-edits.sh` sees only what
Claude writes, and the terms in these chapters are written by the repo owner.
A hook would guard the half of the authorship that is not doing the writing.
This runs in the gate that already exists (`/git`) and the CI step that already
exists (`update-readme.yml`), against whoever typed the line.

What is checked:

- **No chapter contains `\textbf`.** After the conversion that introduced the
  index there are none left: bold in a chapter *was* the term-defining markup,
  every occurrence of it became a `\term`, and so the correct count is zero and
  stays zero. That exactness is the whole value — "bold means a defined term"
  is otherwise a convention with nothing behind it, and a term written
  `\textbf{}` out of habit is missing from the index with nothing to say so.
  `\textbf` elsewhere is untouched: `tex/*/bibliography.tex` sets a journal
  volume in bold, and `tex/preamble.tex` and `tex/index.ist` use it for the
  index's own headings.
- **Every reading is hiragana.** upmendex collates the reading, not the
  headword, so a reading typed in kanji or katakana is a sort key that sorts
  by something other than the sound — the failure the required argument exists
  to prevent, arriving by a different door. Long vowel marks are allowed;
  `docs/index-convention.md` `## The reading` is the rule.
- **Every English sort key is ASCII.** The optional argument of `\term` exists
  because a gloss carrying mathematics cannot sort itself; a key that carries
  the mathematics too has not solved anything.

What is deliberately not checked: whether a reading is the *right* reading.
けん for 圏 and きり for 錐 are both hiragana, and only one of them is correct.
Nothing here can tell them apart -- that is what the approval table at
conversion time was for.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "tex"

# Hiragana, plus the long vowel mark a reading may legitimately carry (ラムダ ->
# らむだ leaves no ー, but ベクトル空間 -> べくとるくうかん and サーベイ do).
READING = re.compile(r"^[\u3041-\u309fー]+$")


def chapters() -> list[Path]:
    """Every chapter source in the repo, in a stable order."""
    return sorted(TEX.glob("*/ch*.tex"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def arguments(text: str, macro: str) -> list[tuple[int, list[str], str | None]]:
    r"""Yield (line number, mandatory arguments, optional argument) per call.

    Brace-balanced rather than regex-matched: a term's arguments hold
    mathematics, and `$C^{\infty}$級多様体` closes a brace it did not open as
    far as a regex is concerned.
    """
    found = []
    for match in re.finditer(re.escape("\\" + macro) + r"(?=[\[{])", text):
        index = match.end()
        optional = None
        if text[index] == "[":
            close = text.index("]", index)
            optional, index = text[index + 1 : close], close + 1
        args = []
        while index < len(text) and text[index] == "{":
            depth, start = 0, index
            while index < len(text):
                if text[index] == "{":
                    depth += 1
                elif text[index] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                index += 1
            args.append(text[start + 1 : index])
            index += 1
        found.append((text.count("\n", 0, match.start()) + 1, args, optional))
    return found


class TestChapterMarkup(unittest.TestCase):
    """The chapters, as they are on disk."""

    def test_there_are_chapters_to_check(self):
        """A glob that matches nothing passes every test below it."""
        self.assertTrue(chapters())

    def test_no_chapter_uses_textbf(self):
        for path in chapters():
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"\\textbf\b", text):
                line = text.count("\n", 0, match.start()) + 1
                self.fail(
                    f"{rel(path)}:{line} uses \\textbf. Bold in a chapter is a "
                    f"defined term: write \\term{{よみ}}{{和文}}{{英文}}, or "
                    f"\\termja / \\termen. See docs/index-convention.md."
                )

    def test_every_reading_is_hiragana(self):
        for path in chapters():
            text = path.read_text(encoding="utf-8")
            for macro in ("term", "termja"):
                for line, args, _ in arguments(text, macro):
                    self.assertTrue(args, f"{rel(path)}:{line} \\{macro} has no arguments")
                    self.assertRegex(
                        args[0],
                        READING,
                        f"{rel(path)}:{line} \\{macro} has the reading {args[0]!r}, "
                        f"which is not hiragana. upmendex sorts the reading, so "
                        f"one written any other way sorts by something other than "
                        f"the sound. See docs/index-convention.md.",
                    )

    def test_every_english_sort_key_is_ascii(self):
        for path in chapters():
            text = path.read_text(encoding="utf-8")
            for line, _, optional in arguments(text, "term"):
                if optional is None:
                    continue
                self.assertTrue(
                    optional.isascii() and "$" not in optional,
                    f"{rel(path)}:{line} has the English sort key {optional!r}. "
                    f"It exists to give a gloss carrying mathematics something "
                    f"sortable; it has to be the spelled-out form, e.g. "
                    f"lambda-term for $\\lambda$-term.",
                )

    def test_every_call_has_the_right_number_of_arguments(self):
        """A missing reading is a compile error; a missing gloss is not.

        `\\term{けん}{圏}` reads as `\\term` followed by a stray brace group and
        can typeset without complaint, so the arity nothing else checks is
        checked here.
        """
        for path in chapters():
            text = path.read_text(encoding="utf-8")
            for macro, arity in (("term", 3), ("termja", 2), ("termen", 1)):
                for line, args, _ in arguments(text, macro):
                    self.assertGreaterEqual(
                        len(args),
                        arity,
                        f"{rel(path)}:{line} \\{macro} takes {arity} arguments, "
                        f"found {len(args)}: {args}",
                    )


if __name__ == "__main__":
    unittest.main()
