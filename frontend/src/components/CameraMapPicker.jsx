/**
 * CameraMapPicker — Carte interactive pour positionner une caméra
 * CAMERA-LOC-MAP: Clic sur carte = position GPS, ZERO saisie manuelle
 */
import React, { useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { MapPin, CheckCircle, Navigation } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Camera marker icon
const cameraPickerIcon = L.divIcon({
  className: 'camera-picker-marker',
  html: `<div style="background:#F59E0B;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:3px solid #fff;box-shadow:0 0 16px 6px rgba(245,158,11,0.5);animation:pulse 2s infinite;">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
  </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

// Click handler component
const MapClickHandler = ({ onPositionSelect }) => {
  useMapEvents({
    click: (e) => {
      onPositionSelect(e.latlng.lat, e.latlng.lng);
    }
  });
  return null;
};

// Recenter component
const RecenterMap = ({ lat, lng }) => {
  const map = useMap();
  if (lat && lng) {
    map.setView([lat, lng], map.getZoom());
  }
  return null;
};

const CameraMapPicker = ({ isOpen, onClose, onConfirm, initialLat, initialLng, cameraName }) => {
  const [selectedLat, setSelectedLat] = useState(initialLat || null);
  const [selectedLng, setSelectedLng] = useState(initialLng || null);

  const defaultCenter = [initialLat || 47.3, initialLng || -71.9];
  const defaultZoom = initialLat ? 14 : 8;

  const handlePositionSelect = useCallback((lat, lng) => {
    setSelectedLat(parseFloat(lat.toFixed(6)));
    setSelectedLng(parseFloat(lng.toFixed(6)));
  }, []);

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
          <DialogDescription>Cliquez sur la carte pour placer la camera</DialogDescription>
        </DialogHeader>

        {/* Map */}
        <div className="w-full h-[400px] rounded-lg overflow-hidden border border-zinc-700" data-testid="camera-picker-map">
          <MapContainer
            center={defaultCenter}
            zoom={defaultZoom}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapClickHandler onPositionSelect={handlePositionSelect} />
            
            {selectedLat && selectedLng && (
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
            )}
          </MapContainer>
        </div>

        {/* Position display */}
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
            <p className="text-xs text-zinc-500">Cliquez sur la carte pour definir la position</p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" className="border-zinc-700" onClick={onClose}>Annuler</Button>
          <Button
            className="bg-amber-600 hover:bg-amber-700"
            onClick={handleConfirm}
            disabled={!selectedLat || !selectedLng}
            data-testid="confirm-camera-position"
          >
            <MapPin className="h-4 w-4 mr-1" /> Confirmer la position
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CameraMapPicker;
