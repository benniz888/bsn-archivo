/* PHASE_1_SPLIT STEP 8. Every remaining tab-rendering function, plus navigation-building
   code step 4 deliberately left out of helpers.js, plus the fourth game ("Quien soy?") step 7
   correctly left behind since it wasn't named for that step. Byte for byte, no renaming, no
   reformatting, no reordering among themselves. Loaded via <script src="js/tabs.js"> right after
   js/games.js, before the rest (init.js territory, a later step).

   Four segments, none contiguous with each other in the original (same situation as every prior
   step) -- the gaps between them are the things that could NOT move this step, see below:

   - SEG1: ARENAS through POOL_BSN26 -- leftover Historia/Hoy/Equipos/Refuerzos tab DATA that
     wasn't named for js/data.js in step 3 (that step took only the explicitly named big
     constants). Includes the small F.agu.ru.push(2026)/F.*.coach patch statements between the
     old POOL and VENUES positions -- bare code, safe, only assigns onto F, already in js/data.js.
   - SEG2: the "IMAGE DROP-IN LAYER" section (crest/portrait SVG rendering) through the
     "SORTABLE / EXPORTABLE TABLE" section (buildTable and friends -- extensively used by nearly
     every tab builder, never named for js/helpers.js in step 4) through NAVIGATION (buildNav,
     the mega-menu, _showPanel, TABS/VIEW_SECS/syncSubnav -- explicitly named this step) through
     every named tab (HOY, HISTORIA, EQUIPOS, the player-profile machinery including showPlayer,
     RECORDS, REFUERZOS, FUENTES, the Ask/Bio feature, QUERY BUILDER, the Hub, GLOSARIO, PRIMER)
     through buildProfile/exportProfile/resetProfile and the section labelled "PERFIL" (which,
     confusingly, is actually the profile STORAGE layer -- PROFILE_KEY/loadProfile/prof/
     saveProfile/setProf -- not the render function; named PERFIL in the original regardless).
   - SEG3: "Quien soy?" (QZ/statClue/newQuiz/drawQuiz/revealClue/guessQuiz -- named this step)
     through COMPARAR (the player-comparison feature). Stops at drawCompare -- does NOT include
     the BOOT array that follows it in the original (see the real bug below).
   - SEG4: the view-router infrastructure (VIEW_MAP, _mkView, _subnavEl, VIEW_DESC, buildLanding,
     buildJuegaViews, buildViews), slug_, revealNode, and applyHash (routing, analogous to
     setHash/showView/showTab already in js/helpers.js).

   LEFT INLINE, not moved this step (web/index.html still has a good chunk of the original script
   left in it -- init.js territory, not this step's job to sort further):
   - The CAPA DE IDIOMA IIFE (`(function translate(){...})()`) and the whole DERIVED section
     (champOf/ruOf/deriveChampions, YEARS/LAST/NSEASONS/FKEYS/ACTIVE/NOTES/POOL_NAME_ALIAS/
     FAME_W/fame, plus four more merge/derive IIFEs) -- core data-postprocessing, not tab-
     specific, and FKEYS in particular has to stay wherever it's computed (see next point).
   - CAT_KEYS and GRID_CLUBS (STILL inline since step 7 -- GRID_CLUBS = FKEYS.filter(...) is a
     top-level `const`, and FKEYS is computed in this same inline script; moving either without
     also moving FKEYS itself would repeat step 7's FKEYS bug). THEME (osTheme through
     initTheme) sits in the same "leave inline" island, between SEG2 and SEG3.
   - const BOOT=[...] -- a REAL bug, found by the real-browser test, not a static check: BOOT is
     a top-level array literal that stores bare function REFERENCES (['tema',initTheme],
     ['nav',buildNav], ...), evaluated the instant its own script runs. Every other entry points
     at a function already in an earlier-loading split file (safe), but ['tema',initTheme] points
     at THEME's initTheme, which stays inline -- moving BOOT into js/tabs.js (an earlier-loading
     file than the inline remainder) threw "ReferenceError: initTheme is not defined" at
     js/tabs.js's own load time, which aborted the rest of ITS top-level execution -- GAMES,
     VIEW_MAP and everything declared after BOOT in js/tabs.js's physical file order silently
     never initialized (a SEPARATE symptom, "Cannot access 'GAMES' before initialization", showed
     up wherever the app tried to use them). Exactly the GRID_CLUBS/FKEYS shape of bug again (step
     7), but on an ARRAY of references instead of a single one, and easy to miss precisely because
     almost every OTHER entry in the same array is perfectly safe. Fixed by leaving the whole
     const BOOT=[...] array inline -- every one of its references (including initTheme) is safe
     there, since the inline remainder always loads last, after every split file AND itself.
   - ARRANQUE (splashProgress, hideSplash, SPLASH_DEADLINE, ligaFold, finishBoot, runBoot, and
     the setInterval(checkRollover,60000) statement) -- the actual boot sequence, not a tab.
   - hydrate() and the final bootstrap statements (window.addEventListener('hashchange',
     applyHash), runBoot(), the service-worker registration) -- these must stay exactly where
     they are: they are what actually STARTS the app, after every other script (including this
     one) has finished loading.

   tests/_app_text.py's `_INSERTION_ORDER` was rebuilt from scratch this step, computed directly
   from every group's marker's byte offset in app/bsn_archivo.html (not incrementally patched):
   this step's 4 segments interleave with 8 of js/data.js's 13 groups, js/data-quality.js's
   group, 3 of js/helpers.js's groups, js/player.js's JUGADORES-archive group, and
   js/games.js's HL_SETS-adjacent group. Verified: app_text() still reconstructs
   app/bsn_archivo.html byte for byte. Replaced entirely once app/bsn_archivo.html becomes the
   archived pointer (step 11/12 of the split).

   STEP 10 (cleanup): MVP_YEARS, SEASON_AWARDS, FINALS_BY_YEAR, OWNERS -- appended at the end of
   this file, moved byte for byte from web/index.html, where their consumers (buildMVPYears,
   buildSeasonAwards, buildFinalsByYear, buildOwners) already lived. Step 9 flagged these as tab
   data that fell inside step 8's SEG-boundary lines by accident of position, not deliberate
   classification, and left them inline since step 9's own scope was js/init.js. Checked for the
   GRID_CLUBS/BOOT failure shape before moving: pure data, no top-level immediate-execution
   hazard (verified directly -- see the STEP 10 commit message). */

const ARENAS=[
  ["Atléticos de San Germán","San Germán","Arquelio Torres Ramírez Coliseum",5000],
  ["Cangrejeros de Santurce","Santurce","Roberto Clemente Coliseum",9000],
  ["Capitanes de Arecibo","Arecibo","Manuel Iguina Coliseum",12000],
  ["Criollos de Caguas","Caguas","Coliseo Roger Mendoza",3000],
  ["Santeros de Aguada","Aguada","Ismael Delgado Coliseum",6000],
  ["Gigantes de Carolina","Canóvanas","Carlos Miguel Mangual Coliseum",5000],
  ["Indios de Mayagüez","Mayagüez","Palacio de Recreación y Deportes",5500],
  ["Leones de Ponce","Ponce","Juan Pachín Vicéns Auditorium",11000],
  ["Mets de Guaynabo","Gurabo","Fernando Hernández Coliseum",3500],
  ["Osos de Manatí","Manatí","Juan Cruz Abreu Coliseum",8000],
  ["Piratas de Quebradillas","Quebradillas","Raymond Dalmau Coliseum",5500],
  ["Vaqueros de Bayamón","Bayamón","Rubén Rodríguez Coliseum",12000]
];

const LEADERS={
 points:[
  [1,"Georgie Torres","SG","1975–2001",15863,679,23.4],
  [2,"Mario Morales","SF","1975–1998",15293,675,22.7],
  [3,"Mario Butler","C","1980–2008",12252,779,15.7],
  [4,"Rolando Frazer","C","1980–2001",12096,603,20.1],
  [5,"Raymond Dalmau","PG","1966–1985",11592,537,21.6],
  [6,"Rubén Rodríguez","PF","1969–1991",11549,631,18.3],
  [7,"Roberto Ríos","PG","1978–2000",11312,681,16.6],
  [8,"Ángel Santiago","SF","1973–1996",11287,617,18.3],
  [9,"José Quiñones","PF","1976–1995",11012,579,19.0],
  [10,"Christian Dalmau","PG","1992–2003, 2009–2017",10570,639,16.5]],
 rebounds:[
  [1,"Mario Butler","C","1980–2008",8236,779,10.6],
  [2,"Rubén Rodríguez","F/C","1969–1991",6178,631,9.8],
  [3,"Rolando Frazer","C","1980–2001",6153,603,10.2],
  [4,"Raymond Dalmau","F/C","1966–1985",5673,537,10.6],
  [5,"Mario Morales","G/F","1975–1998",5665,675,8.4],
  [6,"José «Piculín» Ortiz","C","1980–2006",5314,505,10.5],
  [7,"Carlos Bermúdez","F","1970–1984",4884,422,11.6],
  [8,"Edgar de León","F/C","1981–2001",4837,493,9.8],
  [9,"Teófilo Cruz","C","1957–1982",4672,584,8.0],
  [10,"Ángel Santiago","F","1973–1996",4447,617,7.2]],
 assists:[
  [1,"James Carter","PG","1987–2006",3025,543,5.6],
  [2,"Christian Dalmau","PG/SG","1992–2003, 2009–2017",2931,639,4.6],
  [3,"Pablo Alicea","PG","1987–2006",2762,503,5.5],
  [4,"Javier Antonio Colón","PG","1987–2008",2748,555,5.0],
  [5,"Federico López","PG","1981–1997",2440,446,5.5],
  [6,"Wilfredo Pagán","PG","1992–2018",2367,652,3.6],
  [7,"Roberto Ríos","G/F","1978–2000",2315,681,3.4],
  [8,"Raymond Dalmau","F/C","1966–1985",2302,537,5.1],
  [9,"Bobby Joe Hatton","PG","1994–2012",2235,489,4.6],
  [10,"Georgie Torres","G/F","1975–2001",2203,679,3.2]]
};

const MVP_REPEAT=[["Juan «Pachín» Vicéns",4],["Teófilo Cruz",4],["Mario «Quijote» Morales",4],
  ["Juan Báez",3],["Raymond Dalmau",3],["Georgie Torres",3],["Christian Dalmau",3]];

const SCORING=[
  [1966,"Jaime Frontera","Capitanes de Arecibo","total",400],
  [1967,"Adolfo Porrata","Capitalinos de San Juan","total",516],
  [1968,"Raymond Dalmau","Piratas de Quebradillas","total",499],
  [1969,"Neftalí Rivera","Piratas de Quebradillas","total",602],
  [1970,"Raymond Dalmau","Piratas de Quebradillas","total",546],
  [1971,"Teófilo Cruz","Cangrejeros de Santurce","ppg",22.4],
  [1972,"Samuel Betancourt","Santos de San Juan","ppg",26.9],
  [1973,"Neftalí Rivera","Piratas de Quebradillas","ppg",25.2],
  [1974,"Héctor Blondet","Capitanes de Arecibo","ppg",25.1],
  [1975,"Samuel Betancourt","Santos de San Juan","ppg",22.9],
  [1976,"Samuel Betancourt","Santos de San Juan","ppg",21.9],
  [1977,"Georgie Torres","Cariduros de Fajardo","ppg",30.1],
  [1978,"Georgie Torres","Cariduros de Fajardo","ppg",29.1],
  [1979,"Georgie Torres","Cariduros de Fajardo","ppg",32.9],
  [1980,"Mario Morales","Cangrejeros de Santurce","ppg",32.9],
  [1981,"Rolando Frazer","Polluelos de Aibonito","ppg",33.4],
  [1982,"Rolando Frazer","Polluelos de Aibonito","ppg",34.2],
  [1983,"Jim Maldonado","Capitanes de Arecibo","ppg",30.6],
  [1984,"Georgie Torres","Cariduros de Fajardo","ppg",28.8],
  [1985,"Georgie Torres","Cariduros de Fajardo","ppg",33.5],
  [1986,"Georgie Torres","Cariduros de Fajardo","ppg",29.8],
  [1987,"Georgie Torres","Cariduros de Fajardo","ppg",35.5],
  [1988,"Edgar de León","Cariduros de Fajardo","ppg",29.5],
  [1989,"Wesley Correa","Titanes de Morovis","ppg",30.9],
  [1990,"Edgar de León","Cariduros de Fajardo","ppg",31.8],
  [1991,"Edwin Pellot","Gallitos de Isabela","ppg",31.5]
];

const RECORDS=[
  ["Points, single game","79","Neftalí Rivera",1974,"22 May 1974. Thirty-four field goals, every one a two-pointer — the three-point line had not been adopted."],
  ["Assists, single game","33","Jonathan García",2012,"1 May 2012, Caciques de Humacao against Brujos de Guayama. Broke Pablo Alicea's 25 from 1989 and stands as an unofficial world record."],
  ["Points, career","15,863","Georgie Torres",2001,"679 games. His first seven seasons were played before the three-point line existed."],
  ["Rebounds, career","6,178","Rubén Rodríguez",1991,"631 games."],
  ["Points, single season","810","Rubén Rodríguez",1978,""],
  ["Rebounds, single season","380","Rubén Rodríguez",1978,"Stood thirty years until Lee Benson broke it in 2008."],
  ["Team points, single game","130","Caciques de Humacao",2012,"Same game as García's assist record."],
  ["Team points, one quarter","46","Caciques de Humacao",2012,"Ten-minute quarter."],
  ["Attendance","17,621","Vaqueros de Bayamón",1969,"8 September 1969 against Río Piedras. Beat the previous high of 16,564 for a Ponce–Santurce game."],
  ["Wins, single season","29","Vaqueros de Bayamón",1993,""],
  ["Consecutive titles","5","Vaqueros de Bayamón",1975,"1971 through 1975."]
];

const COACHES=[
  ["Red Holzman","Leones de Ponce","Naismith Hall of Fame. Coached in Ponce during the 1950s and 60s."],
  ["Jack Ramsay","Leones de Ponce","Naismith Hall of Fame."],
  ["Tex Winter","Leones de Ponce","Naismith Hall of Fame. Architect of the triangle offence."],
  ["Phil Jackson","Piratas de Quebradillas, Gallitos de Isabela","Coached in the BSN in the late 1980s, before Chicago."],
  ["Gene Bartow","—",""],["Lou Rossini","—",""],["Del Harris","—",""],
  ["P. J. Carlesimo","—",""],["Bernie Bickerstaff","—",""],["Herb Brown","—",""],
  ["Sergio Hernández","—",""]
];

const NBA_PLAYERS=[
  ["Butch Lee","First BSN player to win an NBA title."],
  ["Georgie Torres","First Puerto Rican to sign an NBA contract."],
  ["José «Piculín» Ortiz","Went on to the NBA after starting in the BSN."],
  ["Ramón Rivas","Started in the BSN."],
  ["Daniel Santiago","Started in the BSN."],
  ["Carlos Arroyo","Started in the BSN."],
  ["J. J. Barea","Started in the BSN."]
];


const STONE=[
 ["Raymond Dalmau","Raymond Dalmau Coliseum · Quebradillas","Home of the Piratas, the only club he played for."],
 ["Rubén Rodríguez","Rubén Rodríguez Coliseum · Bayamón","The league's largest arena at 12,000."],
 ["Juan «Pachín» Vicéns","Juan Pachín Vicéns Auditorium · Ponce","Capacity 11,000."],
 ["Mario Morales","Mario Morales Coliseum · Guaynabo","Home of the Mets."]
];


const REF_TIMELINE=[
 ["2024","Caguas win with three","The Criollos took the title carrying three imports — a right no other club held. Their owner, John Herrero, pushed to extend it league-wide."],
 ["17 Oct 2024","The board votes it through","The BSN board of directors approved three imports per club for 2025 with no nationality restriction, on an 11–2 vote. The Gigantes de Carolina voted against."],
 ["Oct–Nov 2024","The players push back","The players' association rejected the amendment. Gary Browne, Walter Hodge, Chris Ortiz and Ángel Rodríguez recorded a video opposing it. The measure opened eleven new import slots and cut native roster spots from thirteen to twelve."],
 ["2025","Thirty-six imports","The season ran with three per club. Eleven arrived from Australia's NBL; Mayagüez filled all three of its slots from that league. Caguas and Bayamón kept the same trio all year, while Ponce signed ten."],
 ["Oct 2025","Kept for 2026","The board reaffirmed the three-import format for 2026 and added the change limits. Bayamón opened the season with Jae Crowder, Jaylin Galloway and Xavier Cooks."]
];

const REF_SCORERS=[
 [1,"Emmanuel Mudiay","Piratas de Quebradillas","import",779,23.6],
 [2,"Kobi Simmons","Gigantes de Carolina","import",647,20.2],
 [3,"Cheick Diallo","Osos de Manatí","import",636,19.3],
 [4,"Sam Waardenburg","Indios de Mayagüez","import",585,17.2],
 [5,"Ysmael Romero","Mets de Guaynabo","nativizado",578,18.6]
];

/* ---------- season calendar ---------- */
const CALENDAR=[
 {y:2026,n:"97th",start:"21 March",regEnd:"28 June",po:"9 July",games:34,teams:12,
  fmt:"Two conferences. A conference champion is crowned first, then the final.",
  opener:"Leones de Ponce at Indios de Mayagüez, 8:00 pm, Palacio de Recreación y Deportes",
  note:"Playoffs were pushed to July so players could be released for FIBA's third qualifying window for the 2027 World Cup, 29 June to 7 July. Puerto Rico played Canada on 3 July and the Bahamas on 6 July."},
 {y:2025,n:"96th",start:"22 March",regEnd:"30 June",po:"—",games:34,teams:12,
  fmt:"Season ran to 11 August with the final.",opener:"—",
  note:"First season with three imports per club."},
 {y:2024,n:"95th",start:"3 April",regEnd:"1 July",po:"13 July",games:34,teams:12,
  fmt:"Tie-breaker and play-in 10–12 July, then all rounds best-of-seven.",opener:"—",
  note:"Season closed 30 August."}
];
const NEXT_SEASON={
  headline:"The 2027 dates have not been announced yet.",
  body:"The last three seasons opened on 3 April, 22 March and 21 March, so late March is the pattern to expect. The board normally settles dates in the off-season, and the third-import format has been reviewed each November. The women's league, the BSNF, opens its 2026–27 season on 12 September 2026."
};

/* Milestones, each carrying how much it can be trusted. 'confirmado'
   is a date somebody announced; 'proyectado' is this archive doing
   arithmetic on three past seasons; 'patrón' is a thing that has
   happened every year but has no date attached. Mixing those three
   without labelling them is how an archive starts inventing facts. */
const CAL_MILESTONES=[
  {d:'2026-09-12', k:'confirmado', t:'Arranca el BSNF 2026-27',
   b:'La liga femenina abre temporada. Es la próxima fecha anunciada del baloncesto '
    +'puertorriqueño, y la única de esta lista que no depende de un patrón.'},
  {d:null, m:'Noviembre de 2026', k:'patrón', t:'Revisión del formato de refuerzos',
   b:'La regla de importados se ha revisado cada noviembre, incluida la de tres por club '
    +'que entró en 2025. No hay fecha anunciada para esta.'},
  {d:null, m:'Receso 2026-27', k:'patrón', t:'La junta fija las fechas de 2027',
   b:'Las fechas suelen salir en el receso, no con mucha antelación.'},
  {d:'2027-03-21', k:'proyectado', t:'Apertura estimada del BSN 2027',
   b:'Estimado por este archivo, no anunciado por la liga. Las últimas tres temporadas '
    +'abrieron el 21 de marzo, el 22 de marzo y el 3 de abril.'}
];

/* The recurring shape of a BSN year, stated as a range because that is
   what three seasons support — a single date here would be a guess
   wearing a suit. */
const CAL_SHAPE=[
  {w:'Finales de marzo', t:'Apertura', b:'21 de marzo en 2026, 22 de marzo en 2025, 3 de abril en 2024.'},
  {w:'Finales de junio', t:'Cierre de la fase regular', b:'34 juegos por equipo, 12 equipos. 28 de junio en 2026.'},
  {w:'Julio', t:'Playoffs', b:'9 de julio en 2026. En 2024 hubo desempate y repechaje antes.'},
  {w:'Agosto', t:'Final', b:'El último juego de 2026 fue el 23 de agosto.'},
  {w:'Septiembre a febrero', t:'Receso', b:'Sin juegos. Se fijan fechas, se revisa el formato y se mueven los refuerzos.'}
];


/* ---------- 2025 finals, game by game ---------- */
const FINALS_2025={
 title:"2025 Final — La Final Brava",sub:"Vaqueros de Bayamón beat Leones de Ponce 4–1",
 mvp:"Danilo Gallinari",
 games:[
  ["Game 1","3 Aug","Leones de Ponce",76,"Vaqueros de Bayamón",92,"0–1","19–25, 18–12, 14–31, 25–24"],
  ["Game 2","5 Aug","Vaqueros de Bayamón",76,"Leones de Ponce",90,"1–1",""],
  ["Game 3","7 Aug","Leones de Ponce",79,"Vaqueros de Bayamón",100,"1–2",""],
  ["Game 4","9 Aug","Vaqueros de Bayamón",88,"Leones de Ponce",79,"3–1",""],
  ["Game 5","11 Aug","Leones de Ponce",68,"Vaqueros de Bayamón",82,"1–4",""]
 ]};

/* ---------- standings (only seasons captured in full) ---------- */
const STANDINGS={
 2009:{teams:11,games:30,rows:[["Capitanes de Arecibo",23,7],["Piratas de Quebradillas",22,8],
   ["Cangrejeros de Santurce",21,9],["Vaqueros de Bayamón",20,10],["Gigantes de Carolina",17,13],
   ["Atléticos de San Germán",16,14],["Indios de Mayagüez",14,16],["Leones de Ponce",13,17],
   ["Criollos de Caguas",8,22],["Mets de Guaynabo",7,23],["Caciques de Humacao",4,26]],
   note:"Bayamón finished fourth and won the title."}
};

const CLINCHERS=[
 [2026,"Vaqueros de Bayamón","Back-to-back","Renaldo Balkman took Finals MVP at 41 years old."],
 [2025,"Vaqueros de Bayamón","82–68, Game 5","Seventeenth title. Danilo Gallinari Finals MVP."],
 [2024,"Criollos de Caguas","Series over Manatí","Travis Trice Finals MVP at 20.9 points and 6.1 assists."],
 [2023,"Gigantes de Carolina","80–60, Game 5","First championship in franchise history."],
 [2020,"Vaqueros de Bayamón","84–75, Game 3","Won in a hotel bubble with no fans."],
 [2017,"Piratas de Quebradillas","98–90, Game 7","Over Arecibo, on 9 August."],
 [2012,"Indios de Mayagüez","22–8 record","The only title in the franchise's history."],
 [2009,"Vaqueros de Bayamón","Over Quebradillas","Christian Dalmau Finals MVP. Bayamón had finished fourth."]
];

const CHANNELS=[
 ["Official site","bsnpr.com","https://www.bsnpr.com/","Scores, calendar, standings and player pages."],
 ["YouTube","Baloncesto Superior Nacional PR","https://www.youtube.com/@BaloncestoSuperiorNacionalPR","Highlights and full-game uploads."],
 ["Instagram","@bsnpr","https://www.instagram.com/bsnpr/","Clips and daily posts."],
 ["TikTok","@bsnpr","https://www.tiktok.com/@bsnpr","Short-form highlights."],
 ["X","@bsnpr","https://x.com/bsnpr","Live updates."],
 ["Facebook","BSN PR","https://www.facebook.com/bsnpr/","Broadcasts and announcements."],
 ["Mobile app","iOS","https://apps.apple.com/us/app/baloncesto-superior-nacional/id6479825880","The league's own app."],
 ["Mobile app","Android","https://play.google.com/store/apps/details?id=io.genius.bsnpr","Built on Genius Sports."]
];

/* ============================================================
   2026 — the season that just ended.

   Everything below was verified against Puerto Rican press
   (El Nuevo Día, Primera Hora, Telemundo PR, El Vocero, Noticel)
   and against the league's own app, captured 2 September 2026.
   The 2026 title was "provisional" in the previous build; it is
   now confirmed, so the flag has been removed rather than left
   hedging a fact we can source.
   ============================================================ */

/* Aguada's first finals appearance since their 2019 title.
   Patched onto F rather than edited inline so the provenance of
   every runner-up stays traceable to one place. */
F.agu.ru.push(2026);
F.agu.coach = 'Rafael «Pachy» Cruz';
F.cag.coach = 'Wilhelmus Caanen';
F.san.coach = '—';

/* Temporal venue status — separate from VENUES so a one-off caveat doesn't
   force every entry to carry unused trailing nulls, and is a one-line
   delete once it stops being true. */
const VENUE_NOTES = {
  gua:'Los Mets juegan la temporada 2026 en Gurabo mientras el Coliseo Mario «Quijote» Morales pasa por una remodelación de $17M; el regreso se espera en 2028.'
};
/* One sourced line of team lore per active club — HOF "arena named for
   him" tags, the team-page plan's Wikipedia/PlateaPR-cited nickname/lore,
   or a fact confirmed by web search. Arecibo has none of those (the
   source table is blank for it too, not just missed here) and falls back
   to a live-derived line in showTeam(). Caciques de Humacao intentionally
   absent — D-045 (Grises/Humacao split) is unresolved; defunct franchises
   are a later phase. Full sourcing: docs/specs/bsn_team_page_plan.md. */
const TEAM_LORE = {
  bay:'Cinco títulos seguidos, 1971–1975 — la dinastía más larga de la liga. El juego de 1969 contra Río Piedras reunió 17.621 personas, récord de asistencia del BSN.',
  que:'Raymond Dalmau y Neftalí Rivera, el «Dynamic Duo» de 1966–69, encendieron la dinastía de los 70 (4 títulos). Dalmau tiene la cancha nombrada en su honor.',
  man:'El único club activo sin título — el más joven de la liga, y el que todavía se lo debe a su fanaticada.',
  gua:'Mario «Quijote» Morales, 4× MVP y campeón de anotación en 1980, tiene la cancha del club nombrada en su honor.',
  pon:'Juan «Pachín» Vicéns, 4× MVP, tiene el auditorio del club nombrado en su honor — «el Coliseo de Ponce» para la fanaticada.',
  sge:'Conocido como «La Cuna» — y, para su fanaticada, «el hogar del monstruo anaranjado».',
  san:'Los Cangrejeros dejaron el histórico Coliseo José Miguel Agrelot por el Coliseo Roberto Clemente, en San Juan, en 2021.',
  may:'Mayagüez es conocida como «la Sultana del Oeste» — el Palacio de Recreación y Deportes ha sido su cancha desde 1981.',
  cag:'El Coliseo Roger Mendoza es, para la fanaticada criolla, «La Presión».',
  agu:'El Coliseo Ismael «Chavalillo» Delgado se construyó para los Juegos Centroamericanos y del Caribe de 2010.',
  car:'Los Gigantes se mudaron de Carolina a Canóvanas en 2025 tras no llegar a acuerdo con el municipio de Carolina por el uso del Coliseo Guillermo Angulo — hoy juegan como Gigantes de Carolina/Canóvanas en el Coliseo Carlos Miguel Mangual.'
};
/* backlog item 5 — region/barrio identity. A different axis from TEAM_LORE
   (that one is the club; this one is the place) — deliberately no overlap
   with it where the two facts would otherwise repeat (Mayagüez already
   uses "Sultana del Oeste" in TEAM_LORE.may, so this uses "Cuna de Hostos"
   instead). Sourced from es.wikipedia.org's own municipality pages,
   2026-09-14, one fact per active club; que has no entry — every
   "nickname" found for Quebradillas is the team's own arena identity
   already on the page, not separate town character, and this archive
   doesn't force a distinction that isn't real. agu carries a contested
   claim (Aguada vs. Aguadilla over the 1493 Columbus landing site) framed
   the same way the 1945 champion dispute already is elsewhere in this
   app — named, not silently resolved. Same active-12-only / defunct-later
   scope as VENUES/TEAM_LORE. Full sourcing: docs/specs/bsn_team_page_plan.md. */
const TOWN_LORE = {
  bay:'Bayamón es «la Ciudad del Chicharrón» — y sede del primer trapiche hidráulico de la isla, hacia 1548.',
  sge:'San Germán es la «Cuna del Baloncesto Puertorriqueño» — el deporte se introdujo en la isla en la Universidad Interamericana, allí mismo.',
  pon:'Ponce es «la Perla del Sur» — cuna del autonomismo puertorriqueño y del carnaval más antiguo de la isla.',
  san:'Santurce no es un municipio — es un barrio de San Juan, el único pueblo de Puerto Rico fundado por negros libres. Se llamó Cangrejos antes que Santurce; de ahí «Cangrejeros».',
  are:'Arecibo es «la Villa del Capitán Correa» — en 1702, una treintena de milicianos a caballo repelió un desembarco inglés.',
  gua:'Guaynabo es «la Ciudad de los Conquistadores» — en Caparra, aquí mismo, Juan Ponce de León fundó en 1509 el primer poblado español de la isla.',
  cag:'Caguas es «la Ciudad Criolla» — su nombre viene del cacique taíno Caguax, cuya corona lleva el escudo del pueblo.',
  car:'Carolina es «la Ciudad Gigante», apodo ligado a Felipe Birriel González, un carolinense de estatura excepcional — y cuna también de Roberto Clemente y Julia de Burgos. Canóvanas, su nueva sede, es el «Pueblo Valeroso».',
  may:'Mayagüez es «la Cuna de Hostos» — Eugenio María de Hostos, uno de los grandes intelectuales puertorriqueños, nació aquí en 1839.',
  agu:'Aguada se atribuye el desembarco de Cristóbal Colón en 1493 — una fecha que también reclama Aguadilla; la disputa sigue sin resolverse.',
  man:'Manatí es «la Atenas de Puerto Rico» — apodo de principios del siglo XX, cuando sus Juegos Florales y tertulias literarias eclipsaban a las de pueblos más grandes.'
};

/* Final standings, 2026 regular season. Two groups of six, 34 games.
   PCT is the league's own rounding, kept as published. */
const STAND2026 = {
  A:[['bay',22,12,.650,'14-3','8-9'],['cag',22,12,.650,'15-2','7-10'],['san',19,15,.560,'9-8','10-7'],
     ['car',18,16,.530,'9-8','9-8'],['man',15,19,.440,'11-6','4-13'],['gua',14,20,.410,'8-9','6-11']],
  B:[['sge',21,13,.620,'12-5','9-8'],['are',18,16,.530,'12-5','6-11'],['agu',17,17,.500,'10-7','7-10'],
     ['pon',15,19,.440,'10-7','5-12'],['may',13,21,.380,'6-11','7-10'],['que',10,24,.290,'7-10','3-14']]
};

/* La Final Brava 2026 — all seven games.
   Alternating home court, Sunday/Wednesday/Friday. */
const FINALS_2026 = {
  champ:'bay', ru:'agu', mvp:'Renaldo Balkman',
  note:'Primer bicampeonato desde los Leones de Ponce en 2014 y 2015. Octava final a siete juegos desde que la liga adoptó el formato de cancha local en 2002; el anfitrión del séptimo ha ganado siete de las ocho, la excepción fue Bayamón en 2010.',
  games:[
    [1,'9 ago','bay','agu',91,75,'1-0','Bayamón impone ritmo en casa.'],
    [2,'12 ago','agu','bay',86,87,'2-0','Bayamón gana como visitante por un punto. Jones sale con su quinta falta y se arranca el dorsal; lo suspenden para el tercero.'],
    [3,'14 ago','bay','agu',93,95,'2-1','Aguada gana en tiempo extra en el «rancho», sin Jones en el otro banco.'],
    [4,'16 ago','agu','bay',67,64,'2-2','Triple de Manny Camper a 45 segundos. Rigoberto Mendoza, 22 puntos, 15 en el primer parcial.'],
    [5,'19 ago','bay','agu',97,79,'3-2','Chris McCullough, 25 puntos. Bayamón llega a estar 22 arriba.'],
    [6,'21 ago','agu','bay',82,76,'3-3','Aguada borra un déficit de 16 con un avance de 22-1 en el tercero y fuerza el séptimo.'],
    [7,'23 ago','bay','agu',81,74,'4-3','Triples consecutivos de Thompson Jr. y Balkman a 2:43. Mojica sella desde la línea a 19.7 segundos.']
  ]
};

/* The two conference finals that fed it. Aguada's closing game
   against Ponce was not captured in the sources consulted. */
const SEMIS_2026 = [
  ['Final Conferencia A','bay','cag','4-2','Bayamón ganó el quinto 122-79 y cerró en Caguas — su primer triunfo como visitante en la serie.'],
  ['Final Conferencia B','agu','pon','—','Aguada dominaba 3-2 y cerró en Ponce. El marcador del juego decisivo no aparece en las fuentes consultadas.']
];

/* Scoring leaders as published in the league app. The app
   abbreviates first names; three of these five could not be
   expanded from a second source, so they are left as printed. */
const LEAD2026 = [
  ['K. Davis','man',23.4,null],
  ['J. Nowell','car',22.4,'Jaylen Nowell'],
  ['J. Perez','bay',21.4,'Jassel Pérez'],
  ['J. Nelson Jr','man',20.8,null],
  ['J. Mcveigh','are',20.4,null]
];

/* Season awards. Two sources disagree on Harrell's club — RealGM
   puts him in San Germán, Noticel in Caguas — so the row says so. */
const AWARDS_2026 = [
  ['Más Valioso','Travis Trice','Criollos de Caguas','Su segundo MVP tras el de 2024.'],
  ['MVP de la final','Renaldo Balkman','Vaqueros de Bayamón','A los 41 años.'],
  ['Dirigente del Año','Christian Dalmau','Vaqueros de Bayamón',''],
  ['Progreso del Año','André Curbelo','Atléticos de San Germán','Único nativo del Quinteto Ideal.'],
  ['Novato del Año','Daniel Rivera','Gigantes de Carolina',''],
  ['Defensor del Año','Moses Brown','Criollos de Caguas','Según RealGM.'],
  ['Sexto Hombre','Christian López','Criollos de Caguas','Según RealGM.'],
  ['Excelencia Arbitral','Jorge Vázquez','—','']
];

/* Headlines as they appeared in the league's own app on 2 Sep 2026.
   Titles only — no article text is reproduced. */
const NEWS = [
  ['25 ago','Ricardo Dalmau habla de los 96 años de la liga','El presidente del BSN, en la premiación: la liga sigue creciendo y llenando canchas.','pres'],
  ['24 ago','El Juego 7 lideró la televisión puertorriqueña','125 mil personas conectadas en YouTube, 12 mil en el Coliseo Rubén Rodríguez.','tv'],
  ['23 ago','¡Vaqueros campeones! Bayamón conquista su campeonato número 18','81-74 sobre Aguada en el séptimo.','champ'],
  ['21 ago','Rigoberto Mendoza, tras la eliminación de Aguada','El anotador dominicano habla de su grupo.','quote'],
  ['21 ago','Aguada completa la remontada y habrá Juego 7','82-76 en el Chavalillo Delgado.','game'],
  ['19 ago','Chris McCullough: la serie no se había acabado','Tras los 25 puntos del quinto juego.','quote']
];


/* Generated from bsn_2026_official.csv — bsnpr.com official player
   statistics export, 2026 regular season, retrieved 4 September 2026.
   Regular season only: it does NOT include playoff games, which is why
   these totals sit below RealGM's for the same season. */
const POOL_BSN26=[{"n":"Kendric Davis","c":["man"],"d":[2020],"gp":9,"mpg":32.7,"ppg":23.4,"rpg":2.2,"apg":4.7,"spg":1.1,"bpg":0,"tpg":2.4,"fg":0.459,"tp":0.324,"ft":0.754,"tot":{"pts":211,"reb":20,"ast":42,"stl":10,"blk":0,"min":294},"ns":1,"src":"bsnpr26","legs":[["man",9,23.4]],"pos":"PG","posSrc":"perfil","hi":[2026,23.4]},{"n":"Jaylen Nowell","c":["car"],"d":[2020],"gp":32,"mpg":30.9,"ppg":22.4,"rpg":2.8,"apg":3.5,"spg":0.8,"bpg":0.2,"tpg":2,"fg":0.511,"tp":0.424,"ft":0.824,"tot":{"pts":718,"reb":91,"ast":113,"stl":26,"blk":6,"min":990},"ns":1,"src":"bsnpr26","legs":[["car",32,22.4]],"pos":"PG","posSrc":"perfil","hi":[2026,22.4]},{"n":"Jassel Perez","c":["bay"],"d":[2020],"gp":9,"mpg":26.2,"ppg":21.4,"rpg":4,"apg":3.3,"spg":2.2,"bpg":0.3,"tpg":2.6,"fg":0.54,"tp":0.462,"ft":0.767,"tot":{"pts":193,"reb":36,"ast":30,"stl":20,"blk":3,"min":236},"ns":1,"src":"bsnpr26","legs":[["bay",9,21.4]],"pos":"PG","posSrc":"perfil","hi":[2026,21.4]},{"n":"Jack Edward McVeigh","c":["are"],"d":[2020],"gp":19,"mpg":37.3,"ppg":20.4,"rpg":5.7,"apg":3.7,"spg":0.4,"bpg":0.4,"tpg":1.6,"fg":0.473,"tp":0.343,"ft":0.855,"tot":{"pts":387,"reb":108,"ast":71,"stl":8,"blk":7,"min":708},"ns":1,"src":"bsnpr26","legs":[["are",19,20.4]],"pos":"SF","posSrc":"perfil","hi":[2026,20.4]},{"n":"Nathan Sobey","c":["may"],"d":[2020],"gp":23,"mpg":36.7,"ppg":20.2,"rpg":5,"apg":6.9,"spg":0.9,"bpg":0.2,"tpg":2.7,"fg":0.427,"tp":0.359,"ft":0.791,"tot":{"pts":465,"reb":116,"ast":158,"stl":21,"blk":5,"min":843},"ns":1,"src":"bsnpr26","legs":[["may",23,20.2]],"pos":"PG","posSrc":"perfil","hi":[2026,20.2]},{"n":"Jezreel De Jesus","c":["pon"],"d":[2020],"gp":29,"mpg":33.6,"ppg":20,"rpg":2.9,"apg":4.2,"spg":0.9,"bpg":0.1,"tpg":1.7,"fg":0.489,"tp":0.389,"ft":0.834,"tot":{"pts":580,"reb":83,"ast":121,"stl":27,"blk":2,"min":973},"ns":1,"src":"bsnpr26","legs":[["pon",29,20]],"pos":"PG","posSrc":"perfil","hi":[2026,20]},{"n":"Emmanuel Mudiay","c":["que"],"d":[2020],"gp":31,"mpg":35.8,"ppg":19.6,"rpg":4.4,"apg":5.8,"spg":0.8,"bpg":0.1,"tpg":1.9,"fg":0.427,"tp":0.349,"ft":0.767,"tot":{"pts":609,"reb":135,"ast":179,"stl":25,"blk":4,"min":1110},"ns":1,"src":"bsnpr26","legs":[["que",31,19.6]],"pos":"PG","posSrc":"perfil","hi":[2026,19.6]},{"n":"Jameer Nelson Jr","c":["man","que"],"d":[2020],"gp":24,"mpg":32.8,"ppg":19,"rpg":3.7,"apg":3.9,"spg":2.1,"bpg":0.4,"tpg":2.4,"fg":0.495,"tp":0.345,"ft":0.795,"tot":{"pts":457,"reb":89,"ast":94,"stl":50,"blk":10,"min":788},"ns":1,"src":"bsnpr26","legs":[["man",15,20.8],["que",9,16.1]],"pos":"PG","posSrc":"perfil","hi":[2026,19]},{"n":"Moses Brown","c":["cag"],"d":[2020],"gp":32,"mpg":24.3,"ppg":18.9,"rpg":10.6,"apg":0.7,"spg":0.5,"bpg":1.8,"tpg":1.6,"fg":0.643,"tp":0,"ft":0.519,"tot":{"pts":605,"reb":339,"ast":21,"stl":16,"blk":56,"min":777},"ns":1,"src":"bsnpr26","legs":[["cag",32,18.9]],"pos":"C","posSrc":"perfil","hi":[2026,18.9]},{"n":"Tyrell Harrison","c":["may"],"d":[2020],"gp":24,"mpg":29.2,"ppg":18.7,"rpg":9.7,"apg":1.2,"spg":0.6,"bpg":1.3,"tpg":2.4,"fg":0.642,"tp":0.429,"ft":0.555,"tot":{"pts":448,"reb":233,"ast":29,"stl":15,"blk":30,"min":701},"ns":1,"src":"bsnpr26","legs":[["may",24,18.7]],"pos":"C","posSrc":"perfil","hi":[2026,18.7]},{"n":"Travis Trice","c":["cag"],"d":[2020],"gp":34,"mpg":31.1,"ppg":18.4,"rpg":3.3,"apg":10.1,"spg":1.6,"bpg":0.1,"tpg":2.1,"fg":0.446,"tp":0.367,"ft":0.878,"tot":{"pts":625,"reb":113,"ast":343,"stl":54,"blk":2,"min":1059},"ns":1,"src":"bsnpr26","legs":[["cag",34,18.4]],"pos":"PG","posSrc":"perfil","hi":[2026,18.4]},{"n":"Malik Beasley","c":["san"],"d":[2020],"gp":17,"mpg":28.1,"ppg":18.4,"rpg":4.2,"apg":1.8,"spg":1.2,"bpg":0.1,"tpg":1.8,"fg":0.387,"tp":0.303,"ft":0.822,"tot":{"pts":312,"reb":71,"ast":30,"stl":21,"blk":1,"min":478},"ns":1,"src":"bsnpr26","legs":[["san",17,18.4]],"pos":"SF","posSrc":"perfil","hi":[2026,18.4]},{"n":"Brandon Knight","c":["gua"],"d":[2020],"gp":20,"mpg":31.8,"ppg":18,"rpg":3.7,"apg":6.3,"spg":1.1,"bpg":0.1,"tpg":3.1,"fg":0.47,"tp":0.376,"ft":0.78,"tot":{"pts":359,"reb":73,"ast":125,"stl":21,"blk":2,"min":635},"ns":1,"src":"bsnpr26","legs":[["gua",20,18]],"pos":"PG","posSrc":"perfil","hi":[2026,18]},{"n":"Rigoberto Mendoza","c":["agu"],"d":[2020],"gp":33,"mpg":33,"ppg":17.6,"rpg":6.3,"apg":4.7,"spg":1.6,"bpg":0.3,"tpg":1.8,"fg":0.534,"tp":0.351,"ft":0.711,"tot":{"pts":582,"reb":207,"ast":154,"stl":52,"blk":10,"min":1090},"ns":1,"src":"bsnpr26","legs":[["agu",33,17.6]],"pos":"SF","posSrc":"perfil","hi":[2026,17.6]},{"n":"Ramses J. Melendez Vega","c":["are"],"d":[2020],"gp":23,"mpg":29.4,"ppg":17.5,"rpg":5.2,"apg":2.3,"spg":0.8,"bpg":0.7,"tpg":1.7,"fg":0.549,"tp":0.442,"ft":0.708,"tot":{"pts":403,"reb":120,"ast":52,"stl":18,"blk":15,"min":677},"ns":1,"src":"bsnpr26","legs":[["are",23,17.5]],"pos":"SF","posSrc":"perfil","hi":[2026,17.5]},{"n":"Ysmael Romero","c":["gua"],"d":[2020],"gp":32,"mpg":29.1,"ppg":17.4,"rpg":8.1,"apg":2.8,"spg":0.8,"bpg":0.4,"tpg":1.5,"fg":0.578,"tp":0.161,"ft":0.509,"tot":{"pts":557,"reb":260,"ast":89,"stl":24,"blk":14,"min":930},"ns":1,"src":"bsnpr26","legs":[["gua",32,17.4]],"pos":"PF","posSrc":"perfil","hi":[2026,17.4]},{"n":"Eugene German","c":["may"],"d":[2020],"gp":8,"mpg":32.8,"ppg":17.4,"rpg":3.5,"apg":4.5,"spg":0.6,"bpg":0.1,"tpg":2.6,"fg":0.435,"tp":0.305,"ft":0.875,"tot":{"pts":139,"reb":28,"ast":36,"stl":5,"blk":1,"min":262},"ns":1,"src":"bsnpr26","legs":[["may",8,17.4]],"pos":"PG","posSrc":"perfil","hi":[2026,17.4]},{"n":"Alfonso Plummer","c":["are"],"d":[2020],"gp":9,"mpg":32.1,"ppg":17.3,"rpg":1.6,"apg":4.8,"spg":0.7,"bpg":0.2,"tpg":2,"fg":0.456,"tp":0.403,"ft":0.875,"tot":{"pts":156,"reb":14,"ast":43,"stl":6,"blk":2,"min":289},"ns":1,"src":"bsnpr26","legs":[["are",9,17.3]],"pos":"PG","posSrc":"perfil","hi":[2026,17.3]},{"n":"Montrezl Harrell","c":["sge"],"d":[2020],"gp":29,"mpg":31.3,"ppg":17.2,"rpg":10,"apg":2.7,"spg":0.6,"bpg":0.6,"tpg":1.5,"fg":0.615,"tp":0.188,"ft":0.667,"tot":{"pts":500,"reb":291,"ast":78,"stl":18,"blk":17,"min":908},"ns":1,"src":"bsnpr26","legs":[["sge",29,17.2]],"pos":"C","posSrc":"perfil","hi":[2026,17.2]},{"n":"Timothy Soares","c":["are"],"d":[2020],"gp":25,"mpg":31.1,"ppg":17,"rpg":7.8,"apg":2.3,"spg":0.7,"bpg":1.3,"tpg":1.8,"fg":0.523,"tp":0.318,"ft":0.608,"tot":{"pts":426,"reb":196,"ast":58,"stl":18,"blk":32,"min":778},"ns":1,"src":"bsnpr26","legs":[["are",25,17]],"pos":"PF","posSrc":"perfil","hi":[2026,17]},{"n":"Torrey Craig","c":["gua"],"d":[2020],"gp":18,"mpg":35.6,"ppg":16.9,"rpg":6.3,"apg":3.6,"spg":1.2,"bpg":1.6,"tpg":1.3,"fg":0.485,"tp":0.398,"ft":0.816,"tot":{"pts":305,"reb":113,"ast":65,"stl":22,"blk":28,"min":640},"ns":1,"src":"bsnpr26","legs":[["gua",18,16.9]],"pos":"SF","posSrc":"perfil","hi":[2026,16.9]},{"n":"Grant Basile","c":["que"],"d":[2020],"gp":13,"mpg":28.8,"ppg":16.8,"rpg":7.2,"apg":1.3,"spg":0.7,"bpg":0.6,"tpg":1.8,"fg":0.603,"tp":0.394,"ft":0.672,"tot":{"pts":218,"reb":94,"ast":17,"stl":9,"blk":8,"min":374},"ns":1,"src":"bsnpr26","legs":[["que",13,16.8]],"pos":"PF","posSrc":"perfil","hi":[2026,16.8]},{"n":"Kristian Doolittle","c":["man","car"],"d":[2020],"gp":30,"mpg":33.3,"ppg":16.6,"rpg":7.7,"apg":3.7,"spg":0.6,"bpg":0.2,"tpg":2,"fg":0.465,"tp":0.381,"ft":0.893,"tot":{"pts":498,"reb":231,"ast":111,"stl":19,"blk":6,"min":999},"ns":1,"src":"bsnpr26","legs":[["man",19,18.8],["car",11,12.8]],"pos":"PF","posSrc":"perfil","hi":[2026,16.6]},{"n":"Jaysean Paige","c":["gua"],"d":[2020],"gp":32,"mpg":31.8,"ppg":16.5,"rpg":3.3,"apg":4.1,"spg":1.3,"bpg":0.3,"tpg":2.1,"fg":0.446,"tp":0.396,"ft":0.809,"tot":{"pts":528,"reb":107,"ast":131,"stl":43,"blk":9,"min":1019},"ns":1,"src":"bsnpr26","legs":[["gua",32,16.5]],"pos":"PG","posSrc":"perfil","hi":[2026,16.5]},{"n":"Hunter Tyson","c":["car"],"d":[2020],"gp":23,"mpg":28.8,"ppg":16.5,"rpg":5.5,"apg":1.7,"spg":0.5,"bpg":0.4,"tpg":1.3,"fg":0.509,"tp":0.42,"ft":0.774,"tot":{"pts":379,"reb":126,"ast":39,"stl":11,"blk":10,"min":662},"ns":1,"src":"bsnpr26","legs":[["car",23,16.5]],"pos":"SF","posSrc":"perfil","hi":[2026,16.5]},{"n":"Louis King","c":["cag"],"d":[2020],"gp":33,"mpg":30.5,"ppg":16.3,"rpg":6.6,"apg":3.9,"spg":1.2,"bpg":0.6,"tpg":2.5,"fg":0.485,"tp":0.435,"ft":0.734,"tot":{"pts":539,"reb":218,"ast":130,"stl":38,"blk":20,"min":1005},"ns":1,"src":"bsnpr26","legs":[["cag",33,16.3]],"pos":"PF","posSrc":"perfil","hi":[2026,16.3]},{"n":"Tremont Waters","c":["car"],"d":[2020],"gp":30,"mpg":31.6,"ppg":16.3,"rpg":2.5,"apg":6.8,"spg":1.9,"bpg":0.2,"tpg":3.2,"fg":0.386,"tp":0.299,"ft":0.889,"tot":{"pts":488,"reb":75,"ast":204,"stl":57,"blk":5,"min":948},"ns":1,"src":"bsnpr26","legs":[["car",30,16.3]],"pos":"PG","posSrc":"perfil","hi":[2026,16.3]},{"n":"Malik Williams","c":["gua"],"d":[2020],"gp":5,"mpg":30.2,"ppg":16.2,"rpg":9.6,"apg":2.8,"spg":1,"bpg":1.2,"tpg":1,"fg":0.525,"tp":0.364,"ft":0.7,"tot":{"pts":81,"reb":48,"ast":14,"stl":5,"blk":6,"min":151},"ns":1,"src":"bsnpr26","legs":[["gua",5,16.2]],"pos":"C","posSrc":"perfil","hi":[2026,16.2]},{"n":"Cheick Diallo","c":["man"],"d":[2020],"gp":12,"mpg":28.6,"ppg":15.9,"rpg":8.3,"apg":0.9,"spg":0.6,"bpg":0.6,"tpg":2,"fg":0.62,"tp":null,"ft":0.804,"tot":{"pts":191,"reb":99,"ast":11,"stl":7,"blk":7,"min":343},"ns":1,"src":"bsnpr26","legs":[["man",12,15.9]],"pos":"PF","posSrc":"perfil","hi":[2026,15.9]},{"n":"Maxwell Abmas","c":["gua"],"d":[2020],"gp":10,"mpg":30.8,"ppg":15.9,"rpg":2.6,"apg":5.4,"spg":0.5,"bpg":0,"tpg":1.6,"fg":0.505,"tp":0.4,"ft":0.926,"tot":{"pts":159,"reb":26,"ast":54,"stl":5,"blk":0,"min":308},"ns":1,"src":"bsnpr26","legs":[["gua",10,15.9]],"pos":"PG","posSrc":"perfil","hi":[2026,15.9]},{"n":"Nick Perkins","c":["sge"],"d":[2020],"gp":34,"mpg":28.4,"ppg":15.8,"rpg":6.3,"apg":2.1,"spg":0.4,"bpg":0.4,"tpg":1.4,"fg":0.463,"tp":0.313,"ft":0.755,"tot":{"pts":538,"reb":214,"ast":73,"stl":13,"blk":14,"min":965},"ns":1,"src":"bsnpr26","legs":[["sge",34,15.8]],"pos":"PF","posSrc":"perfil","hi":[2026,15.8]},{"n":"Andre Curbelo","c":["sge"],"d":[2020],"gp":28,"mpg":28.1,"ppg":15.7,"rpg":6.4,"apg":6.7,"spg":1.4,"bpg":0.2,"tpg":2.8,"fg":0.492,"tp":0.315,"ft":0.805,"tot":{"pts":439,"reb":179,"ast":187,"stl":39,"blk":6,"min":787},"ns":1,"src":"bsnpr26","legs":[["sge",28,15.7]],"pos":"PF","posSrc":"perfil","hi":[2026,15.7]},{"n":"John Jenkins lll","c":["agu"],"d":[2020],"gp":8,"mpg":29,"ppg":15.4,"rpg":2.4,"apg":1.1,"spg":0.6,"bpg":0,"tpg":1.8,"fg":0.466,"tp":0.431,"ft":0.765,"tot":{"pts":123,"reb":19,"ast":9,"stl":5,"blk":0,"min":232},"ns":1,"src":"bsnpr26","legs":[["agu",8,15.4]],"pos":"SG","posSrc":"perfil","hi":[2026,15.4]},{"n":"Jalen Bernard Crutcher","c":["pon"],"d":[2020],"gp":28,"mpg":32.3,"ppg":15.2,"rpg":3.5,"apg":6.1,"spg":0.7,"bpg":0.1,"tpg":2,"fg":0.488,"tp":0.415,"ft":0.831,"tot":{"pts":425,"reb":98,"ast":172,"stl":19,"blk":3,"min":903},"ns":1,"src":"bsnpr26","legs":[["pon",28,15.2]],"pos":"PG","posSrc":"perfil","hi":[2026,15.2]},{"n":"Xavier Cooks","c":["bay"],"d":[2020],"gp":16,"mpg":21.9,"ppg":15.2,"rpg":6.7,"apg":1.8,"spg":0.6,"bpg":1.1,"tpg":1.3,"fg":0.687,"tp":0,"ft":0.552,"tot":{"pts":243,"reb":107,"ast":29,"stl":9,"blk":17,"min":350},"ns":1,"src":"bsnpr26","legs":[["bay",16,15.2]],"pos":"C","posSrc":"perfil","hi":[2026,15.2]},{"n":"Olumiye Oni","c":["man","may"],"d":[2020],"gp":12,"mpg":35.4,"ppg":14.6,"rpg":6.8,"apg":6.5,"spg":1.2,"bpg":0.3,"tpg":2.5,"fg":0.397,"tp":0.341,"ft":0.729,"tot":{"pts":175,"reb":81,"ast":78,"stl":14,"blk":4,"min":425},"ns":1,"src":"bsnpr26","legs":[["man",6,12.3],["may",6,16.8]],"pos":"PG","posSrc":"perfil","hi":[2026,14.6]},{"n":"Corey Jae Crowder","c":["bay"],"d":[2020],"gp":29,"mpg":26.6,"ppg":14.4,"rpg":5.8,"apg":2.9,"spg":1.4,"bpg":0.5,"tpg":1.1,"fg":0.415,"tp":0.314,"ft":0.767,"tot":{"pts":419,"reb":167,"ast":83,"stl":41,"blk":14,"min":770},"ns":1,"src":"bsnpr26","legs":[["bay",29,14.4]],"pos":"PF","posSrc":"perfil","hi":[2026,14.4]},{"n":"Terence Davis","c":["pon"],"d":[2020],"gp":10,"mpg":28.9,"ppg":14.3,"rpg":5,"apg":3.9,"spg":1.7,"bpg":0,"tpg":1.9,"fg":0.459,"tp":0.349,"ft":0.864,"tot":{"pts":143,"reb":50,"ast":39,"stl":17,"blk":0,"min":289},"ns":1,"src":"bsnpr26","legs":[["pon",10,14.3]],"pos":"PG","posSrc":"perfil","hi":[2026,14.3]},{"n":"Thomas Robinson","c":["pon","que","are","may"],"d":[2020],"gp":28,"mpg":25.8,"ppg":14.2,"rpg":9.6,"apg":1.5,"spg":0.6,"bpg":0.3,"tpg":1.9,"fg":0.589,"tp":0,"ft":0.608,"tot":{"pts":398,"reb":268,"ast":43,"stl":18,"blk":9,"min":722},"ns":1,"src":"bsnpr26","legs":[["pon",10,12.6],["que",8,19.1],["are",8,11.1],["may",2,15]],"pos":"C","posSrc":"perfil","hi":[2026,14.2]},{"n":"Damian Jones","c":["bay"],"d":[2020],"gp":7,"mpg":24.9,"ppg":14.1,"rpg":5.6,"apg":1.1,"spg":0.3,"bpg":2.1,"tpg":1,"fg":0.75,"tp":0.143,"ft":0.867,"tot":{"pts":99,"reb":39,"ast":8,"stl":2,"blk":15,"min":174},"ns":1,"src":"bsnpr26","legs":[["bay",7,14.1]],"pos":"PF","posSrc":"perfil","hi":[2026,14.1]},{"n":"Kenneth Faried","c":["san"],"d":[2020],"gp":4,"mpg":24.5,"ppg":14,"rpg":10.3,"apg":2,"spg":0.5,"bpg":1.5,"tpg":0.5,"fg":0.575,"tp":0.333,"ft":0.75,"tot":{"pts":56,"reb":41,"ast":8,"stl":2,"blk":6,"min":98},"ns":1,"src":"bsnpr26","legs":[["san",4,14]],"pos":"C","posSrc":"perfil","hi":[2026,14]},{"n":"Jaylin Galloway","c":["bay"],"d":[2020],"gp":16,"mpg":26.9,"ppg":13.8,"rpg":2.1,"apg":2.2,"spg":0.8,"bpg":0.7,"tpg":0.8,"fg":0.454,"tp":0.394,"ft":0.818,"tot":{"pts":221,"reb":34,"ast":35,"stl":13,"blk":11,"min":430},"ns":1,"src":"bsnpr26","legs":[["bay",16,13.8]],"pos":"SG","posSrc":"perfil","hi":[2026,13.8]},{"n":"Jordan Murphy","c":["pon"],"d":[2020],"gp":29,"mpg":24.3,"ppg":13.7,"rpg":5.8,"apg":0.8,"spg":0.4,"bpg":0.6,"tpg":1.2,"fg":0.541,"tp":0.391,"ft":0.638,"tot":{"pts":396,"reb":167,"ast":24,"stl":13,"blk":17,"min":705},"ns":1,"src":"bsnpr26","legs":[["pon",29,13.7]],"pos":"PF","posSrc":"perfil","hi":[2026,13.7]},{"n":"Sam Waardenburg","c":["may"],"d":[2020],"gp":20,"mpg":32.9,"ppg":13.7,"rpg":7.3,"apg":3.7,"spg":0.8,"bpg":1.1,"tpg":1.7,"fg":0.484,"tp":0.349,"ft":0.824,"tot":{"pts":274,"reb":145,"ast":73,"stl":16,"blk":21,"min":658},"ns":1,"src":"bsnpr26","legs":[["may",20,13.7]],"pos":"PF","posSrc":"perfil","hi":[2026,13.7]},{"n":"Ian Clark","c":["san"],"d":[2020],"gp":16,"mpg":24.7,"ppg":13.7,"rpg":2.3,"apg":2.6,"spg":0.4,"bpg":0.2,"tpg":1.3,"fg":0.494,"tp":0.489,"ft":0.933,"tot":{"pts":219,"reb":37,"ast":42,"stl":7,"blk":3,"min":395},"ns":1,"src":"bsnpr26","legs":[["san",16,13.7]],"pos":"SG","posSrc":"perfil","hi":[2026,13.7]},{"n":"Jordan Howard","c":["san"],"d":[2020],"gp":15,"mpg":28.7,"ppg":13.7,"rpg":1.6,"apg":3.8,"spg":0.3,"bpg":0,"tpg":1.1,"fg":0.455,"tp":0.489,"ft":0.875,"tot":{"pts":206,"reb":24,"ast":57,"stl":5,"blk":0,"min":431},"ns":1,"src":"bsnpr26","legs":[["san",15,13.7]],"pos":"PG","posSrc":"perfil","hi":[2026,13.7]},{"n":"Tyquan Rolon","c":["man"],"d":[2020],"gp":34,"mpg":28.8,"ppg":13.6,"rpg":2.7,"apg":3.7,"spg":0.6,"bpg":0.1,"tpg":1.6,"fg":0.505,"tp":0.399,"ft":0.774,"tot":{"pts":462,"reb":91,"ast":125,"stl":21,"blk":2,"min":978},"ns":1,"src":"bsnpr26","legs":[["man",34,13.6]],"pos":"PG","posSrc":"perfil","hi":[2026,13.6]},{"n":"Kendall Munson","c":["que"],"d":[2020],"gp":9,"mpg":26.1,"ppg":13.4,"rpg":7.8,"apg":1.7,"spg":0.8,"bpg":0.3,"tpg":1.6,"fg":0.544,"tp":0.444,"ft":0.76,"tot":{"pts":121,"reb":70,"ast":15,"stl":7,"blk":3,"min":235},"ns":1,"src":"bsnpr26","legs":[["que",9,13.4]],"pos":"C","posSrc":"perfil","hi":[2026,13.4]},{"n":"Derrick Walton","c":["are"],"d":[2020],"gp":26,"mpg":30,"ppg":13.2,"rpg":4,"apg":8.8,"spg":1,"bpg":0.1,"tpg":2.6,"fg":0.46,"tp":0.325,"ft":0.829,"tot":{"pts":343,"reb":103,"ast":230,"stl":25,"blk":2,"min":779},"ns":1,"src":"bsnpr26","legs":[["are",26,13.2]],"pos":"PG","posSrc":"perfil","hi":[2026,13.2]},{"n":"Stephen Thompson Jr.","c":["bay"],"d":[2020],"gp":22,"mpg":22.8,"ppg":13.1,"rpg":3.4,"apg":2.5,"spg":0.9,"bpg":0.3,"tpg":1.6,"fg":0.463,"tp":0.398,"ft":0.695,"tot":{"pts":289,"reb":74,"ast":54,"stl":20,"blk":6,"min":501},"ns":1,"src":"bsnpr26","legs":[["bay",22,13.1]],"pos":"PG","posSrc":"perfil","hi":[2026,13.1]},{"n":"Arguster Daniels IV","c":["sge"],"d":[2020],"gp":6,"mpg":29.8,"ppg":13,"rpg":4.7,"apg":3.5,"spg":0.2,"bpg":0.2,"tpg":1.8,"fg":0.508,"tp":0.364,"ft":0.75,"tot":{"pts":78,"reb":28,"ast":21,"stl":1,"blk":1,"min":179},"ns":1,"src":"bsnpr26","legs":[["sge",6,13]],"pos":"PG","posSrc":"perfil","hi":[2026,13]},{"n":"Avry Holmes","c":["pon"],"d":[2020],"gp":6,"mpg":32.5,"ppg":13,"rpg":3.7,"apg":4.2,"spg":0.7,"bpg":0.2,"tpg":1.7,"fg":0.483,"tp":0.5,"ft":0.688,"tot":{"pts":78,"reb":22,"ast":25,"stl":4,"blk":1,"min":195},"ns":1,"src":"bsnpr26","legs":[["pon",6,13]],"pos":"PG","posSrc":"perfil","hi":[2026,13]},{"n":"Jacob Wiley","c":["agu"],"d":[2020],"gp":24,"mpg":24.6,"ppg":12.8,"rpg":6.1,"apg":2.6,"spg":1.1,"bpg":1,"tpg":1.2,"fg":0.558,"tp":0.349,"ft":0.59,"tot":{"pts":308,"reb":146,"ast":62,"stl":26,"blk":23,"min":591},"ns":1,"src":"bsnpr26","legs":[["agu",24,12.8]],"pos":"PF","posSrc":"perfil","hi":[2026,12.8]},{"n":"Brady Manek","c":["pon"],"d":[2020],"gp":19,"mpg":30.6,"ppg":12.8,"rpg":7.3,"apg":2.6,"spg":0.8,"bpg":0.5,"tpg":0.7,"fg":0.425,"tp":0.352,"ft":0.619,"tot":{"pts":243,"reb":138,"ast":50,"stl":16,"blk":9,"min":581},"ns":1,"src":"bsnpr26","legs":[["pon",19,12.8]],"pos":"PF","posSrc":"perfil","hi":[2026,12.8]},{"n":"Tyler Cook","c":["man"],"d":[2020],"gp":19,"mpg":21.8,"ppg":12.8,"rpg":6,"apg":2.2,"spg":0.5,"bpg":0.5,"tpg":1.7,"fg":0.639,"tp":0,"ft":0.597,"tot":{"pts":244,"reb":114,"ast":41,"stl":10,"blk":10,"min":414},"ns":1,"src":"bsnpr26","legs":[["man",19,12.8]],"pos":"PF","posSrc":"perfil","hi":[2026,12.8]},{"n":"John Brown III","c":["agu"],"d":[2020],"gp":12,"mpg":32.4,"ppg":12.8,"rpg":7.4,"apg":3.2,"spg":2.2,"bpg":0,"tpg":1.8,"fg":0.488,"tp":0.333,"ft":0.684,"tot":{"pts":154,"reb":89,"ast":38,"stl":26,"blk":0,"min":389},"ns":1,"src":"bsnpr26","legs":[["agu",12,12.8]],"pos":"PF","posSrc":"perfil","hi":[2026,12.8]},{"n":"Walter Hodge Jr.","c":["san"],"d":[2020],"gp":19,"mpg":25.4,"ppg":12.7,"rpg":1.5,"apg":3.8,"spg":1.1,"bpg":0.1,"tpg":1.7,"fg":0.444,"tp":0.367,"ft":0.879,"tot":{"pts":241,"reb":29,"ast":72,"stl":21,"blk":1,"min":482},"ns":1,"src":"bsnpr26","legs":[["san",19,12.7]],"pos":"PG","posSrc":"perfil","hi":[2026,12.7]},{"n":"Christian Lopez Santiago","c":["cag"],"d":[2020],"gp":28,"mpg":21,"ppg":12.6,"rpg":2.7,"apg":1.8,"spg":0.6,"bpg":0.1,"tpg":1.4,"fg":0.474,"tp":0.515,"ft":0.92,"tot":{"pts":353,"reb":75,"ast":50,"stl":16,"blk":2,"min":588},"ns":1,"src":"bsnpr26","legs":[["cag",28,12.6]],"pos":"SG","posSrc":"perfil","hi":[2026,12.6]},{"n":"Phillip Wheeler","c":["que"],"d":[2020],"gp":22,"mpg":22.9,"ppg":12.6,"rpg":3,"apg":1.1,"spg":0.6,"bpg":0.5,"tpg":1.4,"fg":0.471,"tp":0.347,"ft":0.81,"tot":{"pts":278,"reb":66,"ast":25,"stl":14,"blk":11,"min":503},"ns":1,"src":"bsnpr26","legs":[["que",22,12.6]],"pos":"SF","posSrc":"perfil","hi":[2026,12.6]},{"n":"Ryan Arcidiacono","c":["man"],"d":[2020],"gp":10,"mpg":27.9,"ppg":12.6,"rpg":3.9,"apg":4.4,"spg":0.9,"bpg":0,"tpg":2.3,"fg":0.489,"tp":0.314,"ft":0.725,"tot":{"pts":126,"reb":39,"ast":44,"stl":9,"blk":0,"min":279},"ns":1,"src":"bsnpr26","legs":[["man",10,12.6]],"pos":"PG","posSrc":"perfil","hi":[2026,12.6]},{"n":"Darius Bazley","c":["pon"],"d":[2020],"gp":11,"mpg":29.5,"ppg":12.5,"rpg":10.5,"apg":3,"spg":0.9,"bpg":0.8,"tpg":2,"fg":0.543,"tp":0.412,"ft":0.517,"tot":{"pts":138,"reb":115,"ast":33,"stl":10,"blk":9,"min":325},"ns":1,"src":"bsnpr26","legs":[["pon",11,12.5]],"pos":"C","posSrc":"perfil","hi":[2026,12.5]},{"n":"Justin Reyes","c":["are"],"d":[2020],"gp":25,"mpg":16.6,"ppg":12.4,"rpg":3.4,"apg":1.5,"spg":0.4,"bpg":0.8,"tpg":1.5,"fg":0.613,"tp":0.345,"ft":0.754,"tot":{"pts":309,"reb":85,"ast":38,"stl":11,"blk":19,"min":415},"ns":1,"src":"bsnpr26","legs":[["are",25,12.4]],"pos":"SF","posSrc":"perfil","hi":[2026,12.4]},{"n":"George Alexander Hamilton","c":["sge"],"d":[2020],"gp":22,"mpg":30.7,"ppg":12.3,"rpg":4.5,"apg":4.6,"spg":1.2,"bpg":0.3,"tpg":1.7,"fg":0.535,"tp":0.4,"ft":0.761,"tot":{"pts":271,"reb":99,"ast":101,"stl":26,"blk":7,"min":676},"ns":1,"src":"bsnpr26","legs":[["sge",22,12.3]],"pos":"PG","posSrc":"perfil","hi":[2026,12.3]},{"n":"Angel Rodriguez","c":["san"],"d":[2020],"gp":30,"mpg":25,"ppg":12.2,"rpg":3.4,"apg":6.2,"spg":1.7,"bpg":0.1,"tpg":2.3,"fg":0.44,"tp":0.431,"ft":0.812,"tot":{"pts":366,"reb":101,"ast":187,"stl":50,"blk":3,"min":749},"ns":1,"src":"bsnpr26","legs":[["san",30,12.2]],"pos":"PG","posSrc":"perfil","hi":[2026,12.2]},{"n":"Davon Jefferson","c":["san","may"],"d":[2020],"gp":29,"mpg":27.3,"ppg":12,"rpg":7.9,"apg":1.8,"spg":0.6,"bpg":0.5,"tpg":1.3,"fg":0.639,"tp":0.2,"ft":0.807,"tot":{"pts":347,"reb":230,"ast":53,"stl":16,"blk":14,"min":793},"ns":1,"src":"bsnpr26","legs":[["san",25,11.4],["may",4,15.5]],"pos":"PF","posSrc":"perfil","hi":[2026,12]},{"n":"Devin Williams","c":["gua"],"d":[2020],"gp":25,"mpg":26.2,"ppg":11.9,"rpg":8.9,"apg":1.4,"spg":0.7,"bpg":0.1,"tpg":1.1,"fg":0.528,"tp":0.417,"ft":0.574,"tot":{"pts":298,"reb":223,"ast":35,"stl":18,"blk":3,"min":655},"ns":1,"src":"bsnpr26","legs":[["gua",25,11.9]],"pos":"C","posSrc":"perfil","hi":[2026,11.9]},{"n":"Isaiah Hicks","c":["pon"],"d":[2020],"gp":11,"mpg":20.8,"ppg":11.9,"rpg":4.9,"apg":2,"spg":0.4,"bpg":0.6,"tpg":1.5,"fg":0.704,"tp":0.333,"ft":0.771,"tot":{"pts":131,"reb":54,"ast":22,"stl":4,"blk":7,"min":229},"ns":1,"src":"bsnpr26","legs":[["pon",11,11.9]],"pos":"PF","posSrc":"perfil","hi":[2026,11.9]},{"n":"D J Wilson","c":["san"],"d":[2020],"gp":13,"mpg":29.8,"ppg":11.8,"rpg":7.9,"apg":2.8,"spg":0.3,"bpg":0.3,"tpg":1.5,"fg":0.463,"tp":0.31,"ft":0.563,"tot":{"pts":153,"reb":103,"ast":36,"stl":4,"blk":4,"min":388},"ns":1,"src":"bsnpr26","legs":[["san",13,11.8]],"pos":"PF","posSrc":"perfil","hi":[2026,11.8]},{"n":"David Scott James Jr","c":["car"],"d":[2020],"gp":18,"mpg":22.9,"ppg":11.6,"rpg":6.6,"apg":1.3,"spg":0.3,"bpg":0.2,"tpg":1.2,"fg":0.471,"tp":0.391,"ft":0.775,"tot":{"pts":209,"reb":119,"ast":24,"stl":5,"blk":4,"min":412},"ns":1,"src":"bsnpr26","legs":[["car",18,11.6]],"pos":"PF","posSrc":"perfil","hi":[2026,11.6]},{"n":"Victor Liz","c":["que"],"d":[2020],"gp":33,"mpg":28.8,"ppg":11.4,"rpg":4.6,"apg":2.5,"spg":0.8,"bpg":0.2,"tpg":2.4,"fg":0.457,"tp":0.318,"ft":0.714,"tot":{"pts":375,"reb":153,"ast":82,"stl":26,"blk":8,"min":952},"ns":1,"src":"bsnpr26","legs":[["que",33,11.4]],"pos":"SF","posSrc":"perfil","hi":[2026,11.4]},{"n":"Isaiah Pineiro","c":["san"],"d":[2020],"gp":33,"mpg":24.1,"ppg":11.2,"rpg":4.9,"apg":1.3,"spg":0.9,"bpg":0.2,"tpg":1.3,"fg":0.507,"tp":0.337,"ft":0.798,"tot":{"pts":368,"reb":163,"ast":44,"stl":31,"blk":7,"min":794},"ns":1,"src":"bsnpr26","legs":[["san",33,11.2]],"pos":"SF","posSrc":"perfil","hi":[2026,11.2]},{"n":"Deandre Pinckney","c":["are"],"d":[2020],"gp":6,"mpg":26.5,"ppg":11,"rpg":7.7,"apg":1.7,"spg":0.8,"bpg":0.2,"tpg":1.3,"fg":0.426,"tp":0.3,"ft":0.688,"tot":{"pts":66,"reb":46,"ast":10,"stl":5,"blk":1,"min":159},"ns":1,"src":"bsnpr26","legs":[["are",6,11]],"pos":"PF","posSrc":"perfil","hi":[2026,11]},{"n":"Javier Mojica","c":["bay"],"d":[2020],"gp":34,"mpg":24.9,"ppg":10.7,"rpg":2.6,"apg":2.6,"spg":0.9,"bpg":0.1,"tpg":0.9,"fg":0.434,"tp":0.434,"ft":0.806,"tot":{"pts":365,"reb":90,"ast":90,"stl":32,"blk":4,"min":845},"ns":1,"src":"bsnpr26","legs":[["bay",34,10.7]],"pos":"SG","posSrc":"perfil","hi":[2026,10.7]},{"n":"Ivan Gandia","c":["agu"],"d":[2020],"gp":33,"mpg":24.5,"ppg":10.5,"rpg":1.8,"apg":3.3,"spg":0.7,"bpg":0.1,"tpg":0.9,"fg":0.407,"tp":0.371,"ft":0.822,"tot":{"pts":345,"reb":60,"ast":110,"stl":22,"blk":2,"min":807},"ns":1,"src":"bsnpr26","legs":[["agu",33,10.5]],"pos":"PG","posSrc":"perfil","hi":[2026,10.5]},{"n":"Theophilus A. Pinson Jr.","c":["gua"],"d":[2020],"gp":12,"mpg":30.9,"ppg":10.4,"rpg":4.3,"apg":3.7,"spg":1,"bpg":0.4,"tpg":1.8,"fg":0.345,"tp":0.311,"ft":0.667,"tot":{"pts":125,"reb":51,"ast":44,"stl":12,"blk":5,"min":371},"ns":1,"src":"bsnpr26","legs":[["gua",12,10.4]],"pos":"PG","posSrc":"perfil","hi":[2026,10.4]},{"n":"Gary Browne","c":["bay"],"d":[2020],"gp":30,"mpg":25.4,"ppg":10.2,"rpg":4.2,"apg":7,"spg":1.3,"bpg":0,"tpg":2.1,"fg":0.458,"tp":0.39,"ft":0.76,"tot":{"pts":305,"reb":127,"ast":209,"stl":38,"blk":1,"min":763},"ns":1,"src":"bsnpr26","legs":[["bay",30,10.2]],"pos":"PG","posSrc":"perfil","hi":[2026,10.2]},{"n":"Joel Soriano","c":["agu"],"d":[2020],"gp":5,"mpg":21.2,"ppg":10.2,"rpg":6,"apg":1.4,"spg":0.2,"bpg":0.4,"tpg":1.8,"fg":0.479,"tp":0,"ft":0.625,"tot":{"pts":51,"reb":30,"ast":7,"stl":1,"blk":2,"min":106},"ns":1,"src":"bsnpr26","legs":[["agu",5,10.2]],"pos":"PF","posSrc":"perfil","hi":[2026,10.2]},{"n":"Chris Ortiz","c":["man"],"d":[2020],"gp":14,"mpg":21.9,"ppg":10.1,"rpg":3.9,"apg":0.7,"spg":0.6,"bpg":0.6,"tpg":1.2,"fg":0.421,"tp":0.306,"ft":0.773,"tot":{"pts":142,"reb":54,"ast":10,"stl":9,"blk":8,"min":306},"ns":1,"src":"bsnpr26","legs":[["man",14,10.1]],"pos":"SF","posSrc":"perfil","hi":[2026,10.1]},{"n":"Antonio Ralat","c":["agu"],"d":[2020],"gp":22,"mpg":24.8,"ppg":10,"rpg":2.1,"apg":2.2,"spg":0.7,"bpg":0.2,"tpg":1.2,"fg":0.433,"tp":0.466,"ft":0.881,"tot":{"pts":221,"reb":46,"ast":48,"stl":16,"blk":4,"min":545},"ns":1,"src":"bsnpr26","legs":[["agu",22,10]],"pos":"SG","posSrc":"perfil","hi":[2026,10]},{"n":"Neftali Alvarez","c":["may"],"d":[2020],"gp":19,"mpg":18.4,"ppg":9.7,"rpg":2.1,"apg":3.3,"spg":1,"bpg":0,"tpg":1.3,"fg":0.454,"tp":0.429,"ft":0.692,"tot":{"pts":185,"reb":40,"ast":63,"stl":19,"blk":0,"min":350},"ns":1,"src":"bsnpr26","legs":[["may",19,9.7]],"pos":"PG","posSrc":"perfil","hi":[2026,9.7]},{"n":"Cady Lalanne","c":["are"],"d":[2020],"gp":8,"mpg":19.4,"ppg":9.6,"rpg":5.8,"apg":0.8,"spg":0.3,"bpg":0.4,"tpg":1.4,"fg":0.435,"tp":0.367,"ft":0.75,"tot":{"pts":77,"reb":46,"ast":6,"stl":2,"blk":3,"min":155},"ns":1,"src":"bsnpr26","legs":[["are",8,9.6]],"pos":"C","posSrc":"perfil","hi":[2026,9.6]},{"n":"Alexander Kappos","c":["cag"],"d":[2020],"gp":34,"mpg":21.4,"ppg":9.5,"rpg":3.6,"apg":1.2,"spg":0.5,"bpg":0.5,"tpg":0.5,"fg":0.492,"tp":0.396,"ft":0.8,"tot":{"pts":323,"reb":122,"ast":42,"stl":17,"blk":18,"min":727},"ns":1,"src":"bsnpr26","legs":[["cag",34,9.5]],"pos":"SF","posSrc":"perfil","hi":[2026,9.5]},{"n":"Daniel Rivera","c":["car"],"d":[2020],"gp":34,"mpg":20.6,"ppg":9.4,"rpg":4.5,"apg":1.1,"spg":0.6,"bpg":0.9,"tpg":0.9,"fg":0.63,"tp":0.357,"ft":0.638,"tot":{"pts":320,"reb":153,"ast":37,"stl":21,"blk":29,"min":702},"ns":1,"src":"bsnpr26","legs":[["car",34,9.4]],"pos":"PF","posSrc":"perfil","hi":[2026,9.4]},{"n":"Benito Santiago Jr.","c":["may"],"d":[2020],"gp":33,"mpg":20.1,"ppg":9.4,"rpg":2.5,"apg":1,"spg":0.8,"bpg":0.2,"tpg":0.6,"fg":0.469,"tp":0.447,"ft":0.746,"tot":{"pts":309,"reb":83,"ast":34,"stl":27,"blk":8,"min":662},"ns":1,"src":"bsnpr26","legs":[["may",33,9.4]],"pos":"SF","posSrc":"perfil","hi":[2026,9.4]},{"n":"Rafael A. Pinzon Duperoy","c":["are"],"d":[2020],"gp":29,"mpg":25.6,"ppg":9.4,"rpg":3.3,"apg":1.9,"spg":0.4,"bpg":0.1,"tpg":0.8,"fg":0.409,"tp":0.409,"ft":0.952,"tot":{"pts":274,"reb":95,"ast":55,"stl":12,"blk":4,"min":741},"ns":1,"src":"bsnpr26","legs":[["are",29,9.4]],"pos":"SG","posSrc":"perfil","hi":[2026,9.4]},{"n":"Angel Matias","c":["san"],"d":[2020],"gp":33,"mpg":18.9,"ppg":9.3,"rpg":3.5,"apg":1.5,"spg":0.3,"bpg":0.3,"tpg":1.1,"fg":0.492,"tp":0.368,"ft":0.87,"tot":{"pts":308,"reb":115,"ast":50,"stl":10,"blk":9,"min":624},"ns":1,"src":"bsnpr26","legs":[["san",33,9.3]],"pos":"SF","posSrc":"perfil","hi":[2026,9.3]},{"n":"Jorge L. Pacheco","c":["sge"],"d":[2020],"gp":34,"mpg":23.3,"ppg":9.1,"rpg":1.2,"apg":2.2,"spg":0.8,"bpg":0,"tpg":0.6,"fg":0.458,"tp":0.409,"ft":0.868,"tot":{"pts":309,"reb":42,"ast":76,"stl":26,"blk":0,"min":793},"ns":1,"src":"bsnpr26","legs":[["sge",34,9.1]],"pos":"SG","posSrc":"perfil","hi":[2026,9.1]},{"n":"Noah Horchler","c":["agu"],"d":[2020],"gp":8,"mpg":18.5,"ppg":9.1,"rpg":4.9,"apg":0.5,"spg":0.6,"bpg":0.6,"tpg":0.9,"fg":0.475,"tp":0.308,"ft":0.778,"tot":{"pts":73,"reb":39,"ast":4,"stl":5,"blk":5,"min":148},"ns":1,"src":"bsnpr26","legs":[["agu",8,9.1]],"pos":"PF","posSrc":"perfil","hi":[2026,9.1]},{"n":"Manuel Camper","c":["agu"],"d":[2020],"gp":31,"mpg":19.7,"ppg":9,"rpg":3.5,"apg":1.7,"spg":0.5,"bpg":0.2,"tpg":0.9,"fg":0.484,"tp":0.398,"ft":0.753,"tot":{"pts":279,"reb":109,"ast":54,"stl":16,"blk":7,"min":612},"ns":1,"src":"bsnpr26","legs":[["agu",31,9]],"pos":"SF","posSrc":"perfil","hi":[2026,9]},{"n":"Jared Ruiz","c":["may","pon"],"d":[2020],"gp":27,"mpg":22.3,"ppg":9,"rpg":2.7,"apg":2.3,"spg":0.4,"bpg":0.1,"tpg":1.4,"fg":0.403,"tp":0.385,"ft":0.781,"tot":{"pts":242,"reb":74,"ast":62,"stl":10,"blk":4,"min":603},"ns":1,"src":"bsnpr26","legs":[["may",21,10.2],["pon",6,4.7]],"pos":"SG","posSrc":"perfil","hi":[2026,9]},{"n":"Kevin Allen","c":["may"],"d":[2020],"gp":2,"mpg":14.5,"ppg":9,"rpg":2.5,"apg":1,"spg":0.5,"bpg":0,"tpg":0.5,"fg":0.75,"tp":null,"ft":0.75,"tot":{"pts":18,"reb":5,"ast":2,"stl":1,"blk":0,"min":29},"ns":1,"src":"bsnpr26","legs":[["may",2,9]],"pos":"SF","posSrc":"perfil","hi":[2026,9]},{"n":"Anthony Cowan Jr","c":["que"],"d":[2020],"gp":14,"mpg":23.9,"ppg":8.6,"rpg":1.9,"apg":3.8,"spg":0.6,"bpg":0,"tpg":1.5,"fg":0.371,"tp":0.344,"ft":0.717,"tot":{"pts":121,"reb":27,"ast":53,"stl":9,"blk":0,"min":335},"ns":1,"src":"bsnpr26","legs":[["que",14,8.6]],"pos":"PG","posSrc":"perfil","hi":[2026,8.6]},{"n":"Tjader Fernandez","c":["pon","may"],"d":[2020],"gp":30,"mpg":26.1,"ppg":8.5,"rpg":1.9,"apg":2.9,"spg":0.5,"bpg":0,"tpg":1.2,"fg":0.449,"tp":0.389,"ft":0.931,"tot":{"pts":254,"reb":57,"ast":86,"stl":16,"blk":0,"min":783},"ns":1,"src":"bsnpr26","legs":[["pon",19,6.5],["may",11,11.8]],"pos":"PG","posSrc":"perfil","hi":[2026,8.5]},{"n":"John Holland","c":["agu"],"d":[2020],"gp":12,"mpg":15.8,"ppg":8.3,"rpg":2.1,"apg":1.4,"spg":1,"bpg":0,"tpg":0.7,"fg":0.442,"tp":0.333,"ft":0.714,"tot":{"pts":100,"reb":25,"ast":17,"stl":12,"blk":0,"min":189},"ns":1,"src":"bsnpr26","legs":[["agu",12,8.3]],"pos":"SG","posSrc":"perfil","hi":[2026,8.3]},{"n":"Devon Collier","c":["san"],"d":[2020],"gp":24,"mpg":18.2,"ppg":8.2,"rpg":5.3,"apg":1.7,"spg":0.6,"bpg":0.4,"tpg":0.9,"fg":0.711,"tp":0,"ft":0.648,"tot":{"pts":197,"reb":128,"ast":40,"stl":15,"blk":10,"min":437},"ns":1,"src":"bsnpr26","legs":[["san",24,8.2]],"pos":"PF","posSrc":"perfil","hi":[2026,8.2]},{"n":"Gian Clavell","c":["que"],"d":[2020],"gp":15,"mpg":21.1,"ppg":8.2,"rpg":1.6,"apg":2.4,"spg":0.4,"bpg":0,"tpg":1,"fg":0.392,"tp":0.329,"ft":0.864,"tot":{"pts":123,"reb":24,"ast":36,"stl":6,"blk":0,"min":317},"ns":1,"src":"bsnpr26","legs":[["que",15,8.2]],"pos":"PG","posSrc":"perfil","hi":[2026,8.2]},{"n":"Zhaire Jahi-Ihme Smith","c":["que"],"d":[2020],"gp":6,"mpg":23.7,"ppg":8.2,"rpg":2,"apg":2,"spg":1.2,"bpg":0.5,"tpg":2,"fg":0.514,"tp":0.333,"ft":0.714,"tot":{"pts":49,"reb":12,"ast":12,"stl":7,"blk":3,"min":142},"ns":1,"src":"bsnpr26","legs":[["que",6,8.2]],"pos":"SG","posSrc":"perfil","hi":[2026,8.2]},{"n":"Ryan Pearson","c":["gua"],"d":[2020],"gp":4,"mpg":11.8,"ppg":8,"rpg":4.3,"apg":0.8,"spg":0.3,"bpg":0,"tpg":0.3,"fg":0.65,"tp":0.667,"ft":1,"tot":{"pts":32,"reb":17,"ast":3,"stl":1,"blk":0,"min":47},"ns":1,"src":"bsnpr26","legs":[["gua",4,8]],"pos":"C","posSrc":"perfil","hi":[2026,8]},{"n":"George Conditt IV","c":["car"],"d":[2020],"gp":22,"mpg":26.5,"ppg":7.9,"rpg":7.8,"apg":1.5,"spg":0.9,"bpg":1,"tpg":1,"fg":0.605,"tp":0,"ft":0.425,"tot":{"pts":173,"reb":172,"ast":34,"stl":19,"blk":22,"min":583},"ns":1,"src":"bsnpr26","legs":[["car",22,7.9]],"pos":"C","posSrc":"perfil","hi":[2026,7.9]},{"n":"Tyler Davis","c":["man"],"d":[2020],"gp":23,"mpg":14.5,"ppg":7.6,"rpg":5,"apg":1,"spg":0.3,"bpg":0.4,"tpg":0.9,"fg":0.598,"tp":null,"ft":0.806,"tot":{"pts":175,"reb":115,"ast":23,"stl":7,"blk":9,"min":333},"ns":1,"src":"bsnpr26","legs":[["man",23,7.6]],"pos":"C","posSrc":"perfil","hi":[2026,7.6]},{"n":"Chinanu Onuaku","c":["san"],"d":[2020],"gp":4,"mpg":23.5,"ppg":7.5,"rpg":5.3,"apg":3.8,"spg":1.5,"bpg":1.5,"tpg":2.3,"fg":0.423,"tp":0.333,"ft":0.625,"tot":{"pts":30,"reb":21,"ast":15,"stl":6,"blk":6,"min":94},"ns":1,"src":"bsnpr26","legs":[["san",4,7.5]],"pos":"PF","posSrc":"perfil","hi":[2026,7.5]},{"n":"Renaldo Balkman","c":["bay"],"d":[2020],"gp":33,"mpg":18.7,"ppg":7.2,"rpg":4.6,"apg":1.5,"spg":1.1,"bpg":0.8,"tpg":0.7,"fg":0.69,"tp":0.222,"ft":0.642,"tot":{"pts":236,"reb":152,"ast":49,"stl":35,"blk":25,"min":618},"ns":1,"src":"bsnpr26","legs":[["bay",33,7.2]],"pos":"PF","posSrc":"perfil","hi":[2026,7.2]},{"n":"Josue Erazo","c":["may"],"d":[2020],"gp":26,"mpg":21.3,"ppg":7.2,"rpg":3.8,"apg":0.9,"spg":0.6,"bpg":0.2,"tpg":0.9,"fg":0.45,"tp":0.146,"ft":0.776,"tot":{"pts":186,"reb":99,"ast":23,"stl":16,"blk":6,"min":553},"ns":1,"src":"bsnpr26","legs":[["may",26,7.2]],"pos":"SF","posSrc":"perfil","hi":[2026,7.2]},{"n":"Aleem Ford","c":["pon"],"d":[2020],"gp":6,"mpg":24.7,"ppg":7.2,"rpg":1.7,"apg":1.8,"spg":0.3,"bpg":0.3,"tpg":0.3,"fg":0.5,"tp":0.474,"ft":0.4,"tot":{"pts":43,"reb":10,"ast":11,"stl":2,"blk":2,"min":148},"ns":1,"src":"bsnpr26","legs":[["pon",6,7.2]],"pos":"SG","posSrc":"perfil","hi":[2026,7.2]},{"n":"Carlos Emory","c":["que"],"d":[2020],"gp":34,"mpg":19.6,"ppg":7.1,"rpg":4.1,"apg":0.8,"spg":0.4,"bpg":0.1,"tpg":0.4,"fg":0.434,"tp":0.381,"ft":0.833,"tot":{"pts":240,"reb":139,"ast":28,"stl":13,"blk":4,"min":668},"ns":1,"src":"bsnpr26","legs":[["que",34,7.1]],"pos":"PF","posSrc":"perfil","hi":[2026,7.1]},{"n":"Dimencio Vaughn","c":["que"],"d":[2020],"gp":14,"mpg":16.4,"ppg":7.1,"rpg":2.6,"apg":1.4,"spg":0.7,"bpg":0.2,"tpg":1.1,"fg":0.447,"tp":0.095,"ft":0.732,"tot":{"pts":100,"reb":36,"ast":19,"stl":10,"blk":3,"min":230},"ns":1,"src":"bsnpr26","legs":[["que",14,7.1]],"pos":"SF","posSrc":"perfil","hi":[2026,7.1]},{"n":"Giancarlo Rosado","c":["agu"],"d":[2020],"gp":29,"mpg":16.3,"ppg":6.9,"rpg":2.3,"apg":2.2,"spg":0.3,"bpg":0,"tpg":1.3,"fg":0.546,"tp":0.231,"ft":0.66,"tot":{"pts":200,"reb":68,"ast":64,"stl":9,"blk":0,"min":473},"ns":1,"src":"bsnpr26","legs":[["agu",29,6.9]],"pos":"PG","posSrc":"perfil","hi":[2026,6.9]},{"n":"Matthew Lee","c":["agu"],"d":[2020],"gp":31,"mpg":15.8,"ppg":6.8,"rpg":1,"apg":2.2,"spg":0.2,"bpg":0,"tpg":1,"fg":0.373,"tp":0.333,"ft":0.8,"tot":{"pts":210,"reb":32,"ast":67,"stl":7,"blk":1,"min":490},"ns":1,"src":"bsnpr26","legs":[["agu",31,6.8]],"pos":"PG","posSrc":"perfil","hi":[2026,6.8]},{"n":"Jamil Wilson","c":["man"],"d":[2020],"gp":9,"mpg":27.8,"ppg":6.8,"rpg":6.1,"apg":2.4,"spg":0.8,"bpg":1,"tpg":1.6,"fg":0.397,"tp":0.219,"ft":0.727,"tot":{"pts":61,"reb":55,"ast":22,"stl":7,"blk":9,"min":250},"ns":1,"src":"bsnpr26","legs":[["man",9,6.8]],"pos":"PF","posSrc":"perfil","hi":[2026,6.8]},{"n":"Eric Ayala","c":["gua"],"d":[2020],"gp":27,"mpg":17.5,"ppg":6.7,"rpg":1.7,"apg":1.2,"spg":0.3,"bpg":0.1,"tpg":0.3,"fg":0.434,"tp":0.413,"ft":0.704,"tot":{"pts":181,"reb":46,"ast":33,"stl":7,"blk":3,"min":472},"ns":1,"src":"bsnpr26","legs":[["gua",27,6.7]],"pos":"SG","posSrc":"perfil","hi":[2026,6.7]},{"n":"Jay Shawn Alvarez","c":["que"],"d":[2020],"gp":16,"mpg":12.1,"ppg":6.7,"rpg":2.1,"apg":0.7,"spg":0.5,"bpg":0,"tpg":0.6,"fg":0.436,"tp":0.242,"ft":0.81,"tot":{"pts":107,"reb":34,"ast":11,"stl":8,"blk":0,"min":193},"ns":1,"src":"bsnpr26","legs":[["que",16,6.7]],"pos":"SF","posSrc":"perfil","hi":[2026,6.7]},{"n":"Jordan Daniel Cintron","c":["bay"],"d":[2020],"gp":31,"mpg":16.4,"ppg":6.5,"rpg":3.3,"apg":0.8,"spg":0.5,"bpg":0.1,"tpg":0.6,"fg":0.507,"tp":0.297,"ft":0.803,"tot":{"pts":200,"reb":101,"ast":25,"stl":17,"blk":2,"min":509},"ns":1,"src":"bsnpr26","legs":[["bay",31,6.5]],"pos":"SF","posSrc":"perfil","hi":[2026,6.5]},{"n":"Jonathan Rodriguez","c":["man"],"d":[2020],"gp":30,"mpg":18.2,"ppg":6.5,"rpg":4.6,"apg":0.8,"spg":0.4,"bpg":0.1,"tpg":0.4,"fg":0.493,"tp":0.381,"ft":0.781,"tot":{"pts":195,"reb":138,"ast":23,"stl":12,"blk":3,"min":547},"ns":1,"src":"bsnpr26","legs":[["man",30,6.5]],"pos":"PF","posSrc":"perfil","hi":[2026,6.5]},{"n":"Alejandro Vazquez","c":["pon"],"d":[2020],"gp":23,"mpg":13.3,"ppg":6.5,"rpg":1.9,"apg":1,"spg":0.9,"bpg":0.1,"tpg":0.8,"fg":0.51,"tp":0.353,"ft":0.725,"tot":{"pts":149,"reb":44,"ast":24,"stl":20,"blk":3,"min":306},"ns":1,"src":"bsnpr26","legs":[["pon",23,6.5]],"pos":"SG","posSrc":"perfil","hi":[2026,6.5]},{"n":"Jonathan Zhao Olmos","c":["are"],"d":[2020],"gp":20,"mpg":13.8,"ppg":6.4,"rpg":1.7,"apg":0.7,"spg":0.2,"bpg":0.2,"tpg":0.3,"fg":0.512,"tp":0.387,"ft":0.75,"tot":{"pts":127,"reb":34,"ast":14,"stl":3,"blk":3,"min":275},"ns":1,"src":"bsnpr26","legs":[["are",20,6.4]],"pos":"SF","posSrc":"perfil","hi":[2026,6.4]},{"n":"Jamarion Sharp","c":["bay"],"d":[2020],"gp":5,"mpg":13.4,"ppg":6.4,"rpg":3.4,"apg":0.2,"spg":0,"bpg":2,"tpg":0.8,"fg":0.684,"tp":0,"ft":0.429,"tot":{"pts":32,"reb":17,"ast":1,"stl":0,"blk":10,"min":67},"ns":1,"src":"bsnpr26","legs":[["bay",5,6.4]],"pos":"C","posSrc":"perfil","hi":[2026,6.4]},{"n":"Jeff Early Jr.","c":["cag"],"d":[2020],"gp":34,"mpg":19.3,"ppg":6.3,"rpg":2.2,"apg":1.4,"spg":0.6,"bpg":0.1,"tpg":0.6,"fg":0.453,"tp":0.283,"ft":0.811,"tot":{"pts":214,"reb":76,"ast":48,"stl":22,"blk":3,"min":655},"ns":1,"src":"bsnpr26","legs":[["cag",34,6.3]],"pos":"SG","posSrc":"perfil","hi":[2026,6.3]},{"n":"Christian M. Negron","c":["pon"],"d":[2020],"gp":32,"mpg":16.7,"ppg":6.3,"rpg":3.6,"apg":0.8,"spg":0.3,"bpg":0.8,"tpg":0.5,"fg":0.667,"tp":0,"ft":0.564,"tot":{"pts":203,"reb":115,"ast":24,"stl":11,"blk":25,"min":534},"ns":1,"src":"bsnpr26","legs":[["pon",32,6.3]],"pos":"PF","posSrc":"perfil","hi":[2026,6.3]},{"n":"Johned Walker","c":["pon"],"d":[2020],"gp":28,"mpg":17.9,"ppg":6.3,"rpg":1.4,"apg":1.2,"spg":0.9,"bpg":0,"tpg":0.6,"fg":0.436,"tp":0.36,"ft":0.621,"tot":{"pts":175,"reb":40,"ast":34,"stl":24,"blk":0,"min":500},"ns":1,"src":"bsnpr26","legs":[["pon",28,6.3]],"pos":"SG","posSrc":"perfil","hi":[2026,6.3]},{"n":"Isaac Sosa","c":["car","man"],"d":[2020],"gp":32,"mpg":15.1,"ppg":6.3,"rpg":0.9,"apg":0.3,"spg":0.2,"bpg":0,"tpg":0.3,"fg":0.43,"tp":0.396,"ft":0.912,"tot":{"pts":201,"reb":28,"ast":8,"stl":7,"blk":0,"min":482},"ns":1,"src":"bsnpr26","legs":[["car",19,3.3],["man",13,10.6]],"pos":"SG","posSrc":"perfil","hi":[2026,6.3]},{"n":"Michael O Connell","c":["cag"],"d":[2020],"gp":26,"mpg":14.7,"ppg":6,"rpg":2.5,"apg":2.4,"spg":0.5,"bpg":0,"tpg":0.8,"fg":0.458,"tp":0.294,"ft":0.769,"tot":{"pts":155,"reb":64,"ast":63,"stl":13,"blk":1,"min":383},"ns":1,"src":"bsnpr26","legs":[["cag",26,6]],"pos":"PG","posSrc":"perfil","hi":[2026,6]},{"n":"Corey McKeithan","c":["san"],"d":[2020],"gp":31,"mpg":14.4,"ppg":5.9,"rpg":1,"apg":1.8,"spg":0.3,"bpg":0.1,"tpg":0.6,"fg":0.429,"tp":0.313,"ft":0.765,"tot":{"pts":183,"reb":32,"ast":55,"stl":10,"blk":2,"min":446},"ns":1,"src":"bsnpr26","legs":[["san",31,5.9]],"pos":"PG","posSrc":"perfil","hi":[2026,5.9]},{"n":"Emmanuel Andujar","c":["are"],"d":[2020],"gp":16,"mpg":20.1,"ppg":5.9,"rpg":4.8,"apg":2.3,"spg":0.5,"bpg":0.3,"tpg":1.4,"fg":0.43,"tp":0.304,"ft":0.667,"tot":{"pts":95,"reb":76,"ast":36,"stl":8,"blk":4,"min":322},"ns":1,"src":"bsnpr26","legs":[["are",16,5.9]],"pos":"PF","posSrc":"perfil","hi":[2026,5.9]},{"n":"Marlon Hargis","c":["sge"],"d":[2020],"gp":34,"mpg":15.2,"ppg":5.8,"rpg":1.1,"apg":0.4,"spg":0.6,"bpg":0.1,"tpg":0.3,"fg":0.473,"tp":0.414,"ft":0.818,"tot":{"pts":196,"reb":36,"ast":13,"stl":19,"blk":3,"min":518},"ns":1,"src":"bsnpr26","legs":[["sge",34,5.8]],"pos":"SG","posSrc":"perfil","hi":[2026,5.8]},{"n":"Antonio Gordon","c":["sge"],"d":[2020],"gp":30,"mpg":11.4,"ppg":5.8,"rpg":2.3,"apg":0.5,"spg":0.3,"bpg":0.2,"tpg":0.6,"fg":0.48,"tp":0.371,"ft":0.882,"tot":{"pts":174,"reb":68,"ast":15,"stl":8,"blk":6,"min":343},"ns":1,"src":"bsnpr26","legs":[["sge",30,5.8]],"pos":"SF","posSrc":"perfil","hi":[2026,5.8]},{"n":"Denis Clemente","c":["gua"],"d":[2020],"gp":6,"mpg":8,"ppg":5.8,"rpg":0.3,"apg":0.8,"spg":0,"bpg":0,"tpg":0.7,"fg":0.5,"tp":0.563,"ft":1,"tot":{"pts":35,"reb":2,"ast":5,"stl":0,"blk":0,"min":48},"ns":1,"src":"bsnpr26","legs":[["gua",6,5.8]],"pos":"SG","posSrc":"perfil","hi":[2026,5.8]},{"n":"Isiah Gaiter","c":["may"],"d":[2020],"gp":22,"mpg":14.9,"ppg":5.5,"rpg":1.2,"apg":2,"spg":0.5,"bpg":0.1,"tpg":0.8,"fg":0.5,"tp":0.304,"ft":0.579,"tot":{"pts":120,"reb":27,"ast":45,"stl":12,"blk":2,"min":327},"ns":1,"src":"bsnpr26","legs":[["may",22,5.5]],"pos":"PG","posSrc":"perfil","hi":[2026,5.5]},{"n":"Malachi Smith","c":["are"],"d":[2020],"gp":17,"mpg":10.9,"ppg":5.5,"rpg":1.6,"apg":2.2,"spg":0.6,"bpg":0,"tpg":1.2,"fg":0.446,"tp":0.286,"ft":0.771,"tot":{"pts":93,"reb":28,"ast":38,"stl":10,"blk":0,"min":186},"ns":1,"src":"bsnpr26","legs":[["are",17,5.5]],"pos":"PG","posSrc":"perfil","hi":[2026,5.5]},{"n":"Evander Ortiz Colon","c":["car"],"d":[2020],"gp":34,"mpg":17.9,"ppg":5.4,"rpg":1.4,"apg":2.6,"spg":0.8,"bpg":0,"tpg":0.9,"fg":0.452,"tp":0.339,"ft":0.656,"tot":{"pts":184,"reb":49,"ast":88,"stl":27,"blk":1,"min":610},"ns":1,"src":"bsnpr26","legs":[["car",34,5.4]],"pos":"PG","posSrc":"perfil","hi":[2026,5.4]},{"n":"Diego Gonzalez Pellot","c":["are"],"d":[2020],"gp":32,"mpg":15.3,"ppg":5.3,"rpg":1.8,"apg":1.9,"spg":0.8,"bpg":0.1,"tpg":0.7,"fg":0.508,"tp":0.25,"ft":0.644,"tot":{"pts":170,"reb":59,"ast":61,"stl":26,"blk":2,"min":488},"ns":1,"src":"bsnpr26","legs":[["are",32,5.3]],"pos":"PG","posSrc":"perfil","hi":[2026,5.3]},{"n":"Dyondre Dominguez","c":["car"],"d":[2020],"gp":23,"mpg":13.6,"ppg":5.2,"rpg":3,"apg":0.8,"spg":0.5,"bpg":0.3,"tpg":0.4,"fg":0.506,"tp":0.365,"ft":0.824,"tot":{"pts":119,"reb":68,"ast":18,"stl":12,"blk":7,"min":312},"ns":1,"src":"bsnpr26","legs":[["car",23,5.2]],"pos":"PF","posSrc":"perfil","hi":[2026,5.2]},{"n":"Jesus A. Cruz Galarza","c":["car"],"d":[2020],"gp":23,"mpg":14.7,"ppg":5.2,"rpg":1.4,"apg":1.1,"spg":0.3,"bpg":0.1,"tpg":0.7,"fg":0.449,"tp":0.327,"ft":0.727,"tot":{"pts":120,"reb":33,"ast":25,"stl":7,"blk":2,"min":338},"ns":1,"src":"bsnpr26","legs":[["car",23,5.2]],"pos":"SG","posSrc":"perfil","hi":[2026,5.2]},{"n":"Jayden Martinez","c":["que"],"d":[2020],"gp":14,"mpg":15.8,"ppg":5.2,"rpg":4.6,"apg":1,"spg":0.2,"bpg":0.6,"tpg":0.7,"fg":0.448,"tp":0.231,"ft":0.583,"tot":{"pts":73,"reb":64,"ast":14,"stl":3,"blk":9,"min":221},"ns":1,"src":"bsnpr26","legs":[["que",14,5.2]],"pos":"PF","posSrc":"perfil","hi":[2026,5.2]},{"n":"Giovanni Santiago","c":["man"],"d":[2020],"gp":9,"mpg":13.3,"ppg":5.2,"rpg":0.9,"apg":1.8,"spg":0.3,"bpg":0,"tpg":1,"fg":0.484,"tp":0.444,"ft":0.818,"tot":{"pts":47,"reb":8,"ast":16,"stl":3,"blk":0,"min":120},"ns":1,"src":"bsnpr26","legs":[["man",9,5.2]],"pos":"PG","posSrc":"perfil","hi":[2026,5.2]},{"n":"Michael J. Bruesewitz","c":["man"],"d":[2020],"gp":16,"mpg":14.2,"ppg":5.1,"rpg":1.6,"apg":0.6,"spg":0.4,"bpg":0,"tpg":0.4,"fg":0.37,"tp":0.418,"ft":0.8,"tot":{"pts":81,"reb":25,"ast":10,"stl":6,"blk":0,"min":227},"ns":1,"src":"bsnpr26","legs":[["man",16,5.1]],"pos":"SG","posSrc":"perfil","hi":[2026,5.1]},{"n":"David Huertas","c":["san"],"d":[2020],"gp":13,"mpg":14.8,"ppg":5.1,"rpg":1.5,"apg":1,"spg":0.2,"bpg":0,"tpg":0.2,"fg":0.382,"tp":0.303,"ft":0.824,"tot":{"pts":66,"reb":20,"ast":13,"stl":3,"blk":0,"min":193},"ns":1,"src":"bsnpr26","legs":[["san",13,5.1]],"pos":"SG","posSrc":"perfil","hi":[2026,5.1]},{"n":"Arnaldo Toro","c":["agu"],"d":[2020],"gp":10,"mpg":18,"ppg":5,"rpg":4.9,"apg":2,"spg":0.1,"bpg":0.1,"tpg":0.8,"fg":0.7,"tp":null,"ft":0.667,"tot":{"pts":50,"reb":49,"ast":20,"stl":1,"blk":1,"min":180},"ns":1,"src":"bsnpr26","legs":[["agu",10,5]],"pos":"PF","posSrc":"perfil","hi":[2026,5]},{"n":"Admiral Schofield","c":["agu"],"d":[2020],"gp":7,"mpg":13.9,"ppg":5,"rpg":2.7,"apg":1.7,"spg":0,"bpg":0,"tpg":0.9,"fg":0.382,"tp":0.346,"ft":null,"tot":{"pts":35,"reb":19,"ast":12,"stl":0,"blk":0,"min":97},"ns":1,"src":"bsnpr26","legs":[["agu",7,5]],"pos":"SF","posSrc":"perfil","hi":[2026,5]},{"n":"Isaiah Palermo","c":["bay"],"d":[2020],"gp":32,"mpg":14.4,"ppg":4.8,"rpg":1.7,"apg":0.8,"spg":0.5,"bpg":0.2,"tpg":0.4,"fg":0.4,"tp":0.296,"ft":0.636,"tot":{"pts":154,"reb":53,"ast":26,"stl":16,"blk":5,"min":460},"ns":1,"src":"bsnpr26","legs":[["bay",32,4.8]],"pos":"SF","posSrc":"perfil","hi":[2026,4.8]},{"n":"E.J. Crawford","c":["man"],"d":[2020],"gp":16,"mpg":10.7,"ppg":4.8,"rpg":1.1,"apg":0.5,"spg":0.4,"bpg":0.1,"tpg":0.3,"fg":0.519,"tp":0.412,"ft":0.75,"tot":{"pts":76,"reb":18,"ast":8,"stl":6,"blk":2,"min":171},"ns":1,"src":"bsnpr26","legs":[["man",16,4.8]],"pos":"SG","posSrc":"perfil","hi":[2026,4.8]},{"n":"Elijah Hughes","c":["car"],"d":[2020],"gp":4,"mpg":11,"ppg":4.8,"rpg":1,"apg":0.5,"spg":0,"bpg":0,"tpg":0.5,"fg":0.375,"tp":0.308,"ft":1,"tot":{"pts":19,"reb":4,"ast":2,"stl":0,"blk":0,"min":44},"ns":1,"src":"bsnpr26","legs":[["car",4,4.8]],"pos":"SG","posSrc":"perfil","hi":[2026,4.8]},{"n":"Luis D. Cuascut","c":["may"],"d":[2020],"gp":29,"mpg":12.9,"ppg":4.6,"rpg":2.2,"apg":0.7,"spg":0.4,"bpg":0.7,"tpg":0.7,"fg":0.571,"tp":0.188,"ft":0.435,"tot":{"pts":133,"reb":63,"ast":20,"stl":13,"blk":20,"min":374},"ns":1,"src":"bsnpr26","legs":[["may",29,4.6]],"pos":"SF","posSrc":"perfil","hi":[2026,4.6]},{"n":"Joshua Denton","c":["cag"],"d":[2020],"gp":25,"mpg":10.4,"ppg":4.6,"rpg":1.4,"apg":0.6,"spg":0.4,"bpg":0,"tpg":0.3,"fg":0.477,"tp":0.409,"ft":0.545,"tot":{"pts":115,"reb":35,"ast":16,"stl":10,"blk":1,"min":259},"ns":1,"src":"bsnpr26","legs":[["cag",25,4.6]],"pos":"SF","posSrc":"perfil","hi":[2026,4.6]},{"n":"Joshua Rivera","c":["car"],"d":[2020],"gp":14,"mpg":9.4,"ppg":4.6,"rpg":2.1,"apg":0.6,"spg":0.1,"bpg":0.1,"tpg":0.3,"fg":0.531,"tp":0,"ft":0.464,"tot":{"pts":65,"reb":30,"ast":9,"stl":2,"blk":1,"min":132},"ns":1,"src":"bsnpr26","legs":[["car",14,4.6]],"pos":"PF","posSrc":"perfil","hi":[2026,4.6]},{"n":"Xavier Zambrana","c":["san"],"d":[2020],"gp":15,"mpg":5.9,"ppg":4.5,"rpg":1.7,"apg":0.5,"spg":0.1,"bpg":0,"tpg":0.5,"fg":0.676,"tp":0.5,"ft":0.731,"tot":{"pts":67,"reb":25,"ast":7,"stl":2,"blk":0,"min":88},"ns":1,"src":"bsnpr26","legs":[["san",15,4.5]],"pos":"PF","posSrc":"perfil","hi":[2026,4.5]},{"n":"Jase Febres","c":["agu"],"d":[2020],"gp":14,"mpg":12.3,"ppg":4.5,"rpg":1.8,"apg":1.2,"spg":0.5,"bpg":0.2,"tpg":0.4,"fg":0.473,"tp":0.304,"ft":0.8,"tot":{"pts":63,"reb":25,"ast":17,"stl":7,"blk":3,"min":172},"ns":1,"src":"bsnpr26","legs":[["agu",14,4.5]],"pos":"SG","posSrc":"perfil","hi":[2026,4.5]},{"n":"Reinaldo Santana","c":["que"],"d":[2020],"gp":23,"mpg":13,"ppg":4.4,"rpg":1.4,"apg":2,"spg":0.3,"bpg":0,"tpg":0.9,"fg":0.42,"tp":0.25,"ft":0.633,"tot":{"pts":101,"reb":32,"ast":45,"stl":6,"blk":1,"min":300},"ns":1,"src":"bsnpr26","legs":[["que",23,4.4]],"pos":"PG","posSrc":"perfil","hi":[2026,4.4]},{"n":"Robiel Morales","c":["agu"],"d":[2020],"gp":32,"mpg":12,"ppg":4.3,"rpg":1.9,"apg":1.5,"spg":0.6,"bpg":0.1,"tpg":0.7,"fg":0.5,"tp":0.414,"ft":0.625,"tot":{"pts":136,"reb":62,"ast":48,"stl":18,"blk":3,"min":384},"ns":1,"src":"bsnpr26","legs":[["agu",32,4.3]],"pos":"PG","posSrc":"perfil","hi":[2026,4.3]},{"n":"William Cruz Rodriguez","c":["que"],"d":[2020],"gp":20,"mpg":18.5,"ppg":4.3,"rpg":2.1,"apg":1.6,"spg":0.4,"bpg":0,"tpg":0.5,"fg":0.397,"tp":0.375,"ft":0.545,"tot":{"pts":85,"reb":42,"ast":32,"stl":8,"blk":0,"min":369},"ns":1,"src":"bsnpr26","legs":[["que",20,4.3]],"pos":"SG","posSrc":"perfil","hi":[2026,4.3]},{"n":"Kyle Rose","c":["sge"],"d":[2020],"gp":25,"mpg":10.3,"ppg":4.1,"rpg":1.6,"apg":0.6,"spg":0.6,"bpg":0.2,"tpg":0.8,"fg":0.447,"tp":0.429,"ft":0.5,"tot":{"pts":102,"reb":41,"ast":16,"stl":16,"blk":5,"min":258},"ns":1,"src":"bsnpr26","legs":[["sge",25,4.1]],"pos":"SF","posSrc":"perfil","hi":[2026,4.1]},{"n":"Javier Ezquerra","c":["bay"],"d":[2020],"gp":33,"mpg":16.1,"ppg":4,"rpg":2.5,"apg":2.8,"spg":0.6,"bpg":0,"tpg":1.3,"fg":0.377,"tp":0.309,"ft":0.25,"tot":{"pts":132,"reb":84,"ast":92,"stl":21,"blk":0,"min":532},"ns":1,"src":"bsnpr26","legs":[["bay",33,4]],"pos":"PG","posSrc":"perfil","hi":[2026,4]},{"n":"Emmanuel Maldonado","c":["san"],"d":[2020],"gp":27,"mpg":11,"ppg":3.9,"rpg":1.4,"apg":1.3,"spg":0.5,"bpg":0,"tpg":0.7,"fg":0.402,"tp":0.314,"ft":1,"tot":{"pts":104,"reb":38,"ast":34,"stl":13,"blk":0,"min":297},"ns":1,"src":"bsnpr26","legs":[["san",27,3.9]],"pos":"PG","posSrc":"perfil","hi":[2026,3.9]},{"n":"Luis Hernandez","c":["bay"],"d":[2020],"gp":26,"mpg":9.3,"ppg":3.9,"rpg":2.2,"apg":0.3,"spg":0.3,"bpg":0.1,"tpg":0.5,"fg":0.5,"tp":0,"ft":0.529,"tot":{"pts":101,"reb":56,"ast":7,"stl":8,"blk":2,"min":242},"ns":1,"src":"bsnpr26","legs":[["bay",26,3.9]],"pos":"PF","posSrc":"perfil","hi":[2026,3.9]},{"n":"Richard Nunez","c":["cag"],"d":[2020],"gp":32,"mpg":11.7,"ppg":3.8,"rpg":2.1,"apg":1,"spg":0.6,"bpg":0.2,"tpg":0.5,"fg":0.505,"tp":0.381,"ft":0.714,"tot":{"pts":122,"reb":68,"ast":32,"stl":19,"blk":5,"min":373},"ns":1,"src":"bsnpr26","legs":[["cag",32,3.8]],"pos":"SF","posSrc":"perfil","hi":[2026,3.8]},{"n":"Onzie Branch","c":["sge"],"d":[2020],"gp":30,"mpg":14.3,"ppg":3.8,"rpg":2.5,"apg":1.2,"spg":0.3,"bpg":0.1,"tpg":0.7,"fg":0.462,"tp":0.333,"ft":0.607,"tot":{"pts":113,"reb":74,"ast":36,"stl":9,"blk":3,"min":429},"ns":1,"src":"bsnpr26","legs":[["sge",30,3.8]],"pos":"SF","posSrc":"perfil","hi":[2026,3.8]},{"n":"Luis Rivera Rosario","c":["cag"],"d":[2020],"gp":27,"mpg":6.9,"ppg":3.8,"rpg":0.4,"apg":1.1,"spg":0.1,"bpg":0,"tpg":0.3,"fg":0.376,"tp":0.4,"ft":0.857,"tot":{"pts":102,"reb":10,"ast":29,"stl":4,"blk":0,"min":185},"ns":1,"src":"bsnpr26","legs":[["cag",27,3.8]],"pos":"PG","posSrc":"perfil","hi":[2026,3.8]},{"n":"Jose Roman Angueira","c":["que"],"d":[2020],"gp":19,"mpg":7.7,"ppg":3.8,"rpg":1.8,"apg":0.4,"spg":0.1,"bpg":0,"tpg":0.3,"fg":0.588,"tp":0,"ft":0.722,"tot":{"pts":73,"reb":35,"ast":7,"stl":2,"blk":0,"min":147},"ns":1,"src":"bsnpr26","legs":[["que",19,3.8]],"pos":"PF","posSrc":"perfil","hi":[2026,3.8]},{"n":"Juan Pablo Pineiro","c":["are"],"d":[2020],"gp":18,"mpg":14.9,"ppg":3.8,"rpg":1.5,"apg":1.2,"spg":1.1,"bpg":0.2,"tpg":0.6,"fg":0.473,"tp":0.419,"ft":0.75,"tot":{"pts":68,"reb":27,"ast":21,"stl":19,"blk":3,"min":268},"ns":1,"src":"bsnpr26","legs":[["are",18,3.8]],"pos":"SG","posSrc":"perfil","hi":[2026,3.8]},{"n":"Brandon Boyd","c":["gua"],"d":[2020],"gp":32,"mpg":12,"ppg":3.6,"rpg":1.1,"apg":1.8,"spg":0.5,"bpg":0,"tpg":0.6,"fg":0.342,"tp":0.325,"ft":0.727,"tot":{"pts":114,"reb":35,"ast":59,"stl":16,"blk":1,"min":385},"ns":1,"src":"bsnpr26","legs":[["gua",32,3.6]],"pos":"PG","posSrc":"perfil","hi":[2026,3.6]},{"n":"Jose Carlos Placer Diaz","c":["may"],"d":[2020],"gp":21,"mpg":7.2,"ppg":3.6,"rpg":0.7,"apg":0.6,"spg":0.1,"bpg":0,"tpg":0.4,"fg":0.469,"tp":0.321,"ft":0.6,"tot":{"pts":75,"reb":14,"ast":12,"stl":3,"blk":0,"min":151},"ns":1,"src":"bsnpr26","legs":[["may",21,3.6]],"pos":"SG","posSrc":"perfil","hi":[2026,3.6]},{"n":"Jorge L. Matos","c":["sge"],"d":[2020],"gp":20,"mpg":8.3,"ppg":3.6,"rpg":1.1,"apg":0.2,"spg":0.1,"bpg":0,"tpg":0.2,"fg":0.379,"tp":0.24,"ft":0.733,"tot":{"pts":72,"reb":21,"ast":3,"stl":1,"blk":0,"min":166},"ns":1,"src":"bsnpr26","legs":[["sge",20,3.6]],"pos":"SF","posSrc":"perfil","hi":[2026,3.6]},{"n":"Vicktor Lakhin","c":["san"],"d":[2020],"gp":13,"mpg":10.6,"ppg":3.6,"rpg":3.7,"apg":0.5,"spg":0.2,"bpg":0.2,"tpg":0.4,"fg":0.421,"tp":0.25,"ft":0.8,"tot":{"pts":47,"reb":48,"ast":6,"stl":3,"blk":2,"min":138},"ns":1,"src":"bsnpr26","legs":[["san",13,3.6]],"pos":"C","posSrc":"perfil","hi":[2026,3.6]},{"n":"Julian Torres","c":["sge"],"d":[2020],"gp":13,"mpg":7.3,"ppg":3.6,"rpg":2.2,"apg":0.2,"spg":0,"bpg":0.2,"tpg":0.5,"fg":0.69,"tp":0.5,"ft":0.4,"tot":{"pts":47,"reb":28,"ast":3,"stl":0,"blk":2,"min":95},"ns":1,"src":"bsnpr26","legs":[["sge",13,3.6]],"pos":"C","posSrc":"perfil","hi":[2026,3.6]},{"n":"Alex Abreu","c":["man"],"d":[2020],"gp":25,"mpg":12.4,"ppg":3.5,"rpg":1.2,"apg":1.1,"spg":0.4,"bpg":0,"tpg":0.8,"fg":0.414,"tp":0.447,"ft":0.818,"tot":{"pts":88,"reb":30,"ast":28,"stl":9,"blk":0,"min":311},"ns":1,"src":"bsnpr26","legs":[["man",25,3.5]],"pos":"SG","posSrc":"perfil","hi":[2026,3.5]},{"n":"Wilfredo Rodriguez Valentin","c":["gua"],"d":[2020],"gp":28,"mpg":13.3,"ppg":3.4,"rpg":1.9,"apg":0.9,"spg":0.2,"bpg":0,"tpg":0.4,"fg":0.442,"tp":0.294,"ft":0.667,"tot":{"pts":94,"reb":53,"ast":25,"stl":6,"blk":0,"min":372},"ns":1,"src":"bsnpr26","legs":[["gua",28,3.4]],"pos":"SF","posSrc":"perfil","hi":[2026,3.4]},{"n":"Leandro Allende","c":["agu"],"d":[2020],"gp":24,"mpg":13.4,"ppg":3.4,"rpg":2.2,"apg":1.2,"spg":0.2,"bpg":0.1,"tpg":0.4,"fg":0.471,"tp":0.333,"ft":0.8,"tot":{"pts":82,"reb":52,"ast":28,"stl":5,"blk":3,"min":322},"ns":1,"src":"bsnpr26","legs":[["agu",24,3.4]],"pos":"SF","posSrc":"perfil","hi":[2026,3.4]},{"n":"Luis Lopez Martinez","c":["car"],"d":[2020],"gp":14,"mpg":7.4,"ppg":3.4,"rpg":1.2,"apg":2.1,"spg":0.1,"bpg":0,"tpg":0.6,"fg":0.429,"tp":0.267,"ft":0.6,"tot":{"pts":47,"reb":17,"ast":29,"stl":2,"blk":0,"min":104},"ns":1,"src":"bsnpr26","legs":[["car",14,3.4]],"pos":"PG","posSrc":"perfil","hi":[2026,3.4]},{"n":"Gilberto Clavell","c":["cag"],"d":[2020],"gp":11,"mpg":7.9,"ppg":3.4,"rpg":1.5,"apg":0.7,"spg":0,"bpg":0,"tpg":0.4,"fg":0.5,"tp":0.467,"ft":0.75,"tot":{"pts":37,"reb":16,"ast":8,"stl":0,"blk":0,"min":87},"ns":1,"src":"bsnpr26","legs":[["cag",11,3.4]],"pos":"SF","posSrc":"perfil","hi":[2026,3.4]},{"n":"Fernando Caballero Acevedo","c":["pon"],"d":[2020],"gp":7,"mpg":3.9,"ppg":3.4,"rpg":0.9,"apg":0.3,"spg":0.3,"bpg":0,"tpg":0.1,"fg":0.643,"tp":0.5,"ft":1,"tot":{"pts":24,"reb":6,"ast":2,"stl":2,"blk":0,"min":27},"ns":1,"src":"bsnpr26","legs":[["pon",7,3.4]],"pos":"PF","posSrc":"perfil","hi":[2026,3.4]},{"n":"Janiel Jafet Romer","c":["gua"],"d":[2020],"gp":28,"mpg":9.3,"ppg":3.3,"rpg":1.5,"apg":0.1,"spg":0.3,"bpg":0.1,"tpg":0.1,"fg":0.372,"tp":0.277,"ft":0.5,"tot":{"pts":91,"reb":41,"ast":2,"stl":7,"blk":3,"min":259},"ns":1,"src":"bsnpr26","legs":[["gua",28,3.3]],"pos":"SF","posSrc":"perfil","hi":[2026,3.3]},{"n":"Raymond Cintron Jr","c":["man"],"d":[2020],"gp":31,"mpg":13.1,"ppg":3.2,"rpg":0.7,"apg":1,"spg":0.7,"bpg":0,"tpg":0.4,"fg":0.344,"tp":0.317,"ft":0.8,"tot":{"pts":98,"reb":21,"ast":31,"stl":22,"blk":1,"min":405},"ns":1,"src":"bsnpr26","legs":[["man",31,3.2]],"pos":"SG","posSrc":"perfil","hi":[2026,3.2]},{"n":"Khary Mauras","c":["bay"],"d":[2020],"gp":26,"mpg":9.8,"ppg":3.2,"rpg":1,"apg":1.4,"spg":0.7,"bpg":0,"tpg":0.5,"fg":0.476,"tp":0.304,"ft":0.789,"tot":{"pts":82,"reb":25,"ast":36,"stl":19,"blk":1,"min":255},"ns":1,"src":"bsnpr26","legs":[["bay",26,3.2]],"pos":"PG","posSrc":"perfil","hi":[2026,3.2]},{"n":"Omar Figueroa","c":["pon"],"d":[2020],"gp":21,"mpg":6.9,"ppg":3.2,"rpg":0.6,"apg":0.3,"spg":0.2,"bpg":0,"tpg":0.3,"fg":0.489,"tp":0.467,"ft":0.615,"tot":{"pts":68,"reb":12,"ast":7,"stl":4,"blk":0,"min":145},"ns":1,"src":"bsnpr26","legs":[["pon",21,3.2]],"pos":"SG","posSrc":"perfil","hi":[2026,3.2]},{"n":"Chris Brady","c":["sge"],"d":[2020],"gp":10,"mpg":9.7,"ppg":3.2,"rpg":2,"apg":1.1,"spg":0.2,"bpg":0.5,"tpg":0.5,"fg":0.364,"tp":0.385,"ft":0.75,"tot":{"pts":32,"reb":20,"ast":11,"stl":2,"blk":5,"min":97},"ns":1,"src":"bsnpr26","legs":[["sge",10,3.2]],"pos":"SF","posSrc":"perfil","hi":[2026,3.2]},{"n":"Gianfranco Grafals","c":["gua"],"d":[2020],"gp":25,"mpg":6.1,"ppg":3.1,"rpg":1.2,"apg":0.4,"spg":0.3,"bpg":0.2,"tpg":0.2,"fg":0.517,"tp":0.167,"ft":0.722,"tot":{"pts":77,"reb":29,"ast":10,"stl":7,"blk":4,"min":153},"ns":1,"src":"bsnpr26","legs":[["gua",25,3.1]],"pos":"SF","posSrc":"perfil","hi":[2026,3.1]},{"n":"Hiram Huertas","c":["cag"],"d":[2020],"gp":28,"mpg":9.6,"ppg":3,"rpg":1.4,"apg":1.4,"spg":0.5,"bpg":0,"tpg":0.4,"fg":0.426,"tp":0.357,"ft":0.8,"tot":{"pts":83,"reb":40,"ast":38,"stl":15,"blk":0,"min":268},"ns":1,"src":"bsnpr26","legs":[["cag",28,3]],"pos":"PG","posSrc":"perfil","hi":[2026,3]},{"n":"Ja Kair Sanchez","c":["man"],"d":[2020],"gp":7,"mpg":2.6,"ppg":3,"rpg":0.3,"apg":0.3,"spg":0.1,"bpg":0,"tpg":0.3,"fg":1,"tp":1,"ft":1,"tot":{"pts":21,"reb":2,"ast":2,"stl":1,"blk":0,"min":18},"ns":1,"src":"bsnpr26","legs":[["man",7,3]],"pos":"PG","posSrc":"perfil","hi":[2026,3]},{"n":"Carlos A Colon","c":["san"],"d":[2020],"gp":1,"mpg":7,"ppg":3,"rpg":1,"apg":0,"spg":0,"bpg":0,"tpg":1,"fg":1,"tp":1,"ft":null,"tot":{"pts":3,"reb":1,"ast":0,"stl":0,"blk":0,"min":7},"ns":1,"src":"bsnpr26","legs":[["san",1,3]],"pos":"SF","posSrc":"perfil","hi":[2026,3]},{"n":"Christian Pizarro Rios","c":["sge"],"d":[2020],"gp":32,"mpg":9.3,"ppg":2.9,"rpg":0.7,"apg":2.2,"spg":0.4,"bpg":0,"tpg":1.1,"fg":0.348,"tp":0.278,"ft":0.941,"tot":{"pts":93,"reb":21,"ast":70,"stl":12,"blk":0,"min":297},"ns":1,"src":"bsnpr26","legs":[["sge",32,2.9]],"pos":"PG","posSrc":"perfil","hi":[2026,2.9]},{"n":"Jorge Brian Diaz","c":["are","cag"],"d":[2020],"gp":23,"mpg":8.6,"ppg":2.8,"rpg":1.7,"apg":0.4,"spg":0.2,"bpg":0.3,"tpg":0.4,"fg":0.667,"tp":0.333,"ft":0.8,"tot":{"pts":65,"reb":38,"ast":9,"stl":4,"blk":6,"min":198},"ns":1,"src":"bsnpr26","legs":[["are",12,2.9],["cag",11,2.7]],"pos":"SF","posSrc":"perfil","hi":[2026,2.8]},{"n":"Miguel Martinez","c":["agu"],"d":[2020],"gp":6,"mpg":3.7,"ppg":2.8,"rpg":0.3,"apg":0.2,"spg":0,"bpg":0,"tpg":0.2,"fg":0.538,"tp":0.333,"ft":null,"tot":{"pts":17,"reb":2,"ast":1,"stl":0,"blk":0,"min":22},"ns":1,"src":"bsnpr26","legs":[["agu",6,2.8]],"pos":"SG","posSrc":"perfil","hi":[2026,2.8]},{"n":"Derek Reese","c":["que"],"d":[2020],"gp":29,"mpg":10.4,"ppg":2.6,"rpg":2.8,"apg":0.3,"spg":0.2,"bpg":0.3,"tpg":0.3,"fg":0.418,"tp":0.308,"ft":0.7,"tot":{"pts":74,"reb":81,"ast":10,"stl":5,"blk":9,"min":302},"ns":1,"src":"bsnpr26","legs":[["que",29,2.6]],"pos":"PF","posSrc":"perfil","hi":[2026,2.6]},{"n":"Gabriel J. Belardo","c":["man"],"d":[2020],"gp":9,"mpg":8.8,"ppg":2.6,"rpg":0.8,"apg":1.4,"spg":0.3,"bpg":0,"tpg":0.3,"fg":0.45,"tp":0.333,"ft":1,"tot":{"pts":23,"reb":7,"ast":13,"stl":3,"blk":0,"min":79},"ns":1,"src":"bsnpr26","legs":[["man",9,2.6]],"pos":"PG","posSrc":"perfil","hi":[2026,2.6]},{"n":"Bryan Powell","c":["pon"],"d":[2020],"gp":18,"mpg":7.3,"ppg":2.4,"rpg":1.8,"apg":0.3,"spg":0.2,"bpg":0.3,"tpg":0.5,"fg":0.419,"tp":0.118,"ft":0.833,"tot":{"pts":43,"reb":33,"ast":6,"stl":3,"blk":5,"min":132},"ns":1,"src":"bsnpr26","legs":[["pon",18,2.4]],"pos":"PF","posSrc":"perfil","hi":[2026,2.4]},{"n":"Anthony Morales","c":["cag"],"d":[2020],"gp":16,"mpg":9.3,"ppg":2.4,"rpg":2,"apg":0.3,"spg":0.3,"bpg":0.1,"tpg":0.7,"fg":0.342,"tp":0.333,"ft":0.625,"tot":{"pts":38,"reb":32,"ast":4,"stl":4,"blk":1,"min":148},"ns":1,"src":"bsnpr26","legs":[["cag",16,2.4]],"pos":"PF","posSrc":"perfil","hi":[2026,2.4]},{"n":"Luis Moya","c":["man"],"d":[2020],"gp":5,"mpg":3,"ppg":2.4,"rpg":1,"apg":0.6,"spg":0,"bpg":0,"tpg":0.2,"fg":0.8,"tp":1,"ft":0,"tot":{"pts":12,"reb":5,"ast":3,"stl":0,"blk":0,"min":15},"ns":1,"src":"bsnpr26","legs":[["man",5,2.4]],"pos":"C","posSrc":"perfil","hi":[2026,2.4]},{"n":"Jorge Luis Torres","c":["sge"],"d":[2020],"gp":31,"mpg":9.4,"ppg":2.3,"rpg":2.8,"apg":0.6,"spg":0.2,"bpg":0,"tpg":0.4,"fg":0.531,"tp":0,"ft":0.308,"tot":{"pts":72,"reb":86,"ast":18,"stl":5,"blk":0,"min":290},"ns":1,"src":"bsnpr26","legs":[["sge",31,2.3]],"pos":"C","posSrc":"perfil","hi":[2026,2.3]},{"n":"Alexander Franklin","c":["car"],"d":[2020],"gp":17,"mpg":12,"ppg":2.3,"rpg":2.1,"apg":0.6,"spg":0.2,"bpg":0.1,"tpg":0.5,"fg":0.425,"tp":0.211,"ft":0.25,"tot":{"pts":39,"reb":36,"ast":10,"stl":4,"blk":2,"min":204},"ns":1,"src":"bsnpr26","legs":[["car",17,2.3]],"pos":"SF","posSrc":"perfil","hi":[2026,2.3]},{"n":"Felix A. Rivera Vega","c":["are"],"d":[2020],"gp":24,"mpg":6.8,"ppg":2.2,"rpg":1.4,"apg":0.2,"spg":0.2,"bpg":0,"tpg":0.3,"fg":0.489,"tp":0.316,"ft":0.25,"tot":{"pts":53,"reb":33,"ast":4,"stl":5,"blk":0,"min":164},"ns":1,"src":"bsnpr26","legs":[["are",24,2.2]],"pos":"SF","posSrc":"perfil","hi":[2026,2.2]},{"n":"Bradley Camacho","c":["may"],"d":[2020],"gp":23,"mpg":5.5,"ppg":2.2,"rpg":1.6,"apg":0.2,"spg":0.2,"bpg":0.3,"tpg":0.2,"fg":0.655,"tp":0.25,"ft":0.545,"tot":{"pts":51,"reb":37,"ast":5,"stl":5,"blk":6,"min":126},"ns":1,"src":"bsnpr26","legs":[["may",23,2.2]],"pos":"C","posSrc":"perfil","hi":[2026,2.2]},{"n":"Chris Gaston","c":["may","car"],"d":[2020],"gp":9,"mpg":9,"ppg":2.1,"rpg":1.9,"apg":0.6,"spg":0.2,"bpg":0,"tpg":0.3,"fg":0.421,"tp":0,"ft":0.6,"tot":{"pts":19,"reb":17,"ast":5,"stl":2,"blk":0,"min":81},"ns":1,"src":"bsnpr26","legs":[["may",6,2.8],["car",3,0.7]],"pos":"PF","posSrc":"perfil","hi":[2026,2.1]},{"n":"Oenis Medina","c":["cag"],"d":[2020],"gp":29,"mpg":6.1,"ppg":2,"rpg":1.6,"apg":0.3,"spg":0.1,"bpg":0,"tpg":0.4,"fg":0.512,"tp":null,"ft":0.714,"tot":{"pts":59,"reb":45,"ast":9,"stl":3,"blk":0,"min":176},"ns":1,"src":"bsnpr26","legs":[["cag",29,2]],"pos":"PF","posSrc":"perfil","hi":[2026,2]},{"n":"Carlos Yao Lopez","c":["may"],"d":[2020],"gp":18,"mpg":9.1,"ppg":1.9,"rpg":2.3,"apg":0.6,"spg":0.2,"bpg":0.4,"tpg":0.4,"fg":0.4,"tp":0.5,"ft":0.857,"tot":{"pts":34,"reb":41,"ast":11,"stl":3,"blk":7,"min":163},"ns":1,"src":"bsnpr26","legs":[["may",18,1.9]],"pos":"PF","posSrc":"perfil","hi":[2026,1.9]},{"n":"Ruben Cotto","c":["may"],"d":[2020],"gp":31,"mpg":6.7,"ppg":1.7,"rpg":0.7,"apg":0.5,"spg":0.4,"bpg":0,"tpg":0.2,"fg":0.438,"tp":0.357,"ft":1,"tot":{"pts":54,"reb":21,"ast":16,"stl":12,"blk":0,"min":207},"ns":1,"src":"bsnpr26","legs":[["may",31,1.7]],"pos":"SG","posSrc":"perfil","hi":[2026,1.7]},{"n":"Kevin Maura Colon","c":["gua"],"d":[2020],"gp":30,"mpg":10.2,"ppg":1.6,"rpg":0.7,"apg":1.4,"spg":0.4,"bpg":0,"tpg":0.6,"fg":0.388,"tp":0.333,"ft":0.429,"tot":{"pts":49,"reb":20,"ast":43,"stl":13,"blk":0,"min":307},"ns":1,"src":"bsnpr26","legs":[["gua",30,1.6]],"pos":"PG","posSrc":"perfil","hi":[2026,1.6]},{"n":"Timajh Parker","c":["car"],"d":[2020],"gp":19,"mpg":10.6,"ppg":1.5,"rpg":2.4,"apg":0.6,"spg":0.4,"bpg":0.2,"tpg":0.3,"fg":0.56,"tp":null,"ft":0.333,"tot":{"pts":29,"reb":46,"ast":12,"stl":8,"blk":3,"min":201},"ns":1,"src":"bsnpr26","legs":[["car",19,1.5]],"pos":"PF","posSrc":"perfil","hi":[2026,1.5]},{"n":"Gerardo Texeira","c":["gua"],"d":[2020],"gp":8,"mpg":4.6,"ppg":1.5,"rpg":1.4,"apg":0.5,"spg":0.1,"bpg":0,"tpg":0.1,"fg":0.357,"tp":0.5,"ft":0,"tot":{"pts":12,"reb":11,"ast":4,"stl":1,"blk":0,"min":37},"ns":1,"src":"bsnpr26","legs":[["gua",8,1.5]],"pos":"C","posSrc":"perfil","hi":[2026,1.5]},{"n":"Tory San Antonio","c":["car"],"d":[2020],"gp":15,"mpg":6.3,"ppg":1.4,"rpg":1,"apg":0.5,"spg":0.1,"bpg":0.2,"tpg":0.1,"fg":0.286,"tp":0.235,"ft":0.5,"tot":{"pts":21,"reb":15,"ast":8,"stl":2,"blk":3,"min":95},"ns":1,"src":"bsnpr26","legs":[["car",15,1.4]],"pos":"SF","posSrc":"perfil","hi":[2026,1.4]},{"n":"Owen Perez","c":["agu"],"d":[2020],"gp":5,"mpg":3,"ppg":1.4,"rpg":1,"apg":0.2,"spg":0,"bpg":0,"tpg":0.4,"fg":0.429,"tp":0.25,"ft":null,"tot":{"pts":7,"reb":5,"ast":1,"stl":0,"blk":0,"min":15},"ns":1,"src":"bsnpr26","legs":[["agu",5,1.4]],"pos":"C","posSrc":"perfil","hi":[2026,1.4]},{"n":"Jevin Nikolas Muniz","c":["are"],"d":[2020],"gp":9,"mpg":9.6,"ppg":1.3,"rpg":1.9,"apg":1.1,"spg":0.3,"bpg":0,"tpg":0.9,"fg":0.25,"tp":0.077,"ft":0.25,"tot":{"pts":12,"reb":17,"ast":10,"stl":3,"blk":0,"min":86},"ns":1,"src":"bsnpr26","legs":[["are",9,1.3]],"pos":"SF","posSrc":"perfil","hi":[2026,1.3]},{"n":"Tyler Polo","c":["san"],"d":[2020],"gp":13,"mpg":4.7,"ppg":1.2,"rpg":0.6,"apg":0.2,"spg":0.1,"bpg":0,"tpg":0.4,"fg":0.412,"tp":0.25,"ft":null,"tot":{"pts":16,"reb":8,"ast":3,"stl":1,"blk":0,"min":61},"ns":1,"src":"bsnpr26","legs":[["san",13,1.2]],"pos":"SF","posSrc":"perfil","hi":[2026,1.2]},{"n":"Geancarlo Peguero","c":["cag","are"],"d":[2020],"gp":16,"mpg":5.1,"ppg":1.2,"rpg":0.9,"apg":0.2,"spg":0.1,"bpg":0,"tpg":0.3,"fg":0.421,"tp":0.2,"ft":1,"tot":{"pts":19,"reb":14,"ast":3,"stl":2,"blk":0,"min":81},"ns":1,"src":"bsnpr26","legs":[["cag",8,1.3],["are",8,1.1]],"pos":"SF","posSrc":"perfil","hi":[2026,1.2]},{"n":"Marvin Eliel Mantilla","c":["are"],"d":[2020],"gp":6,"mpg":3.2,"ppg":1.2,"rpg":0.8,"apg":0.2,"spg":0,"bpg":0.2,"tpg":0,"fg":0.4,"tp":0.5,"ft":0.5,"tot":{"pts":7,"reb":5,"ast":1,"stl":0,"blk":1,"min":19},"ns":1,"src":"bsnpr26","legs":[["are",6,1.2]],"pos":"C","posSrc":"perfil","hi":[2026,1.2]},{"n":"Rychell Janga","c":["bay"],"d":[2020],"gp":10,"mpg":2.6,"ppg":1.1,"rpg":0.6,"apg":0.2,"spg":0.3,"bpg":0,"tpg":0,"fg":0.333,"tp":0.333,"ft":0,"tot":{"pts":11,"reb":6,"ast":2,"stl":3,"blk":0,"min":26},"ns":1,"src":"bsnpr26","legs":[["bay",10,1.1]],"pos":"PF","posSrc":"perfil","hi":[2026,1.1]},{"n":"Neftali Acevedo Diaz","c":["bay"],"d":[2020],"gp":10,"mpg":3.6,"ppg":1,"rpg":0.1,"apg":0.6,"spg":0.6,"bpg":0,"tpg":0.2,"fg":0.4,"tp":0,"ft":1,"tot":{"pts":10,"reb":1,"ast":6,"stl":6,"blk":0,"min":36},"ns":1,"src":"bsnpr26","legs":[["bay",10,1]],"pos":"PG","posSrc":"perfil","hi":[2026,1]},{"n":"Nick Lucena","c":["may"],"d":[2020],"gp":7,"mpg":3.9,"ppg":1,"rpg":0.3,"apg":0.6,"spg":0,"bpg":0,"tpg":0.1,"fg":0.333,"tp":0,"ft":0.75,"tot":{"pts":7,"reb":2,"ast":4,"stl":0,"blk":0,"min":27},"ns":1,"src":"bsnpr26","legs":[["may",7,1]],"pos":"PG","posSrc":"perfil","hi":[2026,1]},{"n":"Wilmer Lugo-Sanchez","c":["man"],"d":[2020],"gp":15,"mpg":2.7,"ppg":0.9,"rpg":0.5,"apg":0.3,"spg":0.1,"bpg":0,"tpg":0.1,"fg":0.556,"tp":null,"ft":0.5,"tot":{"pts":13,"reb":8,"ast":4,"stl":1,"blk":0,"min":40},"ns":1,"src":"bsnpr26","legs":[["man",15,0.9]],"pos":"SF","posSrc":"perfil","hi":[2026,0.9]},{"n":"Kenneth Santos Velez","c":["pon"],"d":[2020],"gp":9,"mpg":3.1,"ppg":0.9,"rpg":0.6,"apg":0.2,"spg":0,"bpg":0,"tpg":0.2,"fg":0.25,"tp":0.222,"ft":null,"tot":{"pts":8,"reb":5,"ast":2,"stl":0,"blk":0,"min":28},"ns":1,"src":"bsnpr26","legs":[["pon",9,0.9]],"pos":"SF","posSrc":"perfil","hi":[2026,0.9]},{"n":"Harold Perez Abreu","c":["agu"],"d":[2020],"gp":7,"mpg":2.3,"ppg":0.9,"rpg":0.1,"apg":0.1,"spg":0,"bpg":0,"tpg":0.1,"fg":0.286,"tp":0.4,"ft":null,"tot":{"pts":6,"reb":1,"ast":1,"stl":0,"blk":0,"min":16},"ns":1,"src":"bsnpr26","legs":[["agu",7,0.9]],"pos":"SG","posSrc":"perfil","hi":[2026,0.9]},{"n":"Enrique Ramos","c":["pon"],"d":[2020],"gp":7,"mpg":6.1,"ppg":0.9,"rpg":1.6,"apg":0,"spg":0,"bpg":0,"tpg":0,"fg":0.222,"tp":0,"ft":0.333,"tot":{"pts":6,"reb":11,"ast":0,"stl":0,"blk":0,"min":43},"ns":1,"src":"bsnpr26","legs":[["pon",7,0.9]],"pos":"PF","posSrc":"perfil","hi":[2026,0.9]},{"n":"Bryan Gonzalez Colon","c":["gua"],"d":[2020],"gp":4,"mpg":3.3,"ppg":0.8,"rpg":0.5,"apg":0.5,"spg":0.5,"bpg":0,"tpg":0,"fg":0.25,"tp":0,"ft":0.5,"tot":{"pts":3,"reb":2,"ast":2,"stl":2,"blk":0,"min":13},"ns":1,"src":"bsnpr26","legs":[["gua",4,0.8]],"pos":"PG","posSrc":"perfil","hi":[2026,0.8]},{"n":"Alejandro Ralat","c":["cag"],"d":[2020],"gp":15,"mpg":3.6,"ppg":0.7,"rpg":0.5,"apg":0.5,"spg":0.2,"bpg":0,"tpg":0.3,"fg":0.308,"tp":0.5,"ft":null,"tot":{"pts":11,"reb":8,"ast":7,"stl":3,"blk":0,"min":54},"ns":1,"src":"bsnpr26","legs":[["cag",15,0.7]],"pos":"PG","posSrc":"perfil","hi":[2026,0.7]},{"n":"Jonathan Garcia","c":["may"],"d":[2020],"gp":14,"mpg":4.4,"ppg":0.7,"rpg":0.3,"apg":1.2,"spg":0,"bpg":0,"tpg":0.2,"fg":0.222,"tp":0.167,"ft":0.833,"tot":{"pts":10,"reb":4,"ast":17,"stl":0,"blk":0,"min":61},"ns":1,"src":"bsnpr26","legs":[["may",14,0.7]],"pos":"PG","posSrc":"perfil","hi":[2026,0.7]},{"n":"Joseph Bull","c":["sge"],"d":[2020],"gp":7,"mpg":3.3,"ppg":0.7,"rpg":1.3,"apg":0.4,"spg":0.1,"bpg":0,"tpg":0.9,"fg":0.25,"tp":0,"ft":0.5,"tot":{"pts":5,"reb":9,"ast":3,"stl":1,"blk":0,"min":23},"ns":1,"src":"bsnpr26","legs":[["sge",7,0.7]],"pos":"C","posSrc":"perfil","hi":[2026,0.7]},{"n":"Jampier Lezcano","c":["pon"],"d":[2020],"gp":14,"mpg":3.6,"ppg":0.6,"rpg":0.4,"apg":0.6,"spg":0.1,"bpg":0,"tpg":0.3,"fg":0.273,"tp":0.333,"ft":0.286,"tot":{"pts":9,"reb":6,"ast":8,"stl":1,"blk":0,"min":51},"ns":1,"src":"bsnpr26","legs":[["pon",14,0.6]],"pos":"PG","posSrc":"perfil","hi":[2026,0.6]},{"n":"Daniel Rosado","c":["are"],"d":[2020],"gp":8,"mpg":2.9,"ppg":0.5,"rpg":0.5,"apg":0.3,"spg":0,"bpg":0,"tpg":0,"fg":0.222,"tp":0,"ft":null,"tot":{"pts":4,"reb":4,"ast":2,"stl":0,"blk":0,"min":23},"ns":1,"src":"bsnpr26","legs":[["are",6,0.7],["are",2,0]],"pos":"SF","posSrc":"perfil","hi":[2026,0.5]},{"n":"Luis Henriquez","c":["may"],"d":[2020],"gp":4,"mpg":1.3,"ppg":0.5,"rpg":0,"apg":0,"spg":0,"bpg":0,"tpg":0,"fg":1,"tp":null,"ft":null,"tot":{"pts":2,"reb":0,"ast":0,"stl":0,"blk":0,"min":5},"ns":1,"src":"bsnpr26","legs":[["may",4,0.5]],"pos":"SG","posSrc":"perfil","hi":[2026,0.5]},{"n":"Ibrahima Sylla","c":["que"],"d":[2020],"gp":2,"mpg":14,"ppg":0.5,"rpg":3,"apg":0,"spg":0,"bpg":1,"tpg":1,"fg":0,"tp":null,"ft":0.5,"tot":{"pts":1,"reb":6,"ast":0,"stl":0,"blk":2,"min":28},"ns":1,"src":"bsnpr26","legs":[["que",2,0.5]],"pos":"PF","posSrc":"perfil","hi":[2026,0.5]},{"n":"Rico Hopping","c":["sge"],"d":[2020],"gp":10,"mpg":2.9,"ppg":0.4,"rpg":0.3,"apg":0.1,"spg":0,"bpg":0,"tpg":0.1,"fg":0.154,"tp":0,"ft":null,"tot":{"pts":4,"reb":3,"ast":1,"stl":0,"blk":0,"min":29},"ns":1,"src":"bsnpr26","legs":[["sge",10,0.4]],"pos":"SG","posSrc":"perfil","hi":[2026,0.4]},{"n":"Yahir Cordero Melendez","c":["may"],"d":[2020],"gp":3,"mpg":1,"ppg":0,"rpg":0.7,"apg":0,"spg":0.3,"bpg":0,"tpg":0,"fg":0,"tp":0,"ft":null,"tot":{"pts":0,"reb":2,"ast":0,"stl":1,"blk":0,"min":3},"ns":1,"src":"bsnpr26","legs":[["may",3,0]],"pos":"C","posSrc":"perfil","hi":[2026,0]}];

/* ============================================================
   IMAGE DROP-IN LAYER
   Every crest and portrait renders as drawn SVG. Drop a file at
   the path below and it takes over. The chain lives in a data
   attribute and one delegated capture-phase listener walks it —
   putting the chain in an onerror attribute is what broke this
   in the previous build (quotes terminated the attribute).
   ============================================================ */
const USE_IMAGES=true, CREST_DIR='img/crest/', PLAYER_DIR='img/player/';
const CREST_EXT=['png','svg','jpg','webp'], PLAYER_EXT=['jpg','png','webp'];
/* 5G-A — ASSETS = manifest.assets ({ "img/crest/rio": "img/crest/rio.png", … }),
   set by hydrate(). We emit an <img> ONLY for a base that's listed — one
   request, no extension probing, no 404s. null (file:// or pre-hydrate) or a
   base that isn't there -> SVG only. exts kept in the signature for callers. */
let ASSETS=null;
function imgTry(base,exts,cls,alt){
  if(!USE_IMAGES || !ASSETS) return '';
  const src=ASSETS[base]; if(!src) return '';
  /* Hidden until it loads: visible-until-error flashes broken alt text. */
  return `<img class="${cls}" style="display:none" data-base="${esc(base)}" src="${esc(src)}" alt="${esc(alt)}" decoding="async">`;
}
document.addEventListener('error',e=>{
  const t=e.target;
  if(t && t.tagName==='IMG' && t.dataset.base) t.remove();   /* corrupt/renamed file -> fall back to the SVG behind it */
},true);
document.addEventListener('load',e=>{
  const t=e.target;
  if(t && t.tagName==='IMG' && t.dataset.base && t.naturalWidth>0) t.style.display='block';
},true);

/* illustrated-figures pass (Phase 1) — crests: an original geometric emblem
   for every franchise (shield + abbreviation, "B" from the mockup review),
   with a more detailed original mascot illustration ("D") layered on top
   ONLY for franchise keys that carry an `art` value below. `art` is set on
   exactly 3 keys in this phase (bay/san/pon — the 3 icons reviewed and
   approved live); 13 more D-eligible names are queued for Phase 2, added
   the same way once each icon is designed and shown before it ships.
   Never real logos — original interpretations of what each name literally
   means, never traced from an existing crest. No `art` value is EVER a
   fallback state, not an oversight: 17 franchise names reference real
   Indigenous identity (Indios×2, Taínos, Caciques), real Puerto Rican
   cultural/religious practice (Criollos, Santeros, Brujos), a colonial
   figure (Conquistadores), a name too close to an existing pro mascot
   (Cardenales), a name with no figure at all (Atléticos, Mets, Capitalinos,
   Vega Baja), or a name whose meaning isn't confidently known (Cariduros,
   Atenienses, Avancinos) — those stay on the shield+type fallback forever,
   not just until someone gets around to it. crest_art_harness.mjs enforces
   this: none of those 17 keys may ever carry an `art` value. */
const CREST_ICONS={
  vaquero:(c1,c2)=>`<g fill="${c2}">
      <ellipse cx="56" cy="27" rx="22" ry="6"/><rect x="45" y="9" width="22" height="19" rx="9"/>
      <circle cx="56" cy="39" r="8"/><path d="M50 46h12l-6 7Z"/></g>
    <path d="M43 52h26l-5 26h-16Z" fill="${c2}"/>
    <g stroke="${c2}" stroke-width="5" stroke-linecap="round" fill="none">
      <path d="M43 55q-13 4-10 17"/><path d="M69 55q13 4 8 18"/>
      <path d="M49 78l-4 22"/><path d="M63 78l5 22"/></g>
    <circle cx="30" cy="70" r="7" fill="none" stroke="${c2}" stroke-width="3"/>`,
  cangrejo:(c1,c2)=>`<path d="M30 56Q34 42 44 44Q50 38 56 38Q62 38 68 44Q78 42 82 56Q84 68 72 74Q62 78 56 78Q50 78 40 74Q28 68 30 56Z" fill="${c2}"/>
    <g stroke="${c2}" stroke-width="2.6"><line x1="46" y1="44" x2="43" y2="34"/><line x1="66" y1="44" x2="69" y2="34"/></g>
    <circle cx="43" cy="32" r="3" fill="${c2}"/><circle cx="69" cy="32" r="3" fill="${c2}"/>
    <g fill="${c2}"><path d="M30 50q-10-4-12 6q8 4 14-1Z"/><path d="M22 56q-4 8 4 12q4-6 0-12Z"/>
      <path d="M82 50q10-4 12 6q-8 4-14-1Z"/><path d="M90 56q4 8-4 12q-4-6 0-12Z"/></g>
    <g stroke="${c2}" stroke-width="2.4" fill="none" stroke-linecap="round">
      <path d="M32 62L22 66L17 74"/><path d="M34 70L25 76L21 84"/><path d="M40 76L33 84L30 92"/>
      <path d="M80 62L90 66L95 74"/><path d="M78 70L87 76L91 84"/><path d="M72 76L79 84L82 92"/></g>`,
  leon:(c1,c2)=>`<g fill="${c2}">
      <path d="M56 44l6 -24 6 20Z"/><path d="M56 44l-6 -24 -6 20Z"/>
      <path d="M56 44l14 -20 3 22Z"/><path d="M56 44l-14 -20 -3 22Z"/>
      <path d="M56 44l20 -12 -1 22Z"/><path d="M56 44l-20 -12 1 22Z"/>
      <path d="M56 44l24 -4 -6 20Z"/><path d="M56 44l-24 -4 6 20Z"/>
      <path d="M56 48l25 4 -10 18Z"/><path d="M56 48l-25 4 10 18Z"/>
      <path d="M56 52l22 12 -14 14Z"/><path d="M56 52l-22 12 14 14Z"/></g>
    <circle cx="56" cy="48" r="15" fill="${c2}"/>
    <path d="M44 40q4-6 10-3" fill="none" stroke="${c1}" stroke-width="2"/>
    <path d="M68 40q-4-6-10-3" fill="none" stroke="${c1}" stroke-width="2"/>
    <ellipse cx="49" cy="46" rx="2" ry="2.6" fill="${c1}"/><ellipse cx="63" cy="46" rx="2" ry="2.6" fill="${c1}"/>
    <path d="M53 52h6l-3 4Z" fill="${c1}"/>
    <path d="M48 58q8 5 16 0" fill="none" stroke="${c1}" stroke-width="1.8" stroke-linecap="round"/>
    <g stroke="${c1}" stroke-width="1.2" opacity=".75">
      <line x1="40" y1="52" x2="30" y2="50"/><line x1="40" y1="56" x2="30" y2="57"/>
      <line x1="72" y1="52" x2="82" y2="50"/><line x1="72" y1="56" x2="82" y2="57"/></g>`,
  /* Phase 2, batch 1 (owner-approved mockup) */
  oso:(c1,c2)=>`<circle cx="43" cy="29" r="9" fill="${c2}"/><circle cx="69" cy="29" r="9" fill="${c2}"/>
    <circle cx="56" cy="48" r="20" fill="${c2}"/>
    <ellipse cx="56" cy="58" rx="11" ry="8" fill="${c1}"/>
    <circle cx="49" cy="42" r="2.3" fill="${c1}"/><circle cx="63" cy="42" r="2.3" fill="${c1}"/>
    <ellipse cx="56" cy="56" rx="2.6" ry="2" fill="${c2}"/>`,
  gallo:(c1,c2)=>`<path d="M46 30Q48 18 52 28Q54 16 58 28Q62 16 64 30Z" fill="${c2}"/>
    <circle cx="56" cy="42" r="16" fill="${c2}"/>
    <path d="M70 44L84 40L70 52Z" fill="${c2}"/>
    <path d="M58 54Q58 64 64 62Q60 58 58 54Z" fill="${c2}"/>
    <circle cx="52" cy="40" r="2.3" fill="${c1}"/>`,
  tiburon:(c1,c2)=>`<path d="M40 20L56 48L30 44Z" fill="${c2}"/>
    <path d="M20 56Q30 40 60 44Q84 46 88 58Q80 66 60 66Q34 66 20 56Z" fill="${c2}"/>
    <circle cx="70" cy="54" r="2.2" fill="${c1}"/>
    <path d="M40 62L46 58L52 62L58 58L64 62L70 58L76 62" fill="none" stroke="${c1}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`,
  ancla:(c1,c2)=>`<path d="M50 12l6 10 6-10Z" fill="${c2}"/>
    <path d="M50 20a6 6 0 1 0 12 0a6 6 0 1 0 -12 0" fill="none" stroke="${c2}" stroke-width="4"/>
    <line x1="56" y1="26" x2="56" y2="72" stroke="${c2}" stroke-width="5"/>
    <line x1="42" y1="38" x2="70" y2="38" stroke="${c2}" stroke-width="4"/>
    <path d="M40 60c0 12 8 18 16 18" fill="none" stroke="${c2}" stroke-width="5" stroke-linecap="round"/>
    <path d="M72 60c0 12-8 18-16 18" fill="none" stroke="${c2}" stroke-width="5" stroke-linecap="round"/>`,
  /* Phase 2, batch 2 (owner-approved mockup) */
  pirata:(c1,c2)=>`<path d="M36 26Q56 14 76 26Q68 34 56 30Q44 34 36 26Z" fill="${c2}"/>
    <circle cx="56" cy="40" r="10" fill="${c2}"/>
    <rect x="49" y="37" width="9" height="4" fill="${c1}" transform="rotate(-10 53 39)"/>
    <path d="M43 52h26l-5 26h-16Z" fill="${c2}"/>
    <g stroke="${c2}" stroke-width="4" stroke-linecap="round">
      <line x1="44" y1="66" x2="68" y2="78"/><line x1="68" y1="66" x2="44" y2="78"/></g>
    <circle cx="44" cy="66" r="2.4" fill="${c2}"/><circle cx="68" cy="66" r="2.4" fill="${c2}"/>
    <circle cx="44" cy="78" r="2.4" fill="${c2}"/><circle cx="68" cy="78" r="2.4" fill="${c2}"/>`,
  gigante:(c1,c2)=>`<circle cx="56" cy="26" r="13" fill="${c2}"/>
    <path d="M30 76c0-24 12-34 26-34s26 10 26 34Z" fill="${c2}"/>
    <g stroke="${c2}" stroke-width="7" stroke-linecap="round">
      <path d="M32 50q-14 4-16 20"/><path d="M80 50q14 4 16 20"/></g>
    <g stroke="${c2}" stroke-width="7" stroke-linecap="round">
      <line x1="46" y1="76" x2="40" y2="94"/><line x1="66" y1="76" x2="72" y2="94"/></g>`,
  timon:(c1,c2)=>`<circle cx="56" cy="48" r="22" fill="none" stroke="${c2}" stroke-width="5"/>
    <circle cx="56" cy="48" r="6" fill="${c2}"/>
    <g stroke="${c2}" stroke-width="4" stroke-linecap="round">
      <line x1="56" y1="20" x2="56" y2="30"/><line x1="56" y1="66" x2="56" y2="76"/>
      <line x1="28" y1="48" x2="38" y2="48"/><line x1="74" y1="48" x2="84" y2="48"/>
      <line x1="36" y1="28" x2="43" y2="35"/><line x1="76" y1="68" x2="69" y2="61"/>
      <line x1="76" y1="28" x2="69" y2="35"/><line x1="36" y1="68" x2="43" y2="61"/></g>`,
  torito:(c1,c2)=>`<path d="M30 34Q26 20 36 22Q40 30 38 38Z" fill="${c2}"/>
    <path d="M82 34Q86 20 76 22Q72 30 74 38Z" fill="${c2}"/>
    <circle cx="56" cy="46" r="18" fill="${c2}"/>
    <ellipse cx="56" cy="58" rx="12" ry="9" fill="${c1}"/>
    <circle cx="49" cy="42" r="2.3" fill="${c1}"/><circle cx="63" cy="42" r="2.3" fill="${c1}"/>
    <ellipse cx="56" cy="58" rx="4" ry="3" fill="none" stroke="${c2}" stroke-width="1.6"/>`,
  /* Phase 2, batch 3 — final batch (owner-approved mockup) */
  pollito:(c1,c2)=>`<circle cx="56" cy="42" r="16" fill="${c2}"/>
    <ellipse cx="56" cy="66" rx="20" ry="18" fill="${c2}"/>
    <path d="M70 40L82 38L70 46Z" fill="${c2}"/>
    <circle cx="52" cy="38" r="2.2" fill="${c1}"/>
    <path d="M42 60Q34 62 38 74Q46 72 44 60Z" fill="${c1}"/>`,
  titan:(c1,c2)=>`<path d="M44 20l4 8h16l4-8-6 5h-12Z" fill="${c2}"/>
    <circle cx="56" cy="36" r="13" fill="${c2}"/>
    <path d="M30 74a26 20 0 0 1 52 0Z" fill="${c2}"/>`,
  cocotero:(c1,c2)=>`<path d="M53 30c2 18-1 36-5 48h16c-4-12-7-30-5-48Z" fill="${c2}"/>
    <g fill="${c2}">
      <path d="M56 30Q30 22 20 34Q40 34 56 32Z"/>
      <path d="M56 30Q82 22 92 34Q72 34 56 32Z"/>
      <path d="M56 28Q48 8 34 10Q46 20 56 30Z"/>
      <path d="M56 28Q64 8 78 10Q66 20 56 30Z"/></g>
    <circle cx="50" cy="34" r="4" fill="${c1}"/><circle cx="60" cy="36" r="4" fill="${c1}"/>`,
  maratonista:(c1,c2)=>`<circle cx="60" cy="24" r="10" fill="${c2}"/>
    <path d="M48 40c4-4 10-4 14 0l6 16-10 6-14-8Z" fill="${c2}"/>
    <g stroke="${c2}" stroke-width="6" stroke-linecap="round">
      <path d="M52 44L36 36"/><path d="M62 50L78 42"/>
      <path d="M52 60L36 78"/><path d="M60 62L70 90"/></g>`,
};
function crestSVG(k,w,h){
  const f=F[k]; if(!f) return '';
  const id='cg'+k+w;
  /* Owner-reported bug (live screenshot, all 12 active teams), round 1: the
     icon paths in CREST_ICONS were drawn at full shield scale (hat-to-legs
     on the cowboy spans ~y9-100 of the 130-tall viewBox) and rendered with
     no scale-down at all. Wrapped in a scale transform around (56,44) so
     the icon shrinks and sits higher, without touching a single path
     coordinate in CREST_ICONS itself. This shipped and is real, but it
     wasn't the actual cause of the reported overlap.
     Round 2, the real cause: the abbreviation sat at y=116 since the very
     first version, regardless of icon size. The shield's own outline (a
     cubic bezier, not a rectangle) has already tapered to ~16px wide
     total at y=116 -- computed from the path's real control points, not
     estimated -- while "BAY"/"SAN"/"PON" at that size run ~30-38px wide.
     The text was spilling past the shield's tapered point on every icon-
     bearing crest; the icon was never the cause. Moved to y=105, where
     the shield measures ~58-60px wide -- comfortable real margin. */
  const icon=f.art && CREST_ICONS[f.art]
    ? `<g transform="translate(56,44) scale(.6) translate(-56,-44)">${CREST_ICONS[f.art](f.c1,f.c2)}</g>` : '';
  const abbrY=icon?105:74, abbrSize=icon?16:32;
  return `<svg width="${w}" height="${h}" viewBox="0 0 112 130" aria-hidden="true">
    <defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${f.c1}"/><stop offset="1" stop-color="${f.c1}" stop-opacity=".8"/>
    </linearGradient></defs>
    <path d="M8 10h96v58c0 34-32 48-48 50-16-2-48-16-48-50Z" fill="url(#${id})" stroke="${f.c2}" stroke-width="3"/>
    ${icon}
    <text x="56" y="${abbrY}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="800"
      letter-spacing="-.3" font-size="${abbrSize}" fill="${f.c2}">${esc(f.abbr)}</text>
  </svg>`;
}
function crest(k,w=34,h=41){
  const f=F[k]; if(!f) return '';
  const img=USE_IMAGES?imgTry(CREST_DIR+k,CREST_EXT,'',f.name+' escudo'):'';
  return `<span class="crest" style="width:${w}px;height:${h}px">${crestSVG(k,w,h)}${img}</span>`;
}
/* PHASE_21 (owner-approved, redesign-v2): player avatars -- direction "B,
   Gradiente" from the /tmp avatar-directions exploration (PHASE_20 Part 2):
   a diagonal club-color gradient with initials, no silhouette (the owner's
   own instruction: "remove the silhouette/crescent figure entirely").
   Real WCAG contrast, computed live via the actual relative-luminance
   formula, not eyeballed -- portraitFill() below falls back from a gradient
   to a flat, further-darkened fill for the two real clubs (Cangrejeros,
   San Germán) whose bright orange would otherwise put white initials under
   4.5:1, the exact pair PHASE_20's own printed ratios already flagged.
   No tricolor on avatars (owner: reads as the French flag) -- the corner-
   ring decoration (CSS, .pavatar::after) is the only accent. */
function relLum(rgb){
  const f=v=>{ v/=255; return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4); };
  return 0.2126*f(rgb[0])+0.7152*f(rgb[1])+0.0722*f(rgb[2]);
}
function hexRgb(hex){ const h=String(hex).replace('#',''); return [0,2,4].map(i=>parseInt(h.slice(i,i+2),16)); }
function contrastRatio(hexA,hexB){
  const L1=relLum(hexRgb(hexA)), L2=relLum(hexRgb(hexB));
  const [hi,lo]=L1>L2?[L1,L2]:[L2,L1]; return (hi+0.05)/(lo+0.05);
}
function darkenHex(hex,amt){
  const [r,g,b]=hexRgb(hex); const d=v=>Math.max(0,Math.round(v*(1-amt)));
  return '#'+[d(r),d(g),d(b)].map(v=>v.toString(16).padStart(2,'0')).join('');
}
function lightenHex(hex,amt){
  const [r,g,b]=hexRgb(hex); const l=v=>Math.min(255,Math.round(v+(255-v)*amt));
  return '#'+[l(r),l(g),l(b)].map(v=>v.toString(16).padStart(2,'0')).join('');
}
/* PHASE_22 (owner-approved, redesign-v2): Comparar's new head-to-head cards
   put a real club color directly on TEXT (scoreboard numerals, the winning
   value in a mirrored stat row) for the first time -- every earlier use of
   a club hex (avatar fills, bar fills, accent bars, dots) was either white-
   on-color or a non-text graphical element, 3:1, not 4.5:1. A raw club
   color as small text can fail outright (a pale club color on a light
   theme's white card, or a dark club color on a near-black dark card).
   cmpTextSafe() nudges the real color toward white or black -- whichever
   direction the real background needs -- only as far as it has to, real
   contrast math each step, never a flat "always darken" assumption. A
   CMP_FALLBACK token (the var(--azul)/var(--rojo)/var(--ok) literal
   strings cmpColor() returns for an unclubbed compare slot) is already a
   real, already-proven app token -- returned as-is, both directions,
   since it isn't a hex this function can run math on and doesn't need to
   be, it already flips correctly per theme on its own. */
function cmpTextSafe(hex,bgHex){
  if(!hex||!/^#/.test(hex)) return hex;
  if(contrastRatio(hex,bgHex)>=4.5) return hex;
  const bgDark=relLum(hexRgb(bgHex))<0.4;
  let amt=0.12, adj=hex;
  for(let i=0;i<12;i++){
    adj=bgDark?lightenHex(hex,amt):darkenHex(hex,amt);
    if(contrastRatio(adj,bgHex)>=4.5) break;
    amt=Math.min(0.96,amt+0.1);
  }
  return adj;
}
/* one real color computed two ways -- against the real background hex of
   each theme -- so a CSS [data-theme="light"] override (the same
   mechanism every other theme-reactive value in this file already uses)
   can pick the right one live, without re-running any builder on a theme
   switch (drawCompare() only runs when the comparison itself changes, not
   on every theme toggle -- a single baked-in color would go wrong the
   moment someone switched themes without touching Comparar again).
   bgDark/bgLight default to --card's own two real hexes; PHASE_22 Part 2's
   mirrored rows live on --raise instead (#131E38 dark / #E1E9F5 light --
   a real, if close, different background in each theme), so cmpBarRow()
   passes those explicitly rather than reusing the --card-tuned default. */
function cmpColorPair(hex,bgDark,bgLight){
  return { dark: cmpTextSafe(hex,bgDark||'#0C1428'), light: cmpTextSafe(hex,bgLight||'#FFFFFF') };
}
/* PHASE_26 item 1: a WCAG 1.4.11 check (>=3:1, non-text) for a FILL sitting
   directly against a neutral track/panel, not a text check -- a sibling of
   cmpTextSafe()'s own loop (same lighten/darken-until-it-clears technique,
   same keep-the-hue approach), checked against the worse of two real
   backgrounds at once (the track itself, --line-soft, and the row panel
   around it, --raise -- close but not identical in each theme) so the
   result is genuinely safe against both, not just whichever one happened
   to be passed in. Real measured failures before this existed: Fajardo
   maroon #7A1F3D on dark --raise was 1.65:1; Mets de Guaynabo navy
   #122E5C was 1.24:1 -- both well under 3:1, and both the user's own
   reported examples. */
function cmpFillSafe(hex,bgA,bgB,minRatio){
  if(!hex||!/^#/.test(hex)) return hex;
  minRatio=minRatio||3;
  const worst=c=>Math.min(contrastRatio(c,bgA),contrastRatio(c,bgB));
  if(worst(hex)>=minRatio) return hex;
  const bgDark=relLum(hexRgb(bgA))<0.4;
  let amt=0.12, adj=hex;
  for(let i=0;i<12;i++){
    adj=bgDark?lightenHex(hex,amt):darkenHex(hex,amt);
    if(worst(adj)>=minRatio) break;
    amt=Math.min(0.96,amt+0.1);
  }
  return adj;
}
/* Same dark/light-pair pattern as cmpColorPair() -- CSS (not a theme-
   toggle re-render) picks the right one live. Only bars and the radar
   polygon use this: the two places a fill sits directly against a track/
   panel background with no border of its own. Avatar/top bar/legend keep
   the plain assigned color (COLORS[i], PHASE_25) -- same hue, still the
   same player identity -- since neither is the flat "fill against a bare
   track" case this specific WCAG criterion is about. */
function cmpFillPair(hex){
  return { dark: cmpFillSafe(hex,'#131E38','#16203A',3), light: cmpFillSafe(hex,'#E1E9F5','#DDE6F3',3) };
}
/* PHASE_41 (owner-approved, redesign-v2): owner-reported bug -- the Cangrejeros
   crest is invisible on its card in the dark theme, and the Vaqueros/Criollos/
   Santeros crests' yellow outlines are faint in the light theme. crest()/
   crestSVG() draw f.c1 (fill) and f.c2 (stroke/icon/text) directly, with no
   backdrop of their own -- whatever card background sits behind them is
   whatever it is. The inverse of cmpFillSafe() above: that one nudges a FILL
   until it clears 3:1 against a FIXED background; this nudges a neutral
   BACKDROP (starting from --raise's own real hex, the same "small plate under
   an element" idea --card/--raise already serve app-wide) until BOTH of a
   club's own fixed colors clear 3:1 against it, in each theme. Used only by
   the new .crest-plate wrapper (Apoderados/Retirados), never by crest()
   itself -- every other crest() call site (Equipos tiles, Historia bars,
   showTeam()) is untouched. */
function crestPlate(k){
  const f=F[k];
  /* crestSVG()'s shield is one closed path: fill=c1 (gradient), stroke=c2,
     stroke-width 3 -- an SVG stroke straddles its path's own edge, so the
     OUTERMOST pixels touching whatever sits behind the shield are entirely
     c2's own color; c1 (the fill) is enclosed strictly inside that stroke
     band and never directly borders the plate at all. The crest's own
     internal legibility (icon/abbr on the fill) is a c1-vs-c2 question,
     already fixed by the crest's own original color choice, nothing to do
     with the plate. So only c2 has to clear 3:1 against the plate -- this
     matches every one of the 4 owner-reported cases exactly (Cangrejeros'
     near-black stroke on the dark card, Vaqueros/Criollos/Santeros' gold
     stroke on the light card all failed on c2, not c1 -- checked live
     before this existed).
     contrastRatio() is monotonic moving away from a color's own luminance
     in either direction, so the single backdrop that maximizes contrast
     against any one fixed color is always pure black or pure white --
     confirmed by an earlier, slower version of this function that scanned
     the full 0-255 grey ramp per club and converged on exactly one or the
     other every time, never anything in between. c2 doesn't change per
     theme, so neither does its ideal backdrop -- the plate is a dedicated
     contrast-insurance chip, not a decoration that has to lean dark/light
     with the surrounding card, so the SAME single plate color is correct
     for both themes -- returned as one hex, not a {dark,light} pair the
     way cmpColorPair()/cmpFillPair() return (those two genuinely differ by
     theme; this one, checked live, never does). Full 12-club x 2-theme
     numbers printed by PHASE_41/41B's own report, not assumed. */
  const pure=contrastRatio(f.c2,'#000000')>=contrastRatio(f.c2,'#FFFFFF')?'#000000':'#FFFFFF';
  /* PHASE_41B (owner-approved, redesign-v2): pure black/white glares,
     especially the white plates against the dark theme's own near-black
     page. #0B1020 (near-black, close to --card's own dark hex) and #F4F6FA
     (off-white, close to --card's own light hex) read as part of the app's
     real palette instead of a stark print-poster cutout. Tries the soft
     tone on whichever side (dark/light) the pure check already picked --
     keeps the same direction, just softer -- and only falls back to the
     actual pure color for a club where softening itself would drop that
     club's own real c2 below 3:1 (checked per club below, not assumed to
     always hold just because it held for most). */
  const soft=pure==='#000000'?'#0B1020':'#F4F6FA';
  return contrastRatio(f.c2,soft)>=3?soft:pure;
}
/* no known club (archive-only with no linked team) -- a literal hex, not a
   theme token: the avatar fill has to stay fixed regardless of the site's
   own light/dark toggle, same as every real club color does. Checked live
   against white text: 12.65:1, comfortably clears 4.5:1 -- never implies a
   real club. */
const PORTRAIT_NEUTRAL='#15335C';
function portraitFill(hex){
  const base=(hex&&/^#/.test(hex))?hex:PORTRAIT_NEUTRAL;
  if(contrastRatio('#FFFFFF',base)>=4.5) return {bg:`linear-gradient(135deg,${base},${darkenHex(base,0.42)})`,fg:'#FFFFFF'};
  let amt=0.42, dark=darkenHex(base,amt);
  while(contrastRatio('#FFFFFF',dark)<4.5 && amt<0.85){ amt+=0.08; dark=darkenHex(base,amt); }
  return {bg:dark,fg:'#FFFFFF'};
}
/* given name + first surname -- "Surname(s), Given(s)" (the archive's own
   format: "Llovet Ayala, Francisco" -> given "Francisco" + surname "Llovet"
   -> "FL") vs. "Given [Middle] Surname" (curated display names: "Georgie
   Torres" -> "GT"; a 3-word name takes the FIRST and LAST word, not the
   first two, so a middle name is never mistaken for the surname). */
function playerInitials(name){
  const clean=String(name).replace(/[«»]/g,'').trim();
  const comma=clean.indexOf(',');
  if(comma>-1){
    const given=(clean.slice(comma+1).trim().split(/\s+/)[0]||'');
    const sur=(clean.slice(0,comma).trim().split(/\s+/)[0]||'');
    return ((given[0]||'')+(sur[0]||'')).toUpperCase();
  }
  const words=clean.split(/\s+/).filter(Boolean);
  if(!words.length) return '';
  if(words.length===1) return words[0][0].toUpperCase();
  return (words[0][0]+words[words.length-1][0]).toUpperCase();
}
function portrait(name,c1,c2,w=54,h=66,pos){
  const id='pt'+slug(name);
  const {bg,fg}=portraitFill(c1);
  const ini=playerInitials(name);
  const fs=Math.round(Math.min(w,h)*0.36);
  const img=USE_IMAGES?imgTry(PLAYER_DIR+slug(name),PLAYER_EXT,'',name):'';
  /* aria-hidden, unchanged from before this phase -- purely decorative, the
     real accessible name is always the adjacent heading/button text, never
     this element alone. */
  return `<span class="crest pavatar" style="width:${w}px;height:${h}px;background:${bg}" id="${id}" aria-hidden="true">`
    + `<span class="pini" style="font-size:${fs}px;color:${fg}">${esc(ini)}</span>${img}</span>`;
}

/* ============================================================
   MINI VISUALS (PHASE_8.3) — tiny SVGs for the editorial blocks.
   viewBox only, painted with currentColor so the caller's colour
   flows through and both themes work. No layout read.
   ============================================================ */
function spark(vals,opts){
  opts=opts||{};
  const pts=vals.map(v=>(typeof v==='number'&&v===v)?v:null);
  const nums=pts.filter(v=>v!=null);
  if(nums.length<2) return '';
  const w=opts.w||96, h=opts.h||24, pad=2;
  const mn=Math.min.apply(null,nums), mx=Math.max.apply(null,nums), rng=(mx-mn)||1;
  const step=(w-pad*2)/(pts.length-1);
  const xy=pts.map((v,i)=>v==null?null:[pad+i*step, h-pad-((v-mn)/rng)*(h-pad*2)]).filter(Boolean);
  const d=xy.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
  const first=xy[0], last=xy[xy.length-1];
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true">`
    + (opts.area?`<path d="${d} L ${last[0].toFixed(1)} ${h} L ${first[0].toFixed(1)} ${h} Z" fill="currentColor" opacity=".14"/>`:'')
    + `<path d="${d}" fill="none" stroke="currentColor" stroke-width="${opts.sw||1.6}" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>`
    + (opts.dot?`<circle cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="2.2" fill="currentColor"/>`:'')
    + `</svg>`;
}
function sparkBars(vals,opts){
  opts=opts||{};
  const w=opts.w||140, h=opts.h||22, n=vals.length||1;
  const cells=vals.map(v=>+v||0);
  const mx=opts.scale||Math.max.apply(null,[1].concat(cells));
  const bw=Math.max(1,(w/n)-(opts.gap==null?0.6:opts.gap));
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true">`
    + cells.map((v,i)=>{ if(v<=0) return ''; const bh=Math.max(1.5,(v/mx)*h);
        return `<rect x="${(i*(w/n)).toFixed(2)}" y="${(h-bh).toFixed(2)}" width="${bw.toFixed(2)}" height="${bh.toFixed(2)}" fill="currentColor"/>`; }).join('')
    + `</svg>`;
}
function dotgrid(cells){
  const s=10,g=4,W=3*s+2*g;
  return `<svg viewBox="0 0 ${W} ${W}" aria-hidden="true">`
    + cells.slice(0,9).map((on,i)=>{ const c=i%3,r=(i/3)|0;
        return `<rect x="${c*(s+g)}" y="${r*(s+g)}" width="${s}" height="${s}" rx="2" `
          + `fill="${on?'currentColor':'none'}" stroke="currentColor" stroke-opacity="${on?1:.4}" stroke-width="1.4"/>`; }).join('')
    + `</svg>`;
}

/* ============================================================
   NAVIGATION
   ============================================================ */
/* PHASE_8 — 8→5 top nav. The wordmark is Inicio (home + the live "Ahora"
   view, which absorbed the old Hoy). Consulta folded into Archivo (was
   Fuentes). Perfil stays on the gear button. Section ids that survive keep
   showTab / deep links / the ~55 builders working; old hashes are redirected
   in applyHash().
   TABS[0] (inicio) is the home target — rendered in the mobile bottom bar
   but NOT the desktop top strip (that's NAV = TABS.slice(1)). */
const TABS=[
  ['inicio','Inicio','M3 11 12 3l9 8M5 10v10h14V10'],
  ['historia','Historia','M4 5h16M4 12h16M4 19h10'],
  ['jugadores','Jugadores','M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4 21c0-4 4-6 8-6s8 2 8 6'],
  ['equipos','Equipos','M4 5h6v6H4ZM14 5h6v6h-6ZM4 13h6v6H4ZM14 13h6v6h-6'],
  /* PHASE_9 item 3b (owner-approved, redesign-v2): the old circle+
     meridian-lines path (M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM3 12h18M12
     3c3 4 3 14 0 18M12 3c-3 4-3 14 0 18) was visually indistinguishable
     from a plain globe icon, confirmed live and zoomed in the redesign-v2
     PHASE_9 report -- and shared the same circle-based construction as
     the rail logo right above it, so the two read as near-duplicates in
     the same rail. Replaced with a game-controller glyph: a rounded-rect
     body, a "+" d-pad, and two face-button dots (the two "h.01" segments
     are zero-length lines with round linecap, the standard technique for
     a filled dot inside a single stroked path). Nothing circular left --
     can't be confused with the logo or a globe again. */
  ['juega','Juega','M7 8h10a4 4 0 0 1 4 4v2a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4v-2a4 4 0 0 1 4-4zM8 11v4M6 13h4M16 12.2h.01M18.2 14.4h.01'],
  ['archivo','Archivo','M6 3h9l4 4v14H6ZM15 3v4h4M9 12h7M9 16h7']
];
const NAV=TABS.slice(1);                 /* desktop top strip — inicio is the wordmark */
const BOTTOM=TABS.map(t=>t[0]);          /* mobile bottom bar — all 6 */
/* Every <section role="tabpanel"> id. Perfil has no nav button (gear only). */
const PANELS=[...TABS.map(t=>t[0]),'perfil'];
let CURRENT='inicio';

/* PHASE_2_REDESIGN step 7 (owner-approved, redesign-v2): rail items, same TABS/NAV
   data the bottombar loop just below already uses (same icon paths, so the rail and
   the phone bar always agree visually) -- NAV's own tuples already carry the icon
   path as their 3rd element, so no TABS.find() lookup is needed here the way the
   bottombar loop needs one. role="tab"/aria-selected/aria-controls kept exactly as
   nav.tabs had them; aria-haspopup/aria-expanded dropped (the mega-menu they served
   is retired -- verified first, live, that every one of its destinations already has
   an equivalent subnav pill once you're on that section's page). Roving tabindex
   (0 on the active tab, -1 on the rest) is set here at build time and kept in sync
   on every later activation by _showPanel()'s own NAV loop, not duplicated here. */
function buildNav(){
  const s=$('#railNav'); s.innerHTML='';
  /* PHASE_9 item 1c (owner-approved, redesign-v2): Inicio isn't in NAV
     (it's the rail's own logo, not a tab -- see the comment above NAV's
     definition), so on Inicio no rail tab matches CURRENT and every one
     would get tabIndex=-1, making the whole tablist unreachable by Tab.
     Falls back to the first rail tab whenever CURRENT isn't one of NAV's
     own ids -- same fallback applied in _showPanel()'s own NAV loop. */
  const railFallbackFirst=!NAV.some(([navId])=>navId===CURRENT);
  NAV.forEach(([id,label,d])=>{
    const b=el('a');
    b.href='#'+id;
    b.id='tab-'+id; b.setAttribute('role','tab');
    b.setAttribute('aria-selected',id===CURRENT?'true':'false');
    b.setAttribute('aria-controls',id);
    b.setAttribute('aria-label',label);
    /* PHASE_9 item 1b (owner-approved, redesign-v2): .raillabel is
       display:none at the icon-only rail tier (860-1119px, main.css), so
       without an explicit aria-label every tab -- active or not -- had an
       empty accessible name there (confirmed via the real accessibility
       tree, not assumed). Reuses the SAME `label` string already used for
       .raillabel's own visible text -- no new copy. */
    b.tabIndex=(id===CURRENT||(railFallbackFirst&&id===NAV[0][0]))?0:-1;
    b.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${d}" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="raillabel">${esc(label)}</span>`;
    b.onclick=(e)=>{
      if(e.ctrlKey||e.metaKey||e.shiftKey||e.button!==0) return;   /* let the browser open a new tab/window natively */
      e.preventDefault(); showTab(id);
    };
    s.appendChild(b);
  });
  const bb=$('#bottombar'); bb.innerHTML='';
  BOTTOM.forEach(id=>{
    const t=TABS.find(x=>x[0]===id);
    const b=el('a');
    b.href='#'+id;
    b.setAttribute('role','tab'); b.setAttribute('aria-selected',id===CURRENT?'true':'false');
    b.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${t[2]}" stroke-linecap="round" stroke-linejoin="round"/></svg><span>${esc(t[1])}</span>`;
    b.onclick=(e)=>{
      if(e.ctrlKey||e.metaKey||e.shiftKey||e.button!==0) return;   /* let the browser open a new tab/window natively */
      e.preventDefault(); showTab(id);
    };
    b.onkeydown=(e)=>{ if(e.key===' '){ e.preventDefault(); showTab(id); } };
    bb.appendChild(b);
  });
}
/* PHASE_2_REDESIGN step 7: rail keyboard nav, same manual-activation model as
   Phase 4's showPlayerTab()/playerTabKeydown() (ArrowUp/ArrowDown move focus without
   activating, wrapping at both ends; Enter/Space activates the focused tab) -- a
   vertical tablist uses Up/Down per WAI-ARIA APG, not Left/Right. Wired via
   onkeydown="railKeydown(event)" on #rail itself (index.html), same delegation
   pattern the player tabs use. */
function railKeydown(e){
  const order=NAV.map(([id])=>'tab-'+id);
  const i=order.indexOf(e.target.id); if(i<0) return;
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){
    e.preventDefault();
    const next=order[(i+(e.key==='ArrowDown'?1:-1)+order.length)%order.length];
    order.forEach(t=>{ const el=document.getElementById(t); if(el) el.tabIndex=-1; });
    const nt=document.getElementById(next); if(nt){ nt.tabIndex=0; nt.focus(); }
  }else if(e.key==='Enter'||e.key===' '){
    e.preventDefault();
    showTab(e.target.id.replace(/^tab-/,''));
  }
}

/* ============================================================
   MEGA-MENU (PHASE_8.2 / 8.2b)
   Desktop: hover / focus a top item -> a panel with the section's
   views in grouped columns + one featured block. Mobile: the panel
   is display:none — the bottom bar goes to the section landing, which
   lists the same views. Every menu target is a view slug within the
   section (or "section/slug" to cross over); megaGo routes exactly
   like a subnav pill or a deep link — no scroll-jumping.
   ============================================================ */
const NAV_MENU={
  historia:{cols:[
    ['Campeones',[['La cinta 1930–2026','cinta'],['Títulos por franquicia','titulos'],['Dinastías','dinastias']]],
    ['Finales',[['El careo','finales']]],
    ['Premios',[['MVP y premios por año','premios'],['Campeones de anotación','premios']]],
    ['La liga',[['La regla de los refuerzos','refuerzos']]]
  ],feat:'topfranq'},
  jugadores:{cols:[
    ['Buscar',[['El índice completo','buscar'],['Comparar','comparar']]],
    ['Los mejores',[['Líderes de carrera','lideres'],['Récords de la liga','records'],['Salón de la Fama','salon']]],
    ['Más allá',[['Del BSN a la NBA','nba'],['Dirigentes','dirigentes'],['Canchas y coliseos','canchas']]]
  ],feat:'compare'},
  equipos:{cols:[
    ['Franquicias',[['Los 12 activos','activos'],['Franquicias desaparecidas','desaparecidos']]],
    ['Historia',[['Títulos por franquicia','historia/titulos'],['Números retirados','retirados']]],
    ['Los apoderados',[['Quién es el apoderado','duenos']]]
  ],feat:'myteam'},
  juega:{cols:[
    ['Hoy',[['La Cuadrícula del día','cuadricula']]],
    ['Modos',[['Temporada Perfecta','temporada'],['Quién soy','quiensoy'],['Sube y baja','subeybaja']]]
  ],feat:'daily'},
  archivo:{cols:[
    ['Preguntar',[['Consulta en español','preguntar'],['Consulta a la medida','constructor']]],
    ['El estado del archivo',[['Cobertura, huecos y fuentes','cobertura'],['Calidad de datos','calidad'],['Calendario de temporada','calendario']]],
    ['Referencia',[['Glosario','glosario']]]
  ],feat:'gap'}
};
/* PHASE_2_REDESIGN step 7: MEGA_TAB retired along with the mega-menu it tracked
   (the hover-dropdown that used to set it) -- megaGo()'s own callers are now only
   megaFeat()'s buttons on a section's own landing page (paintLandingFeats(), still
   very much in use), so CURRENT is always the right "from" section. */
function megaGo(target){
  let s=CURRENT, v=target;
  if(target.indexOf('/')>-1){ const parts=target.split('/'); s=parts[0]; v=parts[1]; }
  showView(s,v);
  if(s==='archivo'&&v==='preguntar'){ const i=$('#askInput'); if(i) setTimeout(()=>i.focus(),50); }
}

function titleComb(f,opts){
  return f.won.length ? sparkBars(YEARS.map(y=>f.won.indexOf(y)>-1?1:0),opts||{w:180,h:24,gap:1}) : '';
}
function megaFeat(k){
  if(k==='topfranq'){
    const best=FKEYS.slice().sort((a,b)=>F[b].won.length-F[a].won.length)[0];
    if(!best) return '';
    const f=F[best];
    return `<div class="fx">El más ganador</div>
      <div style="display:flex;align-items:center;gap:10px;margin-top:2px">${crest(best,34,42)}
        <div class="fn">${f.won.length}</div></div>
      <div class="mf-viz" style="color:${f.c1}">${titleComb(f)}</div>
      <div class="ft">${esc(f.name.split(' de ')[0])}</div>
      <div class="fd">títulos en 97 temporadas${f.won.length?' · último en '+Math.max.apply(null,f.won):''}</div>
      <button class="btn" style="padding:6px 12px;font-size:12px" onclick="megaGo('titulos')">Ver todos</button>`;
  }
  if(k==='compare'){
    const mv=cmpMiniViz('Georgie Torres','Mario Morales');
    return `<div class="fx">Comparar</div>
      <div class="ft" style="margin-top:2px">Georgie Torres ⇄ Mario Morales</div>
      ${mv?`<div class="mf-viz">${mv}</div>`:''}
      <div class="fd">Dos o tres jugadores lado a lado — las casillas vacías son huecos del archivo, no ceros.</div>
      <button class="btn" style="padding:6px 12px;font-size:12px" onclick="cmpPreset('Georgie Torres','Mario Morales')">Abrir</button>`;
  }
  if(k==='myteam'){
    const p=prof(), f=p.club&&F[p.club]?F[p.club]:null;
    return `<div class="fx">Tu equipo</div>
      ${f?`<div style="display:flex;align-items:center;gap:10px;margin-top:2px">${crest(p.club,30,36)}
        <div class="ft">${esc(f.name)}</div></div>
        ${f.won.length?`<div class="mf-viz" style="color:${f.c1}">${titleComb(f,{w:180,h:22,gap:1})}</div>`:''}
        <div class="fd">${f.won.length?f.won.length+(f.won.length===1?' título':' títulos'):'sin títulos'} · el archivo se reordena a su alrededor</div>`
      : `<div class="fd" style="margin-top:2px">Escoge un club y el archivo se reordena a su alrededor — tu equipo primero en cada tabla.</div>`}
      <button class="btn" style="padding:6px 12px;font-size:12px" onclick="showTab('perfil')">${f?'Cambiar':'Escoger club'}</button>`;
  }
  if(k==='daily'){
    const n=(typeof puzzleNo==='function')?puzzleNo():'—';
    return `<div class="fx">Hoy</div>
      <div style="display:flex;align-items:flex-end;gap:12px;margin-top:2px">
        <div class="fn">#${n}</div>
        <span class="mf-dot">${dotgrid([0,1,0, 0,0,1, 1,0,0])}</span></div>
      <div class="ft">La Cuadrícula del día</div>
      <div class="fd">Nueve casillas, un jugador que encaje en cada cruce de club × logro.</div>
      <button class="btn" style="padding:6px 12px;font-size:12px" onclick="megaGo('cuadricula')">Jugar</button>`;
  }
  if(k==='gap'){
    return `<div class="fx">Lo que este archivo no sabe</div>
      <div class="ft" style="margin-top:2px">Antes de 2011 no hay estadística por temporada</div>
      <div class="mf-viz">${sparkBars(COVERAGE.map(c=>c[1]),{w:180,h:24,scale:100,gap:2})}</div>
      <div class="fd">Ese es el muro real. Todo lo demás — los huecos, los conflictos entre fuentes, de dónde sale cada dato — está aquí, dicho de frente.</div>
      <button class="btn" style="padding:6px 12px;font-size:12px" onclick="megaGo('cobertura')">Ver los huecos</button>`;
  }
  return '';
}

/* the featured block also heads each section's landing view; re-render
   it on club change (the "myteam" variant reads the stored club). */
function paintLandingFeats(){
  Object.keys(NAV_MENU).forEach(id=>{
    const host=document.querySelector('#'+id+' .view[data-view="__landing"] .landing > .mega-feat');
    if(host) host.innerHTML=megaFeat(NAV_MENU[id].feat);
  });
}

/* PHASE_2_REDESIGN step 7: the mega-menu's own open/close machinery
   (openMega/closeMega/scheduleClose/cancelClose/megaCloseT, the #megaPanel element,
   the Escape-key and scroll-close listeners) is retired along with it -- verified
   first, live, that every destination it offered already has an equivalent subnav
   pill once you're on that section's page (redesign-v2 PHASE 7 report). megaFeat()/
   megaGo()/NAV_MENU/paintLandingFeats() all stay: the featured block they build is
   still very much in use, just on each section's own landing page, never through a
   hover dropdown. */

/* toggle the <section> panels + nav aria; returns whether the section
   actually changed. The public entry is showTab(); deep links and the
   subnav call showView() which calls this. */
function _showPanel(id,noScroll){
  const changed = CURRENT!==id;
  CURRENT=id;
  PANELS.forEach(t=>{ const s=document.getElementById(t); if(s) s.hidden = (t!==id); });
  const shown=document.getElementById(id);
  if(shown && changed){   /* re-trigger the enter animation */
    shown.classList.remove('panel-enter'); void shown.offsetWidth; shown.classList.add('panel-enter');
  }
  /* PHASE_9 item 1c (owner-approved, redesign-v2): same fallback as
     buildNav() -- id may be 'inicio', which isn't in NAV, so nothing
     would match and the whole rail tablist would go unreachable by Tab. */
  const railFallbackFirst=!NAV.some(([navId])=>navId===id);
  NAV.forEach(([t])=>{
    const btn=document.getElementById('tab-'+t);
    if(btn){ btn.setAttribute('aria-selected',t===id?'true':'false'); btn.tabIndex=(t===id||(railFallbackFirst&&t===NAV[0][0]))?0:-1; }
  });
  document.querySelectorAll('#bottombar button').forEach((b,i)=>{
    b.setAttribute('aria-selected',BOTTOM[i]===id?'true':'false');
  });
  const active=document.getElementById('tab-'+id);
  if(active&&active.scrollIntoView) active.scrollIntoView({block:'nearest',inline:'center'});
  if(!noScroll){
    const smooth = changed && !matchMedia('(prefers-reduced-motion:reduce)').matches;
    window.scrollTo({top:0,behavior:smooth?'smooth':'auto'});
  }
  return changed;
}


/* ============================================================
   SECTION VIEW ROUTER (PHASE_8.2b)
   Each nav section holds a set of .view divs — one shown at a time,
   each with a #section/view URL and a subnav pill. buildViews()
   assembles them from the section markup at boot (replaced
   foldSections). showView() is the single switch.
   ============================================================ */
const VIEW_SECS=['historia','jugadores','equipos','juega','archivo'];
let VIEW_NOW={};
let HASH_ECHO=null;
function syncSubnav(sec,view){
  const nav=document.querySelector('#'+sec+' .subnav'); if(!nav) return;
  let active=null;
  Array.from(nav.children).forEach(b=>{
    const on=b.dataset.view===view;
    b.setAttribute('aria-current',String(on));
    if(on) active=b;
  });
  /* PHASE_49: keep the active pill in view on every change (initial load,
     deep-link/hash entry, back/forward) -- scrollLeft only, never
     scrollIntoView() (that can move the whole page vertically too). */
  if(active && nav.scrollWidth>nav.clientWidth){
    const target=Math.max(0,Math.min(
      active.offsetLeft-(nav.clientWidth-active.offsetWidth)/2,
      nav.scrollWidth-nav.clientWidth
    ));
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    nav.scrollTo({left:target,behavior:reduced?'auto':'smooth'});
  }
}

/* ============================================================
   SORTABLE / EXPORTABLE TABLE
   One builder for every table in the app: click a header to sort,
   one button to take the exact rows on screen to CSV. The export
   is the point — a stats site you cannot get data out of is a
   poster, not a tool.
   ============================================================ */
let TBL_SEQ=0;
function buildTable(host,cols,rows,opts){
  opts=opts||{};
  const id='t'+(++TBL_SEQ);
  const state={sort:opts.sort==null?null:opts.sort,dir:opts.dir||-1};
  host.innerHTML='';
  const wrap=el('div','tblwrap'); host.appendChild(wrap);
  const meta=el('div','tbl-meta'); host.appendChild(meta);

  function sorted(){
    if(state.sort==null) return rows.slice();
    const c=cols[state.sort];
    return rows.slice().sort((a,b)=>{
      let x=a[state.sort],y=b[state.sort];
      if(c.num){ x=(x==null?-Infinity:+x); y=(y==null?-Infinity:+y); return (x-y)*state.dir; }
      return String(x==null?'':x).localeCompare(String(y==null?'':y),'es')*state.dir;
    });
  }
  function render(){
    const data=sorted();
    wrap.classList.toggle('tall',data.length>24);   /* sticky header + zebra */
    let h='<table><thead><tr>';
    cols.forEach((c,i)=>{
      const arrow = state.sort===i ? `<span class="arrow">${state.dir>0?'▲':'▼'}</span>` : '';
      h+=`<th class="${c.num?'num ':''}sortable" data-i="${i}" scope="col">${esc(c.label)}${arrow}</th>`;
    });
    h+='</tr></thead><tbody>';
    data.forEach(r=>{
      h+='<tr>';
      cols.forEach((c,i)=>{
        const v=c.render?c.render(r[i],r):esc(dash(r[i]));
        h+=`<td class="${c.num?'num':(c.wide?'name':'')}">${v}</td>`;
      });
      h+='</tr>';
    });
    h+='</tbody></table>';
    wrap.innerHTML=h;
    wrap.querySelectorAll('th.sortable').forEach(th=>{
      th.onclick=()=>{
        const i=+th.dataset.i;
        if(state.sort===i) state.dir=-state.dir; else {state.sort=i;state.dir=cols[i].num?-1:1;}
        render();
      };
    });
    /* right-edge shadow on the sticky first column, only once scrolled */
    const onScroll=()=>wrap.classList.toggle('scrolled',wrap.scrollLeft>2);
    wrap.onscroll=onScroll; onScroll();
    meta.innerHTML=`<span>${data.length} fila${data.length===1?'':'s'}</span>`;
    const b=el('button','btn'); b.style.padding='5px 10px'; b.style.fontSize='12px';
    b.textContent='Descargar CSV';
    /* opts.csvHead / opts.csvRow: export a different (fuller) shape than the columns on screen */
    b.onclick=()=>downloadCSV(opts.csvHead||cols.map(c=>c.label),opts.csvRow?data.map(opts.csvRow):data,(opts.file||'bsn_'+id)+'.csv');
    meta.appendChild(b);
    if(opts.note){ const n=el('span'); n.textContent=opts.note; meta.appendChild(n); }
  }
  render();
  return {render,state};
}
function csvCell(v){
  if(v==null) return '';
  const s=String(v);
  return /[",\n;]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s;
}
function downloadCSV(head,rows,file){
  const lines=[head.map(csvCell).join(',')].concat(rows.map(r=>r.map(csvCell).join(',')));
  const blob=new Blob(['\ufeff'+lines.join('\n')],{type:'text/csv;charset=utf-8'});
  const a=el('a'); a.href=URL.createObjectURL(blob); a.download=file;
  document.body.appendChild(a); a.click();
  setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},400);
}
function bars(host,rows,max,fmt){
  const m=max||Math.max.apply(null,rows.map(r=>r[1]))||1;
  host.innerHTML='<div class="bars">'+rows.map(r=>{
    const w=Math.max(2,Math.round(r[1]/m*100));
    return `<div class="barrow"><span class="bl">${esc(r[0])}</span>
      <span class="bartrack"><span class="barfill" style="width:${w}%;background:${r[2]||'var(--azul)'}"></span></span>
      <span class="bv">${esc(fmt?fmt(r[1]):r[1])}</span></div>`;
  }).join('')+'</div>';
}
/* ============================================================
   HOY
   The official app owns "today" during the season. From September
   to March it has nothing to show. So this tab opens on the one
   number nobody else is counting: how long the island has to wait.
   ============================================================ */
function daysBetween(a,b){
  const A=new Date(a+'T12:00:00'), B=new Date(b+'T12:00:00');
  return Math.round((B-A)/86400000);
}
function todayISO(){
  const d=new Date();
  return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
}
/* PHASE_9 item 3 (owner-approved, redesign-v2): hero rebuild toward the
   approved mockup's headline/dek/stat-row layout. h/p keep the exact same
   three-way season-state text they always had (dropping p was considered
   and rejected: A4 in the redesign-v2 PHASE_9 report confirmed the
   March-August season-shape fact does NOT appear anywhere else on Inicio,
   only in Archivo's #calShape -- so it stays, now a small caption under
   .hero-status instead of the old .herotext p). The old typed
   "21 de marzo de 2027" is gone -- fmtLongDate(SEASON_STATE.nextEstimate)
   (web/js/helpers.js, already used for player bio dates) computes it for
   real, so a future SEASON_STATE update can't silently desync the two.
   .hero-headline is now the page's own <h1> (buildHub()'s own <h1
   class="hubhead"> is demoted to <h2> in the same commit, below, so
   Inicio keeps exactly one h1 like every other panel -- see the
   redesign-v2 PHASE_9 report, item A5). */
function buildHero(){
  const t=todayISO();
  const since=daysBetween(SEASON_STATE.lastGame,t);
  const until=daysBetween(t,SEASON_STATE.nextEstimate);
  const f=F[SEASON_STATE.champ];
  let n,u,h,p;
  if(since<0){ n=Math.abs(since); u='días para el juego decisivo'; h='La temporada sigue viva'; p='El archivo se actualiza cuando termine.'; }
  else if(until>0){
    n=until; u=until===1?'día para la 98.ª':'días para la 98.ª temporada';
    h='Temporada muerta, día '+since;
    p='El BSN corre de finales de marzo a agosto. Los otros siete meses no hay marcador que mirar — hay '+YEARS.length+' temporadas que revisar. Para eso es esto.';
  } else {
    n=since; u='días desde el último juego'; h='Debería estar rodando';
    p='La fecha estimada de apertura ya pasó y la liga no ha anunciado la real.';
  }
  const d=new Date();
  const eye = (DIAS[d.getDay()]+' '+d.getDate()+' de '+MESES[d.getMonth()]+' de '+d.getFullYear()).toUpperCase();
  const backToBack = f.won.indexOf(2025)>-1 && Math.max.apply(null,f.won)===2026;
  const mostEver = FKEYS.every(k=>F[k].won.length<=f.won.length);
  const t2 = 'título '+SEASON_STATE.title+' · '+(backToBack?'bicampeonato':(mostEver?'el máximo de la liga':'récord del club'));
  /* Stat 3: computed, not hardcoded to Bayamón -- today's real leader,
     but this stays whoever actually leads if the data ever changes. */
  const leaderKey = FKEYS.reduce((best,k)=>F[k].won.length>F[best].won.length?k:best, FKEYS[0]);
  const leader = F[leaderKey];
  $('#heroBox').innerHTML=`
  <div class="hero">
    <div class="ed-eye">BSN · ${esc(eye)}</div>
    <h1 class="hero-headline">${YEARS.length} temporadas <span class="hero-headline-full">de baloncesto puertorriqueño,</span> documentadas</h1>
    <p class="hero-dek">Campeones, jugadores y récords desde 1930, con las fuentes y los huecos a la vista.</p>
    <p class="hero-status">${esc(h)} <span class="dim">· Apertura estimada: ${esc(fmtLongDate(SEASON_STATE.nextEstimate))} · ${esc(SEASON_STATE.nextLabel)}</span></p>
    <p class="hero-note">${esc(p)}</p>
    <div class="hero-stats">
      <div class="hero-stat tri-block tri-block-azul"><div class="ed-stat">${n}</div><div class="u">${esc(u)}</div></div>
      <div class="hero-stat"><div class="ed-stat">${YEARS.length}</div><div class="u">temporadas, de ${YEARS[0]} a ${YEARS[YEARS.length-1]}</div></div>
      <div class="hero-stat tri-block tri-block-rojo"><div class="ed-stat">${leader.won.length}</div><div class="u">títulos de ${esc(leader.name)}, el club más ganador</div></div>
    </div>
    <div class="herofoot">
      <div class="trophy">${crest(SEASON_STATE.champ,30,36)}
        <div><div class="t1">${esc(f.name)} — campeón 2026</div>
             <div class="t2">${esc(t2)}</div></div></div>
      <div class="heroaction">
        <span class="herospark" style="color:${f.c1}">${titleComb(f,{w:150,h:20,gap:1})}</span>
        <button class="btn" onclick="showView('historia','cinta')">Ver la cinta</button>
      </div>
    </div>
  </div>`;
}

/* PHASE_12 (owner-approved, redesign-v2): finds a real F key by its own real F[k].name --
   FIVE_2026's own club field is a NAME string, not a key (data.js), and for Harrell it's
   literally the conflict sentence itself ("San Germán según RealGM..."), which matches no
   real club -- returns undefined there, so the caller can skip the crest rather than call
   crest() on a bad key (crest() itself already no-ops on an unknown key, but skipping is
   more honest than rendering an empty shield for a deliberately-ambiguous row). */
function clubKeyByName(name){ return FKEYS.find(k=>F[k].name===name); }
function buildFinalBrava(){
  const host=$('#finalBrava');
  const c=F[FINALS_2026.champ], r=F[FINALS_2026.ru];
  /* PHASE_12 (owner-approved, redesign-v2): the real .series/.seriesrow overview line (item
     6 doesn't ask to change this specific piece, and it already works) is kept exactly as
     before, above the NEW .series-track (item 6's own ask: a real 7-game boxscore as score
     cards) -- both shown, nothing dropped. */
  let h=`<div class="series">
    <div class="seriesrow win">${crest(FINALS_2026.champ,30,36)}<span class="nm">${esc(c.name)}</span><span class="sc">4</span></div>
    <div class="seriesrow lose">${crest(FINALS_2026.ru,30,36)}<span class="nm">${esc(r.name)}</span><span class="sc">3</span></div>
  </div>
  <div class="good">MVP de la final: <b>${esc(FINALS_2026.mvp)}</b>. ${esc(FINALS_2026.note)}</div>
  <div class="series-track">${FINALS_2026.games.map(g=>{
    const [n,,,,hs,as]=g;
    const win = (hs>as) === (g[2]===FINALS_2026.champ);
    return `<div class="gcard${win?' win':''}"><div class="gn">G${n}</div><div class="gs mono">${hs}–${as}</div></div>`;
  }).join('')}</div>`;
  host.innerHTML=h;

  const tbl=el('div'); host.appendChild(tbl);
  const rows=FINALS_2026.games.map(g=>{
    const [n,date,home,away,hs,as,st,note]=g;
    const win = hs>as ? home : away;
    return [ 'Juego '+n, date, F[home].abbr+' (L)', F[away].abbr+' (V)', hs+'-'+as, F[win].abbr, st, note ];
  });
  buildTable(tbl,[
    {label:'Juego'},{label:'Fecha'},{label:'Local'},{label:'Visita'},
    {label:'Marcador',num:false},{label:'Ganó'},{label:'Serie'},{label:'Qué pasó',wide:true}
  ],rows,{file:'final_brava_2026',sort:null});

  const semi=el('div');
  semi.innerHTML='<h4 class="sub">Cómo llegaron</h4>';
  host.appendChild(semi);
  const st=el('div'); semi.appendChild(st);
  buildTable(st,[{label:'Ronda'},{label:'Ganó'},{label:'Perdió'},{label:'Serie'},{label:'Detalle',wide:true}],
    SEMIS_2026.map(s=>[s[0],F[s[1]].name,F[s[2]].name,s[3],s[4]]),{file:'semis_2026',sort:null});

  /* PHASE_12 (owner-approved, redesign-v2): .awards-grid (item 6) -- same real AWARDS_2026
     rows, same 4 real fields (premio/jugador/club/nota); club resolved to a real crest()
     when it names a real franchise (most rows), a bare "—" av box when it doesn't
     (Dirigente/Novato/Defensor/Sexto/Excelencia rows whose club field is literally "—" in
     the real data) -- never a fabricated crest. The real nota text is kept, appended as a
     4th line only when that row actually has one (several real rows have an empty ''). */
  const aw=el('div');
  aw.innerHTML='<h4 class="sub">Premios 2026</h4><div class="awards-grid">'+
    AWARDS_2026.map(a=>{
      const ak=clubKeyByName(a[2]);
      return `<div class="award">${ak?crest(ak,28,32):'<span class="av" style="width:28px;height:28px;display:inline-block;flex:none"></span>'}
        <div class="ab"><div class="al">${esc(a[0])}</div><div class="an">${esc(a[1])}</div>
        <div class="ac">${esc(a[2])}${a[3]?' · '+esc(a[3]):''}</div></div></div>`;
    }).join('')+'</div>';
  host.appendChild(aw);

  /* PHASE_12 (owner-approved, redesign-v2): .allstar-row/.chip (item 6) -- same real
     FIVE_2026 rows. Harrell's own row is the real, unresolved source conflict (data.js) --
     clubKeyByName() returns undefined for it (its "club" field is the conflict sentence
     itself, not a name), so that one chip renders without a crest rather than guessing
     which of the two clubs to show; every other real chip gets its real crest(). The
     Harrell sentence right below is copied verbatim from the real, currently-live string
     -- not reworded -- wrapped in .conflict-note. */
  const q=el('div');
  q.innerHTML='<h4 class="sub">Quinteto Ideal</h4><div class="allstar-row">'+
    FIVE_2026.map(p=>{
      const ck=clubKeyByName(p[2]);
      return `<span class="chip">${ck?crest(ck,22,26):''}<span class="cn">${esc(p[0])}</span><span class="cc">${esc(p[1])} · ${esc(p[2])}</span></span>`;
    }).join('')+'</div>'+
    `<div class="conflict-note"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>Montrezl Harrell aparece con dos clubes distintos según la fuente. RealGM lo pone en San Germán, Noticel en Caguas. El archivo no escoge por ti.</div>`;
  host.appendChild(q);

  /* PHASE_12 (owner-approved, redesign-v2): .news-mini/.newscard (item 6) -- same real
     6-row NEWS array, all 3 real fields kept (the mockup's own sample newscard only shows
     a headline; this app's own date/category tag and one-line summary are real content,
     not dropped to match the simpler sample). */
  const nw=el('div');
  nw.innerHTML='<h4 class="sub">Lo último del cierre</h4>'+
    '<div class="news-mini">'+NEWS.map(n=>`<div class="newscard">
      <div class="nk">${esc(n[0])}</div>
      <div class="nt">${esc(n[1])}</div>
      <div class="muted" style="font-size:var(--fs-2xs);margin-top:4px">${esc(n[2])}</div></div>`).join('')+'</div>'+
    '<p class="note">Titulares vistos en la app oficial del BSN el 2 de septiembre de 2026. Solo los títulos, resumidos — el texto de los artículos es de sus medios.</p>';
  host.appendChild(nw);
}

function buildStandings2026(){
  const host=$('#standings2026'); host.innerHTML='';
  const mine=ST.get('club');
  ['A','B'].forEach(g=>{
    const hd=el('div','standhead');
    hd.innerHTML=`<h4>Grupo ${g}</h4><span class="dim" style="font-size:var(--fs-2xs)">34 juegos · los cuatro primeros a cuartos</span>`;
    host.appendChild(hd);
    const w=el('div','tblwrap'); host.appendChild(w);
    let h='<table><thead><tr><th>#</th><th>Equipo</th><th class="num">PG</th><th class="num">PP</th>'+
      '<th class="num">PCT</th><th class="num">DIF</th><th class="num">LOC</th><th class="num">VIS</th></tr></thead><tbody>';
    const topW=STAND2026[g][0][1], topL=STAND2026[g][0][2];
    STAND2026[g].forEach((r,i)=>{
      const [k,W,L,P,loc,vis]=r;
      const gb=((topW-W)+(L-topL))/2;   /* standard games-behind, not published by the league */
      const cls=(i===3?'cut ':'')+(k===mine?'me':'');
      h+=`<tr class="${cls}"><td class="rank">${i+1}</td>
        <td class="team">${crest(k,22,26)}<span>${esc(F[k].name.split(' de ')[0])}</span></td>
        <td class="num">${W}</td><td class="num">${L}</td><td class="num">${P.toFixed(3).replace('0.','.')}</td>
        <td class="num">${gb===0?'—':gb.toFixed(1)}</td><td class="num">${esc(loc)}</td><td class="num">${esc(vis)}</td></tr>`;
    });
    h+='</tbody></table>';
    w.innerHTML=h;
  });
  const n=el('p','note');
  n.innerHTML='La línea azul marca el corte de cuartos de final. DIF es juegos detrás del primero, calculado aquí — la app oficial no lo publica. '+
    'Bayamón y Caguas terminaron 22-12 empatados; Bayamón se quedó el primer lugar del Grupo A.';
  host.appendChild(n);
  /* PHASE_12 (owner-approved, redesign-v2): item 6 -- "just restyle the button/table."
     Real crest() was already wired here before this phase; the cutoff-row class (.cut) and
     DIF computation just above are untouched. Only the export button's class changed. */
  const dl=el('button','exportbtn2'); dl.textContent='Descargar posiciones 2026 (CSV)';
  dl.onclick=()=>{
    const rows=[];
    ['A','B'].forEach(g=>STAND2026[g].forEach((r,i)=>rows.push([g,i+1,F[r[0]].name,r[1],r[2],r[3],r[4],r[5]])));
    downloadCSV(['grupo','pos','equipo','ganados','perdidos','pct','local','visita'],rows,'bsn_posiciones_2026.csv');
  };
  host.appendChild(dl);
}

/* PHASE_12 (owner-approved, redesign-v2): item 6 -- "reuse Premios' .lead-list styling
   from Historia" (PHASE_11, main.css -- the exact same classes). Same real LEAD2026 rows,
   same real per-row "expandido"/"la app abrevia el nombre" computation (r[3] truthy or
   not), same real crest() (r[1] is already a real club key here, unlike FIVE_2026's own
   club-NAME field). Dropped: buildTable()'s own CSV-export affordance -- a lead-list isn't
   a buildTable() output, the same real tradeoff PHASE_11 already made for Historia's own
   Premios scoring/MVP lists, for the same reason. */
function buildLeaders2026(){
  const host=$('#leaders2026');
  host.innerHTML='<div class="lead-list">'+LEAD2026.map((r,i)=>{
    const name=r[3]||r[0], expanded=!!r[3];
    return `<div class="lead-row">
      <div class="yrchip mono">#${i+1}</div>
      <div class="who" style="display:flex;align-items:center;gap:var(--sp-2_5)">${crest(r[1],28,32)}
        <div style="min-width:0"><div class="pn">${esc(name)}${!expanded?' <span class="muted" style="cursor:help;font-weight:400" title="La app oficial del BSN imprime solo la inicial del nombre">†</span>':''}</div>
        <div class="cl">${esc(F[r[1]].name)}</div></div>
      </div>
      <div class="val"><div class="n mono">${r[2]}</div><div class="u">ppj</div></div>
    </div>`;
  }).join('')+'</div>'
    +'<p class="scrollnote">Fuente: app oficial del BSN, 2 sep 2026. La app imprime solo la inicial del nombre. Dos de los cinco se pudieron confirmar contra la prensa; los otros tres quedan como aparecen, sin adivinar.</p>';
}

function buildClubPicker(){
  const host=$('#clubPicker');
  if(!host) return;   /* PHASE_6 — picker lives in Perfil now (its own tiles); this id is gone from Hoy */
  const cur=ST.get('club');
  host.innerHTML='<div class="tiles">'+ACTIVE.map(k=>
    `<button class="teamtile" aria-pressed="${k===cur?'true':'false'}" onclick="pickClub('${k}')">
      ${crest(k,34,41)}<span class="tn">${esc(F[k].name.split(' de ')[0])}</span>
      <span class="tt">${F[k].won.length} título${F[k].won.length===1?'':'s'}</span></button>`).join('')+'</div>';
}
function pickClub(k){
  setProf('club', prof().club===k ? null : k);
  buildClubPicker(); buildClubCard(); drawClubPill(); buildStandings2026(); if(typeof paintLandingFeats==='function') paintLandingFeats();
  try{ buildHub(); }catch(e){ console.error('BSN: falló el hub al cambiar de club',e); }
  const b=$('#profBody'); if(b&&b.innerHTML) buildProfile();
}
function drawClubPill(){
  const k=ST.get('club');
  $('#clubPillName').textContent = k ? F[k].name.split(' de ')[0] : 'Mi club';
  $('#clubPillCrest').innerHTML = k ? crest(k,20,24) : '';
  /* PHASE_9 item 1 (owner-approved, redesign-v2): rail's own Mi club
     button (>=860px, header.top's clubpill is gone there) mirrors the
     same crest/name, same "Mi club" fallback string, no new copy. */
  const rn=$('#railClubName'); if(rn) rn.textContent = k ? F[k].name.split(' de ')[0] : 'Mi club';
  const rc=$('#railClubCrest'); if(rc) rc.innerHTML = k ? crest(k,20,24) : '';
  /* #railClub carries no static aria-label (matching #clubPill, which has
     none either -- both rely on their own visible text for the accessible
     name). But .raillabel is display:none at the icon-only rail tier
     (860-1119px, main.css), unlike #clubPill's text which is never
     hidden -- so #railClub alone needs an explicit, dynamically-kept-in-
     sync aria-label to still have a real accessible name at that width.
     Same live-updated-attribute pattern applyTheme() already uses for
     #railTheme, just triggered from here instead. */
  const rb=$('#railClub'); if(rb) rb.setAttribute('aria-label', k ? F[k].name.split(' de ')[0] : 'Mi club');
}
function buildClubCard(){
  const host=$('#clubCard');
  if(!host) return;
  const k=ST.get('club');
  if(!k){ host.innerHTML='<p class="note">Sin club escogido. Toca uno arriba.</p>'; return; }
  const f=F[k];
  const last=f.won.length?Math.max.apply(null,f.won):null;
  const drought=last?LAST-last:null;
  /* Rival = the club it has met most often in a final, either side. */
  const tally={};
  f.won.forEach(y=>{const o=ruOf[y]; if(o)tally[o]=(tally[o]||0)+1;});
  f.ru.forEach(y=>{const o=champOf[y]; if(o)tally[o]=(tally[o]||0)+1;});
  const rival=Object.keys(tally).sort((a,b)=>tally[b]-tally[a])[0];
  const st=[].concat(STAND2026.A,STAND2026.B).find(r=>r[0]===k);
  const v=VENUES[k];
  host.innerHTML=`<div class="card" style="margin-top:var(--sp-3);display:flex;gap:var(--sp-4);flex-wrap:wrap;align-items:flex-start">
    ${crest(k,54,64)}
    <div style="flex:1;min-width:220px">
      <h4 style="font-size:20px">${esc(f.name)}</h4>
      <div class="muted" style="font-size:var(--fs-xs)">${esc(f.city)} · desde ${f.founded}${v?' · '+esc(v[0]):''}</div>
      <div class="chips" style="margin-top:var(--sp-2_5)">
        <span class="tag gold">${f.won.length} título${f.won.length===1?'':'s'}</span>
        <span class="tag">${f.ru.length} finales perdidas</span>
        ${last?`<span class="tag">Último: ${last}</span>`:'<span class="tag">Sin títulos</span>'}
        ${drought!=null?`<span class="tag ${drought>15?'gold':''}">${drought===0?'Campeón vigente':drought+' años de sequía'}</span>`:''}
        ${rival?`<span class="tag blue">Rival de finales: ${esc(F[rival].name.split(' de ')[0])} (${tally[rival]})</span>`:''}
        ${st?`<span class="tag">2026: ${st[1]}-${st[2]}</span>`:''}
      </div>
      ${f.coach?`<div class="note">Dirigente: ${esc(f.coach)}</div>`:''}
      ${f.won.length?`<div class="note">Campeón en ${f.won.join(', ')}</div>`:''}
    </div></div>`;
}

function buildOnThisDay(){
  const host=$('#onThisDay');
  const now=new Date(), m=now.getMonth()+1, d=now.getDate();
  const MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
  const exact=ON_THIS_DAY.filter(e=>e[0]===m&&e[1]===d);
  const near=ON_THIS_DAY.filter(e=>e[0]===m&&e[1]!==d).sort((a,b)=>a[1]-b[1]);
  let h='';
  if(exact.length){
    h+=exact.map(e=>`<div class="card" style="border-color:var(--rojo)">
      <div class="dim" style="font-size:var(--fs-3xs);letter-spacing:.07em;font-weight:600">HOY · ${e[1]} DE ${MONTHS[e[0]-1].toUpperCase()} DE ${e[2]}</div>
      <div style="font-weight:700;font-size:17px;margin-top:var(--sp-1)">${esc(e[3])}</div>
      <div class="muted" style="font-size:var(--fs-xs);margin-top:var(--sp-1)">${esc(e[4])}</div></div>`).join('');
  }
  const rest = near.length ? near : ON_THIS_DAY.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]).slice(0,5);
  const label = near.length
    ? `Lo demás de ${MONTHS[m-1]}`
    : `Nada del archivo está fechado en ${MONTHS[m-1]}. Los eventos más tempranos que sí lo están:`;
  h+=`<h4 class="sub">${esc(label)}</h4><div class="cards g2">`+
    rest.map(e=>`<div class="card"><div class="dim" style="font-size:var(--fs-3xs);letter-spacing:.07em;font-weight:600">${e[1]} ${MONTHS[e[0]-1]} ${e[2]}</div>
      <div style="font-weight:700;margin-top:3px">${esc(e[3])}</div>
      <div class="muted" style="font-size:var(--fs-xs);margin-top:3px">${esc(e[4])}</div></div>`).join('')+'</div>';
  host.innerHTML=h;
}

const CAL_KIND={
  confirmado:{cls:'tag blue', label:'Confirmado'},
  proyectado:{cls:'tag gold', label:'Estimado'},
  'patrón'  :{cls:'tag',      label:'Patrón, sin fecha'}
};

function buildCalendar(){
  const today=todayISO();

  /* Two counts, never blended into one. The nearest confirmed date and
     the projected opener answer different questions, and showing only
     the projection would let an estimate pass for a fixture. */
  const dated=CAL_MILESTONES.filter(m=>m.d&&m.d>=today).sort((a,b)=>a.d<b.d?-1:1);
  const nextConf=dated.find(m=>m.k==='confirmado');
  const opener=CAL_MILESTONES.find(m=>m.k==='proyectado');
  const dOpen=opener?daysBetween(today,opener.d):null;
  const dConf=nextConf?daysBetween(today,nextConf.d):null;
  const sinceLast=daysBetween(SEASON_STATE.lastGame,today);

  $('#calCount').innerHTML=`<div class="strip">
    <div><div class="n">${dOpen!=null&&dOpen>0?dOpen:'—'}</div>
      <div class="l">días para la apertura estimada de 2027</div></div>
    <div><div class="n">${dConf!=null&&dConf>0?dConf:'—'}</div>
      <div class="l">días para la próxima fecha confirmada</div></div>
    <div><div class="n">${sinceLast>0?sinceLast:'—'}</div>
      <div class="l">días desde el último juego del BSN</div></div>
  </div>
  <p class="note">La apertura de 2027 es un estimado de este archivo. La liga no ha
    anunciado fechas.</p>`;

  /* PHASE_12 (owner-approved, redesign-v2): .milestone/.mbadge treatment (item 6) -- one
     real row per real CAL_MILESTONES entry (4 today, not the mockup's own hardcoded
     3-row sample), real CAL_KIND label/class per entry via MBADGE_CLS below (a pure ascii
     alias for CAL_KIND's own 'patrón' key -- CSS class names with an accented character
     need escaping this file's own convention doesn't use anywhere else, so the accent-free
     alias is the safer choice, not a data change: CAL_KIND itself, and its label text, are
     untouched). */
  const MBADGE_CLS={confirmado:'confirmado',proyectado:'proyectado','patrón':'patron'};
  $('#calNext').innerHTML='<div class="cal-milestones">'+CAL_MILESTONES.map(m=>{
    const k=CAL_KIND[m.k]||CAL_KIND['patrón'];
    const when=m.d?fmtLongDate(m.d):m.m;
    const past=m.d&&m.d<today;
    return `<div class="milestone"><span class="dot"></span>
      <div class="m-body"><div class="m-t">${esc(m.t)}</div>
        <div class="m-d">${esc(when)}${past?' · ya pasó':''} — ${esc(m.b)}</div></div>
      <span class="mbadge ${MBADGE_CLS[m.k]||'patron'}">${esc(k.label)}</span>
    </div>`;
  }).join('')+'</div>';

  $('#calShape').innerHTML='<div class="timeline">'+CAL_SHAPE.map(s=>
    `<div class="tw">
      <div class="td">${esc(s.w)}</div>
      <div class="tt2">${esc(s.t)}</div>
      <div class="tb">${esc(s.b)}</div>
    </div>`).join('')+'</div>'
    +'<div class="warn"><b>'+esc(NEXT_SEASON.headline)+'</b><br>'+esc(NEXT_SEASON.body)+'</div>';

  const host=$('#calendarBox'); host.innerHTML='';
  buildTable(host,[
    {label:'Año',num:true},{label:'Temp.'},{label:'Inicio'},{label:'Fin reg.'},{label:'Playoffs'},
    {label:'J',num:true},{label:'Equipos',num:true},{label:'Formato',wide:true}
  ],CALENDAR.map(c=>[c.y,c.n,c.start,c.regEnd,c.po,c.games,c.teams,c.fmt]),{file:'calendario',sort:0,dir:-1});

  /* Stated, not hidden. An empty section with no explanation reads as a
     bug; a section that says what is missing and where it would come
     from is the honest version of the same gap. */
  $('#calGap').innerHTML=`
    <div class="warn">
      <b>Este archivo no tiene los juegos uno por uno.</b><br>
      No hay calendario de partidos aquí: ni fechas, ni horas, ni marcadores individuales,
      de ninguna temporada. Lo que sí hay es el marco de cada temporada — apertura, cierre
      de la fase regular, playoffs y formato — que es lo que se ve arriba.
    </div>
    <p class="note">Para los juegos de hoy, la fuente es bsnpr.com y la app oficial de la
      liga, que están enlazadas en Hoy bajo «Canales oficiales». Si en algún momento entra
      un calendario de partidos verificado, va aquí.</p>`;
}

/* PHASE_12 (owner-approved, redesign-v2): .channels-grid/.chnl (item 7) -- same real 8-row
   CHANNELS array, all 3 real fields kept (platform label, handle/name, one-line
   description) -- the mockup's own .chnl sample is a single-line icon+label only, but
   dropping the real platform tag and description to match it would be losing real content
   this phase's own opening line forbids. A plain circular-check icon stands in for every
   row (CHANNELS has no per-platform icon set in the real data to draw from, and inventing
   8 brand icons -- YouTube, Instagram, TikTok, X, Facebook, both app stores -- isn't a
   real asset this pass has; flagged in this phase's own report as a deliberate, minimal
   generic icon rather than fabricated brand marks). */
function buildChannels(){
  const host=$('#channels');
  host.innerHTML='<div class="channels-grid">'+CHANNELS.map(c=>
    `<a class="chnl" href="${esc(c[2])}" target="_blank" rel="noopener" style="align-items:flex-start;flex-direction:column;gap:2px">
      <span style="display:flex;align-items:center;gap:var(--sp-2_5)"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/></svg>
      <span class="dim" style="font-size:var(--fs-3xs);letter-spacing:.07em;font-weight:600">${esc(c[0]).toUpperCase()}</span></span>
      <span style="color:var(--azul-hi)">${esc(c[1])}</span>
      <span class="muted" style="font-size:var(--fs-2xs);font-weight:400">${esc(c[3])}</span></a>`).join('')+'</div>';
}
/* ============================================================
   HISTORIA
   ============================================================ */
/* PHASE_11 (owner-approved, redesign-v2): one real streak-walk, shared by buildRibbon()
   (which years to color as "dynasty") and buildDynasties() (the streak cards themselves) --
   the exact same run-detection buildDynasties() already did, factored out so both callers
   compute it identically rather than duplicating the walk. Same rule as before: a run is
   2+ consecutive seasons won by the same club; single titles are not a "dynasty." */
function historiaStreaks(){
  const runs=[]; let cur=null;
  YEARS.forEach(y=>{
    const k=champOf[y];
    if(k && cur && cur.k===k && y===cur.end+1){ cur.end=y; cur.n++; }
    else { if(cur&&cur.n>1) runs.push(cur); cur = k?{k,start:y,end:y,n:1}:null; }
  });
  if(cur&&cur.n>1) runs.push(cur);
  runs.sort((a,b)=>b.n-a.n||a.start-b.start);
  return runs;
}
/* PHASE_11 (owner-approved, redesign-v2): flat, always-44px ribbon (item 3/7 -- fixes the
   27.6x40px phone touch-target bug the survey found; the old fixed-10-column decade grid
   could never clear 44px at phone width, so the whole row/decade grouping is gone, not just
   the CSS). Every one of the 97 real years (YEARS, not a hardcoded list) gets its own cell,
   labeled by year. Colors 3 real states: a documented champion that's part of a real 2+
   dynasty streak (historiaStreaks() above, not hardcoded), a documented champion that isn't,
   and no champion on record -- matching the new 3-item legend exactly. */
function buildRibbon(){
  const host=$('#ribbon'); if(!host) return;
  /* Computed fresh on every call, not cached at module-parse time: YEARS/champOf are
     defined later, in index.html's own inline script (loaded after this file) -- a
     top-level const evaluated here would hit the exact "used before defined" failure
     already documented and fixed elsewhere in this file (BOOT/GRID_CLUBS). 97 years is
     cheap enough that a fresh walk per call needs no caching. */
  const dynastyYears=new Set();
  historiaStreaks().forEach(r=>{ for(let y=r.start;y<=r.end;y++) dynastyYears.add(y); });
  host.innerHTML=YEARS.map(y=>{
    const k=champOf[y];
    const cls=k?(dynastyYears.has(y)?'dynasty':'champ'):'';
    const label=k?(y+' — '+F[k].name):(y+' — sin campeón registrado');
    return `<button type="button" class="cell ${cls}" data-y="${y}" aria-label="${esc(label)}" onclick="showSeason(${y},this)">${y}</button>`;
  }).join('');
  /* PHASE_11 (owner-approved, redesign-v2): the readout used to sit on a static "Toca una
     temporada" placeholder until a real click -- the mockup's own script always renders a
     real year by default (2026 there). Shows the real most recent season (LAST, currently
     2026) here instead, via the pure renderReadout() below -- NOT showSeason(), which also
     navigates/sets the URL hash; that would rewrite the address bar on every page load
     regardless of which tab is actually open, a real side effect this avoids. */
  renderReadout(LAST);
  loadSeasonExtra(LAST);
  const b=document.querySelector('.cell[data-y="'+LAST+'"]'); if(b) b.classList.add('active');
}
function showSeason(y,btn){
  showView('historia','cinta',{noScroll:true,noHash:true});   /* the ribbon + readout live here */
  setHash('historia/temporada/'+y);
  document.querySelectorAll('.cell.active').forEach(c=>c.classList.remove('active'));
  if(btn) btn.classList.add('active');
  else { const b=document.querySelector('.cell[data-y="'+y+'"]'); if(b) b.classList.add('active'); }
  renderReadout(y);
  loadSeasonExtra(y);
}
function renderReadout(y){
  const k=champOf[y], r=ruOf[y];
  const host=$('#readout'); if(!host) return;
  /* PHASE_11 (owner-approved, redesign-v2): the mockup's own per-row "Fuente única" badge
     has no real backing data -- NOTES only carries 5 real footnotes (1942/1945/1953/2024/
     2026), not a source-confidence field for every one of the 97 seasons, so a "single
     source" pill is never shown here on a year that doesn't actually have one; that would
     be inventing a claim this app doesn't verify. Only a real NOTES[y] entry gets a badge
     (labeled with its own real caveat text), and only a genuinely missing champion gets the
     "missing" badge -- both real, both already-existing data, nothing new fabricated. */
  const noteBadge = NOTES[y] ? `<span class="hbadge note" title="${esc(NOTES[y])}">Nota del archivo</span>` : '';
  if(!k){
    host.innerHTML=`<div class="yr mono">${y}</div>
      <div class="champ-line">Campeón no documentado<span class="hbadge missing">Dato incompleto</span></div>
      <div class="vs-line">${esc(NOTES[y]||'Ninguna fuente consultada nombra un campeón para este año.')}</div>`;
  }else{
    const f=F[k];
    /* PHASE_2_REDESIGN step 2 (kept): a solid flag-color block needs a text color verified
       against ITS OWN background, so the year numeral is never tinted to the champion's own
       arbitrary club color -- unrelated to this pass, left exactly as that phase set it. */
    const sc=SCORING.find(s=>s[0]===y);
    host.innerHTML=`<div class="yr mono">${y}</div>
      <div class="champ-line">${esc(f.name)}${noteBadge}</div>
      <div class="vs-line">${r?'venció a '+esc(F[r].name)+' en la final':'subcampeón no registrado'} · título ${f.won.indexOf(y)+1} de ${f.won.length} para el club</div>
      <div class="btnrow" style="margin-top:var(--sp-3)"><button class="btn" onclick="showTeam('${k}')" style="padding:5px 11px;font-size:var(--fs-2xs)">Ver ${esc(f.name.split(' de ')[0])}</button></div>
      ${sc?`<div class="xlink">Campeón de anotación esa temporada: <a href="#" onclick="showView('historia','premios');return false">${esc(sc[1])} (${esc(sc[2])}) →</a></div>`
        :`<div class="xlink" style="color:var(--ink-3)">Sin campeón de anotación registrado para ${y} — el archivo de premios cubre ${SCORING[0][0]}–${SCORING[SCORING.length-1][0]}.</div>`}`;
  }
}

/* Per-season detail from web/data/seasons/<y>.json — scoring champion,
   awards, standings, leaders — appended below the champion readout when
   the file is reachable (deployed). A local-file open shows nothing
   extra. Guarded against a fast second click by the dataset stamp. */
const SEASON_AW={mvp:'Más Valioso',defensive_player:'Defensa del Año',rookie:'Novato del Año'};
const SEASON_LC={scoring:'Anotación',rebounds:'Rebotes',assists:'Asistencias',blocks:'Bloqueos',
  steals:'Robos',threes:'Triples',free_throws:'Tiros libres',turnovers:'Pérdidas',
  off_rebounds:'Rebotes ofensivos',three_pct:'% de triples',free_throw_pct:'% de tiros libres'};
async function loadSeasonExtra(y){
  y=String(y);
  const host=$('#seasonExtra'); if(!host) return;
  host.innerHTML=''; host.dataset.y=y;
  const d=await DATA.get('seasons/'+y+'.json');
  if(!d || host.dataset.y!==y) return;
  let h='';
  const sc=d.scoring_champion;
  if(sc){
    const v=sc.metric_era==='ppg'
      ? (sc.ppg!=null?sc.ppg+' por juego':'—')
      : (sc.total_points!=null?sc.total_points.toLocaleString('es-PR')+' puntos':'—');
    h+=`<dl class="kv"><dt>Campeón de anotación</dt><dd>${esc(sc.player_raw)}<span class="muted"> · ${esc(sc.team_raw||'')} · ${esc(v)}</span></dd></dl>`;
  }
  if(d.awards && d.awards.length){
    h+='<dl class="kv">'+d.awards.map(a=>
      `<dt>${esc(SEASON_AW[a.award]||a.award)}</dt><dd>${esc(a.player_raw)}<span class="muted"> · ${esc(a.team_raw||'')}</span></dd>`).join('')+'</dl>';
  }
  if(d.standings){
    const st=d.standings;
    h+=`<div class="note" style="margin-top:var(--sp-3)">Posiciones${st.complete?'':` <span class="muted">— parcial, ${st.games_recorded} juegos en el archivo</span>`}</div>`
      +'<div class="tblwrap"><table><thead><tr><th>Equipo</th><th class="num">G</th><th class="num">P</th></tr></thead><tbody>'
      +st.rows.map(row=>`<tr><td>${esc(row.team_raw)}</td><td class="num">${row.w}</td><td class="num">${row.l}</td></tr>`).join('')
      +'</tbody></table></div>';
  }
  if(d.leaders){
    h+='<div class="note" style="margin-top:var(--sp-3)">Líderes de la temporada</div><dl class="kv">';
    for(const cat of Object.keys(d.leaders)){
      const top=d.leaders[cat][0]; if(!top) continue;
      h+=`<dt>${esc(SEASON_LC[cat]||cat)}</dt><dd>${esc(top.player_raw)}<span class="muted"> · ${top.value!=null?top.value:'—'}${top.club_raw?' · '+esc(top.club_raw):''}</span></dd>`;
    }
    h+='</dl>';
  }
  host.innerHTML = h
    ? `<div class="card" style="margin-top:var(--sp-3)">${h}<div class="note">Del archivo de bsnpr.com vía Wayback Machine.</div></div>`
    : '';
}
function buildTitleStats(){
  const withC=YEARS.filter(y=>champOf[y]).length;
  const clubs=FKEYS.filter(k=>F[k].won.length).length;
  const most=FKEYS.slice().sort((a,b)=>F[b].won.length-F[a].won.length)[0];
  const noTitle=FKEYS.filter(k=>F[k].active&&!F[k].won.length).length;
  $('#titleStats').innerHTML=`
    <div><div class="n">${NSEASONS}</div><div class="l">temporadas, 1930 a 2026</div></div>
    <div><div class="n">${withC}</div><div class="l">con campeón identificado</div></div>
    <div><div class="n">${clubs}</div><div class="l">franquicias han ganado</div></div>
    <div><div class="n">${F[most].won.length}</div><div class="l">títulos de ${esc(F[most].name.split(' de ')[0])}, el máximo</div></div>
    <div><div class="n">${noTitle}</div><div class="l">clubes activos sin título</div></div>`;
}
/* PHASE_11 (owner-approved, redesign-v2): medal rank badges (top 3) + the real crest()
   helper per franchise, on the exact same 20-franchise/title-count computation this
   function already did (FKEYS.filter(k=>F[k].won.length), sorted descending) -- only the
   markup changed, not the data. New .bar-row/.rk/.who/.pn/.track/.fill/.v classes, NOT the
   shared bars()/.barrow helper (that one is also Jugadores' own leadBars() -- left
   untouched, out of scope this pass). */
function buildTitleBars(){
  const rows=FKEYS.filter(k=>F[k].won.length).sort((a,b)=>F[b].won.length-F[a].won.length);
  const max=F[rows[0]].won.length;
  $('#titleBars').innerHTML=rows.map((k,i)=>{
    const f=F[k], rk=i<3?' rk'+(i+1):'';
    return `<div class="bar-row${rk}">
      <div class="rk">${i+1}</div>
      <div class="who">${crest(k,32,38)}
        <div class="wrap"><div class="pn">${esc(f.name)}</div>
          <div class="track"><div class="fill" style="width:${f.won.length/max*100}%"></div></div></div>
      </div>
      <div class="v mono">${f.won.length}</div>
    </div>`;
  }).join('')
    +`<p class="scrollnote">${rows.length} franquicias con al menos un título, de ${FKEYS.length} en total.</p>`;
}
/* PHASE_11 (owner-approved, redesign-v2): streak cards with real crest + a per-year
   mini-strip -- same historiaStreaks() walk buildRibbon() uses above (not a second,
   possibly-drifting computation), re-rendered into the mockup's own card visual. */
function buildDynasties(){
  const runs=historiaStreaks();
  const host=$('#dynasties'); if(!host) return;
  host.innerHTML='<div class="streaks">'+runs.slice(0,9).map((r,i)=>{
    const years=[]; for(let y=r.start;y<=r.end;y++) years.push(y);
    return `<div class="streak-card${i<3?' top':''}">
      <div class="rankbadge">${r.n}×</div>
      <div class="body">${crest(r.k,32,38)}
        <div><div class="who">${esc(F[r.k].name)}</div>
        <div class="yrs">${r.start}–${r.end} · ${r.n} títulos seguidos</div></div>
      </div>
      <div class="mini">${years.map(y=>`<i title="${y}">${String(y).slice(2)}</i>`).join('')}</div>
    </div>`;
  }).join('')+'</div>'+
    `<p class="scrollnote">${runs.length} rachas de dos o más títulos consecutivos en 97 temporadas. Bayamón 2025–26 es la primera desde Ponce en 2014–15.</p>`;
}
/* PHASE_11 (owner-approved, redesign-v2): visual polish only -- row/column computation
   (every club with a title vs. every club with a runner-up finish, item 11's own "keep
   real data/interactivity untouched," NOT reduced to the mockup's top-8 sample) is
   byte-identical to before. Only the cell markup changed: a solid weighted color
   (>=3 red, else blue, matching the mockup's own .cellv threshold) instead of a pill,
   plus the new .matrix CSS's zebra striping (main.css, no markup needed for that part). */
function buildMatrix(){
  const active=FKEYS.filter(k=>F[k].won.length||F[k].ru.length);
  const pairs={};
  YEARS.forEach(y=>{const c=champOf[y],r=ruOf[y]; if(c&&r) pairs[c+'|'+r]=(pairs[c+'|'+r]||0)+1;});
  const cols=active.filter(k=>F[k].ru.length).sort((a,b)=>F[b].ru.length-F[a].ru.length);
  const rows=active.filter(k=>F[k].won.length).sort((a,b)=>F[b].won.length-F[a].won.length);
  let h='<div class="matrix"><table><thead><tr><th class="lbl">Campeón \\ Subcampeón</th>'+
    cols.map(k=>`<th class="num" title="${esc(F[k].name)}">${esc(F[k].abbr)}</th>`).join('')+'</tr></thead><tbody>';
  rows.forEach(rk=>{
    h+=`<tr><td class="lbl">${esc(F[rk].abbr)} <span class="dim">${esc(F[rk].name.split(' de ')[0])}</span></td>`;
    cols.forEach(ck=>{
      const n=pairs[rk+'|'+ck]||0;
      h+=n?`<td class="cellv ${n>=3?'hi':'lo'}">${n}</td>`:'<td class="zero">·</td>';
    });
    h+='</tr>';
  });
  h+='</tbody></table></div>';
  $('#matrix').innerHTML=h;
}
let SEASON_Q='',SEASON_CLUB='';
function buildSeasonFilters(){
  const host=$('#seasonFilters');
  host.innerHTML=`<div class="filters">
    <div class="field" style="min-width:200px"><label for="sq">Buscar</label>
      <input type="search" id="sq" placeholder="Año, club, nota…"></div>
    <div class="field"><label for="sclub">Franquicia</label><select id="sclub">
      <option value="">Todas</option>${FKEYS.slice().sort((a,b)=>F[a].name.localeCompare(F[b].name,'es'))
        .map(k=>`<option value="${k}">${esc(F[k].name)}</option>`).join('')}</select></div>
  </div>`;
  $('#sq').oninput=e=>{SEASON_Q=e.target.value;buildSeasonTable();};
  $('#sclub').onchange=e=>{SEASON_CLUB=e.target.value;buildSeasonTable();};
}
function buildSeasonTable(){
  const q=norm(SEASON_Q);
  const rows=YEARS.filter(y=>{
    const c=champOf[y],r=ruOf[y];
    if(SEASON_CLUB && c!==SEASON_CLUB && r!==SEASON_CLUB) return false;
    if(!q) return true;
    const hay=norm([y,c?F[c].name:'',r?F[r].name:'',NOTES[y]||''].join(' '));
    return hay.includes(q);
  }).map(y=>{
    const c=champOf[y],r=ruOf[y];
    return [y,c?F[c].name:null,r?F[r].name:null,NOTES[y]||''];
  }).reverse();
  buildTable($('#seasonTable'),[
    {label:'Año',num:true},
    {label:'Campeón',wide:true,render:(v,r)=>{
      if(!v) return '<span class="dim">sin registrar</span>';
      const k=champOf[r[0]];
      return `<button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showTeam('${k}')">${esc(v)}</button>`;
    }},
    {label:'Subcampeón',wide:true},
    {label:'Nota',wide:true}
  ],rows,{file:'temporadas_bsn',sort:0,dir:-1});
}

/* ============================================================
   EQUIPOS
   ============================================================ */
function tile(k){
  const f=F[k];
  return `<button class="teamtile" onclick="showTeam('${k}')" aria-pressed="false">
    ${crest(k,40,48)}<span class="tn">${esc(f.name.split(' de ')[0])}</span>
    <span class="tt">${f.won.length?f.won.length+'×':'—'}</span></button>`;
}
/* PHASE_42 (owner-approved, redesign-v2): Desaparecidas-only, a separate function from
   tile() rather than an optional flag on it -- tile() stays byte-for-byte what Activos
   already renders (task's own "do not change... the Activos tiles"), no shared branch
   that could regress it later. Fixes a real disambiguation gap: tile()'s own name line
   is f.name.split(' de ')[0], the mascot word only ("Gallitos de la UPR" and "Gallitos
   de Isabela" both render as just "Gallitos") -- the one real collision among the 21
   defunct clubs, confirmed by scanning every short name before writing this. City +
   active years, both straight from F, nothing hardcoded per club -- so this stays
   correct if F's founded/end ever change (hydrate(), init.js, can overwrite them from
   franchises.json). founded/end are both "first season"/"last season" is a judgment
   call, not a literal F field name, but matches how showTeam()'s own phero-sub already
   phrases the exact same two fields ("fundado {founded} ... desaparecido en {end}") --
   not a new interpretation invented here. */
function tileGone(k){
  const f=F[k];
  const bits=[];
  if(f.city) bits.push(esc(f.city));
  const start=f.founded, end=f.end;
  let yrs='';
  if(start!=null&&end!=null) yrs = start===end ? String(start) : start+'–'+end;
  else if(start!=null) yrs=String(start);
  else if(end!=null) yrs=String(end);
  if(yrs) bits.push(yrs);
  const sub=bits.join(' · ');
  return `<button class="teamtile" onclick="showTeam('${k}')" aria-pressed="false">
    ${crest(k,40,48)}<span class="tn">${esc(f.name.split(' de ')[0])}</span>
    ${sub?`<span class="tts">${sub}</span>`:''}
    <span class="tt">${f.won.length?f.won.length+'×':'—'}</span></button>`;
}
function buildTiles(){
  $('#tilesActive').innerHTML=ACTIVE.slice().sort((a,b)=>F[a].name.localeCompare(F[b].name,'es')).map(tile).join('');
  $('#tilesGone').innerHTML=FKEYS.filter(k=>!F[k].active)
    .sort((a,b)=>F[a].name.localeCompare(F[b].name,'es')).map(tileGone).join('');
}
function showTeam(k){
  showView('equipos','equipo',{noScroll:true,noHash:true});
  setHash('equipos/equipo/'+k);
  const f=F[k], host=$('#teamDetail');
  const v=VENUES[k];
  const last=f.won.length?Math.max.apply(null,f.won):null;
  const finals=f.won.length+f.ru.length;
  const opp={};
  f.won.forEach(y=>{const o=ruOf[y];if(o)(opp[o]=opp[o]||[0,0])[0]++;});
  f.ru.forEach(y=>{const o=champOf[y];if(o)(opp[o]=opp[o]||[0,0])[1]++;});
  /* rivalKeys stays the single source for both the top-rival callout below
     and the full "careo" table, so the two can never disagree. */
  const rivalKeys=Object.keys(opp).sort((a,b)=>(opp[b][0]+opp[b][1])-(opp[a][0]+opp[a][1]));
  const oppRows=rivalKeys.map(o=>[F[o].name,opp[o][0],opp[o][1],opp[o][0]+opp[o][1]]);
  const topRival=rivalKeys[0];
  const st=[].concat(STAND2026.A,STAND2026.B).find(r=>r[0]===k);
  const retired=RETIRED.find(r=>r[0]===f.name);
  const roster=POOL.filter(p=>p.c.includes(k));

  const mostEver = f.won.length>0 && FKEYS.every(x=>F[x].won.length<=f.won.length);
  const drought = last ? LAST-last : null;
  const heroNote = f.won.length
    ? (mostEver ? 'El club más ganador de la liga · '+f.won.length+'-'+f.ru.length+' en finales'
       : 'Último título en '+last+(drought>0?', hace '+drought+(drought===1?' año':' años'):'')+' · '+f.won.length+'-'+f.ru.length+' en finales')
    : (f.ru.length ? f.ru.length+(f.ru.length===1?' final perdida':' finales perdidas')+', aún sin título' : 'Sin finales en el archivo');
  /* Coliseo line — name, nickname, ~capacity (tooltip explains the "~"),
     opened year, all nullable; VENUE_NOTES adds a one-off status caveat
     (e.g. a temporary home while the arena is renovated). */
  let venueLine='';
  if(v){
    const [vn,vcap,vnick,vopened]=v;
    venueLine=`${esc(vn)}${vnick?' — «'+esc(vnick)+'»':''} · <span title="Capacidad aproximada — varía por fuente y renovación">~${vcap.toLocaleString('es-PR')}</span>${vopened?' · desde '+vopened:''}`;
  }
  const venueNote=VENUE_NOTES[k];
  /* Top rival — reuses rivalKeys/opp computed above, never a second,
     possibly-divergent count. */
  const rivalLine = topRival
    ? `Mayor rival: ${crest(topRival,16,19)} ${esc(F[topRival].name)} — ${opp[topRival][0]+opp[topRival][1]} finales (${opp[topRival][0]}-${opp[topRival][1]})`
    : '';
  /* One line of team lore — TEAM_LORE if sourced, else a true, always-
     available line derived live from the same F data the rest of the
     card uses (never fabricated, never empty). */
  const lore = TEAM_LORE[k] || (finals
    ? (f.won.length
        ? f.won.length+(f.won.length===1?' título':' títulos')+' en '+finals+' finales — el más reciente en '+last+'.'
        : 'Sin título todavía, con '+f.ru.length+(f.ru.length===1?' final jugada':' finales jugadas')+' en el archivo.')
    : 'Sin finales registradas en el archivo.');
  host.innerHTML=`<div class="card" style="margin-top:22px;border-color:${f.c1}">
    <div class="tri phero-tri"></div>
    <div class="phero">
      ${crest(k,58,70)}
      <div class="phero-body">
        <h2>${esc(f.name)}</h2>
        <div class="phero-sub">${esc(f.city)} · fundado ${f.founded}${f.active?'':' · desaparecido'+(f.end?' en '+f.end:'')}</div>
        <div class="phero-stat"><span class="ed-stat">${f.won.length}</span>
          <span class="phero-spark" style="color:${f.c1}">${titleComb(f,{w:150,h:24,gap:1})}</span></div>
        <div class="phero-statl">${f.won.length===1?'título':'títulos'}</div>
        <div class="phero-note">${esc(heroNote)}</div>
        ${venueLine?`<div class="phero-note">${venueLine}</div>`:''}
        ${venueNote?`<div class="phero-note">${esc(venueNote)}</div>`:''}
        <div class="chips">
          ${st?`<span class="tag blue">2026: ${st[1]}-${st[2]} (${st[3].toFixed(3).replace('0.','.')})</span>`:''}
          <span class="tag" title="Origen del color">${f.colorSrc==='wiki'?'Colores verificados':'Colores aproximados'}</span>
        </div>
        <dl class="kv">
          ${f.coach?`<dt>Dirigente</dt><dd>${esc(f.coach)}</dd>`:''}
          ${retired?`<dt>Números retirados</dt><dd>${retired[1]} — ${esc(retired[2])}</dd>`:''}
          ${f.note?`<dt>Nota</dt><dd>${esc(f.note)}</dd>`:''}
        </dl>
        ${rivalLine?`<div class="phero-note">${rivalLine}</div>`:''}
        <div class="phero-note">${esc(lore)}</div>
        ${TOWN_LORE[k]?`<div class="phero-note">${esc(TOWN_LORE[k])}</div>`:''}
        ${f.won.length?`<div class="note">Campeón: ${f.won.join(' · ')}</div>`:''}
        ${f.ru.length?`<div class="note">Subcampeón: ${f.ru.join(' · ')}</div>`:''}
      </div>
    </div>
    ${roster.length?`<h4 class="sub">En el archivo con este club</h4><div class="chips">${
      roster.map(p=>`<button class="chip" onclick="showPlayer('${esc(p.n).replace(/'/g,"\\'")}')">${esc(p.n)}</button>`).join('')}</div>`:''}
    <div id="teamOpp"></div>
    <div id="teamStartingFive"></div>
  </div>`;
  if(oppRows.length){
    const t=el('div'); t.innerHTML='<h4 class="sub">El careo en finales</h4>'; $('#teamOpp').appendChild(t);
    const tt=el('div'); $('#teamOpp').appendChild(tt);
    buildTable(tt,[{label:'Rival',wide:true},{label:'Ganadas',num:true},{label:'Perdidas',num:true},{label:'Total',num:true}],
      oppRows,{file:'finales_'+k,sort:3,dir:-1});
  }
  loadStartingFive(k,f);
  revealNode(host); host.scrollIntoView({block:'start',behavior:'smooth'});
}

/* ---------- backlog item 3 — cinco inicial (starting five), per team per
   season. No "starter" flag exists in any source; web/data/starting_five/
   <k>.json is built from the 5 players with the most minutes played per
   game (build_starting_fives() in src/build_web_data.py), aggregated to
   the 5 who appear in that group most often across the season — an
   inference, always labeled as one, never presented as an official
   record. Owner-approved floor: >=15 games in the archive AND >=60% of
   those inferred slots resolved to a real archive identity + position;
   a team-season that doesn't clear it is simply absent from its file,
   never a low-confidence card. An unresolved slot within a card that DID
   clear the floor stays honest too — neutral circle, "sin confirmar",
   no invented position — placed in whichever court zone real positions
   left open, since the zone is a layout choice, not a factual claim. ---- */
const SF_ZONE={Armador:[150,40],Escolta:[245,100],Alero:[55,100],Delantero:[215,190],Centro:[85,190]};
const SF_ZONE_ORDER=['Armador','Escolta','Alero','Delantero','Centro'];
let SF_DATA=null,SF_KEY=null;
function sfAssignZones(players){
  const used=new Set(),withZone=[],remaining=[];
  players.forEach(p=>{
    if(p.position && SF_ZONE[p.position] && !used.has(p.position)){ used.add(p.position); withZone.push({...p,zone:p.position}); }
    else remaining.push(p);
  });
  const leftover=SF_ZONE_ORDER.filter(z=>!used.has(z));
  remaining.forEach((p,i)=>withZone.push({...p,zone:leftover[i]}));
  return withZone;
}
function sfInitials(name){
  return name.replace(/[«»]/g,'').split(/\s+/).filter(Boolean).slice(0,2).map(s=>s[0]).join('').toUpperCase();
}
/* PHASE_42 (owner-approved, redesign-v2): owner-reported collision/clipping on this
   court at 1000px -- SVG <text> has no built-in wrap/truncate, so a long name (e.g.
   "Alvarado Sierra, Omar J.", "Mojica Izquierdo, Javier") just kept drawing past its
   own backing rect, bleeding into whatever sat nearby. A hard character budget (fit to
   the real rect width now used for every zone, not the old 84/92px binary split) plus
   an ellipsis is the fix; the full name is never actually lost -- kept in a <title> on
   the group so a screen reader or a hover tooltip still gets it whenever truncation
   actually fires. Layout only: still the same 5 real players, same real zone/position
   data, same ppg -- sfAssignZones()/the data this draws from is untouched. */
function sfFit(name,maxChars){
  if(name.length<=maxChars) return {text:name,truncated:false};
  return {text:name.slice(0,maxChars-1).trimEnd()+'…',truncated:true};
}
function sfCourtSvg(f,players){
  const w=96;
  const groups=sfAssignZones(players).map(p=>{
    const [cx,cy]=SF_ZONE[p.zone];
    const gap=p.bsnpr_id==null;
    const fill=gap?'var(--ink-3)':f.c1, ink=gap?'var(--deep)':f.c2;
    const posLabel=gap?'sin confirmar':esc(p.position||p.zone);
    const posColor=gap?'var(--rojo)':'var(--ink-3)';
    const dash=gap?' stroke="var(--court-line)" stroke-width="1.5" stroke-dasharray="3,2"':'';
    const fit=sfFit(p.name,17);
    return `<g>
      ${fit.truncated?`<title>${esc(p.name)}</title>`:''}
      <circle cx="${cx}" cy="${cy}" r="16" fill="${fill}"${dash}/>
      <text x="${cx}" y="${cy+5}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="800" font-size="11" fill="${ink}">${esc(sfInitials(p.name))}</text>
      <rect x="${cx-w/2}" y="${cy+20}" width="${w}" height="32" rx="6" fill="var(--deep)" opacity=".94"/>
      <text x="${cx}" y="${cy+33}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="700" font-size="9" fill="var(--ink)">${esc(fit.text)}</text>
      <text x="${cx}" y="${cy+45}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="${gap?700:400}" font-size="7.5" fill="${posColor}">${posLabel} · <tspan fill="var(--flag-ink)" font-weight="800">${p.ppg} pts</tspan></text>
    </g>`;
  }).join('');
  return `<svg viewBox="0 0 300 260" aria-hidden="true">
    <path d="M20 15h260v215H20Z" fill="none" stroke="var(--court-line)" stroke-width="2"/>
    <path d="M85 230v-90h130v90" fill="none" stroke="var(--court-line)" stroke-width="2"/>
    <circle cx="150" cy="140" r="30" fill="none" stroke="var(--court-line)" stroke-width="2"/>
    <path d="M20 230a170 170 0 0 1 260 0" fill="none" stroke="var(--court-line)" stroke-width="2"/>
    <circle cx="150" cy="218" r="9" fill="none" stroke="var(--court-line)" stroke-width="2"/>
    <line x1="130" y1="218" x2="170" y2="218" stroke="var(--court-line)" stroke-width="3"/>
    ${groups}
  </svg>`;
}
function renderStartingFive(k,season){
  const host=$('#teamStartingFive'); if(!host || SF_KEY!==k) return;
  const f=F[k], seasons=Object.keys(SF_DATA).sort((a,b)=>b-a), rec=SF_DATA[season];
  const gaps=rec.players.filter(p=>p.bsnpr_id==null).length;
  const pills=seasons.length>1
    ? `<div class="chips">${seasons.map(s=>`<button class="chip" aria-selected="${s===season}" onclick="renderStartingFive('${k}','${s}')">${s}</button>`).join('')}</div>`
    : '';
  host.innerHTML=`<h4 class="sub">Cinco inicial ${esc(season)} — inferido de minutos jugados</h4>
    <p class="lede">No hay un registro oficial de titulares; estos son los 5 jugadores con más minutos en cancha, agregados por temporada — una inferencia declarada, no un dato verificado. El número bajo cada nombre es su promedio real de puntos, no una calificación.</p>
    ${pills}
    <div class="sf-court">${sfCourtSvg(f,rec.players)}</div>
    <div class="note">${rec.games} juegos en el archivo esa temporada · ${5-gaps} de 5 con identidad y posición confirmada${gaps?` · ${gaps} sin confirmar`:''}.</div>`;
}
async function loadStartingFive(k,f){
  const host=$('#teamStartingFive'); if(!host) return;
  host.innerHTML=''; host.dataset.key=k; SF_DATA=null; SF_KEY=null;
  const d=await DATA.get('starting_five/'+k+'.json');
  if(!d || host.dataset.key!==k || !Object.keys(d).length) return;
  SF_DATA=d; SF_KEY=k;
  renderStartingFive(k,Object.keys(d).sort((a,b)=>b-a)[0]);
}

/* ============================================================
   JUGADORES — one index built from every table in the archive
   ============================================================ */
let PINDEX=null;
/* 5D.3b — filled by hydrate() from web/data. PXWALK: norm(curated name) ->
   bsnpr_id for the ~158 owner-reviewed matches. FID2APP: pipeline franchise_id
   -> app 3-letter key, for linking career-row teams. Both null on file:// (no
   fetch) — showPlayer then renders exactly the baked-in card. */
let PXWALK=null, FID2APP=null;
/* 5D.3c — PALL: the 3.303 light rows from index/players.json (whole archive,
   not just the 385 curated). XWALK_REV: bsnpr_id -> curated name, so an
   archive-list click on someone who is a curated player lands on the rich
   card. PMODE: 'top' (Destacados) | 'all' (Todo el archivo). All null/'top'
   on file:// — the toggle stays inert. */
let PALL=null, XWALK_REV=null, PMODE='top';
/* One URL per archive player. PSLUG: url slug -> PALL row; USLUG: id -> its url slug;
   PTWINS: id -> the other players that share its name; PBYID: id -> PALL row. Built by
   buildPlayerSlugs() when PALL lands; null (and the old slug(name) URLs) on file://.
   PREDIR: index/player_redirects.json, where a merged (retired) player id and its old URL go:
   {ids:{retired:survivor}, slugs:{old slug:survivor}}. */
let PSLUG=null, USLUG=null, PTWINS=null, PBYID=null, PREDIR=null;
/* 5D.2b — MVP_ID: year -> bsnpr_id (archive-card click-through for gap-year
   MVPs not in PINDEX). MVP_ALSO: year -> the name the archive records where it
   disagrees with the baked row (footnote, app value stays canonical). */
let MVP_ID=null, MVP_ALSO=null;
/* 5D.4 — set by hydrate() when web/data is present. DATA_TEXT flips the
   "lo que falta" / coverage / MVP-warning copy from the file:// baseline
   (champions-only) to the deployed reality; MANIFEST.counts feeds the numbers. */
let MANIFEST=null, DATA_TEXT=false;
/* PHASE_2_REDESIGN step 4 (owner-approved, redesign-v2): Resumen/Temporadas tabs for the
   player page. Pure show/hide -- #playerDetail and #playerExtra are never re-rendered or
   destroyed on a tab switch, only [hidden] toggles here, so anything already inside them
   (season-compare checkboxes, the /season deep-link card) survives a switch away and back
   untouched (verified live, not assumed -- see the redesign-v2 PHASE 4 report). Both tabs
   are always in the DOM (index.html, never built/rebuilt in JS) -- a player who lacks
   Temporadas-side data still gets that tab, showing loadPlayerExtra()'s own real degraded
   state ("sin ficha vinculada", empty season table, ...), not a hidden/missing tab.
   Manual-activation ARIA tablist (WAI-ARIA APG): arrow keys move focus between tabs
   without activating; Enter/Space activates the focused one. */
/* PHASE_19 (owner-approved, redesign-v2): a real 3-entry map (Resumen/
   Temporadas/Fuentes) instead of the old hardcoded resumen<->temporadas
   pair -- same manual-activation ARIA tablist behavior (aria-selected/
   tabIndex/hidden), just data-driven so a 3rd tab doesn't need a 2nd code
   path. */
const PLAYER_TAB_MAP={resumen:['ptab-resumen','playerDetail'],temporadas:['ptab-temporadas','playerExtra'],fuentes:['ptab-fuentes','playerFuentes']};
function showPlayerTab(which){
  if(!PLAYER_TAB_MAP[which]) return;
  Object.keys(PLAYER_TAB_MAP).forEach(k=>{
    const [tabId,panelId]=PLAYER_TAB_MAP[k];
    const tab=document.getElementById(tabId), panel=document.getElementById(panelId);
    if(!tab||!panel) return;
    const on=k===which;
    tab.setAttribute('aria-selected',String(on)); tab.tabIndex=on?0:-1;
    panel.hidden=!on;
  });
}
function playerTabKeydown(e){
  const order=['ptab-resumen','ptab-temporadas','ptab-fuentes'];
  const i=order.indexOf(e.target.id); if(i<0) return;
  if(e.key==='ArrowRight'||e.key==='ArrowLeft'){
    e.preventDefault();
    const next=order[(i+(e.key==='ArrowRight'?1:-1)+order.length)%order.length];
    order.forEach(t=>{ document.getElementById(t).tabIndex=-1; });
    const nt=document.getElementById(next); nt.tabIndex=0; nt.focus();
  }else if(e.key==='Enter'||e.key===' '){
    e.preventDefault();
    showPlayerTab({'ptab-resumen':'resumen','ptab-temporadas':'temporadas','ptab-fuentes':'fuentes'}[e.target.id]);
  }
}
/* PHASE_19 (owner-approved, redesign-v2): page-level head (back link stays
   static HTML, index.html) -- avatar/eyebrow/name/subline, shown above all
   3 tabs, real team color via --pc (same inline-custom-property pattern
   .cmpfill's own --w already uses in this file) inherited down into
   portrait()'s own .crest border (main.css). c1 null (archive-only, no
   club context) falls back to the real --line token, not a guess. */
function buildPlayerHead(opts){
  const host=$('#playerHead'); if(!host) return;
  host.innerHTML=`<div class="phero-head" style="--pc:${opts.c1||'var(--line)'}">
    ${opts.portraitHtml||''}
    <div class="phero-head-body">
      ${opts.eyebrow?`<div class="ed-eye">${esc(opts.eyebrow)}</div>`:''}
      <h1>${esc(opts.name)}</h1>
      ${opts.meta?`<div class="phero-sub">${esc(opts.meta)}</div>`:''}
    </div>
    ${opts.actionHtml?`<div class="phero-head-action">${opts.actionHtml}</div>`:''}
  </div>`;
}
/* Información del jugador -- one real rebuild per call (sync-only rows at
   first paint, sync+async together once loadPlayerExtra's own fetch
   lands), never an append -- avoids any dedup bookkeeping between the two
   passes. rows is [label,value][]; a null/empty value drops that row
   rather than printing a dash -- an identity field the archive doesn't
   have is omitted, not padded with a placeholder (PC4 by omission, same
   discipline loadPlayerExtra's own old "top" line already used). */
function renderPlayerInfo(rows){
  const host=$('#playerInfo'); if(!host) return;
  const body=(rows||[]).filter(r=>r[1]).map(([k,v])=>`<div class="row"><span class="k">${esc(k)}</span><span class="v">${esc(v)}</span></div>`).join('');
  host.innerHTML=`<h3>Información del jugador</h3>${body||'<p class="note" style="margin-top:0">Sin más datos de identidad en el archivo.</p>'}`;
  /* PHASE_20 item d: a long value ("21 de septiembre de 1957") in the
     narrow info column wraps mid-phrase next to its label instead of
     cleanly under it -- measured live (multi-line .v gets >1 client
     rect), not guessed from a fixed character count, since what counts
     as "too long" depends on the label's own width too. .row-stack (CSS)
     switches that one row to a stacked label/value layout; every other
     row is untouched. */
  host.querySelectorAll('.row').forEach(row=>{
    const v=row.querySelector('.v'); if(!v) return;
    row.classList.toggle('row-stack', v.getClientRects().length>1);
  });
}
/* PHASE_20 item b + PHASE_21 item 3: chips shaped exactly "<label> <year>"
   (SCORING's "Campeón de anotación 1977", MVP_YEARS' "MVP 1984", ...)
   collapse into one real chip per label; PHASE_21 extends this to also
   fold in that label's own "<N>× <label>" counted chip (MVP_REPEAT's
   "3× MVP", HOF/POOL-derived "7× campeón de anotación") when one exists,
   and to drop the bare generic chip ("MVP", "Campeón de anotación") when
   a counted chip already covers that same label -- real facts, fewer
   chips, nothing lost (every year is still printed; the generic chip only
   ever repeated what the counted+year chip already states). Label
   matching is case-insensitive (the real tag text differs in case between
   "Campeón de anotación 1977" and "7× campeón de anotación").
   A label with only one matching year AND no counted chip is left exactly
   as it was -- there is nothing to compress. Consecutive years collapse to
   a range (1984-1987 -> "1984–1987"); non-consecutive years stay listed
   (1977, 1978, 1979 -> "1977 · 1978 · 1979"). Order-preserving where it
   can be: a merged chip appears at its COUNTED tag's own position when one
   exists (that is the real anchor fact), else at its first year-tag's
   position -- not shoved to the end. Display only -- the real p.tags Set
   this reads from is never mutated, so the index's own #pf filter (which
   matches on the real, ungrouped tag text) keeps working unchanged. */
function groupHonorChips(tags){
  const yearRe=/^(.+) (\d{4})$/, countRe=/^(\d+)× (.+)$/, lc=s=>s.toLowerCase();
  const yearsByLabel=new Map();   /* lowercase label -> [years] */
  tags.forEach(t=>{ const m=t.match(yearRe); if(m){
    const k=lc(m[1]); if(!yearsByLabel.has(k)) yearsByLabel.set(k,[]); yearsByLabel.get(k).push(+m[2]);
  }});
  const countedLabel=new Map();   /* lowercase label -> real "<N>× label" tag text */
  tags.forEach(t=>{ const m=t.match(countRe); if(m) countedLabel.set(lc(m[2]),t); });
  const rangeFmt=years=>{
    years=Array.from(new Set(years)).sort((a,b)=>a-b);
    const parts=[]; let i=0;
    while(i<years.length){ let j=i; while(j+1<years.length&&years[j+1]===years[j]+1) j++;
      parts.push(j>i?years[i]+'–'+years[j]:''+years[i]); i=j+1; }
    return parts.join(' · ');
  };
  const emitted=new Set(), out=[];
  tags.forEach(t=>{
    const cm=t.match(countRe);
    if(cm){
      const key=lc(cm[2]);
      if(emitted.has(key)) return;
      emitted.add(key);
      const yrs=yearsByLabel.get(key);
      out.push(t+(yrs&&yrs.length?' · '+rangeFmt(yrs):''));
      return;
    }
    const ym=t.match(yearRe);
    if(ym){
      const key=lc(ym[1]);
      if(emitted.has(key)) return;                 /* its counted chip already emitted this (with years) */
      const yrs=yearsByLabel.get(key)||[];
      if(yrs.length<2 && !countedLabel.has(key)){ out.push(t); return; }   /* a true singleton -- untouched */
      if(countedLabel.has(key)) return;             /* the counted branch will emit (or already did) this label */
      emitted.add(key);
      out.push(ym[1]+' · '+rangeFmt(yrs));
      return;
    }
    /* PHASE_22 item 2: a bare generic ("MVP", "Campeón de anotación") is now
       hidden whenever EITHER a counted chip OR any real year chip for the
       same label is shown -- a year chip, even a lone one left untouched
       above, already states strictly more than the bare generic ever did,
       so the generic adds nothing. Real case this closes: Raymond Dalmau
       has "Campeón de anotación 1968"/"1970" (no counted chip for that
       label) and a separate bare "Campeón de anotación" -- the bare one
       is now dropped since the year chip already covers it. */
    const key=lc(t);
    if(countedLabel.has(key) || yearsByLabel.has(key)) return;
    out.push(t);
  });
  return out;
}
/* Archive-only Ficha paragraph -- templated from the exact real aggregates
   loadPlayerExtra already computes for the season table's own totals line
   (nConf/nDisp/lo/hi/car.length), never hand-written per player. Three
   real cases, not one case force-fit to every player: a DOB conflict (the
   mockup's own Llovet example), a figures-only conflict, or no conflict at
   all -- most archive-only players are the third case and get an honest
   plain summary, not a dispute narrative that doesn't apply to them. */
function archiveFichaParagraph(car,nConf,nDisp,lo,hi,b,dobDisputed){
  if(!car.length) return 'Sin estadísticas por temporada en el archivo.';
  const span=lo?` entre ${lo} y ${hi}`:'';
  if(nDisp){
    return `La ficha de bsnpr.com para este jugador muestra tanto la fecha de nacimiento`
      +(b&&b.date?` del ${esc(fmtArchiveDob(b.date))}`:'')
      +` como ${nDisp} temporada${nDisp===1?'':'s'}${span} — ambos datos vienen de la misma página, `
      +`y no sabemos cuál de los dos es el correcto. El archivo conserva las filas pero las excluye de los totales.`;
  }
  if(nConf){
    return `${nConf} temporada${nConf===1?'':'s'} de este jugador ${nConf===1?'tiene':'tienen'} cifras distintas entre dos páginas de bsnpr.com. `
      +`El archivo conserva ambas filas pero las excluye de los totales — no escoge una.`;
  }
  return `El archivo documenta ${car.length} temporada${car.length===1?'':'s'}${span}, sin conflictos de fuente conocidos.`;
}
function showPlayer(name,id,season){
  [id,name]=survivorOf(id,name);
  buildPlayerIndex();   /* before the hash: playerSlug() needs the curated pool */
  /* PHASE_19 (owner-approved, redesign-v2): a real "jugador" view (VIEW_MAP.jugadores's
     own detail:['jugador','#playerPage']), not a sub-state of Buscar -- same real
     routing/history this app's other detail views (showTeam's #teamDetail) already use. */
  showView('jugadores','jugador',{noScroll:true,noHash:true});
  setHash('jugadores/jugador/'+playerSlug(name,id)+(season!=null?'/'+season:''));
  const pt=$('#playerTabs'); if(pt) pt.hidden=false;
  showPlayerTab(season!=null?'temporadas':'resumen');   /* a /season deep link opens on Temporadas, not Resumen */
  loadPlayerExtra(name,id,season);   /* 5D.3b/c — async, fills #playerExtra + the Información/Fuentes panels; season_detail_spec.md §4 */
  /* PHASE_36: nickKey() fallback -- a caller that still has the old
     plain-name string (a roster chip built from a data.js array that was
     never updated to the nickname form, e.g.) needs to land on the same
     merged card norm() alone would now miss. */
  const p=PINDEX.find(x=>norm(x.name)===norm(name)) || PINDEX.find(x=>nickKey(x.name)===nickKey(name));
  const host=$('#playerDetail');
  const fh=$('#playerFuentes');
  if(!p){
    if(id!=null){ renderArchiveCard(name,id,host); return; }  /* 5D.3c — archive-only player */
    buildPlayerHead({name,eyebrow:'',meta:'',portraitHtml:'',c1:null});
    host.innerHTML='<p class="note">No aparece en el índice.</p>';
    if(fh) fh.innerHTML='';
    revealNode(host); return;
  }
  const c1=p.clubs.size?F[Array.from(p.clubs)[0]].c1:'var(--azul)';
  const c2=p.clubs.size?F[Array.from(p.clubs)[0]].c2:'var(--blanco)';
  const missing=[];
  if(p.pts==null)missing.push('puntos de carrera');
  if(p.reb==null)missing.push('rebotes');
  if(p.ast==null)missing.push('asistencias');
  if(p.gp==null)missing.push('juegos');
  if(!p.years)missing.push('años activos');
  const dagger = norm(p.name)==='raymond dalmau';
  /* PHASE_20 item c: bigN/bigL (the headline number above the strip) always
     restates one of the strip's own 6 real values -- every curated player hit
     this, not just an edge case, since bigN/bigL IS one of pts/ppg/mvp/gp by
     construction. bigKey names which one, so that exact tile is left out of
     the strip below instead of printing the same real number twice. If none
     of the 4 ever resolves (bigKey stays null -- no headline stat at all),
     every tile stays; there is nothing to de-duplicate. */
  let bigN=null,bigL='',bigKey=null;
  if(p.pts!=null){ bigN=num(p.pts); bigL='puntos de carrera'; bigKey='pts'; }
  else if(p.ppg!=null){ bigN=p.ppg; bigL='puntos por juego'; bigKey='ppg'; }
  else if(p.mvp){ bigN=p.mvp; bigL=p.mvp===1?'premio MVP':'premios MVP'; bigKey='mvp'; }
  else if(p.gp!=null){ bigN=num(p.gp); bigL='juegos en el archivo'; bigKey='gp'; }
  const stripAll=[
    {k:'pts',n:num(p.pts),l:'puntos'},
    {k:'reb',n:num(p.reb),l:'rebotes'},
    {k:'ast',n:num(p.ast)+(dagger?'<span style="color:var(--fuego)">†</span>':''),l:'asistencias'},
    {k:'gp',n:num(p.gp),l:'juegos'},
    {k:'ppg',n:p.ppg==null?'—':p.ppg,l:'puntos por juego'},
    {k:'mvp',n:p.mvp||'—',l:'MVP'}
  ].filter(s=>s.k!==bigKey);
  const honorsEmpty = !p.tags.size && !p.clubs.size && !p.bio;
  const honorChips = groupHonorChips(Array.from(p.tags));

  buildPlayerHead({
    eyebrow:'Jugador destacado — ficha curada del archivo',
    name:p.name, c1,
    meta:[p.pos,p.years].filter(Boolean).join(' · ')||'posición y años sin registrar',
    portraitHtml:portrait(p.name,c1,c2,72,88,p.pos),
    /* PHASE_21 item 2: relocated here from the Ficha panel -- a real action,
       level with the name, not a 4th field buried at the bottom of a
       narrower column. */
    actionHtml:`<button class="btn" onclick="cmpFromPlayer(${JSON.stringify(p.name).replace(/"/g,'&quot;')})">Comparar con otro jugador</button>`
  });

  /* Three real panels (Información/Resumen/Ficha), matching the mockup's own
     3-box split -- #playerInfo is built empty here, filled by renderPlayerInfo()
     right after (sync rows only; loadPlayerExtra rebuilds it with the async
     Nacimiento/Lugar/Nacionalidad rows once the archive fetch lands, if linked). */
  host.innerHTML=`<div class="presumen">
    <div class="rp-panel rp-info" id="playerInfo"></div>
    <div class="rp-panel rp-stats">
      <div class="ed-eye">Resumen</div>
      ${bigN!=null?`<div class="phero-stat" style="margin-bottom:var(--sp-2_5)"><span class="ed-stat">${bigN}</span>
        <span class="phero-spark" id="playerSpark" style="color:${c1}"></span></div>
        <div class="phero-statl" style="margin-bottom:var(--sp-3)">${esc(bigL)}</div>`:''}
      <div class="strip">${stripAll.map(s=>`<div><div class="n">${s.n}</div><div class="l">${esc(s.l)}</div></div>`).join('')}</div>
    </div>
    <div class="rp-panel rp-context">
      <div class="ed-eye">Ficha</div>
      ${p.clubs.size?`<div class="chips">${Array.from(p.clubs).map(c=>`<button class="chip" onclick="showTeam('${c}')">${esc(F[c].name)}</button>`).join('')}</div>`:''}
      ${p.bio?`<p class="phero-note" style="margin:${p.clubs.size?'var(--sp-3)':'0'} 0 0">${esc(p.bio)}</p>`:''}
      ${honorsEmpty?'<p class="note" style="margin-top:0">Sin honores, clubes o biografía registrados.</p>':''}
      ${dagger?'<div class="warn" style="margin-top:var(--sp-3)">† 2.302 asistencias en 537 juegos da 4,3 por juego, no 5,1 como publica la fuente. La contradicción está en el dato original y no se ha resuelto; por eso su promedio de asistencias no se usa en los juegos.</div>':''}
      ${missing.length?`<div class="warn" style="margin-top:var(--sp-3)">Lo que este archivo <b>no</b> sabe de ${esc(p.name.split(' ')[0])}: ${esc(missing.join(', '))}. Antes de 2011 no existe ninguna base pública de estadísticas por temporada del BSN.</div>`:''}
      <div id="playerFichaAsync"></div>
    </div>
  </div>
  ${p.tags.size?`<div class="rp-panel rp-panel-honors">
    <div class="ed-eye">Honores</div>
    <div class="chips">${honorChips.map(t=>`<span class="tag ${/MVP|Leyenda|10\.000/.test(t)?'gold':''}">${esc(t)}</span>`).join('')}</div>
    ${p.legendWhy?`<div class="note legend-note"><b>Leyenda</b> por: ${esc(p.legendWhy.join(" · "))}. El criterio está en «El archivo».</div>`:''}
  </div>`:''}
  <div id="playerResumenSeasons"></div>`;
  renderPlayerInfo([['Nombre',p.name],['Posición',p.pos],['Años activos',p.years]]);

  /* Fuentes tab: the real "Aparece en" source list (sync, PINDEX's own p.src) --
     the Wayback attribution line + "Mismo nombre" cross-links are async, filled
     by loadPlayerExtra once id/d resolve (#playerFuentesAsync). */
  if(fh) fh.innerHTML=`<div class="rp-panel rp-fuentes">
    <div class="ed-eye">Fuentes</div>
    <div class="fsrc"><div class="note" style="margin-top:0">Aparece en: ${esc(Array.from(p.src).join(' · '))}</div></div>
    <div class="fsrc" id="playerFuentesAsync"></div>
  </div>`;

  revealNode(host); host.scrollIntoView({block:'start',behavior:'smooth'});
}
/* 5D.3b — per-season career table from web/data/players/<id>.json, below the
   curated card. Never rewrites the card above: the archive's season totals are
   a different source (reg-season, post-2011) and are shown labelled as such,
   not merged into the curated stat strip. file:// -> PXWALK null -> no-op. */
/* season_detail_spec.md — season-vs-season inline compare (checkboxes on
   the table below) + the per-season route. SEASON_CMP_* is per-load state,
   reset at the top of loadPlayerExtra so switching players clears it. */
let SEASON_CMP_CAREER=null, SEASON_CMP_SEL=new Set(), SEASON_CMP_NAME='';

/* Reshapes one career[] row into the flat-property shape cmpBarRow()
   already expects from a player object (§2) — reused as-is for season-vs-
   season, not player-vs-player. PPG/RPG/APG/MIN fall back to a derived
   per-game value (total ÷ games) when the source doesn't publish the rate
   directly, same as the rest of this app labels a calculated figure. */
function seasonCmpObj(c){
  const s=c.stats||null, g=c.games;
  const per=(tot)=> (tot!=null && g) ? +(tot/g).toFixed(1) : null;
  const ak=c.franchise_id && typeof FID2APP!=='undefined' && FID2APP && FID2APP[c.franchise_id];
  return {
    name:String(c.season||'—'), clubs: ak?new Set([ak]):new Set(),
    pts:c.points, gp:g,
    ppg: s&&s.ppg!=null ? s.ppg : per(c.points),
    rpg: s&&s.reb ? per(s.reb.t) : null,
    apg: s ? per(s.ast) : null,
    min: s ? per(s.minutes) : null,
    reb: s&&s.reb ? s.reb.t : null, ast: s?s.ast:null,
    stl: s?s.stl:null, blk: s?s.blk:null, tov: s?s.tov:null,
    fg: s&&s.fg ? s.fg.pct : null,
    tp: s&&s.tp&&s.tp.a ? +(s.tp.m/s.tp.a).toFixed(3) : null,
    ft: s&&s.ft&&s.ft.a ? +(s.ft.m/s.ft.a).toFixed(3) : null,
  };
}
const SEASON_CMP_RATE=[
  {k:'Puntos por juego',s:'ppg'},{k:'Rebotes por juego',s:'rpg'},{k:'Asistencias por juego',s:'apg'}
];
const SEASON_CMP_SHOT=[
  {k:'Tiros de campo',s:'fg',cap:0.70},{k:'Triples',s:'tp',cap:0.50},{k:'Tiros libres',s:'ft',cap:1.00}
];
const SEASON_CMP_TOTAL=[
  {k:'Puntos',s:'pts'},{k:'Rebotes',s:'reb'},{k:'Asistencias',s:'ast'},
  {k:'Robos',s:'stl'},{k:'Tapones',s:'blk'},{k:'Pérdidas',s:'tov'},{k:'Juegos',s:'gp'}
];
function toggleSeasonCmp(cb,idx){
  if(cb.checked){
    if(SEASON_CMP_SEL.size>=3){ cb.checked=false; return; }
    SEASON_CMP_SEL.add(idx);
  } else SEASON_CMP_SEL.delete(idx);
  renderSeasonCmp();
}
function renderSeasonCmp(){
  const host=$('#seasonCmpPanel'); if(!host) return;
  const rows=Array.from(SEASON_CMP_SEL).sort((a,b)=>a-b)
    .map(i=>SEASON_CMP_CAREER&&SEASON_CMP_CAREER[i]).filter(Boolean);
  if(rows.length<2){ host.innerHTML=''; return; }
  const ps=rows.map(seasonCmpObj);
  host.innerHTML=`<div class="card cmpcard" style="margin-top:10px">
    <div class="cmpheads">${ps.map((p,i)=>`<div class="cmphead" style="--cmp-c:${cmpColor(p,i)}">
      <span class="cmpdot" style="background:${cmpColor(p,i)}"></span>
      <span class="cmpname">${esc(SEASON_CMP_NAME)} · ${esc(p.name)}</span></div>`).join('')}</div>
    <div class="cmprows">
      <div class="cmpgrouplab">Por juego</div>
      ${SEASON_CMP_RATE.map(r=>cmpBarRow(r,ps,false)).join('')}
      <div class="cmpgrouplab">Tiro</div>
      ${SEASON_CMP_SHOT.map(r=>cmpBarRow(r,ps,false)).join('')}
      <div class="cmpgrouplab">De la temporada</div>
      ${SEASON_CMP_TOTAL.map(r=>cmpBarRow(r,ps,true)).join('')}
    </div>
    <div class="dim" style="font-size:11px;margin-top:8px">PPG/RPG/APG/MIN se calculan (total ÷ juegos) cuando la fuente no publica el promedio directamente. Un guion es un hueco del archivo, no un cero.</div>
  </div>`;
}

/* One diff, shared by the inline compare panel above and the per-season
   "vs temporada anterior" line below (§3 — not two implementations). */
function seasonDiff(curr,prev){
  if(!curr||!prev) return null;
  const a=seasonCmpObj(curr), b=seasonCmpObj(prev);
  const d=(x,y)=> (x!=null&&y!=null) ? +(x-y).toFixed(1) : null;
  return {ppg:d(a.ppg,b.ppg), rpg:d(a.rpg,b.rpg), apg:d(a.apg,b.apg), from:prev.season};
}
function fmtSeasonDelta(diff){
  if(!diff) return '';
  const f=(v,u)=>v==null?null:(v>=0?'+':'')+v+' '+u;
  const parts=[f(diff.ppg,'PTS'),f(diff.rpg,'REB'),f(diff.apg,'AST')].filter(Boolean);
  return parts.length ? `vs ${diff.from}: ${parts.join(', ')}` : '';
}

/* Per-season profile (#jugadores/jugador/<slug>/<season>, §3/§4). `car` is
   already sorted ascending by loadPlayerExtra. Renders nothing for an
   unknown/mistyped season — never an error state for a bad deep link. */
function renderSeasonDetail(car,season,name,id){
  const host=$('#seasonDetail'); if(!host) return;
  if(season==null){ host.innerHTML=''; return; }
  const matches=car.filter(c=>c.season===season);
  const row=matches.find(c=>c.stats)||matches[0];   /* prefer the stats-bearing sibling (§1) */
  if(!row){ host.innerHTML=''; return; }
  const idx=car.indexOf(row);
  const diff=idx>0?seasonDiff(row,car[idx-1]):null;
  const deltaLine=fmtSeasonDelta(diff);
  const ak=row.franchise_id && FID2APP && FID2APP[row.franchise_id];
  const team=(ak&&F[ak])?F[ak].name:(row.team_raw||'—');
  const s=row.stats, p=seasonCmpObj(row);
  host.innerHTML=`<div class="card pcard" style="margin-top:var(--sp-3)" id="seasonDetailCard">
    <div class="phero-sub" style="margin-bottom:6px">${esc(name)} · ${row.season} · ${esc(team)}</div>
    ${s?`<div class="strip">
      <div><div class="n">${p.ppg??'—'}</div><div class="l">puntos por juego</div></div>
      <div><div class="n">${p.rpg??'—'}</div><div class="l">rebotes por juego</div></div>
      <div><div class="n">${p.apg??'—'}</div><div class="l">asistencias por juego</div></div>
      <div><div class="n">${p.fg!=null?pct(p.fg):'—'}</div><div class="l">tiro de campo</div></div>
      <div><div class="n">${row.games??'—'}</div><div class="l">juegos</div></div>
      <div><div class="n">${s.minutes??'—'}</div><div class="l">minutos</div></div>
    </div>
    <div class="muted" style="font-size:12.5px;margin-top:8px">3PT ${p.tp!=null?pct(p.tp):'—'}${s.tp?` (${s.tp.m}-${s.tp.a})`:''} · TL ${p.ft!=null?pct(p.ft):'—'}${s.ft?` (${s.ft.m}-${s.ft.a})`:''}</div>`
    : `<div class="strip">
      <div><div class="n">${row.games??'—'}</div><div class="l">juegos</div></div>
      <div><div class="n">${row.points!=null?row.points.toLocaleString('es-PR'):'—'}</div><div class="l">puntos</div></div>
    </div>
    <div class="note">Sin más detalle por temporada en el archivo.</div>`}
    ${deltaLine?`<div class="phero-note" style="margin-top:8px">${esc(deltaLine)}</div>`:''}
    <div id="seasonLeaderNote"></div>
  </div>`;
  document.getElementById('seasonDetailCard').scrollIntoView({block:'start',behavior:'smooth'});
  /* optional, low-stakes cross-reference — matched by normalized exact
     name against that season's leaders (already-established identity, a
     display nicety, not a new identity claim); skipped silently if absent */
  DATA.get('seasons/'+row.season+'.json').then(sd=>{
    const ln=document.getElementById('seasonLeaderNote'); if(!ln||!sd||!sd.leaders) return;
    const hit=Object.keys(sd.leaders).find(cat=>(sd.leaders[cat]||[]).some(l=>norm(l.player_raw)===norm(name)));
    if(hit) ln.innerHTML=`<div class="note" style="margin-top:6px">Entre los líderes de la liga en ${esc(_LEADER_CAT_ES[hit]||hit)} esa temporada.</div>`;
  }).catch(()=>{});
}
const _LEADER_CAT_ES={scoring:'anotación',rebounds:'rebotes',assists:'asistencias',blocks:'bloqueos',
  steals:'robos',turnovers:'pérdidas',threes:'triples',three_pct:'% de triples',
  off_rebounds:'rebotes ofensivos',free_throws:'tiros libres',free_throw_pct:'% de tiros libres'};


async function loadPlayerExtra(name,idHint,season){
  const host=$('#playerExtra'); if(!host) return;
  const id = (idHint!=null) ? idHint : (PXWALK && PXWALK[norm(name)]);
  const key = (id!=null) ? 'id:'+id : norm(name);
  host.innerHTML=''; host.dataset.key=key;
  SEASON_CMP_CAREER=null; SEASON_CMP_SEL=new Set(); SEASON_CMP_NAME=name;
  const p=PINDEX&&PINDEX.find(x=>norm(x.name)===norm(name));   /* curated, or null for archive-only */
  if(id==null){
    host.innerHTML=`<div class="card pcard" style="margin-top:var(--sp-3)"><div class="note" style="margin-top:var(--sp-2_5)">Sin ficha vinculada en el archivo de bsnpr.com `
      +`<span class="muted">— no se ha podido identificar con certeza a este jugador en esa base</span>.</div></div>`;
    return;   /* curated+unlinked: Información/Ficha/Fuentes already have everything real there is (showPlayer()'s sync build) */
  }
  const [d]=await Promise.all([DATA.get('players/'+id+'.json'), ensureDQ()]);   /* ensureDQ never rejects; null = no markers */
  if(!d || host.dataset.key!==key) return;

  const b=d.birth||{};
  /* J16 A05: a player with a disputed career row gets an explicit attribution on the DOB itself -- it is
     never called verified, since it has one source family and the ages shown for it are derived, not stated. */
  const dobDisputed=DISPUTED_IDS&&DISPUTED_IDS.has(Number(id));
  const dobStr=b.date?(fmtArchiveDob(b.date)+(dobDisputed?' (según bsnpr.com)':'')):null;
  const nat=(d.nationality&&d.nationality!=='Puerto Rico')?d.nationality:null;

  /* Información del jugador -- full rebuild (renderPlayerInfo(), tabs.js), same
     real fields this function always had (top[]/sameNameLine used to render inline
     above the season table); PHASE_19 only relocates them into their own panel. */
  if(p){
    renderPlayerInfo([['Nombre',p.name],['Posición',p.pos],['Años activos',p.years],
      ['Nacimiento',dobStr],['Lugar',b.city||null],['Nacionalidad',nat]]);
  }else{
    const r=(PALL||[]).find(x=>x.id===id)||{};
    const span=(r.first_season&&r.last_season)
      ? (r.first_season===r.last_season?''+r.first_season:r.first_season+'–'+r.last_season) : '';
    renderPlayerInfo([['Nombre',name],['Posición',r.position||null],['Años',span||null],['Fuente','bsnpr.com'],
      ['Nacimiento',dobStr],['Lugar',b.city||null],['Nacionalidad',nat]]);
  }

  /* 8.3b — fill the hero sparkline with points-by-season (the guard above
     already dropped a stale load, so #playerSpark belongs to this player). */
  const car=(d.career||[]).slice().sort((a,b)=>(a.season||0)-(b.season||0));
  const sp=$('#playerSpark');
  if(sp && car.length){
    const pv=car.map(c=>c.points==null?null:c.points);
    if(pv.filter(v=>v!=null).length>=2) sp.innerHTML=spark(pv,{area:true,dot:true,w:150,h:26});
  }

  /* rows the archive holds twice with different figures (Calidad de datos): both rows stay in the table,
     marked, and both stay out of the totals below; the archive does not pick one. Same for a row that
     conflicts with the player's own birth_date (J16 A05): it stays, is marked, and drops out of totals too. */
  const fl=car.map(c=>dqFlag(id,c));
  const dfl=car.map(c=>disputeFlag(id,c));
  const nConf=new Set(fl.filter(Boolean)).size;
  const nDisp=new Set(dfl.filter(Boolean)).size;
  let tp=0,tg=0; const sea=new Set();
  car.forEach((c,i)=>{ if(fl[i]||dfl[i]) return; if(c.points!=null)tp+=c.points; if(c.games!=null)tg+=c.games; if(c.season)sea.add(c.season); });
  const yrs=car.filter((c,i)=>!fl[i]&&!dfl[i]).map(c=>c.season).filter(Boolean);
  const lo=yrs.length?Math.min(...yrs):null, hi=yrs.length?Math.max(...yrs):null;
  /* the season table's own totals line (below) correctly spans only
     non-flagged years (lo/hi above) -- but "what years does this ficha's
     career[] claim at all" is a different, real question that stays
     answerable even when every row is disputed (Llovet: lo/hi above is
     null since all 5 rows are flagged, yet the archive plainly does have
     rows for 1965-1969 -- the dispute is about the birth date's
     compatibility with those years, not about whether the years exist).
     allLo/allHi back the Resumen "Rango en la ficha" tile and the Ficha
     paragraph's own span, both of which are about what the ficha SAYS,
     not what counts toward the totals. */
  const allYrs=car.map(c=>c.season).filter(Boolean);
  const allLo=allYrs.length?Math.min(...allYrs):null, allHi=allYrs.length?Math.max(...allYrs):null;
  /* PHASE_21 item 4: the mockup's own compact form ("1965–69") for the
     Resumen tile specifically -- same real allLo/allHi, just the shared
     century dropped from the end year so the tile never has to wrap at
     140px. Only compacted when both years share a century (true for every
     real BSN season so far, 1930-present); a genuine cross-century span
     prints in full rather than silently truncating a real digit. */
  const rangeCompact = allLo==null ? '—'
    : (Math.floor(allLo/100)===Math.floor(allHi/100) ? allLo+'–'+String(allHi).slice(-2) : allLo+'–'+allHi);

  /* archive-only Resumen tiles + Ficha paragraph -- real aggregates of the exact
     same per-row flags the season table below computes, never a second, possibly-
     divergent count. Curated players keep their own sync stat strip (showPlayer())
     and never touch these two ids. */
  if(!p){
    const statsHost=$('#playerArchiveStats');
    if(statsHost) statsHost.innerHTML=`<div class="ed-eye">Resumen</div><div class="strip">
      <div><div class="n">${car.length}</div><div class="l">Temporadas documentadas</div></div>
      <div><div class="n">${nConf+nDisp}</div><div class="l">Con conflicto de fuente</div></div>
      <div><div class="n">${rangeCompact}</div><div class="l">Rango en la ficha</div></div>
    </div>`;
    const fichaHost=$('#playerArchiveFicha');
    if(fichaHost) fichaHost.innerHTML=`<div class="ed-eye">Ficha</div>`
      +`<p class="note" style="margin-top:0">${esc(archiveFichaParagraph(car,nConf,nDisp,allLo,allHi,b,dobDisputed))}</p>`;
  }

  /* jugador05.asp scouting note (2005–06), where the archive has one -- curated
     players only (archive-only's own Ficha paragraph above is the whole story for
     them); appended to the sync Ficha panel's own async slot, never replacing it. */
  const bio=d.bio||null;
  if(p && bio && bio.notes_es){
    const fa=$('#playerFichaAsync');
    if(fa){
      const yr=bio.roster && bio.roster.year;
      fa.innerHTML=`<div class="note" style="margin-top:var(--sp-3)">Reseña de bsnpr.com${yr?' · '+yr:''}</div>`
        +`<p class="muted" style="font-size:var(--fs-xs);margin:var(--sp-1) 0 0;line-height:1.5">${esc(bio.notes_es)}</p>`;
    }
  }

  /* Fuentes tab: "Mismo nombre" cross-links (both player types) + the Wayback
     attribution line (curated only -- archive-only's renderArchiveCard() already
     wrote it synchronously, since it has id up front). */
  const fa2=$('#playerFuentesAsync');
  if(fa2){
    let fx='';
    if(p) fx+=`<div class="note" style="margin-top:0">Ficha del archivo de bsnpr.com (jugador #${id}) vía Wayback Machine.</div>`;
    fx+=sameNameLine(id);
    fa2.innerHTML=fx;
  }

  let h='';
  if(car.length){
    h+='<div class="note" style="margin-top:var(--sp-2_5)">Temporada por temporada <span class="dim" style="font-weight:400">— marca 2 o 3 para comparar</span></div>'
      +'<div class="tblwrap"><table><thead><tr><th></th><th>Año</th><th>Equipo</th><th class="num">JJ</th><th class="num">PTS</th></tr></thead><tbody>'
      +car.map((c,i)=>{
        const ak=FID2APP&&FID2APP[c.franchise_id];
        const team=(ak&&F[ak])
          ? `<button class="chip" style="padding:1px 7px" onclick="showTeam('${ak}')">${esc(F[ak].name)}</button>`
          : esc(c.team_raw||'—');
        const tag=(fl[i]?dqTag(fl[i]):'')+(dfl[i]?disputeTag():'');
        const yr=c.season
          ? `<button style="background:none;border:0;padding:0;font:inherit;color:inherit;text-decoration:underline;cursor:pointer" onclick="showPlayer(${JSON.stringify(name).replace(/"/g,'&quot;')},${id},${c.season})">${c.season}</button>`
          : '—';
        return `<tr><td><input type="checkbox" aria-label="Comparar ${c.season||''}" onchange="toggleSeasonCmp(this,${i})"></td>`
          +`<td>${yr}</td><td>${team}${tag?'<div>'+tag+'</div>':''}</td><td class="num">${c.games==null?'—':c.games}</td><td class="num">${c.points==null?'—':c.points.toLocaleString('es-PR')}</td></tr>`;
      }).join('')
      +'</tbody></table></div>'
      +'<div id="seasonCmpPanel"></div>';
    if(tp||tg||nConf||nDisp) h+=`<div class="muted" style="font-size:var(--fs-2xs);margin-top:6px">${seasonTotalsNote(tp,tg,sea,lo,hi,nConf,nDisp)}</div>`;
  }else{
    h+=`<div class="note" style="margin-top:var(--sp-2_5)">Sin estadísticas por temporada en el archivo `
      +`<span class="muted">— ${bio&&bio.notes_es?'sólo la reseña de arriba':'sin ficha detallada'}</span>.</div>`;
  }
  h+='<div id="seasonDetail"></div>';
  host.innerHTML=`<div class="card pcard" style="margin-top:var(--sp-3)">${h}</div>`;
  SEASON_CMP_CAREER=car;
  if(season!=null) renderSeasonDetail(car,season,name,id);

  /* PHASE_21 item 5: the mockup shows "Temporada por temporada" under the 3
     panels on Resumen, not hidden behind the Temporadas tab -- real for
     archive-only players (who have no curated stat strip otherwise) and for
     curated players with real season data. Read-only: no checkboxes, no
     per-season drill-in link -- those stay exclusive to the Temporadas tab
     (owner's own instruction), this is a second, simpler rendering of the
     exact same real car[]/fl/dfl the table above already computed. */
  renderResumenSeasons(car,fl,dfl,tp,tg,sea,lo,hi,nConf,nDisp);
}
/* shared by the Temporadas tab's own totals line and the Resumen-tab read-
   only table's footer below -- one real computation, two real renderings,
   never two separate counts that could quietly disagree. */
function seasonTotalsNote(tp,tg,sea,lo,hi,nConf,nDisp){
  return ((tp||tg)?`Totales del archivo: `
    +`${tp.toLocaleString('es-PR')} puntos en ${tg.toLocaleString('es-PR')} juegos · `
    +`${sea.size} temporada${sea.size===1?'':'s'}${lo?` (${lo}–${hi})`:''}. `
    +`Serie regular; suma de la tabla por temporada de bsnpr.com, no incluye playoffs.`:'')
    +(nConf?` Totales sin ${nConf} temporada${nConf===1?'':'s'} con fuentes en conflicto `
    +`(<a href="#archivo/calidad">ver Calidad de datos</a>).`:'')
    +(nDisp?` Totales sin ${nDisp} temporada${nDisp===1?'':'s'} con la fecha de nacimiento en conflicto `
    +`(<a href="#archivo/calidad">ver Calidad de datos</a>).`:'');
}
function renderResumenSeasons(car,fl,dfl,tp,tg,sea,lo,hi,nConf,nDisp){
  const host=$('#playerResumenSeasons'); if(!host) return;
  if(!car.length){ host.innerHTML=''; return; }
  const rows=car.map((c,i)=>{
    const ak=FID2APP&&FID2APP[c.franchise_id];
    const team=(ak&&F[ak])?esc(F[ak].name):esc(c.team_raw||'—');
    const tag=(fl[i]?dqTag(fl[i]):'')+(dfl[i]?disputeTag():'');
    return `<tr><td>${c.season||'—'}${tag?'<div>'+tag+'</div>':''}</td><td>${team}</td>`
      +`<td class="num">${c.games==null?'—':c.games}</td><td class="num">${c.points==null?'—':c.points.toLocaleString('es-PR')}</td></tr>`;
  }).join('');
  host.innerHTML=`<div class="seasons-resumen">
    <h2>Temporada por temporada</h2>
    <div class="tblwrap"><table><thead><tr><th>Año</th><th>Equipo</th><th class="num">JJ</th><th class="num">PTS</th></tr></thead>
    <tbody>${rows}</tbody></table></div>
    ${(tp||tg||nConf||nDisp)?`<div class="muted" style="font-size:var(--fs-2xs);margin-top:6px">${seasonTotalsNote(tp,tg,sea,lo,hi,nConf,nDisp)}</div>`:''}
  </div>`;
}

let LEAD_CAT='points', LEAD_MODE='total';
function buildLeaderControls(){
  const host=$('#leaderControls');
  host.innerHTML=`<div class="search-card"><div class="filters">
    <div class="field"><label for="lcat">Categoría</label><select id="lcat">
      <option value="points">Puntos</option><option value="rebounds">Rebotes</option><option value="assists">Asistencias</option></select></div>
    <div class="field"><label for="lmode">Orden</label><select id="lmode">
      <option value="total">Total de carrera</option><option value="pg">Por juego</option></select></div></div></div>`;
  $('#lcat').onchange=e=>{LEAD_CAT=e.target.value;buildLeaders();};
  $('#lmode').onchange=e=>{LEAD_MODE=e.target.value;buildLeaders();};
}
function buildLeaders(){
  const src=LEADERS[LEAD_CAT].slice();
  const rows=src.sort((a,b)=>LEAD_MODE==='total'?b[4]-a[4]:b[6]-a[6]);
  const col=LEAD_CAT==='points'?'var(--rojo)':LEAD_CAT==='rebounds'?'var(--azul)':'var(--ok)';
  bars($('#leadBars'),rows.map(r=>[r[1],LEAD_MODE==='total'?r[4]:r[6],col]),null,
    v=>LEAD_MODE==='total'?v.toLocaleString('es-PR'):v.toFixed(1));
  buildTable($('#leadTable'),[
    {label:'#',num:true},
    {label:'Jugador',wide:true,render:v=>`<button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showPlayer(${JSON.stringify(v).replace(/"/g,'&quot;')})">${esc(v)}</button>`},
    {label:'Pos'},{label:'Años'},{label:'Total',num:true},{label:'PJ',num:true},{label:'Por juego',num:true}
  ],rows.map((r,i)=>[i+1,r[1],r[2],r[3],r[4],r[5],r[6]]),
    {file:'lideres_'+LEAD_CAT,sort:null,
     note:LEAD_CAT==='assists'?'† Dalmau: total y promedio no cuadran en la fuente.':''});
}
let HOF_SORT='era';
function buildHOFControls(){
  $('#hofControls').innerHTML=`<div class="filters"><div class="field"><label for="hs">Ordenar por</label>
    <select id="hs"><option value="era">Época</option><option value="pts">Puntos</option><option value="mvp">MVP</option></select></div></div>`;
  $('#hs').onchange=e=>{HOF_SORT=e.target.value;buildHOF();};
}
/* PHASE_14 (owner-approved, redesign-v2): .salon-grid/.salon-card replaces the plain
   .cards.g2 -- same real HOF fields (portrait/name/years/pos/role/chips/note/"Ficha"
   button), unchanged; only the shell and a plain rank chip (this sort's own current
   position, not a "top 3" claim -- era/pts/mvp order has no gold-silver-bronze
   semantics) are new. */
function buildHOF(){
  const list=HOF.slice().sort((a,b)=>{
    if(HOF_SORT==='era')return a.era-b.era;
    if(HOF_SORT==='pts')return (b.pts||0)-(a.pts||0);
    return (b.mvp||0)-(a.mvp||0);
  });
  $('#hofList').innerHTML='<div class="salon-grid">'+list.map((h,i)=>{
    /* PHASE_21: real club color when PINDEX can resolve one for this HOF name
       (most can -- HOF feeds PINDEX's own merge), portrait() itself falls back
       to the real neutral navy otherwise -- never a guessed club. */
    const pp=PINDEX&&PINDEX.find(x=>norm(x.name)===norm(h.n));
    const hc1=pp&&pp.clubs.size?F[Array.from(pp.clubs)[0]].c1:null;
    return `
    <div class="salon-card">
      <span class="rankbadge">${i+1}</span>
      ${portrait(h.n,hc1,null,48,58,h.pos)}
      <div class="body">
        <div class="who">${esc(h.n)}</div>
        <div class="dim" style="font-size:12px">${esc(h.yrs)} · ${esc(h.pos)}</div>
        <div class="muted" style="font-size:13px;margin-top:5px">${esc(h.role)}</div>
        <div class="chips">${h.hon.map(x=>`<span class="tag ${/MVP|Salón|Máximo|Récord|Campeón|récord/i.test(x)?'gold':''}">${esc(x)}</span>`).join('')}</div>
        ${h.note?`<div class="note">${esc(h.note)}</div>`:''}
        <div class="btnrow"><button class="btn" style="padding:3px 9px;font-size:12px"
          onclick="showPlayer(${JSON.stringify(h.n).replace(/"/g,'&quot;')})">Ficha</button></div>
      </div></div>`;
  }).join('')+'</div>';
}
/* PHASE_14 (owner-approved, redesign-v2): reuses .coach-grid/.coach-card (built for
   buildCoaches() just below -- same shape of content: a name/title + two lines, no
   numeral, no portrait). Real STONE fields unchanged. */
function buildStone(){
  $('#stone').innerHTML='<div class="coach-grid">'+STONE.map(s=>`
    <div class="coach-card"><div class="ct">${esc(s[0])}</div>
    <div class="cs">${esc(s[1])}</div>
    <div class="note">${esc(s[2])}</div></div>`).join('')+'</div>';
}

/* ============================================================
   RÉCORDS
   ============================================================ */
/* PHASE_14 (owner-approved, redesign-v2): .rec-grid/.rec-card replaces the plain
   .cards.g2 -- same real RECORDS fields, unchanged; numeral's font-family switches
   from inherit to var(--font-display), the same big-numeral treatment every other
   number in this system already gets (.stat .n/.lead-row .val .n/.bar-row .v). */
function buildRecords(){
  $('#recordList').innerHTML='<div class="rec-grid">'+RECORDS.map(r=>`
    <div class="rec-card">
      <div style="display:flex;align-items:baseline;gap:var(--sp-2_5)">
        <span style="font-family:var(--font-display);font-weight:800;font-size:32px;line-height:1;color:var(--rojo)">${esc(r[1])}</span>
        <span style="font-weight:700">${esc(r[0])}</span></div>
      <div class="muted" style="font-size:var(--fs-xs);margin-top:var(--sp-1)">${esc(r[2])} · ${r[3]}</div>
      ${r[4]?`<div class="note">${esc(r[4])}</div>`:''}</div>`).join('')+'</div>';
}
function buildScoringChart(){
  const pts=SCORING.filter(s=>s[3]==='ppg');
  const W=680,H=230,pad=34;
  const xs=pts.map(p=>p[0]), ys=pts.map(p=>p[4]);
  const x0=Math.min.apply(null,xs), x1=Math.max.apply(null,xs);
  const y0=Math.floor(Math.min.apply(null,ys)-1), y1=Math.ceil(Math.max.apply(null,ys)+1);
  const X=v=>pad+(v-x0)/(x1-x0)*(W-pad*1.4);
  const Y=v=>H-pad-(v-y0)/(y1-y0)*(H-pad*1.6);
  const path=pts.map((p,i)=>(i?'L':'M')+X(p[0]).toFixed(1)+' '+Y(p[4]).toFixed(1)).join(' ');
  let g='';
  for(let v=y0;v<=y1;v+=5) g+=`<line x1="${pad}" y1="${Y(v)}" x2="${W-12}" y2="${Y(v)}" stroke="var(--line)"/>
    <text x="6" y="${Y(v)+4}" fill="var(--ink-3)" font-size="10">${v}</text>`;
  const dots=pts.map(p=>`<circle cx="${X(p[0]).toFixed(1)}" cy="${Y(p[4]).toFixed(1)}" r="3.2" fill="var(--rojo)">
    <title>${p[0]} — ${esc(p[1])}, ${p[4]}</title></circle>`).join('');
  const tvals=[]; for(let v=Math.ceil(x0/5)*5; v<=x1; v+=(x1-x0>28?10:5)) tvals.push(v);
  const ticks=tvals.map(v=>`<text x="${X(v)}" y="${H-10}" fill="var(--ink-3)" font-size="10" text-anchor="middle">${v}</text>`).join('');
  $('#scoringChart').innerHTML=`<div class="card" style="padding:var(--sp-2_5)"><svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto" role="img"
    aria-label="Promedio del campeón de anotación por temporada, ${x0} a ${x1}">
    ${g}<path d="${path}" fill="none" stroke="var(--rojo)" stroke-width="2"/>${dots}${ticks}</svg></div>
    <p class="note">Hasta 1970 la liga premiaba puntos totales; desde 1971, promedio. Las dos series no son comparables, así que solo se grafica la segunda.</p>`;
}
/* PHASE_11 (owner-approved, redesign-v2): consecutive-year, same-player runs, walked live
   over the real (ascending) SCORING array -- returns {year: runLength}, keyed on the run's
   OWN most recent year (so rendering most-recent-first shows the 🔥 pill exactly once per
   run, on its first/newest row, not on every row of the run). Not hardcoded: recomputed
   from SCORING every call, same discipline as historiaStreaks() above. */
function scoringStreaksFor(arr,yearIdx,nameIdx){
  const out={}; let i=0;
  while(i<arr.length){
    let j=i;
    while(j+1<arr.length && arr[j+1][nameIdx]===arr[i][nameIdx] && arr[j+1][yearIdx]===arr[j][yearIdx]+1) j++;
    if(j>i) out[arr[j][yearIdx]]=j-i+1;
    i=j+1;
  }
  return out;
}
/* PHASE_11 (owner-approved, redesign-v2): the old plain sortable table is now the mockup's
   decade-grouped .lead-list, most-recent-first, real 🔥 repeat-champion pill from
   scoringStreaksFor() above -- reads the real, LIVE SCORING array, whatever its current
   state is: 26 rows (1966-1991) is only this file's own baked-in seed for a local/offline
   open; hydrate() (init.js) replaces it in place with a richer, reconciled 68-row set
   (1948-2021) whenever web/data is reachable -- confirmed live, not assumed, since this
   function never caches a row count or year range, only ever reads SCORING fresh. CSV/
   export button removed here (a lead-list isn't a buildTable() output any more) but the
   data itself, the "Ver ficha" link, and the total row count are all unchanged. The line
   chart above (buildScoringChart()) is deliberately kept, not removed -- it's real, working
   data visualization the mockup simply didn't happen to include, and nothing in this
   pass's scope asked for it to go. */
function buildScoringTable(){
  const streaks=scoringStreaksFor(SCORING,0,1);
  const rows=SCORING.slice().reverse();
  let lastDecade=null, html='';
  rows.forEach(r=>{
    const [y,player,club,metric,value]=r;
    const decade=Math.floor(y/10)*10+'s';
    if(decade!==lastDecade){ html+=`<div class="decade-head">${esc(decade)}</div>`; lastDecade=decade; }
    const streak=streaks[y];
    html+=`<div class="lead-row${streak?' repeat':''}">
      <div class="yrchip mono">${y}</div>
      <div class="who">
        <div class="pn"><button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showPlayer(${JSON.stringify(player).replace(/"/g,'&quot;')})">${esc(player)}</button>${streak?`<span class="streakpill">🔥 ${streak}×</span>`:''}</div>
        <div class="cl">${esc(club)}</div>
      </div>
      <div class="val"><div class="n mono">${value}</div><div class="u">${metric==='ppg'?'ppj':'pts totales'}</div></div>
    </div>`;
  });
  $('#scoringTable').innerHTML=`<div class="lead-list">${html}</div>
    <p class="scrollnote">${SCORING.length} temporadas documentadas, ${SCORING[0][0]}–${SCORING[SCORING.length-1][0]}. 🔥 marca rachas de campeonatos consecutivos del mismo jugador.</p>`;
}
/* PHASE_14 (owner-approved, redesign-v2): .coach-grid/.coach-card replaces the plain
   .cards.g2 -- same real COACHES fields, unchanged. */
function buildCoaches(){
  $('#coachList').innerHTML='<div class="coach-grid">'+COACHES.map(c=>`
    <div class="coach-card"><div class="ct">${esc(c[0])}</div>
    <div class="cs">${esc(c[1])}</div>
    ${c[2]?`<div class="note">${esc(c[2])}</div>`:''}</div>`).join('')+'</div>';
}
function buildNBA(){
  $('#nbaList').innerHTML='<div class="chips">'+NBA_PLAYERS.map(p=>
    `<span class="tag blue" title="${esc(p[1])}">${esc(p[0])}</span>`).join('')+'</div>'+
    '<p class="note">'+NBA_PLAYERS.map(p=>esc(p[0])+': '+esc(p[1])).join(' · ')+'</p>';
}
/* PHASE_41 (owner-approved, redesign-v2): RETIRED itself is NOT edited -- still
   [4,5,9,15,16,17,17,54] / [5,9,15], the exact literal PHASE_41A's own read-only
   source check left in place (undeterminable from repo evidence whether Bayamón's
   duplicate 17 is a typo or a real double-retirement; kept exactly as recorded,
   not guessed at either way). Rendering counts occurrences at render time -- a
   Map over r[2].split(' · '), never a splice/dedupe on RETIRED -- so a repeated
   number shows once with an "×N" mark instead of twice, and r[1] (the total,
   still 8 for Bayamón) stays the honest total-slots count while the chip count
   (7 distinct) and the dupe itself both stay visible and spelled out in the
   count line. "La liga los publica como dígitos, sin nombres…" kept verbatim. */
function buildRetiredNums(){
  $('#retiredList').innerHTML='<div class="retired-grid">'+RETIRED.map(r=>{
    const k=FKEYS.find(x=>F[x].name===r[0]);
    const counts=new Map();
    r[2].split(' · ').forEach(n=>counts.set(n,(counts.get(n)||0)+1));
    const dupes=[...counts.entries()].filter(([,c])=>c>1);
    const chips=[...counts.entries()].map(([n,c])=>
      `<span class="jersey-chip">${esc(n)}${c>1?`<i class="x2">×${c}</i>`:''}</span>`).join('');
    const countLine = dupes.length===1
      ? r[1]+' números retirados — el '+esc(dupes[0][0])+' se retiró '
        +(dupes[0][1]===2?'dos veces':dupes[0][1]+' veces')+'.'
      : dupes.length>1
      ? r[1]+' números retirados, con '+dupes.length+' repetidos.'
      : r[1]+' números retirados.';
    const plate=k?crestPlate(k):null;
    const crestHtml=k?`<span class="crest-plate" style="--plate:${plate}">${crest(k,31,36)}</span>`:'';
    return `<div class="card retired-card">
      <div class="retired-head">${crestHtml}<div class="retired-name">${esc(r[0])}</div></div>
      <div class="jersey-row">${chips}</div>
      <div class="note">${countLine} La liga los publica como dígitos, sin nombres — y el archivo no los adivina.</div>
    </div>`;
  }).join('')+'</div>';
}

/* ============================================================
   REFUERZOS
   ============================================================ */
/* PHASE_11 (owner-approved, redesign-v2): visual polish only -- REF_RULES itself (4 real
   bylaw cards) is untouched; new .rules/.rule grid (mockup's own class names, no collision)
   instead of the generic .cards.g2. .timeline (REF_TIMELINE) and the scorer table
   (REF_SCORERS, already a buildTable()/.tblwrap output) are deliberately left alone --
   .timeline is shared with Inicio's own "Lo próximo" (out of scope this pass), and the
   scorer table already gets the shared table treatment for free. */
function buildRefRules(){
  $('#refRules').innerHTML='<div class="rules">'+REF_RULES.map(r=>
    `<div class="rule"><b>${esc(r[0])}</b>${esc(r[1])}<br><span class="muted" style="font-size:var(--fs-2xs)">${esc(r[2])}</span></div>`
  ).join('')+'</div>';
}
function buildRefTimeline(){
  $('#refTimeline').innerHTML='<div class="timeline">'+REF_TIMELINE.map(t=>`
    <div class="tw"><div class="td">${esc(t[0])}</div><div class="tt2">${esc(t[1])}</div>
    <div class="tb">${esc(t[2])}</div></div>`).join('')+'</div>';
}
function buildRefScorers(){
  buildTable($('#refScorers'),[
    {label:'#',num:true},{label:'Jugador',wide:true},{label:'Club',wide:true},{label:'Estatus'},
    {label:'Puntos',num:true},{label:'PPJ',num:true}
  ],REF_SCORERS.map(r=>[r[0],r[1],r[2],r[3],r[4],r[5]]),{file:'refuerzos_2025',sort:4,dir:-1});
  const n=el('div','warn');
  n.innerHTML='Cuatro de los cinco máximos anotadores de 2025 fueron refuerzos. En 2026 el patrón se repite: de los cinco primeros en promedio, el mejor nativo no aparece. Esa es la discusión que la asociación de jugadores perdió 11-2 en octubre de 2024.';
  $('#refScorers').appendChild(n);
}

/* ============================================================
   FUENTES
   ============================================================ */
const REC_LABEL={
  'Points, single game':'puntos en un juego','Assists, single game':'asistencias en un juego',
  'Points, career':'puntos de carrera','Rebounds, career':'rebotes de carrera',
  'Points, single season':'puntos en una temporada','Rebounds, single season':'rebotes en una temporada',
  'Team points, single game':'puntos de equipo','Team points, one quarter':'puntos en un parcial',
  'Assists, career':'asistencias de carrera','Blocks, career':'tapones de carrera',
  'Three-pointers, career':'triples de carrera'
};
const COVERAGE=[
  ['1930s',20,'Campeones sí. Nada más.'],
  ['1940s',25,'Campeones y una disputa sin resolver en 1945.'],
  ['1950s',20,'Campeones; 1953 en blanco.'],
  ['1960s',35,'Campeones y campeones de anotación desde 1966.'],
  ['1970s',45,'Campeones, anotación, algunos récords.'],
  ['1980s',50,'Igual, más líderes de carrera acumulados.'],
  ['1990s',45,'Campeones y anotación hasta 1991; luego se corta.'],
  ['2000s',45,'Campeones, MVP de 2004 y 2009, y la temporada 2009 completa.'],
  ['2010s',60,'Temporadas 2016, 2017 y 2018 con premios y líderes; MVP de 2010, 2011, 2014, 2016, 2017, 2018.'],
  ['2020s',90,'Posiciones, finales juego a juego, premios completos, líderes, dueños.']
];
const LEGEND_NOTE=[
  ['¿Quién es leyenda?',
   'Cuatro pruebas, todas sacadas de tablas que ya están en este archivo: top 10 histórico en puntos, rebotes o asistencias; tres o más MVP; un récord de la liga vigente; o una cancha con su nombre. Basta con una. Cada ficha dice cuál cumplió.'],
  ['Por qué se cambió',
   'Antes la etiqueta estaba puesta a mano sobre diecinueve jugadores sin criterio escrito en ninguna parte, y pesaba más que el MVP tanto en el orden del índice como en la puntuación de La Temporada Perfecta. Una opinión editorial estaba ordenando la liga en silencio.'],
  ['Lo que el criterio no ve',
   'Seis nombres que tenían la etiqueta no pasan las pruebas y ahora aparecen como «Figura del BSN»: Carlos Arroyo, J. J. Barea, Butch Lee, Jerome Mincy, Sammy Betancourt y Raúl «Tinajón» Feliciano. No es que valgan menos. Es que su huella está en la NBA, en la selección o en los años ochenta, y este archivo no guarda todavía las cifras que lo probarían. El hueco es del archivo, no del jugador.']
];
function buildSources(){
  const host=$('#sourcesBox');
  const conflicts=[
    ['1945','Campeón en disputa','Wikipedia en inglés dice Capitalinos de San Juan; la de español, Santos de San Juan. Ambas coinciden en el subcampeón, Gallitos de la UPR. El archivo carga la versión inglesa y lo marca.'],
    ['1942–43','Temporada partida','Español separa 1942 y 1942-43, ambas de San Germán. Aquí van juntas, así que San Germán aparece con 13 títulos donde casi todas las fuentes dicen 14. Arreglarlo necesita una clave de temporada que admita años partidos.'],
    ['1953','Sin campeón','Ninguna fuente consultada registra uno. O no hubo temporada, o la tabla de franquicias está incompleta.'],
    ['Dalmau, asistencias','Total y promedio no cuadran','2.302 en 537 juegos son 4,3 por juego, no 5,1. Es el único dato de las tablas de campeones y líderes que se contradice a sí mismo. Marcado en dos sitios y excluido de los juegos.'],
    ['Harrell 2026','Club en disputa','RealGM lo pone en San Germán; Noticel, en Caguas.'],
    ['2026','Dos cifras para la misma temporada','El export oficial del BSN cuenta solo temporada regular; RealGM incluye la postemporada. Trice aparece con 34 juegos y 18,4 puntos en uno y con 44 y 19,3 en el otro. Ninguna está mal. El archivo guarda las dos y no promedia.'],
    ['Dalmau, asistencias','Posible resolución','bsnpr.com lista al líder de asistencias como Raymond «Richie» Dalmau Santana con 455 juegos, no como Raymond Dalmau Pérez con 537. Si son dos personas distintas, la contradicción de 4,3 contra 5,1 desaparece. Sin confirmar.']
  ];
  const C=(DATA_TEXT&&MANIFEST)?MANIFEST.counts:null;
  const nf=n=>Number(n).toLocaleString('es-PR');
  const gaps = C ? [
    'No hay una base pública de estadísticas por temporada del BSN anterior a 2001. Antes de eso el archivo solo tiene campeones, campeones de anotación y MVP.',
    `Boxscores: ${nf(C.game_files)} partidos con caja completa, de las temporadas 2001–2003 y 2008–2013 — lo que sobrevivió en el Wayback Machine del motor de estadísticas de bsnpr.com. Fuera de esos años no hay ninguno.`,
    `Posiciones: esas mismas ${C.seasons_with_standings} temporadas (derivadas de los partidos archivados, no siempre completas) más 2025 y 2026. 2004–2007 y 2014–2024 no tienen posiciones extraíbles.`,
    `Campeones de anotación 1948–2021 (${C.scoring_titles} temporadas). Faltan 2022 en adelante.`,
    'MVP 1958–2004 de la tabla histórica de bsnpr.com; los recientes según prensa. Faltan 1950, 1953, 1956 y varias temporadas recientes que ninguna fuente pública lista.',
    `Premios y líderes por temporada (Novato, Defensa, líderes de cada categoría) solo donde bsnpr.com o Wikipedia los publican: ${C.seasons_with_awards} temporadas con algún premio, ${C.seasons_with_leaders} con tablas de líderes. 2014–2015 y 2019–2023 son los huecos grandes.`,
    'Los números retirados de Bayamón (8) y Guaynabo (3) se publican como dígitos, sin nombres.',
    'Líderes de carrera y récords vienen de Wikipedia y están ~5 años desactualizados: los jugadores activos aparecen sub-contados.'
  ] : [
    'No existe ninguna base pública de estadísticas por temporada del BSN anterior a 2011. Ese es el muro real.',
    'MVP por año: 39 temporadas recuperadas de la tabla de ganadores repetidos y de las páginas de temporada. Faltan los ganadores de una sola vez, que Wikipedia publica dentro de un widget ordenable que no sobrevive a la extracción de texto.',
    'Solo existen páginas de temporada en Wikipedia para 2009, 2016, 2017, 2018 y 2024 en adelante. Entre 2010 y 2015 y entre 2019 y 2023 no hay fuente pública extraíble de premios ni de líderes.',
    'Campeones de anotación 1956–65 y 1992–presente: mismo artículo, misma tabla, simplemente no se bajó.',
    'Los números retirados de Bayamón (8) y Guaynabo (3) se publican como dígitos, sin nombres.',
    'Posiciones completas solo de 2009, 2025 y 2026.',
    'No hay boxscores. Ninguno, de ninguna temporada.'
  ];
  const pistaBlock = C ? `
    <h3 class="sec">De dónde salieron los boxscores y los líderes</h3>
    <div class="card"><p style="margin:0">El viejo motor de estadísticas de <b>bsnpr.com</b>
    (<code>estadisticas/*.asp</code>, <code>jugadores/jugador?id=N</code>) está muerto en la web
    actual, pero el Wayback Machine guardó buena parte: <b>${nf(C.game_files)} partidos</b> con caja de
    2001–2003 y 2008–2013, la tabla de líderes por temporada, la de MVP históricos (1958–2004) y
    <b>${nf(C.players)} fichas de jugador</b>. Todo eso se bajó, se parseó y es lo que llena las
    pestañas de Temporadas y Jugadores cuando esta página se sirve desde un servidor. Lo que el
    Wayback no capturó — sobre todo 2004–2007 y 2014–2023 — sigue siendo un hueco.</p></div>` : `
    <h3 class="sec">La pista que abre todo</h3>
    <div class="card" style="border-color:var(--ok)">
      <p style="margin:0 0 8px"><b>Hallazgo del 3 de septiembre de 2026:</b> bsnpr.com tiene páginas de jugador vivas en
      <code>bsnpr.com/jugadores/jugador?id=NNN</code>. La de Carlos Arroyo es la 273 y trae una tabla temporada por temporada
      con columnas de caja completas: juegos, minutos, tiros de dos y de tres intentados y anotados, tiros libres,
      asistencias, rebotes y puntos.</p>
      <p class="muted" style="font-size:var(--fs-xs);margin:0">La sesión anterior concluyó que el motor de estadísticas del BSN
      estaba muerto y solo era recuperable por el Wayback Machine. Eso era falso: la ruta vieja murió, pero existe un
      endpoint de jugador vivo e indexado. Si <code>id</code> es un rango denso de enteros, ese endpoint <b>es</b> la base
      de datos de jugadores del BSN. Devuelve 500 a un fetcher automático, así que hay que recorrerlo desde un navegador
      o un script con cabeceras normales. Está incluido: <code>bsnpr_scraper.py</code>.</p>
    </div>
    <div class="card" style="margin-top:var(--sp-3)">
      <p style="margin:0 0 8px">El motor de estadísticas del viejo <b>bsnpr.com</b> publicaba líderes por temporada en
      <code>estadisticas/lideres.asp?anio=YYYY</code>, con años de <b>1957 a 2004</b>. Las páginas ya no existen, pero
      las URLs aparecen citadas una por una en las referencias de Wikipedia — es decir, existieron, y es muy probable
      que estén en el Wayback Machine.</p>
      <p class="muted" style="font-size:13.5px;margin:0">Un solo volcado de ese archivo cerraría casi todos los huecos de arriba a la vez:
      líderes por temporada desde 1957, MVP, posiciones y un grupo de jugadores diez veces más grande — que es lo único que
      frena a los juegos y a las consultas por jugador.</p>
      <div class="note">Consulta CDX: <code>web.archive.org/cdx/search/cdx?url=bsnpr.com/estadisticas*&amp;output=json&amp;collapse=urlkey</code>
      — hay que correrla fuera de este archivo.</div>
    </div>`;
  host.innerHTML=`
    <h3 class="sec">Conflictos entre fuentes</h3>
    <div class="cards g2">${conflicts.map(c=>`<div class="card">
      <div class="dim" style="font-size:11px;letter-spacing:.07em;font-weight:600">${esc(c[0]).toUpperCase()}</div>
      <div style="font-weight:700;margin-top:3px">${esc(c[1])}</div>
      <div class="muted" style="font-size:13.5px;margin-top:4px">${esc(c[2])}</div></div>`).join('')}</div>
    <p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">Las diferencias entre fuentes en las estadísticas de cada jugador están en <a href="#archivo/calidad">Calidad de datos</a>.</p>

    <h3 class="sec">Cómo se decide quién es leyenda</h3>
    <div class="cards g2">${LEGEND_NOTE.map(c=>`<div class="card">
      <div style="font-weight:700">${esc(c[0])}</div>
      <div class="muted" style="font-size:13.5px;margin-top:4px">${esc(c[1])}</div></div>`).join('')}</div>

    <h3 class="sec">Lo que falta</h3>
    <ul class="muted" style="font-size:14px;line-height:1.7;padding-left:18px">${gaps.map(g=>'<li>'+esc(g)+'</li>').join('')}</ul>

    ${pistaBlock}

    <h3 class="sec">De dónde sale cada cosa</h3>
    <div class="cards g2">
      <div class="card"><div style="font-weight:700">Campeones 1930–2025</div>
        <div class="muted" style="font-size:13.5px">Wikipedia, invirtiendo las listas por franquicia. Esa inversión fue lo que reveló el hueco de 1953.</div></div>
      <div class="card"><div style="font-weight:700">Temporada 2026</div>
        <div class="muted" style="font-size:13.5px">El Nuevo Día, Primera Hora, Telemundo PR, El Vocero y Noticel para la final y los premios; la app oficial del BSN para posiciones y líderes.</div></div>
      <div class="card"><div style="font-weight:700">Líderes de carrera y récords</div>
        <div class="muted" style="font-size:13.5px">Wikipedia. Todos verificados contra los CSV del proyecto.</div></div>
      <div class="card"><div style="font-weight:700">Reglas de refuerzos</div>
        <div class="muted" style="font-size:13.5px">Artículos 22.1, 23.1 y 13.1 del reglamento, más la cobertura del voto de octubre de 2024.</div></div>
    </div>

    <h3 class="sec">Escudos y fotos</h3>
    <div class="card"><p style="margin:0">Todos los escudos y retratos están dibujados en SVG con los colores reales del club.
      Los logos oficiales y las fotos de jugadores necesitarían permiso para publicarse — es la razón principal por la que
      Apple rechaza apps de este tipo — así que este archivo no los usa. Con cero imágenes, todo se ve igual de bien.</p></div>`;
}
/* ============================================================
   PREMIOS, MVP POR AÑO Y FINALES JUEGO A JUEGO
   ============================================================ */
/* PHASE_11 (owner-approved, redesign-v2): MVP judgment call, reported explicitly per this
   task's own request -- the referenced mockup's Premios view leaves MVP as an unbuilt
   "en construcción" placeholder, because whoever built that mockup didn't have MVP data on
   hand. This app already has real MVP data live today -- MVP_YEARS' own baked-in seed is
   39 rows (not the "30" an older comment near its declaration claims), and, same discovery
   as SCORING just above, hydrate() (init.js) fills real gaps in from index/mvp.json
   whenever reachable -- 63 rows confirmed live, not assumed, once hydrated. Either way,
   this function only ever reads the current, live MVP_YEARS -- rendering a fake "not
   available yet" card over data that demonstrably exists would
   itself misrepresent the archive, the opposite of this app's whole honesty-about-gaps
   discipline. So MVP gets the SAME real lead-list/decade/🔥-streak treatment as scoring,
   from the real MVP_YEARS array, with its own real "years missing" note kept verbatim
   (never fabricating the ~58 years this array doesn't have a source for) -- "not yet
   available" is honored for what's actually missing (those years), not for the whole tab. */
function buildMVPYears(){
  const streaks=scoringStreaksFor(MVP_YEARS,0,1);
  const rows=MVP_YEARS.slice().reverse();
  let lastDecade=null, html='';
  rows.forEach(r=>{
    const [y,player,club]=r;
    const decade=Math.floor(y/10)*10+'s';
    if(decade!==lastDecade){ html+=`<div class="decade-head">${esc(decade)}</div>`; lastDecade=decade; }
    const streak=streaks[y];
    const id=MVP_ID&&MVP_ID[y], also=MVP_ALSO&&MVP_ALSO[y];
    html+=`<div class="lead-row${streak?' repeat':''}">
      <div class="yrchip mono">${y}</div>
      <div class="who">
        <div class="pn"><button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showPlayer(${JSON.stringify(player).replace(/"/g,'&quot;')}${id!=null?','+id:''})">${esc(player)}</button>${streak?`<span class="streakpill">🔥 ${streak}×</span>`:''}${also?` <span class="muted" style="cursor:help" title="El archivo también registra a ${esc(also)} para este año">†</span>`:''}</div>
        <div class="cl">${esc(club)}</div>
      </div>
      <div class="val"><div class="n mono">${y}</div><div class="u">temporada</div></div>
    </div>`;
  });
  const missing=[];
  for(let y=1950;y<=LAST;y++){ if(!MVP_YEARS.some(r=>r[0]===y)) missing.push(y); }
  const note=(DATA_TEXT
    ? `Recuperados ${MVP_YEARS.length} de las ${LAST-1949} temporadas desde 1950. La tabla histórica de bsnpr.com (una sola captura de 2004) cubre 1958–2004; el resto sale de páginas de temporada y de la lista de ganadores repetidos. Faltan ${missing.length}: 1950, 1953 y 1956, más varias temporadas recientes que ninguna fuente pública lista todavía. `
    : `Recuperados ${MVP_YEARS.length} de las ${LAST-1949} temporadas desde 1950. Faltan ${missing.length}, casi todas de ganadores que solo lo lograron una vez: Wikipedia los publica dentro de un widget ordenable que no sobrevive a la extracción de texto. `)
    + `Años sin MVP en el archivo: ${missing.join(', ')}.`;
  $('#mvpYears').innerHTML=`<div class="lead-list">${html}</div>
    <p class="scrollnote">🔥 marca MVP consecutivos del mismo jugador.</p>
    <div class="warn" style="margin-top:var(--sp-3)">${esc(note)}</div>`;
}

function buildSeasonAwards(){
  const years=Array.from(new Set(SEASON_AWARDS.map(r=>r[0]))).sort((a,b)=>b-a);
  const host=$('#seasonAwards');
  host.innerHTML=`<div class="filters"><div class="field"><label for="awYear">Temporada</label>
    <select id="awYear"><option value="">Todas</option>${years.map(y=>`<option value="${y}">${y}</option>`).join('')}</select></div></div>
    <div id="awTable"></div>`;
  const draw=()=>{
    const y=$('#awYear').value;
    const rows=SEASON_AWARDS.filter(r=>!y||String(r[0])===y)
      .map(r=>[r[0],r[1],r[2],r[3],r[4]]);
    buildTable($('#awTable'),[
      {label:'Año',num:true},{label:'Premio'},
      {label:'Jugador',wide:true,render:v=>`<button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showPlayer(${JSON.stringify(v).replace(/"/g,'&quot;')})">${esc(v)}</button>`},
      {label:'Club',wide:true},{label:'Línea',wide:true}
    ],rows,{file:'premios_bsn',sort:0,dir:-1});
  };
  $('#awYear').onchange=draw; draw();
  const n=el('p','note');
  n.textContent='Solo existen páginas de temporada para 2009, 2016, 2017, 2018 y 2024 en adelante. Los años entre medio no tienen fuente pública que se pueda extraer.';
  host.appendChild(n);
}

let FIN_YEAR=2026;
function buildFinalsByYear(){
  const years=Object.keys(FINALS_BY_YEAR).map(Number).sort((a,b)=>b-a);
  const host=$('#finalsByYear');
  host.innerHTML=`<div class="filters"><div class="field"><label for="finYear">Final</label>
    <select id="finYear">${years.map(y=>`<option value="${y}">${y}</option>`).join('')}</select></div></div>
    <div id="finBody"></div>`;
  $('#finYear').onchange=e=>{FIN_YEAR=+e.target.value;drawFinal();};
  drawFinal();
}
/* PHASE_12 (owner-approved, redesign-v2): item 6's own instruction for this panel --
   "reuse Historia's La Cinta row styling directly, don't design a new look for it." Same
   real FINALS_BY_YEAR data, same series/MVP/table computation; only the container markup
   changed, from the old plain .series/.seriesrow block to Historia's own .readout/
   .champ-line/.vs-line classes (PHASE_11, main.css) -- the exact same classes, not a
   re-declared copy of them. */
function drawFinal(){
  const f=FINALS_BY_YEAR[FIN_YEAR];
  const host=$('#finBody');
  const c=F[f.champ], r=F[f.ru];
  const w=+f.series.split('-')[0], l=+f.series.split('-')[1];
  host.innerHTML=`<div class="readout" style="margin-top:12px">
    <div class="champ-line">${crest(f.champ,28,34)} ${esc(c.name)} <span class="mono">${w}</span></div>
    <div class="vs-line">venció a ${esc(r.name)} <span class="mono">${l}</span> · MVP de la final: <b>${esc(f.mvp)}</b></div>
  </div><div id="finTbl"></div>`;
  const rows=f.games.map(g=>{
    const win = g[4]>g[5] ? g[2] : g[3];
    return ['Juego '+g[0],g[1],F[g[2]].abbr+' (L)',F[g[3]].abbr+' (V)',g[4]+'-'+g[5],
            Math.abs(g[4]-g[5]),F[win].abbr,g[6],g[7]||''];
  });
  buildTable($('#finTbl'),[
    {label:'Juego'},{label:'Fecha'},{label:'Local'},{label:'Visita'},{label:'Marcador'},
    {label:'Margen',num:true},{label:'Ganó'},{label:'Serie'},{label:'Parciales',wide:true}
  ],rows,{file:'final_'+FIN_YEAR,sort:null});
}

/* PHASE_41 (owner-approved, redesign-v2): OWNERS itself is NOT edited -- it still only
   covers 5 of the 12 real active clubs. This now renders all 12 (FKEYS.filter(active)),
   OWNERS' own 5 first in OWNERS' own existing order, then the other 7 in a muted state
   -- "—" where the owner name would sit, "Sin apoderado confirmado en el archivo" where
   the optional note would sit, same card shape both ways, so the gap reads as a real
   archive gap (PC4) rather than as missing content. Intro line computed from F/OWNERS,
   spelled out via numWordsEs() -- cannot say the wrong count the way Equipos' own
   lede used to (PHASE_39/40). Each crest wrapped in the new .crest-plate (crestPlate()
   above) for the dark-theme Cangrejeros / light-theme Vaqueros-Criollos-Santeros
   contrast bug -- crest() itself is untouched. */
function buildOwners(){
  const activeKeys=FKEYS.filter(k=>F[k].active);
  const ownedKeys=OWNERS.map(o=>o[0]);
  const unownedKeys=activeKeys.filter(k=>!ownedKeys.includes(k));
  const wOwned=numWordsEs(OWNERS.length), wActive=numWordsEs(activeKeys.length);
  const intro=wOwned[0].toUpperCase()+wOwned.slice(1)+' de los '+wActive
    +' clubes tienen apoderado confirmado en el archivo.';
  const ownedCards=OWNERS.map(o=>{
    const plate=crestPlate(o[0]);
    return `<div class="card" style="display:flex;gap:var(--sp-3)">
      <span class="crest-plate" style="--plate:${plate}">${crest(o[0],31,36)}</span>
      <div><div style="font-weight:700">${esc(F[o[0]].name)}</div>
      <div class="muted" style="font-size:var(--fs-xs)">${esc(o[1])}</div>
      ${o[2]?`<div class="note">${esc(o[2])}</div>`:''}</div></div>`;
  }).join('');
  const unownedCards=unownedKeys.map(k=>{
    const plate=crestPlate(k);
    return `<div class="card muted" style="display:flex;gap:var(--sp-3)">
      <span class="crest-plate" style="--plate:${plate}">${crest(k,31,36)}</span>
      <div><div style="font-weight:700">${esc(F[k].name)}</div>
      <div class="muted" style="font-size:var(--fs-xs)">—</div>
      <div class="note">Sin apoderado confirmado en el archivo</div></div></div>`;
  }).join('');
  $('#owners').innerHTML=`<p class="lede owners-intro">${esc(intro)}</p>`
    +`<div class="cards g2 owners-grid">${ownedCards}${unownedCards}</div>`;
}
/* ============================================================
   CONSULTA — the reason this archive exists rather than a wiki page

   Two ways in. The ask bar takes a question in plain Spanish and
   answers it with a number and the rows behind it. The query
   builder is the same data with the filters exposed, for when you
   already know what you want and would rather write it yourself.

   Every answer is computed from the local tables. Nothing is
   fetched, nothing is guessed, and every result exports to CSV.
   ============================================================ */

const ASK_EXAMPLES=[
  '¿Cuándo murió Piculín?',
  '¿Qué es un refuerzo?',
  '¿Quién fue Pachín Vicéns?',
  '¿De dónde era Fico López?',
  '¿Quién ganó en 1971?',
  'títulos de Bayamón',
  'campeones de los 70',
  'líder de anotación 1987',
  'máximo anotador de la historia',
  'Bayamón contra Ponce en finales',
  'posiciones 2026',
  'sequía de Mayagüez',
  'récord de puntos en un juego',
  'Georgie Torres'
];

function clubByText(t){
  const q=norm(t);
  if(!q) return null;
  let best=null,bl=0;
  FKEYS.forEach(k=>{
    const f=F[k];
    /* Abbreviations are 2-3 letters and would otherwise match inside
       unrelated words — "CON" inside "Conditt". Only whole words count. */
    const cands=[f.name,f.city,f.abbr,f.name.split(' de ')[0]];
    cands.forEach(c=>{
      const n=norm(c);
      if(n.length<3) return;
      const whole=new RegExp('(^|\\s)'+n.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'($|\\s)').test(q);
      const hit = n.length>=5 ? q.includes(n) : whole;
      if(hit && n.length>bl){best=k;bl=n.length;}
    });
  });
  return best;
}
function answerCard(o){
  const host=$('#askAnswer');
  host.innerHTML=`<div class="answer">
    <div class="ahead">
      <div class="aq">${esc(o.q||'Respuesta')}</div>
      <div class="abig">${o.big}</div>
      ${o.sub?`<div class="asub">${o.sub}</div>`:''}
    </div>
    <div class="abody" id="askBody"></div>
    ${o.foot?`<div class="afoot">${esc(o.foot)}</div>`:''}
  </div>`;
  if(o.table){
    const b=$('#askBody');
    buildTable(b,o.table.cols,o.table.rows,{file:o.table.file||'consulta',sort:o.table.sort,dir:o.table.dir});
    b.querySelector('.tblwrap').style.border='0';
    b.querySelector('.tblwrap').style.borderRadius='0';
    b.querySelector('.tblwrap').style.marginTop='0';
    b.querySelector('.tbl-meta').style.padding='var(--sp-2) var(--sp-4_5) var(--sp-3)';
    b.querySelector('.tbl-meta').style.marginTop='0';
  }
  if(o.chips){
    const c=el('div'); c.style.padding='0 var(--sp-4_5) var(--sp-3_5)';
    c.innerHTML='<div class="chips">'+o.chips+'</div>';
    $('#askBody').appendChild(c);
  }
}

/* Each matcher gets the normalised question and returns a card,
   or null to let the next one try. Order is deliberate: the most
   specific shapes are tested first. */

/* ============================================================
   BIO — quién fue cada quien

   Cada ficha lleva su fuente. Los campos que ninguna fuente
   consultada confirma quedan en null y se muestran como hueco: «no lo
   tengo» es una respuesta cierta, y una fecha inventada no lo es.

   `dis` marca los datos donde las fuentes se contradicen entre sí. No
   se escoge una y se calla la otra; se dicen las dos.
   ============================================================ */
const BIO=[
 {n:'José «Piculín» Ortiz', full:'José Rafael Ortiz Rijos',
  born:'1963-10-25', bornIn:'Aibonito', raised:'Cayey',
  died:'2026-05-05', diedIn:'San Juan',
  cause:'complicaciones de cáncer colorrectal, diagnosticado a finales de 2023',
  ht:'2.08 m', pos:'Pívot', nat:'Puerto Rico',
  nick:'«Piculín» se lo puso una vecina por travieso, de niño. «El Concorde» se lo puso el '
      +'narrador Manuel Rivera Morales, por la estatura.',
  life:'Cinco Copas del Mundo FIBA y cuatro Juegos Olímpicos (Seúl 1988, Barcelona 1992, '
      +'Atlanta 1996, Atenas 2004). Los Utah Jazz lo escogieron 15.º en el sorteo de 1987. '
      +'Jugó en el Real Madrid, el Barcelona y el Unicaja. Salón de la Fama de FIBA en 2019. '
      +'Su número 4 está retirado por Santurce y por la Selección Nacional.',
  src:'Wikipedia (es/en) · FIBA Hall of Fame · El Nuevo Día · EFE'},

 {n:'Georgie Torres', full:'Georgie Torres Dougherty',
  born:'1957-11-21', bornIn:'Camuy', raised:null,
  dis:'La ficha de Wikipedia dice 21 de noviembre de 1957; el texto del mismo artículo dice '
     +'21 de septiembre. El archivo no resuelve cuál es la correcta.',
  died:null, diedIn:null, cause:null,
  ht:'1.93 m', pos:'Escolta', nat:'Puerto Rico',
  nick:'«La Carabina», por la puntería.',
  life:'Máximo anotador en la historia del BSN con 15,863 puntos en 26 temporadas. Debutó con '
      +'Fajardo en 1975, el año que nació la franquicia. Siete veces campeón de anotación, tres '
      +'veces MVP. Anotó 989 triples sin que la línea existiera en sus primeros seis años. '
      +'Fajardo retiró su número 4 en 2022.',
  src:'Wikipedia · El Nuevo Día · Primera Hora'},

 {n:'Mario «Quijote» Morales', full:null,
  born:null, bornIn:null, raised:null, died:null, diedIn:null, cause:null,
  ht:null, pos:'Alero', nat:'Puerto Rico',
  nick:'«Quijote».',
  life:'Debutó en 1974 con Santurce, a los 17 años y todavía en escuela superior. Novato del '
      +'año en 1975. Cuatro veces MVP (1980, 1982, 1983, 1993), récord que comparte con Pachín '
      +'Vicéns y Teófilo Cruz. El coliseo de Guaynabo lleva su nombre. Fue cuñado de Fico López.',
  src:'Wikipedia'},

 {n:'Raymond Dalmau', full:'Raymond Dalmau Pérez',
  born:'1948-10-27', bornIn:'San Juan', raised:'Harlem, Nueva York',
  died:null, diedIn:null, cause:null,
  ht:'1.93 m', pos:'Ala-pívot', nat:'Puerto Rico',
  nick:null,
  life:'Sus padres se mudaron de Santurce a Harlem siendo él niño; volvió a Puerto Rico en 1966, '
      +'a los 17 años, reclutado como refuerzo por Quebradillas, y se quedó veinte temporadas. '
      +'Se retiró en 1985 siendo a la vez líder histórico en puntos, rebotes y asistencias. '
      +'Rechazó un contrato de los Utah Stars de la ABA en 1975 para no perder la elegibilidad '
      +'con la Selección. Le diagnosticaron cáncer de colon en 1993 y se recuperó. Sus tres '
      +'hijos —Christian, Richie y Ricardo— jugaron en el BSN.',
  src:'Wikipedia · Primera Hora'},

 {n:'Teófilo Cruz', full:'Teófilo Cruz',
  born:'1942-01-08', bornIn:'Santurce', raised:null,
  died:'2005-08-30', diedIn:'Trujillo Alto',
  cause:'complicaciones de varios derrames cerebrales',
  ht:'2.06 m', pos:'Pívot', nat:'Puerto Rico',
  nick:'«Teo».',
  life:'Veinticinco temporadas en el BSN y cuatro MVP. Miembro del Salón de la Fama de FIBA. '
      +'Los Lakers lo escogieron en la sexta ronda del sorteo de 1965. Jugó también en España '
      +'y en Bélgica.',
  src:'Wikipedia · ACB · EFE'},

 {n:'Juan «Pachín» Vicéns', full:'Juan Vicéns Sastre',
  born:'1934-09-07', bornIn:'Ciales', raised:'Ponce',
  died:'2007-02-18', diedIn:'Ponce', cause:'complicaciones de salud',
  ht:'1.75 m', pos:'Armador', nat:'Puerto Rico',
  nick:'«Pachín».',
  life:'En el Mundial de Chile en 1959 fue nombrado el Mejor Jugador del Mundo, promediando '
      +'19.8 puntos. Primer jugador del BSN en llegar a 5,000 puntos. Cuatro veces MVP '
      +'(1952, 1954, 1958, 1960) y siete campeonatos, todos con Ponce, donde jugó de 1950 a 1966. '
      +'Jugó en Kansas State bajo Tex Winter. El auditorio de Ponce lleva su nombre desde 1972.',
  src:'Wikipedia · Enciclopedia de Puerto Rico · bsnpr.com'},

 {n:'Rubén Rodríguez', full:'Rubén Rodríguez León',
  born:'1953-08-05', bornIn:'Nueva York', raised:null,
  died:null, diedIn:null, cause:null,
  ht:'2.04 m', pos:'Ala-pívot', nat:'Estados Unidos y Puerto Rico',
  nick:null,
  life:'Veintitrés temporadas en el BSN. Sus 380 rebotes de 1978 aguantaron treinta años. '
      +'Uno de «Los Tres Reyes» junto a Raymond Dalmau y Neftalí Rivera, los nuyoricans que '
      +'cambiaron la liga en los setenta. El coliseo de Bayamón lleva su nombre.',
  src:'Wikipedia (es/en) · Nuyorican Básquet'},

 {n:'Neftalí Rivera', full:'Neftalí Rivera Oliveras',
  born:'1948-11-03', bornIn:'Manhattan, Nueva York', raised:null,
  died:'2017-12-23', diedIn:'Hato Rey', cause:null,
  ht:'1.80 m', pos:'Escolta', nat:'Puerto Rico y Estados Unidos',
  nick:null,
  life:'El 22 de mayo de 1974 anotó 79 puntos contra Mayagüez, récord que sigue en pie. '
      +'Treinta y cuatro canastas de campo, todas de dos, y 52 puntos solo en la segunda mitad. '
      +'Dalmau anotó 30 esa misma noche. Novato del año en 1969 y MVP en 1973.',
  src:'Wikipedia'},

 {n:'Mario Butler', full:'Mario Alberto Butler Graham',
  born:'1957-01-15', bornIn:'Ciudad de Panamá, Panamá', raised:null,
  died:null, diedIn:null, cause:null,
  ht:'2.03 m', pos:'Pívot', nat:'Panamá',
  nick:null,
  life:'Líder histórico de rebotes del BSN con 8,236. Siete veces Jugador Defensivo del Año. '
      +'Aprendió a jugar en las calles de Ciudad de Panamá y llegó becado a Briar Cliff, en Iowa, '
      +'donde conoció a Rolando Frazer.',
  src:'Wikipedia'},

 {n:'Rolando Frazer', full:'Rolando Frazer Thorne',
  born:'1958-07-03', bornIn:'Ciudad de Panamá, Panamá', raised:null,
  died:null, diedIn:null, cause:null,
  ht:'2.01 m', pos:'Pívot', nat:'Panamá',
  nick:null,
  life:'Dos veces MVP del BSN (1981, 1987) y dos veces campeón de anotación. Los Indiana Pacers '
      +'lo escogieron en 1981 pero nunca jugó en la NBA. Casi toda su carrera en Aibonito.',
  src:'Wikipedia'},

 {n:'Christian Dalmau', full:null,
  born:null, bornIn:null, raised:null, died:null, diedIn:null, cause:null,
  ht:null, pos:'Armador', nat:'Puerto Rico',
  nick:null,
  life:'Segundo hijo de Raymond Dalmau. Miembro de la Selección que venció a Estados Unidos en '
      +'Atenas 2004. Jugó en Turquía, Polonia e Israel. Dirige a Bayamón.',
  src:'Wikipedia'},

 {n:'Pablo Alicea', full:null,
  born:'1963-07-07', bornIn:'Santurce', raised:null,
  died:null, diedIn:null, cause:null,
  ht:null, pos:'Armador', nat:'Puerto Rico',
  nick:null,
  life:'Repartió 25 asistencias en un juego de 1989, marca que aguantó hasta 2012. Compitió en '
      +'los Juegos Olímpicos de Atlanta 1996. Fue policía en Puerto Rico y después en Baltimore.',
  src:'Wikipedia'},

 {n:'Butch Lee', full:'Alfred «Butch» Lee Jr.',
  born:'1956-12-05', bornIn:'Santurce', raised:'El Bronx, Nueva York',
  died:null, diedIn:null, cause:null,
  ht:'1.83 m', pos:'Armador', nat:'Puerto Rico',
  nick:'«Butch».',
  life:'Primer puertorriqueño y primer latinoamericano de nacimiento en jugar en la NBA, tras '
      +'ser escogido 10.º en 1978. Ganó el anillo con los Lakers en 1980. Antes había sido '
      +'campeón de la NCAA con Marquette en 1977 y Jugador del Año en 1978. Se crió jugando en '
      +'Rucker Park.',
  src:'Wikipedia · Nuyorican Básquet'},

 {n:'Ángel Santiago', full:'Ángel Santiago del Valle',
  born:'1956-07-03', bornIn:'Río Piedras', raised:null,
  died:null, diedIn:null, cause:null,
  ht:null, pos:'Alero', nat:'Puerto Rico',
  nick:'«Cachorro».',
  life:'Entró al BSN en 1973 con Santurce y jugó más de veinte temporadas. Parte de la Selección '
      +'Nacional entre 1978 y 1987.',
  dis:'Las fuentes discrepan en el largo de la carrera: Wikipedia dice 24 temporadas, el Salón de '
     +'la Fama de Río Piedras dice 23.',
  src:'Wikipedia · Salón de la Fama del Deporte de Río Piedras'},

 {n:'Edgar de León', full:null,
  born:null, bornIn:null, raised:null, died:null, diedIn:null, cause:null,
  ht:null, pos:'Ala-pívot', nat:'Puerto Rico',
  nick:null,
  life:'Campeón de anotación en 1988 y 1990 con Fajardo. Octavo en rebotes de por vida en el BSN. '
      +'Jugó los Mundiales de 1986, 1990 y 1994 y los Juegos Olímpicos de 1988 y 1992.',
  src:'Wikipedia'},

 {n:'Federico «Fico» López', full:'Federico López Camacho',
  born:'1962-03-26', bornIn:'Ciudad de México, México', raised:'Guaynabo',
  died:'2006-11-06', diedIn:'Guaynabo',
  cause:'un aparente infarto, jugando voleibol con amigos en el Caparra Country Club',
  ht:'1.85 m', pos:'Armador', nat:'Puerto Rico',
  nick:'«Fico».',
  life:'Dieciséis temporadas, todas con los Mets de Guaynabo. Dos campeonatos (1982, 1989). '
      +'Nació en México pero representó a Puerto Rico en tres Mundiales y dos Juegos Olímpicos. '
      +'Los Mets retiraron su número 5. Murió a los 44 años en la cancha que lleva su nombre, '
      +'donde había empezado a jugar a los ocho.',
  src:'Wikipedia (es/en) · El Nuevo Día · El Vocero'},

 {n:'Jerome Mincy', full:'Jerome Alfred Mincy Clark',
  born:'1964-11-10', bornIn:'Base Ramey, Aguadilla', raised:'Memphis, Tennessee',
  died:null, diedIn:null, cause:null,
  ht:'1.98 m', pos:'Alero', nat:'Puerto Rico',
  nick:null,
  life:'Entró al BSN con Bayamón a los 18 años, en 1982, mientras estudiaba en UAB. Tres veces '
      +'campeón. Bayamón retiró su número 17 y UAB su número 40. Estuvo en la Selección de 1983 '
      +'a 2002.',
  src:'Wikipedia'}
];

/* Nombres alternos por los que la gente pregunta de verdad: apodos
   sueltos, apellidos, grafías sin acento. La búsqueda por nombre
   completo sola no encuentra «picu» ni «quijote». */
const BIO_ALIAS={
  'José «Piculín» Ortiz':['piculin','picu','jose ortiz','ortiz','el concorde','concorde'],
  'Georgie Torres':['georgie','torres','la carabina','carabina'],
  'Mario «Quijote» Morales':['quijote','mario morales','morales'],
  'Raymond Dalmau':['raymond dalmau','dalmau padre'],
  'Teófilo Cruz':['teo cruz','teofilo','teo'],
  'Juan «Pachín» Vicéns':['pachin','vicens','pachin vicens','juan vicens'],
  'Rubén Rodríguez':['ruben rodriguez'],
  'Neftalí Rivera':['neftali','neftali rivera'],
  'Mario Butler':['butler'],
  'Rolando Frazer':['frazer'],
  'Christian Dalmau':['christian dalmau'],
  'Pablo Alicea':['alicea'],
  'Butch Lee':['butch','alfred lee'],
  'Ángel Santiago':['cachorro','angel santiago','cachorro santiago'],
  'Edgar de León':['de leon','edgar leon'],
  'Federico «Fico» López':['fico','fico lopez','federico lopez'],
  'Jerome Mincy':['mincy']
};

const BIO_BY_NAME={};
BIO.forEach(b=>{ BIO_BY_NAME[b.n]=b; });

/* Longest match wins, so «raymond dalmau» does not get swallowed by
   «dalmau» pointing at his son. */
function bioByText(q){
  const s=norm(q);
  let best=null, bestLen=0;
  BIO.forEach(b=>{
    const keys=[norm(b.n)].concat((BIO_ALIAS[b.n]||[]).map(norm));
    keys.forEach(k=>{
      if(k.length>bestLen && s.indexOf(k)>=0){ best=b; bestLen=k.length; }
    });
  });
  return best;
}

function bioAge(b,onISO){
  if(!b.born) return null;
  const a=b.born.split('-').map(Number);
  const e=String(onISO).split('-').map(Number);
  if(a.length!==3||e.length!==3) return null;
  let age=e[0]-a[0];
  if(e[1]<a[1]||(e[1]===a[1]&&e[2]<a[2])) age--;
  return age>=0?age:null;
}
function bioShort(b){ return b.n.replace(/[«»]/g,''); }

/* Una sola tarjeta para todas las preguntas de vida, con el titular
   cambiado según lo que se preguntó. Los huecos se dicen. */
function bioCard(b,mode){
  const rows=[];
  const add=(k,v)=>rows.push([k, v==null||v===''?'—':v]);
  add('Nombre completo', b.full);
  add('Nacimiento', b.born?fmtLongDate(b.born)+(b.bornIn?' · '+b.bornIn:''):null);
  add('Criado en', b.raised);
  add('Fallecimiento', b.died?fmtLongDate(b.died)+(b.diedIn?' · '+b.diedIn:''):
      (b.born?'No consta. Hasta donde llega el archivo, vive.':null));
  add('Causa', b.cause);
  add('Posición', b.pos);
  add('Estatura', b.ht);
  add('Nacionalidad', b.nat);
  add('Apodo', b.nick);

  let big, sub;
  const short=bioShort(b);
  if(mode==='died'){
    if(b.died){
      const age=bioAge(b,b.died);
      big=fmtLongDate(b.died);
      sub=short+' murió en '+(b.diedIn||'un lugar que el archivo no registra')
         +(age!=null?', a los '+age+' años':'')+'.'+(b.cause?' Causa: '+b.cause+'.':'');
    }else{
      big='No consta que haya fallecido';
      sub='Ninguna fuente de este archivo registra una fecha de muerte para '+short
         +'. Eso no es lo mismo que confirmar que vive: es que el archivo no lo sabe.';
    }
  }else if(mode==='born'){
    if(b.born){
      big=fmtLongDate(b.born);
      sub=short+' nació en '+(b.bornIn||'un lugar que el archivo no registra')+'.'
         +(b.raised?' Se crió en '+b.raised+'.':'');
    }else{
      big='El archivo no tiene su fecha de nacimiento';
      sub='Ninguna fuente consultada la confirma, así que queda vacía en vez de inventada.';
    }
  }else if(mode==='age'){
    const ref=b.died||todayISO();
    const age=bioAge(b,ref);
    if(age==null){ big='El archivo no tiene su fecha de nacimiento'; sub='Sin ella no se puede calcular la edad.'; }
    else if(b.died){ big=age+' años'; sub='Es la edad que tenía al morir, el '+fmtLongDate(b.died)+'.'; }
    else { big=age+' años'; sub='Calculado a la fecha de hoy, a partir del '+fmtLongDate(b.born)+'.'; }
  }else if(mode==='where'){
    big=b.bornIn||'El archivo no lo registra';
    sub=b.bornIn?(short+' nació en '+b.bornIn+'.'+(b.raised?' Se crió en '+b.raised+'.':'')):
        'No hay lugar de nacimiento confirmado para '+short+'.';
  }else if(mode==='nick'){
    big=b.nick?bioShort(b):'Sin apodo registrado';
    sub=b.nick||('El archivo no guarda un apodo para '+short+'.');
  }else{
    big=short;
    sub=b.life||'';
  }

  return {q:mode==='who'?'Quién fue':'Ficha de '+short, big:esc(big), sub:esc(sub),
    table:{cols:[{label:'Dato'},{label:'Valor',wide:true}],rows:rows,file:'bio_'+slug(b.n),sort:null},
    chips:`<button class="chip" onclick="runAsk('${esc(short)}')">Ficha completa</button>`,
    foot:(b.dis?'Fuentes en conflicto: '+esc(b.dis)+' ':'')
        +(b.life&&mode!=='who'?esc(b.life)+' ':'')
        +'Fuentes: '+esc(b.src)+'.'};
}

const ASKERS=[
  /* glosario: qué significa esta palabra */
  q=>{
    if(!/que es|que significa|que quiere decir|definicion de|what is|explicame/.test(q)) return null;
    const g=glosByText(q); if(!g) return null;
    return {q:'Glosario', big:esc(g.t), sub:esc(g.d),
      chips:`<button class="chip" onclick="showView('archivo','glosario')">Ver el glosario completo</button>`};
  },
  /* fallecidos: la lista completa que el archivo sí puede dar */
  q=>{
    if(!/quien(es)? (ha|han) (muerto|fallecido)|jugadores fallecidos|fallecidos|quienes murieron|los que murieron/.test(q))
      return null;
    const rows=BIO.filter(b=>b.died).sort((a,b)=>a.died<b.died?1:-1)
      .map(b=>[bioShort(b), fmtLongDate(b.died), bioAge(b,b.died), b.diedIn||null]);
    return {q:'Fallecidos', big:rows.length+' de '+BIO.length+' fichas',
      sub:'El archivo tiene biografía de '+BIO.length+' jugadores. De esos, '+rows.length
         +' constan como fallecidos. De los demás no consta fecha de muerte, que no es lo mismo '
         +'que confirmar que viven.',
      table:{cols:[{label:'Jugador',wide:true},{label:'Fecha'},{label:'Edad',num:true},{label:'Lugar'}],
        rows:rows,file:'fallecidos',sort:null}};
  },
  /* vida: muerte, nacimiento, edad, origen, apodo, quién fue */
  q=>{
    const LIFE=/muri|murio|falleci|fallecio|deceso|muerte|sigue vivo|esta vivo|vive todavia|\bdie[ds]?\b|death|pass(ed)? away|nacio|nacimiento|cumpleanos|\bborn\b|que edad|cuantos anos|edad tiene|edad tenia|how old|de donde|donde nacio|natural de|apodo|por que le dicen|le decian|nickname|quien es|quien fue|quien era|who (is|was)|biografia/;
    const b=bioByText(q);
    if(!b){
      /* Sin ficha no se contesta con otra cosa. Antes esto caía al buscador
         de jugadores, que emparejaba un nombre de pila y respondía una
         pregunta sobre la muerte de alguien con su línea de estadísticas.
         Contestar la pregunta equivocada con seguridad es peor que no
         contestar. */
      if(!LIFE.test(q)) return null;
      return {q:'Sin biografía', big:'El archivo no tiene esa ficha',
        sub:'Es una pregunta de vida, y solo hay biografía verificada de '+BIO.length
           +' jugadores. Para el resto hay estadísticas, pero no fechas ni datos personales.',
        table:{cols:[{label:'Con ficha biográfica',wide:true},{label:'Años'}],
          rows:BIO.map(x=>[bioShort(x),(x.born?x.born.slice(0,4):'?')+(x.died?'–'+x.died.slice(0,4):'')]),
          file:'con_biografia',sort:null},
        foot:'Buscar estadísticas de un jugador sí funciona: escribe solo su nombre.'};
    }
    if(/muri|murio|falleci|fallecio|deceso|muerte|sigue vivo|esta vivo|vive todavia|\bdie[ds]?\b|death|pass(ed)? away/.test(q))
      return bioCard(b,'died');
    if(/nacio|nacimiento|cumpleanos|fecha de nacimiento|born/.test(q)) return bioCard(b,'born');
    if(/que edad|cuantos anos|edad tiene|edad tenia|how old/.test(q)) return bioCard(b,'age');
    if(/de donde|donde nacio|pueblo de|natural de|origen/.test(q)) return bioCard(b,'where');
    if(/apodo|por que le dicen|le decian|nickname|le llaman/.test(q)) return bioCard(b,'nick');
    if(/quien es|quien fue|quien era|who is|who was|biografia|ficha de/.test(q)) return bioCard(b,'who');
    return null;
  },
  /* season → champion */
  q=>{
    const m=q.match(/\b(19[3-9]\d|20[0-2]\d)\b/);
    if(!m) return null;
    if(!/gan|campe|final|quien|quién|titul|de\s+19|de\s+20|^\s*(19|20)/.test(q) && !/^\s*(19|20)\d\d\s*$/.test(q)) return null;
    const y=+m[1];
    if(y>LAST) return {q:'Temporada '+y,big:'Todavía no se ha jugado',sub:'El archivo llega hasta 2026.'};
    const k=champOf[y], r=ruOf[y];
    if(!k) return {q:'Temporada '+y,big:'Sin campeón registrado',
      sub:esc(NOTES[y]||'Ninguna fuente consultada nombra un campeón para este año.'),
      foot:'Este es un hueco documentado, no un dato que falte por error.'};
    const f=F[k];
    const nth=f.won.indexOf(y)+1;
    return {q:'Campeón '+y, big:esc(f.name),
      sub:(r?'Venció a '+esc(F[r].name)+'. ':'')+`Fue su título número ${nth} de ${f.won.length}.`,
      chips:`<button class="chip" onclick="showTeam('${k}')">Ver ${esc(f.name.split(' de ')[0])}</button>`+
            `<button class="chip" onclick="showSeason(${y})">Ver en la cinta</button>`,
      foot:NOTES[y]||''};
  },
  /* decade */
  q=>{
    const m=q.match(/\b(?:los\s+)?(\d0)s?\b/) || q.match(/d[eé]cada\s+(?:de\s+)?(?:los\s+)?(\d{2,4})/);
    if(!m || !/decada|década|los\s+\d0|a[ñn]os\s+\d0/.test(q)) return null;
    let d=+m[1]; if(d<100) d = d>=30 ? 1900+d : 2000+d;
    d=Math.floor(d/10)*10;
    const rows=YEARS.filter(y=>y>=d&&y<d+10&&champOf[y]).map(y=>[y,F[champOf[y]].name,ruOf[y]?F[ruOf[y]].name:null]);
    if(!rows.length) return null;
    const tally={};rows.forEach(r=>tally[r[1]]=(tally[r[1]]||0)+1);
    const top=Object.keys(tally).sort((a,b)=>tally[b]-tally[a])[0];
    return {q:'Campeones de los '+d,big:esc(top),
      sub:`Ganó ${tally[top]} de los ${rows.length} títulos de la década.`,
      table:{cols:[{label:'Año',num:true},{label:'Campeón',wide:true},{label:'Subcampeón',wide:true}],
        rows,file:'campeones_'+d,sort:0,dir:1}};
  },
  /* titles / droughts for a club */
  q=>{
    if(!/titul|campeonat|sequ|cuantos|cuántos|gan/.test(q)) return null;
    const k=clubByText(q); if(!k) return null;
    const f=F[k];
    const last=f.won.length?Math.max.apply(null,f.won):null;
    if(/sequ/.test(q)){
      return {q:'Sequía de '+f.name.split(' de ')[0],
        big:last?(LAST-last===0?'Campeón vigente':(LAST-last)+' años'):'Nunca ha ganado',
        sub:last?`Su último título fue en ${last}. Ha jugado ${f.ru.length} finales perdidas.`:
          `${f.ru.length} finales jugadas, ninguna ganada.`};
    }
    return {q:'Títulos de '+f.name.split(' de ')[0],
      big:f.won.length+(f.won.length===1?' título':' títulos'),
      sub:f.won.length?`${f.won.join(', ')}. Además ${f.ru.length} finales perdidas.`:`Sin títulos. ${f.ru.length} finales perdidas.`,
      table:f.won.length?{cols:[{label:'Año',num:true},{label:'Venció a',wide:true}],
        rows:f.won.map(y=>[y,ruOf[y]?F[ruOf[y]].name:null]),file:'titulos_'+k,sort:0,dir:-1}:null,
      chips:`<button class="chip" onclick="showTeam('${k}')">Ficha completa</button>`};
  },
  /* head to head in finals */
  q=>{
    if(!/(vs|contra|frente|cara)/.test(q)) return null;
    const parts=q.split(/\s+(?:vs|contra|frente a|cara a cara con)\s+/);
    if(parts.length<2) return null;
    const a=clubByText(parts[0]), b=clubByText(parts[1]);
    if(!a||!b||a===b) return null;
    const aw=F[a].won.filter(y=>ruOf[y]===b), bw=F[b].won.filter(y=>ruOf[y]===a);
    const rows=aw.map(y=>[y,F[a].name,F[b].name]).concat(bw.map(y=>[y,F[b].name,F[a].name])).sort((x,y)=>x[0]-y[0]);
    return {q:'Finales entre ambos',
      big:`${F[a].abbr} ${aw.length} — ${bw.length} ${F[b].abbr}`,
      sub:rows.length?`Se han encontrado ${rows.length} veces en una final.`:'Nunca se han enfrentado en una final.',
      table:rows.length?{cols:[{label:'Año',num:true},{label:'Ganó',wide:true},{label:'Perdió',wide:true}],
        rows,file:'h2h',sort:0,dir:-1}:null};
  },
  /* MVP by year */
  q=>{
    if(!/mvp|mas valioso|más valioso|valioso/.test(q)) return null;
    const m=q.match(/\b(19\d\d|20\d\d)\b/);
    if(m){
      const y=+m[1], r=MVP_YEARS.find(x=>x[0]===y);
      if(!r) return {q:'MVP '+y,big:'No está en el archivo',
        sub:'Solo se recuperaron los ganadores repetidos y las temporadas con página propia. Ver «El archivo».',
        foot:'Hueco conocido.'};
      return {q:'Más Valioso '+y,big:esc(r[1]),sub:esc(r[2]),
        chips:`<button class="chip" onclick="showPlayer(${JSON.stringify(r[1]).replace(/"/g,'&quot;')})">Ficha</button>`};
    }
    const tally={}; MVP_YEARS.forEach(r=>tally[r[1]]=(tally[r[1]]||0)+1);
    const top=Object.keys(tally).sort((a,b)=>tally[b]-tally[a]);
    return {q:'MVP del BSN',big:esc(top[0]),sub:`${tally[top[0]]} premios en el archivo. Se han recuperado ${MVP_YEARS.length} temporadas.`,
      table:{cols:[{label:'Año',num:true},{label:'Jugador',wide:true},{label:'Club',wide:true}],
        rows:MVP_YEARS.map(r=>[r[0],r[1],r[2]]),file:'mvp',sort:0,dir:-1}};
  },
  /* scoring champion by year */
  q=>{
    if(!/anotaci|anotador|puntos/.test(q)) return null;
    const m=q.match(/\b(19\d\d|20\d\d)\b/);
    if(m){
      const y=+m[1];
      const s=SCORING.find(x=>x[0]===y);
      if(!s) return {q:'Campeón de anotación '+y,big:'No está en el archivo',
        sub:'Solo se han bajado los años 1966–1991. Los tramos 1956–65 y 1992 en adelante están en la misma tabla de Wikipedia, sin bajar.',
        foot:'Hueco conocido, listado en «El archivo».'};
      return {q:'Campeón de anotación '+y,big:esc(s[1]),
        sub:`${esc(s[2])} · ${s[4]} ${s[3]==='ppg'?'por juego':'puntos en total'}`,
        chips:`<button class="chip" onclick="showPlayer(${JSON.stringify(s[1]).replace(/"/g,'&quot;')})">Ficha</button>`};
    }
    if(/maxim|máxim|historia|carrera|todos los tiempos|all.?time|mas puntos|más puntos/.test(q)){
      const l=LEADERS.points;
      return {q:'Máximo anotador de la historia',big:esc(l[0][1]),
        sub:`${l[0][4].toLocaleString('es-PR')} puntos en ${l[0][5]} juegos — ${l[0][6]} por juego, entre ${esc(l[0][3])}.`,
        table:{cols:[{label:'#',num:true},{label:'Jugador',wide:true},{label:'Puntos',num:true},{label:'PJ',num:true},{label:'PPJ',num:true}],
          rows:l.map(r=>[r[0],r[1],r[4],r[5],r[6]]),file:'lideres_puntos',sort:2,dir:-1}};
    }
    return null;
  },
  /* career leaders by category */
  q=>{
    let cat=null;
    if(/rebot/.test(q))cat='rebounds'; else if(/asistenc/.test(q))cat='assists';
    else if(/(lider|líder|maxim|máxim).*(punto|anota)/.test(q))cat='points';
    if(!cat) return null;
    const l=LEADERS[cat], label={points:'puntos',rebounds:'rebotes',assists:'asistencias'}[cat];
    return {q:'Líder de '+label+' de carrera',big:esc(l[0][1]),
      sub:`${l[0][4].toLocaleString('es-PR')} ${label} en ${l[0][5]} juegos.`,
      table:{cols:[{label:'#',num:true},{label:'Jugador',wide:true},{label:'Total',num:true},{label:'PJ',num:true},{label:'Por juego',num:true}],
        rows:l.map(r=>[r[0],r[1],r[4],r[5],r[6]]),file:'lideres_'+cat,sort:2,dir:-1}};
  },
  /* standings */
  q=>{
    if(!/posicion|tabla|standing|record.*2026|2026.*record/.test(q)) return null;
    const rows=[];
    ['A','B'].forEach(g=>STAND2026[g].forEach((r,i)=>rows.push([g,i+1,F[r[0]].name,r[1],r[2],r[3],r[4],r[5]])));
    return {q:'Posiciones 2026',big:'Bayamón y Caguas, 22-12',
      sub:'Los dos mejores récords de la liga terminaron empatados en el Grupo A. Bayamón ganó el título; Caguas cayó en la final de conferencia ante Bayamón.',
      table:{cols:[{label:'Gr.'},{label:'Pos',num:true},{label:'Equipo',wide:true},{label:'PG',num:true},
        {label:'PP',num:true},{label:'PCT',num:true},{label:'Local'},{label:'Visita'}],
        rows,file:'posiciones_2026',sort:null}};
  },
  /* records */
  q=>{
    if(!/record|récord|marca|mas puntos en un juego|más puntos en un juego/.test(q)) return null;
    let rows=RECORDS;
    if(/asistenc/.test(q)) rows=RECORDS.filter(r=>/sisten/.test(r[0]));
    else if(/rebot/.test(q)) rows=RECORDS.filter(r=>/ebound|ebot/.test(r[0]));
    else if(/punto/.test(q)) rows=RECORDS.filter(r=>/oint|unto/.test(r[0]));
    else if(/asisten|publico|público|asistencia de/.test(q)) rows=RECORDS.filter(r=>/ttendance/.test(r[0]));
    if(!rows.length) rows=RECORDS;
    return {q:'Récords de la liga',big:esc(rows[0][1])+' — '+esc(rows[0][0]),
      sub:esc(rows[0][2])+' ('+rows[0][3]+'). '+esc(rows[0][4]||''),
      table:{cols:[{label:'Récord',wide:true},{label:'Marca'},{label:'Quién',wide:true},{label:'Año',num:true}],
        rows:RECORDS.map(r=>[r[0],r[1],r[2],r[3]]),file:'records',sort:null}};
  },
  /* player lookup */
  q=>{
    buildPlayerIndex();
    let best=null,bl=0;
    PINDEX.forEach(p=>{
      const n=norm(p.name);
      /* Match both directions: the question may name him in full,
         or give a shorter form of a longer registered name. */
      if(q.includes(n) && n.length>bl){best=p;bl=n.length;}
      else if(q.length>=6 && n.includes(q) && q.length>bl){best=p;bl=q.length;}
      const parts=n.split(' ').filter(x=>x.length>4);
      parts.forEach(sn=>{ if(q.includes(sn) && sn.length>bl){best=p;bl=sn.length;} });
    });
    if(!best) return null;
    return {q:'Jugador',big:esc(best.name),
      sub:esc([best.pos,best.years].filter(Boolean).join(' · '))+(best.bio?' — '+esc(best.bio):''),
      table:{cols:[{label:'Dato'},{label:'Valor',num:true}],
        rows:[['Puntos',best.pts],['Rebotes',best.reb],['Asistencias',best.ast],['Juegos',best.gp],
              ['Puntos por juego',best.ppg],['MVP',best.mvp||null]],file:'jugador',sort:null},
      chips:`<button class="chip" onclick="showPlayer(${JSON.stringify(best.name).replace(/"/g,'&quot;')})">Ficha completa</button>`};
  },
  /* club fallback */
  q=>{
    const k=clubByText(q); if(!k) return null;
    const f=F[k];
    return {q:'Franquicia',big:esc(f.name),
      sub:`${f.city} · desde ${f.founded} · ${f.won.length} títulos, ${f.ru.length} finales perdidas.`,
      chips:`<button class="chip" onclick="showTeam('${k}')">Ficha completa</button>`};
  }
];

function ask(qraw){
  const q=norm(qraw);
  if(!q){ $('#askAnswer').innerHTML=''; return; }
  for(const fn of ASKERS){
    let r=null;
    try{ r=fn(q); }catch(e){ r=null; }
    if(r){ answerCard(r); return; }
  }
  /* fallback: fuzzy search across everything the archive names */
  buildPlayerIndex();
  const hits=[];
  YEARS.forEach(y=>{ if(String(y).includes(q)) hits.push(['Temporada',String(y),champOf[y]?F[champOf[y]].name:'sin campeón',()=>showSeason(y)]); });
  FKEYS.forEach(k=>{ if(norm(F[k].name+' '+F[k].city).includes(q)) hits.push(['Club',F[k].name,F[k].won.length+' títulos',()=>showTeam(k)]); });
  PINDEX.forEach(p=>{ if(norm(p.name).includes(q)) hits.push(['Jugador',p.name,Array.from(p.tags).slice(0,2).join(' · '),()=>showPlayer(p.name)]); });
  BIO.forEach(b=>{ if(norm(b.n).includes(q)) hits.push(['Biografía',bioShort(b),
    (b.born?b.born.slice(0,4):'?')+(b.died?'–'+b.died.slice(0,4):''),()=>runAsk('quién fue '+bioShort(b))]); });
  if(!hits.length){
    /* Antes esto era un callejón sin salida. Si la pregunta menciona a
       alguien con ficha, o suena a pregunta de vida, hay que decir qué
       sí se puede preguntar en vez de cerrar la puerta. */
    const b=bioByText(q);
    if(b) return answerCard(bioCard(b,'who'));
    const lifeish=/muri|falleci|nacio|edad|apodo|quien es|quien fue|de donde/.test(q);
    answerCard({q:'Sin resultado',big:'El archivo no tiene eso',
      sub:lifeish
        ? 'Parece una pregunta de vida, pero ese nombre no tiene ficha aquí. Hay biografía de '
          +BIO.length+' jugadores, casi todos del Salón de la Fama.'
        : 'Prueba con un año, un club, un jugador, o toca uno de los ejemplos de arriba.',
      table:lifeish?{cols:[{label:'Con ficha biográfica',wide:true},{label:'Años'}],
        rows:BIO.map(x=>[bioShort(x),(x.born?x.born.slice(0,4):'?')+(x.died?'–'+x.died.slice(0,4):'')]),
        file:'con_biografia',sort:null}:null,
      foot:'La consulta funciona sobre datos locales: campeones, franquicias, líderes, récords, '
          +'anotación, biografías y la temporada 2026.'});
    return;
  }
  answerCard({q:'Coincidencias',big:hits.length+(hits.length===1?' resultado':' resultados'),
    sub:'La pregunta no encajó en ningún patrón, así que se buscó por nombre.',
    table:{cols:[{label:'Tipo'},{label:'Nombre',wide:true},{label:'Detalle',wide:true}],
      rows:hits.slice(0,40).map(h=>[h[0],h[1],h[2]]),file:'busqueda',sort:null}});
}
function buildAsk(){
  $('#askChips').innerHTML=ASK_EXAMPLES.map(e=>
    `<button class="chip" onclick="runAsk(${JSON.stringify(e).replace(/"/g,'&quot;')})">${esc(e)}</button>`).join('');
  const inp=$('#askInput');
  let t=null;
  inp.oninput=()=>{clearTimeout(t);t=setTimeout(()=>ask(inp.value),220);};
  inp.onkeydown=e=>{if(e.key==='Enter'){clearTimeout(t);ask(inp.value);}};
}
function runAsk(q){ $('#askInput').value=q; ask(q); revealNode($('#askAnswer')); $('#askAnswer').scrollIntoView({block:'nearest',behavior:'smooth'}); }

/* ============================================================
   QUERY BUILDER
   ============================================================ */
const DATASETS={
  temporadas:{
    label:'Temporadas (1930–2026)',
    cols:[{label:'Año',num:true},{label:'Campeón',wide:true},{label:'Subcampeón',wide:true},
          {label:'Década',num:true},{label:'Nota',wide:true}],
    rows:()=>YEARS.map(y=>[y,champOf[y]?F[champOf[y]].name:null,ruOf[y]?F[ruOf[y]].name:null,
      Math.floor(y/10)*10,NOTES[y]||'']),
    yearCol:0, clubCols:[1,2]
  },
  franquicias:{
    label:'Franquicias (32)',
    cols:[{label:'Franquicia',wide:true},{label:'Ciudad'},{label:'Fundada',num:true},{label:'Estado'},
          {label:'Títulos',num:true},{label:'Finales perdidas',num:true},{label:'Finales',num:true},
          {label:'% en finales',num:true},{label:'Último título',num:true}],
    rows:()=>FKEYS.map(k=>{
      const f=F[k], fin=f.won.length+f.ru.length;
      return [f.name,f.city,f.founded,f.active?'activa':'desaparecida',f.won.length,f.ru.length,fin,
        fin?Math.round(f.won.length/fin*100):null, f.won.length?Math.max.apply(null,f.won):null];
    }),
    yearCol:2, clubCols:[0]
  },
  lideres:{
    label:'Líderes de carrera (30)',
    cols:[{label:'Categoría'},{label:'#',num:true},{label:'Jugador',wide:true},{label:'Pos'},
          {label:'Años'},{label:'Total',num:true},{label:'Juegos',num:true},{label:'Por juego',num:true}],
    rows:()=>{
      const out=[];
      [['points','Puntos'],['rebounds','Rebotes'],['assists','Asistencias']].forEach(([k,lab])=>
        LEADERS[k].forEach(r=>out.push([lab,r[0],r[1],r[2],r[3],r[4],r[5],r[6]])));
      return out;
    }
  },
  anotacion:{
    get label(){ return 'Campeones de anotación ('+(SCORING.length?SCORING[0][0]+'–'+SCORING[SCORING.length-1][0]:'')+')'; },
    cols:[{label:'Año',num:true},
      {label:'Jugador',wide:true,render:(v,r)=>r[5]!=null
        ? `<button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showPlayer(${JSON.stringify(v).replace(/"/g,'&quot;')},${r[5]})">${esc(v)}</button>`
        : esc(v)},
      {label:'Club',wide:true},{label:'Métrica'},{label:'Valor',num:true}],
    rows:()=>SCORING.map(s=>[s[0],s[1],s[2],s[3]==='ppg'?'promedio':'total',s[4],s[5]!=null?s[5]:null]),
    yearCol:0, clubCols:[2]
  },
  records:{
    label:'Récords de la liga (11)',
    cols:[{label:'Récord',wide:true},{label:'Marca'},{label:'Quién',wide:true},{label:'Año',num:true},{label:'Contexto',wide:true}],
    rows:()=>RECORDS.map(r=>[r[0],r[1],r[2],r[3],r[4]]),
    yearCol:3
  },
  posiciones2026:{
    label:'Posiciones 2026',
    cols:[{label:'Grupo'},{label:'Pos',num:true},{label:'Equipo',wide:true},{label:'PG',num:true},
          {label:'PP',num:true},{label:'PCT',num:true},{label:'Dif. juegos',num:true},{label:'Local'},{label:'Visita'}],
    rows:()=>{
      const out=[];
      ['A','B'].forEach(g=>{
        const tw=STAND2026[g][0][1], tl=STAND2026[g][0][2];
        STAND2026[g].forEach((r,i)=>out.push([g,i+1,F[r[0]].name,r[1],r[2],r[3],((tw-r[1])+(r[2]-tl))/2,r[4],r[5]]));
      });
      return out;
    },
    clubCols:[2]
  },
  final2026:{
    label:'La Final Brava 2026',
    cols:[{label:'Juego',num:true},{label:'Fecha'},{label:'Local',wide:true},{label:'Visita',wide:true},
          {label:'Pts local',num:true},{label:'Pts visita',num:true},{label:'Margen',num:true},{label:'Serie'}],
    rows:()=>FINALS_2026.games.map(g=>[g[0],g[1],F[g[2]].name,F[g[3]].name,g[4],g[5],Math.abs(g[4]-g[5]),g[6]]),
    clubCols:[2,3]
  },
  jugadores:{
    label:'Índice de jugadores',
    cols:[{label:'Jugador',wide:true},{label:'Pos'},{label:'Años'},{label:'Clubes'},
          {label:'Puntos',num:true},{label:'Rebotes',num:true},{label:'Asistencias',num:true},
          {label:'Juegos',num:true},{label:'MVP',num:true}],
    rows:()=>{buildPlayerIndex();return PINDEX.map(p=>[p.name,p.pos,p.years,
      Array.from(p.clubs).map(c=>F[c].abbr).join(' '),p.pts,p.reb,p.ast,p.gp,p.mvp||null]);}
  },
  mvp:{
    label:'MVP por año (39 recuperados)',
    cols:[{label:'Año',num:true},{label:'Jugador',wide:true},{label:'Club',wide:true},{label:'Década',num:true}],
    rows:()=>MVP_YEARS.map(r=>[r[0],r[1],r[2],Math.floor(r[0]/10)*10]),
    yearCol:0, clubCols:[2]
  },
  premios:{
    label:'Premios por temporada',
    cols:[{label:'Año',num:true},{label:'Premio'},{label:'Jugador',wide:true},{label:'Club',wide:true},{label:'Línea',wide:true}],
    rows:()=>SEASON_AWARDS.map(r=>[r[0],r[1],r[2],r[3],r[4]]),
    yearCol:0, clubCols:[3]
  },
  finales:{
    label:'Finales juego a juego (2024, 2025, 2026)',
    cols:[{label:'Año',num:true},{label:'Juego',num:true},{label:'Fecha'},{label:'Local',wide:true},
          {label:'Visita',wide:true},{label:'Pts local',num:true},{label:'Pts visita',num:true},
          {label:'Margen',num:true},{label:'Serie'}],
    rows:()=>{const out=[];Object.keys(FINALS_BY_YEAR).forEach(y=>FINALS_BY_YEAR[y].games.forEach(g=>
      out.push([+y,g[0],g[1],F[g[2]].name,F[g[3]].name,g[4],g[5],Math.abs(g[4]-g[5]),g[6]])));return out;},
    yearCol:0, clubCols:[3,4]
  },
  premios2026:{
    label:'Premios 2026',
    cols:[{label:'Premio'},{label:'Jugador',wide:true},{label:'Club',wide:true},{label:'Nota',wide:true}],
    rows:()=>AWARDS_2026.map(a=>[a[0],a[1],a[2],a[3]])
  }
};
let QB={ds:'temporadas',q:'',from:'',to:'',club:'',limit:''};
function buildQB(){
  $('#qbControls').innerHTML=`<div class="filters">
    <div class="field" style="min-width:200px"><label for="qbds">Tabla</label><select id="qbds">
      ${Object.keys(DATASETS).map(k=>`<option value="${k}">${esc(DATASETS[k].label)}</option>`).join('')}</select></div>
    <div class="field" style="min-width:170px"><label for="qbq">Contiene</label>
      <input type="search" id="qbq" placeholder="texto libre"></div>
    <div class="field" style="max-width:104px"><label for="qbfrom">Desde</label>
      <input type="text" id="qbfrom" inputmode="numeric" placeholder="1930"></div>
    <div class="field" style="max-width:104px"><label for="qbto">Hasta</label>
      <input type="text" id="qbto" inputmode="numeric" placeholder="2026"></div>
    <div class="field" style="min-width:170px"><label for="qbclub">Franquicia</label><select id="qbclub">
      <option value="">Todas</option>${FKEYS.slice().sort((a,b)=>F[a].name.localeCompare(F[b].name,'es'))
        .map(k=>`<option value="${k}">${esc(F[k].name)}</option>`).join('')}</select></div>
    <div class="field" style="max-width:104px"><label for="qblim">Límite</label>
      <input type="text" id="qblim" inputmode="numeric" placeholder="todo"></div>
  </div>
  <div class="btnrow">
    <button class="btn primary" onclick="runQB()">Ejecutar</button>
    <button class="btn" onclick="resetQB()">Limpiar</button>
    <button class="btn" onclick="copyQB()">Copiar como tabla</button>
  </div>
  <div id="qbSql" class="note" style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace"></div>`;
  ['qbds','qbq','qbfrom','qbto','qbclub','qblim'].forEach(id=>{
    const n=$('#'+id);
    n.addEventListener(id==='qbds'||id==='qbclub'?'change':'input',runQB);
  });
  runQB();
}
function resetQB(){
  ['qbq','qbfrom','qbto','qblim'].forEach(id=>$('#'+id).value='');
  $('#qbclub').value=''; runQB();
}
let QB_LAST={cols:[],rows:[]};
function runQB(){
  const key=$('#qbds').value, d=DATASETS[key];
  const q=norm($('#qbq').value), from=parseInt($('#qbfrom').value,10), to=parseInt($('#qbto').value,10);
  const club=$('#qbclub').value, lim=parseInt($('#qblim').value,10);
  let rows=d.rows();
  if(d.yearCol!=null){
    if(!isNaN(from)) rows=rows.filter(r=>r[d.yearCol]==null||r[d.yearCol]>=from);
    if(!isNaN(to))   rows=rows.filter(r=>r[d.yearCol]==null||r[d.yearCol]<=to);
  }
  if(club && d.clubCols) rows=rows.filter(r=>d.clubCols.some(c=>norm(String(r[c]||'')).includes(norm(F[club].name))));
  else if(club && !d.clubCols) rows=rows.filter(r=>norm(r.join(' ')).includes(norm(F[club].name)));
  if(q) rows=rows.filter(r=>norm(r.map(v=>v==null?'':v).join(' ')).includes(q));
  if(!isNaN(lim)&&lim>0) rows=rows.slice(0,lim);
  QB_LAST={cols:d.cols,rows};
  buildTable($('#qbResult'),d.cols,rows,{file:'bsn_'+key,sort:d.yearCol!=null?d.yearCol:null,dir:-1});
  /* The SQL echo is not decoration: it is the same query written
     the way an analyst would check it. */
  const where=[];
  if(d.yearCol!=null&&!isNaN(from))where.push(`${slug(d.cols[d.yearCol].label)} >= ${from}`);
  if(d.yearCol!=null&&!isNaN(to))where.push(`${slug(d.cols[d.yearCol].label)} <= ${to}`);
  if(club)where.push(`franquicia = '${F[club].name}'`);
  if(q)where.push(`texto LIKE '%${$('#qbq').value}%'`);
  $('#qbSql').textContent='SELECT * FROM '+key+(where.length?' WHERE '+where.join(' AND '):'')+
    (!isNaN(lim)&&lim>0?' LIMIT '+lim:'')+';   -- '+rows.length+' fila'+(rows.length===1?'':'s');
}
function copyQB(){
  const txt=[QB_LAST.cols.map(c=>c.label).join('\t')]
    .concat(QB_LAST.rows.map(r=>r.map(v=>v==null?'':v).join('\t'))).join('\n');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(()=>{
      const n=$('#qbSql'); const old=n.textContent;
      n.textContent='Copiado — pégalo directo en Excel o Sheets.';
      setTimeout(()=>{n.textContent=old;},1800);
    });
  }
}
function buildCoverage(){
  $('#coverage').innerHTML='<div class="covergrid">'+COVERAGE.map(c=>`
    <div class="cov"><div class="cy">${esc(c[0])}</div>
    <div class="cb"><div class="cf" style="width:${c[1]}%;background:${c[1]>60?'var(--ok)':c[1]>40?'var(--azul)':'var(--rojo)'}"></div></div>
    <div class="cl">${esc(c[2])}</div></div>`).join('')+'</div>'+
    '<p class="note">El porcentaje es cuánto de lo que uno querría saber de esa década está en el archivo, no una medida de exactitud. Los años treinta son el 20% porque solo hay campeones.</p>';
}

/* ============================================================
   HUB — the landing

   Thirteen sections arrived as one scroll. The hub makes arriving a
   choice: one card per destination, each showing a number computed
   from the archive rather than a static label, so the front page is
   worth reading even if you go no further.
   ============================================================ */


function hubAsk(e){
  if(e.key!=='Enter') return;
  const v=$('#hubSearch').value.trim();
  if(!v) return;
  showView('archivo','preguntar');
  runAsk(v);
}

/* one editorial block: eyebrow · headline stat + visual · phrase · context · action.
   PHASE_2_REDESIGN step 2: o.lead's own stat (the one full-width featured card per
   hub render -- "18 títulos de Bayamón" today) gets the solid tricolor-block treatment;
   every other (non-lead) stat tile in the grid is untouched, so this stays one real
   spot, not every card on the page. */
function edBlock(o){
  const stat = (o.stat!=null && o.stat!=='')
    ? `<div class="ed-stat${o.lead?' tri-block tri-block-rojo':''}">${esc(String(o.stat))}</div>` : '';
  const viz  = o.viz ? `<span class="ed-viz">${o.viz}</span>` : '';
  /* PHASE_9 hub restyle (owner-approved, redesign-v2): o.icon is one of TABS' own path strings
     (web/js/tabs.js, same array buildNav() reads) -- reusing the rail's own icon set, not new
     SVGs, so a card's glyph matches the rail tab a visitor already sees for that same section.
     Optional: the one hub card with no rail equivalent (Comparar, a Jugadores sub-view, not a
     top-level tab) renders with no icon rather than an invented one.
     PHASE_9 alignment fix (owner-approved, redesign-v2): an icon-less card used to render NO
     first child at all, so its .ed-eye sat 46px higher than its row-mates' (the icon box's own
     38px height plus the .ed flex container's 8px gap -- found live, not assumed: measured
     against the actual .ed-icon height and .ed's own `gap` computed style, and 38+8 is exactly
     the measured 46px). Fixed by always reserving the same box, empty when there's no icon --
     .ed-icon-empty overrides only the background (transparent), keeping width/height/radius
     identical, so the layout footprint matches exactly with nothing painted inside it. */
  const icon = o.icon
    ? `<div class="ed-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${o.icon}" stroke-linecap="round" stroke-linejoin="round"/></svg></div>`
    : '<div class="ed-icon ed-icon-empty" aria-hidden="true"></div>';
  return `<button class="ed${o.lead?' ed-lead':''}" onclick="${o.go}">
    <span class="ed-go" aria-hidden="true">→</span>
    ${icon}
    <div class="ed-eye">${esc(o.eye)}</div>
    ${(stat||viz)?`<div class="ed-row">${stat}${viz}</div>`:''}
    <div class="ed-phrase">${esc(o.phrase)}</div>
    <div class="ed-ctx">${esc(o.ctx)}</div>
    <span class="ed-act">${esc(o.act)} <span aria-hidden="true">→</span></span>
  </button>`;
}
function cmpMiniViz(a,b){
  if(!PINDEX) return '';
  const pa=PINDEX.find(p=>norm(p.name)===norm(a)), pb=PINDEX.find(p=>norm(p.name)===norm(b));
  if(!pa||!pb||pa.pts==null||pb.pts==null) return '';
  const mx=Math.max(pa.pts,pb.pts)||1;
  const bar=(v,c)=>`<i><b style="width:${Math.round(v/mx*100)}%;background:${c}"></b></i>`;
  return `<span class="ed-cmp">${bar(pa.pts,'var(--azul)')}${bar(pb.pts,'var(--rojo)')}</span>`;
}

function buildHub(){
  const pr=prof();
  const club=pr.club, f=club&&F[club]?F[club]:null;
  const cn = f ? f.name.split(' de ')[0] : null;

  /* PHASE_12 (owner-approved, redesign-v2): .club-card treatment (item 3) only when a club
     is actually picked -- same real heading/lede text and the same real crest() call as
     before (56px now, up from 40px, to read as the card's own focal art rather than a
     small icon; still the real SVG shield, or a real photo once one exists in
     web/img/crest/ -- crest() itself decides that, unchanged).
     A real gap found after the fact and fixed here: name-set-but-no-club fell through to
     the plain, unstyled .hubtop div -- real "Hola, [nombre]" text with no card at all, not
     a styling failure, just a state this branch never covered. Now gets a lighter
     .club-card.neutral sibling instead: same real shell (border-radius/padding/corner-ring
     all inherited from .club-card itself), a neutral background/ring (main.css), no crest
     (there's no club to show one for). The real heading text
     ("Hola, "+nombre) and the real lede ("Escoge por dónde entrar...") are byte-identical
     to what the old plain .hubtop rendered -- only the wrapper changed.
     Only the truly anonymous state (no name AND no club) keeps the original plain .hubtop
     layout -- nothing to personalize there, so no card treatment was asked for or added. */
  if(f){
    $('#hubTop').innerHTML = `
    <div class="club-card">
      ${crest(club,56,64)}
      <div class="body">
        <div class="hi">${pr.name ? 'Hola, '+esc(pr.name) : 'El archivo, desde '+esc(cn)}</div>
        <div class="sub">${esc(f.won.length?cn+' tiene '+f.won.length+(f.won.length===1?' título':' títulos')+
                ' en las 97 temporadas que cubre este archivo.'
              : cn+' nunca ha ganado. Está en el archivo igual.')}</div>
      </div>
    </div>`;
  }else if(pr.name){
    $('#hubTop').innerHTML = `
    <div class="club-card neutral">
      <div class="body">
        <div class="hi">Hola, ${esc(pr.name)}</div>
        <div class="sub">Escoge por dónde entrar, o pregunta directamente.</div>
      </div>
    </div>`;
  }else{
    $('#hubTop').innerHTML = `
    <div class="hubtop">
      <div style="flex:1;min-width:240px">
        <h2 class="hubhead">El archivo del BSN</h2>
        <p class="hublede">Escoge por dónde entrar, o pregunta directamente.</p>
      </div>
    </div>`;
  }

  /* LEAD — the user's club title comb, or Bayamón (the all-time leader) */
  const lf = (f && f.won.length) ? f : F.bay;
  const lead = lf===f ? cn : 'Bayamón';
  const blocks=[];

  /* Icons: TABS' own path strings (web/js/tabs.js, the same array buildNav() reads for the
     rail) -- historia/jugadores/juega/archivo each find their entry by id. Comparar has none:
     it's a Jugadores sub-view, never a top-level tab, so no rail icon exists for it -- left
     icon-less rather than inventing one (owner-approved, redesign-v2). */
  const iconOf = id => { const t=TABS.find(x=>x[0]===id); return t ? t[2] : null; };

  /* PHASE_9 hub restyle (owner-approved, redesign-v2): lead-card phrase now states the club's
     first-to-most-recent title span (lf.won[0]/lf.won[lf.won.length-1], never typed literals --
     stays correct for whichever club is picked, or Bayamón un-picked) instead of "el máximo de
     la liga", which just repeated the hero's own stat 3 ("18 títulos de Vaqueros de Bayamón, el
     club más ganador") -- see the redesign-v2 PHASE 9 hub-restyle report, option C. Only shown
     when there's more than one title: a single-title club's own first and most recent title are
     the same year, so "de 1998 a 1998" would read as a typo, not a fact -- those clubs fall back
     to the bare "títulos de X", the same text a non-leader club already got before this change.
     mostEver (whether lf leads the whole league) was only ever used by the text this replaces --
     removed with it, not left dangling unused. */
  blocks.push(edBlock({ lead:true, eye:lf===f?'Historia · tu club':'Historia',
    icon: iconOf('historia'),
    stat: lf.won.length,
    viz: titleComb(lf,{w:220,h:32,gap:1}),
    phrase:'títulos de '+lead+(lf.won.length>1?', de '+lf.won[0]+' a '+lf.won[lf.won.length-1]:''),
    ctx:'La cinta de campeones, 1930 a 2026. Las dinastías se leen como franjas sólidas de color; los años flacos, como huecos.',
    act:'Ver la cinta', go:"showView('historia','cinta')" }));

  const nJug = (PALL&&PALL.length) ? PALL.length : (PINDEX?PINDEX.length:0);
  const topPts = PINDEX ? PINDEX.filter(p=>p.pts!=null).map(p=>p.pts).sort((x,y)=>x-y).slice(-7) : [];
  blocks.push(edBlock({ eye:'Jugadores',
    icon: iconOf('jugadores'),
    stat: nJug ? nJug.toLocaleString('es-PR') : '—',
    viz: topPts.length>=2 ? spark(topPts,{area:true,w:96,h:24}) : '',
    phrase:'jugadores con fuente',
    ctx:'Cada ficha dice también qué no se sabe de él.',
    act:'El índice', go:"showView('jugadores','buscar')" }));

  blocks.push(edBlock({ eye:'Comparar',
    viz: cmpMiniViz('Georgie Torres','Mario Morales'),
    phrase:'Georgie Torres  ⇄  Mario Morales',
    ctx:'Dos carreras lado a lado. Las casillas vacías son huecos del archivo, no ceros.',
    act:'Comparar', go:"cmpPreset('Georgie Torres','Mario Morales')" }));

  const jn = (typeof puzzleNo==='function') ? puzzleNo() : null;
  blocks.push(edBlock({ eye:'Juega',
    icon: iconOf('juega'),
    stat: jn!=null ? '#'+jn : '',
    viz: dotgrid([0,1,0, 0,0,1, 1,0,0]),
    phrase:'La Cuadrícula de hoy',
    ctx:'Nueve cruces de club × logro. Un jugador que encaje en cada uno.',
    act:'Jugar', go:"showView('juega','cuadricula')" }));

  blocks.push(edBlock({ eye:'Archivo', stat:'2011',
    icon: iconOf('archivo'),
    viz: sparkBars(COVERAGE.map(c=>c[1]),{w:110,h:24,scale:100,gap:1.5}),
    phrase:'el muro real',
    ctx:'Antes de 2011 no hay estadística por temporada del BSN. El archivo enseña ese hueco y todos los demás.',
    act:'Cobertura', go:"showView('archivo','cobertura')" }));

  $('#hubGrid').innerHTML='<div class="edhub">'+blocks.join('')+'</div>';

  buildPrimer();
  buildRecentChamps();
  $('#hubFoot').textContent = f
    ? 'Cambia de club desde la píldora de arriba y el archivo se reordena a su alrededor.'
    : 'Escoge un club en Equipos y el archivo se reordena a su alrededor.';
}

/* PHASE_9 hub restyle (owner-approved, redesign-v2): "Últimos campeones" -- built from real
   data already used elsewhere (champOf/YEARS, both inline in index.html; the title-number
   column is the exact same computation showSeason() already does, f.won.indexOf(y)+1 --
   tabs.js's own showSeason()). The last 3 seasons with a documented champion, most recent
   first -- YEARS is already sorted ascending, so this walks backward and stops at 3 real
   entries rather than assuming the last 3 YEARS values all have one (a season with no
   champion registered would otherwise show as a gap here). */
function buildRecentChamps(){
  const host=$('#hubChamps'); if(!host) return;
  const rows=[];
  for(let i=YEARS.length-1; i>=0 && rows.length<3; i--){
    const y=YEARS[i], k=champOf[y];
    if(!k) continue;
    const f=F[k];
    rows.push({y, k, f, num:f.won.indexOf(y)+1});
  }
  if(!rows.length){ host.innerHTML=''; return; }
  /* PHASE_12 (owner-approved, redesign-v2): .champ-strip treatment (item 5), one real strip
     per real row -- all 3 real last-documented-champion rows kept (not reduced to the
     mockup's own single-strip sample; see this phase's own report on "none removed"), real
     crest(), and a real onclick into Historia -> Dinastías (showView, not a placeholder
     href="#") -- exactly the destination item 5 named. */
  host.innerHTML=`
    <h2 class="big">Últimos campeones</h2>
    ${rows.map(r=>`
    <button type="button" class="champ-strip" onclick="showView('historia','dinastias')">
      ${crest(r.k,44,50)}
      <div class="body">
        <div class="who">${esc(r.f.name)} — campeón ${r.y}</div>
        <div class="meta">Título #${r.num} · ver en Historia → Dinastías</div>
      </div>
    </button>`).join('')}`;
}

function buildProfile(){
  const p=prof(), f=p.club&&F[p.club]?F[p.club]:null;
  const st=ST.json('streak')||{};
  const hl=parseInt(ST.get('hlbest')||'0',10)||0;
  const short=k=>F[k].name.split(' de ')[0];

  const themeBtn=(v,label)=>
    `<button onclick="setTheme('${v}')" aria-selected="${p.theme===v?'true':'false'}">${label}</button>`;

  const clubs='<div class="tiles">'+ACTIVE.map(k=>
    `<button class="teamtile" aria-pressed="${k===p.club?'true':'false'}" onclick="pickClub('${k}')">
      ${crest(k,30,36)}<span class="tn">${esc(short(k))}</span></button>`).join('')+'</div>';

  const startOpts=TABS.filter(t=>t[0]!=='perfil').map(([id,label])=>
    `<option value="${id}"${p.start===id?' selected':''}>${esc(label)}</option>`).join('');

  $('#profBody').innerHTML=`
    <div class="card">
      <div class="profrow">
        <div class="proflab"><div class="pl">Nombre</div>
          <div class="ph">Solo para el saludo del inicio.</div></div>
        <div class="profctl">
          <input type="text" id="profName" maxlength="24" value="${esc(p.name)}"
                 placeholder="Como te quieras llamar" aria-label="Tu nombre">
        </div>
      </div>

      <div class="profrow">
        <div class="proflab"><div class="pl">Mi club</div>
          <div class="ph">Reordena el inicio y marca tu club en las tablas.</div></div>
        <div class="profctl">${clubs}
          <p class="note">${f?'Ahora mismo: '+esc(f.name)+'. Tócalo otra vez para quitarlo.'
                            :'Sin club. Toca uno para escogerlo.'}</p></div>
      </div>

      <div class="profrow">
        <div class="proflab"><div class="pl">Tema</div>
          <div class="ph">Automático sigue lo que tenga el teléfono.</div></div>
        <div class="profctl">
          <div class="modebtns" role="group" aria-label="Tema">
            ${themeBtn('auto','Automático')}${themeBtn('light','Claro')}${themeBtn('dark','Oscuro')}
          </div>
          ${p.theme==='auto'?`<p class="note">Tu sistema pide ${osTheme()==='light'?'claro':'oscuro'} ahora mismo.</p>`:''}
        </div>
      </div>

      <div class="profrow">
        <div class="proflab"><div class="pl">¿Qué es el BSN?</div>
          <div class="ph">El recuadro de bienvenida en el inicio.</div></div>
        <div class="profctl">
          <div class="modebtns" role="group" aria-label="¿Qué es el BSN?">
            <button onclick="showPrimer()" aria-selected="${p.primer!=='off'?'true':'false'}">Mostrar</button>
            <button onclick="dismissPrimer()" aria-selected="${p.primer==='off'?'true':'false'}">Ocultar</button>
          </div>
        </div>
      </div>

      <div class="profrow">
        <div class="proflab"><div class="pl">Pantalla de entrada</div>
          <div class="ph">Dónde abre la app al arrancar.</div></div>
        <div class="profctl">
          <select id="profStart" aria-label="Pantalla de entrada">${startOpts}</select>
        </div>
      </div>
    </div>

    <h3 class="sec">Tus números</h3>
    <div class="strip">
      <div><div class="n">${st.cur||0}</div><div class="l">racha actual</div></div>
      <div><div class="n">${st.best||0}</div><div class="l">mejor racha</div></div>
      <div><div class="n">${st.played||0}</div><div class="l">días jugados</div></div>
      <div><div class="n">${st.immaculate||0}</div><div class="l">cuadrículas perfectas</div></div>
      <div><div class="n">${hl}</div><div class="l">mejor en sube y baja</div></div>
    </div>
    <p class="note">El progreso de los juegos se guarda aparte de los ajustes, así que
      restaurar las preferencias no te borra la racha.</p>

    <h3 class="sec">Tus datos</h3>
    <div class="btnrow">
      <button class="btn" onclick="exportProfile()">Descargar mis datos</button>
      <button class="btn" onclick="resetProfile()">Restaurar preferencias</button>
    </div>
    <p class="note" id="profMsg"></p>`;

  $('#profName').oninput=e=>{
    setProf('name',e.target.value.slice(0,24));
    try{ buildHub(); }catch(err){ console.error('BSN: falló el hub al cambiar el nombre',err); }
  };
  $('#profStart').onchange=e=>setProf('start',e.target.value);
}

/* Everything the app holds about you, in one file you can read. The
   point is that "stored locally" is checkable rather than a claim. */
function exportProfile(){
  const dump={profile:prof(),progress:{}};
  ST.keys().forEach(k=>{
    if(k===PROFILE_KEY) return;
    dump.progress[k]=ST.get(k);
  });
  try{
    const blob=new Blob([JSON.stringify(dump,null,2)],{type:'application/json'});
    const a=el('a');
    a.href=URL.createObjectURL(blob);
    a.download='bsn-archivo-'+todayStamp()+'.json';
    document.body.appendChild(a); a.click();
    setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); },1000);
  }catch(e){
    console.error('BSN: falló la descarga del perfil',e);
    $('#profMsg').textContent='Este navegador no dejó descargar el archivo.';
  }
}

/* Two presses, and it says exactly what it will and will not touch.
   A destructive control that fires on the first press is a trap. */
let RESET_ARMED=false;
function resetProfile(){
  const msg=$('#profMsg');
  if(!RESET_ARMED){
    RESET_ARMED=true;
    msg.innerHTML='<span class="warn" style="display:block">Esto borra tu nombre, tu equipo, '
      +'el tema y la pantalla de entrada. No toca tu racha ni tus juegos guardados. '
      +'Toca «Restaurar preferencias» otra vez para confirmar.</span>';
    setTimeout(()=>{ if(RESET_ARMED){ RESET_ARMED=false; if(msg) msg.textContent=''; } },8000);
    return;
  }
  RESET_ARMED=false;
  PROFILE=Object.assign({},PROFILE_DEFAULTS);
  saveProfile();
  applyTheme();
  buildClubPicker(); buildClubCard(); drawClubPill(); buildStandings2026(); if(typeof paintLandingFeats==='function') paintLandingFeats();
  try{ buildHub(); }catch(e){ console.error('BSN: falló el hub tras restaurar',e); }
  buildProfile();
  $('#profMsg').textContent='Preferencias restauradas. Tu progreso sigue intacto.';
}


/* ============================================================
   GLOSARIO

   El archivo llevaba tiempo usando «refuerzo», «nativizado» y «La Más
   Dura» como si todo el mundo los supiera. Alguien que llega de fuera
   —o un puertorriqueño que no sigue el baloncesto— rebota en los
   números por culpa del vocabulario, no por culpa de los datos.
   ============================================================ */
const GLOSARIO=[
 {t:'BSN', k:['bsn','baloncesto superior nacional'],
  d:'Baloncesto Superior Nacional: la liga profesional de baloncesto de Puerto Rico. '
   +'Fundada en 1929, primera temporada en 1930. Doce equipos, 34 juegos por equipo, '
   +'de marzo a agosto.'},
 {t:'La Más Dura', k:['la mas dura','mas dura'],
  d:'El apodo de la liga. La idea es que es un torneo corto y sin descanso: con 34 juegos, '
   +'una mala racha de dos semanas te puede dejar fuera.'},
 {t:'Refuerzo', k:['refuerzo','refuerzos','importado','import'],
  d:'Un jugador extranjero contratado para reforzar a un equipo. Cada club puede tener un '
   +'número limitado; desde 2025 son tres por equipo, antes eran dos. Es la palabra '
   +'puertorriqueña para lo que en otras ligas se llama importado.'},
 {t:'Nativizado', k:['nativizado','nativizada','nativizacion'],
  d:'Un jugador nacido fuera que, por residencia o por vía federativa, cuenta como nativo y '
   +'por tanto no ocupa una de las plazas de refuerzo. La distinción decide cuántos '
   +'extranjeros puede vestir un equipo.'},
 {t:'Final Brava', k:['final brava'],
  d:'El nombre que la liga le da a su serie final. Se juega al mejor de siete.'},
 {t:'Fase regular', k:['fase regular','temporada regular'],
  d:'Los 34 juegos que cada equipo juega antes de los playoffs. Deciden quién clasifica y '
   +'en qué orden.'},
 {t:'Repechaje', k:['repechaje','play-in','play in'],
  d:'Una ronda extra entre los equipos que quedaron justo fuera de la clasificación, para '
   +'darles una última oportunidad de entrar a los playoffs.'},
 {t:'BSNF', k:['bsnf','liga femenina'],
  d:'Baloncesto Superior Nacional Femenino: la liga femenina de Puerto Rico. Corre en '
   +'temporada aparte de la masculina.'},
 {t:'Nuyorican', k:['nuyorican','nuyoricans'],
  d:'Puertorriqueño criado en Nueva York. En los setenta, Raymond Dalmau, Neftalí Rivera y '
   +'Rubén Rodríguez llegaron de las canchas de Harlem y el Bronx y cambiaron cómo se '
   +'jugaba aquí. Al principio contaban como refuerzos.'},
 {t:'Dirigente', k:['dirigente','dirigentes'],
  d:'El entrenador o head coach. Muchos dirigentes del BSN son exjugadores del propio torneo.'},
 {t:'Apoderado', k:['apoderado','apoderados'],
  d:'El dueño o principal responsable de una franquicia. En el BSN el apoderado suele ser una '
   +'figura pública con nombre propio, no una corporación anónima.'},
 {t:'Sequía', k:['sequia','sequias'],
  d:'Los años que lleva un club sin ganar un título. En este archivo se cuenta desde su '
   +'último campeonato hasta 2026.'},
 {t:'Novato del año', k:['novato del ano','novato'],
  d:'El premio al mejor jugador en su primera temporada.'},
 {t:'MVP', k:['mvp','jugador mas valioso'],
  d:'Jugador Más Valioso de la temporada. Pachín Vicéns, Teófilo Cruz y Mario Morales lo '
   +'ganaron cuatro veces cada uno, que es el récord.'},
 {t:'Triple', k:['triple','triples','tiro de tres'],
  d:'El tiro de tres puntos. No existió en el BSN hasta los años ochenta, y por eso los '
   +'totales de anotación de las primeras décadas no se comparan limpiamente con los de hoy.'}
];

function glosByText(q){
  const s=norm(q);
  let best=null,len=0;
  GLOSARIO.forEach(g=>{
    [norm(g.t)].concat(g.k.map(norm)).forEach(k=>{
      if(k.length>len && s.indexOf(k)>=0){ best=g; len=k.length; }
    });
  });
  return best;
}

function buildGlossary(){
  $('#glosBox').innerHTML='<div class="glos">'+GLOSARIO.map(g=>
    `<div class="glositem"><div class="glost">${esc(g.t)}</div>
      <div class="glosd">${esc(g.d)}</div></div>`).join('')+'</div>';
}

/* ============================================================
   PRIMER
   ============================================================ */
function dismissPrimer(){ setProf('primer','off'); buildPrimer(); }
function showPrimer(){ setProf('primer','on'); buildPrimer(); }

function buildPrimer(){
  const host=$('#hubPrimer'); if(!host) return;
  if(prof().primer==='off'){
    host.innerHTML='<p class="note">¿Primera vez por aquí? '
      +'<button class="x" onclick="showPrimer()" style="background:none;border:0;color:var(--azul-hi);'
      +'cursor:pointer;font:inherit;text-decoration:underline">Leer qué es el BSN</button></p>';
    return;
  }
  /* PHASE_12 follow-up (owner-approved, redesign-v2): label+icon swap only, per the
     clarification this task's own answer surfaced -- buildPrimer() is the "¿Qué es el
     BSN?" first-visit explainer, not date-driven content, so the tag now says exactly
     that (matching the real .primerhead h4 just below it) with an info icon, not a clock.
     Every paragraph, the dismiss button, and the glosario link below are still
     byte-identical to before -- this touches only the tag's own label string and its svg. */
  host.innerHTML=`
    <div class="today-card">
      <div class="tc-tag"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 11h1v5h1"/></svg>¿Qué es el BSN?</div>
      <div class="primer">
        <div class="primerhead">
          <h4>¿Qué es el BSN?</h4>
          <button class="x" onclick="dismissPrimer()">Ya lo sé, ocúltalo</button>
        </div>
        <p>El Baloncesto Superior Nacional es la liga profesional de baloncesto de Puerto Rico.
          Empezó en 1930 y no ha parado desde entonces, salvo unos pocos años sueltos. Hoy son
          doce equipos, cada uno de un pueblo, y cada equipo juega 34 partidos entre marzo y
          junio. Después vienen los playoffs, y en agosto se corona un campeón.</p>
        <p>Lo que la hace distinta de otras ligas es el tamaño. Con 34 juegos, dos malas semanas
          te cuestan la temporada; de ahí el apodo, «La Más Dura». Y cada club puede firmar un
          número limitado de jugadores extranjeros, llamados refuerzos, así que el resto de la
          cancha es talento puertorriqueño.</p>
        <p>Este archivo cubre las 97 temporadas: quién ganó, quién anotó, quién jugó y qué se
          perdió por el camino. Si una palabra no te suena, está en el
          <button class="x" onclick="showView('archivo','glosario')">glosario</button>.</p>
      </div>
    </div>`;
}

/* ============================================================
   PERFIL

   One object under one key. The two flat mirrors below are caches,
   not a second source of truth: 'club' because six call sites read it
   directly and rewriting them all buys nothing, and 'theme' because
   the pre-paint script in the head cannot afford to parse JSON before
   the first frame.

   Game progress (streak, hlbest, grid:*) is deliberately NOT in here.
   Preferences are small, portable and safe to reset; a streak is
   neither, and merging them would make "restore defaults" a
   destructive act.
   ============================================================ */
const PROFILE_KEY='profile';
const PROFILE_DEFAULTS={v:1,name:'',club:null,theme:'auto',start:'inicio',primer:'on'};
let PROFILE=null;

function loadProfile(){
  const saved=ST.json(PROFILE_KEY);
  const p=Object.assign({},PROFILE_DEFAULTS,saved||{});
  /* Builds before this one stored club and theme loose. Read them once
     so an existing copy does not silently forget the club you picked. */
  if(!saved){
    const c=ST.get('club'); if(c) p.club=c;
    const t=ST.get('theme'); if(t==='dark'||t==='light') p.theme=t;
  }
  /* Anything unrecognised falls back rather than propagating: a club
     that no longer exists in F would break every crest that reads it. */
  if(p.club&&!F[p.club]) p.club=null;
  if(['auto','dark','light'].indexOf(p.theme)<0) p.theme='auto';
  if(!TABS.some(t=>t[0]===p.start)) p.start='inicio';
  if(p.primer!=='off') p.primer='on';
  PROFILE=p;
  /* Write on first load, so a migrated or repaired profile is durable
     rather than re-derived every session. Without this the legacy keys
     stay the real store and the whole point of the consolidation is
     lost the day something stops reading them. */
  if(!saved) saveProfile();
  return p;
}
function prof(){ return PROFILE||loadProfile(); }
function saveProfile(){
  ST.setJSON(PROFILE_KEY,PROFILE);
  if(PROFILE.club) ST.set('club',PROFILE.club); else ST.del('club');
  ST.set('theme',PROFILE.theme);
}
function setProf(k,v){ prof()[k]=v; saveProfile(); }

/* ============================================================
   ¿QUIÉN SOY?
   Six clues, three guesses, points fall as clues are revealed.
   ============================================================ */
let QZ=null;
/* backlog item 6, part 3 (2026-09-14) — the candidate pool was capped at
   93 of 378 POOL players (25%) because clue 6 required p.b (a curated
   bio), which only HOF/leader-tagged players ever got. The other 285 --
   every one of them, checked directly, not assumed -- have complete
   rpg/apg/spg/bpg, just never a bio sentence. This fills clue 6 from
   those real stats instead of excluding them. Priority: rpg/apg (neither
   is used by any other clue -- clue 4 already covers ppg) over spg/bpg;
   the final fallback text is honest, not currently reachable (every
   bio-less player has at least one of the four), kept for whenever that
   stops being true. */
/* PHASE_47 (owner-approved, redesign-v2): two real bugs found going through this
   function for the position/terminology pass item 4 asked for, not anticipated
   going in. (a) "N rebotes"/"N asistencias"/"N robos"/"N tapones" glued a hardcoded
   plural straight onto the real per-game average -- reachable the moment any of
   those four equals exactly 1 (confirmed live, PHASE_47's own screenshot: a real
   player with ppg=1 showed "Promedió 1 puntos por juego." before the matching fix
   below). plural() (helpers.js) fixes all four here; "tapón"/"tapones" is the one
   genuinely irregular pair in this set (not a plain +s), passed explicitly rather
   than guessed. (b) none of this -- the player-facing text never showed "1 puntos"
   before this phase either, since the bug was below in clueList() for ppg, not here
   -- this function's own rpg/apg/spg/bpg concatenation had the exact same bug,
   just never confirmed with a real low-average player until this pass checked it
   directly. */
function statClue(p){
  const parts=[];
  if(p.rpg!=null) parts.push(p.rpg+' '+plural(p.rpg,'rebote'));
  if(p.apg!=null) parts.push(p.apg+' '+plural(p.apg,'asistencia'));
  if(parts.length) return `Promedió ${parts.join(' y ')} por juego.`;
  const parts2=[];
  if(p.spg!=null) parts2.push(p.spg+' '+plural(p.spg,'robo'));
  if(p.bpg!=null) parts2.push(p.bpg+' '+plural(p.bpg,'tapón','tapones'));
  if(parts2.length) return `Promedió ${parts2.join(' y ')} por juego.`;
  return 'Su producción más allá de los puntos nunca se registró.';
}
/* PHASE_47B (owner-approved, redesign-v2): PHASE_47's own fix only covered SLOT_ES's
   5 standard codes (PG/SG/SF/PF/C) -- "G"/"F"/"F/C" still fell back to the raw code,
   confirmed live, a real and regularly-reachable gap (52 of 376 POOL players, 13.8%,
   /tmp/p47b_pos_values.txt). POS_ES is this one new table the task asked for ("a
   single mapping table so changing them is a one-line edit") -- Quiz-only, kept
   separate from SLOT_ES (games.js, Draft's own, not duplicated) rather than merged
   into it. G->"Base o escolta" and "F/C"->"Poste" are NOT new wording -- Grid's own
   CATS categories (data.js) already treat bare "G" as part of 'guard' and "F/C" as
   part of 'big' via their own real regexes (/G|PG|SG/ and /C|PF|F\/C/); reused
   directly. "F"->"Alero o ala-pívot" has no existing precedent anywhere in the app
   (confirmed: neither CATS regex matches bare "F") -- a genuine new proposal,
   printed in /tmp/p47b_strings.txt for approval before commit, not assumed. */
const POS_ES={G:'Base o escolta',F:'Alero o ala-pívot','F/C':'Poste'};
/* posEs(p) tries SLOT_ES then POS_ES on the full code first (so "F/C" resolves to
   the single clean "Poste" rather than a clunkier token-by-token join); only a code
   NEITHER table recognizes falls through to posTokens() (games.js, already exists --
   reused rather than re-implementing compound-splitting here), translating each
   token separately and joining with " o ". Not exercised by any of today's real
   players (all 8 real codes resolve on the first branch), but in place so a future,
   genuinely novel compound code still translates instead of leaking a raw one. If
   nothing translates at all, returns null -- the clue is OMITTED (clueList() below
   falls back to the same "no está registrada" line already used for a missing pos),
   never a raw code shown to the player. */
function posEs(p){
  const direct=SLOT_ES[p.pos]||POS_ES[p.pos];
  if(direct) return direct;
  const toks=posTokens(p).map(t=>SLOT_ES[t]||POS_ES[t]).filter(Boolean);
  return toks.length?[...new Set(toks)].join(' o '):null;
}
function clueList(p){
  const cl=[];
  cl.push(p.d.length>1?`Jugó en los ${p.d[0]}s y los ${p.d[p.d.length-1]}s.`:`Jugó en los ${p.d[0]}s.`);
  cl.push(p.t.includes('import')?'Llegó a la liga como refuerzo.':p.t.includes('native')?'Es nativo o nativizado.':'Su estatus no está registrado.');
  const pEs=p.pos?posEs(p):null;
  cl.push(pEs?`Jugaba de ${pEs}.`:'Su posición no está registrada.');
  if(p.ppg!=null) cl.push(`Promedió ${p.ppg} ${plural(p.ppg,'punto')} por juego.`);
  else cl.push('Su promedio de anotación nunca se registró.');
  cl.push(p.c.length?`Vistió el uniforme de ${p.c.map(c=>F[c].name).join(', ')}.`:'Su club no está registrado en el archivo.');
  cl.push(p.b || statClue(p));
  return cl;
}
function newQuiz(){
  const cands=POOL.filter(p=>p.d.length&&(p.b||p.rpg!=null||p.apg!=null||p.spg!=null||p.bpg!=null));
  const p=pick(cands);
  QZ={p,clues:clueList(p),shown:1,guesses:3,done:false};
  drawQuiz();
}
/* PHASE_47 (owner-approved, redesign-v2): visual pass (item 1) -- "Otra pista" used
   to share .guessbar with the input+"Adivinar" button, wrapping to its own awkward
   second row at 390px (confirmed live, not assumed) since 3 flex items rarely fit
   one line at that width. Moved into its own .btnrow underneath, the same
   separation Draft already uses between its own primary action (court tap) and
   secondary ones (spin/reset) -- the answer bar now reads as one action, "reveal
   another clue" as a clearly separate one, matching the other 3 games' own
   hierarchy instead of Quiz's own flatter layout. No change to clue text, point
   math, or guess matching -- rendering only. */
function drawQuiz(){
  const host=$('#quizGame');
  if(!QZ){ host.innerHTML=''; return; }
  const pts=[60,40,25,15,10,5][QZ.shown-1];
  let h=`<div class="gamehead"><div class="dim" style="font-size:var(--fs-2xs)">Tres intentos · cada pista revelada baja los puntos</div>
    <div class="chips" style="margin:0"><span class="tag gold">${QZ.done?'—':pts+' puntos'}</span>
      <span class="tag">Intentos ${QZ.guesses}</span></div></div>`;
  h+='<div class="card" style="margin-top:var(--sp-2_5)"><ol style="margin:0;padding-left:20px;line-height:1.8">'+
    QZ.clues.slice(0,QZ.shown).map(c=>'<li>'+esc(c)+'</li>').join('')+'</ol></div>';
  if(!QZ.done){
    h+=`<div class="guessbar"><input type="text" id="qGuess" placeholder="¿Quién es?" autocomplete="off" list="poolNames">
      <button class="btn primary" onclick="guessQuiz()">Adivinar</button></div>
      <div class="btnrow"><button class="btn" onclick="revealClue()" ${QZ.shown>=6?'disabled':''}>Otra pista</button></div>`;
  } else {
    h+=`<div class="btnrow"><button class="btn primary" onclick="newQuiz()">Otro jugador</button>
      <button class="btn" onclick="showPlayer(${JSON.stringify(QZ.p.n).replace(/"/g,'&quot;')})">Ver su ficha</button></div>`;
  }
  h+='<div class="msg" id="qMsg" role="status" aria-live="polite"></div>';
  host.innerHTML=h;
  const i=$('#qGuess'); if(i){ i.onkeydown=e=>{if(e.key==='Enter')guessQuiz();}; }
}
function revealClue(){ if(QZ.shown<6){QZ.shown++;drawQuiz();} }
function guessQuiz(){
  const v=norm($('#qGuess').value); if(!v) return;
  if(norm(QZ.p.n).includes(v)&&v.length>=3){
    QZ.done=true; drawQuiz();
    $('#qMsg').textContent=`Correcto: ${QZ.p.n}. ${[60,40,25,15,10,5][QZ.shown-1]} puntos.`;
    $('#qMsg').className='msg good';
    return;
  }
  QZ.guesses--;
  if(QZ.guesses<=0){
    QZ.done=true; QZ.shown=6; drawQuiz();
    $('#qMsg').textContent='Se acabaron los intentos. Era '+QZ.p.n+'.';
    $('#qMsg').className='msg bad';
  } else {
    drawQuiz();
    $('#qMsg').textContent='No. Te quedan '+QZ.guesses+'.';
    $('#qMsg').className='msg bad';
  }
}

/* ============================================================
   BOOT
   Every builder runs inside its own try/catch. One bad section
   should degrade one section — in the previous build a single
   malformed value in storage killed eleven of them, because the
   boot sequence was one unguarded run of statements.
   ============================================================ */
function poolDatalist(){
  const d=el('datalist'); d.id='poolNames';
  d.innerHTML=POOL.map(p=>`<option value="${esc(p.n)}"></option>`).join('');
  document.body.appendChild(d);
}

/* ============================================================
   COMPARAR

   v1 was a table. Correct, and nobody looked at it twice. A table
   makes you read two numbers and do the subtraction yourself, which
   is exactly the work a comparison view exists to remove.

   v2 answers the question before you finish reading it: a verdict
   line, then one bar per category drawn to scale so the gap has a
   length, then a radar for the shape of a player rather than his
   totals. Colour comes from each player's own club, so Georgie is
   Fajardo maroon and Piculín is San Germán orange — no arbitrary
   chart palette to memorise.

   The one rule inherited from v1 and never bent: an unrecorded
   figure draws no bar at all and is labelled a hole. A zero-length
   bar would read as "worst", and the archive does not know that.
   ============================================================ */
let CMP=[];
const CMP_FALLBACK=['var(--azul)','var(--rojo)','var(--ok)'];

function cmpFind(name){
  if(!PINDEX) return null;
  /* PHASE_36: the nickKey() fallback is what lets cmpAdd('Mario Morales')
     (the plain form, e.g. CMP_PRESETS' own literal string) still resolve
     to the merged "Mario «Quijote» Morales" card once that's his only
     PINDEX entry -- norm() equality/startsWith alone can't, since neither
     is a substring/prefix of the other once the nickname sits in between. */
  return PINDEX.find(x=>norm(x.name)===norm(name)) ||
         PINDEX.find(x=>norm(x.name).startsWith(norm(name))) ||
         PINDEX.find(x=>nickKey(x.name)===nickKey(name));
}
function cmpColor(p,i){
  const c=Array.from(p.clubs).find(k=>F[k]);
  return c?F[c].c1:CMP_FALLBACK[i%3];
}
/* PHASE_25 item 1: two real club colors can be too close to tell apart at
   a glance (same hue family, similar lightness -- e.g. Cariduros de
   Fajardo's maroon #7A1F3D vs Piratas de Quebradillas' red #B3141F,
   hueDist 15.6°/Ldiff 9; or two different "blue" clubs). Collision rule:
   circular hue distance <=20° AND |lightness diff|<=15 (HSL, computed on
   the real hex, both measured live against this league's real palette
   before picking the thresholds -- 20°/15 catches both real examples
   above without also flagging genuinely different hues like Santurce's
   orange (H18.5) against Quebradillas' red (H356, 22.7° apart -- just
   outside the rule, correctly left alone). CMP_DISTINCT is a small fixed
   set of 4 hues chosen to sit in this league's real color gaps (checked
   against all 33 active/historic club c1 hexes available at the time):
   2 of the 4 still land inside the threshold of exactly one specific
   club each (amber/Osos de Manatí, cyan/Capitanes de Arecibo) -- left in
   deliberately rather than chasing a mathematically-impossible "never
   collides with any of 33+ real clubs" set, since the assignment loop
   below already skips any candidate that collides with a color actually
   in use THIS comparison; a real clash only happens if every one of the
   4 is simultaneously unusable, never observed testing up to 3 players. */
const CMP_DISTINCT=['#5B8C1F','#7A3FD1','#C9960C','#0E8FA6'];
function hexHsl(hex){
  const [r,g,b]=hexRgb(hex).map(v=>v/255);
  const max=Math.max(r,g,b), min=Math.min(r,g,b); let h=0,s=0,l=(max+min)/2;
  if(max!==min){
    const d=max-min; s=l>0.5?d/(2-max-min):d/(max+min);
    if(max===r) h=(g-b)/d+(g<b?6:0); else if(max===g) h=(b-r)/d+2; else h=(r-g)/d+4;
    h*=60;
  }
  return [h,s*100,l*100];
}
function cmpColorsCollide(hexA,hexB){
  if(!/^#/.test(hexA)||!/^#/.test(hexB)) return false;
  const [h1,,l1]=hexHsl(hexA), [h2,,l2]=hexHsl(hexB);
  const d=Math.abs(h1-h2)%360, hd=d>180?360-d:d;
  return hd<=20 && Math.abs(l1-l2)<=15;
}
/* The one real color every downstream piece (avatar, card top bar,
   scoreboard numeral, bars, radar polygon, legend) must share -- computed
   ONCE per drawCompare() call and threaded through as a plain array, so
   none of them can silently drift from what another one drew. The first
   player always keeps their real club color (nothing to collide with
   yet); each later player's real color is swapped for a CMP_DISTINCT
   pick only if it actually collides with a color already locked in. */
function cmpAssignColors(ps){
  const used=[];
  return ps.map((p,i)=>{
    let hex=cmpColor(p,i);
    if(used.some(u=>cmpColorsCollide(hex,u))){
      hex=CMP_DISTINCT.find(c=>!used.some(u=>cmpColorsCollide(c,u)))||hex;
    }
    used.push(hex);
    return hex;
  });
}
/* backlog item 4 (season_detail_spec.md addendum) — cross-player season
   comparison. CMP_MODE tracks each added name's chosen side: 'career'
   (today's PINDEX-driven behavior, default whenever available) or a
   career[] array index. CMP_DATA caches that name's fetched career[]
   ('loading' mid-fetch, 'none' when no bsnpr_id resolves at all) so
   switching modes after the first pick never re-fetches. */
let CMP_MODE={}, CMP_DATA={};

/* The picker searches the full 3,357-player archive index, not just the
   ~230 curated PINDEX names Comparar has always offered — otherwise most
   of the 154 players with real Tier-2 season stats (2001-2004) would be
   unreachable. Filtered to `career_seasons` (a build-time count of real
   career[] rows) rather than `n_seasons` (a free-typed players_canonical.csv
   field confirmed to mismatch the real row count on 251 players, 6 of them
   >0 with zero actual rows — spec addendum [FOUND]) or `has_profile`
   (also demonstrably unreliable, same section). */
function cmpCandidateNames(){
  const seen=new Set(), out=[];
  (PINDEX||[]).forEach(p=>{ const k=norm(p.name); if(!seen.has(k)){seen.add(k); out.push(p.name);} });
  (PALL||[]).forEach(p=>{ if((p.career_seasons||0)>0){ const k=p.norm||norm(p.name); if(!seen.has(k)){seen.add(k); out.push(p.name);} } });
  return out;
}
/* Called once index/players.json lands (hydrate), in case Comparar was
   already open — same pattern as refreshPlayerIndexArchive. */
function refreshCompareCandidates(){
  const dl=$('#cmpList');
  if(dl) dl.innerHTML=cmpCandidateNames().map(n=>'<option value="'+esc(n)+'">').join('');
}
function cmpResolveName(v){
  const p=cmpFind(v);
  if(p) return p.name;
  if(!PALL) return null;
  const hit=PALL.find(x=>norm(x.name)===norm(v)) || PALL.find(x=>norm(x.name).startsWith(norm(v)));
  return (hit && (hit.career_seasons||0)>0) ? hit.name : null;
}
/* id resolution mirrors loadPlayerExtra's own priority: the archive index
   itself (works for archive-only, season-only adds) first, PXWALK (the
   curated-name crosswalk) second — a curated display name like "Raymond
   Dalmau" won't literal-match the archive's "Dalmau Santana, Raymond", so
   PXWALK is the only path that resolves those. */
async function cmpEnsureData(name){
  if(CMP_DATA[name] && CMP_DATA[name]!=='loading') return CMP_DATA[name];
  const fromPall=(PALL||[]).find(x=>norm(x.name)===norm(name));
  const id=fromPall?fromPall.id:(PXWALK && PXWALK[norm(name)]);
  if(id==null){ CMP_DATA[name]='none'; return CMP_DATA[name]; }
  CMP_DATA[name]='loading';
  const d=await DATA.get('players/'+id+'.json');
  CMP_DATA[name]={id, career:((d&&d.career)||[]).slice().sort((a,b)=>(a.season||0)-(b.season||0))};
  return CMP_DATA[name];
}
function cmpAdd(name){
  const inp=$('#cmpQ');
  const v=(name||(inp?inp.value:'')||'').trim();
  if(!v) return;
  const rn=cmpResolveName(v);
  const msg=$('#cmpMsg');
  if(!rn){ if(msg) msg.textContent='No aparece en el índice: '+v; return; }
  if(CMP.includes(rn)){ if(msg) msg.textContent='Ya está en la comparación.'; return; }
  if(CMP.length>=3){ if(msg) msg.textContent='Tres es el máximo. Quita a uno primero.'; return; }
  CMP.push(rn);
  /* A player not in PINDEX has no career-level averages to fall back on —
     only ever addable in season mode. Default picked once the fetch lands. */
  CMP_MODE[rn]=cmpFind(rn)?'career':null;
  if(inp) inp.value='';
  if(msg) msg.textContent='';
  cmpEnsureData(rn).then(d=>{
    if(CMP_MODE[rn]==null && d && d!=='none' && d.career && d.career.length)
      CMP_MODE[rn]=d.career.length-1;   /* most recent season, a real default */
    drawCompare();
  });
  drawCompare();
}
function cmpRemove(n){ CMP=CMP.filter(x=>x!==n); delete CMP_MODE[n]; delete CMP_DATA[n]; drawCompare(); }
function cmpClear(){ CMP=[]; CMP_MODE={}; CMP_DATA={}; const m=$('#cmpMsg'); if(m) m.textContent=''; drawCompare(); }
function cmpSetMode(name,val){
  CMP_MODE[name]=(val==='career')?'career':Number(val);
  drawCompare();
}
/* PHASE_6 — Comparar is a promoted mode inside Jugadores (Buscar | Comparar),
   not a buried accordion. */
let JUGVIEW='buscar';
/* PHASE_8.2b — Buscar / Comparar are now sibling views of the router.
   Kept as a shim: some call sites still ask by name. */
function setJugView(v){
  v = (v==='comparar') ? 'comparar' : 'buscar';
  JUGVIEW=v;
  showView('jugadores',v);
  if(v==='comparar'){ try{ buildCompare(); }catch(e){ console.error('BSN: falló Comparar',e); } }
}
function cmpFromPlayer(name){
  showView('jugadores','comparar',{noScroll:true});
  try{ buildCompare(); }catch(e){}
  cmpAdd(name);
  const o=$('#cmpOut'); if(o&&o.scrollIntoView) o.scrollIntoView({block:'start',behavior:'smooth'});
}
/* Two taps to a real comparison beats an empty box and a blinking
   cursor — most people cannot name a second BSN player on demand. */
function cmpPreset(a,b){
  showView('jugadores','comparar',{noScroll:true,noHash:true});
  try{ buildCompare(); }catch(e){}
  /* PHASE_36: resolve each preset name FIRST (cmpResolveName(), the same
     call cmpAdd() already makes) instead of keeping the raw literal string
     CMP_PRESETS carries -- a real bug this merge exposed: CMP_PRESETS[0]'s
     own 'Mario Morales' resolves (via cmpFind()'s new nickKey fallback) to
     the merged "Mario «Quijote» Morales" card, but CMP itself used to keep
     'Mario Morales' verbatim, so cmpEnsureData()/CMP_DATA got written
     under THAT key while cmpSeasonSelect() -- reading cmpResolved(name).name,
     the RESOLVED player's own canonical name -- looked the data up under
     the nickname key instead. Two different keys for the same real fetch
     meant the season select never saw its own data land and stayed on
     "Cargando…" forever. Resolving upfront, the same way cmpAdd() always
     has, keeps CMP/CMP_DATA/CMP_MODE on one consistent key throughout. */
  CMP=[a,b].map(n=>cmpResolveName(n)||n).filter(n=>cmpFind(n));
  CMP.forEach(n=>{ CMP_MODE[n]='career'; cmpEnsureData(n).then(drawCompare); });
  if(CMP.length===2) setHash('jugadores/comparar/'+slug(a)+'/'+slug(b));
  drawCompare();
}

const CMP_PRESETS=[
  ['Georgie Torres','Mario Morales','El uno contra el dos'],
  ['Raymond Dalmau','Rubén Rodríguez','Los setenta'],
  ['Travis Trice','Emmanuel Mudiay','Hoy']
];

/* Per-game rows drive the bars and the radar; career totals sit in a
   separate strip because mixing a 15,863 with a 23.4 on one scale
   makes both unreadable. */
const CMP_RATE=[
  {k:'Puntos por juego',    s:'ppg', a:'PTS'},
  {k:'Rebotes por juego',   s:'rpg', a:'REB'},
  {k:'Asistencias por juego',s:'apg',a:'AST'},
  {k:'Robos por juego',     s:'spg', a:'ROB'},
  {k:'Tapones por juego',   s:'bpg', a:'TAP'}
];
/* Percentages need their own group: on a bar scaled to the row maximum,
   a .486 next to a .512 would show as two nearly full bars and hide the
   gap entirely, so these are scaled against a fixed ceiling instead. */
const CMP_SHOT=[
  {k:'Tiros de campo', s:'fg', cap:0.70},
  {k:'Triples',        s:'tp', cap:0.50},
  {k:'Tiros libres',   s:'ft', cap:1.00},
  {k:'Minutos por juego', s:'mpg', cap:40}
];
const CMP_TOTAL=[
  {k:'Puntos de carrera', s:'pts'},
  {k:'Rebotes de carrera',s:'reb'},
  {k:'Asistencias',       s:'ast'},
  {k:'Juegos',            s:'gp'},
  {k:'MVP',               s:'mvp'}
];

function buildCompare(){
  const host=$('#cmpPick');
  if(!host) return;
  const names=cmpCandidateNames().map(n=>'<option value="'+esc(n)+'">').join('');
  host.innerHTML=`<div class="search-card">
  <div class="filters">
    <div class="field" style="min-width:230px"><label for="cmpQ">Añadir jugador</label>
      <input list="cmpList" id="cmpQ" type="search" placeholder="Escribe un nombre…" autocomplete="off"></div>
    <div class="field"><label>&nbsp;</label><button class="btn primary" onclick="cmpAdd()">Añadir</button></div>
    <div class="field"><label>&nbsp;</label><button class="btn" onclick="cmpClear()">Limpiar</button></div>
  </div>
  <datalist id="cmpList">${names}</datalist>
  <div class="chips" style="margin-top:2px">${CMP_PRESETS.map(p=>
    `<button class="chip" onclick="cmpPreset(${JSON.stringify(p[0]).replace(/"/g,'&quot;')},${JSON.stringify(p[1]).replace(/"/g,'&quot;')})">${esc(p[2])}</button>`).join('')}</div>
  <div class="msg" id="cmpMsg" role="status" aria-live="polite"></div>
  <div class="note" style="margin-top:var(--sp-2)">Cada jugador se puede fijar a su carrera o a una temporada
    específica. El archivo no tiene datos por jugador de 2022 en adelante — esas temporadas
    no aparecen para nadie todavía.</div>
  </div>`;
  const inp=$('#cmpQ');
  if(inp) inp.onkeydown=e=>{ if(e.key==='Enter'){ e.preventDefault(); cmpAdd(); } };
  drawCompare();
}

/* Every added player gets THIS SAME control, always — never a silent gap.
   A curated (PINDEX) name can resolve to a linked bsnpr_id with zero real
   career[] rows (Georgie Torres -> id 788, a known thin/enciclopedia-only
   link — his curated career averages are real, but the archive never
   captured a season for him). Without a disabled fallback that row would
   render with no control at all while every other added player has one —
   indistinguishable from a bug, and it hides the real fact (this player
   can only ever be compared by career) instead of showing it (PC4). */
function cmpSeasonSelectDisabled(label,name){
  return `<select disabled aria-label="Temporada de ${esc(name)}"><option>${esc(label)}</option></select>`;
}
/* Picked once a player's career[] has landed (cmpEnsureData) — "Carrera"
   only offered when they're a PINDEX name (its own career averages exist);
   an archive-only, season-only add just gets the season list. Labelled with
   the resolved club name, same FID2APP->F lookup loadPlayerExtra's own
   season table already uses, team_raw as the honest fallback. */
function cmpSeasonSelect(name){
  const canCareer=!!cmpFind(name);
  const d=CMP_DATA[name];
  if(!d || d==='loading') return cmpSeasonSelectDisabled('Cargando…',name);
  if(d==='none' || !d.career || !d.career.length)
    return cmpSeasonSelectDisabled(canCareer?'Carrera':'Sin datos vinculados',name);
  const mode=CMP_MODE[name];
  const curVal=(mode==null||mode==='career')?'career':String(mode);
  let opts='';
  if(canCareer) opts+=`<option value="career"${curVal==='career'?' selected':''}>Carrera</option>`;
  d.career.forEach((c,i)=>{
    const ak=FID2APP&&FID2APP[c.franchise_id];
    const club=(ak&&F[ak])?F[ak].name:(c.team_raw||'');
    /* MVP_ID (hydrate(), from index/mvp.json — backlog item 4 addendum,
       2026-09-14: historic_awards.csv now runs through identity resolution,
       see docs/specs/season_detail_spec.md). season->bsnpr_id, one MVP per
       year, so a straight equality check is enough — real link, never a
       guess: only marked when this exact player's own career[] season IS
       the archive's own recorded MVP winner for that year. */
    const isMvp = MVP_ID && MVP_ID[c.season]===d.id;
    const label=(c.season||'—')+(club?' · '+club:'')+(isMvp?' — MVP':'');
    opts+=`<option value="${i}"${curVal===String(i)?' selected':''}>${esc(label)}</option>`;
  });
  return `<select aria-label="Temporada de ${esc(name)}"
    onchange="cmpSetMode(${JSON.stringify(name).replace(/"/g,'&quot;')},this.value)">${opts}</select>`;
}
/* PHASE_22 Part 2a: a real head-to-head card (avatar/name/pos·years/club/
   season-select/Quitar), new .cmp2* classes throughout -- cmpHead() is only
   ever called from drawCompare() below (grep-confirmed), so this rewrite
   cannot touch renderSeasonCmp()'s own season-vs-season panel, which has
   always had its own separate inline markup against the old .cmphead/
   .cmpdot/.cmpname classes and is untouched here, left exactly as PHASE_21
   left it. portrait() (PHASE_21's own real direction-B avatar) replaces
   the old bare color dot.
   PHASE_25 item 1: `col` is now a required 3rd param -- drawCompare()'s
   own cmpAssignColors() result, already collision-resolved against every
   other player in THIS comparison -- instead of a fresh cmpColor(p,i)
   call here. Passed straight into portrait() as c1 (the avatar's own fill
   color) so the avatar, the top accent bar, and every other place this
   same color is used downstream are guaranteed the same hex, never three
   independent lookups that could drift. portrait()'s own c2 param has
   never done anything (confirmed reading its body -- portraitFill(c1)
   is the only place c1/c2 feed in, and c2 isn't referenced), so this
   changes nothing about avatars outside Comparar; portrait() itself is
   untouched. */
function cmpHead(p,i,col){
  /* PHASE_25 item 4: this line used to vanish entirely for a season-mode
     player (meta='') while a career-mode player alongside it always had
     one (falling back to the honest 'años sin registrar' text when pos
     AND years are both missing) -- one fewer line on one card shifts its
     own select/Quitar up relative to its neighbor's. Season mode now
     shows the one real fact it actually has here (which season is
     pinned, from the same p._season cmpResolved() already set) instead
     of pos·years it was never going to have; the line itself is always
     rendered either way, never conditionally dropped. */
  const meta=p._mode==='season'
    ? (p._season!=null ? 'Temporada '+esc(String(p._season)) : ' ')
    : esc([p.pos,p.years].filter(Boolean).join(' · ')||'años sin registrar');
  const clubKey=Array.from(p.clubs||[]).find(k=>F[k]);
  const clubName=clubKey?F[clubKey].name:'';
  const c2=clubKey?F[clubKey].c2:null;
  return `<div class="cmp2head" style="--cmp-c:${col}">
    ${portrait(p.name,col,c2,72,88,p.pos)}
    <div class="cmp2name">${esc(p.name)}</div>
    <div class="cmp2meta">${meta}</div>
    ${clubName?`<div class="cmp2meta">${esc(clubName)}</div>`:''}
    <span class="cmp2select">${cmpSeasonSelect(p.name)}</span>
    <button class="btn cmpx cmp2x" onclick="cmpRemove(${JSON.stringify(p.name).replace(/"/g,'&quot;')})" aria-label="Quitar a ${esc(p.name)}">Quitar</button>
  </div>`;
}

/* Radar of the five per-game categories, each scaled against the best
   in the whole index so the shape means something across eras. A
   category the player never had recorded collapses to the centre and
   is called out under the chart, not silently drawn as zero. */
function cmpRadar(ps,colors){
  const maxes={};
  CMP_RATE.forEach(r=>{
    maxes[r.s]=Math.max(1,...(PINDEX||[]).map(p=>typeof p[r.s]==='number'?p[r.s]:0));
  });
  /* PHASE_22 item d: bigger (R 64->90, same proportions scaled ~1.44x) and
     in its own real panel now instead of a narrow sidebar column -- the
     real per-category math/scaling below (against PINDEX's own live
     maxes) is unchanged, only the drawing's own size.
     PHASE_24 item 1: cy pushed down 16px (112->128, viewBox height
     240->256 to match) -- the top axis label ("PTS", i=0, straight up)
     was landing at y=5.7 with a 12.5px font, clipped by the SVG's own
     viewport above y=0. Every other label had real margin (closest was
     the side labels at y=78, nowhere near either edge), so a uniform
     vertical shift was enough; cx/R/the bottom labels' own margin are
     untouched. */
  const R=90, cx=127, cy=128, n=CMP_RATE.length;
  const pt=(i,f)=>{
    const a=-Math.PI/2 + i*2*Math.PI/n;
    return [cx+Math.cos(a)*R*f, cy+Math.sin(a)*R*f];
  };
  let g='';
  [0.25,0.5,0.75,1].forEach(f=>{
    const d=CMP_RATE.map((_,i)=>pt(i,f).map(v=>v.toFixed(1)).join(',')).join(' ');
    g+=`<polygon points="${d}" fill="none" stroke="var(--line)" stroke-width="1"/>`;
  });
  CMP_RATE.forEach((r,i)=>{
    const [x,y]=pt(i,1);
    g+=`<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="var(--line)" stroke-width="1"/>`;
    const [lx,ly]=pt(i,1.22);
    g+=`<text x="${lx.toFixed(1)}" y="${(ly+3.5).toFixed(1)}" text-anchor="middle" font-size="12.5"
        fill="var(--ink-3)" font-weight="700" letter-spacing=".05em">${r.a}</text>`;
  });
  ps.forEach((p,i)=>{
    const col=colors[i];
    /* PHASE_26 item 1: the 2px stroke is fully opaque and sits directly on
       .cmp2radar-panel's own --card background (not --raise -- the radar
       has no track, just the panel itself) -- real measured failures here
       too (e.g. Fajardo maroon 1.61:1 against dark --card). The 16%-opacity
       fill is already a faint wash blended with the panel behind it, so
       running it through the same safe pair costs nothing and keeps fill
       and stroke the same color, just belt-and-suspenders on the one
       that's actually legible at full opacity. */
    const fillPair=cmpFillSafe(col,'#0C1428','#0C1428',3), fillPairLight=cmpFillSafe(col,'#FFFFFF','#FFFFFF',3);
    const d=CMP_RATE.map((r,j)=>{
      const v=typeof p[r.s]==='number'?p[r.s]:0;
      return pt(j, Math.max(0.02, Math.min(1, v/maxes[r.s]))).map(x=>x.toFixed(1)).join(',');
    }).join(' ');
    g+=`<polygon class="cmpspoke" points="${d}" style="--cmp-fd:${fillPair};--cmp-fl:${fillPairLight};animation-delay:${i*90}ms"
        fill-opacity=".16" stroke-width="2" stroke-linejoin="round"/>`;
  });
  return `<svg viewBox="0 0 254 256" width="254" height="256" role="img"
    aria-label="Perfil por categoría de los jugadores comparados">${g}</svg>`;
}

/* PHASE_22 Part 2c, extended PHASE_24 item 4: a 5th, optional `mode` param.
   false/undefined/omitted (the only way renderSeasonCmp() ever calls this,
   3 args, grep-confirmed) renders the exact byte-for-byte original
   .cmprow/.cmpbars/.cmpbarline/.cmptrack/.cmpfill/.cmpval markup, untouched
   -- including its own var(--ok) green lead color and its own min-bar-
   width-on-zero quirk, neither touched here, per the standing "Temporadas
   must stay byte-identical" constraint. mode='mirrored' (Comparar's
   2-player case) renders the "tale of the tape" row: label centered, each
   player's value on the outside, the bar growing from the centre line
   outward on each side. mode='grouped' (Comparar's 3-player case, PHASE_24
   item 4 -- previously silently reused the legacy branch, which is why its
   lead color used to be the same var(--ok) green that collides with a
   teal club color) is new: same per-row grouped-bars shape as legacy, but
   with its own .cmp3* classes so the lead gets the player's own real
   contrast-safe color instead of a flat green, and each bar gets a
   colored owner cue (first name) beside its value -- three players with
   same-ish colors are still only told apart by the head cards above, so
   case where two of the real "find max" colors happen to visually read
   similarly was already a pre-existing risk; this phase doesn't change
   who's assigned which color, only how the lead's OWN color renders as
   text. PHASE_24 item 5: a true 0 now draws no fill (w=0) in BOTH new
   branches, same as a missing value's bar -- only the value text ("0",
   not "—") and the still-rendered row distinguish a real zero from a
   hole. The legacy branch's own 2%-floor-on-zero quirk is left exactly as
   it was, for the same byte-identical reason the lead color is. */
function cmpBarRow(row, ps, isTotal, mode, colors){
  const vals=ps.map(p=>typeof p[row.s]==='number'?p[row.s]:null);
  const known=vals.filter(v=>v!=null);
  const max=row.cap!=null ? row.cap : (known.length?Math.max.apply(null,known):0);
  const best=known.length>1?max:null;
  const fmt=v=>{
    if(v==null) return '—';
    if(row.cap!=null && row.cap<=1) return (v*100).toFixed(1)+'%';
    return isTotal? num(v) : v.toFixed(1);
  };
  const widthOf=v=>(v==null||!max||v===0)?0:Math.max(2,(v/max)*100);
  if(mode==='mirrored' && ps.length===2){
    const tie=known.length===2 && vals[0]===vals[1];
    const cell=(i,side)=>{
      const v=vals[i], col=colors[i];
      const w=widthOf(v);
      const lead=best!=null&&v===best&&!tie;
      const pair=lead?cmpColorPair(col,'#131E38','#E1E9F5'):null;
      const valStyle=pair?` style="--cmp-cd:${pair.dark};--cmp-cl:${pair.light}"`:'';
      /* PHASE_26 item 1: >=3:1 fill pair against the real track/row
         background (cmp2fill's own CSS now reads --cmp-fd/--cmp-fl,
         picked per theme the same way --cmp-cd/--cmp-cl already is for
         text), computed fresh per cell since each side can be a
         different player's color. */
      const fillPair=cmpFillPair(col);
      return {
        val:`<div class="cmp2val ${side}${lead?' lead':''}${v==null?' hole':''}"${valStyle}>${esc(fmt(v))}</div>`,
        fill:`<div class="cmp2half ${side}"><div class="cmp2fill" style="--w:${w}%;--cmp-fd:${fillPair.dark};--cmp-fl:${fillPair.light}"></div></div>`
      };
    };
    const a=cell(0,'l'), b=cell(1,'r');
    return `<div class="cmp2row">
      <div class="cmp2lab">${esc(row.k)}</div>
      <div class="cmp2line">
        ${a.val}
        <div class="cmp2track">${a.fill}${b.fill}</div>
        ${b.val}
      </div>
    </div>`;
  }
  if(mode==='grouped'){
    return `<div class="cmp3row">
      <div class="cmp3lab">${esc(row.k)}</div>
      <div class="cmp3bars">${ps.map((p,i)=>{
        const v=vals[i], col=colors[i];
        const w=widthOf(v);
        const lead=best!=null&&v===best;
        /* PHASE_25 item 2: both the lead value AND the owner cue are real
           text on this same --raise background -- the owner cue used to
           be the flat club/assigned hex with no contrast check at all
           (same bug the lead value already had before PHASE_22 fixed
           it). Same cmpColorPair() treatment for both now. */
        const pair=cmpColorPair(col,'#131E38','#E1E9F5');
        const ownerStyle=` style="--cmp-cd:${pair.dark};--cmp-cl:${pair.light}"`;
        const valStyle=lead?ownerStyle:'';
        const fillPair=cmpFillPair(col);
        return `<div class="cmp3barline">
          <span class="cmp3owner"${ownerStyle}>${esc((p.name||'').split(' ')[0])}</span>
          <div class="cmp3track"><div class="cmp3fill" style="--w:${w}%;--cmp-fd:${fillPair.dark};--cmp-fl:${fillPair.light};animation-delay:${i*70}ms"></div></div>
          <div class="cmp3val${lead?' lead':''}${v==null?' hole':''}"${valStyle}>${esc(fmt(v))}</div>
        </div>`;
      }).join('')}</div>
    </div>`;
  }
  return `<div class="cmprow">
    <div class="cmplab">${row.k}</div>
    <div class="cmpbars">${ps.map((p,i)=>{
      const v=vals[i], col=cmpColor(p,i);
      const w=(v==null||!max)?0:Math.max(2,(v/max)*100);
      const lead=best!=null&&v===best;
      return `<div class="cmpbarline">
        <div class="cmptrack"><div class="cmpfill" style="--w:${w}%;background:${col};animation-delay:${i*70}ms"></div></div>
        <div class="cmpval${lead?' lead':''}${v==null?' hole':''}">${fmt(v)}</div>
      </div>`;
    }).join('')}</div>
  </div>`;
}

/* Resolves one CMP name into the flat cmpBarRow-shaped object its current
   CMP_MODE calls for: the PINDEX career object (unchanged), or
   seasonCmpObj() over the chosen career[] row (season_detail_spec.md §1 —
   already generic, built for the single-player case, reused as-is here).
   null while the fetch is still in flight or nothing ever resolves. */
function cmpResolved(name){
  const mode=CMP_MODE[name];
  if(mode==null || mode==='career'){
    const p=cmpFind(name);
    if(p){ const o=Object.assign({},p); o._mode='career'; return o; }
  }
  const d=CMP_DATA[name];
  if(d && d!=='loading' && d!=='none' && d.career && d.career.length){
    const idx=(mode==null||mode==='career')?d.career.length-1:mode;
    const row=d.career[idx];
    if(row){
      const o=seasonCmpObj(row);
      o._season=o.name; o.name=name; o._mode='season';
      return o;
    }
  }
  return null;
}
/* PHASE_22 Part 2 (owner-approved, redesign-v2): Comparar's own real page,
   in the player page's own visual language (.rp-panel, --card/--raise
   tiers, portrait()'s real avatars, corner-ring decoration -- no tricolor,
   same owner instruction as PHASE_21's avatars). Every real computation
   below (resolved/ps/pending/anySeason/RATE-SHOT-TOTAL/the verdict's a/b/
   shared count/holes) is byte-for-byte the same as before this phase --
   only the markup assembling them changed. cmpBarRow()'s own `mode`
   param ('mirrored'/'grouped', PHASE_24 — previously a bare boolean) is
   the one real behavior switch Comparar drives; it's never passed by
   renderSeasonCmp(), so that path's own real output still never changes. */
function drawCompare(){
  const out=$('#cmpOut'); if(!out) return;
  if(!CMP.length){
    out.innerHTML=`<div class="rp-panel cmpempty">
      <div style="font-weight:700;font-size:var(--fs-base)">Nadie en la comparación todavía</div>
      <p class="muted" style="font-size:var(--fs-xs);margin:6px 0 0">Escribe un nombre arriba o toca uno de los duelos.
      Con dos jugadores aparece el marcador, las barras a escala y el radar de perfil.</p></div>`;
    return;
  }
  const resolved=CMP.map(n=>({name:n,p:cmpResolved(n)}));
  const ps=resolved.map(r=>r.p).filter(Boolean);
  const pending=resolved.filter(r=>!r.p).map(r=>r.name);
  /* Season involved on either side -> the category set a season actually
     has (SEASON_CMP_* — §2/§3 above), no radar (a single season's rate
     stats aren't on cmpRadar's PINDEX-wide career-average scale — spec
     addendum [OUT OF SCOPE]), no curated-tags footer (a season row was
     never curated with any tag). Pure career-vs-career (today's exact
     behavior) keeps the original CMP_RATE/SHOT/TOTAL + radar + tags path. */
  const anySeason=ps.some(p=>p._mode==='season');
  const n=CMP.length;
  /* PHASE_25 item 1: one collision-resolved color per player, computed
     once and threaded everywhere below (avatar, top bar, scoreboard,
     bars, radar, legend) instead of each spot calling cmpColor() fresh.
     Two parallel arrays, not one: HEAD_COLORS covers every card shown
     (including a still-pending add, which has no real stats to put in
     `ps` yet), COLORS covers only the resolved players everything past
     the heads actually renders. They're built from the same objects in
     the same order and so are identical once nothing is still loading —
     the only time they can differ is transiently, while a just-added
     player's data is still in flight. */
  const headObjs=CMP.map((nm,i)=>resolved[i].p||{name:nm,clubs:new Set(),pos:null,years:null,_mode:'pending'});
  const HEAD_COLORS=cmpAssignColors(headObjs);
  const COLORS=cmpAssignColors(ps);
  const headCards=headObjs.map((p,i)=>cmpHead(p,i,HEAD_COLORS[i]));
  const heads=`<div class="cmp2heads n${n}">${n===2?`${headCards[0]}<div class="cmp2vs"><span>VS</span></div>${headCards[1]}`:headCards.join('')}</div>`;

  if(ps.length<2){
    out.innerHTML=`${heads}
      <div class="rp-panel cmpempty" style="margin-top:var(--sp-4)">
        <p class="muted" style="font-size:var(--fs-xs);margin:0">${
          pending.length ? 'Cargando datos de temporada para '+esc(pending.join(', '))+'…'
                          : 'Añade otro jugador para comparar.'}</p></div>`;
    return;
  }

  const RATE=anySeason?SEASON_CMP_RATE:CMP_RATE, SHOT=anySeason?SEASON_CMP_SHOT:CMP_SHOT,
        TOTAL=anySeason?SEASON_CMP_TOTAL:CMP_TOTAL;
  const rows=RATE.concat(SHOT,TOTAL);
  /* PHASE_24 item 4: a named mode instead of a bare boolean -- 'mirrored'
     (2 players) and 'grouped' (3 players) are both new cmpBarRow()
     branches now (own classes, own lead-color handling); mode is never
     passed as anything but these two strings from here, so the legacy
     branch (mode undefined) is only ever reached via renderSeasonCmp(). */
  const mode=ps.length===2?'mirrored':'grouped';

  /* The verdict is counted only over categories both players have on
     record. Winning a row your rival never had measured is not a win. */
  let verdict='', scoreboard='';
  if(ps.length===2){
    let a=0,b=0,shared=0;
    rows.forEach(r=>{
      const x=ps[0][r.s], y=ps[1][r.s];
      if(typeof x!=='number'||typeof y!=='number') return;
      shared++; if(x>y)a++; else if(y>x)b++;
    });
    if(shared){
      const lead=a===b?null:(a>b?ps[0]:ps[1]);
      /* PHASE_25 item 2: this used the flat club/assigned hex as a raw
         inline color with zero contrast check -- live-checked against
         the real #0C1428/#FFFFFF this sits on (.cmp2score's own --card
         background) and both A.D.'s teal and Georgie's maroon measured
         under 4.5:1 in at least one theme. Same cmpColorPair() treatment
         the scoreboard numerals already had. */
      const leadPair=lead?cmpColorPair(COLORS[a>b?0:1]):null;
      const leadStyle=leadPair?` style="--cmp-cd:${leadPair.dark};--cmp-cl:${leadPair.light}"`:'';
      verdict=`<div class="cmpverdict">${lead
        ? `<b class="cmp2verdict-lead"${leadStyle}>${esc(lead.name.split(' ')[0])}</b> gana <b>${Math.max(a,b)}</b> de <b>${shared}</b> renglones comparables`
        : `Empate: <b>${a}</b> a <b>${b}</b> en ${shared} renglones comparables`}
        <span class="dim"> · ${rows.length-shared} sin datos en común</span></div>`;
      /* b. the exact same a/b/shared count above, just also drawn as large
         mirrored numerals -- real colors (cmpColorPair(), the same text-
         safe pair the mirrored rows use), never rendered for a 0-0 "tie"
         that isn't really a tie (see the `shared` guard above/below). */
      const pairA=cmpColorPair(COLORS[0]), pairB=cmpColorPair(COLORS[1]);
      scoreboard=`<div class="rp-panel cmp2score">
        <div class="cmp2score-row">
          <span class="cmp2score-n" style="--cmp-cd:${pairA.dark};--cmp-cl:${pairA.light}">${a}</span>
          <span class="cmp2score-dash">–</span>
          <span class="cmp2score-n" style="--cmp-cd:${pairB.dark};--cmp-cl:${pairB.light}">${b}</span>
        </div>
        ${verdict}
      </div>`;
    } else {
      verdict=`<div class="cmpverdict dim">No hay ni un renglón que los dos tengan registrado. Ese es el hueco del archivo, no un empate.</div>`;
      scoreboard=`<div class="rp-panel cmp2score">${verdict}</div>`;
    }
  }

  const radarPanel = anySeason?'':`<div class="rp-panel cmp2radar-panel">
    <div class="cmp2radar-group">
      <div class="cmp2radar-svg">${cmpRadar(ps,COLORS)}</div>
      <div class="cmp2legend">
        ${ps.map((p,i)=>`<div class="cmp2legend-item"><span class="cmp2legend-dot" style="background:${COLORS[i]}"></span>${esc(p.name)}</div>`).join('')}
        <div class="dim" style="font-size:var(--fs-3xs)">Cada eje va contra el mejor del índice</div>
      </div>
    </div>
  </div>`;

  /* PHASE_24 item 3: a row where every player is missing used to still
     draw its label + an empty track for each side -- real visual noise on
     rows like "Tiros de campo" when neither player has 2012+ box scores.
     Split each group into rows with >=1 known value (rendered as before)
     and rows with zero (collected, never drawn, named in one line at the
     panel's own bottom instead) -- a group with nothing left to render
     also skips its own label, so "TIRO Y CARGA" never sits over nothing. */
  const splitGroup=(group,isTot)=>{
    const kept=[], skippedLabels=[];
    group.forEach(r=>{
      if(ps.some(p=>typeof p[r.s]==='number')) kept.push(cmpBarRow(r,ps,isTot,mode,COLORS));
      else skippedLabels.push(r.k);
    });
    return {kept, skippedLabels};
  };
  const rG=splitGroup(RATE,false), sG=splitGroup(SHOT,false), tG=splitGroup(TOTAL,true);
  const allSkipped=rG.skippedLabels.concat(sG.skippedLabels,tG.skippedLabels);
  const rowsPanel=`<div class="rp-panel cmp2rows-panel">
    ${rG.kept.length?`<div class="ed-eye">Por juego</div>${rG.kept.join('')}`:''}
    ${sG.kept.length?`<div class="ed-eye" style="margin-top:var(--sp-4)">${anySeason?'Tiro':'Tiro y carga'}</div>${sG.kept.join('')}`:''}
    ${tG.kept.length?`<div class="ed-eye" style="margin-top:var(--sp-4)">${anySeason?'De la temporada':'De carrera'}</div>${tG.kept.join('')}`:''}
    ${allSkipped.length?`<div class="cmp2skip dim">Sin datos en común — ${esc(allSkipped.join(' · '))}</div>`:''}
  </div>`;

  const footPanel=`<div class="rp-panel cmp2foot-panel">
    <div class="cmpfoot">
      ${ps.map((p,i)=>`<div class="cmpfootcol">
        <div class="dim" style="font-size:var(--fs-3xs);letter-spacing:.07em;font-weight:700">${esc(p.name.split(' ')[0].toUpperCase())}</div>
        <div style="font-size:var(--fs-2xs);margin-top:3px">${anySeason
          ? (p._mode==='season'?'Temporada '+esc(String(p._season||'—')):'Carrera')+' · '+(Array.from(p.clubs).map(c=>F[c]?F[c].abbr:c).join(' ')||'—')
          : (Array.from(p.clubs).map(c=>F[c]?F[c].abbr:c).join(' ')||'—')}</div>
        ${anySeason?'':`<div class="chips" style="margin-top:5px">${Array.from(p.tags).slice(0,6).map(t=>
          `<span class="tag ${/MVP|Leyenda|10\.000/.test(t)?'gold':''}" style="font-size:var(--fs-3xs)">${esc(t)}</span>`).join('')||'<span class="dim" style="font-size:var(--fs-2xs)">—</span>'}</div>
        ${p.hi?`<div class="muted" style="font-size:var(--fs-3xs);margin-top:5px">Mejor: ${p.hi[1].toFixed(1)} pts en ${p.hi[0]}</div>`:''}`}
      </div>`).join('')}
    </div>
  </div>`;

  let h=heads+scoreboard+radarPanel+rowsPanel+footPanel;

  const holes=[];
  ps.forEach(p=>{
    const c=rows.filter(r=>typeof p[r.s]!=='number').length;
    if(c) holes.push(p.name.split(' ')[0]+': '+c);
  });
  if(holes.length) h+=`<div class="warn" style="margin-top:var(--sp-4)">Casillas sin registrar — ${esc(holes.join(' · '))}. Un guion es un hueco del archivo, no un cero, y por eso no dibuja barra.${anySeason?'':' Antes de 2012 no existe una base pública de estadísticas por temporada del BSN.'}</div>`;
  if(pending.length) h+=`<div class="note">Cargando temporadas de ${esc(pending.join(', '))}…</div>`;
  out.innerHTML=h;
}
/* Deep links: #archivo, #equipos/bay, #jugador/georgie-torres */
/* ============================================================
   PLEGADO DE SECCIONES

   Runs once, after every builder has written its markup, and turns
   each h3.sec plus the siblings that follow it into a disclosure.
   Open/closed is remembered per section so a tab you use every day
   opens the way you left it.
   ============================================================ */
/* ============================================================
   ESTANTE DE JUEGOS
   ============================================================ */
const GAMES=[
  {id:'cuadricula',t:'La Cuadrícula',
   d:'Nueve casillas, un tablero nuevo cada día, y el mismo para todo el mundo. Nombra al jugador que cruza cada fila con cada columna.',
   meta:'Diario · racha',
   art:`<defs><linearGradient id="ga1" x1="0" y1="0" x2="1" y2="1">
     <stop offset="0" stop-color="#1663D8"/><stop offset="1" stop-color="#0B1E3E"/></linearGradient></defs>
   <rect width="320" height="104" fill="url(#ga1)"/>
   <g stroke="#EEF3FB" stroke-opacity=".85" stroke-width="2" fill="none">
     <rect x="112" y="14" width="24" height="24" rx="3"/><rect x="144" y="14" width="24" height="24" rx="3"/><rect x="176" y="14" width="24" height="24" rx="3"/>
     <rect x="112" y="40" width="24" height="24" rx="3"/><rect x="144" y="40" width="24" height="24" rx="3"/><rect x="176" y="40" width="24" height="24" rx="3"/>
     <rect x="112" y="66" width="24" height="24" rx="3"/><rect x="144" y="66" width="24" height="24" rx="3"/><rect x="176" y="66" width="24" height="24" rx="3"/></g>
   <rect x="144" y="40" width="24" height="24" rx="3" fill="#25C26E" fill-opacity=".9"/>
   <rect x="112" y="66" width="24" height="24" rx="3" fill="#EF2B39" fill-opacity=".85"/>`},
  {id:'temporada',t:'La Temporada Perfecta',
   d:'Gira equipo y década, coloca cinco posiciones en la cancha y descubre cuántos de 34 gana tu quinteto.',
   meta:'Quinteto · 5 puestos',
   art:`<defs><linearGradient id="ga2" x1="0" y1="0" x2="1" y2="1">
     <stop offset="0" stop-color="#7A3A12"/><stop offset="1" stop-color="#1A0E06"/></linearGradient></defs>
   <rect width="320" height="104" fill="url(#ga2)"/>
   <g stroke="#EEF3FB" stroke-opacity=".5" stroke-width="2" fill="none">
     <rect x="96" y="8" width="128" height="88" rx="4"/>
     <path d="M136 8h48v30h-48z"/><circle cx="160" cy="52" r="18"/>
     <path d="M124 96a36 36 0 0 1 72 0"/></g>
   <circle cx="160" cy="38" r="7" fill="#FF6A1A"/>
   <g fill="#EEF3FB" fill-opacity=".9"><circle cx="118" cy="80" r="4"/><circle cx="160" cy="86" r="4"/><circle cx="202" cy="80" r="4"/></g>`},
  {id:'quiensoy',t:'¿Quién soy?',
   d:'Seis pistas que van de lo difícil a lo obvio. Mientras menos necesites, más vale el acierto.',
   meta:'Adivinanza · 3 intentos',
   art:`<defs><linearGradient id="ga3" x1="0" y1="0" x2="1" y2="1">
     <stop offset="0" stop-color="#4A2A7A"/><stop offset="1" stop-color="#140A24"/></linearGradient></defs>
   <rect width="320" height="104" fill="url(#ga3)"/>
   <circle cx="160" cy="46" r="24" fill="#EEF3FB" fill-opacity=".12" stroke="#EEF3FB" stroke-opacity=".5" stroke-width="2"/>
   <path d="M160 34a8 8 0 0 1 5 14c-3 2-5 3-5 6" stroke="#EEF3FB" stroke-width="3.4" fill="none" stroke-linecap="round"/>
   <circle cx="160" cy="60" r="2.6" fill="#EEF3FB"/>
   <g fill="#EEF3FB" fill-opacity=".22"><rect x="104" y="82" width="112" height="5" rx="2.5"/><rect x="126" y="92" width="68" height="5" rx="2.5"/></g>`},
  {id:'subeybaja',t:'Sube y Baja',
   d:'Dos jugadores, una cifra. ¿Anotó más o menos? Sigue acertando hasta que falles.',
   meta:'Rachas · sin fin',
   art:`<defs><linearGradient id="ga4" x1="0" y1="0" x2="1" y2="1">
     <stop offset="0" stop-color="#0E5C3A"/><stop offset="1" stop-color="#04180F"/></linearGradient></defs>
   <rect width="320" height="104" fill="url(#ga4)"/>
   <path d="M96 78 L128 58 L160 66 L192 34 L224 44" stroke="#25C26E" stroke-width="3.4" fill="none"
     stroke-linecap="round" stroke-linejoin="round"/>
   <g fill="#EEF3FB"><circle cx="128" cy="58" r="3.4"/><circle cx="192" cy="34" r="3.4"/></g>
   <path d="M206 26h14v14" stroke="#25C26E" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`}
];
let GAME_OPEN=null;

function buildShelf(){
  const host=$('#gameShelf');
  if(!host) return;
  host.innerHTML=GAMES.map(g=>`<button class="tile" onclick="openGame('${g.id}')" aria-label="Abrir ${esc(g.t)}">
    <svg class="tileart" viewBox="0 0 320 104" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${g.art}</svg>
    <span class="tilebody" style="display:block">
      <span class="tiletitle" style="display:block">${esc(g.t)}</span>
      <span class="tiledesc" style="display:block">${esc(g.d)}</span>
      <span class="tilemeta">${esc(g.meta)}<span class="tileplay">Jugar</span></span>
    </span>
  </button>`).join('');
}
function openGame(id){
  if(!GAMES.some(g=>g.id===id)) return;
  showView('juega',id);
  GAME_OPEN=id;
}
function closeGame(){
  showView('juega','__landing');
  GAME_OPEN=null;
}
document.addEventListener('keydown',e=>{ if(e.key==='Escape' && GAME_OPEN) closeGame(); });

/* ── buildViews ───────────────────────────────────────────────────
   Runs once, after every builder has written its markup. Each nav
   section's h3.sec (h4.sub in Equipos) blocks, plus the pre-heading
   content, become focused .view divs; a synthetic __landing view is
   prepended; a .subnav pill rail switches them. Replaces foldSections. */
const VIEW_MAP={
  historia:{ pre:['cinta','La cinta'], split:'h3.sec', map:[
    ['Títulos por franquicia',['titulos','Títulos']],
    ['Dinastías',['dinastias','Dinastías']],
    ['El careo de las finales',['finales','Finales']],
    ['Premios y líderes',['premios','Premios']],
    ['Los refuerzos',['refuerzos','Refuerzos']],
    ['Todas las temporadas',['temporadas','Todas las temporadas']]
  ]},
  jugadores:{ host:'#jugBuscar', drop:['#jugMode'], pre:['buscar','Buscar'], split:'h3.sec',
    detail:['jugador','#playerPage'],
    adopt:[['#jugComparar','comparar','Comparar']], map:[
    ['Líderes de carrera',['lideres','Líderes de carrera']],
    ['Récords de la liga',['records','Récords']],
    ['Salón',['salon','Salón']],
    ['Del BSN a la NBA',['nba','A la NBA']],
    ['Dirigentes',['dirigentes','Dirigentes']],
    ['Honrados en concreto',['canchas','Canchas y coliseos']]
  ]},
  equipos:{ split:'h4.sub', detail:['equipo','#teamDetail'], map:[
    ['Activos',['activos','Activos']],
    ['Quién es el apoderado',['duenos','Apoderados']],
    ['Franquicias desaparecidas',['desaparecidos','Desaparecidas']],
    ['Camisetas retiradas',['retirados','Camisetas retiradas']]
  ]},
  archivo:{ pre:['preguntar','Preguntar'], split:'h3.sec', map:[
    ['Consulta a la medida',['constructor','A la medida']],
    ['Cobertura del archivo',['cobertura','Cobertura y fuentes']],
    ['Calidad de datos',['calidad','Calidad de datos']],
    ['Calendario y cobertura',['calendario','Calendario']],
    ['Glosario',['glosario','Glosario']]
  ]}
};
function _mkView(sec,slug){
  const d=el('div','view'); d.dataset.view=slug; d.dataset.sec=sec; d.hidden=true; return d;
}
function _subnavEl(sec,order,landLabel){
  const nav=el('div','subnav'); nav.setAttribute('role','tablist');
  nav.setAttribute('aria-label','Vistas de '+sec);
  [['__landing',landLabel||'Resumen']].concat(order).forEach(([slug,label])=>{
    const b=el('a'); b.href='#'+sec+(slug==='__landing'?'':'/'+slug); b.dataset.view=slug; b.textContent=label;
    b.setAttribute('role','tab');
    b.onclick=(e)=>{
      if(e.ctrlKey||e.metaKey||e.shiftKey||e.button!==0) return;   /* let the browser open a new tab/window natively */
      e.preventDefault(); showView(sec,slug);
    };
    b.onkeydown=(e)=>{ if(e.key===' '){ e.preventDefault(); showView(sec,slug); } };
    nav.appendChild(b);
  });
  return nav;
}
/* one line per view — the section landing's editorial card copy (8.3c) */
const VIEW_DESC={
  historia:{
    cinta:'Cada temporada desde 1930 con su campeón, pintada del color del club.',
    titulos:'Quién ha ganado más en 97 temporadas.',
    dinastias:'Las rachas de títulos seguidos, club por club.',
    finales:'Cada emparejamiento de final y cuántas veces ocurrió.',
    premios:'MVP, novato del año y líder de anotación, año por año.',
    refuerzos:'La regla de nómina que más mueve el juego en el BSN.',
    temporadas:'La tabla completa, filtrable y exportable a CSV.'
  },
  jugadores:{
    buscar:'Todos los jugadores que el archivo puede nombrar con fuente.',
    comparar:'Dos o tres carreras lado a lado; las casillas vacías son huecos.',
    lideres:'Los totales de por vida: puntos, rebotes, asistencias.',
    records:'Las marcas que la liga reconoce, con fecha y contexto.',
    salon:'Los jugadores con ficha propia y, muchos, biografía.',
    nba:'Los que llegaron a la liga estadounidense.',
    dirigentes:'Los entrenadores que pasaron por aquí — varios, exjugadores.',
    canchas:'Coliseos de Puerto Rico que llevan el nombre de un jugador.'
  },
  equipos:{
    activos:'Los doce clubes que juegan hoy.',
    duenos:'Quién es el apoderado de cada franquicia.',
    /* PHASE_40 (owner-approved, redesign-v2): a getter, not a plain string -- VIEW_DESC
       is a top-level object literal, evaluated the instant tabs.js runs, well before
       web/index.html's own inline script defines FKEYS (the exact GRID_CLUBS/FKEYS
       timing trap games.js's own comment documents) and before hydrate() (init.js) has
       had a chance to overwrite any F[k].active flag from web/data/index/franchises.json.
       A getter defers the count to each real read, which only ever happens from inside
       buildEquiposLanding() at full-boot time (post-hydration) -- so this reads Object.
       values(F) directly rather than FKEYS, sidestepping the trap instead of relying on
       call-order luck. */
    get desaparecidos(){
      const n=Object.values(F).filter(x=>!x.active).length;
      const w=numWordsEs(n,true);
      return w[0].toUpperCase()+w.slice(1)+' clubes que ya no existen, con su historial de finales.';
    },
    retirados:'Camisetas que ningún otro jugador del club volverá a usar.'
  },
  archivo:{
    preguntar:'Pregúntale al archivo en español.',
    constructor:'Escoge una tabla, filtra, ordena y baja a CSV.',
    cobertura:'Cuánto del archivo está verificado, por década, y de dónde sale cada dato.',
    calidad:'Dónde las fuentes no coinciden y qué hicimos con cada caso.',
    calendario:'Lo que se puede reconstruir del calendario del BSN, y lo que falta.',
    glosario:'Las palabras que el archivo usa sin explicar en el resto de la app.'
  }
};
/* PHASE_11 (owner-approved, redesign-v2): Historia's own landing (item 1's "Explora
   Historia" grid + the 3 real stat cards) branches here, ONLY for sec==='historia' --
   every other section (Jugadores/Equipos/Archivo, explicitly out of scope this pass) keeps
   the exact generic mega-feat+landgrid path below, untouched. Real icon paths are the
   mockup's own (generic line icons for a sub-view, not a team/club logo -- no real-data
   concern the way crest() has one), real descriptions are VIEW_DESC.historia's own existing
   copy (order already carries the real [slug,label] pairs VIEW_MAP.historia produced, in
   real order -- cinta/titulos/dinastias/finales/premios/refuerzos/temporadas). */
const HISTORIA_XICON={
  cinta:'M4 12h16M4 7h16M4 17h16',
  titulos:'M4 21h4V11H4ZM10 21h4V4h-4ZM16 21h4v-8h-4Z',
  dinastias:'M12 2l2.5 6.5L21 9l-5 4.5L17.5 21 12 17l-5.5 4L8 13.5 3 9l6.5-.5Z',
  finales:'M4 4h16v16H4Z M4 10h16 M10 4v16',
  premios:'M12 2l2.6 5.9L21 9l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.9L3 9l6.4-1.1Z',
  refuerzos:'M4 6h16M4 12h16M4 18h10',
  temporadas:'M4 5h16v14H4Z M4 10h16 M9 5v14'
};
function buildHistoriaLanding(order){
  const wrap=el('div');
  const most=FKEYS.slice().sort((a,b)=>F[b].won.length-F[a].won.length)[0];
  const withTitles=FKEYS.filter(k=>F[k].won.length).length;
  const stats=el('div','stats3');
  stats.innerHTML=`
    <div class="stat solid"><div class="n mono">${F[most].won.length}</div>
      <div class="l">Títulos de ${esc(F[most].name)}, el club más ganador</div></div>
    <div class="stat"><div class="n mono">${NSEASONS}</div>
      <div class="l">Temporadas documentadas, de ${YEARS[0]} a ${YEARS[YEARS.length-1]}</div></div>
    <div class="stat"><div class="n mono">${withTitles}</div>
      <div class="l">Franquicias distintas que han sido campeonas</div></div>`;
  wrap.appendChild(stats);
  const h2=el('h2','sec'); h2.textContent='Explora Historia'; wrap.appendChild(h2);
  const grid=el('div','explore');
  const D=VIEW_DESC.historia||{};
  order.forEach(([slug,label])=>{
    const b=el('button','xcard'); b.type='button';
    b.innerHTML=`<span class="go" aria-hidden="true">→</span>
      <span class="ic"><svg viewBox="0 0 24 24"><path d="${HISTORIA_XICON[slug]||''}" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span class="t">${esc(label)}</span>
      <span class="d">${esc(D[slug]||'')}</span>`;
    b.onclick=()=>showView('historia',slug);
    grid.appendChild(b);
  });
  wrap.appendChild(grid);
  return wrap;
}
/* PHASE_11 (owner-approved, redesign-v2): rewrites #historia's own .phead in place into
   the mockup's eyebrow/Oswald-pagehead hero (item 4) -- the class add is scoped to this one
   element (classList.add, not a global rule change), so every other section's .phead
   (Inicio/Jugadores/Equipos/Juega/Archivo, all out of scope this pass) is completely
   unaffected; .hhero's own CSS never touches the bare .phead selector either. The arc
   device is the REAL Inicio hero's own repeating-radial-gradient rings (main.css's .hhero
   rule), reused exactly, not a new SVG -- item 4's own instruction. The existing .tri
   flag-strip (shared across every section's .phead) is dropped ONLY here, in its place the
   eyebrow's own gradient tick (var(--tri), the same flag gradient) already carries the same
   red/white/blue accent in miniature -- a deliberate substitution, not an oversight, flagged
   in this pass's own report. */
function buildHistoriaHero(){
  const head=document.querySelector('#historia .phead'); if(!head) return;
  head.classList.add('hhero');
  head.innerHTML=`<div class="eyebrow">EL ARCHIVO DEL BSN · ${YEARS[0]}—${YEARS[YEARS.length-1]}</div>
    <h1>Historia</h1>
    <p class="lede">Ocho vistas construidas con los datos reales del archivo: la cinta de ${NSEASONS} temporadas, títulos por franquicia, dinastías, finales cara a cara, premios, la regla de refuerzos 2024–2026 y la tabla completa de temporadas.</p>`;
}
/* PHASE_14 (owner-approved, redesign-v2): Jugadores' own landing, same mechanism as
   buildHistoriaLanding() above -- branches in buildLanding() below ONLY for
   sec==='jugadores'; every other section (Equipos/Archivo, out of scope this pass)
   keeps the generic mega-feat+landgrid path. Real icon paths are generic line icons
   for a sub-view (not a player likeness or club logo -- no real-data concern the way
   portrait()/crest() have one); real descriptions are VIEW_DESC.jugadores's own
   existing copy; order already carries the real [slug,label] pairs VIEW_MAP.jugadores
   produced (buscar/comparar/lideres/records/salon/nba/dirigentes/canchas). */
const JUGADORES_XICON={
  buscar:'M10.5 3a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15ZM21 21l-5.2-5.2',
  comparar:'M9 6a6 6 0 1 0 0 12M15 6a6 6 0 1 1 0 12',
  lideres:'M4 20h4v-5H4ZM10 20h4v-9H10ZM16 20h4v-13H16Z',
  records:'M12 2l2.6 5.9L21 9l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.9L3 9l6.4-1.1Z',
  salon:'M4 21h16M5 21V10l7-5 7 5v11M9 21v-6h6v6',
  nba:'M4 12h14M13 6l5 6-5 6',
  dirigentes:'M9 3h6v3H9ZM7 6h10l-1 15H8Z',
  canchas:'M3 21h18M5 21V8l7-4 7 4v13M9 21v-5h6v5'
};
function buildJugadoresLanding(order){
  const wrap=el('div');
  const stats=el('div','stats3');
  stats.innerHTML=`
    <div class="stat solid"><div class="n mono">${PINDEX?PINDEX.length:0}</div>
      <div class="l">Jugadores destacados con ficha propia en el archivo</div></div>
    <div class="stat"><div class="n mono">${HOF.length}</div>
      <div class="l">En el Salón: los que definieron la liga</div></div>
    <div class="stat"><div class="n mono">${NBA_PLAYERS.length}</div>
      <div class="l">Llegaron del BSN a la NBA</div></div>`;
  wrap.appendChild(stats);
  const h2=el('h2','sec'); h2.textContent='Explora Jugadores'; wrap.appendChild(h2);
  const grid=el('div','explore');
  const D=VIEW_DESC.jugadores||{};
  order.forEach(([slug,label])=>{
    const b=el('button','xcard'); b.type='button';
    b.innerHTML=`<span class="go" aria-hidden="true">→</span>
      <span class="ic"><svg viewBox="0 0 24 24"><path d="${JUGADORES_XICON[slug]||''}" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span class="t">${esc(label)}</span>
      <span class="d">${esc(D[slug]||'')}</span>`;
    b.onclick=()=>showView('jugadores',slug);
    grid.appendChild(b);
  });
  wrap.appendChild(grid);
  return wrap;
}
function buildJugadoresHero(){
  const head=document.querySelector('#jugadores .phead'); if(!head) return;
  head.classList.add('hhero');
  head.innerHTML=`<div class="eyebrow">EL ARCHIVO DEL BSN</div>
    <h1>Jugadores</h1>
    <p class="lede">El índice reúne a todos los jugadores que este archivo puede nombrar con fuente. Cada ficha dice también qué no se sabe de él.</p>`;
}
/* PHASE_40 (owner-approved, redesign-v2): Equipos' own landing, same mechanism as
   buildHistoriaLanding()/buildJugadoresLanding() above -- branches in buildLanding()
   below ONLY for sec==='equipos'; Archivo (out of scope this pass) keeps the generic
   mega-feat+landgrid path. Real icon paths are generic line icons for a sub-view (not
   a club crest -- no real-data concern the way crest() has one); real descriptions are
   VIEW_DESC.equipos's own existing copy (its own desaparecidos entry is a getter, see
   above); order already carries the real [slug,label] pairs VIEW_MAP.equipos produced
   (activos/duenos/desaparecidos/retirados). All 3 stat numbers are FKEYS/F-derived,
   none typed in -- the PHASE_39 survey's own GAPS#1 finding (copy said "veinte", real
   count is 21) is exactly the class of bug a hardcoded number here would repeat. */
const EQUIPOS_XICON={
  activos:'M4 21V10l8-6 8 6v11M9 21v-7h6v7',
  duenos:'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4 20c0-4 3.5-7 8-7s8 3 8 7',
  desaparecidos:'M3 7l9-4 9 4-9 4-9-4ZM3 7v10l9 4 9-4V7M12 11v10',
  retirados:'M8 4h8l1 3-2 2v12H9V9L7 7Z'
};
function buildEquiposLanding(order){
  const wrap=el('div');
  const activeN=FKEYS.filter(k=>F[k].active).length, goneN=FKEYS.length-activeN;
  /* PHASE_40B (owner-approved, redesign-v2): the #3 stat's number AND its own
     gap clause both come from champOf (web/index.html's DERIVED section) --
     the real per-year "who won" map every YEARS entry gets checked against
     when a champion is recorded, not a second, separately-derived count that
     could silently drift from it. missingYears is the same YEARS/champOf
     pair as champOf's own build; the clause text is 0/1/N-driven, never
     hardcoded -- today that's exactly [1953] (no source consulted records a
     1953 champion, per NOTES[1953] above), the ONE already-known case. */
  const titlesN=Object.keys(champOf).length;
  const missingYears=YEARS.filter(y=>!(y in champOf));
  const titlesGap = missingYears.length===0 ? ''
    : missingYears.length===1 ? ' — falta el de '+missingYears[0]
    : ' — faltan '+missingYears.length;
  const stats=el('div','stats3');
  stats.innerHTML=`
    <div class="stat solid"><div class="n mono">${activeN}</div>
      <div class="l">Clubes activos en el BSN hoy</div></div>
    <div class="stat"><div class="n mono">${goneN}</div>
      <div class="l">Franquicias que ya no existen, con su historial de finales</div></div>
    <div class="stat"><div class="n mono">${titlesN}</div>
      <div class="l">Campeonatos en el archivo${esc(titlesGap)}</div></div>`;
  wrap.appendChild(stats);
  const h2=el('h2','sec'); h2.textContent='Explora Equipos'; wrap.appendChild(h2);
  const grid=el('div','explore');
  const D=VIEW_DESC.equipos||{};
  order.forEach(([slug,label])=>{
    const b=el('button','xcard'); b.type='button';
    b.innerHTML=`<span class="go" aria-hidden="true">→</span>
      <span class="ic"><svg viewBox="0 0 24 24"><path d="${EQUIPOS_XICON[slug]||''}" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span class="t">${esc(label)}</span>
      <span class="d">${esc(D[slug]||'')}</span>`;
    b.onclick=()=>showView('equipos',slug);
    grid.appendChild(b);
  });
  wrap.appendChild(grid);
  return wrap;
}
/* PHASE_44 (owner-approved, redesign-v2): Juega's own hero, same mechanism as
   buildHistoriaHero()/buildJugadoresHero()/buildEquiposHero() above -- the PHASE_43
   survey's own finding was that Juega never got this pass at all (no buildJuegaHero()
   existed, no buildJuegaLanding() either -- out of scope this phase, the existing
   .shelf/.tile gameShelf stays as Juega's own equivalent component, untouched). The
   lede's own meaning is unchanged from the static fallback (web/index.html's own
   .phead, also unchanged this phase since it already reads identically) -- only the
   count word is now computed from GAMES.length via numWordsEs() instead of the literal
   "Cuatro", so it can't silently go stale the way Equipos' own "veinte" bug did. */
function buildJuegaHero(){
  const head=document.querySelector('#juega .phead'); if(!head) return;
  head.classList.add('hhero');
  const wn=numWordsEs(GAMES.length);
  const lede=wn[0].toUpperCase()+wn.slice(1)+' juegos sobre el archivo. Todos usan la'
    +' misma nómina verificada de jugadores, así que ninguno inventa una respuesta.';
  head.innerHTML=`<div class="eyebrow">EL ARCHIVO DEL BSN</div>
    <h1>Juega</h1>
    <p class="lede">${lede}</p>`;
}
function buildEquiposHero(){
  const head=document.querySelector('#equipos .phead'); if(!head) return;
  head.classList.add('hhero');
  const activeN=FKEYS.filter(k=>F[k].active).length, goneN=FKEYS.length-activeN;
  const wa=numWordsEs(activeN), wg=numWordsEs(goneN);
  const lede=wa[0].toUpperCase()+wa.slice(1)+' clubes activos y '+wg
    +' que ya no existen. Cada uno con su historial de finales.';
  head.innerHTML=`<div class="eyebrow">EL ARCHIVO DEL BSN</div>
    <h1>Equipos</h1>
    <p class="lede">${lede}</p>`;
}
/* PHASE_49 (owner-approved, redesign-v2): Archivo's own hero, same mechanism as the
   4 above -- the PHASE_48 survey's own finding was that Archivo never got this pass
   at all (no buildArchivoHero() existed, the exact "one section still looks like the
   old app" gap that survey flagged as its #2 finding). h1/lede reused verbatim from
   the existing static .phead (web/index.html:444-448) -- no new copy, task's own
   explicit "NO new Spanish strings" instruction.
   No eyebrow here, unlike the other 4: the only candidate text that "already covers"
   an eyebrow slot is the literal "EL ARCHIVO DEL BSN" every other hero already uses
   -- but Archivo's own h1 is "El archivo", so that eyebrow would read as "EL ARCHIVO
   DEL BSN" directly above "El archivo", repeating the word immediately. Reusing it
   here isn't really reuse in spirit, it's a worse result from the same bytes; the
   task's own wording ("no eyebrow unless an existing string already covers it")
   reads as permission to omit, not a mandate to force a fit. No new eyebrow string
   proposed either -- omission needs none. */
function buildArchivoHero(){
  const head=document.querySelector('#archivo .phead'); if(!head) return;
  head.classList.add('hhero');
  head.innerHTML=`<h1>El archivo</h1>
    <p class="lede">Pregúntale directamente, o mira qué tiene, qué le falta y de dónde sale cada dato. Un archivo que esconde sus huecos vale menos que uno que los enseña.</p>`;
}
/* PHASE_11 (owner-approved, redesign-v2): Premios subtab split (item 9) -- real markup
   surgery on buildViews()'s already-built #historia .view[data-view="premios"] (moves
   existing element references, appends/creates none of the underlying data containers --
   #mvpYears/#scoringChart/#scoringTable/#seasonAwards keep their own ids and builders
   untouched). Grouped by matching each h4.sub's own real text, not by position, so this
   stays correct even if the real DOM order ever shifts. "Premios por temporada"
   (SEASON_AWARDS, its own real year-filter + table) is item 11's "leave existing real
   data/interactivity untouched" case -- not folded into the 2-tab toggle the mockup itself
   only has for scoring/MVP, kept as its own always-visible block below both tabs, exactly
   the real content/interactivity it already had, only visually placed under the new
   subtab area (a deliberate placement call, reported in this pass's own report). */
function restructurePremios(){
  const view=document.querySelector('#historia .view[data-view="premios"]'); if(!view) return;
  const kids=Array.from(view.children);
  const head=kids.find(n=>n.classList&&n.classList.contains('viewhead'));
  const groups={mvp:[],temporada:[],scoring:[]};
  let cur=null;
  kids.forEach(n=>{
    if(n===head) return;
    if(n.tagName==='H4'){
      const t=norm(n.textContent);
      cur = t.indexOf('mvp')===0 ? 'mvp' : t.indexOf('premios por temporada')===0 ? 'temporada'
        : t.indexOf('campeones de anotaci')===0 ? 'scoring' : null;
      if(cur) groups[cur].push(n); return;
    }
    if(cur) groups[cur].push(n);
  });
  if(!groups.scoring.length && !groups.mvp.length) return;   /* already restructured, or markup missing */
  const subtab=el('div','subtab'); subtab.setAttribute('role','tablist');
  const scoringWrap=el('div'); groups.scoring.forEach(n=>scoringWrap.appendChild(n));
  const mvpWrap=el('div'); groups.mvp.forEach(n=>mvpWrap.appendChild(n)); mvpWrap.hidden=true;
  const bScoring=el('button'); bScoring.type='button'; bScoring.textContent='Campeones de anotación';
  bScoring.setAttribute('aria-current','true');
  const bMvp=el('button'); bMvp.type='button'; bMvp.textContent='MVP'; bMvp.setAttribute('aria-current','false');
  const flip=(showScoring)=>{
    bScoring.setAttribute('aria-current',String(showScoring));
    bMvp.setAttribute('aria-current',String(!showScoring));
    scoringWrap.hidden=!showScoring; mvpWrap.hidden=showScoring;
  };
  bScoring.onclick=()=>flip(true); bMvp.onclick=()=>flip(false);
  subtab.appendChild(bScoring); subtab.appendChild(bMvp);
  const rest=el('div'); groups.temporada.forEach(n=>rest.appendChild(n));
  view.innerHTML='';
  if(head) view.appendChild(head);
  view.appendChild(subtab); view.appendChild(scoringWrap); view.appendChild(mvpWrap); view.appendChild(rest);
}
/* PHASE_12 (owner-approved, redesign-v2): "La liga ahora" accordion skin (item 6's own
   preamble) -- a one-time DOM pass over the REAL <details class="liga"> elements, adding an
   icon + a subtitle (copied from each accordion's own real <p class="lede">, not new text)
   + a chevron SVG into each real <summary>. Does NOT touch ligaFold() (init.js) at all --
   that function only ever sets .open on these same real elements and still runs exactly as
   before, same 860px breakpoint, same open/closed rule. Matched by each accordion's own
   real h4 text, not by position, so this stays correct even if their order ever changes. */
/* Keys are pre-normalized (norm() strips accents/case -- 'ó'->'o' etc.) so the lookup in
   buildLigaAccordionSkin() below, which calls norm(title) on the real h4 text, actually
   matches -- an earlier draft of this map kept the accented spelling here and silently
   matched nothing; caught live before this was ever reported working. */
const LIGA_ICON={
  'lo proximo':'M12 2.7a9.3 9.3 0 1 0 0 18.6 9.3 9.3 0 0 0 0-18.6Zm0 4.6v5l3 3',
  'la final brava 2026':'M12 2l2.6 6.6L21 9l-5 4.6L17.4 21 12 17.3 6.6 21 8 13.6 3 9l6.4-.4Z',
  'finales anteriores, juego a juego':'M4 5h16M4 12h16M4 19h16',
  'posiciones bsn 2026':'M4 19V10M10 19V5M16 19v-7M4 5h.01',
  'lideres 2026':'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4 21c0-4 4-6 8-6s8 2 8 6',
  'canales oficiales':'M12 2a9 9 0 1 0 .01 0M3 12h18M12 3c3 4 3 14 0 18M12 3c-3 4-3 14 0 18'
};
function buildLigaAccordionSkin(){
  document.querySelectorAll('#inicio .liga').forEach(d=>{
    if(d.querySelector('.acc-sum-chev')) return;   /* already skinned (e.g. a re-run) */
    const h4=d.querySelector(':scope > summary h4'); if(!h4) return;
    const title=h4.textContent;
    const sub=d.querySelector(':scope > p.lede');
    const icon=LIGA_ICON[norm(title)]||'';
    const summary=d.querySelector(':scope > summary');
    summary.classList.add('acc-sum-chev');
    summary.innerHTML=`<span class="acc-ic"><svg viewBox="0 0 24 24"><path d="${icon}" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span class="acc-t"><span class="acc-title">${esc(title)}</span>${sub?`<span class="acc-sub">${esc(sub.textContent)}</span>`:''}</span>
      <svg class="chev" viewBox="0 0 24 24" width="18" height="18"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
  });
}
function buildLanding(sec,order){
  if(sec==='historia') return buildHistoriaLanding(order);
  if(sec==='jugadores') return buildJugadoresLanding(order);
  if(sec==='equipos') return buildEquiposLanding(order);
  const wrap=el('div','landing');
  const feat=el('div','mega-feat'); feat.innerHTML=megaFeat(NAV_MENU[sec].feat);
  wrap.appendChild(feat);
  const grid=el('div','landgrid');
  const D=VIEW_DESC[sec]||{};
  order.forEach(([slug,label])=>{
    const a=el('a','landcard'); a.href='#'+sec+'/'+slug;
    a.innerHTML=`<span class="lc-t">${esc(label)}<i aria-hidden="true">→</i></span>`
      + (D[slug]?`<span class="lc-d">${esc(D[slug])}</span>`:'');
    a.onclick=e=>{ e.preventDefault(); showView(sec,slug); };
    grid.appendChild(a);
  });
  wrap.appendChild(grid);
  return wrap;
}
function buildJuegaViews(panel){
  const phead=panel.querySelector(':scope > .phead');
  const stages=Array.from(panel.querySelectorAll(':scope > .stage'));
  const land=_mkView('juega','__landing');
  Array.from(panel.children).forEach(n=>{
    if(n===phead || (n.classList&&n.classList.contains('stage'))) return;
    land.appendChild(n);                       /* streakStrip, storageNote, gameShelf */
  });
  const order=[];
  stages.forEach(s=>{
    s.classList.add('view'); s.dataset.view=s.id.replace('stage-',''); s.dataset.sec='juega'; s.hidden=true;
    const g=GAMES.find(x=>x.id===s.dataset.view);
    order.push([s.dataset.view, g?g.t:s.dataset.view]);
    /* PHASE_44 (owner-approved, redesign-v2): the "‹ Juegos" stagebar used to be typed
       out byte-for-byte 4 times in web/index.html (once per <div class="stage">) --
       same label, class and onclick="closeGame()" every time, a pure drift risk (one
       edited without the other three) with no behavior depending on the static markup
       itself (closeGame()/the Escape handler both only ever touch GAME_OPEN/showView(),
       never query .stagebar) -- confirmed before doing this. Generated here once instead,
       same label/class/behavior, title straight from GAMES' own real [id,t] pair. */
    const bar=el('div','stagebar');
    bar.innerHTML=`<button class="btn" onclick="closeGame()">‹ Juegos</button><span class="stagetitle">${esc(g?g.t:s.dataset.view)}</span>`;
    s.insertBefore(bar,s.firstChild);
  });
  panel.insertBefore(_subnavEl('juega',order,'Juegos'), phead?phead.nextSibling:panel.firstChild);
  panel.insertBefore(land, panel.querySelector(':scope > .subnav').nextSibling);
  stages.forEach(s=>panel.appendChild(s));
  VIEW_NOW.juega='__landing'; syncSubnav('juega','__landing');
}
function buildViews(){
  VIEW_SECS.forEach(sec=>{
    const S=document.getElementById(sec); if(!S) return;
    const panel=S.querySelector(':scope > .panel'); if(!panel) return;
    if(sec==='juega'){ buildJuegaViews(panel); return; }
    const cfg=VIEW_MAP[sec], phead=panel.querySelector(':scope > .phead');
    (cfg.drop||[]).forEach(sel=>{ const e=panel.querySelector(sel); if(e) e.remove(); });
    const host = cfg.host ? panel.querySelector(cfg.host) : panel;
    if(!host) return;
    const kids=Array.from(host.children).filter(n=>n!==phead);
    const isHead=n=>n.matches && n.matches(cfg.split);
    const order=[];
    /* group: nodes before the first heading, then one group per heading */
    let pre=[], groups=[], cur=null;
    kids.forEach(n=>{
      if(isHead(n)){ cur={head:n,nodes:[]}; groups.push(cur); }
      else if(cur) cur.nodes.push(n);
      else pre.push(n);
    });
    /* pre view */
    if(cfg.pre && pre.length){
      const v=_mkView(sec,cfg.pre[0]);
      pre.forEach(n=>v.appendChild(n));
      panel.appendChild(v); order.push(cfg.pre);
    }
    /* adopt an existing container (Comparar) */
    (cfg.adopt||[]).forEach(a=>{
      const e=panel.querySelector(a[0])||S.querySelector(a[0]);
      if(e){ e.classList.add('view'); e.dataset.view=a[1]; e.dataset.sec=sec; e.hidden=true;
        if(!e.querySelector(':scope > .viewhead')){ const hd=el('h2','viewhead'); hd.textContent=a[2]; e.insertBefore(hd,e.firstChild); }
        panel.appendChild(e); order.push([a[1],a[2]]); }
    });
    /* heading views */
    groups.forEach(g=>{
      const found=(cfg.map||[]).find(m=>norm(g.head.textContent).indexOf(norm(m[0]))===0);
      const vslug = found ? found[1][0] : slug_(g.head.textContent);
      const label = found ? found[1][1] : g.head.textContent;
      const v=_mkView(sec,vslug);
      const hd=el('h2','viewhead'); hd.textContent=g.head.textContent; v.appendChild(hd);
      g.nodes.forEach(n=>v.appendChild(n));
      g.head.remove();
      panel.appendChild(v); order.push([vslug,label]);
    });
    /* detail-only view, reached via showTeam / deep link (not in the subnav) */
    if(cfg.detail){
      const v=_mkView(sec,cfg.detail[0]);
      const d=panel.querySelector(cfg.detail[1]);
      v.appendChild(d||el('div'));
      panel.appendChild(v);
    }
    /* drop an emptied host wrapper (jugBuscar) */
    if(cfg.host){ const hw=panel.querySelector(cfg.host); if(hw && !hw.children.length) hw.remove(); }
    /* landing + subnav */
    const land=_mkView(sec,'__landing');
    land.appendChild(buildLanding(sec,order));
    const firstView=panel.querySelector(':scope > .view');
    panel.insertBefore(land, firstView);
    panel.insertBefore(_subnavEl(sec,order), phead?phead.nextSibling:panel.firstChild);
    VIEW_NOW[sec]='__landing'; syncSubnav(sec,'__landing');
  });
}
const slug_=s=>slug(s).split('-').slice(0,3).join('-')||'v';

/* A deep link or a click-through can target a node inside a hidden
   view; surface that view first (scrolling to display:none does nothing). */
function revealNode(node){
  let n=node;
  while(n && n.nodeType===1){
    if(n.classList && n.classList.contains('view') && n.hidden && n.dataset.sec){
      showView(n.dataset.sec, n.dataset.view, {noScroll:true, noHash:true});
      return;
    }
    n=n.parentNode;
  }
}

function applyHash(){
  let raw=(location.hash||'').replace(/^#/,'');
  if(HASH_ECHO!==null && raw===HASH_ECHO){ HASH_ECHO=null; return; }
  HASH_ECHO=null;
  if(!raw){ showTab('inicio'); return; }
  let p=raw.split('/');
  /* legacy single-token redirects (PHASE_6 + PHASE_8) */
  const MOVED={hoy:'inicio',calendario:'inicio',ahora:'inicio',
               records:'jugadores/records',refuerzos:'historia/refuerzos',
               consulta:'archivo/preguntar',fuentes:'archivo/cobertura'};
  if(p.length===1 && MOVED[p[0]]) p=MOVED[p[0]].split('/');
  /* legacy shape redirects */
  if(p[0]==='historia' && /^\d{4}$/.test(p[1]||'')) p=['historia','temporada',p[1]];
  if(p[0]==='historia' && p[1]==='records') p=['historia'];        /* PHASE_6 alias */
  if(p[0]==='equipos' && p[1] && F[p[1]]) p=['equipos','equipo',p[1]];
  if(p[0]==='jugador' && p[1]) p=['jugadores','jugador',p[1]];
  if(p[0]==='comparar') p=['jugadores','comparar',p[1],p[2]];
  const a=p[0], b=p[1], c=p[2];

  if(a==='jugadores' && b==='comparar'){
    showView('jugadores','comparar',{fromHash:true,noScroll:true});
    const nm=s=>{ const x=(PINDEX||[]).find(q=>slug(q.name)===s); return x?x.name:null; };
    const n1=nm(c), n2=nm(p[3]);
    if(n1&&n2) cmpPreset(n1,n2);
    else if(n1){ CMP=[n1]; drawCompare(); }
    return;
  }
  if(a==='jugadores' && b==='jugador' && c){
    showView('jugadores','buscar',{fromHash:true,noScroll:true});
    /* season_detail_spec.md §4 — optional 4th segment: #.../<slug>/<season>.
       An unknown/mistyped season is silently ignored (normal card, no
       per-season block) — never an error state for a bad deep link. */
    const season = p[3] && /^\d{4}$/.test(p[3]) ? +p[3] : null;
    /* PHASE_36: a merged nickname-form card changes its own canonical slug
       (mario-quijote-morales, not mario-morales) -- the second clause keeps
       the OLD plain-name URL resolving to that same card, by comparing c
       against the slug of the nickname-STRIPPED name instead of a second
       real property read (stripNick() is already a pure function of
       x.name, nothing new to look up). */
    const pl=PINDEX&&(PINDEX.find(x=>slug(x.name)===c) || PINDEX.find(x=>slug(stripNick(x.name))===c));
    if(pl) showPlayer(pl.name,null,season);
    else {
      const q=PSLUG&&PSLUG.get(c);
      if(q&&typeof openArchivePlayer==='function') openArchivePlayer(q.id,q.name,season);
      else {
        /* a retired player's old URL: open the survivor and replace the URL (no Back trap) */
        const to=PREDIR&&PREDIR.slugs[c], r=to!=null&&PBYID?PBYID.get(to):null;
        if(r&&typeof openArchivePlayer==='function'){
          history.replaceState(null,'','#jugadores/jugador/'+USLUG.get(r.id)+(season!=null?'/'+season:''));
          openArchivePlayer(r.id,r.name,season);
        }
      }
    }
    return;
  }
  if(a==='equipos' && b==='equipo' && c && F[c]){ showTeam(c); return; }
  if(a==='historia' && b==='temporada' && /^\d{4}$/.test(c||'')){
    showView('historia','cinta',{fromHash:true,noScroll:true});
    if(typeof showSeason==='function') showSeason(+c);
    return;
  }
  if(a==='juega' && b && GAMES.some(g=>g.id===b)){ showView('juega',b,{fromHash:true}); GAME_OPEN=b; return; }

  if(PANELS.includes(a)){
    if(b && VIEW_SECS.indexOf(a)>-1) showView(a,b,{fromHash:true});
    else showTab(a);
    return;
  }
  showTab('inicio');
}
/* ============================================================
   EXPANSIÓN DE JUGADORES Y PREMIOS — 3 sep 2026

   Everything here was pulled this session from English Wikipedia's
   BSN season pages (2009, 2016, 2017, 2018, 2024, 2025, 2026), the
   BSN MVP award page, the league's main article, and Puerto Rican
   press. It exists to close the hole the archive had between 1995
   and 2020 — the era most fans actually remember, and the era in
   which the archive previously knew almost nobody.

   Club fields are left empty where the source names a player but
   not his team. An empty club is a recorded gap, not an oversight.
   ============================================================ */

/* ---- MVP por año ----
   Wikipedia renders the full year-by-year MVP table inside a
   sortable widget that does not survive text extraction. The
   repeat-winners table does survive, and it carries years AND
   clubs — so these 30 seasons are recovered. Single-time winners
   remain unextractable and are listed as a known gap. */
const MVP_YEARS=[
  [1951,'Raúl «Tinajón» Feliciano','Gallitos de la UPR'],
  [1952,'Juan «Pachín» Vicéns','Leones de Ponce'],
  [1954,'Juan «Pachín» Vicéns','Leones de Ponce'],
  [1955,'Raúl «Tinajón» Feliciano','Cardenales de Río Piedras'],
  [1957,'Juan Báez','Cardenales de Río Piedras'],
  [1958,'Juan «Pachín» Vicéns','Leones de Ponce'],
  [1960,'Juan «Pachín» Vicéns','Leones de Ponce'],
  [1962,'Teófilo Cruz','Cangrejeros de Santurce'],
  [1963,'Juan Báez','Cardenales de Río Piedras'],
  [1964,'Juan Báez','Cardenales de Río Piedras'],
  [1967,'Teófilo Cruz','Cangrejeros de Santurce'],
  [1968,'Raymond Dalmau','Piratas de Quebradillas'],
  [1969,'Raymond Dalmau','Piratas de Quebradillas'],
  [1970,'Teófilo Cruz','Cangrejeros de Santurce'],
  [1971,'Teófilo Cruz','Cangrejeros de Santurce'],
  [1972,'Raymond Dalmau','Piratas de Quebradillas'],
  [1980,'Mario «Quijote» Morales','Mets de Guaynabo'],
  [1981,'Rolando Frazer','Polluelos de Aibonito'],
  [1982,'Mario «Quijote» Morales','Mets de Guaynabo'],
  [1983,'Mario «Quijote» Morales','Mets de Guaynabo'],
  [1984,'Georgie Torres','Cariduros de Fajardo'],
  [1985,'Georgie Torres','Cariduros de Fajardo'],
  [1986,'Georgie Torres','Cariduros de Fajardo'],
  [1987,'Rolando Frazer','Polluelos de Aibonito'],
  [1991,'James Carter','Brujos de Guayama'],
  [1993,'Mario «Quijote» Morales','Mets de Guaynabo'],
  [1994,'James Carter','Brujos de Guayama'],
  [2004,'Christian Dalmau','Atléticos de San Germán'],
  [2009,'Jesse Pellot','Atléticos de San Germán'],
  [2010,'Christian Dalmau','Vaqueros de Bayamón'],
  [2011,'Christian Dalmau','Vaqueros de Bayamón'],
  [2014,'Walter Hodge','Capitanes de Arecibo'],
  [2016,'Ángel Daniel Vassallo','—'],
  [2017,'Gary Browne','—'],
  [2018,'Reyshawn Terry','Piratas de Quebradillas'],
  [2022,'Walter Hodge','Capitanes de Arecibo'],
  [2024,'Travis Trice','Criollos de Caguas'],
  [2025,'Emmanuel Mudiay','Piratas de Quebradillas'],
  [2026,'Travis Trice','Criollos de Caguas']
];

/* ---- Premios y líderes por temporada ----
   [year, category, player, club, line] */
const SEASON_AWARDS=[
  [2009,'Más Valioso','Jesse Pellot','Atléticos de San Germán',''],
  [2009,'Líder de anotación','Jesse Pellot','Atléticos de San Germán',''],
  [2009,'MVP de la final','Christian Dalmau','Vaqueros de Bayamón',''],
  [2009,'Primera selección del sorteo','Darnell Hinson','Caciques de Humacao',''],
  [2016,'Más Valioso','Ángel Daniel Vassallo','—',''],
  [2016,'MVP de la final','Renaldo Balkman','Capitanes de Arecibo',''],
  [2016,'Líder de anotación','Damion James','—',''],
  [2016,'Líder de rebotes','Damion James','—',''],
  [2016,'Líder de asistencias','Alex Abreu','—',''],
  [2017,'Más Valioso','Gary Browne','—',''],
  [2017,'Progreso del Año','Gary Browne','—',''],
  [2017,'MVP de la final','Tu Holloway','Piratas de Quebradillas',''],
  [2017,'Líder de anotación','Víctor Liz','—',''],
  [2017,'Líder de rebotes','Eric Dawson','—',''],
  [2017,'Líder de asistencias','Gary Browne','—',''],
  [2018,'Más Valioso','Reyshawn Terry','Piratas de Quebradillas','36 juegos, 835 puntos, 23.2 por juego'],
  [2018,'MVP de la final','Walter Hodge','Capitanes de Arecibo',''],
  [2018,'Líder de anotación','Reyshawn Terry','Piratas de Quebradillas','835 puntos'],
  [2018,'Líder de rebotes','Reyshawn Terry','Piratas de Quebradillas',''],
  [2018,'Líder de asistencias','Carlos Arroyo','Cariduros de Fajardo',''],
  [2018,'2.º en anotación','Brandon Costner','Caciques de Humacao','34 juegos, 668 puntos, 19.6'],
  [2024,'Más Valioso','Travis Trice','Criollos de Caguas','20.7 pts, 7.2 ast, 3.5 reb'],
  [2024,'Defensor del Año','George Conditt IV','Gigantes de Carolina','14.6 pts, 9.2 reb'],
  [2024,'Novato del Año','Jhivvan Jackson','Osos de Manatí','12.0 pts, 2.9 ast, 2.7 reb'],
  [2024,'Sexto Hombre','Emmanuel Maldonado','Cangrejeros de Santurce','8.0 pts, 2.1 reb'],
  [2024,'Progreso del Año','Alfonso Plummer','Capitanes de Arecibo','18.9 pts, 3.8 ast, 3.1 reb'],
  [2024,'Dirigente del Año','Juan Cardona','Capitanes de Arecibo',''],
  [2024,'Gerente del Año','José Manuel Baeza','Capitanes de Arecibo',''],
  [2024,'MVP de la final','Travis Trice','Criollos de Caguas','20.9 pts, 6.1 ast'],
  [2025,'Más Valioso','Emmanuel Mudiay','Piratas de Quebradillas','23.6 pts, 5.8 ast, 4.5 reb'],
  [2025,'Defensor del Año','JaVale McGee','Vaqueros de Bayamón','17.4 pts, 8.4 reb, 1.6 tapones'],
  [2025,'Novato del Año','André Curbelo','Atléticos de San Germán',''],
  [2025,'MVP de la final','Danilo Gallinari','Vaqueros de Bayamón',''],
  [2025,'Líder de anotación','Emmanuel Mudiay','Piratas de Quebradillas','779 puntos en 33 juegos'],
  [2025,'Líder de rebotes','Akil Mitchell','—',''],
  [2025,'Líder de asistencias','Ángel Rodríguez','—',''],
  [2026,'Más Valioso','Travis Trice','Criollos de Caguas','Su segundo MVP'],
  [2026,'MVP de la final','Renaldo Balkman','Vaqueros de Bayamón','A los 41 años'],
  [2026,'Dirigente del Año','Christian Dalmau','Vaqueros de Bayamón',''],
  [2026,'Progreso del Año','André Curbelo','Atléticos de San Germán',''],
  [2026,'Novato del Año','Daniel Rivera','Gigantes de Carolina',''],
  [2026,'Defensor del Año','Moses Brown','Criollos de Caguas','Según RealGM'],
  [2026,'Sexto Hombre','Christian López','Criollos de Caguas','Según RealGM'],
  [2026,'Líder de anotación','K. Davis','Osos de Manatí','23.4 por juego']
];

/* ---- Finales juego a juego, las que se pudieron reconstruir ---- */
const FINALS_BY_YEAR={
  2026:{champ:'bay',ru:'agu',series:'4-3',mvp:'Renaldo Balkman',
    games:FINALS_2026.games.map(g=>[g[0],g[1],g[2],g[3],g[4],g[5],g[6],''])},
  2025:{champ:'bay',ru:'pon',series:'4-1',mvp:'Danilo Gallinari',
    games:[[1,'3 ago','bay','pon',92,76,'1-0','19-25, 18-12, 14-31, 25-24'],
           [2,'5 ago','pon','bay',90,76,'1-1',''],
           [3,'7 ago','bay','pon',100,79,'2-1',''],
           [4,'9 ago','pon','bay',79,88,'3-1',''],
           [5,'11 ago','bay','pon',82,68,'4-1','']]},
  2024:{champ:'cag',ru:'man',series:'4-3',mvp:'Travis Trice',
    games:[[1,'17 ago','cag','man',99,105,'0-1','31-18, 23-26, 29-27, 22-28'],
           [2,'19 ago','man','cag',104,109,'1-1','29-21, 22-24, 22-26, 26-28 · tiempo extra'],
           [3,'21 ago','cag','man',85,89,'1-2','23-25, 30-19, 19-22, 17-19'],
           [4,'23 ago','man','cag',86,91,'2-2','24-29, 23-16, 23-17, 21-24'],
           [5,'25 ago','cag','man',89,98,'2-3','18-16, 29-19, 27-31, 24-23'],
           [6,'27 ago','man','cag',121,122,'3-3','23-22, 18-19, 19-24, 31-26 · doble tiempo extra'],
           [7,'30 ago','cag','man',96,81,'4-3','20-19, 25-30, 13-26, 23-21']]}
};

/* ---- Dueños ---- */
const OWNERS=[
  ['bay','Eric «Duars» Pérez y Carlos Arroyo','Compraron la franquicia en diciembre de 2024 a Yadier Molina, que la había adquirido en octubre de 2020. Ganaron el título en su primera temporada.'],
  ['san','Noah Assad, Jonathan Miranda y Bad Bunny','El club volvió al BSN en abril de 2021; Bad Bunny se sumó al grupo dueño ese mismo mes.'],
  ['man','Ozuna','Compró a los Brujos de Guayama en octubre de 2022 y los mudó a Manatí como los Osos.'],
  ['cag','John Herrero','Empujó la regla de los tres refuerzos a toda la liga tras ganar con tres en 2024.'],
  ['agu','Wilson López','']
];

