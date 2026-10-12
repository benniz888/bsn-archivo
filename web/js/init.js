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
/* PHASE_64: every Inicio .liga starts closed (the whole group now sits inside the collapsed
   "Más de la liga ahora" disclosure); done once, so a width change never re-closes what a
   visitor opened. */
function ligaFold(){
  if(ligaFold.done) return; ligaFold.done=true;
  document.querySelectorAll('#inicio .liga').forEach(d=>{ d.open=false; });
}
if(window.matchMedia){
  const _lmq=matchMedia('(min-width:860px)');
  if(_lmq.addEventListener) _lmq.addEventListener('change',ligaFold);
  else if(_lmq.addListener) _lmq.addListener(ligaFold);
}

/* PHASE_9 search-placeholder fix (owner-approved, redesign-v2): the full example
   (the old, longer example) clips mid-word at
   phone width (measured live: 390px, 19px font -- the string needs ~492px, the
   input only has ~312px to give it there). An <input>'s placeholder attribute is
   a plain string, not markup -- it can't hold a <span> the way hero-headline-full
   does, and no CSS mechanism changes placeholder TEXT CONTENT (only its color/
   font/etc via ::placeholder) -- so the text itself is swapped here, in JS, same
   matchMedia + addEventListener('change', ...) pattern as ligaFold() just above.
   Below 640px: the same example's own first clause, unchanged, verified live to
   fit with real margin at both 360px and 390px. aria-label (index.html) is
   static and always carries the complete example -- this only ever changes
   what's VISUALLY shown before someone starts typing. */
function syncSearchPlaceholder(){
  const el=document.getElementById('hubSearch'); if(!el) return;
  el.placeholder = matchMedia('(max-width:639px)').matches
    ? 'Prueba: títulos de Bayamón'
    : 'Prueba: títulos de Bayamón · 1971';
}
if(window.matchMedia){
  const _spq=matchMedia('(max-width:639px)');
  if(_spq.addEventListener) _spq.addEventListener('change',syncSearchPlaceholder);
  else if(_spq.addListener) _spq.addListener(syncSearchPlaceholder);
}

/* PHASE_61: subnav edge fades. Capture-phase listener because 'scroll' doesn't bubble; syncSubnav()
   dispatches a synthetic scroll so the fades are right on first show, not only after a swipe. */
(function(){
  const edge=n=>{
    n.classList.toggle('fade-l',n.scrollLeft>2);
    n.classList.toggle('fade-r',n.scrollLeft+n.clientWidth<n.scrollWidth-2);
  };
  document.addEventListener('scroll',e=>{
    if(e.target&&e.target.classList&&e.target.classList.contains('subnav')) edge(e.target);
  },true);
  window.addEventListener('resize',()=>document.querySelectorAll('.subnav').forEach(edge));
})();

/* PHASE_61: below 860px the header search is an icon that expands over the header row. An IIFE,
   not a named function -- the top-level declaration inventory is frozen (tests/harness). Desktop
   never sees .searching (the CSS only honours it on phones). */
(function(){
  const hdr=document.querySelector('header.top'), btn=document.getElementById('hdrSearchBtn'),
        inp=document.getElementById('hubSearch');
  if(!hdr||!btn||!inp) return;
  const set=open=>{
    hdr.classList.toggle('searching',open);
    btn.setAttribute('aria-expanded',open?'true':'false');
    btn.setAttribute('aria-label',open?'Cerrar búsqueda':'Buscar en el archivo');
    if(open) inp.focus();
  };
  btn.addEventListener('click',()=>set(!hdr.classList.contains('searching')));
  inp.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&hdr.classList.contains('searching')){ set(false); btn.focus(); }
    else if(e.key==='Enter'&&inp.value.trim()) hdr.classList.remove('searching'), btn.setAttribute('aria-expanded','false'), btn.setAttribute('aria-label','Buscar en el archivo');
  });
})();

