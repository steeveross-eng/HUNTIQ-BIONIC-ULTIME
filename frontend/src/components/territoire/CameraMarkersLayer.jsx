/**
 * CameraMarkersLayer — Affichage des cameras sur la carte Leaflet
 * CAM-LOC-Omega: Layer independant pour la carte principale BIONIC
 */
import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Badge } from '@/components/ui/badge';

const cameraIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>`;

const createCameraIcon = (status) => {
  const color = status === 'active' ? '#F59E0B' : status === 'maintenance' ? '#EAB308' : '#6B7280';
  return L.divIcon({
    className: 'camera-map-marker',
    html: `<div style="background:${color};border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.4);">${cameraIconSvg}</div>`,
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
          <Marker
            key={cam.id}
            position={[lat, lon]}
            icon={createCameraIcon(cam.status)}
            data-testid={`camera-marker-${cam.id}`}
          >
            <Popup>
              <div style={{ minWidth: 160, color: '#1a1a2e' }}>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                  {cam.name || 'Camera'}
                </div>
                <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>
                  {cam.manufacturer} {cam.model || ''}
                </div>
                <div style={{ fontSize: 12, marginBottom: 2 }}>
                  Photos: <strong>{cam.photo_count || 0}</strong>
                </div>
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
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

export default CameraMarkersLayer;
