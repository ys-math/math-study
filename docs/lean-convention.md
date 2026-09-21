# Lean convention

The `lean/` half of this repo is a Lake package where the owner learns Lean 4 by
writing proofs. This document is the single copy of the rules that govern it:
`/formalize`, `/read-back`, `/label` and `/tutor` all point here and none of
them restate it.

The prose half — `tex/` — is notes about mathematics. This half is mathematics
the kernel has checked. They are deliberately not the same artifact, and the
only thing joining them is a naming rule, `## The shared name` below.

## The shape

One Lake package, `math`, holding one library, `Math`.

```
lean/
├── lakefile.toml        ← package, library, the pinned Mathlib require
├── lean-toolchain       ← the Lean version, matching the Mathlib tag
├── lake-manifest.json   ← the resolved revision, written by `lake update`
├── Math.lean            ← the root module: imports every file below
└── Math/
    ├── Learn/           ← working through a curriculum
    │   ├── MIL/         ← Mathematics in Lean
    │   └── TPiL/        ← Theorem Proving in Lean 4
    ├── Study/           ← formalising the notes in tex/: statements only
    │   └── <Topic>/
    │       ├── C03.lean            ← chapter 3's statements, all `sorry`
    │       └── C03.readback.tex    ← their blind English read-back
    └── Proof/           ← the owner's proofs of those statements
        └── <Topic>/
            └── C03.lean
```

`Learn/` and `Study/` split on **lifetime**, which is why they are separate and
not one flat namespace. A `Learn/` file is worked through once and then frozen;
a `Study/` directory grows for as long as the topic it mirrors does, one module
per chapter, `C03.lean` beside `tex/<topic>/ch03.tex`.

`Study/` and `Proof/` split on **authorship**, and that is the subject of
`## Statements and proofs` below.

**`docs/naming-convention.md` owns what the files are called** — the
`UpperCamelCase` rule, the `C<NN><ChapterTitle>` form for curriculum files, and
the slug-to-module transformation that makes `tex/algebraic_k_theory/` into
`Math/Study/AlgebraicKTheory/`. It covers both halves of the repo in one
place, which is the point of it; this document does not restate any of it.

**`Math.lean` is maintained by hand.** A file with no `import` line there still
works in your editor and is still invisible to `lake build`, so CI reports the
repo green while the file rots. Add the import in the same commit as the file.

## The shared name

A formalised statement and the `\label{}` of the theorem it formalises **are the
same string**:

```tex
\begin{lemma} \label{lem: projective_of_free}
```
```lean
theorem projective_of_free ...
```

The label's prefix (`lem: `) is dropped — it encodes the LaTeX environment,
which Lean states differently — and the body is reused verbatim. This works
because `docs/label-convention.md` already takes its naming from Mathlib:
`UpperCamelCase` for types, `Is` + `UpperCamelCase` for properties,
`snake_case` with `_of_` and `_iff_` for statements. That document is the owner
of the naming rules; nothing here overrides it.

There is **no cross-reference** — no comment naming a label, no `\leanref` macro
in `tex/preamble.tex`, no checker. A pointer would be a second copy of the fact
that these two things correspond, and this repo has already been bitten by
copies drifting. One string cannot drift from itself.

**When the correspondence is not one-to-one, do not reuse the name.** This is
the common case, not the exception:

- the formalisation uses Mathlib's definition rather than the note's, and the
  real content becomes an `iff` between them;
- one prose proposition becomes two lemmas and an instance;
- the Lean statement is strictly more general, because that is what Mathlib's
  API made natural.

In all three the shared name would assert an equality that does not hold. Name
the Lean declaration for what it actually says. Silence is the honest answer,
and it costs nothing: the file it lives in already says which topic it belongs
to.

Renaming a `\label{}` therefore has a second consumer. `/label` greps `lean/`
before proposing one, and the rename is one edit covering the `\label{}`, every
`\cref{}` site and the Lean declaration.

## `sorry`

**Allowed, and the build must be green.**

Stating a theorem and proving it are separate units of work, and the first is a
real commit — often the more valuable one, since translating 命題 1.4 into a
Lean statement is where the note's unstated hypotheses surface. `sorry` is how
the second unit stays open, and `Proof/` is where it is closed.

Lean reports `sorry` as a warning, so `lake build` succeeds and `lean.yml` stays
green. Nothing counts them, fails on them or nags about them. CI is checking one
thing: that every file still elaborates.

This is why `lean.yml` passes no `--wfail`. Adding it would fail the build on
unused variables and deprecation notices too, which is a much blunter rule than
the one intended.

## Statements and proofs

A statement and its proof live in **different files**, as on prove2.me: the
statement in `Study/<Topic>/C<NN>.lean`, where every declaration is proved by
`sorry`, and the proof in `Proof/<Topic>/C<NN>.lean`, pinned to it by type:

```lean
-- lean/Math/Proof/AlgebraicKTheory/C03.lean
import Math.Study.AlgebraicKTheory.C03

theorem projective_of_free.proof : type_of% @projective_of_free := by
  ...
```