function finishBoot(){
  clearTimeout(SPLASH_DEADLINE);
  try{ buildShelf(); }catch(e){ console.error('BSN: falló el estante',e); }
  try{ buildViews(); }catch(e){ console.error('BSN: falló el enrutador de vistas',e); }
  /* PHASE_11 (owner-approved, redesign-v2): Historia's own hero rewrite -- must run after
     buildViews() so #historia .phead already exists as buildViews() left it (it only reads
     phead as an insertion anchor, never touches its content, so ordering relative to
     buildViews() itself doesn't matter -- placed here just to sit with the rest of the
     router-level, once-per-boot setup). */
  try{ buildHistoriaHero(); }catch(e){ console.error('BSN: falló el hero de Historia',e); }
  try{ buildJugadoresHero(); }catch(e){ console.error('BSN: falló el hero de Jugadores',e); }
  try{ buildEquiposHero(); }catch(e){ console.error('BSN: falló el hero de Equipos',e); }
  try{ buildJuegaHero(); }catch(e){ console.error('BSN: falló el hero de Juega',e); }
  try{ buildArchivoHero(); }catch(e){ console.error('BSN: falló el hero de Archivo',e); }
  try{ restructurePremios(); }catch(e){ console.error('BSN: falló el subtab de Premios',e); }
  /* PHASE_12 (owner-approved, redesign-v2): skins the real "La liga ahora" accordions
     (item 6) -- run before ligaFold() so the real .liga elements' summary content is
     already in its final form by the time ligaFold() reads/sets their .open state (order
     doesn't actually matter to ligaFold() itself, which never inspects summary content,
     but this keeps the "build markup, then apply fold state" sequence in a sensible order). */
  try{ buildLigaAccordionSkin(); }catch(e){ console.error('BSN: falló el look de "La liga ahora"',e); }
  try{ ligaFold(); }catch(e){ console.error('BSN: falló «La liga ahora»',e); }
  try{ syncSearchPlaceholder(); }catch(e){ console.error('BSN: falló el placeholder de búsqueda',e); }
  /* PHASE_63 B4 (redesign-v3): every filter <select> and search box inside .filters becomes a
     styled combobox / gets a clear button. Closures only (an IIFE inside this existing
     function: no new top-level names). The native <select> stays in the DOM as the source of
     truth -- same id, same onchange handlers, hidden from assistive tech -- so no builder
     changes and the page still works if this block throws. A MutationObserver re-applies it
     to filters that builders draw later or redraw. */
  try{ (()=>{
    let seq=0, openClose=null, openRoot=null;
    const mk=(t,c)=>{ const e=document.createElement(t); if(c) e.className=c; return e; };
    const enhanceSelect=sel=>{
      sel.dataset.cbx='1';
      const n=++seq, bid='cbx'+n, lid='cbxl'+n;
      const lab=sel.id&&sel.closest('.field').querySelector('label[for="'+sel.id+'"]');
      const root=mk('div','cbx'), btn=mk('button','cbx-btn'), txt=mk('span','cbx-val'), chev=mk('span','cbx-chev'), list=mk('ul','cbx-list');
      btn.type='button'; btn.id=bid; btn.setAttribute('role','combobox');
      btn.setAttribute('aria-haspopup','listbox'); btn.setAttribute('aria-expanded','false'); btn.setAttribute('aria-controls',lid);
      if(lab){ lab.htmlFor=bid; if(!lab.id) lab.id='cbxlab'+n; btn.setAttribute('aria-labelledby',lab.id); }
      else btn.setAttribute('aria-label',sel.getAttribute('aria-label')||'Filtro');
      chev.setAttribute('aria-hidden','true');
      list.id=lid; list.setAttribute('role','listbox'); list.hidden=true;
      if(lab) list.setAttribute('aria-labelledby',lab.id);
      btn.appendChild(txt); btn.appendChild(chev);
      sel.parentNode.insertBefore(root,sel);
      root.appendChild(btn); root.appendChild(list); root.appendChild(sel);
      sel.classList.add('cbx-native'); sel.tabIndex=-1; sel.setAttribute('aria-hidden','true');
      let active=-1, buf='', bt=0;
      const opts=()=>Array.from(sel.options);
      const sync=()=>{ const o=sel.options[sel.selectedIndex]; txt.textContent=o?o.text:''; btn.disabled=sel.disabled; };
      const paint=()=>{
        list.innerHTML='';
        opts().forEach((o,i)=>{
          const li=mk('li','cbx-opt'); li.id=lid+'o'+i; li.setAttribute('role','option'); li.dataset.i=i; li.textContent=o.text;
          li.setAttribute('aria-selected',String(i===sel.selectedIndex));
          if(o.disabled) li.setAttribute('aria-disabled','true');
          list.appendChild(li);
        });
      };
      const setActive=i=>{
        const L=list.children; if(!L.length) return;
        active=Math.max(0,Math.min(L.length-1,i));
        Array.from(L).forEach((li,j)=>li.classList.toggle('on',j===active));
        btn.setAttribute('aria-activedescendant',L[active].id);
        L[active].scrollIntoView({block:'nearest'});
      };
      const close=()=>{
        if(list.hidden) return;
        list.hidden=true; btn.setAttribute('aria-expanded','false'); btn.removeAttribute('aria-activedescendant');
        root.classList.remove('up'); if(openRoot===root){ openRoot=null; openClose=null; }
      };
      const open=()=>{
        if(!list.hidden||sel.disabled) return;
        if(openClose) openClose();
        sync(); paint(); list.hidden=false; btn.setAttribute('aria-expanded','true');
        root.classList.toggle('up',btn.getBoundingClientRect().bottom+300>innerHeight&&btn.getBoundingClientRect().top>300);
        openRoot=root; openClose=close; setActive(sel.selectedIndex<0?0:sel.selectedIndex);
      };
      const choose=i=>{
        const o=sel.options[i]; if(!o||o.disabled) return;
        const changed=sel.selectedIndex!==i;
        sel.selectedIndex=i; close(); sync(); btn.focus();
        if(changed) sel.dispatchEvent(new Event('change',{bubbles:true}));
      };
      const typeahead=k=>{
        clearTimeout(bt); buf+=k; bt=setTimeout(()=>{buf='';},600);
        const o=opts(), key=norm(buf), from=buf.length===1?active+1:active;
        for(let d=0;d<o.length;d++){ const i=(from+d+o.length)%o.length; if(!o[i].disabled&&norm(o[i].text).startsWith(key)){ if(list.hidden) open(); setActive(i); return; } }
      };
      btn.addEventListener('click',()=>{ list.hidden?open():close(); });
      btn.addEventListener('keydown',e=>{
        const k=e.key, isOpen=!list.hidden;
        if(k==='ArrowDown'||k==='ArrowUp'){ e.preventDefault(); if(!isOpen) open(); else setActive(active+(k==='ArrowDown'?1:-1)); }
        else if(k==='Home'||k==='End'){ if(isOpen){ e.preventDefault(); setActive(k==='Home'?0:1e9); } }
        else if(k==='PageDown'||k==='PageUp'){ if(isOpen){ e.preventDefault(); setActive(active+(k==='PageDown'?10:-10)); } }
        else if(k==='Enter'||k===' '){ e.preventDefault(); if(isOpen) choose(active); else open(); }
        else if(k==='Escape'){ if(isOpen){ e.preventDefault(); close(); } }
        else if(k==='Tab'){ close(); }
        else if(k.length===1&&!e.ctrlKey&&!e.metaKey&&!e.altKey){ e.preventDefault(); typeahead(k); }
      });
      list.addEventListener('mousedown',e=>e.preventDefault());
      list.addEventListener('click',e=>{ const li=e.target.closest('.cbx-opt'); if(li) choose(+li.dataset.i); });
      root.addEventListener('focusout',e=>{ if(!root.contains(e.relatedTarget)) close(); });
      btn.addEventListener('focus',sync);
      sel.addEventListener('change',sync);
      new MutationObserver(sync).observe(sel,{childList:true,subtree:true,attributes:true});
      sync();
    };
    const enhanceSearch=inp=>{
      inp.dataset.clr='1';
      const wrap=mk('div','sbx'), b=mk('button','sbx-clr');
      b.type='button'; b.hidden=true; b.setAttribute('aria-label','Limpiar búsqueda');
      b.innerHTML='<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
      inp.parentNode.insertBefore(wrap,inp); wrap.appendChild(inp); wrap.appendChild(b);
      const sync=()=>{ b.hidden=!inp.value; };
      inp.addEventListener('input',sync); inp.addEventListener('focus',sync);
      b.addEventListener('click',()=>{ inp.value=''; sync(); inp.dispatchEvent(new Event('input',{bubbles:true})); inp.focus(); });
      sync();
    };
    const scan=()=>{
      document.querySelectorAll('.filters .field select:not([data-cbx])').forEach(enhanceSelect);
      document.querySelectorAll('.filters .field input[type=search]:not([list]):not([data-clr])').forEach(enhanceSearch);
    };
    let queued=false;
    new MutationObserver(()=>{ if(queued) return; queued=true; requestAnimationFrame(()=>{ queued=false; scan(); }); })
      .observe(document.body,{childList:true,subtree:true});
    document.addEventListener('pointerdown',e=>{ if(openRoot&&!openRoot.contains(e.target)) openClose(); });
    scan();
  })(); }catch(e){ console.error('BSN: fallaron los filtros',e); }
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
  }
}
