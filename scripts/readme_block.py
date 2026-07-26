#!/usr/bin/env python3
"""Rewrite a marker-delimited block inside a Markdown file.

Shared by the README generators (scripts/generate_tree.py,
scripts/generate_pdf_links.py). Each generator owns one pair of HTML-comment
markers and hands over the body it wants between them; writing is idempotent, so
running a generator twice with no repo change leaves the file byte-identical.
"""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = ["replace_block", "update_readme"]


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


def update_readme(path: Path, begin: str, end: str, body: str, label: str) -> bool:
    """Rewrite the block in `path`, only touching the file if it changed.

    `label` names the block in the status line, e.g. "tree". Returns True if the
    file was written.
    """
    if not path.exists():
        sys.exit(f"{path} not found; run from the repo root.")

    text = path.read_text(encoding="utf-8")
    new_text = replace_block(text, begin, end, body)
    if new_text == text:
        print(f"{path} {label} already up to date.")
        return False

    path.write_text(new_text, encoding="utf-8")
    print(f"{path} {label} updated.")
    return True
