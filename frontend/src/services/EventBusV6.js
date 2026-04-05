/**
 * Event Bus V6 — Publication / Souscription
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 * 
 * 13 channels. Anti-debounce 500ms. Compat V5.
 */

const CHANNELS = {
  PREDICTIVE_LAYER_UPDATED: 'PREDICTIVE_LAYER_UPDATED',
  POI_GRAPH_UPDATED: 'POI_GRAPH_UPDATED',
  HEATMAP_UPDATED: 'HEATMAP_UPDATED',
  TIMESERIES_UPDATED: 'TIMESERIES_UPDATED',
  TRENDS_UPDATED: 'TRENDS_UPDATED',
  CORRELATION_UPDATED: 'CORRELATION_UPDATED',
  SCORE_CONSOLIDE_UPDATED: 'SCORE_CONSOLIDE_UPDATED',
  SOLUNAR_UPDATED: 'SOLUNAR_UPDATED',
  METEO_UPDATED: 'METEO_UPDATED',
  NUTRITION_UPDATED: 'NUTRITION_UPDATED',
  SPECIES_CHANGED: 'SPECIES_CHANGED',
  ZONE_CHANGED: 'ZONE_CHANGED',
  DATE_CHANGED: 'DATE_CHANGED',
};

class EventBusV6Core {
  constructor() {
    this._subscribers = {};
    this._debounceTimers = {};
    this._debounceMs = 500;
    Object.values(CHANNELS).forEach(ch => { this._subscribers[ch] = []; });
  }

  subscribe(channel, callback) {
    if (!this._subscribers[channel]) this._subscribers[channel] = [];
    this._subscribers[channel].push(callback);
    return () => {
      this._subscribers[channel] = this._subscribers[channel].filter(cb => cb !== callback);
    };
  }

  emit(channel, data) {
    if (this._debounceTimers[channel]) clearTimeout(this._debounceTimers[channel]);
    this._debounceTimers[channel] = setTimeout(() => {
      (this._subscribers[channel] || []).forEach(cb => {
        try { cb(data); } catch (e) { console.error(`EventBusV6 [${channel}]:`, e); }
      });
    }, this._debounceMs);
  }

  emitImmediate(channel, data) {
    (this._subscribers[channel] || []).forEach(cb => {
      try { cb(data); } catch (e) { console.error(`EventBusV6 [${channel}]:`, e); }
    });
  }
}

export const EventBusV6 = new EventBusV6Core();
export { CHANNELS };
export default EventBusV6;
