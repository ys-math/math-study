---
description: Verify that a topic's open review issues are true, and close the ones that are not
argument-hint: "[topic_slug | #N ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Bash(git rev-parse:*), Bash(git status:*), Bash(git diff:*), Bash(latexmk:*), Bash(gh issue list:*), Bash(gh issue view:*), Bash(gh issue close:*), Bash(gh issue edit:*)
---

Check whether the findings `/review-notes` filed are actually true, and close the
ones that are not. `docs/issue-convention.md` `## Verification` is the
specification — the four verdicts, the evidence burden, the closing comment and
the edited body all live there. Read it before judging anything, and restate
none of it here.

Arguments given: $ARGUMENTS

This is the other exit from an issue. `/git` closes a finding when its fix is
committed; a finding that was never true has no fix and no fix is coming, so
without this command it stays open forever, clutters every worklist, and is read
as "already tracked" by every later review.

**This command cannot touch the filesystem.** Neither `Write` nor `Edit` is in
`allowed-tools` above — not `tex/`, not `issues/`, not `lean/`. It reads the
sources and writes only to GitHub.

**It cannot file anything.** `gh issue create` is absent. It judges what is
already filed; finding something new is `/review-notes`'s job, and a finding
made here would have skipped that command's gate.

English structure, Japanese mathematics, per `docs/issue-convention.md`
`## Language`. That governs the closing comments and the chat output alike.

## Picking the issues

- **Slugs given** — verify every open issue of each, in the order given.
- **`#N` or a bare number** — that issue alone. Resolve its topic from its
  `topic:` label; the whole topic still gets read (see `## 2`), so this shortens
  the gate and nothing else.
- **No arguments** — list every topic that has at least one open issue, with the
  count, and stop. Never default to verifying all of them: this command reads a
  whole topic per run and may compile it.
- **Unknown slug, or an issue with no `topic:` label** — say so and stop.

## 1. Fetch

```bash
gh issue list --label "topic:<topic>" --state open \
  --json number,title,body,labels --limit 100
gh issue view <N> --json number,title,body,labels        # for a bare number
git rev-parse --short HEAD
git status --porcelain tex/<topic>
```

`--limit 100` because `gh` defaults to 30, and a run that silently verified two
thirds of the backlog would report a clean bill for issues it never read.

`git status` decides what may be closed, not just what is warned about — see
`## 4`. Say at the gate that the topic is dirty; do not let it change a verdict
quietly.

## 2. Read the sources

Read before opening a single issue body, in this order:

1. `tex/preamble.tex` — the theorem environments and the shared macros.
2. The topic's `main.tex` — which chapters are `\input`, and in what order.
3. Every `ch0N.tex`, in that order.

**The whole topic, every time, even for one issue.** Most findings are claims of
absence — "$\cong$ が定義されずに使われている", "反対圏が定義されていない" — and
absence is only ever settled by looking everywhere. A targeted read of the cited
line can confirm such a claim and can never refute it, which is precisely the
bias this command exists to remove.

Then, per issue, the diff since the commit it was filed against:

```bash
git diff <the issue's **Commit**> -- tex/<topic>/
```

**A single SHA, not `<sha>..HEAD`.** That form compares two commits and omits the
working tree, so every finding you have just fixed but not yet committed would
come back as `rejected` — a hallucination verdict on your own correct work,
written into the permanent record. The one-SHA form diffs against what is
actually on disk, which is what was read in step 2.

Compile only when the set contains a `review:latex` issue:

```bash
latexmk -cd -g tex/<topic>/main.tex
```

A `review:latex` finding is a claim about a compile log, and the only honest way
to check it is to produce the log. `-g` is load-bearing: without it latexmk
answers "Nothing to do" from cache and the finding would be judged against no log
at all. `docs/git-strategy.md` (`## Gates`) owns this invocation. Aux files and
`main.pdf` are gitignored — leave them.

Skip the compile when no `review:latex` issue is in the set. It is the expensive
step and it is evidence for nothing else.

## 3. Judge

The verdicts, the evidence burden and what separates `rejected` from `fixed` are
in `docs/issue-convention.md` `## Verification`. Two things that command file has
to say because they are about how you read rather than what you write:

