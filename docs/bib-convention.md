# Bibliography convention

A topic's references live in `tex/<topic>/bibliography.tex`, as `\bibitem`s
inside a `thebibliography` environment. This document fixes three things: **the
citation key**, **the grammar every entry instantiates**, and **the order**.

The day-to-day version is the `/bib` command, which implements this document;
read on when you are adding a reference by hand, or when you want the reasoning.

**The filename and where it is `\input` are `docs/naming-convention.md`**, not
this document — `## Inside a topic` owns both, including why the file is spelled
out rather than numbered. The two meet at one point: this document assumes the
file exists at that name and in that position, and says nothing more about it.

**No BibTeX.** There is no `.bib` file, no `\bibliographystyle`, and neither
`biblatex` nor `natbib` is loaded in `tex/preamble.tex`. A topic here carries a
handful of references, and the machinery would buy nothing while making every
build depend on a `biber` pass that `.latexmkrc` does not configure. The entries
are written out by hand, which is what the rest of this document is about.

One consequence worth knowing, because it differs from BibTeX: **an uncited
`\bibitem` still prints.** Nothing warns. A reference list that names a book you
read and never cited is therefore a normal thing here, not an oversight.

**Part of this document is checked.** `scripts/check_bibliography.py` validates
the structure below against every `tex/*/bibliography.tex`, and runs wherever
the `scripts/` tests already run. `## What is checked` says exactly how far it
reaches, and — more importantly — how far it cannot.

## The key

```
bib: <Surname>
```

`bib`, colon, **one space**, the author's surname — the same
`<abbr>: <body>` shape `docs/label-convention.md` fixes for `\label{}`, and for
the same reason: a key is read out of context, from a completion list inside
`\cite{`, where the prefix is the only thing saying what kind of name it is.

```tex
\bibitem{bib: Rosenberg}
```

The space after the colon is harmless. LaTeX carries it through unchanged —
`main.aux` records `\bibcite{bib: Rosenberg}{1}` — and `\cite{bib: Rosenberg}`
resolves.

**Bare by default.** Only when a surname is already taken does the key gain the
year:

```
bib: Weibel1994
bib: Weibel2013
```

This is `label-convention.md`'s namespace rule transferred without change —
"Default to bare. Reach for the namespace at that point, not before" — and it
accepts the same visibly mixed result, some keys bare and some carrying a year.
That is the intended state, not drift. The year is used rather than a word from
the title because the year is already sitting in the citation you typed, while
choosing a distinguishing word is a judgement, and the value of this convention
is that a proposed key can be approved at a glance.

**Multiple authors take the first author's surname**, unless the work is
universally known by more than one — `bib: EilenbergSteenrod`. "Universally
known" is the test, not "has two authors".

**A web resource collides on a title word, not the year.** Its key body is the
site or project name — `bib: nLab`, `bib: Stacks` — and the year rule above
fails for it outright: two nLab pages read on the same afternoon both want
`bib: nLab2026`. So the distinguishing part comes from the page title instead,
in `UpperCamelCase`:

```
bib: nLabAdjoint
bib: nLabMonad
```

This is the one place the year rule is departed from, and the reason is narrow:
the year is used everywhere else *because* it distinguishes, and here it does
not. Everything else about the key is unchanged — bare by default, so the first
nLab entry is `bib: nLab` and gains its page only when a second one arrives.

## The grammar

Every entry, of every kind, in every language, is **three lines**:

```
<author>,
<title>,
<locator>.
```

One group per line, so that a diff shows which part of a reference changed
rather than reflowing the whole entry. Lines 1 and 2 end in a comma, line 3 in a
full stop. There is no fourth line and no two-line entry.

Three lines rather than four — with the container getting a slot of its own —
because containerhood is not an extra field: it is a property of the title. A
book *is* its container; an article is not. Line 2 says which, in its markup,
and line 3 is then uniformly "how you look it up".

### Line 1 — the author

Initial and surname; given names are initials, not spelled out. Multiple authors
are **all** listed, commas between, `and` before the last:

```
J. Rosenberg,
S. Eilenberg and N. Steenrod,
M. Hovey, J. Palmieri and N. Strickland,
```

**No `et al.`** A topic here carries a handful of references, the author lists
are short, and a truncation rule is a threshold to remember and a judgement for
`/bib` to make, in exchange for saving a line that was never long.

