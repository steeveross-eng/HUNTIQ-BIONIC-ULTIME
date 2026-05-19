/**
 * useBionicScoringV8 — Hook Score V8 National
 * =============================================
 * BCE-4X V8-INTEGRATION-Omega — PHASE 1
 * Appelle /api/v8/national/score (10 composantes)
 * Appelle /api/v8/national/biome-profile (contexte biome)
 * Cache 90s, abort automatique, ZERO fallback V6/V7
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const useBionicScoringV8 = () => {
  const [scoreV8, setScoreV8] = useState(null);
  const [biomeProfile, setBiomeProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const cacheRef = useRef(new Map());

  const fetchScoreV8 = useCallback(async (lat, lon, species = 'cerf', month, hour) => {
    if (!lat || !lon) return null;

    const now = new Date();
    const m = month || (now.getMonth() + 1);
    const h = hour || now.getHours();
    const cacheKey = `${lat.toFixed(3)}_${lon.toFixed(3)}_${species}_${m}_${h}`;

    const cached = cacheRef.current.get(cacheKey);
    if (cached && Date.now() - cached.ts < 90000) {
      setScoreV8(cached.score);
      setBiomeProfile(cached.biome);
      return cached.score;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    setLoading(true);
    setError(null);

    const token = localStorage.getItem('token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
      const [scoreRes, biomeRes] = await Promise.all([
        fetch(
          `${API}/api/v8/national/score?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}`,
          { headers, signal: abortRef.current.signal }
        ),
        fetch(
          `${API}/api/v8/national/biome-profile?lat=${lat}&lon=${lon}&species=${species}`,
          { signal: abortRef.current.signal }
        ),
      ]);

      let scoreData = null;
      let biomeData = null;

      if (scoreRes.ok) {
        scoreData = await scoreRes.json();
        setScoreV8(scoreData);
      }
      if (biomeRes.ok) {
        biomeData = await biomeRes.json();
        setBiomeProfile(biomeData);
      }

      if (scoreData) {
        cacheRef.current.set(cacheKey, { score: scoreData, biome: biomeData, ts: Date.now() });
        if (cacheRef.current.size > 50) {
          const firstKey = cacheRef.current.keys().next().value;
          cacheRef.current.delete(firstKey);
        }
      }

      return scoreData;
    } catch (err) {
      if (err.name === 'AbortError') return null;
      // P22ΩΩ_TERRITOIRE_STABILISATION_TOTALE_Ω · ignore DataCloneError du script tiers Emergent
      const errMsg = String(err.message || err);
      if (errMsg.includes('DataCloneError') || errMsg.includes('postMessage') || errMsg.includes('could not be cloned')) {
        return null;
      }
      setError(errMsg);
      console.error('[V8-SCORE]', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setScoreV8(null);
    setBiomeProfile(null);
    setError(null);
  }, []);

  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  return {
    scoreV8,
    biomeProfile,
    loading,
    error,
    fetchScoreV8,
    reset,
    composite: scoreV8?.score_v8 ?? null,
    prediction: scoreV8?.prediction ?? null,
    detail: scoreV8?.scores_detail ?? null,
    context: scoreV8?.context ?? null,
    weights: scoreV8?.weights ?? null,
    engine: scoreV8?.engine ?? null,
  };
};

export default useBionicScoringV8;
