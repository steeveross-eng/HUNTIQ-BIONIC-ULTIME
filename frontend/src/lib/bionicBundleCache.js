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
    store: new Map(), // key → { data, ts }
    maxEntries: 128,
    defaultTtlMs: 90 * 1000,
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
  if (Date.now() - entry.ts > root.defaultTtlMs) {
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
  root.store.set(key, { data, ts: Date.now() });
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
