# The agent system

A map of everything in this repo that tells Claude what to do, or stops it doing
something. It exists because that machinery is spread across seven directories
and nothing else shows it in one place.

**This file is a map, not a specification.** It says who owns each rule and where
to change it; it does not restate the rules. Anything written here twice would
drift, which is the failure this repo has already been bitten by — see
`## Where to change things` at the bottom before adding to any of it.

## The four layers

Each layer answers a different question, and they stack rather than compete.

| Layer | Question it answers | Lives in | Binding? |
| --- | --- | --- | --- |
| **Instructions** | What should Claude do, and why? | `CLAUDE.md`, `docs/*.md` | advisory |
| **Commands** | How is this specific job done, step by step? | `.claude/commands/*.md` | advisory, but capability-scoped |
| **Enforcement** | What holds even if Claude ignores the above? | `.claude/settings.json`, `.claude/hooks/` | mechanical |
| **Automation** | What happens with nobody watching? | `.github/workflows/`, `/watch-ci` | mechanical, unattended |

Advisory layers explain; mechanical layers enforce. A rule that matters usually
wants both — `git add -A` is explained in `docs/git-strategy.md`, restated as a
prohibition in `/git`, and made impossible by `.claude/hooks/guard-bash.sh`. The
hook is what stops it; the explanation is what stops Claude looking for a way
around the hook.

## Instructions — who owns what

Loaded on **every** session, so it holds only what cannot be found at the moment
it is needed:

- **`CLAUDE.md`** — the licence boundary, the coupling rules, the generated
  artifacts, and the rule that the mathematics is not Claude's to write. Its own
  preamble states its admission policy; honour it.

Loaded **on demand**, by a command that names them:

- **`docs/git-strategy.md`** — branching, commit format, attribution, gates, and
  the canonical `latexmk` invocation. `/git` and `/git-merge` execute it.
- **`docs/label-convention.md`** — `\label{}` naming. `/label` executes it, and
  it binds any label written by hand too.
- **`docs/issue-convention.md`** — what a review finding looks like as a GitHub
  issue: labels, title, body, deduplication, closing. `/review-notes` files
  them, `/git` closes them, `/delete-topic` cleans them up and `/issues` renders
  them locally — four commands, one specification.
- **`docs/agent-system.md`** — this file.

## Commands

They live in `.claude/commands/`. Each one's `description:` and
`argument-hint:` frontmatter is authoritative for *what it does*; the table
below carries only what the frontmatter cannot tell you — **what it is allowed
to touch**, which is what you actually need when choosing between them.

| Command | Writes | Commits | Stops for confirmation | Output |
| --- | --- | --- | --- | --- |
| `/new-topic` | `tex/<topic>/` via the script | no | when proposing a slug | English |
| `/label` | `tex/**` | no | always, before applying | English |
| `/review-notes` | GitHub issues | no | always, before filing | **Japanese findings, English structure** |
| `/issues` | `issues/**` only | no | no | **Japanese findings, English structure** |
| `/audit` | `.claude/audits/**`, then the files it audits | no | always, before applying a fix | English |
| `/git` | index, commits | yes, pushes | always, before any commit | English |
| `/git-merge` | squash-merges a PR | yes | always | English |
| `/delete-topic` | deletes a topic, closes its issues | **yes, itself** | always | English |
| `/watch-ci` | nothing | no | no | English |

Worth knowing without looking them up:

- **`/delete-topic` commits and pushes on its own**, and is now the one command
  that also *closes* issues. Every other command leaves the working tree
  for `/git`.
- **`/review-notes` never edits `tex/`** — it has no write tool at all, which is
  a stronger boundary than the `Write(reviews/**)` it used to be locked to. It
  files findings as GitHub issues and cannot close one: `gh issue close` is
  absent from its `allowed-tools`, so an undetected finding is reported to the
  user rather than acted on.
- **`/issues` writes the only local artifact left** — `issues/<topic>.md`,
  gitignored and overwritten, a view of the open issues with links that resolve
  in your working copy. GitHub is the record; regenerate rather than trust it.
- **`/audit` does edit what it audits**, in a second phase the user has to ask
  for by naming findings from the report. It is the one command whose
  `allowed-tools` reaches `.claude/`, `docs/`, `.github/` and `CLAUDE.md`, so it
  is the one that can break the machinery in this table. What holds is the
  gate, not the capability: it writes the report first, and applies only what
  the report argued for.

Each command's `allowed-tools` line is a real capability boundary, not
documentation. `/git-merge` cannot commit; `/delete-topic` cannot `rm`;
`/watch-ci` cannot write at all. When a command's prose says it "cannot" do
something, check that the frontmatter agrees — that is the half that holds.

## Enforcement

`.claude/settings.json` wires up two hooks and a permission list.

