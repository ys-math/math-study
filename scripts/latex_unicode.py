#!/usr/bin/env python3
"""Render a short LaTeX fragment as Markdown-safe inline text.

Used to turn a document's ``\\DocTitle`` into the link label of the PDF list in
README.md, e.g. ``$\\lambda$計算`` -> ``λ計算``.

Only the subset of LaTeX that shows up in a note title is supported: math
delimiters, symbol commands, the blackboard/fraktur/script alphabets, and
sub/superscripts (rendered as ``<sub>``/``<sup>``, which GitHub honours inside
link labels). Anything else raises UnsupportedLatex rather than guessing, so a
malformed label can never reach README.md.
"""

from __future__ import annotations

import string

__all__ = ["UnsupportedLatex", "render"]


class UnsupportedLatex(ValueError):
    """Raised when a fragment contains LaTeX we refuse to guess at."""


GREEK = {
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ϵ",
    r"\varepsilon": "ε",
    r"\zeta": "ζ",
    r"\eta": "η",
    r"\theta": "θ",
    r"\vartheta": "ϑ",
    r"\iota": "ι",
    r"\kappa": "κ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\nu": "ν",
    r"\xi": "ξ",
    r"\pi": "π",
    r"\varpi": "ϖ",
    r"\rho": "ρ",
    r"\varrho": "ϱ",
    r"\sigma": "σ",
    r"\varsigma": "ς",
    r"\tau": "τ",
    r"\upsilon": "υ",
    r"\phi": "ϕ",
    r"\varphi": "φ",
    r"\chi": "χ",
    r"\psi": "ψ",
    r"\omega": "ω",
    r"\Gamma": "Γ",
    r"\Delta": "Δ",
    r"\Theta": "Θ",
    r"\Lambda": "Λ",
    r"\Xi": "Ξ",
    r"\Pi": "Π",
    r"\Sigma": "Σ",
    r"\Upsilon": "Υ",
    r"\Phi": "Φ",
    r"\Psi": "Ψ",
    r"\Omega": "Ω",
}

LETTERLIKE = {
    r"\ell": "ℓ",
    r"\hbar": "ℏ",
    r"\aleph": "ℵ",
    r"\beth": "ℶ",
    r"\gimel": "ℷ",
    r"\daleth": "ℸ",
    r"\wp": "℘",
    r"\Re": "ℜ",
    r"\Im": "ℑ",
    r"\partial": "∂",
    r"\nabla": "∇",
    r"\infty": "∞",
    r"\emptyset": "∅",
    r"\varnothing": "∅",
    r"\top": "⊤",
    r"\bot": "⊥",
    r"\prime": "′",
    r"\circledS": "Ⓢ",
}

OPERATORS = {
    # Binary operators.
    r"\times": "×",
    r"\div": "÷",
    r"\pm": "±",
    r"\mp": "∓",
    r"\cdot": "⋅",
    r"\ast": "∗",
    r"\star": "⋆",
    r"\dagger": "†",
    r"\ddagger": "‡",
    r"\circ": "∘",
    r"\bullet": "∙",
    r"\oplus": "⊕",
    r"\ominus": "⊖",
    r"\otimes": "⊗",
    r"\oslash": "⊘",
    r"\odot": "⊙",
    r"\wedge": "∧",
    r"\vee": "∨",
    r"\sqcup": "⊔",
    r"\sqcap": "⊓",
    r"\cup": "∪",
    r"\cap": "∩",
    r"\setminus": "∖",
    r"\smallsetminus": "∖",
    r"\ltimes": "⋉",
    r"\rtimes": "⋊",
    r"\boxtimes": "⊠",
    # Relations.
    r"\le": "≤",
    r"\leq": "≤",
    r"\ge": "≥",
    r"\geq": "≥",
    r"\ll": "≪",
    r"\gg": "≫",
    r"\ne": "≠",
    r"\neq": "≠",
    r"\equiv": "≡",
    r"\sim": "∼",
    r"\simeq": "≃",
    r"\cong": "≅",
    r"\approx": "≈",
    r"\propto": "∝",
    r"\in": "∈",
    r"\notin": "∉",
    r"\ni": "∋",
    r"\subset": "⊂",
    r"\subseteq": "⊆",
    r"\subsetneq": "⊊",
    r"\supset": "⊃",
    r"\supseteq": "⊇",
    r"\supsetneq": "⊋",
    r"\perp": "⊥",
    r"\parallel": "∥",
    r"\mid": "∣",
    r"\vdash": "⊢",
    r"\dashv": "⊣",
    r"\models": "⊨",
    r"\angle": "∠",
    r"\triangle": "△",
    r"\square": "□",
    r"\diamond": "⋄",
    # Arrows.
    r"\to": "→",
    r"\rightarrow": "→",
    r"\longrightarrow": "⟶",
    r"\leftarrow": "←",
    r"\longleftarrow": "⟵",
    r"\leftrightarrow": "↔",
    r"\mapsto": "↦",
    r"\longmapsto": "⟼",
    r"\hookrightarrow": "↪",
    r"\hookleftarrow": "↩",
    r"\twoheadrightarrow": "↠",
    r"\rightarrowtail": "↣",
    r"\Rightarrow": "⇒",
    r"\Longrightarrow": "⟹",
    r"\Leftarrow": "⇐",
    r"\Leftrightarrow": "⇔",
    r"\iff": "⇔",
    r"\uparrow": "↑",
    r"\downarrow": "↓",
    r"\rightsquigarrow": "⇝",
    # Big operators.
    r"\sum": "∑",
    r"\prod": "∏",
    r"\coprod": "∐",
    r"\int": "∫",
    r"\oint": "∮",
    r"\iint": "∬",
    r"\bigoplus": "⨁",
    r"\bigotimes": "⨂",
    r"\bigcup": "⋃",
    r"\bigcap": "⋂",
    r"\bigsqcup": "⨆",
    r"\bigwedge": "⋀",
    r"\bigvee": "⋁",
    # Logic and misc.
    r"\forall": "∀",
    r"\exists": "∃",
    r"\nexists": "∄",
    r"\neg": "¬",
    r"\lnot": "¬",
    r"\therefore": "∴",
    r"\because": "∵",
    r"\ldots": "…",
    r"\dots": "…",
    r"\cdots": "⋯",
    r"\vdots": "⋮",
    r"\ddots": "⋱",
    r"\surd": "√",
    r"\deg": "°",
    r"\langle": "⟨",
    r"\rangle": "⟩",
    r"\lVert": "‖",
    r"\rVert": "‖",
    r"\lfloor": "⌊",
    r"\rfloor": "⌋",
    r"\lceil": "⌈",
    r"\rceil": "⌉",
}

