/**
 * Predictive Layer Service — API Client M3
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */

const API = process.env.REACT_APP_BACKEND_URL;
const BASE = `${API}/api/v1/predict-layer`;

async function safeFetch(url) {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

async function safePost(url, body) {
  try {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export const PredictiveLayerAPI = {
  health: () => safeFetch(`${BASE}/health`),
  getLayer: (zoneId, species, date, lat, lng) => {
    const p = new URLSearchParams();
    if (date) p.set('target_date', date);
    if (lat) p.set('lat', lat);
    if (lng) p.set('lng', lng);
    return safeFetch(`${BASE}/zone/${zoneId}/species/${species}?${p}`);
  },
  getAtPoint: (lat, lng, species, date) => {
    const p = date ? `?target_date=${date}` : '';
    return safeFetch(`${BASE}/at/${lat}/${lng}/species/${species}${p}`);
  },
  getHeatmap: (zoneId, species, date) => {
    const p = new URLSearchParams({ species });
    if (date) p.set('target_date', date);
    return safeFetch(`${BASE}/heatmap/${zoneId}?${p}`);
  },
  getBestTimes: (zoneId, species, date, lat, lng) => {
    const p = new URLSearchParams();
    if (date) p.set('target_date', date);
    if (lat) p.set('lat', lat);
    if (lng) p.set('lng', lng);
    return safeFetch(`${BASE}/best-times/${zoneId}/${species}?${p}`);
  },
  getTimeSeries: (zoneId, species, metric, limit) => {
    const p = new URLSearchParams({ metric: metric || 'activity_index' });
    if (limit) p.set('limit', limit);
    return safeFetch(`${BASE}/timeseries/${zoneId}/${species}?${p}`);
  },
  getTrends: (species, zoneId, year) => {
    const p = new URLSearchParams();
    if (zoneId) p.set('zone_id', zoneId);
    if (year) p.set('year', year);
    return safeFetch(`${BASE}/trends/${species}?${p}`);
  },
  getCorrelation: (zoneId, species, lat, lng) => {
    const p = new URLSearchParams({ species: species || 'orignal' });
    if (lat) p.set('lat', lat);
    if (lng) p.set('lng', lng);
    return safeFetch(`${BASE}/correlation/meteo/${zoneId}?${p}`);
  },
  forceCompute: (zoneId, species, date) =>
    safePost(`${BASE}/compute/${zoneId}`, { species, target_date: date }),
};

export default PredictiveLayerAPI;
