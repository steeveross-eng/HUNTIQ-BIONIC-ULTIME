/**
 * AlphaHotspotsLayer — Couche géospatiale ALPHA pour Leaflet
 * Affiche les hotspots ALPHA/dominant sur la carte avec halo et popup enrichi.
 */
import React from 'react';
import { Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';

const crownSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m2 4 3 12h14l3-12-5 4-5-4-5 4z"/><path d="M5 16h14v2H5z"/></svg>`;

const createAlphaIcon = (category) => {
  const color = category === 'alpha' ? '#F59E0B' : '#F97316';
  const size = category === 'alpha' ? 34 : 28;
  const glow = category === 'alpha' ? 'box-shadow:0 0 16px 6px rgba(245,158,11,0.6);' : 'box-shadow:0 0 10px 3px rgba(249,115,22,0.4);';
  return L.divIcon({
    className: 'alpha-marker',
    html: `<div style="background:${color};border-radius:50%;width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center;border:3px solid #fff;${glow}">${crownSvg}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -(size / 2 + 4)]
  });
};

const AlphaHotspotsLayer = ({ hotspots = [] }) => {
  if (!hotspots || hotspots.length === 0) return null;

  return (
    <>
      {hotspots.map(hs => (
        <React.Fragment key={hs.id}>
          {/* Halo ALPHA */}
          <Circle
            center={[hs.lat, hs.lon]}
            radius={hs.haloRadius}
            pathOptions={{
              color: hs.category === 'alpha' ? '#F59E0B' : '#F97316',
              weight: 2,
              opacity: 0.5,
              fillColor: hs.category === 'alpha' ? '#F59E0B' : '#F97316',
              fillOpacity: 0.1,
              dashArray: hs.category === 'alpha' ? '' : '8 4'
            }}
          />
          <Marker
            position={[hs.lat, hs.lon]}
            icon={createAlphaIcon(hs.category)}
            data-testid={`alpha-marker-${hs.id}`}
          >
            <Popup>
              <div style={{ minWidth: 200, color: '#1a1a2e' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                  <span style={{
                    display: 'inline-flex', alignItems: 'center', gap: 3,
                    padding: '2px 8px', borderRadius: 6, fontSize: 12, fontWeight: 700,
                    background: hs.category === 'alpha' ? '#FEF3C7' : '#FFEDD5',
                    color: hs.category === 'alpha' ? '#92400E' : '#9A3412'
                  }}>
                    {hs.category === 'alpha' ? '\u2605' : '\u25C6'} {hs.category.toUpperCase()}
                  </span>
                  <span style={{ fontSize: 18, fontWeight: 800, color: hs.category === 'alpha' ? '#D97706' : '#EA580C' }}>
                    {hs.score}
                  </span>
                </div>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, textTransform: 'capitalize' }}>
                  {hs.species?.replace('_', ' ')}
                </div>
                <div style={{ fontSize: 12, color: '#555', marginBottom: 2 }}>
                  Sexe: <strong>{hs.sex}</strong>
                </div>
                <div style={{ fontSize: 12, color: '#555', marginBottom: 2 }}>
                  Camera: {hs.cameraName}
                </div>
                <div style={{ fontSize: 11, color: '#888', marginBottom: 4 }}>
                  {hs.lat.toFixed(5)}, {hs.lon.toFixed(5)}
                </div>
                {hs.timestamp && (
                  <div style={{ fontSize: 11, color: '#999' }}>
                    {new Date(hs.timestamp).toLocaleString('fr-CA')}
                  </div>
                )}
                <div style={{ marginTop: 8, borderTop: '1px solid #eee', paddingTop: 6 }}>
                  <a href="/admin-premium" style={{ fontSize: 11, color: '#D97706', textDecoration: 'none', fontWeight: 600 }}>
                    ADMIN Analyse ALPHA &rarr;
                  </a>
                </div>
              </div>
            </Popup>
          </Marker>
        </React.Fragment>
      ))}
    </>
  );
};

export default AlphaHotspotsLayer;