**Read the region before you read the reasoning.** Open the cited file at the
cited line, work out for yourself what the passage says and what is in scope
there, and only then read the issue's explanation. A fluent Japanese account of
why 命題 2.5 is broken is persuasive in proportion to how well it is written,
which is not evidence. Reversing the order is the whole failure mode.

**Neither verdict is free.** Upholding by nodding along and rejecting by
asserting are the same error wearing different clothes, and rejecting is the
more expensive one: a closed real finding leaves no trace in the notes and no
issue to find it by. When neither a supporting nor a refuting line can be named,
the verdict is `unsure` and nothing happens to the issue.

Verify against the definitions this topic gives, using your own knowledge of the
mathematics. No web lookups — the material is standard.

## 4. Gate, and stop

Print every verdict with the action it proposes and **wait**. Nothing before this
point has changed anything.

```
galois_theory (ガロア理論) — HEAD af549ea

⚠ tex/galois_theory/ch02.tex is uncommitted
  — a fix found here is /git's to close, not this command's

Verified 7 (upheld 4 / rejected 1 / fixed 1 / unsure 1)

  1  #12  upheld                                            ch01.tex:27
  2  #14  rejected  → close (not planned)                   ch01.tex:31
          綴りは lem:free_presentation で正しい — ch01.tex:31
  3  #15  upheld (body wrong) → edit                        ch01.tex:44
          指摘は正しいが Location が補題 1.3 の行を指している
  4  #17  upheld                                            ch02.tex:9
  5  #18  fixed     → uncommitted, /git closes it           ch02.tex:16
  6  #19  unsure                                            ch02.tex:38
          系 1.5 の index のずれは定義 1.4 の添字規約次第で判断できない
  7  #21  upheld                                            ch03.tex:5

Which should I act on? (all / numbers / none)
```

Number the lines continuously, ordered by `file:line`, so the answer can be
`3 と 7`. The number is for this conversation; the issue number is the real name.

Every `rejected`, every `fixed` and every `upheld (body wrong)` line carries its
one-line reason and the `file:line` that settles it, on the line beneath. A
verdict whose evidence does not fit on one line is a verdict that has not been
made yet.

**`fixed` on a dirty topic is reported and never offered.** The fix is not in any
commit, `docs/issue-convention.md` `## Closing` gives that moment to `/git`, and
closing it here would leave `/git` proposing a `Closes` trailer for an issue that
is already shut. Show the line, mark it, move on.

`unsure` lines are questions, not proposals. Answer one and the verdict may move;
say so and it will be re-judged and re-gated rather than acted on from the same
breath.

The user's answer is the whole authority for what happens. `none` is valid and
ends the run for that topic.

## 5. Act

Only on what the user named, following `docs/issue-convention.md`
`## Verification` for the wording of every comment and body.

```bash
gh issue close <N> --reason "not planned" --comment "$(cat <<'EOF'
...
EOF
)"

gh issue close <N> --comment "$(cat <<'EOF'
...
EOF
)"

gh issue edit <N> --body "$(cat <<'EOF'
...
EOF
)"
```

The bodies go through quoted heredocs: `docs/issue-convention.md` `## Body`
owns why, and why the delimiter is `<<'EOF'`.

`--reason "not planned"` on a rejection and nothing on a fix. That field is the
only structured, English, queryable record of which findings were hallucinated;
a Japanese comment says why, but `gh issue list --state closed --json
number,stateReason` is what counts them.

One topic's actions before the next topic's reading.

## 6. Report

```
galois_theory: 7 verified — upheld 4, rejected 1 (#14), edited 1 (#15)

Fixed but uncommitted:
  #18  ch02: 定理 2.1 の仮定が足りない  → /git proposes Closes #18 from the diff

Unsure, left open:
  #19  ch01: 系 1.5 の index が 1 ずれている

Run /issues galois_theory to regenerate the local worklist.
```

The `/issues` pointer matters because nothing else refreshes the worklist: this
command cannot write it, and a stale `issues/<topic>.md` still lists every issue
just closed — which is exactly where you would go looking for work.

With several topics, one block per topic and a one-line total at the end.
Commit nothing: no tracked file changed.
