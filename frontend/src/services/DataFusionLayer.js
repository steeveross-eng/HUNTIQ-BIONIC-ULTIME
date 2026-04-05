/**
 * Data Fusion Layer (DFL) — Fusion, normalisation, cache, redistribution
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 *
 * DFL-R1: Retourne Data Contracts V6 valides
 * DFL-R4: ZERO logique metier
 * DFL-R5: Stateless (pas de store interne)
 */

import { PredictiveLayerAPI } from '../modules/intelligence-v6/PredictiveLayerService';
import { POIGraphAPI } from '../modules/intelligence-v6/POIGraphService';
import {
  validateConsolidatedView, validateScoreConsolide, validateHeatmapData,
  validateTimeSeries, validateTrends, validateCorrelation, validateBestTimes,
} from './DataContractsV6';
import { EventBusV6, CHANNELS } from './EventBusV6';

const CACHE_TTL = 5 * 60 * 1000;
const _cache = new Map();

function cacheKey(...args) { return args.join('::'); }

function getCache(key) {
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > CACHE_TTL) { _cache.delete(key); return null; }
  return entry.data;
}

function setCache(key, data) {
  _cache.set(key, { data, ts: Date.now() });
  if (_cache.size > 100) {
    const oldest = _cache.keys().next().value;
    _cache.delete(oldest);
  }
}

export const DataFusionLayer = {

  async fetchConsolidatedView(zoneId, species, date, lat, lng) {
    const key = cacheKey('consolidated', zoneId, species, date);
    const cached = getCache(key);
    if (cached) return cached;

    const [layerRaw, corrRaw] = await Promise.all([
      PredictiveLayerAPI.getLayer(zoneId, species, date, lat, lng),
      PredictiveLayerAPI.getCorrelation(zoneId, species, lat, lng),
    ]);

    const validated = validateConsolidatedView(layerRaw);

    if (corrRaw?.optimal_conditions) {
      validated.meteo.optimal_conditions = corrRaw.optimal_conditions;
    }

    setCache(key, validated);
    EventBusV6.emit(CHANNELS.PREDICTIVE_LAYER_UPDATED, validated);
    EventBusV6.emit(CHANNELS.SOLUNAR_UPDATED, validated.solunar);
    EventBusV6.emit(CHANNELS.METEO_UPDATED, validated.meteo);
    return validated;
  },

  async fetchHeatmapData(zoneId, species, date) {
    const key = cacheKey('heatmap', zoneId, species);
    const cached = getCache(key);
    if (cached) return cached;

    const raw = await PredictiveLayerAPI.getHeatmap(zoneId, species, date);
    const validated = validateHeatmapData(raw);
    setCache(key, validated);
    EventBusV6.emit(CHANNELS.HEATMAP_UPDATED, validated);
    return validated;
  },

  async fetchTimeSeries(zoneId, species, metric) {
    const raw = await PredictiveLayerAPI.getTimeSeries(zoneId, species, metric);
    const validated = validateTimeSeries(raw);
    EventBusV6.emit(CHANNELS.TIMESERIES_UPDATED, validated);
    return validated;
  },

  async fetchTrends(species, zoneId) {
    const key = cacheKey('trends', species, zoneId);
    const cached = getCache(key);
    if (cached) return cached;

    const raw = await PredictiveLayerAPI.getTrends(species, zoneId);
    const validated = validateTrends(raw);
    setCache(key, validated);
    EventBusV6.emit(CHANNELS.TRENDS_UPDATED, validated);
    return validated;
  },

  async fetchCorrelationMatrix(zoneId, species, lat, lng) {
    const key = cacheKey('correlation', zoneId, species);
    const cached = getCache(key);
    if (cached) return cached;

    const raw = await PredictiveLayerAPI.getCorrelation(zoneId, species, lat, lng);
    const validated = validateCorrelation(raw);
    setCache(key, validated);
    EventBusV6.emit(CHANNELS.CORRELATION_UPDATED, validated);
    return validated;
  },

  async fetchBestTimes(zoneId, species, date, lat, lng) {
    const raw = await PredictiveLayerAPI.getBestTimes(zoneId, species, date, lat, lng);
    const validated = validateBestTimes(raw);
    return validated;
  },

  async fetchScoreConsolide(zoneId, species, date, lat, lng) {
    const key = cacheKey('score', zoneId, species, date);
    const cached = getCache(key);
    if (cached) return cached;

    const [layerRaw, clusterRaw] = await Promise.all([
      PredictiveLayerAPI.getLayer(zoneId, species, date, lat, lng),
      POIGraphAPI.getCluster(lat || 46.85, lng || -71.25, 5000),
    ]);

    const peakProb = (layerRaw?.aggregation?.peak_probability ?? 0) * 100;
    const solunarScore = layerRaw?.solunar_context?.solunar_score ?? 50;
    const meteoFactor = (layerRaw?.meteo_context?.activity_multiplier ?? 0.65) * 100;
    const nutritionFactor = 55;
    const poiCount = clusterRaw?.poi_count ?? 0;
    const territoryScore = Math.min(100, poiCount * 10 + (clusterRaw?.density_per_km2 ?? 0) * 5);
    const legalScore = 80;

    const validated = validateScoreConsolide({
      predictive: Math.round(peakProb),
      solunar: Math.round(solunarScore),
      meteo: Math.round(meteoFactor),
      nutrition: nutritionFactor,
      territory: Math.round(territoryScore),
      legal: legalScore,
    });

    setCache(key, validated);
    EventBusV6.emit(CHANNELS.SCORE_CONSOLIDE_UPDATED, validated);
    return validated;
  },

  async fetchPOIEnriched(poiId) {
    const [poiRaw, scoreRaw] = await Promise.all([
      POIGraphAPI.getNode(poiId),
      POIGraphAPI.getScore(poiId),
    ]);

    const node = poiRaw?.node || {};
    const coords = node.location?.coordinates || [0, 0];

    return {
      poi_id: node.poi_id || poiId,
      name: node.name || '',
      type: node.type || '',
      location: { lat: coords[1], lng: coords[0] },
      score: scoreRaw?.score || node.score || { global: 0 },
      prediction: {
        current_probability: 0,
        peak_hour: 0,
        peak_probability: 0,
        best_window: { start: 0, end: 0 },
      },
      nutrition: node.nutrition || {},
      legal: { province: node.province || '', zone_chasse: node.zone_id || '', regulations: [] },
      connections: node.connections?.length ?? 0,
      edge_count: node.edge_count ?? 0,
    };
  },

  clearCache() { _cache.clear(); },
};

export default DataFusionLayer;
