// PHASE_72A probe for tests/test_phase72a.py. Serves web/ statically, loads #archivo in Chromium and
// reads the site's own globals. Prints one JSON document. Needs playwright-core (PLAYWRIGHT_CORE=<dir>).
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
await page.goto(`http://localhost:${srv.address().port}/#archivo/cobertura`);
await page.waitForFunction(() => typeof POOL !== 'undefined' && typeof LAST !== 'undefined' && typeof buildLeaders === 'function');
await page.waitForTimeout(2500);
const out = await page.evaluate(() => {
  const res = {};
  res.last = LAST; res.years = [YEARS[0], YEARS[YEARS.length - 1], YEARS.length];
  res.coverage = COVERAGE.derive().map(c => c.slice());
  res.coverageHtml = document.querySelector('#coverage').textContent;
  LEAD_CAT = 'rebounds'; buildLeaders();
  res.leadersRebounds = document.querySelector('#leadTable').textContent;
  LEAD_CAT = 'points'; buildLeaders();
  res.leadersPoints = document.querySelector('#leadTable').textContent;
  res.records = RECORDS.map(r => r[0]);
  res.piculin = POOL.find(p => p.n === 'José «Piculín» Ortiz').b;
  const eng = /\b(the|and|reached|first|of|came|started|went)\b/i;
  res.englishBios = POOL.filter(p => p.b && eng.test(p.b)).map(p => p.n);
  res.englishRoles = HOF.filter(h => eng.test(h.role)).map(h => h.n);
  res.englishNba = NBA_PLAYERS.filter(r => eng.test(r[1])).map(r => r[0]);
  res.seasonAw = SEASON_AW; res.sa = SEASON_AWARDS.map(r => r[1]);
  res.finYear = (buildFinalsByYear(), FIN_YEAR); res.finLabel = DATASETS.finales.label;
  res.hofButler = HOF.find(h => /Butler/.test(h.n));
  return res;
});
out.pageErrors = errors;
console.log(JSON.stringify(out));
await browser.close(); srv.close();
