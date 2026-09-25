/* PHASE_1_SPLIT STEP 6. The #archivo/calidad data-quality tab, moved out of web/index.html's
   inline <script>, byte for byte -- no renaming, no reformatting, no reordering. Loaded via
   <script src="js/data-quality.js"> right after js/player.js, before the rest.

   One contiguous block: the file's own "CALIDAD DE DATOS" section entirely, including its state
   (DQ, DQ_IDX, DISPUTE_IDX, DISPUTED_IDS, DQ_T, DQ_SORT, DQ_FILTER -- all one `let` statement,
   moved as-is), ensureDQ, buildDQ, openDQ, drawDQ, drawDQTable.

   RECONCILED WITH STEP 5: dqFlag, dqTag, disputeFlag, disputeTag were already moved to
   web/js/player.js in step 5, as "the disputed-row tag/tooltip helpers" -- they are pure
   formatting functions called only from loadPlayerExtra's career-row table (web/index.html,
   still inline), not from anything in THIS file. They read DQ_IDX/DISPUTE_IDX/DISPUTED_IDS,
   which now live here instead of in web/index.html -- an ordinary cross-file global read, no
   different from any other name defined in one split file and used in another. Moving them here
   too would separate dqFlag from dqTag and disputeFlag from disputeTag, which doesn't read as
   "the cleanest home" for either pair; leaving all four in player.js, next to each other, is.
   No duplication: each of the four exists in exactly one file, player.js.

   ensureDQ() and loadPlayerExtra (web/index.html) both call each other's world -- ensureDQ is
   called by loadPlayerExtra (a player page also needs data-quality markers) and by openDQ (this
   tab). That's the reason ensureDQ/DQ_IDX/DISPUTE_IDX/DISPUTED_IDS didn't move with player.js in
   step 5: they were never player-page-exclusive. They're #archivo/calidad-exclusive from openDQ/
   drawDQ/drawDQTable's point of view, EXCEPT that loadPlayerExtra also reaches into them
   (ensureDQ(), DISPUTED_IDS) -- an ordinary cross-file global read again, not a reason to keep
   them in web/index.html once their true owner (ensureDQ, which builds them) moves out.

   tests/_app_text.py knows how to splice this file, js/data.js, js/helpers.js, js/player.js and
   web/index.html back into the exact original byte stream. Replaced entirely once
   app/bsn_archivo.html becomes the archived pointer (step 11/12 of the split). */

/* ============================================================
   CALIDAD DE DATOS — #archivo/calidad
   index/data_quality.json (build_data_quality; docs/specs/data_quality_view_spec.md): the places where two
   pages of bsnpr.com give different figures, and what was decided about each. Only recorded facts.
   Fetched on demand, by this view or by a player page; when it cannot be fetched the player page just
   shows no marker and the totals stay as they were.
   ============================================================ */
let DQ=null, DQ_IDX=null, DISPUTE_IDX=null, DISPUTED_IDS=null, DQ_T=null, DQ_SORT={sort:0,dir:1}, DQ_FILTER={q:'',season:''};
async function ensureDQ(fresh){
  if(DQ) return DQ;
  const d=await DATA.get('index/data_quality.json',fresh);
  if(!d || !Array.isArray(d.conflicts)) return null;
  DQ=d; DQ_IDX=new Map(); DISPUTE_IDX=new Map(); DISPUTED_IDS=new Set();
  d.conflicts.forEach(c=>{
    const k=c.id+'|'+c.season+'|'+c.franchise_id;
    if(!DQ_IDX.has(k)) DQ_IDX.set(k,[]);
    DQ_IDX.get(k).push(c);
  });
  (d.disputed_rows||[]).forEach(r=>{
    DISPUTED_IDS.add(r.id);
    const k=r.id+'|'+r.season+'|'+r.team;
    if(!DISPUTE_IDX.has(k)) DISPUTE_IDX.set(k,[]);
    DISPUTE_IDX.get(k).push(r);
  });
  return DQ;
}
function buildDQ(){
  const host=$('#dqBox'); if(host) host.innerHTML='<p class="note">Cargando…</p>';
}
async function openDQ(){
  const host=$('#dqBox'); if(!host || host.dataset.ready) return;
  const d=await ensureDQ(host.dataset.tried==='1');   /* a second visit after a miss asks the network again */
  if(!d){
    host.dataset.tried='1';
    host.innerHTML=`<div class="card"><div class="note">No se pudieron cargar los datos de esta vista`
      +`${DATA.base===null?' (hace falta abrir el sitio publicado, no el archivo suelto)':''}. Vuelve a intentarlo más tarde.</div></div>`;
    return;
  }
  host.dataset.ready='1';
  drawDQ(host,d);
}
function drawDQ(host,d){
  const c=d.counts, nf=n=>Number(n).toLocaleString('es-PR');
  const btn=(id,name,season)=>`<button class="btn" style="padding:2px var(--sp-1);font-size:var(--fs-2xs);text-align:left;white-space:normal" `
    +`onclick="openArchivePlayer(${id},${JSON.stringify(name).replace(/"/g,'&quot;')}${season!=null?','+season:''})">${esc(name)}</button>`;
  const gEq=d.conflicts.filter(x=>x.a.games===x.b.games).length;
  const pEq=d.conflicts.filter(x=>x.a.points===x.b.points).length;
  const both=d.conflicts.length-gEq-pEq;
  const mSeasons=Object.keys(c.merged_by_season).map(Number);
  const nMerge=d.decisions.filter(x=>x.kind==='merge').length, nSame=d.decisions.length-nMerge;
  const seasons=Object.keys(c.conflicts_by_season);

  const decisions=d.decisions.map(x=>{
    const [a,b]=x.ids, nm=i=>x.names[String(i)];
    const head = x.kind==='merge'
      ? `Se unieron: ${esc(nm(a===x.survivor_id?b:a))} (ID ${a===x.survivor_id?b:a}) ahora es ${esc(nm(x.survivor_id))} (ID ${x.survivor_id})`
      : `No se unen: ${esc(nm(a))} (ID ${a}) y ${esc(nm(b))} (ID ${b})`;
    const links = x.kind==='merge' ? btn(x.survivor_id,nm(x.survivor_id)) : btn(a,nm(a))+' '+btn(b,nm(b));
    return `<div class="card" style="margin-top:var(--sp-3)">`
      +`<div style="font-weight:700">${head}</div>`
      +`<p style="margin:var(--sp-2) 0 0;line-height:1.5">${esc(x.text_es)}</p>`
      +`<div class="muted" style="font-size:var(--fs-2xs);margin-top:var(--sp-2)">Decidido el ${esc(fmtLongDate(x.decided_at))} · ${links}</div></div>`;
  }).join('');

  host.innerHTML=`
    <div class="strip">
      <div><div class="n">${nf(c.stat_conflicts)}</div><div class="l">cifras distintas entre dos páginas de bsnpr.com, en ${nf(c.stat_conflict_players)} jugadores</div></div>
      <div><div class="n">${nf(c.merged_pairs)}</div><div class="l">filas que las dos páginas dan idénticas, en ${nf(c.merged_players)} jugadores (${Math.min(...mSeasons)}–${Math.max(...mSeasons)})</div></div>
      <div><div class="n">${nf(d.decisions.length)}</div><div class="l">decisiones de identidad registradas: ${nMerge} uniones y ${nSame} «no se unen»</div></div>
      <div><div class="n">${nf(c.dob_open)}</div><div class="l">fechas de nacimiento con dos valores, sin resolver</div></div>
    </div>

    <h4 class="sub">Cifras que no coinciden</h4>
    <p class="lede">Dos páginas archivadas de bsnpr.com traen filas de carrera del mismo jugador, equipo y temporada con juegos (JJ) o puntos (PTS) distintos.
      El archivo guarda las dos filas y muestra las dos cifras. En la ficha del jugador esas filas llevan la marca «2 fuentes» y quedan fuera de los totales.</p>
    <p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">Por temporada: ${seasons.map(y=>`${y} (${nf(c.conflicts_by_season[y])})`).join(' · ')}.
      En ${gEq} coinciden los juegos y difieren los puntos; en ${pEq} coinciden los puntos y difieren los juegos; en ${both} difieren los dos.</p>
    ${c.season_totals?`<p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">En ${nf(c.season_totals)} casos la fila de jug05 es el total de la temporada de un jugador que cambió de equipo. El archivo conserva las filas por equipo y registra el total como corroboración.</p>`:''}
    ${c.relabeled?`<p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">En las capturas de jug05 a partir de mayo de 2006, la temporada más reciente conserva la etiqueta 2005. En 100 de ${nf(c.relabeled)} filas las cifras coinciden con la temporada 2006 de la ficha del jugador. Reasignamos las ${nf(c.relabeled)} a 2006 y publicamos el registro.</p>`:''}
    ${c.foreign_rows?`<p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">En ${nf(c.foreign_rows)} filas de ${nf(new Set((d.foreign_rows||[]).map(x=>x.id)).size)} jugadores, una página de jug05 mostraba la línea de otro jugador. Las quitamos de la ficha y de los totales y publicamos el registro. No podemos detectar los casos cuyo dueño no tiene captura.</p>`:''}
    <div class="filters">
      <div class="field"><label for="dqQ">Jugador</label><input id="dqQ" type="search" placeholder="Buscar por nombre" autocomplete="off"></div>
      <div class="field"><label for="dqS">Temporada</label><select id="dqS"><option value="">Todas</option>${seasons.map(y=>`<option value="${y}">${y}</option>`).join('')}</select></div>
    </div>
    <div id="dqTable" style="margin-top:var(--sp-3)"></div>
    <p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">Cada celda muestra JJ / PTS. <b>Ficha</b> es la página del jugador en bsnpr.com (jugador.asp); <b>jug05</b>, su página de estadísticas (jug05.asp).
      Cada par enlaza a la captura en Internet Archive; en negrita, la cifra que difiere. Las dos columnas se ordenan por PTS.</p>

    <h4 class="sub">Identidades: qué se unió y qué no</h4>
    <p class="lede">Al unir dos IDs, las filas idénticas no se cuentan dos veces: ${nf(c.dropped_rows)} filas del ID retirado eran idénticas a filas del ID que se conserva y quedaron en un registro aparte.
      Un ID retirado sigue abriendo la ficha que se conservó.</p>
    ${decisions}
    <details style="margin-top:var(--sp-3)"><summary class="muted" style="cursor:pointer">Las ${nf(c.merged_pairs)} filas idénticas, por temporada</summary>
      <p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">${mSeasons.map(y=>`${y}: ${nf(c.merged_by_season[y])}`).join(' · ')}.
        Donde las dos páginas coinciden en juegos y puntos, la fila se cuenta una vez.</p></details>

    <h4 class="sub">Fechas de nacimiento</h4>
    <p class="lede">${nf(c.dob_open)} jugadores tienen dos fechas distintas en dos páginas de bsnpr.com. El archivo conserva las dos y no escoge. «Archivo» es el valor que carga el archivo; «jugador05», el de la página jugador05 de bsnpr.com (formato M/D/AAAA).</p>
    <div id="dqDob" style="margin-top:var(--sp-3)"></div>
    <p class="muted" style="font-size:var(--fs-2xs);margin:var(--sp-2) 0 0">Otras ${nf(c.dob_corrections)} fechas ya se corrigieron. En ${nf(c.dob_corrections_high)}, el registro de correcciones cita
      dos páginas de bsnpr.com (jug05 y jugador05) que respaldan la fecha nueva${c.dob_corrections_low?`; en ${nf(c.dob_corrections_low)}, la fecha anterior era imposible y solo jugador05 da una plausible (confianza baja)`:''}.</p>

    <h4 class="sub">Temporadas que no concuerdan con la ficha</h4>
    <p class="lede">${c.disputed_career_rows===1
      ?'1 fila de temporada no es compatible con la fecha de nacimiento en la misma ficha de bsnpr.com. El archivo conserva la fila, pero la excluye de los totales; no sabemos cuál de los dos datos es el correcto.'
      :`${nf(c.disputed_career_rows)} filas de temporada no son compatibles con la fecha de nacimiento en la misma ficha de bsnpr.com. El archivo conserva las filas, pero las excluye de los totales; no sabemos cuál de los dos datos es el correcto.`}</p>
    <div id="dqDisputed" style="margin-top:var(--sp-3)"></div>

    <h4 class="sub">Cómo decidimos</h4>
    <ul style="margin:var(--sp-2) 0 0;padding-left:var(--sp-5);line-height:1.6;max-width:70ch">
      <li>Nunca unimos a dos jugadores solo por el nombre.</li>
      <li>Cuando dos fuentes dan cifras distintas, mostramos las dos; no las promediamos.</li>
      <li>Una unión necesita evidencia y queda registrada con quién la decidió y cuándo.</li>
    </ul>`;

  $('#dqQ').oninput=e=>{ DQ_FILTER.q=e.target.value; drawDQTable(); };
  $('#dqS').onchange=e=>{ DQ_FILTER.season=e.target.value; drawDQTable(); };
  drawDQTable();
  buildTable($('#dqDob'),[
    {label:'Jugador',wide:true,render:(v,r)=>btn(r[3],v)},
    {label:'Archivo'},{label:'jugador05'}
  ],d.dob_open.map(x=>[x.name,x.canonical,x.jugador05,x.id]),
    {file:'bsn_fechas_nacimiento_sin_resolver',sort:0,dir:1,
     csvHead:['ID','Jugador','Valor en el archivo (M/D/AAAA)','Valor en jugador05 (M/D/AAAA)'],csvRow:r=>[r[3],r[0],r[1],r[2]]});
  buildTable($('#dqDisputed'),[
    {label:'Jugador',wide:true,render:(v,r)=>btn(r[5],v)},
    {label:'Año',num:true,render:(v,r)=>`<button style="background:none;border:0;padding:0;font:inherit;color:inherit;text-decoration:underline;cursor:pointer" onclick="openArchivePlayer(${r[5]},${JSON.stringify(r[0]).replace(/"/g,'&quot;')},${v})">${v}</button>`},
    {label:'Equipo'},{label:'JJ',num:true},{label:'PTS',num:true}
  ],d.disputed_rows.map(x=>[x.name,x.season,x.team,x.games,x.points,x.id]),
    {file:'bsn_temporadas_sin_concordar_ficha',sort:1,dir:1,
     csvHead:['ID','Jugador','Temporada','Equipo','JJ','PTS','Captura'],
     csvRow:r=>[r[5],r[0],r[1],r[2],r[3],r[4],d.disputed_rows.find(x=>x.id===r[5]&&x.season===r[1]).url]});
}
function drawDQTable(){
  const host=$('#dqTable'); if(!host||!DQ) return;
  if(DQ_T) DQ_SORT={sort:DQ_T.state.sort,dir:DQ_T.state.dir};   /* a filter change keeps the current sort */
  const q=norm(DQ_FILTER.q||'');
  const list=DQ.conflicts.filter(x=>(!DQ_FILTER.season||String(x.season)===DQ_FILTER.season)&&(!q||norm(x.name).includes(q)));
  /* four columns so it reads at phone width; the cells that hold two figures sort by PTS. A row carries
     what the cells and the CSV need beyond the columns: [name, season, ficha PTS, jug05 PTS, id, team,
     ficha JJ, jug05 JJ, ficha url, jug05 url] */
  const rows=list.map(x=>{
    const ak=FID2APP&&FID2APP[x.franchise_id];
    return [x.name,x.season,x.a.points,x.b.points,x.id,(ak&&F[ak])?F[ak].name:x.a.team,x.a.games,x.b.games,x.a.url,x.b.url];
  });
  const pair=(g,p,og,op,url)=>{
    const one=(v,o)=>v==null?'—':(v!==o?'<b>'+v.toLocaleString('es-PR')+'</b>':v.toLocaleString('es-PR'));
    return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${one(g,og)} / ${one(p,op)}</a>`;
  };
  DQ_T=buildTable(host,[
    {label:'Jugador',wide:true,render:(v,r)=>`<button class="btn" style="padding:2px var(--sp-1);font-size:var(--fs-2xs);text-align:left;white-space:normal" onclick="openArchivePlayer(${r[4]},${JSON.stringify(v).replace(/"/g,'&quot;')})">${esc(v)}</button>`
      +`<div class="muted" style="font-size:var(--fs-3xs);margin-top:var(--sp-1)">${esc(r[5])}</div>`},
    {label:'Año',num:true,render:(v,r)=>`<button style="background:none;border:0;padding:0;font:inherit;color:inherit;text-decoration:underline;cursor:pointer" onclick="openArchivePlayer(${r[4]},${JSON.stringify(r[0]).replace(/"/g,'&quot;')},${v})">${v}</button>`},
    {label:'Ficha',num:true,render:(v,r)=>pair(r[6],v,r[7],r[3],r[8])},
    {label:'jug05',num:true,render:(v,r)=>pair(r[7],v,r[6],r[2],r[9])}
  ],rows,{file:'bsn_cifras_en_conflicto',sort:DQ_SORT.sort,dir:DQ_SORT.dir,
    csvHead:['ID','Jugador','Temporada','Equipo','JJ ficha','PTS ficha','JJ jug05','PTS jug05','Captura ficha','Captura jug05'],
    csvRow:r=>[r[4],r[0],r[1],r[5],r[6],r[2],r[7],r[3],r[8],r[9]],
    note:list.length!==DQ.conflicts.length?`de ${DQ.conflicts.length}`:''});
}
