# Issue convention

GitHub issues are where a review finding lives from the moment it is found to
the moment it is fixed — or to the moment it turns out never to have been true.
`/review-notes` files them, `/git` closes them, `/verify-issues` checks whether
they hold and closes the ones that do not, and `/delete-topic` cleans them up;
`/issues` renders the open ones as a local file you can fix from.

**This is the single copy.** Those five commands point here and restate none of
it — the shape of an issue is one fact, and a fact written in five places is a
fact that will disagree with itself.

It replaced a local `reviews/<topic>.md` that was gitignored and overwritten on
every run, which meant a finding you had not got to yet was silently discarded
the next time you reviewed that topic. Nothing about the reviewing changed; only
where the findings go.

## One finding, one issue

Not one issue per review run with a checklist inside. A finding is closed
independently of its neighbours, carries its own labels, and is named by the
commit that fixes it — none of which a checkbox in a shared body can do.

## Language

**English for structure, Japanese for the mathematics.** Field names, field
values, label names and category names are English; the title's 見出し and every
line of explanation are Japanese.

The split is not cosmetic. The English half is queried — by `gh issue list
--label`, by a re-running review matching against open issues, by you scanning a
backlog. The Japanese half is read. A value that gets compared should not depend
on which language it was written in.

## Labels

Two axes, both machine-queryable:

| Label | Values | Colour |
| --- | --- | --- |
| `topic:<slug>` | the `tex/` directory name | `0e8a16` |
| `review:<category>` | `math`, `typo`, `latex` | `d73a4a`, `fbca04`, `1d76db` |

`topic:` is what makes the deduplication in `/review-notes` possible at all —
without it a re-run cannot ask what is already open for this topic.

`review:` maps onto the three categories the review already reports:
`math` = 数学的正しさ, `typo` = 誤字・記法, `latex` = LaTeX の健全性.

**Labels are created on demand**, by the command that needs one:

```bash
gh label create "topic:<slug>" -c 0e8a16 2>/dev/null || true
```

Creating a label that exists is an error, so the failure is swallowed. This is
deliberately not a setup step and deliberately not a job for `/new-topic`: a
label that must be created when a topic is created is a coupling rule, and a
coupling rule is a thing that gets forgotten and fails days later. On-demand
creation cannot be forgotten.

**There is no confidence label.** Confidence is in the body. It has already done
its work by the time an issue exists — you saw it at the confirmation gate and
chose to file this finding, so it is a note on the reasoning, not a filter.

## Title

```
ch01: 補題 1.2 の証明が空のまま $\blacksquare$ で閉じている
```

The chapter file, a colon, then the one-line 見出し the review would have used
as its section heading.

**No line number.** A line number in a title is wrong the moment you insert a
line above it, and nothing updates it. The chapter is stable enough to be worth
having when scanning a backlog that spans topics, and the body carries the
precise location.

**No topic prefix.** The `topic:` label says that, and says it in a form you can
filter on.

## Body

````markdown
**Confidence**: High
**Commit**: `af549ea`
**Location**: https://github.com/ys-math/math-study/blob/af549ea/tex/algebraic_k_theory/ch01.tex#L27

```tex
\begin{proof}

\end{proof}
```

`proof` 環境の中身が空白行だけなので、組版結果は「証明」の見出しと行末の
$\blacksquare$ だけになり、証明済みの補題として読めてしまう。

**Suggested fix**: 証明を書くまでは `proof` 環境ごと削除する。

```tex
\begin{proof}[\bfseries 証明 (略)]
\end{proof}
```
````

- **Confidence** — `High` / `Medium` / `Low`, on `review:math` issues only.
  `review:typo` and `review:latex` findings do not carry one, and the field is
  omitted rather than left blank.
- **Commit** — the short SHA the review was run against. Without it the quoted
  line has no referent.
- **Location** — see below.
- **The `tex` fence** — the offending line, quoted exactly. This is the copy that
  survives: it is right even after the file moves, and it is visible in
  `gh issue view` where a permalink is just a URL.
- **The explanation** — what is wrong and why, in Japanese.
- **Suggested fix** — the prose, then a second fence holding the replacement.
  Omit the whole block when there is nothing concrete to propose; never file a
  fence with a guess in it.

**A body written by a command goes through a quoted heredoc.** `/review-notes`
and `/verify-issues` have no write tool, so `--body-file` is unavailable to
them and the text reaches `gh` through the shell. Quote the delimiter —
`<<'EOF'`, never `<<EOF` — or the shell expands `$\blacksquare$`, `\begin` and
every backslash in the fenced `.tex`, which is most of what a body is.

### Location, and the dirty tree

**Location is a blob permalink pinned to the reviewed SHA**, not a branch URL.
GitHub renders a permalink on its own line as an inline snippet, and a pinned
SHA keeps pointing at what was actually reviewed however the file changes
afterwards.

```
https://github.com/ys-math/math-study/blob/<sha>/tex/<topic>/ch0N.tex#L<n>
```

