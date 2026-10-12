// PHASE_66 probe for tests/test_equipos_phase66.py. Serves web/ statically and, in Chromium AND WebKit at
// 390 and 1000px in dark and light, opens the club page for Santurce, Bayamon and a defunct club (Capitalinos)
// and checks (geometry): no decorative element in the club hero (the title-count bars, the tenure bar, any
// absolutely positioned element or pseudo-element that is not the crest) intersects the INK rectangles of the
// hero text (Range rects). Prints one JSON document. Needs playwright-core (PLAYWRIGHT_CORE = its directory).
import http from 'http'; import fs from 'fs'; import path from 'path';
import { pathToFileURL } from 'url';
const core = process.env.PLAYWRIGHT_CORE;
const pw = await import(core ? pathToFileURL(path.join(core, 'index.js')).href : 'playwright-core');
const P = pw.chromium ? pw : pw.default;
const root = process.env.WEB_ROOT || path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../web');
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(root, p);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d); } });
}).listen(0);
const base = `http://localhost:${srv.address().port}/`;

function measure() {
  const scope = document.querySelector('.eq-page'); if (!scope) return { missing: true };
  const hero = scope.querySelector('.eq-hero'), ten = scope.querySelector('.eq-ten');
  const inCrest = n => !!(n.closest && n.closest('.crest'));
  const decor = [];
  [hero, ten].filter(Boolean).forEach(root => root.querySelectorAll('*').forEach(e => {
    if (inCrest(e)) return;
    const cs = getComputedStyle(e);
    if (e.matches('.phero-spark, .phero-spark *') && e.tagName === 'svg' || e === ten || cs.position === 'absolute' && !e.matches('.eq-ten span')) decor.push(e);
    for (const ps of ['::before', '::after']) { const p = getComputedStyle(e, ps); if (p.content !== 'none' && p.position === 'absolute') decor.push({ pseudo: ps, el: e }); }
  }));
  if (ten) decor.push(ten);
  const textRects = [];
  [hero, scope.querySelector('.eq-ten-l')].filter(Boolean).forEach(root => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.textContent.trim() || inCrest(n.parentElement) || n.parentElement.closest('svg')) continue;
      const r = document.createRange(); r.selectNodeContents(n);
      for (const q of r.getClientRects()) if (q.width > 0 && q.height > 0) textRects.push({ t: n.textContent.trim().slice(0, 24), l: q.left, t0: q.top, r: q.right, b: q.bottom });
    }
  });
  const overlaps = [];
  decor.forEach(d => {
    const el = d.el || d, rect = el.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    textRects.forEach(t => {
      const w = Math.min(rect.right, t.r) - Math.max(rect.left, t.l), h = Math.min(rect.bottom, t.b) - Math.max(rect.top, t.t0);
      if (w > 0.5 && h > 0.5) overlaps.push({ decor: (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) || el.tagName, text: t.t, w: +w.toFixed(1), h: +h.toFixed(1) });
    });
  });
  return { overlaps, decor: decor.length, text: textRects.length };
}

const out = { results: [], errors: [] };
for (const [name, eng] of [['chromium', P.chromium], ['webkit', P.webkit]]) {
  const br = await eng.launch();
  for (const w of [390, 1000]) for (const theme of ['dark', 'light']) {
    const ctx = await br.newContext({ viewport: { width: w, height: 900 }, colorScheme: theme });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error' && !/ERR_NETWORK|Failed to load resource/.test(m.text())) out.errors.push(`${name}/${w}/${theme}: ${m.text()}`); });
    page.on('pageerror', e => out.errors.push(`${name}/${w}/${theme}: ${e.message}`));
    for (const k of ['san', 'bay', 'cap']) {
      await page.goto(base + '#equipos/equipo/' + k, { waitUntil: 'load' });
      await page.waitForSelector('.eq-hero', { timeout: 15000 }); await page.waitForTimeout(600);
      const m = await page.evaluate(measure);
      out.results.push({ cfg: `${name}/${w}/${theme}`, club: k, ...m });
    }
    await ctx.close();
  }
  await br.close();
}
srv.close();
console.log(JSON.stringify(out));
