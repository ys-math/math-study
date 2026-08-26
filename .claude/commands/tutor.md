---
description: Consult about the mathematics, the LaTeX or the Lean in this repo, grounded in the passage you are actually asking about
argument-hint: "<question>  (plain language — the anchor is inferred and shown)"
allowed-tools: Read, Glob, Grep, Bash(gh issue list:*), Bash(latexmk:*), Bash(cd lean && lake build), Bash(git rev-parse:*)
disallowed-tools: Write, Edit
---

Answer a question about this repo's mathematics, its LaTeX or its Lean — after
finding the passage it is about, and after asking what the user already thinks.

Arguments given: $ARGUMENTS

**This command cannot write.** `disallowed-tools` removes `Write` and `Edit`,
and it is the only command here that uses that field; every other "never touches
X" in `docs/agent-system.md` is prose the reader has to trust. It is mechanical
here because the whole premise is that the user types the mathematics. A
`/tutor` that could patch a proof would be a slower `/formalize` with the fence
taken out.

English structure, Japanese mathematics, per `docs/issue-convention.md`
`## Language`. The same rule `/review-notes` and `/issues` follow, for the same
reason: the notes under discussion are written that way, and an explanation that
switches language halfway through a quotation is harder to read than either
language alone.

## What it is for

Three domains: **the mathematics**, **the LaTeX**, **the Lean**.

A question about the machinery — the git strategy, `scripts/`, CI, how to add a
chapter — is not a tutor question. Answer it plainly in a line or two, name the
file that owns it, and skip everything below. There is no understanding to
build there, only a fact to look up, and `CLAUDE.md` is loaded already.

The test is what the user is trying to do, not which file holds the answer.
Reading `docs/label-convention.md` to explain why a `\label{}` is being rejected
is a LaTeX question. Asking how `/label` works is not.

## 1. Find the anchor

The question names the mathematics, not the file. Locate it before reading
anything at length.

```bash
grep -rn "<the distinctive term>" tex/ lean/
```

Prefer terms that will not appear everywhere: a theorem name, a notation, a
`\label{}` body, a Lean declaration, the literal text of an error message.
Japanese terms grep as well as English ones and are usually the more
distinctive of the two in these notes.

Then **say what you chose, before answering anything**:

```
読んでいる箇所: tex/topology/ch02.tex §2.3「コンパクト性」(l.88–124)
```

One line, and it is the user's chance to redirect you. Answering the wrong
passage confidently is the failure this step exists to prevent, and it is
invisible to the user unless you say where you are reading.

- **Several plausible anchors** — name them as a numbered list and ask which.
  This is the one disambiguation question allowed before step 3.
- **No anchor** — say the question has no home in these notes, then answer it as
  general mathematics or hand it to `/teach-math`, which is built for exactly
  that and needs no repo. Do not promote a loose match to an anchor.

## 2. Climb only as far as you need

The anchor's own environment or section is always in scope — the
`\begin{theorem}…\end{theorem}` and the definitions it names, not the chapter
around it. Beyond that, climb a rung only when the question needs it:

| Rung | When | How |
| --- | --- | --- |
| `tex/preamble.tex` | the notation looks wrong | the theorem environments and the shared macros live there; without it a house convention reads as an inconsistency |
| the topic's open issues | whenever the topic is known | `gh issue list --label "topic:<topic>" --state open --json number,title,body` |
| the Lean mirror | the anchor carries a `\label{}` | `lean/Math/Study/<Topic>.lean` — the declaration sharing the label body, per `docs/lean-convention.md` `## The shared name` |
| a `docs/*-convention.md` | the question is about form | the one that owns it; `docs/agent-system.md` says which |

**The issues rung is the cheap one that changes the answer.** If
`/review-notes` has already filed a finding on the line being asked about, that
finding usually *is* the answer — and without the lookup you will re-derive a
known defect from scratch and present it as a discovery. One call, at the start.

**No cross-topic grep.** Sweeping every chapter that mentions the same notion is
a review, not a consultation, and `/review-notes` is the command for it.

Say which files you read. A consultation grounded in three files should name
three files; otherwise the user cannot tell grounded from remembered.

### Seeing the real error

