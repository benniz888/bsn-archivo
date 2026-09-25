/* PHASE_1_SPLIT STEP 7. Three of the four archive games, moved out of web/index.html's inline
   <script>, byte for byte -- no renaming, no reformatting, no reordering. Loaded via
   <script src="js/games.js"> right after js/data-quality.js, before the rest.

   Two blocks (Cuadricula and Temporada Perfecta sit directly next to each other in the original,
   with nothing but a blank line between, so they moved as one merged block; Sube y baja is
   separate, with "Quien soy?" -- a fourth game, NOT named in this step and left in
   web/index.html -- sitting between them in the original):

   - CUADRICULA+TEMPORADA_PERFECTA: axLabel, axFull, axMatch, solutions (the grid game's axis
     logic) through the whole "LA CUADRICULA" section (GRID_SCHEMA, GB, newBoard and every
     drawing/interaction function down to setGMode), then directly into the whole "LA TEMPORADA
     PERFECTA" section (DEC, SLOTS, SLOT_ES, FITS, TAGV, DR, CAL_K/CAL_S, posTokens/fits, the
     draft flow down to shareDraft). CAT_KEYS and GRID_CLUBS -- declared right before axLabel in
     the original, and easy to assume they travel together with it -- do NOT move: GRID_CLUBS is
     `FKEYS.filter(...)`, a plain top-level `const`, evaluated the instant games.js runs, not
     deferred inside a function body like every other cross-file reference in this split. FKEYS
     itself is computed in web/index.html's own inline <script> (the "DERIVED" section), which
     loads AFTER games.js -- so GRID_CLUBS's own initializer would throw ReferenceError: FKEYS is
     not defined at games.js's load time, which aborts the rest of the script's top-level
     execution and leaves GB/DR/HL and everything after permanently uninitialized (caught by the
     real-browser test, not a static check -- see the STEP 7 commit message). axLabel/axFull/
     axMatch/solutions don't reference CAT_KEYS or GRID_CLUBS at all (only CATS/F/POOL, inside
     function bodies -- safe), so only they moved; CAT_KEYS and GRID_CLUBS stayed in
     web/index.html, right where FKEYS is already defined earlier in the same script.

   - SUBE_Y_BAJA: HL and its newHL/drawHL/answerHL functions. HL_SETS itself (the question data)
     already moved to js/data.js in step 3 -- its own section header moved with it then, so this
     group starts clean with no header of its own.

   CROSS-FILE READS (all inside function bodies, evaluated only once every script has loaded --
   safe, unlike the FKEYS case above): newBoard calls mulberry32 (js/helpers.js); the grid/draft
   code reads POOL, F, CATS (js/data.js) and calls pick() (js/helpers.js); ST (js/helpers.js) for
   bsn:grid/bsn:hlbest/bsn:streak persistence; esc/$/el (js/helpers.js) for rendering; newHL
   calls pick(HL_SETS) (js/helpers.js's pick, js/data.js's HL_SETS); combos()/poolFor() read
   FKEYS (web/index.html) -- safe here because they're function bodies, only called at boot time
   (runBoot(), after web/index.html's own inline script -- which defines FKEYS -- has finished).

   tests/_app_text.py knows how to splice this file, js/data.js, js/helpers.js, js/player.js,
   js/data-quality.js and web/index.html back into the exact original byte stream. Replaced
   entirely once app/bsn_archivo.html becomes the archived pointer (step 11/12 of the split). */

function axLabel(a){ return a.t==='c' ? F[a.k].name.split(' de ')[0] : CATS[a.k][0]; }
function axFull(a){ return a.t==='c' ? F[a.k].name : CATS[a.k][0]; }
function axMatch(p,a){ return a.t==='c' ? p.c.includes(a.k) : CATS[a.k][1](p); }
function solutions(r,c){
  if(r.t===c.t && r.k===c.k) return [];
  return POOL.filter(p=>axMatch(p,r)&&axMatch(p,c));
}

/* ============================================================
   LA CUADRÍCULA
   Real Immaculate Grid rules, which is what makes it hard:
   nine guesses total, a wrong guess burns one, and no player can
   be used twice. Rarity is scored the way the original does —
   the share of players who would name that answer — except that
   with no crowd to measure, the share is modelled from how
   famous each player is. Lower is better.
   ============================================================ */
const GRID_SCHEMA=3;
let GB=null, GMODE='daily';

