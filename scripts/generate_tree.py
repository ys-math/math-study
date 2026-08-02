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


def build_tree(paths: list[str]) -> dict:
    """Nested dict; a file maps to None, a directory maps to a sub-dict."""
    tree: dict = {}
    for path in paths:
        node = tree
        parts = path.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        # Leaf, and setdefault rather than assignment so a directory already
        # recorded under this name is not clobbered by a file of the same name.
        node.setdefault(parts[-1], None)
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
