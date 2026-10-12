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

## PHASE_67C — ¿Quién soy? findings (added 2026-10-11)
Found while building PHASE_67C (¿Quién soy?). Nothing here was changed in data; each item says what the game does meanwhile.

### Held out of ¿Quién soy? until resolved
- **Mario Butler** — the MVP 1988 attribution comes from a first+last-name join and is unverified; HOF/LEADERS list his career as 1980–2008 (779 games), a range that looks too long; POOL has no club for him. Held (`HOLD` in `clueList.init`, tabs.js).
- **Teófilo Cruz** — POOL.c = [san] (Cangrejeros de Santurce) is unverified. Held.

### Conflicts and wording
- **Mario Morales' club** — POOL.c = ["san"] (Cangrejeros de Santurce) but STONE and HOF say his home is the Mets de Guaynabo (Coliseo Mario Morales). The new ladder does not use his club clue; the field still feeds La Cuadrícula.
- **Hodge's MVP years** — the request listed them as missing from the structured MVP list. They are there: MVP_YEARS has 2014 and 2022 (Capitanes de Arecibo) and SEASON_AWARDS has the 2018 finals MVP. My PHASE_67C step-1 note saying they were missing was wrong (an earlier join did not find them). No data gap; nothing to fix.
- **Piculín's English bio** — "«Piculín». Reached the NBA and came home to finish." is the only English line among the 93 POOL bios. Never shown now; the line still sits in POOL.b and needs a Spanish rewrite if it is to be used elsewhere.
- **Plummer's award name** — his Progreso del Año (2024) row comes from SEASON_AWARDS as "Progreso del Año" (capital Año); his POOL bio says "Progreso del año". The clue reads "Ganó el premio de Progreso del Año en 2024." Owner to confirm the official award name and casing.
- **Butler's career range** — see above (1980–2008).

### Legends still out of ¿Quién soy? (cannot reach 3 clues; missing field)
| Player | Missing |
|---|---|
| J. J. Barea | No structured award, record, rank, title or season line (only tags native/nba/figura). No club count/ppg/rpg/apg. |
| Jerome Mincy | Same: no award/record/rank/title; no clubs, no averages. |
| Butch Lee | No award/record/rank/title; no clubs. NBA_PLAYERS has a note ("Primer jugador del BSN en ganar un campeonato de la NBA") but it is free text, not a field the final clue may use. |
| Sammy Betancourt | Has scoring titles 1972, 1975, 1976 (SCORING) and two clubs, but no ppg/rpg/apg, so only position and decades can narrow the pool before the final clue, and those would leave a single candidate too early. Needs career averages or a club count. |

Included now with exactly 3 clues (thin but valid): Federico López, Carlos Bermúdez, Jesse Pellot, Juan Báez, Mario Morales, Ángel Santiago.

### Free-text bio lines no longer shown (93)
POOL.b is never displayed in ¿Quién soy? now. Each claim that exists as a structured field (MVP, scoring titles, finals MVP, rookie/defensive/sixth/progress awards, all-time rank, league record, named coliseum, titles from season rows) is rebuilt from that field; the rest is dropped. Full list of the lines that are no longer shown:

