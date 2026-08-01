---
description: Review a topic's notes for mathematical correctness, typos and LaTeX health, and file the findings as GitHub issues
argument-hint: "[topic_slug ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Bash(latexmk:*), Bash(git rev-parse:*), Bash(git status:*), Bash(gh issue list:*), Bash(gh issue create:*), Bash(gh label create:*)
---

Review the notes of one or more topics and file each finding as a GitHub issue.
`docs/issue-convention.md` is the specification for what an issue looks like —
read it before filing, and restate none of it here.

Arguments given: $ARGUMENTS

**This command has no write tool at all.** Not `Write`, not `Edit` — check
`allowed-tools` above. It cannot touch `tex/`, and there is no longer a local
report for it to write either. It finds things and files them; applying the fix
is a separate instruction from the user.

**It cannot close anything.** `gh issue close` is absent from `allowed-tools`,
deliberately — see `## 5. Report`.

English structure, Japanese mathematics, per `docs/issue-convention.md`
`## Language`. That governs the chat output too, not just the issue bodies.

## Picking the topics

- **Slugs given** — review each one, in the order given.
- **No arguments** — list every topic as a numbered plain list, showing the slug,
  the `\DocTitle` from its `main.tex`, and `(empty)` where every chapter file is
  empty. Then stop and wait for the user to name the ones to review. Never
  default to reviewing all of them.
- **Unknown slug** — say so, print the same list, and stop.
- **Every chapter empty** — report `<topic> は中身が空です` and file nothing.

## 1. Look before you review

Two lookups, both before reading a single line of mathematics.

```bash
gh issue list --label "topic:<topic>" --state open --json number,title,body
git status --porcelain tex/<topic>
```

The first is what stops a re-run duplicating every finding you have not fixed
yet. Read the bodies, not just the titles — matching is a judgement about
whether it is the same defect, and the wording will differ.

The second decides whether the issues can carry permalinks. If anything under
`tex/<topic>/` is modified or untracked, the content you are about to review is
in no commit, and `docs/issue-convention.md` `### Location, and the dirty tree`
says what to do. Say so at the gate in step 4, do not silently drop the links.

## 2. Reviewing

Read in this order, always:

1. `tex/preamble.tex` — the theorem environments (`definition`, `proposition`,
   `lemma`, `theorem`, `example`, `corollary`, `remark`) and the shared macros
   (`\ob`, `\mor`, `\dom`, `\cod`, `\id`) live here. Without this you cannot
   tell a real notation inconsistency from a house convention, and you will
   file `\mathrm{id}` vs `\id` findings backwards.
2. The topic's `main.tex` — which chapters are `\input`, and in what order.
3. Every `ch0N.tex`, in that order. Definitions in earlier chapters bind the
   notation used in later ones.

Then compile the topic, from the repo root:

```bash
latexmk -cd -g tex/<topic>/main.tex
```

`-cd` makes latexmk enter the topic directory, so there is no need to `cd`
yourself. `-g` is load-bearing *here* in particular: without it latexmk reports
"Nothing to do" from cache for a file that does not compile, and a broken topic
would come back with no `review:latex` findings at all — a clean bill of health
for a document that does not build. `docs/git-strategy.md` (`## Gates`) is the
single copy of this invocation; do not add `-r`. Aux files and `main.pdf` are
gitignored — leave them, do not run `latexmk -c`.

A compile failure does not abort the review. Report it at the top of the gate,
quoting the `-file-line-error` lines, and carry on with the rest of the
findings. It is not itself an issue to file: it is a fact about the run, and the
`review:latex` findings it produces are the issues.

### What to report

Three categories, and nothing else. Each maps to a `review:` label:

- **数学的正しさ** → `review:math` — false statements, wrong or incomplete
  proofs, missing hypotheses, quantifier slips, index and subscript errors,
  symbols used before they are defined.
- **誤字・記法** → `review:typo` — Japanese typos, 表記ゆれ, LaTeX command typos,
  notation that contradicts an earlier definition, hand-rolled markup where a
  preamble macro exists.
