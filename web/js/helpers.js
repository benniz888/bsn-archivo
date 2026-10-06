/* PHASE_1_SPLIT STEP 4. Shared helpers moved out of web/index.html's inline <script>, byte
   for byte -- no renaming, no reformatting, no reordering among themselves. Loaded via
   <script src="js/helpers.js"> right after js/data.js, before the rest (still inline for now).

   Seven blocks, none contiguous in the original (same situation as js/data.js in STEP 3): DOM/
   string micro-helpers ($, el, esc, slug, norm, num, dash, pct -- the file's own "HELPERS"
   section), the two routing functions that don't belong to a specific tab's UI-building code
   (showTab, plus setHash+showView together a few lines later -- the rest of the NAVIGATION
   section, like buildNav and the mega-menu, is tab-specific UI, not a shared helper, and stayed
   behind), the storage/fetch layer (MEM+ST+DATA, the file's own "STORAGE" section plus DATA's
   own adjacent header), the DOB formatter -- fmtLongDate on its own, THEN separately
   _daysInMonth+fmtArchiveDob (their shared comment) -- split into two groups here because
   MESES/DIAS (step 3, now in js/data.js) originally sat between them; merging them would have
   been wrong the moment MESES/DIAS moved out from between, not just cosmetically -- and the
   puzzle PRNG (mulberry32, EPOCH, todayStamp, puzzleNo, seededShuffle, pick -- the file's own
   "SEEDING" section). tests/_app_text.py knows how to splice this file, js/data.js and
   web/index.html back into the exact original byte stream, in original document order (a few
   anchors point into ANOTHER split file's content, not web/index.html, exactly because of the
   fmtLongDate/MESES/DIAS/_daysInMonth situation above -- see its module docstring). Replaced
   entirely once app/bsn_archivo.html becomes the archived pointer (step 11/12 of the split). */

/* ============================================================
   HELPERS
   ============================================================ */
