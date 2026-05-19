/**
 * usePhaseAV8 — Hook TERRITOIRE-Ω Relocalisation + Salines
 * =========================================================
 *
 * P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES · 2026-05-18 · STEEVE-MAX
 *
 * MIGRATION INSTITUTIONNELLE :
 *   - Ancien : /api/v8/map/relocalisation + /api/v8/map/salines (V8-PHASE-A, 404 depuis 2026-05-12)
 *   - Nouveau : /api/v20/territoire/relocalisation + /api/v20/territoire/salines-placement (Ω)
 *
 * Le nom du hook (`usePhaseAV8`) est conservé pour stabilité d'import frontend.
 * Le comportement extérieur est strictement identique (même shape de retour).
 *
 * Cache 30s · Abort automatique · ZERO dépendance V6.
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
      // P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES — endpoints Ω
      const [relocRes, salinesRes] = await Promise.all([
        fetch(
          `${API}/api/v20/territoire/relocalisation?lat=${lat}&lon=${lon}&species=${species}&month=${m}&wind_deg=${windDeg}&radius_m=800&n_candidates=16`,
          { signal }
        ),
        fetch(
          `${API}/api/v20/territoire/salines-placement?lat=${lat}&lon=${lon}&species=${species}&month=${m}&n_salines=4&min_distance_m=300`,
          { signal }
        ),
      ]);

      if (!relocRes.ok || !salinesRes.ok) {
        setError('Erreur serveur TERRITOIRE-Ω Relocalisation/Salines');
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
      // P22ΩΩ_TERRITOIRE_STABILISATION_TOTALE_Ω · ignore DataCloneError tiers Emergent
      const errMsg = String(err.message || err);
      if (errMsg.includes('DataCloneError') || errMsg.includes('postMessage') || errMsg.includes('could not be cloned')) {
        return;
      }
      console.error('[TERRITOIRE-Ω-RELOC-SALINES]', err);
      setError(errMsg);
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
