/* BSN Archivo — service worker (PHASE_5 5E).
 *
 * Two caches, no install-time precache (the shell's deployed filename isn't
 * known here — it's cached on the first successful load instead):
 *   bsn-shell : the HTML document
 *   bsn-data  : the per-entity JSON under data/
 *
 * Routing (same-origin GET only; everything else passes straight through):
 *   navigation           -> network-first, cache the response, offline falls
 *                           back to the cached shell
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
