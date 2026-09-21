#!/usr/bin/env python3
"""Tests for the read-back's mechanical half.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

`lean_statements.py` is what keeps `/read-back` honest, and the properties
worth pinning are the ones a model would get wrong by being helpful: the reader
must never see a theorem's name, a changed statement — or a changed definition
under an unchanged one — must lose its audit, and a block nobody asked to
rewrite must come through byte for byte, `audited=yes` included.

None of this runs Lean. The dump is parsed from synthetic `READBACK` lines, so
these tests pass on a machine with no toolchain and stay under a second, as the
gate in `docs/git-strategy.md` promises.
"""

from __future__ import annotations

import json
import unittest

from lean_statements import (
    MARK,
    Chapter,
    assemble,
    chapter_id,
    classify,
    parse_dump,
    parse_reader,
    parse_readback,
    reader_view,
    topic_module,
)

CH = Chapter("AlgebraicKTheory", "C01")
MODULE = CH.module


def line(name, kind, n, type_, value=None, parts=()):
    return MARK + json.dumps(
        {"module": MODULE, "name": name, "kind": kind, "line": n, "type": type_, "value": value, "parts": list(parts)}
    )


def dump(*lines):
    return parse_dump("noise before\n" + "\n".join(lines) + "\nwarning: declaration uses `sorry`\n")[MODULE]


DEF = line("IsRetract", "def", 5, "(R : Type) → [inst : Ring R] → Prop", value="fun R [Ring R] => True")
THM = line("retract_of_free", "theorem", 9, "∀ (R : Type) [inst : Ring R], IsRetract R → 1 = 1")


class TestNames(unittest.TestCase):
    def test_topic_module_matches_the_naming_convention(self):
        self.assertEqual(topic_module("algebraic_k_theory"), "AlgebraicKTheory")
        self.assertEqual(topic_module("category_theory"), "CategoryTheory")

    def test_topic_module_refuses_a_non_slug(self):
        with self.assertRaises(ValueError):
            topic_module("CategoryTheory")

    def test_every_spelling_of_a_chapter(self):
        for arg in ("3", "03", "ch03", "C03"):
            self.assertEqual(chapter_id(arg), "C03")

    def test_chapter_zero_is_not_a_chapter(self):
        with self.assertRaises(ValueError):
            chapter_id("0")

    def test_the_three_paths_of_a_chapter(self):
        self.assertEqual(str(CH.source), "lean/Math/Study/AlgebraicKTheory/C01.lean")
        self.assertEqual(str(CH.readback), "lean/Math/Study/AlgebraicKTheory/C01.readback.tex")


class TestDump(unittest.TestCase):
    def test_entries_come_in_source_order_with_ids(self):
        entries = dump(THM, DEF)
        self.assertEqual([(e.id, e.name) for e in entries], [("T1", "IsRetract"), ("T2", "retract_of_free")])

    def test_the_reader_never_sees_a_theorem_name(self):
        view = reader_view(dump(DEF, THM))
        self.assertNotIn("retract_of_free", view)
        self.assertIn("[T2] theorem\n", view)

    def test_the_reader_keeps_definition_names(self):
        self.assertIn("[T1] def IsRetract", reader_view(dump(DEF, THM)))

    def test_a_theorem_named_inside_another_entry_is_hidden_too(self):
        uses = line("uses", "def", 12, "Prop", value="retract_of_free = retract_of_free")
        view = reader_view(dump(DEF, THM, uses))
        self.assertNotIn("retract_of_free", view)
        self.assertIn(":= T2 = T2", view)

    def test_renaming_a_theorem_keeps_its_stamp(self):
        """A `/label` rename changes no mathematics, so it must not cost an audit."""
        renamed = THM.replace("retract_of_free", "free_is_retract")
        self.assertEqual(dump(DEF, THM)[1].sha, dump(DEF, renamed)[1].sha)

    def test_changing_a_statement_changes_its_stamp(self):
        changed = THM.replace("1 = 1", "2 = 2")
        self.assertNotEqual(dump(DEF, THM)[1].sha, dump(DEF, changed)[1].sha)

    def test_changing_a_definition_stales_the_theorem_that_uses_it(self):
        """The theorem's elaborated type is byte-identical; its meaning is not."""
        redefined = DEF.replace("=> True", "=> False")
        before, after = dump(DEF, THM), dump(redefined, THM)
        self.assertEqual(before[1].type, after[1].type)
        self.assertNotEqual(before[1].sha, after[1].sha)

    def test_a_definition_the_theorem_does_not_mention_leaves_it_alone(self):
        other = line("Unrelated", "def", 3, "Prop", value="True")
        changed = other.replace("True", "False")
        self.assertEqual(dump(other, DEF, THM)[2].sha, dump(changed, DEF, THM)[2].sha)


