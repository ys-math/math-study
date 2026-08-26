#!/bin/bash
# PostToolUse(Write|Edit) — the two repo rules that are stated but unenforced.
set -uo pipefail

block() { jq -n --arg r "$1" '{decision: "block", reason: $r}'; exit 0; }

input=$(cat)
path=$(jq -r '.tool_input.file_path // empty' <<<"$input")
[ -n "$path" ] && [ -f "$path" ] || exit 0
cwd=$(jq -r '.cwd // empty' <<<"$input")
rel="${path#"$cwd"/}"

# 1. Chapter files need the CC BY-NC-ND header on line 1. new_topic.py stamps
#    ch01.tex; ch02.tex onward is hand-made, and no CI step checks the header.
#    A topic's bibliography.tex is the notes too — same licence, same hole, and
#    nothing generates it at all — but it sits outside the ch*.tex pattern, so
#    it has to be named here. See docs/naming-convention.md, ## Inside a topic.
if [[ $rel == tex/*/ch*.tex || $rel == tex/*/bibliography.tex ]]; then
  if ! head -n 1 "$path" | grep -q 'SPDX-License-Identifier: CC-BY-NC-ND-4.0'; then
    block "$rel is missing its licence header. The root LICENSE is the MIT one, so an unmarked file reads as MIT by default. Add as line 1:

% SPDX-License-Identifier: CC-BY-NC-ND-4.0

See CLAUDE.md, ## Licensing."
  fi
fi

# 2. Lean files need the Apache header. Same hole as the chapters above and the
#    same reason it has to be a hook: lean/Math/** commits straight to main, so
#    no pull request ever reads one, and the root LICENSE is the MIT one. The
#    header is Mathlib's, except that it names LICENSE-APACHE-2.0 — this repo's
#    LICENSE is not the Apache text, so Mathlib's wording would misdirect.
#    .lake/ is excluded: it holds Mathlib's own sources, which carry their own.
if [[ $rel == lean/*.lean && $rel != lean/.lake/* ]]; then
  if ! head -n 5 "$path" | grep -q 'Released under Apache 2.0 license'; then
    block "$rel is missing its licence header. The root LICENSE is the MIT one, so an unmarked Lean file reads as MIT by default while everything it imports is Apache 2.0. Add as lines 1-5:

/-
Copyright (c) <year> @ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: @ys-math
-/

See docs/lean-convention.md."
  fi
fi

# 3. Claude may write a statement into lean/Math/Study/, never a proof. The rule
#    is in CLAUDE.md and docs/lean-convention.md; this is the half of it a hook
#    can hold, and the owner is learning Lean, so it is the half that matters.
#
#    The test is syntactic and deliberately narrow: every `by` must be followed
#    by `sorry`. Term-mode definitions keep working, which /formalize needs when
#    a notion has no Mathlib counterpart, and a term-mode *proof* slips through —
#    accepted, because tightening it would refuse ordinary `def`s and a hook
#    people work around is worse than one that catches the realistic case.
#
#    Only the text this call wrote is examined — .content for Write, .new_string
#    for Edit — never the file on disk. That distinction is the whole design: the
#    owner's own proofs, already in the file, must never be what trips it. A
#    whole-file Write over those proofs is caught, and should be.
if [[ $rel == lean/Math/Study/*.lean ]]; then
  written=$(jq -r '.tool_input.content // .tool_input.new_string // empty' <<<"$input")
  if [ -n "$written" ] && ! printf '%s' "$written" | perl -0777 -ne '
        s{/-.*?-/}{}gs;      # block comments and docstrings, which discuss proofs
        s{--[^\n]*}{}g;      # line comments
        exit 1 if /\bby\b(?!\s*sorry\b)/;
        exit 0;'; then
    block "$rel: this command writes statements, not proofs — every tactic block must be exactly \`sorry\`.

Write the statement and stop:

  theorem foo (h : P) : Q := by sorry

The proof is the repo owner's; they are learning Lean, and a proof written here is the one part of that which cannot be undone. Naming the Mathlib lemma that would close the goal, or explaining what the elaborator is complaining about, is help — typing the tactic block is not.

See docs/lean-convention.md, ## What Claude may write here."
  fi
fi

# 4. Losing a README marker does not fail any build — the generator simply stops
#    finding its block and the README quietly freezes.
if [[ $rel == README.md ]]; then
  for m in "BEGIN PDF LINKS" "END PDF LINKS" "BEGIN TREE" "END TREE"; do
    n=$(grep -c -- "<!-- $m -->" "$path" || true)
    if [ "$n" -ne 1 ]; then
      block "README.md must contain exactly one <!-- $m --> marker; found $n. generate_pdf_links.py and generate_tree.py locate their blocks by these markers, and update-readme.yml will silently stop updating the README without them. See CLAUDE.md, ## Generated artifacts."
    fi
  done
fi
exit 0