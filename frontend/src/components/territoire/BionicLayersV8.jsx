/**
 * BionicLayersV8.jsx — Rendu V8 ORGANIQUE conforme STEEVE-MAX
 * =============================================================
 * V8-VISUAL-STEVE-MAX-Omega:
 * - Zones: polygones organiques, contours opaques 2.5px, interieur TRANSPARENT
 * - Corridors: courbes Bezier, largeur variable intensite, opacite 0.85
 * - Affuts: icones vectorielles, orientation vent, halo discret
 * - ZERO micro-points, ZERO artefacts, ZERO rectangles
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const ZONE_COLORS = {
  alimentation: { stroke: '#4CAF50', label: 'Alimentation' },
  repos:        { stroke: '#2196F3', label: 'Repos' },
  rut:          { stroke: '#FF9800', label: 'Rut' },
  affuts:       { stroke: '#F44336', label: 'Affuts' },
  eau:          { stroke: '#00BCD4', label: 'Eau' },
};

const CORRIDOR_STYLES = {
  critique: { color: '#FF0000', weight: 4.0, opacity: 0.85, label: 'Critique' },
  majeur:   { color: '#CC0000', weight: 3.5, opacity: 0.85, label: 'Majeur' },
  fort:     { color: '#FF8C00', weight: 3.0, opacity: 0.85, label: 'Fort' },
  modere:   { color: '#FFD700', weight: 2.5, opacity: 0.85, label: 'Modere' },
  faible:   { color: '#9E9E9E', weight: 2.0, opacity: 0.85, label: 'Faible' },
};

const AFFUT_QUALITY = {
  optimal:    { color: '#10B981', radius: 8, halo: 14 },
  bon:        { color: '#F59E0B', radius: 7, halo: 12 },
  acceptable: { color: '#EF4444', radius: 6, halo: 10 },
};

const BionicLayersV8 = ({
  bundleData,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  enabled = true,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const groupRef = useRef(null);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const clearOwnLayers = useCallback(() => {
    if (groupRef.current && map) {
      try { map.removeLayer(groupRef.current); } catch (e) { /* */ }
      groupRef.current = null;
    }
  }, [map]);

  const renderLayers = useCallback(() => {
    if (!map || !enabled || !bundleData) return;
    clearOwnLayers();

    const group = L.featureGroup();
    const zones = bundleData.zones || [];
    const corridors = bundleData.corridors || [];
    const affuts = bundleData.affuts || [];

    // ═══ ZONES ORGANIQUES (contour opaque, interieur TRANSPARENT) ═══
    if (showZones && zones.length > 0) {
      zones.forEach(z => {
        const colors = ZONE_COLORS[z.type] || ZONE_COLORS.alimentation;
        if (z.polygon && z.polygon.length >= 4) {
          const poly = L.polygon(z.polygon, {
            color: colors.stroke,
            weight: 2.5,
            opacity: 1.0,
            fillColor: colors.stroke,
            fillOpacity: 0,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: true,
          });
          poly.bindTooltip(
            `<b style="color:${colors.stroke}">${colors.label}</b><br><span style="font-size:10px">Score: ${z.score}/100</span>`,
            { sticky: true, opacity: 0.92 }
          );
          poly.on('mouseover', function () { this.setStyle({ weight: 4, fillOpacity: 0.08 }); });
          poly.on('mouseout', function () { this.setStyle({ weight: 2.5, fillOpacity: 0 }); });
          group.addLayer(poly);
        }
      });
    }

    // ═══ CORRIDORS COURBES (intensite variable) ═══
    if (showCorridors && corridors.length > 0) {
      const order = { faible: 0, modere: 1, fort: 2, majeur: 3, critique: 4 };
      const sorted = [...corridors].sort((a, b) => (order[a.type] || 0) - (order[b.type] || 0));

      sorted.forEach(c => {
        const style = CORRIDOR_STYLES[c.type] || CORRIDOR_STYLES.faible;
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];

        // Glow for critique + majeur
        if (c.type === 'critique' || c.type === 'majeur') {
          L.polyline(path, {
            color: style.color, weight: style.weight + 5, opacity: 0.12,
            lineCap: 'round', lineJoin: 'round', interactive: false,
          }).addTo(group);
          L.polyline(path, {
            color: style.color, weight: style.weight + 2.5, opacity: 0.25,
            lineCap: 'round', lineJoin: 'round', interactive: false,
          }).addTo(group);
        }

        const line = L.polyline(path, {
          color: style.color,
          weight: style.weight,
          opacity: style.opacity,
          lineCap: 'round',
          lineJoin: 'round',
          interactive: true,
        });
        line.bindTooltip(
          `<b style="color:${style.color}">${style.label}</b><br><span style="font-size:10px">Intensite: ${c.intensity}</span>`,
          { sticky: true }
        );
        line.on('mouseover', function () { this.setStyle({ weight: style.weight + 2 }); });
        line.on('mouseout', function () { this.setStyle({ weight: style.weight }); });
        group.addLayer(line);
      });
    }

    // ═══ AFFUTS ENRICHIS (icone + halo + orientation) ═══
    if (showAffuts && affuts.length > 0) {
      affuts.forEach(a => {
        const q = AFFUT_QUALITY[a.quality] || AFFUT_QUALITY.acceptable;

        // Halo discret
        L.circleMarker([a.lat, a.lng], {
          radius: q.halo, color: 'transparent',
          fillColor: q.color, fillOpacity: 0.12,
          weight: 0, interactive: false,
        }).addTo(group);

        // Affut marker (triangle oriented by wind)
        const orientRad = (a.orientation_deg || 0) * Math.PI / 180;
        const sz = 0.00015;
        const cos_lat = Math.max(0.5, Math.cos(a.lat * Math.PI / 180));
        const tip = [a.lat + Math.cos(orientRad) * sz * 2, a.lng + Math.sin(orientRad) * sz * 2 / cos_lat];
        const left = [a.lat + Math.cos(orientRad + 2.3) * sz, a.lng + Math.sin(orientRad + 2.3) * sz / cos_lat];
        const right = [a.lat + Math.cos(orientRad - 2.3) * sz, a.lng + Math.sin(orientRad - 2.3) * sz / cos_lat];
        const triangle = L.polygon([tip, left, right], {
          color: q.color,
          fillColor: q.color,
          fillOpacity: 0.85,
          weight: 1.5,
          opacity: 1.0,
          interactive: true,
        });
        triangle.bindTooltip(
          `<b style="color:${q.color}">Affut ${a.quality}</b><br>` +
          `<span style="font-size:10px">Zone: ${a.zone_type} (${a.zone_score})<br>Orient: ${a.orientation_deg}&deg;</span>`,
          { sticky: true }
        );
        group.addLayer(triangle);
      });
    }

    group.addTo(map);
    groupRef.current = group;

    if (onDataLoadedRef.current) {
      onDataLoadedRef.current({
        zones_count: zones.length,
        corridors_count: corridors.length,
        affuts_count: affuts.length,
        engine: 'V8-MAP-BUNDLE',
      });
    }
  }, [map, bundleData, enabled, showZones, showCorridors, showAffuts, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;
