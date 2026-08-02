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

`docs/working-loop.ebnf` is the one enumeration that is not a table. It is the
source for the diagram in `README.md`, and the diagram is an SVG produced by a
browser tool — nothing here can read the picture, so the grammar behind it is
checked instead. That check runs one way only; see `TestWorkingLoopGrammar`.

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
WORKING_LOOP = DOC_DIR / "working-loop.ebnf"


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


class TestWorkingLoopGrammar(unittest.TestCase):
    """The grammar behind the README's working-loop diagram.

    Checked one way: every command the grammar names must exist. Deleting a
    command fails this loudly; adding one does not, and that asymmetry is the
    point — the diagram is a happy path, not an inventory. `/delete-topic` is
    absent from it on purpose, being an exit rather than a step.

    The other direction would be worse than useless here. This module runs as a
    step in `update-readme.yml`, and the SVG can only be regenerated by hand, so
    a check demanding the grammar mention every command would make adding one
    block the README from regenerating until somebody opened a browser.
    """

    def test_every_command_in_the_grammar_exists(self):
        # Terminal strings in ISO 14977 are quoted; the slash commands are the
        # only quoted terminals in this grammar. Special sequences (? … ?) hold
        # the prose steps and are deliberately not matched.
        named = set(re.findall(r'"/([a-z][a-z0-9-]*)"', WORKING_LOOP.read_text()))
        self.assertTrue(named, f"{rel(WORKING_LOOP)} names no commands at all")
        for name in sorted(named):
            self.assertIn(name, command_names(), f"{rel(WORKING_LOOP)} names /{name}")

    def test_the_diagram_is_committed_beside_it(self):
        """A grammar with no rendered diagram is a README with a broken image."""
        svg = DOC_DIR / "images" / "working-loop.svg"
        self.assertTrue(svg.exists(), f"{rel(svg)} is missing")
        self.assertIn(svg.relative_to(ROOT).as_posix(), README.read_text())


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
