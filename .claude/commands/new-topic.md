---
description: Create a new topic directory with main.tex and ch01.tex
argument-hint: "<topic_slug> <title>  (slug optional — I'll propose one)"
allowed-tools: Glob, Bash(python scripts/new_topic.py:*)
---

Create a new topic in this repo by running `scripts/new_topic.py`. Topics live
in `tex/`; the script creates `tex/<topic>/` and must be run from the repo root.

Arguments given: $ARGUMENTS

All output is English.

The script takes a directory name and the document title:

```bash
python scripts/new_topic.py <topic> --title <title>
```

The directory name must match `^[a-z][a-z0-9_]*$` — it is interpolated into a
regex in `.github/workflows/build-pdf.yml`, a filename in `pdf/`, and the
`\TexRepo` URL, so the script rejects anything else.

How to handle the arguments:

- **Both a slug and a title were given** (e.g. `sheaf_theory 層論`) — run the
  script directly, no confirmation needed.
- **Only a title was given** (e.g. `層論`) — propose a slug and **wait for the
  user to confirm or correct it** before running anything. See below.
- **No arguments** — ask for the title.

## Proposing a slug

Glob `tex/*/main.tex` first, every run. The directory names it returns are the
style guide, and they are the only copy — a list quoted in this file would be
stale the moment a topic is added, and would steer the proposal wrong for as
long as it stayed that way.

Take the standard English name for that field of mathematics, in `snake_case`,
and match the granularity of what is already there. Some topics are a single
word, others are compounds; neither is the house style on its own. The shortest
name that is not ambiguous against the existing set is.

The directory name is permanent — it appears in the README, the PDF path and the
`\TexRepo` URL — so never pick it silently. Show the exact command, and the set
you picked it against:

```
sheaf_theory — 層論

  python scripts/new_topic.py sheaf_theory --title 層論

  existing: <every directory the Glob returned, comma-separated>

Proceed?
```

The list is there so the user can see the name in context — that is where a
wrong granularity becomes obvious. Do not offer alternatives unless the call was
genuinely close; if it was, name the runner-up on one line and say why you did
not take it.

After running, report the script's output verbatim, in particular the rendered
README label, and let the user check that it reads correctly. Do not stage,
commit, or regenerate the README: `.github/workflows/update-readme.yml` does
that on the next push.

If the script exits with an error, relay it and stop — the errors are actionable
(an invalid name, an already-taken name, or a `\DocTitle` that
`scripts/latex_unicode.py` cannot render).
