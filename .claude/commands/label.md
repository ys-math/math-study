---
description: Propose \label{} names for a topic's theorem environments, then apply the ones you pick
argument-hint: "[topic_slug ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Edit(tex/**), Bash(latexmk:*), Bash(grep:*)
---

Propose a `\label{}` for every unlabelled theorem environment in a topic, show
them as a numbered table, and apply the ones the user picks.

Arguments given: $ARGUMENTS

All output is English.

**The naming rules are in `docs/label-convention.md`. Read it first, every run.**
It is the single copy; nothing below restates it. This file is the workflow.

**This command edits `tex/` only after the user picks rows from the table.**
Never apply on the first turn, however obvious the names look — the labels are
permanent in a way the surrounding prose is not, and a label the owner did not
choose is one they will read a hundred times.

## Picking the topics

- **Slugs given** — handle each in order.
- **No arguments** — list every topic as a numbered plain list, showing the slug,
  the `\DocTitle` from its `main.tex`, and `(empty)` where every chapter file is
  empty. Stop and wait. Never default to all of them.
- **Unknown slug** — say so, print the same list, stop.
- **No environments at all** in the topic — say so and stop. Nothing to propose.

## Reading

Always the whole topic, never the single chapter the user is looking at. Labels
must be unique across the document, and a `\cref` in `ch03.tex` can point at a
label defined in `ch01.tex` — a rename that does not see it breaks the build.

1. `docs/label-convention.md` — the rules.
2. `tex/preamble.tex` — the seven `\declaretheorem` environments and their
   `\crefname`s, so the environment list is read off the source and not from
   memory.
3. The topic's `main.tex` — which chapters are `\input`, in what order.
4. Every `ch0N.tex` in that order.

Collect, before proposing anything:

- every environment and whether it already has a label
- every existing label, as the uniqueness set
- every `\cref{}` site, keyed by the label it names

## What to propose

**Unlabelled environments** — a new label, per the convention.

**Labelled environments** — a rename **only when the existing label violates the
convention**: a wrong or missing prefix, a missing `: ` separator, spaces in the
body, wrong casing, a missing `Is` on a property.

A label that follows the convention is left alone. Do not propose a rename
because a different name would read better; do not mention that you would have
named it differently. That restraint is what makes the table approvable at a
glance, and CLAUDE.md's rule against fixing the owner's files in passing points
the same way.

If a proposed name collides with an existing label, disambiguate with a
namespace — that is what the convention's "load-bearing" case means — and say in
the row that it was a collision.

### Confidence

Two of the rules are judgement calls: **which casing a definition takes**
(structure / property / data), and **whether a statement has a genuinely
established name**. Mark a row `[Low]` when the call was close, `[Medium]` when it
leaned one way. Leave the marker off entirely when the row is not in doubt.

Do not hedge to be safe. A table where every row is marked tells the user
nothing, and the point of the marker is to say *these three* are worth arguing
about.

## The table

Numbered, ordered by `file:line`, continuous across all chapters of the topic.

```
tex/algebraic_k_theory/ — 4 environments, 2 to name, 2 renames

 №  location      env         statement                          proposed
 1  ch01.tex:5    definition  R 加群 P が射影加群であること      def: IsProjective
                              (was: def: projective_module)
 2  ch01.tex:18   lemma       短完全列の分裂条件 (1)-(4) の同値  lem: splitting_lemma  [Medium]
 3  ch01.tex:42   proposition 射影加群の特徴づけ (1)-(3)         prop: projective_tfae
                              (was: prop: characterization of projective modules, 0 \cref sites)
```

Each row carries: number, `file:line`, environment, a short excerpt so the user
can tell which statement it is, and the proposed label. A rename adds a second
line with the old label and how many `\cref` sites move with it — that count is
the blast radius, and the user is entitled to see it before saying yes.

The excerpt is Japanese, because the notes are. Everything else is English.

Then stop and ask which to apply. The user answers with numbers ("1, 3"), a
range, "all", or a correction ("3 but call it `prop: projective_iff_summand`").
A correction is an instruction, not a discussion: take the name given, apply it
as written, and do not argue the convention at them.

## Applying

Only the rows the user named.

- **New label** — insert on the `\begin{env}` line, one space after it, as the
  convention specifies.
- **Rename** — change the `\label{}` and every `\cref{}` site naming it, in the
  same batch of edits. Never one without the other.

If any row is a rename, **compile the topic before touching anything**:

```bash
latexmk -cd -g tex/<topic>/main.tex
```

That baseline is the only way to tell "this topic was already broken" from "I
broke it", and `-g` is what makes it one: without it latexmk answers "Nothing to
do" from cache for a file that does not compile, and the baseline passes on a
document that is already broken — the exact confusion it exists to prevent.
`docs/git-strategy.md` (`## Gates`) is the single copy of this invocation; do not
add `-r`. Report a pre-existing failure and ask whether to continue; do not
silently proceed to edit a document that does not build.

### Verifying

After the edits, in this order:

1. **Static gate** — for each renamed label, `grep -rn 'cref{<old>}' tex/<topic>/`
   returns nothing; no two labels in the topic are equal. This is instant and
   catches the actual failure mode.
2. **Compile** — the same `latexmk` line. Read the log for undefined references
   and missing labels. Suppress Overfull/Underfull `\hbox` warnings; Japanese in
   `jlreq` emits them constantly and they bury everything else.

Aux files and `main.pdf` are gitignored — leave them, do not run `latexmk -c`.

If the compile fails or a reference is undefined, say so with the
`-file-line-error` lines and stop. Do not attempt a second round of fixes on top
of a broken build.

## Afterwards

Report compactly: which rows were applied, the grep result, the compile result.

```
Applied 1, 3.

  ch01.tex:5   def: IsProjective        (was def: projective_module)
  ch01.tex:42  prop: projective_tfae    (was prop: characterization of projective modules)

grep: no stale \cref sites
latexmk: OK, no undefined references
```

**Do not commit.** `tex/<topic>/**` commits straight to `main` per
`docs/git-strategy.md`, but that is `/git`'s job — the user may want to adjust a
name by hand first, and nothing here is unrecoverable if left in the working
tree. Say the changes are uncommitted; do not offer to commit them.
