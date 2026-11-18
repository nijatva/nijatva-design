# Wording

How Nijatva talks. Short, plain, and never louder than the job.

This is the source of truth for *what to write*. The strings themselves live in
`strings/common-en.xml` and `strings/common-hi.xml`, and eventually compile into
`nijatva-core` so apps inherit them instead of copying.

## Voice

- **Second person, present tense.** "Deletes the photo from this device", not
  "The photo will be deleted".
- **Say what happens, then stop.** One sentence beats two. No paragraph needs a
  third.
- **No marketing inside the app.** The website sells; the app works. An app
  screen never says "powerful", "seamless" or "best-in-class".
- **No exclamation marks.** Not one, anywhere.
- **No "please".** A permission prompt explains the reason; it does not beg.
- **Never blame the user.** "That file could not be opened" — not "You chose an
  invalid file".

## Case and punctuation

- **Sentence case everywhere**: "Delete this note", not "Delete This Note".
- No full stop on labels, buttons or headings. Full stops in body text.
- No ellipsis on buttons. "Saving…" is fine as a status, "Save…" is not.
- No ALL CAPS. If something needs emphasis, shorten the sentence instead.
- Buttons are verbs: "Delete", "Share", "Retry". Not "OK", not "Yes".

## Numbers, dates, money

- Latin digits (0-9) in the UI, in every language. Devanagari and other native
  numerals make versions, sizes and dates harder to scan.
- Dates: `18 November 2026`. Short form `18/11/2026`.
- Money: `₹1,499`. Lakh and crore in prose, never in a table.
- Sizes: `2.4 MB`. Storage: `1.2 GB of 64 GB`.
- Units: metric only.

## Terms we have decided

| Write | Not | Why |
|---|---|---|
| Settings | Preferences, Options, Config | One word for one screen |
| Delete | Remove | Remove implies it might come back; Delete does not |
| Trash | Recycle bin | Shorter, and it is what the button says |
| Folder | Directory | Directory is a programmer's word |
| Photo | Image, Picture | Photo is what people say |
| Sign in | Log in | Log in and log out is a coin flip; sign in is not |
| Offline | No internet | Offline is a state, not a fault |
| Permissions | Access rights | Shorter, and Android uses it |
| Theme | Appearance mode | Appearance is the screen; Theme is the setting |
| Accent colour | Primary colour | It is an accent, not a primary |

## Hindi and other Indian languages

- **Keep technical nouns in Latin script** where the Hindi word is obscure:
  `Wi-Fi`, `Bluetooth`, `PDF`, `APK`, `PIN`. Transliterating them into Devanagari
  makes them slower to read, not friendlier.
- **Translate the verb, not the noun.** "Delete" → "हटाएँ", but "Storage" stays
  closer to "संग्रहण" than a long paraphrase.
- **Avoid gendered verbs** where a neutral form exists. Prefer "आप कर सकते हैं"
  over constructions that assume a gender.
- **Text grows about 30%.** Never fix a button width. Let it wrap or shorten the
  English instead.
- **No string concatenation.** Use `<plurals>` and `%1$s`. "File " + name + "
  deleted" breaks in every language that puts the verb last.

## The states everyone forgets

- **Empty**: say what would be here and how to get it. "No notes yet. Write one
  with the button above." Never a bare "No data".
- **Error**: what failed, and what to do next. "The file could not be opened. It
  may have been moved." Not "Error 0x20".
- **Permission**: why it is needed, what breaks without it, and that it is
  optional when it is. "Camera access lets the scanner read a code. You can also
  type the text instead."
- **Loading**: a verb, not a noun. "Checking for updates…" beats "Loading…".

## Never

- Never claim a feature the app does not have.
- Never say "coming soon" inside a shipped app.
- Never ask for a permission the app does not use — the empty permission list is
  a feature, and it is on the website.
- Never add a rating prompt, a review nag, or a "tell your friends" card.
