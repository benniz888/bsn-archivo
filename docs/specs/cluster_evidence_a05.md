# A05 DOB/career conflict -- evidence and decision (id 721/722)

PHASE_A05_DOB_EVIDENCE (read-only investigation) and PHASE_A05_FLAG_PLAN (this decision), 2026-09-24.
Extends the A05 section of docs/specs/cluster_evidence_batch2.md (not edited -- that file is read-only evidence
from its own phase); this file documents what changed since and the decision that followed. The A05 merge of
722 into 721 stays HELD; nothing about the merge decision changes here.

## Summary

id 721's own bsnpr.com profile page carries a birth date of 5/9/1980 and a 1965-1969 career table for
Capitanes de Arecibo on the same capture. A 1980-born player cannot have played in 1965-1969. The DOB appears
on three bsnpr.com pages, all the same source family (not independent of one another), and the ages shown on
two of them are arithmetic on that DOB, not a separate data point; the career rows appear nowhere else at all.
No source outside bsnpr.com was found for either. Decision: keep the DOB visible, flag the 5 career rows as a
source discrepancy (neutral wording, no claim of which datum is wrong), exclude them from the player's career
totals. 722's merge into 721 stays HELD.

## 1. Every DOB sighting for 721 and 722

source|captures|value|notes
enciclopedia listing row|77 captures, 2007-04-17 to 2021-09-01|5/9/1980|stable for BOTH ids, every capture
jugador.asp profile (721 only)|1 capture, 2007-08-28|5/9/1980|"Nacimiento" cell; "Edad" cell reads 27
jugador05.asp bio (721 only)|1 capture, 2005-09-03, San German roster|5/9/1980|"Fecha:" label; "Edad:" reads 25
latinbasket roster|n/a|none|0 rows for 721 or 722
Wikipedia|n/a|none|no repo source; web search (section 5) found nothing either
player_dob_overrides.csv / jugador05_dob_conflicts.csv|n/a|not present|721/722 never flagged -- both sources agree

All three pages agree on 5/9/1980, and the two pages that also show an age are each internally consistent with
it at their own capture date (27 in 2007, 25 in 2005). No other id in players_canonical.csv shares this exact
value (checked directly: exactly 2 matches, 721 and 722).

## 2. 721's page: the DOB and the disputed career table are the same capture

Source: https://web.archive.org/web/20070828224742/http://www.bsnpr.com/jugadores/jugador.asp?id=721&e=
Raw page: one `<b>Llovet Ayala, Francisco</b>` header, one DOB table row (Nacimiento 5/9/1980, Edad 27), one
career table with 5 rows, all Capitanes de Arecibo, all attributed to that same header -- no other name
appears anywhere on the capture.

season|team|games|points
1965|Capitanes, Arecibo|13|32
1966|Capitanes, Arecibo|10|12
1967|Capitanes, Arecibo|18|44
1968|Capitanes, Arecibo|10|12
1969|Capitanes, Arecibo|16|74

Checked for a duplicate elsewhere in the dataset: every id with a Capitanes-de-Arecibo row in 1965-1969 (176,
721, 1103, 1851, 1886, 1931, 2258) has a distinct games/points combination -- 721's table is not a copy of
anyone else's, and no other id carries these exact 5 rows.

## 3. 722 has no career rows

player_career_seasons.csv has zero rows for id 722 -- it is an enciclopedia-only stub (same name, same jersey
23, same DOB as 721, no profile page, no bio, no box rows). Nothing about 722 conflicts with itself.

## 4. Ages shown are derived from the DOB, not independently stated

Neither page that shows an "Edad" field states it as free text pulled from a separate record -- both times it
equals exactly (capture year minus 1980), on two different pages two years apart (27 in 2007, 25 in 2005). The
enciclopedia listing shows no age field at all, only jersey and DOB. This is circumstantial (bsnpr.com's own
server code was not inspected) but consistent throughout: nothing suggests "Edad" is a second, independently
sourced data point; it reads as computed at page-generation time.

## 5. No independent (non-bsnpr.com) source found

Web search for "Francisco Llovet" + San German/BSN, "Llovet Ayala" + Arecibo/Capitanes, and Capitanes de
Arecibo rosters 1965-1969 generally: no hits naming this player specifically on Wikipedia, proballers, RealGM
or any other indexed source. UNVERIFIED -- no independent DOB or 1960s-roster source exists in the record.

## 6. The 47 orphan game_box_player.csv rows -- a finding, logged, NOT linked

