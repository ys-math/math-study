#!/usr/bin/env python3
r"""Render a chapter's Lean statements for a blind read-back, and keep its audit stamps.

Run from the repo root:
    python scripts/lean_statements.py status   [<topic> [<chapter>]]
    python scripts/lean_statements.py prepare  <topic> <chapter>
    python scripts/lean_statements.py assemble <topic> <chapter>

`/read-back` is the only caller. It audits the statement file
`lean/Math/Study/<Topic>/C<NN>.lean` by having a reader that has never seen the
notes turn it into English, and this script is every part of that which must be
mechanical rather than kept:

- **What the reader sees is what Lean elaborated, not what the source says.**
  The dump comes from the kernel's view of each declaration — auto-bound
  implicits, coercions and instance arguments all visible — because every
  silent mistranslation lives in the gap between the two. Comments and
  docstrings never reach it.
- **Theorem names are hidden.** A theorem's name is its `\label{}` body
  (`docs/lean-convention.md`, `## The shared name`), so a reader shown
  `projective_of_free` can write "a free module is projective" without reading
  the type. Theorems become `T<n>`; `def`, `structure` and Mathlib names stay,
  being the vocabulary the statements are written in.
- **An audit cannot outlive what it audited.** Each block in the read-back is
  stamped with a hash of the declaration as elaborated, folded together with the
  hashes of the same chapter's definitions it mentions. Change the statement, or
  a definition under it, and the stamp stops matching: the block is stale and
  its `audited=yes` is gone on the next run. A proof never affects a stamp —
  proofs live in `lean/Math/Proof/`, which this script never reads.

It reads nothing under `tex/`. That is the design, not an omission: the reader
must be blind, and `docs/repo-structure.md` declines any machinery joining the
halves. The comparison against the notes is the owner's.

`prepare` writes the dump it showed to `lean/.lake/readback/`, and `assemble`
reads that same dump back, so the `T<n>` ids the reader answered for are the ids
being filed — refused if the statement file changed in between.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

LEAN_DIR = Path("lean")
STUDY_DIR = LEAN_DIR / "Math" / "Study"
WORK_DIR = LEAN_DIR / ".lake" / "readback"  # gitignored with the rest of .lake/
MARK = "READBACK "

STAMP = re.compile(r"^% readback: (?P<name>\S+) sha=(?P<sha>[0-9a-f]{12}) audited=(?P<audited>yes|no)$")
END = "% end readback"
KIND_HEADING = {
    "theorem": "Theorem",
    "def": "Definition",
    "structure": "Structure",
    "inductive": "Inductive type",
    "instance": "Instance",
    "axiom": "Axiom",
    "opaque": "Opaque constant",
}

# The Lean half of the dump. Run with `lake env lean` from lean/, importing the
# modules named in MODULES. Only declarations with source ranges are kept, which
# is what drops the auxiliary ones Lean generates (recursors, `noConfusion`,
# equation lemmas); constructors and projections are reported under the type
# that owns them rather than as entries of their own.
DUMP_PROGRAM = r"""
import Lean
open Lean Meta Elab Command

run_cmd do
  let env ← getEnv
  let pp (e : Expr) : CommandElabM String := liftTermElabM do return toString (← ppExpr e)
  for mod in MODULES do
    let some idx := env.getModuleIdx? mod | throwError "module {mod} is not imported"
    for n in env.header.moduleData[idx.toNat]!.constNames do
      if n.isInternalDetail then continue
      let some ci := env.find? n | continue
      if ci matches .ctorInfo _ | .recInfo _ | .quotInfo _ then continue
      if isAuxRecursor env n || isNoConfusion env n then continue
      if (env.getProjectionFnInfo? n).isSome then continue
      let some rng ← findDeclarationRanges? n | continue
      let kind := match ci with
        | .thmInfo _ => "theorem"
        | .defnInfo _ => if isInstanceCore env n then "instance" else "def"
        | .inductInfo _ => if isStructure env n then "structure" else "inductive"
        | .axiomInfo _ => "axiom"
        | .opaqueInfo _ => "opaque"
        | _ => "other"
      let value ← match ci with
        | .defnInfo d => pure (Json.str (← pp d.value))
        | _ => pure Json.null
      let mut parts : Array Json := #[]
      if isStructure env n then
        for f in getStructureFields env n do
          if let some p := env.find? (n ++ f) then
            parts := parts.push (Json.mkObj [("name", toJson f), ("type", Json.str (← pp p.type))])
      else if let .inductInfo i := ci then
        for c in i.ctors do
          if let some cc := env.find? c then
            parts := parts.push (Json.mkObj [("name", toJson c), ("type", Json.str (← pp cc.type))])
      IO.println ("READBACK " ++ (Json.mkObj [("module", toJson mod), ("name", toJson n),
        ("kind", Json.str kind), ("line", toJson rng.range.pos.line),
        ("type", Json.str (← pp ci.type)), ("value", value), ("parts", Json.arr parts)]).compress)