**An authorless work puts the responsible body here** — the site, the project,
the editorial department. `nLab,`  `The Stacks Project,`  `数学セミナー編集部,`.
This is what keeps a web resource a three-line entry rather than a two-line
exception, and it is also where its key body comes from.

### Line 2 — the title

The markup is decided by two things: whether the work is its own published
container, and what language it is in.

| | self-contained | inside a container |
| --- | --- | --- |
| Latin script | `\textit{Title}` | `` ``Title'' `` |
| 日本語 | `『題名』` | `「題名」` |

**The italic marks the published container** — the thing you would look up in a
catalogue. For a book that is the book; for an article it is the journal, which
lives on line 3, never the article's own title. That single rule is what keeps
every shape below consistent with the others.

**Language is an axis, not a kind.** A Japanese article, a Japanese preprint and
a Japanese website all follow the row above without needing an example each.
『』 and 「」 sit exactly where `\textit{}` and the quotes sit.

**Quotes are `` `` `` and `''`, never `"`.** This is not a stylistic
preference. Under `jlreq` with LuaLaTeX the encoding is `TU` and the input `"`
typesets as `”` — a *closing* quote — so `"Title"` prints with a closing quote
at both ends. The source looks balanced and the PDF is wrong, which is why the
pair is fixed here rather than left to the eye.

**Do not wrap Japanese in `\textit{}`.** It is inert: Japanese fonts have no
italic, so under `jlreq` with LuaLaTeX the CJK renders upright and the markup
carries nothing. The source looks correct and the emphasis is silently absent
from the PDF — which is why 『』 has to do the work rather than sit inside an
italic that does nothing.

**Do not romanise.** The notes are in Japanese, and a transliterated title
cannot be looked up in a Japanese catalogue or ordered from a Japanese
bookshop — it optimises for a reader who is not here.

### Line 3 — the locator

This is where the kinds differ, and the only place they do.

#### A book

```tex
\bibitem{bib: Rosenberg}
J. Rosenberg,
\textit{Algebraic $K$-Theory and Its Applications},
Graduate Texts in Mathematics 147, Springer-Verlag, 1994.
```

Series and number, publisher, year.

**No place of publication.** It is the field most often unknown or ambiguous —
Springer alone prints Berlin, New York and Cham on comparable volumes — and
`/bib` cannot look anything up, so requiring it means either blocking on the
user for a datum they rarely have to hand, or inviting a guess. A guessed place
produces a well-formed entry that reads as real, which is the failure this
document exists to prevent.

#### A journal article

```tex
\bibitem{bib: Milnor}
J. Milnor,
``On manifolds homeomorphic to the 7-sphere'',
\textit{Annals of Mathematics} \textbf{64} (1956), 399--405.
```

Journal italic, volume bold, year parenthesised, page range with an en-dash
(`--`).

#### An arXiv preprint

```tex
\bibitem{bib: Leinster}
T. Leinster,
``Basic Category Theory'',
preprint, arXiv:1612.09375 [math.CT], 2025.
```

**No `\textit{}` anywhere.** The italic marks a published container and a
preprint has none, so italicising the title would claim a container that does
not exist — which is exactly why line 2 quotes it instead.

The arXiv identifier stands where the journal, volume and pages stand, because
it is what you look the thing up by: `arXiv:`, the number, the primary class in
brackets, then the year of the version cited.

**No `\url{}` here.** `arXiv:1612.09375` already resolves, and a URL beside it
duplicates the identifier. The `url` field of a pasted BibTeX entry is dropped,
not transcribed. This rule is about the arXiv identifier being self-sufficient;
it does not reach the web shape below, where the URL *is* the identifier.

**A preprint since published takes the book or article shape instead**, with its
publisher or journal and that year. The shape follows the object you mean to
cite, not the file you happened to paste.

#### A web resource

```tex
\bibitem{bib: nLab}
nLab,
``adjoint functor'',
\url{https://ncatlab.org/nlab/show/adjoint+functor}, 2026-08-31.
```

`\url{}`, then the access date, then the full stop. `url` is loaded with
`[hyphens]` in `tex/preamble.tex`, so a long URL breaks rather than running into
the margin.

**The date is the access date, bare and ISO 8601.** Bare, with no `accessed` or
`閲覧` in front of it, because a label word would have to pick a language: English
reads as an intrusion in Japanese notes, and 閲覧 reads oddly beside a
Latin-script site name. `YYYY-MM-DD` is unambiguous in either language and needs
no word to explain it.

