"""Builds the animated ink-wash header: a brush slash reveals "WINTER", then a red seal stamps down.

Text is turned into SVG paths, so the header needs no web font.
Needs fontTools and, in fonts/: PatrickHand-Regular.ttf and Yomogi-Regular.ttf (both SIL OFL).
Run: python scripts/gen_header.py  ->  assets/header-light.svg, assets/header-dark.svg
"""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 320


def text_path(font_file, text, size, x, baseline, tracking=0.0):
    """SVG path data for `text` set at `size` px, starting at x on `baseline`; returns (d, width)."""
    font = TTFont(ROOT / "fonts" / font_file)
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(glyphs)
    cursor = x
    for ch in text:
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
        cursor += glyphs[name].width * scale + tracking
    return pen.getCommands(), cursor - x - tracking


def header(theme):
    paper, ink, wash, red = {
        "light": ("#F4EFE3", "#1C1A17", "#1C1A17", "#B8352A"),
        "dark": ("#0D1117", "#ECE5D5", "#8B8578", "#D9483B"),
    }[theme]

    word, word_w = text_path("PatrickHand-Regular.ttf", "WINTER", 150, 0, 0, tracking=10)
    word_x = (W - word_w) / 2 - 40
    sub, sub_w = text_path("PatrickHand-Regular.ttf", "indie games & tiny tools · Việt Nam", 26, 0, 0, tracking=1)
    seal, _ = text_path("Yomogi-Regular.ttf", "冬", 58, 0, 0)
    seal_x = word_x + word_w + 36

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Winter">
<style>
  .reveal {{ animation: reveal .55s cubic-bezier(.6,0,.3,1) .45s both; }}
  .slash {{ animation: slash .4s cubic-bezier(.7,0,.2,1) .2s both; }}
  .slash-fade {{ animation: fade 1.2s ease-out 1.1s both; }}
  .dot {{ transform-box: fill-box; transform-origin: center; animation: pop .35s ease-out both; }}
  .seal {{ transform-box: fill-box; transform-origin: center; animation: stamp .3s cubic-bezier(.3,1.6,.5,1) 1.15s both; }}
  .sub {{ animation: rise .6s ease-out 1.35s both; }}
  @keyframes reveal {{ from {{ width: 0; }} to {{ width: {W}px; }} }}
  @keyframes slash {{ from {{ width: 0; }} to {{ width: {W}px; }} }}
  @keyframes fade {{ to {{ opacity: .32; }} }}
  @keyframes pop {{ from {{ transform: scale(0); }} }}
  @keyframes stamp {{ from {{ transform: scale(1.8) rotate(-8deg); opacity: 0; }} }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} }}
</style>
<defs>
  <clipPath id="word-clip"><rect class="reveal" x="0" y="0" height="{H}" width="{W}"/></clipPath>
  <clipPath id="slash-clip"><rect class="slash" x="0" y="0" height="{H}" width="{W}"/></clipPath>
  <filter id="rough"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="7"/>
    <feDisplacementMap in="SourceGraphic" scale="5"/></filter>
</defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<rect width="{W}" height="{H}" rx="14" fill="{paper}"/>
<g clip-path="url(#card)"><g fill="{wash}" filter="url(#rough)">
  <path opacity=".06" d="M0 250 C120 190 190 150 280 175 C360 120 430 110 520 170 C600 140 650 160 720 200 C820 120 930 100 1040 170 C1110 150 1160 170 1200 190 V360 H0Z"/>
  <path opacity=".09" d="M0 285 C140 240 260 220 380 250 C520 215 640 230 760 262 C900 230 1040 235 1200 260 V360 H0Z"/>
</g></g>
<g clip-path="url(#slash-clip)">
  <path class="slash-fade" fill="{ink}" filter="url(#rough)"
    d="M70 232 C330 168 640 120 1130 54 C1140 53 1142 60 1131 63 C700 132 380 188 82 244 C60 248 52 237 70 232Z"/>
</g>
<g fill="{ink}" filter="url(#rough)">
  <circle class="dot" style="animation-delay:.55s" cx="1150" cy="44" r="6"/>
  <circle class="dot" style="animation-delay:.6s" cx="1168" cy="62" r="3.5"/>
  <circle class="dot" style="animation-delay:.62s" cx="1124" cy="34" r="2.5"/>
  <circle class="dot" style="animation-delay:.66s" cx="1176" cy="38" r="2"/>
</g>
<g clip-path="url(#word-clip)">
  <path fill="{ink}" transform="translate({word_x:.1f} 205)" d="{word}"/>
</g>
<g class="seal">
  <rect x="{seal_x:.1f}" y="96" width="78" height="78" rx="9" fill="{red}" filter="url(#rough)"/>
  <path fill="{paper}" transform="translate({seal_x + 10:.1f} 157)" d="{seal}"/>
</g>
<path class="sub" fill="{ink}" opacity=".72" transform="translate({(W - sub_w) / 2:.1f} 262)" d="{sub}"/>
</svg>
"""


if __name__ == "__main__":
    for theme in ("light", "dark"):
        out = ROOT / "assets" / f"header-{theme}.svg"
        out.write_text(header(theme))
        print(out, out.stat().st_size, "bytes")
