// PHASE_67D2 probe for tests/test_hl_consistency_67d2.py. Loads web/ in Chromium, drives the site's
// OWN newHL() 3000 times and prints the pairs it built plus each set's option rows as JSON.
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
await page.goto(`http://localhost:${srv.address().port}/#juega`);
await page.waitForFunction(() => typeof HL_SETS !== 'undefined' && typeof newHL === 'function');
await page.waitForTimeout(1500);
const out = await page.evaluate(() => {
  const sets = HL_SETS.map(s => ({ label: s.label, rows: s.rows() }));
  const pairs = [];
  for (let i = 0; i < 3000; i++) { newHL(false); pairs.push({ label: HL.set.label, a: HL.a, b: HL.b }); }
  const bad = LEADERS.assists.filter(r => Math.abs(r[4] / r[5] - r[6]) > 0.15).map(r => r[1]);
  return { sets, pairs, bad };
});
out.errors = errors;
console.log(JSON.stringify(out));
await browser.close(); srv.close();
