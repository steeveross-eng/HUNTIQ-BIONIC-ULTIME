/**
 * SERVICE WORKER KILLSWITCH (sw-v2 alias) — PHASE_DESACTIVATION_TOTALE_SW.
 * Identique à /sw.js — assure que les clients enregistrés sur /sw-v2.js
 * (via l'ancien serviceWorkerRegistration.js) se désinscrivent eux aussi.
 */
self.addEventListener('install', (event) => { self.skipWaiting(); });
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    } catch (_e) {}
    try { await self.registration.unregister(); } catch (_e) {}
    try {
      await self.clients.claim();
      const cs = await self.clients.matchAll({ includeUncontrolled: true, type: 'window' });
      for (const c of cs) {
        try { if ('navigate' in c) await c.navigate(c.url); } catch (_e) {}
      }
    } catch (_e) {}
  })());
});
