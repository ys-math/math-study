---
description: Report the state of the CI runs for a commit, then stop
argument-hint: "[commit sha]  (omit — the current HEAD)"
allowed-tools: Bash(git rev-parse:*), Bash(git log:*), Bash(gh run list:*), Bash(gh run view:*)
---

Report the GitHub Actions runs for one commit and stop.

Arguments given: $ARGUMENTS

All output is English.

**This command never fixes anything.** It has no write tool, no `gh run rerun`
and no `git` that mutates — see `allowed-tools` above. A red build is a finding
for the user, never a task to pick up. That restraint is not politeness: this
command is built to run under `/loop`, where nobody reads the intermediate
turns, and an agent that starts repairing things unattended is how a loop turns
into an incident.

## What runs, and when

`docs/git-strategy.md` (`## CI's own commits`) is the specification. What this
command needs from it:

| Workflow | Triggered by | Observed duration |
| --- | --- | --- |
| `Update README` | every push to `main` | 8–20 s |
| `Build PDFs` | a push touching `**.tex` or `.latexmkrc` | 1m45s–2m20s |

A push touching no `.tex` starts only `Update README`. **Both are expected to be
absent on a commit that CI itself made** — the bots' own commits do not always
start a new run, and a missing run is not a failure.

## 1. The commit

With a sha, use it. Without one, `git rev-parse HEAD`. Report the short sha and
subject line so the user can see *which* push is being reported on — a loop's
output is read out of context, hours later.

## 2. The runs

```bash
gh run list --commit <sha> --json name,status,conclusion,databaseId,startedAt
```

## 3. Classify — this is the loop's exit condition

Land on exactly one of three states and **name it on the last line**, verbatim.
A loop reads that line to decide whether to keep going.

- **`watch-ci: done`** — every run for the commit has a conclusion, or there are
  no runs at all and the commit is older than three minutes (nothing was
  triggered; that is an answer, not a pending state). **A loop stops here.**
- **`watch-ci: pending (<workflow>, <elapsed>)`** — at least one run is queued or
  in progress. **A loop re-checks.**
- **`watch-ci: unknown (<reason>)`** — `gh` failed, is unauthenticated, or the
  commit is not on the remote. Report the error verbatim. **A loop stops** — an
  error that repeats every iteration is not going to resolve itself, and a loop
  that keeps retrying it just prints the same failure forever.

## 4. Report

Green, and nothing else to say:

```
a1b2c3d  feat(manifold): add a definition of tangent spaces

  Build PDFs      success   1m52s
  Update README   success      11s

watch-ci: done
```

Still running:

```
a1b2c3d  feat(manifold): add a definition of tangent spaces

  Build PDFs      in_progress   0m48s
  Update README   success          11s

watch-ci: pending (Build PDFs, 0m48s)
```

Red — and only here does the report get long. Pull the failing step and its log
tail, because the whole point of watching is to not have to go and look:

```bash
gh run view <databaseId> --log-failed
```

Quote the `-file-line-error` lines if it is a LaTeX failure, the assertion if it
is `scripts/`. Suppress Overfull/Underfull `\hbox` warnings, as everywhere else
in this repo. Then say which topic broke and stop — do not diagnose beyond the
log, and do not propose an edit.

## Pacing, under `/loop`

**Never re-check faster than the thing you are watching changes.** `Build PDFs`
takes about two minutes, so a ~90 s interval sees at most one real transition
per check. A 10 s interval returns the same answer twelve times and spends the
session to learn nothing.

If both workflows have already concluded, there is no interval that helps: the
answer is final, and the correct action is to stop the loop rather than schedule
another look.
