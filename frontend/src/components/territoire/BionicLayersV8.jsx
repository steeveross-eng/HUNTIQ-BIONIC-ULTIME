/**
 * BionicLayersV8.jsx — RENDERER V20-INSTITUTIONNEL
 * ==================================================
 * PHASE-INSTITUTIONNELLE-Omega V20
 *
 * CONTOUR:     L.circle 600m, #9E9E9E, 2.2px, pointilles, 0.85
 * CORRIDORS:   4 niveaux (EXTREME/INTENSE/SAISONNIER/NORMAL) + RESEAU
 *              Catmull-Rom, smoothFactor=0
 * ZONES:       Catmull-Rom 22-40 vertices, terrain reel + IA
 * CONTAMINATION: Multi-cones SOURCE=AFFUTS, 3 intensites
 * SALINES:     VALIDEE jaune / A-REPOSITIONNER rouge + suggestion
 * HOTSPOTS:    intensite 1-5
 * AFFUTS:      cercle gris #9E9E9E + X #424242
 * VENT:        delegue a WindFlowLayer (Ventusky)
 *
 * Z-ORDER: contour < zones < corridors < contamination < salines < hotspots < affuts
 * ZERO pression. ZERO buffer. ZERO Bezier. ZERO smoothing. ZERO fallback.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

// ═══ PALETTE BCE-4X V9-INSTITUTIONNEL ═══
const ZONE_COLORS = {
  rut:          { stroke: '#C62828', weight: 2.5 },
  alimentation: { stroke: '#2E7D32', weight: 2.0 },
  repos:        { stroke: '#1565C0', weight: 1.8 },
  eau:          { stroke: '#29B6F6', weight: 1.5 },
  affuts:       { stroke: '#C62828', weight: 2.0 },
};

// CORRIDORS Omega: 4 niveaux
// STYLE-HIERARCHISE V11-SUPRA (Directive III)
// Intensite = Epaisseur + Surbrillance strictement croissantes
// Source: frontend/src/config/territoire_defaults.js CORRIDOR_STYLE_HIERARCHY
import { CORRIDOR_STYLE_HIERARCHY as HIER } from '@/config/territoire_defaults';
const CORRIDOR_STYLES = {
  extreme:    HIER.extreme,     // CRITIQUE #FF0000 4.0px 1.0
  intense:    HIER.intense,     // MAJEUR   #FF6A00 3.2px 0.85
  saisonnier: HIER.saisonnier,  // FORT     #FFC300 2.6px 0.75
  normal:     HIER.normal,      // MODERE   #00B050 2.0px 0.65
  faible:     HIER.faible,      // FAIBLE   #00B0F0 1.4px 0.55 (reserve)
};

const AFFUT_COLOR = '#9E9E9E';
const AFFUT_X_COLOR = '#424242';
const AFFUT_SIZE = { optimal: 8, bon: 7, acceptable: 6 };

const SALINE_COLOR = '#FDD835';
const CONTAM_COLOR = '#FF7043';

const HOTSPOT_COLORS = ['#FFCDD2', '#EF9A9A', '#EF5350', '#E53935', '#B71C1C'];
const HOTSPOT_SIZES = [4, 5, 6, 7, 8];

// CONTOUR-TERRITOIRE 600m
const CONTOUR_COLOR = '#9E9E9E';

const BionicLayersV8 = ({
  bundleData,
  waypointCenter = null,
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  showSalines = true,
  showHotspots = true,
  showWind = true,
  showContamination = true,
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
    if (!map) return;
    // PHASE-PERFORMANCE-Omega: Lazy decharge — si master OFF ou no data, clear + abort
    if (!enabled || !bundleData) {
      clearOwnLayers();
      return;
    }
    clearOwnLayers();

    const group = L.featureGroup();
    const zones = bundleData.zones || [];
    const corridors = bundleData.corridors || [];
    const affuts = bundleData.affuts || [];
    const salines = bundleData.salines || [];
    const hotspots = bundleData.hotspots || [];
    const contamination = bundleData.contamination || null;

    // ═══ Z-0: CONTOUR-TERRITOIRE-Omega 600m ═══
    // Cercle institutionnel centre sur waypoint. Rayon 600m exact.
    // Element visuel AUTONOME. ZERO interaction avec aucun engine.
    if (waypointCenter) {
      const contour = L.circle([waypointCenter.lat, waypointCenter.lng], {
        radius: 600,
        color: CONTOUR_COLOR,
        weight: 2.2,
        opacity: 0.85,
        fillOpacity: 0,
        dashArray: '4,4',
        interactive: false,
      });
      group.addLayer(contour);
    }

    // ═══ Z-2: ZONES (Catmull-Rom V9, smoothFactor=0, ZERO interpolation) ═══
    if (showZones && zones.length > 0) {
      zones.forEach(z => {
        const cfg = ZONE_COLORS[z.type] || ZONE_COLORS.alimentation;
        if (!z.polygon || z.polygon.length < 4) return;

        const poly = L.polygon(z.polygon, {
          color: cfg.stroke,
          weight: cfg.weight,
          opacity: 1.0,
          fillColor: cfg.stroke,
          fillOpacity: 0,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 0,
          interactive: true,
        });

        const t = z.terrain || {};
        const terrain = t.canopy !== undefined
          ? `<br><span style="font-size:9px;color:#888">Canopy ${Math.round(t.canopy*100)}% | Pente ${t.pente_deg}deg | Eau ${t.distance_eau_m}m</span>`
          : '';
        const excl = z.excluded
          ? `<br><span style="font-size:9px;color:#EF4444;font-weight:700">EXCLU: ${z.exclusion_reason}</span>`
          : '';

        poly.bindTooltip(
          `<b style="color:${cfg.stroke}">${z.type}</b> ${z.score}/100${terrain}${excl}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(poly);
      });
    }

    // ═══ Z-2: CORRIDORS-Omega — STYLE-HIERARCHISE V11-SUPRA (Directive III) ═══
    // CRITIQUE #FF0000 4.0px / MAJEUR #FF6A00 3.2px / FORT #FFC300 2.6px / MODERE #00B050 2.0px / FAIBLE #00B0F0 1.4px
    // PRIORITE: defaults hierarchy >> backend-provided style (force homogeneite institutionnelle)
    if (showCorridors && corridors.length > 0) {
      corridors.forEach(c => {
        const path = c.path || [[c.start.lat, c.start.lng], [c.end.lat, c.end.lng]];
        const style = CORRIDOR_STYLES[c.type] || CORRIDOR_STYLES.normal;
        // Directive III: style hierarchise impose (ignore backend overrides)
        const color = style.color;
        const weight = style.weight;
        const opacity = style.opacity;

        const line = L.polyline(path, {
          color: color,
          weight: weight,
          opacity: opacity,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 0,
          interactive: true,
        });

        // ANTI-LEGACY-Omega V11-SUPRA: PURGE fleche polygone pleine
        // (triangle blanc opaque identifie comme couche fantome par DIAGNOSTIC-Omega)
        // Remplace par fleche-ligne stroke-only (2 segments courts, ZERO fill)
        if (path.length >= 3) {
          const midIdx = Math.floor(path.length / 2);
          const prev = path[midIdx - 1] || path[0];
          const mid = path[midIdx];
          const next = path[midIdx + 1] || path[path.length - 1];
          const dx = next[1] - prev[1];
          const dy = next[0] - prev[0];
          const len = Math.sqrt(dx * dx + dy * dy);
          if (len > 0.0001) {
            const arrowSize = 0.00025; // 3x plus petit, zero impact visuel
            const nx = dx / len;
            const ny = dy / len;
            // Tete de fleche en 2 segments V-shape (polyline stroke-only, ZERO fill)
            const tipLat = mid[0] + ny * arrowSize;
            const tipLng = mid[1] + nx * arrowSize;
            const leftLat = mid[0] - ny * arrowSize * 0.6 + nx * arrowSize * 0.5;
            const leftLng = mid[1] - nx * arrowSize * 0.6 - ny * arrowSize * 0.5;
            const rightLat = mid[0] - ny * arrowSize * 0.6 - nx * arrowSize * 0.5;
            const rightLng = mid[1] - nx * arrowSize * 0.6 + ny * arrowSize * 0.5;
            const chev = L.polyline(
              [[leftLat, leftLng], [tipLat, tipLng], [rightLat, rightLng]],
              { color, weight, opacity, lineCap: 'round', lineJoin: 'round', smoothFactor: 0, interactive: false, fill: false }
            );
            group.addLayer(chev);
          }
        }

        const costStr = c.cost_surface !== undefined ? ` | cost:${c.cost_surface}` : '';
        const netStr = c.is_network_link ? ' [RESEAU]' : '';
        line.bindTooltip(
          `<b style="color:${color}">${c.type.toUpperCase()}</b> int:${Math.round(c.intensity)}${costStr} | ${c.species_profile || ''}${netStr}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(line);
      });
    }

    // ═══ Z-4: CONTAMINATION-Omega (multi-cones depuis AFFUTS) ═══
    // SOURCE = AFFUTS OPTIMAUX. ZERO waypoint. 3 intensites par affut.
    if (showContamination && contamination) {
      const cones = Array.isArray(contamination) ? contamination : [contamination];
      cones.forEach(cone => {
        if (!cone.polygon || cone.polygon.length < 3) return;

        const color = cone.color || '#FF7043';
        const opacity = cone.opacity || 0.2;
        const fillOpacity = cone.fill_opacity || 0.1;

        const poly = L.polygon(cone.polygon, {
          color: color,
          weight: 1.2,
          opacity: opacity,
          fillColor: color,
          fillOpacity: fillOpacity,
          dashArray: cone.intensity === 'faible' ? '3,3' : cone.intensity === 'moyen' ? '5,3' : null,
          smoothFactor: 0,
          interactive: true,
        });

        const src = cone.affut_source || {};
        poly.bindTooltip(
          `<b style="color:${color}">Contamination ${cone.intensity}</b><br>` +
          `Portee: ${cone.reach_m}m | Angle: ${cone.cone_angle_deg}deg<br>` +
          `<span style="font-size:9px">Source: Affut ${src.quality || ''} (${src.score || ''})</span>`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(poly);
      });
    }

    // ═══ Z-5: SALINES-V11-SUPRA — JAUNE INSTITUTIONNEL UNIFORME ═══
    // Directive III: toutes salines (VALIDEE + A-REPOSITIONNER) rendues JAUNE #FDD835
    // A-REPOSITIONNER: halo pulse leger opacity 0.45
    if (showSalines && salines.length > 0) {
      salines.forEach(s => {
        const lat = s.lat || s.center?.lat;
        const lon = s.lng || s.lon || s.center?.lng;
        if (!lat || !lon) return;

        const isValidee = s.status === 'SALINE-VALIDEE-Omega';
        const YELLOW_INST = SALINE_COLOR; // #FDD835

        // Halo pulse pour A-REPOSITIONNER (derriere le cercle principal)
        if (!isValidee) {
          const halo = L.circleMarker([lat, lon], {
            radius: 13,
            color: YELLOW_INST,
            fillColor: YELLOW_INST,
            fillOpacity: 0.45,
            weight: 0,
            opacity: 0.7,
            className: 'saline-halo-pulse',
            interactive: false,
          });
          group.addLayer(halo);
        }

        const circle = L.circleMarker([lat, lon], {
          radius: isValidee ? 8 : 7,
          color: YELLOW_INST,
          fillColor: YELLOW_INST,
          fillOpacity: 1.0,
          weight: 2.2,
          opacity: 1.0,
          interactive: true,
        });

        const statusLabel = isValidee ? 'SALINE-VALIDEE-Omega' : 'SALINE-A-REPOSITIONNER-Omega';
        let tooltipHtml = `<b style="color:${YELLOW_INST}">${statusLabel}</b> ${s.score || ''}/100`;
        tooltipHtml += `<br><span style="font-size:9px">Eau: ${s.eau_distance_m || '?'}m ${s.eau_conforme ? 'OK' : 'HORS'}`;
        tooltipHtml += ` | Corridor: ${s.corridor_distance_m || '?'}m ${s.corridor_conforme ? 'OK' : 'HORS'}</span>`;
        // V11-SUPRA: axes scoring si presents
        if (s.score_bio_global != null) {
          tooltipHtml += `<br><span style="font-size:9px;color:#90CAF9">Bio:${s.score_bio_global} Terrain:${s.score_terrain} Reseau:${s.score_reseau} Nutri:${s.score_nutrition} Acc:${s.score_accoutumance}</span>`;
        }
        if (s.statut_institutionnel) {
          tooltipHtml += `<br><span style="font-size:9px;color:#FDD835">Statut: ${s.statut_institutionnel}</span>`;
        }
        if (s.recommandations && s.recommandations.length) {
          tooltipHtml += `<br><span style="font-size:9px;color:#CE93D8">Reco: ${s.recommandations.slice(0, 2).join('; ')}</span>`;
        }
        if (s.suggestion) {
          tooltipHtml += `<br><span style="font-size:9px;color:#4CAF50">Suggestion: lat=${s.suggestion.lat} lon=${s.suggestion.lon} (score ${s.suggestion.score})</span>`;
        }

        circle.bindTooltip(tooltipHtml, { sticky: true, opacity: 0.95 });
        group.addLayer(circle);

        // Suggestion de repositionnement (visible seulement si repositionnee)
        if (s.suggestion && !isValidee) {
          const sg = s.suggestion;
          const sugMarker = L.circleMarker([sg.lat, sg.lon], {
            radius: 5,
            color: '#4CAF50',
            fillColor: '#4CAF50',
            fillOpacity: 0.4,
            weight: 1.5,
            opacity: 0.8,
            dashArray: '2,2',
            interactive: true,
          });
          sugMarker.bindTooltip(
            `<b style="color:#4CAF50">Position suggeree</b><br>Eau: ${sg.eau_distance_m}m | Corridor: ${sg.corridor_distance_m}m`,
            { sticky: true, opacity: 0.95 }
          );
          group.addLayer(sugMarker);

          // Ligne pointillee saline → suggestion
          const line = L.polyline([[lat, lon], [sg.lat, sg.lon]], {
            color: '#4CAF50',
            weight: 1,
            opacity: 0.5,
            dashArray: '3,5',
            interactive: false,
          });
          group.addLayer(line);
        }
      });
    }

    // ═══ Z-6: HOTSPOTS (intensite 1-5) ═══
    if (showHotspots && hotspots.length > 0) {
      hotspots.forEach(h => {
        const lat = h.lat || h.center?.lat;
        const lon = h.lng || h.lon || h.center?.lng;
        if (!lat || !lon) return;

        const intensity = h.intensity || 50;
        const level = Math.min(4, Math.max(0, Math.floor(intensity / 20)));
        const color = HOTSPOT_COLORS[level];
        const size = HOTSPOT_SIZES[level];

        const circle = L.circleMarker([lat, lon], {
          radius: size,
          color: color,
          fillColor: color,
          fillOpacity: 0.6,
          weight: 2,
          opacity: 1.0,
          interactive: true,
        });
        circle.bindTooltip(
          `<b style="color:${color}">Hotspot</b> intensite:${level+1}/5 (${Math.round(intensity)})`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(circle);
      });
    }

    // ═══ Z-7: AFFUTS-Omega (FIXE PERMANENT + TEMPORAIRES) ═══
    if (showAffuts && affuts.length > 0) {
      affuts.forEach(a => {
        const isFixed = a.type === 'FIXE_PERMANENT';
        const rend = a.renderer || {};
        const color = rend.color || (isFixed ? AFFUT_COLOR : '#1E88E5');
        const weight = rend.weight || (isFixed ? 3 : 2.4);
        const fillOpacity = rend.fill_opacity || (isFixed ? 0.35 : 0.3);
        const sz_px = isFixed ? 10 : 7;

        const circle = L.circleMarker([a.lat, a.lng], {
          radius: sz_px,
          color: color,
          fillColor: color,
          fillOpacity: fillOpacity,
          weight: weight,
          opacity: 1.0,
          interactive: true,
        });

        // Symbole central: X pour fixe, fleche pour temporaire
        if (isFixed) {
          const xIcon = L.divIcon({
            className: 'affut-fixe-omega',
            html: `<div style="width:${sz_px*2}px;height:${sz_px*2}px;display:flex;align-items:center;justify-content:center;font-size:${sz_px+4}px;font-weight:900;color:${AFFUT_X_COLOR};line-height:1;">X</div>`,
            iconSize: [sz_px*2, sz_px*2],
            iconAnchor: [sz_px, sz_px],
          });
          L.marker([a.lat, a.lng], { icon: xIcon, interactive: false }).addTo(group);
        } else {
          // Fleche directionnelle pour temporaire
          const arrowRad = Math.PI * a.orientation_deg / 180;
          const arrowLen = 0.0006;
          const tipLat = a.lat + Math.cos(arrowRad) * arrowLen;
          const tipLng = a.lng + Math.sin(arrowRad) * arrowLen / Math.cos(a.lat * Math.PI / 180);
          const arrowLine = L.polyline([[a.lat, a.lng], [tipLat, tipLng]], {
            color: color, weight: 2, opacity: 0.8, interactive: false,
          });
          group.addLayer(arrowLine);
        }

        // Tooltip enrichi
        const typeLabel = isFixed ? 'FIXE PERMANENT' : 'TEMPORAIRE';
        let tooltip = `<b style="color:${color}">Affut ${typeLabel}</b> ${a.score}/100`;
        tooltip += `<br><span style="font-size:9px">${a.description || ''}</span>`;
        tooltip += `<br><span style="font-size:9px">Corridor: ${a.corridor_type || '?'} a ${a.distance_corridor_m || '?'}m | Orient: ${a.orientation_deg}deg</span>`;
        if (a.distance_saline_m) {
          tooltip += `<br><span style="font-size:9px">Saline: ${a.distance_saline_m}m (score ${a.saline_score || '?'})</span>`;
        }

        circle.bindTooltip(tooltip, { sticky: true, opacity: 0.95 });
        group.addLayer(circle);
      });
    }

    group.addTo(map);
    groupRef.current = group;

    if (onDataLoadedRef.current) {
      onDataLoadedRef.current({
        zones_count: zones.length,
        corridors_count: corridors.length,
        affuts_count: affuts.length,
        salines_count: salines.length,
        hotspots_count: hotspots.length,
        contamination: Array.isArray(contamination) ? contamination.length : 0,
        engine: 'V20-INSTITUTIONNEL',
        esi_omega: bundleData.esi_omega,
      });
    }
  }, [map, bundleData, waypointCenter, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, showContamination, clearOwnLayers]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;