It is an *access* date rather than a publication date because a web page has
neither a fixed publication nor a guarantee of permanence — the date records
which version you actually read, and is the only date the entry carries.

A Japanese page takes the same line, with 「」 on line 2:

```tex
\bibitem{bib: 数学セミナー編集部}
数学セミナー編集部,
「圏論のはなし」,
\url{https://example.jp/...}, 2026-08-31.
```

### Anything else

The grammar settles lines 1 and 2 for a kind this document has not met — a
chapter in a collected volume, a lecture-note set, a recorded talk. The author or
responsible body goes on line 1; line 2 is decided by the table above, on whether
the thing is its own published container. Neither needs approval.

**Line 3 does.** A locator convention this document does not fix is the one part
that can be invented two different ways, with nothing anywhere reporting the
divergence — which is how the place-of-publication field came to be present in
one book entry and absent from another. So: **propose the locator, get it
approved, and write it into this document in the same change.** Not doing so
means the next entry of that kind gets a different line 3 from the first.

## The order of entries

**Alphabetical by surname** — which is to say, by the key body, **case
insensitively**. The fold matters: `bib: nLab` belongs before `bib: Riehl`, and
a raw byte comparison puts it after, because lowercase `n` sorts above uppercase
`R` in ASCII.

The usual objection to alphabetical order under a numeric style does not apply
here. The printed `[1]`, `[2]`, … are generated by LaTeX from position, and
every reference site is `\cite{bib: Surname}`, so inserting an entry mid-list
moves the numbers and changes **no** `\cite` site and no line of prose. The
insertion point is then determined rather than a judgement, which is the same
reason `docs/naming-convention.md` notes that nothing in this repo lists
anything in any order but alphabetical.

Order of first citation is the classical alternative and is rejected for the
opposite reason: it is an order you maintain by hand, it shifts whenever a
paragraph cites something new, and getting it wrong produces no error.

## The file

```tex
% SPDX-License-Identifier: CC-BY-NC-ND-4.0
% !TEX root = main.tex

\phantomsection
\addcontentsline{toc}{section}{参考文献}
\begin{thebibliography}{9}

\bibitem{bib: Rosenberg}
...

\end{thebibliography}
```

Line 1 is the licence header, and it is not optional: the root `LICENSE` is the
MIT text, so an unmarked file reads as MIT while the notes it belongs to are
CC BY-NC-ND. `.claude/hooks/guard-edits.sh` names `tex/*/bibliography.tex`
explicitly and blocks a write without it. Line 2 pins the root file for LaTeX
Workshop, as every chapter does.

`\phantomsection` before `\addcontentsline` is what makes the table-of-contents
entry point at the bibliography rather than at whatever preceded it; `hyperref`
needs the anchor to exist before the line is written.

**The `9` is the widest label, not a capacity.** It sets the indentation the
numbers are typeset into, so a list that reaches ten entries needs `{99}` or the
labels misalign. Nothing errors when it is wrong — the page simply looks off,
which is why it is checked rather than left to the eye.

## What is checked

```bash
python scripts/check_bibliography.py          # every topic
python scripts/check_bibliography.py <topic>  # one
```

It runs wherever the `scripts/` tests already run — `/git`'s gate and
`update-readme.yml` — via `scripts/test_check_bibliography.py`, and `/bib` runs
it directly after writing.

It reads structure, and only structure:

- line 1 of the file is the CC BY-NC-ND SPDX header
- every key matches `bib: ` followed by a non-empty body with no spaces
- every entry is exactly three lines
- lines 1 and 2 end in a comma, line 3 in a full stop
- line 2 opens with one of `\textit{`, ` `` `, `『`, `「` — which is what catches
  a straight `"` finding its way back in
- entries are in case-insensitive alphabetical order by key body
- `thebibliography`'s argument is wide enough for the number of entries

**What it cannot check is most of what matters.** Whether the year is right,
whether the publisher is right, whether the thing you called a book is a book,
whether the author's initial is the one they publish under — none of that is
visible to a script, and an entry that is wrong in every one of those ways
passes cleanly. A citation is a factual claim about a physical object, and the
checker's guarantee stops at the shape of the sentence making it.

That is also why `/bib` has no `WebSearch` and no `WebFetch`: the facts come
from you.
