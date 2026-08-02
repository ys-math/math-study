#!/usr/bin/env python3
"""Regenerate the directory-structure tree in README.md.

Reads the set of git-tracked files, applies a prune rule, renders a
box-drawing tree, and rewrites the block between the marker comments in
README.md. Idempotent: running it twice with no repo change leaves the
file byte-identical.

Run from the repo root:  python scripts/generate_tree.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from readme_block import update_readme

ROOT_LABEL = "math-study/"
BEGIN_MARKER = "<!-- BEGIN TREE -->"
END_MARKER = "<!-- END TREE -->"
README = Path("README.md")

# Top-level directories pruned entirely from the tree.
PRUNED_DIRS = {"pdf", ".github"}

# Directories rendered as one collapsed entry, contents and all. The Lean
# library gains a file per proof session and would turn this tree into a file
# listing; the tree exists to orient a reader, and lean/'s build files — which
# stay visible, being outside the collapsed prefix — already say what kind of
# thing is inside. Prefixes are matched whole-segment, so a sibling named
# lean/Mathlib would not be swallowed by "lean/Math".
COLLAPSED_DIRS = ("lean/Math",)


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def keep(path: str) -> bool:
    """Apply the prune rule to a repo-relative path."""
    parts = path.split("/")
    top = parts[0]
    if top in PRUNED_DIRS:
        return False
    # Drop any top-level dotfile / dot-directory (.gitignore, .latexmkrc, ...).
    if top.startswith("."):
        return False
    return True


def collapse(path: str) -> tuple[str, bool]:
    """Return what to render for `path`, and whether it was collapsed.

    A path inside a COLLAPSED_DIRS prefix renders as the prefix itself; anything
    else renders as itself. The prefix is only ever matched with the separator
    attached, so it never matches the collapsed directory's own siblings.
    """
    for prefix in COLLAPSED_DIRS:
        if path.startswith(prefix + "/"):
            return prefix, True
    return path, False


def build_tree(paths: list[str]) -> dict:
    """Nested dict; a file maps to None, a directory maps to a sub-dict."""
    tree: dict = {}
    for path in paths:
        rendered, collapsed = collapse(path)
        node = tree
        parts = rendered.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        # Leaf. A collapsed prefix is a directory with nothing under it, so it
        # maps to an empty dict and render() gives it a trailing slash and no
        # children; anything else is a file. Don't clobber a dir sharing the name.
        node.setdefault(parts[-1], {} if collapsed else None)
    return tree


def sort_key(item: tuple[str, object]) -> tuple[int, str]:
    name, child = item
    # Directories (dict) before files (None), then alphabetical.
    return (0 if isinstance(child, dict) else 1, name)


def render(node: dict, prefix: str = "") -> list[str]:
    lines: list[str] = []
    entries = sorted(node.items(), key=sort_key)
    for i, (name, child) in enumerate(entries):
        last = i == len(entries) - 1
        connector = "└── " if last else "├── "
        suffix = "/" if isinstance(child, dict) else ""
        lines.append(f"{prefix}{connector}{name}{suffix}")
        if isinstance(child, dict):
            extension = "    " if last else "│   "
            lines.extend(render(child, prefix + extension))
    return lines


def build_body() -> str:
    paths = [p for p in tracked_files() if keep(p)]
    tree = build_tree(paths)
    body = "\n".join([ROOT_LABEL, *render(tree)])
    return f"```\n{body}\n```"


def main() -> int:
    update_readme(README, BEGIN_MARKER, END_MARKER, build_body(), "tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
