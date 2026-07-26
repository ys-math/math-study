# 数学勉強ノート
勉強した数学の内容をLaTeXを用いてまとめていきます。
トピックごとにディレクトリを分けています。

各トピックのPDFは以下から閲覧できます。

<!-- BEGIN PDF LINKS -->
* [代数的K理論](./pdf/algebraic_k_theory.pdf)
* [圏論](./pdf/category_theory.pdf)
* [微分幾何学](./pdf/differential_geometry.pdf)
* [群論](./pdf/group_theory.pdf)
* [λ計算](./pdf/lambda_calculus.pdf)
* [多様体論](./pdf/manifold.pdf)
* [位相幾何学](./pdf/topology.pdf)
<!-- END PDF LINKS -->

## ディレクトリ構造
<!-- BEGIN TREE -->
```
math-study/
├── algebraic_k_theory/
│   ├── ch01.tex
│   └── main.tex
├── category_theory/
│   ├── ch01.tex
│   └── main.tex
├── differential_geometry/
│   ├── ch01.tex
│   └── main.tex
├── group_theory/
│   ├── ch01.tex
│   └── main.tex
├── lambda_calculus/
│   ├── ch01.tex
│   ├── ch02.tex
│   ├── ch03.tex
│   └── main.tex
├── manifold/
│   ├── ch01.tex
│   └── main.tex
├── scripts/
│   ├── generate_pdf_links.py
│   ├── generate_tree.py
│   ├── latex_unicode.py
│   ├── readme_block.py
│   └── test_latex_unicode.py
├── topology/
│   ├── ch01.tex
│   └── main.tex
├── LICENSE
├── README.md
├── colophon.tex
└── preamble.tex
```
<!-- END TREE -->

## Adding a new topic
Each topic is one top-level directory holding a `main.tex` and its chapters.
To create one:

```bash
python scripts/new_topic.py sheaf_theory --title 層論
```

The directory name must be lowercase letters, digits and underscores; the title
is the `\DocTitle`, which also becomes the link label in the PDF list above.

1. Run the command above. It writes `sheaf_theory/main.tex` and an empty
   `sheaf_theory/ch01.tex`, and prints the label the README will show.
2. Write the mathematics in `ch01.tex`.
3. Commit and push to `main`.
4. CI takes it from there: `build-pdf.yml` compiles the topic and commits
   `pdf/sheaf_theory.pdf`, and `update-readme.yml` regenerates the PDF list and
   the directory tree above. Both sections are generated — edit the `.tex`
   sources, not the lists.

To add a chapter, create `ch02.tex` and add `\input{ch02.tex}` to that topic's
`main.tex` by hand; nothing does this automatically.

## ライセンス
Shield: [![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License][cc-by-nc-nd].

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg