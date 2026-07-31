#!/bin/bash
# PreToolUse(Bash) — refuse the git invocations docs/git-strategy.md forbids
# unconditionally.
#
# Why a hook and not a permission rule: permission rules prefix-match, and every
# one of these flags can appear at any position on the command line. There is no
# prefix that catches `git push origin main --force`.
#
# Input: the PreToolUse JSON on stdin. Output: a deny decision, or nothing.
set -uo pipefail

deny() {
  jq -n --arg r "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $r
    }
  }'
  exit 0
}

input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
[ -n "$cmd" ] || exit 0

# Split on shell separators and inspect each segment. A segment only counts if it
# *starts* with git, so `grep 'git add -A' notes.txt` is not treated as a match.
while IFS= read -r seg; do
  seg="${seg#"${seg%%[![:space:]]*}"}"
  [[ $seg == git\ * ]] || continue

  case "$seg" in
    "git add "*)
      if grep -qE '(^|[[:space:]])(-A|--all|\.)([[:space:]]|$)' <<<"${seg#git add}"; then
        deny "git add -A / git add . is forbidden in this repo: the working tree may hold another session's work in progress. Stage explicit paths instead — docs/git-strategy.md, ## Never."
      fi
      ;;
    "git push "*)
      if grep -qE '(^|[[:space:]])(-f|--force|--force-with-lease)([[:space:]=]|$)' <<<"$seg"; then
        deny "Force-pushing is forbidden in this repo, --force-with-lease included. A bad commit on main is corrected by a follow-up commit — docs/git-strategy.md, ## Never."
      fi
      ;;
    "git clean "*)
      rest=$(sed -E 's/^git[[:space:]]+clean//' <<<"$seg")
      paths=$(tr ' ' '\n' <<<"$rest" | grep -vE '^-|^$' || true)
      if [ -z "$paths" ]; then
        deny "git clean without an explicit pathspec would delete untracked files anywhere in the tree — including chapters that have never been committed. Name the paths, as .claude/commands/delete-topic.md does."
      fi
      ;;
  esac
done < <(printf '%s\n' "$cmd" | sed -E 's/(&&|\|\||[;|])/\n/g')

exit 0
