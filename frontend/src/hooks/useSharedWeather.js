/**
 * BCE-4X — Hook Meteo Partage
 * ============================
 * Hook unifie pour TOUS les modules BIONIC.
 * Se branche sur useWeatherStore (source unique).
 * 
 * Usage:
 *   const { weather, wind, conditions, refresh } = useSharedWeather(lat, lng);
 */
import { useEffect, useCallback, useRef } from 'react';
import useWeatherStore from '@/stores/useWeatherStore';

const WIND_DIRECTIONS = [
  'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
  'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO'
];

const getWindLabel = (deg) => {
  if (deg == null) return '--';
  const idx = Math.round(((deg % 360) + 360) % 360 / 22.5) % 16;
  return WIND_DIRECTIONS[idx];
};

const getConditionLabel = (code) => {
  if (!code) return 'Inconnu';
  const c = parseInt(code);
  if (c === 800) return 'Ciel degage';
  if (c >= 801 && c <= 804) return 'Nuageux';
  if (c >= 500 && c <= 531) return 'Pluie';
  if (c >= 600 && c <= 622) return 'Neige';
  if (c >= 200 && c <= 232) return 'Orage';
  if (c >= 300 && c <= 321) return 'Bruine';
  if (c >= 701 && c <= 781) return 'Brouillard';
  return 'Variable';
};

const getWindScore = (speed, gusts) => {
  // Score vent pour la chasse (0-100, 100 = conditions parfaites)
  const s = speed || 0;
  const g = gusts || 0;
  if (s < 5) return 95;     // Calme
  if (s < 10) return 85;    // Leger
  if (s < 20) return 70;    // Modere
  if (s < 30) return 50;    // Fort
  if (s < 40) return 30;    // Tres fort
  return 15;                // Tempete
};

const useSharedWeather = (lat, lng, options = {}) => {
  const { autoFetch = true, liveMode = false } = options;
  const mountedRef = useRef(true);

  const current = useWeatherStore(s => s.current);
  const forecast = useWeatherStore(s => s.forecast);
  const influence = useWeatherStore(s => s.influence);
  const windField = useWeatherStore(s => s.windField);
  const loading = useWeatherStore(s => s.loading);
  const error = useWeatherStore(s => s.error);
  const fetchAll = useWeatherStore(s => s.fetchAll);
  const startPolling = useWeatherStore(s => s.startPolling);
  const stopPolling = useWeatherStore(s => s.stopPolling);

  // Fetch initial + polling
  useEffect(() => {
    mountedRef.current = true;
    if (autoFetch && lat && lng) {
      fetchAll(lat, lng);
      const interval = liveMode ? 60000 : 600000;
      startPolling(lat, lng, interval);
    }
    return () => {
      mountedRef.current = false;
      stopPolling();
    };
  }, [lat, lng, autoFetch, liveMode, fetchAll, startPolling, stopPolling]);

  const refresh = useCallback(() => {
    if (lat && lng) fetchAll(lat, lng, true);
  }, [lat, lng, fetchAll]);

  // Donnees derivees — vent
  const windSpeed = current?.wind_speed_kmh ?? null;
  const windDir = current?.wind_direction_deg ?? null;
  const windGusts = current?.wind_gust_kmh ?? 0;
  const windLabel = getWindLabel(windDir);
  const windScore = getWindScore(windSpeed, windGusts);

  // Conditions
  const temp = current?.temperature_c ?? null;
  const apparentTemp = current?.apparent_temperature_c ?? null;
  const humidity = current?.humidity_pct ?? null;
  const pressure = current?.pressure_hpa ?? null;
  const weatherCode = current?.weather_code;
  const conditionLabel = getConditionLabel(weatherCode);
  const description = current?.description ?? conditionLabel;
  const icon = current?.icon;
  const visibility = current?.visibility_m ?? null;
  const uvIndex = current?.uv_index ?? null;
  const dewPoint = current?.dew_point_c ?? null;
  const sunrise = current?.sunrise ?? null;
  const sunset = current?.sunset ?? null;
  const huntingScore = current?.hunting_score ?? null;

  return {
    // Donnees brutes
    current,
    forecast,
    influence,
    windField,

    // Etat
    loading,
    error,
    hasData: !!current,

    // Meteo generale
    weather: {
      temperature: temp,
      apparentTemperature: apparentTemp,
      humidity,
      pressure,
      description,
      conditionLabel,
      icon,
      weatherCode,
      visibility,
      uvIndex,
      dewPoint,
      sunrise,
      sunset,
    },

    // Vent (bloc unifie)
    wind: {
      speed: windSpeed,
      direction: windDir,
      directionLabel: windLabel,
      gusts: windGusts,
      score: windScore,
    },

    // Score meteo chasse (v3)
    huntingScore,

    // Previsions
    hourly: forecast?.forecasts?.slice(0, 24) || [],

    // Influence sur scores
    influenceData: influence,

    // WindField pour animation carte
    windFieldData: windField,

    // Actions
    refresh,
  };
};

export default useSharedWeather;
