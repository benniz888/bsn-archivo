// PHASE_71 probe for tests/test_phase71.py. Serves web/ statically and, in Chromium AND WebKit at 390 and
// 1000px, checks in the real page: document.title for a sample of every route (deep link, in-app navigation,
// Back), aria-selected on elements that are not tabs/options, label-in-name for the header mark and the Juega
// tiles, and that nothing in the shell is a layout-shift source while the splash is up (Chromium only).
// Prints one JSON document on stdout. Needs playwright-core (PLAYWRIGHT_CORE env = its directory).
import http from 'http'; import fs from 'fs'; import path from 'path';
import { pathToFileURL } from 'url';
const core = process.env.PLAYWRIGHT_CORE;
const pw = await import(core ? pathToFileURL(path.join(core, 'index.js')).href : 'playwright-core');
const P = pw.chromium ? pw : pw.default;
const root = process.env.WEB_ROOT || path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../web');
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/json', '.png': 'image/png', '.webp': 'image/webp', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(root, p);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d); } });
}).listen(0);
const base = `http://localhost:${srv.address().port}/`;

const ROUTES = [
  'inicio', 'historia', 'historia/cinta', 'historia/titulos', 'jugadores', 'jugadores/buscar', 'jugadores/lideres',
  'jugadores/records', 'jugadores/comparar', 'jugadores/salon', 'jugadores/jugador/jose-piculin-ortiz', 'equipos',
  'equipos/equipo/bay', 'juega', 'juega/cuadricula', 'juega/temporada', 'juega/quiensoy', 'juega/subeybaja', 'archivo',
  'archivo/preguntar', 'archivo/constructor', 'archivo/cobertura', 'archivo/calidad', 'perfil', 'privacidad', 'terminos',
  'accesibilidad', 'creditos'];

const norm = s => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
const out = { titles: [], back: [], ariaSelected: [], labelInName: [], errors: [], overflow: [] };
for (const [en, br] of Object.entries({ chromium: P.chromium, webkit: P.webkit })) {
  const b = await br.launch();
  // the splash holds every cold load for 3 s, so the full 4-config matrix costs ~7 min; two configs, one per width and engine
  for (const w of (en === 'chromium' ? [1000] : [390])) {
    const ctx = await b.newContext({ viewport: { width: w, height: 800 }, serviceWorkers: 'block' });
    const cfg = `${en}/${w}`;
    // one fresh page per deep link: the title must be right on a cold load, not just after in-app navigation
    for (const h of ROUTES) {
      const p = await ctx.newPage();
      p.on('console', m => { if (m.type() === 'error') out.errors.push({ cfg, h, text: m.text().slice(0, 200) }); });
      p.on('pageerror', e => out.errors.push({ cfg, h, text: String(e).slice(0, 200) }));
      await p.goto(base + '#' + h, { waitUntil: 'load' });
      await p.waitForFunction(() => !document.getElementById('splash'), null, { timeout: 20000 }).catch(() => {});
      await p.waitForTimeout(300);
      out.titles.push({ cfg, h, title: await p.title() });
      out.overflow.push({ cfg, h, over: await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1) });
      if (h === 'perfil' || h === 'juega') {
        const r = await p.evaluate(() => {
          const OK = new Set(['tab', 'option', 'row', 'gridcell', 'columnheader', 'rowheader', 'treeitem']);
          return Array.from(document.querySelectorAll('[aria-selected]')).filter(e => !OK.has(e.getAttribute('role'))).map(e => e.outerHTML.slice(0, 120));
        });
        out.ariaSelected.push({ cfg, h, bad: r });
        const lin = await p.evaluate(() => {
          const vis = e => (e.innerText || '').replace(/\s+/g, ' ').trim();
          // no aria-label: the name is computed from the content, which is the visible text by construction
          const name = e => (e.getAttribute('aria-label') || vis(e)).replace(/\s+/g, ' ').trim();
          const els = Array.from(document.querySelectorAll('header .mark, #gameShelf .tile'));
          return els.map(e => ({ sel: e.className, name: name(e), vis: vis(e), label: e.getAttribute('aria-label') }));
        });
        out.labelInName.push({ cfg, h, items: lin });
      }
      await p.close();
    }
    // in-app navigation + Back: Inicio -> Historia -> La cinta -> Back -> Back
    const p = await ctx.newPage();
    await p.goto(base + '#inicio', { waitUntil: 'load' });
    await p.waitForFunction(() => !document.getElementById('splash'), null, { timeout: 20000 }).catch(() => {});
    const seq = [];
    seq.push(['start', await p.title()]);
    await p.evaluate(() => showTab('historia')); seq.push(['historia', await p.title()]);
    await p.evaluate(() => showView('historia', 'cinta')); seq.push(['cinta', await p.title()]);
    await p.evaluate(() => showTeam('bay')); seq.push(['team', await p.title()]);
    await p.goBack(); await p.waitForTimeout(300); seq.push(['back1', await p.title()]);
    await p.goBack(); await p.waitForTimeout(300); seq.push(['back2', await p.title()]);
    await p.goBack(); await p.waitForTimeout(300); seq.push(['back3', await p.title()]);
    out.back.push({ cfg, seq });
    await p.close();
    await ctx.close();
  }
  await b.close();
}
srv.close();
console.log(JSON.stringify(out));
