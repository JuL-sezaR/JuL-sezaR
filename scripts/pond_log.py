"""Draws assets/pond-log.svg, the stats card, from public GitHub activity.

Runs nightly in .github/workflows/pond.yml with the workflow's built-in token:

    GH_TOKEN=... python3 scripts/pond_log.py --login JuL-sezaR

Standard library only. If GitHub can't be reached, an existing card is kept
as it is, so a bad night never leaves a broken image on the profile.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone

from pondkit import BLOOM, C, ROOT, font_css, pixels, t, text_width, window

OUT = ROOT / "assets" / "pond-log.svg"
API = "https://api.github.com/graphql"

HEAT = ["#15303a", "#1d4a4c", "#2c6e5f", "#5c9f74", C["gold"]]  # still water → blooming


# ------------------------------------------------------------------ fetch ---
def gql(query: str, variables: dict, token: str) -> dict:
    req = urllib.request.Request(
        API, data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "pond-log"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise RuntimeError(body["errors"][0].get("message", body["errors"]))
    return body["data"]


REPOS_Q = """
query($login:String!, $cursor:String) {
  user(login:$login) {
    createdAt
    followers { totalCount }
    repositories(first:100, after:$cursor, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) { edges { size node { name color } } }
      }
    }
  }
}"""


def fetch(login: str, token: str, today: date) -> dict:
    stars, langs, colors, cursor = 0, Counter(), {}, None
    while True:
        user = gql(REPOS_Q, {"login": login, "cursor": cursor}, token)["user"]
        repos = user["repositories"]
        for node in repos["nodes"]:
            stars += node["stargazerCount"]
            for e in node["languages"]["edges"]:
                langs[e["node"]["name"]] += e["size"]
                colors[e["node"]["name"]] = e["node"]["color"] or C["mist"]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]

    created = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00")).date()
    years = range(created.year, today.year + 1)
    parts = []
    for y in years:
        end = f"{today.isoformat()}T23:59:59Z" if y == today.year else f"{y}-12-31T23:59:59Z"
        parts.append(f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{end}") '
                     "{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }")
    data = gql("query($login:String!){ user(login:$login){ " + " ".join(parts) + " } }",
               {"login": login}, token)["user"]
    days = {}
    for y in years:
        for w in data[f"y{y}"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[date.fromisoformat(d["date"])] = d["contributionCount"]

    return {"days": days, "stars": stars, "repos": repos["totalCount"],
            "followers": user["followers"]["totalCount"], "created": created,
            "langs": langs, "colors": colors}


def demo(today: date) -> dict:
    """Plausible made-up numbers, only for previewing the card locally."""
    rnd = random.Random(4)
    days = {}
    for i in range(700):
        d = today - timedelta(days=i)
        busy = 0.55 + 0.35 * (d.weekday() < 5)
        days[d] = rnd.choice([0, 1, 2, 3, 5, 8]) if rnd.random() < busy else 0
    for i in range(1, 9):
        days[today - timedelta(days=i)] = rnd.randint(1, 6)
    return {"days": days, "stars": 23, "repos": 14, "followers": 31,
            "created": today - timedelta(days=700),
            "langs": Counter({"Python": 61, "C++": 22, "Java": 9, "Jupyter Notebook": 6, "Shell": 2}),
            "colors": {"Python": "#3572A5", "C++": "#f34b7d", "Java": "#b07219",
                       "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051"}}


# ------------------------------------------------------------------ stats ---
def streaks(days: dict, today: date):
    """Current and longest runs of days with at least one contribution.
    Today still counts as unbroken while it's young: a zero today only breaks
    the streak once the day is over."""
    cur_start = None
    d = today if days.get(today, 0) else today - timedelta(days=1)
    n = 0
    while days.get(d, 0) > 0:
        n, cur_start = n + 1, d
        d -= timedelta(days=1)
    best, best_span, run, run_start = 0, None, 0, None
    for d in sorted(k for k in days if k <= today):
        if days[d] > 0:
            if run == 0:
                run_start = d
            run += 1
            if run > best:
                best, best_span = run, (run_start, d)
        else:
            run = 0
    return n, cur_start, best, best_span


def fmt_day(d: date) -> str:
    return f"{d:%b} {d.day}"


def fmt_span(a: date, b: date) -> str:
    if a == b:
        return fmt_day(a)
    if a.year != b.year:
        return f"{a:%b %Y} – {b:%b %Y}"
    return f"{fmt_day(a)} – {fmt_day(b)}"


def soften(hex_color: str, amount: float = .18) -> str:
    """Nudge a language color toward lantern cream so it sits in the palette."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return C["mist"]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    cr, cg, cb = (int(C["cream"][i:i + 2], 16) for i in (1, 3, 5))
    mix = lambda a, c: round(a + (c - a) * amount)
    return f"#{mix(r, cr):02x}{mix(g, cg):02x}{mix(b, cb):02x}"


