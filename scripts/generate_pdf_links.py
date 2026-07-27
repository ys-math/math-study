#!/usr/bin/env python3
"""Regenerate the list of PDF links in README.md.

One topic is one directory in tex/ owning a main.tex; its display name is the
`\\DocTitle` declared in that file, rendered to Markdown-safe text, and its link
target is the artifact pdf/<topic>.pdf that .github/workflows/build-pdf.yml
compiles. Idempotent: running it twice with no repo change leaves the file
byte-identical.

The list is derived from the .tex sources rather than from the contents of pdf/,
because build-pdf.yml commits the PDFs as github-actions[bot] and bot pushes do
not trigger further workflows — a pdf/-derived list would go stale until the next
human push.

Run from the repo root:  python scripts/generate_pdf_links.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from latex_unicode import UnsupportedLatex, render
from readme_block import update_readme

BEGIN_MARKER = "<!-- BEGIN PDF LINKS -->"
END_MARKER = "<!-- END PDF LINKS -->"
README = Path("README.md")
PDF_DIR = Path("pdf")
TEX_DIR = Path("tex")
TITLE_MACRO = r"\newcommand{\DocTitle}"


def topic_files() -> list[Path]:
    """Every git-tracked tex/<topic>/main.tex, sorted by topic directory name.

    Uses git rather than a glob so an untracked local scratch directory cannot
    add a link.
    """
    out = subprocess.run(
        ["git", "ls-files", f"{TEX_DIR}/*/main.tex"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    paths = [Path(line) for line in out.splitlines() if line]
    # Topics are flat inside tex/: "tex/manifold/main.tex", not "tex/a/b/main.tex".
    return sorted((p for p in paths if len(p.parts) == 3), key=topic_name)


def topic_name(path: Path) -> str:
    """The topic a tex/<topic>/main.tex belongs to; also its pdf/ basename."""
    return path.parts[1]


def extract_title(path: Path) -> str:
    r"""Return the raw LaTeX argument of \newcommand{\DocTitle}{...} in `path`."""
    text = path.read_text(encoding="utf-8")

    occurrences = []
    search_from = 0
    while (found := text.find(TITLE_MACRO, search_from)) != -1:
        occurrences.append(found)
        search_from = found + len(TITLE_MACRO)

    if not occurrences:
        sys.exit(f"{path}: no {TITLE_MACRO}{{...}} declaration found.")
    if len(occurrences) > 1:
        sys.exit(f"{path}: {TITLE_MACRO} is declared {len(occurrences)} times.")

    start = occurrences[0] + len(TITLE_MACRO)
    if start >= len(text) or text[start] != "{":
        sys.exit(f"{path}: {TITLE_MACRO} is not followed by a braced argument.")

    depth = 0
    for position in range(start, len(text)):
        if text[position] == "{":
            depth += 1
        elif text[position] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : position]
    sys.exit(f"{path}: unbalanced braces in the {TITLE_MACRO} argument.")


def link_label(path: Path) -> str:
    """Render the topic's \\DocTitle as the Markdown link label."""
    title = extract_title(path)
    try:
        label = render(title)
    except UnsupportedLatex as error:
        sys.exit(
            f"{path} \\DocTitle: {error} in {title!r}\n"
            f"  -> add it to SYMBOLS in scripts/latex_unicode.py, or reword the title."
        )
    if not label.strip():
        sys.exit(f"{path} \\DocTitle: renders to an empty label from {title!r}")
    return label


def warn_about_pdfs(topics: list[str]) -> None:
    """Flag links that do not resolve yet, and PDFs no topic claims."""
    for topic in topics:
        if not (PDF_DIR / f"{topic}.pdf").exists():
            print(
                f"warning: {PDF_DIR}/{topic}.pdf does not exist yet; "
                "the link will 404 until build-pdf.yml compiles it.",
                file=sys.stderr,
            )

    if not PDF_DIR.is_dir():
        return
    known = set(topics)
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        if pdf.stem not in known:
            print(
                f"warning: {pdf} has no matching {TEX_DIR}/{pdf.stem}/main.tex; "
                "it is an orphan and nothing links to it.",
                file=sys.stderr,
            )


def build_body(paths: list[Path]) -> str:
    return "\n".join(
        f"* [{link_label(path)}](./{PDF_DIR}/{topic_name(path)}.pdf)" for path in paths
    )


def main() -> int:
    paths = topic_files()
    if not paths:
        sys.exit(f"No {TEX_DIR}/*/main.tex found; run from the repo root.")

    body = build_body(paths)
    warn_about_pdfs([topic_name(path) for path in paths])
    update_readme(README, BEGIN_MARKER, END_MARKER, body, "PDF links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
