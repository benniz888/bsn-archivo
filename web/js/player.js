/* PHASE_1_SPLIT STEP 5. The archive player page, moved out of web/index.html's inline
   <script>, byte for byte -- no renaming, no reformatting, no reordering among themselves.
   Loaded via <script src="js/player.js"> right after js/helpers.js, before the rest.

   Two blocks. The first is the whole "JUGADORES" index-building and archive-card run, minus
   the shared state it reads/writes (PINDEX, PXWALK, PALL, PSLUG, MVP_ID, MANIFEST, etc. stay in
   web/index.html -- loadPlayerExtra, buildMVPYears, hydrate() and others all read or write them
   too, so they aren't "only" the archive player page's): buildPlayerIndex,
   refreshPlayerIndexArchive, buildPlayerSlugs, survivorOf, playerSlug, sameNameLine (the "Mismo
   nombre" cross-link line), renderPlayerIndex (the Jugadores-index row builder), ARCH_CAP +
   renderArchiveIndex, openArchivePlayer, renderArchiveCard. Stops right before showPlayer --
   the full curated player card is a bigger, separate thing, not named for this step.

   The second is the disputed-row tag/tooltip helpers -- dqFlag, dqTag, disputeFlag, disputeTag
   -- pure formatting functions called only from loadPlayerExtra's career-row table (both a
   curated and an archive-only player go through it). ensureDQ() and the DQ_IDX/DISPUTE_IDX
   state they read stay behind: openDQ() (the Archivo/calidad tab) needs them too, so they're
   not player-page-exclusive either -- a later "data-quality" step's territory.

   tests/_app_text.py knows how to splice this file, js/data.js, js/helpers.js and
   web/index.html back into the exact original byte stream. Replaced entirely once
   app/bsn_archivo.html becomes the archived pointer (step 11/12 of the split). */

