/* PHASE_1_SPLIT STEP 3. The big hand-curated constants, moved out of web/index.html's
   inline <script> byte for byte -- no renaming, no reformatting, no reordering among
   themselves. Loaded via <script src="js/data.js"> before any other extracted script,
   so everything below is defined before the rest of the app runs.

   This is a straight extraction, not a reorganization: each block below keeps its own
   original header comment (the ones that actually describe IT -- section dividers and
   comments describing code that stays behind in web/index.html were left there). The
   13 blocks are NOT contiguous in the original file; the gaps between them (mostly
   other constants -- ARENAS, LEADERS, STONE, NEWS, POOL_BSN26, MVP_YEARS, OWNERS, etc,
   and some executable patch statements like F.agu.ru.push(2026)) stay in
   web/index.html, in their original relative order, untouched. tests/_app_text.py
   knows how to splice this file and web/index.html back into the exact original byte
   stream; see it for the precise boundaries. Replaced entirely once
   app/bsn_archivo.html becomes the archived pointer (step 11/12 of the split). */

const F = {
  bay:{name:"Vaqueros de Bayamón",abbr:"BAY",city:"Bayamón",founded:1930,active:1,c1:"#1B4F9C",c2:"#E8B23A",colorSrc:"wiki",
       art:"vaquero",
       coach:"Christian Dalmau",
       won:[1933,1935,1967,1969,1971,1972,1973,1974,1975,1981,1988,1995,1996,2009,2020,2022,2025,2026],
       ru:[1930,1934,1970,2001,2002,2005,2010,2016,2018,2023]},
  sge:{name:"Atléticos de San Germán",abbr:"SG",city:"San Germán",founded:1930,active:1,c1:"#F26A21",c2:"#141414",colorSrc:"wiki",
       coach:"Eddie Casiano",
       won:[1932,1938,1939,1941,1942,1947,1948,1949,1950,1985,1991,1994,1997],
       ru:[1931,1933,1936,1940,1954,1955,1956,1957,1965,1986,2022]},
  pon:{name:"Leones de Ponce",abbr:"PON",city:"Ponce",founded:1946,active:1,c1:"#C8102E",c2:"#F0C24B",colorSrc:"approx",
       art:"leon",
       won:[1952,1954,1960,1961,1964,1965,1966,1990,1992,1993,2002,2004,2014,2015],
       ru:[1949,1958,1963,1967,1989,1995,1996,1998,2003,2013,2019,2025]},
  san:{name:"Cangrejeros de Santurce",abbr:"SAN",city:"Santurce",founded:1918,active:1,c1:"#E85D1F",c2:"#191919",colorSrc:"approx",
       art:"cangrejo",
       won:[1962,1968,1998,1999,2000,2001,2003,2007],ru:[1942,1951,1952,1964,2006]},
  are:{name:"Capitanes de Arecibo",abbr:"ARE",city:"Arecibo",founded:1946,active:1,c1:"#0E7C7B",c2:"#F2F2F2",colorSrc:"approx",
       art:"ancla",
       won:[1959,2005,2008,2010,2011,2016,2018,2021],
       ru:[1932,1946,1948,1961,1966,1992,2007,2012,2014,2015,2017]},
  que:{name:"Piratas de Quebradillas",abbr:"QUE",city:"Quebradillas",founded:1926,active:1,c1:"#B3141F",c2:"#1A1A1A",colorSrc:"wiki",
       art:"pirata",
       coach:"Ángel Daniel Vassallo",
       won:[1970,1977,1978,1979,2013,2017],
       ru:[1937,1972,1973,1975,1976,1980,1982,1999,2000,2009,2011,2020]},
  gua:{name:"Mets de Guaynabo",abbr:"GBO",city:"Guaynabo",founded:1935,active:1,c1:"#122E5C",c2:"#25C4E0",colorSrc:"wiki",
       coach:"Jorge Rincón",
       won:[1980,1982,1989],ru:[1978,1981,1983,1985,1990,1993,2021]},
  cag:{name:"Criollos de Caguas",abbr:"CAG",city:"Caguas",founded:1976,active:1,c1:"#6B2C8F",c2:"#EFD25C",colorSrc:"approx",
       won:[2006,2024],ru:[]},
  car:{name:"Gigantes de Carolina/Canóvanas",abbr:"CAR",city:"Carolina/Canóvanas",founded:1971,active:1,c1:"#1E9B54",c2:"#F5F5F5",colorSrc:"approx",
       art:"gigante",
       won:[2023],ru:[1979,1997,2008]},
  may:{name:"Indios de Mayagüez",abbr:"MAY",city:"Mayagüez",founded:1956,active:1,c1:"#1F5B3A",c2:"#D9342B",colorSrc:"wiki",
       coach:"Iván Vélez",
       won:[2012],ru:[]},
  agu:{name:"Santeros de Aguada",abbr:"AGU",city:"Aguada",founded:1992,active:1,c1:"#0C4DA2",c2:"#F0A81E",colorSrc:"approx",
       won:[2019],ru:[]},
  man:{name:"Osos de Manatí",abbr:"MAN",city:"Manatí",founded:2014,active:1,c1:"#7A4A22",c2:"#E4C07A",colorSrc:"approx",
       art:"oso",
       won:[],ru:[2024]},

  cap:{name:"Capitalinos de San Juan",abbr:"SJ",city:"San Juan",founded:1930,active:0,end:1998,c1:"#8E1B3C",c2:"#E2C9A0",colorSrc:"approx",
       won:[1930,1931,1940,1945,1958],ru:[1943,1944,1950,1974]},
  rio:{name:"Cardenales de Río Piedras",abbr:"RP",city:"Río Piedras",founded:1940,active:0,end:1985,c1:"#A81F2E",c2:"#2B2B2B",colorSrc:"approx",
       won:[1946,1955,1956,1957,1963,1976],ru:[1941,1947,1959,1960,1962,1968,1969,1971,1977]},
  veg:{name:"Vega Baja",abbr:"VB",city:"Vega Baja",founded:1934,active:0,end:1939,c1:"#2F6E8F",c2:"#EDE3D0",colorSrc:"approx",
       won:[1934,1937],ru:[1935,1939]},
  upr:{name:"Gallitos de la UPR",abbr:"UPR",city:"Río Piedras",founded:1944,active:0,end:1951,c1:"#4B7A2B",c2:"#F1E7B8",colorSrc:"approx",
       art:"gallo",
       won:[1944,1951],ru:[1945]},
  cno:{name:"Indios de Canóvanas",abbr:"CAN",city:"Canóvanas",founded:1980,active:0,end:1996,c1:"#B65418",c2:"#2A2A2A",colorSrc:"approx",
       won:[1983,1984],ru:[1988]},
  nau:{name:"Club Náutico de San Juan",abbr:"CN",city:"San Juan",founded:1936,active:0,end:1936,c1:"#1D6C8C",c2:"#F2F2F2",colorSrc:"approx",
       art:"timon",
       won:[1936],ru:[]},
  aib:{name:"Polluelos de Aibonito",abbr:"AIB",city:"Aibonito",founded:1977,active:0,end:2001,c1:"#2F8A3E",c2:"#F2D840",colorSrc:"wiki",
       art:"pollito",
       won:[1986],ru:[1987]},
  mor:{name:"Titanes de Morovis",abbr:"MOR",city:"Morovis",founded:1977,active:0,end:2006,c1:"#4A3F8C",c2:"#D8D2E8",colorSrc:"approx",
       art:"titan",
       won:[1987],ru:[]},
  toi:{name:"Cocoteros de Tortuguero",abbr:"TOR",city:"Tortuguero",founded:1943,active:0,end:1943,c1:"#5E7A2E",c2:"#EBE0BC",colorSrc:"approx",
       art:"cocotero",
       won:[1943],ru:[]},
  guy:{name:"Brujos de Guayama",abbr:"GUY",city:"Guayama",founded:1971,active:0,end:2022,c1:"#1A1A1A",c2:"#D4A63C",colorSrc:"wiki",
       won:[],ru:[1991,1994],note:"Bought in 2022 and relocated as the Osos de Manatí."},
  isa:{name:"Gallitos de Isabela",abbr:"ISA",city:"Isabela",founded:1969,active:0,end:2005,c1:"#9C1F5B",c2:"#F0E0C8",colorSrc:"approx",
       art:"gallo",
       won:[],ru:[1984]},
  coa:{name:"Maratonistas de Coamo",abbr:"COA",city:"Coamo",founded:1985,active:0,end:2015,c1:"#2A6F97",c2:"#F2C14E",colorSrc:"approx",
       art:"maratonista",
       won:[],ru:[2004]},
  faj:{name:"Cariduros de Fajardo",abbr:"FAJ",city:"Fajardo",founded:1973,active:0,end:2023,c1:"#7A1F3D",c2:"#E8D6A8",colorSrc:"approx",won:[],ru:[]},
  hum:{name:"Grises de Humacao",abbr:"HUM",city:"Humacao",founded:2005,active:0,end:2023,c1:"#5C6670",c2:"#D6DCE2",colorSrc:"approx",won:[],ru:[],
       note:"Sold in 2023 and rebranded as the Criollos de Caguas."},
  ate:{name:"Atenienses de Manatí",abbr:"ATE",city:"Manatí",founded:2014,active:0,end:2017,c1:"#3B5E3C",c2:"#E4D9B8",colorSrc:"approx",won:[],ru:[],
       note:"Se mudó a Fajardo en 2017."},
  vil:{name:"Avancinos de Villalba",abbr:"VIL",city:"Villalba",founded:1996,active:0,end:1998,c1:"#6B4E9E",c2:"#EDE4F5",colorSrc:"approx",won:[],ru:[]},
  cab:{name:"Taínos de Cabo Rojo",abbr:"CR",city:"Cabo Rojo",founded:1989,active:0,end:1993,c1:"#B5651D",c2:"#F2E2C4",colorSrc:"approx",won:[],ru:[],
       note:"The Indios de Mayagüez under a different name and city."},
  agd:{name:"Tiburones de Aguadilla",abbr:"AGD",city:"Aguadilla",founded:1990,active:0,end:1998,c1:"#1C6E8C",c2:"#DCE9EF",colorSrc:"approx",
       art:"tiburon",won:[],ru:[],
       note:"Merged with the Capitalinos in 1998 to revive the Cangrejeros."},
  con:{name:"Conquistadores de Aguada",abbr:"CON",city:"Aguada",founded:1994,active:0,end:1998,c1:"#8C6A1F",c2:"#F0E6C8",colorSrc:"approx",won:[],ru:[]},
  cay:{name:"Toritos de Cayey",abbr:"CAY",city:"Cayey",founded:2002,active:0,end:2004,c1:"#8C2F2F",c2:"#E8D2C0",colorSrc:"approx",
       art:"torito",won:[],ru:[]},
  cac:{name:"Caciques de Humacao",abbr:"CAC",city:"Humacao",founded:2009,active:0,end:2018,c1:"#7A2E3B",c2:"#E0C9A6",colorSrc:"approx",won:[],ru:[],
       note:"Distintos de los Grises de Humacao. Las fechas se infieren de las temporadas en que aparece en el archivo, no de una fuente que las declare."}
};
const RECENT=[
 {year:"2026",label:"97th season · 21 March – 28 June · two conferences",champ:"Vaqueros de Bayamón",ru:null,
  rows:[["Most valuable player","Travis Trice","Criollos de Caguas"],
        ["Finals MVP","Renaldo Balkman","Vaqueros de Bayamón"],
        ["Defender of the year","Moses Brown","Criollos de Caguas"],
        ["Most improved","Andre Curbelo","Atléticos de San Germán"],
        ["Rookie of the year","Daniel Rivera","Gigantes de Carolina"],
        ["Sixth man","Christian López","Criollos de Caguas"]],
  allstar:[["Moses Brown","C","Criollos de Caguas","7-2, 258 lb, 26"],
           ["Andre Curbelo","PG","Atléticos de San Germán","6-0, 167 lb, 24"],
           ["Montrezl Harrell","F","Atléticos de San Germán","6-7, 240 lb, 32"],
           ["Jaylen Nowell","SG","Gigantes de Carolina","6-4, 201 lb, 26"],
           ["Travis Trice","PG","Criollos de Caguas","6-2, 175 lb, 33"]],
  warn:"Awards come from RealGM, which labels this season 2025–26. Wikipedia's franchise table has not been updated past 2025, so Bayamón's eighteenth title is recorded here as provisional. The opener was Ponce at Mayagüez; Bayamón's imports were Jae Crowder, Jaylin Galloway and Xavier Cooks."},
 {year:"2025",label:"96th season · 22 March – 11 August · 34 games · 12 teams",champ:"Vaqueros de Bayamón",ru:"Leones de Ponce",
  rows:[["Most valuable player","Emmanuel Mudiay","Piratas de Quebradillas"],
        ["Finals MVP","Danilo Gallinari","Vaqueros de Bayamón"],
        ["Points leader","Emmanuel Mudiay","779 in 33 games — 23.6 per game"],
        ["Rebounds leader","Akil Mitchell","—"],
        ["Assists leader","Ángel Rodríguez","—"]],
  extra:[["Franchise title","17th","Regular season ended 30 June"],
         ["Points, 2nd","Kobi Simmons (Gigantes)","647 — 20.2"],
         ["Points, 3rd","Cheick Diallo (Manatí)","636 — 19.3"],
         ["Blocks leader","JaVale McGee (Bayamón)","40 in 25 games — 1.6"],
         ["Three-point leader","Iván Gandía (Aguada)","91 in 27 games at 44%"]]},
 {year:"2024",label:"95th season · 3 April – 30 August · 34 games · 12 teams",champ:"Criollos de Caguas",ru:"Osos de Manatí",
  rows:[["Most valuable player","Travis Trice","Criollos de Caguas"],
        ["Finals MVP","Travis Trice","20.9 points, 6.1 assists"],
        ["Most improved","Alfonso Plummer","Capitanes — 18.9 pts, 3.8 ast, 3.1 reb"],
        ["Coach of the year","Juan Cardona","Capitanes de Arecibo"],
        ["General manager of the year","José Manuel Baeza","Capitanes de Arecibo"]],
  extra:[["Regular season","3 April – 1 July","Play-in 10–12 July, playoffs from 13 July"],
         ["Format","Best-of-seven","Every round"],
         ["Caguas title","2nd","First since 2006"]]},
 {year:"2020",label:"Played in a hotel bubble, no crowds",champ:"Vaqueros de Bayamón",ru:"Piratas de Quebradillas",
  rows:[["Clinching game","84–75","Game 3 of the final"],
        ["Franchise title","15th","First since 2009"],
        ["Owner","Yadier Molina","Took over the club that October"]]},
 {year:"2017",label:"88th season · 10 teams",champ:"Piratas de Quebradillas",ru:"Capitanes de Arecibo",
  rows:[["Most valuable player","Gary Browne","—"],
        ["Finals MVP","Tu Holloway","Piratas de Quebradillas"],
        ["Points leader","Víctor Liz","—"],
        ["Rebounds leader","Eric Dawson","—"],
        ["Assists leader","Gary Browne","—"]],
  extra:[["Final","Game 7, 98–90 over Arecibo","Clinched 9 August"]]},
 {year:"2009",label:"89th season · 11 teams · 30 games each",champ:"Vaqueros de Bayamón",ru:"Piratas de Quebradillas",
  rows:[["Most valuable player","Jesse Pellot","Atléticos de San Germán"],
        ["Top scorer","Jesse Pellot","Atléticos de San Germán"],
        ["Finals MVP","Christian Dalmau","Vaqueros de Bayamón"],
        ["Top draft pick","Darnell Hinson","Caciques de Humacao"]],
  standings:[["Capitanes de Arecibo",23,7],["Piratas de Quebradillas",22,8],
    ["Cangrejeros de Santurce",21,9],["Vaqueros de Bayamón",20,10],
    ["Gigantes de Carolina",17,13],["Atléticos de San Germán",16,14],
    ["Indios de Mayagüez",14,16],["Leones de Ponce",13,17],
    ["Criollos de Caguas",8,22],["Mets de Guaynabo",7,23],["Caciques de Humacao",4,26]],
  extra:[["Note","Bayamón finished 4th and won","The only full set of standings in this archive"]]}
];

