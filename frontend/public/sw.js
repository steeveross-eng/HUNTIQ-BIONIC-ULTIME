/**
 * SERVICE WORKER CONTROLLED — P20_PHASE4_STABILIZE_TERRITOIRE_OMEGA_Ω
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * P20_PHASE4 · `reactivate_service_worker_controlled: ENABLED`
 *
 * STRATEGY (anti-générique stricte) :
 *   1. NETWORK-ONLY for /api/v30/super-masters/* (no cache, no fallback)
 *   2. NETWORK-ONLY for /admin/bce-4x-premium/*  (no cache, no fallback)
 *   3. CACHE-FIRST for /static/{js,css}/* (versioned chunks, immutable)
 *   4. NETWORK-ONLY for /api/* (other api endpoints)
 *   5. NETWORK-FIRST for HTML (fresh document, fallback cache)
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY
 * ════════════════════════════════════════════════════════════════════════
 */

const CACHE_VERSION = 'bce-4x-omega-v13-p22c-force-reload-2026-05-09';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const HTML_CACHE = `html-${CACHE_VERSION}`;

const NETWORK_ONLY_PATH_PREFIXES = [
  '/api/v30/super-masters/',
  '/admin/bce-4x-premium/',
  '/api/',
];

const STATIC_PATH_PATTERNS = [
  /\/static\/js\/.*\.chunk\.js$/,
  /\/static\/js\/.*\.js$/,
  /\/static\/css\/.*\.css$/,
  /\/static\/media\//,
  /\.woff2?$/,
];

self.addEventListener('install', (event) => {
  console.log('[SW-CONTROLLED] install · version=' + CACHE_VERSION);
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW-CONTROLLED] activate · purge old caches');
  event.waitUntil((async () => {
    // Purge any cache that does NOT belong to current version
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => {
      if (k !== STATIC_CACHE && k !== HTML_CACHE) {
        console.log('[SW-CONTROLLED] purge old cache:', k);
        return caches.delete(k);
      }
      return null;
    }));
    await self.clients.claim();
    console.log(
      '[SW-CONTROLLED] activated · CacheStorage clean · clients claimed');
  })());
});

const isNetworkOnly = (url) =>
  NETWORK_ONLY_PATH_PREFIXES.some((p) => url.pathname.startsWith(p));

const isStaticAsset = (url) =>
  STATIC_PATH_PATTERNS.some((rx) => rx.test(url.pathname));

const isHtmlNav = (request) =>
  request.mode === 'navigate'
  || (request.method === 'GET'
      && request.headers.get('accept')?.includes('text/html'));

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  let url;
  try {
    url = new URL(request.url);
  } catch (_e) {
    return;
  }

  // Skip cross-origin (let the browser handle natively)
  if (url.origin !== self.location.origin) return;

  // 1. NETWORK-ONLY rules — no cache touch
  if (isNetworkOnly(url)) {
    // Default browser fetch (no SW intervention) → respect Cache-Control
    return;
  }

  // 2. Static assets → CACHE-FIRST
  if (isStaticAsset(url)) {
    event.respondWith((async () => {
      try {
        const cached = await caches.match(request);
        if (cached) return cached;
        const network = await fetch(request);
        if (network.ok) {
          const cache = await caches.open(STATIC_CACHE);
          cache.put(request, network.clone()).catch(() => {});
        }
        return network;
      } catch (e) {
        const cached = await caches.match(request);
        if (cached) return cached;
        throw e;
      }
    })());
    return;
  }

  // 3. HTML navigation → NETWORK-FIRST with cache fallback
  if (isHtmlNav(request)) {
    event.respondWith((async () => {
      try {
        const network = await fetch(request);
        if (network.ok) {
          const cache = await caches.open(HTML_CACHE);
          cache.put(request, network.clone()).catch(() => {});
        }
        return network;
      } catch (_e) {
        const cached = await caches.match(request);
        if (cached) return cached;
        throw _e;
      }
    })());
    return;
  }

  // Default: pass-through (no SW intervention)
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'BCE_4X_FORCE_PURGE') {
    event.waitUntil((async () => {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
      console.log('[SW-CONTROLLED] manual force purge complete');
      const allClients = await self.clients.matchAll({ type: 'window' });
      for (const c of allClients) {
        c.postMessage({ type: 'BCE_4X_FORCE_PURGE_DONE', ts: Date.now() });
      }
    })());
  }
});