data/clean/game_box_player.csv carries 47 rows across 29 distinct games for "Llovet, Francisco" at SAN GERMAN:
2001 (9 games, jersey 23), 2002 (14 games, jersey 11), 2003 (6 games, jersey 23) -- full stat lines, source
wayback_bsnpr_games. Every one of these 47 rows has a BLANK bsnpr_id: none are linked to 721, 722, or any other
id. game_box_player.csv's season coverage is 2001-2013 overall; it has zero rows before 2001, so it can
neither confirm nor rule out the 1965-1969 table either way.

This body of evidence was not surfaced in the original A05 packet (docs/specs/cluster_evidence_batch2.md),
which stated box scores had no row for either id -- true as far as id-linkage goes, but incomplete: there IS a
substantial, well-documented career under this exact name that the parsing pipeline never matched to 721,
likely because 721's own career_seasons field says 1965-1969, so nothing in 2001-2003 would look linkable to
it. San German (2001-2003 box rows, 2005 bio) and jersey 23 (enciclopedia, and 2 of 3 box seasons) line up with
each other and with a 1980 birth (age 21-23 in 2001-2003); none of that lines up with the 1965-1969 table.

Decision: this finding is logged only. Linking these 47 rows to 721 (or to a corrected id) is a separate,
larger identity decision -- not proposed or applied in this phase.

## 7. id 1947 checked -- does not share 721's shape

The user's plan asked whether id 1947 (Rivera, Raul: canonical DOB 8/31/1982, one career row in 1963 for
Capitanes de Arecibo) has the same shape as 721 (one page asserting both a real DOB and a conflicting career
row). Checked directly: NO.
Source: https://web.archive.org/web/20070930203415/http://www.bsnpr.com/jugadores/jugador.asp?id=1947&e=2
This capture -- the one cited as 1947's birth_date source -- shows Nacimiento 1/1/1900, Edad 107, Posicion "No
se sabe": a sentinel/placeholder for "unknown", not a real value. The actual 8/31/1982 in players_canonical.csv
comes from a DIFFERENT capture (jugador05.asp, 2005-03-22, digest AMBTJ6T4CQW3QJBFOPFYVF6ENYTY4Z6T: "Edad: 22",
"Fecha: 8/31/1982"), but the canonical row's source_url citation points at the jugador.asp capture instead --
a mislabeled citation, not a within-page conflict. Because the page that carries the 1963 career row never
itself asserts a real DOB, 1947 is excluded from this phase's flag list. The citation mismatch is a separate,
smaller finding, not corrected here.

## 8. Fix options considered

A. Hide the DOB, flag it as a source discrepancy. Rejected: the DOB is the one value on this record that
   appears more than once (3 bsnpr.com pages, all one source family, not independent of each other) and is
   never contradicted anywhere; hiding it would suppress the one recurring fact and leave the actually
   out-of-place data (the career table) unflagged.
B. CHOSEN. Keep the DOB visible (with attribution, "segun bsnpr.com" -- never called verified). Flag the 5
   career rows: they stay visible on 721's page, marked, excluded from the career totals, with a neutral note.
   Reuses the app's existing "row stays, marked, excluded from totals" display pattern (built for same-season
   stat conflicts); the data model is new (a hand-curated, single-row flag list, since there is no second
   conflicting row here and no known owner), read by both parse_players.py (validates the list still matches
   the career CSV) and build_web_data.py (publishes it to data_quality.json).
C. Do nothing, log as an open question only. Rejected: leaves an internally-contradictory profile page live
   with no flag at all.

## 9. What this phase applied

data/interim/disputed_career_rows.csv: 5 rows, all id 721, one per season (1965-1969), with evidence/evidence_es
citing this document. src/parse_players.py: load_disputed_rows() / check_disputed_rows() (validate-only, never
drops a row). src/build_web_data.py: data_quality.json gains disputed_rows (5) and counts.disputed_career_rows.
app/bsn_archivo.html: season rows tagged "No concuerda con la ficha"; totals footnote gains a count-driven
clause; bio DOB line gains "(segun bsnpr.com)" for a flagged player only; new Calidad de datos section
"Temporadas que no concuerdan con la ficha", titled to not read as a subsection of the existing "Fechas de
nacimiento" (DOB-vs-DOB) section, which is a different mechanism. Exact wording approved by the owner before
this file was written; see the phase's own approval messages for the string-by-string sign-off.
