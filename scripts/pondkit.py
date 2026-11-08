"""Shared pieces for the pond: palette, embedded pixel fonts, text metrics, sprites.

Standard library only, so the nightly workflow needs no installs.
"""
from __future__ import annotations

import base64
import json
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# ---------------------------------------------------------------- palette ---
# A night pond: deep teal water, warm lantern cream, koi orange, lily green,
# and the profile's own blue (#5884a8) as the accent.
C = {
    "deep": "#0b171b",      # darkest water
    "water": "#0f2126",     # card background
    "panel": "#132a30",     # raised surface
    "line": "#21414a",      # borders, hairlines
    "line2": "#2b525c",
    "cream": "#efe3c8",     # main text
    "mist": "#9db3ad",      # secondary text
    "dim": "#5f7d7b",       # tertiary text
    "blue": "#5884a8",      # profile accent
    "sky": "#8fb3d1",       # light accent (text on dark)
    "koi": "#e8875b",       # koi orange
    "gold": "#e9c46a",      # lantern / fireflies
    "lily": "#7fb48a",      # lily pads
    "lily_dk": "#4f8463",
    "lotus": "#e9a6a1",     # lotus pink
    "moon": "#f3ead2",
}

FONT_STACK = {
    "vt323": "'VT323', 'Courier New', monospace",
    "silk": "'Silkscreen', 'Courier New', monospace",
    "pixelify": "'Pixelify Sans', 'Courier New', monospace",
}
FONT_FAMILY = {"vt323": "VT323", "silk": "Silkscreen", "pixelify": "Pixelify Sans"}


@lru_cache(maxsize=None)
def _font_b64(name: str) -> str:
    return base64.b64encode((FONT_DIR / f"{name}.woff2").read_bytes()).decode()


def font_css(*names: str) -> str:
    """@font-face rules with the fonts embedded, so the SVG renders the same
    everywhere (an SVG shown through <img> may not load anything external)."""
    return "".join(
        f"@font-face{{font-family:'{FONT_FAMILY[n]}';"
        f"src:url(data:font/woff2;base64,{_font_b64(n)}) format('woff2');}}"
        for n in names
    )


@lru_cache(maxsize=None)
def _metrics() -> dict:
    return json.loads((FONT_DIR / "metrics.json").read_text())


def text_width(text: str, font: str, size: float, spacing: float = 0) -> float:
    m = _metrics()[font]
    return sum(m.get(ch, 0.5) for ch in text) * size + spacing * max(len(text) - 1, 0)


def t(x, y, text, font="vt323", size=20, fill=None, anchor="start", extra="", spacing=0):
    """A <text> element."""
    fill = fill or C["cream"]
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x:g}" y="{y:g}" font-family="{FONT_STACK[font]}" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}"{ls} {extra}>{escape(text)}</text>'
    )


def svg_open(w, h, title, desc="", css="", extra=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" {extra}>'
        f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc or title)}</desc>'
        f"<style>{css}"
        # Calm by default, still for anyone who asks their system for less motion.
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        "</style>"
    )


# ---------------------------------------------------------------- window ---
def window(W, H, title, body, css="", desc=""):
    RX = 14
    dots = "".join(f'<rect x="{18 + i * 14}" y="13" width="8" height="8" fill="{c}"/>'
                   for i, c in enumerate((C["koi"], C["gold"], C["lily"])))
    return (svg_open(W, H, title, desc, font_css("vt323", "silk") + css)
            + f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="{RX}" fill="{C["water"]}" '
              f'stroke="{C["line2"]}" stroke-width="1.5"/>'
            + f'<path d="M.75 {RX}a{RX - .75} {RX - .75} 0 0 1 {RX - .75}-{RX - .75}h{W - 2 * RX}'
              f'a{RX - .75} {RX - .75} 0 0 1 {RX - .75} {RX - .75}v20H.75z" fill="{C["panel"]}"/>'
            + f'<line x1="1" y1="34" x2="{W - 1}" y2="34" stroke="{C["line"]}"/>'
            + f'<g shape-rendering="crispEdges">{dots}</g>'
            + t(W / 2, 22, title, "silk", 12, C["mist"], "middle", spacing=1.5)
            + body)


# ---------------------------------------------------------------- pixels ---
def pixels(rows: list[str], colors: dict[str, str], x: float, y: float, px: float,
           extra: str = "") -> str:
    """Draw a pixel sprite. Each row is a string; each char maps to a color in
    `colors` ('.' or ' ' is transparent). Horizontal runs merge into one rect."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch in ". " or ch not in colors:
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            out.append(
                f'<rect x="{x + start * px:g}" y="{y + r * px:g}" '
                f'width="{(c - start) * px:g}" height="{px:g}" fill="{colors[ch]}"/>'
            )
    return f'<g shape-rendering="crispEdges" {extra}>{"".join(out)}</g>'


def pixel_disc(radius: int) -> list[str]:
    rows = []
    for yy in range(-radius, radius + 1):
        row = ""
        for xx in range(-radius, radius + 1):
            d = (xx + 0.5) ** 2 + (yy + 0.5) ** 2
            row += "#" if d <= radius * radius else "."
        rows.append(row)
    return rows


def lily_pad(rx: int, ry: int, notch: int = 0) -> list[str]:
    """A pixel lily pad: an ellipse with a wedge cut out and a darker rim."""
    rows = []
    for yy in range(-ry, ry + 1):
        row = ""
        for xx in range(-rx, rx + 1):
            e = ((xx + .5) / (rx + .5)) ** 2 + ((yy + .5) / (ry + .5)) ** 2
            side = xx if notch == 0 else -xx - 1
            # a thin slit from the center to the edge, like a real pad
            in_notch = side > 0 and yy == 0 or (side > rx * .55 and yy == -1)
            if e <= 1 and not in_notch:
                if e > .7 and (yy + .5) * (ry and 1) > 0 and xx * (1 if notch == 0 else -1) > -rx * .3:
                    row += "r"          # shaded lower rim
                elif e > .72 and yy < 0 and (xx < 0 if notch == 0 else xx > 0):
                    row += "h"          # moonlit upper rim
                else:
                    row += "g"
            else:
                row += "."
        rows.append(row)
    return rows


LILY_COLORS = {"g": C["lily"], "r": C["lily_dk"], "h": "#a6d0a8"}

LOTUS = [
    "...p...",
    "..ppp..",
    ".pPpPp.",
    "pPPyPPp",
    ".pPPPp.",
    "..ggg..",
]
LOTUS_COLORS = {"p": C["lotus"], "P": "#f4c7c2", "y": C["gold"], "g": C["lily_dk"]}

# small flower bullet (5x5)
BLOOM = [
    ".a.a.",
    "aaaaa",
    ".aya.",
    "aaaaa",
    ".a.a.",
]

ENVELOPE = [
    "aaaaaaaaaaa",
    "ab.......ba",
    "a.b.....b.a",
    "a..b...b..a",
    "a...bbb...a",
    "a.........a",
    "aaaaaaaaaaa",
]

LINKEDIN = [
    "aaaaaaaaaaa",
    "a.a.......a",
    "a.........a",
    "a.a.aaaa..a",
    "a.a.a..a..a",
    "a.a.a..a..a",
    "aaaaaaaaaaa",
]

# a koi silhouette seen from above, swimming right (for the faint banner shadow)
KOI_SHADOW = [
    "..aa...............",
    ".aaa......aa.......",
    "aaaaa..aaaaaaaaa...",
    ".aaaaaaaaaaaaaaaaa.",
    "aaaaa..aaaaaaaaaaaa",
    ".aaa......aa.aaaa..",
    "..aa...............",
]
