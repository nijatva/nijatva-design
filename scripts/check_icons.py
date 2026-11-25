#!/usr/bin/env python3
"""Validate every icon set in icons/.

For each set:
  1. the five required files exist (svg, 3 drawables, 2 mipmap wirings)
  2. icon.svg is a 96-unit square with a stroke width
  3. the glyph stays inside Android's 66dp safe circle once the repo's
     mapping is applied (96 units -> 72dp: translate 18, scale 0.75)
  4. the tile colour is one of the eight suite colours
  5. white-on-tile contrast is at least 3:1 (WCAG non-text minimum)

Needs: pip install svgpathtools

Usage: python3 scripts/check_icons.py [--quiet]
Exit 1 on any failure.
"""
import math
import re
import sys
from pathlib import Path

try:
    from svgpathtools import parse_path
except ImportError:
    print("pip install svgpathtools", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "icons"

# The eight suite tile colours (README: indigo, maroon, plum, teal, slate, olive, rust, green).
TILE_COLOURS = {
    "#262a5c": "indigo", "#6d2131": "maroon", "#43306b": "plum", "#14504a": "teal",
    "#333a52": "slate", "#4a4a1c": "olive", "#8a4b0f": "rust", "#1f5130": "green",
}
REQUIRED = [
    "res/drawable/ic_launcher_foreground.xml",
    "res/drawable/ic_launcher_background.xml",
    "res/drawable/ic_launcher_monochrome.xml",
    "res/mipmap-anydpi-v26/ic_launcher.xml",
    "res/mipmap-anydpi-v26/ic_launcher_round.xml",
]
SCALE, OFFSET, CENTRE = 0.75, 18.0, 54.0   # 96 units -> 72dp on a 108dp canvas
SAFE_RADIUS_DP = 33.0                       # 66dp safe circle
MIN_CONTRAST = 3.0


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in ch)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rounded_rect_points(x, y, w, h, rx, steps=24):
    rx = min(rx, w / 2, h / 2)
    pts = []
    corners = [
        (x + w - rx, y + rx, -90, 0), (x + w - rx, y + h - rx, 0, 90),
        (x + rx, y + h - rx, 90, 180), (x + rx, y + rx, 180, 270),
    ]
    for cx, cy, a0, a1 in corners:
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((cx + rx * math.cos(a), cy + rx * math.sin(a)))
    return pts


def glyph_points(svg: str):
    pts = []
    for d in re.findall(r'\sd="([^"]+)"', svg):
        for seg in parse_path(d):
            n = 2 if type(seg).__name__ == "Line" else 64
            for i in range(n + 1):
                p = seg.point(i / n)
                pts.append((p.real, p.imag))
    for tag in re.findall(r"<rect[^>]*>", svg):
        if 'width="96"' in tag and 'height="96"' in tag:
            continue                                    # the tile, not the glyph
        num = lambda k, dflt=0.0: float(m.group(1)) if (m := re.search(rf'\b{k}="([-\d.]+)"', tag)) else dflt
        pts += rounded_rect_points(num("x"), num("y"), num("width"), num("height"), num("rx"))
    for tag in re.findall(r"<circle[^>]*>", svg):
        cx, cy, r = (float(re.search(rf'\b{k}="([-\d.]+)"', tag).group(1)) for k in ("cx", "cy", "r"))
        pts += [(cx + r * math.cos(2 * math.pi * i / 64), cy + r * math.sin(2 * math.pi * i / 64)) for i in range(65)]
    return pts


def check_set(folder: Path):
    problems, info = [], {}
    svg_path = folder / "icon.svg"
    if not svg_path.exists():
        problems.append("icon.svg missing")
        return problems, info
    svg = svg_path.read_text()
    if 'viewBox="0 0 96 96"' not in svg:
        problems.append("icon.svg is not a 96x96 viewBox")
    sw = float(m.group(1)) if (m := re.search(r'stroke-width="([\d.]+)"', svg)) else 0.0
    if not sw:
        problems.append("icon.svg has no stroke-width (line-art expected)")
    for rel in REQUIRED:
        if not (folder / rel).exists():
            problems.append(f"missing {rel}")

    bg = folder / "res/drawable/ic_launcher_background.xml"
    if bg.exists():
        found = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", bg.read_text())}
        if found:
            colour = sorted(found)[0]
            info["tile"] = colour
            if colour not in TILE_COLOURS:
                problems.append(f"tile colour {colour} is outside the eight suite colours")
            else:
                cr = contrast("#ffffff", colour)
                info["contrast"] = round(cr, 2)
                if cr < MIN_CONTRAST:
                    problems.append(f"white glyph contrast {cr:.2f}:1 is below {MIN_CONTRAST}:1")

    pts = glyph_points(svg)
    if not pts:
        problems.append("no glyph geometry found in icon.svg")
    else:
        radius = max(math.hypot(x - CENTRE, y - CENTRE) for x, y in pts) * SCALE + sw / 2 * SCALE
        info["radius_dp"] = round(radius, 1)
        if radius > SAFE_RADIUS_DP:
            problems.append(f"glyph radius {radius:.1f}dp exceeds the 33dp safe circle")
    return problems, info


def main() -> int:
    if not ICONS.is_dir():
        print("no icons/ directory", file=sys.stderr)
        return 2
    quiet = "--quiet" in sys.argv
    sets = sorted(p for p in ICONS.iterdir() if p.is_dir())
    failures, radii = 0, []
    for folder in sets:
        problems, info = check_set(folder)
        if "radius_dp" in info:
            radii.append(info["radius_dp"])
        if problems:
            failures += 1
            print(f"FAIL {folder.name}")
            for p in problems:
                print(f"     - {p}")
        elif not quiet:
            print(f"ok   {folder.name:13s} r={info.get('radius_dp'):>5}dp  "
                  f"tile={info.get('tile')} ({TILE_COLOURS.get(info.get('tile'), '?')})  "
                  f"contrast={info.get('contrast')}:1")
    if radii:
        print(f"\nradius {min(radii)}–{max(radii)}dp (limit 33.0), "
              f"median {sorted(radii)[len(radii) // 2]}, spread {max(radii) / min(radii):.2f}x")
    print(f"{len(sets)} sets checked, {len(sets) - failures} clean, {failures} with problems")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
