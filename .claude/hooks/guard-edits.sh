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
#    ch01.tex; ch02.tex onward is hand-made, and validate.yml never sees
#    tex/<topic>/** because it only runs on pull requests.
if [[ $rel == tex/*/ch*.tex ]]; then
  if ! head -n 1 "$path" | grep -q 'SPDX-License-Identifier: CC-BY-NC-ND-4.0'; then
    block "$rel is missing its licence header. The root LICENSE is the MIT one, so an unmarked chapter reads as MIT by default. Add as line 1:

% SPDX-License-Identifier: CC-BY-NC-ND-4.0

See CLAUDE.md, ## Licensing."
  fi
fi

# 2. Losing a README marker does not fail any build — the generator simply stops
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