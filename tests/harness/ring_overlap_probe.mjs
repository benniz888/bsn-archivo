// PHASE_65 probe for tests/test_player_ring_overlap.py. Serves web/ statically and, in Chromium AND
// WebKit at 390 and 1000px in dark and light, measures (geometry, not pixels):
//   - every decorative circle (absolutely positioned circular ::before/::after) in #jugadores against
//     the INK rectangles of the text in its tile (Range rects, not the block box that spans the tile),
//   - that the content is painted above the circle (z-order),
//   - label/number contrast, rendered-DOM emoji on Historia and Jugadores, landing layout, console errors.
// Prints one JSON document on stdout. Needs playwright-core (PLAYWRIGHT_CORE env = its directory).
// Never part of what Pages publishes.
import http from 'http'; import fs from 'fs'; import path from 'path';
import { pathToFileURL } from 'url';
const core = process.env.PLAYWRIGHT_CORE;
const pw = await import(core ? pathToFileURL(path.join(core, 'index.js')).href : 'playwright-core');
const P = pw.chromium ? pw : pw.default;
// WEB_ROOT lets a caller point the probe at another copy of web/ (used once to prove the test fails on the pre-fix CSS).
const root = process.env.WEB_ROOT || path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../web');
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/json', '.svg': 'image/svg+xml' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(root, p);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d); } });
}).listen(0);
const base = `http://localhost:${srv.address().port}/`;

