/* BSN Archivo — service worker (PHASE_5 5E; PHASE_1_SPLIT added css/js routing;
 * PHASE_61 added the brand-asset precache and bumped the shell cache to v2;
 * PHASE_69 self-hosted the fonts: shell cache v3, the two woff2 files precached, /fonts/ cache-first).
 *
 * Two caches. Install precaches only the small, fixed-name brand files (the
 * header mark, icons, manifest — PRECACHE below); everything else is cached on
 * its own first successful request instead:
 *   bsn-shell-v3 : the HTML document, plus web/css/*.css, web/js/*.js, the
 *                  brand files and the self-hosted fonts
 *   bsn-data  : the per-entity JSON under data/
 *
 * Routing (same-origin GET only; everything else passes straight through):
 *   navigation           -> network-first, cache the response, offline falls
 *                           back to the cached shell
 *   fonts/ paths         -> cache-first (filenames carry the package version, so a
 *                           cached file is never stale)
 *   css/ and js/ paths   -> network-first, cache the response, offline falls
 *                           back to that same file's own cache entry (added
 *                           for PHASE_1_SPLIT: these used to be inline in the
 *                           one document the navigate handler already cached)
 *   data manifest.json   -> network-first (it is the freshness signal), cache
 *                           fallback
 *   other data JSON      -> stale-while-revalidate
 *
 * The page posts {type:'purge-data'} from DATA.syncVersion() when manifest.json's
 * source_digest changes, so the data cache is dropped in lockstep with the
 * page's localStorage cache after a rebuild + redeploy.
 */
'use strict';

// Bump the suffix whenever the shell's markup changes shape: activate() drops every cache not in
// KEEP, so a bump evicts a stale cached document that would otherwise show the old header offline.
const SHELL = 'bsn-shell-v3';
const DATA = 'bsn-data';
const KEEP = [SHELL, DATA];

const PRECACHE = [
  'manifest.webmanifest',
  'favicon.ico',
  'img/brand/logo_mark_64.webp',
  'img/brand/logo_mark_128.webp',
  'img/brand/apple_touch_icon_180.png',
  'img/brand/icon_192.png',
  'img/brand/icon_512.png',
  'img/brand/icon_maskable_512.png',
  'fonts/inter-latin-opsz-normal-5.3.0.woff2',
  'fonts/oswald-latin-wght-normal-5.3.0.woff2',
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  // Best-effort: a missing icon must not block the worker from installing.
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(PRECACHE)).catch((err) => {
    console.warn('BSN sw: brand precache skipped', err);
  }));
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => !KEEP.includes(k)).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'purge-data') {
    e.waitUntil(caches.delete(DATA));
  }
});

function isDataJson(url) {
  return url.pathname.includes('/data/') && url.pathname.endsWith('.json');
}

// PHASE_1_SPLIT: the shell used to be one file, cached only via the navigate handler below.
// Split into web/css/*.css and web/js/*.js means those are now separate same-origin GET requests
// the navigate handler never sees -- without this, they'd get no offline caching at all (a real
// regression from today, where everything is inline in the one document the navigate handler
// already caches). Same strategy as navigation, deliberately: network-first, cache the response,
// fall back to the cache offline. Not stale-while-revalidate (that's the /data/ policy, chosen
// because data changes over time and a visitor tolerates a beat of staleness; a shell asset must
// never silently mismatch the shell that requested it).
function isShellAsset(url) {
  return url.pathname.includes('/css/') || url.pathname.includes('/js/') ||
         url.pathname.includes('/img/brand/') || url.pathname.endsWith('/manifest.webmanifest') ||
         url.pathname.endsWith('/favicon.ico');
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  if (url.origin !== self.location.origin) return;

  // The shell.
  if (req.mode === 'navigate') {
    e.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res && res.ok) (await caches.open(SHELL)).put(req, res.clone());
        return res;
      } catch (_) {
        const cache = await caches.open(SHELL);
        return (await cache.match(req)) || (await cache.match('./')) ||
               Response.error();
      }
    })());
    return;
  }

  // Fonts: the version is in the filename, so a cached copy can never be stale. Cache-first.
  if (url.pathname.includes('/fonts/')) {
    e.respondWith((async () => {
      const cache = await caches.open(SHELL);
      const hit = await cache.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    })());
    return;
  }

  // CSS/JS shell assets — network-first, same shape as the navigate handler above, sharing its
  // cache (they're part of the shell, not data). No fallback to a different file on a miss offline
  // (unlike navigate's fallback to './'): there is no sensible substitute for a specific missing
  // asset, so a true miss is a real error, not silently served wrong.
  if (isShellAsset(url)) {
    e.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res && res.ok) (await caches.open(SHELL)).put(req, res.clone());
        return res;
      } catch (_) {
        const cache = await caches.open(SHELL);
        return (await cache.match(req)) || Response.error();
      }
    })());
    return;
  }

  if (!isDataJson(url)) return;

  // manifest.json — always try the network; it is small and it is what tells
  // the page (and this worker) that the data changed.
  if (url.pathname.endsWith('/manifest.json')) {
    e.respondWith(fetch(req).catch(() => caches.match(req)));
    return;
  }

  // Every other JSON file: serve the cache immediately, refresh behind it.
  e.respondWith((async () => {
    const cache = await caches.open(DATA);
    const cached = await cache.match(req);
    const fresh = fetch(req).then((res) => {
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    }).catch(() => null);
    return cached || (await fresh) ||
           new Response('null', { headers: { 'Content-Type': 'application/json' } });
  })());
});