function buildPlayerIndex(){
  if(!PINDEX){
    const map=new Map();
    const get=n=>{
      const key=norm(n);
      if(!map.has(key)) map.set(key,{name:n,src:new Set(),tags:new Set(),clubs:new Set(),
        pts:null,reb:null,ast:null,gp:null,ppg:null,years:null,pos:null,bio:null,mvp:0});
      return map.get(key);
    };
    /* SCORING / MVP_YEARS / SEASON_AWARDS hold raw source names (and grow when
       hydrate() swaps in the full tables). Only enrich a player already curated
       from POOL/LEADERS/HOF — a bare scoring-champ name belongs in "Todo el
       archivo", not "Destacados". Keeps the count stable across file:// / http. */
    const getIf=n=>map.get(norm(n));
    ['points','rebounds','assists'].forEach(cat=>{
      LEADERS[cat].forEach(r=>{
        const p=get(r[1]); p.src.add('Líderes de carrera'); p.pos=p.pos||r[2]; p.years=p.years||r[3];
        p.gp=p.gp||r[5];
        if(cat==='points'){p.pts=r[4];p.ppg=p.ppg||r[6];}
        /* The leaders table carries a per-game column. Without this the
           only comparable rows between two pre-2012 players were points
           and games, and the comparison read as mostly holes. */
        if(cat==='rebounds'){p.reb=r[4];p.rpg=p.rpg||r[6];}
        if(cat==='assists'){p.ast=r[4];p.apg=p.apg||r[6];}
        p.tags.add('Líder de carrera');
      });
    });
    HOF.forEach(h=>{
      const p=get(h.n); p.src.add('Salón'); p.pos=p.pos||h.pos; p.years=p.years||h.yrs;
      p.bio=p.bio||h.role; p.mvp=Math.max(p.mvp,h.mvp||0);
      if(h.pts)p.pts=p.pts||h.pts; if(h.gp)p.gp=p.gp||h.gp; if(h.ppg)p.ppg=p.ppg||h.ppg;
      (h.hon||[]).forEach(x=>p.tags.add(x));
    });
    SCORING.forEach(s=>{
      const p=getIf(s[1]); if(!p) return;
      p.src.add('Campeones de anotación'); p.tags.add('Campeón de anotación '+s[0]);
      const fk=FKEYS.find(k=>F[k].name===s[2]); if(fk)p.clubs.add(fk);
    });
    POOL.forEach(q=>{
      const p=get(q.n); p.src.add('Grupo de juego'); p.pos=p.pos||q.pos; p.bio=p.bio||q.b;
      q.c.forEach(c=>p.clubs.add(c));
      q.t.forEach(t=>p.tags.add({mvp:'MVP',scoring:'Campeón de anotación',champion:'Campeón',
        import:'Refuerzo',native:'Nativo',nba:'NBA','10k':'10.000+ puntos',legend:'Leyenda',figura:'Figura del BSN'}[t]||t));
      if(q.ppg!=null)p.ppg=p.ppg||q.ppg;
      if(q.legendWhy) p.legendWhy=q.legendWhy;
      /* The season corpus brought categories the index never had a
         column for. Carried through here so Comparar has real rows
         instead of five dashes for every modern player. */
      ['rpg','apg','spg','bpg','mpg','fg','tp','ft','ns','hi'].forEach(k=>{ if(p[k]==null && q[k]!=null) p[k]=q[k]; });
      if(p.gp==null && q.gp!=null) p.gp=q.gp;
      if(q.posSrc) p.posSrc=q.posSrc;
      p.decades=q.d;
    });
    MVP_REPEAT.forEach(m=>{const p=get(m[0]);p.mvp=Math.max(p.mvp,m[1]);p.tags.add(m[1]+'× MVP');});
    /* These three were previously not indexed at all, which is why
       searching a name like Carlos Arroyo returned nothing. */
    NBA_PLAYERS.forEach(r=>{const p=get(r[0]);p.src.add('BSN a la NBA');p.tags.add('NBA');p.bio=p.bio||r[1];});
    MVP_YEARS.forEach(r=>{
      const p=getIf(r[1]); if(!p) return;
      p.src.add('MVP por año'); p.tags.add('MVP '+r[0]);
      const fk=FKEYS.find(k=>F[k].name===r[2]); if(fk)p.clubs.add(fk);
    });
    SEASON_AWARDS.forEach(r=>{
      const p=getIf(r[2]); if(!p) return;
      p.src.add('Premios por temporada'); p.tags.add(r[1]+' '+r[0]);
      const fk=FKEYS.find(k=>F[k].name===r[3]); if(fk)p.clubs.add(fk);
      if(r[4]&&!p.bio) p.bio=r[4];
    });
    PINDEX=Array.from(map.values()).sort((a,b)=>a.name.localeCompare(b.name,'es'));
  }
  const host=$('#playerSearch');
  if(!host.dataset.built){
    host.dataset.built='1';
    host.innerHTML=`<div class="filters">
      <div class="field" style="min-width:220px"><label for="pq">Buscar jugador</label>
        <input type="search" id="pq" placeholder="Nombre, club, honor…"></div>
      <div class="field"><label for="pmode">Índice</label><select id="pmode">
        <option value="top">Destacados (${PINDEX.length})</option>
        <option value="all">Todo el archivo${PALL?' ('+PALL.length.toLocaleString('es-PR')+')':''}</option>
      </select></div>
      <div class="field" id="pfField"><label for="pf">Filtro</label><select id="pf">
        <option value="">Todos (${PINDEX.length})</option>
        <option value="MVP">MVP</option><option value="Campeón de anotación">Campeones de anotación</option>
        <option value="10.000">10.000+ puntos</option><option value="NBA">Pasaron por la NBA</option>
        <option value="Refuerzo">Refuerzos</option><option value="Nativo">Nativos</option>
      </select></div></div>`;
    $('#pq').oninput=renderPlayerIndex;
    $('#pf').onchange=renderPlayerIndex;
    $('#pmode').onchange=e=>{ PMODE=e.target.value; renderPlayerIndex(); };
  }
  renderPlayerIndex();
}
/* Called from hydrate() once index/players.json lands, in case the tab was
   already open. Refreshes the "Todo el archivo (N)" label + the list. */
function refreshPlayerIndexArchive(){
  const sel=$('#pmode');
  if(sel && PALL){
    const o=sel.querySelector('option[value="all"]');
    if(o) o.textContent='Todo el archivo ('+PALL.length.toLocaleString('es-PR')+')';
  }
  if($('#playerSearch').dataset.built) renderPlayerIndex();
}
/* Players sharing slug(name) (57 slugs, 118 players): the richest keeps the plain slug
   (career_seasons, then a birth year, then the lowest id); every other one is <slug>-<id>.
   Curated-pool slugs are unchanged and the router still tries them first. */
