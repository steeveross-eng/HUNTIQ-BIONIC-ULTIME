/**
 * useBionicWeather Hook — BCE-4X UNIFIED v3.0
 * ==============================================
 * SOURCE UNIQUE: useWeatherStore (Weather Engine V3)
 * ZERO pipeline V1, ZERO fallback Open-Meteo direct, ZERO divergence.
 *
 * BCE-4X WEATHER UNIFICATION — STEEVE-MAX directive 28 Mars 2026:
 *   - Supprime fetchWeatherData legacy (/api/v1/weather/now)
 *   - Supprime fetchFromOpenMeteo direct
 *   - Source unique: /api/v3/weather/current via useWeatherStore
 *   - Interface de retour IDENTIQUE pour compatibilite zero-regression
 */

import { useEffect, useCallback, useRef, useMemo } from 'react';
import useWeatherStore from '@/stores/useWeatherStore';

const WIND_DIRECTIONS = [
  'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
  'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO'
];

const getWindDirectionText = (degrees) => {
  if (degrees == null) return '--';
  const index = Math.round(((degrees % 360) + 360) % 360 / 22.5) % 16;
  return WIND_DIRECTIONS[index];
};

const getWeatherDescription = (description, code) => {
  if (description) return description;
  if (code == null && code !== 0) return 'Conditions inconnues';
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

const THERMAL_STATES = {
  STABLE: 'stable',
  ASCENDING: 'ascending',
  DESCENDING: 'descending'
};

const useBionicWeather = (latitude, longitude, options = {}) => {
  const {
    autoFetch = true,
    pollInterval = 10 * 60 * 1000,
    enabled = true
  } = options;

  const isMountedRef = useRef(true);

  // BCE-4X: Source UNIQUE — useWeatherStore (V3)
  const current = useWeatherStore(s => s.current);
  const loading = useWeatherStore(s => s.loading);
  const error = useWeatherStore(s => s.error);
  const source = useWeatherStore(s => s.source);
  const fetchAll = useWeatherStore(s => s.fetchAll);
  const startPolling = useWeatherStore(s => s.startPolling);
  const stopPolling = useWeatherStore(s => s.stopPolling);

  // Fetch initial + polling via V3
  useEffect(() => {
    isMountedRef.current = true;
    if (autoFetch && enabled && latitude && longitude) {
      fetchAll(latitude, longitude);
      startPolling(latitude, longitude, pollInterval);
    }
    return () => {
      isMountedRef.current = false;
      stopPolling();
    };
  }, [autoFetch, enabled, latitude, longitude, pollInterval, fetchAll, startPolling, stopPolling]);

  const refresh = useCallback(() => {
    if (latitude && longitude) fetchAll(latitude, longitude, true);
  }, [latitude, longitude, fetchAll]);

  // Construire l'objet weather compatible avec l'ancienne interface
  const weather = useMemo(() => {
    if (!current) return null;
    const desc = getWeatherDescription(current.description, current.weather_code);
    return {
      timestamp: new Date().toISOString(),
      source: source || 'weather-v3',
      windDirectionDeg: current.wind_direction_deg,
      windSpeedKmh: current.wind_speed_kmh,
      windGustsKmh: current.wind_gust_kmh,
      temperatureC: current.temperature_c,
      apparentTemperatureC: current.apparent_temperature_c ?? current.feels_like_c,
      humidityPercent: current.humidity_pct,
      pressureHpa: current.pressure_hpa,
      precipitationMm: current.precipitation_mm ?? 0,
      cloudCoverPercent: current.cloud_cover_pct ?? 0,
      weatherCode: current.weather_code,
      conditionText: desc,
      sunrise: current.sunrise,
      sunset: current.sunset,
      tempMaxC: current.temp_max_c,
      tempMinC: current.temp_min_c,
      thermalState: THERMAL_STATES.STABLE,
      thermalRiskLevel: 0,
      frontType: 'none',
      hourlyForecast: [],
      huntingConditions: {
        score: typeof current.hunting_score === 'object'
          ? current.hunting_score?.overall ?? 0
          : current.hunting_score ?? 0,
        rating: 'unknown',
        factors: [],
      },
    };
  }, [current, source]);

  // Donnees derivees — vent
  const windInfo = useMemo(() => {
    if (!current) return null;
    return {
      direction: getWindDirectionText(current.wind_direction_deg),
      directionDeg: current.wind_direction_deg,
      speed: current.wind_speed_kmh,
      gusts: current.wind_gust_kmh ?? 0,
    };
  }, [current]);

  // Donnees derivees — thermiques
  const thermalInfo = useMemo(() => ({
    state: THERMAL_STATES.STABLE,
    riskLevel: 0,
    stateLabel: 'Stables',
  }), []);

  const huntingScore = weather?.huntingConditions?.score || 0;
  const huntingRating = weather?.huntingConditions?.rating || 'unknown';

  return {
    // Donnees meteo completes (V3)
    weather,

    // Etat
    isLoading: loading,
    error,
    lastUpdate: current ? new Date().toISOString() : null,

    // Donnees simplifiees (V3 source unique)
    temperature: current?.temperature_c ?? null,
    humidity: current?.humidity_pct ?? null,
    pressure: current?.pressure_hpa ?? null,
    precipitation: current?.precipitation_mm ?? 0,
    cloudCover: current?.cloud_cover_pct ?? 0,
    weatherCode: current?.weather_code ?? null,
    weatherDescription: weather
      ? getWeatherDescription(current?.description, current?.weather_code)
      : null,

    // Vent
    windInfo,

    // Thermiques
    thermalInfo,

    // Soleil
    sunrise: current?.sunrise ?? null,
    sunset: current?.sunset ?? null,

    // Front meteo
    frontType: 'none',

    // Analyse chasse
    huntingScore,
    huntingRating,
    huntingFactors: [],

    // Prochaine fenetre optimale
    nextOptimalWindow: null,

    // Previsions horaires
    hourlyForecast: [],

    // Actions
    refresh,
    startPolling: () => { if (latitude && longitude) startPolling(latitude, longitude, pollInterval); },
    stopPolling,

    // Statut
    isEnabled: enabled,
    hasData: !!current,
  };
};

export default useBionicWeather;
