/**
 * AccessRouteV6Layer.jsx — Layer unique GOLDEN pour acces aux affuts V6
 * PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
 * Branche: STEEVE-MAX-x3200-V6-CORE
 *
 * 1 Layer unique — ZERO duplication autorisee.
 * Rendu 4 couleurs:
 *   - Vert #2ECC71  : Sentier reel OSM
 *   - Bleu #3498DB / Orange #E67E22 : Hybride sentier+terrain
 *   - Or #F1C40F    : Hors-sentier optimise
 *   - Rouge #E74C3C : Non conforme
 *
 * Interactions:
 *   - Hover segment: tooltip avec type, distance, temps estime
 *   - Hover hors-sentier: tooltip enrichi avec analyse vegetation
 *   - Click jonction: detail transition sentier→terrain
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const SEGMENT_STYLES = {
  trail: {
    color: '#2ECC71',
    weight: 4,
    opacity: 0.9,
    dashArray: null,
  },
  hybrid: {
    color: '#3498DB',
    weight: 3,
    opacity: 0.85,
    dashArray: null,
  },
  off_trail_optimized: {
    color: '#F1C40F',
    weight: 3,
    opacity: 0.85,
    dashArray: '8, 5',
  },
  non_conformant: {
    color: '#E74C3C',
    weight: 2,
    opacity: 0.8,
    dashArray: '4, 6',
  },
};

const JUNCTION_ICON = L.divIcon({
  className: 'access-junction-marker',
  html: '<div style="width:10px;height:10px;border-radius:50%;background:#E67E22;border:2px solid #fff;box-shadow:0 0 4px rgba(0,0,0,0.4)"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const AccessRouteV6Layer = ({ routeData, enabled = true }) => {
  const map = useMap();
  const layerGroupRef = useRef(null);

  const clearLayers = useCallback(() => {
    if (layerGroupRef.current) {
      layerGroupRef.current.clearLayers();
    }
  }, []);

  useEffect(() => {
    if (!layerGroupRef.current) {
      layerGroupRef.current = L.layerGroup().addTo(map);
    }
    return () => {
      if (layerGroupRef.current) {
        map.removeLayer(layerGroupRef.current);
        layerGroupRef.current = null;
      }
    };
  }, [map]);

  useEffect(() => {
    if (!layerGroupRef.current || !enabled) {
      clearLayers();
      return;
    }

    clearLayers();

    if (!routeData || routeData.status !== 'ok' || !routeData.route) return;

    const route = routeData.route;
    const segments = route.segments || [];

    segments.forEach((seg, idx) => {
      if (!seg.coordinates || seg.coordinates.length < 2) return;

      const latLngs = seg.coordinates.map(c => [c[1], c[0]]);
      const style = SEGMENT_STYLES[seg.type] || SEGMENT_STYLES.non_conformant;

      const polyline = L.polyline(latLngs, {
        color: seg.color || style.color,
        weight: style.weight,
        opacity: style.opacity,
        dashArray: style.dashArray,
        lineCap: 'round',
        lineJoin: 'round',
      });

      // Tooltip hover — type + distance + temps
      let tooltipContent = `<div style="font-size:12px;font-family:system-ui;padding:2px 4px;">
        <b>${seg.label || seg.type}</b><br/>
        Distance: ${seg.distance_m ? Math.round(seg.distance_m) + 'm' : 'N/A'}`;

      if (seg.trail_name) {
        tooltipContent += `<br/>Sentier: ${seg.trail_name}`;
      }
      if (seg.surface && seg.surface !== 'unknown') {
        tooltipContent += `<br/>Surface: ${seg.surface}`;
      }

      // Hover enrichi pour hors-sentier
      if (seg.vegetation) {
        const v = seg.vegetation;
        tooltipContent += `<br/><hr style="margin:3px 0;border-color:#555"/>
          <b>Vegetation:</b><br/>
          Couvert: ${Math.round((v.canopy_avg || 0) * 100)}%<br/>
          Encombrement: ${v.encumbrance || 'N/A'}<br/>
          Espece: ${(v.dominant_species || '').replace(/_/g, ' ')}<br/>
          Strategie: ${v.strategy || 'N/A'}`;
      }

      tooltipContent += '</div>';

      polyline.bindTooltip(tooltipContent, {
        sticky: true,
        direction: 'top',
        offset: [0, -8],
        className: 'access-route-tooltip',
      });

      polyline.addTo(layerGroupRef.current);

      // Marqueur de jonction entre segments (sauf dernier)
      if (idx < segments.length - 1 && seg.type === 'trail') {
        const lastCoord = seg.coordinates[seg.coordinates.length - 1];
        if (lastCoord) {
          const marker = L.marker([lastCoord[1], lastCoord[0]], { icon: JUNCTION_ICON });
          marker.bindPopup(
            `<div style="font-size:12px;font-family:system-ui;">
              <b>Point de jonction</b><br/>
              Transition: sentier &rarr; terrain<br/>
              Segment suivant: ${segments[idx + 1]?.label || 'N/A'}
            </div>`,
            { maxWidth: 200 }
          );
          marker.addTo(layerGroupRef.current);
        }
      }
    });

    // Marqueur destination (affut)
    if (segments.length > 0) {
      const lastSeg = segments[segments.length - 1];
      const lastCoord = lastSeg.coordinates?.[lastSeg.coordinates.length - 1];
      if (lastCoord) {
        const destIcon = L.divIcon({
          className: 'access-dest-marker',
          html: '<div style="width:14px;height:14px;border-radius:50%;background:#E74C3C;border:3px solid #fff;box-shadow:0 0 6px rgba(0,0,0,0.5)"></div>',
          iconSize: [20, 20],
          iconAnchor: [10, 10],
        });
        const destMarker = L.marker([lastCoord[1], lastCoord[0]], { icon: destIcon });
        destMarker.bindTooltip('Affut cible', { direction: 'top', offset: [0, -12] });
        destMarker.addTo(layerGroupRef.current);
      }
    }
  }, [routeData, enabled, map, clearLayers]);

  return null;
};

export default AccessRouteV6Layer;
