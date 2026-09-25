/* PHASE_1_SPLIT STEP 9. hydrate() and the whole boot sequence (ARRANQUE), moved out of
   web/index.html's inline <script>, byte for byte -- no renaming, no reformatting, no
   reordering. Loaded via <script src="js/init.js"> right after js/tabs.js, before whatever
   still has to stay inline.

   One contiguous block: the "ARRANQUE" section (splashProgress, hideSplash, SPLASH_DEADLINE,
   ligaFold, finishBoot, runBoot, and the setInterval(checkRollover,60000) statement) directly
   into hydrate(). These are the only two of the 37 declarations left in web/index.html after
   step 8 that are genuinely init-only -- see the STEP 9 commit message for the classification
   of all 37, done before cutting anything, same as step 8. Most of the rest (MVP_YEARS,
   SEASON_AWARDS, FINALS_BY_YEAR, OWNERS, the whole DERIVED section, CAT_KEYS/GRID_CLUBS, THEME,
   BOOT itself) are NOT boot machinery -- they're data, data-derivation, or things that would
   break evaluation order if moved (the GRID_CLUBS/BOOT failure shape from steps 7-8) -- and stay
   inline, explained in that commit message rather than silently swept in here.

   tests/_app_text.py's `_INSERTION_ORDER` gained one entry, placed directly before
   js/tabs.js's "SEG4_VIEWS_thru_applyHash" (this file's content sits between ARRANQUE and SEG4
   in the true original order, confirmed against app/bsn_archivo.html's own byte offsets) --
   SEG4's own anchor (the comment right before setInterval(checkRollover,60000)) is text that
   moved into THIS file, so js/init.js's group has to be spliced back in before SEG4's anchor
   search runs. Verified: app_text() still reconstructs app/bsn_archivo.html byte for byte.
   Replaced entirely once app/bsn_archivo.html becomes the archived pointer (step 11/12). */

/* ============================================================
   ARRANQUE

   The builders used to run in one synchronous loop, which meant the
   browser could not paint anything until all of them had finished.
   They now run in frame-sized batches so the splash bar can actually
   move; batching rather than yielding per builder keeps the wait
   about as short as it was, since yielding 49 times costs more in
   frames than it saves.
   ============================================================ */
function splashProgress(frac,label){
  const f=document.getElementById('splashFill');
  if(f) f.style.width=Math.round(frac*100)+'%';
  const s=document.getElementById('splashStep');
  if(s&&label) s.textContent=label;
}
function hideSplash(){
  const s=document.getElementById('splash');
  if(!s||s.classList.contains('gone')) return;
  s.classList.add('gone');
  /* Removed rather than left hidden: an aria-live region parked over
     the app keeps announcing itself to a screen reader. */
  setTimeout(()=>{ if(s.parentNode) s.parentNode.removeChild(s); },400);
}
/* Whatever happens above, the splash comes down. A load screen that
   can outlive its own failure is worse than no load screen. */
const SPLASH_DEADLINE=setTimeout(hideSplash,9000);

/* "La liga ahora" open state: every block open on desktop, only the first
   on a phone. Managed here — not in CSS — because a closed <details> hides
   its content differently across engines (Chrome's ::details-content is not
   overridable), which had left the desktop blocks unclickable. */
function ligaFold(){
  const wide = matchMedia('(min-width:860px)').matches;
  document.querySelectorAll('#inicio .liga').forEach((d,i)=>{ d.open = wide || i===0; });
}
if(window.matchMedia){
  const _lmq=matchMedia('(min-width:860px)');
  if(_lmq.addEventListener) _lmq.addEventListener('change',ligaFold);
  else if(_lmq.addListener) _lmq.addListener(ligaFold);
}

