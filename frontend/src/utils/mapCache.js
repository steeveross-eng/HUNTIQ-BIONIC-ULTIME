/**
 * MAP-PERF-Omega: Client-side map data cache utility
 * Uses sessionStorage for fast reload (< 200ms)
 */
const CACHE_KEY = 'bionic_map_cache';
const CACHE_TTL = 300000; // 5 minutes

export function getCachedMapData(key) {
  try {
    const raw = sessionStorage.getItem(`${CACHE_KEY}_${key}`);
    if (!raw) return null;
    const entry = JSON.parse(raw);
    if (Date.now() - entry.ts < CACHE_TTL) return entry.data;
    sessionStorage.removeItem(`${CACHE_KEY}_${key}`);
    return null;
  } catch {
    return null;
  }
}

export function setCachedMapData(key, data) {
  try {
    sessionStorage.setItem(`${CACHE_KEY}_${key}`, JSON.stringify({ data, ts: Date.now() }));
  } catch {
    // sessionStorage full — silently fail
  }
}

export function clearMapCache() {
  try {
    Object.keys(sessionStorage).forEach(k => {
      if (k.startsWith(CACHE_KEY)) sessionStorage.removeItem(k);
    });
  } catch {
    // noop
  }
}
