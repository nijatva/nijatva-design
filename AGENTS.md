# AGENTS.md — nijatva-design

Paste this file at the repo root. It is the standing instruction for any coding agent
(Claude Code, Cursor, Copilot, ChatGPT) working in this repository.

**Verified: 24 November 2026** — by reading the repository, not the README.

---

## 1. What this repository is for

One job: **hold the sources that make 31 apps look like one suite** — icon sources and
generated Android icon resources, the design tokens, and the shared wording/strings.

It is **not** an Android library. Nothing here compiles into an app. Apps copy the
`res/` files in, or (later) depend on `core:design`, which reads the same values.

```
nijatva-design            what the suite looks like and how it talks
nijatva-core              the code that implements it (:signature today, core:design later)
nijatva-suite             the registry and policies that decide what exists
```

**This repo decides the look. Core implements it. Never both in one place.**

---

## 2. Verified state — 24 November 2026

| Area | Reality |
|---|---|
| Icon sets | **31** — `appmanager, appstore, browser, calc, calendar, camera, clock, contacts, deviceinfo, dialer, editor, expenses, files, gallery, keyboard, launcher, minix, music, notes, pdf, photos, qr, recorder, rss, sms, tasks, translate, vault, video, weather, webstore` |
| Files per set | 5 required: `icon.svg`, `res/drawable/ic_launcher_{foreground,background,monochrome}.xml`, `res/mipmap-anydpi-v26/ic_launcher{,_round}.xml` — **all 31 sets are complete** |
| Tile colours | exactly **8** in use: `#262a5c` indigo, `#6d2131` maroon, `#43306b` plum, `#14504a` teal, `#333a52` slate, `#4a4a1c` olive, `#8a4b0f` rust, `#1f5130` green |
| Shared strings | `strings/common-en.xml` + `common-hi.xml` — **40 keys each, parity clean**, every key prefixed `nj_` |
| Wording | `wording.md` — voice, case, numbers, decided terms. Good; treat as law |
| Tokens (colour/spacing/type) | **Not present** — the one real gap |
| CI | **None** — nothing validates icons, strings or generated files |
| Templates, screenshot assets | **Not present, deliberately.** Deferred, not forgotten |
| Licence | Apache-2.0 for the code; the name "Nijatva" and the icons are excluded |

### README numbers are wrong (fix this first, it is a one-line change)

The README says *"The icons that keep twenty-nine apps looking like one suite. Thirty-one
sets live here"* — and then *"Thirty-one sets: the twenty-five in the suite, plus
Appstore, Photos, Video Player, Browser Mini X, Photo Editor and Web Store"* (25 + 6 = 31,
so that line is right, the first is not). It also calls `editor` "Photo Editor" and `sms`
"Messages" while the folder names are `editor` and `sms`.

Correct sentence: **"Thirty-one icon sets: one per app and store surface in the suite."**
Numbers that must match: `nijatva-suite/docs/APP-REGISTRY.json` says 32 apps tracked,
19 with a repository. If a count changes there, this README changes with it.

---

## 3. What to do, in order

### T1 — Add design tokens (the only real gap)

`tokens/tokens.json` is the single source for colour, spacing, radius, type, motion and
the 48dp touch minimum. `scripts/gen_tokens.py` generates:

```
generated/values/colors.xml           dark theme
generated/values-night/colors.xml     AMOLED (#000000 background)
generated/values/dimens.xml           spacing, radius, type sizes, touch minimum
```

Both files already exist in the package this prompt came with. Push them, run the
generator, commit the generated XML.

**Done when:** `python3 scripts/gen_tokens.py --check` passes, and a Java app can use
`@color/nj_accent` and `@dimen/nj_space_l` by copying the generated files — no Compose
required. That is the whole point: six apps in the suite are Java.

**Why tokens live here and not in `core:design`:** this repo holds *sources*; the Compose
theme in `core:design` will read the same values. A token added here reaches both the
Java and the Compose half of the suite. A token added in Compose code reaches only half.

### T2 — Add the CI gate

`.github/workflows/validate.yml` (in the package) runs three checks and fails the PR:

| Check | Catches |
|---|---|
| `gen_tokens.py --check` | generated XML drifting from `tokens.json` |
| `check_icons.py` | a missing drawable, an SVG that is not a 96-unit square, a tile colour outside the eight, a missing monochrome layer |
| `check_strings.py` | a key present in `en` but missing in `hi`, a key not prefixed `nj_`, an empty value |
| binary guard | an accidental `.png`, `.apk`, `.jar`, `.aar` |

**Done when:** the workflow is green on `main`, and a deliberately broken icon set fails
it on a throwaway branch. A gate nobody has seen fail is not a gate.

### T3 — Decide the language set for `strings/`

Only English and Hindi exist today. The suite claims India's 22 scheduled languages in
`nijatva-translate`, so "we support 22 languages" and "40 strings in 2 languages" cannot
both stay true in the same ecosystem.

Two honest options — pick one and write it in the README:

1. **Ship 2 languages now** and say so: "common strings: English, Hindi". Every app's own
   strings stay English-only until translated. Nothing is claimed that is not shipped.
