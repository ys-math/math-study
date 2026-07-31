# Label convention

Every numbered environment in `tex/*/ch0N.tex` — `definition`, `proposition`,
`lemma`, `theorem`, `corollary`, `remark`, `example` — can carry a `\label{}`,
and `\cref{}` is how the notes point back at it. This document fixes what goes
inside the braces.

The day-to-day version is the `/label` command, which implements this document;
read on when you are naming a label by hand, or when you want the reasoning.

Two facts drive the whole thing:

- **A label is read out of context.** You type `\cref{` in `ch03.tex` and pick
  from a list of strings. Nothing in that list tells you what kind of thing you
  are citing, or which chapter it came from, unless the string itself does.
- **A label is expensive to change.** Renaming one means rewriting every
  `\cref` site in the same edit or the build silently prints `??`. So the
  convention has to be one you can still apply on the fortieth label.

The naming follows Lean 4 / mathlib, adapted. Not out of deference — the two
libraries share a problem, which is naming a large pile of statements about a
handful of objects without collapsing into `thm1`, `thm2`, `thm3`.

## The shape

```
<abbr>: <body>
```

Abbreviation, colon, **one space**, body.

| environment   | prefix  |
| ------------- | ------- |
| `definition`  | `def: ` |
| `proposition` | `prop: `|
| `lemma`       | `lem: ` |
| `theorem`     | `thm: ` |
| `corollary`   | `cor: ` |
| `remark`      | `rem: ` |
| `example`     | `ex: `  |

The prefix is the one thing mathlib would not write — it carries the kind in
casing and namespace instead. It is here because `\cref` prints the *Japanese*
name from `\crefname` (定義, 命題, …), so the label string is the only place the
kind survives on the authoring side, where you are picking from a list.

`ex` covers `example`. If exercises ever appear they need a different
abbreviation, not a reassignment of this one.

The label goes on the `\begin` line, one space after it:

```tex
\begin{definition} \label{def: IsProjective}
```

## The body — definitions

Casing says what the definition *produces*, exactly as in mathlib:

| the definition introduces          | casing            | example                |
| ---------------------------------- | ----------------- | ---------------------- |
| a type or structure                | `UpperCamelCase`  | `def: ChainComplex`    |
| a property something can have      | `Is` + UpperCamel | `def: IsProjective`    |
| data — a construction, an invariant| `lowerCamelCase`  | `def: grothendieckGroup` |

The split between the first two rows is worth stating plainly, because it is
the judgement the convention most often gets wrong: a **structure** is a thing
you can hand someone (a chain complex, a topology, a sheaf), a **property** is
something a thing you already have either satisfies or does not (projective,
compact, exact).

`Is` is used on every property, namespaced or not — `def: IsProjective`,
`def: Module.IsProjective`. Mathlib drops it under a namespace, on the grounds
that `Module.Projective` already reads as "a module is projective". That
coupling is not worth importing: it would mean that adding a namespace later,
to disambiguate, forces a second change to the same string. Here the namespace
decision and the name are independent.

## The body — statements

`proposition`, `lemma`, `theorem`, `corollary`. All `snake_case`.

**An established name wins.** Where mathematicians already index the result by
a name, that name is the label, keeping its `_lemma` or `_theorem` word:

```
lem: splitting_lemma
lem: free_presentation_lemma
thm: yoneda_lemma
```

Yes, `lem: splitting_lemma` says "lemma" twice. The alternative, `lem:
splitting`, is not a thing anyone says, and four characters is not worth a
label you have to translate back on sight. When the environment and the name
disagree — Yoneda's lemma stated as a `theorem` — the body keeps the name
mathematicians use and the prefix reflects the environment actually written.

**Otherwise the name is built from the statement**, with mathlib's connectives:

| the statement is                | connective | example                            |
| ------------------------------- | ---------- | ---------------------------------- |
| an implication                  | `_of_`     | `prop: split_of_projective`        |
| an equivalence                  | `_iff_`    | `prop: projective_iff_free_summand`|
| three or more equivalent forms  | `_tfae`    | `prop: projective_tfae`            |

`_of_` puts the **conclusion first** and the hypothesis after, so
`split_of_projective` is "splits, given projective". It reads backwards for
about a week.

`_tfae` — "the following are equivalent" — is the one that earns its keep here.
The notes state results as 次の(1)-(4)は同値 constantly, and `projective_tfae`
says both what the statement is about and what shape it has, which a prose
description like `characterization_of_projective_modules` does not.

## The body — remarks and examples

Neither is a Lean declaration, so neither casing nor the connectives apply.
Plain `snake_case` describing the subject:

```
ex: free_module_is_projective
rem: projective_not_free
```

## Namespaces

Dotted, mathlib-style — `def: Module.IsProjective` — but **only where the bare
name would be ambiguous within the topic**. Default to bare.

One topic is one document, so the disambiguation pressure mathlib faces mostly
is not here. It is not zero: a `category_theory` chapter covering functors,
natural transformations and adjunctions at once will want `def: Functor.Faithful`
rather than `def: Faithful`. Reach for the namespace at that point, not before.

This does leave the corpus visibly mixed, some labels dotted and some bare. That
is the intended state, not drift.

## Name the subject, never the position

```
def: IsProjective        ✓
def: definition_1_2      ✗
```

Numbering moves the moment a section is inserted above. This is the one rule
with no exceptions.

## What this does not cover

**Sections and equations are out of scope.** No `\section` in the repo carries a
label, and display math is written `\[ ... \]`, which is unnumbered — there is
nothing to reference.

Section labels are a reasonable thing to want, since one `\section` is one
chapter here and nothing in `ch03.tex` can currently point at `ch02.tex`. They
are blocked on a decision this document will not make for you: `\cref` of a
section prints English unless `tex/preamble.tex` gains a
`\crefname{section}{節}{節}`, which is a shared-file change — a branch, a PR and
a full CI rebuild of every topic — and it has to commit to 節 or 章. Do that as
its own change, and `/label` picks up sections afterwards.

Equations would mean converting `\[ ... \]` to `equation` environments, which
changes how the mathematics renders. That is an authoring decision, never a
side effect of naming labels.

## Renaming

A rename is a rename **plus** every `\cref{}` site, in the same edit. Miss one
and the PDF prints `??` while the error stays buried in `main.log`. Check with

```bash
grep -rn 'cref{<old label>}' tex/<topic>/
```

before and after, and compile the topic afterwards:

```bash
latexmk -cd -r .latexmkrc tex/<topic>/main.tex
```

**A label that already follows this document is never renamed for taste.** The
rules above are mechanically checkable, and that is the property that makes a
proposed rename something you can approve at a glance. A well-formed label you
chose deliberately stands, whatever a later reader thinks of it.