| Player | Dropped line |
|---|---|
| Raymond Dalmau | Se retiró en 1985 liderando la liga en puntos, rebotes y asistencias a la vez. |
| Neftalí Rivera | Anotó 79 puntos en un solo juego en 1974; sigue siendo el récord. |
| Georgie Torres | Máximo anotador histórico con 15,863 puntos. |
| Mario Morales | Segundo de todos los tiempos en puntos y cuatro veces MVP. |
| Rolando Frazer | Centro panameño, dos títulos de anotación seguidos con Aibonito. |
| Ángel Santiago | Ganó el título de 1986 con los Polluelos. |
| Christian Dalmau | Veinticinco temporadas con ocho clubes del BSN. MVP de la final en 2009. |
| Teófilo Cruz | Cuatro MVP y un puesto en el Salón de la Fama de FIBA. |
| José «Piculín» Ortiz | «Piculín». Reached the NBA and came home to finish. |
| Edgar de León | Dos títulos de anotación con Fajardo. |
| Pablo Alicea | Tuvo el récord de asistencias en un juego durante veintitrés años. |
| Sammy Betancourt | «El Francotirador». Tres títulos de anotación y un puesto en el Salón del Deporte. |
| Juan «Pachín» Vicéns | Quinteto del Mundial de 1959. |
| Jaime Frontera | Lideró la liga con 400 puntos en 1966. |
| Adolfo Porrata | 516 puntos para liderar la liga en 1967. |
| Héctor Blondet | Campeón de anotación en 1974. |
| Jim Maldonado | Promedió 30.6 para ganar el título de 1983. |
| Wesley Correa | Campeón de anotación con Morovis en 1989. |
| Edwin Pellot | 31.5 por juego con Isabela en 1991. |
| Jesse Pellot | MVP y líder de anotación en 2009. |
| Gary Browne | MVP y líder de asistencias en 2017. Campeón con Bayamón en 2026. |
| Tu Holloway | MVP de la final del título de 2017. |
| Víctor Liz | Lideró la liga en anotación en 2017. |
| Jonathan García | 33 asistencias en un juego en 2012. |
| Emmanuel Mudiay | 779 puntos en 33 juegos para ganar el MVP de 2025. |
| Kobi Simmons | Segundo en anotación en 2025. |
| Cheick Diallo | Tercero en anotación y segundo en tapones en 2025. |
| Sam Waardenburg | Cuarto en anotación con Mayagüez en 2025. |
| Ysmael Romero | El mejor anotador local de 2025, jugando como nativizado. |
| JaVale McGee | Lideró la liga en tapones en 2025 con 40 en 25 juegos. |
| Iván Gandía | 91 triples al 44 por ciento para liderar la liga en 2025. |
| Alexander Kappos | Segundo en triples en 2025 con 78. |
| Travis Trice | MVP en 2024 y 2026, y MVP de la final del título de 2024. |
| Renaldo Balkman | MVP de la final en 2016 con Arecibo y otra vez en 2026 con Bayamón, a los cuarenta y un años. |
| Moses Brown | Defensor del año en 2026. |
| Andre Curbelo | Progreso del año en 2026 y único nativo del Quinteto Ideal. |
| Montrezl Harrell | Quinteto Ideal en 2026. |
| Jaylen Nowell | Quinteto Ideal en 2026 y segundo en anotación. |
| Daniel Rivera | Novato del año en 2026, nacido en San Juan. |
| Christian López | Sexto hombre del año en 2026. |
| Danilo Gallinari | MVP de la final del título de Bayamón en 2025. |
| Jae Crowder | Firmado por Bayamón para la temporada 2026. |
| Alfonso Plummer | Progreso del año en 2024 con Arecibo. |
| Emmanuel Maldonado | Premiado con Santurce en 2024. |
| Jordan Murphy | Segundo en tapones en 2025 con 30. |
| Jassel Pérez | Dominicano. Tercero en anotación en 2026 y líder ofensivo del campeón. |
| Chris McCullough | 25 puntos en el quinto juego de la final de 2026. |
| Stephen Thompson Jr. | Triple decisivo a 2:43 del final del séptimo juego de 2026. |
| Javier Mojica | Selló el título 18 desde la línea a 19.7 segundos. |
| Arnaldo Toro | Disponible para el séptimo juego tras dudas de última hora. |
| Rigoberto Mendoza | Dominicano. Líder ofensivo de Aguada en la final de 2026: 22 puntos en el cuarto juego, 15 en el primer parcial. |
| Manny Camper | 11.5 puntos y la defensa sobre Jassel Pérez en la final de 2026. |
| Joel Soriano | Dominicano. Donqueo con 1:23 que puso a Aguada arriba en el sexto. |
| Jacob Wiley | Refuerzo de Aguada en la final de 2026. |
| John Holland | Veterano de Aguada en la final de 2026. |
| Carlos Arroyo | Doce temporadas en el BSN. Novato del Año en 1996 con Fajardo, cinco campeonatos con los Cangrejeros entre 1998 y 2003, MVP de la final en 2003, MVP del Juego de Estrellas en 2017 y líder de asistencias en 2018. Se retiró con Ponce en 2019. Santurce retiró su número 7 el 7 de octubre de 2021. Hoy es coapoderado de los Vaqueros. |
| J. J. Barea | Debutó con los Indios de Mayagüez en 2001 y volvió con ellos en 2002. Jugó con los Cangrejeros en 2006 y otra vez en 2021 y 2022. Campeón de la NBA con Dallas en 2011. Dirigió a Mayagüez en 2017 y a los Mets en 2024 y 2025. |
| Walter Hodge | MVP de la liga en 2014 y otra vez en 2022 con Arecibo, y MVP de la final de 2018. |
| Reyshawn Terry | MVP y líder de anotación y rebotes en 2018: 835 puntos en 36 juegos, 23.2 por partido. |
| George Conditt IV | Defensor del Año en 2024 con los Gigantes: 14.6 puntos y 9.2 rebotes. |
| Jhivvan Jackson | Novato del Año en 2024 con los Osos de Manatí. |
| Juan Báez | Tres veces MVP con los Cardenales de Río Piedras: 1957, 1963 y 1964. |
| Raúl «Tinajón» Feliciano | MVP en 1951 con los Gallitos de la UPR y en 1955 con los Cardenales de Río Piedras. |
| James Carter | Máximo asistente histórico del BSN con 3,025, y MVP en 1991 y 1994 con los Brujos de Guayama. |
| Jerome Mincy | Una de las figuras que definieron el baloncesto puertorriqueño de los ochenta. |
| Ángel «Munch» Cruz | Figura de los ochenta citada junto a Morales, Dalmau y Piculín. |
| Ramón Rivas | Empezó en el BSN y llegó a la NBA. |
| Daniel Santiago | Empezó en el BSN y llegó a la NBA. |
| Butch Lee | El primer puertorriqueño y el primer jugador del BSN en llegar a la NBA, y el primero en ganar allí un campeonato. |
| Larry Ayuso | Parte de la plantilla con la que Santurce ganó el título de 2007. |
| Robert «Tractor» Traylor | Ala-pívot exNBA que encabezó el título de los Cangrejeros en 2007. Falleció en 2011. |
| Lee Benson | Rompió en 2008 el récord de rebotes en una temporada que Rubén Rodríguez había fijado en 1978. |
| Jeffrion Aubry | Segundo de todos los tiempos en tapones con 642. |
| Damion James | Líder de anotación y de rebotes en 2016. |
| Alex Abreu | Líder de asistencias en 2016. |
| Eric Dawson | Líder de rebotes en 2017. |
| Brandon Costner | Segundo en anotación en 2018 con los Caciques de Humacao: 668 puntos en 34 juegos. |
| Darnell Hinson | Primera selección del sorteo de 2009, por los Caciques de Humacao. |
| Ángel Daniel Vassallo | MVP de la liga en 2016. Hoy dirige a los Piratas de Quebradillas. |
| Akil Mitchell | Líder de rebotes en 2025. |
| Ángel Rodríguez | Líder de asistencias en 2025 y una de las voces contra la tercera plaza de refuerzo. |
| Chris Ortiz | Firmó junto a Browne, Hodge y Rodríguez el video contra la tercera plaza de refuerzo en 2024. |
| Xavier Cooks | Refuerzo de Bayamón para la temporada 2026. |
| Jaylin Galloway | Refuerzo de Bayamón para la temporada 2026. |
| Mario Butler | Número 1 de todos los tiempos en rebotes, con 8,236 rebotes en 1980–2008. |
| Rubén Rodríguez | Número 2 de todos los tiempos en rebotes, con 6,178 rebotes en 1969–1991. |
| Roberto Ríos | Número 7 de todos los tiempos en anotación, con 11,312 puntos en 1978–2000. |
| José Quiñones | Número 9 de todos los tiempos en anotación, con 11,012 puntos en 1976–1995. |
| Carlos Bermúdez | Número 7 de todos los tiempos en rebotes, con 4,884 rebotes en 1970–1984. |
| Javier Antonio Colón | Número 4 de todos los tiempos en asistencias, con 2,748 asistencias en 1987–2008. |
| Federico López | Número 5 de todos los tiempos en asistencias, con 2,440 asistencias en 1981–1997. |
| Wilfredo Pagán | Número 6 de todos los tiempos en asistencias, con 2,367 asistencias en 1992–2018. |
| Bobby Joe Hatton | Número 9 de todos los tiempos en asistencias, con 2,235 asistencias en 1994–2012. |

