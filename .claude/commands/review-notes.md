---
description: Review a topic's notes for mathematical correctness, typos and LaTeX health, and write a report
argument-hint: [topic_slug ...]  (omit — I'll list the topics)
allowed-tools: Read, Glob, Grep, Bash(latexmk:*), Bash(git rev-parse:*), Bash(date:*), Write(reviews/**)
---

Review the notes of one or more topics and write a report per topic to
`reviews/<topic>.md`. That directory is gitignored: the reports are local
scaffolding, not part of the repo.

Arguments given: $ARGUMENTS

**This command never edits `tex/`.** It reports; applying the fixes is a
separate instruction from the user. `allowed-tools` above enforces that — the
only writable path is `reviews/`.

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

Ignore any previous `reviews/<topic>.md`; review fresh and overwrite it.

## The report

Japanese, at `reviews/<topic>.md`, overwritten each run. Findings grouped by
category, ordered by `file:line` within each, numbered continuously across the
whole report so the user can say "1 と 4 を直して".

```markdown
# <DocTitle> レビュー

- 対象: `tex/<topic>/` (ch01.tex, ch02.tex)
- コミット: <git rev-parse --short HEAD>
- 日時: <date '+%Y-%m-%d %H:%M'>
- 指摘: 数学 1件 / 誤字・記法 2件 / LaTeX 0件

## 数学的正しさ

### 1. <一行の見出し> — ch01.tex:31  [確信度: 高]

> <該当行をそのまま引用>

<何が誤りで、なぜそうなのか>

**修正案**: <具体的にどう直すか>

## 誤字・記法

### 2. ...

## LaTeX の健全性

指摘なし
```

When a category has no findings, keep the heading and write `指摘なし`. When
nothing at all is found, still write the file — its existence is the proof that
the review ran.

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