function finishBoot(){
  clearTimeout(SPLASH_DEADLINE);
  try{ buildShelf(); }catch(e){ console.error('BSN: falló el estante',e); }
  try{ buildViews(); }catch(e){ console.error('BSN: falló el enrutador de vistas',e); }
  try{ ligaFold(); }catch(e){ console.error('BSN: falló «La liga ahora»',e); }
  if(location.hash){
    try{ applyHash(); }catch(e){ console.error('BSN: falló el enlace directo',e); }
  }else{
    try{ showTab(prof().start,true); }
    catch(e){ console.error('BSN: falló la pantalla de entrada',e); }
  }
  splashProgress(1,'Listo');
  /* Real completion still gates dismissal (measured from navigation start
     via performance.now(), never a fixed fake delay) — this floor is a
     deliberate branding choice (give the splash room to register on a
     warm cache), not a load-time constraint. */
  const MIN_SPLASH_MS=3000, elapsed=(window.performance&&performance.now)?performance.now():MIN_SPLASH_MS;
  if(elapsed<MIN_SPLASH_MS) setTimeout(hideSplash,MIN_SPLASH_MS-elapsed);
  else hideSplash();
}

async function runBoot(){
  /* Pull the built data before the builders run. Raced against a
     timeout so a slow or dead network can't stall the boot — the
     splash covers the wait, and hydrate() no-ops on a local open. */
  await Promise.race([hydrate().catch(()=>{}), new Promise(r=>setTimeout(r,2500))]);
  let i=0;
  const total=BOOT.length;
  const raf=window.requestAnimationFrame||(fn=>setTimeout(fn,16));
  function step(){
    const t0=(window.performance&&performance.now)?performance.now():Date.now();
    const now=()=>((window.performance&&performance.now)?performance.now():Date.now());
    while(i<total && now()-t0<26){
      const name=BOOT[i][0], fn=BOOT[i][1];
      i++;
      try{ fn(); }
      catch(e){ console.error('BSN: falló el constructor «'+name+'»',e); }
    }
    splashProgress(i/total, i<total?BOOT[i-1][0]:'');
    if(i<total) raf(step); else finishBoot();
  }
  raf(step);
}


/* A tab left open past midnight was serving yesterday's board
   while the streak strip showed today's number. */
setInterval(checkRollover,60000);

/* Merge the built data over the baked-in blocks when web/data is
   reachable (deployed); a local-file open falls through untouched. Same
   rule as translate(): layer on top, never lose what the block already
   had. F names/colours/coaches stay baked in (curated, accented); only
   the pipeline facts — founded/status/end and the reconciled won/ru —
   come from the JSON. */
