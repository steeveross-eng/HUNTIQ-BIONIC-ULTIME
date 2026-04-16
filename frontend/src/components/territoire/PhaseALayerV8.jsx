/**
 * PhaseALayerV8.jsx — Couche carte Phase A (Relocalisation + Salines)
 * ====================================================================
 * V8-FRONTEND-PHASE-A-Omega
 * Rendu Leaflet organique: marqueurs relocalisation (top-3) + salines optimales
 * Style conforme STEEVE-MAX: triangles orientes, halos, ZERO rectangles
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const RELOC_COLORS = [
  { fill: '#10B981', stroke: '#059669', label: '#1' },
  { fill: '#3B82F6', stroke: '#2563EB', label: '#2' },
  { fill: '#8B5CF6', stroke: '#7C3AED', label: '#3' },
];

const SALINE_COLOR = { fill: '#F59E0B', stroke: '#D97706' };

const PhaseALayerV8 = ({
  relocalisations = [],
  salines = [],
  siteActuel = null,
  showReloc = true,
  showSalines = true,
  enabled = true,
  onRelocClick = null,
  onSalineClick = null,
}) => {
  const map = useMap();
  const groupRef = useRef(null);

  const clearLayers = useCallback(() => {
    if (groupRef.current && map) {
      try { map.removeLayer(groupRef.current); } catch (e) { /* */ }
      groupRef.current = null;
    }
  }, [map]);

  const renderLayers = useCallback(() => {
    if (!map || !enabled) return;
    clearLayers();

    const group = L.featureGroup();

    // Site actuel — cercle rouge pointille si EXCLUDED ou A EVITER
    if (siteActuel && siteActuel.lat && siteActuel.lon) {
      const isExcluded = siteActuel.exclusion === 'EXCLUDED' || siteActuel.status === 'A EVITER';
      L.circleMarker([siteActuel.lat, siteActuel.lon], {
        radius: 10,
        color: isExcluded ? '#EF4444' : '#6B7280',
        fillColor: isExcluded ? '#EF4444' : '#6B7280',
        fillOpacity: 0.15,
        weight: 2,
        dashArray: isExcluded ? '6,4' : null,
        interactive: true,
      }).bindTooltip(
        `<div style="font-family:system-ui;font-size:11px;">` +
        `<b style="color:${isExcluded ? '#EF4444' : '#6B7280'}">Site actuel</b><br>` +
        `<span>Composite: ${siteActuel.composite_score}/100</span><br>` +
        `<span style="color:${isExcluded ? '#EF4444' : '#10B981'}">${siteActuel.status || siteActuel.exclusion}</span>` +
        `</div>`,
        { sticky: true, opacity: 0.95 }
      ).addTo(group);
    }

    // Relocalisations (top-3) — cercles organiques + halo
    if (showReloc && relocalisations.length > 0) {
      relocalisations.slice(0, 3).forEach((r, idx) => {
        const colors = RELOC_COLORS[idx] || RELOC_COLORS[2];

        // Halo externe
        L.circleMarker([r.lat, r.lon], {
          radius: 18,
          color: 'transparent',
          fillColor: colors.fill,
          fillOpacity: 0.08,
          weight: 0,
          interactive: false,
        }).addTo(group);

        // Cercle principal
        const marker = L.circleMarker([r.lat, r.lon], {
          radius: 9,
          color: colors.stroke,
          fillColor: colors.fill,
          fillOpacity: 0.35,
          weight: 2.5,
          interactive: true,
        });

        // Tooltip detaille
        const lines = (r.explanation || []).slice(0, 4).join('<br>');
        marker.bindTooltip(
          `<div style="font-family:system-ui;font-size:11px;max-width:220px;">` +
          `<b style="color:${colors.fill}">Relocalisation ${colors.label}</b><br>` +
          `<span>Composite: <b>${r.composite_score}</b>/100</span><br>` +
          `<span>Saline: ${r.saline_score} | Affut: ${r.affut_score}</span><br>` +
          `<span>Distance: ${r.distance_m}m</span>` +
          (lines ? `<hr style="border-color:#333;margin:4px 0"><span style="font-size:10px;color:#aaa">${lines}</span>` : '') +
          `</div>`,
          { sticky: true, opacity: 0.95 }
        );

        marker.on('click', () => { if (onRelocClick) onRelocClick(r, idx); });
        marker.on('mouseover', function () { this.setStyle({ fillOpacity: 0.6, weight: 3.5 }); });
        marker.on('mouseout', function () { this.setStyle({ fillOpacity: 0.35, weight: 2.5 }); });

        // Rank label
        const rankIcon = L.divIcon({
          className: 'phase-a-rank',
          html: `<div style="
            width:16px;height:16px;border-radius:50%;
            background:${colors.fill};color:#fff;
            font-size:9px;font-weight:800;
            display:flex;align-items:center;justify-content:center;
            box-shadow:0 1px 4px rgba(0,0,0,0.4);
            border:1px solid ${colors.stroke};
          ">${idx + 1}</div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8],
        });
        L.marker([r.lat, r.lon], { icon: rankIcon, interactive: false }).addTo(group);
        marker.addTo(group);

        // Ligne de connexion site actuel -> relocalisation
        if (siteActuel && siteActuel.lat) {
          L.polyline([[siteActuel.lat, siteActuel.lon], [r.lat, r.lon]], {
            color: colors.fill,
            weight: 1.5,
            opacity: 0.25,
            dashArray: '4,6',
            interactive: false,
          }).addTo(group);
        }
      });
    }

    // Salines optimales — losanges organiques
    if (showSalines && salines.length > 0) {
      salines.forEach((s, idx) => {
        // Halo
        L.circleMarker([s.lat, s.lon], {
          radius: 14,
          color: 'transparent',
          fillColor: SALINE_COLOR.fill,
          fillOpacity: 0.1,
          weight: 0,
          interactive: false,
        }).addTo(group);

        // Losange organique (4 vertices)
        const sz = 0.00018;
        const lat = s.lat, lon = s.lon;
        const diamond = [
          [lat + sz, lon],
          [lat, lon + sz * 1.3],
          [lat - sz, lon],
          [lat, lon - sz * 1.3],
        ];

        const poly = L.polygon(diamond, {
          color: SALINE_COLOR.stroke,
          fillColor: SALINE_COLOR.fill,
          fillOpacity: 0.45,
          weight: 2,
          interactive: true,
        });

        const expLines = (s.explanation || []).slice(0, 3).join('<br>');
        poly.bindTooltip(
          `<div style="font-family:system-ui;font-size:11px;max-width:200px;">` +
          `<b style="color:${SALINE_COLOR.fill}">Saline #${idx + 1}</b><br>` +
          `<span>Score: <b>${s.score}</b>/100</span><br>` +
          `<span>Distance centre: ${s.distance_centre_m}m</span>` +
          (expLines ? `<hr style="border-color:#333;margin:4px 0"><span style="font-size:10px;color:#aaa">${expLines}</span>` : '') +
          `</div>`,
          { sticky: true, opacity: 0.95 }
        );

        poly.on('click', () => { if (onSalineClick) onSalineClick(s, idx); });
        poly.on('mouseover', function () { this.setStyle({ fillOpacity: 0.7, weight: 3 }); });
        poly.on('mouseout', function () { this.setStyle({ fillOpacity: 0.45, weight: 2 }); });
        poly.addTo(group);
      });
    }

    group.addTo(map);
    groupRef.current = group;
  }, [map, enabled, relocalisations, salines, siteActuel, showReloc, showSalines, clearLayers, onRelocClick, onSalineClick]);

  useEffect(() => {
    renderLayers();
    return () => clearLayers();
  }, [renderLayers, clearLayers]);

  return null;
};

export default PhaseALayerV8;