### PHASE_67C fixup — career rebound record vs all-time list (found 2026-10-11)
Two fields disagree about who leads career rebounds:
- `RECORDS` (web/js/tabs.js ~160, same data in `web/data/index/records.json` and `data/clean/bsn_records.csv`): "Most rebounds, career", Rubén Rodríguez, 6,178, note "631 games".
- `LEADERS.rebounds` (web/js/tabs.js; same figures in `web/data/index/career_leaders.json`, the Wikipedia-derived table that `stale_note` calls a floor): #1 Mario Butler 8,236 (779 games, 1980–2008), #2 Rubén Rodríguez 6,178 (631 games, 1969–1991). Butler's total/games is 10.6, consistent with his listed average; Rodríguez's 6,178 is the same number in both fields.
So the two sources agree on Rodríguez's total and disagree on whether anyone is above it. One of them is wrong or the record is stated for a different scope. Butler is also the held-back player (career range 1980–2008, MVP join unverified). Not resolved here; needs an independent source. Until then ¿Quién soy? builds no "récord", "número 1" or "máximo" clue for anyone (the record clue type is gone), and uses rank clues only from `LEADERS` rows whose total/games matches their listed average.
- **Second inconsistency in LEADERS:** Raymond Dalmau's assists row (rank 8): total 2,302 in 537 games is 4.3 per game, but the row lists 5.1 (his POOL apg is also 5.1, which would be about 2,740). The row is skipped for clues. Everything else in the three tables is sorted, sequential and ratio-consistent.
- **García:** his only structured "final" clue was the RECORDS single-game assists record (33, 2012). With record clues removed he has no award, rank or title field, so he is not drawable. The POOL bio's "récord mundial extraoficial" claim (also flagged in PHASE_65 for Inicio) is never shown in ¿Quién soy?.


