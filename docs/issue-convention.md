# Issue convention

GitHub issues are where a review finding lives from the moment it is found to
the moment it is fixed. `/review-notes` files them, `/git` closes them, and
`/delete-topic` cleans them up; `/issues` renders the open ones as a local file
you can fix from.

**This is the single copy.** Those four commands point here and restate none of
it — the shape of an issue is one fact, and a fact written in four places is a
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
close` is absent from `/review-notes`'s `allowed-tools`, so this holds whatever
the model decides.

## Closing

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
