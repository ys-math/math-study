---
description: Mirror a topic's labelled theorems into lean/Math/Study/ as Lean statements with sorry proofs
argument-hint: "<topic_slug> [label ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Write(lean/Math/Study/**), Edit(lean/Math/Study/**), Edit(lean/Math.lean), Bash(cd lean && lake build), Bash(grep:*), Bash(git ls-files:*), Bash(gh issue list:*)
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

Two mechanisms hold it, and neither is this paragraph. The `allowed-tools` line
above bounds *where*: `lean/Math/Study/**` and the import list in
`lean/Math.lean`, nothing else — not `tex/`, not `Math/Learn/**`, and no commit.
`.claude/hooks/guard-edits.sh` bounds *what*: it refuses a write here whose
tactic blocks are not exactly `sorry`. So a proof written by this command is
rejected by the hook, not merely discouraged by this file.

The hook's test is syntactic, so a term-mode proof would pass it. Do not go
looking for that gap. It exists because closing it would refuse ordinary `def`s,
not because term-mode proofs are permitted.

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
7. The topic's open review findings:

   ```bash
   gh issue list --label "topic:<topic>" --state open --json number,title,body
   ```

Read the *statement*, not just the label. The label names the result; the Lean
declaration has to say it, and that needs the hypotheses, which live in the
environment body and often in the surrounding prose.

### Open findings block the rows they touch

An open `topic:<topic>` issue is a known defect in the notes, and mirroring a
statement it names would carve that defect into a Lean declaration and give it a
name asserting the two agree.

Match each finding against the labels being mirrored — `docs/issue-convention.md`
`### Location, and the dirty tree` is how an issue says where it is. A row a finding names is marked
`[blocked #N]` in the table and **is not offered**. Say why in one clause, and
point at the issue.

Block the row, never the run. A finding about 補題 1.2 says nothing about 定理
3.4, and refusing the whole topic over one open issue is how a gate becomes
something people route around. If every row is blocked, say so and stop — there
is nothing to propose.

This is a check against the record, not a review. `/review-notes` is what finds
defects, and this command cannot file, close or fix one.

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
- **Understated** — the note is missing something the Lean statement needs: a
  hypothesis, a non-triviality condition, a typeclass assumption without which
  the statement is false. See below. This row is **not offered**.

`docs/lean-convention.md` `## The shared name` is the authority on this split.
Do not stretch a name to make a row look tidy — a wrong shared name is worse
than no row, because the whole scheme rests on the name being trustworthy.

### Never repair a statement in passing

**If the Lean statement needs a hypothesis the prose does not state, that is a
finding about the notes. Report it. Do not add it.**

This is the one failure that survives everything else. Adding the missing `[Nontrivial R]`
takes a second, produces Lean that typechecks and proves, and leaves the note
exactly as wrong as it was — while the shared name now certifies that the two
say the same thing. Every gate downstream reads green: the build passes, the
hook passes, `sorry` is honest, CI is happy. Nobody ever finds out.

Compare the loud version. Mirror the statement *as written*, and it fails to
typecheck, or sits unprovable until the owner works out why. That is the whole
value of formalising your own notes, and quietly patching the statement is
precisely how it is thrown away.

So an understated row is reported, never written:

```
 7  lem: splitting_lemma   understated — 命題 as written omits that the sequence
                           is short exact; `Function.Exact` needs it. Not offered.
                           → /review-notes algebraic_k_theory to file it
```

The same holds for anything else that makes the mathematics *work* rather than
merely translating it: strengthening a conclusion, weakening a hypothesis,
silently choosing the Mathlib definition where the note's would fail. Any of
those is a divergent or understated row with the reason stated, never a direct
mirror.

This command has no `gh issue create` and cannot file the finding itself. Say
what it is and point at `/review-notes`; the owner decides whether the note or
the statement is what is wrong, and that decision is not yours.

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
