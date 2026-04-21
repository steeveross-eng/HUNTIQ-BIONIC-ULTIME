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
// PHASE_XII_SUPRA_S : extension opacity=1.0, weight 4.0, waypoint radius.
export const RENDU_OMEGA = Object.freeze({
  color: '#FF8F00',
  colorName: 'Orange ambre institutionnel',
  weightsAllowedPx: [1.2, 2.0, 3.0, 4.0],
  weightMapping: {
    faible: 1.2, modere: 1.2,
    fort: 2.0,
    critique: 3.0, majeur: 3.0,
    extreme: 4.0, extreme_max: 4.0,
  },
  // SUPRA_S : opacité = 1.00 obligatoire (toute valeur < 1.00 = ERREUR RENDU-Ω)
  opacityMin: 1.0,
  opacityDefault: 1.0,
  geometryType: 'catmull-rom',
  controlPointsMin: 25,
  controlPointsMax: 30,
  segmentMaxM: 20.0,
  angleMaxDeg: 45.0,
  functionalRadiusMinM: 420.0,
  functionalRadiusMaxM: 780.0,
  functionalRadiusNominalM: 600.0,
  minZoom: 13,
  zIndexOrder: ['zones', 'hydrologie', 'terrain', 'corridors', 'salines', 'affuts', 'hotspots', 'vent'],
  forbidAffutInteraction: true,
  forbidDirectionalArrow: true,   // SUPRA_S : aucune flèche directionnelle autorisée
  previewEqualsFinal: true,
  // SUPRA_S ART — micro-biomimétisme
  microOscillationPct: 0.005,     // 0.3–0.7 %, valeur médiane 0.5 %
  microWeightDeltaPx: 0.1,
  luminosityStepPct: 0.20,        // +20 % par niveau d'intensité
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
 */
export function resolveZIndex(layerKey) {
  const idx = RENDU_OMEGA.zIndexOrder.indexOf(String(layerKey).toLowerCase());
  if (idx < 0) return 400;
  return 400 + idx * 10;
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
 *  @param {Array<[lat, lng]>} ctrl  points de contrôle (≥ 2)
 *  @param {number} nOut             nombre de points résultants
 *  @returns {Array<[lat, lng]>}
 */
export function catmullRomResample(ctrl, nOut) {
  if (!Array.isArray(ctrl) || ctrl.length < 2) return ctrl || [];
  const n = Math.max(2, nOut | 0);
  // Étend le path avec points miroirs (tangentes de bord stables)
  const p = [ctrl[0], ...ctrl, ctrl[ctrl.length - 1]];
  const segs = p.length - 3;
  if (segs < 1) return ctrl.slice();
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = (i / (n - 1)) * segs;
    const s = Math.min(segs - 1, Math.floor(t));
    const u = t - s;
    const p0 = p[s], p1 = p[s + 1], p2 = p[s + 2], p3 = p[s + 3];
    // Catmull-Rom uniforme
    const u2 = u * u, u3 = u2 * u;
    const lat = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u +
      (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 +
      (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3);
    const lng = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u +
      (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 +
      (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3);
    out.push([lat, lng]);
  }
  return out;
}

/** Déspike : supprime les points qui produisent un angle > maxAngleDeg
 *  (conservation des extrémités). Itératif jusqu'à stabilité.
 */
export function despikePath(path, maxAngleDeg = RENDU_OMEGA.angleMaxDeg) {
  if (!Array.isArray(path) || path.length < 3) return path || [];
  let cur = path.slice();
  for (let pass = 0; pass < 3; pass++) {
    const next = [cur[0]];
    let removed = 0;
    for (let i = 1; i < cur.length - 1; i++) {
      const a = _angleDegAt(cur[i - 1], cur[i], cur[i + 1]);
      if (a > maxAngleDeg) {
        removed++;
        continue; // drop spike
      }
      next.push(cur[i]);
    }
    next.push(cur[cur.length - 1]);
    cur = next;
    if (removed === 0) break;
  }
  return cur;
}

/** Densifie / décime un path pour qu'aucun segment ne dépasse segmentMaxM.
 *  Insère des points intermédiaires linéaires si besoin, puis re-lisse via Catmull-Rom.
 */
export function enforceSegmentMax(path, segmentMaxM = RENDU_OMEGA.segmentMaxM) {
  if (!Array.isArray(path) || path.length < 2) return path || [];
  const out = [path[0]];
  for (let i = 1; i < path.length; i++) {
    const a = out[out.length - 1], b = path[i];
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

/** Signature par espèce (micro-oscillations) — applique des micro-modulations
 *  au path affiché sans changer la structure globale.
 *  Amplitude maximale limitée à microOscillationPct (défaut 0.5 %).
 */
export function applySpeciesSignature(path, species) {
  if (!Array.isArray(path) || path.length < 3) return path || [];
  const key = String(species || '').toLowerCase();
  const profiles = {
    chevreuil: { freq: 3.5, ampFactor: 1.0 },   // courbes serrées, fréquence haute
    cerf: { freq: 3.5, ampFactor: 1.0 },
    orignal: { freq: 1.2, ampFactor: 0.5 },     // courbes larges, stables
    wapiti: { freq: 1.0, ampFactor: 0.4 },      // courbes longues
    ours_noir: { freq: 2.0, ampFactor: 0.9 },   // irrégularités contrôlées
    ours: { freq: 2.0, ampFactor: 0.9 },
    dindon: { freq: 4.5, ampFactor: 0.6 },      // zigzags subtils
  };
  const prof = profiles[key] || { freq: 2.0, ampFactor: 0.7 };
  const amp = RENDU_OMEGA.microOscillationPct * prof.ampFactor; // 0.5 % × ampFactor
  const out = [path[0]];
  for (let i = 1; i < path.length - 1; i++) {
    const p = path[i];
    // Vecteur normal local
    const prev = path[i - 1], next = path[i + 1];
    const dx = next[1] - prev[1], dy = next[0] - prev[0];
    const len = Math.hypot(dx, dy);
    if (len < 1e-10) { out.push(p); continue; }
    // Normal (perpendiculaire) unitaire en lat/lng
    const nx = -dy / len, ny = dx / len;
    // Oscillation locale phase freq × i
    const phase = Math.sin((i / path.length) * Math.PI * 2 * prof.freq);
    // Échelle lat/lng : amp est un % du pas moyen, approximé par un delta
    const stepApprox = len;
    const offset = amp * stepApprox * phase;
    out.push([p[0] + ny * offset, p[1] + nx * offset]);
  }
  out.push(path[path.length - 1]);
  return out;
}

/** Pipeline complet SUPRA_S pour un corridor affiché :
 *    alignGeometryOmega → applySpeciesSignature → clipToFunctionalRadius
 */
export function prepareDisplayPath(rawPath, opts = {}) {
  const { species, isOrganic = false, center, clip = true } = opts;
  const aligned = alignGeometryOmega(rawPath, { isOrganic });
  const signed = applySpeciesSignature(aligned, species);
  if (!clip || !center) return [signed];
  return clipToFunctionalRadius(signed, center);
}

/** Détection convergence — marque les corridors partageant ≥ 2 extrémités
 *  proches (< mergeRadiusM) comme appartenant à une VEINE PRINCIPALE.
 *  Retourne un Set d'IDs de corridors promus (fusion visuelle côté rendu).
 */
export function detectConvergenceMainVein(corridors, mergeRadiusM = 120) {
  if (!Array.isArray(corridors)) return new Set();
  const endpoints = [];
  corridors.forEach((c, idx) => {
    const p = c?.path;
    if (!Array.isArray(p) || p.length < 2) return;
    endpoints.push({ idx, at: 'start', pt: p[0] });
    endpoints.push({ idx, at: 'end', pt: p[p.length - 1] });
  });
  const promoted = new Set();
  const seen = new Map(); // clé grille ~mergeRadiusM → liste d'endpoints
  const gridKey = (pt) => `${Math.round(pt[0] * 500)}_${Math.round(pt[1] * 500)}`;
  for (const ep of endpoints) {
    const k = gridKey(ep.pt);
    for (const other of (seen.get(k) || [])) {
      if (other.idx !== ep.idx && _haversineM(ep.pt, other.pt) < mergeRadiusM) {
        promoted.add(ep.idx);
        promoted.add(other.idx);
      }
    }
    if (!seen.has(k)) seen.set(k, []);
    seen.get(k).push(ep);
  }
  return promoted;
}

/** Style halo dérivé — halo interne ultra-léger + halo externe adaptatif selon fond.
 *  Le rendu instancie 2 polylines supplémentaires autour de la principale.
 */
export function computeSupraArtHaloSpec(weight, { background = 'forest', isMainVein = false } = {}) {
  // background: forest|snow|water|cover — ajuste l'opacité halo externe
  const bgOpacityMap = { forest: 0.22, snow: 0.30, water: 0.26, cover: 0.20 };
  const externalOpacity = bgOpacityMap[String(background).toLowerCase()] ?? 0.22;
  const mainVeinBoost = isMainVein ? 1.25 : 1.0; // +25 % halo externe si veine principale
  return {
    inner: { weight: weight + 0.4, opacity: 0.55, color: '#FFD380' }, // halo interne (glow chaud)
    external: { weight: (weight + 2.4) * mainVeinBoost, opacity: externalOpacity, color: '#FF8F00' },
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
 *  avec luminosité croissante 3–5 % le long du path (remplace la flèche).
 *  N'est utilisé que si mode inspection bio ON ou pour expression minimale du flux.
 */
export function computeDirectionalLuminosityGradient(path, steps = 6) {
  if (!Array.isArray(path) || path.length < 3) return [];
  const out = [];
  const n = path.length;
  const chunk = Math.max(2, Math.floor(n / steps));
  for (let i = 0; i < steps; i++) {
    const a = i * chunk;
    const b = Math.min(n, (i + 1) * chunk + 1);
    if (b - a < 2) continue;
    const luminosity = 1.0 + 0.03 + (i / (steps - 1)) * 0.02; // 3 → 5 %
    out.push({ sub: path.slice(a, b), luminosityBoost: luminosity });
  }
  return out;
}
