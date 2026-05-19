/**
 * useZerocostBundle.js — Hook frontend dual-read CDN ZEROCOST → API V20
 * ============================================================
 * P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · 2026-02-XX
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU
 *
 * Stratégie de lecture (par ordre de priorité) :
 *   1. Cache LKG IndexedDB (instant, hors-ligne friendly)
 *   2. CDN ZEROCOST (Cloudflare R2 + Cache, <50ms global)
 *   3. API V20 backend live (fallback dynamique)
 *   4. LKG expiré (>7j) en dernier recours si everything fails
 *
 * Feature flag : process.env.REACT_APP_ZEROCOST_ENABLED === 'true'
 * URL CDN     : process.env.REACT_APP_ZEROCOST_CDN_URL
 *               (par défaut : https://cdn-zerocost.bionichunt.com/v1)
 */

import { useState, useCallback } from 'react';
import { lkgGet, lkgSave } from '../lib/lkgCacheOmega';

const API = process.env.REACT_APP_BACKEND_URL;
const ZEROCOST_ENABLED = process.env.REACT_APP_ZEROCOST_ENABLED === 'true';
const ZEROCOST_CDN_URL = (
  process.env.REACT_APP_ZEROCOST_CDN_URL
  || 'https://cdn-zerocost.bionichunt.com/v1'
).replace(/\/$/, '');

const QUANTIZE_DECIMALS = 4; // ~11m

/**
 * Construit l'URL CDN d'une tuile ZEROCOST.
 *  Pattern : <CDN>/v1/{species}/{lat_q}_{lng_q}/m{MM}_h{HH}.json.gz
 */
export const buildZerocostTileUrl = (species, lat, lng, month, hour) => {
  const latQ = Number(lat).toFixed(QUANTIZE_DECIMALS);
  const lngQ = Number(lng).toFixed(QUANTIZE_DECIMALS);
  const mm = String(month).padStart(2, '0');
  const hh = String(hour).padStart(2, '0');
  return `${ZEROCOST_CDN_URL}/${species}/${latQ}_${lngQ}/m${mm}_h${hh}.json.gz`;
};

/**
 * Trouve le créneau horaire le plus proche (7|14|19) de l'heure courante.
 * Doit matcher le précalcul de zerocost_precompute_shadow.py (HOURS_PILOT).
 */
const _nearestCreneau = (hour) => {
  const creneaux = [7, 14, 19];
  return creneaux.reduce((best, c) => (
    Math.abs(c - hour) < Math.abs(best - hour) ? c : best
  ), creneaux[0]);
};

const _nearestMonth = (month) => {
  // Précalcul couvre : 5 (mai), 9 (sept), 10 (oct), 11 (nov)
  const months = [5, 9, 10, 11];
  return months.reduce((best, m) => (
    Math.abs(m - month) < Math.abs(best - month) ? m : best
  ), months[0]);
};

const useZerocostBundle = () => {
  const [bundleData, setBundleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState(null); // 'LKG' | 'CDN' | 'API' | 'LKG_STALE'

  const fetchBundle = useCallback(async (lat, lng, species = 'chevreuil', month, hour) => {
    if (!lat || !lng) return null;
    setLoading(true);

    const now = new Date();
    const m = _nearestMonth(month || (now.getMonth() + 1));
    const h = _nearestCreneau(hour != null ? hour : now.getHours());

    // ── 1. LKG IndexedDB (priorité absolue, instant) ────────────────────
    try {
      const lkg = await lkgGet(species, lat, lng);
      if (lkg && lkg._lkg && lkg._lkg.age_ms < 60 * 60 * 1000) {
        // LKG frais (<1h) → on sert direct
        setBundleData(lkg);
        setSource('LKG');
        setLoading(false);
        return lkg;
      }
    } catch (e) { /* silent */ }

    // ── 2. CDN ZEROCOST (si feature flag activé) ────────────────────────
    if (ZEROCOST_ENABLED) {
      try {
        const url = buildZerocostTileUrl(species, lat, lng, m, h);
        const res = await fetch(url, { mode: 'cors' });
        if (res.ok) {
          const data = await res.json();
          // Stamp CDN provenance
          data._zerocost = {
            served_from_cdn: true,
            cdn_url: url,
            fetched_at: new Date().toISOString(),
            doctrine: 'P22ΩΩ_ZEROCOST_Ω',
          };
          setBundleData(data);
          setSource('CDN');
          setLoading(false);
          // Update LKG en background
          lkgSave(species, lat, lng, data).catch(() => {});
          return data;
        }
      } catch (e) { /* CDN unavailable, fall through to API */ }
    }

    // ── 3. API V20 backend (fallback dynamique) ─────────────────────────
    try {
      const url = `${API}/api/v20/territoire/bundle?lat=${lat}&lon=${lng}&species=${species}&month=${m}&hour=${h}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data && data.status !== 'DEGRADED') {
          setBundleData(data);
          setSource('API');
          setLoading(false);
          lkgSave(species, lat, lng, data).catch(() => {});
          return data;
        }
      }
    } catch (e) { /* API unavailable */ }

    // ── 4. LKG expiré (>7j) en ultime recours ───────────────────────────
    try {
      const stale = await lkgGet(species, lat, lng);
      if (stale) {
        setBundleData(stale);
        setSource('LKG_STALE');
        setLoading(false);
        return stale;
      }
    } catch (e) { /* silent */ }

    setLoading(false);
    return null;
  }, []);

  return { bundleData, loading, source, fetchBundle, zerocostEnabled: ZEROCOST_ENABLED };
};

export default useZerocostBundle;
