/**
 * BCE-4X-UI — Bloc Meteo Intelligent
 * =====================================
 * Panneau unifie regroupant VENT, Rafales, Direction, Score, Conditions.
 * Position: au-dessus du Score badge, a droite de la carte.
 * Protection: BCE-4X-UI PositionLock, ZIndexGuard, RenderGuard.
 */
import React, { memo, useEffect, useState } from 'react';
import { Wind, Thermometer, Droplets, Gauge, Cloud, ArrowUp, Eye, Sun } from 'lucide-react';

const WIND_DIRECTIONS = [
  'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
  'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO'
];

const getWindLabel = (deg) => {
  if (deg == null) return '--';
  const idx = Math.round(((deg % 360) + 360) % 360 / 22.5) % 16;
  return WIND_DIRECTIONS[idx];
};

const getWindScoreColor = (score) => {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#84cc16';
  if (score >= 40) return '#eab308';
  if (score >= 20) return '#f97316';
  return '#ef4444';
};

const getWindScoreLabel = (score) => {
  if (score >= 80) return 'Optimal';
  if (score >= 60) return 'Bon';
  if (score >= 40) return 'Modere';
  if (score >= 20) return 'Difficile';
  return 'Mauvais';
};

const WeatherPanel = memo(({ wind, weather, loading, huntingScore, scoreV8 }) => {
  // PHASE_TERRITOIRE_Ω_AUDIT_PHASE_A_A — layout responsive anti-superposition
  // Si la fenêtre est trop courte (≤ 600 px), CompassOmegaWidget (top:120, h:163)
  // et WeatherPanel (bottom:90, h:~250) overlap. On replace WeatherPanel à
  // top:320 dans ce cas pour préserver la lisibilité.
  const [shouldRepositionTop, setShouldRepositionTop] = useState(false);
  useEffect(() => {
    const computeOverlapRisk = () => {
      try {
        const h = window.innerHeight || 0;
        // CompassOmega occupe top: 120 → 283 (height ≈ 163)
        // WeatherPanel monte du bas avec hauteur ≈ 250 + bottom: 90 → top ≈ h - 340
        // Overlap si (h - 340) < 290 → h < 630
        setShouldRepositionTop(h > 0 && h < 630);
      } catch (_e) { setShouldRepositionTop(false); }
    };
    computeOverlapRisk();
    window.addEventListener('resize', computeOverlapRisk);
    return () => window.removeEventListener('resize', computeOverlapRisk);
  }, []);

  if (!wind && !weather) return null;

  const windSpeed = wind?.speed;
  const windDir = wind?.direction;
  const windGusts = wind?.gusts || 0;
  const windScore = wind?.score ?? 50;
  const windLabel = wind?.directionLabel || getWindLabel(windDir);
  const scoreColor = getWindScoreColor(windScore);
  const scoreLabel = getWindScoreLabel(windScore);

  const temp = weather?.temperature;
  const humidity = weather?.humidity;
  const pressure = weather?.pressure;
  const conditionLabel = weather?.conditionLabel || weather?.description || '--';
  const visibility = weather?.visibility;
  const uvIndex = weather?.uvIndex;
  const dewPoint = weather?.dewPoint;

  const hasWind = windSpeed != null;
  const hasWeather = temp != null;

  if (!hasWind && !hasWeather && !loading) return null;

  return (
    <div
      data-testid="bce4x-weather-panel"
      data-bce4x-locked="true"
      data-bce4x-repositioned-top={shouldRepositionTop ? 'true' : 'false'}
      style={{
        position: 'absolute',
        ...(shouldRepositionTop
          ? { top: '320px', bottom: 'auto' }
          : { bottom: '90px', top: 'auto' }),
        right: '12px',
        zIndex: 1000,
        background: 'rgba(8, 12, 22, 0.92)',
        backdropFilter: 'blur(12px)',
        borderRadius: '10px',
        padding: '10px 14px',
        color: '#e0e8f0',
        fontSize: '11px',
        lineHeight: '1.4',
        pointerEvents: 'auto',
        border: '1px solid rgba(100, 160, 180, 0.2)',
        minWidth: '180px',
        maxWidth: '220px',
      }}
    >
      {/* Titre */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '6px',
        marginBottom: '8px', paddingBottom: '6px',
        borderBottom: '1px solid rgba(100, 160, 180, 0.15)',
      }}>
        <Cloud style={{ width: 14, height: 14, color: '#64b5f6' }} />
        <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.5px', color: '#90caf9' }}>
          METEO BIONIC
        </span>
        {loading && (
          <span style={{ fontSize: '8px', color: '#64b5f6', marginLeft: 'auto', opacity: 0.7 }}>MAJ...</span>
        )}
      </div>

      {/* Conditions */}
      {hasWeather && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Thermometer style={{ width: 12, height: 12, color: '#4ade80' }} />
            <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>{temp?.toFixed?.(1) ?? temp}°C</span>
          </div>
          <span style={{ fontSize: '10px', color: '#94a3b8' }}>{conditionLabel}</span>
        </div>
      )}

      {/* Vent principal */}
      {hasWind && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          borderRadius: '8px', padding: '8px',
          border: '1px solid rgba(100, 160, 180, 0.1)',
          marginBottom: '6px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Wind style={{ width: 13, height: 13, color: '#60a5fa' }} />
              <span style={{ fontWeight: 700, fontFamily: 'monospace', fontSize: '13px' }}>
                {windSpeed?.toFixed?.(1) ?? windSpeed}
              </span>
              <span style={{ fontSize: '9px', color: '#64748b' }}>km/h</span>
            </div>
            {/* Fleche direction */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
              <ArrowUp style={{
                width: 14, height: 14, color: '#60a5fa',
                transform: `rotate(${(windDir || 0) + 180}deg)`,
                transition: 'transform 0.5s ease',
              }} />
              <span style={{ fontWeight: 600, fontSize: '11px' }}>{windLabel}</span>
              <span style={{ fontSize: '9px', color: '#64748b' }}>{windDir?.toFixed?.(0) ?? windDir}°</span>
            </div>
          </div>

          {/* Rafales */}
          {windGusts > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '3px', opacity: 0.7 }}>
              <Wind style={{ width: 10, height: 10, color: '#f97316' }} />
              <span style={{ fontSize: '10px' }}>Rafales: {windGusts?.toFixed?.(1) ?? windGusts} km/h</span>
            </div>
          )}

          {/* Score vent */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            marginTop: '6px', paddingTop: '5px',
            borderTop: '1px solid rgba(100, 160, 180, 0.1)',
          }}>
            <div style={{
              width: '100%', height: '4px', borderRadius: '2px',
              background: 'rgba(30, 41, 59, 0.8)',
            }}>
              <div style={{
                width: `${windScore}%`, height: '100%', borderRadius: '2px',
                background: scoreColor,
                transition: 'width 0.5s ease, background 0.5s ease',
              }} />
            </div>
            <span style={{ fontSize: '9px', color: scoreColor, fontWeight: 600, whiteSpace: 'nowrap' }}>
              {scoreLabel}
            </span>
          </div>
        </div>
      )}

      {/* Humidite + Pression + V3 extras */}
      {hasWeather && (
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: '6px' }}>
          {humidity != null && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
              <Droplets style={{ width: 10, height: 10, color: '#38bdf8' }} />
              <span style={{ fontSize: '10px', fontFamily: 'monospace' }}>{humidity}%</span>
            </div>
          )}
          {pressure != null && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
              <Gauge style={{ width: 10, height: 10, color: '#a78bfa' }} />
              <span style={{ fontSize: '10px', fontFamily: 'monospace' }}>{pressure} hPa</span>
            </div>
          )}
          {visibility != null && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
              <Eye style={{ width: 10, height: 10, color: '#94a3b8' }} />
              <span style={{ fontSize: '10px', fontFamily: 'monospace' }}>{visibility >= 10000 ? '>10km' : `${(visibility / 1000).toFixed(1)}km`}</span>
            </div>
          )}
          {uvIndex != null && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
              <Sun style={{ width: 10, height: 10, color: '#fbbf24' }} />
              <span style={{ fontSize: '10px', fontFamily: 'monospace' }}>UV {uvIndex}</span>
            </div>
          )}
        </div>
      )}

      {/* Score V8 National (prioritaire) ou Score Chasse V7 (fallback) */}
      {scoreV8 && scoreV8.score_v8 > 0 ? (
        <div style={{
          marginTop: '6px', paddingTop: '6px',
          borderTop: '1px solid rgba(100, 160, 180, 0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <span style={{ fontSize: '9px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Score V8</span>
          <span style={{
            fontSize: '11px', fontWeight: 700,
            color: scoreV8.score_v8 >= 65 ? '#22c55e' : scoreV8.score_v8 >= 50 ? '#eab308' : '#f97316',
          }}>
            {Math.round(scoreV8.score_v8)}/100 — {scoreV8.prediction || 'V8'}
          </span>
        </div>
      ) : huntingScore && (
        <div style={{
          marginTop: '6px', paddingTop: '6px',
          borderTop: '1px solid rgba(100, 160, 180, 0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <span style={{ fontSize: '9px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Score chasse</span>
          <span style={{
            fontSize: '11px', fontWeight: 700,
            color: huntingScore.overall >= 65 ? '#22c55e' : huntingScore.overall >= 50 ? '#eab308' : '#f97316',
          }}>
            {huntingScore.overall}/100 — {huntingScore.label}
          </span>
        </div>
      )}
    </div>
  );
});

WeatherPanel.displayName = 'WeatherPanel';

export default WeatherPanel;