// Runs in the page. Returns one measurement per decorated tile.
function measureTiles() {
  const EMOJI = /\p{Emoji_Presentation}|[\u{1F000}-\u{1FAFF}]|️|‍|⃣/u;
  const lum = ([r, g, b]) => { const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const rgba = s => { const m = s.match(/[\d.]+/g).map(Number); return { c: m.slice(0, 3), a: m.length > 3 ? m[3] : 1 }; };
  const bgOf = el => { // composite ancestors' backgrounds, nearest first
    const layers = [];
    for (let n = el; n; n = n.parentElement) { const c = rgba(getComputedStyle(n).backgroundColor); if (c.a > 0) layers.push(c); if (c.a === 1) break; }
    let base = [255, 255, 255]; for (const l of layers.reverse()) base = base.map((v, i) => v * (1 - l.a) + l.c[i] * l.a); return base;
  };
  const contrast = el => { const t = rgba(getComputedStyle(el).color), bg = bgOf(el);
    const fg = t.c.map((v, i) => v * t.a + bg[i] * (1 - t.a)); const a = lum(fg), b = lum(bg); return (Math.max(a, b) + .05) / (Math.min(a, b) + .05); };
  const out = [];
  document.querySelectorAll('#jugadores .strip>div, #jugadores .pcard, #jugadores .rec-card').forEach(tile => {
    const tr = tile.getBoundingClientRect(); if (!tr.width) return;
    const circles = [];
    for (const pseudo of ['::before', '::after']) {
      const cs = getComputedStyle(tile, pseudo);
      if (cs.content === 'none' || cs.position !== 'absolute') continue;
      const w = parseFloat(cs.width), h = parseFloat(cs.height); if (!(w > 0 && h > 0)) continue;
      const radius = parseFloat(cs.borderTopLeftRadius); if (!(radius >= Math.min(w, h) / 2 || cs.borderTopLeftRadius.includes('%'))) continue; // circular only
      const bw = parseFloat(cs.borderTopWidth) || 0, d = cs.boxSizing === 'border-box' ? w : w + 2 * bw;
      const left = parseFloat(cs.left), top = parseFloat(cs.top);
      circles.push({ pseudo, cx: tr.left + tile.clientLeft + left + d / 2, cy: tr.top + tile.clientTop + top + d / 2, r: d / 2,
        z: cs.zIndex === 'auto' ? 0 : Number(cs.zIndex) });
    }
    const isRec = tile.classList.contains('rec-card');
    if (!circles.length && !isRec) return; // record cards are always measured: they hold the long notes
    const clip = { l: tr.left + tile.clientLeft, t: tr.top + tile.clientTop, r: tr.right - tile.clientLeft, b: tr.bottom - tile.clientTop };
    const ink = []; const walker = document.createTreeWalker(tile, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (!n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const rc of rg.getClientRects()) if (rc.width && rc.height) ink.push({ text: n.textContent.trim().slice(0, 30), l: rc.left, t: rc.top, r: rc.right, b: rc.bottom, el: n.parentElement });
    }
    const hits = [], zfail = [];
    for (const c of circles) for (const k of ink) {
      const l = Math.max(k.l, clip.l), t = Math.max(k.t, clip.t), r = Math.min(k.r, clip.r), b = Math.min(k.b, clip.b);
      if (r <= l || b <= t) continue;
      const nx = Math.max(l, Math.min(c.cx, r)), ny = Math.max(t, Math.min(c.cy, b));
      const dist = Math.hypot(nx - c.cx, ny - c.cy);
      if (dist < c.r) hits.push({ pseudo: c.pseudo, text: k.text, overlapPx: +(c.r - dist).toFixed(1) });
      const cs = getComputedStyle(k.el), z = cs.zIndex === 'auto' ? 0 : Number(cs.zIndex);
      if (!(cs.position !== 'static' && z > c.z) && !zfail.some(f => f.text === k.text)) zfail.push({ text: k.text, position: cs.position, z, circleZ: c.z });
    }
    const labels = [...tile.querySelectorAll('.l, .n')].map(e => ({ text: e.textContent.trim().slice(0, 24), ratio: +contrast(e).toFixed(2) }));
    const noteInk = ink.filter(k => k.el.closest('.note')).length;
    out.push({ tile: tile.className || tile.tagName, circles: circles.length, ink: ink.length, noteInk, hits, zfail, labels });
  });
  return out;
}

const results = [], errors = [];
const names = [];
for (const [engName, eng] of [['chromium', P.chromium], ['webkit', P.webkit]]) {
  const browser = await eng.launch();
  for (const width of [390, 1000]) for (const theme of ['dark', 'light']) {
    const ctx = await browser.newContext({ viewport: { width, height: 844 }, colorScheme: theme });
    const page = await ctx.newPage();
    const errs = []; page.on('pageerror', e => errs.push(String(e))); page.on('console', m => m.type() === 'error' && errs.push(m.text()));
    const cfg = `${engName}/${width}/${theme}`;
    await page.goto(base + '#jugadores'); await page.waitForFunction(() => typeof showPlayer === 'function' && typeof PINDEX !== 'undefined', null, { timeout: 20000 });
    await page.evaluate(t => { document.documentElement.dataset.theme = t; }, theme); await page.waitForTimeout(600);
    if (!names.length) { const all = await page.evaluate(() => { buildPlayerIndex(); return PINDEX.map(p => p.name); });
      names.push('Georgie Torres', all[40], all[200]); }
    for (const nm of names) {
      await page.evaluate(n => showPlayer(n), nm); await page.waitForTimeout(900);
      const tiles = await page.evaluate(measureTiles);
      results.push({ cfg, kind: 'player', player: nm, tiles });
    }
    // Récords: the long note text must stay clear of any decoration
    await page.goto(base + '#jugadores/records'); await page.waitForTimeout(1800);
    await page.evaluate(t => { document.documentElement.dataset.theme = t; }, theme);
    results.push({ cfg, kind: 'records', tiles: await page.evaluate(measureTiles) });
    // rendered-DOM emoji + landing layout, Historia and Jugadores
    for (const [view, hash] of [['historia', '#historia'], ['historia-cinta', '#historia/cinta'], ['jugadores', '#jugadores']]) {
      await page.goto(base + hash); await page.waitForTimeout(1800);
      await page.evaluate(t => { document.documentElement.dataset.theme = t; }, theme);
      const info = await page.evaluate(secId => {
        const EMOJI = /\p{Emoji_Presentation}|[\u{1F000}-\u{1FAFF}]|️|‍|⃣/u;
        const sec = document.getElementById(secId);
        const txt = sec ? sec.innerText + ' ' + [...sec.querySelectorAll('[title],[aria-label]')].map(e => (e.title || '') + (e.getAttribute('aria-label') || '')).join(' ') : '';
        const m = txt.match(EMOJI);
        const hdr = document.querySelector('header.top').getBoundingClientRect();
        const h1 = sec && sec.querySelector('h1');
        const card = sec && sec.querySelector('.explore .xcard');
        const tabs = document.querySelector('#bottombar, nav.tabs');
        const tb = tabs && getComputedStyle(tabs).display !== 'none' ? tabs.getBoundingClientRect() : null;
        const xs = sec ? [...sec.querySelectorAll('.explore .xcard')] : [];
        const rects = xs.map(x => x.getBoundingClientRect());
        const rowTops = [...new Set(rects.map(r => Math.round(r.top)))];
        const lastRow = rects.filter(r => Math.round(r.top) === rowTops[rowTops.length - 1]);
        const grid = sec && sec.querySelector('.explore'), head = sec && sec.querySelector('h2.sec');
        const gr = grid && grid.getBoundingClientRect();
        const explore = xs.length ? { n: xs.length, cols: new Set(rects.slice(0, 4).map(r => Math.round(r.left))).size,
          lastRowSpan: +(Math.max(...lastRow.map(r => r.right)) - Math.min(...lastRow.map(r => r.left))).toFixed(1),
          gridWidth: +gr.width.toFixed(1), gap: head ? +(rects[0].top - head.getBoundingClientRect().bottom).toFixed(1) : null,
          icons: xs.map(x => x.querySelector('.ic path') && x.querySelector('.ic path').getAttribute('d')) } : null;
        const kpis = sec ? [...sec.querySelectorAll('.stats3 .stat, #titleStats>div')].filter(e => e.getClientRects().length).length : 0; // visible only
        return { emoji: m ? m[0].codePointAt(0).toString(16) : null, hdrBottom: hdr.bottom, h1Top: h1 ? h1.getBoundingClientRect().top : null,
          cardBottom: card ? card.getBoundingClientRect().bottom : null, tabsTop: tb ? tb.top : innerHeight, vh: innerHeight, kpis, explore };
      }, view.split('-')[0]);
      results.push({ cfg, kind: 'page', view, ...info });
    }
    errors.push(...errs.map(e => `${cfg}: ${e}`));
    await ctx.close();
    if (width === 390) { // touch: Premios must not keep a sticky :hover look after Back to Resumen
      const tctx = await browser.newContext({ viewport: { width, height: 844 }, hasTouch: true, isMobile: true, colorScheme: theme });
      const tp = await tctx.newPage();
      await tp.goto(base + '#historia'); await tp.waitForTimeout(2500);
      await tp.evaluate(t => { document.documentElement.dataset.theme = t; }, theme);
      await tp.locator('#historia .subnav a', { hasText: 'Premios' }).tap(); await tp.waitForTimeout(500);
      await tp.goBack(); await tp.waitForTimeout(900);
      const pills = await tp.evaluate(() => [...document.querySelectorAll('#historia .subnav a')].map(a => { const c = getComputedStyle(a);
        return { text: a.textContent, current: a.getAttribute('aria-current') === 'true', hover: a.matches(':hover'), focusVisible: a.matches(':focus-visible'), border: c.borderTopColor, outline: c.outlineStyle }; }));
      results.push({ cfg, kind: 'subnav', pills });
      await tctx.close();
    }
  }
  await browser.close();
}
srv.close();
console.log(JSON.stringify({ results, errors, players: names }));
