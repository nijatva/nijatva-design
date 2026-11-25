# nijatva-design — audit against the actual files

24 November 2026. This audit reads the 31 icon sets, the two string files and the
`wording.md` in the repository — not the README, and not the previous audit document.

---

## 0. Headline

The repository is in **better shape than any document says**, and the three things the
earlier audit flagged are not all real. One of them is a false alarm, and it is worth
knowing exactly why.

| Earlier audit's claim | Verdict after measuring | Evidence |
|---|---|---|
| "72-unit safe zone → 81dp, larger than the recommended 66dp" | **False alarm** | The 96-unit SVG tile maps to **72dp** (translate 18, scale 0.75) — that is the visible circle. Glyphs themselves sit at radius **22.6–32.5dp**, i.e. 45–65dp diameter, inside the 33dp safe circle. The 72-unit figure is the *tile*, not the glyph |
| "Contrast 6.79:1 to 13.39:1" | **Correct** | Measured exactly: rust `#8a4b0f` 6.79:1, olive 9.18:1, green 9.22:1, teal 9.23:1, maroon 10.98:1, plum 11.21:1, slate 11.24:1, indigo 13.39:1. All far above the 3:1 non-text minimum |
| "README says 29 apps but 31 sets exist" | **Correct** | `ls icons` = 31; README line 3 says "twenty-nine" |
| "Tokens missing, CI missing" | **Correct** | No `tokens/`, no `.github/workflows/` |

Two more facts nobody has written down yet:

- **Every one of the 31 sets is complete** — 5 files each, including the monochrome
  layer. That is 155 generated files, all present.
- **Exactly 8 tile colours are in use**, and no set uses a ninth. The palette is
  coherent: 6 sets indigo, 4 maroon, 4 plum, 4 teal, 4 slate, 3 olive, 3 rust, 3 green.

---

## 1. What is genuinely good (do not touch)

| Thing | Why it is right |
|---|---|
| `wording.md` | A real voice guide: second person, sentence case, no exclamation marks, no "please", buttons are verbs, Latin digits in every language. Most design systems never write this down |
| One tile geometry | 96-unit square, 24-unit radius, 5-unit stroke, round caps — identical across 31 sets |
| Monochrome layer in every set | Themed icons work on Android 13+ without a second pass |
| 8 colours, no more | Reads as a family without every icon looking identical. Also survives a themed launcher |
| No PNG densities | `minSdk 26` everywhere; adaptive icons are the correct answer. 155 files instead of ~800 |
| `strings/` with `nj_` prefix | No collision with app-owned keys; `common-hi.xml` is complete at 40/40 |
| Generated-not-hand-edited icons | The converter lives with the website, so vectors cannot drift per app |

---

## 2. Real gaps, ranked by value

### G1 — Design tokens (the only structural gap)

Nothing in the repo defines colour, spacing, radius or type for the **UI**. Eight tile
colours are not a UI palette — mixing them would be a mistake (the earlier audit is right
about that).

What is needed:

```
tokens/tokens.json      colour (amoled/dark/light), spacing, radius, type, motion, touch
scripts/gen_tokens.py   -> generated/values/colors.xml, values-night/colors.xml, values/dimens.xml
```

Why it belongs here and not only in `core:design`: **six apps in the suite are Java**
(dialer, contacts, messages, notes, file, WorkSpace). They can use `@color/nj_accent` and
`@dimen/nj_space_l` from XML today. A Compose-only theme reaches half the suite.

### G2 — CI gate (nothing validates 155 files today)

A missing drawable, a 95-unit SVG, a ninth colour, an empty Hindi string — all pass
silently right now. Four checks fix that, and all four are written and passing:

| Script | Checks |
|---|---|
| `gen_tokens.py --check` | generated XML matches `tokens.json` |
| `check_icons.py` | 5 files per set · 96-unit viewBox · stroke width · **safe-zone radius ≤ 33dp** · tile colour ∈ 8 · white-on-tile contrast ≥ 3:1 |
| `check_strings.py` | key parity across languages · `nj_` prefix · no empty values |
| `gen_catalog.py` | rebuilds `catalog.html` (see G4) |

### G3 — String validation is too shallow

