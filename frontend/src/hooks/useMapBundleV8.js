/**
 * useMapBundleV8 — Hook bundle V8 unique
 * ========================================
 * UI-V8-FORCE-Omega: Consomme EXCLUSIVEMENT /api/v8/map/bundle
 * ZERO source V7. GOVERNANCE-INDEPENDENT.
 * Cache 30s, abort automatique.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const useMapBundleV8 = () => {
  const [bundleData, setBundleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef(null);
  const cacheRef = useRef(new Map());

  const fetchBundle = useCallback(async (lat, lon, species = 'cerf', month, hour) => {
    if (!lat || !lon) return null;

    const now = new Date();
    const m = month || (now.getMonth() + 1);
    const h = hour || now.getHours();
    const cacheKey = `${lat.toFixed(3)}_${lon.toFixed(3)}_${species}_${m}`;

    const cached = cacheRef.current.get(cacheKey);
    if (cached && Date.now() - cached.ts < 30000) {
      setBundleData(cached.data);
      return cached.data;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    setLoading(true);

    try {
      const res = await fetch(
        `${API}/api/v8/map/bundle?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}`,
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
      console.error('[V8-BUNDLE]', err);
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
    exclusion: bundleData?.exclusion || null,
    biome: bundleData?.biome || null,
    governanceMode: bundleData?.governance_mode || 'LOCKED',
    computeMs: bundleData?.compute_ms || 0,
    fromCache: bundleData?.from_cache || false,
  };
};

export default useMapBundleV8;
