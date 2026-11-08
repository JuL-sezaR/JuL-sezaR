"""Draws the static pieces of the profile into assets/.

    python3 scripts/build_assets.py

Edit the text in CONTENT below and rerun to change what the cards say.
"""
from __future__ import annotations

import random
from pathlib import Path

from pondkit import (BLOOM, C, window, ENVELOPE, KOI_SHADOW, LILY_COLORS, LINKEDIN, LOTUS,
                     LOTUS_COLORS, ROOT, font_css, lily_pad, pixel_disc, pixels,
                     svg_open, t, text_width)

OUT = ROOT / "assets"

CONTENT = {
    "name": "JuL-sezaR",
    "tagline": "AI Engineering @ Hacettepe University",
    "roles": ["quantum computing", "quantum machine learning", "ai engineering",
              "data science", "research oriented"],
    "motto": "research-driven · code-focused",
    "focus": ["Quantum Algorithms & Quantum ML", "Machine Learning & Data Science",
              "AI Infrastructure & Systems", "High-Performance Computing"],
    "toolbox": [
        ("languages", [("C++", "#7fa7d6"), ("Python", "#e9c46a"), ("Java", "#e8875b"), ("Rust", "#dea584")]),
        ("ml & data", [("PyTorch", "#ee8a5e"), ("NumPy", "#79a6c9"), ("Matplotlib", "#8fb8de")]),
        ("quantum", [("Qiskit", "#b49ad9"), ("Cirq", "#7fb4c9"), ("CUDA-Q", "#9ccf7f"),
                     ("PennyLane", "#e9a6a1"), ("Qollab", "#e9c46a")]),
    ],
}


def write(name: str, svg: str) -> None:
    (OUT / name).write_text(svg + "</svg>\n")
    print(f"assets/{name}: {len(svg) / 1024:.1f} KB")


def pixel_corners(w, h, inset=10, arm=4, px=3, color=C["gold"], opacity=.55):
    """Little L-shaped pixel brackets in each corner, like an old game frame."""
    g = []
    for cx, cy, sx, sy in ((inset, inset, 1, 1), (w - inset, inset, -1, 1),
                           (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)):
        for i in range(arm):
            g.append(f'<rect x="{cx + sx * i * px - (px if sx < 0 else 0):g}" '
                     f'y="{cy - (px if sy < 0 else 0):g}" width="{px}" height="{px}"/>')
            if i:
                g.append(f'<rect x="{cx - (px if sx < 0 else 0):g}" '
                         f'y="{cy + sy * i * px - (px if sy < 0 else 0):g}" width="{px}" height="{px}"/>')
    return f'<g fill="{color}" opacity="{opacity}" shape-rendering="crispEdges">{"".join(g)}</g>'


