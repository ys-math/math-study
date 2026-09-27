#!/usr/bin/env python3
"""Tests for the marker-block writer the README generators share.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

The property that matters is that the two READMEs move together: every block is
written to both, and a README missing a marker stops the run before either is
touched. A half-written pair is the failure mode — the English and Japanese
pages would disagree about which PDFs exist, with a green run to show for it.
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from readme_block import READMES, replace_block, update_readmes

BEGIN = "<!-- BEGIN X -->"
END = "<!-- END X -->"


def page(heading: str, body: str) -> str:
    return f"# {heading}\n\n{BEGIN}\n{body}\n{END}\n\ntrailing prose\n"


class TestReplaceBlock(unittest.TestCase):
    def test_replaces_only_between_markers(self):
        self.assertEqual(replace_block(page("h", "old"), BEGIN, END, "new"), page("h", "new"))

    def test_missing_marker_exits(self):
        with self.assertRaises(SystemExit):
            replace_block("# h\n\nno markers\n", BEGIN, END, "new")


class TestUpdateReadmes(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        root = Path(self.dir.name)
        self.en = root / "README.md"
        self.ja = root / "README.ja.md"
        self.paths = (self.en, self.ja)

    def tearDown(self):
        self.dir.cleanup()

    def run_update(self, body: str) -> list[Path]:
        with redirect_stdout(io.StringIO()):
            return update_readmes(BEGIN, END, body, "x", self.paths)

    def test_default_targets_are_both_languages(self):
        self.assertEqual(READMES, (Path("README.md"), Path("README.ja.md")))

    def test_writes_the_same_body_to_every_readme_and_keeps_their_prose(self):
        self.en.write_text(page("English", "old"), encoding="utf-8")
        self.ja.write_text(page("日本語", "old"), encoding="utf-8")
        self.assertEqual(self.run_update("new"), [self.en, self.ja])
        self.assertEqual(self.en.read_text(encoding="utf-8"), page("English", "new"))
        self.assertEqual(self.ja.read_text(encoding="utf-8"), page("日本語", "new"))

    def test_idempotent(self):
        self.en.write_text(page("English", "old"), encoding="utf-8")
        self.ja.write_text(page("日本語", "old"), encoding="utf-8")
        self.run_update("new")
        self.assertEqual(self.run_update("new"), [])

    def test_only_the_stale_readme_is_written(self):
        self.en.write_text(page("English", "new"), encoding="utf-8")
        self.ja.write_text(page("日本語", "old"), encoding="utf-8")
        self.assertEqual(self.run_update("new"), [self.ja])

    def test_a_readme_missing_its_markers_leaves_both_untouched(self):
        english = page("English", "old")
        self.en.write_text(english, encoding="utf-8")
        self.ja.write_text("# 日本語\n\nマーカーなし\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as caught:
            self.run_update("new")
        self.assertIn("README.ja.md", str(caught.exception.code))
        self.assertEqual(self.en.read_text(encoding="utf-8"), english)

    def test_a_missing_readme_exits(self):
        self.en.write_text(page("English", "old"), encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.run_update("new")


if __name__ == "__main__":
    unittest.main()