### PHASE_67C fixup 2 — players dropped because their only possible last clue was a best-season line (2026-10-11)
Rule: the best-season stat line (year plus value) is never a last clue; a player stays in ¿Quién soy? only if the last clue is a structured honor (award, title, all-time rank, named coliseum). 246 players were playable before this fixup and are not now (209 lesser-tier, 37 mid-tier; 212 from the 2020s, 33 from the 2010s, 1 from the 2000s). They are grouped by what would let them back in.

**A. All their recorded seasons have no award row of any kind (34).** SEASON_AWARDS covers 2009, 2016, 2017, 2018 and 2024-2026; MVP_YEARS adds 2010, 2011, 2014 and 2022; FINALS_BY_YEAR is 2024-2026. So 2012, 2013, 2015, 2019, 2020, 2021 and 2023 have no award row at all. Adding the league's MVP / rookie / defensive / sixth-man / progress / scoring-leader rows for those seasons would let any of these players qualify if they won one:
Alade Aminu (2021); Alejandro Carmona Sanchez (2013); Alex Morales (2023); Angel Nunez (2021); Angel Suero (2019,2020,2021); Archie Goodwin (2023); Benito Santiago Jr. (2019); Braxton Key (2023); Chaundee Brown Jr. (2023); D.J. Hogg (2023); Dewan Hernandez (2023); Diamond Stone (2021); Emmy Andujar (2023); Frank Gaines (2021); Greg Smith (2019); Guillermo Diaz (2020); Ike Diogu (2013); Isaac Sosa (2019,2023); James Ennis (2023); Jessie Govan (2021); Juan Miguel Suero (2019); Kalin Lucas (2021); L.J. Figueroa (2023); Melo Trimble (2019); Mitchell Creek (2023); Nick Minnerath (2019); Ricky Sanchez (2015); Robert Glenn (2019); Tai Wesley (2019); Tony Bishop Jr (2021,2023); Tyreke Evans (2023); Weyinmi Efejuku Rose (2013); Will Daniels (2015,2020); Zavier Simpson (2023)

