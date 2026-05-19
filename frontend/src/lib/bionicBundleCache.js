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
    // P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω · 2026-02-XX
    // TTL adaptatif strict :
    //  - HALT_MASK     : 60s     (bundles avec bio_presence_mask_halt=True)
    //  - ESSENTIEL_T0  : 60s     (bundles dégradés ESSENTIEL — réduit de 3600s
    //                             pour empêcher contamination inter-espèces)
    //  - COMPLET_T0    : 24h
    //  - ENRICHI_TDELTA: 24h     (servi via re-fetch silencieux T+Δ)
    // Capacité 5 000 entrées pour 2 000 membres.
    maxEntries: 5000,
    defaultTtlMs: 60 * 1000, // 60s pour bundles ESSENTIELS (verite stricte)
    essentielTtlMs: 60 * 1000, // P0 — vérité doctrinale stricte
    haltTtlMs: 60 * 1000, // 60s pour bundles mask_halt (purge agressive)
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
  // P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω : TTL strict
  //  - bundle.bio_presence_mask_halt === true → haltTtlMs (60s)
  //  - tier ESSENTIEL_T0                       → essentielTtlMs (60s)
  //  - tier COMPLET_T0 / ENRICHI_TDELTA       → completTtlMs (24h)
  const data = entry.data;
  const isHalt = data && data.bio_presence_mask_halt === true;
  const tier = entry.tier || (data && data.bundle_tier) || 'ESSENTIEL_T0';
  let ttl;
  if (isHalt) {
    ttl = root.haltTtlMs;
  } else if (tier === 'COMPLET_T0' || tier === 'ENRICHI_TDELTA') {
    ttl = root.completTtlMs;
  } else {
    ttl = root.essentielTtlMs;
  }
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
 * P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω :
 * Invalidation explicite d'une cacheKey (utilisée pour purger un bundle
 * mask_halt après sa réception, ou pour reset sur changement d'espèce).
 */
export const bundleCacheDelete = (key) => {
  const root = _root();
  if (!root) return;
  root.store.delete(key);
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

/**
 * P22ΩΩ_TERRITOIRE_TTL_ESSENTIEL_3600S : retourne l'âge en ms d'une entrée cache.
 * Utilisé par useMapBundleV8 pour décider si un re-fetch silencieux T+Δ est
 * encore pertinent (BG_CACHE backend finit en ~50-60s).
 */
export const bundleCacheAge = (key) => {
  const root = _root();
  if (!root) return null;
  const entry = root.store.get(key);
  if (!entry) return null;
  return Date.now() - entry.ts;
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