function newBoard(seed){
  const rnd=mulberry32(seed);
  const clubAx=GRID_CLUBS.map(k=>({t:'c',k}));
  const catAx=CAT_KEYS.map(k=>({t:'a',k}));
  for(let attempt=0;attempt<900;attempt++){
    const rows=seededShuffle(clubAx,rnd).slice(0,3);
    /* Columns mix clubs and attributes. A pure club×club board is
       the better game but this pool rarely supports nine of them,
       so the generator takes what it can get and prefers boards
       with at least one club column. */
    const pool=seededShuffle(clubAx.concat(catAx,catAx),rnd);
    const cols=[];
    for(const c of pool){
      if(cols.length===3) break;
      if(cols.some(x=>x.t===c.t&&x.k===c.k)) continue;
      if(rows.some(x=>x.t===c.t&&x.k===c.k)) continue;
      cols.push(c);
    }
    if(cols.length<3) continue;
    const sol=[],counts=[];
    let ok=true;
    for(let i=0;i<3;i++){
      sol.push([]);
      for(let j=0;j<3;j++){
        const s=solutions(rows[i],cols[j]);
        if(!s.length){ ok=false; break; }
        sol[i].push(s); counts.push(s.length);
      }
      if(!ok) break;
    }
    if(!ok) continue;
    const avg=counts.reduce((a,b)=>a+b,0)/9;
    const ones=counts.filter(n=>n===1).length;
    const tight=counts.filter(n=>n<=3).length;
    /* Difficulty gate. Two failure modes to avoid, not one: a board
       where every cell has ten obvious answers is not a puzzle, and
       a board where six cells have a single valid answer out of a
       55-player pool is not solvable in nine guesses. Aim between.
       The gate loosens as attempts run out so generation always
       terminates. */
    if(attempt<400){ if(avg<3.2||avg>8||ones>2||tight<2) continue; }
    else if(attempt<700){ if(avg<2.4||ones>4) continue; }
    /* backlog item 6, part 1 — avg/ones/tight were already computed to
       decide whether to accept this board, then thrown away. Kept on the
       returned object so the UI can show real difficulty instead of a
       guess; no new computation. */
    return {rows,cols,sol,day:todayStamp(),seed,avg,ones,tight,
      ans:[[null,null,null],[null,null,null],[null,null,null]],
      guesses:0,used:new Set(),history:[]};
  }
  return null;
}
/* backlog item 6, part 1 — thresholds are the generator's own gate, not
   picked separately: `ones>2` is exactly where the strict pass (attempt
   <400) already rejects a board, so "Normal" tops out right where the
   code already draws the line. Checked against a real 300-board sample
   before choosing these: ~17% Fácil / ~82% Normal / ~2% Difícil — three
   tiers that mean something, not an arbitrary split. */
function gridDifficulty(b){
  if(b.ones===0) return {label:'Fácil'};
  if(b.ones<=2) return {label:'Normal'};
  return {label:'Difícil'};
}
function boardFor(mode){
  if(mode==='daily'){
    const n=puzzleNo();
    for(let k=0;k<40;k++){ const b=newBoard(n*7919+k); if(b) return b; }
  }
  for(let k=0;k<60;k++){ const b=newBoard(Math.floor(Math.random()*1e9)); if(b) return b; }
  return null;
}
function cellShare(p,sol){
  const tot=sol.reduce((a,x)=>a+fame(x),0)||1;
  return fame(p)/tot*100;
}
function loadOrStartDaily(){
  GB=boardFor('daily');
  if(!GB) return;
  const saved=ST.json('grid:'+todayStamp());
  let discarded=false;
  if(saved && saved.v===GRID_SCHEMA && Array.isArray(saved.ans) && saved.ans.length===3){
    const sameAxes = JSON.stringify(saved.rows)===JSON.stringify(GB.rows.map(a=>a.t+':'+a.k)) &&
                     JSON.stringify(saved.cols)===JSON.stringify(GB.cols.map(a=>a.t+':'+a.k));
    if(sameAxes){
      let g=0;
      saved.ans.forEach((row,i)=>{
        if(!Array.isArray(row)) return;
        row.forEach((cell,j)=>{
          if(!cell||!cell.name) return;
          const p=POOL.find(x=>x.n===cell.name);
          if(!p) return;
          if(GB.used.has(p.n)) return;
          /* the verdict is recomputed, never trusted from storage */
          const ok=GB.sol[i][j].some(x=>x.n===p.n);
          if(!ok) return;
          GB.ans[i][j]={name:p.n,ok:true,share:cellShare(p,GB.sol[i][j])};
          GB.used.add(p.n);
        });
      });
      GB.guesses = Math.max(0, Math.min(9, saved.guesses|0));
      const filled=GB.ans.flat().filter(Boolean).length;
      if(GB.guesses<filled) GB.guesses=filled;
    } else discarded=true;
  } else if(saved) discarded=true;
  GB.discarded=discarded;
}
function saveDaily(){
  if(GMODE!=='daily'||!GB) return;
  ST.setJSON('grid:'+todayStamp(),{
    v:GRID_SCHEMA,
    rows:GB.rows.map(a=>a.t+':'+a.k),
    cols:GB.cols.map(a=>a.t+':'+a.k),
    guesses:GB.guesses,
    ans:GB.ans.map(r=>r.map(c=>c?{name:c.name}:null))
  });
  const done=GB.guesses>=9;
  if(!done) return;
  const st=ST.json('streak')||{cur:0,best:0,played:0,last:null,totalScore:0,immaculate:0};
  if(st.last===todayStamp()) return;
  const y=new Date(); y.setDate(y.getDate()-1);   /* setDate is DST-aware; ms arithmetic is not */
  const ys=y.getFullYear()+'-'+String(y.getMonth()+1).padStart(2,'0')+'-'+String(y.getDate()).padStart(2,'0');
  st.cur = st.last===ys ? st.cur+1 : 1;
  st.best=Math.max(st.best,st.cur);
  st.played++; st.last=todayStamp();
  const hits=GB.ans.flat().filter(Boolean).length;
  st.totalScore=(st.totalScore||0)+hits;
  if(hits===9) st.immaculate=(st.immaculate||0)+1;
  ST.setJSON('streak',st);
  drawStreak();
}
function pruneOldBoards(){
  const y=new Date(); y.setDate(y.getDate()-1);
  const ys=y.getFullYear()+'-'+String(y.getMonth()+1).padStart(2,'0')+'-'+String(y.getDate()).padStart(2,'0');
  ST.keys().forEach(k=>{
    if(k.indexOf('grid:')===0 && k!=='grid:'+todayStamp() && k!=='grid:'+ys) ST.del(k);
  });
}
function checkRollover(){
  if(GMODE==='daily' && GB && GB.day!==todayStamp()){
    loadOrStartDaily(); drawBoard();
    $('#gMsg').textContent='Cambió el día. Cuadrícula nueva; lo de ayer quedó guardado.';
  }
}
function drawStreak(){
  const st=ST.json('streak')||{cur:0,best:0,played:0,totalScore:0,immaculate:0};
  $('#streakStrip').innerHTML=`<div class="strip">
    <div><div class="n">#${puzzleNo()}</div><div class="l">cuadrícula de hoy</div></div>
    <div><div class="n">${st.cur||0}</div><div class="l">racha actual</div></div>
    <div><div class="n">${st.best||0}</div><div class="l">mejor racha</div></div>
    <div><div class="n">${st.played||0}</div><div class="l">días jugados</div></div>
    <div><div class="n">${st.immaculate||0}</div><div class="l">cuadrículas perfectas</div></div>
    <div><div class="n">${st.played?(st.totalScore/st.played).toFixed(1):'—'}</div><div class="l">aciertos por día</div></div>
  </div>`;
}
function drawStorageNote(){
  $('#storageNote').innerHTML = ST.wrote ? '' :
    '<div class="warn">Este navegador no deja guardar. Puedes jugar, pero el progreso no sobrevive una recarga.</div>';
}
let SUGG_I=-1;
function drawBoard(){
  const host=$('#gridGame');
  if(!GB){ host.innerHTML='<p class="note">No se pudo generar una cuadrícula con el grupo actual.</p>'; return; }
  const left=9-GB.guesses;
  const hits=GB.ans.flat().filter(Boolean).length;
  const rare=GB.ans.flat().filter(Boolean).reduce((a,c)=>a+c.share,0);
  /* backlog item 6, part 1 — real difficulty, not a spoiler: the label
     is an aggregate (how many cells are a single-answer trap), never
     which cell, so it doesn't give the grid away. */
  const diff=gridDifficulty(GB);
  let h=`<div class="gamehead">
    <div class="modebtns" role="tablist">
      <button role="tab" aria-selected="${GMODE==='daily'}" onclick="setGMode('daily')">Diaria</button>
      <button role="tab" aria-selected="${GMODE==='practice'}" onclick="setGMode('practice')">Práctica</button>
    </div>
    <div class="dim" style="font-size:var(--fs-2xs)">9 intentos · cada intento cuenta, acierte o falle · ningún jugador se repite<br>
      La nómina verificada es de ${POOL.length} jugadores; el autocompletar te enseña quiénes existen.<br>
      Dificultad de hoy: <b>${diff.label}</b>${GB.ones?` — ${GB.ones} casilla${GB.ones===1?'':'s'} con una sola respuesta posible`:''}.</div>
  </div>
  <div class="gridwrap"><div class="gridtable">
    <div class="gcorner"></div>`;
  GB.cols.forEach(c=>{
    h+=`<div class="ghead">${c.t==='c'?crest(c.k,26,31):''}<span>${esc(axLabel(c))}</span></div>`;
  });
  for(let i=0;i<3;i++){
    const r=GB.rows[i];
    h+=`<div class="ghead row">${r.t==='c'?crest(r.k,26,31):''}<span>${esc(axLabel(r))}</span></div>`;
    for(let j=0;j<3;j++){
      const a=GB.ans[i][j];
      const cls=a?(a.ok?'ok':'bad'):'';
      const sel=(GB.sel&&GB.sel[0]===i&&GB.sel[1]===j)?'true':'false';
      h+=`<button class="gcell ${cls}" aria-pressed="${sel}" ${a||left<=0?'disabled':''} onclick="selectCell(${i},${j})">`;
      if(a) h+=`<span class="pn">${esc(a.name)}</span><span class="pr">${a.share.toFixed(1)}%</span>`;
      else h+=`<span class="plus">+</span>`;
      h+='</button>';
    }
  }
  h+='</div></div>';
  h+=`<div class="pips" aria-label="Intentos usados">`;
  for(let i=0;i<9;i++){
    const ev=GB.history[i];
    h+=`<span class="pip ${ev?(ev.ok?'hit':'miss'):''}"></span>`;
  }
  h+=`<span class="dim" style="font-size:var(--fs-2xs);margin-left:var(--sp-2)">${left} intento${left===1?'':'s'}</span></div>`;

  if(left>0){
    h+=`<div class="guessbar" style="position:relative">
      <input type="text" id="gGuess" placeholder="${GB.sel?'Nombre del jugador para esa casilla…':'Toca una casilla primero'}"
        autocomplete="off" spellcheck="false" ${GB.sel?'':'disabled'} aria-label="Escribe un nombre">
      <button class="btn primary" onclick="submitGuess()" ${GB.sel?'':'disabled'}>Enviar</button>
      <div id="gSugg"></div></div>`;
  } else {
    h+=`<div class="scoreline"><span>Aciertos <b>${hits}/9</b></span>
      <span>Rareza <b>${rare.toFixed(1)}</b> <span class="dim">(mientras más baja, mejor)</span></span>
      ${hits===9?'<span style="color:var(--ok);font-weight:700">PERFECTA</span>':''}</div>
      <div class="btnrow"><button class="btn" onclick="shareGrid()">Copiar resultado</button>
      <button class="btn" onclick="revealGrid()">Ver respuestas</button>
      <button class="btn" onclick="setGMode('practice')">Otra en práctica</button></div>`;
  }
  h+=`<div class="msg" id="gMsg" role="status" aria-live="polite"></div>`;
  if(GB.discarded) h+='<div class="warn">Había una partida guardada de otra cuadrícula. Se descartó en vez de mezclar respuestas viejas con casillas nuevas.</div>';
  h+=`<div id="gReveal"></div>`;
  host.innerHTML=h;
  const inp=$('#gGuess');
  if(inp){
    inp.oninput=()=>drawSugg(inp.value);
    inp.onkeydown=e=>{
      const box=$('#gSugg').querySelectorAll('button');
      if(e.key==='ArrowDown'){SUGG_I=Math.min(SUGG_I+1,box.length-1);paintSugg();e.preventDefault();}
      else if(e.key==='ArrowUp'){SUGG_I=Math.max(SUGG_I-1,0);paintSugg();e.preventDefault();}
      else if(e.key==='Enter'){
        e.preventDefault();
        if(SUGG_I>=0&&box[SUGG_I]) box[SUGG_I].click(); else submitGuess();
      }
    };
    if(GB.sel) inp.focus();
  }
}
function drawSugg(v){
  const q=norm(v); const box=$('#gSugg');
  SUGG_I=-1;
  if(q.length<2){ box.innerHTML=''; box.className=''; return; }
  /* Suggestions come from the whole pool, not just the valid
     answers — showing only correct names would give the game away. */
  const hits=POOL.filter(p=>norm(p.n).includes(q)).slice(0,8);
  if(!hits.length){ box.innerHTML=''; box.className=''; return; }
  box.className='sugg';
  box.innerHTML=hits.map(p=>{
    const used=GB.used.has(p.n);
    return `<button ${used?'disabled style="opacity:.4"':''} onclick="chooseSugg(${JSON.stringify(p.n).replace(/"/g,'&quot;')})">
      ${esc(p.n)} <span class="sm">${esc([p.pos,p.c.map(c=>F[c].abbr).join('/')].filter(Boolean).join(' · '))}${used?' · ya usado':''}</span></button>`;
  }).join('');
}
function paintSugg(){
  $('#gSugg').querySelectorAll('button').forEach((b,i)=>b.classList.toggle('on',i===SUGG_I));
}
function chooseSugg(n){ $('#gGuess').value=n; $('#gSugg').innerHTML=''; $('#gSugg').className=''; submitGuess(); }
function selectCell(i,j){ if(GB.ans[i][j]) return; GB.sel=[i,j]; drawBoard(); }
function submitGuess(){
  checkRollover();
  if(!GB||!GB.sel) return;
  const inp=$('#gGuess'); if(!inp) return;
  const v=norm(inp.value);
  if(!v) return;
  const p=POOL.find(x=>norm(x.n)===v) || POOL.find(x=>norm(x.n).includes(v));
  const [i,j]=GB.sel;
  if(!p){ $('#gMsg').textContent='Ese nombre no está en la nómina verificada. No gasta intento.'; $('#gMsg').className='msg bad'; return; }
  if(GB.used.has(p.n)){ $('#gMsg').textContent='Ya lo usaste. No gasta intento.'; $('#gMsg').className='msg bad'; return; }
  const ok=GB.sol[i][j].some(x=>x.n===p.n);
  GB.guesses++;
  GB.history.push({name:p.n,ok,i,j});
  if(ok){
    GB.ans[i][j]={name:p.n,ok:true,share:cellShare(p,GB.sol[i][j])};
    GB.used.add(p.n);
  }
  GB.sel=null;
  saveDaily();
  drawBoard();
  const m=$('#gMsg');
  if(ok){ m.textContent=`${p.n} entra. ${GB.sol[i][j].length} jugador${GB.sol[i][j].length===1?'':'es'} del grupo sirven ahí.`; m.className='msg good'; }
  else { m.textContent=`${p.n} no cumple ${axFull(GB.rows[i])} + ${axFull(GB.cols[j])}. Intento gastado.`; m.className='msg bad'; }
}
function revealGrid(){
  let h='<h4 class="sub">Quién servía en cada casilla</h4><div class="cards g3">';
  for(let i=0;i<3;i++)for(let j=0;j<3;j++){
    const s=GB.sol[i][j].slice().sort((a,b)=>fame(b)-fame(a));
    h+=`<div class="card"><div class="dim" style="font-size:var(--fs-3xs)">${esc(axLabel(GB.rows[i]))} + ${esc(axLabel(GB.cols[j]))}</div>
      <div class="chips">${s.map(p=>`<span class="tag ${GB.ans[i][j]&&GB.ans[i][j].name===p.n?'gold':''}">${esc(p.n)} · ${cellShare(p,GB.sol[i][j]).toFixed(0)}%</span>`).join('')}</div></div>`;
  }
  h+='</div><p class="note">El porcentaje es cuánta gente escogería a ese jugador ahí, estimado a partir de qué tan conocido es. En el juego original ese número sale de millones de partidas; aquí sale de un modelo, y se dice.</p>';
  $('#gReveal').innerHTML=h;
}
function shareGrid(){
  const hits=GB.ans.flat().filter(Boolean).length;
  const rare=GB.ans.flat().filter(Boolean).reduce((a,c)=>a+c.share,0);
  let g='';
  for(let i=0;i<3;i++){ for(let j=0;j<3;j++) g+=GB.ans[i][j]?'🟩':'⬛'; g+='\n'; }
  const txt=`BSN Archivo · La Cuadrícula #${puzzleNo()}\n${hits}/9 · rareza ${rare.toFixed(1)}\n${g}`;
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(()=>{$('#gMsg').textContent='Copiado.';$('#gMsg').className='msg good';});
  }
}
function setGMode(m){
  GMODE=m;
  if(m==='daily') loadOrStartDaily(); else GB=boardFor('practice');
  drawBoard();
}

/* ============================================================
   LA TEMPORADA PERFECTA — 34-0
   The BSN season is 34 games. You draft five players from spun
   decades and the model projects a record. The roster rule is the
   league's own: no more than three refuerzos, and at least one
   nativo on the floor. That constraint is the game — the best five
   names are often four imports, and the rules will not let you.
   ============================================================ */
/* ============================================================
   LA TEMPORADA PERFECTA (34-0)

   Rebuilt from a decade-only slot machine into a team-and-decade
   one with five real positions. The old version asked "who played
   in the 80s" — a question the archive could answer for almost
   anyone, which is why it was chosen. Team-by-decade is a harder
   question and only became answerable once the season corpus
   arrived with clubs attached to per-season lines.

   Positions are the constraint that makes a draft a draft: without
   them a roster is just the five highest-rated players available.
   ============================================================ */
const DEC=[1950,1960,1970,1980,1990,2000,2010,2020];
const SLOTS=['PG','SG','SF','PF','C'];
const SLOT_ES={PG:'Base',SG:'Escolta',SF:'Alero',PF:'Ala-pívot',C:'Pívot'};

/* A player listed simply as "G" is a guard; the archive rarely
   distinguishes the two backcourt spots before the modern era, so a
   generic listing is allowed to fill either. */
const FITS={PG:['PG','G'],SG:['SG','G'],SF:['SF','F'],PF:['PF','F','F/C'],C:['C','F/C']};
const TAGV={mvp:9,scoring:7,'10k':5,legend:5,nba:3,champion:2,native:0,import:0};
let DR=null;
/* backlog item 6, part 2 (2026-09-14) — recalibrated after simulating real
   drafts through the actual spin()/place()/skipSpin() functions (not
   guessed): a "greedy" bot that always takes the highest-rate() legal
   option (exactly what the sorted candidate list already hands a player)
   won 34-0 in 16-20% of games and >=30 wins 75% of the time under the old
   K=110/S=18 — worse than the "median 30-4" the prior recalibration's own
   comment names as the problem it was trying to fix. K=116 is chosen so a
   zero-skill ("random-legal") bot's median roster is exactly a .500
   season by construction; S=40 (vs. the old 18) is wide enough that the
   ~50-point rating gap between random and greedy play no longer saturates
   win probability near-certain. Matched before/after on the same 250
   simulated rosters each: greedy median 32-2 -> 25-9, greedy 34-0 rate
   19.6% -> 0%, random median 18-16 -> 16-18 (still close to .500,
   slightly under). Full record: docs/session.md, 2026-09-14. */
