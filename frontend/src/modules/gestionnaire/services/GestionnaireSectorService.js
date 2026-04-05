/**
 * GestionnaireSectorService — Gestion Secteurs/Blocs
 * Directive x7100-M4 Phase C | BCE-4X GOLDEN V6+
 *
 * Émet : DC-13 (SectorStatus) via EventBus EB-18 (SECTOR_UPDATED)
 */

import DataFusionLayer from '../../../services/DataFusionLayer';

const API = process.env.REACT_APP_BACKEND_URL;

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

const GestionnaireSectorService = {
  async getSectors(territoryId) {
    const data = await safeFetch(`${API}/api/v1/gestionnaire/sectors/${territoryId}`);
    if (data?.sectors) {
      data.sectors.forEach(s => DataFusionLayer.emitSectorUpdate(s));
    }
    return data;
  },

  async updateSectorStatus(sectorId, status) {
    const data = await safePost(`${API}/api/v1/gestionnaire/sectors/${sectorId}/status`, { status });
    if (data?.sector) DataFusionLayer.emitSectorUpdate(data.sector);
    return data;
  },

  async assignHunter(sectorId, userId) {
    return safePost(`${API}/api/v1/gestionnaire/sectors/${sectorId}/assign`, { user_id: userId });
  },

  async removeHunter(sectorId, userId) {
    return safePost(`${API}/api/v1/gestionnaire/sectors/${sectorId}/remove`, { user_id: userId });
  },
};

export default GestionnaireSectorService;