async function hydrate(){
  await DATA.syncVersion();
  const fr=await DATA.get('index/franchises.json');
  if(!fr) return;
  const yrs=a=>a.filter(t=>/^\d{4}$/.test(t)).map(Number);
  const uni=(a,b)=>[...new Set([...a,...b])].sort((x,y)=>x-y);
  for(const f of fr){
    const k=f.app_key; if(!F[k]) continue;
    F[k].founded=f.founded;
    F[k].active=f.status==='active'?1:0;
    F[k].end=f.end;
    /* union, not replace: the reconciled CSV omits the D5-disputed 1945
       (carried in F as Capitalinos + a caveat) and the D3 1942-43 split.
       Build-time check confirms 0 season CONFLICTS. */
    F[k].won=uni(F[k].won, yrs(f.titles));
    F[k].ru=uni(F[k].ru, yrs(f.finals_lost));
  }
  deriveChampions();
  ACTIVE.length=0; FKEYS.forEach(k=>{ if(F[k].active) ACTIVE.push(k); });

  /* SCORING: 26 rows (1966-1991) -> the reconciled 1948-2021 set. One row
     per year; the two D4-boundary years use the ppg champion, as the
     baked-in table does. Club: the F name when the franchise resolved,
     else club_raw, else whatever the baked-in row had for that year (so
     an older scoring_titles.json without club fields keeps the 1966-91
     names instead of blanking the column). */
  const st=await DATA.get('index/scoring_titles.json');
  if(st){
    const fk={}; fr.forEach(f=>fk[f.franchise_id]=f.app_key);
    const baked={}; SCORING.forEach(s=>{ baked[s[0]]=s[2]; });
    const club=(c,yr)=>{
      const k=c.franchise_id&&fk[c.franchise_id];
      return (k&&F[k]&&F[k].name) || c.club_raw || baked[yr] || '—';
    };
    const rows=[];
    for(const s of st){
      const c=s.dual?s.dual.ppg:s.champion; if(!c) continue;
      const metric=s.metric_era==='ppg'?'ppg':'total';
      const val=metric==='ppg'?(c.value!=null?c.value:c.ppg):c.total_points;
      if(val!=null) rows.push([s.season,c.player,club(c,s.season),metric,val,c.bsnpr_id!=null?c.bsnpr_id:null]);
    }
    rows.sort((a,b)=>a[0]-b[0]);
    SCORING.length=0; rows.forEach(r=>SCORING.push(r));
  }

  /* 5D.3b — player career detail. FID2APP lets a career row link to its team;
     PXWALK maps the curated index name to a bsnpr_id. */
  FID2APP={}; fr.forEach(f=>{ if(f.franchise_id) FID2APP[f.franchise_id]=f.app_key; });
  const xw=await DATA.get('index/player_xwalk.json');
  if(xw){ PXWALK=xw; XWALK_REV={}; for(const k in xw) XWALK_REV[xw[k]]=k; }

  /* 5D.3c — the whole 3.303-row archive index, for "Todo el archivo" search. */
  const pr=await DATA.get('index/player_redirects.json');
  if(pr) PREDIR=pr;
  const pa=await DATA.get('index/players.json');
  if(pa){ PALL=pa; buildPlayerSlugs(); if(typeof refreshPlayerIndexArchive==='function') refreshPlayerIndexArchive();
    if(typeof refreshCompareCandidates==='function') refreshCompareCandidates(); }

  /* 5D.2b — fill MVP_YEARS gaps (1959-2003) from historic_awards. Union: a
     baked year is never overwritten (it carries the accented name); a genuine
     name disagreement is kept as a footnote via MVP_ALSO. */
  const mvp=await DATA.get('index/mvp.json');
  if(mvp){
    MVP_ID={}; MVP_ALSO={};
    const have=new Set(MVP_YEARS.map(r=>r[0]));
    mvp.forEach(m=>{
      if(m.bsnpr_id!=null) MVP_ID[m.season]=m.bsnpr_id;
      if(m.also && have.has(m.season)) MVP_ALSO[m.season]=m.also;
      if(!have.has(m.season)){
        const ak=m.franchise_id&&FID2APP[m.franchise_id];
        MVP_YEARS.push([m.season, m.player, (ak&&F[ak]&&F[ak].name) || m.team_raw || '—']);
      }
    });
    MVP_YEARS.sort((a,b)=>a[0]-b[0]);
  }

  /* 5D.4 — deployed-reality copy for the "lo que falta" / coverage sections. */
  const mf=await DATA.get('manifest.json');
  if(mf) ASSETS=mf.assets||{};   /* 5G-A — {} = probe nothing (no 404s) */
  if(mf && mf.counts){
    MANIFEST=mf; DATA_TEXT=true;
    const cov=[
      ['1930s',20,'Campeones sí. Nada más.'],
      ['1940s',25,'Campeones y una disputa sin resolver en 1945.'],
      ['1950s',30,'Campeones, y MVP desde 1958.'],
      ['1960s',45,'Campeones, MVP y campeones de anotación.'],
      ['1970s',50,'Campeones, MVP, anotación, algunos récords.'],
      ['1980s',55,'Igual, más MVP completo y líderes de carrera acumulados.'],
      ['1990s',50,'Campeones, MVP y anotación completos; sin estadísticas por partido.'],
      ['2000s',70,'MVP hasta 2004, anotación, y boxscores + posiciones de 2001–2003 y 2008–2009.'],
      ['2010s',75,'Boxscores y posiciones 2010–2013; premios y líderes de 2016–2018; MVP disperso.'],
      ['2020s',90,'Posiciones, finales juego a juego, premios completos, líderes, dueños.']
    ];
    COVERAGE.length=0; cov.forEach(r=>COVERAGE.push(r));
  }
}
