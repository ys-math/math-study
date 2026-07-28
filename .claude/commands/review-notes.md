---
description: Review a topic's notes for mathematical correctness, typos and LaTeX health, and write a report
argument-hint: "[topic_slug ...]  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Bash(latexmk:*), Bash(git rev-parse:*), Bash(date:*), Write(reviews/**)
---

Review the notes of one or more topics and write a report per topic to
`reviews/<topic>.md`. That directory is gitignored: the reports are local
scaffolding, not part of the repo.

Arguments given: $ARGUMENTS

**This command never edits `tex/`.** It reports; applying the fixes is a
separate instruction from the user. `allowed-tools` above enforces that — the
only writable path is `reviews/`.

The report and its summary are Japanese.

## Picking the topics

- **Slugs given** — review each one, in the order given.
- **No arguments** — list every topic as a numbered plain list, showing the slug,
  the `\DocTitle` from its `main.tex`, and `(空)` where every chapter file is
  empty. Then stop and wait for the user to name the ones to review. Never
  default to reviewing all of them.
- **Unknown slug** — say so, print the same list, and stop.
- **Every chapter empty** — report `<topic> は中身が空です` and write no file. An
  empty report is worse than none; it looks like a clean bill of health.

## Reviewing

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
latexmk -cd -r .latexmkrc tex/<topic>/main.tex
```

`-cd` makes latexmk enter the topic directory so `\input{../preamble.tex}`
resolves; there is no need to `cd` yourself. Aux files and `main.pdf` are
gitignored — leave them, do not run `latexmk -c`. A compile failure does not
abort the review: write the report anyway, with a `## ビルド失敗` section first
quoting the `-file-line-error` lines, then the rest of the findings.

### What to report

Three categories, and nothing else:

- **数学的正しさ** — false statements, wrong or incomplete proofs, missing
  hypotheses, quantifier slips, index and subscript errors, symbols used before
  they are defined.
- **誤字・記法** — Japanese typos, 表記ゆれ, LaTeX command typos, notation that
  contradicts an earlier definition, hand-rolled markup where a preamble macro
  exists.
- **LaTeX の健全性** — grounded in the compile log: undefined control sequences,
  undefined references, missing labels. **Suppress Overfull/Underfull \hbox
  warnings** — Japanese text in `jsarticle` emits them constantly and they bury
  everything else.

Do **not** comment on exposition, motivation, missing examples, or chapter
ordering. The mathematics is the repo owner's; unsolicited pedagogy dilutes the
findings that are actually checkable.

### Discipline

Verify each proof step against the definitions given in that topic, using your
own knowledge of the mathematics. No web lookups — the material is standard, and
the errors that matter are local slips, not misremembered theorems.

**A finding must name the specific line that fails and say why.** "The proof of
命題 1.2 feels incomplete" is not a finding; drop it rather than filing it with
low confidence. Math findings carry 確信度 (高/中/低) so the user can triage —
that is for calibration, not for smuggling in guesses.

Ignore any previous `reviews/<topic>.md`; review fresh and overwrite it. Never
carry anything over from it — including the state of its checkboxes (see 概要
below). A finding the owner has already fixed will not be found again, so a
carried-over tick could only ever sit next to a finding that is still there.

### The report is Markdown, not LaTeX

The report is read in a Markdown preview whose math renderer is KaTeX, which
knows nothing about this repo's preamble. Two rules follow:

