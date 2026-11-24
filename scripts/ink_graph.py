"""Draws the contribution calendar as an ink-wash scene: a red brush sweeps across the weeks,
cuts down the ink yokai sitting on the busiest days, and leaves ink behind in each day it passes.

Standard library only. Needs a GitHub token in GITHUB_TOKEN (the Actions token is enough).
Run: python scripts/ink_graph.py <login>  ->  dist/ink-graph-light.svg, dist/ink-graph-dark.svg
     python scripts/ink_graph.py --sample  (random data, for trying the look offline)
"""

import json
import os
import random
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CELL, GAP, PAD = 11, 3, 20
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
CYCLE = 12  # seconds per loop
SWEEP = (6, 66)  # brush crosses the calendar between these percents of the loop

THEMES = {
    "light": {
        "paper": "#F4EFE3",
        "ink": ["#E7E0D0", "#CFC7B6", "#9A9384", "#57524A", "#1C1A17"],
        "yokai": "#1C1A17",
        "eye": "#F4EFE3",
        "red": "#B8352A",
        "text": "#6F695E",
    },
    "dark": {
        "paper": "#0D1117",
        "ink": ["#1A1F27", "#3A3833", "#6E685D", "#B3AC9D", "#ECE5D5"],
        "yokai": "#ECE5D5",
        "eye": "#0D1117",
        "red": "#D9483B",
        "text": "#8B8578",
    },
}


def fetch(login):
    query = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
      totalContributions weeks { contributionDays { contributionLevel contributionCount } } } } } }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[LEVELS.index(d["contributionLevel"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def sample():
    rng = random.Random(4)
    weeks = [[min(4, int(rng.expovariate(0.9))) for _ in range(7)] for _ in range(53)]
    return weeks, sum(sum(w) for w in weeks) * 3


def yokai(x, y, t):
    """A small ink blob with two eyes, centred in the cell at (x, y)."""
    cx, cy = x + CELL / 2, y + CELL / 2
    return (
        f'<circle cx="{cx}" cy="{cy}" r="5.6" fill="{t["yokai"]}"/>'
        f'<circle cx="{cx - 2}" cy="{cy - 0.8}" r="1.3" fill="{t["eye"]}"/>'
        f'<circle cx="{cx + 2}" cy="{cy - 0.8}" r="1.3" fill="{t["eye"]}"/>'
    )


def render(weeks, total, theme):
    t = THEMES[theme]
    cols = len(weeks)
    w = PAD * 2 + cols * (CELL + GAP) - GAP
    h = PAD * 2 + 7 * (CELL + GAP) - GAP + 22
    start, end = SWEEP

    def at(c):  # percent of the loop when the brush reaches column c
        return start + (end - start) * c / max(1, cols - 1)

    css, base, inked, foes = [], [], [], []
    for c, days in enumerate(weeks):
        p = at(c)
        css.append(
            f"@keyframes k{c}{{0%,{p:.2f}%{{opacity:0}}{p + 1:.2f}%,90%{{opacity:1}}97%,100%{{opacity:0}}}}"
            f".c{c}{{animation:k{c} {CYCLE}s linear infinite}}"
            f"@keyframes f{c}{{0%,{p:.2f}%{{opacity:1}}{p + 0.6:.2f}%,98%{{opacity:0}}100%{{opacity:1}}}}"
            f".f{c}{{animation:f{c} {CYCLE}s linear infinite}}"
        )
        x = PAD + c * (CELL + GAP)
        ink_cells, foe_cells = [], []
        for r, level in enumerate(days):
            y = PAD + r * (CELL + GAP)
            base.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["ink"][0]}"/>')
            if level:
                ink_cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["ink"][level]}"/>')
            if level == 4:
                foe_cells.append(yokai(x, y, t))
        if ink_cells:
            inked.append(f'<g class="c{c}">{"".join(ink_cells)}</g>')
        if foe_cells:
            foes.append(f'<g class="f{c}">{"".join(foe_cells)}</g>')

    grid_h = 7 * (CELL + GAP) - GAP
    x0, x1 = PAD - 14, PAD + (cols - 1) * (CELL + GAP) + CELL + 4
    css.append(
        f"@keyframes brush{{0%,{start - 1}%{{transform:translateX({x0}px);opacity:0}}{start}%{{opacity:1}}"
        f"{end}%{{transform:translateX({x1}px);opacity:1}}{end + 3}%,100%{{transform:translateX({x1}px);opacity:0}}}}"
        f".brush{{animation:brush {CYCLE}s cubic-bezier(.45,0,.55,1) infinite}}"
    )
    label = f"{total} contributions in the last year · each one an ink stroke"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
<style>{"".join(css)}</style>
<rect width="{w}" height="{h}" rx="12" fill="{t["paper"]}"/>
{"".join(base)}
{"".join(inked)}
{"".join(foes)}
<g class="brush">
  <path d="M-4 {PAD - 8} C 3 {PAD + grid_h * 0.3} 1 {PAD + grid_h * 0.7} 6 {PAD + grid_h + 8}" stroke="{t["red"]}" stroke-width="5" stroke-linecap="round" fill="none" opacity=".9"/>
  <path d="M-10 {PAD - 4} C -6 {PAD + grid_h * 0.4} -8 {PAD + grid_h * 0.6} -4 {PAD + grid_h + 4}" stroke="{t["red"]}" stroke-width="1.6" stroke-linecap="round" fill="none" opacity=".45"/>
</g>
<text x="{PAD}" y="{h - 12}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="11" fill="{t["text"]}">{label}</text>
</svg>
"""


if __name__ == "__main__":
    weeks, total = sample() if sys.argv[1:] == ["--sample"] else fetch(sys.argv[1])
    out_dir = ROOT / "dist"
    out_dir.mkdir(exist_ok=True)
    for theme in THEMES:
        out = out_dir / f"ink-graph-{theme}.svg"
        out.write_text(render(weeks, total, theme))
        print(out, out.stat().st_size, "bytes")