2. **Add the next 4–6** (Bengali, Marathi, Telugu, Tamil, Gujarati, Kannada) through
   `translate_text`, then `check_strings.py` proves parity. Never add a language with a
   partial key set.

### T4 — Wire the tokens into `core:design` (cross-repo, later)

When `nijatva-core` gains a `core:design` module, it reads these values. That PR belongs
in `nijatva-core`; this repo only stops being copied by hand at that point.

### T5 — Do not build these yet

- **Screenshot templates / brand assets.** Deferred until the store client renders real
  listings. A template for a screen that does not exist is decoration.
- **PNG densities.** `minSdk 26` everywhere; adaptive icons are enough. Adding
  `mipmap-hdpi/xhdpi/...` is dead weight.
- **A bundled font.** System fonts (Roboto/Noto) only. A font file costs APK size and
  breaks Indian-script fallback.

---

## 4. What you cannot do in this repository — say so, do not fake it

| Cannot | Because | Where it actually happens |
|---|---|---|
| Write Compose theme or Kotlin components | This repo has no code and no Gradle build | `nijatva-core` → `core:design` |
| Build or install anything | No Android SDK, no APK here | each app repo, in CI |
| See an icon on a device, check launcher masking, verify themed icons | No emulator or phone | the owner, on a real device |
| Generate a new icon from scratch | The SVG sources come from `nijatva/nijatva.github.io` `assets/icons/` | that repo's converter |
| Publish, tag or release | This repo has no releases and needs none | — |
| Add a ninth tile colour | Eight colours keep the family coherent | needs an explicit decision, not a PR |
| Read another repo's files | Only what is in this clone | ask for the path or the clone |

---

## 5. Rules (a PR that breaks one of these is rejected)

1. **Generated files are never hand-edited.** `generated/**` comes from `tokens.json`;
   the icon `res/` files come from `icon.svg`. Change the source, run the script.
2. **One tile geometry, one stroke weight.** 96-unit square, 24-unit corner radius,
   5-unit stroke, round caps and joins, glyph inside the 72dp safe zone.
3. **White glyph on a tile colour.** Never a gradient, never a photographic background,
   never text as the glyph.
4. **Every set keeps all five files**, including the monochrome layer — it is what makes
   Android 13 themed icons work.
5. **No binaries in git.** No PNG, APK, AAR, JAR, keystore.
6. **Strings:** sentence case, no exclamation marks, no "please", buttons are verbs,
   Latin digits in every language, `nj_` prefix on every key. `wording.md` is the law.
7. **Hindi is never partial.** A key added to `common-en.xml` lands in every other
   language in the same commit, or the PR fails CI.
8. **The licence note stays.** Apache-2.0 covers the code; the name and icons do not.

---

## 6. Verify before you claim anything

```bash
python3 scripts/gen_tokens.py --check      # tokens up to date
python3 scripts/check_icons.py             # 31 sets checked, 31 clean
python3 scripts/check_strings.py           # 2 languages, 40 keys each, clean
ls icons | wc -l                           # must equal the number the README claims
git ls-files | grep -Ei '\.(png|aar|apk|jar|jks|keystore)$'   # must print nothing
```

Current expected output: `31 sets checked, 31 clean, 0 with problems` and
`2 languages, keys per file: en=40, hi=40` / `clean`.

---

## 7. Question bank (paste these to audit the repo)

**Capability**
1. Can you add a new icon set end to end without the website's converter? If not, what is missing?
2. Can you change the accent colour across all 31 icons in one PR? What would break?
3. Can you verify that a themed (monochrome) icon actually renders on Android 13? What do you need?
4. Can you add Bengali strings without breaking the Hindi parity check?
5. Can you generate a Compose theme here? Why not?

**Audit**
6. How many icon sets exist, and how many are complete? Prove it, do not guess.
7. Which tile colours are in use, and does any set use a colour outside the eight?
8. Is any generated file out of sync with its source right now?
9. Which README sentence is factually wrong today?
10. Do `common-en.xml` and `common-hi.xml` have identical keys? Show the diff count.

**Improve**
11. What is the smallest change that lets a Java app use the suite palette without Compose?
12. Should tokens live in this repo or in `core:design`? Argue both, recommend one.
13. What breaks first if we add 6 more languages — the strings, the icons, or the CI?
14. Which three things in this repo are decoration and should be deleted?

**Traps**
15. "Add a PNG fallback for old devices." — No: `minSdk 26`, adaptive icons are enough.
16. "Put the Compose theme here, it is a design repo." — No: no Gradle build here; `core:design`.
17. "Just hand-edit the generated colors.xml, it is quicker." — No: regenerate from tokens.
18. "Add a ninth colour for the new app." — Not without a decision; eight keeps the family coherent.
19. "The README says 29 apps, so we have 29." — 31 sets exist; the README line is wrong.

---

## 8. Definition of done for any PR here

1. Sources changed, never the generated output.
2. `gen_tokens.py --check`, `check_icons.py`, `check_strings.py` all pass.
3. The README count still matches `ls icons | wc -l`.
4. No binary, no font, no ninth colour, no Compose code.
5. If a string was added, every language file has it.

---

*Nijatva is built in India. Icons and name are not covered by Apache-2.0.*