const $=s=>document.querySelector(s);
const el=(t,c)=>{const n=document.createElement(t);if(c)n.className=c;return n};
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const slug=s=>String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')
  .replace(/[«»"'.]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const norm=s=>String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')
  .replace(/[«»"'.]/g,'').trim();
/* PHASE_36 (owner-approved, redesign-v2): norm()/slug() strip the «»""''
   PUNCTUATION a quoted nickname sits in, never the nickname WORD itself --
   "Mario «Quijote» Morales" and "Mario Morales" normalize to two different
   strings (confirmed PHASE_35 survey: exactly 2 real PINDEX pairs affected,
   Mario Morales and Federico "Fico" López, both the SAME real archive
   person split into two curated cards by this gap). stripNick() drops the
   whole quoted segment, guillemets or straight quotes, before norm()'s own
   fold runs; nickKey() is the merge key built on top of it. Used ONLY as
   buildPlayerIndex()'s own Map key (player.js) -- norm()/slug() themselves,
   and every other one of their ~50 call sites (search/filter matching, URL
   slugs, PXWALK lookups, ARIA labels), are completely unchanged. A few
   lookups that search or route BY NAME still need to find a now-merged
   entry under its old plain-name form too -- those call stripNick()/
   nickKey() directly at their own call site (player.js's renderPlayerIndex
   search filter, tabs.js's cmpFind() and the #jugadores/jugador/<slug>
   route) rather than this function growing hidden side effects. */
const stripNick=s=>String(s).replace(/«[^»]*»|"[^"]*"|'[^']*'/g,' ').replace(/\s+/g,' ').trim();
const nickKey=s=>norm(stripNick(s));
/* PHASE_40 (owner-approved, redesign-v2): Equipos' own computed lede ("Doce clubes
   activos y veintiuno que ya no existen...") needs its counts spelled out in Spanish
   words, not digits -- a tiny 0-39 lookup (falls back to the digit above that) rather
   than a general number-to-words algorithm, since nothing in this archive ever counts
   past the 30s. beforeNoun=true asks for the masculine-apocope form (veintiuno ->
   veintiún) needed only when the number directly modifies a plural noun like "clubes"
   (VIEW_DESC.equipos.desaparecidos, tabs.js) -- the lede itself uses the number as a
   standalone pronoun ("y veintiuno que ya no existen"), where no apocope applies.
   Placed here, before num/dash/pct, rather than after them: tests/_web_text.py
   splices web/index.html back together using pct()'s own exact trailing text as the
   anchor for the next original segment -- inserting after pct() breaks that anchor,
   found live the first time this landed there (every test that calls web_text(),
   not just the frozen byte-diff one, failed). */
const NUM_WORDS_ES=['cero','uno','dos','tres','cuatro','cinco','seis','siete','ocho','nueve','diez',
  'once','doce','trece','catorce','quince','dieciséis','diecisiete','dieciocho','diecinueve','veinte',
  'veintiuno','veintidós','veintitrés','veinticuatro','veinticinco','veintiséis','veintisiete','veintiocho','veintinueve','treinta',
  'treinta y uno','treinta y dos','treinta y tres','treinta y cuatro','treinta y cinco','treinta y seis','treinta y siete','treinta y ocho','treinta y nueve'];
const NUM_WORDS_ES_APOCOPE={1:'un',21:'veintiún',31:'treinta y un'};
const numWordsEs=(n,beforeNoun)=>(!Number.isInteger(n)||n<0||n>39) ? String(n)
  : (beforeNoun && NUM_WORDS_ES_APOCOPE[n]) || NUM_WORDS_ES[n];
const num=v=>v==null?'—':(typeof v==='number'?v.toLocaleString('es-PR'):v);
const dash=v=>(v==null||v==='')?'—':v;
const pct=v=>v==null?'—':('.'+String(Math.round(v*1000)).padStart(3,'0'));
/* Public nav entry. A nav word / bottom-bar tap / hub card lands on the
   section's landing view (its overview). Deep links, the subnav and the
   mega-menu go through showView() directly. */
function showTab(id,noScroll){
  if(!PANELS.includes(id)) return;   /* includes 'perfil', which has no nav button */
  _showPanel(id,noScroll);
  if(VIEW_SECS.indexOf(id)>-1) showView(id,'__landing',{panel:false,noScroll:true,fromNav:true});
  else setHash(id);
}
function setHash(h){
  if(('#'+h)===location.hash) return;
  HASH_ECHO=h;
  try{ location.hash=h; }catch(e){}
}

function showView(sec,view,opts){
  opts=opts||{};
  if(VIEW_SECS.indexOf(sec)<0){ showTab(sec,opts.noScroll); return; }
  let panelChanged=false;
  if(opts.panel!==false) panelChanged=_showPanel(sec,true);
  const S=document.getElementById(sec); if(!S) return;
  const panel=S.querySelector(':scope > .panel'); if(!panel) return;
  const views=Array.from(panel.querySelectorAll(':scope > .view'));
  if(!views.length) return;
  let target=views.find(v=>v.dataset.view===view) || views.find(v=>v.dataset.view==='__landing');
  if(!target) return;
  const now=target.dataset.view;
  views.forEach(v=>{ v.hidden = v!==target; });
  if(!panelChanged && !opts.fromNav && VIEW_NOW[sec]!==now){
    target.classList.remove('view-enter'); void target.offsetWidth; target.classList.add('view-enter');
  }
  VIEW_NOW[sec]=now;
  if(sec==='archivo'&&now==='calidad') openDQ();   /* index/data_quality.json is fetched only here and on a player page */
  /* PHASE_19 (owner-approved, redesign-v2): the real "jugador" page (a detail-only
     view, VIEW_MAP.jugadores's own detail:['jugador','#playerPage']) gets its own
     back-link/avatar/name header (tabs.js buildPlayerHead()) instead of the
     section's shared "JUGADORES" .phead/.subnav every other Jugadores view shows --
     hidden only for this one view, restored for every other (buscar/lideres/salon/
     .../comparar), same two elements every other section still always shows. */
  if(sec==='jugadores'){
    const ph=panel.querySelector(':scope > .phead'), sn=panel.querySelector(':scope > .subnav'), inPlayer=now==='jugador';
    if(ph) ph.hidden=inPlayer;
    /* .subnav{display:flex} in the stylesheet outranks the [hidden] attribute
       (same real specificity-vs-[hidden] gotcha #pfField's own display toggle
       already works around, player.js renderPlayerIndex()) -- found live, not
       assumed: the pill row stayed visible with .hidden=true until this was
       checked against a real screenshot. style.display, not the attribute. */
    if(sn) sn.style.display = inPlayer ? 'none' : '';
  }
  syncSubnav(sec,now);
  if(!opts.fromHash && !opts.noHash) setHash(now==='__landing'?sec:sec+'/'+now);
  if(!opts.noScroll){
    const smooth=!matchMedia('(prefers-reduced-motion:reduce)').matches;
    window.scrollTo({top:0,behavior:smooth?'smooth':'auto'});
  }
}
/* ============================================================
   STORAGE
   localStorage when the file is opened normally, memory when it
   is sandboxed. Never throws. ST.wrote records whether the last
   real write landed, so a silent failure can be shown to the user
   instead of pretending the save worked.
   ============================================================ */
const MEM={};
const ST={
  wrote:true,
  get(k){ if(k in MEM) return MEM[k];
    try{ const v=localStorage.getItem('bsn:'+k); return v===null?null:v; }catch(e){ return null; } },
  json(k){ const v=ST.get(k); if(v==null) return null; try{ return JSON.parse(v); }catch(e){ return null; } },
  set(k,v){ MEM[k]=String(v);
    try{ localStorage.setItem('bsn:'+k,String(v)); ST.wrote=true; }catch(e){ ST.wrote=false; } },
  setJSON(k,o){ ST.set(k,JSON.stringify(o)); },
  del(k){ delete MEM[k]; try{ localStorage.removeItem('bsn:'+k); }catch(e){} },
  keys(){ try{ return Object.keys(localStorage).filter(k=>k.indexOf('bsn:')===0).map(k=>k.slice(4)); }
    catch(e){ return Object.keys(MEM); } }
};

/* ============================================================
   DATA — fetch web/data/*.json when this file is served over http
   (i.e. deployed). Opened as a local file there is no data/ to
   reach, so get() returns null and every reader falls through to
   the constants baked in near the top. Same layering idea as
   translate(): merge over a source block, never edit it.
   Cache: memory -> localStorage (bsn:data:*, via ST) -> network.
   ============================================================ */
const DATA={
  base: location.protocol==='file:' ? null : new URL('data/',location.href).href,
  mem:{},
  async get(path,fresh){
    if(this.base===null) return null;
    if(!fresh && (path in this.mem)) return this.mem[path];
    if(!fresh){ const c=ST.json('data:'+path); if(c!==null){ this.mem[path]=c; return c; } }
    try{
      const r=await fetch(this.base+path);
      if(!r.ok) throw 0;
      const j=await r.json();
      this.mem[path]=j; ST.setJSON('data:'+path,j);
      return j;
    }catch(e){ if(!fresh) this.mem[path]=null; return null; }
  },
  /* Drop the cached JSON when web/data has been rebuilt (source_digest changed). */
  async syncVersion(){
    if(this.base===null) return;
    const m=await this.get('manifest.json',true);
    if(!m || ST.get('data:digest')===m.source_digest) return;
    ST.keys().forEach(k=>{ if(k.indexOf('data:')===0 && k!=='data:digest') ST.del(k); });
    this.mem={}; ST.set('data:digest',m.source_digest);
    /* 5E — drop the service worker's data cache in lockstep with the ST layer. */
    try{ navigator.serviceWorker.controller.postMessage({type:'purge-data'}); }catch(e){}
  }
};
function fmtLongDate(iso){
  const p=String(iso).split('-');
  if(p.length!==3) return String(iso);
  const m=MESES[parseInt(p[1],10)-1];
  return parseInt(p[2],10)+' de '+(m||p[1])+' de '+p[0];
}
/* Archive DOBs are stored M/D/YYYY (bsnpr.com's own format, src/parse_players.py:403). Reformats to
   fmtLongDate's "D de mes de YYYY" for display, unambiguously. Pure string/arithmetic throughout --
   the M/D/YYYY parse below and fmtLongDate itself both only split/pad/concatenate strings, never
   construct a Date object, so there is no UTC/local boundary anywhere and no timezone can shift the
   day. _daysInMonth is calendar arithmetic (with the standard leap-year rule), not Date-based either.
   Any parse failure or calendar-invalid date (e.g. 2/30) falls back to the raw string, unchanged --
   the exact same text this line rendered before this function existed. No new Spanish text: on the
   success path this is just fmtLongDate's own output; on failure, the untouched raw value. */
function _daysInMonth(y,m){
  const d=[31,(y%4===0&&(y%100!==0||y%400===0))?29:28,31,30,31,30,31,31,30,31,30,31];
  return d[m-1];
}
function fmtArchiveDob(raw){
  const m=/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(String(raw||''));
  if(!m) return raw;
  const mo=+m[1], da=+m[2], yr=+m[3];
  if(mo<1||mo>12||da<1||da>_daysInMonth(yr,mo)) return raw;
  return fmtLongDate(yr+'-'+String(mo).padStart(2,'0')+'-'+String(da).padStart(2,'0'));
}
/* ============================================================
   SEEDING — everyone gets the same puzzle on the same day
   ============================================================ */
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;
  let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;
  return((t^t>>>14)>>>0)/4294967296;};}
const EPOCH=Date.UTC(2026,0,1);
function todayStamp(){const d=new Date();
  return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function puzzleNo(){const d=new Date();
  return Math.floor((Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())-EPOCH)/86400000)+1;}
function seededShuffle(arr,rnd){const a=arr.slice();
  for(let i=a.length-1;i>0;i--){const j=Math.floor(rnd()*(i+1));const t=a[i];a[i]=a[j];a[j]=t;}return a;}
function pick(a){return a[Math.floor(Math.random()*a.length)];}