`type_of% @projective_of_free` elaborates to the statement's type exactly, so
the proof is of *that* statement or it does not build. A proof may use other
statements, proved or not — prove2.me's proof-sketch — and
`#print axioms projective_of_free.proof` names the `sorry` still underneath it.

The split makes three things structural that were conventions:

- **A statement changes only through `/formalize`.** The owner never edits the
  statement file to make a proof go through — there is nowhere in `Proof/` to
  weaken it, because `type_of%` fixes the type. Stuck on a missing hypothesis
  means the note is wrong, which is the finding; the fix is in the note, then a
  `/formalize … modify`.
- **An audited read-back stays valid while the owner proves.** Proving touches
  only `Proof/`, which the read-back never reads.
- **The fence is a path.** Claude writes `Study/**` and nothing under
  `Proof/**` — see `## What Claude may write here`.

A statement changed by `/formalize` breaks every proof pinned to it, loudly, in
`lake build`. That is the design: the proof was of the old statement.

`Math.lean` imports both trees. A `Proof/` module imports its own chapter's
`Study/` module and any other it uses, never the reverse: statements must not
depend on proofs.

## Read-back

A statement file is audited by reading it back into English **without the
notes**, and comparing the English with the chapter by eye — prove2.me's
"compare math to math, not code". `/read-back` runs it; the rules are here.

- **The reader is blind by construction.** `.claude/agents/read-back.md` is a
  subagent that starts with no conversation and whose one tool is `Write`, so
  it cannot have seen `tex/`. It is shown not the source but a dump from
  `scripts/lean_statements.py` of what Lean *elaborated* — auto-bound
  variables, coercions and instance arguments visible — with theorem names
  replaced by `T<n>`, because a theorem's name is its `\label{}` body. It
  writes literally: every hypothesis Lean has appears in the English, and
  anything odd on the Lean's own terms becomes a *Reader note*.
- **The read-back is committed**, as `Study/<Topic>/C<NN>.readback.tex`: a
  standalone English `article` with only `amsmath` and `amssymb`, none of the
  notes' macros. `/read-back` compiles it into `lean/.lake/readback/` as a
  check; the PDF is never committed. Being a `.tex`, committing one wakes
  `build-pdf.yml`'s `**.tex` filter, which finds no topic under `tex/` changed
  and rebuilds nothing.
- **Every block carries a stamp**:
  `% readback: <declaration> sha=<hash> audited=no`. The hash is of the
  declaration as elaborated, folded with the hashes of the same chapter's
  definitions it mentions, so redefining `IsFoo` stales every theorem stated
  in terms of it. A renamed declaration keeps its hash; a proof never affects
  one.
- **`audited=yes` is the owner's word, and only the owner's.** It is set by
  hand, or by Claude on an explicit instruction naming the blocks — never on
  Claude's initiative, and never after Claude compared anything to the notes.
- **A stale block loses its audit.** When the hash no longer matches,
  `/read-back` reads that declaration again and files it as `audited=no`.
  Unchanged blocks are kept byte for byte.

A block that does not match the note is a finding for one side or the other:
the note is wrong (`/review-notes`), or the Lean is (`/formalize` with the row
named as `modify`). Deciding which is the owner's.

Nothing checks audits. No workflow fails on `audited=no` or on a stale block,
for the reason `docs/repo-structure.md` declines a coverage check: a study repo
is not a backlog. `python scripts/lean_statements.py status` reports them.

`scripts/lean_statements.py` reads nothing under `tex/` and the reader sees
nothing of it, so none of this joins the halves by machinery; the only join is
still the shared name, and the comparison.

## Licensing

`lean/**` is **Apache 2.0** — a third licence, alongside the repo's MIT and
CC BY-NC-ND. `README.md`'s path table is authoritative and lists it.

Apache rather than MIT because it is what the entire Lean ecosystem uses:
Mathlib, Mathematics in Lean and Theorem Proving in Lean are all Apache 2.0, and
Mathlib requires Apache 2.0 of contributions. Anything that ever goes upstream
needs to already be under it.

Every `.lean` file carries Mathlib's header, with one deviation:

```lean
/-
Copyright (c) 2026 ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: ys-math
-/
```

Mathlib's own wording is "the file LICENSE", which is right in Mathlib and wrong
here — this repo's `LICENSE` is the MIT text. The header names
`LICENSE-APACHE-2.0` instead.

`.claude/hooks/guard-edits.sh` refuses to write a `.lean` file without it. That
is mechanical rather than advisory for the same reason the chapter headers are:
`lean/Math/**` commits straight to `main`, so no pull request ever reads one.

## Mathlib

Pinned to a **release tag**, in two files that must agree:

| file | holds |
| --- | --- |
| `lean/lakefile.toml` | `rev = "v4.32.2"` in the Mathlib `[[require]]` |
| `lean/lean-toolchain` | `leanprover/lean4:v4.32.2` |

