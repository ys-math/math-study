# 数学勉強ノート
勉強した数学の内容をLaTeXを用いてまとめていきます。
LaTeXのソースは `tex/` にまとめ、トピックごとにディレクトリを分けています。

各トピックのPDFは以下から閲覧できます。

<!-- BEGIN PDF LINKS -->
* [代数的K理論](./pdf/algebraic_k_theory.pdf)
* [圏論](./pdf/category_theory.pdf)
* [微分幾何学](./pdf/differential_geometry.pdf)
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
│   └── git-strategy.md
├── scripts/
│   ├── generate_pdf_links.py
│   ├── generate_tree.py
│   ├── latex_unicode.py
│   ├── new_topic.py
│   ├── readme_block.py
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
└── README.md
```
<!-- END TREE -->

## Commands
Run everything from the repo root.

| Command | What it does |
| --- | --- |
| `python scripts/new_topic.py <topic> --title <title>` | Creates `tex/<topic>/` with a `main.tex` and an empty `ch01.tex`. `<topic>` is lowercase letters, digits and underscores; the title is the `\DocTitle`, which becomes the link label in the PDF list above |
| `cd tex/<topic> && latexmk -r ../../.latexmkrc main.tex` | Compiles the topic's PDF locally |
| `python -m unittest discover -s scripts -t scripts -p 'test_*.py'` | Tests for `scripts/`; run before committing anything there |
| `python scripts/generate_pdf_links.py`<br>`python scripts/generate_tree.py` | Rewrite the generated README blocks. CI normally does this, so you rarely need to |

Claude Code slash commands:

| Command | What it does |
| --- | --- |
| `/new-topic <topic> <title>` | Creates a topic by running `new_topic.py` above |
| `/delete-topic <topic>` | Deletes a topic — `tex/<topic>/`, `pdf/<topic>.pdf` and its local artifacts — then commits and pushes the removal. Renaming is still by hand |
| `/review-notes [topic ...]` | Reviews a topic's notes for mathematical correctness, typos and LaTeX health, writing `reviews/<topic>.md` (gitignored, overwritten on every run) |
| `/git [description]` | Syncs, commits and pushes per `docs/git-strategy.md` |
| `/git-merge [PR number]` | Re-runs a pull request's gates, then squash-merges it |

To add a chapter, create `ch02.tex` and add `\input{ch02.tex}` to that topic's
`main.tex` by hand; nothing does this automatically.

Once you push to `main`, CI takes over: `build-pdf.yml` commits
`pdf/<topic>.pdf`, and `update-readme.yml` regenerates the PDF list and the
directory tree above. Both are generated — edit the `.tex` sources, not the
lists.

## ライセンス
Shield: [![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License][cc-by-nc-nd].

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg