/**
 * useFicheSalineUltimeV12Plus — Hook FETCH V12-SUPRA+ Ω
 * ═════════════════════════════════════════════════════════════════
 * P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_Ω · STEEVE-MAX · 2026-02-19
 * BCE-4X ULTIME ABSOLU · Verrou Phase III maintenu
 *
 * TRIGGER : clic / dblclick sur SALINE SUGGÉRÉE pour ESPÈCE ACTIVE
 *           dans BionicLayersV8 → NutritionPanelOmega
 *
 * Endpoint : POST /api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime
 *
 * Garantie : additif (n'altère pas le payload local bindNutritionToSaline).
 *            Anti-spam : cache mémoire par (saline_id|lat|lng, species, month).
 */
import { useCallback, useEffect, useRef, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;
const CACHE = new Map();

const _key = (saline, species, month) => {
  const id = saline?.id || `${(saline?.lat ?? 0).toFixed(4)}_${(saline?.lng ?? saline?.lon ?? 0).toFixed(4)}`;
  return `${id}|${species}|${month}`;
};

const _resolveSpecies = (s) => {
  const x = (s || 'orignal').toString().toLowerCase();
  if (x === 'tous' || x === 'all' || x === '') return 'orignal';
  return x;
};

const _hourFromDate = () => {
  try { return new Date().getHours(); } catch { return 14; }
};

const _profilFromMonth = (m) => {
  // Doctrine V12+ : rut → male_rut, gestation → femelle_gest, etc.
  if (m === 10 || m === 11) return 'male_rut';
  if (m >= 4 && m <= 6) return 'femelle_lact';
  if (m === 1 || m === 2 || m === 3 || m === 12) return 'femelle_gest';
  return 'moyenne';
};

export function useFicheSalineUltimeV12Plus({ saline, species, month, wind } = {}) {
  const [state, setState] = useState({ data: null, loading: false, error: null });
  const lastKeyRef = useRef(null);

  const reset = useCallback(() => {
    lastKeyRef.current = null;
    setState({ data: null, loading: false, error: null });
  }, []);

  useEffect(() => {
    if (!saline || saline.ok === false) { reset(); return; }
    const sp = _resolveSpecies(species);
    const mo = Number(month) || (new Date().getMonth() + 1);
    const key = _key(saline, sp, mo);
    if (lastKeyRef.current === key) return;
    lastKeyRef.current = key;

    if (CACHE.has(key)) {
      setState({ data: CACHE.get(key), loading: false, error: null });
      return;
    }

    const lat = saline.lat ?? saline.center?.lat;
    const lon = saline.lng ?? saline.lon ?? saline.center?.lng;
    if (lat == null || lon == null) { reset(); return; }

    const ctrl = new AbortController();
    setState({ data: null, loading: true, error: null });

    const body = {
      lat: Number(lat),
      lon: Number(lon),
      species: sp,
      month: mo,
      profil: _profilFromMonth(mo),
      hour: _hourFromDate(),
      wind_deg: Number(wind?.directionDeg ?? wind?.deg ?? 225),
      wind_speed: Number(wind?.speed ?? wind?.kmh ?? 12),
      saline_id: saline.id || null,
      saline_score: Number(saline.attractiveness_score ?? saline.score ?? saline.score_bio_global ?? 70),
      saline_type: saline.type || saline.statut_institutionnel || 'naturelle',
    };

    fetch(`${API}/api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    })
      .then(async (r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const json = await r.json();
        // Anti-502 ZEROCOST Ω : 202 EN_COURS → on garde data=null, loading=true affichable
        if (json && json.status === 'EN_COURS') {
          setState({ data: null, loading: true, error: null, enCours: true });
          return;
        }
        CACHE.set(key, json);
        setState({ data: json, loading: false, error: null });
      })
      .catch((e) => {
        if (e.name === 'AbortError') return;
        setState({ data: null, loading: false, error: e.message || 'V12+ fetch failed' });
      });

    return () => { ctrl.abort(); };
  }, [saline, species, month, wind?.directionDeg, wind?.speed, reset]);

  return { ...state, reset };
}

export default useFicheSalineUltimeV12Plus;