- **LaTeX の健全性** → `review:latex` — grounded in the compile log: undefined
  control sequences, undefined references, missing labels. **Suppress
  Overfull/Underfull \hbox warnings** — Japanese text in `jlreq` emits them
  constantly and they bury everything else.

Do **not** comment on exposition, motivation, missing examples, or chapter
ordering. The mathematics is the repo owner's; unsolicited pedagogy dilutes the
findings that are actually checkable.

### Discipline

Verify each proof step against the definitions given in that topic, using your
own knowledge of the mathematics. No web lookups — the material is standard, and
the errors that matter are local slips, not misremembered theorems.

**A finding must name the specific line that fails and say why.** "The proof of
命題 1.2 feels incomplete" is not a finding; drop it rather than filing it with
low confidence. `review:math` findings carry a confidence so the user can
triage — that is for calibration, not for smuggling in guesses.

**Review fresh.** The open issues from step 1 tell you what is already tracked;
they are not a starting point for the reading. Re-derive every finding from the
sources, then match. A finding you only "found" because an issue described it is
not a finding.

## 3. Match against what is open

Classify every finding as one of three, per `docs/issue-convention.md`
`## Deduplication`:

- **new** — nothing open covers it. It gets filed.
- **`#N`** — an open issue is the same defect. Nothing is filed; it is already
  tracked.
- **same as `#N`?** — you are not sure. It goes to the user at the gate.

Then the mirror: every open issue that this run did **not** re-find. Collect
them for step 5; do not act on them.

## 4. Gate, and stop

Print the findings and **wait**. Nothing before this point has changed anything.

```
galois_theory (ガロア理論) — commit af549ea

⚠ tex/galois_theory/ch01.tex is uncommitted — issues will carry no permalink

Found 7 (new 5 / existing 2)

  1  math   補題 1.2 の証明が空のまま閉じている        [High]   new
  2  math   命題 1.4 に (3)⇒(1) がない                [High]   #12
  3  math   系 1.5 の index が 1 ずれている            [Medium] new
  4  typo   ラベル lem: free_presentaion の綴り誤り              same as #14?
  5  typo   「R 部分加群」と「部分 R 加群」の表記ゆれ            new
  6  typo   R^{(S)} と e_s が定義されずに使われている            new
  7  latex  \texorpdfstring の PDF 文字列に _ が残る              new

Which should I file? (all / numbers / none)
```

Number the findings continuously across all three categories, ordered by
`file:line` within each, so the user can answer `1 と 4`. The number is for this
conversation only — it is not written anywhere, and the issue number replaces it
the moment the issue exists.

The user's answer is the whole authority for what gets filed. `none` is a valid
answer and ends the run for that topic.

## 5. File

For each finding the user picked, ensure its labels exist, then create the
issue. Both are specified in `docs/issue-convention.md`; follow it exactly.

```bash
gh label create "topic:<topic>" -c 0e8a16 2>/dev/null || true
gh issue create --title "..." --body "$(cat <<'EOF'
...
EOF
)" --label "topic:<topic>,review:math"
```

The body goes through a quoted heredoc because this command has no write tool
and therefore cannot use `--body-file`. Quote the delimiter (`<<'EOF'`) or the
shell will expand `$\blacksquare$`, `\begin` and every backslash in the fenced
`.tex` — which is most of what the body is.

File one topic's issues before moving to the next topic's review.

## 6. Report

```
galois_theory: filed 5 (#19 #20 #21 #22 #23), 2 already open (#12 #14)

Open issues not found this run:
  #15  ch02: 定理 2.1 の仮定が足りない
  → fixed already? gh issue close 15

Run /issues galois_theory to regenerate the local worklist.
```

**Report the undetected issues; never close them.** A finding can go undetected
because this run missed it, not because it was fixed, and closing on that
evidence loses a real defect with no trace. The `gh issue close` hint is for the
user to run. `allowed-tools` is what makes this hold rather than the paragraph.

The `/issues` pointer matters because nothing else refreshes the worklist — this
command cannot write it, and a stale `issues/<topic>.md` is the one thing that
would make the new issues invisible where you actually work.

With several topics, print one report per topic and a one-line total at the end.
Commit nothing: nothing in the working tree changed.
