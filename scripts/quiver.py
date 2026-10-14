#!/usr/bin/env python3
r"""Decode a quiver URL into the objects and arrows of the diagram it draws.

A figure drafted in quiver (https://q.uiver.app) keeps its source as a comment
above the `tikzcd` in the chapter:

    % https://q.uiver.app/#q=WzAsNCxbMCwwLCJBIl0s...

The part after `#q=` is base64 of a JSON array, and this script turns it back
into something readable. It is the first step of `/interactive`, which builds
an interactive page (docs/interactive-convention.md) from that draft.

**Why a script.** Decoding is the one fully mechanical step of making a page,
and the one where a slip goes unseen: an arrow index off by one, a dropped
`offset`, a label with a mangled backslash. A tested decoder settles it once.

The format, as quiver writes it:

    [version, n, vertex_1, ..., vertex_n, edge_1, ..., edge_m]

    vertex = [x, y, label?, label_colour?]
    edge   = [source, target, label?, alignment?, options?, label_colour?]

Cells are numbered vertices first, then edges, so an edge whose source or
target is `>= n` points at another edge: a 2-cell. Everything after the label
is optional and dropped from the end when it has its default value.

Usage, from the repo root — a chapter line holding the URL, or the URL itself:

    python scripts/quiver.py tex/category_theory/ch05.tex:33
    python scripts/quiver.py 'https://q.uiver.app/#q=WzAsMixbMCwwLCJBIl0sWzEsMCwiQiJdLFswLDEsImYiXV0='

It prints JSON: `objects` (index, x, y, label) and `arrows` (index, from, to,
label, alignment, offset, curve, the remaining options, and whether it is a
2-cell).

Run the tests from the repo root:
    python -m unittest discover -s scripts -t scripts -p 'test_*.py'
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

URL = re.compile(r"https://q\.uiver\.app/#q=([A-Za-z0-9+/=_-]+)")
ALIGNMENT = ["left", "centre", "right", "over"]


def find_url(text: str) -> str:
    """The base64 payload of the one quiver URL in `text`."""
    found = URL.findall(text)
    if len(found) != 1:
        raise ValueError(f"expected one quiver URL, found {len(found)}")
    return found[0]


def decode_payload(payload: str) -> list:
    """The raw JSON array behind a `#q=` payload."""
    payload = payload.replace("-", "+").replace("_", "/")
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.b64decode(payload).decode("utf-8"))


def parse(raw: list) -> dict:
    """Objects and arrows, with every optional field filled in."""
    if len(raw) < 2:
        return {"objects": [], "arrows": []}
    n = raw[1]
    cells = raw[2:]
    objects = []
    for i, v in enumerate(cells[:n]):
        objects.append({"index": i, "x": v[0], "y": v[1], "label": v[2] if len(v) > 2 else ""})
    arrows = []
    for k, e in enumerate(cells[n:]):
        options = dict(e[4]) if len(e) > 4 else {}
        arrows.append({
            "index": n + k,
            "from": e[0],
            "to": e[1],
            "label": e[2] if len(e) > 2 else "",
            "alignment": ALIGNMENT[e[3] if len(e) > 3 else 0],
            "offset": options.pop("offset", 0),
            "curve": options.pop("curve", 0),
            "options": options,
            "two_cell": e[0] >= n or e[1] >= n,
        })
    return {"objects": objects, "arrows": arrows}


def read_target(target: str) -> str:
    """The text holding the URL: a `path:line` of a chapter, or the URL itself."""
    if target.startswith("https://"):
        return target
    path, sep, line = target.rpartition(":")
    if not sep or not line.isdigit():
        raise ValueError(f"expected <file>:<line> or a URL, got {target!r}")
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    k = int(line)
    if not 1 <= k <= len(lines):
        raise ValueError(f"{path} has no line {k}")
    return lines[k - 1]


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        print("usage: python scripts/quiver.py <file>:<line> | <url>", file=sys.stderr)
        return 2
    try:
        diagram = parse(decode_payload(find_url(read_target(argv[0]))))
    except (ValueError, OSError) as err:
        print(f"quiver.py: {err}", file=sys.stderr)
        return 1
    print(json.dumps(diagram, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