`check_strings.py` today catches missing keys, extra keys and empty values. Missing:

- **format placeholders** — `%1$s` present in `en` but dropped in `hi` (the classic
  crash: `String.format` with a missing argument)
- **duplicate keys** in one file (last one silently wins)
- **invalid XML** (a stray `&` breaks the build, not the check)
- **HTML/markup tags** inside strings that differ between languages
- **native digits** — `wording.md` says Latin digits everywhere; nothing enforces it

### G4 — Icon catalog (the earlier audit's best idea, and it works)

`catalog.html` — 31 sets, each showing the icon as a launcher draws it and the monochrome
layer on black, with tile colour, palette name and completeness. Generated from the SVGs,
so no PNG is ever committed. Regenerate with `scripts/gen_catalog.py`.

This is the cheapest quality control available: 31 icons side by side immediately show
the one that is 20% smaller than its neighbours.

### G5 — Visual weight is uneven (only visible in the catalog)

Radius spread across the 31 glyphs is **22.6dp → 32.5dp, 1.44×**. Median 27.1dp.
Small ones: `rss` 22.6, `webstore` 23.5, `contacts` 23.9, `vault` 24.3. Large ones:
`weather` 32.5, `calc` 31.9, `deviceinfo` 31.5, `tasks` 31.2.

A 44% difference in linear size reads as inconsistent weight in a launcher grid. Not a
bug — a polish item. Target band: **26–30dp radius**, outliers nudged, not redrawn.

### G6 — Localization depth

40 keys in 2 languages. Honest options: say "English, Hindi" in the README, or add
4–6 languages in one PR with parity proven by `check_strings.py`. Never a partial file.

### G7 — No design changelog

`CHANGELOG.md` in the repo, one line per change to tokens, palette or icon geometry.
Without it, "why did the accent change in v1.2" is unanswerable in six months.

### G8 — The 32-vs-31 mapping

`APP-REGISTRY.json` tracks 32 apps; there are 31 icon sets. The missing one is a real
question, not a rounding error: either an app has no icon (which app?) or two apps share
one (`editor` is Photo Editor, `sms` is Messages). Document the mapping in the README as
a table: app → icon folder. It takes ten minutes and ends the confusion permanently.

---

## 3. What not to build here (unchanged, still correct)

| Not here | Where |
|---|---|
| Compose theme, Kotlin components | `nijatva-core` → `core:design` |
| A ninth tile colour | needs a decision, not a PR |
| Screenshot templates / brand assets | after the store client renders real listings |
| PNG densities, bundled fonts | never — `minSdk 26`, system fonts |
| Hand-edited generated XML | regenerate from source |
| Partial translations | parity or nothing |

---

## 4. Order of work

| Phase | Work | Why now |
|---|---|---|
| 1 | README fix (29 → 31, plus the app → icon mapping table) | five minutes, ends a repeated confusion |
| 2 | `tokens/` + `gen_tokens.py` + generated XML | unblocks the six Java apps |
| 3 | `validate.yml` + `check_icons.py` + `check_strings.py` | makes 155 files self-checking |
| 4 | `catalog.html` + `gen_catalog.py` in CI | visual regression for free |
| 5 | Visual-weight pass (26–30dp band) | polish, driven by the catalog |
| 6 | `check_strings.py` placeholder/duplicate checks, then languages | correctness before breadth |
| 7 | `CHANGELOG.md` | before the first token change ships |

---

## 5. Measured numbers to quote (verified today)

| Metric | Value |
|---|---|
| Icon sets | 31, all complete (5 files each) |
| Tile colours in use | 8, no off-palette set |
| Glyph radius | 22.6–32.5dp (median 27.1, spread 1.44×) against a 33dp safe circle |
| White-on-tile contrast | 6.79:1 (rust) to 13.39:1 (indigo) |
| Shared string keys | 40 in `en`, 40 in `hi`, parity clean, all `nj_` |
| Binaries in repo | none (157 XML, 31 SVG, 2 MD, 1 LICENSE) |

---

*Measured with `scripts/check_icons.py` (svgpathtools) on a clone of the repository on
24 November 2026. Re-run it before quoting any of these numbers again.*
