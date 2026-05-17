/**
 * IntelligentPreloadWidget — P22ΩΩ_PRECHARGEMENT_INTELLIGENT_GEOLOCALISATION
 * ============================================================================
 * Widget Premium qui précharge en arrière-plan les bundles TERRITOIRE Ω pour :
 *   - le waypoint favori de l'utilisateur (profil)
 *   - ses 3 espèces préférées (profil)
 *
 * Fonctionne en single-worker (séquentiel, jamais bloquant).
 * Stocke les HIT dans le cache LRU global window (90s TTL).
 * Affiche un état discret en bas-droite de la carte.
 *
 * Doctrine BCE-4X · COMMANDANT STEEVE-MAX · 2026-05-14
 */

import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Brain, Zap, CheckCircle2, Loader2 } from 'lucide-react';
import { useAuth } from '@/components/GlobalAuth';
import { useUserProfile } from '@/modules/onboarding/hooks/useUserProfile';
import {
  buildBundleCacheKey,
  bundleCacheGet,
  bundleCacheSet,
} from '@/lib/bionicBundleCache';

const API = process.env.REACT_APP_BACKEND_URL;

// Espèces canoniques par défaut si l'utilisateur n'a pas configuré ses préférences
const DEFAULT_TOP_SPECIES = ['chevreuil', 'orignal', 'ours_noir'];

// Mappe les IDs d'onboarding vers les codes canoniques backend
const SPECIES_ID_MAP = {
  cerf: 'cerf',
  chevreuil: 'chevreuil',
  cerf_virginie: 'chevreuil',
  white_tailed_deer: 'chevreuil',
  orignal: 'orignal',
  moose: 'orignal',
  ours: 'ours_noir',
  ours_noir: 'ours_noir',
  black_bear: 'ours_noir',
  coyote: 'coyote',
  loup: 'coyote',
  dindon: 'dindon_sauvage',
  dindon_sauvage: 'dindon_sauvage',
  turkey: 'dindon_sauvage',
};

const normalizeSpeciesId = (id) => {
  if (!id) return null;
  const key = String(id).toLowerCase().trim();
  return SPECIES_ID_MAP[key] || key;
};

const isPremiumUser = (user) => {
  if (!user) return false;
  if (user.role === 'admin') return true;
  if (user.premium_tier && String(user.premium_tier).toLowerCase() !== 'free') return true;
  if (user.is_premium === true) return true;
  if (user.tier && String(user.tier).toLowerCase() !== 'free') return true;
  return false;
};

// P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER 2026-05-18 · STEEVE-MAX
// Détecte si l'utilisateur est authentifié (pas Premium-only).
// Le préchargement T0 ESSENTIEL est désormais activé pour TOUS les membres.
const isAuthenticatedUser = (user) => Boolean(user && (user.id || user.email || user.username));

