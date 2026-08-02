#!/usr/bin/env python3
"""Tests for the README directory tree, and for the one rule that is not obvious.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

`generate_tree.py` renders `git ls-files` as a tree, and everything about that
is visible in the output — except the collapse rule. `lean/Math/` is rendered as
a bare directory with its contents hidden, because the Lean library gains a file
per proof session and the README tree is meant to orient a reader rather than
list files.

That rule has exactly one failure mode worth guarding: a collapsed prefix has to
come out as a *directory* and not as a file. It reaches `render()` as a leaf,
same as `README.md` does, and the only thing distinguishing the two is whether
the leaf maps to an empty dict or to None. Get that wrong and the tree grows a
line reading `Math` with no trailing slash — which looks like a file called
Math, is wrong in a way nobody would query, and would survive indefinitely.
"""

from __future__ import annotations

import unittest

from generate_tree import build_body, build_tree, collapse, keep, render


class TestCollapse(unittest.TestCase):
    def test_path_inside_a_collapsed_prefix_renders_as_the_prefix(self):
        self.assertEqual(collapse("lean/Math/Study/AlgebraicKTheory.lean"), ("lean/Math", True))

    def test_path_outside_is_returned_unchanged(self):
        self.assertEqual(collapse("lean/lakefile.toml"), ("lean/lakefile.toml", False))

    def test_the_prefix_itself_is_not_collapsed(self):
        """`lean/Math.lean` is the library root file, not a path inside `lean/Math/`.

        The two differ by one character, and the separator is what tells them
        apart — which is why the prefix is only ever matched with it attached.
        """
        self.assertEqual(collapse("lean/Math.lean"), ("lean/Math.lean", False))

    def test_a_sibling_sharing_the_prefix_is_not_collapsed(self):
        self.assertEqual(collapse("lean/Mathlib/Foo.lean"), ("lean/Mathlib/Foo.lean", False))


class TestBuildTree(unittest.TestCase):
    def test_a_collapsed_directory_is_a_directory_not_a_file(self):
        tree = build_tree(["lean/Math/Learn/MIL/C02.lean"])
        self.assertEqual(tree, {"lean": {"Math": {}}})

    def test_an_ordinary_file_is_a_file(self):
        tree = build_tree(["lean/lean-toolchain"])
        self.assertEqual(tree, {"lean": {"lean-toolchain": None}})

    def test_many_collapsed_files_render_as_one_entry(self):
        tree = build_tree(
            [
                "lean/Math/Learn/MIL/C02.lean",
                "lean/Math/Learn/TPiL/Ch02.lean",
                "lean/Math/Study/AlgebraicKTheory.lean",
            ]
        )
        self.assertEqual(tree, {"lean": {"Math": {}}})


class TestRender(unittest.TestCase):
    def test_collapsed_directory_gets_a_slash_and_no_children(self):
        lines = render(build_tree(["lean/Math/Study/AlgebraicKTheory.lean", "lean/lakefile.toml"]))
        self.assertEqual(lines, ["└── lean/", "    ├── Math/", "    └── lakefile.toml"])

    def test_directories_sort_before_files(self):
        lines = render(build_tree(["tex/preamble.tex", "tex/topology/main.tex"]))
        self.assertEqual(lines, ["└── tex/", "    ├── topology/", "    │   └── main.tex", "    └── preamble.tex"])


class TestKeep(unittest.TestCase):
    """The prune rule, which predates the collapse rule and is unchanged by it."""

    def test_generated_and_dot_paths_are_dropped(self):
        for path in ("pdf/topology.pdf", ".github/workflows/lean.yml", ".gitignore"):
            with self.subTest(path=path):
                self.assertFalse(keep(path))

    def test_sources_are_kept(self):
        for path in ("tex/topology/ch01.tex", "lean/Math.lean", "README.md"):
            with self.subTest(path=path):
                self.assertTrue(keep(path))


class TestAgainstTheRepo(unittest.TestCase):
    """One check against the real `git ls-files`, not a synthetic path list.

    The unit tests above would all pass with COLLAPSED_DIRS naming a directory
    that does not exist. This is what notices the prefix no longer matching
    anything on disk — a rename of the Lean library, most likely.
    """

    def test_the_lean_library_is_collapsed_in_the_real_tree(self):
        body = build_body()
        self.assertIn("── Math/\n", body, "lean/Math/ is not in the tree at all")
        self.assertNotIn("Learn/", body, "lean/Math/ is in the tree uncollapsed")


if __name__ == "__main__":
    unittest.main()
