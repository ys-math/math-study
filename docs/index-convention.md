# Index convention

Every topic's PDF carries a 索引, and every entry in it comes from one mark in
the prose. This document fixes **which mark**, **what a reading looks like**,
and **what goes in the index at all**.

There is no `/index` command. Unlike a `\label{}` or a `\bibitem{}`, a term is
written in the same keystroke as the definition that introduces it, so this
document is read by whoever is writing the chapter — which is the repo owner.

**Where the index is built is not here.** `tex/preamble.tex` defines the three
macros, `tex/index.ist` is the upmendex style file, and `.latexmkrc` names the
program; each carries its reasoning as a comment. `docs/git-strategy.md` decides
which of them takes a branch, and all of them do.

## Where it sits

`main.tex` carries one bare `\printindex`, after the last chapter and **before**
`bibliography.tex` where the topic has one:

```tex
\input{ch07.tex}

\printindex

\newpage
\input{bibliography.tex}

\newpage
\input{../colophon.tex}
```

It is the one line there with no `\newpage` in front of it, and that is not an
omission: the page break lives in `tex/index.ist`'s `preamble`, along with the
table-of-contents line, so that both appear only when the topic actually has an
index. A `\newpage` here would give a topic with no terms a blank page.

## The three macros

```tex
\term{けん}{圏}{category}          →  \textbf{圏}(category)
\termja{たいしょう}{対象}           →  \textbf{対象}
\termen{Nakayama's lemma}          →  \textbf{Nakayama's lemma}
```

Each typesets exactly the bytes the `\textbf` it replaced did, and additionally
files its term. Nothing about the printed page changed when the notes were
converted; the 索引 appeared and that was all.

**Which one:**

| the notes give the term | macro |
| --- | --- |
| a Japanese name and an English gloss | `\term` |
| a Japanese name only | `\termja` |
| a name in Latin script only | `\termen` |

`\term` with an empty third argument is not the way to write the second row.
The distinction is the point: `\termja{たいしょう}{対象}` says the notes have no
English for this term, and `\term{たいしょう}{対象}{}` would be indistinguishable
from a gloss someone meant to fill in.

**Bold in a chapter is always one of these three.** `\textbf` does not appear in
`tex/*/ch0N.tex` at all, and `scripts/test_index_markup.py` fails if it does.
The rule is worth its strictness: a term written `\textbf{…}` out of habit
typesets identically and is silently absent from the index, which is the one
error the finished PDF does not show you. Bold *as emphasis* is not available in
a chapter — if a passage ever needs it, it needs a macro of its own and a line
in this section, not a bare `\textbf`.

Elsewhere `\textbf` is ordinary: `tex/*/bibliography.tex` sets a journal volume
in bold, and the index's own headings are bold by way of `tex/index.ist`.

## The reading

The first argument of `\term` and `\termja` is the term's reading, in
**hiragana**. It is what upmendex sorts on, and it is mandatory.

It is mandatory because of the shape of its absence. upmendex sorts a kanji
headword carrying no reading by code point and files it in a clump at the end
of the index — no warning in the `.ilg`, no message in the log, nothing to find
except a term that is not where a reader looks for it. As a required argument
it is instead an error on the line being written.

- **Hiragana, not katakana.** Both sort identically; one is a convention so
  that the readings read as one column, and it is the one the headings are
  printed in (`letter_head 2` in `tex/index.ist`). `ー` is allowed —
  `べくとるくうかん` needs none, but a term built on a katakana loan may.
- **A term carrying mathematics is read as it is spoken.**
  `$\lambda$項` is `らむだこう`, `$C^{\infty}$級多様体` is `しーむげんきゅうたようたい`.
  The reading is the sound, so the mathematics in the headword is simply read
  aloud; nothing about `$` reaches the sort key.
- **The reading is checked for script, never for correctness.**
  `scripts/test_index_markup.py` can tell hiragana from kanji. It cannot tell
  `けん` from `きり`, and nothing else can either — a wrong reading produces a
  well-formed index, correctly sorted on the wrong sound.

Where a term has two readings in currency, use the one you would say when
reading the sentence aloud, and do not record the other: a second entry for the
same page is noise, and `\index`'s cross-reference machinery is deliberately
unused here (see `## What is not here`).

## The English sort key

`\term` takes one optional argument, before the reading:

```tex
\term[lambda-term]{らむだこう}{$\lambda$項}{$\lambda$-term}
```

It is the sort key for the **欧文** entry, and it is needed exactly when the
English gloss carries mathematics — upmendex would otherwise sort
`$\lambda$-term` under `$`. Write the gloss as it is spelled out, in ASCII:
`lambda-term`, `T-algebra`, `R-module`.

A gloss in plain Latin script never needs it. Adding one anyway is not an
error, but it is a second place for the same word to be typed, and they drift.

## What is in the index

**Every term the notes define, and nothing else.** In practice that is every
term the notes set in bold, which is the same set — see the first section.

Named theorems are in: 米田の補題, Nakayama's lemma and Morita invariance are
bold in the notes for the same reason a term is, and they are exactly what a
reader looks up by name. They take the same macros and sit in the same list.

**A synonym is its own entry.** 小さい圏 and 小圏 are two names for one notion
and get one `\term` and one `\termja` respectively, landing two entries on the
same page. This is deliberately not a cross-reference: a `see` entry sends a
reader to a second place in the index to be told a page number the first place
could have printed, and with the two names a line apart in the notes there is
nothing to send them to.

**An entry is a definition site, so it carries one page.** Nothing indexes a
term where it is merely used. That is why the locator needs no convention for
distinguishing a definition from a mention — bold-for-definition, the usual
one, would mark every entry in the list.

## What is not here

Each of these was considered while the index was designed and left out. They
are recorded so that adding one later is a decision, not a discovery.

- **No sub-entries.** `\index`'s `!` levels are unused; every entry is flat.
  The notes are small enough that a two-level index would have one entry under
  most heads.
- **No cross-references.** No `see`, no `see also`. See the synonym rule above.
- **No page ranges.** A term is defined in one place, so `upmendex -r` would
  have nothing to collapse.
- **No 定義番号 locators.** An entry could read 定義 1.1 rather than a page —
  more precise, stable under repagination, and buildable by capturing
  cleveref's `\cref@currentlabel` inside the macro. It was declined because the
  locator is a hyperlink either way, and the machinery would live in
  `tex/preamble.tex`, whose blast radius is every topic.
- **No second index.** 和文 and 欧文 entries share one list, one `\printindex`
  and one `.idx`, separated by where the kana headings stop and the Latin ones
  begin. Two real indexes would need two index streams and custom dependencies
  in `.latexmkrc` to build them.
