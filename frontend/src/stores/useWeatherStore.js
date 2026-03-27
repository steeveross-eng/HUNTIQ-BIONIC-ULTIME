/**
 * BCE-4X — Store Meteo Centralise (Zustand)
 * ==========================================
 * SOURCE DE VERITE UNIQUE pour toutes les donnees meteo dans BIONIC.
 * Strategie: Backend OWM (cache 30min) -> Fallback Open-Meteo (gratuit)
 * 
 * Consommateurs:
 *   - TERRITOIRE (carte, animation vent, overlays)
 *   - SUPRA PANEL
 *   - INTELLIGENCE  
 *   - COMMANDER
 *   - TerritoireHeader
 *   - WeatherPanel (bloc meteo intelligent)
 */
import { create } from 'zustand';

const API = process.env.REACT_APP_BACKEND_URL;
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Fetch meteorologique avec fallback Open-Meteo.
 * Backend OWM -> Open-Meteo (gratuit, sans cle)
 */
const fetchWeatherWithFallback = async (lat, lng) => {
  // Tentative Weather Engine v3 (backend)
  try {
    const resp = await fetch(`${API}/api/v3/weather/current?lat=${lat}&lng=${lng}`);
    if (resp.ok) {
      const data = await resp.json();
      if (data && data.temperature_c != null) {
        // Normalisation v3: ajouter description, hunting_score plat, visibility_km
        return {
          source: 'weather-v3',
          data: {
            ...data,
            description: data.description || getWeatherLabel(data.weather_code),
            visibility_km: data.visibility_km ?? (data.visibility_m != null ? Math.round(data.visibility_m / 100) / 10 : null),
            hunting_score_overall: typeof data.hunting_score === 'object' ? data.hunting_score.overall : data.hunting_score,
            hunting_score_label: typeof data.hunting_score === 'object' ? data.hunting_score.label : null,
            hunting_score_components: typeof data.hunting_score === 'object' ? data.hunting_score.components : null,
          },
        };
      }
    }
  } catch (e) { /* fallthrough to v1 */ }

  // Fallback Weather v1 (backend OWM)
  try {
    const resp = await fetch(`${API}/api/v1/weather/now?lat=${lat}&lng=${lng}`);
    if (resp.ok) {
      const data = await resp.json();
      if (data && data.temperature_c != null) return { source: 'owm', data };
    }
  } catch (e) { /* fallthrough */ }

  // Fallback Open-Meteo (gratuit)
  try {
    const params = new URLSearchParams({
      latitude: lat, longitude: lng,
      current: 'temperature_2m,relative_humidity_2m,precipitation,weather_code,cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
      timezone: 'America/Toronto',
    });
    const resp = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`);
    if (resp.ok) {
      const raw = await resp.json();
      const c = raw.current;
      return {
        source: 'open-meteo',
        data: {
          temperature_c: c?.temperature_2m,
          humidity_pct: c?.relative_humidity_2m,
          pressure_hpa: c?.surface_pressure,
          wind_speed_kmh: c?.wind_speed_10m,
          wind_direction_deg: c?.wind_direction_10m,
          wind_gust_kmh: c?.wind_gusts_10m,
          precipitation_mm: c?.precipitation,
          cloud_cover_pct: c?.cloud_cover,
          weather_code: c?.weather_code,
          description: getWeatherLabel(c?.weather_code),
        },
      };
    }
  } catch (e) { /* all sources failed */ }

  return null;
};

const getWeatherLabel = (code) => {
  if (!code && code !== 0) return 'Inconnu';
  const c = parseInt(code);
  if (c === 0) return 'Ciel degage';
  if (c <= 3) return 'Partiellement nuageux';
  if (c >= 45 && c <= 48) return 'Brouillard';
  if (c >= 51 && c <= 57) return 'Bruine';
  if (c >= 61 && c <= 67) return 'Pluie';
  if (c >= 71 && c <= 77) return 'Neige';
  if (c >= 80 && c <= 82) return 'Averses';
  if (c >= 95) return 'Orage';
  return 'Variable';
};

const useWeatherStore = create((set, get) => ({
  // Donnees meteo normalisees
  current: null,
  forecast: null,
  influence: null,
  windField: null,
  source: null,

  // Etat
  loading: false,
  error: null,
  lastFetchCoords: null,
  lastFetchTime: null,
  pollIntervalId: null,

  fetchAll: async (lat, lng, force = false) => {
    if (!lat || !lng) return;

    const state = get();
    const now = Date.now();
    const coordKey = `${lat.toFixed(4)},${lng.toFixed(4)}`;

    if (
      !force &&
      state.lastFetchCoords === coordKey &&
      state.lastFetchTime &&
      now - state.lastFetchTime < CACHE_TTL_MS &&
      state.current
    ) {
      return;
    }

    set({ loading: true, error: null });

    try {
      // Fetch meteo avec fallback
      const weatherResult = await fetchWeatherWithFallback(lat, lng);

      // Fetch windfield en parallele (non-bloquant)
      let windField = null;
      try {
        const windRes = await fetch(`${API}/api/v1/bionic/weather-shadow/windfield`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ center_lat: lat, center_lng: lng }),
        });
        if (windRes.ok) windField = await windRes.json();
      } catch (e) { /* non-bloquant */ }

      set({
        current: weatherResult?.data || null,
        source: weatherResult?.source || null,
        windField,
        loading: false,
        lastFetchCoords: coordKey,
        lastFetchTime: now,
      });
    } catch (err) {
      set({ loading: false, error: err.message });
    }
  },

  startPolling: (lat, lng, intervalMs = 600000) => {
    const state = get();
    if (state.pollIntervalId) clearInterval(state.pollIntervalId);
    const id = setInterval(() => { get().fetchAll(lat, lng, true); }, intervalMs);
    set({ pollIntervalId: id });
  },

  stopPolling: () => {
    const state = get();
    if (state.pollIntervalId) {
      clearInterval(state.pollIntervalId);
      set({ pollIntervalId: null });
    }
  },
}));

export default useWeatherStore;