When the question is why something does not build, read the actual error rather
than reasoning about the source.

```bash
latexmk -cd -g tex/<topic>/main.tex
cd lean && lake build
```

Both are the repo's own gates — `docs/git-strategy.md` `## Gates` owns the
flags and explains why `lake` is invoked through `cd` rather than `--dir`. They
write only build artifacts and `.olean` files, which is why they are reachable
from a command that cannot write.

**Warn before running `lake build` cold.** Against an unbuilt Mathlib it is
minutes, not the three seconds `README.md` quotes for a warm tree, and a
consultation that goes silent mid-question looks broken.

Skip both when the source answers the question on its own. A mismatched brace
does not need a compiler.

## 3. Ask, at most twice

Surface what the user already believes, then answer. These questions are not
disambiguation — step 1 already found the passage mechanically — and the answer
is not gated on the replies: step 4 gives the full argument either way. They
calibrate where to start, which step to spend the words on, and whether the
obstacle is the mathematics or the notation.

So a long interview is pure friction. **Two questions, and often none.**

Ask nothing when the question is already precise: a named lemma, a quoted error,
a specific step. Ask when it is not:

- What have you already tried, and where did it stop working?
- Which step stops convincing you? Not "do you follow" — which step.
- What did you expect to hold here that the notes do not say?
- Is the obstacle the mathematics, or how it has been written down?

One at a time, and wait for the answer. Two at once is a form, not a
conversation, and the user answers neither well.

## 4. Answer in full

Complete and rigorous, every time. Then stop — no coda, no related-topics list,
no proposed course of study. The user asked one question.

- **Motivation first**, then the content. Why the notion is set up this way
  before what it says.
- **Rigorous and constructive.** No ambiguous words, no logical gaps, nothing
  left as "clearly".
- **LaTeX for every formula.** Academic tone.
- **A proof if it is short**, a sketch if it would be long. Say which you gave.
- **No history, no exercises** unless the user asked for them.
- **No words inside formulas** or inside set-builder conditions.
- **Answer in the notes' own notation.** The anchor was read for this; an answer
  in different symbols makes the user do the translation.
- **Name the Mathlib lemma** when the question is Lean, and give the tactic
  block when that is what was asked.

The last one deserves saying plainly, because `CLAUDE.md` reads the other way at
a glance. Its fence — statements yes, proofs never — is about **files**:
"everything after `by` is the owner's". This command cannot write a file at all,
so it cannot cross that fence, and withholding in chat would only make it a
worse `/teach-math`. **The exercise is preserved by who types it, not by what
gets said.**

### These style rules are a deliberate copy

They overlap the `teach-math` skill in `~/.claude/skills/`, which is the user's
and lives outside this repo. Keeping a second copy is the intent: that skill is
not guaranteed to exist on a fresh clone, and a command that silently degrades
when a global skill is missing is worse than a duplicated paragraph. `/audit`
should report the duplication as intended rather than resolve it by deleting a
side.

Where the two differ, this file wins here, because `/tutor` answers a question
about a passage rather than delivering a lesson — hence no section-0 numbering,
no related-topics coda, no course plan.

## 5. When the notes are actually wrong

A consultation finds real defects, because it reads closely. Report them **under
their own heading**, after the answer, and say which command files them:

```
ついでに見つかったもの（回答とは別）:
  ch02.tex:96 — 補題 2.4 の主張がハウスドルフ性を落としている
  → /review-notes topology で issue にできます
```

Never fold a defect into the answer by explaining the theorem the notes *should*
have stated. That is the failure `CLAUDE.md` names for `/formalize` — repairing
a statement while translating it — arriving through a different door: the user
understands a corrected theorem, the notes stay wrong, and nothing anywhere
records the disagreement.

**This command files nothing.** `gh issue create` is absent from `allowed-tools`
deliberately: `docs/issue-convention.md` has one filing channel, and a one-off
finding from a consultation lacks the systematic sweep that makes a review issue
worth trusting. Hand it to `/review-notes` and let it decide whether the finding
survives a real review.

## Reporting

There is no report. The answer is the output, the working tree is untouched, and
nothing needs committing — `/tutor` writes no file, gitignored or otherwise.
