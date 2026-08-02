---
description: Mirror a topic's labelled theorems into lean/Math/Study/ as Lean statements with sorry proofs
argument-hint: "<topic_slug> [label ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Write(lean/Math/Study/**), Edit(lean/Math/Study/**), Edit(lean/Math.lean), Bash(lake:*), Bash(grep:*), Bash(git ls-files:*)
---

Translate a topic's labelled theorem environments into Lean statements in
`lean/Math/Study/<Topic>.lean`, each proved by `sorry`, and stop there.

Arguments given: $ARGUMENTS

All output is English.

**The rules are in three documents, and they are the single copies; nothing
below restates them.** Read all three first, every run:
`docs/lean-convention.md` for how `lean/` works, `docs/naming-convention.md` for
what the file is called, and `docs/label-convention.md` for what a declaration
is called. This file is the workflow.

## The boundary

**This command writes statements. It never writes a proof.** Every declaration
it produces ends `:= by sorry`, and `sorry` is the only tactic it may type.
That is not a style preference — the owner is learning Lean, and a proof written
by an agent is the one part of the exercise that cannot be un-done.

The `allowed-tools` line above holds the half that can be held: this command can
write `lean/Math/Study/**` and add an import to `lean/Math.lean`, and nothing
else. It cannot touch `tex/`, cannot touch `Math/Learn/**`, cannot commit.
The rest is kept rather than enforced — no capability boundary can tell a
statement from a proof.

If the user asks for a proof mid-run, say that this command cannot, and offer to
discuss the goal outside it.

## 1. Picking the topic

- **Slug given** — use it.
- **No arguments** — list every topic as a numbered plain list: the slug, the
  `\DocTitle` from its `main.tex`, how many labelled environments it has, and
  how many of those are already mirrored. Stop and wait. Never default to all.
- **Unknown slug** — say so, print the same list, stop.
- **Several slugs** — one topic per invocation. Say so and stop.

A topic with no `\label{}` at all is the common case right now, and it is a stop,
not an error: the shared name is the only join between the two halves, so there
is nothing to mirror until the theorems are labelled. Say so and suggest
`/label <topic>`.

## 2. Reading

Always the whole topic, and always the existing Lean file:

1. `docs/lean-convention.md` — the shape, the shared name, `sorry`, the header.
2. `docs/naming-convention.md` — the slug-to-module transformation, so the file
   you write to is the one `/delete-topic` will later look for.
3. `docs/label-convention.md` — what the label bodies mean, since the body is
   the declaration name.
4. Every `tex/<topic>/ch*.tex` — the labelled environments and their statements.
5. `lean/Math/Study/<Topic>.lean` if it exists — what is already mirrored.
6. `lean/Math.lean` — whether the module is already imported.

Read the *statement*, not just the label. The label names the result; the Lean
declaration has to say it, and that needs the hypotheses, which live in the
environment body and often in the surrounding prose.

## 3. Deciding what a statement becomes

For each labelled environment not already mirrored, work out the Lean statement
and classify it:

- **Direct mirror** — the Lean statement says what the note says. The
  declaration takes the label body verbatim as its name.
- **Divergent** — the natural Lean statement is Mathlib's, or splits into
  several declarations, or is strictly more general. Then the shared name would
  assert a correspondence that does not hold. Name it for what it actually says
  and say so in the table.
- **Not expressible yet** — the note's definition has no Mathlib counterpart and
  formalising it means building the definition first. Propose the `def` as its
  own row, or skip it.

`docs/lean-convention.md` `## The shared name` is the authority on this split.
Do not stretch a name to make a row look tidy — a wrong shared name is worse
than no row, because the whole scheme rests on the name being trustworthy.

## 4. Propose, and stop

Print a numbered table and **wait**. Nothing has been written yet.

```
algebraic_k_theory (代数的K理論) → lean/Math/Study/AlgebraicKTheory.lean

  #  label                              declaration                    kind
  1  def: IsProjective                  Module.Projective              divergent — Mathlib has it
  2  def: IsRetract                     IsRetract                      direct
  3  lem: projective_of_free            projective_of_free             direct
  4  lem: retract_iff_summand           retract_iff_summand            direct
  5  prop: projective_iff_epi_splits    projective_iff_epi_splits      direct
  ...

  Math.lean gains: import Math.Study.AlgebraicKTheory

Which rows?
```

For every **divergent** row, give the reason in one clause — the reader is
approving a decision about mathematical correspondence, and the name alone does
not carry it.

Show the Lean statement for any row the user asks to see. Show all of them if
the user asks; the table is a summary, not a substitute.

## 5. Write

Only the rows the user named.

A new file gets the licence header from `docs/lean-convention.md`, then the
imports, then a module docstring naming the topic and its `\DocTitle`. Add the
`import Math.Study.<Topic>` line to `lean/Math.lean` in the same run — a module
nobody imports is invisible to `lake build`, which is how a file rots while CI
reports green.

Declarations go in the order the theorems appear in the notes. That order is the
one the owner can navigate, and it usually satisfies Lean's dependency order for
free.

Then the gate, from the repo root — the invocation is in `docs/git-strategy.md`
`## Gates`. A `sorry` warning per declaration is the expected output and is not
a failure; an elaboration error is, and means a statement does not typecheck.
Fix the statement, or report it and leave the row out rather than guessing.

## 6. Report

Print what was written, the `sorry` count, and the gate's result. Then stop —
**this command does not commit.** `/git` does, and it will route
`lean/Math/Study/**` straight to `main`.

Say plainly that every proof is open, and that filling them in is the owner's
work, not a follow-up this command can be asked for.