const HOF=[
 {n:"Georgie Torres",yrs:"1975–2001",pos:"SG",era:1975,pts:15863,gp:679,ppg:23.4,mvp:3,
  role:"The league's all-time leading scorer and the first Puerto Rican to sign an NBA contract.",
  hon:["All-time scoring leader","3× MVP","7× scoring champion"],
  note:"Played his first seven seasons before the three-point line existed."},
 {n:"Mario «Quijote» Morales",yrs:"1975–1998",pos:"SF",era:1975,pts:15293,gp:675,ppg:22.7,mvp:4,
  role:"Second all-time in points and joint-record holder for MVP awards.",
  hon:["4× MVP","Scoring champion 1980","Arena named for him"],
  note:"The Mets play at the Mario Morales Coliseum in Guaynabo."},
 {n:"Raymond Dalmau",yrs:"1966–1985",pos:"PG",era:1966,pts:11592,gp:537,ppg:21.6,mvp:3,
  role:"Retired in 1985 as the league leader in points, rebounds and assists simultaneously.",
  hon:["4× champion","3× MVP","Rookie of the year 1966","Arena named for him"],
  note:"Arrived from Harlem in 1966 as an import and stayed twenty years, all with Quebradillas. Later coached Puerto Rico."},
 {n:"Teófilo Cruz",yrs:"1957–1982",pos:"C",era:1957,pts:null,gp:584,ppg:null,mvp:4,
  role:"Twenty-five seasons at centre and a member of the FIBA Hall of Fame.",
  hon:["FIBA Hall of Fame","4× MVP","Scoring champion 1971"],
  note:"Started for Puerto Rico when the national team was among the strongest in the Americas."},
 {n:"Juan «Pachín» Vicéns",yrs:"1950s–60s",pos:"G",era:1950,pts:null,gp:null,ppg:null,mvp:4,
  role:"Named to the All-Tournament Team at the 1959 FIBA World Championship in Santiago.",
  hon:["4× MVP","1959 World Championship All-Tournament","Arena named for him"],
  note:"Ponce play at the Juan Pachín Vicéns Auditorium."},
 {n:"Rubén Rodríguez",yrs:"1969–1991",pos:"PF",era:1969,pts:11549,gp:631,ppg:18.3,mvp:0,
  role:"Set the league's early benchmarks in both scoring and rebounding.",
  hon:["Career rebounds record","810 points in 1978","Arena named for him"],
  note:"His 380 rebounds in 1978 stood for thirty years. Bayamón play in the coliseum bearing his name."},
 {n:"Neftalí Rivera",yrs:"1969–1980s",pos:"G",era:1969,pts:null,gp:null,ppg:null,mvp:0,
  role:"Holds the single-game scoring record that has stood since 1974.",
  hon:["79 points, 22 May 1974","Rookie of the year 1969","2× scoring champion"],
  note:"Thirty-four field goals in that game, every one a two-pointer. With Dalmau he formed Quebradillas' «Dynamic Duo»."},
 {n:"Mario Butler",yrs:"1980–2008",pos:"C",era:1980,pts:12252,gp:779,ppg:15.7,mvp:0,
  role:"Panamanian centre, the league's all-time leading rebounder and its most-capped player.",
  hon:["All-time rebounds leader","779 games, a record","3rd all-time in points"],
  note:"Twenty-eight seasons — the longest career in the archive."},
 {n:"Rolando Frazer",yrs:"1980–2001",pos:"C",era:1980,pts:12096,gp:603,ppg:20.1,mvp:0,
  role:"Panamanian centre who won back-to-back scoring titles for Aibonito.",
  hon:["2× scoring champion","4th all-time in points"],
  note:"Averaged 34.2 in 1982, the highest mark captured in this archive apart from Torres."},
 {n:"Christian Dalmau",yrs:"1992–2017",pos:"SG",era:1992,pts:10570,gp:639,ppg:16.5,mvp:3,
  role:"Raymond's son. Twenty-five seasons, ten in Europe, and now head coach at Bayamón.",
  hon:["3× MVP","Finals MVP 2009","2nd all-time in assists"],
  note:"Born in Arecibo, 1975. Wore 9 and 11. Played for eight different BSN clubs."},
 {n:"Pablo Alicea",yrs:"1987–2006",pos:"PG",era:1987,pts:null,gp:503,ppg:null,mvp:0,
  role:"Held the single-game assist record for twenty-three years.",
  hon:["25 assists in 1989","3rd all-time in assists"],
  note:"His mark fell to Jonathan García's 33 in 2012."},
 {n:"James Carter",yrs:"1987–2006",pos:"PG",era:1987,pts:null,gp:543,ppg:null,mvp:0,
  role:"The league's all-time assists leader.",hon:["All-time assists leader"],note:"3,025 across 543 games."},
 {n:"Sammy Betancourt",yrs:"1966–1985",pos:"G",era:1966,pts:null,gp:null,ppg:null,mvp:0,
  role:"«The Sharpshooter». Three scoring titles and a ninety per cent free-throw stroke.",
  hon:["Puerto Rico Sports Hall of Fame","3× scoring champion"],
  note:"Inducted 7 October 2012. Seventeen seasons with the Santos de San Juan; two Pan American Games."},
 {n:"Butch Lee",yrs:"1970s–80s",pos:"G",era:1976,pts:null,gp:null,ppg:null,mvp:0,
  role:"The first Puerto Rican and first BSN player to reach the NBA, and the first to win a title there.",
  hon:["First BSN player to win an NBA title"],note:""},
 {n:"José «Piculín» Ortiz",yrs:"1980–2006",pos:"C",era:1980,pts:null,gp:505,ppg:null,mvp:0,
  role:"Reached the NBA after starting in the BSN and returned to finish his career at home.",
  hon:["6th all-time in rebounds","NBA"],note:"5,314 rebounds across 505 games."},
 {n:"Ángel Santiago",yrs:"1973–1996",pos:"SF",era:1973,pts:11287,gp:617,ppg:18.3,mvp:0,
  role:"Twenty-three seasons and a title with the 1986 Polluelos de Aibonito.",
  hon:["8th all-time in points","Champion 1986"],note:""},
 {n:"Edgar de León",yrs:"1981–2001",pos:"F/C",era:1981,pts:null,gp:493,ppg:null,mvp:0,
  role:"Two scoring titles for Fajardo either side of the turn of the nineties.",
  hon:["2× scoring champion","8th all-time in rebounds"],note:""},
 {n:"Federico «Fico» López",yrs:"1981–1997",pos:"PG",era:1981,pts:null,gp:446,ppg:null,mvp:0,
  role:"One of the league's defining point guards through the eighties.",
  hon:["5th all-time in assists"],note:""}
];
const RETIRED=[
 ["Vaqueros de Bayamón",8,"4 · 5 · 9 · 15 · 16 · 17 · 17 · 54"],
 ["Mets de Guaynabo",3,"5 · 9 · 15"]
];

const REF_RULES=[
 ["Article 22.1","Three imports per club","Every one of the twelve franchises may carry three refuerzos. There is no nationality restriction on who those three may be."],
 ["Article 22.1","Six changes, then two more","A club may replace an import six times before the trade deadline and twice more during the postseason. Injuries count against the total."],
 ["Article 23.1","Imports trade only for imports","A refuerzo may be swapped only for another refuerzo. Trading an import for a local player is not permitted."],
 ["Article 13.1","Two routes to native status","A player born off the island who is eligible through a parent or grandparent and has five or more BSN seasons counts as a native. So does the child of an owner with three seasons in the league, regardless of citizenship."]
];
/* ---------- on this day ---------- */
const ON_THIS_DAY=[
 [5,22,1974,"Neftalí Rivera scores 79","Still the BSN single-game record. Thirty-four field goals, every one a two-pointer, plus eleven free throws."],
 [5,1,2012,"Jonathan García hands out 33 assists","Caciques de Humacao against Brujos de Guayama. Broke Pablo Alicea's 25 from 1989 and stands as an unofficial world record. Humacao also set the team scoring record with 130 that night, and 46 in a single quarter."],
 [9,8,1969,"17,621 fans in Bayamón","The largest crowd in league history, against Río Piedras. Beat a Ponce–Santurce game that had drawn 16,564."],
 [8,9,2017,"Quebradillas take Game 7","98–90 over Arecibo for the Piratas' sixth title and their first since 2013."],
 [7,27,2023,"Carolina win their first","The Gigantes beat Bayamón 80–60 in Game 5 to take the franchise's first championship."],
 [7,19,2023,"LeBron James turns up in the finals","He watched Game 1 as Carolina beat Bayamón 89–85 in overtime."],
 [12,18,2020,"Bayamón win in the bubble","84–75 over Quebradillas in Game 3, played without fans in a hotel bubble. Yadier Molina's first title as owner and the club's fifteenth."],
 [8,11,2025,"Bayamón close out Ponce","82–68 in Game 5 for a seventeenth title. Danilo Gallinari took Finals MVP."],
 [10,7,2012,"Sammy Betancourt enters the Hall","The three-time scoring champion inducted into the Puerto Rico Sports Hall of Fame."],
 [10,17,2024,"The third import is approved","The board voted 11–2 to let every club carry three refuerzos with no nationality restriction, cutting native roster spots from thirteen to twelve."],
 [10,16,2020,"Yadier Molina buys the Vaqueros","The nine-time Gold Glove catcher took over his hometown club."],
 [4,6,2021,"The Cangrejeros come back","Approved to return under Noah Assad and Jonathan Miranda. Bad Bunny joined the ownership group later that month."],
 [9,19,2019,"Ricardo Dalmau elected president","Succeeded Fernando Quiñones Bodea."],
 [8,17,2023,"Humacao becomes Caguas","The board approved the transfer of the Grises, reviving a name that had been out of the league since 2009."],
 [8,30,2024,"Caguas finish the job","The Criollos closed out their second championship, and their first since 2006."]
];
/* ============================================================
   PLAYER POOL — the games run on this and nothing else.
   Every entry's club and decades were verified during research.
   ppg/rpg/apg are null where the category was never recorded;
   the games show a dash rather than inventing a number.
   t = tags. d = decades. c = franchise keys.
   ============================================================ */
