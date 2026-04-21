/**
 * CompassOmegaWidget.jsx — Widget COMPASS_Ω hors-carte
 * ======================================================
 * PHASE_XI_SUPRA_VERITE_TERRAIN_Ω (X80-ABSOLU-Ω) — représentation VENT
 * hors-carte, strictement distincte des corridors ambre. Palette blanche/grise
 * institutionnelle uniquement.
 *
 * Source de vérité : bundleData.wind_vectors (ENGINE-SENSORIEL-VENT-ODEURS-Ω V30).
 */
import React, { useMemo } from 'react';

const QUALIF = (speed) => {
  if (speed < 2) return 'CALME';
  if (speed < 6) return 'LEGER';
  if (speed < 12) return 'MODERE';
  if (speed < 20) return 'SOUTENU';
  if (speed < 30) return 'FORT';
  return 'TEMPETE';
};

export const CompassOmegaWidget = ({ bundleDataV8, showWind }) => {
  const stats = useMemo(() => {
    const wv = bundleDataV8?.wind_vectors || [];
    if (!wv.length) return null;
    const meanDir = wv.reduce((a, v) => a + (v.direction_deg || 0), 0) / wv.length;
    const meanSpeed = wv.reduce((a, v) => a + (v.speed_kmh || 0), 0) / wv.length;
    // 8 secteurs cardinaux avec intensité
    const sectors = Array(8).fill(0);
    wv.forEach(v => {
      const s = Math.round(((v.direction_deg || 0) / 45)) % 8;
      sectors[s] = Math.max(sectors[s], v.speed_kmh || 0);
    });
    const maxSpeed = Math.max(1, ...sectors);
    return { meanDir, meanSpeed, sectors, maxSpeed };
  }, [bundleDataV8?.wind_vectors]);

  if (!showWind || !stats) return null;

  const size = 110;
  const cx = size / 2;
  const cy = size / 2;
  const radius = size / 2 - 8;

  return (
    <div
      data-testid="compass-omega-vent"
      style={{
        position: 'absolute',
        top: 120,
        right: 12,
        width: size,
        background: 'rgba(20,20,24,0.78)',
        backdropFilter: 'blur(6px)',
        WebkitBackdropFilter: 'blur(6px)',
        border: '1px solid rgba(245,245,245,0.22)',
        borderRadius: 10,
        padding: 8,
        color: '#F5F5F5',
        fontFamily: 'system-ui, -apple-system, Segoe UI, sans-serif',
        fontSize: 10,
        zIndex: 1100,
        pointerEvents: 'auto',
        boxShadow: '0 4px 18px rgba(0,0,0,0.35)',
      }}
      title={`COMPASS_Ω · ${Math.round(stats.meanDir)}° · ${stats.meanSpeed.toFixed(1)} km/h`}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4, letterSpacing: '0.08em', textTransform: 'uppercase', fontSize: 9, color: '#E0E0E0' }}>
        <span>VENT Ω</span>
        <span style={{ color: '#FAFAFA', fontWeight: 700 }}>{QUALIF(stats.meanSpeed)}</span>
      </div>
      <svg width={size - 16} height={size - 16} viewBox={`0 0 ${size} ${size}`} style={{ display: 'block' }}>
        {/* Cercle extérieur */}
        <circle cx={cx} cy={cy} r={radius} fill="rgba(255,255,255,0.04)" stroke="rgba(245,245,245,0.35)" strokeWidth={1} />
        {/* Secteurs bars */}
        {stats.sectors.map((s, i) => {
          const angle = i * 45;
          const rad = (angle - 90) * Math.PI / 180;
          const len = 8 + (s / stats.maxSpeed) * (radius - 14);
          const x1 = cx + Math.cos(rad) * 10;
          const y1 = cy + Math.sin(rad) * 10;
          const x2 = cx + Math.cos(rad) * len;
          const y2 = cy + Math.sin(rad) * len;
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#BDBDBD" strokeWidth={2} strokeLinecap="round" opacity={0.55 + (s / stats.maxSpeed) * 0.4} />;
        })}
        {/* Flèche principale */}
        {(() => {
          const rad = (stats.meanDir - 90) * Math.PI / 180;
          const len = radius - 6;
          const tipX = cx + Math.cos(rad) * len;
          const tipY = cy + Math.sin(rad) * len;
          const baseX = cx - Math.cos(rad) * 14;
          const baseY = cy - Math.sin(rad) * 14;
          const perp = rad + Math.PI / 2;
          const wingX1 = tipX - Math.cos(rad) * 8 + Math.cos(perp) * 5;
          const wingY1 = tipY - Math.sin(rad) * 8 + Math.sin(perp) * 5;
          const wingX2 = tipX - Math.cos(rad) * 8 - Math.cos(perp) * 5;
          const wingY2 = tipY - Math.sin(rad) * 8 - Math.sin(perp) * 5;
          return (
            <g>
              <line x1={baseX} y1={baseY} x2={tipX} y2={tipY} stroke="#FFFFFF" strokeWidth={2.5} strokeLinecap="round" />
              <polygon points={`${tipX},${tipY} ${wingX1},${wingY1} ${wingX2},${wingY2}`} fill="#FFFFFF" />
            </g>
          );
        })()}
        {/* N S E W labels */}
        <text x={cx} y={12} textAnchor="middle" fill="#F5F5F5" fontSize={9} fontWeight={700}>N</text>
        <text x={cx} y={size - 4} textAnchor="middle" fill="#BDBDBD" fontSize={8}>S</text>
        <text x={size - 4} y={cy + 3} textAnchor="end" fill="#BDBDBD" fontSize={8}>E</text>
        <text x={4} y={cy + 3} textAnchor="start" fill="#BDBDBD" fontSize={8}>O</text>
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4, fontSize: 10 }}>
        <span style={{ color: '#E0E0E0' }}>{Math.round(stats.meanDir)}°</span>
        <span style={{ color: '#FFFFFF', fontWeight: 700 }}>{stats.meanSpeed.toFixed(1)} km/h</span>
      </div>
      <div style={{ fontSize: 8, color: '#9E9E9E', marginTop: 2 }}>engine_vent Ω · V30</div>
    </div>
  );
};

export default CompassOmegaWidget;
