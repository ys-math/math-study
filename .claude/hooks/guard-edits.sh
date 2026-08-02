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
if [[ $rel == tex/*/ch*.tex ]]; then
  if ! head -n 1 "$path" | grep -q 'SPDX-License-Identifier: CC-BY-NC-ND-4.0'; then
    block "$rel is missing its licence header. The root LICENSE is the MIT one, so an unmarked chapter reads as MIT by default. Add as line 1:

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

# 3. Losing a README marker does not fail any build — the generator simply stops
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