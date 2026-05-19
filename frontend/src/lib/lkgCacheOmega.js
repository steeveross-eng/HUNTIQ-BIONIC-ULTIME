/**
 * lkgCacheOmega.js — Last Known Good Cache (IndexedDB)
 * ============================================================
 * P22ΩΩ_ZEROCOST_PHASE1_SHADOW_ET_LKG_Ω · 2026-02-XX
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU
 *
 * Doctrine : stocker dans IndexedDB le dernier bundle TERRITOIRE Ω valide
 * par (species, lat_quantized, lng_quantized). En cas de DEGRADED ou échec
 * réseau, le frontend sert le LKG pour préserver la continuité UX.
 *
 * LKG QUANTIZATION : lat/lng à 4 décimales (~11m).
 * TTL LKG : 7 jours. MAX_ENTRIES : 200.
 */

const DB_NAME = 'bionic_lkg_omega_v1';
const DB_VERSION = 1;
const STORE_NAME = 'territoire_bundles';
const LKG_TTL_MS = 7 * 24 * 3600 * 1000;
const MAX_ENTRIES = 200;

let _dbPromise = null;

const _openDb = () => {
  if (_dbPromise) return _dbPromise;
  _dbPromise = new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('IndexedDB not available'));
      return;
    }
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'cache_key' });
        store.createIndex('species', 'species', { unique: false });
        store.createIndex('ts', 'ts', { unique: false });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  return _dbPromise;
};

export const buildLkgKey = (species, lat, lng) => {
  const sp = String(species || 'unknown').toLowerCase();
  const latQ = Number(lat).toFixed(4);
  const lngQ = Number(lng).toFixed(4);
  return `${sp}|${latQ}|${lngQ}`;
};

export const lkgSave = async (species, lat, lng, bundleData) => {
  if (!bundleData) return false;
  if (bundleData.status === 'DEGRADED') return false;
  if (bundleData.doctrine === 'P22ΩΩ_NEVER_BLANK_Ω') return false;
  try {
    const db = await _openDb();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const cache_key = buildLkgKey(species, lat, lng);
    store.put({
      cache_key,
      species: String(species || 'unknown').toLowerCase(),
      lat: Number(lat),
      lng: Number(lng),
      bundle: bundleData,
      ts: Date.now(),
      schema: 1,
    });
    await new Promise((resolve, reject) => {
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
    await _gcIfNeeded();
    return true;
  } catch (err) {
    return false;
  }
};

export const lkgGet = async (species, lat, lng) => {
  try {
    const db = await _openDb();
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const cache_key = buildLkgKey(species, lat, lng);
    return await new Promise((resolve, reject) => {
      const req = store.get(cache_key);
      req.onsuccess = () => {
        const entry = req.result;
        if (!entry) return resolve(null);
        if (Date.now() - entry.ts > LKG_TTL_MS) return resolve(null);
        resolve({
          ...entry.bundle,
          _lkg: {
            served_from_lkg: true,
            age_ms: Date.now() - entry.ts,
            saved_at: new Date(entry.ts).toISOString(),
            doctrine: 'P22ΩΩ_LKG_Ω',
          },
        });
      };
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    return null;
  }
};

const _gcIfNeeded = async () => {
  try {
    const db = await _openDb();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const count = await new Promise((resolve, reject) => {
      const r = store.count();
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
    if (count <= MAX_ENTRIES) return;
    const idx = store.index('ts');
    const cursorReq = idx.openCursor();
    const toDelete = count - MAX_ENTRIES;
    let deleted = 0;
    await new Promise((resolve) => {
      cursorReq.onsuccess = (e) => {
        const cursor = e.target.result;
        if (!cursor || deleted >= toDelete) return resolve();
        cursor.delete();
        deleted += 1;
        cursor.continue();
      };
      cursorReq.onerror = () => resolve();
    });
  } catch (err) { /* silent */ }
};

export const lkgStats = async () => {
  try {
    const db = await _openDb();
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const count = await new Promise((resolve, reject) => {
      const r = store.count();
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
    return { db_name: DB_NAME, entries: count, max: MAX_ENTRIES, ttl_ms: LKG_TTL_MS };
  } catch (err) {
    return { error: err.message || String(err) };
  }
};

export const lkgPurge = async () => {
  try {
    const db = await _openDb();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).clear();
    await new Promise((resolve) => { tx.oncomplete = resolve; });
    return true;
  } catch (err) {
    return false;
  }
};

if (typeof window !== 'undefined') {
  window.__BIONIC_LKG_OMEGA__ = { lkgGet, lkgSave, lkgStats, lkgPurge, buildLkgKey };
}
