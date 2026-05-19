/**
 * useMapBundleV8 — Hook V20-PERFORMANCE-Omega
 * ============================================
 * PHASE-PERFORMANCE-Omega: Consomme /api/v20/territoire/bundle (cache TTL 24h).
 *
 * P22ΩΩ_PRECHARGEMENT_INTELLIGENT 2026-05-14 — utilise le cache GLOBAL window
 * partagé avec IntelligentPreloadWidget.
 *
 * P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER 2026-05-18 — Profil 2-passes :
 *  1. T0 : affiche immédiatement le bundle ESSENTIEL (terrain + meteo +
 *     zones + hotspots + salines + species, sans corridors_vitaux ni affuts détaillés).
 *  2. T+Δ : re-fetch silencieux après 12s pour récupérer le bundle ENRICHI
 *     (le BG_CACHE backend a complété entre-temps). Si la nouvelle réponse
 *     a `bundle_tier === "ENRICHI_TDELTA"` ou `"COMPLET_T0"`, on met à jour
 *     silencieusement la carte sans relancer le squelette.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { buildBundleCacheKey, bundleCacheGet, bundleCacheSet, bundleCacheTier, bundleCacheAge, bundleCacheDelete } from '../lib/bionicBundleCache';

const API = process.env.REACT_APP_BACKEND_URL;

// P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER : délais re-fetch silencieux
const REFETCH_DELAYS_MS = [12000, 25000]; // 12s puis 25s
// P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω · 2026-02-XX
// TTL strict 60s pour ESSENTIEL_T0 (au lieu de 3600s) :
// vérité doctrinale > performance cache. Le re-fetch silencieux T+Δ reste
// pertinent dans la fenêtre 0-60s après l'arrivée du bundle ESSENTIEL_T0.
const REFETCH_AGE_THRESHOLD_MS = 60_000; // 60s

const useMapBundleV8 = () => {
  const [bundleData, setBundleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [bundleTier, setBundleTier] = useState(null); // ESSENTIEL_T0 | ENRICHI_TDELTA | COMPLET_T0
  const abortRef = useRef(null);
  const refetchTimersRef = useRef([]);
  // P22ΩΩ_FULL_PACK_X10_Ω : traque la dernière espèce demandée pour purge stricte
  // entre changements (élimine contamination inter-espèces visuelle).
  const lastSpeciesRef = useRef(null);

  const _clearRefetchTimers = () => {
    refetchTimersRef.current.forEach((t) => clearTimeout(t));
    refetchTimersRef.current = [];
  };

  // Re-fetch silencieux : ne modifie pas le loading state, met à jour
  // bundleData uniquement si le nouveau bundle est de tier supérieur.
  const _silentRefetch = useCallback(async (cacheKey, url) => {
    try {
      const res = await fetch(url);
      if (!res.ok) return null;
      const newTier = res.headers.get('X-Bundle-Tier') || '';
      const data = await res.json();
      const dataTier = data.bundle_tier || newTier || 'ESSENTIEL_T0';
      // Mise à jour SILENCIEUSE uniquement si on monte de tier
      if (dataTier === 'ENRICHI_TDELTA' || dataTier === 'COMPLET_T0') {
        bundleCacheSet(cacheKey, data);
        setBundleData(data);
        setBundleTier(dataTier);
        console.info(`[P22ΩΩ_ESSENTIEL_1WORKER] Silent refetch upgraded bundle → ${dataTier}`);
        return data;
      }
      return null;
    } catch (e) {
      // Silencieux : pas de console.error
      return null;
    }
  }, []);

  const fetchBundle = useCallback(async (lat, lon, species = 'cerf', month, hour, windDeg) => {
    if (!lat || !lon) return null;

    // P22ΩΩ_FULL_PACK_X10_Ω · PURGE STRICTE INTER-ESPÈCES
    // À chaque changement d'espèce, vider bundleData immédiatement pour éviter
    // l'affichage de corridors stale issus de l'espèce précédente.
    if (lastSpeciesRef.current !== species) {
      setBundleData(null);
      setBundleTier(null);
      _clearRefetchTimers();
      lastSpeciesRef.current = species;
    }

    const now = new Date();
    const m = month || (now.getMonth() + 1);
    const h = hour || now.getHours();
    const w = windDeg || 225;
    const cacheKey = buildBundleCacheKey(lat, lon, species, m, h, w);

    // P22ΩΩ — lecture cache LRU GLOBAL window (partagé avec preload widget)
    const cached = bundleCacheGet(cacheKey);
    if (cached) {
      // P22ΩΩ_FULL_PACK_X10_Ω · Invalidation agressive si bundle servi est HALT
      // → on évite de servir 0 corridors qui pourraient être interprétés comme
      // un état figé. Le cache TTL halt 60s + invalidation garantit fraîcheur.
      if (cached.bio_presence_mask_halt === true) {
        // On sert quand même le cache halt (corridors=[] est l'état attendu),
        // mais on invalide l'entrée après lecture pour forcer le re-fetch
        // au prochain accès (vérité MFFP en temps réel).
        bundleCacheDelete(cacheKey);
      }
      setBundleData(cached);
      const cTier = cached.bundle_tier || bundleCacheTier(cacheKey) || 'ESSENTIEL_T0';
      setBundleTier(cTier);
      // P22ΩΩ_FULL_PACK_X10_Ω : ne programmer un re-fetch silencieux T+Δ que si :
      //   - cache est ESSENTIEL_T0 (potentiellement upgradable)
      //   - NON-halt (mask présent = pas de upgrade possible)
      //   - ET l'âge du cache est < 60s
      if (cTier === 'ESSENTIEL_T0' && !cached.bio_presence_mask_halt) {
        const age = bundleCacheAge(cacheKey) || 0;
        if (age < REFETCH_AGE_THRESHOLD_MS) {
          const url = `${API}/api/v20/territoire/bundle?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}&wind_deg=${w}`;
          _clearRefetchTimers();
          REFETCH_DELAYS_MS.forEach((delay) => {
            const t = setTimeout(() => _silentRefetch(cacheKey, url), Math.max(0, delay - age));
            refetchTimersRef.current.push(t);
          });
        } else {
          console.info(`[P22ΩΩ_TTL_60S] Skip re-fetch ESSENTIEL (age=${Math.round(age/1000)}s > ${REFETCH_AGE_THRESHOLD_MS/1000}s)`);
        }
      }
      return cached;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    setLoading(true);
    _clearRefetchTimers();

    // Retry automatique sur 502/504 (cold-start backend V10)
    const RETRY_DELAYS_MS = [2000, 8000];
    const url = `${API}/api/v20/territoire/bundle?lat=${lat}&lon=${lon}&species=${species}&month=${m}&hour=${h}&wind_deg=${w}`;

    for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt += 1) {
      try {
        const res = await fetch(url, { signal: abortRef.current.signal });
        if ((res.status === 502 || res.status === 503 || res.status === 504) && attempt < RETRY_DELAYS_MS.length) {
          console.warn(`[V20-PERFORMANCE] Bundle ${res.status} attempt ${attempt + 1}, retry in ${RETRY_DELAYS_MS[attempt]}ms`);
          // eslint-disable-next-line no-await-in-loop
          await new Promise((r) => setTimeout(r, RETRY_DELAYS_MS[attempt]));
          continue;
        }
        if (!res.ok) {
          setLoading(false);
          return null;
        }
        // eslint-disable-next-line no-await-in-loop
        const data = await res.json();
        const tier = data.bundle_tier || res.headers.get('X-Bundle-Tier') || 'ESSENTIEL_T0';
        // P22ΩΩ_FULL_PACK_X10_Ω : vérité doctrinale stricte
        //  - si bio_presence_mask_halt=True → on force corridors=[] (élimine
        //    tout corridor stale qui aurait pu remonter par contamination)
        //  - cache invalidé après set pour ne pas polluer 60s
        if (data && data.bio_presence_mask_halt === true) {
          data.corridors = [];
        }
        setBundleData(data);
        setBundleTier(tier);
        bundleCacheSet(cacheKey, data);
        if (data && data.bio_presence_mask_halt === true) {
          // Vérité MFFP : invalider immédiatement pour re-fetch au prochain accès
          // (l'entrée est conservée 60s par TTL mais purgée à la lecture).
          // Pas de purge ici pour éviter la double-charge réseau ; le get-side
          // s'en charge.
        }
        setLoading(false);
        // P22ΩΩ_FULL_PACK_X10_Ω : si on a reçu ESSENTIEL_T0 NON-halt, programmer
        // re-fetch silencieux pour récupérer la version ENRICHI_TDELTA après BG_CACHE.
        if (tier === 'ESSENTIEL_T0' && !data.bio_presence_mask_halt) {
          console.info('[P22ΩΩ_FULL_PACK_X10] T0 reçu → programmation re-fetch T+Δ');
          REFETCH_DELAYS_MS.forEach((delay) => {
            const t = setTimeout(() => _silentRefetch(cacheKey, url), delay);
            refetchTimersRef.current.push(t);
          });
        }
        return data;
      } catch (err) {
        if (err.name === 'AbortError') {
          setLoading(false);
          return null;
        }
        // P22ΩΩ_TERRITOIRE_STABILISATION_TOTALE_Ω · 2026-02-XX
        // DataCloneError est lancé par le script tiers Emergent (assets.emergent.sh/scripts/emergent-main.js)
        // qui essaie de postMessage(Request) au parent window — pas notre code.
        // Comme le fetch RÉEL fonctionne et que res.json() a déjà été lu, on ignore
        // ces erreurs silencieusement pour ne plus polluer la console.
        const errMsg = String(err.message || err);
        const isDataCloneError = errMsg.includes('DataCloneError')
          || errMsg.includes('postMessage')
          || errMsg.includes('could not be cloned');
        if (isDataCloneError) {
          // Silent : retry sans warn pollué
          if (attempt < RETRY_DELAYS_MS.length) {
            // eslint-disable-next-line no-await-in-loop
            await new Promise((r) => setTimeout(r, RETRY_DELAYS_MS[attempt]));
            continue;
          }
          setLoading(false);
          return null;
        }
        if (attempt < RETRY_DELAYS_MS.length) {
          console.warn(`[V20-PERFORMANCE] Bundle network error attempt ${attempt + 1}, retry in ${RETRY_DELAYS_MS[attempt]}ms:`, errMsg);
          // eslint-disable-next-line no-await-in-loop
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
  }, [_silentRefetch]);

  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
      _clearRefetchTimers();
    };
  }, []);

  return {
    bundleData,
    loading,
    bundleTier, // 🌟 P22ΩΩ_ESSENTIEL_1WORKER : ESSENTIEL_T0 | ENRICHI_TDELTA | COMPLET_T0
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
