# Math Study Notes

English | [日本語](./README.ja.md)

## PDF

<!-- BEGIN PDF LINKS -->
* [代数的K理論](./pdf/algebraic_k_theory.pdf)
* [圏論](./pdf/category_theory.pdf)
* [可換環論](./pdf/commutative_ring_theory.pdf)
* [ホモロジー代数](./pdf/homological_algebra.pdf)
* [λ計算](./pdf/lambda_calculus.pdf)
<!-- END PDF LINKS -->

<!-- BEGIN TEXT METER -->
```
category_theory          █████████░░░░░░░░░░░   45.2%   65,996
homological_algebra      ██████▎░░░░░░░░░░░░░   31.4%   45,850
algebraic_k_theory       ██▍░░░░░░░░░░░░░░░░░   12.1%   17,748
lambda_calculus          █▍░░░░░░░░░░░░░░░░░░    7.0%   10,191
commutative_ring_theory  ▉░░░░░░░░░░░░░░░░░░░    4.3%    6,325
                                                       -------
total                                                  146,110
```
<!-- END TEXT METER -->

## Directory structure
<!-- BEGIN TREE -->
```
math-study/
├── docs/
│   ├── images/
│   │   ├── audit-workflow.svg
│   │   ├── routing-rule.svg
│   │   └── working-loop.svg
│   ├── agent-system.md
│   ├── audit-workflow.ebnf
│   ├── bib-convention.md
│   ├── git-strategy.md
│   ├── index-convention.md
│   ├── interactive-convention.md
│   ├── issue-convention.md
│   ├── label-convention.md
│   ├── naming-convention.md
│   ├── routing-rule.ebnf
│   └── working-loop.ebnf
├── scripts/
│   ├── check_bibliography.py
│   ├── generate_pdf_links.py
│   ├── generate_text_meter.py
│   ├── generate_tree.py
│   ├── latex_unicode.py
│   ├── new_topic.py
│   ├── quiver.py
│   ├── quiver_macros.py
│   ├── readme_block.py
│   ├── test_agent_docs.py
│   ├── test_assumes.py
│   ├── test_check_bibliography.py
│   ├── test_generate_text_meter.py
│   ├── test_generate_tree.py
│   ├── test_index_markup.py
│   ├── test_interactive.py
│   ├── test_latex_unicode.py
│   ├── test_new_topic.py
│   ├── test_quiver.py
│   ├── test_quiver_macros.py
│   └── test_readme_block.py
├── tex/
│   ├── algebraic_k_theory/
│   │   ├── bibliography.tex
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── category_theory/
│   │   ├── bibliography.tex
│   │   ├── ch01.tex
│   │   ├── ch02.tex
│   │   ├── ch03.tex
│   │   ├── ch04.tex
│   │   ├── ch05.tex
│   │   ├── ch06.tex
│   │   ├── ch07.tex
│   │   ├── ch08.tex
│   │   ├── ch09.tex
│   │   ├── ch10.tex
│   │   └── main.tex
│   ├── commutative_ring_theory/
│   │   ├── bibliography.tex
│   │   ├── ch01.tex
│   │   └── main.tex
│   ├── homological_algebra/
│   │   ├── html/
│   │   │   └── biproduct-sphere.html
│   │   ├── ch01.tex
│   │   ├── ch02.tex
│   │   ├── ch03.tex
│   │   ├── ch04.tex
│   │   ├── ch05.tex
│   │   ├── ch06.tex
│   │   ├── ch07.tex
│   │   ├── ch08.tex
│   │   ├── chA.tex
│   │   └── main.tex
│   ├── html-common/
│   │   ├── diagram.css
│   │   ├── diagram.js
│   │   └── latin-modern.css
│   ├── lambda_calculus/
│   │   ├── ch01.tex
│   │   ├── ch02.tex
│   │   ├── ch03.tex
│   │   └── main.tex
│   ├── colophon.tex
│   ├── index.ist
│   └── preamble.tex
├── CLAUDE.md
├── LICENSE
├── LICENSE-CC-BY-NC-ND-4.0
├── README.ja.md
└── README.md
```
<!-- END TREE -->

## AI usage

This repo is written with [Claude Code](https://claude.com/claude-code), and the
line between what it writes and what the author writes is drawn on purpose.

- **The mathematics is the author's.** The prose in `tex/*/ch*.tex` — every
  definition, theorem, proof and example in the PDFs — is written by the author.
  Claude does not write or rewrite it. `/review-notes` reads the notes and files
  what it finds as GitHub issues; which of those get fixed, and how, is the
  author's call.
- **The tooling is mostly Claude's.** `scripts/`, `.github/`, `docs/`,
  `.claude/`, both READMEs, and the shared `tex/preamble.tex`,
  `tex/colophon.tex` and `tex/index.ist` are largely written by Claude.
- **`git log` shows which is which, at commit granularity.** A commit containing
  Claude's work carries a `Co-Authored-By: Claude` trailer. A pull request is
  squash-merged into one commit, which carries the trailer if any part of it
  did. Four commits that touch chapter files carry it, and none of them for
  writing mathematics: `d47c1ab` moved every source under `tex/`, `446572b`
  switched the build to LuaLaTeX and jlreq, `eada0b3` added `\term` index
  markup, and `1b34b3a` (#55) is a squash whose chapter prose came from a
  commit without the trailer.

The rules behind this are in `CLAUDE.md`, which is what Claude reads first.

## License
[![MIT][mit-shield]][mit] [![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

| Path | License |
| --- | --- |
| `tex/*/ch*.tex`, `tex/*/bibliography.tex`, `tex/*/html/*.html`, `pdf/*.pdf` | [CC BY-NC-ND 4.0][cc-by-nc-nd] |
| `tex/html-common/latin-modern.css` | [GUST Font License][gust] |
| everything else | [MIT][mit] |

Full texts: [`LICENSE`](./LICENSE) (MIT) and
[`LICENSE-CC-BY-NC-ND-4.0`](./LICENSE-CC-BY-NC-ND-4.0).

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[mit]: https://opensource.org/licenses/MIT
[gust]: https://www.gust.org.pl/projects/e-foundry/licenses
[mit-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg
