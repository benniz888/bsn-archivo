# Brand and logo

## Pick: `Logo Options/logos-04.png` (blue-to-red gradient tile)
Why
- The gradient is the Puerto Rico flag palette (blue, white wash, red). It matches the flag-stripe indicator already used in the nav and the blue/red accents across the site.
- The orange ball and navy folder are the same in every option; only the tile differs. The orange and black tiles (03, 05, 07, 08) fight the orange ball or look off on the navy theme. 05 and 07 make the ball disappear into the tile.
- The mark reads "EL ARCHIVO" with no "BSN", so it survives the planned rename.
- 06 (folder only, no tile) is the fallback if a flat mark is ever needed; its navy body has weak contrast on the dark theme, so it is not the primary.

Known limits
- "EL ARCHIVO" is illegible below ~64px. That is fine: at small sizes the mark is the folder + ball shape. Do not try to make the arc text legible at 32px.
- The tile's left edge is a pale cream/white wash. On the light theme add a 1px outline using a border token so the tile does not dissolve into the page.

## Files already generated (in `assets/logo/`, from logos-04)
| File | Use |
|---|---|
| logo_mark_tile_1024.png | master, rounded tile, transparent corners |
| logo_mark_128.png / logo_mark_64.png | header mark |
| app_icon_1024_fullbleed.png | App Store / source for all icons (full-bleed square, no alpha: iOS applies its own rounding) |
| apple_touch_icon_180.png | `<link rel="apple-touch-icon">` (home screen on iPhone) |
| icon_192.png, icon_512.png | manifest `purpose: any` |
| icon_maskable_512.png | manifest `purpose: maskable` (art inside the 80% safe zone) |
| favicon.ico, favicon_32.png, favicon_16.png | browser tab |

Owner check before shipping: open `app_icon_1024_fullbleed.png` and `icon_maskable_512.png` and confirm the corners look clean (they were rebuilt by extending the gradient, not redrawn).

## Placement rules
- Desktop header (top-left, like Statmuse): mark (40px tall) + wordmark "BSN ARCHIVO" to its right. Wordmark text is live text, not part of the image.
- Phone header: mark only, no wordmark (as in Statmuse). The wordmark stays available to screen readers: the link keeps `aria-label="Inicio"` plus visible-hidden text of the site name.
- The mark links to Inicio. Minimum 44x44 hit area.
- Home-screen install on iPhone: `apple-touch-icon` 180, manifest icons 192/512/maskable, `theme-color` matches the header background in both themes.
- Replace the existing hand-drawn flag-stripe brand mark in the header and the rail logo (it was 32px, under 44px tap target).
- Splash screen (existing bouncing basketball) stays; check it does not show the old mark.

## Highlight color
Owner: the selected/active outline should use one of the site colors, not orange.
- Selected/active state: site blue (existing `--accent` blue used by "Diaria" / primary buttons).
- Focus ring: keep visible and >= 3:1, same blue (or white on blue backgrounds).
- Orange stays only for data accents (bars, sparklines, links?), not outlines. Decide link color in PHASE_61 and list the choice in `docs/strings_pending_phase61.md` as a design note for owner approval.

## Phone nav bug (seen in your screenshots)
- The flag-stripe indicator under the tabs stays on Inicio while you move between tabs. In the Equipos screenshot the bottom nav also highlights Inicio while the page is Equipos. So the active-tab state is not updating from the route (hash router). Fix: derive active tab from the current route on every route change, on load, and on back/forward; animate the indicator with `transform: translateX` only; respect `prefers-reduced-motion`.
- Header overlaps the page title on scroll (EQUIPOS is cut by the sticky header; a red line crosses it). Use `scroll-padding-top` / `scroll-margin-top` equal to the header height.
- Subnav pills clip at the right edge ("Desap"). Add edge fade and scroll-snap, and make sure the active pill scrolls into view.
- "Mi club" pill clips at 320px (already in backlog).
