#!/usr/bin/env python3
r"""Check every tex/<topic>/bibliography.tex against docs/bib-convention.md.

The convention fixes one grammar for every entry, of every kind, in every
language: three lines, ``<author>,`` / ``<title>,`` / ``<locator>.``, where only
the third differs between a book, an article, a preprint and a web resource.
That is checkable, and until this script existed nothing checked it -- which is
how one book entry came to carry a place of publication and another not, and how
a straight ``"`` (which jlreq/LuaLaTeX typesets as a *closing* quote at both
ends) sat in a shipped PDF.

**It reads structure and nothing else.** Whether the year is right, whether the
publisher is right, whether the thing called a book is a book, whether the
author's initial is the one they publish under -- an entry wrong in every one of
those ways passes here without a word. A citation is a factual claim about a
physical object, and no script can see the object. The guarantee stops at the
shape of the sentence making the claim.

So the failure modes to keep in mind when reading a green run:

* a well-formed entry naming a book that does not exist,
* a key whose surname is not the author's,
* a locator in the shape of a book that describes an article.

Each is invisible here and visible to a reader. That is the division of labour
this script is built around, not a gap in it.

Run from the repo root:

    python scripts/check_bibliography.py            # every topic
    python scripts/check_bibliography.py topology   # one
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

__all__ = ["Problem", "check_file", "check_text", "entries_of"]

ROOT = Path(__file__).resolve().parent.parent
TEX_DIR = ROOT / "tex"
BIBLIOGRAPHY = "bibliography.tex"

SPDX = "% SPDX-License-Identifier: CC-BY-NC-ND-4.0"

# `bib: ` then a body with no whitespace. docs/bib-convention.md fixes the one
# space after the colon; the body is a surname, a surname plus a year, or a site
# name plus a page word, and this deliberately does not try to tell them apart.
KEY = re.compile(r"^bib: (\S+)$")

BIBITEM = re.compile(r"^\\bibitem\{([^}]*)\}$")

BEGIN = re.compile(r"^\\begin\{thebibliography\}\{(\d+)\}$")

# The four sanctioned openings of line 2: italic and ``...'' for Latin script,
# 『』 and 「」 for Japanese. A straight `"` matches none of them, which is the
# point -- that is the check that keeps the closing-quote bug from returning.
TITLE_MARKS = ("\\textit{", "``", "『", "「")

# Latin-script markup wrapped around Japanese is the silent one: \textit{} is
# inert on CJK, so under jlreq the title renders upright and the emphasis is
# absent from the PDF while the source looks right. 『』 and 「」 are what carry
# it, which is why the convention forbids the italic rather than tolerating it.
LATIN_MARKS = ("\\textit{", "``")
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")


class Problem(NamedTuple):
    """One failure, addressed to a line so the message can be pasted into an editor."""

    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def entries_of(lines: list[str]) -> list[tuple[int, str, list[str]]]:
    r"""Split the file into (line number of the \bibitem, key, following lines).

    An entry runs from its ``\bibitem`` to the next blank line, ``\bibitem`` or
    ``\end{thebibliography}``. The grammar says that block is three lines, but
    finding the block and judging its length are separate jobs: this returns
    whatever is there so that check_text can say "four lines" rather than
    failing to parse.
    """
    entries: list[tuple[int, str, list[str]]] = []
    for index, line in enumerate(lines):
        match = BIBITEM.match(line.strip())
        if not match:
            continue
        body: list[str] = []
        for following in lines[index + 1 :]:
            stripped = following.strip()
            if not stripped or BIBITEM.match(stripped) or stripped.startswith(r"\end{"):
                break
            body.append(stripped)
        entries.append((index + 1, match.group(1), body))
    return entries


def check_text(path: str, text: str) -> list[Problem]:
    """Every structural problem in one bibliography.tex, in line order."""
    problems: list[Problem] = []
    lines = text.splitlines()

    if not lines or lines[0].rstrip() != SPDX:
        # The root LICENSE is MIT, so an unmarked file reads as MIT while the
        # notes it belongs to are CC BY-NC-ND. guard-edits.sh blocks a write
        # without this; a hand edit that strips it reaches here instead.
        problems.append(Problem(path, 1, f"line 1 must be {SPDX!r}"))

    entries = entries_of(lines)

    for number, key, body in entries:
        match = KEY.match(key)
        if not match:
            problems.append(
                Problem(path, number, f"key {key!r} is not 'bib: ' plus a spaceless body")
            )

        if len(body) != 3:
            problems.append(
                Problem(
                    path,
                    number,
                    f"entry has {len(body)} lines, not 3 "
                    "(author, title, locator -- docs/bib-convention.md '## The grammar')",
                )
            )
            continue

        author, title, locator = body
        for offset, (line, ending, role) in enumerate(
            ((author, ",", "author"), (title, ",", "title"), (locator, ".", "locator"))
        ):
            if not line.endswith(ending):
                problems.append(
                    Problem(path, number + 1 + offset, f"{role} line must end in {ending!r}")
                )

        if not title.startswith(TITLE_MARKS):
            problems.append(
                Problem(
                    path,
                    number + 2,
                    "title must open with \\textit{, ``, 『 or 「 -- a straight "
                    '" typesets as a closing quote at both ends under jlreq',
                )
            )
        elif title.startswith(LATIN_MARKS) and CJK.search(title):
            problems.append(
                Problem(
                    path,
                    number + 2,
                    "a Japanese title takes 『』 or 「」, not \\textit{} or ``'' -- "
                    "the italic is inert on CJK and the PDF loses it silently",
                )
            )

    bodies = [KEY.match(key).group(1) if KEY.match(key) else key for _, key, _ in entries]
    for (number, key, _), previous, current in zip(entries[1:], bodies, bodies[1:]):
        # Case-insensitive: `bib: nLab` belongs before `bib: Riehl`, and a byte
        # comparison puts it after, lowercase n sorting above uppercase R.
        if current.casefold() < previous.casefold():
            problems.append(
                Problem(path, number, f"{key!r} sorts before the entry above it")
            )

    for index, line in enumerate(lines):
        match = BEGIN.match(line.strip())
        if not match:
            continue
        # The argument is the widest *label*, not a capacity: it sets the
        # indentation the numbers are typeset into. Too narrow and nothing
        # errors -- the page just looks off, which is why it is checked here.
        width, count = len(match.group(1)), len(entries)
        if width < len(str(count)):
            problems.append(
                Problem(
                    path,
                    index + 1,
                    f"thebibliography{{{match.group(1)}}} is too narrow for {count} entries",
                )
            )

    return sorted(problems, key=lambda problem: problem.line)


def check_file(path: Path) -> list[Problem]:
    relative = path.relative_to(ROOT).as_posix()
    return check_text(relative, path.read_text(encoding="utf-8"))


def bibliographies(topic: str | None) -> list[Path]:
    if topic is not None:
        return [TEX_DIR / topic / BIBLIOGRAPHY]
    return sorted(TEX_DIR.glob(f"*/{BIBLIOGRAPHY}"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check bibliography.tex against docs/bib-convention.md.",
    )
    parser.add_argument(
        "topic",
        nargs="?",
        help="a topic slug; omit to check every topic that has a bibliography",
    )
    args = parser.parse_args()

    if not TEX_DIR.is_dir():
        sys.exit(f"{TEX_DIR} not found; run from the repo root.")

    paths = bibliographies(args.topic)
    if args.topic is not None and not paths[0].is_file():
        # Most topics have no bibliography and that is not an error; being asked
        # about a named one that does not exist is, since it means a typo.
        sys.exit(f"{paths[0].relative_to(ROOT).as_posix()} does not exist.")

    problems = [problem for path in paths for problem in check_file(path)]
    for problem in problems:
        print(problem, file=sys.stderr)

    if problems:
        print(
            f"\n{len(problems)} problem(s). The rules are docs/bib-convention.md.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(paths)} bibliograph{'y' if len(paths) == 1 else 'ies'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
