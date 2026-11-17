# nijatva-design

The icons and templates that keep thirty apps looking like one suite.

## What is here

```
icons/<app>/icon.svg                        the 96px source, for the site and store listings
icons/<app>/res/drawable/ic_launcher_foreground.xml   the glyph, white, inside the safe zone
icons/<app>/res/drawable/ic_launcher_background.xml   the tile colour
icons/<app>/res/drawable/ic_launcher_monochrome.xml   the same glyph, for Android 13 themed icons
icons/<app>/res/mipmap-anydpi-v26/ic_launcher.xml     adaptive-icon wiring
icons/<app>/res/mipmap-anydpi-v26/ic_launcher_round.xml
```

Thirty apps: the twenty-four in the suite, plus Appstore, Photos, Video Player,
Browser Mini X, Photo Editor and Web Store.

## Using one in an app

Copy the four `res/` files into the app module, keeping the paths:

```
app/src/main/res/drawable/ic_launcher_foreground.xml
app/src/main/res/drawable/ic_launcher_background.xml
app/src/main/res/drawable/ic_launcher_monochrome.xml
app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml
app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml
```

Then in `AndroidManifest.xml`:

```xml
<application
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round"
    ... >
```

**No PNGs are needed.** Every app in the suite has `minSdk 26`, and adaptive icons
arrive with API 26. Shipping five densities of PNG alongside them is weight for
nothing.

## The design rules

- One tile geometry: a rounded square, 96 units, 24 unit corner radius.
- One stroke weight: 5 units, round caps and joins, white on the tile colour.
- Eight tile colours, so the suite reads as a family without every icon looking
  the same: indigo, rust, green, teal, maroon, slate, plum, olive.
- The glyph sits inside the 72dp safe zone, so no launcher mask can clip it.
- A monochrome layer is included, so themed icons work on Android 13 and later.

## Regenerating

The sources come from the website's icon set (`nijatva/nijatva.github.io`,
`assets/icons/`). The converter lives with the site; ask there rather than
hand-editing the vectors here.

## Licence

Apache-2.0 for the code. The name "Nijatva" and these icons are not covered by
that licence — a fork must use its own name and its own icon.
