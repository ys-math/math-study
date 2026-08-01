---
description: Audit the commands, instructions and hooks for contradictions, stale claims and dead steps
argument-hint: "[file ...]  (omit — audits the whole system)"
allowed-tools: Read, Glob, Grep, Bash(python -m unittest:*), Bash(git rev-parse:*), Bash(git diff:*), Bash(date:*), Bash(printf:*), Bash(.claude/hooks/guard-bash.sh:*), Bash(.claude/hooks/guard-edits.sh:*), Write(.claude/audits/**), Edit(.claude/audits/**), Edit(CLAUDE.md), Edit(README.md), Edit(docs/**), Edit(.claude/commands/**), Edit(.claude/settings.json), Edit(.claude/hooks/**), Edit(.github/workflows/**)
---

Audit the machinery that tells Claude what to do — `CLAUDE.md`, `docs/*.md`,
`.claude/commands/*.md`, `.claude/settings.json`, `.claude/hooks/`,
`.github/workflows/*.yml`, and the prose in `README.md` outside the generated
markers — and write a report to `.claude/audits/audit.md`. That directory is
gitignored: the report is scaffolding, not a record. It sits inside `.claude/`
because what it describes does; the mathematics belongs to `/review-notes`,
which files its findings as GitHub issues rather than writing a report at all.

Arguments given: $ARGUMENTS

With paths given, audit those files but read the rest for context; a
contradiction is only visible from both sides. With no arguments, audit
everything.

All output is English.

**This command runs in two phases, and the second one is yours to authorise.**
Sections 1–3 read and report, exactly as they always have. Section 4 applies
fixes — but only the ones you name, after the report exists, in reply to the
index printed at the end of section 3. **Never edit anything before that
reply**, not even a defect so obvious it seems free: a fix applied before the
report is a fix you were never shown.

**It never audits `tex/**` or `scripts/**`.** The mathematics belongs to the
repo owner and to `/review-notes`; a note that contradicts itself is not this
command's business. `scripts/` is code with its own tests, and neither is
writable here — see `allowed-tools`. If a fix would need a change in either,
say so in the finding and leave it for the user.

## 1. Run the mechanical checks first

```bash
python -m unittest discover -s scripts -t scripts -p 'test_*.py'
```

`scripts/test_agent_docs.py` already decides every question that is a matter of
comparing names: which commands are listed where, whether the hooks are
registered and executable, whether the counts in the prose match the disk.

If it fails, open the report with those failures, quoted verbatim, as the first
findings — then **carry on with the audit**. They are cheap to fix and they do
not invalidate anything else.

If it passes, **do not re-derive any of it by hand.** A judgment finding that
restates what a green test already guarantees is noise, and it teaches the
reader to skim.

## 2. Read before filing

In this order, because each layer makes claims about the ones after it:

1. `CLAUDE.md` — loaded in every session, so anything wrong here is wrong everywhere.
2. `docs/agent-system.md` — the map; it asserts things about every other file.
3. `docs/git-strategy.md`, `docs/label-convention.md` — the specifications.
4. `.claude/commands/*.md` — **frontmatter included**; `allowed-tools` is half of what each command means.
5. `.claude/settings.json` and `.claude/hooks/*.sh` — what holds regardless of
   the prose. **Run the hooks; do not just read them.** Feed each one crafted
   `tool_input` JSON on stdin and check the decision, including the cases it is
   supposed to *allow*. Both enforcement gaps found on the first run of this
   command were invisible on the page and obvious in one command:

   ```bash
   printf '{"tool_name":"Bash","tool_input":{"command":"git clean -xdf -e main.pdf"}}' \
     | .claude/hooks/guard-bash.sh
   ```
6. `.github/workflows/*.yml` — what happens with nobody watching.

## What to report

Seven categories, and nothing else:

- **Contradiction** — two files stating different things about one fact, or a
  file contradicting itself. Both have happened here: three spellings of the
  `latexmk` invocation across six files, and `/label` declaring "All output is
  English" a hundred lines above an example printing `(空)`.
- **Stale claim** — a statement about the repo that the repo no longer
  satisfies. Verify it against the filesystem, never against another document;
  two documents can be stale in the same direction.
- **Capability mismatch** — the prose and `allowed-tools` disagree. Both
  directions count: a restriction claimed in prose but not in the frontmatter
  is a promise nothing keeps, and a tool granted but never used is a boundary
  wider than the command needs.
- **Dead instruction** — a step that cannot fire. A path, flag, file, tool or
  workflow that does not exist; an argument case nothing can reach; a rule
  whose trigger was removed.
- **Unreachable exit** — a procedure whose stopping condition cannot be met, a
  `/loop` target with no machine-readable terminal state, or a CI cascade with
  no fixed point. Say which of the two terminations is missing: output disjoint
  from the trigger, or convergence to identical bytes.
- **Unowned duplication** — one fact written in two places with neither
  declared the copy. The finding is the missing owner, not the second copy.
- **Enforcement gap** — a hook that does not refuse what it claims to refuse,
  or refuses what it should allow. The other six describe defects in prose;
  this one is for the two files that are code, and it is the category the first
  run of this command needed and did not have.

Do **not** report style, tone, ordering, length, or "this could be clearer".
The instructions are the owner's prose, on the same terms as the mathematics.

## Discipline

**Quote the line and name what breaks.** A finding is `file:line`, the text,
and the concrete wrong action an agent takes because of it — "an agent reading
`git.md:92` will compile 8 topics when there are 9". "These two sections feel
inconsistent" is not a finding; drop it rather than file it weakly.

**Divergence is not automatically drift.** Three commands list the repo's
topics in three different shapes — differing chapter counts, differing terminal
cases, one in Japanese — and every one of those differences is correct, because
the commands do different things. Before filing an unowned-duplication finding,
establish that the two passages make the *same* claim and that neither already
points at the other. Findings that get re-filed every run and dismissed every
run are how an audit becomes something nobody reads.

**Prefer the fix that deletes.** When one fact sits in two files, the repair is
usually to name an owner and replace the copy with a pointer — not to edit both
into agreement, which leaves two things to keep in step. Say which file should
own it.

Each judgment finding carries a confidence — High / Medium / Low — for triage.
That is calibration, not a licence to file guesses. Findings quoted from the
test run carry none; they are decided.

Ignore any previous `.claude/audits/audit.md`. Audit fresh and overwrite it,
carrying nothing over — including the state of its checkboxes, and including
findings you applied a fix for last time. A fix that did not take is a finding
this run has to rediscover on its own evidence.

## This is still not a `/loop` target

It used to be excluded for lacking a fixed point: the report was a function of
prose only a human edits, so a second unattended run reproduced the first
exactly. Section 4 removes that argument — an audit that repairs what it finds
*does* change its own inputs, and repeated runs converge on zero findings.

The gate is what keeps it out of a loop now. Section 4 waits for the user to
name the findings, so an unattended run either stalls there having done
nothing, or — worse, if it reads the gate as a formality — edits the owner's
instruction files with nobody watching. Convergence to a fixed point is not a
reason to get there unsupervised.

Run it after the system changes, not on a schedule. There is deliberately no
`audit: ...` line for a loop to read.

## The report

English, at `.claude/audits/audit.md`, overwritten each run. Findings grouped by
category, ordered by `file:line`, numbered continuously across the whole report
so the user can say "fix 2 and 5".

The two findings below are **real defects this repo had and has since fixed**,
shown for shape. Never copy a finding out of this file into a report; audit
what is on disk today.

````markdown
# Agent system audit

- Scope: `CLAUDE.md`, `docs/` (3), `.claude/commands/` (8), hooks, workflows
- Commit: <git rev-parse --short HEAD>
- Date: <date '+%Y-%m-%d %H:%M'>
- Mechanical: <n> tests, 0 failures
- Findings: 1 contradiction / 1 unowned duplication / 0 other

## Summary

- [ ] **1** Contradiction — `/label` declares English output, then prints `(空)`
      [`label.md:118`](../commands/label.md#L118) [High]
- [ ] **2** Unowned duplication — three spellings of the `latexmk` gate
      [`git-strategy.md:219`](../../docs/git-strategy.md#L219) [High]

## Contradiction

### 1. `/label` declares English output, then prints `(空)` — label.md:118  [High]

[`label.md:118`](../commands/label.md#L118)

```markdown
<the line, quoted>
```

Line 12 declares `All output is English`. An agent following the example emits
a Japanese status marker instead, so the two rules cannot both be obeyed and
which one wins depends on which the model read last.

**Fix**: line 12 is the owner — it is the standing rule, and the example is the
copy. Change `label.md:118` to `(empty)`.

## Unowned duplication

### 2. Three spellings of the `latexmk` gate — git-strategy.md:219  [High]

[`git-strategy.md:219`](../../docs/git-strategy.md#L219)

```bash
<the invocation, quoted>
```

Six files give this command and no two of the three variants agree on the
flags. Nothing declares which is authoritative, so each was edited on its own
and the most-cited one is missing `-g` — the flag that stops latexmk reporting
"Nothing to do" for a file that does not compile.

**Fix**: `docs/git-strategy.md` `## Gates` owns it and should say so in those
words. Replace the other five with a pointer rather than correcting them.

## Stale claim

None.
````

Every fence carries its location on the line directly above it, as a link —
the report sits in `.claude/audits/`, so paths are relative and the `#L<n>`
fragment opens the file at the line in a Markdown preview. Count the levels:
a sibling under `.claude/` is `../commands/label.md` or `../hooks/guard-bash.sh`,
and anything at the repo root is two up — `../../docs/git-strategy.md`,
`../../CLAUDE.md`, `../../.github/workflows/build-pdf.yml`. Keep the link text
in backticks so it still reads as a path. A **Fix** describes a change that is
not in the file yet, so it names its target in a plain code span, not a link.

Keep every heading, writing `None.` under the categories with nothing in them —
the absences are the part a reader trusts. Write every checkbox unticked: at the
time the report is written nothing has been fixed, and a re-run resets them.
Section 4 is the only thing that ever ticks one.

## 3. Print the index, then ask

Print a compact index to the chat — the path, the counts, one line per finding.
Not the report; it is in a file precisely so it does not fill the scrollback.

```
.claude/audits/audit.md written (mechanical: <n> pass / <category> <count> / …)

<Category>
  <n>. <the finding's one-line heading> — <file>:<line> [<confidence>]

Say which to fix — numbers, `all`, or nothing.
```

The index is placeholders on purpose: every value in it is already in the
report you have just written, so read them back from there rather than from
here. A worked example would be a second copy of the report example above, and
the two of them drifted apart the first time this file was edited — the index
went on claiming a finding about `/git-merge` that the report example had
dropped for being fabricated.

Then **stop and wait**. Silence is not consent, and neither is a report full of
High-confidence findings. If the answer names nothing, stop for good: the report
is on disk and nothing else was touched.

## 4. Applying the fixes

Only what the user named, and only the **Fix** the report already argued for.

**Apply the fix as written, or stop and say why.** The report is what the user
read before choosing; a fix that has quietly become something else is a change
they did not agree to. If applying one shows the reasoning was wrong — the line
moved, the quoted text does not match, two fixes contradict each other, the
repair turns out to need `scripts/` or `tex/` — apply nothing for that finding,
say so, and carry on with the rest.

**Edit the lines the finding quotes, and nothing else.** No reformatting, no
rewrapping a paragraph you touched one word in, no improving a sentence nearby.
These files are the owner's prose on the same terms as the mathematics: a diff
that is bigger than the finding is one the user cannot check against the report.
Where the fix is *"replace the copy with a pointer"*, deleting is the change —
do not also rewrite what you point at.

Two edits need saying out loud when you make them:

- **A fix inside `.claude/commands/audit.md` is a fix to the file you are
  executing.** The session keeps running on the version it loaded, so the change
  takes effect next run. Say which behaviour will differ, and do not re-derive
  the audit from the new text.
- **A fix inside `.claude/settings.json` or a hook changes what the *user's*
  next tool call is allowed to do**, this session included. Name the rule that
  moved.

### Verifying

Not optional, and not "the tests probably still pass":

1. `python -m unittest discover -s scripts -t scripts -p 'test_*.py'` — always,
   whatever you edited. Every fix here lands in a path that test reads: it holds
   the command tables to `.claude/commands/`, the hook and workflow and `docs/`
   names to their directories, and every count written in digits to what it
   counts. A fix that renames or deletes something is exactly what it watches for.
2. **If you edited a hook, run it again** — the same crafted stdin from section
   2, including the cases it must *allow*. A hook fix verified by reading is a
   hook fix not verified; that is how both enforcement gaps got in.
3. `git diff` over what you touched, read against the report. Anything in the
   diff that no finding asked for is yours to revert.

If a check fails, revert that fix rather than patching on top of it, and report
the failure with the finding it came from.

### Recording it

In `.claude/audits/audit.md`, tick the summary box of each finding you applied
and append ` — applied` to the line. Leave everything else exactly as written,
including the finding's own section: the report stays the argument for the
change, and the tick is the note that it happened. A finding you were asked for
but could not apply keeps its empty box and gets ` — not applied: <reason>`.

Then reprint the index with those markers, and **stop without committing.**
`docs/git-strategy.md` `## The shape` owns where a change goes and `/git` step 4
executes that table, so do not classify the commit here. The one thing worth
knowing in advance: a fix touching `.github/**` is the only one of these paths
that takes a branch and a PR. `/git` knows that, and the gates, and which paths
may carry `Co-Authored-By: Claude`. Say what changed and hand the working tree
over; do not re-implement any of it here.