**When the topic's files are dirty, there is no such SHA.** The content reviewed
is not in any commit, so a permalink would point at `HEAD` — a different version
of the file, possibly without the defect, and the link would look like it worked.

So a finding from an uncommitted file ships without a permalink:

```markdown
**Location**: `ch01.tex:27` (uncommitted)
```

The `tex` fence still carries the true line, which is why this degrades rather
than fails. The filing command warns at its gate so you can commit and re-run if
you want the links.

### Math renders as MathJax

GitHub renders `$…$` in issue bodies with MathJax, which — exactly like the
KaTeX preview the old reports were written for — knows nothing about
`tex/preamble.tex`.

- **Every line of `.tex` goes in a ```tex fence**, never inline and never in a
  blockquote. A bare `\id` or `\labelenumi` is parsed as math and dies.
- **In prose, use primitives only.** Write `$\mathrm{id}_P$` even where the note
  writes `$\id_P$`. When the finding is *about* the macro, put it in a code span
  — `` `\id_P` `` — not in math.

## Deduplication

A re-run of `/review-notes` finds every unfixed finding again. It lists the open
issues for the topic first and files only what is not already there.

**Matching is a judgement, not a key comparison.** The line will have moved and
the wording will differ; what matters is whether it is the same defect. Titles
and bodies are read, not just titles.

There is no hidden fingerprint in the body. A key would have to be invented by
the same judgement it claims to replace, and would fail silently — a
slightly-different key produces a duplicate with no sign anything went wrong. A
judgement that is unsure can say so, which is the whole difference:

```
Found 7 (new 5 / existing 2)
  1 math   補題 1.2 の証明が空          [High]  → #12
  2 math   命題 1.4 に (3)⇒(1) がない    [High]  → new
  3 typo   綴り誤り presentaion                 → same as #14?
```

An ambiguous match goes to the confirmation gate as a question. You decide.

**The mirror case is reported, never acted on.** An open issue the review no
longer detects is listed with a `gh issue close` hint and left alone. A finding
can go undetected because this run missed it, not because you fixed it, and a
command that closes on that evidence loses real defects quietly. `gh issue
close` is absent from `/review-notes`'s `allowed-tools`, and the omission is
deliberate — though it is a rule the command keeps rather than one the
frontmatter enforces (`docs/agent-system.md` `## Commands`).

### A rejected finding must not come back

`/review-notes` reviews fresh, by design. So a finding `/verify-issues` rejected
and closed will be re-derived by the next run, in the same way and for the same
reason, and re-filed — and verifying it again would close it again, forever.

So the fetch in `/review-notes` step 1 is **not** `--state open` alone. It also
reads the closed issues whose `stateReason` is `NOT_PLANNED`, which is exactly
the set `/verify-issues` rejected:

```bash
gh issue list --label "topic:<topic>" --state closed \
  --json number,title,body,stateReason --limit 100
```

A finding that matches one of those is a fourth class beside `new`, `#N` and
`same as #N?`:

```
  4 math   命題 3.5 の始対象性               → previously rejected #86
```

**It is shown, not dropped.** It defaults to not being filed, and the gate is
where you say otherwise. A rejection is a judgement and judgements are wrong
sometimes; silently suppressing a finding because a past run disbelieved it is
the same failure as silently closing one because a past run missed it, and this
file refuses that two paragraphs above.

## Verification

`/verify-issues` asks of an already-filed finding the one question `/review-notes`
could not ask of its own output: **is this true?** A review that reads fresh and
files what it finds will sometimes file something it invented, and nothing
downstream catches it — `/git` only ever sees the issues you chose to fix, and
`/issues` renders whatever is open without judging it.

### Four verdicts

| Verdict | What it means | What happens to the issue |
| --- | --- | --- |
| `upheld` | the claim holds against the sources | nothing |
| `upheld (body wrong)` | the defect is real, the body misdescribes it | the body is edited |
| `rejected` | the claim does not hold, and never did | closed, `--reason "not planned"` |
| `fixed` | the claim held when filed; the defect is gone | closed, reason `completed` |
| `unsure` | neither can be shown | nothing, and it is reported as a question |

`upheld (body wrong)` is a note on `upheld`, not a fifth verdict: the finding
survives either way, and only the body moves.

### Every verdict names a line

**`upheld` costs exactly what `rejected` costs.** Both must name a `file:line`
that settles them and say why in one sentence. Upholding by nodding along and
rejecting by asserting are the same error, and there is no verdict for "I read
it and it seemed fine" — that is `unsure`, which changes nothing.

The asymmetry worth knowing is in the consequences, not the burden. A wrongly
upheld finding stays open and wastes your time; a wrongly rejected one is closed
with a comment saying the mathematics was never wrong, and the defect goes back
into the notes with nothing left pointing at it. When the two verdicts look
equally supported, the answer is `unsure`.

This is the mirror of the rule `/review-notes` already keeps — *a finding must
name the specific line that fails* — pointed the other way.

