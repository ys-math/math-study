---
description: Delete a topic — its tex/ directory, its PDF, its Lean mirror, its review issues and its local artifacts — and commit the removal
argument-hint: "<topic_slug>  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Edit(lean/Math.lean), Bash(git status:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git fetch:*), Bash(git pull:*), Bash(git log:*), Bash(git ls-files:*), Bash(git diff:*), Bash(wc:*), Bash(git rm:*), Bash(git clean:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(lake:*), Bash(gh issue list:*), Bash(gh issue close:*), Bash(gh label list:*), Bash(gh label delete:*)
---

Delete one topic: `tex/<topic>/`, `pdf/<topic>.pdf`, its Lean mirror, its open
review issues, and the local artifacts that neither git nor CI will clean up.
Then commit and push the removal.

Arguments given: $ARGUMENTS

Nothing else in the repo names a topic: `build-pdf.yml` enumerates
`tex/*/main.tex`, and both README generators read `git ls-files`. So the topic
leaves the README on its own after the push — but `pdf/<topic>.pdf` is only ever
written to, never pruned, and an orphan there lingers forever. That is the whole
reason this command exists.

The Lean mirror is the same shape of problem with a louder failure. If
`lean/Math/Study/<Topic>.lean` exists, `lean/Math.lean` imports it, and removing
the file without removing the import breaks `lake build` for **every** proof in
the repo — a topic deletion that reds `main` for a reason nobody will connect to
it. Both go in the same commit.

The same is true off-disk. `topic:<topic>` issues and the label itself outlive
the files, and an issue about a chapter that no longer exists can be neither
fixed nor found. `docs/issue-convention.md` `## Deletion` is the specification.

**This command deletes one topic per invocation.** If several slugs are given,
say so and stop.

**It cannot rename.** Renaming is still the manual recipe in `CLAUDE.md`.

All output is English.

## 1. Pre-flight

```bash
git rev-parse --abbrev-ref HEAD
git fetch origin
git status --porcelain=v2 --branch
```

**Not on `main` — stop.** Name the branch and say a topic deletion belongs on
`main`. Do not switch: the user is presumably mid-PR on a shared change, and
moving HEAD as a side effect of a delete command is worse than one round trip.

If `main` is behind, `git pull --rebase --autostash origin main`. This cannot
conflict — CI only writes `pdf/*.pdf` and the marker blocks in `README.md`. It
is not optional either: CI pushes after every push of yours, so a stale `main`
turns the final `git push` into a rejection *after* the destructive step.

## 2. Picking the topic

- **No arguments** — list every topic as a numbered plain list, showing the slug,
  the `\DocTitle` from its `main.tex`, the chapter count, and `(empty)` where
  every chapter file is empty. Then stop and wait. Never guess.
- **Unknown slug** — say so, print the same list, and stop.
- **Several slugs** — one at a time; print the list and stop.

## 3. Survey

Gather, for the chosen topic:

```bash
git ls-files tex/<topic> pdf/<topic>.pdf lean/Math/Study/<Topic>.lean
wc -l tex/<topic>/*.tex
grep -n "Math.Study.<Topic>" lean/Math.lean
git log --oneline -n 1 -- tex/<topic>
git status --porcelain tex/<topic>
gh issue list --label "topic:<topic>" --state open --json number,title
```

`<Topic>` is the slug transformed as `docs/naming-convention.md` specifies —
`algebraic_k_theory` → `AlgebraicKTheory`. Most topics have no mirror; that is
not a refusal, it just drops the two Lean lines from everything below.

Read the `\DocTitle` out of `main.tex` — the survey must show what the topic is
called, not just its slug. A slug is easy to mistype and hard to recognise.

`pdf/<topic>.pdf` may legitimately not exist, on a topic that has never been
built. Note it in the survey; it is not a refusal. It *is* load-bearing for the
command you build in step 6: `git rm` aborts wholesale on a path it cannot
match, so include the PDF in that command only when `git ls-files` reported it.

## 4. Refuse

Git history is the entire safety net here, so the one case that destroys work
for good is a topic that has never reached it.

**Uncommitted prose — stop.** Untracked chapters, or modified ones. Show the
paths, and tell the user to commit via `/git` first, then re-run.

