/**
 * useInstitutionalV8.js — Hook Institutionnel V8
 * =================================================
 * PHASE-2: Connecte TERRITOIRE aux 24 ENGINES institutionnels
 * Pipelines: geospatial, comportemental, sensoriel, predictif
 * ESI-Omega validation incluse
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const useInstitutionalV8 = () => {
  const [fullData, setFullData] = useState(null);
  const [conformite, setConformite] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const cacheRef = useRef(new Map());

  const fetchInstitutional = useCallback(async (lat, lon, species = 'cerf', month, hour, windDeg = 225) => {
    if (!lat || !lon) return;
    const m = month || (new Date().getMonth() + 1);
    const h = hour || new Date().getHours();
    const cacheKey = `${lat.toFixed(3)}_${lon.toFixed(3)}_${species}_${m}_${h}`;

    const cached = cacheRef.current.get(cacheKey);
    if (cached && Date.now() - cached.ts < 30000) {
      setFullData(cached.full);
      setConformite(cached.conf);
      return;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    const signal = abortRef.current.signal;

    setLoading(true);
    setError(null);

    try {
      const [fullRes, confRes] = await Promise.all([
        fetch(`${API}/api/v8/institutional/full?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}&wind_deg=${windDeg}`, { signal }),
        fetch(`${API}/api/v8/esi/conformite/full?lat=${lat}&lon=${lon}&species=${species}`, { signal }),
      ]);

      if (!fullRes.ok || !confRes.ok) {
        setError('Erreur serveur V8 Institutionnel');
        return;
      }

      const full = await fullRes.json();
      const conf = await confRes.json();
      setFullData(full);
      setConformite(conf);

      cacheRef.current.set(cacheKey, { full, conf, ts: Date.now() });
      if (cacheRef.current.size > 10) {
        const firstKey = cacheRef.current.keys().next().value;
        cacheRef.current.delete(firstKey);
      }
    } catch (err) {
      if (err.name === 'AbortError') return;
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, []);

  return {
    fullData,
    conformite,
    loading,
    error,
    fetchInstitutional,
    scoreGlobal: fullData?.prediction_intelligence?.score_global,
    classification: fullData?.prediction_intelligence?.classification,
    isConforme: conformite?.conformite_globale === 'CONFORME',
  };
};

export default useInstitutionalV8;