### What separates `rejected` from `fixed`

One thing, and it is not a judgement:

```bash
git diff <the issue's **Commit**> -- tex/<topic>/
```

- The cited region is **unchanged** since that SHA and the claim does not hold →
  it never held. `rejected`.
- The cited region **changed** → the claim may well have held when it was filed.
  `fixed`, whatever it looks like now.

**A single SHA, not `<sha>..HEAD`.** The two-dot form compares commits and
ignores the working tree, so a defect you fixed an hour ago and have not
committed reads as unchanged — and the finding is closed as a hallucination with
your own correction sitting on disk beside it. That is the one mistake in this
section that writes a falsehood into the permanent record.

**A `fixed` verdict on a dirty topic is reported, never acted on.** The fix is in
no commit, `## Closing` gives that moment to `/git`, and closing it early leaves
`/git` proposing a `Closes` trailer for an issue that is already shut.

### The closing comment

One shape for both closes; the prose says which it is.

````markdown
**Verified**: `ca20f91`
**Evidence**: `ch03.tex:33`

```tex
$(B,x)$を$\mathscr{C}$の任意の対象と射の組とする.
```

指摘は「証明が $(B,x)$ を固定したまま始対象性と同値だとしている」というものだが、
`ch03.tex:33` は $(B,x)$ を任意に取っており、以降の議論もその一般性を保っている。
この指摘は成り立たない。
````

- **Verified** — the short SHA the verification read, or `` `ch03.tex:33`
  (uncommitted) `` when the topic was dirty, exactly as `**Location**` degrades.
- **Evidence** — the `file:line` that settles it. The same one shown at the gate.
- **The `tex` fence** — that line, quoted exactly, for the same reason the body's
  fence exists: it survives the file moving and it is legible in `gh issue view`.
- **The explanation** — Japanese, and it must engage the finding's own claim
  rather than restate the conclusion. A comment that says only 「この指摘は誤り
  です」 is not a reason and cannot be argued with six months later.

**Never close without one.** The comment is the whole of what makes a wrong
rejection recoverable: the issue is one click from reopening, and the comment is
the only thing that tells you it should be.

### The edited body

When only the body is wrong, the body is rewritten to `## Body` above, with
three things re-pinned to the SHA the verification read:

- **Commit** — the new SHA.
- **Location** — the permalink rebuilt on it, or `(uncommitted)` per
  `### Location, and the dirty tree`.
- **The `tex` fence** — re-quoted from the file *at that SHA*.

All three or none. A corrected fence under a stale `**Commit**` is a body that
contradicts itself, which is worse than the error it replaced — the original at
least described some version of the file truthfully.

The title is left alone unless it is the thing that is wrong. GitHub's *edited*
marker is the record that this happened; nothing is added to the body to say so.

### There is no verdict label

A third label axis would have to be created on demand, filtered against, and
kept in step with the two real ones — to record a distinction GitHub already
models. `stateReason` is a structured, English, queryable field that means
precisely "closed, but not because it was done":

```bash
gh issue list --label "topic:<topic>" --state closed \
  --json number,title,stateReason
```

That is how the hallucination rate gets counted, and how `/review-notes` knows
not to re-file what was rejected (`### A rejected finding must not come back`).
The Japanese comment says why; this says which.

## Closing

A finding that stands has two exits, and they are not interchangeable.
`/git` closes it when its fix is committed; `/verify-issues` closes one that
was never true, which has no fix and never will. This section is the first;
`## Verification` above is the second.

`/git` closes issues, at the moment the fix is committed.

When a commit touches `tex/<topic>/` and that topic has open review issues,
`/git` reads them, matches them against the diff, and puts the trailer in the
plan it already stops on:

```
fix(galois_theory): 補題 1.2 の証明を埋める

Closes #12
```

GitHub closes `#12` when the commit lands on `main`, which content commits do
directly. The trailer is proposed, never assumed — it appears in the plan and
you strike it out or add to it before anything is committed.

`Closes` is the only spelling used, for `git log --grep` to stay simple.

## Deletion

`/delete-topic` closes the topic's open issues and deletes its `topic:` label,
alongside the files. It already removes `pdf/<topic>.pdf` and the local worklist
for the same reason: nothing else prunes them, and an issue about a chapter that
no longer exists is unfixable and unfindable.

The issues and the label appear in its confirmation summary before any of it
happens.

## Reading them locally

`/issues [topic ...]` writes `issues/<topic>.md` — the open issues rendered with
**relative** links, `[`` `ch01.tex:27` ``](../tex/<topic>/ch01.tex#L27)`, which
VS Code's Markdown preview opens at that line in your own working copy.

That is the one thing issues are worse at than the file they replaced. A
permalink is correct and durable, and it opens a browser; while fixing, you want
the local file. So the worklist is generated rather than authoritative:
`issues/` is gitignored, every run overwrites it, and GitHub remains the record.

Regenerate it rather than trusting it. It is a snapshot of the issues at the
moment it was written, and it says so at the top.
