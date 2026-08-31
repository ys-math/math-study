---
description: Add a reference to a topic's bibliography.tex, creating the file and wiring it into main.tex if it has none
argument-hint: "<topic_slug> <citation>  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Write(tex/*/bibliography.tex), Edit(tex/*/bibliography.tex), Edit(tex/*/main.tex), Edit(docs/bib-convention.md), Bash(latexmk:*), Bash(python -m unittest:*), Bash(python scripts/check_bibliography.py:*), Bash(grep:*)
---

File a reference into a topic's `tex/<topic>/bibliography.tex`, creating that
file and `\input`ing it from `main.tex` before the colophon when the topic has
none yet.

Arguments given: $ARGUMENTS

All output is English. **Entries are shown verbatim** — see `## The proposal`.

**The rules are in `docs/bib-convention.md`. Read it first, every run.** It is
the single copy; nothing below restates the key shape, the entry shapes or the
ordering. This file is the workflow.

**This command does not look anything up.** There is no `WebSearch` or
`WebFetch` in `allowed-tools`, and no command in this repo has one. The
citation comes from the user, in the arguments. A citation is a factual claim
about a physical object — the series number, the publisher, the year — and a
wrong one does not look wrong: it produces a well-formed `\bibitem` naming a
book that reads as real. If the arguments do not carry enough to build an
entry, ask for the missing fields; never fill them in.

**This command never edits `tex/*/ch*.tex`.** `Edit(tex/*/ch*.tex)` is absent
from `allowed-tools`. It does not insert `\cite{}` and does not offer to:
deciding which sentence attributes a result to which author is a claim about
the mathematics, inside the owner's prose, and CLAUDE.md's first fence is
exactly that. Report the key at the end and let the user type the `\cite`.

**It cannot commit.** No `git` verb is in `allowed-tools`. See `## Afterwards`.

**It appends; it does not amend.** See `## Already there`.

## Picking the topic

- **Slug given** — handle it.
- **No arguments** — list every topic as a numbered plain list, showing the
  slug, the `\DocTitle` from its `main.tex`, and whether it already has a
  `bibliography.tex`. Stop and wait.
- **Unknown slug** — say so, print the same list, stop.
- **Slug but no citation** — say what is missing, print nothing else, stop.

## Reading

1. `docs/bib-convention.md` — the rules.
2. `tex/<topic>/bibliography.tex`, if it exists — every existing key, and every
   existing entry, as the duplicate set for `## Already there`.
3. `tex/<topic>/main.tex` — whether `bibliography.tex` is already `\input`, and
   where the colophon line is.

A file that exists but is not `\input` is a real state and a silent one: it
compiles fine and appears nowhere. Say so if you find it, and treat the run as
a create for the `main.tex` half.

## The proposal

Show, and then stop:

- the rendered `\bibitem`, **byte for byte as it will be written**
- the key, and — if it carries a year — that it was a collision, naming the key
  it collided with
