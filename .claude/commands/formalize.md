---
description: Translate one chapter's labelled theorems, and the definitions they need, into a frozen Lean statement file with sorry proofs
argument-hint: "<topic_slug> <chapter> [label ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Write(lean/Math/Study/**), Edit(lean/Math/Study/**), Edit(lean/Math.lean), Bash(cd lean && lake build), Bash(grep:*), Bash(git ls-files:*), Bash(gh issue list:*)
---

Translate one chapter's labelled theorem environments, and the definitions they
are stated in terms of, into `lean/Math/Study/<Topic>/C<NN>.lean` — every one
proved by `sorry` — and stop there. `/read-back` then audits what was written.

Arguments given: $ARGUMENTS

All output is English.

**The rules are in three documents, and they are the single copies; nothing
below restates them.** Read all three first, every run:
`docs/lean-convention.md` for how `lean/` works — the statement/proof split, the
shared name, `sorry`, the header, the read-back — `docs/naming-convention.md`
for what the file is called, and `docs/label-convention.md` for what a
declaration is called. This file is the workflow.

## The boundary

**This command writes statements. It never writes a proof** — not in the
statement file, and not in `lean/Math/Proof/**`, which is the owner's and which
nothing here may open for writing.

Two mechanisms hold it, and neither is this paragraph:

- `.claude/settings.json` denies every write under `lean/Math/Proof/**`, before
  it happens.
- `.claude/hooks/guard-edits.sh` refuses a write under `lean/Math/Study/**`
  whose tactic blocks are not exactly `sorry`.

The hook is syntactic, so a term-mode proof would pass it. Do not go looking
for that gap; it exists because closing it would refuse ordinary `def`s.

If the user asks for a proof mid-run, say that this command cannot, and offer to
discuss the goal outside it.

## 1. Picking the chapter

- **Topic and chapter given** — use them. The chapter is a number (`3`, `03`,
  `ch03`) naming `tex/<topic>/ch<NN>.tex`.
- **Labels given after the chapter** — only those rows are proposed.
- **No arguments** — list every topic as a numbered plain list: the slug, the
  `\DocTitle` from its `main.tex`, and per chapter how many labelled
  environments it has and how many are already in its statement file. Stop and
  wait. Never default to all.
- **Topic only** — print that topic's chapter line from the same list and stop.
- **Unknown slug or chapter** — say so, print the list, stop.
- **Several topics or chapters** — one chapter per invocation. Say so and stop.

A chapter with no `\label{}` at all is a stop, not an error: the shared name is
the only join between the two halves, so there is nothing to mirror until the
theorems are labelled. Say so and suggest `/label <topic>`.

## 2. Reading

1. The three documents above.
2. `tex/<topic>/ch<NN>.tex` in full, and the earlier chapters wherever this one
   leans on their definitions.
3. `lean/Math/Study/<Topic>/C<NN>.lean` if it exists — what is already stated —
   and the earlier chapters' statement files, which this one may import.
4. `lean/Math/Proof/<Topic>/C<NN>.lean` if it exists — **read only**, to know
   which statements a proof depends on. `grep -n 'type_of% @' ` it.
5. `lean/Math.lean` — whether the module is already imported.
6. The topic's open review findings:

   ```bash
   gh issue list --label "topic:<topic>" --state open --json number,title,body
   ```

Read the *statement*, not just the label. The label names the result; the Lean
declaration has to say it, and that needs the hypotheses, which live in the
environment body and often in the surrounding prose.

### Open findings block the rows they touch

An open `topic:<topic>` issue is a known defect in the notes, and stating a
theorem it names would carve that defect into a Lean declaration and give it a
name asserting the two agree.

Match each finding against the rows — `docs/issue-convention.md`
`### Location, and the dirty tree` is how an issue says where it is. A row a
finding names is marked `[blocked #N]` and **is not offered**. Block the row,
never the run; if every row is blocked, say so and stop.

This is a check against the record, not a review. `/review-notes` is what finds
defects, and this command cannot file, close or fix one.

## 3. Deciding what each row becomes

A row is a labelled environment of the chapter, or a definition one of them is
stated in terms of. **Definitions are in scope, not optional**: a theorem that
reads back perfectly about a wrongly defined `IsFoo` says nothing true about the
note, and the read-back audits definitions for exactly that reason. Where
Mathlib already has the notion, the row is a divergent one (below) naming
Mathlib's; where it does not, the `def` is its own row, stated before the
theorems that use it.

Classify every row:

- **Direct** — the Lean says what the note says. The declaration takes the
  label body verbatim as its name.
