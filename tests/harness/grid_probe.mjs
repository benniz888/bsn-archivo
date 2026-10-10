// PHASE_62 probe for tests/test_cuadricula_exhaustive.py. Serves web/ statically, loads #juega in
// Chromium and drives the site's OWN submitGuess() (not a re-implementation) for every spelling
// of every player. Prints one JSON document on stdout. Needs playwright-core (PLAYWRIGHT_CORE env
// = path to its directory, else resolved normally). Never part of what Pages publishes.
import http from 'http'; import fs from 'fs'; import path from 'path';
import { pathToFileURL } from 'url';
const core = process.env.PLAYWRIGHT_CORE;
const pw = await import(core ? pathToFileURL(path.join(core, 'index.js')).href : 'playwright-core');
const chromium = pw.chromium || pw.default.chromium; // CommonJS package: named export may be absent
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../web');
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(root, p);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d); } });
}).listen(0);
const browser = await chromium.launch();
const page = await browser.newPage();
const errors = []; page.on('pageerror', e => errors.push(String(e)));
await page.goto(`http://localhost:${srv.address().port}/#juega`);
await page.waitForFunction(() => typeof POOL !== 'undefined' && POOL.length > 0 && typeof boardFor === 'function');
await page.waitForTimeout(1500);
const out = await page.evaluate(async () => {
  const strip = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '');
  const variants = n => {
    const v = { exact: n, lower: n.toLowerCase(), upper: n.toUpperCase(), accentless: strip(n) };
    if (/[«"']/.test(n)) {
      v.no_nickname = n.replace(/\s*(«[^»]*»|"[^"]*"|'[^']*')\s*/g, ' ').replace(/\s+/g, ' ').trim();
      v.straight_quotes = n.replace(/[«»]/g, '"');
    }
    if (/\b(Jr|Sr|II|III|IV)\b\.?/.test(n)) {
      v.no_suffix = n.replace(/\s+(Jr|Sr|II|III|IV)\b\.?/, '').trim();
      v.suffix_with_comma = n.replace(/\s+(Jr|Sr)\b\.?/, ', $1.');
    }
    if (/\b[A-Z]\.\s?[A-Z]?\.?/.test(n)) {
      v.dots_removed = n.replace(/\./g, '');
      v.dots_spaced = n.replace(/\.(?=[A-Z])/g, '. ');
    }
    if (/-/.test(n)) v.hyphen_as_space = n.replace(/-/g, ' ');
    v.padded = '  ' + n.replace(/ /g, '  ') + ' ';
    return v;
  };
  // Axes: rows are clubs, columns clubs or categories (exactly what newBoard() can emit).
  const clubs = GRID_CLUBS.map(k => ({ t: 'c', k })), cats = CAT_KEYS.map(k => ({ t: 'a', k }));
  const cells = [];
  for (const r of clubs) for (const c of clubs.concat(cats)) {
    if (r.t === c.t && r.k === c.k) continue;
    cells.push({ r: r.t + ':' + r.k, c: c.t + ':' + c.k, sol: solutions(r, c).map(p => p.n) });
  }
  // Resolve each (player, spelling) once through the real submitGuess, against an empty-solution
  // cell so the result is "which POOL entry did the game pick" (history[-1].name), or null.
  if (!GB) GB = boardFor('daily');
  GMODE = 'practice'; drawBoard();
  const resolveCache = {};
  const resolve = text => {
    if (text in resolveCache) return resolveCache[text];
    GB.used = new Set(); GB.history = []; GB.guesses = 0; GB.sel = [0, 0];
    GB.rows[0] = { t: 'a', k: 'd1980' }; GB.cols[0] = { t: 'a', k: 'd2020' }; // axes with no missing-data case
    GB.sol[0][0] = []; GB.ans[0][0] = null; drawBoard();
    const inp = document.querySelector('#gGuess'); inp.value = text; submitGuess();
    const h = GB.history[GB.history.length - 1];
    return (resolveCache[text] = h ? h.name : null);
  };
  const names = [...new Set(cells.flatMap(c => c.sol))];
  const rows = [];
  for (const n of names) {
    const vs = variants(n);
    for (const [kind, text] of Object.entries(vs)) rows.push({ name: n, kind, text, resolved: resolve(text) });
  }
  const extra = ['Candido Fret', 'Alamo', 'Alamo, Candido Fret', 'Hector Reyes', 'Reyes', 'Hector', 'Zzzz Nobody', 'ab', 'Dalmau', 'Blondet'];
  const probes = extra.map(t => ({ text: t, resolved: resolve(t) }));
  // Rejection text for a player who meets the row club but not the column, and for one with no club data.
  const msgFor = (r, c, name) => {
    GB.used = new Set(); GB.history = []; GB.sel = [0, 0];
    GB.rows[0] = r; GB.cols[0] = c; GB.sol[0][0] = solutions(r, c); GB.ans[0][0] = null; drawBoard();
    GB.guesses = 0; document.querySelector('#gGuess').value = name; submitGuess();
    reasons.lastSpent = GB.guesses;
    return document.querySelector('#gMsg').textContent;
  };
  const reasons = {};
  outer: for (const r of clubs) for (const c of cats) {
    const sol = new Set(solutions(r, c).map(p => p.n));
    const w = POOL.find(p => p.c.includes(r.k) && !axMatch(p, c) && !sol.has(p.n));
    if (w) { reasons.wrong_player = msgFor(r, c, w.n); reasons.wrong_spent = reasons.lastSpent; reasons.failed_axis_label = axFull(c); reasons.passed_axis_label = axFull(r); reasons.sample = w.n; break outer; }
  }
  const nodata = POOL.find(p => !p.c.length);
  if (nodata) { reasons.no_data_text = msgFor(clubs[0], clubs[1], nodata.n); reasons.no_data_spent = reasons.lastSpent; }
  return {
    reasons,
    pool: POOL.map(p => ({ n: p.n, c: p.c, d: p.d, pos: p.pos || null, ppg: p.ppg == null ? null : p.ppg, hi: p.hi || null, ss: p.ss || null, o26: !!p.o26, t: p.t })),
    clubs: GRID_CLUBS, cats: CAT_KEYS, catLabels: Object.fromEntries(CAT_KEYS.map(k => [k, CATS[k][0]])),
    cells, rows, probes,
    fkeys: Object.fromEntries(FKEYS.map(k => [k, F[k].name])),
  };
});
out.pageErrors = errors;
process.stdout.write(JSON.stringify(out));
await browser.close(); srv.close();
