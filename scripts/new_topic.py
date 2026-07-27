#!/usr/bin/env python3
r"""Create the directory for a new topic: tex/<topic>/main.tex and its ch01.tex.

Every topic in this repo has the same two-file skeleton, and its main.tex is
byte-identical to every other one apart from \DocTitle and the tail of
\TexRepo. Copying an existing topic by hand is easy but easy to get subtly
wrong, and two of the mistakes are only caught much later:

* The topic name is interpolated into a regex in .github/workflows/build-pdf.yml,
  a filename in pdf/, and a URL in \TexRepo, so it has to stay plain.
* \DocTitle becomes the README link label via scripts/latex_unicode.py, which
  refuses to guess at LaTeX it does not know; an unrenderable title breaks
  scripts/generate_pdf_links.py in CI, days after the topic was created.

Both are checked here, before anything is written, and the rendered label is
echoed so the README text is visible at creation time.

Nothing is staged, committed or regenerated: .github/workflows/update-readme.yml
owns the generated README blocks and rewrites them on the next push.

Run from the repo root:  python scripts/new_topic.py sheaf_theory --title 層論
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from latex_unicode import UnsupportedLatex, render

__all__ = ["InvalidTopic", "render_main", "validate_title", "validate_topic"]

# Plain enough to be safe as a regex fragment, a filename and a URL segment.
TOPIC_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

# Every topic lives here, alongside the preamble and colophon they all \input.
TEX_DIR = Path("tex")

# Names that must never become a topic. "latex_out" is a build directory that
# can appear inside tex/; "pdf" and "scripts" no longer sit next to the topics,
# but a tex/pdf or tex/scripts would still read as a twin of the root one.
RESERVED = frozenset({"pdf", "scripts", "latex_out"})

REPO_TREE_URL = f"https://github.com/ys-math/math-study/tree/main/{TEX_DIR}"

CHAPTER = "ch01.tex"

# A file that only exists at this path in the repo, used to check where we are
# running.
ROOT_MARKER = TEX_DIR / "preamble.tex"

# Placeholders are @-delimited because LaTeX uses both {} and $, which rules out
# str.format and string.Template. Keep the body byte-identical to the existing
# topics: no trailing newline after \end{document}.
MAIN_TEMPLATE = r"""\documentclass[uplatex,dvipdfmx]{jsarticle}

\input{../preamble.tex}

\newcommand{\DocTitle}{@DOCTITLE@}
\newcommand{\TexRepo}{@TEXREPO@}

\title{\DocTitle}
\date{\today}
\author{\DocAuthor}

\begin{document}
\maketitle
\newpage
\tableofcontents
\newpage
\input{ch01.tex}

\newpage
\input{../colophon.tex}

\end{document}"""


class InvalidTopic(ValueError):
    """Raised when a topic name cannot be used as a directory name."""


def validate_topic(topic: str, taken: object = ()) -> None:
    """Check `topic` as a directory name, given the `taken` names in tex/.

    `taken` is anything supporting `in`; pass the existing entries of tex/ so an
    occupied name is refused before any file is written.
    """
    if not TOPIC_PATTERN.match(topic):
        raise InvalidTopic(
            f"invalid topic name {topic!r}: use lowercase letters, digits and "
            f"underscores, starting with a letter, e.g. 'sheaf_theory'."
        )
    if topic in RESERVED:
        raise InvalidTopic(f"{topic!r} is reserved for something that is not a topic.")
    if topic in taken:
        raise InvalidTopic(
            f"{topic!r} already exists; this script only creates new topics."
        )


def validate_title(title: str) -> str:
    r"""Return the README link label for `title`, or raise UnsupportedLatex.

    Mirrors what scripts/generate_pdf_links.py will do with the \DocTitle later,
    so a title that would break the README is rejected up front.
    """
    label = render(title)
    if not label.strip():
        raise UnsupportedLatex(f"renders to an empty label from {title!r}")
    return label


def render_main(topic: str, title: str) -> str:
    r"""Return the main.tex source for `topic`, titled `title`."""
    return MAIN_TEMPLATE.replace("@DOCTITLE@", title).replace(
        "@TEXREPO@", f"{REPO_TREE_URL}/{topic}"
    )


def tex_dir_names() -> list[str]:
    return [path.name for path in TEX_DIR.iterdir()]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new topic directory with main.tex and ch01.tex.",
    )
    parser.add_argument(
        "topic",
        help="directory name, e.g. sheaf_theory (lowercase, digits, underscores)",
    )
    parser.add_argument(
        "--title",
        required=True,
        help=r"the \DocTitle, e.g. 層論; also becomes the README link label",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()

    if not ROOT_MARKER.is_file():
        sys.exit(f"{ROOT_MARKER} not found; run from the repo root.")

    try:
        validate_topic(args.topic, tex_dir_names())
    except InvalidTopic as error:
        sys.exit(str(error))

    try:
        label = validate_title(args.title)
    except UnsupportedLatex as error:
        sys.exit(
            f"\\DocTitle: {error} in {args.title!r}\n"
            f"  -> add it to SYMBOLS in scripts/latex_unicode.py, or reword the title."
        )

    directory = TEX_DIR / args.topic
    directory.mkdir()
    (directory / "main.tex").write_text(
        render_main(args.topic, args.title), encoding="utf-8"
    )
    (directory / CHAPTER).write_text("", encoding="utf-8")

    print(f"Created {directory}/ (README label: {label})")
    print(f"next: write {directory / CHAPTER}, then git add {directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
