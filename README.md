# 数学勉強ノート
勉強した数学の内容をLaTeXを用いてまとめていきます。
LaTeXのソースは `tex/` にまとめ、トピックごとにディレクトリを分けています。

各トピックのPDFは以下から閲覧できます。

<!-- BEGIN PDF LINKS -->
* [代数的K理論](./pdf/algebraic_k_theory.pdf)
* [圏論](./pdf/category_theory.pdf)
* [微分幾何学](./pdf/differential_geometry.pdf)
* [ガロア理論](./pdf/galois_theory.pdf)
* [λ計算](./pdf/lambda_calculus.pdf)
* [多様体論](./pdf/manifold.pdf)
* [シンプレクティック多様体](./pdf/symplectic_manifold.pdf)
* [位相幾何学](./pdf/topology.pdf)
<!-- END PDF LINKS -->

## ディレクトリ構造
<!-- BEGIN TREE -->
```
math-study/
├── docs/
│   ├── agent-system.md
│   ├── git-strategy.md
│   ├── issue-convention.md
│   └── label-convention.md
├── scripts/
│   ├── generate_pdf_links.py
│   ├── generate_tree.py
│   ├── latex_unicode.py
│   ├── new_topic.py
│   ├── readme_block.py
│   ├── test_agent_docs.py
│   ├── test_latex_unicode.py
│   └── test_new_topic.py
├── tex/
│   ├── algebraic_k_theory/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── category_theory/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── differential_geometry/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── galois_theory/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── lambda_calculus/
│   │   ├── ch01.tex
│   │   ├── ch02.tex
│   │   ├── ch03.tex
│   │   └── main.tex
│   ├── manifold/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── symplectic_manifold/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── topology/
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── colophon.tex
│   └── preamble.tex
├── CLAUDE.md
├── LICENSE
├── LICENSE-CC-BY-NC-ND-4.0
└── README.md
```
<!-- END TREE -->

## Commands
Run everything from the repo root.

| Command | What it does |
| --- | --- |
| `python scripts/new_topic.py <topic> --title <title>` | Creates `tex/<topic>/` with a `main.tex` and a `ch01.tex` holding just its CC BY-NC-ND SPDX header. `<topic>` is lowercase letters, digits and underscores; the title is the `\DocTitle`, which becomes the link label in the PDF list above |
| `latexmk -cd -g tex/<topic>/main.tex` | Compiles the topic's PDF locally. `-cd` enters the topic directory so `\input{../preamble.tex}` resolves; `-g` forces a rebuild past latexmk's cache. See `docs/git-strategy.md`, `## Gates` |
| `python -m unittest discover -s scripts -t scripts -p 'test_*.py'` | Tests for `scripts/`; run before committing anything there |
| `python scripts/generate_pdf_links.py`<br>`python scripts/generate_tree.py` | Rewrite the generated README blocks. CI normally does this, so you rarely need to |

Claude Code slash commands:

| Command | What it does |
| --- | --- |
| `/new-topic <topic> <title>` | Creates a topic by running `new_topic.py` above |
| `/delete-topic <topic>` | Deletes a topic — `tex/<topic>/`, `pdf/<topic>.pdf`, its open review issues and its local artifacts — then commits and pushes the removal. Renaming is still by hand |
| `/label [topic ...]` | Proposes `\label{}` names for a topic's theorem environments per `docs/label-convention.md`, and applies the ones you pick |
| `/review-notes [topic ...]` | Reviews a topic's notes for mathematical correctness, typos and LaTeX health, then files the findings you pick as GitHub issues per `docs/issue-convention.md`. Skips what an open issue already covers; closes nothing |
| `/issues [topic ...]` | Renders a topic's open review issues as `issues/<topic>.md` (gitignored, overwritten on every run) with links that open your working copy at the line |
| `/audit [file ...]` | The same, for the machinery rather than the mathematics: checks the commands, instructions and hooks for contradictions, stale claims and dead steps, writing `.claude/audits/audit.md` (gitignored, overwritten on every run). Then applies the fixes you name — and only those, leaving the commit to `/git` |
| `/git [description]` | Syncs, commits and pushes per `docs/git-strategy.md` |
| `/git-merge [PR number]` | Re-runs a pull request's gates, then squash-merges it |
| `/watch-ci [sha]` | Reports the CI runs for a commit and stops. Built to run under `/loop` |

`docs/agent-system.md` maps the whole setup — these commands, the instruction
files, the hooks that enforce the repo's rules, and how the CI cascade
terminates.

To add a chapter, create `ch02.tex` and add `\input{ch02.tex}` to that topic's
`main.tex` by hand; nothing does this automatically. Copy the
`% SPDX-License-Identifier: CC-BY-NC-ND-4.0` line from `ch01.tex` while you are
there — only the generated `ch01.tex` gets it for free.

Once you push to `main`, CI takes over: `build-pdf.yml` commits
`pdf/<topic>.pdf`, and `update-readme.yml` regenerates the PDF list and the
directory tree above. Both are generated — edit the `.tex` sources, not the
lists.

## ライセンス
[![MIT][mit-shield]][mit] [![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

This repository is dual-licensed. The table below is authoritative: it matches
on paths, so a file is covered whether or not it carries an SPDX header.

| Path | License |
| --- | --- |
| `tex/*/ch*.tex`, `pdf/*.pdf` | [CC BY-NC-ND 4.0][cc-by-nc-nd] |
| everything else | [MIT][mit] |

The mathematics — the chapter sources and the PDFs built from them — is
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International][cc-by-nc-nd].
Everything that builds it is MIT: `scripts/`, `.github/`, `.latexmkrc`, and the
shared `tex/preamble.tex`, `tex/colophon.tex` and every `tex/*/main.tex`, which
`new_topic.py` generates. Reuse the build system freely.

Full texts: [`LICENSE`](./LICENSE) (MIT) and
[`LICENSE-CC-BY-NC-ND-4.0`](./LICENSE-CC-BY-NC-ND-4.0).

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[mit]: https://opensource.org/licenses/MIT
[mit-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg