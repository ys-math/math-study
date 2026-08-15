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
  # Squeeze runs of whitespace to one space. Every pattern below is written with
  # single spaces, so without this `git  clean -xdf` matches none of them and is
  # waved through.
  seg=$(tr -s '[:space:]' ' ' <<<"$seg")
  [[ $seg == git\ * ]] || continue

  case "$seg" in
    "git add "*)
      if grep -qE '(^|[[:space:]])(-[a-zA-Z]*A[a-zA-Z]*|--all|\.|:/)([[:space:]]|$)' <<<"${seg#git add}"; then
        deny "git add -A / git add . is forbidden in this repo: the working tree may hold another session's work in progress. Stage explicit paths instead — docs/git-strategy.md, ## Never."
      fi
      ;;
    "git push "*)
      if grep -qE '(^|[[:space:]])(-[a-zA-Z]*f[a-zA-Z]*|--force|--force-with-lease)([[:space:]=]|$)' <<<"$seg"; then
        deny "Force-pushing is forbidden in this repo, --force-with-lease included. A bad commit on main is corrected by a follow-up commit — docs/git-strategy.md, ## Never."
      fi
      ;;
    "git clean "*)
      # Two things a plain "does any token not start with -" test gets wrong:
      # -e takes a *separate* argument, which is not a pathspec however much it
      # looks like one, and -n only prints. Both were live defects — `git clean
      # -xdf -e main.pdf` was allowed, and `git clean -n` was refused.
      dry=0; paths=0; skip=0
      while IFS= read -r tok; do
        [ -n "$tok" ] || continue
        if [ "$skip" = 1 ]; then skip=0; continue; fi
        case "$tok" in
          -n|--dry-run) dry=1 ;;    # prints what it would remove; removes nothing
          -e|--exclude) skip=1 ;;   # its argument is a pattern, not a path
          --*)          ;;          # --exclude=<pattern> and every other long flag
          -*n*)         dry=1 ;;    # bundled short flags: -ndx
          -*)           ;;
          *)            paths=1 ;;
        esac
      done < <(tr ' ' '\n' <<<"${seg#git clean}")
      if [ "$dry" = 0 ] && [ "$paths" = 0 ]; then
        deny "git clean without an explicit pathspec would delete untracked files anywhere in the tree — including chapters that have never been committed. Name the paths, as .claude/commands/delete-topic.md does, or pass -n to preview."
      fi
      ;;
    "git restore "*)
      # `git restore .` and `git restore :/` discard every uncommitted change
      # in the tree — the same harm as `git clean` with no pathspec. /audit's
      # rollback step is the only place this repo runs restore at all.
      if grep -qE '(^|[[:space:]])(\.|:/)([[:space:]]|$)' <<<"${seg#git restore}"; then
        deny "git restore . / git restore :/ would discard every uncommitted change in the tree, including work another session has not committed. Name the paths you edited instead — .claude/commands/audit.md, ## If a check fails, roll back."
      fi
      ;;
  esac
done < <(printf '%s\n' "$cmd" | sed -E 's/(&&|\|\||[;|])/\n/g')

exit 0
