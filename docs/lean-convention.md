# Lean convention

The `lean/` half of this repo is a Lake package where the owner learns Lean 4 by
writing proofs. This document is the single copy of the rules that govern it:
`/formalize`, `/label`, `/delete-topic` and `/git` all point here and none of
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
    └── Study/           ← formalising the notes in tex/
```

`Learn/` and `Study/` split on **lifetime**, which is why they are separate and
not one flat namespace. A `Learn/` file is worked through once and then frozen;
a `Study/` file grows for as long as the topic it mirrors does.

**`docs/naming-convention.md` owns what the files are called** — the
`UpperCamelCase` rule, the `C<NN><ChapterTitle>` form for curriculum files, and
the slug-to-module transformation that makes `tex/algebraic_k_theory/` into
`Math/Study/AlgebraicKTheory.lean`. It covers both halves of the repo in one
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
the second unit stays open.

Lean reports `sorry` as a warning, so `lake build` succeeds and `lean.yml` stays
green. Nothing counts them, fails on them or nags about them. CI is checking one
thing: that every file still elaborates.

This is why `lean.yml` passes no `--wfail`. Adding it would fail the build on
unused variables and deprecation notices too, which is a much blunter rule than
the one intended.

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
Copyright (c) 2026 @ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: @ys-math
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
3. `lake --dir=lean update` — rewrites `lake-manifest.json`.
4. `lake --dir=lean exe cache get`, then the gate, and fix what the bump broke.

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

**Statements, never proofs.** Claude writes the licence header, the imports, and

```lean
theorem projective_of_free ... := by sorry
```

Everything after `by` is the owner's. Translating a proposition into a Lean
statement is a Mathlib API question — which definition, which typeclass
assumptions — and Claude is useful there. Producing the proof is the thing being
learned, and an agent that does it removes the entire point of the exercise.

Claude may still read errors, explain why the elaborator is unhappy, name the
Mathlib lemma that would close a goal, and describe a tactic. It stops at
writing the tactic block into the file.

`Math/Learn/**` is the owner's alone. Those files exist to be struggled with.

This is a layer-2 rule, in `docs/agent-system.md`'s terms: advisory, not
mechanical. No hook can tell a statement from a proof. `/formalize` narrows it
where it can — its `allowed-tools` reach only `lean/Math/Study/**` — but the
rule itself is kept, not enforced.