# Spacing commands: keep the visual gap, or drop it where a title would not want
# one. \, and friends collapse to nothing so that "$K$\,理論" reads as "K理論".
SPACING = {
    r"\,": "",
    r"\;": "",
    r"\:": "",
    r"\!": "",
    r"\ ": " ",
    r"\quad": " ",
    r"\qquad": "  ",
}

# Escaped literals.
ESCAPES = {
    r"\$": "$",
    r"\%": "%",
    r"\&": "&",
    r"\#": "#",
    r"\_": "_",
    r"\{": "{",
    r"\}": "}",
    r"\textbackslash": "\\",
    r"\LaTeX": "LaTeX",
    r"\TeX": "TeX",
}

SYMBOLS: dict[str, str] = {**GREEK, **LETTERLIKE, **OPERATORS, **SPACING, **ESCAPES}

# Literal characters that Markdown or HTML would otherwise interpret. The output
# is an inline Markdown link label, so anything active has to be neutralised.
# '*' maps to the asterisk operator instead of an escape, since in a title it is
# always the math operator (as in C^*-algebra) and it needs no escaping.
LITERALS = {
    "*": "∗",
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "[": r"\[",
    "]": r"\]",
    "`": r"\`",
    "_": r"\_",
    "\\": r"\\",
    "$": r"\$",
}


def _alphabet(base_upper: int, base_lower: int, exceptions: dict[str, str]) -> dict[str, str]:
    """Build a letter -> styled-letter map from a contiguous Unicode block.

    Unicode carved several styled letters out into the Letterlike Symbols block
    long before the Mathematical Alphanumeric Symbols block existed, leaving
    holes in the latter; `exceptions` fills those in.
    """
    table = {}
    for offset, letter in enumerate(string.ascii_uppercase):
        table[letter] = chr(base_upper + offset)
    for offset, letter in enumerate(string.ascii_lowercase):
        table[letter] = chr(base_lower + offset)
    table.update(exceptions)
    return table


# U+1D538 MATHEMATICAL DOUBLE-STRUCK CAPITAL A / U+1D552 small a.
BLACKBOARD = _alphabet(
    0x1D538,
    0x1D552,
    {"C": "ℂ", "H": "ℍ", "N": "ℕ", "P": "ℙ", "Q": "ℚ", "R": "ℝ", "Z": "ℤ"},
)

# U+1D504 MATHEMATICAL FRAKTUR CAPITAL A / U+1D51E small a.
FRAKTUR = _alphabet(
    0x1D504,
    0x1D51E,
    {"C": "ℭ", "H": "ℌ", "I": "ℑ", "R": "ℜ", "Z": "ℨ"},
)

