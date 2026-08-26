# Repo structure

A map of what this repository contains and how the parts relate. It exists
because the repo holds two products that share a directory and almost nothing
else, and that arrangement looks accidental from the inside.

**This file is a map, not a specification.** Every rule it mentions is owned by
another file, named here and not restated. What it does own is the last two
sections: what joins the halves, and what deliberately does not.

`docs/agent-system.md` is the companion map, for the machinery that governs
Claude rather than the machinery that builds anything.

## The two halves

| | `tex/` | `lean/` |
| --- | --- | --- |
| product | PDFs of study notes, in Japanese, one per topic | one Lake library of formalised mathematics |
| unit | a topic — one directory, one `main.tex`, its `ch0N.tex` chapters | a module under `Math/Learn/` or `Math/Study/` |
| built by | LuaLaTeX via `latexmk` | `lake`, against a pinned Mathlib |
| licence | CC BY-NC-ND 4.0 | Apache 2.0 |
| CI | `build-pdf.yml`, `validate.yml` | `lean.yml` |
| owned by | `CLAUDE.md`, `README.md` | `docs/lean-convention.md` |

Both are the repo owner's mathematics, and `CLAUDE.md` fences both off from
Claude — in `tex/` at the prose, in `lean/` at the `by`.

## The supporting third

Neither half; both halves depend on it. All of it is MIT.

**"Supporting" is a claim about dependency, not about worth.** `README.md`
frames the same directories as one of three learning tracks, and both framings
are true on different axes: nothing here is the point of the repo *to build*,
and all of it is the point of the repo *to learn*. That is also why this third
changes more often than either half — note-making keeps asking it for something
it does not yet do.

| directory | serves | owned by |
| --- | --- | --- |
| `scripts/` | the README's generated blocks, topic creation, and the drift tests that hold every enumeration in `docs/` and `README.md` to what is on disk | script docstrings |
| `.github/workflows/` | the workflows — see `docs/agent-system.md` `## Automation` for the table and why the push cascade terminates | that section |
| `.claude/` | commands, hooks, permissions | `docs/agent-system.md` |
| `docs/` | the specifications, one rule per owner | `docs/agent-system.md` `## Instructions` |
| `pdf/` | build output, committed by CI, never hand-edited | `CLAUDE.md` |

## What joins the halves

The whole list, and its shortness is the point — read it as an inventory, not a
sample.

1. **A name.** A `\label{}` body and the Lean declaration formalising it are the
   same string; a topic slug and its module name are the same word re-cased.
   `docs/label-convention.md` and `docs/naming-convention.md` own the two rules.
2. **Three commands that reach across.** `/formalize` reads `tex/` and writes
   `lean/Math/Study/`; `/label` renames on both sides at once; `/delete-topic`
   removes a topic and its mirror together. Each is a capability boundary in its
   `allowed-tools` line, not a convention.
3. **One script that lists both**, `scripts/generate_tree.py`, purely to draw the
   README's directory tree. It reads no content and imposes no order.

That is the entire coupling. Everything else — toolchains, gates, workflows,
licences, routing rules — is per half.

## What deliberately does not join them

This is the section with a reason to exist. Each of these was considered and
declined, and each will look like an obvious improvement to whoever reads the
repo next.

- **No build dependency, in either direction.** `lake build` never reads `tex/`;
  `latexmk` never reads `lean/`. Nothing generates one half from the other. A
  broken chapter cannot fail the Lean build and a broken proof cannot fail a
  PDF, which is why the two have separate gates and separate CI.
- **No extraction step.** The Lean is not pulled out of the `.tex` by a script,
  and the `.tex` does not `\input` anything generated from Lean. Literate-style
  extraction would make one half a build artifact of the other, and the whole
  point is that the note and the formalisation are allowed to disagree — see
  `docs/lean-convention.md` `## The shared name` on why a one-to-one
  correspondence is usually a lie.
- **No `\leanref` macro.** Making the PDF cite Lean declarations would put a
  second copy of the correspondence in `tex/preamble.tex` — a shared file with a
  blast radius of every topic — and the links would rot silently on rename. The
  shared name carries the same information with nothing to drift.
- **No coverage check.** Nothing counts which labelled theorems are formalised
  or fails when the number drops. `sorry` is allowed and the build stays green
  on it, deliberately; a coverage gate would turn a study repo into a backlog.

The through-line: **the halves are coupled by convention, never by machinery.**
Convention is cheap to break on purpose — you simply do not reuse a name when
the mathematics does not match. Machinery is not, and this repo has one author
who is learning Lean, not a library with a compatibility promise.

If a future change would make one half unbuildable without the other, that is
the thing to argue about, not the thing to assume.

## Where to look

| question | file |
| --- | --- |
| What is this repo, how do I build it? | `README.md` |
| What must Claude know in every session? | `CLAUDE.md` |
| What governs Claude — commands, hooks, CI? | `docs/agent-system.md` |
| Which branch does a change go on, and what gates it? | `docs/git-strategy.md` |
| What is this file or directory called? | `docs/naming-convention.md` |
| What goes inside a `\label{}`? | `docs/label-convention.md` |
| How does `lean/` work? | `docs/lean-convention.md` |
| What does a review finding look like? | `docs/issue-convention.md` |
| What does a `\bibitem{}` look like? | `docs/bib-convention.md` |
