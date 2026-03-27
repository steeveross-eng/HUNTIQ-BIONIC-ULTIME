/**
 * AdvancedWeatherWidget — BCE-4X PHASE 2
 * SOURCE UNIQUE: useWeatherStore (Weather Engine v3)
 * ZERO auto-refresh interne. ZERO fallback. ZERO smoothing.
 * Lecture DIRECTE du store Zustand — aucune transformation.
 */
import React, { useEffect, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import {
  Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, Eye,
  Moon, RefreshCw, MapPin, Target
} from 'lucide-react';
import useWeatherStore from '../../../stores/useWeatherStore';

const getWeatherIconFromCode = (code, size = 'h-8 w-8') => {
  if (code == null) return <Cloud className={`${size} text-gray-400`} />;
  const c = parseInt(code);
  if (c === 0) return <Sun className={`${size} text-yellow-400`} />;
  if (c <= 3) return <Cloud className={`${size} text-gray-300`} />;
  if (c >= 45 && c <= 48) return <Cloud className={`${size} text-gray-500`} />;
  if (c >= 51 && c <= 67) return <CloudRain className={`${size} text-blue-400`} />;
  if (c >= 71 && c <= 77) return <Cloud className={`${size} text-blue-200`} />;
  if (c >= 80 && c <= 82) return <CloudRain className={`${size} text-blue-400`} />;
  if (c >= 95) return <CloudRain className={`${size} text-purple-400`} />;
  return <Cloud className={`${size} text-gray-400`} />;
};

const getActivityColor = (level) => {
  const colors = { peak: 'bg-green-500', high: 'bg-emerald-500', moderate: 'bg-yellow-500', low: 'bg-red-500' };
  return colors[level] || 'bg-gray-500';
};

const getActivityLabel = (level) => {
  const labels = { peak: 'Optimale', high: 'Elevee', moderate: 'Moderee', low: 'Faible' };
  return labels[level] || level || 'N/A';
};

const getWindDirectionText = (deg) => {
  if (deg == null) return '';
  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'];
  return dirs[Math.round(deg / 45) % 8];
};

/**
 * BCE-4X Phase 2 — Widget meteo unifie
 * Lit EXCLUSIVEMENT useWeatherStore. Aucun fetch propre. Aucun state local meteo.
 */
const AdvancedWeatherWidget = ({
  lat = 46.8139,
  lng = -71.2080,
  compact = false
}) => {
  // BCE-4X: Lecture SEULE du store v3
  const weatherCurrent = useWeatherStore(s => s.current);
  const weatherSource = useWeatherStore(s => s.source);
  const weatherLoading = useWeatherStore(s => s.loading);
  const weatherError = useWeatherStore(s => s.error);
  const fetchAll = useWeatherStore(s => s.fetchAll);

  // Si le store est vide, declencher UN SEUL fetch initial (pas d'auto-refresh)
  useEffect(() => {
    if (!weatherCurrent && !weatherLoading) {
      fetchAll(lat, lng);
    }
  }, [weatherCurrent, weatherLoading, fetchAll, lat, lng]);

  // Hunting conditions calculees depuis le store (deterministe, zero API)
  const huntingConditions = useMemo(() => {
    if (!weatherCurrent) return null;
    const w = weatherCurrent;
    const temp = w.temperature_c ?? 0;
    const wind = w.wind_speed_kmh ?? 0;
    const press = w.pressure_hpa ?? 1013;
    const hum = w.humidity_pct ?? 50;

    const tempScore = temp >= -5 && temp <= 10 ? 85 : temp >= -15 && temp <= 20 ? 60 : 30;
    const windScore = wind <= 15 ? 80 : wind <= 25 ? 55 : 25;
    const pressScore = press >= 1010 && press <= 1030 ? 85 : press >= 990 ? 60 : 35;
    const humScore = hum >= 40 && hum <= 80 ? 80 : hum >= 20 && hum <= 95 ? 55 : 30;
    const overall = Math.round(tempScore * 0.3 + windScore * 0.25 + pressScore * 0.25 + humScore * 0.2);

    const level = overall >= 80 ? 'peak' : overall >= 60 ? 'high' : overall >= 40 ? 'moderate' : 'low';

    return { overall_score: overall, activity_level: level };
  }, [weatherCurrent]);

  if (weatherLoading && !weatherCurrent) {
    return (
      <Card className="bg-gray-900/50 border-gray-700" data-testid="weather-widget-loading">
        <CardContent className="p-6 flex items-center justify-center">
          <RefreshCw className="h-8 w-8 text-amber-500 animate-spin" />
          <span className="ml-3 text-gray-400">Chargement meteo...</span>
        </CardContent>
      </Card>
    );
  }

  if (weatherError && !weatherCurrent) {
    return (
      <Card className="bg-gray-900/50 border-red-500/30" data-testid="weather-widget-error">
        <CardContent className="p-6 text-center">
          <Cloud className="h-12 w-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-400">{weatherError}</p>
          <Button
            variant="ghost"
            onClick={() => fetchAll(lat, lng, true)}
            className="mt-4 text-amber-400"
            data-testid="weather-retry-btn"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!weatherCurrent) return null;

  // Lecture DIRECTE du store — aucune transformation, aucun smoothing
  const w = weatherCurrent;

  return (
    <Card className="bg-gray-900/50 border-gray-700" data-testid="advanced-weather-widget">
      {/* Header */}
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getWeatherIconFromCode(w.weather_code, 'h-10 w-10')}
            <div>
              <CardTitle className="text-2xl text-white flex items-center gap-2">
                {w.temperature_c != null ? Math.round(w.temperature_c) : '--'}°C
                <span className="text-base text-gray-400 font-normal">
                  Ressenti {w.feels_like_c != null ? Math.round(w.feels_like_c) : Math.round(w.temperature_c ?? 0)}°C
                </span>
              </CardTitle>
              <p className="text-gray-400 capitalize">{w.description || 'N/A'}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-gray-400 text-sm">
              <MapPin className="h-4 w-4" />
              <span>{lat.toFixed(2)}, {lng.toFixed(2)}</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => fetchAll(lat, lng, true)}
              className="text-gray-500 hover:text-amber-400 p-1"
              data-testid="weather-refresh-btn"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Wind className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-xs text-gray-500">Vent</p>
              <p className="text-white font-medium" data-testid="weather-wind">
                {w.wind_speed_kmh != null ? Math.round(w.wind_speed_kmh) : '--'} km/h {getWindDirectionText(w.wind_direction_deg)}
              </p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Droplets className="h-5 w-5 text-cyan-400" />
            <div>
              <p className="text-xs text-gray-500">Humidite</p>
              <p className="text-white font-medium" data-testid="weather-humidity">
                {w.humidity_pct != null ? Math.round(w.humidity_pct) : '--'}%
              </p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Thermometer className="h-5 w-5 text-orange-400" />
            <div>
              <p className="text-xs text-gray-500">Pression</p>
              <p className="text-white font-medium" data-testid="weather-pressure">
                {w.pressure_hpa != null ? Math.round(w.pressure_hpa) : '--'} hPa
              </p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Eye className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Visibilite</p>
              <p className="text-white font-medium" data-testid="weather-visibility">
                {w.visibility_km != null ? w.visibility_km : '--'} km
              </p>
            </div>
          </div>
        </div>

        {/* Hunting Analysis — from store data, deterministic */}
        {huntingConditions && (
          <div className="bg-amber-900/20 border border-amber-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-amber-400" />
                <span className="text-amber-400 font-semibold">Conditions de Chasse</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-white" data-testid="weather-hunting-score">
                  {huntingConditions.overall_score}
                </span>
                <span className="text-gray-400">/100</span>
                <Badge className={`${getActivityColor(huntingConditions.activity_level)} text-white ml-2`}>
                  {getActivityLabel(huntingConditions.activity_level)}
                </Badge>
              </div>
            </div>
          </div>
        )}

        {/* Source indicator */}
        {!compact && weatherSource && (
          <p className="text-xs text-gray-600 text-right" data-testid="weather-source">
            Source: {weatherSource}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default AdvancedWeatherWidget;
