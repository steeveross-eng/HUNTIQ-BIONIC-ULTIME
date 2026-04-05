/**
 * SecoursService — Urgences Terrain
 * Directive x7100-M4 Phase C | BCE-4X GOLDEN V6+
 *
 * Émet : DC-14 (EmergencyAlert) via EventBus EB-19 (EMERGENCY_ALERT)
 * Le bouton SECOURS = consentement explicite immédiat pour transmettre la position.
 */

import DataFusionLayer from '../../../services/DataFusionLayer';
import GestionnairePositionService from './GestionnairePositionService';

const API = process.env.REACT_APP_BACKEND_URL;

const SecoursService = {
  async triggerAlert(userId, userName, message, territoryId) {
    const pos = GestionnairePositionService.lastPosition;
    const alertData = {
      alert_id: `alert_${Date.now()}_${userId}`,
      user_id: userId,
      user_name: userName || userId,
      position: pos ? { lat: pos.lat, lng: pos.lng, accuracy: pos.accuracy } : { lat: 0, lng: 0, accuracy: 0 },
      timestamp: new Date().toISOString(),
      status: 'active',
      type: 'secours',
      message: message || 'URGENCE — Demande de secours',
      channel_id: `emergency_${Date.now()}`,
      territory_id: territoryId || pos?.territory_id || '',
      responders: [],
    };

    DataFusionLayer.emitEmergencyAlert(alertData);

    if (!GestionnairePositionService.isActive) {
      GestionnairePositionService.setUser(userId, 'emergency', territoryId);
      GestionnairePositionService.grantPermanentConsent();
      GestionnairePositionService.start();
    }

    try {
      await fetch(`${API}/api/v1/gestionnaire/emergency`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alertData),
      });
    } catch { /* Offline tolerance */ }

    return alertData;
  },

  async acknowledgeAlert(alertId, responderId, responderName) {
    try {
      const r = await fetch(`${API}/api/v1/gestionnaire/emergency/${alertId}/ack`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: responderId, name: responderName }),
      });
      if (!r.ok) return null;
      return r.json();
    } catch { return null; }
  },

  async resolveAlert(alertId) {
    try {
      const r = await fetch(`${API}/api/v1/gestionnaire/emergency/${alertId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      if (!r.ok) return null;
      return r.json();
    } catch { return null; }
  },
};

export default SecoursService;
