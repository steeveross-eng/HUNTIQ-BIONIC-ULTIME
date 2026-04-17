/**
 * useMapBundleV8 — Hook V8-INSTITUTIONNEL EXCLUSIF
 * ==================================================
 * PHASE-4B: Consomme EXCLUSIVEMENT /api/v8/institutional/territoire
 * ZERO source legacy. ZERO fallback. ZERO cache externe.
 * ESI-Omega validation integree cote serveur.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

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
    const cacheKey = `${lat.toFixed(3)}_${lon.toFixed(3)}_${species}_${m}_${h}_w${Math.round(w)}`;

    const cached = cacheRef.current.get(cacheKey);
    if (cached && Date.now() - cached.ts < 30000) {
      setBundleData(cached.data);
      return cached.data;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    setLoading(true);

    try {
      // SOURCE UNIQUE V8-INSTITUTIONNEL — ZERO fallback
      const res = await fetch(
        `${API}/api/v8/institutional/territoire?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}&wind_deg=${w}`,
        { signal: abortRef.current.signal }
      );
      if (!res.ok) return null;
      const data = await res.json();
      setBundleData(data);
      cacheRef.current.set(cacheKey, { data, ts: Date.now() });
      if (cacheRef.current.size > 30) {
        const firstKey = cacheRef.current.keys().next().value;
        cacheRef.current.delete(firstKey);
      }
      return data;
    } catch (err) {
      if (err.name === 'AbortError') return null;
      console.error('[V8-INSTITUTIONNEL]', err);
      return null;
    } finally {
      setLoading(false);
    }
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
  };
};

export default useMapBundleV8;
