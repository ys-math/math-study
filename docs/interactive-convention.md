# Interactive convention

How a figure in the notes gets an interactive version: a rotatable 3D page,
published on GitHub Pages and linked from the PDF under the figure it extends.
This file owns every rule about those pages: where they live, what a page
contains, how the PDF links to one, and what checks the pair. Other files point
here instead of restating it.

## Layout

```
tex/
  html-common/                 the engine, shared by every page
    diagram.js                 Diagram.mount(): builds the page and runs it
    diagram.css                layout, colours, controls, opening animation
    latin-modern.css           the embedded fonts, under their own licence
  <slug>/
    ch01.tex …                 \Interactive{<name>} under the figure
    html/
      <name>.html              one page per figure: data only
```

**A page belongs to its topic.** It sits in `tex/<slug>/html/`, so it moves
with the topic on a rename and goes with it on a delete. `<name>` is
kebab-case (`biproduct-sphere`), the same as the other web-facing names in
`docs/naming-convention.md`.

**`tex/html-common/` is not a topic.** The hyphen guarantees it: a topic slug
cannot contain one, so `scripts/new_topic.py` can never create a topic with
that name, and nothing that reads `tex/*/main.tex` sees it. It is a shared path
in the sense of `docs/git-strategy.md`: a change to the engine is a change to
every page at once, so it goes on a branch and through a PR, like
`tex/preamble.tex`.

## The address

```
https://ys-math.github.io/math-study/<slug>/html/<name>.html
```

`.github/workflows/pages.yml` publishes `tex/html-common/` and every
`tex/*/html/*.html` **at their paths under `tex/`, unchanged**. That is why the
URL keeps the `html/` segment: the relative path from a page to the engine,
`../../html-common/`, then resolves the same way on disk as on the site, so
opening the file locally previews exactly what ships. Shortening the URL would
mean rewriting every page during the deploy, and the local preview would stop
proving anything.

The address is written in one place, the `\Interactive` macro in
`tex/preamble.tex`. If the hosting ever moves, that one edit re-points every
PDF on its next build.

## A page

A page is the skeleton below plus one `Diagram.mount({...})` call. Everything a
reader sees is built by the engine: the title, the link back to
`pdf/<slug>.pdf` (worked out from the page's own path), the Auto/Light/Dark
switch, the canvas with its Reset/Spin/Depth controls, the equation panel and
the opening animation. That is what keeps every page the same: the structure
is in one file and nowhere else. The UI is in English.

```html
<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Biproduct Sphere</title>
<link rel="stylesheet" href="../../html-common/latin-modern.css">
<link rel="stylesheet" href="../../html-common/diagram.css">
<script src="../../html-common/diagram.js"></script>
</head>
<body>
<script>
Diagram.mount({ ... });
</script>
</body>
</html>
```

A page needing something the engine cannot do gets it as a new engine option,
through a PR. It never gets it as HTML of its own. `scripts/test_interactive.py`
checks that a page loads the shared engine, so a page that inlines one fails.

### The config

`tex/homological_algebra/html/biproduct-sphere.html` is the worked example, and
uses every field.

| field | meaning |
| --- | --- |
| `title` | the page heading, and the same text as `<title>` |
| `description` | one sentence for screen readers, describing the diagram |
| `objects` | `{ id: { at: [x, y, z], tex, plain } }`. The vertices, on the unit sphere. `tex` is typeset by MathJax, and `plain` is the fallback while it loads or if it fails |
| `arrows` | `[{ id, from, to, tex, plain }]`, drawn as great-circle arcs. `straight: true` makes a chord through the middle instead, and `labelAt` (default `0.5`) is where along the arrow its label sits |
| `home` | `[{ axis, deg }, …]`. The rotations, composed left to right, that give the home view: where Reset returns to and the opening animation ends |
| `intro` | optional: `{ objects: { id: ms }, arrows: { id: ms } }`, the start time of each item in the opening animation. Without it, things appear in the order they are listed |
| `tabs` | the equation panel, one entry per tab; see below |

A **tab** is `{ label, groups: [{ title, note?, faces: [...] }] }`, or a
definitions tab `{ label, intro?, key?, definitions: [...] }`. Titles, notes,
intros and definition texts take `$...$` for inline TeX.

A **face** is an equation the reader can hover over or pin. It highlights
arrows by role, and on click it turns the diagram to a view of itself:

| field | meaning |
| --- | --- |
| `path` | arrow ids of the composite, in blue |
| `direct` | the arrow (or arrows) it equals, in orange |
| `legs` | arrows kept in strong ink without a colour |
| `objects` | the objects it involves; the others fade |
| `tex`, `plain` | the equation, as in `objects` |
| `key` | optional `[path label, direct label]` for the colour key; the default is "composite path" / "arrow it equals" |
| `view` | a fixed direction `[x, y, z]` to look from |
| `look` | used when there is no `view`: `'outside'` (the default) looks from beyond the centroid of the first three objects; `'plane'` looks square-on to the plane through them, nudged by `tilt: [x, y, z]`; `'none'` leaves the view alone |
| `up` | optional up direction for the view, default `[0, 1, 0]` |

A **definition** is `{ sym, text, path, direct, objects }`. It highlights like a
face but never turns the view.

## Linking from the PDF

```latex
\begin{tikzpicture} … \end{tikzpicture}
\Interactive{biproduct-sphere}
```

On its own line, directly after the figure, in a chapter of the same topic.
It prints a centred "▶ interactive" link and nothing else. There is no
footnote, so the address is only the link's target and does not appear in a
printed copy. The chapter is the owner's
prose: the owner writes this line.

**A page and its `\Interactive` line land in the same commit.**
`scripts/test_interactive.py` checks both directions: every link has a page,
and every page has a link. Either half alone fails it, and because the
`scripts/` tests also run in `update-readme.yml`, the README bot then stays red
until the other half arrives.

Both halves are `tex/<topic>/**`, so the pair commits straight to `main`, and
like a chapter it carries no `Co-Authored-By`.

## Licence

| path | licence |
| --- | --- |
| `tex/*/html/*.html` | CC BY-NC-ND 4.0, the same as the chapters. A page's data is the owner's mathematics |
| `tex/html-common/diagram.js`, `diagram.css` | MIT, like `tex/preamble.tex` |
| `tex/html-common/latin-modern.css` | GUST Font License: Latin Modern, embedded. That file holds nothing else, so the boundary is one file wide |

A page carries `<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->` on line 1,
and the test checks it. The path table in `README.md` `## License` is
authoritative, as for every other file.

MathJax is not in the repo. The engine loads one exact version from jsDelivr,
and only `MATHJAX_URL` in `diagram.js` names it, so upgrading is a one-line PR.

## Previewing

Open the page file in a browser. Both the stylesheets and the engine are
classic relative loads, which work over `file://`. MathJax needs the network.
Choose reduced motion in the OS settings to skip the opening animation while
iterating.

## Renaming and deleting

- **A page** renamed is its `\Interactive{}` line renamed in the same commit.
  The old URL simply stops working, and nothing redirects it.
- **A topic** renamed with `git mv` takes `html/` along, and `\DocSlug` follows
  `\TexRepo`, so the PDF links follow too. The published URLs change with the
  slug.
- **A topic** deleted takes its pages with it. The next Pages deploy drops them,
  because the site is rebuilt from the tree each time.
