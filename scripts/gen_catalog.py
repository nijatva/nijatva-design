#!/usr/bin/env python3
"""Generate catalog.html — a visual index of every icon set, from the SVGs.

No PNGs, no screenshots: the SVGs are inlined, so the page is self-contained and
regenerates in a second. Run after changing an icon.

Usage: python3 scripts/gen_catalog.py [output.html]
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "icons"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "catalog.html"

TILE_NAMES = {
    "#262a5c": "indigo", "#6d2131": "maroon", "#43306b": "plum", "#14504a": "teal",
    "#333a52": "slate", "#4a4a1c": "olive", "#8a4b0f": "rust", "#1f5130": "green",
}


def inline(svg: str, mono: bool) -> str:
    body = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    body = re.sub(r'<rect width="96" height="96"[^>]*/>', "", body) if mono else body
    if mono:
        body = body.replace('stroke="#ffffff"', 'stroke="#f2f2f2"')
    body = re.sub(r'\s(width|height|role|aria-label)="[^"]*"', "", body)
    return f'<svg viewBox="0 0 96 96" class="icon{" mono" if mono else ""}">{body}</svg>'


def main() -> int:
    sets = sorted(p for p in ICONS.iterdir() if p.is_dir())
    cards = []
    for folder in sets:
        svg_file = folder / "icon.svg"
        if not svg_file.exists():
            continue
        svg = svg_file.read_text()
        bg = folder / "res/drawable/ic_launcher_background.xml"
        colour = (re.findall(r"#[0-9a-fA-F]{6}", bg.read_text())[0].lower() if bg.exists() else "#000000")
        complete = all((folder / p).exists() for p in (
            "res/drawable/ic_launcher_foreground.xml",
            "res/drawable/ic_launcher_background.xml",
            "res/drawable/ic_launcher_monochrome.xml",
            "res/mipmap-anydpi-v26/ic_launcher.xml",
            "res/mipmap-anydpi-v26/ic_launcher_round.xml",
        ))
        cards.append(f"""
    <article class="card">
      <div class="pair">
        <div class="tile">{inline(svg, False)}</div>
        <div class="tile dark">{inline(svg, True)}</div>
      </div>
      <h3>{html.escape(folder.name)}</h3>
      <p class="meta"><span class="dot" style="background:{colour}"></span>{colour} · {TILE_NAMES.get(colour, 'off-palette')}</p>
      <p class="meta">{'5/5 files' if complete else 'incomplete'} · {'monochrome ok' if (folder / 'res/drawable/ic_launcher_monochrome.xml').exists() else 'no monochrome'}</p>
    </article>""")

    OUT.write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nijatva icon catalog — {len(cards)} sets</title>
<style>
  :root{{--bg:#0a0a0a;--surface:#111;--border:#1e1e1e;--text:#f2f2f2;--dim:#9a9a9a;--accent:#c2664b}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font:14px/1.5 "DM Sans",-apple-system,sans-serif;padding:40px 24px 64px}}
  header{{max-width:1180px;margin:0 auto 28px}}
  h1{{font-size:26px;font-weight:500;letter-spacing:-.02em}}
  h1 span{{color:var(--dim);font-weight:400}}
  .lede{{color:var(--dim);margin-top:8px;font-size:13px;max-width:70ch}}
  .grid{{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(196px,1fr));gap:14px}}
  .card{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px}}
  .pair{{display:flex;gap:8px}}
  .tile{{flex:1;border-radius:10px;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:6px;background:#000}}
  .tile.dark{{background:#080808;border:1px solid #1a1a1a}}
  .icon{{width:100%;height:auto;display:block}}
  h3{{font-size:13px;font-weight:500;margin-top:10px;letter-spacing:.01em}}
  .meta{{font:10.5px/1.6 "Fira Code",ui-monospace,monospace;color:var(--dim);display:flex;align-items:center;gap:6px}}
  .dot{{width:7px;height:7px;border-radius:2px;display:inline-block}}
  footer{{max-width:1180px;margin:34px auto 0;color:var(--dim);font:11px "Fira Code",monospace}}
</style></head><body>
<header>
  <h1>Nijatva icon catalog <span>· {len(cards)} sets</span></h1>
  <p class="lede">Left: the icon as a launcher draws it. Right: the monochrome layer on black, as Android 13 themed icons use it.
  Generated from <code>icons/*/icon.svg</code> by <code>scripts/gen_catalog.py</code> — no PNGs, no screenshots.</p>
</header>
<div class="grid">{''.join(cards)}
</div>
<footer>Nijatva · design sources · generated {len(cards)} sets · Apache-2.0 code, name and icons excluded</footer>
</body></html>
""")
    print(f"wrote {OUT} ({len(cards)} sets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