def scanlines(w, h, rx):
    return (f'<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="#000"/></pattern>'
            f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
            f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#scan)" opacity=".10"/>')


# ------------------------------------------------------------------ banner ---
def banner():
    W, H, RX = 840, 300, 18
    rnd = random.Random(7)
    css = font_css("vt323", "silk", "pixelify") + """
    .fly{animation:fly 6s ease-in-out infinite;}
    .drift{animation:drift 11s ease-in-out infinite alternate;}
    @keyframes fly{0%,100%{opacity:0}40%,60%{opacity:1}}
    @keyframes drift{from{transform:translate(0,0)}to{transform:translate(9px,-7px)}}
    .bob{animation:bob 8s ease-in-out infinite;}
    @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(2px)}}
    .wobble{animation:wobble 5s ease-in-out infinite;}
    @keyframes wobble{0%,100%{transform:translateX(0)}50%{transform:translateX(2px)}}
    .shim{animation:shim 4.5s ease-in-out infinite;}
    @keyframes shim{0%,100%{opacity:.15;transform:translateX(0)}50%{opacity:.55;transform:translateX(5px)}}
    .ripple{transform-box:fill-box;transform-origin:center;animation:ripple 7s ease-out infinite;}
    @keyframes ripple{0%{transform:scale(.25);opacity:0}12%{opacity:.22}100%{transform:scale(1.7);opacity:0}}
    .swim{animation:swim 52s linear infinite;}
    @keyframes swim{from{transform:translateX(-90px)}to{transform:translateX(930px)}}
    .sway{animation:sway 3.2s ease-in-out infinite alternate;}
    @keyframes sway{from{transform:translateY(-3px)}to{transform:translateY(3px)}}
    .role{opacity:0;animation:role 17.5s ease-in-out infinite both;}
    .role.first{opacity:1}
    @keyframes role{0%{opacity:0;transform:translateY(4px)}2.5%{opacity:1;transform:translateY(0)}
      17%{opacity:1;transform:translateY(0)}19.5%{opacity:0;transform:translateY(-3px)}100%{opacity:0}}
    .blink{animation:blink 1.1s steps(1) infinite;}
    @keyframes blink{50%{opacity:0}}
    """
    s = [svg_open(W, H, f"{CONTENT['name']} - {CONTENT['tagline']}",
                  "A pixel-art koi pond at night with a moon reflection, lily pads and fireflies.",
                  css)]
    s.append(f'''<defs>
      <radialGradient id="water" cx="78%" cy="38%" r="85%">
        <stop offset="0" stop-color="#16343d"/><stop offset=".45" stop-color="{C["water"]}"/>
        <stop offset="1" stop-color="{C["deep"]}"/></radialGradient>
      <radialGradient id="glow"><stop offset="0" stop-color="{C["moon"]}" stop-opacity=".35"/>
        <stop offset="1" stop-color="{C["moon"]}" stop-opacity="0"/></radialGradient>
      <radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset=".6" stop-color="#000" stop-opacity="0"/>
        <stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
      <filter id="soft"><feGaussianBlur stdDeviation="2.2"/></filter>
    </defs>''')
    s.append(f'<rect width="{W}" height="{H}" rx="{RX}" fill="url(#water)"/>')

    # dithered depth specks
    specks = []
    for _ in range(140):
        x, y = rnd.randrange(8, W - 8, 3), rnd.randrange(8, H - 8, 3)
        col = rnd.choice(["#1a3a43", "#0a1418", "#17323a"])
        specks.append(f'<rect x="{x}" y="{y}" width="3" height="3" fill="{col}"/>')
    s.append(f'<g shape-rendering="crispEdges" opacity=".8">{"".join(specks)}</g>')

    # moon reflection
    mx, my, px = 640, 52, 4
    disc = pixel_disc(9)
    shade = [row[:] for row in disc]
    s.append(f'<circle cx="{mx + 38}" cy="{my + 38}" r="95" fill="url(#glow)"/>')
    moon_rows = []
    for r, row in enumerate(shade):
        moon_rows.append("".join(
            ("s" if (ch == "#" and (c - r) > 9) else ("d" if ch == "#" and (r, c) in
             {(5, 6), (5, 7), (6, 6), (11, 11), (12, 11), (12, 12), (8, 13)} else ch))
            for c, ch in enumerate(row)))
    s.append(f'<g class="wobble">{pixels(moon_rows, {"#": C["moon"], "s": "#d9cfb4", "d": "#cbbf9f"}, mx, my, px)}</g>')
    for i, (dx, dy, w) in enumerate([(-6, 92, 88), (6, 102, 64), (-14, 112, 104), (14, 122, 48), (2, 132, 70)]):
        s.append(f'<rect class="shim" style="animation-delay:{i * .7:.1f}s" x="{mx + dx}" y="{my + dy}" '
                 f'width="{w}" height="3" fill="{C["moon"]}" shape-rendering="crispEdges"/>')

    # ripples
    for cx, cy, d in ((735, 248, 0), (500, 96, 2.4), (610, 270, 4.6)):
        s.append(f'<ellipse class="ripple" style="animation-delay:{d}s" cx="{cx}" cy="{cy}" rx="42" ry="13" '
                 f'fill="none" stroke="{C["cream"]}" stroke-width="1" opacity="0"/>')

    # lily pads + lotus
    for (x, y, rx, ry, n, d) in ((535, 196, 10, 6, 0, 0), (720, 222, 9, 5, 1, 1.5),
                                 (790, 140, 6, 4, 0, 3), (470, 250, 6, 4, 1, 2.2)):
        s.append(f'<g class="bob" style="animation-delay:{d}s">'
                 f'{pixels(lily_pad(rx, ry, n), LILY_COLORS, x, y, 4)}</g>')
    s.append(f'<g class="bob" style="animation-delay:0s">{pixels(LOTUS, LOTUS_COLORS, 560, 192, 4)}</g>')
    s.append(f'<g class="bob" style="animation-delay:1.5s">{pixels(LOTUS, LOTUS_COLORS, 737, 214, 3)}</g>')

    # a faint koi shadow gliding under the surface
    s.append(f'<g clip-path="url(#frame-clip)"><g class="swim"><g class="sway">'
             f'{pixels(KOI_SHADOW, {"a": "#050d10"}, 0, 262, 3, "opacity=\".55\"")}</g></g></g>')
    s.append(f'<defs><clipPath id="frame-clip"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath></defs>')

    # fireflies
    for i in range(8):
        x, y = rnd.randint(380, 815), rnd.randint(24, 280)
        dur, dl = rnd.uniform(5, 8), rnd.uniform(0, 6)
        s.append(f'<g class="drift" style="animation-delay:{-dl:.1f}s"><g class="fly" '
                 f'style="animation-duration:{dur:.1f}s;animation-delay:{dl:.1f}s">'
                 f'<circle cx="{x}" cy="{y}" r="4" fill="{C["gold"]}" opacity=".5" filter="url(#soft)"/>'
                 f'<rect x="{x - 1}" y="{y - 1}" width="2.5" height="2.5" fill="#fff4cc"/></g></g>')

    # text
    s.append(t(57, 70, "~ welcome to my pond ~", "silk", 12, C["mist"], spacing=2))
    s.append(t(55, 136, CONTENT["name"], "pixelify", 62, C["deep"]))
    s.append(t(52, 132, CONTENT["name"], "pixelify", 62, C["cream"]))
    s.append(t(57, 172, CONTENT["tagline"], "vt323", 29, C["sky"]))
    s.append(t(57, 214, ">", "vt323", 27, C["gold"]))
    x0 = 57 + text_width("> ", "vt323", 27)
    for i, role in enumerate(CONTENT["roles"]):
        cx = x0 + text_width(role, "vt323", 27) + 4
        cls = "role first" if i == 0 else "role"
        s.append(f'<g class="{cls}" style="animation-delay:{i * 3.5}s">'
                 + t(x0, 214, role, "vt323", 27, C["cream"])
                 + f'<rect class="blink" x="{cx:.1f}" y="196" width="11" height="20" fill="{C["gold"]}" opacity=".85"/></g>')
    s.append(t(57, 252, CONTENT["motto"], "vt323", 22, C["dim"]))

    s.append(f'<g clip-path="url(#frame-clip)">{scanlines(W, H, RX)}</g>')
    s.append(f'<rect width="{W}" height="{H}" rx="{RX}" fill="url(#vig)"/>')
    s.append(pixel_corners(W, H))
    s.append(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="{RX}" fill="none" '
             f'stroke="{C["line2"]}" stroke-width="1.5"/>')
    write("banner.svg", "".join(s))


# ------------------------------------------------------------ window cards ---
def about():
    W, H = 412, 290
    css = (".blink{animation:blink 1.1s steps(1) infinite;}@keyframes blink{50%{opacity:0}}")
    fs, x = 23, 24
    prompt = lambda y, cmd: (t(x, y, "$", "vt323", fs, C["gold"])
                             + t(x + 18, y, cmd, "vt323", fs, C["mist"]))
    out = lambda y, txt, col=C["cream"]: t(x + 18, y, txt, "vt323", fs, col)
    body = "".join([
        prompt(68, "whoami"),
        out(94, "JuL-sezaR · AI Engineering"),
        out(119, "@ Hacettepe University", C["sky"]),
        prompt(154, "cat interests.txt"),
        out(180, "quantum computing · QML · AI systems"),
        prompt(215, "cat approach.txt"),
        out(241, "research-driven · code-focused", C["lily"]),
        t(x, 272, "$", "vt323", fs, C["gold"]),
        f'<rect class="blink" x="{x + 18}" y="256" width="10" height="18" fill="{C["gold"]}" opacity=".85"/>',
    ])
    for line in ("quantum computing · QML · AI systems", "JuL-sezaR · AI Engineering"):
        assert x + 18 + text_width(line, "vt323", fs) < W - 16, line
    write("about.svg", window(W, H, "whoami.sh", body, css,
                              "JuL-sezaR, AI Engineering at Hacettepe University. Interests: quantum computing, "
                              "quantum machine learning, AI systems. Research-driven and code-focused."))


def focus():
    W, H = 412, 290
    cols = [C["koi"], C["gold"], C["lily"], C["sky"]]
    body = [t(24, 68, "what i'm tending", "silk", 12, C["gold"], spacing=1.5)]
    for i, item in enumerate(CONTENT["focus"]):
        y = 110 + i * 44
        body.append(pixels(BLOOM, {"a": cols[i], "y": C["cream"]}, 26, y - 15, 3))
        body.append(t(52, y, item, "vt323", 23, C["cream"]))
        assert 52 + text_width(item, "vt323", 23) < W - 16, item
        if i < 3:
            body.append(f'<line x1="52" y1="{y + 16}" x2="{W - 24}" y2="{y + 16}" stroke="{C["line"]}" '
                        f'stroke-dasharray="3 5"/>')
    body.append(pixels(LOTUS, LOTUS_COLORS, W - 46, 52, 3, 'opacity=".9"'))
    write("focus.svg", window(W, H, "focus.md", "".join(body),
                              desc="Technical focus: " + "; ".join(CONTENT["focus"])))


def toolbox():
    W = 840
    fs, ch, gap = 21, 32, 10
    x_label, x_chips, y = 28, 168, 66
    body = []
    for label, chips in CONTENT["toolbox"]:
        body.append(t(x_label, y + 21, label, "silk", 11, C["mist"], spacing=1.5))
        x = x_chips
        for name, col in chips:
            w = text_width(name, "vt323", fs) + 44
            if x + w > W - 26:
                x, y = x_chips, y + ch + gap
            body.append(
                f'<rect x="{x}" y="{y + 3}" width="{w:.0f}" height="{ch}" rx="5" fill="{C["deep"]}"/>'
                f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{ch}" rx="5" fill="{C["panel"]}" '
                f'stroke="{C["line2"]}"/>'
                f'<rect x="{x + 13}" y="{y + 12}" width="8" height="8" fill="{col}" shape-rendering="crispEdges"/>'
                + t(x + 30, y + 22, name, "vt323", fs, C["cream"]))
            x += w + gap
        y += ch + 22
        if label != CONTENT["toolbox"][-1][0]:
            body.append(f'<line x1="28" y1="{y - 11}" x2="{W - 28}" y2="{y - 11}" stroke="{C["line"]}" '
                        f'stroke-dasharray="3 5"/>')
    H = y + 6
    names = "; ".join(f"{l}: " + ", ".join(n for n, _ in c) for l, c in CONTENT["toolbox"])
    write("toolbox.svg", window(W, H, "toolbox", "".join(body), desc="Toolbox. " + names))


# --------------------------------------------------------------- dividers ---
def divider(label, fname):
    W, H = 840, 46
    col = C["blue"]
    s = [svg_open(W, H, label, css=font_css("silk"))]
    lw = text_width(label, "silk", 13, 3)
    s.append(t(W / 2, 29, label, "silk", 13, col, "middle", spacing=3))
    wave = []
    left_end, right_start = W / 2 - lw / 2 - 34, W / 2 + lw / 2 + 34
    for x in range(40, int(left_end), 6):
        dy = (0, -3, -3, 0, 3, 3)[(x // 6) % 6] if False else [0, -3, 0, 3][(x // 6) % 4]
        wave.append(f'<rect x="{x}" y="{22 + dy}" width="6" height="3"/>')
    for x in range(int(right_start), W - 40, 6):
        dy = [0, -3, 0, 3][(x // 6) % 4]
        wave.append(f'<rect x="{x}" y="{22 + dy}" width="6" height="3"/>')
    s.append(f'<g fill="{col}" opacity=".55" shape-rendering="crispEdges">{"".join(wave)}</g>')
    s.append(pixels(BLOOM, {"a": C["koi"], "y": C["gold"]}, left_end + 6, 16, 3))
    s.append(pixels(BLOOM, {"a": C["koi"], "y": C["gold"]}, right_start - 21, 16, 3))
    write(fname, "".join(s))


# ---------------------------------------------------------------- buttons ---
def button(label, icon, fname):
    W, H = 210, 52
    s = [svg_open(W, H, label, css=font_css("silk"))]
    s.append(f'<rect x="1" y="5" width="{W - 2}" height="{H - 6}" rx="9" fill="{C["deep"]}"/>')
    s.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 6}" rx="9" fill="{C["water"]}" '
             f'stroke="{C["line2"]}" stroke-width="1.5"/>')
    s.append(pixels(icon, {"a": C["gold"], "b": C["gold"]}, 20, 13, 3))
    s.append(t(64, 30, label, "silk", 14, C["cream"], spacing=1.5))
    s.append(t(W - 20, 30, "»", "silk", 16, C["koi"], "end"))
    write(fname, "".join(s))


# ----------------------------------------------------------------- footer ---
def footer():
    W, H = 840, 120
    css = font_css("vt323") + """
    .bob{animation:bob 8s ease-in-out infinite;}
    @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(2px)}}"""
    s = [svg_open(W, H, "Thanks for drifting by", css=css)]
    for (x, y, rx, ry, n, d) in ((90, 62, 8, 5, 0, 0), (180, 80, 5, 3, 1, 2), (640, 78, 6, 4, 0, 1),
                                 (722, 58, 9, 5, 1, 3)):
        s.append(f'<g class="bob" style="animation-delay:{d}s">{pixels(lily_pad(rx, ry, n), LILY_COLORS, x, y, 4)}</g>')
    s.append(f'<g class="bob">{pixels(LOTUS, LOTUS_COLORS, 112, 52, 4)}</g>')
    s.append(f'<g class="bob" style="animation-delay:3s">{pixels(LOTUS, LOTUS_COLORS, 742, 48, 4)}</g>')
    s.append(t(W / 2, 62, "thanks for drifting by", "vt323", 28, C["blue"], "middle"))
    s.append(t(W / 2, 88, "the koi grows a little every night ~", "vt323", 21, C["dim"], "middle"))
    write("footer.svg", "".join(s))


# ---------------------------------------------------------------- koi pond ---
def koi_pond():
    """The koi GIF set into a pond. The GIF is embedded, so it animates inside
    the SVG and the whole pond is one image. Needs koi/koi.gif (git-koi)."""
    import base64
    gif = ROOT / "koi" / "koi.gif"
    if not gif.exists():
        print("koi/koi.gif not found yet; skipping koi-pond.svg")
        return
    W, H, RX = 840, 300, 18
    rnd = random.Random(11)
    css = font_css("vt323", "silk") + """
    .bob{animation:bob 8s ease-in-out infinite;}
    @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(2px)}}
    .ripple{transform-box:fill-box;transform-origin:center;animation:ripple 8s ease-out infinite;}
    @keyframes ripple{0%{transform:scale(.4);opacity:0}12%{opacity:.18}100%{transform:scale(1.5);opacity:0}}"""
    s = [svg_open(W, H, "My koi",
                  "My koi, redrawn every night from my GitHub activity: languages color it, "
                  "contributions grow it, streaks mark it, and yesterday decides how it swims.", css)]
    s.append(f'''<defs>
      <radialGradient id="pw" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#173a43"/>
        <stop offset=".55" stop-color="{C["water"]}"/><stop offset="1" stop-color="{C["deep"]}"/></radialGradient>
      <radialGradient id="pool"><stop offset="0" stop-color="#1d4650" stop-opacity=".9"/>
        <stop offset="1" stop-color="#1d4650" stop-opacity="0"/></radialGradient>
      <clipPath id="pc"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath></defs>''')
    s.append(f'<rect width="{W}" height="{H}" rx="{RX}" fill="url(#pw)"/>')
    specks = "".join(f'<rect x="{rnd.randrange(8, W - 8, 3)}" y="{rnd.randrange(8, H - 8, 3)}" width="3" '
                     f'height="3" fill="{rnd.choice(["#1a3a43", "#0a1418", "#17323a"])}"/>' for _ in range(110))
    s.append(f'<g shape-rendering="crispEdges" opacity=".8">{specks}</g>')
    s.append('<ellipse cx="420" cy="150" rx="190" ry="125" fill="url(#pool)"/>')
    for cx, cy, d in ((420, 150, 0), (420, 150, 4)):
        s.append(f'<ellipse class="ripple" style="animation-delay:{d}s" cx="{cx}" cy="{cy}" rx="150" ry="70" '
                 f'fill="none" stroke="{C["cream"]}" stroke-width="1" opacity="0"/>')
    b64 = base64.b64encode(gif.read_bytes()).decode()
    s.append(f'<image href="data:image/gif;base64,{b64}" x="292" y="22" width="256" height="256" '
             'style="image-rendering:pixelated;image-rendering:crisp-edges"/>')

    for (x, y, rx, ry, n, d) in ((26, 222, 9, 5, 0, 0), (110, 252, 5, 3, 1, 2.5),
                                 (742, 24, 9, 5, 1, 1.2), (690, 64, 5, 3, 0, 3.4)):
        s.append(f'<g class="bob" style="animation-delay:{d}s">'
                 f'{pixels(lily_pad(rx, ry, n), LILY_COLORS, x, y, 4)}</g>')
    s.append(f'<g class="bob">{pixels(LOTUS, LOTUS_COLORS, 50, 214, 4)}</g>')
    s.append(f'<g class="bob" style="animation-delay:1.2s">{pixels(LOTUS, LOTUS_COLORS, 764, 16, 4)}</g>')

    # left: what this is
    s.append(t(40, 80, "my koi", "silk", 12, C["gold"], spacing=2))
    s.append(t(40, 112, "redrawn every night", "vt323", 23, C["cream"]))
    s.append(t(40, 136, "from my GitHub activity", "vt323", 23, C["cream"]))
    s.append(t(40, 168, "it grows as I build", "vt323", 20, C["dim"]))
    # right: how it's read
    s.append(t(590, 116, "how to read it", "silk", 10, C["mist"], spacing=1.5))
    rows = [("languages", "its colors", C["koi"]), ("commits", "its size", C["gold"]),
            ("streaks", "its markings", C["lily"]), ("yesterday", "how it swims", C["sky"])]
    for i, (a, b_, col) in enumerate(rows):
        y = 144 + i * 26
        s.append(pixels(BLOOM, {"a": col, "y": C["cream"]}, 590, y - 11, 2))
        s.append(t(606, y, a, "vt323", 20, C["cream"]))
        s.append(t(696, y, "» " + b_, "vt323", 20, C["mist"]))

    s.append(f'<g clip-path="url(#pc)">{scanlines(W, H, RX)}</g>')
    s.append(pixel_corners(W, H))
    s.append(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="{RX}" fill="none" '
             f'stroke="{C["line2"]}" stroke-width="1.5"/>')
    write("koi-pond.svg", "".join(s))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    banner()
    about()
    focus()
    toolbox()
    divider("the pond", "div-koi.svg")
    divider("about", "div-about.svg")
    divider("pond log", "div-log.svg")
    divider("say hello", "div-hello.svg")
    button("email me", ENVELOPE, "btn-email.svg")
    button("linkedin", LINKEDIN, "btn-linkedin.svg")
    footer()
    koi_pond()