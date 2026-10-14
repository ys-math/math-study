#!/usr/bin/env python3
"""Tests for quiver.py, the decoder `/interactive` starts from.

The fixtures are real URLs copied out of the notes, held here as constants
rather than read from the chapters: the chapters are the owner's prose and
change under their own rules, and a redrawn figure should not fail this test.
Between them they cover labels with backslashes and primes, every alignment,
curves, offsets, `shorten` and 2-cells.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import quiver

# category_theory/ch05.tex: the triangle identities, two rows of three with a curved identity each
TRIANGLES = "https://q.uiver.app/#q=WzAsNixbMCwwLCJGKEEpIl0sWzEsMCwiRihHKEYoQSkpKSJdLFsyLDAsIkYoQSkiXSxbMCwxLCJHKEIpIl0sWzEsMSwiRyhGKEcoQikpKSJdLFsyLDEsIkcoQikiXSxbMCwxLCJGKFxcZXRhX0EpIiwyXSxbMSwyLCJcXHZhcmVwc2lsb25fe0YoQSl9IiwyXSxbMCwyLCJcXG1hdGhybXtpZH1fe0YoQSl9IiwwLHsiY3VydmUiOi0zfV0sWzMsNCwiXFxldGFfe0coQil9Il0sWzQsNSwiRyhcXHZhcmVwc2lsb25fe0J9KSJdLFszLDUsIlxcbWF0aHJte2lkfV97RyhCKX0iLDIseyJjdXJ2ZSI6M31dXQ=="
# category_theory/ch05.tex: naturality of the adjunction bijection, with Φ and Φ⁻¹ shifted apart
NATURALITY = "https://q.uiver.app/#q=WzAsNCxbMCwwLCJcXG1hdGhybXtNb3J9X3tcXG1hdGhzY3J7RH19KEYoWCksWSkiXSxbMSwwLCJcXG1hdGhybXtNb3J9X3tcXG1hdGhzY3J7Q319KFgsRyhZKSkiXSxbMCwxLCJcXG1hdGhybXtNb3J9X3tcXG1hdGhzY3J7RH19KEYoWCcpLFknKSJdLFsxLDEsIlxcbWF0aHJte01vcn1fe1xcbWF0aHNjcntDfX0oWCcsRyhZJykpIl0sWzAsMiwidiBcXGNpcmMgKC0pIFxcY2lyYyBGKHUpIiwyXSxbMCwxLCJcXFBoaV97KFgsIFkpfSIsMCx7Im9mZnNldCI6LTF9XSxbMSwzLCJHKHYpIFxcY2lyYyAoLSkgXFxjaXJjIHUiXSxbMiwzLCJcXFBoaV97KFgnLCBZJyl9IiwwLHsib2Zmc2V0IjotMX1dLFsxLDAsIlxcUGhpXnstMX1feyhYLCBZKX0iLDAseyJvZmZzZXQiOi0xfV0sWzMsMiwiXFxQaGleey0xfV97KFgnLCBZJyl9IiwwLHsib2Zmc2V0IjotMX1dXQ=="
# category_theory/ch09.tex: a left Kan extension, whose 2-cells run between arrows
KAN = "https://q.uiver.app/#q=WzAsNSxbMCwwLCJcXG1hdGhzY3J7Q30iXSxbMiwwLCJcXG1hdGhzY3J7RH0iXSxbNCwwLCJcXG1hdGhzY3J7RX0iXSxbNiwwLCJcXG1hdGhzY3J7Q30iXSxbNywwLCJcXG1hdGhzY3J7RX0iXSxbMCwxLCJLIiwyXSxbMSwyLCJcXG1hdGhybXtMYW59X0soRikiXSxbMCwyLCJGIiwwLHsiY3VydmUiOi01fV0sWzEsMiwiRyIsMix7ImN1cnZlIjo0fV0sWzMsNCwiRiIsMCx7ImN1cnZlIjotMn1dLFszLDQsIkdLIiwyLHsiY3VydmUiOjJ9XSxbNywxLCJcXGV0YSIsMix7InNob3J0ZW4iOnsic291cmNlIjoyMH19XSxbNiw4LCJcXGFscGhhIiwwLHsic2hvcnRlbiI6eyJzb3VyY2UiOjIwLCJ0YXJnZXQiOjIwfX1dLFs5LDEwLCJcXGdhbW1hIiwwLHsic2hvcnRlbiI6eyJzb3VyY2UiOjIwLCJ0YXJnZXQiOjIwfX1dXQ=="


def decode(url: str) -> dict:
    return quiver.parse(quiver.decode_payload(quiver.find_url(url)))


class Decode(unittest.TestCase):
    def test_objects_keep_their_grid_positions_and_labels(self):
        d = decode(TRIANGLES)
        self.assertEqual(len(d["objects"]), 6)
        self.assertEqual(d["objects"][1], {"index": 1, "x": 1, "y": 0, "label": "F(G(F(A)))"})
        self.assertEqual(d["objects"][3], {"index": 3, "x": 0, "y": 1, "label": "G(B)"})

    def test_arrows_are_numbered_after_the_objects(self):
        d = decode(TRIANGLES)
        self.assertEqual([a["index"] for a in d["arrows"]], list(range(6, 12)))

    def test_labels_keep_single_backslashes(self):
        d = decode(TRIANGLES)
        self.assertEqual(d["arrows"][0]["label"], r"F(\eta_A)")
        self.assertEqual(d["arrows"][1]["label"], r"\varepsilon_{F(A)}")

    def test_omitted_fields_take_their_defaults(self):
        eta = decode(TRIANGLES)["arrows"][3]  # [3, 4, "\\eta_{G(B)}"]: no alignment, no options
        self.assertEqual(eta["alignment"], "left")
        self.assertEqual((eta["offset"], eta["curve"], eta["options"]), (0, 0, {}))

    def test_alignment_and_curve(self):
        a = decode(TRIANGLES)["arrows"]
        self.assertEqual((a[0]["alignment"], a[2]["curve"]), ("right", -3))
        self.assertEqual((a[5]["alignment"], a[5]["curve"]), ("right", 3))

    def test_offsets_are_lifted_out_of_the_options(self):
        a = decode(NATURALITY)["arrows"]
        self.assertEqual([x["offset"] for x in a], [0, -1, 0, -1, -1, -1])
        self.assertTrue(all(x["options"] == {} for x in a))
        self.assertEqual(a[4]["label"], r"\Phi^{-1}_{(X, Y)}")
        self.assertEqual((a[4]["from"], a[4]["to"]), (1, 0))

    def test_primes_survive(self):
        self.assertEqual(decode(NATURALITY)["arrows"][3]["label"], r"\Phi_{(X', Y')}")

    def test_two_cells_point_at_arrows(self):
        a = decode(KAN)["arrows"]
        self.assertEqual([x["two_cell"] for x in a], [False] * 6 + [True] * 3)
        self.assertEqual((a[7]["from"], a[7]["to"]), (6, 8))
        self.assertEqual(a[7]["options"], {"shorten": {"source": 20, "target": 20}})

    def test_url_safe_and_unpadded_payloads(self):
        payload = quiver.find_url(TRIANGLES).rstrip("=")
        self.assertEqual(quiver.parse(quiver.decode_payload(payload)), decode(TRIANGLES))

    def test_empty_diagram(self):
        self.assertEqual(decode("https://q.uiver.app/#q=WzAsMF0="), {"objects": [], "arrows": []})


class Target(unittest.TestCase):
    def test_reads_the_given_line_of_a_chapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            ch = Path(tmp) / "ch01.tex"
            ch.write_text(f"\\section{{x}}\n% {KAN}\n\\begin{{tikzcd}}\n", encoding="utf-8")
            self.assertEqual(quiver.find_url(quiver.read_target(f"{ch}:2")), quiver.find_url(KAN))

    def test_a_line_without_a_url_is_an_error(self):
        with self.assertRaises(ValueError):
            quiver.find_url("\\begin{tikzcd}")

    def test_a_missing_line_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            ch = Path(tmp) / "ch01.tex"
            ch.write_text("one line\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                quiver.read_target(f"{ch}:5")

    def test_main_reports_errors_without_a_traceback(self):
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            self.assertEqual(quiver.main(["no-such-file.tex:1"]), 1)
        self.assertIn("quiver.py:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