let CAL_K=116, CAL_S=40;

function posTokens(p){ return String(p.pos||'').split('/').map(s=>s.trim()).filter(Boolean); }
function fits(p,slot){
  const t=posTokens(p);
  if(!t.length) return true;          /* unrecorded position fills anywhere, and says so */
  return t.some(x=>FITS[slot].includes(x));
}
function resetDraft(){
  DR={slots:{},used:new Set(),club:null,dec:null,skips:2,done:false,sel:null,msg:''};
  SLOTS.forEach(s=>DR.slots[s]=null);
  spin();
}
function rosterOf(){ return SLOTS.map(s=>DR.slots[s]).filter(Boolean); }
function openSlots(){ return SLOTS.filter(s=>!DR.slots[s]); }
function importsIn(r){ return r.filter(p=>(p.t||[]).includes('import')).length; }

function rate(p){
  let v=8;
  (p.t||[]).forEach(t=>v+=(TAGV[t]||0));
  if(p.ppg!=null) v+=Math.max(0,(p.ppg-12))*1.5;
  if(p.rpg!=null) v+=Math.max(0,(p.rpg-5))*1.1;
  if(p.apg!=null) v+=Math.max(0,(p.apg-2.5))*1.6;
  if(p.spg!=null) v+=Math.max(0,(p.spg-0.8))*3.0;
  if(p.bpg!=null) v+=Math.max(0,(p.bpg-0.5))*3.0;
  return v;
}

/* Every club-decade pair the pool can actually answer. Computed fresh
   each spin because a filled slot changes which pairs are still useful. */
