---
description: Have a blind reader turn a chapter's Lean statements back into English TeX, so you can audit them against your notes
argument-hint: "[<topic_slug> <chapter>]  (omit — I'll show every chapter's audit state)"
allowed-tools: Agent, Bash(python scripts/lean_statements.py:*), Edit(lean/Math/Study/**/*.readback.tex)
---

Turn the statements in `lean/Math/Study/<Topic>/C<NN>.lean` back into English,
using a reader that has never seen the notes, and file the result next to them
as `C<NN>.readback.tex`. **You** then compare it with the chapter. This command
never does that comparison.

Arguments given: $ARGUMENTS

All output is English.

`docs/lean-convention.md` `## Read-back` is the specification — the audit
stamp, what makes a block stale, who may set `audited=yes`. Read it first. This
file is the workflow.

## Why the reader is blind

A `/formalize` mistranslation reads green everywhere: it builds, `sorry` is
honest, CI passes. The only instrument that sees it is a reading of the Lean
that owes nothing to the note, so that a dropped hypothesis shows up as a
missing clause in the English. A reader who has seen the note writes the note
back, and the audit passes for the wrong reason.

So blindness is structural, not a request:

- **The reader is `.claude/agents/read-back.md`**, a subagent. It starts with
  none of this conversation, and its one tool is `Write` — it cannot read
  `tex/`, `pdf/`, the Lean source or anything else.
- **What it is shown is a dump, not the source.** `scripts/lean_statements.py`
  prints what Lean *elaborated*, with theorem names replaced by `T<n>` and no
  comments: the name is the `\label{}` body, and a reader shown it could read
  the name instead of the type.
- **You pass the dump through untouched.** Do not summarise, annotate, reorder
  or explain it in the prompt, and add nothing you know about the topic, its
  notes, or its chapter titles. The prompt below is the whole prompt.

## 1. No arguments — status, and stop

```bash
python scripts/lean_statements.py status
```

Print its table — per chapter: declarations, unread, stale, unaudited,
audited — and any orphaned blocks it reports, then stop. Suggest
`/read-back <topic> <chapter>` for any chapter with unread or stale rows.

## 2. Prepare

```bash
python scripts/lean_statements.py prepare <topic> <chapter>
```

It builds the module, dumps it, and prints the handoff path, the `read:` ids
and the reader view. A build failure is a stop: the statement file does not
elaborate, and that is `/formalize`'s to fix.

If `read:` says nothing needs reading, say every block is current, print the
status line for the chapter, and stop.

## 3. Launch the reader

One `Agent` call, `subagent_type: read-back`, with exactly this prompt and the
printed values substituted:

```
Handoff path: <absolute path of the handoff file>
Answer for: <the read: ids, space-separated>

<the reader view, verbatim, everything after the "--- reader view ---" line>
```

Nothing else. Wait for it to finish.

## 4. Assemble

```bash
python scripts/lean_statements.py assemble <topic> <chapter>
```

It files the reader's answers as fresh blocks, keeps every current block byte
for byte, drops orphaned ones, and compiles the result into
`lean/.lake/readback/` as a check. It refuses — writing nothing — if the reader
skipped an id, answered for one it was not asked, or wrote non-ASCII. On a
refusal or a compile failure, launch the reader once more with the same prompt
and assemble again; if it fails twice, report the error and stop.

**Never edit the reader's text**, even where it is plainly wrong about the
notes. It is wrong about the notes by design — it has not read them — and
correcting it with what you know is exactly the leak this command exists to
prevent. If the reading is wrong about the *Lean*, re-run the reader; do not
fix it by hand.

## 5. Report

Print the path of the read-back and of its compiled PDF, which blocks are new,
which were stale and have lost their audit, and every `NOTE:` the reader wrote,
each under its declaration name. Then say what the owner does next:

- read the PDF beside the chapter;
- where a block matches the note, set its stamp's `audited=no` to `yes`;
- where it does not, decide which side is wrong — the note (`/review-notes`) or
  the Lean (`/formalize <topic> <chapter>` with the row named as `modify`).

Do not offer your own comparison, and do not suggest which blocks look fine.

## Setting `audited=yes`

**Only on the owner's explicit instruction naming the blocks** — "mark
`projective_of_free` audited". Then change `audited=no` to `audited=yes` on
exactly those stamp lines and touch nothing else. Never set it on your own
initiative, never propose it, and never after comparing anything to the notes:
an audit is the owner's reading, and a stamp Claude chose is not one.

This command never commits; `/git` does.
