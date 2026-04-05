/**
 * GestionnairePositionService — Source Unique Position LIVE
 * Directive x7100-M4 Phase C | BCE-4X GOLDEN V6+
 *
 * ZERO DOUBLON : remplace les 5 implémentations fragmentées par une source unique.
 * Consomme : navigator.geolocation (natif)
 * Émet : DC-12 (LivePosition) via EventBus EB-17 (LIVE_POSITION_UPDATED)
 * Distribue à : CARTE, Groupe, GPS Tracking, Replay, Parcours, SECOURS
 */

import DataFusionLayer from '../../../services/DataFusionLayer';

const API = process.env.REACT_APP_BACKEND_URL;

class GestionnairePositionServiceCore {
  constructor() {
    this._watchId = null;
    this._active = false;
    this._consent = 'none';
    this._territoryId = '';
    this._userId = '';
    this._lastPosition = null;
    this._listeners = [];
    this._sendInterval = null;
  }

  get isActive() { return this._active; }
  get consent() { return this._consent; }
  get lastPosition() { return this._lastPosition; }

  setUser(userId, consent, territoryId) {
    this._userId = userId;
    this._consent = consent || 'none';
    this._territoryId = territoryId || '';
  }

  grantPermanentConsent() {
    this._consent = 'permanent';
  }

  start() {
    if (this._active || !navigator.geolocation) return false;
    if (this._consent === 'none') return false;

    this._active = true;
    this._watchId = navigator.geolocation.watchPosition(
      (pos) => this._onPosition(pos),
      (err) => console.warn('GestionnairePosition: GPS error', err.message),
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 }
    );

    this._sendInterval = setInterval(() => this._syncToServer(), 30000);
    return true;
  }

  stop() {
    if (this._watchId !== null) {
      navigator.geolocation.clearWatch(this._watchId);
      this._watchId = null;
    }
    if (this._sendInterval) {
      clearInterval(this._sendInterval);
      this._sendInterval = null;
    }
    this._active = false;
  }

  _onPosition(pos) {
    const data = {
      user_id: this._userId,
      lat: pos.coords.latitude,
      lng: pos.coords.longitude,
      accuracy: pos.coords.accuracy,
      heading: pos.coords.heading,
      speed: pos.coords.speed,
      altitude: pos.coords.altitude,
      timestamp: new Date().toISOString(),
      status: 'active',
      consent: this._consent,
      territory_id: this._territoryId,
    };

    this._lastPosition = data;
    DataFusionLayer.emitLivePosition(data);
    this._listeners.forEach(fn => { try { fn(data); } catch (e) { /* noop */ } });
  }

  async _syncToServer() {
    if (!this._lastPosition) return;
    try {
      await fetch(`${API}/api/v1/gestionnaire/position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this._lastPosition),
      });
    } catch { /* Offline tolerance */ }
  }

  onPosition(callback) {
    this._listeners.push(callback);
    return () => {
      this._listeners = this._listeners.filter(fn => fn !== callback);
    };
  }
}

const GestionnairePositionService = new GestionnairePositionServiceCore();
export default GestionnairePositionService;