function poolFor(club,dec){
  return POOL.filter(p=>p.c.includes(club)&&p.d.includes(dec)&&!DR.used.has(p.n));
}
function combos(){
  const out=[], open=openSlots();
  FKEYS.forEach(club=>{
    DEC.forEach(dec=>{
      const cand=poolFor(club,dec);
      if(cand.some(p=>open.some(s=>fits(p,s)))) out.push({club,dec,n:cand.length});
    });
  });
  return out;
}
function spin(){
  if(!openSlots().length){ finishDraft(); return; }
  const c=combos();
  if(!c.length){ DR.done=true; DR.msg='El archivo se queda sin jugadores para las posiciones que faltan.'; finishDraft(); return; }
  /* Weighted by depth so a club-decade with one lonely player is not as
     likely as a real roster — otherwise most spins are dead ends. */
  const w=c.map(x=>Math.min(x.n,6)), tot=w.reduce((a,b)=>a+b,0);
  let r=Math.random()*tot, i=0;
  while(r>w[i]){ r-=w[i]; i++; }
  DR.club=c[i].club; DR.dec=c[i].dec; DR.sel=null; DR.msg='';
  drawPicks();
}
function skipSpin(){
  if(DR.skips<=0){ DR.msg='No quedan pases.'; drawPicks(); return; }
  DR.skips--; spin();
}
function selectSlot(s){
  if(DR.done) return;
  DR.sel = (DR.sel===s ? null : s);
  drawPicks();
}
function legal(p,slot){
  const next=rosterOf().concat([p]);
  if(importsIn(next)>3) return 'La regla de refuerzos: máximo tres por plantilla.';
  if(!fits(p,slot)) return 'No juega en esa posición.';
  return null;
}
function place(name){
  if(DR.done) return;
  const slot=DR.sel;
  if(!slot){ DR.msg='Escoge primero una posición en la cancha.'; drawPicks(); return; }
  const p=poolFor(DR.club,DR.dec).find(x=>x.n===name);
  if(!p) return;
  const bad=legal(p,slot);
  if(bad){ DR.msg=bad; drawPicks(); return; }
  DR.slots[slot]=p; DR.used.add(p.n); DR.sel=null; DR.msg='';
  spin();
}

function posLabel(p){
  const t=p.pos||'—';
  return p.posSrc==='perfil' ? t+'<span class="muted" title="Perfil calculado de sus propios promedios; la fuente no publica su posición">*</span>' : t;
}
function courtHTML(){
  /* A slot the current spin cannot fill is a dead tap. Marking it up
     front turns a mystery into a choice: pick another position, or
     spin again. */
  const avail=s=>poolFor(DR.club,DR.dec).some(p=>fits(p,s));
  const cell=s=>{
    const p=DR.slots[s], on=DR.sel===s, open=!p;
    const dead=open&&!DR.done&&!avail(s);
    const border = on?'var(--fuego)':(dead?'var(--line-soft)':(open?'var(--line)':'var(--ok)'));
    return `<button onclick="selectSlot('${s}')" style="all:unset;cursor:${DR.done?'default':'pointer'};
      display:block;border:2px ${open?'dashed':'solid'} ${border};border-radius:12px;padding:var(--sp-2_5) var(--sp-2);
      text-align:center;background:${on?'var(--tint-fuego)':'var(--hair-2)'};min-height:58px">
      <div style="font-size:var(--fs-3xs);letter-spacing:.08em;font-weight:700;color:${open?'var(--ink-3)':'var(--ink-2)'}">${s}</div>
      ${p?`<div style="font-weight:700;font-size:var(--fs-xs);margin-top:3px;line-height:1.2">${esc(p.n)}</div>
           <div class="dim" style="font-size:var(--fs-3xs)">${p.c.map(c=>F[c]?F[c].abbr:c).join(' ')}</div>`
        :`<div class="dim" style="font-size:var(--fs-3xs);margin-top:3px${dead?';opacity:.45':''}">${SLOT_ES[s]}${dead?' · vacío':''}</div>`}
    </button>`;
  };
  return `<div style="border:1px solid var(--line);border-radius:14px;padding:var(--sp-3_5);
    background:linear-gradient(180deg,var(--hair),transparent)">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-2_5);max-width:340px;margin:0 auto var(--sp-2_5)">
      ${cell('C')}${cell('PF')}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:var(--sp-2_5);max-width:460px;margin:0 auto">
      ${cell('SF')}${cell('PG')}${cell('SG')}</div>
  </div>`;
}

