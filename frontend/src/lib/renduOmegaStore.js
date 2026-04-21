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
export const RENDU_OMEGA = Object.freeze({
  color: '#FF8F00',
  colorName: 'Orange ambre institutionnel',
  weightsAllowedPx: [1.2, 2.0, 3.0],
  weightMapping: {
    faible: 1.2, modere: 1.2,
    fort: 2.0,
    critique: 3.0, majeur: 3.0,
  },
  opacityMin: 0.75,
  opacityDefault: 0.85,
  geometryType: 'catmull-rom',
  controlPointsMin: 25,
  controlPointsMax: 30,
  segmentMaxM: 20.0,
  angleMaxDeg: 45.0,
  functionalRadiusMinM: 420.0,
  functionalRadiusMaxM: 780.0,
  minZoom: 13,
  zIndexOrder: ['zones', 'hydrologie', 'terrain', 'corridors', 'salines', 'affuts', 'hotspots', 'vent'],
  forbidAffutInteraction: true,
  previewEqualsFinal: true,
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
 *   - 'critique'|'majeur'|'extreme'            → 3.0 px
 *   - 'fort'|'intense'                         → 2.0 px
 *   - 'faible'|'modere'|'normal'|'saisonnier'  → 1.2 px
 *   - numérique 0-100                           → 1.2 (<33) / 2.0 (<66) / 3.0 (≥66)
 */
export function resolveCorridorWeight(intensity) {
  if (typeof intensity === 'number') {
    if (intensity >= 66) return 3.0;
    if (intensity >= 33) return 2.0;
    return 1.2;
  }
  if (!intensity) return 1.2;
  const key = String(intensity).toLowerCase().trim();
  if (['critique', 'majeur', 'extreme', 'critical'].includes(key)) return 3.0;
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
    opacity: RENDU_OMEGA.opacityDefault, // 0.85 (≥ 0.75 min)
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
  // Clamp dans les valeurs RENDU-Ω (1.2 / 2.0 / 3.0 via arrondi au plus proche)
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