def block(name, sha, audited="no", text="Body."):
    return f"% readback: {name} sha={sha} audited={audited}\n\\begin{{rbentry}}{{X}}{{{name}}}\n{text}\n\\end{{rbentry}}\n% end readback\n"


class TestReadback(unittest.TestCase):
    def setUp(self):
        self.entries = dump(DEF, THM)
        self.def_sha, self.thm_sha = (e.sha for e in self.entries)

    def test_parse_keeps_each_block_verbatim(self):
        text = "preamble\n" + block("IsRetract", self.def_sha, "yes") + "\n" + block("retract_of_free", "0" * 12)
        blocks = parse_readback(text)
        self.assertTrue(blocks["IsRetract"].audited)
        self.assertEqual(blocks["IsRetract"].text, block("IsRetract", self.def_sha, "yes"))

    def test_a_block_with_no_end_line_is_refused(self):
        with self.assertRaises(ValueError):
            parse_readback(block("IsRetract", self.def_sha).replace("% end readback\n", ""))

    def test_classify(self):
        blocks = parse_readback(block("IsRetract", self.def_sha, "yes") + block("retract_of_free", "0" * 12, "yes")
                                + block("gone", "1" * 12))
        state = classify(self.entries, blocks)
        self.assertEqual(state["audited"], ["IsRetract"])
        self.assertEqual(state["stale"], ["retract_of_free"])
        self.assertEqual(state["orphaned"], ["gone"])

    def test_an_unstamped_declaration_is_unread(self):
        self.assertEqual(classify(self.entries, {})["unread"], ["IsRetract", "retract_of_free"])


class TestReaderHandoff(unittest.TestCase):
    def test_sections_and_notes(self):
        out = parse_reader("=== T1\nA $p$.\nNOTE: odd.\n\n=== T2\nB.\n")
        self.assertEqual(out, {"T1": ("A $p$.", ["odd."]), "T2": ("B.", [])})

    def test_prose_before_the_first_header_is_refused(self):
        with self.assertRaises(ValueError):
            parse_reader("Here is the read-back:\n=== T1\nA.\n")

    def test_a_repeated_id_is_refused(self):
        with self.assertRaises(ValueError):
            parse_reader("=== T1\nA.\n=== T1\nB.\n")


class TestAssemble(unittest.TestCase):
    def setUp(self):
        self.entries = dump(DEF, THM)
        self.def_sha = self.entries[0].sha

    def test_an_audited_current_block_survives_byte_for_byte(self):
        kept = block("IsRetract", self.def_sha, "yes", text="The owner's audited reading.")
        text, fresh = assemble(CH, self.entries, parse_readback(kept), {"T2": ("New.", [])})
        self.assertIn(kept, text)
        self.assertEqual(fresh, ["retract_of_free"])

    def test_a_fresh_block_is_never_audited(self):
        text, _ = assemble(CH, self.entries, {}, {"T1": ("A.", []), "T2": ("B.", [])})
        self.assertNotIn("audited=yes", text)
        self.assertEqual(text.count("audited=no"), 2)

    def test_a_stale_block_loses_its_audit(self):
        old = parse_readback(block("IsRetract", "0" * 12, "yes"))
        text, _ = assemble(CH, self.entries, old, {"T1": ("A.", []), "T2": ("B.", [])})
        self.assertNotIn("audited=yes", text)

    def test_notes_appear_as_comment_and_in_the_pdf(self):
        text, _ = assemble(CH, self.entries, {}, {"T1": ("A.", ["unused hypothesis"]), "T2": ("B.", [])})
        self.assertIn("% note: unused hypothesis", text)
        self.assertIn("\\begin{readernote}unused hypothesis\\end{readernote}", text)

    def test_a_missing_answer_is_refused(self):
        with self.assertRaises(ValueError):
            assemble(CH, self.entries, {}, {"T1": ("A.", [])})

    def test_an_answer_nobody_asked_for_is_refused(self):
        kept = parse_readback(block("IsRetract", self.def_sha, "yes"))
        with self.assertRaises(ValueError):
            assemble(CH, self.entries, kept, {"T1": ("Rewritten.", []), "T2": ("B.", [])})

    def test_non_ascii_is_refused(self):
        with self.assertRaises(ValueError):
            assemble(CH, self.entries, {}, {"T1": ("A.", []), "T2": ("For all x ∈ ℕ.", [])})

    def test_the_document_is_complete(self):
        text, _ = assemble(CH, self.entries, {}, {"T1": ("A.", []), "T2": ("B.", [])})
        self.assertTrue(text.startswith("% SPDX-License-Identifier: Apache-2.0\n"))
        self.assertIn("\\begin{document}", text)
        self.assertTrue(text.endswith("\\end{document}\n"))


if __name__ == "__main__":
    unittest.main()
