# Bibliography convention

A topic's references live in `tex/<topic>/bibliography.tex`, as `\bibitem`s
inside a `thebibliography` environment. This document fixes two things: **the
citation key**, and **the shape of an entry**.

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

## The shape of an entry

Fields run in fixed order, **one group per line**, so that a diff shows which
part of a reference changed rather than reflowing the whole entry.

`\textit{}` marks **the published container** — the thing you would look up in a
catalogue. For a book that is the book; for an article it is the journal, never
the article's own title. That single rule is what keeps the shapes below
consistent with each other.

### A book

```tex
\bibitem{bib: Rosenberg}
J. Rosenberg,
\textit{Algebraic $K$-Theory and Its Applications},
Graduate Texts in Mathematics 147, Springer-Verlag, New York, 1994.
```

Initial and surname; italic title; then series and number, publisher, place,
year — on one line, ending in a full stop. Given names are initials, not spelled
out.

### A journal article

```tex
\bibitem{bib: Milnor}
J. Milnor,
"On manifolds homeomorphic to the 7-sphere",
\textit{Annals of Mathematics} \textbf{64} (1956), 399--405.
```

The article title is upright and quoted; without the quotes it runs into the
journal name with nothing to separate them. Volume bold, year parenthesised,
page range with an en-dash (`--`).

### An arXiv preprint

```tex
\bibitem{bib: Leinster}
T. Leinster,
"Basic Category Theory",
preprint, arXiv:1612.09375 [math.CT], 2025.
```

Title upright and quoted, exactly as an article's is, and **no `\textit{}`
anywhere**. The italic marks a published container and a preprint has none, so
italicising the title would claim a container that does not exist.

The arXiv identifier stands where the journal, volume and pages stand, because
it is what you look the thing up by: `arXiv:`, the number, the primary class in
brackets, then the year of the version cited.

**No `\url{}`.** `arXiv:1612.09375` already resolves, and a URL beside it
duplicates the identifier while adding an element neither shape above has. The
`url` field of a pasted BibTeX entry is dropped, not transcribed.

**A preprint since published takes the published shape instead**, with its
publisher or journal and that year. The shape follows the object you mean to
cite, not the file you happened to paste.

### Japanese-language works

Japanese takes the Japanese shape. 『』 marks the container and 「」 the article,
exactly where `\textit{}` and quotes go above:

```tex
\bibitem{bib: 松本}
松本幸夫,
『多様体の基礎』,
東京大学出版会, 1988.
```

The key body is the surname in Japanese, matching the author as printed.

**Do not wrap Japanese in `\textit{}`.** It is inert here: Japanese fonts have
no italic, so under `jlreq` with LuaLaTeX the CJK renders upright and the markup
carries nothing. The source looks correct and the emphasis is silently absent
from the PDF — which is why 『』 has to do the work rather than sit inside an
italic that does nothing.

**Do not romanise.** The notes are in Japanese, and a transliterated title
cannot be looked up in a Japanese catalogue or ordered from a Japanese
bookshop — it optimises for a reader who is not here.

### Anything else

Book, article and preprint are the three shapes fixed above. A web resource, a
chapter in a collected volume, a lecture-note set — none has a shape yet, on
purpose: there is no entry of any of those kinds in the repo, and inventing one
now would be guessing at a format before there is anything to format.

The rule for meeting one is therefore explicit, because the failure mode
otherwise is silent: **propose a shape, get it approved, and write it into this
document in the same change.** Not doing so means the next preprint gets a
different shape from the first, and nothing anywhere reports the divergence.

## The order of entries

**Alphabetical by surname** — which is to say, by the key body.

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
which is why it is written down here rather than left to the eye.