- which kind it is (book, journal article, arXiv preprint, web resource, or
  one whose locator is being proposed under the convention's fallback), and
  which line-2 markup that gives it
- where it lands in the list, by the entry it follows
- every structural change: creating `bibliography.tex`, inserting the `\input`
  into `main.tex`, widening `{9}` to `{99}`

**Verbatim means verbatim.** Do not tidy 松本幸夫 into "Y. Matsumoto", do not
normalise `$K$-Theory`, do not fix the user's capitalisation. The user approves
what the preview shows, so the preview and the write must be the same bytes; a
helpful adjustment between the two means approving one thing and filing
another.

**Never write on the first turn.** There is more judgement in an append than it
looks — which of `J.`/`Jonathan` the author gets, whether "Graduate Texts in
Mathematics 147" is a series or part of the title, whether the thing is a book
or an article, whether the key collides. Those are the decisions worth showing.

If the citation is of a kind the convention fixes no locator for, build lines 1
and 2 from the grammar — those it settles for every kind, and they need no
approval — then propose **line 3 only**, and say in the proposal that accepting
it also writes that locator into `docs/bib-convention.md`. That is the
convention's own fallback rule and it is not optional: a locator approved and
not recorded means the next entry of the kind gets a different one, with nothing
to report the divergence. The place-of-publication field that was present in one
book entry and absent from another is what that looks like when it happens.

## Already there

Before proposing, check the existing entries two ways:

- the proposed **key** is already used
- the proposed **author and title** already appear, under any key

Either way: show the existing entry, say which check matched, and stop. Do not
file a second copy, and do not update the existing one — `Edit` on
`bibliography.tex` is for appending and for the `{9}` widening, not for
rewriting an entry that was already reviewed and approved once. A mistyped year
in the arguments must produce a refusal naming the existing entry, never a
silent overwrite of a correct one. Fixing a wrong field is a hand edit.

## Applying

Only after the user approves.

**Baseline first, always:**

```bash
latexmk -cd -g tex/<topic>/main.tex
```

That baseline is the only way to tell "this topic was already broken" from "I
broke it", and `-g` is what makes it one: without it latexmk answers "Nothing to
do" from cache for a file that does not compile. `docs/git-strategy.md`
(`## Gates`) is the single copy of this invocation; do not add `-r`. Report a
pre-existing failure and ask whether to continue.

`/label` takes this baseline only for renames. This command takes it every run,
on purpose: it runs a handful of times per topic ever, so the second compile
costs nothing, and a pasted title carrying `$K$-Theory` or a stray brace fails
in a way that looks nothing like its cause.

**Then:**

- **Appending** — insert the `\bibitem` in alphabetical position. Widen `{9}` to
  `{99}` if this is the tenth entry.
- **Creating** — write `bibliography.tex` with the skeleton the convention
  gives, licence header included. `.claude/hooks/guard-edits.sh` blocks the
  write without it, so a missing header is a blocked tool call, not a silent
  hole.
- **Wiring** — insert into `main.tex`, before the colophon:

  ```tex
  \newpage
  \input{bibliography.tex}
  ```

  Match `tex/algebraic_k_theory/main.tex` exactly: the blank line, the
  `\newpage`, the `\input`, then the blank line and `\newpage` that already
  precede `\input{../colophon.tex}`.

## The skeleton guard

**Only when `main.tex` was edited.** `scripts/test_new_topic.py` asserts that
`MAIN_TEMPLATE` in `scripts/new_topic.py` reproduces certain topics' `main.tex`
**byte for byte**, and adding an `\input` line to one of those breaks it.

Read which topics those are rather than remembering them:

```bash
grep -n 'assert_reproduces' scripts/test_new_topic.py
```

The test's own docstring says a topic is dropped from that list once its
`main.tex` "has grown past the skeleton" — so the topic you just edited leaving
the guard is the designed outcome, not damage. What is not this command's to do
is perform it: `scripts/` is a shared path under `docs/git-strategy.md`, and
`Edit(scripts/**)` is absent from `allowed-tools`.

So: run the suite, and report the failure as a finding with its fix.

```bash
python -m unittest discover -s scripts -t scripts -p 'test_*.py'
```

This matters because of what the user will do next. `tex/<topic>/**` commits
straight to `main`, so the natural move is `/git` — whose gate runs this same
suite and will stop with an error that looks unrelated to adding a reference.
Say plainly: the topic left the skeleton guard, `scripts/test_new_topic.py`
must drop it, and that is a `scripts/` change, so it takes a branch and a pull
request.

## Verifying

After the edits, in this order:

1. **Structure** — run the checker on the topic:

   ```bash
   python scripts/check_bibliography.py <topic>
   ```

   It reads the SPDX header, the key shape, the three-line grammar, the line-2
   markup, the ordering and the `{9}` width, so none of those need checking by
   eye. What it does not read is whether the key appears exactly once in the
   topic — check that yourself, and remember the checker is silent about every
   factual field in the entry.
2. **Compile** — the same `latexmk` line. Suppress Overfull/Underfull `\hbox`
   warnings; Japanese in `jlreq` emits them constantly and they bury everything
   else.
3. **The suite**, if `main.tex` changed — `## The skeleton guard`.

If the compile fails, say so with the `-file-line-error` lines and stop. Do not
attempt a second round of fixes on top of a broken build.

Aux files and `main.pdf` are gitignored — leave them, do not run `latexmk -c`.

## Afterwards

Report compactly: the entry, the key, the structural changes, the compile
result, and the suite result when it ran.

```
tex/algebraic_k_theory/bibliography.tex — added bib: Milnor (2 entries)

  J. Milnor,
  ``On manifolds homeomorphic to the 7-sphere'',
  \textit{Annals of Mathematics} \textbf{64} (1956), 399--405.

  placed after bib: Rosenberg  ·  main.tex unchanged
  check_bibliography: OK  ·  latexmk: OK

Cite it with \cite{bib: Milnor}.
```

**Do not commit.** `tex/<topic>/**` commits straight to `main` per
`docs/git-strategy.md`, but that is `/git`'s job — the user may want to adjust a
field by hand first, and an unwanted `\bibitem` is one `git restore` away. Say
the changes are uncommitted; do not offer to commit them.
