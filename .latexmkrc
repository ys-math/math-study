# .latexmkrc — compile with upLaTeX + dvipdfmx
$latex     = 'uplatex -halt-on-error -interaction=nonstopmode -file-line-error %O %S';
$bibtex    = 'upbibtex %O %B';
$biber     = 'biber --bblencoding=utf8 -u -U --output_safechars %O %B';
$makeindex = 'upmendex %O -o %D %S';
$dvipdf    = 'dvipdfmx %O -o %D %S';
$pdf_mode  = 3;    # 3 = build the PDF from the DVI using dvipdfmx
$max_repeat = 5;   # allow enough passes for references/TOC to settle
