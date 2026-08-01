# .latexmkrc — compile with LuaLaTeX
$lualatex  = 'lualatex -halt-on-error -interaction=nonstopmode -file-line-error -synctex=1 %O %S';
$pdf_mode  = 4;    # 4 = lualatex writes the PDF directly, with no DVI step
$max_repeat = 5;   # allow enough passes for references/TOC to settle
