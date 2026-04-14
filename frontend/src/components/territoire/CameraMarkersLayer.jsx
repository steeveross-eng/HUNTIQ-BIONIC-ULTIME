/**
 * CameraMarkersLayer — Affichage des cameras sur la carte Leaflet
 * CAM-LOC-Omega: Layer avec halo 600m, popup enrichi, icone ambre
 */
import React from 'react';
import { Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';

const cameraIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>`;

const createCameraIcon = (inZone600m) => {
  const color = inZone600m ? '#F59E0B' : '#6B7280';
  const glow = inZone600m ? 'box-shadow:0 0 12px 4px rgba(245,158,11,0.5);' : '';
  return L.divIcon({
    className: 'camera-map-marker',
    html: `<div style="background:${color};border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border:2px solid #fff;${glow}">${cameraIconSvg}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -18]
  });
};

const CameraMarkersLayer = ({ cameras = [] }) => {
  if (!cameras || cameras.length === 0) return null;

  return (
    <>
      {cameras.map(cam => {
        const lat = cam.gps_lat || cam.location?.coordinates?.[1];
        const lon = cam.gps_lon || cam.location?.coordinates?.[0];
        if (!lat || !lon) return null;

        return (
          <React.Fragment key={cam.id}>
            {/* Halo 600m pour cameras dans la zone */}
            {cam.inZone600m && (
              <Circle
                center={[lat, lon]}
                radius={600}
                pathOptions={{
                  color: '#F59E0B',
                  weight: 1,
                  opacity: 0.4,
                  fillColor: '#F59E0B',
                  fillOpacity: 0.08,
                  dashArray: '6 4'
                }}
              />
            )}
            <Marker
              position={[lat, lon]}
              icon={createCameraIcon(cam.inZone600m)}
              data-testid={`camera-marker-${cam.id}`}
            >
              <Popup>
                <div style={{ minWidth: 180, color: '#1a1a2e' }}>
                  <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                    {cam.name || 'Camera'}
                  </div>
                  <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>
                    {cam.manufacturer} {cam.model || ''}
                  </div>
                  <div style={{ fontSize: 12, marginBottom: 2 }}>
                    Photos: <strong>{cam.photo_count || 0}</strong>
                  </div>
                  {cam.nearestWaypointDist != null && (
                    <div style={{ fontSize: 11, color: cam.inZone600m ? '#D97706' : '#888', marginBottom: 2 }}>
                      {cam.inZone600m ? 'Dans zone 600m' : `${cam.nearestWaypointDist}m du waypoint`}
                    </div>
                  )}
                  <div style={{ fontSize: 11, color: '#888' }}>
                    {lat.toFixed(5)}, {lon.toFixed(5)}
                  </div>
                  <div style={{ marginTop: 4 }}>
                    <span style={{
                      display: 'inline-block', padding: '1px 6px', borderRadius: 4,
                      fontSize: 10, fontWeight: 600,
                      background: cam.status === 'active' ? '#D4EDDA' : '#F8D7DA',
                      color: cam.status === 'active' ? '#155724' : '#721C24'
                    }}>
                      {cam.status}
                    </span>
                  </div>
                  <div style={{ marginTop: 6 }}>
                    <a href="/cameras" style={{ fontSize: 11, color: '#F59E0B', textDecoration: 'none', fontWeight: 600 }}>
                      Galerie & Stats &rarr;
                    </a>
                  </div>
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        );
      })}
    </>
  );
};

export default CameraMarkersLayer;
