// PHASE_72C probe for tests/test_phase72c.py. Serves web/ statically and drives the site's own functions
// in Chromium: the curated player search (by the corrected and the original spelling), the 1986 season
// detail, the Premios scoring table, a Líderes table. Prints one JSON document.
import http from 'http'; import fs from 'fs'; import path from 'path';
import { pathToFileURL } from 'url';
const core = process.env.PLAYWRIGHT_CORE;
const pw = await import(core ? pathToFileURL(path.join(core, 'index.js')).href : 'playwright-core');
const chromium = pw.chromium || pw.default.chromium;
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
await page.goto(`http://localhost:${srv.address().port}/#jugadores`);
await page.waitForFunction(() => typeof PALL !== 'undefined' && PALL && PALL.length > 0 && DATA.aka);
await page.waitForTimeout(2000);
const out = await page.evaluate(async () => {
  const res = {};
  buildPlayerIndex();
  const search = q => { const el = document.querySelector('#pq'); el.value = q; PMODE = 'cur'; renderPlayerIndex(); return document.querySelector('#playerIndex').innerText; };
  res.akaKeys = Object.keys(DATA.aka).filter(k => /torres/.test(k));
  res.searchCorrected = search('georgie torres').includes('Georgie Torres');
  res.searchOriginal = search('goergie').includes('Georgie Torres');
  res.searchCaps = search('GOERGIE TORRES').includes('Georgie Torres');
  res.searchNone = search('zzzzqq').includes('Georgie Torres');
  document.querySelector('#pq').value = ''; renderPlayerIndex();
  await loadSeasonExtra(1986);
  res.season1986 = document.querySelector('#seasonExtra').innerText;
  buildScoringTable();
  res.scoringTable = (document.querySelector('#scoringTable') || document.body).innerText;
  LEAD_CAT = 'points'; buildLeaders();
  res.leaders = document.querySelector('#leadTable').innerText.slice(0, 400);
  res.scoring1948 = SCORING.find(s => s[0] === 1948).slice(0, 2);
  res.moralesClubs = POOL.find(p => p.n === 'Mario Morales').c;
  res.cruzClubs = POOL.find(p => p.n === 'Teófilo Cruz').c;
  return res;
});
out.pageErrors = errors;
console.log(JSON.stringify(out));
await browser.close(); srv.close();
