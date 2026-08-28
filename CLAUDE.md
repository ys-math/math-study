# CLAUDE.md

Mathematics study notes written in LaTeX. One topic is one directory under
`tex/`, holding a `main.tex` and its `ch0N.tex` chapters; every topic `\input`s
the shared `tex/preamble.tex` and `tex/colophon.tex`. `pdf/` and two blocks of
`README.md` are build artifacts, not sources.

`lean/` is the other half: a Lake package where the owner learns Lean 4 by
formalising those notes. **`docs/lean-convention.md` owns everything about it**
and is not summarised here — read it before touching `lean/`.

The two halves share no build dependency, on purpose. **Read
`docs/repo-structure.md` before writing anything that couples them** — a script
that extracts one from the other, a `\leanref` macro, a coverage check. Each of
those was declined for a reason recorded there.

Your job in this repo is the Python tooling in `scripts/`, the CI in
`.github/workflows/`, and repo chores. See `README.md` for the human-facing
workflow and the script docstrings for design rationale.

**This file carries only what you cannot find at the moment you need it** — the
surprises, and the rules nothing enforces. Everything routine lives in the file
that owns it (`docs/`, `.claude/commands/`); do not restate it here, because a
second copy is a copy that drifts.

## The mathematics is not yours to write

The prose in `tex/*/ch0N.tex` is authored by the repo owner. Edit it only when
asked to, and never rewrite, reformat or "fix" it in passing while doing tooling
work.

The same fence runs through `lean/`, in a different place: **statements yes,
proofs never.** You may write the header, the imports and
`theorem foo : ... := by sorry`; everything after `by` is the owner's, and
`Math/Learn/**` is theirs entirely. Naming a Mathlib lemma that would close a
goal is help; typing the tactic block is taking the exercise away.

`guard-edits.sh` enforces this under `lean/Math/Study/**` — every tactic block
must be exactly `sorry` — but only there, and only syntactically. `Math/Learn/**`
is unguarded, and a term-mode proof would pass. Both gaps are real; neither is
permission.

And the rule the hook cannot reach at all: **never repair a statement while
translating it.** A hypothesis the prose omits is a finding about the notes, not
something to add in passing — adding it produces Lean that proves, notes that
stay wrong, and a shared name certifying they agree. That one reads green
everywhere.

## Licensing

Three licences. `tex/*/ch*.tex`, `tex/*/bibliography.tex` and `pdf/*.pdf` are CC
BY-NC-ND 4.0; `lean/**` is Apache 2.0; everything else is MIT — including the
shared `tex/preamble.tex`, `tex/colophon.tex` and the generated
`tex/*/main.tex`. The root `LICENSE` is the MIT one, so an unmarked file reads
as MIT and the other two are the ones that have to be marked:

- **A new chapter file needs `% SPDX-License-Identifier: CC-BY-NC-ND-4.0` on
  line 1.** `new_topic.py` stamps the `ch01.tex` it creates; a `ch02.tex` added
  by hand is on whoever adds it. **Only `guard-edits.sh` checks this** — no workflow
  step looks at the header, whether or not the file reaches a pull request.
- **A new `.lean` file needs the Apache header**, whose text is in
  `docs/lean-convention.md`. This one *is* checked, by `guard-edits.sh`. Note it
  names `LICENSE-APACHE-2.0`, not `LICENSE` as Mathlib's own wording does — the
  root `LICENSE` here is the MIT text, so copying Mathlib's header verbatim
  points at the wrong licence.
- The path table under `## License` in `README.md` is authoritative, so a
  missing header is untidy rather than a licensing hole. Keep the table right.

## Generated artifacts — never hand-edit

- `pdf/*.pdf` — committed by `.github/workflows/build-pdf.yml`.
- The `<!-- BEGIN PDF LINKS -->` and `<!-- BEGIN TREE -->` blocks in `README.md`
  — rewritten by `.github/workflows/update-readme.yml`. Prose outside the
  markers is yours to edit.

Change the `.tex` sources and let CI regenerate. Both generators read
`git ls-files`, so a new topic is invisible to them until it is tracked.

## Coupling rules

These are the changes that break silently, days later:

- **Editing the topic skeleton** means editing `MAIN_TEMPLATE` in
  `scripts/new_topic.py` *and* every existing `tex/*/main.tex` in the same
  commit. `scripts/test_new_topic.py` asserts the template reproduces 3 of them
  byte for byte — `topology`, `category_theory` and `manifold` — so a partial
  update passes; check the rest by hand. A topic drops out of that list when its
  `main.tex` grows past the skeleton, which is what `lambda_calculus` and
  `algebraic_k_theory` have already done and what `/bib` does to a topic when it
  wires in a `bibliography.tex`.
- **Adding a shared `.tex` that all topics `\input`** means adding it to the
  `SHARED` regex in `.github/workflows/build-pdf.yml`. That regex is how the
  workflow decides to rebuild everything; miss it and touching the new file
  rebuilds nothing, with a green CI run.
