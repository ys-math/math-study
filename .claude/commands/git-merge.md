---
description: Inspect an open pull request, re-run its gates, then squash-merge it
argument-hint: [PR番号]  (省略時は現在のブランチの PR)
allowed-tools: Read, Grep, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git fetch:*), Bash(git pull:*), Bash(git switch:*), Bash(git rev-parse:*), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(gh pr list:*), Bash(gh pr merge:*), Bash(latexmk:*), Bash(python -m unittest:*)
---

Merge a pull request following `docs/git-strategy.md`. Read that file first.

Arguments given: $ARGUMENTS

**This command cannot commit new work.** `git add`, `git commit` and `git push`
are absent from `allowed-tools` above. It merges what is already on the branch,
or it stops.

Under this repo's strategy, PRs exist only for changes that can break every
topic at once — `scripts/`, `.github/`, `.latexmkrc`, `tex/preamble.tex`,
`tex/colophon.tex`. Every PR you are asked to merge is, by construction, one of
the risky ones. Behave accordingly.

## 1. Find the PR

With a number, use it. Without one, `gh pr list --head "$(git branch --show-current)"`.
If there is no PR for the current branch, say so and stop — do not guess at
another one.

## 2. Show what is being merged

```bash
gh pr view <n>
gh pr diff <n>
```

Report, compactly:

- Title, author, branch name, commit count.
- The changed paths **grouped by category** — `scripts/`, `.github/`,
  build config, shared `.tex` — so the blast radius is visible without reading
  the diff.
- The diff stat.

Read the diff yourself. You are about to vouch for it.

## 3. Checks

```bash
gh pr checks <n>
```

`validate.yml` runs on `pull_request`: it compiles all 8 topics and runs the
script tests.

- **Red** — report which check failed and **stop**. Do not offer to merge
  anyway.
- **Pending** — say so and stop. Offer to re-run the command shortly rather
  than waiting in a loop.
- **No checks reported** — treat as a warning, not a blocker, and say why: the
  workflow may not have been triggered. The local gates in step 4 still apply.

## 4. Re-run the gates locally

CI proves the branch. This proves the branch *as it will land*, which is not
the same thing when `main` has moved.

```bash
git fetch origin
git switch <branch> && git pull --rebase --autostash origin <branch>
```

Then, by category:

| PR touches | Gate |
| --- | --- |
| `tex/preamble.tex`, `tex/colophon.tex`, `.latexmkrc` | `latexmk -cd -g` for all 8 topics |
| `scripts/**` | `python -m unittest discover -s scripts -t scripts -p 'test_*.py'` |
| `.github/**` only | nothing local to run — say so explicitly |

Any failure stops the merge and is reported verbatim.

Do not review the mathematics here. `/code-review` covers the diff; this
command covers whether the thing builds and merges cleanly. Point at
`/code-review` if the PR looks like it wants a real read.

## 5. Confirm

Print a summary and **wait for an explicit yes**. Squash-merging is not
reversible from here.

```
PR #7  ci: validate pull requests before they land
  ブランチ: ci/pr-validation (3 commits)
  変更: .github/workflows/validate.yml, .github/workflows/build-pdf.yml
  CI: validate / tex OK, validate / scripts OK
  ローカルゲート: .github/ のみ — ローカル実行なし

squash merge しますか?
```

## 6. Merge

```bash
gh pr merge <n> --squash --delete-branch
```

Squash keeps `main` linear — one commit per branch, no merge bubbles. The
squash commit's subject is the PR title, so check it satisfies the convention
in `docs/git-strategy.md` before merging; if it does not, say so and let the
user retitle the PR rather than merging a message that breaks the log.

Then return to a clean `main`:

```bash
git switch main
git pull --rebase --autostash origin main
```

## 7. Report

Print `git log --oneline -3` and confirm the branch was deleted both locally
and on the remote.

If the merge touched `**.tex` or `.latexmkrc`, `build-pdf.yml` is now
rebuilding every topic and will commit `chore(ci): update compiled PDFs` in a
few minutes. Say so and finish — do not poll `gh run list` waiting for it.
