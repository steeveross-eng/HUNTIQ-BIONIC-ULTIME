/**
 * POI Graph Service — API Client M2
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */

const API = process.env.REACT_APP_BACKEND_URL;
const BASE = `${API}/api/v1/poi-graph`;

async function safeFetch(url) {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export const POIGraphAPI = {
  health: () => safeFetch(`${BASE}/health`),
  getNodes: (params = {}) => {
    const p = new URLSearchParams();
    if (params.zone_id) p.set('zone_id', params.zone_id);
    if (params.type) p.set('type', params.type);
    if (params.species) p.set('species', params.species);
    return safeFetch(`${BASE}/nodes?${p}`);
  },
  getNode: (poiId) => safeFetch(`${BASE}/nodes/${poiId}`),
  getNear: (lat, lng, radius, type) => {
    const p = new URLSearchParams();
    if (radius) p.set('radius_m', radius);
    if (type) p.set('type', type);
    return safeFetch(`${BASE}/near/${lat}/${lng}?${p}`);
  },
  getCluster: (lat, lng, radius) => safeFetch(`${BASE}/cluster/${lat}/${lng}/${radius || 5000}`),
  getScore: (poiId) => safeFetch(`${BASE}/score/${poiId}`),
  getEdges: (poiId) => safeFetch(`${BASE}/edges/${poiId}`),
};

export default POIGraphAPI;
