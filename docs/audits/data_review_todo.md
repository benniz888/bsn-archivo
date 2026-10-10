# Data review to-do (PHASE_62 follow-ups)

Nothing here was applied to the game. Each item needs a source check before any tag or club is added (PC1, D1, D5).

## Disputed award tags

| Player | Tag | Conflict |
|---|---|---|
| Larry Ayuso | scoring | `scoring_titles.json` 2002 row says ELIAS AYUSO (id 574); pool says Larry. |
| Carlos Bermúdez | mvp | `mvp.json` 1978 row says Charlie Bermudez (id 334); pool says Carlos. |
| Mario Butler | mvp | `mvp.json` 1988 vs Hall-of-Fame card `mvp:0` (data.js). |
| Rubén Rodríguez | mvp | `mvp.json` 1979 vs Hall-of-Fame card `mvp:0`. |
| Neftalí Rivera | mvp | `mvp.json` 1973 vs Hall-of-Fame card `mvp:0`. |
| Rolando Frazer | mvp | `mvp.json` 1981 vs Hall-of-Fame card `mvp:0`. |

Also not added (no effect on any cell, players have no club): Ramón Rivas MVP 1989, Roberto Ríos MVP 1995.

## Players with no club list (`c: []`)

They cannot fill any club cell, and a guess for one is now reported as "sin datos" and is free. Needs source data for their clubs.

16 players: Bobby Joe Hatton, Butch Lee, Carlos Bermúdez, Daniel Santiago, Federico López, Javier Antonio Colón, Jeffrion Aubry, Jerome Mincy, José Quiñones, Lee Benson, Mario Butler, Ramón Rivas, Roberto Ríos, Rubén Rodríguez, Wilfredo Pagán, Ángel «Munch» Cruz.

## Other

- Autocomplete (`drawSugg`) matches with `norm()` only, so `Jose Ortiz` gives no suggestion although submitting it works.
- Alamo / Candido Fret and Reyes / Hector are archive-index same-name players outside the 376-player game pool.

## Mojibake in game box-score player names (PHASE_66 fixup, found Oct 10)

Not edited. Affects `data/clean/game_box_player.csv` (column `player_raw`), 3 distinct names, 296 rows, no other `data/clean/*.csv` contains it:

| Broken `player_raw` | Rows | Should read | First row (file line) |
|---|---|---|---|
| `GonzÃ¡lez, Javier` | 58 | González, Javier | see `grep -n` on the string |
| `Lloreda, JosÃ© Jaime` | 118 | Lloreda, José Jaime | 26832 (BS20111004, 2011) |
| `Cotto, RubÃ©n` | 120 | Cotto, Rubén | 26932 (BS20111018, 2011) |

By season: 2011 = 34 rows, 2012 = 92, 2013 = 170. It reaches `web/data/games/**` (167 game files) and `web/data/starting_five/san.json` and `sge.json`.

Origin: `src/parse_games.py` lines 144, 217 and 354 decode every raw page as `cp1252`. Of the raw pages with non-ASCII bytes, 392 are valid UTF-8 (not cp1252), so their accents turn into two characters. The other ~4,730 pages are real cp1252 and are correct.

Related, needs a decision: the same player appears under three spellings in the file: `Gonzalez, Javier` (82 rows, ASCII), `González, Javier` (2 rows) and the broken `GonzÃ¡lez, Javier` (58). Resolving them to one identity is a D1 question (birth year + first season + club), not a text fix.

Proposed repair (NOT applied, awaiting approval): (a) root fix in `src/parse_games.py`: decode as UTF-8 first and fall back to `cp1252` only when UTF-8 fails, then re-run the games parse (needs your OK, it rewrites `data/interim`/`data/clean`); or (b) display-only repair in `src/build_web_data.py`: when a name contains `Ã` or `Â`, replace it with `name.encode('cp1252').decode('utf-8')` if that round trip succeeds, otherwise keep the name unchanged.

## PHASE_72 follow-ups (recorded Oct 10, PHASE_66 fixup 2)

1. **Mojibake root cause (still open).** The published site is repaired display-only: `src/build_web_data.py` `_read()` now round-trips any value containing "Ã" or "Â" through `encode('cp1252').decode('utf-8')` and leaves it unchanged if that fails. `data/clean/game_box_player.csv` still holds the broken names (296 rows). Real fix: in `src/parse_games.py` lines 144, 217 and 354, decode each raw page as UTF-8 first and fall back to `cp1252` only when UTF-8 fails; then re-run `make parse-games` and review the FULL diff of `data/interim` and `data/clean` (expect exactly the 3 names, 296 rows, and nothing else) before accepting. `tests/test_web_data_encoding.py` fails if any mojibake reaches `web/data/**`.
2. **Javier González identity (D1).** One player under three spellings in `game_box_player.csv`: `Gonzalez, Javier` (82 rows, ASCII), `González, Javier` (2 rows) and the broken `GonzÃ¡lez, Javier` (58 rows). After the repair the last two read the same, but nothing merges them with the ASCII form. Match on birth year + first season + primary club, never on name alone.
3. **Atenienses de Manatí → Cariduros de Fajardo note ("Se mudó a Fajardo en 2017.", `web/js/data.js` `ate.note`) is unverified.** Sources recorded in `src/reconcile.py` `FRANCHISE_SOURCES` (owner 2026-09-20, a primerahora.com URL, wikipedia:Cariduros_de_Fajardo) were taken from search results and never fetched; es.wikipedia `Cariduros_de_Fajardo` returned 404 on Oct 10. No lineage event links the two in `franchise_events.csv` or `franchises.json`; Cariduros is 1973–2023 ("derived:champion/scoring rows"); the archive shows Atenienses only in 2015 and 2016 (`manati_audit_spec.md` F5). Needs an independent source before the note stays on the page.