const POOL=[
 {n:"Raymond Dalmau",d:[1960,1970,1980],c:["que"],ppg:21.6,rpg:10.6,apg:5.1,pos:"PG",
  t:["mvp","champion","scoring","native","legend"],b:"Retired in 1985 leading the league in points, rebounds and assists at once."},
 {n:"Neftalí Rivera",d:[1960,1970],c:["que"],ppg:25.2,rpg:null,apg:null,pos:"G",
  t:["scoring","champion","native","legend"],b:"Scored 79 in a single game in 1974, still the record."},
 {n:"Georgie Torres",d:[1970,1980,1990],c:["faj"],ppg:23.4,rpg:null,apg:3.2,pos:"SG",
  t:["mvp","scoring","native","legend","10k"],b:"All-time leading scorer with 15,863 points."},
 {n:"Mario Morales",d:[1970,1980,1990],c:["san"],ppg:22.7,rpg:8.4,apg:null,pos:"SF",
  t:["mvp","scoring","native","legend","10k"],b:"Second all-time in points and a four-time MVP."},
 {n:"Rolando Frazer",d:[1980,1990,2000],c:["aib"],ppg:20.1,rpg:10.2,apg:null,pos:"C",
  t:["scoring","import","10k"],b:"Panamanian centre, back-to-back scoring titles for Aibonito."},
 {n:"Ángel Santiago",d:[1970,1980,1990],c:["aib"],ppg:18.3,rpg:7.2,apg:null,pos:"SF",
  t:["champion","native","10k"],b:"Won the 1986 title with the Polluelos."},
 {n:"Christian Dalmau",d:[1990,2000,2010],c:["que","san","sge","bay","gua","car","coa","vil"],
  ppg:16.5,rpg:null,apg:4.6,pos:"SG",t:["mvp","champion","native","10k"],
  b:"Twenty-five seasons across eight BSN clubs. Finals MVP in 2009."},
 {n:"Teófilo Cruz",d:[1950,1960,1970,1980],c:["san"],ppg:null,rpg:8.0,apg:null,pos:"C",
  t:["mvp","scoring","native","legend"],b:"Four MVPs and a place in the FIBA Hall of Fame."},
 {n:"José «Piculín» Ortiz",d:[1980,1990,2000],c:["sge","san","are"],ppg:18.0,rpg:10.5,apg:null,pos:"C",
  t:["mvp","champion","nba","native","legend"],b:"«Piculín». Reached the NBA and came home to finish."},
 {n:"Edgar de León",d:[1980,1990,2000],c:["faj"],ppg:null,rpg:9.8,apg:null,pos:"F/C",
  t:["scoring","native"],b:"Two scoring titles for Fajardo."},
 {n:"Pablo Alicea",d:[1980,1990,2000],c:["car"],ppg:null,rpg:null,apg:5.5,pos:"PG",
  t:["native","legend"],b:"Held the single-game assist record for twenty-three years."},
 {n:"Sammy Betancourt",d:[1960,1970,1980],c:["gua","cag"],ppg:null,rpg:null,apg:null,pos:"G",
  t:["scoring","native","legend"],b:"«The Sharpshooter». Three scoring titles and a Hall of Fame place."},
 {n:"Juan «Pachín» Vicéns",d:[1950,1960],c:["pon"],ppg:null,rpg:null,apg:null,pos:"G",
  t:["mvp","native","legend"],b:"All-Tournament Team at the 1959 World Championship."},
 {n:"Jaime Frontera",d:[1960],c:["are"],ppg:null,rpg:null,apg:null,pos:"G",
  t:["scoring","native"],b:"Led the league with 400 points in 1966."},
 {n:"Adolfo Porrata",d:[1960],c:["cap"],ppg:null,rpg:null,apg:null,pos:"G",
  t:["scoring","native"],b:"516 points to lead the league in 1967."},
 {n:"Héctor Blondet",d:[1970],c:["are"],ppg:25.1,rpg:null,apg:null,pos:"G",
  t:["scoring","native"],b:"Scoring champion in 1974."},
 {n:"Jim Maldonado",d:[1980],c:["are"],ppg:30.6,rpg:null,apg:null,pos:"F",
  t:["scoring"],b:"Averaged 30.6 to win the 1983 title."},
 {n:"Wesley Correa",d:[1980],c:["mor"],ppg:30.9,rpg:null,apg:null,pos:"F",
  t:["scoring"],b:"Scoring champion for Morovis in 1989."},
 {n:"Edwin Pellot",d:[1990],c:["isa"],ppg:31.5,rpg:null,apg:null,pos:"F",
  t:["scoring"],b:"31.5 a game for Isabela in 1991."},
 {n:"Jesse Pellot",d:[2000],c:["sge"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["mvp","scoring"],b:"MVP and scoring leader in 2009."},
 {n:"Gary Browne",d:[2010],c:[],ppg:null,rpg:null,apg:null,pos:"PG",
  t:["mvp","native"],b:"MVP and assists leader in 2017."},
 {n:"Tu Holloway",d:[2010],c:["que"],ppg:null,rpg:null,apg:null,pos:"PG",
  t:["champion","import"],b:"Finals MVP of the 2017 title run."},
 {n:"Víctor Liz",d:[2010],c:[],ppg:null,rpg:null,apg:null,pos:"G",
  t:["scoring","import"],b:"Led the league in scoring in 2017."},
 {n:"Jonathan García",d:[2010],c:[],ppg:null,rpg:null,apg:null,pos:"PG",
  t:["native","legend"],b:"33 assists in one game in 2012, an unofficial world record."},
 {n:"Emmanuel Mudiay",d:[2020],c:["que"],ppg:23.6,rpg:null,apg:null,pos:"PG",
  t:["mvp","scoring","import","nba"],b:"779 points in 33 games to win the 2025 MVP."},
 {n:"Kobi Simmons",d:[2020],c:["car"],ppg:20.2,rpg:null,apg:null,pos:"G",
  t:["import"],b:"Second in scoring in 2025."},
 {n:"Cheick Diallo",d:[2020],c:["man"],ppg:19.3,rpg:null,apg:null,pos:"C",
  t:["import","nba"],b:"Third in scoring and joint second in blocks in 2025."},
 {n:"Sam Waardenburg",d:[2020],c:["may"],ppg:17.2,rpg:null,apg:null,pos:"F",
  t:["import"],b:"Fourth in scoring for Mayagüez in 2025."},
 {n:"Ysmael Romero",d:[2020],c:["gua"],ppg:18.6,rpg:null,apg:null,pos:"F",
  t:["native"],b:"The top-placed local scorer in 2025, playing as a nativizado."},
 {n:"JaVale McGee",d:[2020],c:["bay"],ppg:null,rpg:null,apg:null,pos:"C",
  t:["import","nba","champion"],b:"Led the league in blocks in 2025 with 40 in 25 games."},
 {n:"Iván Gandía",d:[2020],c:["agu"],ppg:null,rpg:null,apg:null,pos:"PG",
  t:["native"],b:"91 three-pointers at 44 per cent to lead the league in 2025."},
 {n:"Alexander Kappos",d:[2020],c:["cag"],ppg:null,rpg:null,apg:null,pos:"G",
  t:["native"],b:"Second in three-pointers in 2025 with 78."},
 {n:"Travis Trice",d:[2020],c:["cag"],ppg:20.9,rpg:null,apg:6.1,pos:"PG",
  t:["mvp","champion","import"],b:"MVP in 2024 and 2026, and Finals MVP of the 2024 title."},
 {n:"Renaldo Balkman",d:[2010,2020],c:["bay"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["champion","import","nba"],b:"Finals MVP in 2026 at forty-one years old."},
 {n:"Moses Brown",d:[2020],c:["cag"],ppg:null,rpg:null,apg:null,pos:"C",
  t:["import","nba"],b:"Defender of the year in 2026."},
 {n:"Andre Curbelo",d:[2020],c:["sge"],ppg:null,rpg:null,apg:null,pos:"PG",
  t:["native"],b:"Most improved player in 2026."},
 {n:"Montrezl Harrell",d:[2020],c:["sge"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["import","nba"],b:"All-Star five in 2026."},
 {n:"Jaylen Nowell",d:[2020],c:["car"],ppg:null,rpg:null,apg:null,pos:"SG",
  t:["import","nba"],b:"All-Star five in 2026."},
 {n:"Daniel Rivera",d:[2020],c:["car"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["native"],b:"Rookie of the year in 2026, born in San Juan."},
 {n:"Christian López",d:[2020],c:["cag"],ppg:null,rpg:null,apg:null,pos:"G",
  t:["native"],b:"Sixth man of the year in 2026."},
 {n:"Danilo Gallinari",d:[2020],c:["bay"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["champion","import","nba"],b:"Finals MVP of Bayamón's 2025 title."},
 {n:"Jae Crowder",d:[2020],c:["bay"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["import","nba"],b:"Signed by Bayamón for the 2026 season."},
 {n:"Alfonso Plummer",d:[2020],c:["are"],ppg:18.9,rpg:3.1,apg:3.8,pos:"G",
  t:["native"],b:"Most improved player in 2024 for Arecibo."},
 {n:"Emmanuel Maldonado",d:[2020],c:["san"],ppg:8.0,rpg:2.1,apg:null,pos:"G",
  t:["native"],b:"Award winner for Santurce in 2024."},
 {n:"Jordan Murphy",d:[2020],c:["pon"],ppg:null,rpg:null,apg:null,pos:"F",
  t:["import"],b:"Joint second in blocks in 2025 with 30."}
];
/* The league app lists these venues; they supersede the older
   English-language arena names carried from Wikipedia. */
/* [name, capacity, nickname|null, opened year|null]. Capacities vary by
   source/renovation — shown with a "~" and a tooltip, never as precise.
   gua corrected (was "Coliseo Fernando «Rube» Hernández", 3500 — wrong):
   the HOF entry for Mario «Quijote» Morales already said, in an unrelated
   note, "The Mets play at the Mario Morales Coliseum" — confirmed against
   El Nuevo Día + Wikipedia. bsn_team_page_plan.md has full sourcing. */
const VENUES = {
  sge:['Coliseo Arquelio Torres Ramírez',5000,'La Cuna',1985],
  san:['Coliseo Roberto Clemente',9000,null,null],
  are:['Coliseo Manuel «Petaca» Iguina',12000,null,null],
  cag:['Coliseo Roger Mendoza',3000,'La Presión',null],
  car:['Coliseo Carlos Miguel Mangual',5500,null,null],
  may:['Palacio de Recreación y Deportes Wilkins',5500,'Sultana del Oeste',1981],
  pon:['Auditorio Pachín Vicéns',11000,'Coliseo de Ponce',1972],
  gua:['Coliseo Mario «Quijote» Morales',5500,null,1983],
  man:['Coliseo Juan Aubín Cruz',8000,null,null],
  que:['Coliseo Raymond Dalmau',5500,'La Guarida del Pirata',2008],
  agu:['Coliseo Ismael «Chavalillo» Delgado',7500,null,2010],
  bay:['Coliseo Rubén Rodríguez',12000,'El Rancho Vaquero',1988]
};
const FIVE_2026 = [
  ['Travis Trice','PG','Criollos de Caguas'],
  ['André Curbelo','PG','Atléticos de San Germán'],
  ['Jaylen Nowell','SG','Gigantes de Carolina'],
  ['Montrezl Harrell','F','San Germán según RealGM · Caguas según Noticel'],
  ['Moses Brown','C','Criollos de Caguas']
];
/* Reference points for the offseason clock. The 2027 opener has
   not been announced; the last four seasons opened 3 abr, 22 mar,
   21 mar and 21 mar, so late March is the estimate, labelled as one. */
const SEASON_STATE = {
  lastGame:'2026-08-23',
  champ:'bay', title:18,
  nextEstimate:'2027-03-21',
  nextLabel:'estimado — la liga no ha anunciado la fecha'
};

/* Players verified from 2026 finals coverage. Kept separate from
   the original POOL so the provenance of each block is one source. */
const POOL_2026 = [
  {n:'Jassel Pérez',d:[2020],c:['bay'],ppg:21.4,rpg:null,apg:null,pos:'G',
   t:['import','champion'],b:'Dominicano. Tercero en anotación en 2026 y líder ofensivo del campeón.'},
  {n:'Chris McCullough',d:[2010,2020],c:['bay'],ppg:null,rpg:null,apg:null,pos:'F',
   t:['import','nba','champion'],b:'25 puntos en el quinto juego de la final de 2026.'},
  {n:'Stephen Thompson Jr.',d:[2020],c:['bay'],ppg:null,rpg:null,apg:null,pos:'G',
   t:['import','champion'],b:'Triple decisivo a 2:43 del final del séptimo juego de 2026.'},
  {n:'Javier Mojica',d:[2010,2020],c:['bay'],ppg:null,rpg:null,apg:null,pos:'G',
   t:['native','champion'],b:'Selló el título 18 desde la línea a 19.7 segundos.'},
  {n:'Arnaldo Toro',d:[2020],c:['bay'],ppg:null,rpg:null,apg:null,pos:'F',
   t:['native','champion'],b:'Disponible para el séptimo juego tras dudas de última hora.'},
  {n:'Rigoberto Mendoza',d:[2020],c:['agu'],ppg:null,rpg:null,apg:null,pos:'G',
   t:['import'],b:'Dominicano. 22 puntos en el cuarto juego de la final de 2026, 15 en el primer parcial.'},
  {n:'Manny Camper',d:[2020],c:['agu'],ppg:null,rpg:null,apg:null,pos:'G',
   t:['import'],b:'11.5 puntos y la defensa sobre Jassel Pérez en la final de 2026.'},
  {n:'Joel Soriano',d:[2020],c:['agu'],ppg:null,rpg:null,apg:null,pos:'C',
   t:['import'],b:'Dominicano. Donqueo con 1:23 que puso a Aguada arriba en el sexto.'},
  {n:'Jacob Wiley',d:[2020],c:['agu'],ppg:null,rpg:null,apg:null,pos:'F',
   t:['import'],b:'Refuerzo de Aguada en la final de 2026.'},
  {n:'John Holland',d:[2010,2020],c:['agu'],ppg:null,rpg:null,apg:null,pos:'G',
   t:['import','nba'],b:'Veterano de Aguada en la final de 2026.'}
];

/* Gary Browne's club was blank in the original pool; the 2026
   finals coverage places him in Bayamón, so the gap closes. */
/* Generated from bsn_player_seasons_realgm.csv — RealGM season leaders,
   2012-2026. `pos` here is a profile computed from the player's own
   recorded rates, not a listed position; posSrc marks which is which. */
const POOL_RGM=[{"n":"Al Thornton","c":["guy"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":23.3,"rpg":8.3,"apg":1.9,"spg":1,"bpg":1.3,"gp":60,"ns":2,"hi":[2012,25.3],"ss":[[2012,"guy",28,25.3,9.2,2,1.3,1.6,0.498],[2014,"guy",32,21.6,7.5,1.9,0.8,1,0.447]]},{"n":"Reyshawn Terry","c":["que"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":23.2,"rpg":8,"apg":2.8,"spg":1.1,"bpg":0.3,"gp":46,"ns":1,"hi":[2018,23.2],"ss":[[2018,"que",46,23.2,8,2.8,1.1,0.3,0.523]]},{"n":"Sheldon Mac","c":["car","sge","man","agu"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":22.9,"rpg":4.7,"apg":3.3,"spg":1.3,"bpg":0.1,"gp":87,"ns":6,"hi":[2022,24.5],"ss":[[2022,"car",31,24.5,4.1,3.3,1.5,0.1,0.498],[2022,"sge",5,22.2,4.6,1.8,1,0,0.526],[2023,"man",19,22.4,4.9,4.1,1.1,0.1,0.458],[2023,"car",5,18.2,4.4,4,1.2,0.2,0.413],[2024,"man",7,23.6,5.7,2.6,1.9,0,0.543],[2024,"agu",20,22.2,5.3,3,1.1,0.2,0.498]]},{"n":"John Meeks","c":["agu"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":22.5,"rpg":5.9,"apg":2.5,"spg":0.6,"bpg":0.1,"gp":15,"ns":1,"hi":[2024,22.5],"ss":[[2024,"agu",15,22.5,5.9,2.5,0.6,0.1,0.555]]},{"n":"Justin Keenan","c":["coa"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":22.2,"rpg":7.8,"apg":1.7,"spg":0.8,"bpg":0.2,"gp":29,"ns":1,"hi":[2014,22.2],"ss":[[2014,"coa",29,22.2,7.8,1.7,0.8,0.2,0.488]]},{"n":"Emmanuel Mudiay","c":["san","que"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":21.9,"rpg":5,"apg":5.6,"spg":1.1,"bpg":0.2,"gp":114,"ns":4,"hi":[2025,23.3],"ss":[[2023,"san",10,21.4,5.8,5.9,1,0.5,0.451],[2024,"que",41,22.2,5.8,5.4,1,0.2,0.478],[2025,"que",36,23.3,4.6,5.7,1.3,0.1,0.484],[2026,"que",27,19.6,4.2,5.6,0.9,0.1,0.433]]},{"n":"Nick Minnerath","c":["pon"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":21.9,"rpg":5.9,"apg":1,"spg":0.4,"bpg":0.5,"gp":25,"ns":1,"hi":[2019,21.9],"ss":[[2019,"pon",25,21.9,5.9,1,0.4,0.5,0.523]]},{"n":"Mike Scott","c":["car"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":21.8,"rpg":9.4,"apg":2.2,"spg":0.8,"bpg":0.2,"gp":25,"ns":1,"hi":[2023,21.8],"ss":[[2023,"car",25,21.8,9.4,2.2,0.8,0.2,0.511]]},{"n":"Q.J. Peterson","c":["bay"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":21.8,"rpg":4.4,"apg":4.2,"spg":1,"bpg":0.5,"gp":11,"ns":1,"hi":[2024,21.8],"ss":[[2024,"bay",11,21.8,4.4,4.2,1,0.5,0.412]]},{"n":"Brandon Goodwin","c":["car"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":21.7,"rpg":5,"apg":7.6,"spg":1.1,"bpg":0.3,"gp":37,"ns":1,"hi":[2024,21.7],"ss":[[2024,"car",37,21.7,5,7.6,1.1,0.3,0.502]]},{"n":"Terrence Jones","c":["gua","faj","may"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":21.4,"rpg":9.3,"apg":3,"spg":1.3,"bpg":1.3,"gp":41,"ns":3,"hi":[2022,23.6],"ss":[[2020,"gua",11,19.1,9.8,2.7,1,1.4,0.463],[2022,"faj",23,23.6,9.2,2.8,1.7,1.4,0.494],[2022,"may",7,17.6,9,4.1,0.7,1,0.479]]},{"n":"Jaylen Nowell","c":["car"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":21.4,"rpg":3.1,"apg":3.5,"spg":1,"bpg":0.2,"gp":34,"ns":1,"hi":[2026,21.4],"ss":[[2026,"car",34,21.4,3.1,3.5,1,0.2,0.49]]},{"n":"D.J. Hogg","c":["may"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":21.2,"rpg":6.2,"apg":3.8,"spg":1.3,"bpg":1.5,"gp":17,"ns":1,"hi":[2023,21.2],"ss":[[2023,"may",17,21.2,6.2,3.8,1.3,1.5,0.451]]},{"n":"Paris Bass","c":["sge","are"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":21,"rpg":9.7,"apg":3.2,"spg":1.1,"bpg":0.8,"gp":78,"ns":3,"hi":[2021,22.9],"ss":[[2020,"sge",15,22,10.3,2.1,0.9,0.9,0.457],[2021,"sge",31,22.9,9.4,4.8,1.3,0.9,0.501],[2023,"are",32,18.8,9.6,2.2,1.1,0.7,0.498]]},{"n":"Angel Suero","c":["faj","hum"],"d":[2010,2020],"pos":"SF","posSrc":"perfil","ppg":21,"rpg":5,"apg":4,"spg":1.2,"bpg":0.2,"gp":36,"ns":3,"hi":[2021,21.8],"ss":[[2019,"faj",15,21.5,4.8,4.9,1.3,0.3,0.504],[2020,"faj",11,19.5,5,4,0.7,0.2,0.41],[2021,"hum",10,21.8,5.4,2.8,1.5,0.1,0.452]]},{"n":"Jared Sullinger","c":["san"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":21,"rpg":14.9,"apg":2.9,"spg":0.9,"bpg":1.2,"gp":25,"ns":1,"hi":[2024,21],"ss":[[2024,"san",25,21,14.9,2.9,0.9,1.2,0.558]]},{"n":"Hassan Whiteside","c":["que","san"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":20.9,"rpg":13.1,"apg":1.1,"spg":0.5,"bpg":2.5,"gp":47,"ns":2,"hi":[2023,22.2],"ss":[[2023,"que",37,22.2,13.5,1.4,0.6,2.6,0.537],[2025,"san",10,16,11.6,0.2,0.3,2.1,0.587]]},{"n":"Theo Pinson","c":["gua"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":20.9,"rpg":4.7,"apg":4.5,"spg":0.8,"bpg":0.6,"gp":11,"ns":1,"hi":[2025,20.9],"ss":[[2025,"gua",11,20.9,4.7,4.5,0.8,0.6,0.415]]},{"n":"Jameer Nelson Jr.","c":["man"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":20.8,"rpg":3.7,"apg":4.6,"spg":1.9,"bpg":0.4,"gp":14,"ns":1,"hi":[2026,20.8],"ss":[[2026,"man",14,20.8,3.7,4.6,1.9,0.4,0.518]]},{"n":"Brandon Knight","c":["que","are","gua"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":20.6,"rpg":4.2,"apg":5.4,"spg":1.2,"bpg":0.1,"gp":77,"ns":3,"hi":[2023,23.3],"ss":[[2023,"que",36,23.3,4.4,5,1.3,0.1,0.455],[2025,"are",22,19,4.3,5.5,1.2,0.1,0.415],[2026,"gua",19,17.5,3.7,6.2,0.9,0.1,0.467]]},{"n":"Diamond Stone","c":["gua"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":20.5,"rpg":9.8,"apg":1.7,"spg":0.5,"bpg":0.7,"gp":11,"ns":1,"hi":[2021,20.5],"ss":[[2021,"gua",11,20.5,9.8,1.7,0.5,0.7,0.537]]},{"n":"Ismael Cruz","c":["man"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":20.3,"rpg":2.6,"apg":4.4,"spg":1.4,"bpg":0.1,"gp":16,"ns":1,"hi":[2025,20.3],"ss":[[2025,"man",16,20.3,2.6,4.4,1.4,0.1,0.497]]},{"n":"Damien Wilkins","c":["guy"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":20.2,"rpg":5.4,"apg":4.3,"spg":1.7,"bpg":0.5,"gp":31,"ns":1,"hi":[2017,20.2],"ss":[[2017,"guy",31,20.2,5.4,4.3,1.7,0.5,0.469]]},{"n":"Mike Young","c":["pon"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":20.1,"rpg":5.3,"apg":2.9,"spg":0.6,"bpg":0.6,"gp":22,"ns":1,"hi":[2018,20.1],"ss":[[2018,"pon",22,20.1,5.3,2.9,0.6,0.6,0.519]]},{"n":"Alize Johnson","c":["sge"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":20,"rpg":12.4,"apg":4.4,"spg":0.7,"bpg":0,"gp":11,"ns":1,"hi":[2024,20],"ss":[[2024,"sge",11,20,12.4,4.4,0.7,0,0.535]]},{"n":"Sam Young","c":["bay"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":19.9,"rpg":7.8,"apg":2.5,"spg":1.3,"bpg":0.8,"gp":39,"ns":1,"hi":[2014,19.9],"ss":[[2014,"bay",39,19.9,7.8,2.5,1.3,0.8,0.565]]},{"n":"Jack McVeigh","c":["are"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":19.9,"rpg":6.1,"apg":4.1,"spg":0.5,"bpg":0.2,"gp":16,"ns":1,"hi":[2026,19.9],"ss":[[2026,"are",16,19.9,6.1,4.1,0.5,0.2,0.463]]},{"n":"Kobi Simmons","c":["car"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":19.8,"rpg":3.2,"apg":4.7,"spg":1.1,"bpg":0.1,"gp":36,"ns":1,"hi":[2025,19.8],"ss":[[2025,"car",36,19.8,3.2,4.7,1.1,0.1,0.513]]},{"n":"Frank Gaines","c":["san"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":19.8,"rpg":3.5,"apg":2.7,"spg":1,"bpg":0.3,"gp":20,"ns":1,"hi":[2021,19.8],"ss":[[2021,"san",20,19.8,3.5,2.7,1,0.3,0.475]]},{"n":"Brandon Costner","c":["cac","hum"],"d":[2010,2020],"pos":"PF","posSrc":"perfil","ppg":19.7,"rpg":7,"apg":3.1,"spg":0.8,"bpg":0.4,"gp":82,"ns":3,"hi":[2016,19.9],"ss":[[2016,"cac",38,19.9,6.2,2.3,0.7,0.5,0.406],[2018,"cac",33,19.6,7.7,3.4,1,0.4,0.416],[2021,"hum",11,19.5,7.4,4.7,0.9,0.2,0.418]]},{"n":"Von Wafer","c":["may"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":19.7,"rpg":3.6,"apg":3,"spg":0.5,"bpg":0.2,"gp":35,"ns":1,"hi":[2014,19.7],"ss":[[2014,"may",35,19.7,3.6,3,0.5,0.2,0.467]]},{"n":"Jahlil Okafor","c":["are"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":19.7,"rpg":7.8,"apg":2.7,"spg":0.2,"bpg":0.2,"gp":29,"ns":1,"hi":[2024,19.7],"ss":[[2024,"are",29,19.7,7.8,2.7,0.2,0.2,0.648]]},{"n":"Travis Trice","c":["hum","cag"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":19.6,"rpg":3.3,"apg":8,"spg":1.3,"bpg":0.1,"gp":136,"ns":4,"hi":[2024,20.7],"ss":[[2023,"hum",20,17.2,2.6,7.9,1,0.1,0.457],[2024,"cag",54,20.7,3.5,7.2,1.1,0.1,0.426],[2025,"cag",18,20,3.1,7,1.1,0,0.447],[2026,"cag",44,19.3,3.5,9.5,1.7,0,0.449]]},{"n":"Tu Holloway","c":["que","san"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":19.6,"rpg":2.8,"apg":6.4,"spg":1.3,"bpg":0.1,"gp":43,"ns":2,"hi":[2021,20.2],"ss":[[2021,"que",37,20.2,2.9,6.5,1.4,0.1,0.445],[2023,"san",6,16,2.5,6,0.8,0.2,0.38]]},{"n":"Rondae Hollis-Jefferson","c":["sge","gua"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":19.5,"rpg":8.3,"apg":4.8,"spg":1.5,"bpg":0.9,"gp":82,"ns":3,"hi":[2023,21.7],"ss":[[2022,"sge",31,19.6,8.7,5.3,1,0.9,0.479],[2023,"sge",22,21.7,9.4,4.8,2.1,0.6,0.461],[2024,"gua",29,17.6,7,4.4,1.7,1.1,0.451]]},{"n":"Bryn Forbes","c":["agu","gua"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":19.5,"rpg":2.7,"apg":2.9,"spg":1.2,"bpg":0,"gp":21,"ns":2,"hi":[2025,21],"ss":[[2025,"agu",11,21,2.2,3.5,1.2,0,0.563],[2025,"gua",10,17.8,3.2,2.3,1.3,0,0.48]]},{"n":"Danilo Gallinari","c":["bay"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":19.3,"rpg":6,"apg":2.7,"spg":0.7,"bpg":0.3,"gp":43,"ns":1,"hi":[2025,19.3],"ss":[[2025,"bay",43,19.3,6,2.7,0.7,0.3,0.453]]},{"n":"David Stockton","c":["gua","san","are"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":19.2,"rpg":3.6,"apg":6.4,"spg":1.2,"bpg":0.2,"gp":108,"ns":4,"hi":[2021,20.7],"ss":[[2020,"gua",12,18.9,3.4,4.9,1.2,0.3,0.482],[2021,"gua",32,20.7,4.5,7.3,1.1,0.2,0.474],[2023,"san",24,19.5,3.3,6.6,1,0.1,0.491],[2024,"are",40,17.9,3.2,5.9,1.3,0.1,0.498]]},{"n":"Jassel Perez","c":["bay"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":19.2,"rpg":4.9,"apg":4,"spg":2,"bpg":0.3,"gp":26,"ns":1,"hi":[2026,19.2],"ss":[[2026,"bay",26,19.2,4.9,4,2,0.3,0.485]]},{"n":"Mike Harris","c":["sge","pon","may"],"d":[2010,2020],"pos":"C","posSrc":"perfil","ppg":19.1,"rpg":10,"apg":2.1,"spg":0.9,"bpg":0.9,"gp":150,"ns":4,"hi":[2013,20.4],"ss":[[2012,"sge",36,19.1,10.3,1.8,0.7,1.1,0.505],[2013,"pon",49,20.4,10.5,2,1.1,0.9,0.509],[2014,"pon",54,18.6,9.3,2.4,0.8,0.8,0.487],[2020,"may",11,15.6,9.8,2.3,1,0.8,0.632]]},{"n":"Tai Odiase","c":["que"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":19.1,"rpg":6.8,"apg":1.3,"spg":0.4,"bpg":1.3,"gp":29,"ns":1,"hi":[2024,19.1],"ss":[[2024,"que",29,19.1,6.8,1.3,0.4,1.3,0.62]]},{"n":"Archie Goodwin","c":["faj"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":19.1,"rpg":4.6,"apg":3.5,"spg":1,"bpg":0.5,"gp":15,"ns":1,"hi":[2023,19.1],"ss":[[2023,"faj",15,19.1,4.6,3.5,1,0.5,0.498]]},{"n":"Ike Diogu","c":["pon"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":19,"rpg":8.6,"apg":1.5,"spg":0.3,"bpg":0.7,"gp":41,"ns":1,"hi":[2013,19],"ss":[[2013,"pon",41,19,8.6,1.5,0.3,0.7,0.494]]},{"n":"DeMarcus Cousins","c":["gua"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":18.8,"rpg":9.6,"apg":4.4,"spg":1.3,"bpg":1.4,"gp":37,"ns":2,"hi":[2023,19],"ss":[[2023,"gua",27,19,9.8,4.3,1.3,1.4,0.522],[2025,"gua",10,18.2,9,4.7,1.4,1.4,0.478]]},{"n":"Mitchell Creek","c":["gua"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":18.8,"rpg":5.7,"apg":2.5,"spg":1,"bpg":0.4,"gp":35,"ns":1,"hi":[2023,18.8],"ss":[[2023,"gua",35,18.8,5.7,2.5,1,0.4,0.528]]},{"n":"Tyrell Harrison","c":["may"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":18.7,"rpg":9.8,"apg":1.5,"spg":0.8,"bpg":1.1,"gp":46,"ns":2,"hi":[2025,18.8],"ss":[[2025,"may",25,18.8,10.2,1.8,0.8,0.8,0.66],[2026,"may",21,18.5,9.4,1.2,0.7,1.4,0.648]]},{"n":"Alejandro Carmona Sanchez","c":["cac"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":18.6,"rpg":7.8,"apg":2.1,"spg":0.8,"bpg":0.2,"gp":33,"ns":1,"hi":[2013,18.6],"ss":[[2013,"cac",33,18.6,7.8,2.1,0.8,0.2,0.515]]},{"n":"Damion James","c":["san"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":18.6,"rpg":10.4,"apg":2.6,"spg":1.2,"bpg":1.1,"gp":47,"ns":1,"hi":[2016,18.6],"ss":[[2016,"san",47,18.6,10.4,2.6,1.2,1.1,0.398]]},{"n":"Chaundee Brown Jr.","c":["may"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":18.6,"rpg":6.6,"apg":2.2,"spg":0.4,"bpg":0,"gp":12,"ns":1,"hi":[2023,18.6],"ss":[[2023,"may",12,18.6,6.6,2.2,0.4,0,0.447]]},{"n":"Victor Liz","c":["pon","are"],"d":[2010,2020],"pos":"SG","posSrc":"perfil","ppg":18.5,"rpg":4.6,"apg":3.3,"spg":1.3,"bpg":0.1,"gp":179,"ns":5,"hi":[2019,20.7],"ss":[[2017,"pon",39,19.9,3.9,3.7,1.6,0.1,0.444],[2019,"pon",53,20.7,5.2,3.8,1.3,0.1,0.488],[2021,"pon",10,16.4,5.4,3.4,0.8,0.1,0.429],[2022,"are",39,16.9,4.5,2.7,1.1,0.1,0.477],[2025,"are",38,16.1,4.4,2.8,1.3,0.1,0.455]]},{"n":"Chris Duarte","c":["bay"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":18.5,"rpg":4.7,"apg":4.5,"spg":1.5,"bpg":0.3,"gp":40,"ns":1,"hi":[2025,18.5],"ss":[[2025,"bay",40,18.5,4.7,4.5,1.5,0.3,0.485]]},{"n":"Malik Beasley","c":["san"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":18.4,"rpg":4.1,"apg":1.6,"spg":1.3,"bpg":0.1,"gp":15,"ns":1,"hi":[2026,18.4],"ss":[[2026,"san",15,18.4,4.1,1.6,1.3,0.1,0.384]]},{"n":"Walter Hodge","c":["are"],"d":[2010,2020],"pos":"PG","posSrc":"perfil","ppg":18.3,"rpg":2.8,"apg":6.3,"spg":1.2,"bpg":0.1,"gp":131,"ns":3,"hi":[2021,19.8],"ss":[[2014,"are",47,16.5,2.9,6.8,1.7,0.1,0.491],[2021,"are",48,19.8,2.8,6.2,0.9,0,0.506],[2022,"are",36,18.7,2.5,5.6,1,0.2,0.476]]},{"n":"Jordan Howard","c":["guy","man"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":18.3,"rpg":2.5,"apg":4.5,"spg":0.7,"bpg":0,"gp":29,"ns":2,"hi":[2025,18.4],"ss":[[2020,"guy",14,18.1,2.8,4.1,0.7,0,0.494],[2025,"man",15,18.4,2.2,4.9,0.7,0,0.495]]},{"n":"Nathaniel Mason","c":["sge"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":18.2,"rpg":3.6,"apg":5.9,"spg":0.9,"bpg":0.1,"gp":63,"ns":2,"hi":[2023,20.9],"ss":[[2022,"sge",35,16.1,3.3,5.7,0.8,0.2,0.421],[2023,"sge",28,20.9,4,6.1,1.1,0,0.498]]},{"n":"Alfonso Plummer","c":["are"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":18.2,"rpg":2.8,"apg":4,"spg":0.6,"bpg":0.1,"gp":55,"ns":2,"hi":[2024,19],"ss":[[2024,"are",40,19,3.2,3.8,0.7,0.1,0.495],[2026,"are",15,16.1,1.7,4.4,0.5,0.2,0.47]]},{"n":"Jezreel De Jesus","c":["coa","sge","may","pon"],"d":[2010,2020],"pos":"SG","posSrc":"perfil","ppg":18.1,"rpg":3.4,"apg":4.2,"spg":0.9,"bpg":0.1,"gp":320,"ns":9,"hi":[2021,21.1],"ss":[[2014,"coa",36,19.3,3.3,4.3,0.8,0.1,0.449],[2018,"sge",25,15.9,3.2,2.9,0.8,0.1,0.459],[2019,"may",18,17.5,3.4,4,1.5,0.1,0.513],[2021,"pon",28,21.1,3.9,5.2,1,0.1,0.552],[2022,"pon",43,18.1,2.9,5,1.2,0.1,0.482],[2023,"pon",37,18.1,4.3,5.2,0.9,0.1,0.485],[2024,"pon",48,16.6,3.2,3.5,0.7,0.1,0.445],[2025,"pon",47,16.7,3.6,3.5,0.9,0.1,0.456],[2026,"pon",38,19.9,3.1,4.1,0.9,0.1,0.472]]},{"n":"Larry Ayuso","c":["are","gua","bay"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":18.1,"rpg":2.5,"apg":1.8,"spg":0.8,"bpg":0,"gp":182,"ns":4,"hi":[2013,20],"ss":[[2012,"are",47,17.2,2.6,1.2,0.9,0,0.386],[2013,"gua",43,20,2.9,2.1,0.9,0,0.379],[2014,"bay",43,16.9,2.4,1.9,0.8,0.1,0.366],[2015,"gua",49,18.5,2.1,2,0.6,0,0.411]]},{"n":"Chane Behanan","c":["agu"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":18.1,"rpg":9.6,"apg":2,"spg":1.2,"bpg":0.4,"gp":47,"ns":1,"hi":[2016,18.1],"ss":[[2016,"agu",47,18.1,9.6,2,1.2,0.4,0.52]]},{"n":"Robert Glenn","c":["faj"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":18.1,"rpg":6.9,"apg":3.5,"spg":0.8,"bpg":1.1,"gp":31,"ns":1,"hi":[2019,18.1],"ss":[[2019,"faj",31,18.1,6.9,3.5,0.8,1.1,0.584]]},{"n":"Ben Moore","c":["gua"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":18.1,"rpg":9.1,"apg":2.9,"spg":1,"bpg":1,"gp":31,"ns":1,"hi":[2022,18.1],"ss":[[2022,"gua",31,18.1,9.1,2.9,1,1,0.63]]},{"n":"Ismael Romero","c":["gua"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":18,"rpg":9.2,"apg":2.6,"spg":1,"bpg":0.4,"gp":62,"ns":2,"hi":[2025,18.6],"ss":[[2025,"gua",31,18.6,10.1,2.4,1.1,0.5,0.602],[2026,"gua",31,17.5,8.3,2.8,0.8,0.4,0.581]]},{"n":"Jose Gadiel Rodriguez","c":["guy"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":17.9,"rpg":6.8,"apg":2.6,"spg":1.1,"bpg":0.3,"gp":16,"ns":1,"hi":[2020,17.9],"ss":[[2020,"guy",16,17.9,6.8,2.6,1.1,0.3,0.513]]},{"n":"Kalin Lucas","c":["car"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":17.9,"rpg":3.5,"apg":9.2,"spg":1.3,"bpg":0,"gp":11,"ns":1,"hi":[2021,17.9],"ss":[[2021,"car",11,17.9,3.5,9.2,1.3,0,0.419]]},{"n":"Moses Brown","c":["cag"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":17.9,"rpg":10.2,"apg":0.6,"spg":0.5,"bpg":1.6,"gp":42,"ns":1,"hi":[2026,17.9],"ss":[[2026,"cag",42,17.9,10.2,0.6,0.5,1.6,0.611]]},{"n":"Alade Aminu","c":["sge"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":17.9,"rpg":8,"apg":2.1,"spg":1.1,"bpg":0.9,"gp":30,"ns":1,"hi":[2021,17.9],"ss":[[2021,"sge",30,17.9,8,2.1,1.1,0.9,0.603]]},{"n":"Deonte Burton","c":["gua"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.9,"rpg":4.7,"apg":2.6,"spg":1.5,"bpg":0.4,"gp":14,"ns":1,"hi":[2024,17.9],"ss":[[2024,"gua",14,17.9,4.7,2.6,1.5,0.4,0.509]]},{"n":"Isaac Sosa","c":["sge","man"],"d":[2010,2020],"pos":"SG","posSrc":"perfil","ppg":17.8,"rpg":2.9,"apg":2.6,"spg":0.7,"bpg":0.1,"gp":71,"ns":2,"hi":[2019,18.3],"ss":[[2019,"sge",38,18.3,3.2,2.8,0.8,0.2,0.517],[2023,"man",33,17.2,2.6,2.4,0.5,0,0.464]]},{"n":"Grant Basile","c":["que"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":17.8,"rpg":7.6,"apg":1.3,"spg":0.8,"bpg":0.7,"gp":12,"ns":1,"hi":[2026,17.8],"ss":[[2026,"que",12,17.8,7.6,1.3,0.8,0.7,0.623]]},{"n":"James Ennis","c":["hum"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":17.8,"rpg":8,"apg":3.2,"spg":1.5,"bpg":0.2,"gp":12,"ns":1,"hi":[2023,17.8],"ss":[[2023,"hum",12,17.8,8,3.2,1.5,0.2,0.53]]},{"n":"Terrence Shannon","c":["bay"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":17.8,"rpg":8,"apg":2.2,"spg":0.7,"bpg":0.8,"gp":29,"ns":1,"hi":[2013,17.8],"ss":[[2013,"bay",29,17.8,8,2.2,0.7,0.8,0.52]]},{"n":"Nathan Sobey","c":["agu","may"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":17.7,"rpg":4.4,"apg":4.9,"spg":1.4,"bpg":0.3,"gp":49,"ns":2,"hi":[2026,20.5],"ss":[[2025,"agu",30,16,3.9,3.9,1.6,0.3,0.448],[2026,"may",19,20.5,5.3,6.4,1.1,0.3,0.432]]},{"n":"Kyle Vinales","c":["cac","gua"],"d":[2010,2020],"pos":"PG","posSrc":"perfil","ppg":17.7,"rpg":2.9,"apg":4.7,"spg":1.2,"bpg":0,"gp":53,"ns":2,"hi":[2018,20.1],"ss":[[2018,"cac",26,20.1,3.4,3.6,1.5,0,0.487],[2022,"gua",27,15.4,2.4,5.7,0.9,0,0.432]]},{"n":"Terrico White","c":["guy"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.7,"rpg":5.6,"apg":3,"spg":1.1,"bpg":0.2,"gp":15,"ns":1,"hi":[2022,17.7],"ss":[[2022,"guy",15,17.7,5.6,3,1.1,0.2,0.419]]},{"n":"L.J. Figueroa","c":["hum"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.7,"rpg":4.8,"apg":2,"spg":1.3,"bpg":0.4,"gp":16,"ns":1,"hi":[2023,17.7],"ss":[[2023,"hum",16,17.7,4.8,2,1.3,0.4,0.554]]},{"n":"Ricky Ledo","c":["bay"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":17.7,"rpg":5.2,"apg":4.1,"spg":1.3,"bpg":0.4,"gp":21,"ns":1,"hi":[2018,17.7],"ss":[[2018,"bay",21,17.7,5.2,4.1,1.3,0.4,0.449]]},{"n":"Angel Rodriguez","c":["bay"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":17.6,"rpg":5,"apg":7.7,"spg":2.2,"bpg":0,"gp":38,"ns":2,"hi":[2021,19],"ss":[[2020,"bay",14,15.2,4.1,6.4,2.3,0.1,0.413],[2021,"bay",24,19,5.6,8.4,2.1,0,0.462]]},{"n":"Javier Mojica","c":["bay"],"d":[2010,2020],"pos":"SG","posSrc":"perfil","ppg":17.6,"rpg":4.1,"apg":3.7,"spg":1.1,"bpg":0.1,"gp":89,"ns":3,"hi":[2021,18.8],"ss":[[2019,"bay",37,17.3,3.5,3.3,0.9,0.2,0.446],[2020,"bay",21,16.5,5,4,2,0,0.462],[2021,"bay",31,18.8,4.2,4.1,0.8,0,0.445]]},{"n":"Rigoberto Mendoza","c":["agu"],"d":[2010,2020],"pos":"SF","posSrc":"perfil","ppg":17.6,"rpg":5.8,"apg":3.9,"spg":1.6,"bpg":0.4,"gp":94,"ns":2,"hi":[2016,18],"ss":[[2016,"agu",44,18,5.5,2.8,1.5,0.5,0.494],[2026,"agu",50,17.3,6,4.9,1.6,0.3,0.515]]},{"n":"Angel Nunez","c":["gua"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":17.6,"rpg":7.2,"apg":2.5,"spg":0.8,"bpg":1.1,"gp":21,"ns":1,"hi":[2021,17.6],"ss":[[2021,"gua",21,17.6,7.2,2.5,0.8,1.1,0.433]]},{"n":"R.J. Melendez","c":["are"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.5,"rpg":5.2,"apg":2.3,"spg":0.8,"bpg":0.7,"gp":23,"ns":1,"hi":[2026,17.5],"ss":[[2026,"are",23,17.5,5.2,2.3,0.8,0.7,0.549]]},{"n":"Gabe York","c":["gua","sge"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":17.4,"rpg":3.7,"apg":3.6,"spg":0.9,"bpg":0,"gp":35,"ns":2,"hi":[2024,17.8],"ss":[[2024,"gua",13,17.8,3.2,3.8,1.2,0,0.409],[2025,"sge",22,17.2,4,3.5,0.7,0,0.471]]},{"n":"Norris Cole","c":["man"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":17.4,"rpg":2.6,"apg":8.2,"spg":1,"bpg":0.1,"gp":41,"ns":1,"hi":[2024,17.4],"ss":[[2024,"man",41,17.4,2.6,8.2,1,0.1,0.499]]},{"n":"Zavier Simpson","c":["hum"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":17.4,"rpg":3.7,"apg":5.7,"spg":1,"bpg":0,"gp":10,"ns":1,"hi":[2023,17.4],"ss":[[2023,"hum",10,17.4,3.7,5.7,1,0,0.54]]},{"n":"Melo Trimble","c":["que"],"d":[2010],"pos":"PG","posSrc":"perfil","ppg":17.4,"rpg":2.8,"apg":6.3,"spg":0.9,"bpg":0,"gp":26,"ns":1,"hi":[2019,17.4],"ss":[[2019,"que",26,17.4,2.8,6.3,0.9,0,0.481]]},{"n":"Kristian Doolittle","c":["bay","man"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":17.3,"rpg":8.5,"apg":4.2,"spg":0.7,"bpg":0.3,"gp":38,"ns":2,"hi":[2026,18.4],"ss":[[2024,"bay",20,16.3,8.6,3.9,0.7,0.5,0.448],[2026,"man",18,18.4,8.3,4.5,0.7,0.1,0.463]]},{"n":"Victor Rudd","c":["are","faj"],"d":[2010,2020],"pos":"PF","posSrc":"perfil","ppg":17.1,"rpg":7.7,"apg":4.2,"spg":0.9,"bpg":0.4,"gp":99,"ns":5,"hi":[2023,21.5],"ss":[[2019,"are",35,16.5,7.3,3.6,1.3,0.4,0.429],[2020,"are",11,18.8,7.1,4.1,0.8,0.1,0.462],[2021,"faj",37,17.4,8.1,4.5,0.6,0.4,0.429],[2022,"faj",12,14.6,7.9,4.6,null,null,null],[2023,"faj",4,21.5,8.0,5.8,null,null,null]]},{"n":"Christopher Ortiz","c":["guy","man"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.2,"rpg":5.8,"apg":2,"spg":0.9,"bpg":0.4,"gp":82,"ns":3,"hi":[2023,18.7],"ss":[[2021,"guy",34,15.3,5.6,2.1,1,0.3,0.442],[2022,"guy",15,18.1,5.1,1.7,0.7,0.6,0.423],[2023,"man",33,18.7,6.2,2,0.8,0.4,0.487]]},{"n":"A.D. Vassallo","c":["are","pon"],"d":[2010,2020],"pos":"SF","posSrc":"perfil","ppg":17.2,"rpg":5,"apg":2.7,"spg":0.6,"bpg":0.4,"gp":189,"ns":5,"hi":[2016,18.4],"ss":[[2013,"are",43,17.8,6.2,2.6,0.7,0.6,0.425],[2016,"pon",34,18.4,4.1,3.7,0.7,0.4,0.443],[2018,"pon",47,17.1,4.5,2.3,0.6,0.2,0.426],[2019,"pon",53,16.4,4.9,2.5,0.6,0.5,0.434],[2020,"pon",12,15.5,5.2,2.8,0.7,0.4,0.403]]},{"n":"Angel Matias","c":["san"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.2,"rpg":5.5,"apg":2.4,"spg":0.6,"bpg":0.3,"gp":76,"ns":2,"hi":[2023,17.9],"ss":[[2023,"san",42,17.9,6.1,2.4,0.8,0.4,0.545],[2024,"san",34,16.4,4.7,2.3,0.4,0.2,0.55]]},{"n":"Bryce Cotton","c":["gua"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":17.2,"rpg":3.1,"apg":5.1,"spg":1.5,"bpg":0,"gp":23,"ns":1,"hi":[2025,17.2],"ss":[[2025,"gua",23,17.2,3.1,5.1,1.5,0,0.462]]},{"n":"Sam Waardenburg","c":["may"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":17.2,"rpg":7.6,"apg":2.4,"spg":0.9,"bpg":0.8,"gp":46,"ns":1,"hi":[2025,17.2],"ss":[[2025,"may",46,17.2,7.6,2.4,0.9,0.8,0.538]]},{"n":"JaVale McGee","c":["bay"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":17.2,"rpg":9,"apg":1.6,"spg":0.9,"bpg":1.5,"gp":41,"ns":1,"hi":[2025,17.2],"ss":[[2025,"bay",41,17.2,9,1.6,0.9,1.5,0.566]]},{"n":"Tyreke Evans","c":["may"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":17.2,"rpg":3.8,"apg":3.3,"spg":1,"bpg":0.2,"gp":12,"ns":1,"hi":[2023,17.2],"ss":[[2023,"may",12,17.2,3.8,3.3,1,0.2,0.395]]},{"n":"Will Barton","c":["san"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":17.2,"rpg":4.1,"apg":4,"spg":0.8,"bpg":0.4,"gp":18,"ns":1,"hi":[2024,17.2],"ss":[[2024,"san",18,17.2,4.1,4,0.8,0.4,0.422]]},{"n":"Cheick Diallo","c":["san","man"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":17.1,"rpg":10.2,"apg":1.4,"spg":0.5,"bpg":0.9,"gp":103,"ns":4,"hi":[2025,19.3],"ss":[[2022,"san",27,16.7,13.8,1.2,0.3,1,0.66],[2024,"man",31,15.7,8.3,1.2,0.5,0.8,0.664],[2025,"man",33,19.3,9.6,1.8,0.6,0.9,0.637],[2026,"man",12,15.9,8.3,0.9,0.6,0.6,0.62]]},{"n":"Nick Perkins","c":["may","sge"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":17.1,"rpg":6.4,"apg":1.8,"spg":0.5,"bpg":0.5,"gp":79,"ns":3,"hi":[2025,18.9],"ss":[[2024,"may",22,18,6.6,1.4,0.6,0.5,0.502],[2025,"may",20,18.9,7.4,2.2,0.5,0.5,0.481],[2026,"sge",37,15.5,5.8,1.9,0.4,0.4,0.463]]},{"n":"Montrezl Harrell","c":["sge"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":17.1,"rpg":9.9,"apg":2.8,"spg":0.7,"bpg":0.5,"gp":27,"ns":1,"hi":[2026,17.1],"ss":[[2026,"sge",27,17.1,9.9,2.8,0.7,0.5,0.625]]},{"n":"Christian Dalmau","c":["bay"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":17.1,"rpg":3,"apg":4.1,"spg":1.5,"bpg":0.2,"gp":40,"ns":1,"hi":[2012,17.1],"ss":[[2012,"bay",40,17.1,3,4.1,1.5,0.2,0.376]]},{"n":"Juan Miguel Suero","c":["faj"],"d":[2010],"pos":"PG","posSrc":"perfil","ppg":17,"rpg":5.4,"apg":5.7,"spg":1.5,"bpg":0.4,"gp":26,"ns":1,"hi":[2019,17],"ss":[[2019,"faj",26,17,5.4,5.7,1.5,0.4,0.483]]},{"n":"Louis King","c":["cag"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":16.9,"rpg":6,"apg":3.3,"spg":1.4,"bpg":0.7,"gp":113,"ns":3,"hi":[2024,18.5],"ss":[[2024,"cag",41,18.5,6,2.8,1.6,0.8,0.469],[2025,"cag",29,16.2,5.1,3.2,1.2,0.4,0.452],[2026,"cag",43,15.8,6.5,3.9,1.3,0.7,0.465]]},{"n":"Jaysean Paige","c":["gua"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":16.9,"rpg":3.5,"apg":3.6,"spg":1.3,"bpg":0.2,"gp":146,"ns":4,"hi":[2024,18.4],"ss":[[2023,"gua",46,16.6,3.3,3.1,1.1,0.1,0.459],[2024,"gua",40,18.4,4,3.6,1.6,0.4,0.459],[2025,"gua",29,15.6,3.3,3.7,1.2,0.2,0.466],[2026,"gua",31,16.7,3.4,4.2,1.4,0.3,0.444]]},{"n":"Thomas Robinson","c":["san","que","pon","hum"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":16.8,"rpg":9.5,"apg":1.8,"spg":0.8,"bpg":0.7,"gp":79,"ns":4,"hi":[2021,17.4],"ss":[[2021,"san",37,17.4,9.9,1.7,0.8,0.9,0.586],[2022,"que",18,16.8,10.6,2.4,0.9,0.4,0.49],[2023,"pon",11,16.5,5.9,1.1,0.8,0.7,0.603],[2023,"hum",13,15.5,9.9,1.7,0.8,0.8,0.541]]},{"n":"Alex Galindo","c":["san","may"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":16.7,"rpg":4.1,"apg":1.4,"spg":0.7,"bpg":0.3,"gp":79,"ns":2,"hi":[2016,17.6],"ss":[[2013,"san",46,16,3.8,1,0.8,0.3,0.418],[2016,"may",33,17.6,4.5,1.9,0.6,0.3,0.473]]},{"n":"Timothy Soares","c":["gua","are"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16.7,"rpg":7.8,"apg":2.1,"spg":0.8,"bpg":1.3,"gp":47,"ns":2,"hi":[2026,17],"ss":[[2023,"gua",19,16.3,7.6,1.9,1.2,1.6,0.575],[2026,"are",28,17,7.9,2.3,0.6,1.1,0.522]]},{"n":"Gilberto Clavell","c":["agu"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":16.7,"rpg":3.9,"apg":1.7,"spg":1,"bpg":0.1,"gp":7,"ns":1,"hi":[2020,16.7],"ss":[[2020,"agu",7,16.7,3.9,1.7,1,0.1,0.518]]},{"n":"David Laury","c":["may"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":16.7,"rpg":9.3,"apg":3,"spg":0.8,"bpg":0.6,"gp":36,"ns":1,"hi":[2017,16.7],"ss":[[2017,"may",36,16.7,9.3,3,0.8,0.6,0.504]]},{"n":"David Huertas","c":["que","are"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":16.6,"rpg":4.4,"apg":3.4,"spg":0.7,"bpg":0.2,"gp":208,"ns":4,"hi":[2014,17.5],"ss":[[2013,"que",51,15.8,4.3,4,0.8,0.2,0.412],[2014,"que",46,17.5,4.7,3.1,0.8,0.1,0.472],[2017,"are",54,17.4,4.3,3.4,0.5,0.2,0.434],[2018,"are",57,16,4.2,3,0.9,0.2,0.418]]},{"n":"Phillip Wheeler","c":["que"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":16.6,"rpg":5.1,"apg":1.1,"spg":1.1,"bpg":0.7,"gp":54,"ns":2,"hi":[2022,17.3],"ss":[[2022,"que",30,17.3,5.9,1.3,1.2,0.8,0.509],[2025,"que",24,15.8,4.2,0.8,1,0.5,0.518]]},{"n":"Tony Bishop Jr","c":["gua","sge"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16.6,"rpg":8.3,"apg":2.5,"spg":0.9,"bpg":0.6,"gp":55,"ns":2,"hi":[2021,16.6],"ss":[[2021,"gua",34,16.6,7.9,2.7,0.9,0.6,0.46],[2023,"sge",21,16.6,9,2.2,0.9,0.7,0.491]]},{"n":"Andre Curbelo","c":["sge"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16.6,"rpg":6.6,"apg":6.1,"spg":1.4,"bpg":0.5,"gp":31,"ns":1,"hi":[2026,16.6],"ss":[[2026,"sge",31,16.6,6.6,6.1,1.4,0.5,0.511]]},{"n":"Peter John Ramos","c":["que","bay"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":16.5,"rpg":8.5,"apg":1.7,"spg":0.2,"bpg":1,"gp":89,"ns":2,"hi":[2012,17.1],"ss":[[2012,"que",40,17.1,8.8,1.6,0.3,1.2,0.599],[2016,"bay",49,16,8.2,1.8,0.2,0.8,0.569]]},{"n":"Scottie James","c":["car"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":16.5,"rpg":8.5,"apg":2.1,"spg":0.4,"bpg":0.5,"gp":42,"ns":1,"hi":[2024,16.5],"ss":[[2024,"car",42,16.5,8.5,2.1,0.4,0.5,0.484]]},{"n":"Carlos Arroyo","c":["faj"],"d":[2010],"pos":"PG","posSrc":"perfil","ppg":16.5,"rpg":2.7,"apg":7.5,"spg":0.9,"bpg":0,"gp":43,"ns":1,"hi":[2018,16.5],"ss":[[2018,"faj",43,16.5,2.7,7.5,0.9,0,0.408]]},{"n":"Jahvari Josiah","c":["guy"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":16.5,"rpg":5.2,"apg":2.1,"spg":1.7,"bpg":0.3,"gp":30,"ns":1,"hi":[2022,16.5],"ss":[[2022,"guy",30,16.5,5.2,2.1,1.7,0.3,0.486]]},{"n":"Tremont Waters","c":["car"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":16.4,"rpg":2.7,"apg":6.9,"spg":1.9,"bpg":0.1,"gp":116,"ns":4,"hi":[2022,18.2],"ss":[[2022,"car",29,18.2,2.7,7.8,1.6,0,0.442],[2023,"car",42,15.3,2.7,6.5,2,0,0.42],[2024,"car",13,15.3,2.3,6.3,1.8,0,0.411],[2026,"car",32,16.6,2.7,6.7,1.9,0.2,0.394]]},{"n":"Akil Mitchell","c":["hum"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16.4,"rpg":6.7,"apg":3.3,"spg":1,"bpg":0.4,"gp":16,"ns":1,"hi":[2023,16.4],"ss":[[2023,"hum",16,16.4,6.7,3.3,1,0.4,0.544]]},{"n":"Chinanu Onuaku","c":["agu"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":16.4,"rpg":10.1,"apg":3.3,"spg":0.9,"bpg":0.8,"gp":21,"ns":1,"hi":[2024,16.4],"ss":[[2024,"agu",21,16.4,10.1,3.3,0.9,0.8,0.524]]},{"n":"Emmy Andujar","c":["faj"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16.4,"rpg":6.7,"apg":4.9,"spg":1.1,"bpg":0.3,"gp":12,"ns":1,"hi":[2023,16.4],"ss":[[2023,"faj",12,16.4,6.7,4.9,1.1,0.3,0.5]]},{"n":"Torrey Craig","c":["gua"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":16.4,"rpg":6.2,"apg":3.8,"spg":1.1,"bpg":1.5,"gp":17,"ns":1,"hi":[2026,16.4],"ss":[[2026,"gua",17,16.4,6.2,3.8,1.1,1.5,0.48]]},{"n":"Mike Rosario","c":["que"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":16.4,"rpg":3.2,"apg":2.3,"spg":1.1,"bpg":0,"gp":47,"ns":1,"hi":[2017,16.4],"ss":[[2017,"que",47,16.4,3.2,2.3,1.1,0,0.45]]},{"n":"Will Daniels","c":["gua","guy"],"d":[2010,2020],"pos":"SF","posSrc":"perfil","ppg":16.3,"rpg":6,"apg":1.6,"spg":1.1,"bpg":0.6,"gp":67,"ns":2,"hi":[2020,16.4],"ss":[[2015,"gua",48,16.2,6.4,1.6,1.1,0.7,0.526],[2020,"guy",19,16.4,5.1,1.7,1.1,0.5,0.543]]},{"n":"Jessie Govan","c":["may"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":16.3,"rpg":6,"apg":1.3,"spg":0.9,"bpg":0.5,"gp":19,"ns":1,"hi":[2021,16.3],"ss":[[2021,"may",19,16.3,6,1.3,0.9,0.5,0.595]]},{"n":"Alex Morales","c":["man"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16.1,"rpg":7.8,"apg":3.9,"spg":1,"bpg":0.7,"gp":11,"ns":1,"hi":[2023,16.1],"ss":[[2023,"man",11,16.1,7.8,3.9,1,0.7,0.548]]},{"n":"Georgie Pacheco-Ortiz","c":["may"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":16.1,"rpg":2.9,"apg":3.5,"spg":0.7,"bpg":0,"gp":34,"ns":1,"hi":[2024,16.1],"ss":[[2024,"may",34,16.1,2.9,3.5,0.7,0,0.445]]},{"n":"Ivan Gandia-Rosa","c":["agu"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":16,"rpg":3.3,"apg":4.4,"spg":0.4,"bpg":0.1,"gp":27,"ns":1,"hi":[2025,16],"ss":[[2025,"agu",27,16,3.3,4.4,0.4,0.1,0.446]]},{"n":"Ben McCauley","c":["guy"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":16,"rpg":8,"apg":3.2,"spg":0.7,"bpg":0.1,"gp":24,"ns":1,"hi":[2022,16],"ss":[[2022,"guy",24,16,8,3.2,0.7,0.1,0.412]]},{"n":"Greg Smith","c":["bay"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":16,"rpg":10,"apg":2.8,"spg":1.3,"bpg":0.7,"gp":47,"ns":1,"hi":[2019,16],"ss":[[2019,"bay",47,16,10,2.8,1.3,0.7,0.57]]},{"n":"Will Martinez","c":["cac","car"],"d":[2010,2020],"pos":"SG","posSrc":"perfil","ppg":15.9,"rpg":2.3,"apg":1.6,"spg":0.7,"bpg":0.1,"gp":60,"ns":2,"hi":[2021,16.6],"ss":[[2017,"cac",32,15.2,2.7,1.9,0.8,0.1,0.409],[2021,"car",28,16.6,1.9,1.2,0.5,0,0.437]]},{"n":"Benito Santiago Jr","c":["bay"],"d":[2010],"pos":"SG","posSrc":"perfil","ppg":15.9,"rpg":2.9,"apg":2.4,"spg":1.3,"bpg":0.3,"gp":41,"ns":1,"hi":[2019,15.9],"ss":[[2019,"bay",41,15.9,2.9,2.4,1.3,0.3,0.462]]},{"n":"Max Abmas","c":["gua"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":15.9,"rpg":2.6,"apg":5.4,"spg":0.5,"bpg":0,"gp":10,"ns":1,"hi":[2026,15.9],"ss":[[2026,"gua",10,15.9,2.6,5.4,0.5,0,0.505]]},{"n":"Renaldo Balkman","c":["are"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":15.8,"rpg":7.8,"apg":2.1,"spg":1.3,"bpg":1.2,"gp":99,"ns":2,"hi":[2016,15.9],"ss":[[2015,"are",52,15.7,7.2,1.7,1.3,1.2,0.545],[2016,"are",47,15.9,8.4,2.5,1.4,1.2,0.531]]},{"n":"Joel Soriano","c":["agu"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":15.8,"rpg":8.9,"apg":1.8,"spg":0.3,"bpg":1.1,"gp":37,"ns":2,"hi":[2025,15.9],"ss":[[2025,"agu",13,15.9,10.8,2.2,0.5,1.2,0.593],[2026,"agu",24,15.8,7.9,1.6,0.2,1,0.543]]},{"n":"Kaleb Werson","c":["may"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":15.8,"rpg":8.1,"apg":2.7,"spg":0.3,"bpg":0.8,"gp":12,"ns":1,"hi":[2022,15.8],"ss":[[2022,"may",12,15.8,8.1,2.7,0.3,0.8,0.55]]},{"n":"Tai Wesley","c":["guy"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":15.8,"rpg":6.4,"apg":2.9,"spg":0.7,"bpg":1.3,"gp":24,"ns":1,"hi":[2019,15.8],"ss":[[2019,"guy",24,15.8,6.4,2.9,0.7,1.3,0.539]]},{"n":"Jalen Crutcher","c":["pon"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":15.8,"rpg":3.7,"apg":6.3,"spg":0.7,"bpg":0.1,"gp":37,"ns":1,"hi":[2026,15.8],"ss":[[2026,"pon",37,15.8,3.7,6.3,0.7,0.1,0.48]]},{"n":"Josh Perkins","c":["guy"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":15.7,"rpg":3.6,"apg":5.9,"spg":0.8,"bpg":0.3,"gp":15,"ns":1,"hi":[2022,15.7],"ss":[[2022,"guy",15,15.7,3.6,5.9,0.8,0.3,0.455]]},{"n":"Stevie Thompson","c":["bay"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":15.7,"rpg":4,"apg":2.3,"spg":1.2,"bpg":0.3,"gp":23,"ns":1,"hi":[2024,15.7],"ss":[[2024,"bay",23,15.7,4,2.3,1.2,0.3,0.427]]},{"n":"Tyquan Rolon","c":["que"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":15.7,"rpg":3.5,"apg":3,"spg":0.5,"bpg":0.3,"gp":13,"ns":1,"hi":[2024,15.7],"ss":[[2024,"que",13,15.7,3.5,3,0.5,0.3,0.479]]},{"n":"Nick Rakocevic","c":["agu"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":15.6,"rpg":8.2,"apg":1.4,"spg":0.4,"bpg":0.6,"gp":16,"ns":1,"hi":[2025,15.6],"ss":[[2025,"agu",16,15.6,8.2,1.4,0.4,0.6,0.469]]},{"n":"Cameron McGriff","c":["agu"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":15.6,"rpg":5.1,"apg":1.8,"spg":0.8,"bpg":0.2,"gp":19,"ns":1,"hi":[2024,15.6],"ss":[[2024,"agu",19,15.6,5.1,1.8,0.8,0.2,0.436]]},{"n":"Xavier Cooks","c":["bay"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":15.5,"rpg":6.6,"apg":1.8,"spg":0.7,"bpg":1.1,"gp":13,"ns":1,"hi":[2026,15.5],"ss":[[2026,"bay",13,15.5,6.6,1.8,0.7,1.1,0.685]]},{"n":"Gary Browne","c":["que"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":15.5,"rpg":4.9,"apg":6.5,"spg":1.1,"bpg":0.1,"gp":18,"ns":1,"hi":[2022,15.5],"ss":[[2022,"que",18,15.5,4.9,6.5,1.1,0.1,0.392]]},{"n":"Gaby Belardo","c":["hum"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":15.4,"rpg":3.9,"apg":5.2,"spg":1,"bpg":0,"gp":29,"ns":1,"hi":[2022,15.4],"ss":[[2022,"hum",29,15.4,3.9,5.2,1,0,0.46]]},{"n":"Dewan Hernandez","c":["san"],"d":[2020],"pos":"C","posSrc":"perfil","ppg":15.4,"rpg":8.7,"apg":1.7,"spg":0.6,"bpg":1,"gp":10,"ns":1,"hi":[2023,15.4],"ss":[[2023,"san",10,15.4,8.7,1.7,0.6,1,0.553]]},{"n":"Jordan Murphy","c":["pon"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":15.4,"rpg":6.6,"apg":1.4,"spg":0.7,"bpg":0.8,"gp":42,"ns":1,"hi":[2025,15.4],"ss":[[2025,"pon",42,15.4,6.6,1.4,0.7,0.8,0.504]]},{"n":"Brian Conklin","c":["que"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":15.4,"rpg":6.2,"apg":2.1,"spg":1,"bpg":0.3,"gp":40,"ns":1,"hi":[2016,15.4],"ss":[[2016,"que",40,15.4,6.2,2.1,1,0.3,0.499]]},{"n":"Leon Williams","c":["san"],"d":[2010],"pos":"C","posSrc":"perfil","ppg":15.4,"rpg":9.5,"apg":1.3,"spg":1.3,"bpg":0.5,"gp":47,"ns":1,"hi":[2014,15.4],"ss":[[2014,"san",47,15.4,9.5,1.3,1.3,0.5,0.542]]},{"n":"Ricky Sanchez","c":["man"],"d":[2010],"pos":"PF","posSrc":"perfil","ppg":15.3,"rpg":6.6,"apg":1.9,"spg":0.8,"bpg":0.7,"gp":50,"ns":1,"hi":[2015,15.3],"ss":[[2015,"man",50,15.3,6.6,1.9,0.8,0.7,0.406]]},{"n":"Weyinmi Efejuku Rose","c":["may"],"d":[2010],"pos":"SF","posSrc":"perfil","ppg":15.3,"rpg":4.7,"apg":2.1,"spg":0.9,"bpg":0.2,"gp":34,"ns":1,"hi":[2013,15.3],"ss":[[2013,"may",34,15.3,4.7,2.1,0.9,0.2,0.445]]},{"n":"Kay Felder","c":["cag"],"d":[2020],"pos":"PG","posSrc":"perfil","ppg":15.3,"rpg":1.4,"apg":5,"spg":1.7,"bpg":0.4,"gp":7,"ns":1,"hi":[2025,15.3],"ss":[[2025,"cag",7,15.3,1.4,5,1.7,0.4,0.427]]},{"n":"Milton Doyle","c":["may"],"d":[2020],"pos":"SF","posSrc":"perfil","ppg":15.3,"rpg":5.7,"apg":5.6,"spg":0.8,"bpg":0.1,"gp":20,"ns":1,"hi":[2024,15.3],"ss":[[2024,"may",20,15.3,5.7,5.6,0.8,0.1,0.406]]},{"n":"Guillermo Diaz","c":["agu"],"d":[2020],"pos":"SG","posSrc":"perfil","ppg":15.3,"rpg":2.1,"apg":1.6,"spg":1.1,"bpg":0.4,"gp":8,"ns":1,"hi":[2020,15.3],"ss":[[2020,"agu",8,15.3,2.1,1.6,1.1,0.4,0.553]]},{"n":"Braxton Key","c":["bay"],"d":[2020],"pos":"PF","posSrc":"perfil","ppg":15.2,"rpg":7.5,"apg":4.1,"spg":2.2,"bpg":1.1,"gp":17,"ns":1,"hi":[2023,15.2],"ss":[[2023,"bay",17,15.2,7.5,4.1,2.2,1.1,0.502]]}];
const POOL_PATCH = {
  'Gary Browne':{c:['bay'],t:['mvp','native','champion']},
  'Travis Trice':{c:['cag'],t:['mvp','champion','import']},
  'Renaldo Balkman':{c:['bay'],t:['champion','import','nba']}
};
/* ---- Jugadores recuperados ----
   n: nombre · c: claves de club · d: décadas · pos · tags · bio
   Los que no traen club es porque la fuente no lo dice. */
const PLAYERS_NEW=[
  {n:'Carlos Arroyo',c:['faj','san','pon'],d:[1990,2000,2010],pos:'PG',
   t:['champion','native','nba','legend'],
   b:'Doce temporadas en el BSN. Novato del Año en 1996 con Fajardo, cinco campeonatos con los Cangrejeros entre 1998 y 2003, MVP de la final en 2003, MVP del Juego de Estrellas en 2017 y líder de asistencias en 2018. Se retiró con Ponce en 2019. Santurce retiró su número 7 el 7 de octubre de 2021. Hoy es coapoderado de los Vaqueros.'},
  {n:'J. J. Barea',c:['may','san'],d:[2000,2020],pos:'PG',
   t:['native','nba','legend'],
   b:'Debutó con los Indios de Mayagüez en 2001 y volvió con ellos en 2002. Jugó con los Cangrejeros en 2006 y otra vez en 2021 y 2022. Campeón de la NBA con Dallas en 2011. Dirigió a Mayagüez en 2017 y a los Mets en 2024 y 2025.'},
  {n:'Walter Hodge',c:['are'],d:[2010,2020],pos:'PG',t:['mvp','champion','native'],
   b:'MVP de la liga en 2014 y otra vez en 2022 con Arecibo, y MVP de la final de 2018.'},
  {n:'Reyshawn Terry',c:['que'],d:[2010],pos:'F',t:['mvp','scoring','import'],
   b:'MVP y líder de anotación y rebotes en 2018: 835 puntos en 36 juegos, 23.2 por partido.'},
  {n:'Renaldo Balkman',c:['are','bay'],d:[2010,2020],pos:'F',t:['champion','import','nba'],
   b:'MVP de la final en 2016 con Arecibo y otra vez en 2026 con Bayamón, a los cuarenta y un años.'},
  {n:'George Conditt IV',c:['car'],d:[2020],pos:'C',t:['import'],ppg:14.6,rpg:9.2,
   b:'Defensor del Año en 2024 con los Gigantes: 14.6 puntos y 9.2 rebotes.'},
  {n:'Jhivvan Jackson',c:['man'],d:[2020],pos:'G',t:['native'],ppg:12.0,apg:2.9,rpg:2.7,
   b:'Novato del Año en 2024 con los Osos de Manatí.'},
  {n:'Juan Báez',c:['rio'],d:[1950,1960],pos:'F',t:['mvp','legend'],
   b:'Tres veces MVP con los Cardenales de Río Piedras: 1957, 1963 y 1964.'},
  {n:'Raúl «Tinajón» Feliciano',c:['upr','rio'],d:[1950],pos:'F',t:['mvp','legend'],
   b:'MVP en 1951 con los Gallitos de la UPR y en 1955 con los Cardenales de Río Piedras.'},
  {n:'James Carter',c:['guy'],d:[1980,1990,2000],pos:'PG',t:['mvp','legend'],
   b:'Máximo asistente histórico del BSN con 3,025, y MVP en 1991 y 1994 con los Brujos de Guayama.'},
  {n:'Jerome Mincy',c:[],d:[1980,1990],pos:'F',t:['native','legend'],
   b:'Una de las figuras que definieron el baloncesto puertorriqueño de los ochenta.'},
  {n:'Ángel «Munch» Cruz',c:[],d:[1980,1990],pos:'G',t:['native'],
   b:'Figura de los ochenta citada junto a Morales, Dalmau y Piculín.'},
  {n:'Ramón Rivas',c:[],d:[1980,1990],pos:'C',t:['native','nba'],
   b:'Empezó en el BSN y llegó a la NBA.'},
  {n:'Daniel Santiago',c:[],d:[1990,2000],pos:'C',t:['native','nba'],
   b:'Empezó en el BSN y llegó a la NBA.'},
  {n:'Butch Lee',c:[],d:[1970,1980],pos:'G',t:['native','nba','legend'],
   b:'El primer puertorriqueño y el primer jugador del BSN en llegar a la NBA, y el primero en ganar allí un campeonato.'},
  {n:'Larry Ayuso',c:['san'],d:[2000,2010],pos:'G',t:['champion','native'],
   b:'Parte de la plantilla con la que Santurce ganó el título de 2007.'},
  {n:'Robert «Tractor» Traylor',c:['san'],d:[2000],pos:'C',t:['champion','import','nba'],
   b:'Ala-pívot exNBA que encabezó el título de los Cangrejeros en 2007. Falleció en 2011.'},
  {n:'Lee Benson',c:[],d:[2000,2010],pos:'F',t:['import'],
   b:'Rompió en 2008 el récord de rebotes en una temporada que Rubén Rodríguez había fijado en 1978.'},
  {n:'Jeffrion Aubry',c:[],d:[1990,2000],pos:'C',t:['native'],
   b:'Segundo de todos los tiempos en tapones con 642.'},
  {n:'Damion James',c:[],d:[2010],pos:'F',t:['scoring','import','nba'],
   b:'Líder de anotación y de rebotes en 2016.'},
  {n:'Alex Abreu',c:[],d:[2010],pos:'PG',t:['native'],
   b:'Líder de asistencias en 2016.'},
  {n:'Eric Dawson',c:['faj'],d:[2010],pos:'C',t:['import'],
   b:'Líder de rebotes en 2017.'},
  {n:'Brandon Costner',c:['hum'],d:[2010],pos:'F',t:['import'],ppg:19.6,
   b:'Segundo en anotación en 2018 con los Caciques de Humacao: 668 puntos en 34 juegos.'},
  {n:'Darnell Hinson',c:['hum'],d:[2000,2010],pos:'G',t:['native'],
   b:'Primera selección del sorteo de 2009, por los Caciques de Humacao.'},
  {n:'Ángel Daniel Vassallo',c:['que'],d:[2010],pos:'G',t:['mvp','native'],
   b:'MVP de la liga en 2016. Hoy dirige a los Piratas de Quebradillas.'},
  {n:'Akil Mitchell',c:[],d:[2020],pos:'F',t:['import'],
   b:'Líder de rebotes en 2025.'},
  {n:'Ángel Rodríguez',c:[],d:[2020],pos:'PG',t:['native'],
   b:'Líder de asistencias en 2025 y una de las voces contra la tercera plaza de refuerzo.'},
  {n:'Chris Ortiz',c:[],d:[2010,2020],pos:'F',t:['native'],
   b:'Firmó junto a Browne, Hodge y Rodríguez el video contra la tercera plaza de refuerzo en 2024.'},
  {n:'Xavier Cooks',c:['bay'],d:[2020],pos:'F',t:['import'],
   b:'Refuerzo de Bayamón para la temporada 2026.'},
  {n:'Jaylin Galloway',c:['bay'],d:[2020],pos:'F',t:['import'],
   b:'Refuerzo de Bayamón para la temporada 2026.'},
  {n:'Rigoberto Mendoza',c:['agu'],d:[2020],pos:'G',t:['import'],
   b:'Dominicano. Líder ofensivo de Aguada en la final de 2026: 22 puntos en el cuarto juego, 15 en el primer parcial.'}
];
const MESES=['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre'];
const DIAS=['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
/* ============================================================
   CATEGORIES
   ============================================================ */
const CATS={
  mvp:['Ganó un MVP',p=>p.t.includes('mvp')],
  scoring:['Campeón de anotación',p=>p.t.includes('scoring')],
  champion:['Campeón del BSN',p=>p.t.includes('champion')],
  import:['Jugó de refuerzo',p=>p.t.includes('import')],
  native:['Nativo o nativizado',p=>p.t.includes('native')],
  nba:['También jugó en la NBA',p=>p.t.includes('nba')],
  '10k':['10.000+ puntos',p=>p.t.includes('10k')],
  legend:['Leyenda de la liga',p=>p.t.includes('legend')],
  /* backlog item 6 / grid fix (2026-09-14) — a career-wide weighted average
     silently failed real 20+ ppg seasons whenever a player's other seasons
     pulled it back under 20 (Hollis-Jefferson 21.7 in 2023, Stockton 20.7 in
     2021 — both real, externally confirmed, both rejected before this fix).
     Best-season ppg matches how every other category here already works:
     a lifetime fact about the player, not a same-season-as-the-club
     requirement (real Immaculate Grid doesn't require that co-occurrence
     either). Falls back to career ppg only for hand-authored legends with
     no season breakdown (no `hi` field) -- unchanged for them. */
  p20:['Promedió 20+ puntos',p=>{const v=p.hi?p.hi[1]:p.ppg;return v!=null&&v>=20;}],
  guard:['Base o escolta',p=>/G|PG|SG/.test(p.pos||'')],
  big:['Poste',p=>/C|PF|F\/C/.test(p.pos||'')],
  /* backlog item 6, part 1 (2026-09-14) — d1950/d1960/d1970 used to be
     separate categories at 4/9/13 POOL players each, rarely enough to
     overlap with any given club and mostly landing as accidental
     single-answer traps rather than real puzzle variety. Folded into one
     bucket: 18 players by real union (not the naive 4+9+13=26 sum — some
     players span more than one of those decades), usable against 9 of
     the 19 clubs. */
  dpre1980:['Jugó antes de 1980',p=>p.d.some(y=>y<1980)],
  d1980:['Jugó en los 80',p=>p.d.includes(1980)],
  d1990:['Jugó en los 90',p=>p.d.includes(1990)],
  d2000:['Jugó en los 2000',p=>p.d.includes(2000)],
  d2010:['Jugó en los 2010',p=>p.d.includes(2010)],
  d2020:['Jugó en los 2020',p=>p.d.includes(2020)]
};
/* ============================================================
   SUBE Y BAJA
   Two careers, one question. Runs on the only fully verified
   numbers in the archive, so it never has to guess.
   ============================================================ */
const HL_SETS=[
  {label:'puntos de carrera',rows:()=>LEADERS.points.map(r=>[r[1],r[4]]),unit:'puntos'},
  {label:'rebotes de carrera',rows:()=>LEADERS.rebounds.map(r=>[r[1],r[4]]),unit:'rebotes'},
  {label:'asistencias de carrera',rows:()=>LEADERS.assists.map(r=>[r[1],r[4]]),unit:'asistencias'},
  {label:'juegos jugados',rows:()=>LEADERS.points.map(r=>[r[1],r[5]]),unit:'juegos'},
  {label:'títulos de la franquicia',rows:()=>FKEYS.filter(k=>F[k].won.length).map(k=>[F[k].name,F[k].won.length]),unit:'títulos'}
];
