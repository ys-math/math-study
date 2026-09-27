#!/usr/bin/env python3
"""Rewrite a marker-delimited block inside the READMEs.

Shared by the README generators (scripts/generate_tree.py,
scripts/generate_pdf_links.py, scripts/generate_text_meter.py). Each generator
owns one pair of HTML-comment markers and hands over the body it wants between
them; writing is idempotent, so running a generator twice with no repo change
leaves every file byte-identical.

There are two READMEs, one per language, and each carries every block: the
bodies are language-neutral (the PDF labels are the Japanese \\DocTitle either
way), so both get the same bytes. `update_readmes` checks every file for its
markers before writing any, so a README that lost one fails the run without
leaving the other half-updated.
"""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = ["READMES", "replace_block", "update_readmes"]

READMES = (Path("README.md"), Path("README.ja.md"))


def replace_block(text: str, begin: str, end: str, body: str) -> str:
    """Return `text` with everything between `begin` and `end` replaced by `body`.

    The markers themselves are kept. Exits with a message if either marker is
    missing or they appear out of order.
    """
    start = text.find(begin)
    stop = text.find(end)
    if start == -1 or stop == -1 or stop < start:
        sys.exit(f"Could not find markers {begin!r} / {end!r} in the file.")
    stop += len(end)
    return text[:start] + f"{begin}\n{body}\n{end}" + text[stop:]


def update_readmes(
    begin: str, end: str, body: str, label: str, paths: tuple[Path, ...] = READMES
) -> list[Path]:
    """Rewrite the block in every file of `paths`, touching only those that change.

    `label` names the block in the status lines, e.g. "tree". Returns the files
    that were written.
    """
    for path in paths:
        if not path.exists():
            sys.exit(f"{path} not found; run from the repo root.")

    rewritten = {}
    for path in paths:
        text = path.read_text(encoding="utf-8")
        try:
            rewritten[path] = (text, replace_block(text, begin, end, body))
        except SystemExit as exc:
            sys.exit(f"{path}: {exc}")

    written = []
    for path, (text, new_text) in rewritten.items():
        if new_text == text:
            print(f"{path} {label} already up to date.")
            continue
        path.write_text(new_text, encoding="utf-8")
        print(f"{path} {label} updated.")
        written.append(path)
    return written