function buildPlayerSlugs(){
  if(!PALL) return;
  PBYID=new Map(PALL.map(p=>[p.id,p]));
  const by=new Map();
  PALL.forEach(p=>{ const s=slug(p.name); if(!by.has(s)) by.set(s,[]); by.get(s).push(p); });
  const rank=(a,b)=>(b.career_seasons||0)-(a.career_seasons||0)||(b.birth_year?1:0)-(a.birth_year?1:0)||a.id-b.id;
  PSLUG=new Map(); USLUG=new Map(); PTWINS=new Map();
  const rest=[];
  by.forEach((list,s)=>{
    const best=list.length>1?list.slice().sort(rank)[0]:list[0];
    PSLUG.set(s,best); USLUG.set(best.id,s);
    list.forEach(p=>{ if(p!==best) rest.push([s,p]); });
    if(list.length>1) list.forEach(p=>PTWINS.set(p.id,list.filter(q=>q!==p)));
  });
  rest.forEach(([s,p])=>{ let u=s+'-'+p.id; while(PSLUG.has(u)) u+='-'+p.id; PSLUG.set(u,p); USLUG.set(p.id,u); });
}
/* A retired player id (merged into a survivor) resolves to the survivor, and its name follows. */
function survivorOf(id,name){
  const to=PREDIR&&id!=null?PREDIR.ids[id]:null;
  if(to==null) return [id,name];
  const q=PBYID&&PBYID.get(to);
  return [to,q?q.name:name];
}
/* The hash for a player card: curated (pool) names keep slug(name); an archive player gets
   its unique slug. Needs PINDEX built, so showPlayer() calls buildPlayerIndex() first. */
