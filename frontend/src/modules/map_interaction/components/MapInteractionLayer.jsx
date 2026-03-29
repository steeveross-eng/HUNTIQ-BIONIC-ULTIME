/**
 * MapInteractionLayer — V6 SUPRA (BCE-4X Purge V1-V5)
 * ======================================================
 * 
 * Module d'interaction cartographique V6 PURIFIE.
 * - Affichage coordonnees GPS LIVE (mousemove) UNIQUEMENT
 * - ZERO creation waypoint par double-clic (PURGE V1-V5)
 * - La barre Waypoint V6 dans le header est l'UNIQUE source de creation
 * 
 * BCE-4X: Toute logique legacy onDoubleClick, InteractionHint,
 *   WaypointPopup, PendingWaypointMarker = SUPPRIMEE DEFINITIVEMENT.
 *
 * Conformite: BCE-4X | ULTRA-MAX++ | STEEVE-MAX
 * Date purge: Fevrier 2026
 * 
 * @module modules/map_interaction
 */
import React, { useState, useCallback } from 'react';
import { useMapEvents } from 'react-leaflet';
import { Navigation } from 'lucide-react';

/**
 * GPS Coordinates Display Component
 */
const CoordinatesOverlay = ({ lat, lng, visible }) => {
  if (!visible || lat === null || lng === null) return null;

  return (
    <div 
      className="absolute bottom-4 left-4 z-[1000] bg-black/80 backdrop-blur-sm text-white px-4 py-2 rounded-lg shadow-lg border border-white/10"
      data-testid="coordinates-overlay"
    >
      <div className="flex items-center gap-3">
        <Navigation className="h-4 w-4 text-[#f5a623]" />
        <div className="font-mono text-sm">
          <span className="text-gray-400">LAT:</span>{' '}
          <span className="text-white font-semibold">{lat.toFixed(6)}</span>
          <span className="mx-2 text-gray-500">|</span>
          <span className="text-gray-400">LNG:</span>{' '}
          <span className="text-white font-semibold">{lng.toFixed(6)}</span>
        </div>
      </div>
    </div>
  );
};

/**
 * Map Event Handler — V6 GPS Only (ZERO double-clic)
 */
const MapEventHandler = ({ onMouseMove, onMouseEnter, onMouseLeave }) => {
  useMapEvents({
    mousemove: (e) => {
      onMouseMove(e.latlng.lat, e.latlng.lng);
    },
    mouseout: () => {
      onMouseLeave();
    },
    mouseover: () => {
      onMouseEnter();
    }
  });

  return null;
};

/**
 * MapInteractionLayer — V6 SUPRA (GPS Coordinates Only)
 * 
 * BCE-4X PURGE COMPLETE:
 *   - SUPPRIME: enableWaypointCreation, showHint, onWaypointCreated, userId
 *   - SUPPRIME: onDoubleClick, WaypointPopup, PendingWaypointMarker, InteractionHint
 *   - CONSERVE: showCoordinates (overlay GPS uniquement)
 * 
 * @param {Object} props
 * @param {boolean} props.showCoordinates - Show GPS coordinates overlay (default: true)
 */
export const MapInteractionLayer = ({
  showCoordinates = true,
}) => {
  const [mousePosition, setMousePosition] = useState({ lat: null, lng: null });
  const [isMouseOnMap, setIsMouseOnMap] = useState(false);

  const handleMouseMove = useCallback((lat, lng) => {
    setMousePosition({ lat, lng });
  }, []);

  const handleMouseEnter = useCallback(() => {
    setIsMouseOnMap(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsMouseOnMap(false);
    setMousePosition({ lat: null, lng: null });
  }, []);

  return (
    <>
      <MapEventHandler
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      />

      {showCoordinates && (
        <CoordinatesOverlay
          lat={mousePosition.lat}
          lng={mousePosition.lng}
          visible={isMouseOnMap}
        />
      )}
    </>
  );
};

export default MapInteractionLayer;
