#!/usr/bin/env python3
"""Validate every icon set in icons/.

For each set:
  1. the five required files exist (svg, 3 drawables, 2 mipmap wirings)
  2. icon.svg is a 96-unit square with a stroke width
  3. the glyph stays inside Android's 66dp safe circle once the repo's
     mapping is applied (96 units -> 72dp: translate 18, scale 0.75)
  4. the tile colour is one of the eight suite colours
  5. white-on-tile contrast is at least 3:1 (WCAG non-text minimum)

With --weight it also reports ink coverage per set: stroke length x stroke width
divided by the glyph bounding box. Boundary radius alone hides visual weight —
two icons can sit inside the same safe circle and still read 2x heavier.

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


def ink_coverage(svg: str):
    """Stroke ink area / glyph bbox area, in percent. A rough but honest proxy
    for visual weight: it counts how much of the glyph box the ink fills."""
    sw = float(m.group(1)) if (m := re.search(r'stroke-width="([\d.]+)"', svg)) else 0.0
    length = 0.0
    xs, ys = [], []
    for d in re.findall(r'\sd="([^"]+)"', svg):
        path = parse_path(d)
        length += path.length()
        for seg in path:
            for i in range(33):
                pt = seg.point(i / 32)
                xs.append(pt.real)
                ys.append(pt.imag)
    for tag in re.findall(r"<rect[^>]*>", svg):
        if 'width="96"' in tag and 'height="96"' in tag:
            continue
        num = lambda k, dflt=0.0: float(m.group(1)) if (m := re.search(rf'\b{k}="([-\d.]+)"', tag)) else dflt
        x, y, w, h, rx = num("x"), num("y"), num("width"), num("height"), num("rx")
        if rx:
            d = (f"M{x+rx},{y} h{w-2*rx} a{rx},{rx} 0 0 1 {rx},{rx} v{h-2*rx} "
                 f"a{rx},{rx} 0 0 1 {-rx},{rx} h{-(w-2*rx)} a{rx},{rx} 0 0 1 {-rx},{-rx} "
                 f"v{-(h-2*rx)} a{rx},{rx} 0 0 1 {rx},{-rx} z")
        else:
            d = f"M{x},{y} h{w} v{h} h{-w} z"
        path = parse_path(d)
        length += path.length()
        for seg in path:
            for i in range(17):
                pt = seg.point(i / 16)
                xs.append(pt.real)
                ys.append(pt.imag)
    for tag in re.findall(r"<circle[^>]*>", svg):
        cx, cy, r = (float(re.search(rf'\b{k}="([-\d.]+)"', tag).group(1)) for k in ("cx", "cy", "r"))
        length += 2 * math.pi * r
        xs += [cx - r, cx + r]
        ys += [cy - r, cy + r]
    if not xs:
        return None
    w = (max(xs) - min(xs)) + sw
    h = (max(ys) - min(ys)) + sw
    if w <= 0 or h <= 0:
        return None
    return 100.0 * (length * sw) / (w * h)


def report_weight(sets) -> int:
    """Report ink coverage across all sets. Report-only by default: a heavy icon
    is a design judgement, not a build failure. --strict-weight makes it fail."""
    rows = []
    for folder in sets:
        svg_file = folder / "icon.svg"
        if not svg_file.exists():
            continue
        cov = ink_coverage(svg_file.read_text())
        if cov is not None:
            rows.append((folder.name, round(cov, 1)))
    if not rows:
        print("no measurable glyphs", file=sys.stderr)
        return 1
    values = sorted(v for _, v in rows)
    median = values[len(values) // 2]
    lo, hi = median * 0.65, median * 1.35
    print(f"\nink coverage (stroke ink / glyph box), {len(rows)} sets")
    print(f"{'set':15s}{'coverage':>9s}   verdict")
    outliers = 0
    for name, cov in sorted(rows, key=lambda r: -r[1]):
        if cov > hi:
            verdict, outliers = "heavy (outside band)", outliers + 1
        elif cov < lo:
            verdict, outliers = "light (outside band)", outliers + 1
        else:
            verdict = "in band"
        print(f"{name:15s}{cov:>8}%   {verdict}")
    print(f"\nmin {values[0]}% · median {median}% · max {values[-1]}% · "
          f"spread {values[-1] / values[0]:.2f}x")
    print(f"band {lo:.1f}%–{hi:.1f}% (±35% of median) · {outliers} outliers")
    print("Report-only: change an icon only after looking at it. Never auto-nudge.")
    return 1 if ("--strict-weight" in sys.argv and outliers) else 0


def main() -> int:
    if not ICONS.is_dir():
        print("no icons/ directory", file=sys.stderr)
        return 2
    quiet = "--quiet" in sys.argv or "--weight" in sys.argv
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
    if "--weight" in sys.argv:
        weight_fail = report_weight(sets)
        if weight_fail:
            return weight_fail
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