| Hook | Event | Refuses |
| --- | --- | --- |
| `guard-bash.sh` | `PreToolUse(Bash)` | `git add -A` / `git add .`; force-push including `--force-with-lease`; `git clean` with no pathspec, unless it is a dry run |
| `guard-edits.sh` | `PostToolUse(Write\|Edit)` | a `tex/*/ch*.tex` missing its SPDX header; a `README.md` with a generator marker destroyed |

Permissions additionally deny writes to `pdf/**` and allow about twenty
read-only commands through without a prompt.

Two properties to preserve if you touch these:

- **Hooks must be executable.** A non-executable hook fails at invocation, not at
  config load: the setup looks correct and silently does nothing. Both are
  committed mode `100755`.
- **Path-shaped rules belong in `permissions`, everything else in a hook.**
  Permission rules prefix-match, so no rule can catch
  `git push origin main --force`. That single limitation decided which rules went
  where.

### Keeping this map true

Every table in this file enumerates something on disk, and a stale enumeration
reads exactly like a correct one. `scripts/test_agent_docs.py` is what notices:
it holds the command tables here and in `README.md` to `.claude/commands/`, the
hook and workflow and `docs/` names to their directories, the hooks to being
registered and executable, and every count written in digits to what it counts.

It runs wherever the `scripts/` tests already run — `/git`'s gate and the
`update-readme.yml` step — rather than in a checker somebody has to remember to
invoke, which would have the failure mode it is guarding against. So a command
added without a table row fails before the commit exists; if one somehow lands,
the README bot stays red until it is fixed.

Two conventions keep it able to see, and both are load-bearing:

- **Counts go in digits, or go away.** "all 8 topics" is checked. "Seven, in
  `.claude/commands/`" was not, and was wrong within a week — as was "the six
  commands" in `CLAUDE.md`. Where a table already enumerates the things, do not
  also say how many.
- **Enumerations are tables**, keyed on the first column, so prose can name a
  command freely — `/loop` is discussed below and is not a command in this repo.

What no test can check is whether any of this is *true*, only whether the names
line up. `/audit` is the judgment half: it reads for contradictions between
files, claims the repo no longer satisfies, prose that disagrees with an
`allowed-tools` line, steps that cannot fire, procedures with no reachable exit,
and hooks that do not refuse what they claim to. It runs the tests first and
never re-derives what they decide.

It then repairs what you tell it to, which is why the tests are its gate on the
way out as well as in: a fix that renames a command, deletes a document or
changes a count in digits breaks one of the enumerations above, and the run that
made the change is the one that has to notice.

## Automation

Three workflows in `.github/workflows/`:

| Workflow | Trigger | Does |
| --- | --- | --- |
| `build-pdf.yml` | push to `main` touching `**.tex`, `.latexmkrc` | compiles affected topics, commits `pdf/*.pdf` |
| `update-readme.yml` | **every** push to `main` | runs the script tests, regenerates the README blocks, commits |
| `validate.yml` | `pull_request` | compiles all 8 topics, runs the script tests |

Measured run times live in `.claude/commands/watch-ci.md`, which is the only
thing that needs them — they set its polling interval, and they are re-observed
there rather than remembered here.

`validate.yml` runs only on pull requests, and `tex/<topic>/**` never goes
through one — which is why the licence header is enforced by a hook instead.

### Why the push cascade terminates

Both workflows push to `main`, so both could retrigger CI forever. They don't,
by two different mechanisms, and both are worth preserving:

- **`build-pdf.yml` writes what it does not watch.** It commits `pdf/*.pdf`,
  which matches neither of its path filters. It cannot trigger itself.
- **`update-readme.yml` converges.** It has no path filter, so it *does* trigger
  itself — but its output is a pure function of `git ls-files`, so the second run
  produces identical bytes, `git diff --cached --quiet` succeeds, and it commits
  nothing. The cascade dies at the fixed point.

Both also retry a rebase three times, because the fast workflow pushes while the
slow one is still in TeX Live.

`/watch-ci` reports the result and stops; it is built to run under `/loop` and
ends every run with a `watch-ci: done|pending|unknown` line for a loop to read.

## Where to change things

The routing question, in the order worth asking it:

1. **Does it need to hold even when Claude is not cooperating?** → a hook in
   `.claude/hooks/`, or a `permissions` rule if it is purely path-shaped.
2. **Is it one job with steps?** → a command in `.claude/commands/`.
3. **Is it a rule several commands share?** → `docs/`, named as the single copy,
   with each command pointing at it and *not* restating it.
4. **Would Claude go wrong without knowing it exists, in any session?** → and
   only then, `CLAUDE.md`.

Most things belong at 2 or 3. `CLAUDE.md` is the expensive tier — it is paid on
every session, including the ones it is irrelevant to.

Whatever you add, add it to the tables above in the same commit — see
`### Keeping this map true`. A map that is a commit behind is worse than no
map, because it is still believed.

When a fact ends up in more than one file, name one owner and make the others
point at it. This repo once carried three different spellings of the local
`latexmk` command across six files, and the authoritative one was wrong about
its own flags; nobody was careless, and nothing caught it, because no file
claimed to be the copy.