function playerSlug(name,id){
  const pooled=PINDEX&&PINDEX.some(x=>norm(x.name)===norm(name));
  return (!pooled && id!=null && USLUG && USLUG.has(id)) ? USLUG.get(id) : slug(name);
}
/* "Mismo nombre" line: the other archive players with this exact name, as slug-id links. */
function sameNameLine(id){
  const tw=PTWINS&&PTWINS.get(id); if(!tw||!tw.length) return '';
  const yrs=q=>q.first_season?(q.first_season===q.last_season?''+q.first_season:q.first_season+'–'+q.last_season):'sin años';
  return `<div class="note">Mismo nombre en el archivo: ${tw.map(q=>`<a href="#jugadores/jugador/${USLUG.get(q.id)}">${esc(q.name)} (${yrs(q)} · #${q.id})</a>`).join(' · ')}</div>`;
}
function renderPlayerIndex(){
  const q=norm($('#pq')?$('#pq').value:''), f=$('#pf')?$('#pf').value:'';
  /* inline display, not [hidden] — .field{display:flex} in the stylesheet
     outranks the UA [hidden] rule, so the attribute alone leaves it visible. */
  const pf=$('#pfField'); if(pf) pf.style.display = (PMODE==='all') ? 'none' : '';
  if(PMODE==='all'){ renderArchiveIndex(q); return; }
  const list=PINDEX.filter(p=>{
    const tags=Array.from(p.tags).join(' ');
    if(f && !tags.includes(f)) return false;
    if(!q) return true;
    const clubs=Array.from(p.clubs).map(c=>F[c].name).join(' ');
    return norm(p.name+' '+tags+' '+clubs+' '+(p.bio||'')).includes(q);
  });
  const rows=list.map(p=>[
    p.name, p.pos, p.years, Array.from(p.clubs).map(c=>F[c].abbr).join(' '), p.pts, p.reb, p.ast, p.gp,
    Array.from(p.src).length
  ]);
  buildTable($('#playerIndex'),[
    {label:'Jugador',wide:true,render:v=>`<button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="showPlayer(${JSON.stringify(v).replace(/"/g,'&quot;')})">${esc(v)}</button>`},
    {label:'Pos'},{label:'Años'},{label:'Clubes'},
    {label:'Pts',num:true},{label:'Reb',num:true},{label:'Ast',num:true},{label:'PJ',num:true},
    {label:'Fuentes',num:true}
  ],rows,{file:'jugadores_bsn',sort:4,dir:-1});
}
/* 5D.3c — "Todo el archivo" mode: search index/players.json (all 3.303), not
   the 385 curated. Token-AND over norm(name) so "george torres" finds
   "Torres Dougherty, George". Display cap keeps the DOM bounded. */
const ARCH_CAP=500;
function renderArchiveIndex(q){
  const host=$('#playerIndex');
  if(!PALL){
    /* file:// (no data/ to reach) vs. hydrate still in flight over http. */
    host.innerHTML = DATA.base===null
      ? '<p class="note">El índice completo (3.303 jugadores) solo está disponible en la versión publicada, con conexión. Esta copia local trae los '+(PINDEX?PINDEX.length:385)+' jugadores destacados.</p>'
      : '<p class="note">Cargando el índice completo del archivo…</p>';
    return;
  }
  const toks=q.split(/\s+/).filter(Boolean);
  const list=PALL.filter(p=>{ const n=p.norm||norm(p.name); return toks.every(t=>n.includes(t)); });
  const shown=list.slice(0,ARCH_CAP);
  const span=p=>(p.first_season&&p.last_season)
    ? (p.first_season===p.last_season?''+p.first_season:p.first_season+'–'+p.last_season) : '';
  const rows=shown.map(p=>[p.name, p.position||'', span(p), p.n_seasons, p.id]);
  buildTable(host,[
    {label:'Jugador',wide:true,render:(v,r)=>`<button class="btn" style="padding:2px var(--sp-2);font-size:var(--fs-2xs)" onclick="openArchivePlayer(${r[4]},${JSON.stringify(v).replace(/"/g,'&quot;')})">${esc(v)}</button>`},
    {label:'Pos'},{label:'Años'},{label:'Temp.',num:true}
  ],rows,{file:'archivo_bsn',sort:0,dir:1,
    note:list.length>ARCH_CAP?`Mostrando ${ARCH_CAP} de ${list.length.toLocaleString('es-PR')} — afiná la búsqueda.`:''});
}
function openArchivePlayer(id,name,season){
  [id,name]=survivorOf(id,name);
  if(XWALK_REV && XWALK_REV[id]!=null){ showPlayer(XWALK_REV[id],null,season); return; }  /* is a curated player -> rich card */
  showPlayer(name,id,season);
}
function renderArchiveCard(name,id,host){
  const r=(PALL||[]).find(x=>x.id===id)||{};
  const span=(r.first_season&&r.last_season)
    ? (r.first_season===r.last_season?''+r.first_season:r.first_season+'–'+r.last_season) : '';
  const meta=[r.position,span,(r.nationality&&r.nationality!=='Puerto Rico')?r.nationality:''].filter(Boolean).join(' · ');
  host.innerHTML=`<div class="card" style="margin-top:var(--sp-4_5)">
    <div style="display:flex;gap:16px;flex-wrap:wrap">
      ${portrait(name,'var(--azul)','var(--blanco)',60,74,r.position)}
      <div style="flex:1;min-width:230px">
        <h2 style="font-size:24px">${esc(name)}</h2>
        <div class="muted" style="font-size:var(--fs-xs)">${esc(meta||'sin datos de posición o años')}</div>
      </div>
    </div>
    <div class="note">Del índice del archivo — no es uno de los jugadores destacados con ficha curada. Lo que sigue es solo lo que registra el archivo de bsnpr.com.</div>
  </div>`;
  revealNode(host); host.scrollIntoView({block:'start',behavior:'smooth'});
}
/* the conflict a career row belongs to (either of its two rows), or null */
function dqFlag(id,row){
  const l=DQ_IDX&&DQ_IDX.get(Number(id)+'|'+row.season+'|'+row.franchise_id); if(!l) return null;
  const same=s=>row.games===s.games&&row.points===s.points&&row.team_raw===s.team;
  return l.find(c=>same(c.a)||same(c.b))||null;
}
function dqTag(c){
  const f=v=>v==null?'—':v;
  const tip='Dos páginas de bsnpr.com dan cifras distintas para este equipo y temporada: '
    +`ficha del jugador ${f(c.a.games)} JJ, ${f(c.a.points)} PTS · página jug05 ${f(c.b.games)} JJ, ${f(c.b.points)} PTS. `
    +'El archivo no escoge una: las dos filas quedan fuera de los totales.';
  return `<a class="tag" href="#archivo/calidad" title="${esc(tip)}">2 fuentes</a>`;
}
/* the disputed-row entry a career row belongs to (id+season+team+games+points), or null (J16 A05) */
function disputeFlag(id,row){
  const l=DISPUTE_IDX&&DISPUTE_IDX.get(Number(id)+'|'+row.season+'|'+row.team_raw); if(!l) return null;
  return l.find(r=>r.games===row.games&&r.points===row.points)||null;
}
function disputeTag(){
  const tip='La fecha de nacimiento en la ficha de este jugador (bsnpr.com) no es compatible con esta temporada. '
    +'No sabemos cuál de los dos datos es el correcto. La fila se conserva, pero no cuenta en los totales de abajo.';
  return `<a class="tag" href="#archivo/calidad" title="${esc(tip)}">No concuerda con la ficha</a>`;
}
