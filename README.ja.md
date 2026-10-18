# 数学勉強ノート

[English](./README.md) | 日本語

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
category_theory          █████████▍░░░░░░░░░░   46.7%   71,257
homological_algebra      ██████▏░░░░░░░░░░░░░   30.8%   46,937
algebraic_k_theory       ██▍░░░░░░░░░░░░░░░░░   11.6%   17,748
lambda_calculus          █▍░░░░░░░░░░░░░░░░░░    6.7%   10,191
commutative_ring_theory  ▉░░░░░░░░░░░░░░░░░░░    4.1%    6,325
                                                       -------
total                                                  152,458
```
<!-- END TEXT METER -->

## ディレクトリ構成
<!-- BEGIN TREE -->
```
math-study/
├── docs/
│   ├── images/
│   │   ├── audit-workflow.svg
│   │   └── routing-rule.svg
│   ├── agent-system.md
│   ├── audit-workflow.ebnf
│   ├── bib-convention.md
│   ├── git-strategy.md
│   ├── index-convention.md
│   ├── interactive-convention.md
│   ├── issue-convention.md
│   ├── label-convention.md
│   ├── naming-convention.md
│   └── routing-rule.ebnf
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
│   │   │   ├── matrix-sphere.html
│   │   │   └── pullback.html
│   │   ├── ch01.tex
│   │   ├── ch02.tex
│   │   ├── ch03.tex
│   │   ├── ch04.tex
│   │   ├── ch05.tex
│   │   ├── ch06.tex
│   │   ├── ch07.tex
│   │   ├── ch08.tex
│   │   ├── ch09.tex
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

## AI の利用

このレポは [Claude Code](https://claude.com/claude-code) を使って書かれており, Claude が書くものと著者が書くものの境界は意図して引かれています。

- **数学は著者のものです。**
  `tex/*/ch*.tex` の文章, つまり PDF に載っている定義, 定理, 証明, 例はすべて著者が書いています。
  Claude はそれを書くことも書き直すこともしません。
  `/review-notes` はノートを読んで見つけたことを GitHub の issue にするだけで, どれをどう直すかは著者が決めます。
- **ツール類はおもに Claude のものです。**
  `scripts/`, `.github/`, `docs/`, `.claude/`, 両方の README, 共有の `tex/preamble.tex`, `tex/colophon.tex`, `tex/index.ist` は大部分を Claude が書いています。
- **どちらが書いたかは `git log` でコミット単位で分かります。**
  Claude の作業を含むコミットには `Co-Authored-By: Claude` のトレーラーが付きます。
  プルリクエストはスカッシュマージで一つのコミットにまとめられ, 一部にでもトレーラーがあればまとめたコミットにも付きます。
  章のファイルに触れるコミットのうち四つにトレーラーが付いていますが, どれも数学を書いたものではありません。
  `d47c1ab` はすべてのソースを `tex/` の下に移し, `446572b` はビルドを LuaLaTeX と jlreq に切り替え, `eada0b3` は索引用の `\term` マークアップを加えたもので, `1b34b3a` (#55) は章の文章がトレーラーのないコミットから来たスカッシュです。

この背後にあるルールは, Claude が最初に読む `CLAUDE.md` にあります。

## ライセンス
[![MIT][mit-shield]][mit] [![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

| パス | ライセンス |
| --- | --- |
| `tex/*/ch*.tex`, `tex/*/bibliography.tex`, `tex/*/html/*.html`, `pdf/*.pdf` | [CC BY-NC-ND 4.0][cc-by-nc-nd] |
| `tex/html-common/latin-modern.css` | [GUST Font License][gust] |
| それ以外すべて | [MIT][mit] |

全文: [`LICENSE`](./LICENSE) (MIT),
[`LICENSE-CC-BY-NC-ND-4.0`](./LICENSE-CC-BY-NC-ND-4.0)

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[mit]: https://opensource.org/licenses/MIT
[gust]: https://www.gust.org.pl/projects/e-foundry/licenses
[mit-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg
