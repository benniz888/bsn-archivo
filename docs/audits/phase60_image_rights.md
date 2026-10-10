# PHASE_60 audit: image and asset rights

(The prompt named `docs/image_rights.csv`; PHASE_60 may only write `docs/audits/phase60_*.md`, so the table is here. Convert to CSV when you approve a location.)

## Finding 1: `web/img/` contains no images
`web/img/crest/.gitkeep` and `web/img/player/.gitkeep` are the only files (`git ls-files web`). `web/data/manifest.json` has `"assets": {}`, so the drop-in image layer (`imgTry`, tabs.js ~L467) emits no `<img>`. Every crest and portrait is drawn inline SVG (`tabs.js` ~L3183, public text: "Todos los escudos y retratos están dibujados en SVG ... este archivo no los usa"). No rasters on any route; Lighthouse and the network capture saw zero image requests.

## Finding 2: image-like assets that DO exist (flag, nothing deleted)
| file / location | subject | apparent source | license / status |
|---|---|---|---|
| `web/index.html` L20 `apple-touch-icon` (data URI PNG, 7,668 B decoded) | brand icon | not recorded in repo; cannot be determined from the file | UNKNOWN: confirm it is the owner's own artwork |
| `web/index.html` L21 `icon` 32x32 (data URI PNG, 1,425 B) | favicon | same | UNKNOWN: same |
| `web/index.html` L22 manifest (data URI, ~40 KB decoded) with embedded PNG icons | PWA icons | same | UNKNOWN: same |
| crest/mascot SVGs generated in `tabs.js` ("original geometric emblem", "original mascot illustration", per franchise) | club identities | drawn by this project, in club colors | Original drawings. Risk: mascot art and club names/colors depict league clubs' marks; the page itself says official logos need permission. Show the league |
| `docs/specs/redesign_v3/assets/logo/*` (11 files; new, untracked) | new "EL ARCHIVO" mark | generated for this redesign | Owner's; not yet in `web/` |
| Fonts: Inter, Oswald (fonts.googleapis.com / fonts.gstatic.com) | typography | Google Fonts | SIL OFL (from the Google Fonts catalog, not verified in repo). Third-party request at load, see summary section 3 |

## Finding 3: non-image rights flags found while looking
- `tabs.js` ~L1429 shows news headlines "vistos en la app oficial del BSN" (titles only, summarized). Third-party editorial content.
- `tabs.js` L451: `POOL_BSN26` comment says it is generated from `bsn_2026_official.csv` (bsnpr.com official player export). Data from the league's own export.
- `data.js` / RealGM and latinbasket derived data: master plan says keep as is, add no new mentions. Not touched.
- Outbound links to league social accounts and app-store pages (`tabs.js` L301-308): links only, no embeds.
