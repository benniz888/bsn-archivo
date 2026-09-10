# Spec: PHASE_7 — visual redesign

A polish pass on the existing design system, not a re-theme. Structure /
density modelled on basketball-reference.com (its density, not its styling);
polish / motion modelled on apple.com; the BSN flag palette and "hardwood in
shadow" warm-dark ground stay as the foundation.

## [DECISION]

Owner-approved 2026-09-10 after the UI audit:

1. **Type: one family — Inter everywhere.** No separate display face. Headings
   lean on `font-weight:800` + negative tracking; big numerals add tighter
   tracking + tabular figures. The tricolor rule is now the sole identity
   device. (Barlow / Barlow Condensed dropped.)
2. **Density: auto-expand all folded sections on desktop ≥1120px**, keep the
   disclosure behaviour on mobile. (commit 2)
3. **Light mode: refinement pass** on the existing hand-built theme — firmer
   surfaces / gridlines, tint-alpha bump, softer shadows, per-crest legibility
   check, header `auto → light → dark` cycle. Not a rebuild. (commit 3)
4. **Phased rollout, 3 commits**, each independently reviewable, each green on
   `make verify` + `make test` + `make site`.

## [INTERFACES]

Everything lives in `app/bsn_archivo.html` (`<link>` + `<style>` + a few inline
`style=` strings in JS render code). `make site` mirrors to `web/index.html`;
`verify_web_data` byte-compares; `test_site_index_matches_shell` pins it.

### Token system (added to `:root`, commit 1)

- **Type scale** — 10 tokens, ratio ~1.20, base 15px:
  `--fs-3xs 11 · --fs-2xs 12 · --fs-xs 13 · --fs-sm 14 · --fs-base 15 ·
   --fs-md 18 · --fs-lg 22 · --fs-xl 27 · --fs-2xl clamp(30,5vw,40) ·
   --fs-num 31 · --fs-hero clamp(52,14vw,86)`. Plus `--lh-body 1.5`,
  `--lh-head 1.15`.
- **Spacing** — 4px base: `--sp-1 4 … --sp-9 96`.
- **Motion** (used from commit 2): `--ease cubic-bezier(.22,.8,.3,1)`,
  `--ease-io cubic-bezier(.4,0,.2,1)`, `--dur-fast 120 · --dur 200 ·
  --dur-slow 340`.

## [COMMITS]

### Commit 1 — tokens, Inter, type scale, spacing (DONE)

- `<link>` → Inter `wght@400;500;600;700;800` + italic 400, optical-size axis.
- `body` → Inter, `--fs-base` / `--lh-body`, `text-rendering:optimizeLegibility`.
- `h1–h4` → `font-family:inherit; font-weight:800; letter-spacing:-.02em;
  line-height:var(--lh-head)`.
- Big-numeral group (`.clock .n`, `.strip .n`, `.seriesrow .sc`, `.answer
  .abig`, `.readout .yr`, `.hubn`, `.hubhead`) → `letter-spacing:-.03em;
  font-feature-settings:"tnum" 1,"cv05" 1`.
- 23 `Barlow` / `Barlow Condensed` references removed (CSS + SVG crest/portrait
  fallback `<text>` + inline JS style strings).
- Structural spacing / type retokenised: `.panel`, `.phead`, `h2.big`,
  `h3.sec`, `h4.sub`, `.lede`, `.note`, `.card`, `.cards`, `nav.tabs button`,
  `.markname`, `.standhead h4`. Section rhythm → `--sp-6` between blocks.
- **No behaviour or layout-structure change** beyond the font swap and a looser
  vertical rhythm.

### Commit 2 — motion + density (pending)

`panel-enter` transition on every `showTab`; sliding tab underline; theme
cross-fade; sticky table header + first column; tighter data rows; zebra option
for long tables; desktop ≥1120px auto-expand of `foldSections()`.

### Commit 3 — light-mode refinement (pending)

`--raise`/`--line` firmer, tints 10–14%, softer `--shadow`; flatten decorative
gradients (`.answer .ahead`, `.primer`, `.seriesrow.win`); ~10 hardcoded hexes
in JS → tokens; header theme control → `auto/light/dark` cycle; per-crest
legibility pass on the light ground.

## [ALTERNATIVES_REJECTED]

- **Hybrid type (Inter + a condensed display face).** Considered and offered;
  owner chose the single family for a cleaner, more restrained result.
- **Removing folded sections everywhere.** Reverts a deliberate PHASE_6 IA
  decision and lengthens the mobile scroll. Kept on mobile, dropped on desktop.
- **Rebuilding the light palette.** The existing one is a considered
  non-inversion (flag blue at 1/10 luminance, red pulled down in L\*); refine,
  don't restart.