# U+1D49C MATHEMATICAL SCRIPT CAPITAL A / U+1D4B6 small a.
SCRIPT = _alphabet(
    0x1D49C,
    0x1D4B6,
    {
        "B": "ℬ",
        "E": "ℰ",
        "F": "ℱ",
        "H": "ℋ",
        "I": "ℐ",
        "L": "ℒ",
        "M": "ℳ",
        "R": "ℛ",
        "e": "ℯ",
        "g": "ℊ",
        "o": "ℴ",
    },
)

# Commands taking one argument whose letters are restyled character by character.
ALPHABETS = {
    r"\mathbb": BLACKBOARD,
    r"\Bbb": BLACKBOARD,
    r"\mathfrak": FRAKTUR,
    r"\mathcal": SCRIPT,
    r"\mathscr": SCRIPT,
}

# Commands taking one argument that is simply unwrapped.
TRANSPARENT = {
    r"\mathrm",
    r"\mathbf",
    r"\mathit",
    r"\mathsf",
    r"\mathtt",
    r"\mathnormal",
    r"\operatorname",
    r"\text",
    r"\textrm",
    r"\textbf",
    r"\textit",
    r"\textsf",
    r"\texttt",
    r"\textnormal",
    r"\mbox",
}


def _command_at(source: str, index: int) -> tuple[str, int]:
    """Read the command starting at `source[index]` ('\\'); return it and the next index."""
    rest = source[index + 1 :]
    name = ""
    for char in rest:
        if char.isalpha():
            name += char
        else:
            break
    if not name:
        # Single non-alphabetic control sequence: \, \! \{ \$ ...
        if not rest:
            raise UnsupportedLatex("trailing backslash")
        return "\\" + rest[0], index + 2
    return "\\" + name, index + 1 + len(name)


def _skip_spaces(source: str, index: int) -> int:
    while index < len(source) and source[index] == " ":
        index += 1
    return index


def _group_at(source: str, index: int) -> tuple[str, int]:
    """Read a braced group starting at `source[index]` ('{'); return body and next index."""
    depth = 0
    for position in range(index, len(source)):
        if source[position] == "{":
            depth += 1
        elif source[position] == "}":
            depth -= 1
            if depth == 0:
                return source[index + 1 : position], position + 1
    raise UnsupportedLatex("unbalanced '{'")


def _argument_at(source: str, index: int, command: str) -> tuple[str, int]:
    """Read the mandatory argument of `command`: a braced group or a single token."""
    index = _skip_spaces(source, index)
    if index >= len(source) or source[index] in "$}^_":
        raise UnsupportedLatex(f"'{command}' is missing its argument")
    if source[index] == "{":
        return _group_at(source, index)
    if source[index] == "\\":
        command_name, next_index = _command_at(source, index)
        return command_name, next_index
    return source[index], index + 1


def _escape(text: str) -> str:
    """Neutralise Markdown/HTML-active characters in literal text."""
    return "".join(LITERALS.get(char, char) for char in text)


def _restyle(text: str, table: dict[str, str], command: str) -> str:
    rendered = render(text)
    if not rendered:
        raise UnsupportedLatex(f"'{command}' is missing its argument")
    out = []
    for char in rendered:
        if char in table:
            out.append(table[char])
        elif char in " -" or char.isdigit():
            out.append(char)
        else:
            raise UnsupportedLatex(f"'{command}' cannot restyle {char!r}")
    return "".join(out)


def render(latex: str) -> str:
    """Convert a LaTeX fragment to Markdown-safe inline text.

    Raises UnsupportedLatex for anything outside the supported subset.
    """
    out: list[str] = []
    index = 0
    while index < len(latex):
        char = latex[index]

        if char == "$":
            # Math mode is purely a typesetting hint here; the content is
            # rendered the same either way.
            index += 1
        elif char == "{":
            body, index = _group_at(latex, index)
            out.append(render(body))
        elif char == "}":
            raise UnsupportedLatex("unbalanced '}'")
        elif char in "^_":
            argument, index = _argument_at(latex, index + 1, char)
            tag = "sup" if char == "^" else "sub"
            out.append(f"<{tag}>{render(argument)}</{tag}>")
        elif char == "\\":
            command, index = _command_at(latex, index)
            if command in SYMBOLS:
                out.append(_escape(SYMBOLS[command]))
            elif command in ALPHABETS:
                argument, index = _argument_at(latex, index, command)
                out.append(_restyle(argument, ALPHABETS[command], command))
            elif command in TRANSPARENT:
                argument, index = _argument_at(latex, index, command)
                out.append(render(argument))
            else:
                raise UnsupportedLatex(f"unsupported command '{command}'")
        else:
            out.append(_escape(char))
            index += 1

    return "".join(out)
