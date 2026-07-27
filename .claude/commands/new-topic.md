---
description: Create a new topic directory with main.tex and ch01.tex
argument-hint: <topic_slug> <タイトル>  (slug optional — I'll propose one)
allowed-tools: Bash(python scripts/new_topic.py:*)
---

Create a new topic in this repo by running `scripts/new_topic.py`. Topics live
in `tex/`; the script creates `tex/<topic>/` and must be run from the repo root.

Arguments given: $ARGUMENTS

The script takes a directory name and the document title:

```bash
python scripts/new_topic.py <topic> --title <タイトル>
```

The directory name must match `^[a-z][a-z0-9_]*$` — it is interpolated into a
regex in `.github/workflows/build-pdf.yml`, a filename in `pdf/`, and the
`\TexRepo` URL, so the script rejects anything else.

How to handle the arguments:

- **Both a slug and a title were given** (e.g. `sheaf_theory 層論`) — run the
  script directly, no confirmation needed.
- **Only a title was given** (e.g. `層論`) — propose a slug: the standard
  English name for that field of mathematics, in `snake_case`, consistent with
  the existing topic directories (`category_theory`, `algebraic_k_theory`,
  `differential_geometry`). Show the exact command you would run and **wait for
  the user to confirm or correct the slug** before running it. The directory
  name is permanent — it appears in the README, the PDF path and the `\TexRepo`
  URL — so never pick it silently.
- **No arguments** — ask for the title.

After running, report the script's output verbatim, in particular the rendered
README label, and let the user check that it reads correctly. Do not stage,
commit, or regenerate the README: `.github/workflows/update-readme.yml` does
that on the next push.

If the script exits with an error, relay it and stop — the errors are actionable
(an invalid name, an already-taken name, or a `\DocTitle` that
`scripts/latex_unicode.py` cannot render).
