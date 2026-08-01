---
description: Render a topic's open review issues as a local worklist you can fix from
argument-hint: "[topic_slug ...]  (omit — every topic with open issues)"
allowed-tools: Read, Glob, Grep, Bash(gh issue list:*), Bash(git rev-parse:*), Bash(date:*), Write(issues/**)
---

Fetch the open review issues and write them to `issues/<topic>.md`, with links
that open the file at the line in *your* working copy.

Arguments given: $ARGUMENTS

GitHub is the record; this is a view of it. `issues/` is gitignored and every
run overwrites it. `docs/issue-convention.md` `## Reading them locally` says why
it exists at all: a GitHub permalink is correct and durable and it opens a
browser, and while fixing you want the local file.

**This command only writes `issues/`.** It never edits `tex/` and never touches
GitHub — `gh issue list` is the only `gh` verb in `allowed-tools`.

It is cheap: no compile, no review, one API call per topic. Run it whenever the
worklist looks stale rather than wondering whether it is.

English structure, Japanese mathematics — the issues are already written that
way, and this command copies them rather than rephrasing them.

## Picking the topics

- **Slugs given** — render each one, in the order given, even if it has no open
  issues (an empty worklist is a fact worth seeing).
- **No arguments** — every topic that has at least one open issue. Say which
  topics were skipped for having none; do not write empty files for all 8.
- **Unknown slug** — say so, list the topics, and stop.

## 1. Fetch

```bash
gh issue list --label "topic:<topic>" --state open \
  --json number,title,body,labels --limit 100
git rev-parse --short HEAD
```

`--limit 100` because `gh` defaults to 30 and a silently truncated worklist is
worse than no worklist.

## 2. Re-locate each finding

The issue body records the line as it was at the commit reviewed. Lines move.

For each issue, take the quoted `.tex` line out of its first fence and `grep` it
in the current file. Use **that** line number in the link.

- **Found once** — link to it.
- **Found several times** — link to the one nearest the recorded number.
- **Not found** — the line has been edited, quite possibly fixed. Link to the
  file with no fragment, and mark the entry `line not found — fixed?` so the
  worklist says so instead of pointing somewhere wrong.

This is the step that makes the worklist worth generating rather than reading
the issues directly, so do not skip it when the numbers look plausible.

## 3. Write

`issues/<topic>.md`, overwritten. Ordered by file, then by line.

````markdown
# <DocTitle> — open issues (4)

- topic: `tex/<topic>/`
- HEAD: <git rev-parse --short HEAD>
- fetched: <date '+%Y-%m-%d %H:%M'>
- open: math 2 / typo 1 / latex 1

## 概要

- [ ] [#12](https://github.com/ys-math/math-study/issues/12) math [High] —
      補題 1.2 の証明が空のまま閉じている
      [`ch01.tex:27`](../tex/<topic>/ch01.tex#L27)
- [ ] [#14](https://github.com/ys-math/math-study/issues/14) typo —
      ラベル `lem: free_presentaion` の綴り誤り
      [`ch01.tex:31`](../tex/<topic>/ch01.tex#L31)

## #12 — 補題 1.2 の証明が空のまま閉じている

`review:math` [High] · [`ch01.tex:27`](../tex/<topic>/ch01.tex#L27) ·
[issue](https://github.com/ys-math/math-study/issues/12)

```tex
\begin{proof}

\end{proof}
```

<the issue's explanation, verbatim>

**Suggested fix**: <verbatim>

```tex
\begin{proof}[\bfseries 証明 (略)]
\end{proof}
```
````

The links are **relative** — `../tex/<topic>/ch01.tex#L27` — because the file
sits in `issues/`. VS Code's Markdown preview resolves the `#L<n>` fragment and
opens your working copy at that line, which is the entire point. The issue
number stays an absolute link so you can get to GitHub to close it.

Copy the explanation and the fences **verbatim** from the issue body. Do not
summarise, re-translate or improve them; a worklist that disagrees with the
issue is worse than one that is merely long.

Every fence carries its location on the line above, as the issue body does — a
fence scrolled away from its heading has to stand on its own.

**Write every checkbox unticked.** They are yours to tick while working; nothing
reads them back and the next run resets them. Closing the issue is what records
that a finding is done — say so in the report rather than letting a ticked box
feel like progress that persisted.

When a topic has no open issues, still write the file: the heading reads
`— open issues (0)`, 概要 reads `open issue なし`, and its existence is the
proof that the fetch ran.

## 4. Report

```
issues/galois_theory.md — 4 open (math 2 / typo 1 / latex 1)
  #12 [High] 補題 1.2 の証明が空       ch01.tex:27
  #14        綴り誤り presentaion      ch01.tex:31  ← line not found, fixed?

Fixing one? /git proposes the Closes trailer from the diff.
```

Flag every `line not found` entry in the report, not only in the file — it is
the signal that a finding may already be fixed and its issue wants closing.

With several topics, one block per topic and a one-line total at the end.
Commit nothing: `issues/` is gitignored.