function drawPicks(){
  const host=$('#draftGame');
  if(!DR){ host.innerHTML=''; return; }
  const roster=rosterOf(), imp=importsIn(roster);
  const nat=roster.filter(p=>(p.t||[]).includes('native')).length;
  let h=`<div class="gamehead">
    <div class="dim" style="font-size:var(--fs-2xs)">Gira equipo y década · coloca cinco posiciones · ${DR.skips} pases</div>
    <div class="chips" style="margin:0">
      <span class="tag ${imp>=3?'gold':''}">Refuerzos ${imp}/3</span>
      <span class="tag">Nativos ${nat}</span>
      <span class="tag">${roster.length}/5</span></div>
  </div>`;

  if(!DR.done){
    h+=`<div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-2_5);margin:var(--sp-3) 0">
      <div class="card" style="text-align:center;border-color:#E8B23A;padding:var(--sp-2_5)">
        <div style="font-size:var(--fs-3xs);letter-spacing:.1em;font-weight:700;color:#E8B23A">EQUIPO</div>
        <div style="font-family:inherit;font-weight:800;font-size:30px;line-height:1.1">${esc(F[DR.club].abbr)}</div>
        <div class="dim" style="font-size:var(--fs-3xs)">${esc(F[DR.club].name)}</div></div>
      <div class="card" style="text-align:center;border-color:#9B6BE0;padding:var(--sp-2_5)">
        <div style="font-size:var(--fs-3xs);letter-spacing:.1em;font-weight:700;color:#9B6BE0">DÉCADA</div>
        <div style="font-family:inherit;font-weight:800;font-size:30px;line-height:1.1">${DR.dec}s</div>
        <div class="dim" style="font-size:var(--fs-3xs)">${poolFor(DR.club,DR.dec).length} disponibles</div></div>
    </div>
    <div class="btnrow" style="margin-bottom:var(--sp-3)">
      <button class="btn primary" onclick="skipSpin()" ${DR.skips?'':'disabled'}>Girar de nuevo (${DR.skips})</button>
      <button class="btn" onclick="resetDraft()">Empezar de nuevo</button></div>`;
  }

  h+=courtHTML();

  if(!DR.done){
    const open=openSlots();
    if(!DR.sel){
      h+=`<p class="note" style="margin-top:var(--sp-3)">Toca una posición en la cancha para colocar a alguien de ${esc(F[DR.club].name)} en los ${DR.dec}s.</p>`;
    } else {
      const cand=poolFor(DR.club,DR.dec).filter(p=>fits(p,DR.sel));
      h+=`<h4 class="sub">${SLOT_ES[DR.sel]} · ${esc(F[DR.club].name)} · ${DR.dec}s</h4>`;
      if(!cand.length){
        h+=`<p class="note">Nadie en el archivo cubre esa posición para este equipo y esta década. Escoge otra posición o gira de nuevo.</p>`;
      } else {
        h+='<div class="cards g2">';
        cand.sort((a,b)=>rate(b)-rate(a)).forEach(p=>{
          const bad=legal(p,DR.sel);
          const line=[p.ppg!=null?p.ppg+' pts':null,p.rpg!=null?p.rpg+' reb':null,
                      p.apg!=null?p.apg+' ast':null,p.gp!=null?p.gp+' PJ':null].filter(Boolean).join(' · ');
          h+=`<button class="card" style="text-align:left;cursor:pointer;${bad?'opacity:.55':''}"
            onclick="place(${JSON.stringify(p.n).replace(/"/g,'&quot;')})">
            <div style="font-weight:700">${esc(p.n)}</div>
            <div class="dim" style="font-size:var(--fs-2xs)">${posLabel(p)} · ${p.c.map(c=>F[c]?F[c].abbr:c).join(' ')}</div>
            ${line?`<div class="muted" style="font-size:var(--fs-2xs);margin-top:var(--sp-1)">${line}</div>`
                 :`<div class="muted" style="font-size:var(--fs-2xs);margin-top:var(--sp-1)">Sin promedios registrados.</div>`}
            <div class="chips">${(p.t||[]).map(t=>`<span class="tag">${esc({mvp:'MVP',scoring:'Anotación',champion:'Campeón',import:'Refuerzo',native:'Nativo',nba:'NBA','10k':'10k',legend:'Leyenda',figura:'Figura del BSN'}[t]||t)}</span>`).join('')}</div>
            ${bad?`<div class="note" style="color:var(--bad-ink)">${esc(bad)}</div>`:''}
          </button>`;
        });
        h+='</div>';
      }
      h+=`<div class="btnrow"><button class="btn" onclick="selectSlot('${DR.sel}')">Cambiar de posición</button></div>`;
    }
    if(open.length && !openSlots().some(s=>poolFor(DR.club,DR.dec).some(p=>fits(p,s)))){
      h+=`<p class="note">Este equipo y esta década no cubren ninguna posición libre. Gira de nuevo.</p>`;
    }
  }

  h+=`<div class="msg ${DR.msg?'bad':''}" id="dMsg" role="status" aria-live="polite">${esc(DR.msg||'')}</div>
      <div id="dResult" role="status" aria-live="polite"></div>`;
  host.innerHTML=h;
}

