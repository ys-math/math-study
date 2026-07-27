# CLAUDE.md

Mathematics study notes written in LaTeX. One topic is one directory under
`tex/`, holding a `main.tex` and its `ch0N.tex` chapters; every topic `\input`s
the shared `tex/preamble.tex` and `tex/colophon.tex`. `pdf/` and two blocks of
`README.md` are build artifacts, not sources.

Your job in this repo is the Python tooling in `scripts/`, the CI in
`.github/workflows/`, and repo chores. See `README.md` for the human-facing
workflow and the script docstrings for design rationale.

## The mathematics is not yours to write

The prose in `tex/*/ch0N.tex` is authored by the repo owner. Edit it only when
asked to, and never rewrite, reformat or "fix" it in passing while doing tooling
work.

## Generated artifacts — never hand-edit

- `pdf/*.pdf` is committed by `.github/workflows/build-pdf.yml`.
- The two marker-delimited blocks in `README.md` (`<!-- BEGIN PDF LINKS -->`,
  `<!-- BEGIN TREE -->`) are rewritten by `.github/workflows/update-readme.yml`.

Change the `.tex` sources instead and let CI regenerate. Both generators read
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

Run the scripts from the repo root — they resolve `README.md` and `tex/`
relative to the working directory.

```bash
python -m unittest discover -s scripts -t scripts -p 'test_*.py'
python scripts/new_topic.py sheaf_theory --title 層論
cd tex/<topic> && latexmk -r ../../.latexmkrc main.tex   # -r: the root rc file
```

## Chores

**New topic** — `scripts/new_topic.py`, or the `/new-topic` slash command. Do
not stage, commit or regenerate the README afterwards; CI owns that. Full
walkthrough in `README.md`.

**Deleting or renaming a topic** — nothing automates this, and CI will not clean
up after you:

1. Delete or `git mv` the `tex/<topic>/` directory.
2. `git rm pdf/<topic>.pdf` — the build only ever copies PDFs into `pdf/`, so an
   orphan lingers forever otherwise.
3. On a rename, update `\TexRepo` inside the moved `main.tex`; it embeds the
   directory name.

**Reviewing a topic's notes** — the `/review-notes` slash command. It reads a
topic, compiles it, and writes `reviews/<topic>.md`; that directory is
gitignored and the report is overwritten on every run, so never cite one as a
record. The command is read-only with respect to `tex/` by design — act on a
finding only when the owner asks for that finding to be fixed.

## Before pushing

- Run the test suite before committing anything in `scripts/`; a failure in
  `update-readme.yml` blocks the README regeneration. Extend the tests when
  behaviour changes — new `SYMBOLS` entries in `scripts/latex_unicode.py`, any
  `MAIN_TEMPLATE` edit.
- Compile locally before pushing changes to `tex/preamble.tex`,
  `tex/colophon.tex` or `.latexmkrc`. They force all topics to rebuild in CI, so
  one mistake costs a full failed run.

## Git

Full rules and their reasoning: `docs/git-strategy.md`. Use the `/git` and
`/git-merge` slash commands, which implement it. The rules that matter most:

- **Shared paths go on a branch and through a PR** — `scripts/`, `.github/`,
  `.latexmkrc`, `tex/preamble.tex`, `tex/colophon.tex`. They can break every
  topic at once. Everything else, `tex/<topic>/**` included, commits straight
  to `main`.
- **Conventional commits in English**: `feat`, `fix`, `docs`, `ci`, `refactor`,
  `chore`, `test`. The scope is the topic directory name for content changes
  (`feat(algebraic_k_theory): ...`), the file stem for shared `.tex`
  (`fix(preamble): ...`), and omitted otherwise. The history also contains
  `remove:` — do not continue it; use `chore:` or `refactor:`.
- **Never force-push and never rewrite pushed history.** Correct a bad commit
  on `main` with a follow-up commit.
- **Path-scoped `git add` only**, never `-A` or `.`; the working tree may hold
  someone else's work in progress.
- **`Co-Authored-By: Claude` on what Claude wrote** — `scripts/`, `.github/`,
  `docs/`, `.claude/`, `tex/preamble.tex`, `tex/colophon.tex` — and never on
  `tex/<topic>/**`.

CI pushes to `main` after every push of yours, so `git pull --rebase` first.
It cannot conflict: the bots only touch `pdf/*.pdf` and the generated `README.md`
blocks.