- **All LaTeX source goes in a ```tex fence, never a blockquote and never
  inline.** That covers both the quoted line and the replacement you propose in
  **修正案** — a blockquoted or inline `.tex` line gets parsed as math and dies
  on the first `\id` or `\labelenumi`.
- **In your own prose, use KaTeX-safe primitives only.** Write
  `$\mathrm{id}_P$` even where the note writes `$\id_P$`; the shared macros
  (`\id`, `\ob`, `\mor`, `\dom`, `\cod`) are undefined in KaTeX and produce
  `Undefined control sequence`. When the finding is *about* the macro, put the
  macro name in a code span — `` `\id_P` `` — rather than in math.

## The report

Japanese, at `reviews/<topic>.md`, overwritten each run. Findings grouped by
category, ordered by `file:line` within each, numbered continuously across the
whole report so the user can say "1 と 4 を直して".

````markdown
# <DocTitle> レビュー

- 対象: `tex/<topic>/` (ch01.tex, ch02.tex)
- コミット: <git rev-parse --short HEAD>
- 日時: <date '+%Y-%m-%d %H:%M'>
- 指摘: 数学 1件 / 誤字・記法 2件 / LaTeX 0件

## 概要

- [ ] **1** 数学 — <一行の見出し>
      [`ch01.tex:31`](../tex/<topic>/ch01.tex#L31) [確信度: 高]
- [ ] **2** 誤字・記法 — <一行の見出し>
      [`ch01.tex:38`](../tex/<topic>/ch01.tex#L38)

## 数学的正しさ

### 1. <一行の見出し> — ch01.tex:31  [確信度: 高]

[`ch01.tex:31`](../tex/<topic>/ch01.tex#L31)

```tex
<該当行をそのまま引用>
```

<何が誤りで、なぜそうなのか>

**修正案**: <説明>

`ch01.tex:31` (修正案)

```tex
<修正後の行>
```

## 誤字・記法

### 2. ...

## LaTeX の健全性

指摘なし
````

Every fence carries the location it came from on the line directly above it. The
heading names the location too, but a fence scrolled away from its heading has
to stand on its own.

Make that location a **link to the line**: the report sits in `reviews/`, so the
path is relative — `[`` `ch01.tex:31` ``](../tex/<topic>/ch01.tex#L31)`. VS
Code's Markdown preview resolves the `#L<n>` fragment and opens the file at that
line, which is the difference between reading the report and fixing from it. Do
the same for the location in each 概要 item, and inline wherever the prose
names another line (`ch01.tex:22`, `preamble.tex:47`). Keep the link text in
backticks so it still reads as a path.

Two exceptions, both because there is nothing to jump to: a **修正案** fence
shows text that is not in the file yet, so its caption stays a plain code span
`ch01.tex:31` (修正案); a compile-log excerpt is captioned
`[`` `main.log` ``](../tex/<topic>/main.log)` with no line number, since the log
is regenerated on every build and its line numbers do not survive.

The 概要 list carries every finding in the same order and numbering as the
sections below, so the report opens with something readable in ten seconds. Each
item is one bullet: the checkbox, the number in bold, the category, the one-line
heading, then the linked location. `[確信度: 高/中/低]` closes the item for
数学 findings only — 誤字・記法 and LaTeX findings do not carry one, so theirs
simply ends at the location rather than trailing an empty `—`.

The wrapped second line is a lazy continuation of the same bullet; it keeps the
source inside 80 columns and collapses back to one line in the preview. The
checkbox has to be a list item to render as a checkbox at all — that is why 概要
is a list and not a table, and why the numbered `###` headings below carry no box
of their own.

**Always write every box unticked.** The boxes are the owner's own progress
tracking, for ticking by hand while working through the report; nothing reads
them back, and the overwrite rule above means a re-run resets them. `## ビルド失敗`
gets no box: it is not a numbered finding and there is nothing to triage.

When a category has no findings, keep the heading and write `指摘なし`. When
nothing at all is found, still write the file — 概要 reads `指摘なし` in place of
the list, and the file's existence is the proof that the review ran.

## Afterwards

Print a compact index to the chat — the path, the counts, and one line per
finding. Not the report itself; it is in the file precisely so it does not have
to fill the scrollback.

```
reviews/algebraic_k_theory.md に書き出しました (数学 1 / 誤字・記法 2 / LaTeX 0)

数学的正しさ
  1. \pi_1 と \pi_2 の取り違え — ch01.tex:31 [高]
誤字・記法
  2. \mathrm{id}_P と \id_P の混在 — ch01.tex:38
```

With several topics, print one index per topic and a one-line total at the end.
Do not commit anything: `reviews/` is gitignored, and the `.tex` sources are
untouched by this command.