function finishDraft(){
  DR.done=true;
  const roster=rosterOf();
  const base=roster.reduce((a,p)=>a+rate(p),0);
  let bonus=0; const notes=[];
  const nat=roster.filter(p=>(p.t||[]).includes('native')).length;
  if(nat>=3){ bonus+=8; notes.push('Tres o más nativos: +8, la química de una plantilla criolla.'); }
  const clubs=new Set(); roster.forEach(p=>p.c.forEach(c=>clubs.add(c)));
  if(clubs.size<=2 && roster.length===5){ bonus+=9; notes.push('Casi todos del mismo club: +9, ya se conocen la cancha.'); }
  const decs=new Set(); roster.forEach(p=>p.d.forEach(d=>decs.add(d)));
  if(decs.size<=2){ bonus+=5; notes.push('Todos de la misma época: +5.'); }
  const mvps=roster.filter(p=>(p.t||[]).includes('mvp')).length;
  if(mvps>=2){ bonus+=7; notes.push(mvps+' MVP en la plantilla: +7.'); }
  if(roster.length===5){ bonus+=6; notes.push('Cinco posiciones cubiertas: +6.'); }
  const total=base+bonus;
  /* Recalibrated after the pool grew and steals and blocks entered the
     rating; the old K/S produced a median of 30-4 against the new numbers. */
  const K=CAL_K,S=CAL_S;
  const pr=1/(1+Math.exp(-(total-K)/S));
  const wins=Math.max(0,Math.min(34,Math.round(pr*34)));
  const missing=roster.reduce((a,x)=>a+(x.ppg==null?1:0)+(x.rpg==null?1:0)+(x.apg==null?1:0),0);
  const guessed=roster.filter(p=>p.posSrc==='perfil').length;
  const verdict = wins===34?'Temporada perfecta. Nadie lo ha hecho de verdad — el récord real es 29-5, Bayamón 1993.'
    : wins>=30?'Mejor que cualquier temporada real del BSN.'
    : wins>=25?'Campeón claro.'
    : wins>=20?'Playoffs cómodos.'
    : wins>=15?'Pelea por el último boleto.'
    : 'Se queda fuera.';
  drawPicks();
  $('#dResult').innerHTML=`<div class="card" style="margin-top:var(--sp-3_5);border-color:${wins>=25?'var(--ok)':'var(--line)'}">
    <div style="font-family:inherit;font-weight:800;font-size:46px;line-height:1">${wins}-${34-wins}</div>
    <div class="muted" style="font-size:var(--fs-base);margin-top:var(--sp-1)">${esc(verdict)}</div>
    <div class="scoreline"><span>Base <b>${base.toFixed(0)}</b></span><span>Bonos <b>+${bonus}</b></span>
      <span>Total <b>${total.toFixed(0)}</b></span></div>
    ${notes.length?`<ul class="muted" style="font-size:var(--fs-xs);padding-left:var(--sp-4_5);margin-top:var(--sp-2)">${notes.map(n=>'<li>'+esc(n)+'</li>').join('')}</ul>`:''}
    <div class="warn">${missing} de ${roster.length*3} casillas estadísticas de esta plantilla nunca se registraron.${guessed?` ${guessed} ${guessed===1?'jugador tiene':'jugadores tienen'} la posición calculada a partir de sus promedios porque la fuente no la publica.`:''}
      Ese hueco es el proyecto de archivo, no un defecto del juego.</div>
    <div class="btnrow"><button class="btn" onclick="shareDraft(${wins})">Copiar resultado</button>
      <button class="btn primary" onclick="resetDraft()">Otra plantilla</button></div>
  </div>`;
}
function shareDraft(w){
  const txt=`BSN Archivo · La Temporada Perfecta\n${w}-${34-w}\n`+
    SLOTS.filter(s=>DR.slots[s]).map(s=>s+' · '+DR.slots[s].n).join('\n');
  if(navigator.clipboard&&navigator.clipboard.writeText) navigator.clipboard.writeText(txt);
}
let HL=null;
function newHL(keep){
  const set=pick(HL_SETS);
  const rows=set.rows();
  let a=pick(rows),b=pick(rows),n=0;
  while((b[0]===a[0]||b[1]===a[1])&&n++<40) b=pick(rows);
  HL={set,a,b,streak:keep?HL.streak:0,done:false};
  drawHL();
}
function drawHL(){
  const host=$('#hlGame');
  const best=parseInt(ST.get('hlbest')||'0',10)||0;
  let h=`<div class="gamehead"><div class="dim" style="font-size:var(--fs-2xs)">¿Quién tiene más ${esc(HL.set.label)}?</div>
    <div class="chips" style="margin:0"><span class="tag">Racha ${HL.streak}</span><span class="tag gold">Mejor ${best}</span></div></div>`;
  h+='<div class="cards g2" style="margin-top:var(--sp-2_5)">';
  [HL.a,HL.b].forEach((x,i)=>{
    h+=`<button class="card" style="cursor:pointer;text-align:left" ${HL.done?'disabled':''} onclick="answerHL(${i})">
      <div style="font-weight:700;font-size:17px">${esc(x[0])}</div>
      <div class="dim" style="font-size:var(--fs-2xs)">${HL.done?x[1].toLocaleString('es-PR')+' '+esc(HL.set.unit):'?'}</div></button>`;
  });
  h+='</div><div class="msg" id="hMsg" role="status" aria-live="polite"></div>';
  if(HL.done) h+='<div class="btnrow"><button class="btn primary" onclick="newHL(true)">Siguiente</button></div>';
  host.innerHTML=h;
}
function answerHL(i){
  const picked=i===0?HL.a:HL.b, other=i===0?HL.b:HL.a;
  const ok=picked[1]>other[1];
  HL.done=true;
  if(ok){ HL.streak++; const best=parseInt(ST.get('hlbest')||'0',10)||0;
    if(HL.streak>best) ST.set('hlbest',HL.streak); }
  else HL.streak=0;
  drawHL();
  $('#hMsg').textContent = ok
    ? `Correcto. ${picked[0]}: ${picked[1].toLocaleString('es-PR')} contra ${other[1].toLocaleString('es-PR')}.`
    : `No. ${other[0]} tiene ${other[1].toLocaleString('es-PR')}.`;
  $('#hMsg').className='msg '+(ok?'good':'bad');
}
