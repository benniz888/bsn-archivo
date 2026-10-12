// PHASE_67C probe for tests/test_quiz_clues_67c.py. Serves web/ statically, loads #juega in Chromium
// and drives the site's OWN clueList()/newQuiz()/drawQuiz()/guessQuiz() (no re-implementation).
// Prints one JSON document on stdout. Needs playwright-core (PLAYWRIGHT_CORE env = its directory,
// else resolved normally). Never part of what Pages publishes.
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
await page.waitForFunction(() => typeof POOL !== 'undefined' && POOL.length > 0 && typeof clueList === 'function');
await page.waitForTimeout(1500);
const out = await page.evaluate(() => {
  const Q = clueList.Q || (clueList.Q = clueList.init());
  const rows = POOL.map(p => ({ n: p.n, d: p.d, tier: Q.tier(p), L: clueList(p), bio: p.b || null }));
  // draw: 400 rounds through the real newQuiz(); recent is reset first
  ST.del('quiz:recent');
  const draws = [], tiers = { f: 0, m: 0, l: 0 };
  for (let i = 0; i < 400; i++) { newQuiz(); draws.push(QZ.p.n); tiers[Q.tier(QZ.p)]++; }
  const stored = ST.json('quiz:recent');
  // guess behaviour, on a fresh round
  newQuiz(); const ans = QZ.p.n, g0 = QZ.guesses;
  const inp = () => document.querySelector('#qGuess');
  const type = v => { inp().value = v; inp().dispatchEvent(new Event('input')); };
  const res = {};
  type('dal'); guessQuiz();
  res.ambig = { guesses: QZ.guesses, done: QZ.done, open: !document.querySelector('#qSugg').hidden, opts: document.querySelectorAll('#qSugg [role=option]').length, msg: document.querySelector('#qMsg').textContent };
  type('zzzzqq'); guessQuiz();
  res.nomatch = { guesses: QZ.guesses, done: QZ.done, msg: document.querySelector('#qMsg').textContent };
  const other = POOL.find(p => p.n !== ans && p.n.length > 8).n;
  type(other.toUpperCase()); guessQuiz();
  res.wrongFull = { guesses: QZ.guesses, done: QZ.done, msg: document.querySelector('#qMsg').textContent };
  const sub = ans.split(' ').slice(-1)[0].slice(0, 4); // a fragment of the answer: never accepted
  type(sub); guessQuiz();
  res.fragment = { guesses: QZ.guesses, done: QZ.done };
  type(ans.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()); guessQuiz();
  res.exact = { done: QZ.done, msg: document.querySelector('#qMsg').textContent, guessesStart: g0 };
  return { leaders: LEADERS, rows, draws, tiers, stored, res, poolTiers: POOL.reduce((a, p) => (a[Q.tier(p)] = (a[Q.tier(p)] || 0) + 1, a), {}) };
});
out.pageErrors = errors;
process.stdout.write(JSON.stringify(out));
await browser.close(); srv.close();
