#!/usr/bin/env python3
r"""Regenerate the per-topic text meter in README.md.

One topic is one directory in tex/; its size is the number of characters in its
chapter sources, and its share is that size over the sum across every topic. The
block is a fenced code block rather than a table because a meter nobody can
compare against its neighbours is not doing its job: the bars only line up in a
monospace context, which a fence guarantees and a markdown table does not.

What is counted, and why it is only this:

- `ch*.tex`, not `bibliography.tex` and not `main.tex`. The chapters are the
  mathematics. A bibliography would let a topic show progress it has not made,
  and `main.tex` is generated boilerplate whose identical floor under every
  topic would flatten the very differences the meter exists to show.
- Comment lines are dropped, so the two-line SPDX-and-`!TEX root` header every
  chapter carries does not read as content. A topic with no prose measures 0.
- LaTeX markup is *not* stripped. In these notes the mathematics is written in
  math mode, so discounting `$\cod(g \circ f)$` would systematically undercount
  the densest chapters. The caption in README.md says "characters of source" for
  exactly this reason -- the number is honest about being a source measurement.

Bars carry eighth-block resolution and a floor of one eighth for any nonzero
topic, so an empty bar means "nothing written" and nothing else. That
distinction is load-bearing here: of the topics on disk, several are stubs and
several are merely just-started, and at whole-cell resolution they render
identically.

Rows are sorted by size, descending -- the one size-ordered list in the repo,
which `docs/naming-convention.md` notes as the exception to its otherwise
alphabetical ordering. The `total` row is pinned below the sort.

Idempotent: running it twice with no repo change leaves the file byte-identical.

Run from the repo root:  python scripts/generate_text_meter.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from readme_block import update_readme

BEGIN_MARKER = "<!-- BEGIN TEXT METER -->"
END_MARKER = "<!-- END TEXT METER -->"
README = Path("README.md")
TEX_DIR = Path("tex")

BAR_WIDTH = 20
#: Left-to-right eighths of a filled cell; PARTIALS[n - 1] is n/8 of a cell.
PARTIALS = "▏▎▍▌▋▊▉█"
FULL = "█"
EMPTY = "░"
TOTAL_LABEL = "total"


def chapter_files() -> list[Path]:
    """Every git-tracked tex/<topic>/ch*.tex, grouped later by topic.

    Uses git rather than a glob so an untracked local scratch directory cannot
    contribute characters, matching generate_pdf_links.py.
    """
    out = subprocess.run(
        ["git", "ls-files", f"{TEX_DIR}/*/ch*.tex"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    paths = [Path(line) for line in out.splitlines() if line]
    # Chapters are flat inside a topic: "tex/manifold/ch01.tex", never deeper.
    return sorted(p for p in paths if len(p.parts) == 3)


def topic_dirs() -> list[str]:
    """Every topic that owns a git-tracked main.tex.

    Derived from main.tex rather than from the chapters so that a topic whose
    only chapter is an empty stub still gets a row -- a 0.0% row is the honest
    answer for a topic that exists and has nothing in it, and dropping it would
    make the meter silently disagree with the PDF list above it.
    """
    out = subprocess.run(
        ["git", "ls-files", f"{TEX_DIR}/*/main.tex"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    paths = [Path(line) for line in out.splitlines() if line]
    return sorted(p.parts[1] for p in paths if len(p.parts) == 3)


def count_characters(path: Path) -> int:
    r"""Characters of content in one chapter file.

    A line whose first non-whitespace character is `%` is a comment and counts
    for nothing; every other line contributes its stripped length, so trailing
    whitespace and the indentation of a nested `itemize` do not inflate a topic.
    """
    total = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        total += len(stripped)
    return total


def topic_sizes() -> dict[str, int]:
    """Map every topic to its chapter-character count, zero included."""
    sizes = {topic: 0 for topic in topic_dirs()}
    for path in chapter_files():
        topic = path.parts[1]
        # A chapter under a topic with no main.tex is not a topic; skip it
        # rather than inventing a row the PDF list will never have.
        if topic in sizes:
            sizes[topic] += count_characters(path)
    return sizes


def bar(fraction: float, width: int = BAR_WIDTH) -> str:
    """Render `fraction` of `width` cells, with eighth-of-a-cell resolution.

    Any nonzero fraction gets at least one eighth. Without that floor a topic
    holding a single real sentence renders identically to one holding nothing,
    which is the one distinction this meter must not blur.
    """
    eighths = round(fraction * width * 8)
    if fraction > 0:
        eighths = max(eighths, 1)
    eighths = min(eighths, width * 8)

    full, remainder = divmod(eighths, 8)
    filled = FULL * full + (PARTIALS[remainder - 1] if remainder else "")
    return filled + EMPTY * (width - len(filled))


def build_body(sizes: dict[str, int]) -> str:
    """The fenced code block, bars and all."""
    total = sum(sizes.values())
    # Descending by size; alphabetical among ties, so the two 0.0% stubs keep a
    # stable order and the block does not churn between runs.
    rows = sorted(sizes.items(), key=lambda item: (-item[1], item[0]))

    label_width = max(len(topic) for topic in sizes) if sizes else len(TOTAL_LABEL)
    label_width = max(label_width, len(TOTAL_LABEL))
    count_width = max(len(f"{size:,}") for size in [*sizes.values(), total])

    # Everything left of the count column: label, gap, bar, gap, "100.0%", gap.
    # Derived once so the total row and its rule cannot drift from the data rows.
    share_width = len(f"{100.0:5.1f}%")
    prefix_width = label_width + 2 + BAR_WIDTH + 2 + share_width + 2

    lines = ["```"]
    for topic, size in rows:
        share = size / total if total else 0.0
        lines.append(
            f"{topic:<{label_width}}  {bar(share)}  "
            f"{100 * share:5.1f}%  {size:>{count_width},}"
        )

    lines.append(" " * prefix_width + "-" * count_width)
    lines.append(f"{TOTAL_LABEL:<{prefix_width}}{total:>{count_width},}")
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    sizes = topic_sizes()
    if not sizes:
        sys.exit(f"No {TEX_DIR}/*/main.tex found; run from the repo root.")

    update_readme(README, BEGIN_MARKER, END_MARKER, build_body(sizes), "text meter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
