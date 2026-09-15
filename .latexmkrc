# .latexmkrc — compile with LuaLaTeX
$lualatex  = 'lualatex -halt-on-error -interaction=nonstopmode -file-line-error -synctex=1 %O %S';
$pdf_mode  = 4;    # 4 = lualatex writes the PDF directly, with no DVI step
$max_repeat = 5;   # allow enough passes for references/TOC to settle

# upmendex, not makeindex: makeindex sorts a Japanese headword by code point,
# which is not an order any reader can follow. upmendex takes the reading from
# the "よみ@漢字" that \term writes and collates it through ICU.
#
# -g groups the Japanese headings by 行 (あ か さ …) instead of one per mora,
# and is a command-line flag with no style-file equivalent. tex/index.ist is
# reached relatively because latexmk already runs with the topic directory as
# the working directory — that is what -cd does locally and what
# work_in_root_file_dir does in CI, and \input{../preamble.tex} needs the very
# same thing.
#
# The conditional is not defensive programming. \makeindex opens the .idx file
# whether or not anything is written to it, so a topic with no \term at all —
# four of them right now — still reaches this rule, with an empty file. upmendex
# treats "0 entries accepted" as an error and exits 255, which fails latexmk and
# would have made the index impossible to adopt gradually. Writing an empty .ind
# instead keeps \printindex inert for those topics: it inputs a file with
# nothing in it, and no 索引 page or table-of-contents line is produced.
$makeindex = 'if [ -s %S ]; then upmendex -g -s ../index.ist %O -o %D %S; else : > %D; fi';
