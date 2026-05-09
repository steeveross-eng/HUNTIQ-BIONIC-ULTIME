/**
 * SERVICE WORKER KILLSWITCH — P22C_FIX_BLANK_SCREEN_Ω
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * P22C_FIX · 2026-05-09 · KILLSWITCH AUTO-UNREGISTER
 *
 * MISSION :
 *   Toutes les versions précédentes du SW (notamment v13 avec
 *   skipWaiting + clients.claim) avortaient les requêtes API en cours
 *   pendant le mount de React, provoquant un écran blanc total
 *   sur /mon-territoire-bionic.
 *
 * COMPORTEMENT :
 *   1. Au install → skipWaiting() immédiat
 *   2. Au activate → purge TOUS les caches + unregister() + reload des clients
 *   3. Au fetch → passthrough total (aucune interception)
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY
 * ════════════════════════════════════════════════════════════════════════
 */

const KILLSWITCH_VERSION = 'bce-4x-killswitch-p22c-fix-2026-05-09';

self.addEventListener('install', (event) => {
  console.log('[SW-KILLSWITCH] install · version=' + KILLSWITCH_VERSION);
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW-KILLSWITCH] activate · purging all caches + unregister');
  event.waitUntil((async () => {
    try {
      // Purge ALL caches (no exception)
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => {
        console.log('[SW-KILLSWITCH] purge cache:', k);
        return caches.delete(k);
      }));
      console.log('[SW-KILLSWITCH] all caches purged · count=' + keys.length);

      // Claim clients to deliver this killswitch immediately
      await self.clients.claim();

      // Unregister this SW
      await self.registration.unregister();
      console.log('[SW-KILLSWITCH] self.registration.unregister() OK');

      // Notify all clients to reload (so they no longer have a controller)
      const allClients = await self.clients.matchAll({ type: 'window' });
      for (const c of allClients) {
        try {
          c.postMessage({
            type: 'BCE_4X_KILLSWITCH_DONE',
            ts: Date.now(),
            version: KILLSWITCH_VERSION,
          });
        } catch (_e) { /* no-op */ }
      }
      console.log(
        '[SW-KILLSWITCH] notified ' + allClients.length + ' client(s)');
    } catch (e) {
      console.error('[SW-KILLSWITCH] activate error:', e);
    }
  })());
});

// Fetch handler : passthrough TOTAL (aucune interception)
self.addEventListener('fetch', (_event) => {
  // No event.respondWith() → laisse le navigateur faire le fetch natif
});

// Conserve le handler de purge manuelle pour compat
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'BCE_4X_FORCE_PURGE') {
    event.waitUntil((async () => {
      try {
        const keys = await caches.keys();
        await Promise.all(keys.map((k) => caches.delete(k)));
        await self.registration.unregister();
        console.log('[SW-KILLSWITCH] manual force purge + unregister done');
      } catch (_e) { /* no-op */ }
    })());
  }
});