**B. They played in a season that has award rows, but won none of the stored honors (212).** Nothing in the structured data can end their ladder. Fields that would: per-player championship rows (today titles come only from `ss` season rows matched to a club's title years), all-league teams (AWARDS_2026 lists the 2026 Quinteto Ideal but is not part of SEASON_AWARDS), second-in-scoring and other leaderboard finishes (the seasons index has leaders for only 15 seasons), and all-time list placements for 2010s-2020s players. Names:
A.D. Vassallo (2013,2016,2018,2019,2020); Admiral Schofield (2026); Aleem Ford (2026); Alejandro Ralat (2026); Alejandro Vazquez (2026); Alex Galindo (2013,2016); Alexander Franklin (2026); Alize Johnson (2024); Angel Matias (2023,2024); Anthony Cowan Jr (2026); Anthony Morales (2026); Antonio Ralat (2026); Arguster Daniels IV (2026); Avry Holmes (2026); Ben McCauley (2022); Ben Moore (2022); Bradley Camacho (2026); Brady Manek (2026); Brandon Boyd (2026); Brandon Costner (2016,2018,2021); Brandon Goodwin (2024); Brandon Knight (2023,2025,2026); Brian Conklin (2016); Bryan Gonzalez Colon (2026); Bryan Powell (2026); Bryce Cotton (2025); Cady Lalanne (2026); Cameron McGriff (2024); Carlos A Colon (2026); Carlos Yao Lopez (2026); Chane Behanan (2016); Cheick Diallo (2022,2024,2025,2026); Chris Brady (2026); Christian Lopez Santiago (2026); Christian Pizarro Rios (2026); Corey Jae Crowder (2026); Corey McKeithan (2026); D J Wilson (2026); Damian Jones (2026); Damien Wilkins (2017); Daniel Rosado (2026); Darius Bazley (2026); David Laury (2017); David Scott James Jr (2026); David Stockton (2020,2021,2023,2024); DeMarcus Cousins (2023,2025); Deandre Pinckney (2026); Denis Clemente (2026); Deonte Burton (2024); Derek Reese (2026); Derrick Walton (2026); Devin Williams (2026); Devon Collier (2026); Diego Gonzalez Pellot (2026); E.J. Crawford (2026); Elijah Hughes (2026); Emmanuel Andujar (2026); Eric Ayala (2026); Eugene German (2026); Evander Ortiz Colon (2026); Felix A. Rivera Vega (2026); Fernando Caballero Acevedo (2026); Gabriel J. Belardo (2026); Gaby Belardo (2022); George Alexander Hamilton (2026); Georgie Pacheco-Ortiz (2024); Gerardo Texeira (2026); Giancarlo Rosado (2026); Gianfranco Grafals (2026); Giovanni Santiago (2026); Grant Basile (2026); Harold Perez Abreu (2026); Hassan Whiteside (2023,2025); Hiram Huertas (2026); Hunter Tyson (2026); Ibrahima Sylla (2026); Isaiah Hicks (2026); Isaiah Palermo (2026); Isaiah Pineiro (2026); Isiah Gaiter (2026); Ismael Cruz (2025); Ismael Romero (2025,2026); Ivan Gandia-Rosa (2025); Ja Kair Sanchez (2026); Jack Edward McVeigh (2026); Jack McVeigh (2026); Jahlil Okafor (2024); Jahvari Josiah (2022); Jalen Bernard Crutcher (2026); Jalen Crutcher (2026); Jamarion Sharp (2026); Jamil Wilson (2026); Jampier Lezcano (2026); Janiel Jafet Romer (2026); Jared Sullinger (2024); Jase Febres (2026); Javier Ezquerra (2026); Jay Shawn Alvarez (2026); Jayden Martinez (2026); Jaylen Nowell (2026); Jaysean Paige (2023,2024,2025,2026); Jeff Early Jr. (2026); Jevin Nikolas Muniz (2026); Jezreel De Jesus (2014,2018,2019,2021,2022,2023,2024,2025,2026); Joel Soriano (2025,2026); John Brown III (2026); John Jenkins lll (2026); John Meeks (2024); Jonathan Rodriguez (2026); Jonathan Zhao Olmos (2026); Jordan Daniel Cintron (2026); Jordan Howard (2020,2025); Jordan Murphy (2025); Jorge L. Pacheco (2026); Jorge Luis Torres (2026); Jose Carlos Placer Diaz (2026); Jose Roman Angueira (2026); Joseph Bull (2026); Josh Perkins (2022); Joshua Denton (2026); Joshua Rivera (2026); Josue Erazo (2026); Juan Pablo Pineiro (2026); Justin Keenan (2014); Justin Reyes (2026); Kaleb Werson (2022); Kay Felder (2025); Kendall Munson (2026); Kendric Davis (2026); Kenneth Faried (2026); Kevin Maura Colon (2026); Khary Mauras (2026); Kobi Simmons (2025); Kristian Doolittle (2024,2026); Kyle Rose (2026); Kyle Vinales (2018,2022); Larry Ayuso (2012,2013,2014,2015); Leon Williams (2014); Luis D. Cuascut (2026); Luis Henriquez (2026); Luis Hernandez (2026); Luis Lopez Martinez (2026); Luis Moya (2026); Malachi Smith (2026); Malik Beasley (2026); Malik Williams (2026); Manuel Camper (2026); Matthew Lee (2026); Maxwell Abmas (2026); Michael J. Bruesewitz (2026); Michael O Connell (2026); Miguel Martinez (2026); Mike Young (2018); Milton Doyle (2024); Montrezl Harrell (2026); Nathan Sobey (2025,2026); Nathaniel Mason (2022,2023); Neftali Acevedo Diaz (2026); Neftali Alvarez (2026); Nick Lucena (2026); Nick Rakocevic (2025); Noah Horchler (2026); Norris Cole (2024); Oenis Medina (2026); Olumiye Oni (2026); Omar Figueroa (2026); Onzie Branch (2026); Owen Perez (2026); Peter John Ramos (2012,2016); Phillip Wheeler (2022,2025); Q.J. Peterson (2024); Rafael A. Pinzon Duperoy (2026); Ramses J. Melendez Vega (2026); Raymond Cintron Jr (2026); Reinaldo Santana (2026); Ricky Ledo (2018); Rico Hopping (2026); Rigoberto Mendoza (2016,2026); Robiel Morales (2026); Rondae Hollis-Jefferson (2022,2023,2024); Ruben Cotto (2026); Ryan Arcidiacono (2026); Ryan Pearson (2026); Rychell Janga (2026); Sam Waardenburg (2025); Sam Young (2014); Scottie James (2024); Stevie Thompson (2024); Tai Odiase (2024); Terence Davis (2026); Terrence Jones (2020,2022); Terrico White (2022); Theo Pinson (2025); Theophilus A. Pinson Jr. (2026); Thomas Robinson (2021,2022,2023); Timajh Parker (2026); Torrey Craig (2026); Tory San Antonio (2026); Tyler Cook (2026); Tyler Davis (2026); Tyler Polo (2026); Tyrell Harrison (2025,2026); Vicktor Lakhin (2026); Victor Rudd (2019,2020,2021,2022,2023); Von Wafer (2014); Wilfredo Rodriguez Valentin (2026); Will Barton (2024); Will Martinez (2017,2021); William Cruz Rodriguez (2026); Wilmer Lugo-Sanchez (2026); Xavier Zambrana (2026); Yahir Cordero Melendez (2026)

### PHASE_67C string fixup 3 — award names to confirm (2026-10-11)
- Defensive award: SEASON_AWARDS labels it "Defensor del Año"; SEASON_AW (web/js/tabs.js, the per-season award files' display names) labels the same award "Defensa del Año". ¿Quién soy? uses "Defensor del Año" ("Ganó el premio de Defensor del Año."). Owner to confirm the official name and make the two tables agree.
- Sixth-man award: the archive labels it "Sexto Hombre" (no "del Año"), unlike Novato / Defensor / Progreso del Año. The clue reads "Ganó el premio de Sexto Hombre." Owner to confirm the official name.


### PHASE_67D2 — LEADERS rows excluded from Sube y Baja (2026-10-11)
Rule: a LEADERS row is not used as a question option when total ÷ games differs from its listed average by more than 0.15 (same rule as the ¿Quién soy? rank clues). Checked every row of points (10), rebounds (10), assists (10); "juegos jugados" reads the games column of the points rows, which all pass; "títulos de la franquicia" reads F[k].won (no ratio to check).
- Fails (1 of 30): **assists #8 Raymond Dalmau**, 2,302 in 537 games = 4.29 per game, listed 5.1. Points 0 fail, rebounds 0 fail, games 0 fail, titles n/a. Still open: either the total or the average is wrong (5.1 would be about 2,740); needs an independent source. His points (11,592 / 537 = 21.6) and rebounds (5,673 / 537 = 10.6) rows are consistent and stay.
- Pairing rule (not a data issue): two values are never paired when they differ by less than max(1, 2% of the larger).


### PHASE_68 — Archivo build: items deferred (2026-10-11)
Source: docs/audits/phase68_archivo_audit.md. Nothing below was touched in PHASE_68.

**PHASE_72 (data)**
- **A02 — source-name quality in per-season detail and the Premios scoring list.** Typo "GOERGIE TORRES" (1986 MVP); names truncated by the parse ("Ayuso, Elias 'Lar", "Morales, Mario 'Qui", "Butler, Mario Albe" in 2013 and 1986 leaders); ALL-CAPS and unaccented forms ("RAUL FELICIANO", "Teofilo Cruz", "NEFTALI RIVERA"); three name formats on one page ("Bass, Paris", "CHRISTIAN DALMAU", "Hector Blondet"). The same player shows as "Teófilo Cruz" elsewhere. Fix at the parse (`src/`), not by display rewrite; where `bsnpr_id` resolves, the build can show the canonical name, otherwise the raw string stays.
- **A03 — Rubén Rodríguez 6,178 (Récords) vs Mario Butler 8,236 (Líderes) career rebounds.** Already recorded above under "PHASE_67C fixup" (the two RECORDS/LEADERS bullets); not repeated. PHASE_68 built no note and picked no side.

**PHASE_73 (look)**
- **A13 — sub-view header.** Every Archivo view repeats the page title plus a 4-line lede above the subnav (about 300px at 390px). Collapsing the lede on sub-views is a layout and look decision, not a code fix.
- **A15 — subnav edge fade.** The audit saw clipped pills with no cue; the existing `.subnav.fade-l/.fade-r` mask does render (visible in the PHASE_68 error-state screenshot at 390px). Re-check at the audit's own configurations before treating it as open.

**Seen during PHASE_68 verification (data-adjacent, not changed)**
- `manifest.counts.seasons` is 98 and `YEARS.length` is 97 (the `1942-1943` split-season file is the extra one, per D3). Every "N temporadas" in the app uses `YEARS.length` (97); the manifest's 98 counts files, not seasons.
- `seasons_with_leaders` is 15: 1986, 2000, 2001, 2002, 2007–2010, 2012–2014, 2018–2021 (from `web/data/seasons/*.json`). Any prose that still describes leader coverage by a fixed year should be read against that list.

## PHASE_69 follow-ups (Oct 12)

- **Lawyer question: verbatim bio prose.** The player biographies from bsnpr.com (Wayback captures) are shown verbatim on player pages. Is reproducing that prose acceptable, or should it be shortened, paraphrased or dropped? Créditos (PHASE_69) says the bios, season stats, tables and boxscores come from bsnpr.com files kept by the Internet Archive; it does not answer the rights question.
- **PHASE_72: English one-liners with no provenance.** `HOF[].role`, `POOL[].b`, `NBA_PLAYERS` and `SEASON_AWARDS` carry English one-line descriptions with no recorded source. Find the source for each or replace the text before it is relied on (PC1, PC3).
- **Lawyer: registrar and DNS provider unknown.** The privacy text says the site is served from GitHub Pages and that the host sees visitor IPs. Who the domain registrar is, and whether a DNS or proxy provider sits in front of `bsnarchivo.com`, is not recorded; any of them may also process visitor data. Confirm and, if needed, add them to the privacy text.

## PHASE_72A — career rebounds decision logged (2026-10-12, owner D1)
Decision: Mario Butler's 8,236 career rebounds (Líderes #1) stays visible with a **SIN CONFIRMAR** flag; Rubén Rodríguez's 6,178 is **no longer shown as a record** (the "Rebotes de carrera" row is removed from Récords; his figure still appears as Líderes #2 with its source row unchanged).
Why still open: both numbers come from one unsourced seed (`data/clean/bsn_records.csv:3`, `bsn_career_leaders.csv:12-13`, scaffold `195fc2a`, no provenance columns). The spine supports Butler's games (789 minus a 10-game duplicate 2001 row = 779) and Rodríguez's (631, id 2113) but holds no per-season rebound totals, so neither total can be confirmed from the repo. Evidence and confidence: `docs/audits/phase72_audit.md` item 1 (about 80% that Butler leads).
Also flagged in the same words: Butler's HOF chip and role, and the "Líder histórico de rebotes" line in his bio. Not changed: `data/clean/*.csv`, `web/data/index/records.json` and `career_leaders.json` (data layer untouched; the generated records.json still has the Rodríguez row, which the page no longer reads).
To close: an independent career-rebound figure (outside data, D4 forbids fetching it in this phase), then drop the flag or correct the row, and add provenance columns to both CSVs.
Superseded by the 72C audit finding: the "expect exactly 296 rows" note for the mojibake regeneration above is wrong; see `docs/audits/phase72_audit.md` item 3.

## PHASE_72B — mojibake repaired, González split (2026-10-12, owner D3/D8)
Done: per-sequence decoder in `src/parse_games.py` (`_decode`, three sites); `src/apply_game_name_repair.py --apply` repaired the 296 rows of `data/clean/game_box_player.csv` (Lloreda 118 -> id 2690, Cotto 120 -> id 2675, González 58 -> id 2513). `parse-games` was not re-run; the 365 unrelated `bsnpr_id` values are unchanged (pinned by digest in `tests/test_phase72b.py`).
Supersedes the two PHASE_72 follow-ups above: (1) "re-run `make parse-games` and expect exactly 296 rows" is wrong (a re-parse also moves 365 ids); (2) "Javier González: one player under three spellings" is wrong: the 58 `GonzÃ¡lez` rows are id 2513 (González López, b. 1989; 2013 Santurce and 2012 Humacao match his career rows).
Still open (left as is, not guessed): 82 rows `Gonzalez, Javier` (Quebradillas 2001-03; only candidate id 1006 has no season rows) and 2 rows `González, Javier` (2008, no team; 2513 starts in 2011).
