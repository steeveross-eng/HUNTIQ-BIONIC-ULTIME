/**
 * WeatherWidget - BCE-4X Weather Engine v3 UNIFIED
 * Source unique: useWeatherStore (Weather Engine v3 -> OWM -> Open-Meteo)
 * Interdit d'utiliser WeatherService V1
 */
import React, { useEffect } from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { useLanguage } from '../../../contexts/LanguageContext';
import useWeatherStore from '../../../stores/useWeatherStore';
import { Sun, Cloud, CloudRain, Snowflake, CloudLightning, CloudFog, Wind, CloudSun, Droplets, Gauge, Eye, Loader2 } from 'lucide-react';

const WeatherIcon = ({ condition, className = "h-8 w-8" }) => {
  const cl = (condition || '').toLowerCase();
  const map = {
    'ciel degage': { I: Sun, c: 'text-amber-400' },
    'partiellement nuageux': { I: CloudSun, c: 'text-amber-300' },
    'variable': { I: CloudSun, c: 'text-amber-300' },
    'brouillard': { I: CloudFog, c: 'text-gray-400' },
    'bruine': { I: CloudRain, c: 'text-blue-300' },
    'pluie': { I: CloudRain, c: 'text-blue-400' },
    'neige': { I: Snowflake, c: 'text-cyan-300' },
    'averses': { I: CloudRain, c: 'text-blue-400' },
    'orage': { I: CloudLightning, c: 'text-purple-400' },
  };
  const match = Object.entries(map).find(([k]) => cl.includes(k));
  const { I: Icon, c: color } = match ? match[1] : { I: Cloud, c: 'text-gray-400' };
  return <Icon className={`${className} ${color}`} />;
};

export const WeatherWidget = ({ lat, lng, compact = false, onWeatherLoad }) => {
  const { t } = useLanguage();
  const current = useWeatherStore(s => s.current);
  const loading = useWeatherStore(s => s.loading);
  const source = useWeatherStore(s => s.source);
  const fetchAll = useWeatherStore(s => s.fetchAll);

  useEffect(() => {
    if (lat && lng) fetchAll(lat, lng);
  }, [lat, lng, fetchAll]);

  useEffect(() => {
    if (current && onWeatherLoad) {
      onWeatherLoad({
        temperature: current.temperature_c,
        humidity: current.humidity_pct,
        wind_speed: current.wind_speed_kmh,
        wind_direction: current.wind_direction_deg,
        wind_gust: current.wind_gust_kmh,
        pressure: current.pressure_hpa,
        visibility_km: current.visibility_km,
        uv_index: current.uv_index,
        condition: current.description,
        hunting_index: current.hunting_score,
        source,
      });
    }
  }, [current, source, onWeatherLoad]);

  if (loading && !current) {
    return (
      <Card className="bg-[#111122] border-[rgba(255,255,255,0.06)]" data-testid="weather-widget-loading">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-[#FF9800]" />
            <span className="text-gray-400 text-sm">Chargement Weather v3...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!current) {
    return (
      <Card className="bg-[#111122] border-[rgba(255,255,255,0.06)]" data-testid="weather-widget-error">
        <CardContent className="p-4 text-center text-gray-500">
          <CloudSun className="h-8 w-8 text-[#FF9800] mx-auto" />
          <p className="text-sm mt-2">{t('weather_unavailable')}</p>
        </CardContent>
      </Card>
    );
  }

  const w = current;

  if (compact) {
    return (
      <div className="flex items-center gap-2 bg-[#111122]/80 rounded-lg px-3 py-2" data-testid="weather-widget-compact">
        <WeatherIcon condition={w.description} className="h-6 w-6" />
        <span className="text-white font-bold">{w.temperature_c ?? '--'}°C</span>
        <span className="text-gray-400 text-xs ml-1">{w.description}</span>
      </div>
    );
  }

  return (
    <Card className="bg-[#111122] border-[rgba(255,255,255,0.06)]" data-testid="weather-widget">
      <CardContent className="p-4 space-y-3">
        {/* Ligne 1 : Temperature + Condition */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <WeatherIcon condition={w.description} className="h-10 w-10" />
            <div>
              <div className="text-3xl font-bold text-white tabular-nums">
                {w.temperature_c ?? '--'}°C
              </div>
              <div className="text-gray-400 text-sm capitalize">
                {w.description || 'N/A'}
              </div>
            </div>
          </div>
          <div className="text-right space-y-1">
            <div className="text-sm">
              <span className="text-gray-500">{t('weather_humidity_label')}:</span>
              <span className="text-blue-400 ml-2 tabular-nums">{w.humidity_pct ?? '--'}%</span>
            </div>
            <div className="text-sm">
              <span className="text-gray-500">{t('weather_wind_label')}:</span>
              <span className="text-cyan-400 ml-2 tabular-nums">{w.wind_speed_kmh ?? '--'} km/h</span>
            </div>
            <div className="text-sm">
              <span className="text-gray-500">{t('weather_pressure_label')}:</span>
              <span className="text-purple-400 ml-2 tabular-nums">{w.pressure_hpa ?? '--'} hPa</span>
            </div>
          </div>
        </div>

        {/* Ligne 2 : Details supplementaires */}
        <div className="flex items-center gap-4 pt-2 border-t border-white/5 text-xs text-gray-400">
          {w.wind_gust_kmh != null && (
            <span className="flex items-center gap-1">
              <Wind className="h-3 w-3 text-cyan-500" />
              Rafales: {w.wind_gust_kmh} km/h
            </span>
          )}
          {w.wind_direction_deg != null && (
            <span className="flex items-center gap-1">
              <Wind className="h-3 w-3 text-gray-500" />
              {w.wind_direction_deg}°
            </span>
          )}
          {w.visibility_km != null && (
            <span className="flex items-center gap-1">
              <Eye className="h-3 w-3 text-gray-500" />
              {w.visibility_km} km
            </span>
          )}
          {w.uv_index != null && (
            <span className="flex items-center gap-1">
              <Sun className="h-3 w-3 text-amber-400" />
              UV {w.uv_index}
            </span>
          )}
          <span className="ml-auto text-[10px] text-gray-600 uppercase">
            v3 ({source || '?'})
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

export default WeatherWidget;
