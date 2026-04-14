/**
 * CameraMapPicker — Carte interactive pour positionner une caméra
 * CAMERA-LOC-MAP-CENTER-FIX: Centrage auto waypoints du membre
 */
import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { MapPin, CheckCircle, Navigation } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const cameraPickerIcon = L.divIcon({
  className: 'camera-picker-marker',
  html: `<div style="background:#F59E0B;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:3px solid #fff;box-shadow:0 0 16px 6px rgba(245,158,11,0.5);">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
  </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const waypointIcon = L.divIcon({
  className: 'waypoint-ref-marker',
  html: `<div style="background:#3B82F6;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.3);">
    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
  </div>`,
  iconSize: [22, 22],
  iconAnchor: [11, 11]
});

const MapClickHandler = ({ onPositionSelect }) => {
  useMapEvents({
    click: (e) => {
      onPositionSelect(e.latlng.lat, e.latlng.lng);
    }
  });
  return null;
};

const AutoCenter = ({ lat, lng, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (lat && lng) {
      map.setView([lat, lng], zoom || 14, { animate: true });
    }
  }, [lat, lng, zoom, map]);
  return null;
};

const CameraMapPicker = ({ isOpen, onClose, onConfirm, initialLat, initialLng, cameraName, waypoints = [] }) => {
  const [selectedLat, setSelectedLat] = useState(initialLat || null);
  const [selectedLng, setSelectedLng] = useState(initialLng || null);

  // Compute center from waypoints, camera position, or Quebec default
  const { centerLat, centerLng, centerZoom } = useMemo(() => {
    // Priority 1: existing camera position
    if (initialLat && initialLng) {
      return { centerLat: initialLat, centerLng: initialLng, centerZoom: 15 };
    }
    // Priority 2: waypoints centroid
    const wps = (waypoints || []).filter(w => (w.lat || w.gps_lat) && (w.lng || w.lon || w.gps_lon));
    if (wps.length > 0) {
      const avgLat = wps.reduce((s, w) => s + (w.lat || w.gps_lat), 0) / wps.length;
      const avgLng = wps.reduce((s, w) => s + (w.lng || w.lon || w.gps_lon), 0) / wps.length;
      return { centerLat: avgLat, centerLng: avgLng, centerZoom: wps.length === 1 ? 15 : 13 };
    }
    // Priority 3: Quebec default
    return { centerLat: 47.3, centerLng: -71.9, centerZoom: 8 };
  }, [initialLat, initialLng, waypoints]);

  const handlePositionSelect = useCallback((lat, lng) => {
    setSelectedLat(parseFloat(lat.toFixed(6)));
    setSelectedLng(parseFloat(lng.toFixed(6)));
  }, []);

  // Reset when modal opens
  useEffect(() => {
    if (isOpen) {
      setSelectedLat(initialLat || null);
      setSelectedLng(initialLng || null);
    }
  }, [isOpen, initialLat, initialLng]);

  const handleConfirm = () => {
    if (selectedLat && selectedLng) {
      onConfirm(selectedLat, selectedLng);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-zinc-900 border-zinc-800 max-w-2xl max-h-[85vh]" data-testid="camera-map-picker">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Navigation className="h-5 w-5 text-amber-500" />
            Positionner: {cameraName || 'Camera'}
          </DialogTitle>
          <DialogDescription>
            {waypoints.length > 0
              ? `Carte centree sur vos ${waypoints.length} waypoint(s). Cliquez pour placer la camera.`
              : 'Cliquez sur la carte pour placer la camera.'
            }
          </DialogDescription>
        </DialogHeader>

        <div className="w-full h-[400px] rounded-lg overflow-hidden border border-zinc-700" data-testid="camera-picker-map">
          <MapContainer
            center={[centerLat, centerLng]}
            zoom={centerZoom}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <AutoCenter lat={centerLat} lng={centerLng} zoom={centerZoom} />
            <MapClickHandler onPositionSelect={handlePositionSelect} />

            {/* Waypoint markers (blue, click to snap) */}
            {(waypoints || []).map((wp, idx) => {
              const wLat = wp.lat || wp.gps_lat;
              const wLng = wp.lng || wp.lon || wp.gps_lon;
              if (!wLat || !wLng) return null;
              return (
                <Marker
                  key={wp.id || idx}
                  position={[wLat, wLng]}
                  icon={waypointIcon}
                  eventHandlers={{ click: () => handlePositionSelect(wLat, wLng) }}
                >
                  <Popup>
                    <div style={{ color: '#1a1a2e', fontSize: 12 }}>
                      <strong>{wp.name || `Waypoint ${idx + 1}`}</strong><br />
                      <span style={{ fontSize: 10, color: '#3B82F6' }}>Cliquez pour placer la camera ici</span>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

            {/* Selected position marker */}
            {selectedLat && selectedLng && (
              <>
                <Circle center={[selectedLat, selectedLng]} radius={20} pathOptions={{ color: '#F59E0B', fillColor: '#F59E0B', fillOpacity: 0.15, weight: 1 }} />
                <Marker position={[selectedLat, selectedLng]} icon={cameraPickerIcon}>
                  <Popup>
                    <div style={{ textAlign: 'center', color: '#1a1a2e' }}>
                      <strong>{cameraName || 'Camera'}</strong><br />
                      <span style={{ fontSize: 11, fontFamily: 'monospace' }}>
                        {selectedLat.toFixed(6)}, {selectedLng.toFixed(6)}
                      </span>
                    </div>
                  </Popup>
                </Marker>
              </>
            )}
          </MapContainer>
        </div>

        {selectedLat && selectedLng ? (
          <div className="bg-zinc-800/50 rounded-lg p-3 flex items-center justify-between" data-testid="position-confirmed">
            <div>
              <p className="text-xs text-zinc-400">Position selectionnee</p>
              <code className="text-sm text-amber-400 font-mono">
                {selectedLat.toFixed(6)}, {selectedLng.toFixed(6)}
              </code>
            </div>
            <CheckCircle className="h-5 w-5 text-green-500" />
          </div>
        ) : (
          <div className="bg-zinc-800/30 rounded-lg p-3 text-center">
            <p className="text-xs text-zinc-500">
              {waypoints.length > 0
                ? 'Cliquez sur un waypoint (bleu) ou sur la carte pour positionner'
                : 'Cliquez sur la carte pour definir la position'}
            </p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" className="border-zinc-700" onClick={onClose}>Annuler</Button>
          <Button className="bg-amber-600 hover:bg-amber-700" onClick={handleConfirm} disabled={!selectedLat || !selectedLng} data-testid="confirm-camera-position">
            <MapPin className="h-4 w-4 mr-1" /> Confirmer la position
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CameraMapPicker;
