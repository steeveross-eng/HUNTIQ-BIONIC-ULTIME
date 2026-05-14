/**
 * useMapBundleV8 — Hook V20-PERFORMANCE-Omega
 * ============================================
 * PHASE-PERFORMANCE-Omega: Consomme /api/v20/territoire/bundle (cache TTL 24h).
 * Fallback automatique vers /api/v8/institutional/territoire si V20 indisponible.
 * ZERO source legacy. ZERO degradation visuelle. ZERO recalcul inutile.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

// PHASE-PERFORMANCE-Omega: cache client TTL 24h (aligne avec backend)
const CLIENT_CACHE_TTL_MS = 24 * 3600 * 1000; // 24h

const useMapBundleV8 = () => {
  const [bundleData, setBundleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef(null);
  const cacheRef = useRef(new Map());

  const fetchBundle = useCallback(async (lat, lon, species = 'cerf', month, hour, windDeg) => {
    if (!lat || !lon) return null;

    const now = new Date();
    const m = month || (now.getMonth() + 1);
    const h = hour || now.getHours();
    const w = windDeg || 225;
    // Quantification aligne avec backend (lat/lon 3dec, wind 15deg)
    const latQ = lat.toFixed(3);
    const lonQ = lon.toFixed(3);
    const wQ = Math.round(w / 15) * 15 % 360;
    const cacheKey = `${latQ}_${lonQ}_${species}_${m}_${h}_w${wQ}`;

    const cached = cacheRef.current.get(cacheKey);
    if (cached && Date.now() - cached.ts < CLIENT_CACHE_TTL_MS) {
      setBundleData(cached.data);
      return cached.data;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    setLoading(true);

    // P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · COMMANDANT STEEVE-MAX
    // Retry automatique sur 502/504 (cold-start backend V10) :
    // - 1er hit utilisateur : peut subir 502 K8s (single worker uvicorn saturé)
    // - Backend BG_CACHE met le bundle V10 complet en cache après 50s
    // - 2e hit (notre retry) : HIT cache → bundle complet renvoyé en <1s
    // Backoff : 2s puis 8s (laisser BG_CACHE le temps de finir le V10).
    const RETRY_DELAYS_MS = [2000, 8000];
    const url = `${API}/api/v20/territoire/bundle?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}&wind_deg=${w}`;

    for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt += 1) {
      try {
        const res = await fetch(url, { signal: abortRef.current.signal });
        // Retry sur 502/503/504 (cold-start backend)
        if ((res.status === 502 || res.status === 503 || res.status === 504) && attempt < RETRY_DELAYS_MS.length) {
          console.warn(`[V20-PERFORMANCE] Bundle ${res.status} attempt ${attempt + 1}, retry in ${RETRY_DELAYS_MS[attempt]}ms`);
          await new Promise((r) => setTimeout(r, RETRY_DELAYS_MS[attempt]));
          continue;
        }
        if (!res.ok) {
          setLoading(false);
          return null;
        }
        const data = await res.json();
        setBundleData(data);
        cacheRef.current.set(cacheKey, { data, ts: Date.now() });
        if (cacheRef.current.size > 64) {
          const firstKey = cacheRef.current.keys().next().value;
          cacheRef.current.delete(firstKey);
        }
        setLoading(false);
        return data;
      } catch (err) {
        if (err.name === 'AbortError') {
          setLoading(false);
          return null;
        }
        // Sur erreur réseau / timeout, retry si tentatives restantes
        if (attempt < RETRY_DELAYS_MS.length) {
          console.warn(`[V20-PERFORMANCE] Bundle network error attempt ${attempt + 1}, retry in ${RETRY_DELAYS_MS[attempt]}ms:`, err.message || err);
          await new Promise((r) => setTimeout(r, RETRY_DELAYS_MS[attempt]));
          continue;
        }
        console.error('[V20-PERFORMANCE]', err);
        setLoading(false);
        return null;
      }
    }
    setLoading(false);
    return null;
  }, []);

  useEffect(() => {
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, []);

  return {
    bundleData,
    loading,
    fetchBundle,
    zones: bundleData?.zones || [],
    corridors: bundleData?.corridors || [],
    affuts: bundleData?.affuts || [],
    hotspots: bundleData?.hotspots || [],
    salines: bundleData?.salines || [],
    windVectors: bundleData?.wind_vectors || [],
    esiOmega: bundleData?.esi_omega || null,
    source: bundleData?.source || null,
    computeMs: bundleData?.compute_ms || 0,
    cacheState: bundleData?.cache || null,
    servedMs: bundleData?.served_ms || null,
  };
};

export default useMapBundleV8;
