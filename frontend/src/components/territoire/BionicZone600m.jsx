/**
 * BionicZone600m.jsx — Zone circulaire 600 m centree sur le waypoint actif
 * VERSION: 2.0.0 — Norme officielle BIONIC V6.x
 * DIRECTIVE STEEVE-MAX: ZERO carre, cercle 600m
 *
 * SPECIFICATIONS V6.x:
 *   - Cercle 600 m de rayon (1.2 km de diametre)
 *   - Centre EXACTEMENT sur le waypoint actif
 *   - Contour pointille orange BIONIC (#f5a623, faible intensite)
 *   - Sans remplissage (fillOpacity = 0)
 *   - Affiche en permanence pour tous les waypoints actifs
 *   - ZERO zone carree
 *
 * Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x100
 */

import React from 'react';
import { Circle, Tooltip } from 'react-leaflet';

// V6.x: Rayon officiel (directive STEEVE-MAX)
const ZONE_RADIUS_M = 600;

/**
 * BionicZone600m — Cercle 600m centre sur un waypoint
 */
const BionicZone600m = ({ 
  waypoint,
  showTooltip = false,
  opacity = 0.7,
}) => {
  const lat = waypoint?.lat ?? waypoint?.latitude;
  const lng = waypoint?.lng ?? waypoint?.longitude;
  
  if (lat == null || lng == null) return null;
  
  // Style BIONIC V6 officiel
  const pathOptions = {
    color: '#f5a623',
    weight: 2,
    opacity: opacity,
    fillColor: 'transparent',
    fillOpacity: 0,
    dashArray: '8, 6',
    dashOffset: '0',
    lineCap: 'round',
    lineJoin: 'round',
  };
  
  const areaKm2 = Math.PI * (ZONE_RADIUS_M / 1000) ** 2;
  
  return (
    <Circle
      center={[lat, lng]}
      radius={ZONE_RADIUS_M}
      pathOptions={pathOptions}
      data-testid="bionic-zone-600m"
    >
      {showTooltip && (
        <Tooltip 
          permanent={false} 
          direction="top" 
          offset={[0, -10]}
          className="bionic-zone-tooltip"
        >
          <div className="bg-gray-900/95 border border-[#f5a623]/40 rounded-lg p-2 min-w-[160px]">
            <div className="flex items-center gap-2 mb-1">
              <div 
                className="w-3 h-3 rounded-full border-2 border-dashed" 
                style={{ borderColor: '#f5a623' }}
              />
              <span className="text-white font-semibold text-sm">Zone V6</span>
            </div>
            <div className="text-gray-400 text-xs">
              Cercle {ZONE_RADIUS_M}m | {areaKm2.toFixed(2)} km2
            </div>
          </div>
        </Tooltip>
      )}
    </Circle>
  );
};

// Export par defaut + nomme pour compatibilite
export default BionicZone600m;
export { BionicZone600m };
