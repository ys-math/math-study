#!/usr/bin/env python3
"""Drift guard for the documentation that describes this repo's agent system.

Run from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'

`README.md` and `docs/agent-system.md` enumerate things that live on disk: the
commands in `.claude/commands/`, the hooks, the workflows, the documents in
`docs/`. A hand-written enumeration goes stale the moment the disk changes, and
nothing about a stale one looks wrong from the inside — `CLAUDE.md` described
"the six commands" for four days after the seventh was added, in a file whose
own preamble is about not letting copies drift.

These tests are what notices. They live in `scripts/` so that they run in the
gate that already exists (`/git`, step 5) and the CI step that already exists
(`update-readme.yml`), rather than in a checker somebody has to remember to
invoke — which is the failure mode being guarded against.

Two conventions make the prose checkable, and both are load-bearing:

- **A count is written in digits, or not written at all.** "all 8 topics" is
  tested; "Seven, in `.claude/commands/`" is invisible here and was deleted
  rather than trusted. Where a table already enumerates the things, do not
  restate how many there are.
- **Enumerations are markdown tables**, keyed on the first column. Prose may
  name a command freely — `/loop` is discussed in two files and is not a
  command in this repo — so only table cells are read as claims of membership.

The diagrams are the enumerations that are not tables, and they need a third
convention: **a diagram is checked through its source, never its picture.** A
railroad diagram's `.ebnf` and a ```mermaid block are both plain text and are
read directly; the rendered SVG is opaque here and is only checked for
existing. Those checks run one way only — see `TestDiagrams` for why the
reverse would hold CI hostage to a browser.

What is deliberately not checked: whether any of the prose is *right*. These
tests compare sets of names. Contradictions, dead steps, capability mismatches
and redundant procedures need judgment, and belong to `/audit`.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMAND_DIR = ROOT / ".claude" / "commands"
HOOK_DIR = ROOT / ".claude" / "hooks"
WORKFLOW_DIR = ROOT / ".github" / "workflows"
DOC_DIR = ROOT / "docs"
SETTINGS = ROOT / ".claude" / "settings.json"
README = ROOT / "README.md"
AGENT_SYSTEM = DOC_DIR / "agent-system.md"


def prose_files() -> list[Path]:
    """Every hand-written file that describes the system."""
    return [README, ROOT / "CLAUDE.md", *sorted(DOC_DIR.glob("*.md")), *sorted(COMMAND_DIR.glob("*.md"))]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def table_keys(text: str) -> list[str]:
    """The first cell of every markdown table row.

    Header and separator rows come back too; callers filter by what they are
    looking for, which keeps this free of assumptions about how many tables a
    file holds or what their headers say.
    """
    keys = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|"):
            keys.append(line.split("|")[1].strip())
    return keys


def tabled_commands(text: str) -> set[str]:
    """Slash commands claimed by the first column of any table in `text`."""
    found = set()
    for key in table_keys(text):
        match = re.match(r"`/([a-z][a-z0-9-]*)", key)
        if match:
            found.add(match.group(1))
    return found


def command_names() -> set[str]:
    return {path.stem for path in COMMAND_DIR.glob("*.md")}


def topic_count() -> int:
    return len(list((ROOT / "tex").glob("*/main.tex")))


class TestCommandTables(unittest.TestCase):
    """The two tables that promise to list every slash command."""

    def test_readme_lists_every_command(self):
        self.assertEqual(command_names(), tabled_commands(README.read_text()))

    def test_agent_system_lists_every_command(self):
        self.assertEqual(command_names(), tabled_commands(AGENT_SYSTEM.read_text()))

    def test_no_file_tables_a_command_that_does_not_exist(self):
        """Catches the deletion half: a removed command still listed somewhere.

        `docs/git-strategy.md` tables only `/git` and `/git-merge` on purpose,
        so membership is checked one way here — every tabled command is real —
        and both ways only for the two tables above.
        """
        for path in prose_files():
            for name in tabled_commands(path.read_text()):
                self.assertIn(name, command_names(), f"{rel(path)} tables /{name}")


class TestDiagrams(unittest.TestCase):
    """The names inside the diagrams, which no reader of the pictures can check.

    Two notations, because the two subjects are different shapes. A railroad
    diagram draws a grammar — the working loop, the routing rule — and comes
    from an `.ebnf` rendered by an external browser tool, so the SVG is opaque
    here and the grammar behind it is what gets read. A ```mermaid block draws
    a graph — the CI cascade — and is already plain text, so it is read where
    it sits.

    Every check below runs **one way**: a name that appears must exist. The
    reverse would be worse than useless. This module runs as a step in
    `update-readme.yml`, and an SVG can only be regenerated by hand, so a check
    demanding that every command appear in a grammar would make adding one
    block the README from regenerating until somebody opened a browser.

    So: deleting a command or a workflow fails this loudly; adding one does
    not. The diagrams are happy paths, not inventories — `/delete-topic` is
    absent from the working loop on purpose, being an exit rather than a step.
    """

    def grammars(self) -> list[Path]:
        return sorted(DOC_DIR.glob("*.ebnf"))

    def test_there_are_grammars_to_check(self):
        """Guards the glob: a renamed extension would silently check nothing."""
        self.assertTrue(self.grammars(), f"no *.ebnf under {rel(DOC_DIR)}")

    def test_every_command_in_a_grammar_exists(self):
        # Terminal strings in ISO 14977 are quoted; the slash commands are the
        # only quoted terminals in these grammars. Special sequences (? … ?)
        # hold the prose steps and are deliberately not matched.
        for path in self.grammars():
            with self.subTest(grammar=path.name):
                named = set(re.findall(r'"/([a-z][a-z0-9-]*)"', path.read_text()))
                self.assertTrue(named, f"{rel(path)} names no commands at all")
                for name in sorted(named):
                    self.assertIn(name, command_names(), f"{rel(path)} names /{name}")

    def test_every_grammar_is_rendered_and_shown(self):
        """A grammar nobody renders is a diagram nobody sees.

        The SVG shares its source's stem (`docs/naming-convention.md`), so the
        pair is checkable without recording the mapping anywhere else.
        """
        prose = {path: path.read_text() for path in prose_files()}
        for path in self.grammars():
            with self.subTest(grammar=path.name):
                svg = DOC_DIR / "images" / f"{path.stem}.svg"
                self.assertTrue(svg.exists(), f"{rel(svg)} is missing")
                shown = [rel(p) for p, text in prose.items() if svg.name in text]
                self.assertTrue(shown, f"no document embeds {rel(svg)}")

    def test_every_workflow_in_a_mermaid_block_exists(self):
        """The cascade diagram names workflows; a deleted one must not linger."""
        on_disk = {path.name for path in WORKFLOW_DIR.glob("*.yml")}
        blocks = 0
        for path in prose_files():
            for block in re.findall(r"```mermaid\n(.*?)```", path.read_text(), re.S):
                blocks += 1
                for name in sorted(set(re.findall(r"[a-z0-9-]+\.yml", block))):
                    self.assertIn(name, on_disk, f"{rel(path)} diagrams {name}")
        self.assertTrue(blocks, "no mermaid blocks found; has the fence changed?")


class TestCommandFrontmatter(unittest.TestCase):
    """Every command declares what it does and what it may touch.

    `allowed-tools` is the one that matters: it is the capability boundary, and
    a command that omits it silently inherits every tool in the session.
    """

    def test_frontmatter_is_complete(self):
        for path in sorted(COMMAND_DIR.glob("*.md")):
            with self.subTest(command=path.stem):
                lines = path.read_text().splitlines()
                self.assertEqual(lines[0], "---", "frontmatter must open on line 1")
                end = lines.index("---", 1)
                keys = {line.split(":", 1)[0] for line in lines[1:end] if ":" in line}
                self.assertLessEqual({"description", "argument-hint", "allowed-tools"}, keys)


class TestHooks(unittest.TestCase):
    """Hooks exist, are wired up, can run, and are documented."""

    def setUp(self):
        settings = json.loads(SETTINGS.read_text())
        self.registered = {
            Path(hook["command"]).name
            for groups in settings["hooks"].values()
            for group in groups
            for hook in group["hooks"]
        }
        self.on_disk = {path.name for path in HOOK_DIR.glob("*.sh")}

    def test_every_hook_is_registered(self):
        self.assertEqual(self.on_disk, self.registered)

    def test_every_hook_is_executable(self):
        """A non-executable hook fails at invocation, not at config load.

        The setup reads as correct and enforces nothing, which is worse than
        having no hook at all — the rules it covers stop being watched by
        anyone, mechanically or otherwise.
        """
        for path in sorted(HOOK_DIR.glob("*.sh")):
            with self.subTest(hook=path.name):
                self.assertTrue(path.stat().st_mode & 0o111, f"{rel(path)} is not executable")

    def test_every_hook_is_documented(self):
        text = AGENT_SYSTEM.read_text()
        for name in sorted(self.on_disk):
            self.assertIn(name, text, f"{rel(AGENT_SYSTEM)} does not mention {name}")


class TestGeneratedAndAutomated(unittest.TestCase):
    def test_every_workflow_is_documented(self):
        text = AGENT_SYSTEM.read_text()
        for path in sorted(WORKFLOW_DIR.glob("*.yml")):
            self.assertIn(path.name, text, f"{rel(AGENT_SYSTEM)} does not mention {path.name}")

    def test_every_doc_is_documented(self):
        """`docs/agent-system.md` says which document owns which rule.

        A document nobody points at is one an agent will not read, which makes
        it a rule that does not bind.
        """
        text = AGENT_SYSTEM.read_text()
        for path in sorted(DOC_DIR.glob("*.md")):
            self.assertIn(path.name, text, f"{rel(AGENT_SYSTEM)} does not mention {path.name}")


class TestCountsInProse(unittest.TestCase):
    """Counts written in digits must match what is on disk.

    Both of these are one `/new-topic` or one new command away from being
    wrong, in files whose whole purpose is to be believed. If a number here is
    genuinely not a count of anything — a duration, a step number — spell it
    out or reword; do not weaken the pattern.
    """

    def assert_count(self, pattern: str, expected: int):
        for path in prose_files():
            for line_no, line in enumerate(path.read_text().splitlines(), 1):
                for match in re.finditer(pattern, line):
                    self.assertEqual(
                        int(match.group(1)),
                        expected,
                        f"{rel(path)}:{line_no} claims {match.group(0)!r}",
                    )

    def test_topic_counts(self):
        self.assert_count(r"(\d+) topics", topic_count())

    def test_command_counts(self):
        self.assert_count(r"(\d+) commands", len(command_names()))


if __name__ == "__main__":
    unittest.main()
