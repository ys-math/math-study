#!/usr/bin/env python3
"""Tests for the README directory tree.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

`generate_tree.py` renders `git ls-files` as a tree, and everything about that
is visible in its output, so what is worth testing is the shape: a file has to
come out as a file, a directory as a directory with its children indented under
it, and directories have to sort before files.

`lean/Math/` was once rendered as a single collapsed entry with its contents
hidden, on the grounds that the Lean library gains a file per proof session.
That is gone. The curriculum files under `Learn/MIL/` and `Learn/TPiL/` are one
file per chapter of a book, and a listing of them is how you see how far through
the book you are — which is the tree earning its place rather than padding it.

`TestAgainstTheRepo` is the only test here that reads the real `git ls-files`.
Everything above it would keep passing if the Lean library were renamed out from
under it, because synthetic paths cannot notice that.
"""

from __future__ import annotations

import unittest

from generate_tree import build_body, build_tree, keep, render


class TestBuildTree(unittest.TestCase):
    def test_nested_directories_become_nested_dicts(self):
        tree = build_tree(["lean/Math/Learn/MIL/C02Basics.lean"])
        self.assertEqual(tree, {"lean": {"Math": {"Learn": {"MIL": {"C02Basics.lean": None}}}}})

    def test_an_ordinary_file_is_a_file(self):
        tree = build_tree(["lean/lean-toolchain"])
        self.assertEqual(tree, {"lean": {"lean-toolchain": None}})

    def test_siblings_share_their_parent(self):
        tree = build_tree(
            [
                "lean/Math/Learn/MIL/C02Basics.lean",
                "lean/Math/Learn/TPiL/C02DependentTypeTheory.lean",
                "lean/Math/Study/AlgebraicKTheory.lean",
            ]
        )
        self.assertEqual(
            tree,
            {
                "lean": {
                    "Math": {
                        "Learn": {
                            "MIL": {"C02Basics.lean": None},
                            "TPiL": {"C02DependentTypeTheory.lean": None},
                        },
                        "Study": {"AlgebraicKTheory.lean": None},
                    }
                }
            },
        )

    def test_a_directory_and_a_file_differing_only_by_suffix_stay_apart(self):
        """`lean/Math/` and `lean/Math.lean` are one character apart.

        The separator is what tells them apart, and it did so under the old
        collapse rule too — that rule matched its prefix only with the separator
        attached for exactly this reason. Keep the case even though the code
        that needed it is gone: it is the pair most likely to be confused by a
        future change here.
        """
        tree = build_tree(["lean/Math/Learn/MIL/C02Basics.lean", "lean/Math.lean"])
        self.assertEqual(tree["lean"]["Math"], {"Learn": {"MIL": {"C02Basics.lean": None}}})
        self.assertIsNone(tree["lean"]["Math.lean"])


class TestRender(unittest.TestCase):
    def test_a_directory_gets_a_slash_and_its_children_indented(self):
        lines = render(build_tree(["lean/Math/Learn/MIL/C02Basics.lean", "lean/lakefile.toml"]))
        self.assertEqual(
            lines,
            [
                "└── lean/",
                "    ├── Math/",
                "    │   └── Learn/",
                "    │       └── MIL/",
                "    │           └── C02Basics.lean",
                "    └── lakefile.toml",
            ],
        )

    def test_directories_sort_before_files(self):
        lines = render(build_tree(["tex/preamble.tex", "tex/topology/main.tex"]))
        self.assertEqual(lines, ["└── tex/", "    ├── topology/", "    │   └── main.tex", "    └── preamble.tex"])


class TestKeep(unittest.TestCase):
    """The prune rule, which predates the collapse rule and outlived it."""

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

    This is what notices the Lean library moving. A rename of `lean/Math/`, of
    `Learn/`, or of either book directory leaves every test above passing and
    drops the curriculum out of the README tree silently.
    """

    def test_the_lean_curriculum_is_listed_in_the_real_tree(self):
        body = build_body()
        for name in ("Math/", "Learn/", "MIL/", "TPiL/"):
            with self.subTest(name=name):
                self.assertIn(f"── {name}\n", body, f"lean/…/{name} is not in the tree")

    def test_the_chapter_files_are_listed_and_not_just_their_directories(self):
        """The directories above exist in the tree even with nothing under them.

        Only a leaf proves the files themselves are being rendered, which is the
        whole point of having removed the collapse rule.
        """
        body = build_body()
        chapters = [ln for ln in body.splitlines() if ln.endswith(".lean") and "Math.lean" not in ln]
        self.assertTrue(chapters, "no Lean chapter files in the tree")


if __name__ == "__main__":
    unittest.main()
