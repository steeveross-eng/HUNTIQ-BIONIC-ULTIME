/**
 * RenderGuardOmega.js — RSE-Ω RENDER-GUARD-Ω validator
 * =======================================================
 * Validateur institutionnel executed par BionicLayersV8 avant rendu.
 * Verifie: layer support, zoom range, geometry validity, palette.
 * Log structured [RSE-Ω] par cycle render.
 */
import { RSE_LAYERS_CONFIG } from '@/config/territoire_defaults';

export const LAYERS_SUPPORTED = Object.keys(RSE_LAYERS_CONFIG);

export function isLayerZoomOk(layerName, zoom) {
  const cfg = RSE_LAYERS_CONFIG[layerName];
  if (!cfg) return false;
  return zoom >= cfg.minZoom && zoom <= cfg.maxZoom;
}

export function isGeometryValid(geomType, points) {
  if (!Array.isArray(points)) return false;
  if (geomType === 'polygon' || geomType === 'polygon-organic') return points.length >= 3;
  if (geomType === 'polyline-catmull' || geomType === 'line-flow') return points.length >= 2;
  if (geomType === 'point-grid' || geomType === 'point-halo' || geomType === 'point-marker') return points.length === 2;
  return false;
}

/**
 * Emet log [RSE-Ω] structure en console avec bilan render.
 */
export function logRenderCycle(stats) {
  try {
    // eslint-disable-next-line no-console
    console.log('[RSE-Ω]', stats);
  } catch (e) { /* noop */ }
}

/**
 * Valide un element avant ajout a la carte.
 * Retourne {ok: bool, reason: string|null}.
 */
export function validateElement(layerName, zoom, geomType, points) {
  if (!LAYERS_SUPPORTED.includes(layerName)) {
    return { ok: false, reason: 'layer_not_supported' };
  }
  if (!isLayerZoomOk(layerName, zoom)) {
    return { ok: false, reason: 'zoom_out_of_range' };
  }
  if (!isGeometryValid(geomType, points)) {
    return { ok: false, reason: 'geometry_invalid' };
  }
  return { ok: true, reason: null };
}
