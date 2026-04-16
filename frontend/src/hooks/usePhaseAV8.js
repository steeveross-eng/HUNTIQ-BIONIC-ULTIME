/**
 * usePhaseAV8 — Hook Phase A V8 (Relocalisation + Salines)
 * =========================================================
 * V8-FRONTEND-PHASE-A-Omega
 * Consomme /api/v8/map/relocalisation et /api/v8/map/salines
 * ZERO dependance V6. Cache 30s. Abort automatique.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const usePhaseAV8 = () => {
  const [relocData, setRelocData] = useState(null);
  const [salinesData, setSalinesData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const cacheRef = useRef(new Map());

  const fetchPhaseA = useCallback(async (lat, lon, species = 'cerf', month, windDeg = 180) => {
    if (!lat || !lon) return;

    const m = month || (new Date().getMonth() + 1);
    const cacheKey = `${lat.toFixed(3)}_${lon.toFixed(3)}_${species}_${m}`;

    const cached = cacheRef.current.get(cacheKey);
    if (cached && Date.now() - cached.ts < 30000) {
      setRelocData(cached.reloc);
      setSalinesData(cached.salines);
      return;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    const signal = abortRef.current.signal;

    setLoading(true);
    setError(null);

    try {
      const [relocRes, salinesRes] = await Promise.all([
        fetch(
          `${API}/api/v8/map/relocalisation?lat=${lat}&lon=${lon}&species=${species}&month=${m}&wind_deg=${windDeg}&radius_m=800&n_candidates=16`,
          { signal }
        ),
        fetch(
          `${API}/api/v8/map/salines?lat=${lat}&lon=${lon}&species=${species}&month=${m}&n_salines=4&min_distance_m=300`,
          { signal }
        ),
      ]);

      if (!relocRes.ok || !salinesRes.ok) {
        setError('Erreur serveur Phase A');
        return;
      }

      const reloc = await relocRes.json();
      const salines = await salinesRes.json();

      setRelocData(reloc);
      setSalinesData(salines);

      cacheRef.current.set(cacheKey, { reloc, salines, ts: Date.now() });
      if (cacheRef.current.size > 20) {
        const firstKey = cacheRef.current.keys().next().value;
        cacheRef.current.delete(firstKey);
      }
    } catch (err) {
      if (err.name === 'AbortError') return;
      console.error('[V8-PHASE-A]', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, []);

  return {
    relocData,
    salinesData,
    loading,
    error,
    fetchPhaseA,
    relocalisations: relocData?.relocalisations || [],
    siteActuel: relocData?.site_actuel || null,
    salines: salinesData?.salines || [],
    relocComputeMs: relocData?.compute_ms || 0,
    salinesComputeMs: salinesData?.compute_ms || 0,
  };
};

export default usePhaseAV8;
