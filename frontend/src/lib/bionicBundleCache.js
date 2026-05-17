/**
 * bionicBundleCache · P22ΩΩ_PRECHARGEMENT_INTELLIGENT_GEOLOCALISATION
 * ============================================================
 * Cache LRU GLOBAL (window-level) partagé entre :
 *  - le hook useMapBundleV8 (consommation au rendu carte)
 *  - le widget IntelligentPreloadWidget (préchargement Premium)
 *
 * TTL par défaut : 90 000 ms (90s) — aligné sur le DEGRADED_CACHE backend.
 * Capacité : 128 entrées max (LRU eviction).
 *
 * Doctrine BCE-4X — STEEVE-MAX · 2026-05-14
 */

const GLOBAL_KEY = '__BIONIC_BUNDLE_CACHE_V1';

if (typeof window !== 'undefined' && !window[GLOBAL_KEY]) {
  window[GLOBAL_KEY] = {
    store: new Map(), // key → { data, ts, tier }
    // P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · 2026-05-18 · STEEVE-MAX
    // Capacité 5 000 entrées + TTL 600s adapté pour 2 000 membres
    // (aligné backend _CACHE_ESSENTIEL_TTL_SEC = 600s).
    maxEntries: 5000,
    defaultTtlMs: 600 * 1000, // 10 min pour bundles ESSENTIELS
    essentielTtlMs: 600 * 1000,
    completTtlMs: 24 * 3600 * 1000, // 24h pour bundles COMPLET_T0 / ENRICHI_TDELTA
  };
}

const _root = () => (typeof window !== 'undefined' ? window[GLOBAL_KEY] : null);

/**
 * Construit la clé de cache alignée sur le `_cache_key` backend
 * (lat/lon 3dec, wind quantifié 15°, hour IGNORÉ).
 */
export const buildBundleCacheKey = (lat, lon, species, month, _hour, windDeg) => {
  const latQ = Number(lat).toFixed(3);
  const lonQ = Number(lon).toFixed(3);
  const wQ = (Math.round((Number(windDeg) || 225) / 15) * 15) % 360;
  return `${latQ}_${lonQ}_${species}_${month}_w${wQ}`;
};

export const bundleCacheGet = (key) => {
  const root = _root();
  if (!root) return null;
  const entry = root.store.get(key);
  if (!entry) return null;
  // P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER : TTL adaptatif selon tier
  // - ESSENTIEL_T0 : 600s
  // - COMPLET_T0 / ENRICHI_TDELTA : 24h
  const tier = entry.tier || (entry.data && entry.data.bundle_tier) || 'ESSENTIEL_T0';
  const ttl =
    tier === 'COMPLET_T0' || tier === 'ENRICHI_TDELTA'
      ? root.completTtlMs
      : root.essentielTtlMs;
  if (Date.now() - entry.ts > ttl) {
    root.store.delete(key);
    return null;
  }
  // Marque comme récemment utilisé (réordonne LRU)
  root.store.delete(key);
  root.store.set(key, entry);
  return entry.data;
};

export const bundleCacheSet = (key, data) => {
  const root = _root();
  if (!root) return;
  if (root.store.size >= root.maxEntries) {
    const oldest = root.store.keys().next().value;
    if (oldest !== undefined) root.store.delete(oldest);
  }
  const tier = (data && data.bundle_tier) || 'ESSENTIEL_T0';
  root.store.set(key, { data, ts: Date.now(), tier });
};

/**
 * P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER : indique si le bundle dans le cache est
 * ESSENTIEL_T0 (donc remplaçable par une version enrichie via re-fetch silencieux).
 */
export const bundleCacheTier = (key) => {
  const root = _root();
  if (!root) return null;
  const entry = root.store.get(key);
  if (!entry) return null;
  return entry.tier || (entry.data && entry.data.bundle_tier) || 'ESSENTIEL_T0';
};

export const bundleCacheStats = () => {
  const root = _root();
  if (!root) return { size: 0, max: 0 };
  return {
    size: root.store.size,
    max: root.maxEntries,
    keys: Array.from(root.store.keys()),
  };
};

export const bundleCacheClear = () => {
  const root = _root();
  if (root) root.store.clear();
};