# ----------------------------------------------------------------- render ---
def tile(x, y, w, h, value, label, sub, color):
    return (f'<rect x="{x}" y="{y + 3}" width="{w}" height="{h}" rx="8" fill="{C["deep"]}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{C["panel"]}" stroke="{C["line2"]}"/>'
            + pixels(BLOOM, {"a": color, "y": C["cream"]}, x + 14, y + 14, 2)
            + t(x + 30, y + 23, label, "silk", 10, C["mist"], spacing=1.2)
            + t(x + 14, y + 60, value, "pixelify", 34, color)
            + t(x + 14, y + h - 10, sub, "vt323", 18, C["dim"]))


def render(s: dict | None, today: date) -> str:
    W, H = 840, 336
    body = []
    if s is None:
        vals = [("—", "contributions", "all time", C["koi"]), ("—", "current streak", "days", C["gold"]),
                ("—", "longest streak", "days", C["lily"]), ("—", "stars", "earned", C["sky"])]
    else:
        days = s["days"]
        total = sum(v for d, v in days.items() if d <= today)
        cur, cur_start, best, best_span = streaks(days, today)
        vals = [
            (f"{total:,}", "contributions", f"since {s['created']:%b %Y}", C["koi"]),
            (f"{cur}", "current streak", f"since {fmt_day(cur_start)}" if cur else "a quiet pond today", C["gold"]),
            (f"{best}", "longest streak", fmt_span(*best_span) if best else "the first ripple awaits", C["lily"]),
            (f"{s['stars']:,}", "stars", f"across {s['repos']} public repos", C["sky"]),
        ]
    tw, gap = 186, 12
    for i, (v, label, sub, col) in enumerate(vals):
        body.append(tile(24 + i * (tw + gap), 52, tw, 92, v, label, sub, col))

    # heatmap: the last 53 weeks, Sunday-first columns like GitHub's
    hx, hy, cell, cg = 24, 192, 9, 2
    body.append(t(hx, 178, "the last year, one lily per day", "silk", 10, C["mist"], spacing=1.2))
    start = today - timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
    nz = sorted(v for d, v in (s["days"].items() if s else []) if v > 0 and start <= d <= today)
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]
    level = lambda v: 0 if v <= 0 else 1 + sum(v > x for x in q)
    rects = []
    for i in range(53 * 7):
        d = start + timedelta(days=i)
        if d > today:
            break
        v = s["days"].get(d, 0) if s else 0
        col, row = divmod(i, 7)
        rects.append(f'<rect x="{hx + col * (cell + cg)}" y="{hy + row * (cell + cg)}" width="{cell}" '
                     f'height="{cell}" fill="{HEAT[min(level(v), 4)]}"><title>{d}: {v}</title></rect>')
    body.append(f'<g shape-rendering="crispEdges">{"".join(rects)}</g>')
    lx = hx + 53 * (cell + cg) - cg - text_width("more", "vt323", 16) - 6 - 5 * (cell + cg)
    body.append(t(lx - 6, 178, "less", "vt323", 16, C["dim"], "end"))
    body.append("".join(f'<rect x="{lx + i * (cell + cg)}" y="{170}" width="{cell}" height="{cell}" '
                        f'fill="{c}" shape-rendering="crispEdges"/>' for i, c in enumerate(HEAT)))
    body.append(t(lx + 5 * (cell + cg) + 4, 178, "more", "vt323", 16, C["dim"]))

    # languages
    lx0 = 640
    body.append(t(lx0, 178, "languages", "silk", 10, C["mist"], spacing=1.2))
    if s and s["langs"]:
        tot = sum(s["langs"].values())
        top = s["langs"].most_common(5)
        bar_x, bar_w = lx0, W - 24 - lx0
        acc = 0
        for name, size in top:
            w = bar_w * size / tot
            body.append(f'<rect x="{bar_x + acc:.1f}" y="192" width="{max(w, 1.5):.1f}" height="8" '
                        f'fill="{soften(s["colors"].get(name, C["mist"]))}" shape-rendering="crispEdges"/>')
            acc += w
        body.append(f'<rect x="{bar_x + acc:.1f}" y="192" width="{max(bar_w - acc, 0):.1f}" height="8" '
                    f'fill="{C["line"]}"/>')
        for i, (name, size) in enumerate(top):
            y = 224 + i * 17
            label = name if text_width(name, "vt323", 18) < 120 else name[:13] + "…"
            body.append(f'<rect x="{lx0}" y="{y - 9}" width="7" height="7" '
                        f'fill="{soften(s["colors"].get(name, C["mist"]))}"/>')
            body.append(t(lx0 + 14, y, label, "vt323", 18, C["cream"]))
            body.append(t(W - 24, y, f"{100 * size / tot:.1f}%", "vt323", 18, C["mist"], "end"))
    else:
        body.append(t(lx0, 226, "fills in after", "vt323", 18, C["dim"]))
        body.append(t(lx0, 244, "the first night", "vt323", 18, C["dim"]))

    body.append(f'<line x1="24" y1="{H - 34}" x2="{W - 24}" y2="{H - 34}" stroke="{C["line"]}" stroke-dasharray="3 5"/>')
    left = (f"{s['repos']} public repos · {s['followers']} followers" if s
            else "the pond log fills in after the first nightly run")
    body.append(t(24, H - 13, left, "vt323", 18, C["dim"]))
    body.append(t(W - 24, H - 13, f"last tended {today.isoformat()} · redrawn nightly", "vt323", 18, C["dim"], "end"))

    desc = ("GitHub activity: " + ", ".join(f"{label} {v}" for v, label, _, _ in vals)) if s else "GitHub activity"
    return window(W, H, "pond_log.txt", "".join(body), font_css("pixelify"), desc) + "</svg>\n"


# ------------------------------------------------------------------- main ---
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default=os.environ.get("GITHUB_REPOSITORY_OWNER"))
    ap.add_argument("--demo", action="store_true", help="render made-up numbers for a preview")
    ap.add_argument("--placeholder", action="store_true", help="render the empty card")
    ap.add_argument("--output", default=str(OUT))
    a = ap.parse_args()
    today = datetime.now(timezone.utc).date()

    if a.demo:
        stats = demo(today)
    elif a.placeholder:
        stats = None
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not (token and a.login):
            print("pond-log: needs --login and GH_TOKEN", file=sys.stderr)
            return 1
        try:
            stats = fetch(a.login, token, today)
        except Exception as e:  # keep yesterday's card rather than a broken one
            print(f"pond-log: couldn't reach GitHub ({e}); keeping the existing card", file=sys.stderr)
            return 0
    with open(a.output, "w") as f:
        f.write(render(stats, today))
    print(f"pond-log: wrote {a.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
