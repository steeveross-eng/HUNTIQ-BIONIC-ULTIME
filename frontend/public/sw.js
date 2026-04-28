/**
 * SERVICE WORKER KILLSWITCH — PHASE_DESACTIVATION_TOTALE_SW (2026-04-28)
 * ════════════════════════════════════════════════════════════════════════
 * Ordre Commandant STEEVE-MAX (Articles 1-6) : DÉSACTIVATION TOTALE du SW.
 * Ce fichier remplace le SW v9.2 par un KILLSWITCH AUTO-DÉSINSCRIPTION qui :
 *   - purge TOUS les caches CacheStorage à l'activation,
 *   - s'auto-désinscrit (`registration.unregister()`),
 *   - libère tous les clients (`clients.claim()`) et leur ordonne un reload,
 *   - n'intercepte PLUS aucune requête (aucun fetch handler).
 *
 * Garantie : tout client qui visite l'app pour la 1re fois après ce déploiement
 * verra son SW v9.x se substituer par ce killswitch, qui se suicide. À la
 * visite suivante (post-reload), aucun SW n'est plus actif.
 *
 * BCE-4X ULTIME ABSOLU — TOP-ABSOLU — V30 LOCKED INVIOLÉ
 */

self.addEventListener('install', (event) => {
  console.log('[SW-KILLSWITCH] install — skipWaiting');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW-KILLSWITCH] activate — PURGE TOTALE + UNREGISTER + CLIENTS RELOAD');
  event.waitUntil(
    (async () => {
      // 1) Purge totale CacheStorage
      try {
        const keys = await caches.keys();
        await Promise.all(keys.map((k) => {
          console.log('[SW-KILLSWITCH] caches.delete', k);
          return caches.delete(k);
        }));
      } catch (_e) { /* no-op */ }
      // 2) Auto-désinscription
      try {
        await self.registration.unregister();
        console.log('[SW-KILLSWITCH] self.registration.unregister() OK');
      } catch (_e) { /* no-op */ }
      // 3) Claim + reload tous les clients
      try {
        await self.clients.claim();
        const allClients = await self.clients.matchAll({ includeUncontrolled: true, type: 'window' });
        for (const client of allClients) {
          try {
            client.postMessage({ type: 'SW_KILLSWITCH_DONE', ts: Date.now() });
            // Forcer reload pour libérer le client de tout SW
            if (client.url && 'navigate' in client) {
              await client.navigate(client.url);
            }
          } catch (_e) { /* no-op */ }
        }
      } catch (_e) { /* no-op */ }
      console.log('[SW-KILLSWITCH] mission accomplie — SW désactivé totalement');
    })()
  );
});

// AUCUN fetch handler — toutes les requêtes vont directement au réseau.
// AUCUN message handler — pas de surface d'attaque.