"""

PREAMBLE = r"""% SPDX-License-Identifier: Apache-2.0
% A blind read-back of {source}, written by /read-back.
% The reader saw only the elaborated statements, with theorem names hidden, and
% never the notes. Compare it with the notes yourself; see docs/lean-convention.md.
% Change a stamp's audited to yes by hand once its block matches the notes. Every
% other line is regenerated: edit the Lean, then re-run /read-back.
\documentclass{{article}}
\usepackage{{amsmath,amssymb}}
\newenvironment{{rbentry}}[2]
  {{\par\bigskip\noindent\textbf{{#1}}\quad\texttt{{\detokenize{{#2}}}}\par\nopagebreak\smallskip}}
  {{\par}}
\newenvironment{{readernote}}
  {{\par\smallskip\begin{{quote}}\small\textit{{Reader note.}}\ }}
  {{\end{{quote}}}}
\title{{Read-back of \texttt{{{module}}}}}
\date{{}}
\begin{{document}}
\maketitle
"""
POSTAMBLE = "\\end{document}\n"


# ── Names and paths ─────────────────────────────────────────────────────────


def topic_module(slug: str) -> str:
    """`algebraic_k_theory` → `AlgebraicKTheory`, per docs/naming-convention.md."""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", slug):
        raise ValueError(f"not a topic slug: {slug!r}")
    return "".join(part[:1].upper() + part[1:] for part in slug.split("_") if part)


def chapter_id(arg: str) -> str:
    """`3`, `03`, `ch03` and `C03` all name chapter three: `C03`."""
    match = re.fullmatch(r"(?:ch|C|c)?0*(\d{1,2})", arg)
    if not match or int(match.group(1)) == 0:
        raise ValueError(f"not a chapter: {arg!r}")
    return f"C{int(match.group(1)):02d}"


@dataclass(frozen=True)
class Chapter:
    topic: str  # UpperCamelCase module segment
    chapter: str  # C<NN>

    @property
    def module(self) -> str:
        return f"Math.Study.{self.topic}.{self.chapter}"

    @property
    def source(self) -> Path:
        return STUDY_DIR / self.topic / f"{self.chapter}.lean"

    @property
    def readback(self) -> Path:
        return STUDY_DIR / self.topic / f"{self.chapter}.readback.tex"

    @property
    def stem(self) -> str:
        return f"{self.topic}.{self.chapter}"


def chapters_on_disk(topic: str | None = None, chapter: str | None = None) -> list[Chapter]:
    """Every statement file under lean/Math/Study/<Topic>/, optionally narrowed."""
    found = []
    for path in sorted(STUDY_DIR.glob("*/C[0-9][0-9].lean")):
        ch = Chapter(path.parent.name, path.stem)
        if topic and ch.topic != topic:
            continue
        if chapter and ch.chapter != chapter:
            continue
        found.append(ch)
    return found


# ── The dump ────────────────────────────────────────────────────────────────


@dataclass
class Entry:
    module: str
    name: str
    kind: str
    line: int
    type: str
    value: str | None = None
    parts: list[dict] = field(default_factory=list)
    id: str = ""
    sha: str = ""

    @property
    def hidden(self) -> bool:
        """Theorem names are label bodies; everything else is vocabulary."""
        return self.kind == "theorem"


def parse_dump(output: str) -> dict[str, list[Entry]]:
    """The READBACK lines of a dump run, grouped by module, in source order."""
    by_module: dict[str, list[Entry]] = {}
    for line in output.splitlines():
        if not line.startswith(MARK):
            continue
        raw = json.loads(line[len(MARK):])
        entry = Entry(
            module=raw["module"],
            name=raw["name"],
            kind=raw["kind"],
            line=raw["line"],
            type=raw["type"],
            value=raw.get("value"),
            parts=raw.get("parts") or [],
        )
        by_module.setdefault(entry.module, []).append(entry)
    for entries in by_module.values():
        entries.sort(key=lambda e: e.line)
        for n, entry in enumerate(entries, 1):
            entry.id = f"T{n}"
        stamp(entries)
    return by_module


def body(entry: Entry) -> str:
    """What the declaration says, without its own name when that name is hidden."""
    lines = [entry.type]
    if entry.value is not None:
        lines.append(f":= {entry.value}")
    for part in entry.parts:
        lines.append(f"| {part['name']} : {part['type']}")
    return "\n".join(lines)


def mentions(text: str, name: str) -> bool:
    return re.search(rf"(?<![\w.']){re.escape(name)}(?![\w'])", text) is not None


def stamp(entries: list[Entry]) -> None:
    """Hash each entry, folding in the hashes of this chapter's defs it mentions.

    Folding is what makes a redefinition stale every theorem stated in terms of
    it: the theorem's elaborated type is byte-identical, and its meaning is not.
    Entries are in source order and Lean requires a name to be declared before
    use, so every def an entry mentions already has its hash.
    """
    done: dict[str, str] = {}
    for entry in entries:
        text = body(entry)
        deps = sorted(done[n] for n in done if n != entry.name and mentions(text, n))
        own = entry.name if not entry.hidden else ""
        digest = hashlib.sha256("\n".join([entry.kind, own, text, *deps]).encode()).hexdigest()
        entry.sha = digest[:12]
        if not entry.hidden:
            done[entry.name] = entry.sha


def reader_view(entries: list[Entry]) -> str:
    """The dump as the blind reader sees it: theorem names replaced by ids."""
    hidden = {e.name: e.id for e in entries if e.hidden}
    out = []
    for entry in entries:
        text = body(entry)
        for name, ident in hidden.items():
            text = re.sub(rf"(?<![\w.']){re.escape(name)}(?![\w'])", ident, text)
        heading = f"[{entry.id}] {entry.kind}" + ("" if entry.hidden else f" {entry.name}")
        out.append(heading + "\n" + "\n".join("  " + line for line in text.splitlines()))
    return "\n\n".join(out) + "\n"


def run_dump(chapters: list[Chapter]) -> dict[str, list[Entry]]:
    """Build the modules, then dump them in one Lean run (Mathlib loads once)."""
    for ch in chapters:
        if not ch.source.exists():
            sys.exit(f"{ch.source} does not exist; run /formalize first.")
    modules = [ch.module for ch in chapters]
    build = subprocess.run(["lake", "build", *modules], cwd=LEAN_DIR, capture_output=True, text=True)
    if build.returncode != 0:
        sys.exit(f"lake build failed; fix the statement file first.\n{build.stdout}{build.stderr}")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    program = "".join(f"import {m}\n" for m in modules) + DUMP_PROGRAM.replace(
        "MODULES", "#[" + ", ".join(f"`{m}" for m in modules) + "]"
    )
    (WORK_DIR / "Dump.lean").write_text(program)
    run = subprocess.run(
        ["lake", "env", "lean", str(Path(".lake") / "readback" / "Dump.lean")],
        cwd=LEAN_DIR,
        capture_output=True,
        text=True,
    )
    if run.returncode != 0:
        sys.exit(f"the dump failed:\n{run.stdout}{run.stderr}")
    return parse_dump(run.stdout)


# ── The read-back file ──────────────────────────────────────────────────────


@dataclass
class Block:
    name: str
    sha: str
    audited: bool
    text: str  # verbatim, stamp line through end line


def parse_readback(text: str) -> dict[str, Block]:
    """The stamped blocks of an existing read-back, keyed by declaration name."""
    blocks: dict[str, Block] = {}
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        match = STAMP.match(lines[i].rstrip("\n"))
        if not match:
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].rstrip("\n") != END:
            j += 1
        if j == len(lines):
            raise ValueError(f"block for {match['name']} has no {END!r} line")
        blocks[match["name"]] = Block(
            match["name"], match["sha"], match["audited"] == "yes", "".join(lines[i : j + 1])
        )
        i = j + 1
    return blocks


def classify(entries: list[Entry], blocks: dict[str, Block]) -> dict[str, list[str]]:
    """Each declaration's audit state, plus blocks whose declaration is gone."""
    state: dict[str, list[str]] = {"unread": [], "stale": [], "unaudited": [], "audited": [], "orphaned": []}
    for entry in entries:
        block = blocks.get(entry.name)
        if block is None:
            state["unread"].append(entry.name)
        elif block.sha != entry.sha:
            state["stale"].append(entry.name)
        elif block.audited:
            state["audited"].append(entry.name)
        else:
            state["unaudited"].append(entry.name)
    names = {e.name for e in entries}
    state["orphaned"] = [name for name in blocks if name not in names]
    return state


def parse_reader(text: str) -> dict[str, tuple[str, list[str]]]:
    """The reader's handoff: `=== T<n>` sections, each a TeX body and NOTE: lines."""
    sections: dict[str, tuple[list[str], list[str]]] = {}
    current = None
    for line in text.splitlines():
        header = re.fullmatch(r"=== (T\d+)\s*", line)
        if header:
            current = header.group(1)
            if current in sections:
                raise ValueError(f"{current} appears twice in the reader's output")
            sections[current] = ([], [])
        elif current is None:
            if line.strip():
                raise ValueError(f"text before the first === header: {line!r}")
        elif line.startswith("NOTE:"):
            sections[current][1].append(line[len("NOTE:"):].strip())
        else:
            sections[current][0].append(line)
    return {k: ("\n".join(b).strip(), notes) for k, (b, notes) in sections.items()}


def render_block(entry: Entry, tex: str, notes: list[str]) -> str:
    """A fresh block, always `audited=no`: only the owner ever sets yes."""
    out = [f"% readback: {entry.name} sha={entry.sha} audited=no"]
    out.append(f"\\begin{{rbentry}}{{{KIND_HEADING.get(entry.kind, entry.kind)}}}{{{entry.name}}}")
    out.append(tex)
    for note in notes:
        out.append(f"% note: {note}")
        out.append(f"\\begin{{readernote}}{note}\\end{{readernote}}")
    out.append("\\end{rbentry}")
    out.append(END)
    return "\n".join(out) + "\n"


def assemble(ch: Chapter, entries: list[Entry], old: dict[str, Block], reader: dict) -> tuple[str, list[str]]:
    r"""The new read-back: unchanged blocks verbatim, the rest from the reader.

    Returns the file and the names whose blocks were written fresh. Refuses if
    the reader left out a block that needed writing, or answered for one that
    did not, or wrote anything but ASCII — the document is compiled with no
    font set up for Unicode, and `\mathbb{N}` is what the reader should write.
    """
    wanted = to_read(entries, old)
    unknown = sorted(set(reader) - {e.id for e in entries if e.name in wanted}, key=lambda s: int(s[1:]))
    if unknown:
        raise ValueError(f"the reader answered for {', '.join(unknown)}, which it was not asked for")
    fresh = []
    parts = [PREAMBLE.format(source=ch.source, module=ch.module)]
    for entry in entries:
        if entry.name in wanted:
            if entry.id not in reader:
                raise ValueError(f"the reader did not answer for {entry.id} ({entry.name})")
            tex, notes = reader[entry.id]
            if not tex:
                raise ValueError(f"the reader's answer for {entry.id} is empty")
            for piece in [tex, *notes]:
                if not piece.isascii():
                    raise ValueError(f"the reader's answer for {entry.id} is not ASCII: use TeX commands")
            parts.append(render_block(entry, tex, notes))
            fresh.append(entry.name)
        else:
            parts.append(old[entry.name].text)
        parts.append("\n")
    parts.append(POSTAMBLE)
    return "".join(parts), fresh


def to_read(entries: list[Entry], blocks: dict[str, Block]) -> list[str]:
    state = classify(entries, blocks)
    return state["unread"] + state["stale"]


# ── Commands ────────────────────────────────────────────────────────────────


def resolve(args) -> list[Chapter]:
    topic = topic_module(args.topic) if args.topic else None
    chapter = chapter_id(args.chapter) if getattr(args, "chapter", None) else None
    chapters = chapters_on_disk(topic, chapter)
    if not chapters:
        where = STUDY_DIR / (topic or "*") / f"{chapter or 'C??'}.lean"
        sys.exit(f"no statement file matches {where}")
    return chapters


def load_blocks(ch: Chapter) -> dict[str, Block]:
    return parse_readback(ch.readback.read_text()) if ch.readback.exists() else {}


def cmd_status(args) -> None:
    chapters = resolve(args)
    dumps = run_dump(chapters)
    print(f"{'chapter':<32} {'decls':>5} {'unread':>6} {'stale':>5} {'unaudited':>9} {'audited':>7}")
    for ch in chapters:
        entries = dumps.get(ch.module, [])
        state = classify(entries, load_blocks(ch))
        print(
            f"{ch.module:<32} {len(entries):>5} {len(state['unread']):>6} {len(state['stale']):>5}"
            f" {len(state['unaudited']):>9} {len(state['audited']):>7}"
        )
        if state["orphaned"]:
            print(f"  orphaned blocks (declaration gone or renamed): {', '.join(state['orphaned'])}")


def cmd_prepare(args) -> None:
    (ch,) = resolve(args)
    entries = run_dump([ch]).get(ch.module, [])
    blocks = load_blocks(ch)
    wanted = to_read(entries, blocks)
    state = classify(entries, blocks)
    handoff = WORK_DIR / f"{ch.stem}.reader.tex"
    handoff.unlink(missing_ok=True)  # the reader's Write must create it fresh
    saved = {
        "source_sha": hashlib.sha256(ch.source.read_bytes()).hexdigest(),
        "entries": [e.__dict__ for e in entries],
    }
    (WORK_DIR / f"{ch.stem}.dump.json").write_text(json.dumps(saved, ensure_ascii=False, indent=1))
    ids = [e.id for e in entries if e.name in wanted]
    print(f"module: {ch.module}")
    print(f"handoff: {handoff}")
    print(f"read: {' '.join(ids) if ids else '(nothing — every block is current)'}")
    for key in ("stale", "orphaned"):
        if state[key]:
            print(f"{key}: {', '.join(state[key])}")
    print("--- reader view ---")
    print(reader_view(entries), end="")


def cmd_assemble(args) -> None:
    (ch,) = resolve(args)
    dump = WORK_DIR / f"{ch.stem}.dump.json"
    handoff = WORK_DIR / f"{ch.stem}.reader.tex"
    if not dump.exists():
        sys.exit(f"{dump} is missing; run prepare first.")
    saved = json.loads(dump.read_text())
    if saved["source_sha"] != hashlib.sha256(ch.source.read_bytes()).hexdigest():
        sys.exit(f"{ch.source} changed since prepare; run prepare again.")
    entries = [Entry(**raw) for raw in saved["entries"]]
    old = load_blocks(ch)
    reader = parse_reader(handoff.read_text()) if handoff.exists() else {}
    try:
        text, fresh = assemble(ch, entries, old, reader)
    except ValueError as err:
        sys.exit(f"refused: {err}")
    ch.readback.write_text(text)
    outdir = WORK_DIR / ch.stem
    tex = subprocess.run(
        ["latexmk", "-lualatex", "-interaction=nonstopmode", "-halt-on-error", f"-outdir={outdir}", str(ch.readback)],
        capture_output=True,
        text=True,
    )
    dropped = [name for name in old if name not in {e.name for e in entries}]
    print(f"wrote {ch.readback}: {len(fresh)} block(s) fresh, {len(entries) - len(fresh)} kept")
    if dropped:
        print(f"dropped orphaned blocks: {', '.join(dropped)}")
    if tex.returncode != 0:
        sys.exit(f"the read-back does not compile:\n{tex.stdout[-3000:]}")
    print(f"compiled: {outdir / (ch.readback.stem + '.pdf')}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("status", help="audit state of every formalized chapter")
    p.add_argument("topic", nargs="?")
    p.add_argument("chapter", nargs="?")
    p.set_defaults(func=cmd_status)
    for name, func in (("prepare", cmd_prepare), ("assemble", cmd_assemble)):
        p = sub.add_parser(name)
        p.add_argument("topic")
        p.add_argument("chapter")
        p.set_defaults(func=func)
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ValueError as err:
        sys.exit(str(err))


if __name__ == "__main__":
    main()
