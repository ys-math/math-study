# CLAUDE.md

Mathematics study notes written in LaTeX. One topic is one directory under
`tex/`, holding a `main.tex` and its `ch0N.tex` chapters; every topic `\input`s
the shared `tex/preamble.tex` and `tex/colophon.tex`. `pdf/` and two blocks of
`README.md` are build artifacts, not sources.

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

## Licensing

`tex/*/ch*.tex` and `pdf/*.pdf` are CC BY-NC-ND 4.0; everything else is MIT —
including the shared `tex/preamble.tex`, `tex/colophon.tex` and the generated
`tex/*/main.tex`. The root `LICENSE` is the MIT one, so an unmarked file reads
as MIT and the CC side is the one that has to be marked:

- **A new chapter file needs `% SPDX-License-Identifier: CC-BY-NC-ND-4.0` on
  line 1.** `new_topic.py` stamps the `ch01.tex` it creates; a `ch02.tex` added
  by hand is on whoever adds it. **Nothing in CI checks this** — `validate.yml`
  runs only on pull requests, and `tex/<topic>/**` never goes through one.
- The path table under `## ライセンス` in `README.md` is authoritative, so a
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
  commit. `scripts/test_new_topic.py` asserts the template reproduces the files
  on disk byte for byte and will fail otherwise.
- **Adding a shared `.tex` that all topics `\input`** means adding it to the
  `SHARED` regex in `.github/workflows/build-pdf.yml`. That regex is how the
  workflow decides to rebuild everything; miss it and touching the new file
  rebuilds nothing, with a green CI run.

## Commands

Run everything from the repo root — the scripts resolve `README.md` and `tex/`
relative to the working directory.

```bash
python -m unittest discover -s scripts -t scripts -p 'test_*.py'
python scripts/new_topic.py sheaf_theory --title 層論
latexmk -cd -g tex/<topic>/main.tex   # flags: docs/git-strategy.md, ## Gates
```

Gate before committing, per `docs/git-strategy.md` `## Gates`. One consequence
that section omits: the `scripts/` tests also run as a step in
`update-readme.yml`, so a failure there blocks the README regeneration, not just
your commit. Extend them when behaviour changes — a new `SYMBOLS` entry in
`scripts/latex_unicode.py`, any `MAIN_TEMPLATE` edit.

## Slash commands — only the surprises

The six commands in `.claude/commands/` describe themselves; read the one you
are running. What you would not guess from outside:

- **`/delete-topic` commits and pushes on its own** — every other command leaves
  the tree for `/git`. A deleted-but-uncommitted topic is the one state where
  the owner's prose is unrecoverable.
- **`/review-notes` never edits `tex/`**, and `reviews/` is gitignored and
  overwritten every run: never cite a report as a record, and act on a finding
  only when the owner asks for that finding to be fixed.
- **`docs/label-convention.md` binds every `\label{}` you write**, whether or
  not you got there through `/label`.

**Renaming a topic is not automated, and CI will not clean up after you:**

1. `git mv` the `tex/<topic>/` directory.
2. `git rm pdf/<topic>.pdf` — the build only ever copies PDFs into `pdf/`, so an
   orphan lingers forever otherwise.
3. Update `\TexRepo` inside the moved `main.tex`; it embeds the directory name.

## Git

`docs/git-strategy.md` is the specification and `/git` / `/git-merge` implement
it — read it before doing anything by hand. What binds regardless:

- **Shared paths go on a branch and through a PR** — `scripts/`, `.github/`,
  `.latexmkrc`, `tex/preamble.tex`, `tex/colophon.tex`. They can break every
  topic at once. Everything else, `tex/<topic>/**` included, commits straight to
  `main`.
- **Path-scoped `git add` only**, never `-A` or `.`; the working tree may hold
  someone else's work in progress.
- **Never force-push and never rewrite pushed history.** Correct a bad commit on
  `main` with a follow-up commit.
- **`Co-Authored-By: Claude` only on what Claude wrote** — `scripts/`,
  `.github/`, `docs/`, `.claude/`, `tex/preamble.tex`, `tex/colophon.tex` — and
  **never on `tex/<topic>/**`**.

CI pushes to `main` after every push of yours, so `git pull --rebase` first. It
cannot conflict: the bots only touch `pdf/*.pdf` and the generated `README.md`
blocks.
