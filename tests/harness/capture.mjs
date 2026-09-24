/* PHASE_1_SPLIT STEP 0a/1 harness. Captures, for a set of routes, normalized rendered DOM,
 * a computed-style sample, an accessibility-tree snapshot, console errors and failed requests --
 * in Chromium AND WebKit, at 1000px and 390px. Writes one JSON file per route+engine+width under
 * tests/harness/baseline/ (or --out-dir). Never touches web/; never published.
 *
 * Usage: node capture.mjs <baseUrl> <outDir> [--label=name]
 */
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { chromium, webkit } = require('playwright');

const baseUrl = process.argv[2] || 'http://localhost:8933';
const outDir = process.argv[3] || 'baseline';
const label = (process.argv.find(a => a.startsWith('--label=')) || '--label=snap').split('=')[1];
mkdirSync(outDir, { recursive: true });

const TABS = ['inicio', 'historia', 'jugadores', 'equipos', 'juega', 'archivo'];
const PLAYERS = [
  { id: 721, name: 'Llovet Ayala, Francisco' },
  { id: 152, name: 'Vidot Fernandez, Angelo' },
  { id: 578, name: 'Rivera Lopez, Eliezer' },
  { id: 194, name: 'Arroyo Gonzalez, Antonio' },
  { id: 344, name: 'Travieso Peña, Carmelo' },
];
const STYLE_SELECTORS = ['body', 'nav.tabs', '.card', '.foot', 'a', 'button.btn', 'h1, h2', '.note'];
const STYLE_PROPS = ['color', 'background-color', 'font-size', 'font-family', 'display', 'padding',
  'margin', 'border-radius', 'line-height'];

function normalizeHtml(html) {
  return html.replace(/>\s+</g, '><').replace(/\s+/g, ' ').trim();
}

async function sha256(text) {
  const { createHash } = await import('node:crypto');
  return createHash('sha256').update(text).digest('hex');
}

async function captureRoute(page, routeName, containerSelector, act) {
  const errors = [];
  const failedRequests = [];
  const onErr = e => errors.push('pageerror:' + e.message);
  const onCon = m => { if (m.type() === 'error') errors.push('console:' + m.text()); };
  const onFail = r => failedRequests.push(r.url() + ' :: ' + (r.failure()?.errorText || ''));
  const onResp = r => { if (r.status() >= 400) failedRequests.push(r.url() + ' :: HTTP ' + r.status()); };
  page.on('pageerror', onErr); page.on('console', onCon);
  page.on('requestfailed', onFail); page.on('response', onResp);

  await act();
  await page.waitForTimeout(1200);

  const rawHtml = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    return el ? el.outerHTML : null;
  }, containerSelector);
  const domText = rawHtml ? normalizeHtml(rawHtml) : null;
  const domHash = domText ? await sha256(domText) : null;

  const styles = await page.evaluate(({ selectors, props }) => {
    const out = {};
    selectors.forEach(sel => {
      const el = document.querySelector(sel);
      if (!el) { out[sel] = null; return; }
      const cs = getComputedStyle(el);
      out[sel] = Object.fromEntries(props.map(p => [p, cs.getPropertyValue(p)]));
    });
    return out;
  }, { selectors: STYLE_SELECTORS, props: STYLE_PROPS });

  let a11y = null;
  try { a11y = await page.accessibility.snapshot(); } catch (e) { a11y = { error: String(e) }; }

  page.off('pageerror', onErr); page.off('console', onCon);
  page.off('requestfailed', onFail); page.off('response', onResp);

  return { route: routeName, domHash, domText, styles, a11y, consoleErrors: errors, failedRequests };
}

async function run(engineName, engine, width) {
  const browser = await engine.launch();
  const ctx = await browser.newContext({ viewport: { width, height: 900 } });
  const page = await ctx.newPage();
  // Determinism: the app has at least one Math.random()-seeded preview (the Juega landing view,
  // app/bsn_archivo.html:6826) and date-seeded content (todayStamp()/puzzleNo()). Both must be
  // fixed BEFORE any page script runs, or two captures of the identical code differ from each
  // other (proven directly: two back-to-back captures of unmodified main@27c16a4 gave different
  // #juega content, "SAN" vs "GBO"). A seeded LCG, not a constant, so code that calls
  // Math.random() more than once per render still gets varied-but-reproducible values.
  await page.addInitScript(() => {
    let seed = 42;
    Math.random = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
    const FIXED = new Date('2026-09-24T12:00:00Z').getTime();
    const RealDate = Date;
    class FixedDate extends RealDate {
      constructor(...args) { if (args.length === 0) super(FIXED); else super(...args); }
      static now() { return FIXED; }
    }
    // eslint-disable-next-line no-global-assign
    Date = FixedDate;
  });
  await page.goto(baseUrl + '/index.html#inicio', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const results = [];
  for (const tab of TABS) {
    results.push(await captureRoute(page, `tab:${tab}`, `#${tab}`, async () => {
      await page.evaluate((t) => { location.hash = '#' + t; }, tab);
      await page.waitForTimeout(500);
    }));
  }
  results.push(await captureRoute(page, 'archivo/calidad', '#dqBox', async () => {
    await page.evaluate(() => { location.hash = '#archivo/calidad'; });
    await page.waitForTimeout(500);
    await page.evaluate(() => window.openDQ && window.openDQ());
  }));
  for (const p of PLAYERS) {
    results.push(await captureRoute(page, `player:${p.id}`, '#playerExtra', async () => {
      await page.evaluate(([id, name]) => window.openArchivePlayer(id, name), [p.id, p.name]);
    }));
  }

  await browser.close();

  for (const r of results) {
    const slug = r.route.replace(/[^a-z0-9]+/gi, '-');
    const file = `${outDir}/${slug}__${engineName}__${width}__${label}.json`;
    writeFileSync(file, JSON.stringify(r, null, 2));
  }
  console.log(`[${engineName} ${width}px] captured ${results.length} routes`);
  return results;
}

for (const width of [1000, 390]) {
  await run('chromium', chromium, width);
  await run('webkit', webkit, width);
}