**The exception**: untracked *and* every chapter file empty. That is the
wrong-slug-from-`/new-topic` case — a skeleton created minutes ago with nothing
in it. Delete it plainly with `git clean -xdf tex/<topic>`; there is nothing to
commit, because nothing was ever tracked. Say that is what happened, and skip
steps 5 through 7.

## 5. Confirm, and stop

Print the survey and **wait**. Nothing before this point has changed the
repository.

```
Delete topology (位相幾何学)?

  tex/topology/main.tex        18 lines
  tex/topology/ch01.tex       242 lines
  pdf/topology.pdf            (tracked)
  lean/Math/Study/Topology.lean   31 lines, 6 declarations (4 sorry)
  lean/Math.lean               import Math.Study.Topology  → removed
  tex/topology/               ignored build artifacts (main.aux, main.pdf, latex_out/)
  issues/topology.md          local worklist

  open issues: #21 #22 #23 #24   → closed
  label topic:topology           → deleted

  last commit: a1b2c3d feat(topology): add the separation axioms

  commit: chore: remove the topology topic
  push:   main

  recoverable afterwards with:
    git checkout a1b2c3d -- tex/topology

Proceed?
```

Show the recovery command with the *real* SHA of the last commit touching the
topic — that commit still has the files, so it is `git checkout <sha> --
tex/<topic>`, no `^` needed. The escape hatch belongs on screen at the moment of
deciding, not in the report afterwards.

## 6. Execute

```bash
git rm -r tex/<topic> pdf/<topic>.pdf lean/Math/Study/<Topic>.lean
git clean -xdf tex/<topic> issues/<topic>.md
# delete the `import Math.Study.<Topic>` line from lean/Math.lean, then:
git add lean/Math.lean
git commit -m "chore: remove the <topic> topic"
git push origin main
```

`git rm` only removes tracked files, so it leaves the directory standing, full
of ignored build junk. `git clean -xdf` sweeps that and the now-empty directory,
and the stale `issues/<topic>.md` with it — a worklist for notes that no longer
exist. Both paths are pathspecs: a pathspec matching nothing is a silent no-op,
so a topic with no worklist and no build artifacts needs no special case. The
same is true of the Lean path in the `git rm` line — but only when it was never
tracked. Include it only if the survey found it, because `git rm` aborts
wholesale on a path it cannot match, exactly as with the PDF.

The import line is the one deletion git cannot do for you, and it must be in
this commit: `lean/Math.lean` importing a file that no longer exists fails
`lake build` for every proof in the repo. Build before committing — the
invocation is in `docs/git-strategy.md` `## Gates` — whenever a mirror was
removed.

Use `git clean`, never `rm`. `Bash(rm:*)` is absent from `allowed-tools` above,
deliberately — nothing in this command should be able to delete a path git has
not been told about.

Then the issues, **after** the push and only if it succeeded:

```bash
gh issue close <n> --comment "Topic removed in <sha>."
gh label delete "topic:<topic>" --yes
```

Order matters. The commit is the thing that can fail — a rejected push leaves
the topic in place, and issues closed before it would be closed against files
that still exist. Deleting the label last keeps the closed issues findable right
up to the moment there is nothing left to find.

Skip `gh issue close` when the survey found no open issues. Delete the label
independently of that — a topic whose findings were all fixed and closed still
has one — but only when it exists: `gh label delete` on a missing label is an
error, not a no-op.

The commit scope is omitted rather than `chore(<topic>):`, because after this
commit the directory that scope names does not exist. One commit, both paths.

**No `Co-Authored-By` trailer.** The prose being deleted is the repo owner's;
this command only carried out the removal.

### Never

`--force`, `commit --amend`, `git add -A`, `git add .`, `git clean` without an
explicit pathspec. A bad deletion on `main` is corrected by restoring from
history in a follow-up commit, not by rewriting the one that removed it.

## 7. Report

Print `git log --oneline -n 1`, the issues closed, and the recovery command
again. Note that recovery restores the files only — reopening the issues is
`gh issue reopen`, and the label would have to be recreated.

Then say what CI will do: `update-readme.yml` drops the topic from the PDF list
and rebuilds the tree, a commit that arrives in seconds. `build-pdf.yml` fires
too — the deleted `.tex` files match its path filter — but it selects no topics
to build and exits without committing. The next `/git` rebases over the README
commit automatically, so the user need do nothing.

Do not poll `gh run list`. Mention it and finish.
