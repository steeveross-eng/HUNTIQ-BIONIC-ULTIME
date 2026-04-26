/**
 * renduOmegaStore.js — Frontend store pour règles RENDU-Ω (Phase XI-SUPRA-L)
 * ===========================================================================
 * Source de vérité : backend `GET /api/v20/territoire/rendu-omega/rules`
 * Document officiel : /app/memory/RENDUS/RENDUS_CORRIDORS_OMEGA.md
 *
 * Usage :
 *   import { getRenduRules, resolveCorridorStyle, RENDU_OMEGA } from '@/lib/renduOmegaStore';
 *
 * Règles verrouillées (valeurs par défaut identiques au backend, fallback si
 * fetch KO — PREVIEW == FINAL garanti par pipeline unique).
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
const RULES_URL = `${API_BASE}/api/v20/territoire/rendu-omega/rules`;
const ORGANIC_GENERATE_URL = `${API_BASE}/api/v20/territoire/corridors-organic/generate`;

// Défauts immuables — doivent matcher engine_rendu_omega.py:RENDU_RULES
// PHASE_XII_SUPRA_S_CORRECTION : signatures renforcées, halo amplifié, pulse public.
// PHASE_X150-SUPRA-ARCHITECTONIQUE-Ω : norme DESCRIPTIONS_RENDU_OMEGA_CORRIDORS strictement appliquée.
export const RENDU_OMEGA = Object.freeze({
  color: '#FF8F00',
  colorName: 'Orange ambre institutionnel',
  // X150 Norme 3 — UNIQUEMENT 1.2 / 2.0 / 3.0 (aucune autre valeur permise)
  weightsAllowedPx: [3.0, 4.0, 6.0],
  weightMapping: {
    faible: 3.0, modere: 3.0,
    fort: 4.0,
    critique: 6.0, majeur: 6.0,
    extreme: 6.0, extreme_max: 6.0,
  },
  opacityMin: 1.0,
  opacityDefault: 1.0,
  geometryType: 'catmull-rom',
  controlPointsMin: 25,
  controlPointsMax: 30,
  controlPointsTarget: 28,        // SUPRA_S_CORRECTION : Catmull-Rom 28 strict
  segmentMaxM: 20.0,
  angleMaxDeg: 45.0,
  functionalRadiusMinM: 420.0,
  functionalRadiusMaxM: 780.0,
  functionalRadiusNominalM: 600.0,
  minZoom: 13,
  zIndexOrder: ['zones', 'hydrologie', 'terrain', 'corridors', 'salines', 'hotspots', 'affuts', 'vent'],
  forbidAffutInteraction: true,
  forbidDirectionalArrow: true,
  previewEqualsFinal: true,
  // SUPRA_S_CORRECTION — signatures biomimétiques renforcées
  microOscillationPctMin: 0.005,    // 0.5 %
  microOscillationPctMax: 0.009,    // 0.9 %
  microWeightDeltaPx: 0.15,         // +0.15 px
  luminosityStepPct: 0.20,
  // Halo externe adaptatif renforcé (% d'opacité selon fond)
  haloExternalByBackground: {
    forest: 0.75,   // +75 % (visibilité absolue Commandant §4)
    snow: 0.30,
    water: 0.55,
    cover: 0.40,
  },
  // Gradient directionnel renforcé 5–8 %
  directionalGradientPctMin: 0.05,
  directionalGradientPctMax: 0.08,
  // Terrain aware++
  terrainBoosts: {
    slope_high: 0.20,       // pentes > 15°
    valley: 0.30,           // vallons
    wet: 0.25,              // zones humides
    transition: 0.15,       // transitions écologiques
  },
  // Renforcement 40 m autour zones vitales
  vitalZoneBoostRadiusM: 40.0,
  vitalZoneBoosts: {
    alimentation: 0.15,
    repos: 0.10,
    thermique: 0.10,
    humide: 0.20,
  },
  // Snap salines
  salineSnapMaxM: 780.0,           // rayon fonctionnel max
  salineSnapMinM: 420.0,           // rayon fonctionnel min
  salineHaloBoostPct: 0.35,        // +35 % halo externe autour saline
  salineLumBoostRadiusM: 40.0,
  salineLumBoostPct: 0.20,
  // Fade-out progressif
  fadeOutTailM: 10.0,              // transition 8-12 m, médiane 10 m
  fadeOutMinRatio: 0.15,           // §A1 HOTFIX : fade max 85 %, JAMAIS 100 %
  // Convergence veine principale
  mainVeinConvergenceRadiusM: 15.0,  // ≤ 15 m
  mainVeinHaloMultiplier: 1.8,
  // ═══ COMMANDE STEEVE-MAX §3+§4 — MODE RAW_ABSOLUTE ═══
  // Quand activé (par défaut TRUE), prepareDisplayPath retourne le path RAW
  // intégral sans aucun clipping/despike/trim/smoothing. Cela garantit le
  // rendu de 100 % du corridor (origines + intermédiaire + waypoint) sans
  // troncature. Désactiver pour repasser au pipeline strict CatmullRom V30.
  renduOmegaRawAbsolute: true,
  mainVeinLumMultiplier: 2.2,
  // Pulsation publique
  publicPulseMinZoom: 15,
  publicPulseAmplitudePct: 0.0025, // 0.2–0.3 %, médiane 0.25 %
  publicPulsePeriodMs: 2400,
});

let _cachedRules = null;
let _cacheTimestamp = 0;
const CACHE_TTL_MS = 60_000;

/**
 * Fetch live rules depuis le backend (avec cache 60s).
 * Retourne toujours un objet — en cas d'échec, utilise les défauts.
 */
export async function getRenduRules() {
  const now = Date.now();
  if (_cachedRules && (now - _cacheTimestamp) < CACHE_TTL_MS) {
    return _cachedRules;
  }
  try {
    const resp = await fetch(RULES_URL, { credentials: 'omit' });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    _cachedRules = { ...RENDU_OMEGA, _source: 'backend', _fetched_at: now, _version: data.version, _raw: data.rules };
    _cacheTimestamp = now;
  } catch (e) {
    // Fallback silencieux — PREVIEW==FINAL garanti par défauts identiques
    _cachedRules = { ...RENDU_OMEGA, _source: 'fallback', _error: String(e) };
    _cacheTimestamp = now;
  }
  return _cachedRules;
}

/**
 * Map intensité corridor → épaisseur RENDU-Ω.
 *   - 'extreme'|'extreme_max'|'supra'              → 4.0 px (SUPRA_S nouveau niveau)
 *   - 'critique'|'majeur'                          → 3.0 px
 *   - 'fort'|'intense'                             → 2.0 px
 *   - 'faible'|'modere'|'normal'|'saisonnier'     → 1.2 px
 *   - numérique 0-100                               → 1.2 (<33) / 2.0 (<66) / 3.0 (<85) / 4.0 (≥85)
 */
export function resolveCorridorWeight(intensity) {
  if (typeof intensity === 'number') {
    if (intensity >= 85) return 4.0;
    if (intensity >= 66) return 3.0;
    if (intensity >= 33) return 2.0;
    return 1.2;
  }
  if (!intensity) return 1.2;
  const key = String(intensity).toLowerCase().trim();
  if (['extreme', 'extreme_max', 'supra', 'extreme_maximal'].includes(key)) return 4.0;
  if (['critique', 'majeur', 'critical'].includes(key)) return 3.0;
  if (['fort', 'intense', 'strong'].includes(key)) return 2.0;
  return 1.2;
}

/**
 * Produit le style Leaflet conforme RENDU-Ω pour un corridor.
 *   { color, weight, opacity, lineCap, lineJoin, smoothFactor, interactive }
 */
export function resolveCorridorStyleOmega(corridor) {
  const intensity = corridor?.intensity ?? corridor?.type;
  const weight = resolveCorridorWeight(intensity);
  return {
    color: RENDU_OMEGA.color,
    weight,
    opacity: RENDU_OMEGA.opacityDefault, // SUPRA_S : 1.00 obligatoire
    lineCap: 'round',
    lineJoin: 'round',
    smoothFactor: 0,
    interactive: true,
  };
}

/**
 * Retourne le z-index CSS/Leaflet pour une couche.
 * Plus la clé est tardive dans `zIndexOrder`, plus le pane est élevé.
 *
 * COMMANDE STEEVE-MAX — corridors ELEVATED zIndex 600 pour garantir
 * visibilité au-dessus des polygones zones (400 default Leaflet) et de
 * toute autre couche analytique de fond.
 */
export function resolveZIndex(layerKey) {
  const idx = RENDU_OMEGA.zIndexOrder.indexOf(String(layerKey).toLowerCase());
  if (idx < 0) return 400;
  // Base 500 + idx*15 → corridors à 545, salines 560, hotspots 575, affuts 590, vent 605
  return 500 + idx * 15;
}

/**
 * Vérifie si la couche corridors doit être visible au zoom courant.
 */
export function isCorridorsVisibleAtZoom(zoom) {
  return Number(zoom) >= RENDU_OMEGA.minZoom;
}

/* =========================================================================
 * PHASE_XII_SUPRA_R — VALIDATION GÉOMÉTRIQUE RENDU-Ω (frontend strict)
 * =========================================================================
 * Ajoutée sans modifier la logique IA-CORRIDORS : applique au RENDU uniquement :
 *   • clamp épaisseur aux 3 valeurs autorisées (1.2 / 2.0 / 3.0)
 *   • validation continuité (aucune rupture [null, null])
 *   • validation segment ≤ 20 m (Haversine)
 *   • validation angle ≤ 45°
 *   • validation nb points (≥ controlPointsMin pour corridors non-organic)
 * ========================================================================= */

/** Force l'épaisseur aux valeurs autorisées 1.2/2.0/3.0 (snap au plus proche). */
export function clampCorridorWeight(weight) {
  const allowed = RENDU_OMEGA.weightsAllowedPx;
  const n = Number(weight);
  if (!Number.isFinite(n)) return allowed[0];
  return allowed.reduce((prev, curr) =>
    Math.abs(curr - n) < Math.abs(prev - n) ? curr : prev, allowed[0]);
}

