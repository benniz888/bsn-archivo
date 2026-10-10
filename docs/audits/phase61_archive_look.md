# PHASE_61 step 2: "El Archivo" look (sample, not wired in)

Sample page: `docs/audits/phase61_archive_look_sample.html` (open it directly; add `?theme=light` or `?theme=dark` to force a theme, or use the toggle). Not linked from the site. Nothing under `web/` changed in this step.

Spec source: the "Design direction" table and "Shared folder component" line in `docs/specs/redesign_v3/05_page_specs.md`. The `frontend-design` skill is not installed in this environment, so I did not use it; the design follows the spec and the site's own tokens.

## The three pieces

**Folder.** One `<button>` holds the tab and the body top (so the whole head is the tap target, 44px or more), followed by a panel that expands under it. Variants: `azul`, `rojo`, neutral. Optional crest slot (a generic shield in the sample; real crests wait on the image-rights decision) and `--fld-accent`, a 4px spine in a club colour. Club colours must be marked "aproximados" on the club pages, as the Equipos spec says.

**Paper card.** Index-card look: ruled lines, a red header rule, a typed mono label in the top-left. The card is light in both themes, like real card stock, so text on it is one fixed pair. Label links ("drawer labels") reuse the paper style.

**Stamp.** Static, rotated 4 degrees, typed caps, double border. For `Sin fuente`, `Disputado`, `Aproximado`. It sits in the flow below the content; it never covers text. The sample showed that an overlapping stamp hid the title on a phone, so it was moved.

## Choices and why
- **Site blue and red only.** Folders are tints of the flag blue and red. Orange stays for live data; it never outlines anything here. Focus ring is the site's blue `--focus`.
- **One element per folder head.** Avoids a small tab being the only click target.
- **Mono label font is a system stack** (`ui-monospace, SF Mono, Menlo`), so no new web font and no new third-party request. Oswald and Inter stay the site fonts.
- **Open/close.** The panel appears instantly and its contents fade and slide in (opacity and transform, 220ms). Height is not animated, because only transform and opacity are allowed. Closing is instant.
- **Hover lift** is `translateY(-4px)` on closed folders only, with a separate shadow layer that fades (opacity). Hover only on devices that hover; touch gets none.
- **Motion rules:** transform and opacity only, 150 to 300ms (`--dur-fast` 150, `--dur` 220), ease-out (`cubic-bezier(.22,.8,.3,1)`, the site's `--ease`). Under `prefers-reduced-motion` the lift, the chevron turn, the panel entrance and the stamp-in all turn off.
- **No emoji.** Icons are inline SVG.
- **No fabricated data.** Every value in the sample is a dash or the word "ejemplo".

## Proposed tokens (new, prefixed)
| Token | Dark | Light |
|---|---|---|
| `--fld-azul-body / -tab / -edge` | #12306E / #1A44A0 / #5B93E8 | #E4EDFB / #C6DAF6 / #0F52B8 |
| `--fld-rojo-body / -tab / -edge` | #5E1019 / #8E1119 / #E8606B | #FBE6E8 / #F4C6CB / #C8121F |
| `--fld-slate-body / -tab / -edge` | #131E38 / #1E2C4C / #6F89BA | #FFFFFF / #E1E9F5 / #5A6C8E |
| `--fld-ink / -ink-2 / -tab-ink` | #EEF3FB / #C5D3EA / #FFFFFF | #0B1730 / #3C5177 / #0B1730 |
| `--paper / -ink / -ink-2 / -rule / -edge` | #E9EEF7 / #0B1730 / #3C5177 / #C3D2E8 / #9FB3D3 | #FFFFFF / same / same / same / #6D82A6 |
| `--paper-red` | #A3101C | #A3101C |
| `--stamp-rojo / --stamp-azul` (on page) | #FF8A93 / #8DB8FF | #A3101C / #0A3E90 |

## Contrast (computed, WCAG relative luminance; script `/tmp/bsn_harness_v2/contrast.py`)
Every text pair is 6.6:1 or better (target 4.5:1). Every graphic edge against the page is 3.5:1 or better (target 3:1). Focus ring against folder bodies: 3.79:1 (dark azul body), 4.05:1 (dark rojo body), 8:1 or more in light. The tightest results are the dark focus ring on the azul body (3.79) and the light paper edge (3.53). One failure was found and fixed during the build: the light paper edge was 2.32:1 and is now #6D82A6 (3.53:1). Dark-theme paper edge is 9.18:1.

## Verified
Chromium and WebKit, 390px and 1000px, dark and light: no horizontal overflow, no console errors, every button and link at least 44px, folder toggle works (`aria-expanded` and `hidden` agree). Screenshots in `/tmp/bsn_harness_v2/shots/look_<engine>_<phone|desk>_<dark|light>.png` (8 files). Hover lift and reduced-motion behaviour were not exercised in a browser; they are CSS-only and unverified beyond reading.

## How each page will use it
| Page | Metaphor | Folder | Paper / stamp |
|---|---|---|---|
| Inicio | The desk | The four entry cards (Jugadores, Comparar, Juega, Archivo) become closed folders that lift. The club hero is the one open folder, accented with the club's colour. | A "Sigue donde lo dejaste" index card for recently viewed players and clubs. |
| Historia | Timeline drawer | Decade tabs along the top are folder tabs; the selected decade is the open folder holding the season list. | Season rows as paper lines; `Disputado` stamp on the 1945 champion and `Sin fuente` on 1953, from the existing data flags. |
| Jugadores | Personnel files | Each player is a dossier folder (neutral or club-accented). | The player summary is the paper card; `Sin fuente` / `Aproximado` stamps where provenance is missing. This is the main stamp page. |
| Equipos | Club cabinet | One folder per club, accented with its colour (marked "aproximados") and generic SVG crest slot. | Franchise lineage as index cards; retired jerseys are separate SVG art, not part of this component. |
| Juega | Game room | Used sparingly: only the game chooser. Each game keeps its own look (board, reels, case file, ladder). | The "Quien Soy" case file can use paper cards. No stamps on the game boards. |
| Archivo | Filing cabinet | Drawer rows: one closed folder per section (Calidad de datos, Fuentes, Cobertura, Preguntar). | Label links for drawers; the coverage gaps use `Sin fuente` stamps, in line with the "show the gaps" rule. |

## Cautions before it spreads
- Folder heads are buttons that toggle. Where a folder only navigates (Inicio entry cards), it should be an `<a>` with the same look and no chevron; the sample does not include that variant yet.
- Long lists inside open folders need the shared table from PHASE_63, not this component.
- Every public Spanish string on the real pages goes to `docs/strings_pending_<phase>.md`. The sample's Spanish text (headings, notes, "ejemplo") is for review only.
- Adding the component to `web/` adds CSS, and the top-level function inventory is frozen at 476: the open/close script must be an IIFE or a delegated handler, not new top-level functions.
