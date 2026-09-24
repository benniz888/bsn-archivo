/* BSN Archivo — service worker (PHASE_5 5E; PHASE_1_SPLIT added css/js routing).
 *
 * Two caches, no install-time precache (the shell's deployed filenames aren't
 * known here — each is cached on its own first successful request instead):
 *   bsn-shell : the HTML document, plus web/css/*.css and web/js/*.js
 *   bsn-data  : the per-entity JSON under data/
 *
 * Routing (same-origin GET only; everything else passes straight through):
 *   navigation           -> network-first, cache the response, offline falls
 *                           back to the cached shell
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

const SHELL = 'bsn-shell';
const DATA = 'bsn-data';
const KEEP = [SHELL, DATA];

self.addEventListener('install', (e) => {
  self.skipWaiting();
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
  return url.pathname.includes('/css/') || url.pathname.includes('/js/');
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
