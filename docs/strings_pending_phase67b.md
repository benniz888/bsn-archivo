# Strings pending: PHASE_67B (La Temporada Perfecta difficulty)

Status: PROPOSED wording is already in the working tree (uncommitted); owner approval pending.

| # | Where | Current | Proposed |
|---|---|---|---|
| 1 | Result verdict at 34-0 (`finishDraft`, games.js) | "Temporada perfecta. Nadie lo ha hecho de verdad — el récord real es 29-5, Bayamón 1993." | "Temporada perfecta. 34 victorias, ninguna derrota." |

Source check for row 1 (searched `data/clean/bsn_records.csv`, `bsn_champions_by_season.csv`, `standings.csv`, `web/data`, `web/js`, `web/index.html`): `bsn_records.csv` line 11 has `"Most wins, single season",Vaqueros de Bayamon,29,1993,` — 29 wins only, no losses, no games-in-season, and the file has no source column (inventoried in session.md as "inherited, seed"). "29-5", "nadie lo ha hecho" and a 34-game 1993 season are not supported by any source field. `standings.csv` has no 1993 rows. Clause removed, nothing paraphrased.

| 2 | Result verdict at 30-33 wins (`finishDraft`) | "Mejor que cualquier temporada real del BSN." | "Cuatro derrotas o menos." (states only the player's own result; true for every 30-33 win season; no record or history mentioned) |

Row 2: the old line depended on the same unsourced 29-win record as row 1. Removed.

## Not changed, flagged
- In-UI scoring explanation / share text: none mentions what a perfect season needs. Share text ("El Archivo · La Temporada Perfecta\n{w}-{34-w}\n…") unchanged and still correct. No new strings added.
- Behavior note (fixup): a 33-win band now covers totals in [236, 240), so results step 32 -> 33 -> 34 with no gap. No new strings.