- **Adding a `.lean` file** means adding its `import` to `lean/Math.lean` in the
  same commit. Lake builds what the root module reaches, so an unimported file
  compiles in your editor, is skipped by `lake build`, and rots behind a green
  CI run. Nothing checks this.
- **Adding a command, hook, workflow or `docs/` file** means listing it in
  `docs/agent-system.md` in the same commit — and a command in `README.md`'s
  table as well. `scripts/test_agent_docs.py` compares those tables against the
  directories and fails otherwise. It also checks every count written in
  digits, which is why "all 8 topics" is spelled that way and why nothing says
  how many commands there are: a table two lines below already does.

## Commands

Run everything from the repo root — the scripts resolve `README.md` and `tex/`
relative to the working directory.

```bash
python -m unittest discover -s scripts -t scripts -p 'test_*.py'
python scripts/new_topic.py sheaf_theory --title 層論
latexmk -cd -g tex/<topic>/main.tex   # flags: docs/git-strategy.md, ## Gates
cd lean && lake build                 # same section owns this one
```

Gate before committing, per `docs/git-strategy.md` `## Gates`. One consequence
that section omits: the `scripts/` tests also run as a step in
`update-readme.yml`, so a failure there blocks the README regeneration, not just
your commit. Extend them when behaviour changes — a new `SYMBOLS` entry in
`scripts/latex_unicode.py`, any `MAIN_TEMPLATE` edit.

## Slash commands — only the surprises

The commands in `.claude/commands/` describe themselves; read the one you are
running, and `docs/agent-system.md` for what they may touch. What you would not
guess from outside:

- **`/delete-topic` commits and pushes on its own** — every other command leaves
  the tree for `/git`. A deleted-but-uncommitted topic is the one state where
  the owner's prose is unrecoverable.
- **`/review-notes` never edits `tex/`** — it has no write tool — and it files
  findings as GitHub issues rather than a report. Act on one only when the owner
  asks for that finding to be fixed.
- **The open issues are the record, `issues/` is not.** `/issues` renders a
  local worklist that is gitignored and overwritten every run; a finding lives
  and dies on GitHub. Never cite the worklist as evidence a finding is still
  open — regenerate it, or ask `gh`.
- **`/formalize` writes statements, never proofs**, and cannot commit. It is the
  fence above turned into an `allowed-tools` line as far as one can go.
- **`docs/issue-convention.md` binds every issue you file**,
  **`docs/label-convention.md` binds every `\label{}` you write**,
  **`docs/bib-convention.md` binds every `\bibitem{}` you write**,
  **`docs/lean-convention.md` binds every `.lean` file**, and
  **`docs/naming-convention.md` binds every path you create or rename**, in both
  halves of the repo — whether or not you got there through `/review-notes`,
  `/label`, `/bib` or `/formalize`.

**A `\label{}` is now two names, not one.** The label body doubles as the Lean
declaration name that formalises it, so renaming one is a rename of the
`\label{}`, every `\cref{}` site *and* the declaration in `lean/Math/Study/`.
`docs/lean-convention.md` `## The shared name` has the rule, including when the
two deliberately diverge.

**Renaming a topic is not automated, and CI will not clean up after you:**

1. `git mv` the `tex/<topic>/` directory.
2. `git rm pdf/<topic>.pdf` — the build only ever copies PDFs into `pdf/`, so an
   orphan lingers forever otherwise.
3. Update `\TexRepo` inside the moved `main.tex`; it embeds the directory name.
4. `git mv` the mirror at `lean/Math/Study/<Topic>.lean` if it exists, and fix
   its `import` in `lean/Math.lean`. A stale import fails `lake build` outright,
   so this one at least tells you.

## Git

`docs/git-strategy.md` is the specification and `/git` / `/git-merge` implement
it — read it before doing anything by hand. What binds regardless:

- **Shared paths go on a branch and through a PR** — `scripts/`, `.github/`,
  `.latexmkrc`, `tex/preamble.tex`, `tex/colophon.tex`, and `lean/`'s build
  configuration (`lakefile.toml`, `lean-toolchain`, `lake-manifest.json`). They
  can break every topic, or every proof, at once. Everything else —
  `tex/<topic>/**` and `lean/Math/**` included — commits straight to `main`.
- **Path-scoped `git add` only**, never `-A` or `.`; the working tree may hold
  someone else's work in progress.
- **Never force-push and never rewrite pushed history.** Correct a bad commit on
  `main` with a follow-up commit.
- **`Co-Authored-By: Claude` only on what Claude wrote** — `scripts/`,
  `.github/`, `docs/`, `.claude/`, `README.md`, `CLAUDE.md`,
  `tex/preamble.tex`, `tex/colophon.tex`, and
  `lean/`'s build configuration — and **never on `tex/<topic>/**` or
  `lean/Math/**`**. A statement `/formalize` typed is still the owner's
  mathematics, only transported; the proof under it will be theirs outright.

CI pushes to `main` after every push of yours, so `git pull --rebase` first. It
cannot conflict: the bots only touch `pdf/*.pdf` and the generated `README.md`
blocks.