- **Divergent** — the natural Lean statement is Mathlib's, or splits into
  several declarations, or is strictly more general. Name it for what it
  actually says and give the reason in the table.
- **Understated** — the note is missing something the Lean needs to be true: a
  hypothesis, a non-triviality condition, a type class. **Not offered.** See
  below.

`docs/lean-convention.md` `## The shared name` is the authority on this split.
A wrong shared name is worse than no row.

### Never repair a statement in passing

**If the Lean statement needs a hypothesis the prose does not state, that is a
finding about the notes. Report it. Do not add it.**

Adding the missing `[Nontrivial R]` takes a second, produces Lean that
typechecks and proves, and leaves the note exactly as wrong as it was — while
the shared name, and now an audited read-back, certify that the two agree.
Every gate reads green and nobody ever finds out. Mirror the statement *as
written* and it fails loudly instead: it does not typecheck, or the owner's
proof will not go through. That is the value of formalising your own notes.

So an understated row is reported, never written:

```
 7  lem: splitting_lemma   understated — as written it omits that the sequence
                           is short exact; `Function.Exact` needs it. Not offered.
                           → /review-notes algebraic_k_theory to file it
```

The same for strengthening a conclusion, weakening a hypothesis, or silently
picking the Mathlib definition where the note's would fail.

### Rows already in the file

The statement file is **frozen once written**: `/read-back` stamps each
declaration, and the owner's proofs are pinned to each type by `type_of%`. So an
existing row is never touched unless the user names it:

- **Unnamed existing rows** are listed as `kept` and left byte for byte alone —
  even one you now think is wrong. Say what you think in the report instead.
- **`modify <label>`** — the user wants that statement changed, usually because
  the note was fixed. Show the old and the new statement side by side.
- **`delete <label>`** — the user wants it gone.

For a modify or a delete, say what it costs, every time: its read-back block
goes stale and loses its audit on the next `/read-back`, and if `Proof/` pins
it, **that proof stops building**, because `type_of%` no longer matches. That
failure is the design — the owner's proof was of the old statement — but it
turns `lake build` red until they deal with it, so it is the owner's call, made
with the table in front of them.

A new row is appended in note order among the existing ones; appending changes
no other declaration's stamp.

## 4. Propose, and stop

Print a numbered table and **wait**. Nothing has been written yet.

```
category_theory ch01 (圏論) → lean/Math/Study/CategoryTheory/C01.lean

  #  label                              declaration                    kind
  1  def: IsRetract                     IsRetract                      direct
  2  def: IsProjective                  Module.Projective              divergent — Mathlib has it
  3  lem: projective_of_free            projective_of_free             direct
  4  prop: projective_iff_epi_splits    projective_iff_epi_splits      kept
  5  lem: retract_iff_summand           retract_iff_summand            modify — pinned by Proof/; that proof will stop building
  6  lem: splitting_lemma               —                              understated — …  Not offered.
     [blocked #41] thm: five_lemma                                       open finding about its hypotheses

  Math.lean gains: import Math.Study.CategoryTheory.C01

Which rows?
```

Show the Lean statement for any row the user asks to see, or all of them.

## 5. Write

Only the rows the user named.

A new statement file is, in order: the licence header from
`docs/lean-convention.md`; the imports (Mathlib, and earlier chapters'
statement files it uses — never a `Proof/` module); **`set_option autoImplicit
false`**, without which a misspelled variable silently becomes a new universally
quantified argument; a module docstring naming the topic, its `\DocTitle` and
the chapter. An existing file already has all four — do not rewrite them.

Declarations go in the order they appear in the notes, each `:= by sorry`, or
`:= sorry` for a `def` that has no body yet. **No docstrings or comments on the
declarations.** `/read-back` never shows them to its reader, so they could not
leak; but a paraphrase of the note sitting on the declaration is a second copy
of the note in `lean/`, and it drifts.

Add `import Math.Study.<Topic>.C<NN>` to `lean/Math.lean` in the same run if it
is not there.

Then the gate from the repo root — the invocation is in `docs/git-strategy.md`
`## Gates`. A `sorry` warning per declaration is expected; an elaboration error
is not, and means a statement does not typecheck. Fix the statement, or report
it and leave the row out rather than guessing — and never by adding a
hypothesis.

## 6. Report

Print what was written, what was kept, the `sorry` count and the gate's result.
Name any proof in `Proof/` that a modify or delete broke. Then point at the next
step: `/read-back <topic> <chapter>` — every new or changed row is unread until
it has been read back and audited.

Then stop — **this command does not commit.** `/git` does. Say plainly that
every proof is open, and that filling them in is the owner's work in
`lean/Math/Proof/`, not a follow-up this command can be asked for.