The toolchain is whatever the Mathlib tag's own `lean-toolchain` says. Take it
from there, never from what happens to be installed locally.

A tag rather than `master` for two reasons. `lake exe cache get` only ever hits
on a revision Mathlib's CI has built, which a tag always is. And master moves
daily, so proofs written last week break under you — real Lean practice, and a
bad thing to fight while learning the basics.

### Bumping it

1. Read the new tag's `lean-toolchain`:
   `gh api "repos/leanprover-community/mathlib4/contents/lean-toolchain?ref=<tag>" -q .content | base64 -d`
2. Write that into `lean/lean-toolchain` and the tag into `lakefile.toml`'s `rev`.
3. `cd lean && lake update` — rewrites `lake-manifest.json`.
4. `cd lean && lake exe cache get`, then the gate, and fix what the bump broke.

Both from inside `lean/`, for the reason `docs/git-strategy.md` `## Gates`
gives: elan picks the toolchain from the working directory, and running these
from the repo root resolves the *old* default rather than the `lean-toolchain`
you just wrote in step 2 — which is exactly the file a bump changes.

All three files are branch-and-PR paths (`docs/git-strategy.md`), so this lands
through a pull request that `lean.yml` checks. Deprecations are the usual
breakage; fix them in the same PR rather than leaving `main` warning.

There is no scheduled bump. Bump when you want something Mathlib has added.

## Gates and CI

Before committing anything under `lean/`, the gate is a `lake build`.
**`docs/git-strategy.md` `## Gates` holds the invocation**, alongside the
`latexmk` one, and is the single copy of both; this document does not restate
it.

The build is incremental, so it is about 3 seconds when warm — Lean rebuilds
only what changed and its dependents, and Mathlib never rebuilds. Cold, or
straight after a toolchain bump, it is minutes; that is the branch path, where
`lean.yml` on the pull request is the real authority anyway.

`.lake/` is gitignored. Never commit it, never clean it — it is several
gigabytes and every rebuild reuses it.

`.github/workflows/lean.yml` runs on pushes to `main` and on pull requests, both
filtered to `lean/**`. It commits nothing.

## What Claude may write here

**Statements, never proofs.** Claude writes the licence header, the imports,
`set_option autoImplicit false`, and

```lean
theorem projective_of_free ... := by sorry
```

into `Study/`, and the read-back beside it. Everything after `by` is the
owner's, and so is every file under `Proof/`.

Every statement file sets `autoImplicit` off, just after its imports. Lean's
default is on and `lakefile.toml` leaves it so — `Learn/` follows books that
rely on it — but in a statement it turns a misspelled variable into a new
universally quantified argument, silently. Translating a proposition into a Lean
statement is a Mathlib API question — which definition, which typeclass
assumptions — and Claude is useful there. Producing the proof is the thing being
learned, and an agent that does it removes the entire point of the exercise.

Claude may still read errors, explain why the elaborator is unhappy, name the
Mathlib lemma that would close a goal, and describe a tactic. It stops at
writing the tactic block into the file.

`Math/Learn/**` is the owner's alone. Those files exist to be struggled with.

### What holds it

`.claude/settings.json` denies every Write and Edit under `lean/Math/Proof/**`
before it happens, and `.claude/hooks/guard-edits.sh` repeats that as a
backstop. The same hook refuses a Write or Edit under `lean/Math/Study/**`
whose tactic blocks are not exactly `sorry`. It reads only
the text that call wrote — `.content` for Write, `.new_string` for Edit — never
the file on disk. Statement files written before the split may still hold
proofs the owner typed there, and those are never what trips it; a whole-file
overwrite of them *is* caught, which is the point.

It is a `PostToolUse` hook, so the write has already landed when it blocks: the
message goes back to Claude, and removing what was written is Claude's next
action rather than the hook's.

Two gaps, both deliberate, neither an invitation:

- **The test is syntactic.** Every `by` must be followed by `sorry`; a term-mode
  proof would pass. Closing that would mean refusing ordinary `def`s, which
  `/formalize` needs when a notion has no Mathlib counterpart.
- **`Math/Learn/**` is unguarded.** The rule there is that Claude should not be
  writing at all, which is a different rule, and a hook broad enough to enforce
  it would block asking for help with an exercise.

### What nothing holds

**Never repair a statement while translating it.** If the Lean needs a
hypothesis the prose omits, that is a finding about the notes — report it, do not
add it.

No hook can see this one. Adding the missing assumption yields Lean that
typechecks and proves, notes that stay wrong, and a shared name certifying the
two agree; the build passes, `sorry` is honest, CI is green, and the defect is
now carved into a verified artifact. Mirroring the statement as written fails
loudly instead, which is the entire reason to formalise your own notes.

The read-back narrows this gap without closing it. A hypothesis `/formalize`
added shows up in the blind English as a clause the note does not have — but
only to an owner who reads the two side by side, which is why `audited=yes` is
theirs to set.

This is the layer-2 half, in `docs/agent-system.md`'s terms, and it is the one
worth reading twice.
