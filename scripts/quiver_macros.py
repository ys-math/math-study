#!/usr/bin/env python3
r"""Publish the preamble's macros to the gist quiver loads them from.

quiver (https://q.uiver.app) renders labels with KaTeX, which knows nothing of
`tex/preamble.tex`, so a draft written with `\Hom` or `\colim` shows red until
quiver is given the definitions. It takes them from a URL: the macros pane, or
`&macro_url=` on the address, which quiver then keeps in every link it
exports. That URL is the raw file of one public gist, `GIST_ID` below.

**Why not point quiver at the preamble itself.** quiver reads one definition
per line and requires the line to end at the definition's closing brace, so
every operator with a trailing `% comment` (`\Res`, `\Im`, `\OO`, `\colim`, ...)
would be dropped without a word. This script strips the comments and keeps only
the lines quiver can read: `\newcommand`, `\renewcommand`,
`\DeclareMathOperator[*]` and `\definecolor`, minus the document macros in
`NOT_MATH`, which mean nothing in a diagram.

**The gist is a copy, and nothing syncs it.** After changing a macro in the
preamble, rerun with `--push`; until then quiver renders the old set. The
preamble is the source; never edit the gist by hand.

Usage, from the repo root:

    python scripts/quiver_macros.py          # print the macro file
    python scripts/quiver_macros.py --push   # overwrite the gist with it (needs `gh`)
    python scripts/quiver_macros.py --draft  # a blank quiver diagram with the macros loaded

`--draft` carries an empty `q=` because quiver ignores `macro_url` on an
address without one.

Run the tests from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

PREAMBLE = Path("tex/preamble.tex")
GIST_ID = "3ce50ecce6044bd5f2629781f2a56d8e"
FILENAME = "quiver-macros.tex"
MACRO_URL = f"https://gist.githubusercontent.com/ys-math/{GIST_ID}/raw/{FILENAME}"
EMPTY_DIAGRAM = "WzAsMF0="  # base64 of [0,0]: format version 0, no objects

HEADER = """\
% SPDX-License-Identifier: MIT
% Generated from tex/preamble.tex of https://github.com/ys-math/math-study
% by scripts/quiver_macros.py. Edit the preamble and rerun; not this file.
"""

# quiver's own patterns (src/ui.mjs, `load_macros`), so the file holds exactly
# the lines quiver will read.
NEWCOMMAND = re.compile(
    r"^\\((?:re)?newcommand|DeclareMathOperator)(\*?)\{?\\([a-zA-Z]+)\}?(?:\[(\d)\])?\{(.*)\}$"
)
BRACKETS = re.compile(r"^\\((re)?newcommand|DeclareMathOperator)\*?(\{\\[a-zA-Z]+\}|\\[a-zA-Z]+[^\}])")
DEFINECOLOR = re.compile(
    r"^\\definecolor\{([a-zA-Z0-9\-]+)\}\{(rgb|RGB|gray|HTML)\}"
    r"\{((?:\d+(?:\.\d+)?)(?:,(?:\d+(?:\.\d+)?))*|[a-fA-F\d]{6})\}$"
)
COMMENT = re.compile(r"(?<!\\)%.*$")

# Macros that typeset the document rather than mathematics.
NOT_MATH = {
    "DocSlug", "GitHub", "DocAuthorName", "DocAuthor", "DocRepo",
    "DocCompiler", "DocClass", "proofname", "qedsymbol",
}


def extract(preamble: str) -> list[str]:
    """The preamble's definitions quiver can read, comments stripped, in order."""
    kept = []
    for line in preamble.splitlines():
        line = COMMENT.sub("", line).strip()
        m = NEWCOMMAND.match(line)
        if m and BRACKETS.match(line):
            if m.group(3) not in NOT_MATH:
                kept.append(line)
        elif DEFINECOLOR.match(re.sub(r"\s", "", line)):
            kept.append(line)
    return kept


def render(preamble: str) -> str:
    return HEADER + "\n".join(extract(preamble)) + "\n"


def draft_url() -> str:
    return f"https://q.uiver.app/#q={EMPTY_DIAGRAM}&macro_url={urllib.parse.quote(MACRO_URL, safe='')}"


def push(text: str) -> None:
    body = json.dumps({"files": {FILENAME: {"content": text}}})
    subprocess.run(
        ["gh", "api", "--method", "PATCH", f"gists/{GIST_ID}", "--input", "-", "--silent"],
        input=body, text=True, check=True,
    )


def main(argv: list[str]) -> int:
    if argv not in ([], ["--push"], ["--draft"]):
        print("usage: python scripts/quiver_macros.py [--push | --draft]", file=sys.stderr)
        return 2
    if argv == ["--draft"]:
        print(draft_url())
        return 0
    preamble = PREAMBLE.read_text(encoding="utf-8")
    text = render(preamble)
    if argv == ["--push"]:
        try:
            push(text)
        except (OSError, subprocess.CalledProcessError) as err:
            print(f"quiver_macros.py: could not update gist {GIST_ID}: {err}", file=sys.stderr)
            return 1
        print(f"{len(extract(preamble))} definitions -> {MACRO_URL}")
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
