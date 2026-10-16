#!/usr/bin/env python3
"""Tests for the README directory tree.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

`generate_tree.py` renders `git ls-files` as a tree, and everything about that
is visible in its output, so what is worth testing is the shape: a file has to
come out as a file, a directory as a directory with its children indented under
it, and directories have to sort before files.

`TestAgainstTheRepo` is the only test here that reads the real `git ls-files`.
Everything above it would keep passing if the topics were moved out from under
it, because synthetic paths cannot notice that.
"""

from __future__ import annotations

import unittest

from generate_tree import build_body, build_tree, keep, render


class TestBuildTree(unittest.TestCase):
    def test_nested_directories_become_nested_dicts(self):
        tree = build_tree(["tex/topology/html/cover.html"])
        self.assertEqual(tree, {"tex": {"topology": {"html": {"cover.html": None}}}})

    def test_an_ordinary_file_is_a_file(self):
        tree = build_tree(["tex/index.ist"])
        self.assertEqual(tree, {"tex": {"index.ist": None}})

    def test_siblings_share_their_parent(self):
        tree = build_tree(
            [
                "tex/topology/html/cover.html",
                "tex/topology/ch01.tex",
                "tex/manifold/ch01.tex",
            ]
        )
        self.assertEqual(
            tree,
            {
                "tex": {
                    "topology": {
                        "html": {"cover.html": None},
                        "ch01.tex": None,
                    },
                    "manifold": {"ch01.tex": None},
                }
            },
        )

    def test_a_directory_and_a_file_differing_only_by_suffix_stay_apart(self):
        """`tex/html/` and `tex/html.css` are one character apart.

        The separator is what tells them apart; it is the pair most likely to be
        confused by a future change here.
        """
        tree = build_tree(["tex/html/cover.html", "tex/html.css"])
        self.assertEqual(tree["tex"]["html"], {"cover.html": None})
        self.assertIsNone(tree["tex"]["html.css"])


class TestRender(unittest.TestCase):
    def test_a_directory_gets_a_slash_and_its_children_indented(self):
        lines = render(build_tree(["tex/topology/html/cover.html", "tex/topology/main.tex"]))
        self.assertEqual(
            lines,
            [
                "└── tex/",
                "    └── topology/",
                "        ├── html/",
                "        │   └── cover.html",
                "        └── main.tex",
            ],
        )

    def test_directories_sort_before_files(self):
        lines = render(build_tree(["tex/preamble.tex", "tex/topology/main.tex"]))
        self.assertEqual(lines, ["└── tex/", "    ├── topology/", "    │   └── main.tex", "    └── preamble.tex"])


class TestKeep(unittest.TestCase):
    """The prune rule, which predates the collapse rule and outlived it."""

    def test_generated_and_dot_paths_are_dropped(self):
        for path in ("pdf/topology.pdf", ".github/workflows/build-pdf.yml", ".gitignore"):
            with self.subTest(path=path):
                self.assertFalse(keep(path))

    def test_sources_are_kept(self):
        for path in ("tex/topology/ch01.tex", "scripts/new_topic.py", "README.md"):
            with self.subTest(path=path):
                self.assertTrue(keep(path))


class TestAgainstTheRepo(unittest.TestCase):
    """One check against the real `git ls-files`, not a synthetic path list.

    A rename of `tex/` leaves every test above passing and drops the topics out
    of the README tree silently.
    """

    def test_the_chapter_files_are_listed_and_not_just_their_directories(self):
        """Only a leaf proves the files themselves are being rendered."""
        body = build_body()
        chapters = [ln for ln in body.splitlines() if ln.endswith(".tex") and "── ch" in ln]
        self.assertTrue(chapters, "no chapter files in the tree")


if __name__ == "__main__":
    unittest.main()