const IntelligentPreloadWidget = ({ favLat, favLon, favSpeciesOverride }) => {
  const { user } = useAuth();
  const { profile } = useUserProfile();

  // P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER : préchargement ouvert à tous les
  // membres authentifiés (Free + Premium). Le widget est toujours affiché
  // s'il y a au moins un user connecté + un waypoint favori.
  const authenticated = useMemo(() => isAuthenticatedUser(user), [user]);
  const premium = useMemo(() => isPremiumUser(user), [user]);

  // 3 espèces préférées (normalisées) — fallback si vide
  const topSpecies = useMemo(() => {
    if (favSpeciesOverride && favSpeciesOverride.length > 0) {
      return favSpeciesOverride.slice(0, 3).map(normalizeSpeciesId).filter(Boolean);
    }
    const raw = (profile?.species || []).map(normalizeSpeciesId).filter(Boolean);
    const unique = [...new Set(raw)];
    return unique.length >= 3 ? unique.slice(0, 3) : [...unique, ...DEFAULT_TOP_SPECIES.filter((s) => !unique.includes(s))].slice(0, 3);
  }, [profile?.species, favSpeciesOverride]);

  const [status, setStatus] = useState('idle'); // idle | running | done | skipped
  const [progress, setProgress] = useState({ done: 0, total: 0, lastSpecies: null });
  const startedRef = useRef(false);

  useEffect(() => {
    // Garde-fous
    if (startedRef.current) return;
    // P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER : si pas authentifié, on skippe
    if (!authenticated) {
      setStatus('skipped');
      return;
    }
    if (!favLat || !favLon) {
      // Waypoint favori manquant — on attend
      return;
    }
    if (!topSpecies || topSpecies.length === 0) {
      setStatus('skipped');
      return;
    }

    startedRef.current = true;
    setStatus('running');
    setProgress({ done: 0, total: topSpecies.length, lastSpecies: null });

    const now = new Date();
    const month = now.getMonth() + 1;
    const hour = now.getHours();
    const windDeg = 225; // valeur frontend par défaut

    let cancelled = false;

    const preloadOne = async (species) => {
      const cacheKey = buildBundleCacheKey(favLat, favLon, species, month, hour, windDeg);
      // Skip si déjà dans le cache local 90s
      if (bundleCacheGet(cacheKey)) {
        return { species, hit: true };
      }
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 12000); // 12s soft cap
        const url = `${API}/api/v20/territoire/bundle?lat=${favLat}&lon=${favLon}&species=${species}&month=${month}&hour=${hour}&wind_deg=${windDeg}`;
        const res = await fetch(url, { signal: controller.signal });
        clearTimeout(timer);
        if (res.ok) {
          const data = await res.json();
          bundleCacheSet(cacheKey, data);
          return { species, hit: true, data };
        }
        // Si 502/504 → backend BG_CACHE va peupler ; on retry une fois dans 6s
        if (res.status === 502 || res.status === 504 || res.status === 503) {
          await new Promise((r) => setTimeout(r, 6000));
          if (cancelled) return { species, hit: false };
          const res2 = await fetch(url, { signal: controller.signal });
          if (res2.ok) {
            const data2 = await res2.json();
            bundleCacheSet(cacheKey, data2);
            return { species, hit: true, data: data2 };
          }
        }
        return { species, hit: false };
      } catch (err) {
        // Soft cap atteint : le backend continue BG_CACHE en arrière-plan
        return { species, hit: false, err: err?.name || 'fetch_error' };
      }
    };

    (async () => {
      for (let i = 0; i < topSpecies.length; i += 1) {
        if (cancelled) return;
        const sp = topSpecies[i];
        setProgress((p) => ({ ...p, lastSpecies: sp }));
        // eslint-disable-next-line no-await-in-loop
        await preloadOne(sp);
        if (cancelled) return;
        setProgress((p) => ({ ...p, done: p.done + 1, lastSpecies: sp }));
        // Pause inter-espèces pour ne pas saturer le single worker
        if (i < topSpecies.length - 1) {
          // eslint-disable-next-line no-await-in-loop
          await new Promise((r) => setTimeout(r, 1500));
        }
      }
      if (!cancelled) setStatus('done');
    })();

    return () => {
      cancelled = true;
    };
  }, [authenticated, favLat, favLon, topSpecies]);

  // Cache l'affichage si non-authentifié
  if (!authenticated || status === 'skipped') return null;

  // Pas encore prêt (attend waypoint favori)
  if (status === 'idle') return null;

  return (
    <div
      data-testid="intelligent-preload-widget"
      className="fixed bottom-4 right-4 z-[1100] pointer-events-none"
      style={{ maxWidth: '320px' }}
    >
      <div
        className={`rounded-2xl border backdrop-blur-md shadow-2xl px-4 py-3 transition-all duration-500 ${
          status === 'done'
            ? 'bg-emerald-950/70 border-emerald-500/40'
            : 'bg-slate-900/75 border-cyan-500/30'
        }`}
        style={{ minWidth: '260px' }}
      >
        <div className="flex items-center gap-2.5">
          <div
            className={`rounded-full p-1.5 flex items-center justify-center ${
              status === 'done' ? 'bg-emerald-500/20' : 'bg-cyan-500/15'
            }`}
          >
            {status === 'running' ? (
              <Loader2 className="w-3.5 h-3.5 text-cyan-300 animate-spin" />
            ) : status === 'done' ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300" />
            ) : (
              <Brain className="w-3.5 h-3.5 text-cyan-300" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <Zap className="w-3 h-3 text-cyan-400" />
              <span
                className="text-[10px] font-bold uppercase tracking-widest text-cyan-300"
                data-testid="intelligent-preload-label"
              >
                {premium ? 'Préchargement intelligent · Premium' : 'Préchargement intelligent'}
              </span>
            </div>
            <div
              className={`text-[11px] mt-0.5 ${
                status === 'done' ? 'text-emerald-200' : 'text-slate-200'
              }`}
              data-testid="intelligent-preload-status"
            >
              {status === 'running'
                ? `T0 ESSENTIEL · ${progress.done}/${progress.total} · ${progress.lastSpecies || '…'}`
                : `0-cold-start prêt · ${progress.done}/${progress.total} espèces`}
            </div>
          </div>
        </div>
        {/* Mini barre de progression */}
        <div className="mt-2 h-0.5 w-full bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-700 ${
              status === 'done' ? 'bg-emerald-400' : 'bg-gradient-to-r from-cyan-400 to-fuchsia-400'
            }`}
            style={{
              width: `${progress.total ? Math.round((progress.done / progress.total) * 100) : 0}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default IntelligentPreloadWidget;
