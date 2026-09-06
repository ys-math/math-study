---
description: Add a reference to a topic's bibliography.tex, creating the file and wiring it into main.tex if it has none
argument-hint: "<topic_slug> <citation>  (omit — I'll list the topics)"
allowed-tools: Read, Glob, Grep, Write(tex/*/bibliography.tex), Edit(tex/*/bibliography.tex), Edit(tex/*/main.tex), Edit(docs/bib-convention.md), Bash(latexmk:*), Bash(python -m unittest:*), Bash(python scripts/check_bibliography.py:*), Bash(grep:*), Bash(date:*), WebFetch(domain:ndlsearch.ndl.go.jp), WebFetch(domain:openlibrary.org), WebFetch(domain:api.crossref.org), WebFetch(domain:export.arxiv.org)
---

File a reference into a topic's `tex/<topic>/bibliography.tex`, creating that
file and `\input`ing it from `main.tex` before the colophon when the topic has
none yet.

Arguments given: $ARGUMENTS

All output is English. **Entries are shown verbatim** — see `## The proposal`.

**The rules are in `docs/bib-convention.md`. Read it first, every run.** It is
the single copy; nothing below restates the key shape, the entry shapes or the
ordering. This file is the workflow.

**This command reads catalogue records, never pages.** `allowed-tools` pins
`WebFetch` to a fixed set of catalogue hosts and carries no `WebSearch`, so an
ISBN, a DOI or an arXiv id can be resolved against the body that issues it and
nothing else is reachable. That
distinction is the whole of the design. A record is re-queryable and somebody
else is accountable for it; a page that merely mentions the book is prose, and a
field lifted out of prose is a guess wearing a citation's clothes. A citation is
a factual claim about a physical object — the series number, the publisher, the
year — and a wrong one does not look wrong: it produces a well-formed `\bibitem`
naming a book that reads as real. So a record proposes and the user disposes;
`## Looking it up` is the whole procedure. If neither the arguments nor a record
carries a required field, ask for it; never fill it in.

**This command never edits `tex/*/ch*.tex`.** `Edit(tex/*/ch*.tex)` is absent
from `allowed-tools`. It does not insert `\cite{}` and does not offer to:
deciding which sentence attributes a result to which author is a claim about
the mathematics, inside the owner's prose, and CLAUDE.md's first fence is
exactly that. Report the key at the end and let the user type the `\cite`.

**It cannot commit.** No `git` verb is in `allowed-tools`. See `## Afterwards`.

**It appends; it does not amend.** See `## Already there`.

## Picking the topic

- **Slug given** — handle it.
- **No arguments** — list every topic as a numbered plain list, showing the
  slug, the `\DocTitle` from its `main.tex`, and whether it already has a
  `bibliography.tex`. Stop and wait.
- **Unknown slug** — say so, print the same list, stop.
- **Slug but no citation** — say what is missing, print nothing else, stop.

## Reading

1. `docs/bib-convention.md` — the rules.
2. `tex/<topic>/bibliography.tex`, if it exists — every existing key, and every
   existing entry, as the duplicate set for `## Already there`.
3. `tex/<topic>/main.tex` — whether `bibliography.tex` is already `\input`, and
   where the colophon line is.

A file that exists but is not `\input` is a real state and a silent one: it
compiles fine and appears nowhere. Say so if you find it, and treat the run as
a create for the `main.tex` half.

## Looking it up

**Check `## Already there` first.** A reference the topic already holds needs no
record, and the duplicate check reads only files. Ordering it before the query
is not about the network round trip; it is that a duplicate must produce the
same refusal whether or not a catalogue happened to answer.

**When to query.** An identifier always queries — it is one exact call, so
checking the user's own fields against a record costs nothing beyond it. A
missing required field queries. A complete citation carrying no identifier does
**not**: verifying it would mean a title search and a candidate list for an
entry the user already considers finished. Say which happened in the report —
"filed from your text alone; no identifier to check it against" — because an
entry nobody checked and an entry that checked clean must not read the same.

| given | host | query |
| --- | --- | --- |
| ISBN beginning `4-` or `978-4-` | `ndlsearch.ndl.go.jp` | `/api/opensearch?isbn=<isbn>` |
| any other ISBN | `openlibrary.org` | `/isbn/<isbn>.json` |
| DOI | `api.crossref.org` | `/works/<doi>` |
| arXiv id | `export.arxiv.org` | `/api/query?id_list=<id>` |
| title, Japanese | `ndlsearch.ndl.go.jp` | `/api/opensearch?any=<title and author>&cnt=5` |
| title, Latin script | `api.crossref.org` | `/works?query.bibliographic=<title and author>&rows=5` |

**A URL is mined for an identifier, never fetched.** `arxiv.org/abs/1612.09375`
is an arXiv id, `doi.org/10.2307/1969983` is a DOI, and a publisher page with an
ISBN in its path is an ISBN. A URL carrying none of those is not a lookup at
all: it is a web resource, whose site name and page title come from the user
exactly as before. Only the access date is yours to supply — `date +%F`, said in
the proposal to be the run date, and overridden if the user read the page
earlier. None of the four hosts can serve an arbitrary page, so this is a rule
the `allowed-tools` line already enforces; it is written here so the refusal is
explained rather than mysterious.

**A title query proposes candidates and stops.** Show up to five, with the
fields that tell them apart — year, publisher, edition, identifier — and let the
user pick before anything is rendered as a `\bibitem`. Never auto-select, not
even on an exact title match: what that gets wrong is editions, and this repo
already contains the example, since `『復刊 可換環論』` (2000) and `『可換環論』`
(1980) are the same author, title and publisher. A ranked first hit is a guess
with a rank on it. `query.bibliographic=Basic Category Theory Leinster` returns
the Cambridge monograph first, which is a different object from the arXiv
preprint `tex/category_theory` actually cites.

**One source per proposal.** Every field on screen should trace to one query.
An absent *optional* field — a series — is omitted and named as absent, so the
user can tell "this book has no series" from "that record did not say". An
absent *required* one is asked for. Cross-checking a second catalogue is
**offered, never done silently**: an entry quietly assembled from two records is
one that no single record supports, and it may describe two different printings.

**Conflicts do not overwrite.** Where a record contradicts a field the user
typed, the proposed entry keeps the user's bytes and the report carries the
disagreement, naming both values and the host — "you gave 1995; openlibrary.org
gives 1996 for that ISBN. Not changed. Say which." A record is evidence, not a
verdict, and the entry is the user's claim to make.

**Failure degrades to the old behaviour.** Zero results, a 404, or a host that
does not answer is reported as exactly that, and then the missing fields are
asked for. Never proceed on a partial record as though it were whole, and never
substitute another host for a failed one without saying so.

### What each record actually returns

None of the following is guessable from the API's documentation, and each was
observed against a reference this repo already cites.

- **NDL matches the ISBN string its record carries.** A pre-2007 Japanese book
  holds only an ISBN-10, so `isbn=9784320016582` returns zero results for
  `『復刊 可換環論』` while `isbn=4-320-01658-0` returns it. Hyphens are
  tolerated; the wrong length is not. On zero results, try the other form before
  reporting nothing found. Do not trust the record's own `dcndl:ISBN13` field to
  be an ISBN-13 — for that book it repeats the ISBN-10.
- **NDL's `dc:creator` carries life dates**: `松村, 英之, 1930-1995`. Line 1 is
  `松村英之` — the dates and the comma go, and so does the 著 that a cover or
  another record may append. `docs/bib-convention.md` `### Line 1` has the rule.
- **NDL has no media-type filter that this repo has verified.** Do not invent
  one; an unknown parameter is silently folded into the query text and returns
  nothing. Narrow a Japanese title search by putting the author in `any=`.
- **Crossref's `page` may be the first page alone.** `10.2307/1969983` returns
  `"page": "399"` for the paper whose range is 399–405. A page range is required
  by the article shape, so ask for it; never file a single page as a range.
- **Crossref gives the journal's formal name and the publisher's
  capitalisation** — `The Annals of Mathematics`, `On Manifolds Homeomorphic to
  the 7-Sphere`, where `tex/category_theory`'s sibling entry uses the usual name
  and sentence case. Both are proposals to show, never corrections to apply.
- **Do not put an email address in the request.** Crossref's polite pool asks
  for a `mailto`; the anonymous pool answers, and the owner's address is not
  this repo's to hand to a third party.
- **OpenLibrary's `authors` are keys, not names.** `/isbn/<isbn>.json` gives
  `{"key": "/authors/OL321218A"}`, and the name needs a second fetch to
  `/authors/OL321218A.json` — which answers `Rosenberg, J.`, already initialised
  and in the wrong order for line 1.
- **OpenLibrary's `series` arrives split and lowercased**:
  `["Graduate texts in mathematics ;", "147"]`. Joining it is mechanical; the
  capitalisation the entry wants is editorial, so show the raw value beside it.
- **OpenLibrary's `publish_date` is the printing that record describes.** For
  the ISBN of `bib: Rosenberg` it says `1996`, where the entry says 1994. That
  is a conflict to report, never a year to correct.
- **`publish_places` is returned and dropped** — `["New York"]` for that same
  book. `docs/bib-convention.md` `#### A book` says why.
- **arXiv's year is `<updated>`, not `<published>`.** The convention cites the
  version you read: `1612.09375v2` is `<updated>2025-08-26`, published 2016. The
  class is `<arxiv:primary_category>`, not the first `<category>` — they happen
  to agree for that paper and need not.
- **An `<arxiv:journal_ref>` means the preprint shape is wrong.** The convention
  says a preprint since published takes the book or article shape instead, and
  that element is how you find out. Report it and let the user choose the shape;
  do not switch shapes on your own.

## The proposal

Show, and then stop:

- the rendered `\bibitem`, **byte for byte as it will be written**
- the key, and — if it carries a year — that it was a collision, naming the key
  it collided with
- which kind it is (book, journal article, arXiv preprint, web resource, or
  one whose locator is being proposed under the convention's fallback), and
  which line-2 markup that gives it
- where it lands in the list, by the entry it follows
- every structural change: creating `bibliography.tex`, inserting the `\input`
  into `main.tex`, widening `{9}` to `{99}`
- when a record was read: the host, the identifier queried, each raw field used
  and the transform applied to it — see below

**Verbatim means verbatim.** Do not tidy 松本幸夫 into "Y. Matsumoto", do not
normalise `$K$-Theory`, do not fix the user's capitalisation. The user approves
what the preview shows, so the preview and the write must be the same bytes; a
helpful adjustment between the two means approving one thing and filing
another.

**Verbatim binds the user's bytes; a record's fields are transformed by
definition.** The two rules never meet, because they never apply to the same
string. Nothing the user typed is adjusted. Everything a record supplies is:
`{"given": "John", "family": "Milnor"}` is not a line 1, and neither is
`Rosenberg, J.` or `松村, 英之, 1930-1995`. What keeps that honest is showing
each transform next to its input, so what the user approves is the change and
not merely its result:

```
\bibitem{bib: 松村}
松村英之,
『復刊 可換環論』,
共立出版, 2000.

  ndlsearch.ndl.go.jp — isbn=4-320-01658-0
    dc:creator      「松村, 英之, 1930-1995」 → line 1, life dates dropped
    dc:title        「可換環論」               → line 2, 『』 added
    dc:publisher    「共立出版」               → line 3
    dcterms:issued  「2000.9」                 → line 3, year only
    ! no series field in this record
    ! you gave 『復刊 可換環論』; the record says 『可換環論』. Kept yours.
```

**Never write on the first turn.** There is more judgement in an append than it
looks — which of `J.`/`Jonathan` the author gets, whether "Graduate Texts in
Mathematics 147" is a series or part of the title, whether the thing is a book
or an article, whether the key collides. Those are the decisions worth showing.

If the citation is of a kind the convention fixes no locator for, build lines 1
and 2 from the grammar — those it settles for every kind, and they need no
approval — then propose **line 3 only**, and say in the proposal that accepting
it also writes that locator into `docs/bib-convention.md`. That is the
convention's own fallback rule and it is not optional: a locator approved and
not recorded means the next entry of the kind gets a different one, with nothing
to report the divergence. The place-of-publication field that was present in one
book entry and absent from another is what that looks like when it happens.

## Already there

Before proposing, check the existing entries two ways:

- the proposed **key** is already used
- the proposed **author and title** already appear, under any key

Either way: show the existing entry, say which check matched, and stop. Do not
file a second copy, and do not update the existing one — `Edit` on
`bibliography.tex` is for appending and for the `{9}` widening, not for
rewriting an entry that was already reviewed and approved once. A mistyped year
in the arguments must produce a refusal naming the existing entry, never a
silent overwrite of a correct one. Fixing a wrong field is a hand edit.

## Applying

Only after the user approves.

**Baseline first, always:**

```bash
latexmk -cd -g tex/<topic>/main.tex
```

That baseline is the only way to tell "this topic was already broken" from "I
broke it", and `-g` is what makes it one: without it latexmk answers "Nothing to
do" from cache for a file that does not compile. `docs/git-strategy.md`
(`## Gates`) is the single copy of this invocation; do not add `-r`. Report a
pre-existing failure and ask whether to continue.

`/label` takes this baseline only for renames. This command takes it every run,
on purpose: it runs a handful of times per topic ever, so the second compile
costs nothing, and a pasted title carrying `$K$-Theory` or a stray brace fails
in a way that looks nothing like its cause.

**Then:**

- **Appending** — insert the `\bibitem` in alphabetical position. Widen `{9}` to
  `{99}` if this is the tenth entry.
- **Creating** — write `bibliography.tex` with the skeleton the convention
  gives, licence header included. `.claude/hooks/guard-edits.sh` blocks the
  write without it, so a missing header is a blocked tool call, not a silent
  hole.
- **Wiring** — insert into `main.tex`, before the colophon:

  ```tex
  \newpage
  \input{bibliography.tex}
  ```

  Match `tex/algebraic_k_theory/main.tex` exactly: the blank line, the
  `\newpage`, the `\input`, then the blank line and `\newpage` that already
  precede `\input{../colophon.tex}`.

## The skeleton guard

**Only when `main.tex` was edited.** `scripts/test_new_topic.py` asserts that
`MAIN_TEMPLATE` in `scripts/new_topic.py` reproduces certain topics' `main.tex`
**byte for byte**, and adding an `\input` line to one of those breaks it.

Read which topics those are rather than remembering them:

```bash
grep -n 'assert_reproduces' scripts/test_new_topic.py
```

The test's own docstring says a topic is dropped from that list once its
`main.tex` "has grown past the skeleton" — so the topic you just edited leaving
the guard is the designed outcome, not damage. What is not this command's to do
is perform it: `scripts/` is a shared path under `docs/git-strategy.md`, and
`Edit(scripts/**)` is absent from `allowed-tools`.

So: run the suite, and report the failure as a finding with its fix.

```bash
python -m unittest discover -s scripts -t scripts -p 'test_*.py'
```

This matters because of what the user will do next. `tex/<topic>/**` commits
straight to `main`, so the natural move is `/git` — whose gate runs this same
suite and will stop with an error that looks unrelated to adding a reference.
Say plainly: the topic left the skeleton guard, `scripts/test_new_topic.py`
must drop it, and that is a `scripts/` change, so it takes a branch and a pull
request.

## Verifying

After the edits, in this order:

1. **Structure** — run the checker on the topic:

   ```bash
   python scripts/check_bibliography.py <topic>
   ```

   It reads the SPDX header, the key shape, the three-line grammar, the line-2
   markup, the ordering and the `{9}` width, so none of those need checking by
   eye. What it does not read is whether the key appears exactly once in the
   topic — check that yourself, and remember the checker is silent about every
   factual field in the entry.
2. **Compile** — the same `latexmk` line. Suppress Overfull/Underfull `\hbox`
   warnings; Japanese in `jlreq` emits them constantly and they bury everything
   else.
3. **The suite**, if `main.tex` changed — `## The skeleton guard`.

If the compile fails, say so with the `-file-line-error` lines and stop. Do not
attempt a second round of fixes on top of a broken build.

Aux files and `main.pdf` are gitignored — leave them, do not run `latexmk -c`.

## Afterwards

Report compactly: the entry, the key, the structural changes, the compile
result, the suite result when it ran, and **where the fields came from** — the
host and identifier, or the plain statement that nothing was checked against a
record. An unverified entry and a verified one must not read the same three
weeks later.

```
tex/algebraic_k_theory/bibliography.tex — added bib: Milnor (2 entries)

  J. Milnor,
  ``On manifolds homeomorphic to the 7-sphere'',
  \textit{Annals of Mathematics} \textbf{64} (1956), 399--405.

  placed after bib: Rosenberg  ·  main.tex unchanged
  fields from api.crossref.org, doi=10.2307/1969983; pages yours
  check_bibliography: OK  ·  latexmk: OK

Cite it with \cite{bib: Milnor}.
```

**Do not commit.** `tex/<topic>/**` commits straight to `main` per
`docs/git-strategy.md`, but that is `/git`'s job — the user may want to adjust a
field by hand first, and an unwanted `\bibitem` is one `git restore` away. Say
the changes are uncommitted; do not offer to commit them.