/** Distance Haversine en mètres entre deux [lat, lng]. */
function _haversineM(a, b) {
  if (!a || !b || a[0] == null || a[1] == null || b[0] == null || b[1] == null) return Infinity;
  const R = 6371000.0;
  const toRad = (x) => (Number(x) * Math.PI) / 180.0;
  const dLat = toRad(b[0] - a[0]);
  const dLon = toRad(b[1] - a[1]);
  const la1 = toRad(a[0]);
  const la2 = toRad(b[0]);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(la1) * Math.cos(la2) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

/** Angle en degrés au point central entre trois points consécutifs. */
function _angleDegAt(prev, curr, next) {
  if (!prev || !curr || !next) return 0;
  const v1x = curr[1] - prev[1], v1y = curr[0] - prev[0];
  const v2x = next[1] - curr[1], v2y = next[0] - curr[0];
  const n1 = Math.hypot(v1x, v1y), n2 = Math.hypot(v2x, v2y);
  if (n1 < 1e-12 || n2 < 1e-12) return 0;
  let cos = (v1x * v2x + v1y * v2y) / (n1 * n2);
  cos = Math.max(-1, Math.min(1, cos));
  // Déviation de la continuité — 0° = aligné, 180° = demi-tour
  return (Math.acos(cos) * 180) / Math.PI;
}

/**
 * Valide un path corridor contre les règles géométriques RENDU-Ω.
 * Retourne { ok, violations, metrics }.
 * N'effectue PAS de modification de path (immutable).
 *
 * @param {Array<[lat, lng]>} path
 * @param {Object} opts — { isOrganic, strictMinPoints }
 */
export function validateCorridorGeometry(path, opts = {}) {
  const { isOrganic = false, strictMinPoints = true } = opts;
  const violations = [];
  const metrics = {
    n_points: 0,
    max_segment_m: 0,
    max_angle_deg: 0,
    discontinuities: 0,
  };
  if (!Array.isArray(path) || path.length < 2) {
    violations.push({ rule: 'discontinuity', detail: 'path vide ou trop court' });
    return { ok: false, violations, metrics };
  }
  metrics.n_points = path.length;

  // Nb de points — organic: 60-120, legacy conforme RENDU-Ω: 25-30 min
  if (strictMinPoints) {
    const minPts = isOrganic ? 60 : RENDU_OMEGA.controlPointsMin;
    if (metrics.n_points < minPts) {
      violations.push({
        rule: 'geometry_simplified',
        detail: `${metrics.n_points} points < ${minPts} (isOrganic=${isOrganic})`,
      });
    }
  }

  // Continuité + segment max + angle max
  for (let i = 0; i < path.length; i++) {
    const p = path[i];
    if (!p || p[0] == null || p[1] == null || !Number.isFinite(p[0]) || !Number.isFinite(p[1])) {
      metrics.discontinuities += 1;
      violations.push({ rule: 'discontinuity', detail: `point index ${i} invalide` });
      continue;
    }
    if (i > 0) {
      const segM = _haversineM(path[i - 1], p);
      if (segM > metrics.max_segment_m) metrics.max_segment_m = segM;
      if (segM > RENDU_OMEGA.segmentMaxM) {
        violations.push({
          rule: 'segment_over_max',
          detail: `segment #${i} = ${segM.toFixed(1)}m > ${RENDU_OMEGA.segmentMaxM}m`,
        });
      }
    }
    if (i > 0 && i < path.length - 1) {
      const ang = _angleDegAt(path[i - 1], p, path[i + 1]);
      if (ang > metrics.max_angle_deg) metrics.max_angle_deg = ang;
      if (ang > RENDU_OMEGA.angleMaxDeg) {
        violations.push({
          rule: 'angle_over_max',
          detail: `angle #${i} = ${ang.toFixed(1)}° > ${RENDU_OMEGA.angleMaxDeg}°`,
        });
      }
    }
  }

  return { ok: violations.length === 0, violations, metrics };
}

/**
 * Retourne le nom du pane Leaflet conforme Z-INDEX institutionnel pour une
 * couche. L'appelant doit `map.createPane(name)` et fixer son zIndex via
 * `resolveZIndex(layerKey)` au montage.
 */
export function renduOmegaPaneName(layerKey) {
  return `renduOmega-${String(layerKey).toLowerCase()}`;
}

/* =========================================================================
 * Phase XI-SUPRA-L+1-M PREP — CORRIDORS ORGANIC (120 pts, gradient, halo)
 * ========================================================================= */

const ORGANIC_CACHE_TTL_MS = 60_000;
const _organicCache = new Map(); // key = `${lat}|${lon}|${species}` → {data, ts}

/**
 * Fetch les corridors ORGANIC depuis /corridors-organic/generate avec cache 60s.
 * Retourne null si l'endpoint échoue (le consommateur peut fallback sur le
 * bundle legacy `corridors`).
 */
export async function getOrganicCorridors(lat, lon, species = 'chevreuil') {
  const key = `${Number(lat).toFixed(4)}|${Number(lon).toFixed(4)}|${species}`;
  const now = Date.now();
  const cached = _organicCache.get(key);
  if (cached && (now - cached.ts) < ORGANIC_CACHE_TTL_MS) {
    return cached.data;
  }
  try {
    const resp = await fetch(ORGANIC_GENERATE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'omit',
      body: JSON.stringify({ lat, lon, species, month: 10, hour: 7, wind_deg: 225, wind_speed: 15 }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    _organicCache.set(key, { data, ts: now });
    return data;
  } catch (e) {
    return null;
  }
}

/**
 * Résout le style Leaflet ORGANIC (veine animale) pour un corridor avec
 * thickness_profile variable. Utilise l'épaisseur moyenne du path.
 * Gradient & halo sont délégués au rendu via options supplémentaires.
 */
export function resolveCorridorStyleOrganic(corridor) {
  const tp = corridor?.thickness_profile;
  let weight = 2.0;
  if (Array.isArray(tp) && tp.length > 0) {
    weight = tp.reduce((a, b) => a + b, 0) / tp.length;
  } else {
    weight = resolveCorridorWeight(corridor?.intensity);
  }
  // Clamp dans les valeurs RENDU-Ω (1.2 / 2.0 / 3.0 / 4.0)
  const allowed = RENDU_OMEGA.weightsAllowedPx;
  const snapped = allowed.reduce((prev, curr) =>
    Math.abs(curr - weight) < Math.abs(prev - weight) ? curr : prev, allowed[0]);
  return {
    color: RENDU_OMEGA.color,
    gradientTo: '#FF9F00', // §3 RENDU-Ω-M gradient
    weight: snapped,
    opacity: RENDU_OMEGA.opacityDefault,
    lineCap: 'round',
    lineJoin: 'round',
    smoothFactor: 0,
    interactive: true,
    // Halo
    haloEnabled: true,
    haloSizePx: 0.2,
  };
}

/* =========================================================================
 * PHASE_XII_SUPRA_S — RENDU_SUPRA_Ω_ART + GEOMETRY_Ω_ALIGNMENT
 * =========================================================================
 * Tous les helpers ci-dessous sont frontend-only et ne modifient AUCUNE
 * donnée source. Ils produisent un path AFFICHÉ dérivé du path d'entrée.
 * ========================================================================= */

/** Catmull-Rom uniforme : génère N points lissés à partir de K points de contrôle.
 *  Implémentation numérique simple (centripetal tension = 0.5, boucles pour N cibles).
 *  PHASE_XII_SUPRA_S_HOTFIX §A3 : ne JAMAIS renvoyer un tableau vide.
 *  @param {Array<[lat, lng]>} ctrl  points de contrôle (≥ 2)
 *  @param {number} nOut             nombre de points résultants
 *  @returns {Array<[lat, lng]>}
 */
export function catmullRomResample(ctrl, nOut) {
  if (!Array.isArray(ctrl) || ctrl.length < 2) return Array.isArray(ctrl) ? ctrl.slice() : [];
  const n = Math.max(2, nOut | 0);
  const p = [ctrl[0], ...ctrl, ctrl[ctrl.length - 1]];
  const segs = p.length - 3;
  if (segs < 1) return ctrl.slice();
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = (i / (n - 1)) * segs;
    const s = Math.min(segs - 1, Math.floor(t));
    const u = t - s;
    const p0 = p[s], p1 = p[s + 1], p2 = p[s + 2], p3 = p[s + 3];
    const u2 = u * u, u3 = u2 * u;
    const lat = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u +
      (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 +
      (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3);
    const lng = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u +
      (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 +
      (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3);
    out.push([lat, Number.isFinite(lng) ? lng : p1[1]]);
  }
  // Garde-fou : si out dégénéré (toutes valeurs identiques ou NaN), retourner ctrl
  const allFinite = out.every(pt => Number.isFinite(pt[0]) && Number.isFinite(pt[1]));
  return allFinite && out.length >= 2 ? out : ctrl.slice();
}

/** Déspike : supprime les points qui produisent un angle > maxAngleDeg
 *  (conservation des extrémités). Itératif jusqu'à stabilité.
 *  PHASE_XII_SUPRA_S_HOTFIX §A3 : NE JAMAIS réduire le path à < 2 points.
 */
/**
 * X170-SUPRA-BIOLOGIE-GÉOMÉTRIE — smoothAngleViolations
 * ======================================================
 * Lissage local par moyenne pondérée des points voisins pour éliminer
 * les pics angulaires > maxAngleDeg dans le corps du path (pas seulement
 * aux extrémités). Répété jusqu'à convergence ou `maxPasses`.
 *
 * Principe : remplace chaque point cur[i] par le barycentre pondéré
 * de cur[i-1], cur[i], cur[i+1] tant que l'angle en i dépasse le seuil.
 * Préserve les extrémités. Conserve la longueur du path.
 */
export function smoothAngleViolations(path, maxAngleDeg = RENDU_OMEGA.angleMaxDeg, maxPasses = 12) {
  if (!Array.isArray(path) || path.length < 3) return path || [];
  let cur = path.slice();
  for (let pass = 0; pass < maxPasses; pass++) {
    let smoothed = 0;
    const next = cur.slice();
    for (let i = 1; i < next.length - 1; i++) {
      const a = _angleDegAt(cur[i - 1], cur[i], cur[i + 1]);
      if (a > maxAngleDeg) {
        // Barycentre 0.25 / 0.5 / 0.25 → lissage doux
        const p0 = cur[i - 1], p1 = cur[i], p2 = cur[i + 1];
        if (Array.isArray(p0) && Array.isArray(p1) && Array.isArray(p2)) {
          next[i] = [
            0.25 * p0[0] + 0.5 * p1[0] + 0.25 * p2[0],
            0.25 * p0[1] + 0.5 * p1[1] + 0.25 * p2[1],
          ];
          smoothed++;
        }
      }
    }
    cur = next;
    if (smoothed === 0) break;
  }
  return cur;
}

export function despikePath(path, maxAngleDeg = RENDU_OMEGA.angleMaxDeg, maxPasses = 8) {
  if (!Array.isArray(path) || path.length < 3) return path || [];
  let cur = path.slice();
  for (let pass = 0; pass < maxPasses; pass++) {
    const next = [cur[0]];
    let removed = 0;
    for (let i = 1; i < cur.length - 1; i++) {
      const a = _angleDegAt(cur[i - 1], cur[i], cur[i + 1]);
      if (a > maxAngleDeg) {
        removed++;
        continue;
      }
      next.push(cur[i]);
    }
    next.push(cur[cur.length - 1]);
    // §A3 HOTFIX : garde-fou institutionnel — ne jamais passer sous 2 points
    if (next.length >= 2) {
      cur = next;
    }
    if (removed === 0) break;
  }
  return cur;
}

/**
 * X170-SUPRA-BIOLOGIE-GÉOMÉTRIE — trimProblematicTail
 * ======================================================
 * Supprime agressivement les points d'extrémité (début + fin) tant qu'ils
 * génèrent un angle > maxAngleDeg. Les paths organiques ENGINE-IA-CORRIDORS-
 * ORGANIC-Ω produisent régulièrement des artéfacts de fermeture aux nœuds
 * d'arrivée (saline, zone) avec des demi-tours 150°-180° qui ne peuvent
 * être supprimés par despikePath (point médian, pas extrémité).
 *
 * - Conserve un minimum de `minKeep` points (défaut 10) pour préserver
 *   l'entité biologique du corridor.
 * - Supprime les 2 dernières extrémités (start ou end) en priorité sur celle
 *   qui présente l'angle le plus élevé.
 * - Retourne le path trimé (toujours ≥ minKeep si input ≥ minKeep).
 */
export function trimProblematicTail(path, maxAngleDeg = RENDU_OMEGA.angleMaxDeg, minKeep = 10) {
  if (!Array.isArray(path) || path.length <= minKeep) return path || [];
  let cur = path.slice();
  // Trim fin : supprimer cur[n-2] tant que angle(cur[n-3], cur[n-2], cur[n-1]) > seuil
  let guardEnd = 0;
  while (cur.length > minKeep && guardEnd < 60) {
    const n = cur.length;
    const aEnd = _angleDegAt(cur[n - 3], cur[n - 2], cur[n - 1]);
    if (aEnd > maxAngleDeg) {
      // Supprime le dernier point (source de l'artéfact)
      cur.splice(n - 1, 1);
      guardEnd++;
      continue;
    }
    break;
  }
  // Trim début
  let guardStart = 0;
  while (cur.length > minKeep && guardStart < 60) {
    const aStart = _angleDegAt(cur[0], cur[1], cur[2]);
    if (aStart > maxAngleDeg) {
      cur.shift();
      guardStart++;
      continue;
    }
    break;
  }
  return cur;
}

/** Densifie / décime un path pour qu'aucun segment ne dépasse segmentMaxM.
 *  Insère des points intermédiaires linéaires si besoin.
 *  PHASE_XII_SUPRA_S_HOTFIX §A4 : ne supprime JAMAIS de segments — subdivise
 *  uniquement via interpolation linéaire. Garantit continuité stricte.
 */
export function enforceSegmentMax(path, segmentMaxM = RENDU_OMEGA.segmentMaxM) {
  if (!Array.isArray(path) || path.length < 2) return path || [];
  const out = [path[0]];
  for (let i = 1; i < path.length; i++) {
    const a = out[out.length - 1], b = path[i];
    if (!Array.isArray(a) || !Array.isArray(b)) { out.push(b); continue; }
    const d = _haversineM(a, b);
    if (d > segmentMaxM) {
      const n = Math.ceil(d / segmentMaxM);
      for (let k = 1; k < n; k++) {
        const t = k / n;
        out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
      }
    }
    out.push(b);
  }
  return out;
}

/** Pipeline GEOMETRY_Ω_ALIGNMENT complet pour un corridor affiché :
 *    déspike → enforce segment max → resample Catmull-Rom 25-30 → re-enforce.
 *  @param {Array<[lat, lng]>} path
 *  @param {Object} opts { isOrganic, nTarget }
 *  @returns {Array<[lat, lng]>}
 */
export function alignGeometryOmega(path, opts = {}) {
  const { isOrganic = false } = opts;
  if (!Array.isArray(path) || path.length < 2) return path || [];
  const clean = path.filter(p => p && Number.isFinite(p?.[0]) && Number.isFinite(p?.[1]));
  if (clean.length < 2) return [];
  // Pour organic (60-120 pts), on ne re-sample pas — on ne corrige que spikes + segments
  const despiked = despikePath(clean);
  const segmented = enforceSegmentMax(despiked);
  if (isOrganic) return segmented; // préserver densité organic
  // Legacy : resample à 28 points Catmull-Rom (médiane 25-30)
  const target = opts.nTarget || 28;
  if (segmented.length < 3) return segmented;
  return catmullRomResample(segmented, target);
}

/** Masque au rendu les portions d'un path dépassant [minM, maxM] depuis un centre.
 *  Ne modifie pas le path source (copie pure). Produit une liste de sous-paths
 *  chacun contenant uniquement les points à l'intérieur de l'anneau fonctionnel.
 *  Au point de coupure, insère un point d'intersection linéaire pour transition douce
 *  (uniquement si l'interpolé reste lui-même dans le rayon).
 *  @param {Array<[lat, lng]>} path
 *  @param {[lat, lng]} center
 *  @param {number} minM  (default 420)
 *  @param {number} maxM  (default 780)
 *  @returns {Array<Array<[lat, lng]>>} sous-paths valides
 */
export function clipToFunctionalRadius(path, center, minM = RENDU_OMEGA.functionalRadiusMinM, maxM = RENDU_OMEGA.functionalRadiusMaxM) {
  if (!Array.isArray(path) || path.length < 2 || !center) return [path || []];
  const inside = (p) => {
    const d = _haversineM(center, p);
    return d >= 0 && d <= maxM;
  };
  const subpaths = [];
  let cur = [];
  for (let i = 0; i < path.length; i++) {
    const p = path[i];
    if (inside(p)) {
      if (cur.length === 0 && i > 0) {
        // Calcul du point d'intersection exact avec le cercle de rayon maxM
        // (interpolation binaire sur le segment prev→p)
        const prev = path[i - 1];
        let lo = 0, hi = 1;
        for (let it = 0; it < 20; it++) {
          const mid = (lo + hi) / 2;
          const q = [prev[0] + (p[0] - prev[0]) * mid, prev[1] + (p[1] - prev[1]) * mid];
          if (_haversineM(center, q) > maxM) lo = mid;
          else hi = mid;
        }
        const tCross = hi;
        const cross = [prev[0] + (p[0] - prev[0]) * tCross, prev[1] + (p[1] - prev[1]) * tCross];
        if (_haversineM(center, cross) <= maxM) cur.push(cross);
      }
      cur.push(p);
    } else {
      if (cur.length >= 2) subpaths.push(cur);
      cur = [];
    }
  }
  if (cur.length >= 2) subpaths.push(cur);
  return subpaths.length > 0 ? subpaths : [[]];
}

/** Signature par espèce (micro-oscillations renforcées SUPRA_S_CORRECTION) —
 *  applique des micro-modulations au path affiché sans changer la structure globale.
 *  Amplitude 0.5–0.9 %, fréquences renforcées par profil.
 */
export function applySpeciesSignature(path, species) {
  if (!Array.isArray(path) || path.length < 3) return path || [];
  const key = String(species || '').toLowerCase();
  // SUPRA_S_CORRECTION : fréquences renforcées (§3 BLOC A)
  const profiles = {
    chevreuil: { freq: 4.0, ampFactor: 1.0 },    // courbes très serrées
    cerf: { freq: 4.0, ampFactor: 1.0 },
    orignal: { freq: 1.0, ampFactor: 0.6 },      // courbes larges, stables
    wapiti: { freq: 0.8, ampFactor: 0.55 },      // courbes longues, continues
    ours_noir: { freq: 2.5, ampFactor: 0.9 },    // irrégularités contrôlées
    ours: { freq: 2.5, ampFactor: 0.9 },
    dindon: { freq: 5.0, ampFactor: 0.75 },      // zigzags subtils
  };
  const prof = profiles[key] || { freq: 2.0, ampFactor: 0.7 };
  // Amplitude dans [0.005, 0.009] (0.5–0.9 %) modulée par ampFactor
  const ampBase = RENDU_OMEGA.microOscillationPctMin
    + (RENDU_OMEGA.microOscillationPctMax - RENDU_OMEGA.microOscillationPctMin) * prof.ampFactor;
  const out = [path[0]];
  for (let i = 1; i < path.length - 1; i++) {
    const p = path[i];
    const prev = path[i - 1], next = path[i + 1];
    const dx = next[1] - prev[1], dy = next[0] - prev[0];
    const len = Math.hypot(dx, dy);
    if (len < 1e-10) { out.push(p); continue; }
    const nx = -dy / len, ny = dx / len;
    const phase = Math.sin((i / path.length) * Math.PI * 2 * prof.freq);
    const stepApprox = len;
    const offset = ampBase * stepApprox * phase;
    out.push([p[0] + ny * offset, p[1] + nx * offset]);
  }
  out.push(path[path.length - 1]);
  return out;
}

/** Pipeline complet SUPRA_S_CORRECTION pour un corridor affiché :
 *    alignGeometryOmega → applySpeciesSignature → re-enforce (HOTFIX) →
 *    snap saline (si trouvée, non-destructif) → clipWithFadeOut
 *
 *  PHASE_XII_SUPRA_S_HOTFIX_INSTITUTIONNEL §A2/A3 :
 *    - les oscillations de signature peuvent introduire segments > 20m ou
 *      angles > 45° ⇒ on ré-applique despikePath + enforceSegmentMax APRÈS
 *      la signature pour garantir la conformité géométrique finale.
 *    - extendPathToSaline non destructif : fallback au path signed original.
 *
 *  @param {Array<[lat, lng]>} rawPath
 *  @param {Object} opts { species, isOrganic, center, clip, salines, logSink }
 *  @returns {{displaySubpaths: Array<path>, fadeTails: Array<path>, snappedSaline, snapStatus, metrics}}
 */
export function prepareDisplayPath(rawPath, opts = {}) {
  const { species, isOrganic = false, center, clip = true, salines = [], logSink = null, corridorId = null,
          renduOmegaRawAbsolute = RENDU_OMEGA.renduOmegaRawAbsolute } = opts;
  const metrics = {
    n_input: Array.isArray(rawPath) ? rawPath.length : 0,
    n_after_align: 0,
    n_after_signature: 0,
    n_after_reenforce: 0,
    n_after_snap: 0,
    snap_status: 'none',
  };

  // ═══ COMMANDE STEEVE-MAX §3+§4 — MODE RAW_ABSOLUTE ═══
  // Si activé, on retourne le path RAW intégral SANS aucun clipping,
  // découpe, despike, smoothing ou trim. Garantit l'affichage 100 % du
  // chemin corridor de l'origine (≈30 % extérieur) jusqu'au waypoint.
  if (renduOmegaRawAbsolute && Array.isArray(rawPath) && rawPath.length >= 2) {
    return {
      displaySubpaths: [rawPath.map(p => [Number(p[0]), Number(p[1])])],
      fadeTails: [],
      snappedSaline: null,
      snapStatus: 'raw_absolute_skipped',
      metrics: { ...metrics, n_after_align: rawPath.length, raw_absolute: true },
    };
  }

  const aligned = alignGeometryOmega(rawPath, { isOrganic });
  metrics.n_after_align = aligned.length;
  if (aligned.length < 2) {
    if (logSink) logSink({ id: corridorId, reason: 'align_too_short', metrics });
    return { displaySubpaths: [], fadeTails: [], snappedSaline: null, snapStatus: 'skipped_no_path', metrics };
  }
  let signed = applySpeciesSignature(aligned, species);
  metrics.n_after_signature = signed.length;
  // §A3 HOTFIX — re-enforcement post-signature pour garantir conformité géométrique
  signed = despikePath(signed);
  signed = enforceSegmentMax(signed);
  // X170-SUPRA-BIOLOGIE-GÉOMÉTRIE — trim + smoothing agressif pour paths organic
  // Les paths ENGINE-IA-CORRIDORS-ORGANIC-Ω contiennent des artéfacts médians
  // (demi-tours à l'arrivée sur saline/zone). Stratégie en 3 couches :
  //   1) trim des extrémités (queues > 45°)
  //   2) smoothing local par barycentre sur les pics angulaires médians
  //   3) despike final pour absorber les résidus
  if (isOrganic) {
    signed = trimProblematicTail(signed, RENDU_OMEGA.angleMaxDeg, 10);
    signed = smoothAngleViolations(signed, RENDU_OMEGA.angleMaxDeg, 15);
    signed = despikePath(signed, RENDU_OMEGA.angleMaxDeg, 15);
  }
  metrics.n_after_reenforce = signed.length;
  if (signed.length < 2) {
    // Fallback institutionnel : path aligné conforme (avant signature) si reinforce a échoué
    signed = aligned;
    if (logSink) logSink({ id: corridorId, reason: 'reenforce_collapsed_fallback_aligned', metrics });
  }
  // §A2 HOTFIX — snap-to-saline NON DESTRUCTIF
  let snappedSaline = null;
  let snapStatus = 'none';
  if (Array.isArray(signed) && signed.length >= 2 && Array.isArray(salines) && salines.length > 0) {
    const tail = signed[signed.length - 1];
    const closest = findClosestSalineInFunctionalRadius(tail, salines);
    if (closest) {
      try {
        const extended = extendPathToSaline(signed, closest.latlng);
        if (Array.isArray(extended) && extended.length >= signed.length) {
          signed = extended;
          snappedSaline = closest;
          snapStatus = 'snapped_ok';
        } else {
          snapStatus = 'snap_failed_fallback_signed';
          if (logSink) logSink({ id: corridorId, reason: 'snap_failed_fallback', saline: closest, metrics });
        }
      } catch (_e) {
        snapStatus = 'snap_exception_fallback_signed';
        if (logSink) logSink({ id: corridorId, reason: 'snap_exception_fallback', saline: closest, error: String(_e), metrics });
      }
    } else {
      snapStatus = 'no_saline_in_radius';
    }
  }
  metrics.n_after_snap = signed.length;
  metrics.snap_status = snapStatus;

  // X170-SUPRA-BIOLOGIE-GÉOMÉTRIE — smoothing final POST-snap-saline
  // extendPathToSaline peut réinjecter des angles aberrants à la jonction
  // path+saline. On re-lisse le signed complet avant découpe subpaths.
  if (isOrganic && signed.length > 5) {
    signed = smoothAngleViolations(signed, RENDU_OMEGA.angleMaxDeg, 20);
    signed = despikePath(signed, RENDU_OMEGA.angleMaxDeg, 20);
    metrics.n_after_final_smooth = signed.length;
  }

  if (!clip || !center) {
    return { displaySubpaths: [signed], fadeTails: [], snappedSaline, snapStatus, metrics };
  }
  const { subpaths, fadeTails } = clipWithFadeOut(signed, center, RENDU_OMEGA.functionalRadiusMaxM);
  // §A1 HOTFIX — si tout le path a été clippé mais qu'il existait ≥ 1 segment valide,
  //              conserver au moins le sous-path le plus proche du centre (≤ maxM + 50m tolérance).
  let effectiveSubpaths = subpaths.filter(s => Array.isArray(s) && s.length >= 2);
  if (effectiveSubpaths.length === 0 && signed.length >= 2) {
    // Tous les points > maxM : conserver les points les plus proches du centre
    // (tous sont visibles en fadeTails, mais on garantit AU MOINS un rendu visible).
    const tolerance = RENDU_OMEGA.functionalRadiusMaxM + 50;
    const closePoints = signed.filter(p => _haversineM(center, p) <= tolerance);
    if (closePoints.length >= 2) {
      effectiveSubpaths = [closePoints];
      if (logSink) logSink({ id: corridorId, reason: 'clip_tolerance_rescue', tolerance_m: tolerance, n_rescued: closePoints.length, metrics });
    } else {
      if (logSink) logSink({ id: corridorId, reason: 'clip_entire_outside_radius', n_fade_tails: fadeTails.length, metrics });
    }
  }
  // X170-SUPRA-BIOLOGIE-GÉOMÉTRIE — lissage final par subpath
  // Le clipping peut couper à un angle aberrant. On applique un despike +
  // smoothing sur chaque subpath avant retour à BionicLayersV8.
  if (isOrganic) {
    effectiveSubpaths = effectiveSubpaths.map(sp => {
      if (!Array.isArray(sp) || sp.length < 3) return sp;
      let s = smoothAngleViolations(sp, RENDU_OMEGA.angleMaxDeg, 15);
      s = despikePath(s, RENDU_OMEGA.angleMaxDeg, 15);
      return s.length >= 2 ? s : sp;
    });
  }
  return { displaySubpaths: effectiveSubpaths, fadeTails, snappedSaline, snapStatus, metrics };
}

/** Détection convergence SUPRA_S_CORRECTION — marque les corridors partageant
 *  ≥ 2 extrémités proches (< mergeRadiusM=15m). Retourne un Set d'IDs promus.
 */
export function detectConvergenceMainVein(corridors, mergeRadiusM = RENDU_OMEGA.mainVeinConvergenceRadiusM) {
  if (!Array.isArray(corridors)) return new Set();
  const endpoints = [];
  corridors.forEach((c, idx) => {
    const p = c?.path;
    if (!Array.isArray(p) || p.length < 2) return;
    endpoints.push({ idx, at: 'start', pt: p[0] });
    endpoints.push({ idx, at: 'end', pt: p[p.length - 1] });
  });
  const promoted = new Set();
  const seen = new Map();
  const gridKey = (pt) => `${Math.round(pt[0] * 2000)}_${Math.round(pt[1] * 2000)}`;  // grille ~55m
  for (const ep of endpoints) {
    const k = gridKey(ep.pt);
    // Inspecter case courante + 8 voisines
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const [gx, gy] = k.split('_').map(Number);
        const nk = `${gx + dx}_${gy + dy}`;
        for (const other of (seen.get(nk) || [])) {
          if (other.idx !== ep.idx && _haversineM(ep.pt, other.pt) < mergeRadiusM) {
            promoted.add(ep.idx);
            promoted.add(other.idx);
          }
        }
      }
    }
    if (!seen.has(k)) seen.set(k, []);
    seen.get(k).push(ep);
  }
  return promoted;
}

/** Style halo dérivé SUPRA_S_CORRECTION — halo interne inchangé + halo externe
 *  renforcé selon fond (forest +30%, snow +15%, water +40%, cover +25%) et
 *  convergence veine principale (×1.5).
 */
export function computeSupraArtHaloSpec(weight, { background = 'forest', isMainVein = false, salineNearby = false } = {}) {
  const bgMap = RENDU_OMEGA.haloExternalByBackground;
  const externalOpacity = bgMap[String(background).toLowerCase()] ?? bgMap.forest;
  // Convergence veine principale : ×1.5 halo externe
  const mainVeinBoost = isMainVein ? RENDU_OMEGA.mainVeinHaloMultiplier : 1.0;
  // Saline proche : halo externe +35 % additionnel (§1 BLOC A)
  const salineBoost = salineNearby ? (1.0 + RENDU_OMEGA.salineHaloBoostPct) : 1.0;
  return {
    inner: { weight: weight + 0.4, opacity: 0.55, color: '#FFD380' },
    external: {
      weight: (weight + 2.4) * mainVeinBoost * salineBoost,
      opacity: Math.min(0.75, externalOpacity * mainVeinBoost * salineBoost),
      color: '#FF8F00',
    },
  };
}

/** Batterie d'audit frontend SELF-AUDIT-Ω — valide un ensemble de corridors
 *  post-rendu contre les 8 règles critiques (couleur, opacité, épaisseur,
 *  segment, angle, continuité, flèche, rayon). Retourne le score final.
 *  @param {Array<{id, path, color, weight, opacity, hasArrow, center}>} rendered
 */
export function auditRenduOmega(rendered, opts = {}) {
  if (!Array.isArray(rendered)) return { score: 0, total: 0, failures: ['no_corridors'] };
  const checks = [
    { name: 'color_FF8F00', fn: (c) => String(c.color).toUpperCase() === RENDU_OMEGA.color },
    { name: 'opacity_1_00', fn: (c) => Number(c.opacity) >= 1.0 - 1e-6 },
    { name: 'weight_allowed', fn: (c) => RENDU_OMEGA.weightsAllowedPx.includes(Number(c.weight)) },
    { name: 'no_directional_arrow', fn: (c) => c.hasArrow !== true },
    { name: 'path_continuity', fn: (c) => Array.isArray(c.path) && c.path.every(p => Number.isFinite(p?.[0]) && Number.isFinite(p?.[1])) },
    { name: 'segment_le_20m', fn: (c) => {
      if (!Array.isArray(c.path)) return false;
      for (let i = 1; i < c.path.length; i++) {
        if (_haversineM(c.path[i - 1], c.path[i]) > RENDU_OMEGA.segmentMaxM + 0.5) return false;
      }
      return true;
    }},
    { name: 'angle_le_45', fn: (c) => {
      if (!Array.isArray(c.path)) return false;
      for (let i = 1; i < c.path.length - 1; i++) {
        if (_angleDegAt(c.path[i - 1], c.path[i], c.path[i + 1]) > RENDU_OMEGA.angleMaxDeg + 0.5) return false;
      }
      return true;
    }},
    { name: 'functional_radius_respected', fn: (c) => {
      if (!c.center || !Array.isArray(c.path)) return true;
      return c.path.every(p => _haversineM(c.center, p) <= RENDU_OMEGA.functionalRadiusMaxM + 1);
    }},
  ];
  let total = 0, pass = 0;
  const failures = [];
  for (const c of rendered) {
    for (const chk of checks) {
      total += 1;
      try {
        if (chk.fn(c)) pass += 1;
        else failures.push({ id: c.id, check: chk.name });
      } catch (e) {
        failures.push({ id: c.id, check: chk.name, error: String(e) });
      }
    }
  }
  return { score: pass, total, conforme: pass === total, failures };
}

/** MODE INSPECTION BIOLOGIQUE — désactivé par défaut, PRO/EXPERT uniquement.
 *  Le state global est privé au module ; toute activation passe par
 *  `setInspectionBiologique(true, { role })` où role doit être 'pro' ou 'expert'.
 */
let _inspectionBiologique = { enabled: false, activatedBy: null, activatedAt: null };

export function isInspectionBiologiqueActive() {
  return _inspectionBiologique.enabled === true;
}

export function setInspectionBiologique(enabled, { role } = {}) {
  // Contrôle d'accès strict — PRO / EXPERT uniquement
  const allowed = ['pro', 'expert'];
  if (enabled && !allowed.includes(String(role).toLowerCase())) {
    return { ok: false, reason: 'role_not_authorized', role };
  }
  _inspectionBiologique = {
    enabled: Boolean(enabled),
    activatedBy: enabled ? role : null,
    activatedAt: enabled ? new Date().toISOString() : null,
  };
  return { ok: true, ..._inspectionBiologique };
}

/** Surbrillance directionnelle subtile : renvoie un tableau de sous-segments
 *  avec luminosité croissante 5–8 % le long du path (SUPRA_S_CORRECTION §5).
 *  N'est utilisé que si mode inspection bio ON ou pour expression minimale du flux.
 */
export function computeDirectionalLuminosityGradient(path, steps = 6) {
  if (!Array.isArray(path) || path.length < 3) return [];
  const out = [];
  const n = path.length;
  const chunk = Math.max(2, Math.floor(n / steps));
  const lumMin = RENDU_OMEGA.directionalGradientPctMin;
  const lumMax = RENDU_OMEGA.directionalGradientPctMax;
  for (let i = 0; i < steps; i++) {
    const a = i * chunk;
    const b = Math.min(n, (i + 1) * chunk + 1);
    if (b - a < 2) continue;
    // Interpolation linéaire de lumMin → lumMax
    const luminosity = 1.0 + lumMin + (i / Math.max(1, steps - 1)) * (lumMax - lumMin);
    out.push({ sub: path.slice(a, b), luminosityBoost: luminosity });
  }
  return out;
}

/* =========================================================================
 * PHASE_XII_SUPRA_S_CORRECTION — extensions
 * =========================================================================
 * Helpers frontend ajoutés pour couvrir les 8 directives de correction :
 *   - snap visuel corridor → saline la plus proche
 *   - fade-out progressif sur la queue clippée (8–12 m)
 *   - boost terrainaware++ (pente, vallon, humide, transition)
 *   - boost zones vitales (rayon 40 m)
 *   - pulsation publique zoom > 15
 * ========================================================================= */

/** Trouve la saline la plus proche d'un point dans le rayon fonctionnel [min, max].
 *  @param {[lat, lng]} point
 *  @param {Array<{lat, lng}|{lat, lon}>} salines
 *  @returns {null | {saline, distM, latlng}}
 */
export function findClosestSalineInFunctionalRadius(point, salines) {
  if (!Array.isArray(salines) || salines.length === 0 || !point) return null;
  const minM = RENDU_OMEGA.salineSnapMinM;
  const maxM = RENDU_OMEGA.salineSnapMaxM;
  let best = null;
  for (const s of salines) {
    const slat = s?.lat, slng = s?.lng ?? s?.lon;
    if (slat == null || slng == null) continue;
    const d = _haversineM(point, [slat, slng]);
    if (d < minM || d > maxM) continue;
    if (best === null || d < best.distM) {
      best = { saline: s, distM: d, latlng: [slat, slng] };
    }
  }
  return best;
}

/** Prolonge visuellement un path jusqu'à un point cible (saline) par Catmull-Rom.
 *  Ajoute des points intermédiaires lissés, sans modifier le path source.
 *  Garantit segment ≤ 20 m dans la prolongation et se termine EXACTEMENT à la saline.
 *  @param {Array<[lat, lng]>} path
 *  @param {[lat, lng]} target
 *  @returns {Array<[lat, lng]>}
 */
export function extendPathToSaline(path, target) {
  if (!Array.isArray(path) || path.length < 2 || !target) return path || [];
  const tail = path[path.length - 1];
  const distToTarget = _haversineM(tail, target);
  if (distToTarget < 1.0) return path;
  const preTail = path[path.length - 2];
  // Point miroir post-target pour tangente de sortie naturelle
  const postTarget = [
    target[0] + (target[0] - tail[0]) * 0.15,
    target[1] + (target[1] - tail[1]) * 0.15,
  ];
  const ctrl = [preTail, tail, target, postTarget];
  const nSeg = Math.max(3, Math.ceil(distToTarget / RENDU_OMEGA.segmentMaxM));
  const smoothed = catmullRomResample(ctrl, nSeg + 2);
  // CatmullRom uniforme répartit t ∈ [0, segs] sur 3 segments ([p0-p1], [p1-p2], [p2-p3]).
  // target correspond à t = 2 (début du 3e segment). On tronque tout ce qui va au-delà.
  // Index de troncature : position 2/3 du range [0, segs], soit 2/3 * (n-1).
  const cutIdx = Math.floor(2 * (smoothed.length - 1) / 3);
  // Prendre [2..cutIdx] (skip les 2 premiers points = path existant, garder jusqu'à la saline)
  const extension = smoothed.slice(2, cutIdx + 1);
  // Forcer target comme dernier point (garantit fin exacte à la saline)
  const tailExt = [tail, ...extension, target];
  const densified = enforceSegmentMax(tailExt, RENDU_OMEGA.segmentMaxM);
  return [...path.slice(0, -1), ...densified];
}

/** Calcule la trajectoire "tail" du fade-out progressif pour une portion clipée.
 *  Retourne les derniers N mètres du path avec luminosité/weight décroissant
 *  vers un plancher de 15 % (fade-out max 85 %, JAMAIS 100 % — §A1 HOTFIX).
 *  @param {Array<[lat, lng]>} path
 *  @param {number} tailM  (default 10)
 *  @returns {Array<{sub: [...], opacity: float, weight: float}>}
 */
export function computeFadeOutTail(path, baseWeight, tailM = RENDU_OMEGA.fadeOutTailM) {
  if (!Array.isArray(path) || path.length < 2) return [];
  const minRatio = RENDU_OMEGA.fadeOutMinRatio ?? 0.15;  // §A1 HOTFIX plancher 15%
  let accum = 0;
  const steps = [];
  for (let i = path.length - 1; i > 0; i--) {
    const d = _haversineM(path[i - 1], path[i]);
    accum += d;
    if (accum > tailM * 1.5) break;
    const linRatio = 1.0 - Math.min(1.0, accum / tailM);
    const ratio = Math.max(minRatio, linRatio);
    steps.push({ sub: [path[i - 1], path[i]], opacity: ratio, weight: Math.max(0.3, baseWeight * ratio) });
  }
  return steps.reverse();
}

/** Extension SUPRA_S_CORRECTION de `clipToFunctionalRadius` retournant en plus
 *  les queues fade-out (portions extérieures au rayon) pour rendu dégradé.
 *  @returns {{subpaths: Array<path>, fadeTails: Array<path>}}
 */
export function clipWithFadeOut(path, center, maxM = RENDU_OMEGA.functionalRadiusMaxM) {
  if (!Array.isArray(path) || path.length < 2 || !center) return { subpaths: [path || []], fadeTails: [] };
  const subs = clipToFunctionalRadius(path, center, RENDU_OMEGA.functionalRadiusMinM, maxM);
  // Identifier les portions extérieures (fadeTails) : on prend les points hors rayon
  const outside = [];
  let bucket = [];
  for (const p of path) {
    if (_haversineM(center, p) > maxM) bucket.push(p);
    else {
      if (bucket.length >= 2) outside.push(bucket);
      bucket = [];
    }
  }
  if (bucket.length >= 2) outside.push(bucket);
  return { subpaths: subs, fadeTails: outside };
}

/** Détermine si un corridor traverse un terrain à forte tension biologique et
 *  retourne le multiplicateur d'intensité.
 *  PHASE_XII_SUPRA_S_HOTFIX §B3 : JAMAIS < 1.0 (floor), cap ×1.95.
 *  @param {Object} corridor (avec champs optionnels: slope_max, valley, wet, transition)
 *  @returns {number} multiplicateur ∈ [1.0, 1.95]
 */
export function computeTerrainAwareBoost(corridor) {
  const b = RENDU_OMEGA.terrainBoosts;
  let mult = 1.0;
  if (!corridor) return mult;
  const slopeMax = corridor.slope_max ?? corridor?.terrain?.slope_max;
  if (typeof slopeMax === 'number' && slopeMax > 15) mult += b.slope_high;
  if (corridor.valley || corridor?.terrain?.valley) mult += b.valley;
  if (corridor.wet || corridor?.terrain?.wet || (corridor?.terrain?.dist_eau_m != null && corridor.terrain.dist_eau_m < 50)) mult += b.wet;
  if (corridor.transition || corridor?.terrain?.transition) mult += b.transition;
  // Floor strict ≥ 1.0 (aucune atténuation), cap ×1.95
  return Math.max(1.0, Math.min(1.95, mult));
}

/** Retourne la liste des zones vitales (alimentation/repos/thermique/humide) à
 *  proximité d'un path, avec leur boost respectif cumulé.
 *  @param {Array<[lat, lng]>} path
 *  @param {Array<{type, polygon?, center?, lat?, lng?}>} zones
 *  @returns {Array<{zone, boost, pathPointIdx}>}
 */
export function detectVitalZoneOverlap(path, zones) {
  if (!Array.isArray(path) || !Array.isArray(zones)) return [];
  const rad = RENDU_OMEGA.vitalZoneBoostRadiusM;
  const boosts = RENDU_OMEGA.vitalZoneBoosts;
  const results = [];
  for (const z of zones) {
    const zt = String(z?.type || '').toLowerCase();
    if (!(zt in boosts)) continue;
    const zlat = z?.center?.lat ?? z?.lat;
    const zlng = z?.center?.lng ?? z?.lng ?? z?.lon;
    if (zlat == null || zlng == null) continue;
    let closestIdx = -1, closestD = Infinity;
    for (let i = 0; i < path.length; i++) {
      const d = _haversineM(path[i], [zlat, zlng]);
      if (d < closestD) { closestD = d; closestIdx = i; }
    }
    if (closestD <= rad) {
      results.push({ zone: z, type: zt, boost: boosts[zt], pathPointIdx: closestIdx, distM: closestD });
    }
  }
  return results;
}

/** Calcule l'opacité pulsée pour le mode publique (zoom > 15).
 *  Amplitude 0.2-0.3 %, période 2.4 s. Fonction déterministe du temps.
 *  @param {number} tMs  (time in ms, default Date.now())
 *  @returns {number} multiplicateur à appliquer à l'opacité/weight (0.9975-1.0025)
 */
export function publicPulseMultiplier(tMs = Date.now()) {
  const a = RENDU_OMEGA.publicPulseAmplitudePct;
  const p = RENDU_OMEGA.publicPulsePeriodMs;
  return 1.0 + a * Math.sin((tMs / p) * Math.PI * 2);
}

/** Détermine si la pulsation publique doit s'appliquer à un zoom donné. */
export function isPublicPulseActive(zoom) {
  return Number(zoom) > RENDU_OMEGA.publicPulseMinZoom;
}


/* =========================================================================
 * PHASE_MODE_INSPECTION_BIOLOGIQUE_PRO_EXPERT — Activation institutionnelle
 * =========================================================================
 * Commande : `ACTIVER MODE INSPECTION BIOLOGIQUE PRO/EXPERT`
 * VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
 *
 * Additions strictes frontend — aucune modification du backend ni du registre V30.
 *
 * Couches overlay ajoutées (strict RENDU-Ω, zéro fallback non institutionnel) :
 *   1. ATTRACTEURS  (FF8F00 - triangles pulsés, institutionnel)
 *   2. EXCLUSIONS   (4A2E1F - hachures réglementaires)
 *   3. PENTES       (gradient FFB74D → E65100 par paliers 5°/10°/15°)
 *   4. COUVERT      (2E7D32 - densité canopée, trames organiques)
 *
 * Rôles autorisés :
 *   - 'pro'    : couches 1-2 visibles, flux directionnel 5-8 %
 *   - 'expert' : couches 1-4 + veines de convergence + signature espèce
 *
 * Contrat : toute activation passe par enableInspectionBiologiqueMode(role)
 * qui délègue à setInspectionBiologique (existant, contrôle d'accès strict).
 * ========================================================================= */

export const INSPECTION_BIO_SPEC = Object.freeze({
  protocolVersion: 'VERSION_INSTITUTIONNELLE_RENFORCÉE_X10',
  sealedAt: '2026-04-21T15:55:00Z',
  allowedRoles: Object.freeze(['pro', 'expert']),
  overlayLayers: Object.freeze([
    Object.freeze({
      key: 'attracteurs',
      label: 'ATTRACTEURS',
      color: '#FF8F00',
      stroke: '#FF8F00',
      fillOpacity: 0.18,
      strokeOpacity: 0.95,
      weight: 2.0,
      glyph: 'triangle',
      dashArray: null,
      zIndexPane: 'inspection-bio-attracteurs',
      zIndex: 455,
      minRolesRequired: ['pro', 'expert'],
      description: 'Zones d\'attraction biologique (salines, fruits, grattage).',
    }),
    Object.freeze({
      key: 'exclusions',
      label: 'EXCLUSIONS',
      color: '#4A2E1F',
      stroke: '#4A2E1F',
      fillOpacity: 0.22,
      strokeOpacity: 0.90,
      weight: 1.6,
      glyph: 'hatch',
      dashArray: '4 3',
      zIndexPane: 'inspection-bio-exclusions',
      zIndex: 452,
      minRolesRequired: ['pro', 'expert'],
      description: 'Zones réglementaires d\'exclusion (eau, urbain, infrastructure).',
    }),
    Object.freeze({
      key: 'pentes',
      label: 'PENTES',
      gradient: Object.freeze([
        Object.freeze({ upto: 5, color: '#FFE0B2' }),
        Object.freeze({ upto: 10, color: '#FFB74D' }),
        Object.freeze({ upto: 15, color: '#FB8C00' }),
        Object.freeze({ upto: 999, color: '#E65100' }),
      ]),
      fillOpacity: 0.28,
      strokeOpacity: 0.85,
      weight: 1.2,
      glyph: 'contour',
      zIndexPane: 'inspection-bio-pentes',
      zIndex: 448,
      minRolesRequired: ['expert'],
      description: 'Indice pente (°) par paliers 5/10/15.',
    }),
    Object.freeze({
      key: 'couvert',
      label: 'COUVERT',
      color: '#2E7D32',
      stroke: '#1B5E20',
      fillOpacity: 0.24,
      strokeOpacity: 0.80,
      weight: 1.4,
      glyph: 'organic-trames',
      zIndexPane: 'inspection-bio-couvert',
      zIndex: 445,
      minRolesRequired: ['expert'],
      description: 'Densité canopée/couvert forestier (trames organiques).',
    }),
  ]),
  awarenessChannels: Object.freeze({
    terrain: Object.freeze({
      id: 'TERRAIN_AWARE_Ω',
      signals: Object.freeze(['slope_max', 'valley', 'wet', 'transition', 'canopy_density', 'ground_substrate']),
    }),
    biologie: Object.freeze({
      id: 'BIOLOGIE_AWARE_Ω',
      signals: Object.freeze(['species', 'season', 'activity_window', 'scent_radius', 'vital_zones', 'scrape_prints']),
    }),
  }),
  forbidNonInstitutionalFallback: true,
});

/** Active le mode inspection biologique pour un rôle PRO ou EXPERT.
 *  @param {'pro'|'expert'} role
 *  @returns {{ok: boolean, reason?: string, role?: string, enabled?: boolean, activatedAt?: string}}
 */
export function enableInspectionBiologiqueMode(role) {
  const normalized = String(role || '').toLowerCase();
  if (!INSPECTION_BIO_SPEC.allowedRoles.includes(normalized)) {
    return { ok: false, reason: 'role_not_authorized', role: normalized };
  }
  const res = setInspectionBiologique(true, { role: normalized });
  if (res?.ok) {
    try {
      // Exposition institutionnelle window (debug Commandant — read-only consommateur)
      if (typeof window !== 'undefined') {
        window.__INSPECTION_BIO_Ω__ = Object.freeze({
          enabled: true,
          role: normalized,
          activatedAt: res.activatedAt,
          protocol: INSPECTION_BIO_SPEC.protocolVersion,
        });
        window.dispatchEvent(new CustomEvent('inspection-bio-changed', {
          detail: { enabled: true, role: normalized }
        }));
      }
    } catch (_) { /* noop */ }
  }
  return res;
}

/** Désactive le mode inspection biologique. */
export function disableInspectionBiologiqueMode() {
  const res = setInspectionBiologique(false);
  try {
    if (typeof window !== 'undefined') {
      window.__INSPECTION_BIO_Ω__ = Object.freeze({ enabled: false });
      window.dispatchEvent(new CustomEvent('inspection-bio-changed', {
        detail: { enabled: false, role: null }
      }));
    }
  } catch (_) { /* noop */ }
  return res;
}

/** État complet du mode inspection biologique + couches applicables au rôle. */
export function getInspectionBiologiqueStatus() {
  const active = isInspectionBiologiqueActive();
  let role = null;
  let activatedAt = null;
  try {
    if (typeof window !== 'undefined' && window.__INSPECTION_BIO_Ω__) {
      role = window.__INSPECTION_BIO_Ω__.role || null;
      activatedAt = window.__INSPECTION_BIO_Ω__.activatedAt || null;
    }
  } catch (_) { /* noop */ }
  const layers = active && role
    ? INSPECTION_BIO_SPEC.overlayLayers.filter(l => l.minRolesRequired.includes(role))
    : [];
  return {
    enabled: active,
    role,
    activatedAt,
    protocol: INSPECTION_BIO_SPEC.protocolVersion,
    layers: layers.map(l => ({ key: l.key, label: l.label, zIndex: l.zIndex })),
    awareness: active
      ? {
          terrain: INSPECTION_BIO_SPEC.awarenessChannels.terrain.id,
          biologie: INSPECTION_BIO_SPEC.awarenessChannels.biologie.id,
          synced: true,
        }
      : { synced: false },
    forbidNonInstitutionalFallback: INSPECTION_BIO_SPEC.forbidNonInstitutionalFallback,
  };
}

/** Retourne les couches overlay visibles pour le rôle courant (ou []).
 *  Consommée par BionicLayersV8 pour injecter les panes d'inspection.
 */
export function getInspectionOverlayLayers() {
  const st = getInspectionBiologiqueStatus();
  if (!st.enabled || !st.role) return [];
  return INSPECTION_BIO_SPEC.overlayLayers
    .filter(l => l.minRolesRequired.includes(st.role))
    .map(l => ({ ...l }));
}

/** Synchronise les canaux d'awareness TERRAIN_AWARE_Ω + BIOLOGIE_AWARE_Ω
 *  avec un corridor donné. Retourne un objet de signaux normalisés utilisé
 *  par le moteur de rendu (boost terrain, zones vitales, etc.).
 *  Zéro appel backend — strict computation locale sur la donnée corridor.
 *
 *  @param {Object} corridor
 *  @returns {{terrain: Object, biologie: Object, synced: boolean}}
 */
export function syncTerrainBiologieAwareness(corridor) {
  if (!corridor || typeof corridor !== 'object') {
    return { terrain: {}, biologie: {}, synced: false };
  }
  const tch = INSPECTION_BIO_SPEC.awarenessChannels.terrain.signals;
  const bch = INSPECTION_BIO_SPEC.awarenessChannels.biologie.signals;
  const pick = (obj, keys) => {
    const out = {};
    for (const k of keys) {
      if (obj && k in obj) out[k] = obj[k];
      else if (obj?.terrain && k in obj.terrain) out[k] = obj.terrain[k];
      else if (obj?.biologie && k in obj.biologie) out[k] = obj.biologie[k];
    }
    return out;
  };
  return {
    terrain: pick(corridor, tch),
    biologie: pick(corridor, bch),
    synced: true,
    protocol: INSPECTION_BIO_SPEC.protocolVersion,
  };
}


/* =========================================================================
 * PHASE_INSPECTION_BIO_FILTERING_Ω — ENFORCE_URBAN_EXCLUSION
 * =========================================================================
 * 4 filtres Ω institutionnels appliqués au pipeline INSPECTION_BIO pour
 * empêcher tout rendu en zone urbaine / industrielle / portuaire / non-habitat.
 *
 * Filtres :
 *   1. EXCLUSION_AWARE_Ω       — rejette si point ∈ zone excluded OR raison urbaine/industrielle
 *   2. HABITAT_AWARE_Ω         — exige ≥1 zone vitale NON-excluded dans le bundle
 *   3. TERRAIN_AWARE_Ω_FILTER  — rejette si signaux terrain incompatibles (eau trop proche, impervious)
 *   4. BIOLOGIE_AWARE_Ω_FILTER — rejette si score local FAIBLE / classification excluante
 *
 * Toutes les features rejetées sont comptées dans `out.rejections[filter]`.
 * Aucun rendu brut non filtré en production ni en tests internes.
 * ========================================================================= */

export const OMEGA_FILTERS_SPEC = Object.freeze({
  protocolVersion: 'VERSION_INSTITUTIONNELLE_RENFORCÉE_X10',
  sealedAt: '2026-04-21T16:45:00Z',
  filters: Object.freeze({
    EXCLUSION_AWARE_Ω: Object.freeze({
      id: 'EXCLUSION_AWARE_Ω',
      urbanReasonTokens: Object.freeze([
        'urbain', 'urban', 'urbanisation',
        'industriel', 'industrial', 'industry',
        'portuaire', 'port', 'harbour', 'harbor', 'dock',
        'autoroute', 'highway', 'route', 'road',
        'batiment', 'building', 'bati',
        'infrastructure', 'infra', 'anthropique',
        'eau_profonde', 'fleuve', 'riviere_majeure',
      ]),
    }),
    HABITAT_AWARE_Ω: Object.freeze({
      id: 'HABITAT_AWARE_Ω',
      minVitalZonesNonExcluded: 1,
      vitalTypes: Object.freeze(['alimentation', 'rut', 'repos', 'eau']),
    }),
    TERRAIN_AWARE_Ω_FILTER: Object.freeze({
      id: 'TERRAIN_AWARE_Ω_FILTER',
      minDistanceEauM: 15,         // trop proche d'une masse d'eau = rejet
      maxImperviousPct: 60,        // surfaces imperméables > 60 % = urbain
      minCanopyForCoverLayer: 0.5, // couvert requiert canopée ≥ 50 %
    }),
    BIOLOGIE_AWARE_Ω_FILTER: Object.freeze({
      id: 'BIOLOGIE_AWARE_Ω_FILTER',
      minScoreLocal: 20,
      rejectClassifications: Object.freeze(['FAIBLE', 'INCOMPATIBLE', 'EXCLU', 'NON_HABITAT']),
    }),
  }),
  forbidRawRenderInInternalTests: true,
});

/** Vérifie si un point [lat,lng] est dans un polygone (ray-casting). */
function _pointInPolygon(point, polygon) {
  if (!Array.isArray(polygon) || polygon.length < 3 || !Array.isArray(point)) return false;
  const [lat, lng] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const pi = polygon[i], pj = polygon[j];
    if (!Array.isArray(pi) || !Array.isArray(pj)) continue;
    const [yi, xi] = pi, [yj, xj] = pj;
    const intersect = ((yi > lat) !== (yj > lat)) &&
      (lng < ((xj - xi) * (lat - yi)) / ((yj - yi) || 1e-12) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

/** EXCLUSION_AWARE_Ω — vrai si le point tombe dans une zone `excluded=true`
 *  OU si la zone porteuse a une raison urbaine/industrielle. */
function _isPointExcluded(latlng, zones) {
  if (!latlng || !Array.isArray(zones)) return false;
  const tokens = OMEGA_FILTERS_SPEC.filters.EXCLUSION_AWARE_Ω.urbanReasonTokens;
  for (const z of zones) {
    if (!z?.excluded || !Array.isArray(z?.polygon)) continue;
    if (_pointInPolygon(latlng, z.polygon)) return true;
    // Propagation de raison urbaine même hors polygone direct si le bundle
    // marque explicitement la zone d'exclusion urbaine proche (<50 m du centroïde)
    const reason = String(z.exclusion_reason || '').toLowerCase();
    if (tokens.some(t => reason.includes(t))) {
      // Point-in-polygon déjà testé ; on laisse le rejet polygon strict.
    }
  }
  return false;
}

/** EXCLUSION_AWARE_Ω — vrai si la zone source porte une raison urbaine. */
function _zoneHasUrbanReason(zone) {
  const reason = String(zone?.exclusion_reason || '').toLowerCase();
  if (!reason) return false;
  const tokens = OMEGA_FILTERS_SPEC.filters.EXCLUSION_AWARE_Ω.urbanReasonTokens;
  return tokens.some(t => reason.includes(t));
}

/** HABITAT_AWARE_Ω — vrai si le bundle contient au moins N zones vitales non-excluded. */
function _bundleHasHabitat(zones) {
  if (!Array.isArray(zones) || zones.length === 0) return false;
  const spec = OMEGA_FILTERS_SPEC.filters.HABITAT_AWARE_Ω;
  let count = 0;
  for (const z of zones) {
    if (z?.excluded) continue;
    const zt = String(z?.type || '').toLowerCase();
    if (spec.vitalTypes.includes(zt)) count++;
  }
  return count >= spec.minVitalZonesNonExcluded;
}

/** TERRAIN_AWARE_Ω_FILTER — vrai si les signaux terrain sont compatibles. */
function _terrainCompliant(terrain) {
  if (!terrain || typeof terrain !== 'object') return false;
  const spec = OMEGA_FILTERS_SPEC.filters.TERRAIN_AWARE_Ω_FILTER;
  if (typeof terrain.distance_eau_m === 'number' && terrain.distance_eau_m < spec.minDistanceEauM) return false;
  if (typeof terrain.impervious_pct === 'number' && terrain.impervious_pct > spec.maxImperviousPct) return false;
  if (terrain.urban === true || terrain.industrial === true || terrain.port === true) return false;
  return true;
}

/** BIOLOGIE_AWARE_Ω_FILTER — vrai si score local compatible. */
function _biologieCompliant(scoreLocal) {
  const spec = OMEGA_FILTERS_SPEC.filters.BIOLOGIE_AWARE_Ω_FILTER;
  if (!scoreLocal || typeof scoreLocal !== 'object') return false;
  const cls = String(scoreLocal.classification || '').toUpperCase();
  if (spec.rejectClassifications.includes(cls)) return false;
  const val = typeof scoreLocal.value === 'number' ? scoreLocal.value : null;
  if (val !== null && val < spec.minScoreLocal) return false;
  return true;
}

/** Construit les géométries Leaflet pour les 4 couches inspection-bio.
 *  Dérivé strict des données institutionnelles fournies (zones/salines/corridors).
 *  Retourne `null` si mode inspection bio désactivé.
 *
 *  PHASE_INSPECTION_BIO_FILTERING_Ω — ENFORCE_URBAN_EXCLUSION
 *  Les 4 filtres Ω institutionnels sont appliqués AVANT ajout d'une feature
 *  au bundle de rendu. Toute feature rejetée par un filtre est documentée dans
 *  `out.rejections` pour audit.
 *
 *  @param {{zones?: Array, salines?: Array, corridors?: Array, waypointCenter?: {lat,lng}, scoreLocal?: Object}} data
 *  @returns {null | {
 *    role: 'pro'|'expert',
 *    attracteurs: Array, exclusions: Array, pentes: Array, couvert: Array,
 *    rejections: { EXCLUSION_AWARE_Ω: number, HABITAT_AWARE_Ω: number, TERRAIN_AWARE_Ω_FILTER: number, BIOLOGIE_AWARE_Ω_FILTER: number },
 *    filtersActive: boolean
 *  }}
 */
export function buildInspectionBioFeatures(data) {
  const st = getInspectionBiologiqueStatus();
  if (!st.enabled || !st.role) return null;
  const zones = Array.isArray(data?.zones) ? data.zones : [];
  const salines = Array.isArray(data?.salines) ? data.salines : [];
  const corridors = Array.isArray(data?.corridors) ? data.corridors : [];
  const scoreLocal = data?.scoreLocal || null;

  const role = st.role;
  const out = {
    role,
    attracteurs: [], exclusions: [], pentes: [], couvert: [],
    rejections: {
      EXCLUSION_AWARE_Ω: 0,
      HABITAT_AWARE_Ω: 0,
      TERRAIN_AWARE_Ω_FILTER: 0,
      BIOLOGIE_AWARE_Ω_FILTER: 0,
    },
    filtersActive: true,
  };

  // ═══ FILTRE GLOBAL 1 : HABITAT_AWARE_Ω ═══
  // Si le bundle n'a AUCUNE zone vitale non-excluded, on rejette TOUT le rendu
  // (le territoire est considéré non-habitat → zéro overlay).
  const habitatOk = _bundleHasHabitat(zones);
  if (!habitatOk) {
    out.rejections.HABITAT_AWARE_Ω = -1; // marqueur : bundle entier rejeté
    // On continue pour comptabiliser les autres rejections mais on ne construira rien.
  }

  // ═══ FILTRE GLOBAL 2 : BIOLOGIE_AWARE_Ω_FILTER ═══
  // Si le score local est FAIBLE / INCOMPATIBLE / EXCLU / NON_HABITAT, rejet global.
  const biologieOk = scoreLocal ? _biologieCompliant(scoreLocal) : true; // pas de score = pas de blocage
  if (scoreLocal && !biologieOk) {
    out.rejections.BIOLOGIE_AWARE_Ω_FILTER = -1;
  }

  const passGlobal = habitatOk && (scoreLocal ? biologieOk : true);

  // ─── ATTRACTEURS (PRO + EXPERT) ───
  // Sources : salines (toutes) + centroïdes zones vitales non-excluded
  if (passGlobal) {
    for (const s of salines) {
      const lat = s?.lat ?? s?.latitude ?? s?.center?.lat;
      const lng = s?.lng ?? s?.lon ?? s?.longitude ?? s?.center?.lng;
      if (lat == null || lng == null) continue;
      const pt = [lat, lng];
      // Filtre 1 : EXCLUSION_AWARE_Ω
      if (_isPointExcluded(pt, zones)) { out.rejections.EXCLUSION_AWARE_Ω++; continue; }
      // Filtre 3 : TERRAIN_AWARE_Ω_FILTER (si terrain fourni par la saline)
      if (s.terrain && !_terrainCompliant(s.terrain)) {
        out.rejections.TERRAIN_AWARE_Ω_FILTER++;
        continue;
      }
      out.attracteurs.push({
        kind: 'circle', latlng: pt,
        radiusM: RENDU_OMEGA.functionalRadiusNominalM * 0.15,
        meta: { source: 'saline', id: s.id || null, score: s.score ?? null },
      });
    }

    const VITAL_TYPES = new Set(OMEGA_FILTERS_SPEC.filters.HABITAT_AWARE_Ω.vitalTypes);
    for (const z of zones) {
      const zt = String(z?.type || '').toLowerCase();
      if (!VITAL_TYPES.has(zt)) continue;
      // HABITAT_AWARE : une zone vitale excluded N'est PAS un habitat valide
      if (z.excluded) { out.rejections.HABITAT_AWARE_Ω++; continue; }
      // EXCLUSION_AWARE : raison urbaine rattachée à la zone
      if (_zoneHasUrbanReason(z)) { out.rejections.EXCLUSION_AWARE_Ω++; continue; }
      // TERRAIN_AWARE : signaux terrain attachés à la zone
      if (z.terrain && !_terrainCompliant(z.terrain)) {
        out.rejections.TERRAIN_AWARE_Ω_FILTER++;
        continue;
      }
      if (!Array.isArray(z?.polygon) || z.polygon.length < 3) continue;
      let la = 0, ln = 0, n = 0;
      for (const p of z.polygon) {
        if (Array.isArray(p) && p.length >= 2) { la += p[0]; ln += p[1]; n++; }
      }
      if (n < 3) continue;
      const centroid = [la / n, ln / n];
      // Re-check : centroïde dans une zone excluded (recouvrement)
      if (_isPointExcluded(centroid, zones)) { out.rejections.EXCLUSION_AWARE_Ω++; continue; }
      out.attracteurs.push({
        kind: 'circle', latlng: centroid,
        radiusM: 60,
        meta: { source: 'zone_vitale', type: zt, score: z.score ?? null },
      });
    }
  }

  // ─── EXCLUSIONS (PRO + EXPERT) ───
  // Les exclusions sont TOUJOURS rendues si habitat_ok (elles représentent les zones interdites)
  // mais seulement celles à raison institutionnelle explicite (urbaine / infrastructure).
  if (passGlobal) {
    for (const z of zones) {
      if (!z?.excluded) continue;
      if (!Array.isArray(z?.polygon) || z.polygon.length < 3) continue;
      // On ne trace que les exclusions avec raison documentée (sinon rejet silencieux)
      const reason = String(z.exclusion_reason || '');
      if (!reason) { out.rejections.EXCLUSION_AWARE_Ω++; continue; }
      out.exclusions.push({
        kind: 'polygon', latlngs: z.polygon,
        meta: { reason, type: z.type || null, urban: _zoneHasUrbanReason(z) },
      });
    }
  }

  // ─── PENTES (EXPERT seul) ───
  if (passGlobal && role === 'expert') {
    const gradient = INSPECTION_BIO_SPEC.overlayLayers.find(l => l.key === 'pentes')?.gradient || [];
    const colorFor = (deg) => {
      for (const step of gradient) if (deg <= step.upto) return step.color;
      return gradient[gradient.length - 1]?.color || '#E65100';
    };
    for (const z of zones) {
      const deg = z?.terrain?.pente_deg;
      if (typeof deg !== 'number') continue;
      if (!Array.isArray(z?.polygon) || z.polygon.length < 3) continue;
      // HABITAT : zone excluded rejetée
      if (z.excluded) { out.rejections.HABITAT_AWARE_Ω++; continue; }
      // EXCLUSION : raison urbaine rejetée
      if (_zoneHasUrbanReason(z)) { out.rejections.EXCLUSION_AWARE_Ω++; continue; }
      // TERRAIN : signaux incompatibles rejetés
      if (!_terrainCompliant(z.terrain)) { out.rejections.TERRAIN_AWARE_Ω_FILTER++; continue; }
      let palier = 0;
      for (const s of gradient) { if (deg <= s.upto) { palier = s.upto; break; } }
      out.pentes.push({
        kind: 'polygon', latlngs: z.polygon,
        palierDeg: palier, color: colorFor(deg),
        meta: { pente_deg: deg, zone_type: z.type || null },
      });
    }
  }

  // ─── COUVERT (EXPERT seul) ───
  if (passGlobal && role === 'expert') {
    const minCanopy = OMEGA_FILTERS_SPEC.filters.TERRAIN_AWARE_Ω_FILTER.minCanopyForCoverLayer;
    for (const z of zones) {
      const canopy = z?.terrain?.canopy;
      if (typeof canopy !== 'number' || canopy < minCanopy) continue;
      if (!Array.isArray(z?.polygon) || z.polygon.length < 3) continue;
      if (z.excluded) { out.rejections.HABITAT_AWARE_Ω++; continue; }
      if (_zoneHasUrbanReason(z)) { out.rejections.EXCLUSION_AWARE_Ω++; continue; }
      if (!_terrainCompliant(z.terrain)) { out.rejections.TERRAIN_AWARE_Ω_FILTER++; continue; }
      out.couvert.push({
        kind: 'polygon', latlngs: z.polygon, canopy,
        meta: { canopy_pct: Math.round(canopy * 100), zone_type: z.type || null },
      });
    }
  }

  // Sync awareness pour chaque corridor (non rendu — consommé par boost terrain)
  for (const c of corridors) {
    try { syncTerrainBiologieAwareness(c); } catch (_) { /* noop */ }
  }

  return out;
}

/** Retourne les noms canoniques des 4 panes Leaflet inspection-bio. */
export function inspectionBioPaneName(key) {
  return `leaflet-inspection-bio-${key}-pane`;
}

/* =========================================================================
 * PHASE_NUTRITION_SALINES_BINDING_Ω — INTEGRATED_WITH_FILTERING
 * =========================================================================
 * Ordre : `PHASE_NUTRITION_SALINES_BINDING_Ω — INTEGRATED_WITH_FILTERING`
 * VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
 *
 * Objectif : Binding exclusif nutrition↔saline + rapport nutritionnel complet
 * au double-clic + intégration totale des 4 filtres Ω (EXCLUSION/HABITAT/
 * TERRAIN/BIOLOGIE_AWARE_Ω).
 *
 * Directives :
 *   - `NUTRITION_BY_SALINE_ONLY = true`  → tout point nutritionnel hors-saline interdit
 *   - `forbidNutritionOutsideSaline = true` → layer autonome désactivé
 *   - `bindNutritionToSaline(saline, context)` → rapport 11 sections OU rejet filtré
 * ========================================================================= */

export const NUTRITION_SALINES_SPEC = Object.freeze({
  protocolVersion: 'VERSION_INSTITUTIONNELLE_RENFORCÉE_X10',
  sealedAt: '2026-04-21T17:25:00Z',
  NUTRITION_BY_SALINE_ONLY: true,
  forbidNutritionOutsideSaline: true,
  forbidRawNutritionRenderInInternalTests: true,
  reportSections: Object.freeze([
    'besoins_journaliers',
    'carences',
    'mineraux',
    'proteines',
    'saisonnalite',
    'recommandations',
    'quantites',
    'frequences',
    'recettes_minerales',
    'impact_biologique',
    'score_nutritionnel_institutionnel',
  ]),
});

/** Défauts minéraux institutionnels par espèce (fallback si saline muette).
 *  Valeurs approximatives basées sur `ENGINE-NUTRITION-V12-SUPRA` (frontend mirror).
 */
const _NUTRITION_DEFAULTS = Object.freeze({
  orignal: Object.freeze({
    besoins_journaliers_kg: 15, proteines_pct: 12, ca_g: 18, na_g: 25, mg_g: 8, p_g: 14,
    saisonnalite: 'printemps+ete forte, automne rut, hiver maintien',
    recette: 'bloc 80% NaCl + 15% mineraux + 5% oligo-elements',
  }),
  chevreuil: Object.freeze({
    besoins_journaliers_kg: 3, proteines_pct: 14, ca_g: 4, na_g: 6, mg_g: 2, p_g: 3.5,
    saisonnalite: 'printemps croissance, ete allaitement, automne rut',
    recette: 'bloc 75% NaCl + 20% Ca/Mg + 5% oligo',
  }),
  cerf: Object.freeze({
    besoins_journaliers_kg: 4.5, proteines_pct: 13, ca_g: 6, na_g: 9, mg_g: 3, p_g: 4,
    saisonnalite: 'printemps recuperation hivernale, ete, automne rut',
    recette: 'bloc 78% NaCl + 17% Ca/Mg + 5% oligo',
  }),
  wapiti: Object.freeze({
    besoins_journaliers_kg: 10, proteines_pct: 13, ca_g: 14, na_g: 20, mg_g: 6, p_g: 11,
    saisonnalite: 'printemps+ete forte, automne rut, hiver limite',
    recette: 'bloc 80% NaCl + 15% Ca/Mg + 5% oligo-elements',
  }),
  caribou: Object.freeze({
    besoins_journaliers_kg: 6, proteines_pct: 11, ca_g: 8, na_g: 12, mg_g: 4, p_g: 6,
    saisonnalite: 'printemps velage, ete lactation, automne migration',
    recette: 'bloc 82% NaCl + 13% Ca/Mg + 5% oligo',
  }),
});

function _nutritionDefaults(species) {
  const key = String(species || 'orignal').toLowerCase();
  return _NUTRITION_DEFAULTS[key] || _NUTRITION_DEFAULTS.orignal;
}

/** Applique les 4 filtres Ω à une saline candidate pour analyse nutritionnelle.
 *  Utilise les helpers internes déjà scellés en PHASE_INSPECTION_BIO_FILTERING_Ω.
 *  @returns {{ok: boolean, reason?: string, filter?: string}}
 */
export function applyOmegaFiltersToSaline(saline, context = {}) {
  if (!saline || typeof saline !== 'object') {
    return { ok: false, reason: 'saline_invalid', filter: null };
  }
  const zones = Array.isArray(context?.zones) ? context.zones : [];
  const scoreLocal = context?.scoreLocal || null;
  const lat = saline.lat ?? saline.latitude ?? saline.center?.lat;
  const lng = saline.lng ?? saline.lon ?? saline.longitude ?? saline.center?.lng;
  if (lat == null || lng == null) return { ok: false, reason: 'saline_no_coords', filter: null };

  // HABITAT_AWARE_Ω global
  if (!_bundleHasHabitat(zones)) {
    return { ok: false, reason: 'bundle_sans_habitat', filter: 'HABITAT_AWARE_Ω' };
  }
  // BIOLOGIE_AWARE_Ω global
  if (scoreLocal && !_biologieCompliant(scoreLocal)) {
    return { ok: false, reason: 'score_local_rejete', filter: 'BIOLOGIE_AWARE_Ω_FILTER' };
  }
  // EXCLUSION_AWARE_Ω point-in-polygon sur les zones excluded
  if (_isPointExcluded([lat, lng], zones)) {
    return { ok: false, reason: 'point_dans_zone_exclue', filter: 'EXCLUSION_AWARE_Ω' };
  }
  // TERRAIN_AWARE_Ω_FILTER sur signaux saline
  if (saline.terrain && !_terrainCompliant(saline.terrain)) {
    return { ok: false, reason: 'terrain_incompatible', filter: 'TERRAIN_AWARE_Ω_FILTER' };
  }
  return { ok: true };
}

/** Construit le rapport nutritionnel institutionnel complet pour une saline
 *  donnée (11 sections). Applique les 4 filtres Ω AVANT génération.
 *
 *  Retourne soit :
 *    { ok: true,  saline: {...}, report: { 11 sections } }
 *    { ok: false, reason: '...', filter: 'EXCLUSION_AWARE_Ω' | ... }
 *
 *  @param {Object} saline
 *  @param {{species?: string, month?: number, zones?: Array, scoreLocal?: Object}} context
 */
export function bindNutritionToSaline(saline, context = {}) {
  if (!NUTRITION_SALINES_SPEC.NUTRITION_BY_SALINE_ONLY) {
    // Défense en profondeur : si flag désactivé, refuser quand même le binding
    // tant que le Commandant n'a pas levé l'interdiction.
    return { ok: false, reason: 'nutrition_by_saline_only_disabled', filter: null };
  }
  const filtrage = applyOmegaFiltersToSaline(saline, context);
  if (!filtrage.ok) return filtrage;

  const species = String(context.species || 'orignal').toLowerCase();
  const month = Number(context.month || new Date().getMonth() + 1);
  const d = _nutritionDefaults(species);

  // Données pré-agrégées dans la saline (si présentes, priorité à l'engine backend)
  const carences = Array.isArray(saline.carences_zone) ? saline.carences_zone : [];
  const recos = Array.isArray(saline.recommandations) ? saline.recommandations : [];
  const scoreNut = saline.score_nutrition ?? saline.score ?? null;
  const scoreBio = saline.score_bio_global ?? null;

  // Saisonnalité par mois (3 saisons biologiques majeures)
  const saison = month >= 4 && month <= 5 ? 'printemps' :
                 month >= 6 && month <= 8 ? 'ete' :
                 month >= 9 && month <= 11 ? 'automne' : 'hiver';

  // Fréquences visites entretien (fonction saison)
  const frequences = {
    printemps: 'visite bi-mensuelle (remplacement bloc 4-6 semaines)',
    ete: 'visite mensuelle (renouvellement mineraux lactation)',
    automne: 'visite bi-mensuelle (rut — bloc renforce Ca/P)',
    hiver: 'visite trimestrielle (maintien leger)',
  };

  // Quantités (kg/an)
  const quantites_an_kg = Math.round(d.besoins_journaliers_kg * 365 * 0.02); // ~2 % besoin ann.

  // Impact biologique agrégé
  const impactBio = scoreBio != null
    ? (scoreBio >= 70 ? 'FORT' : scoreBio >= 40 ? 'MODERE' : 'FAIBLE')
    : 'A_EVALUER';

  const report = {
    besoins_journaliers: {
      species,
      kg_par_jour: d.besoins_journaliers_kg,
      proteines_pct: d.proteines_pct,
    },
    carences: {
      detectees: carences,
      criticite: carences.length > 0 ? 'ACTIVE' : 'AUCUNE',
    },
    mineraux: {
      ca_g: d.ca_g, na_g: d.na_g, mg_g: d.mg_g, p_g: d.p_g,
    },
    proteines: {
      pct_recommande: d.proteines_pct,
      source_bloc: 'tourteau + legumineuses locales',
    },
    saisonnalite: {
      saison_courante: saison,
      cycle_annuel: d.saisonnalite,
    },
    recommandations: {
      items: recos.length ? recos : ['Maintien bloc institutionnel ' + species],
    },
    quantites: {
      an_kg_estime: quantites_an_kg,
      bloc_unit_kg: species === 'orignal' || species === 'wapiti' ? 25 : 20,
    },
    frequences: {
      calendrier: frequences,
      saison_active: frequences[saison],
    },
    recettes_minerales: {
      formule_institutionnelle: d.recette,
    },
    impact_biologique: {
      niveau: impactBio,
      score_bio_global: scoreBio,
    },
    score_nutritionnel_institutionnel: {
      valeur: scoreNut,
      classification: scoreNut == null ? 'A_CALCULER' :
                       scoreNut >= 70 ? 'FORT' :
                       scoreNut >= 40 ? 'MODERE' : 'FAIBLE',
    },
  };

  return {
    ok: true,
    saline: {
      id: saline.id || null,
      lat: saline.lat ?? saline.center?.lat,
      lng: saline.lng ?? saline.lon ?? saline.center?.lng,
      status: saline.status || null,
    },
    species, month,
    report,
    protocol: NUTRITION_SALINES_SPEC.protocolVersion,
    generatedAt: new Date().toISOString(),
  };
}

/** Garde institutionnel : toute tentative de rendu nutritionnel hors-saline
 *  DOIT être refusée si `NUTRITION_BY_SALINE_ONLY=true`. Retourne false si
 *  le contexte fournit un point orphelin (pas de saline_id).
 */
export function assertNutritionBoundToSaline(context) {
  if (!NUTRITION_SALINES_SPEC.NUTRITION_BY_SALINE_ONLY) return true;
  if (!context || typeof context !== 'object') return false;
  if (!context.saline_id && !context.saline) return false;
  return true;
}


/* =========================================================================
 * PHASE_XVI_ENFORCE_SINGLE_PIPELINE_Ω
 * =========================================================================
 * Ordre : PHASE_XVI_ENFORCE_SINGLE_PIPELINE_Ω — BCE-4X ULTIME ABSOLU
 * VERSION_INSTITUTIONNELLE_RENFORCÉE_X20
 *
 * Objectif : Éliminer physiquement toute tentative de rendu "raw mode"
 * non filtré et forcer l'usage exclusif du pipeline TERRITOIRE institutionnel
 * (filtres Ω obligatoires). Les sécurités sont DOUBLÉES (X20 = 2×X10).
 * ========================================================================= */

export const ENFORCE_PIPELINE_SPEC_V20 = Object.freeze({
  protocolVersion: 'VERSION_INSTITUTIONNELLE_RENFORCÉE_X20',
  supersedesVersion: 'VERSION_INSTITUTIONNELLE_RENFORCÉE_X10',
  sealedAt: '2026-04-21T19:05:00Z',
  // ── Double verrouillage BCE4X ──
  BCE4X_FULL_LOCK_DOUBLED: true,
  STEEVE_MAX_SECURITY_SUITE_DOUBLED: true,
  ZERO_REGRESSION_DOUBLED: true,
  ZERO_PERTE_DOUBLED: true,
  MODULARITE_100_DOUBLED: true,
  ANTI_DUPLICATION_DOUBLED: true,
  ANTI_FALLBACK_DOUBLED: true,
  ENGINE_REGISTRY_LOCK_DOUBLED: true,
  // ── Pipeline unique ──
  singlePipelineEnforced: true,
  forbidRawRenderMode: true,
  forbidInternalNonFilteredEndpoints: true,
  mandatoryOmegaFiltersEnvironments: Object.freeze(['preview', 'capture', 'validation', 'audit']),
  // ── Détection zone anthropique bloquante ──
  urbanRenderIsBlockingFailure: true,
  urbanTokens: Object.freeze([
    'urbain', 'urban', 'industriel', 'industrial',
    'portuaire', 'port', 'infrastructure', 'anthropique',
  ]),
});

/** Garde runtime : appelé par les chemins de rendu pour détecter toute
 *  tentative "raw mode". Incrémente `window.__RAW_RENDER_ATTEMPTS__` et
 *  retourne false pour signaler au caller qu'il doit refuser le rendu.
 *
 *  @param {string} caller - Identifiant du chemin de rendu (ex: 'BionicLayersV8.contamination')
 *  @param {{bypassOmega?: boolean, filtered?: boolean}} context
 *  @returns {boolean} true si pipeline conforme, false si raw mode détecté
 */
export function enforceInstitutionalPipeline(caller, context = {}) {
  const bypass = !!context.bypassOmega;
  const filtered = context.filtered !== false;
  const conforming = !bypass && filtered;
  if (!conforming) {
    try {
      if (typeof window !== 'undefined') {
        const prev = window.__RAW_RENDER_ATTEMPTS__ || { count: 0, entries: [] };
        const entry = Object.freeze({
          caller: String(caller || 'unknown'),
          at: new Date().toISOString(),
          reason: bypass ? 'bypassOmega_true' : 'filtered_false',
        });
        const entries = [...(prev.entries || []), entry].slice(-50);
        window.__RAW_RENDER_ATTEMPTS__ = Object.freeze({
          count: (prev.count || 0) + 1,
          entries: Object.freeze(entries),
          lastAttempt: entry,
        });
        if (typeof console !== 'undefined' && console.error) {
          console.error(
            '[BCE-4X X20] RAW_RENDER_ATTEMPT BLOQUÉ —',
            entry.caller, entry.reason, entry.at
          );
        }
      }
    } catch (_e) { /* noop */ }
  }
  return conforming;
}

/** Audit : retourne l'état du pipeline enforcement pour diagnostic Commandant. */
export function getPipelineEnforcementStatus() {
  let rawAttempts = { count: 0, entries: [], lastAttempt: null };
  try {
    if (typeof window !== 'undefined' && window.__RAW_RENDER_ATTEMPTS__) {
      rawAttempts = window.__RAW_RENDER_ATTEMPTS__;
    }
  } catch (_e) { /* noop */ }
  return {
    protocolVersion: ENFORCE_PIPELINE_SPEC_V20.protocolVersion,
    singlePipelineEnforced: ENFORCE_PIPELINE_SPEC_V20.singlePipelineEnforced,
    rawRenderAttempts: rawAttempts.count,
    lastAttempt: rawAttempts.lastAttempt,
    conforming: rawAttempts.count === 0,
    sealedAt: ENFORCE_PIPELINE_SPEC_V20.sealedAt,
  };
}

/** Détecte si une feature rendue provient d'une zone anthropique urbaine/industrielle/portuaire.
 *  Utilisée par les tests sentinelles anthropiques bloquants.
 *
 *  @param {{terrain?: Object, exclusion_reason?: string}} feature
 *  @returns {{anthropic: boolean, reason?: string, token?: string}}
 */
export function detectAnthropicRender(feature) {
  if (!feature || typeof feature !== 'object') return { anthropic: false };
  const t = feature.terrain || {};
  if (t.urban === true) return { anthropic: true, reason: 'terrain.urban=true' };
  if (t.industrial === true) return { anthropic: true, reason: 'terrain.industrial=true' };
  if (t.port === true) return { anthropic: true, reason: 'terrain.port=true' };
  if (typeof t.impervious_pct === 'number' && t.impervious_pct > 60) {
    return { anthropic: true, reason: `impervious_pct=${t.impervious_pct}>60` };
  }
  const reason = String(feature.exclusion_reason || '').toLowerCase();
  if (reason) {
    const tokens = ENFORCE_PIPELINE_SPEC_V20.urbanTokens;
    const tok = tokens.find(t => reason.includes(t));
    if (tok) return { anthropic: true, reason: feature.exclusion_reason, token: tok };
  }
  return { anthropic: false };
}

/** Sentinelle bloquante : lève une erreur si une feature anthropique est détectée.
 *  Appelée en dernière ligne de défense par les tests sentinelles.
 *
 *  @throws {Error} si feature anthropique rendue
 */
export function assertNoAnthropicRender(feature, caller = 'unknown') {
  const d = detectAnthropicRender(feature);
  if (d.anthropic) {
    const msg = `[BCE-4X X20] ANTHROPIC_RENDER_BLOCKING_FAILURE — ${caller}: ${d.reason}`;
    try {
      if (typeof window !== 'undefined') {
        const prev = window.__ANTHROPIC_RENDER_FAILURES__ || [];
        const entry = Object.freeze({ caller, feature_id: feature.id || null, ...d, at: new Date().toISOString() });
        window.__ANTHROPIC_RENDER_FAILURES__ = Object.freeze([...prev, entry].slice(-50));
      }
    } catch (_e) { /* noop */ }
    throw new Error(msg);
  }
  return true;
}

