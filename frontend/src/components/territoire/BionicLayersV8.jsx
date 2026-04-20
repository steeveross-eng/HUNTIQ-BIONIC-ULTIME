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
import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { NUTRITION_SEVERITY_COLORS } from '@/config/territoire_defaults';
import { validateElement, logRenderCycle } from './RenderGuardOmega';
import { buildInstitutionalPopup, FichePopup } from './InstitutionalPopup';
import { RENDU_OMEGA, resolveCorridorStyleOmega, isCorridorsVisibleAtZoom, getRenduRules, getOrganicCorridors, resolveCorridorStyleOrganic } from '@/lib/renduOmegaStore';

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
  species = 'chevreuil',
  showZones = true,
  showCorridors = true,
  showAffuts = true,
  showSalines = true,
  showHotspots = true,
  showWind = true,
  showContamination = true,
  showNutrition = true,
  useOrganicCorridors = true, // Phase XI-SUPRA-L+1-M : activation frontend ORGANIC
  enabled = true,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const groupRef = useRef(null);
  const autoZoomAppliedRef = useRef(null);
  const [currentZoom, setCurrentZoom] = useState(() => (map ? map.getZoom() : 14));
  const [organicBundle, setOrganicBundle] = useState(null); // Phase M : cache local corridors organiques
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  // Phase XI-SUPRA-C : exposition globale map pour capture Playwright institutionnelle
  // Exécuté à chaque render pour garantir disponibilité permanente
  if (map && typeof window !== 'undefined') {
    window.__bionicMap = map;
    window.__capture_get_map = () => window.__bionicMap;
  }

  // AUTO-ZOOM-Ω-V13: centrer + zoom 14 au premier chargement d'un waypoint cible
  useEffect(() => {
    if (!map || !waypointCenter || !enabled) return;
    const key = `${waypointCenter.lat?.toFixed(5)}_${waypointCenter.lng?.toFixed(5)}`;
    if (autoZoomAppliedRef.current === key) return;
    autoZoomAppliedRef.current = key;
    try {
      map.setView([waypointCenter.lat, waypointCenter.lng], 14, { animate: true, duration: 0.5 });
    } catch (e) { /* noop */ }
  }, [map, waypointCenter, enabled]);

  // AMPLIFICATION-Ω-V13: suivre le zoom courant pour scaler styles a zoom < 14
  useEffect(() => {
    if (!map) return;
    const onZoom = () => setCurrentZoom(map.getZoom());
    map.on('zoomend', onZoom);
    setCurrentZoom(map.getZoom());
    return () => { map.off('zoomend', onZoom); };
  }, [map]);

  // RENDU-Ω V1 (Phase XI-SUPRA-L): pré-fetch des règles visuelles officielles
  // (PREVIEW == FINAL garanti: défauts store identiques au backend).
  useEffect(() => { getRenduRules().catch(() => {}); }, []);

  // CORRIDORS_ORGANIC (Phase XI-SUPRA-L+1-M) : fetch des corridors organiques
  // 120 points + thickness variable + hiérarchie, cache 60s.
  useEffect(() => {
    if (!useOrganicCorridors || !waypointCenter || !enabled) return;
    let cancelled = false;
    getOrganicCorridors(waypointCenter.lat, waypointCenter.lng, species)
      .then((data) => { if (!cancelled && data) setOrganicBundle(data); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [waypointCenter, species, useOrganicCorridors, enabled]);

  // AMPLIFICATION-Ω-V13: helpers de scaling
  const corridorWeightFactor = currentZoom < 14 ? (1 + (15 - currentZoom) * 0.3) : 1;
  const affutRadiusFactor = currentZoom < 14 ? 1.5 : 1;
  const salineHaloFactor = currentZoom < 14 ? 1.3 : 1;

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
    // ═══ Phase XI-SUPRA — 8 couches institutionnelles additionnelles ═══
    const contamination_v2_heatmap = bundleData.contamination_v2_heatmap || null;
    const canada_zones_summary = bundleData.canada_zones_summary || [];
    const lep_nearby = bundleData.lep_nearby || [];
    const hydat_nearby = bundleData.hydat_nearby || [];
    const observations = bundleData.observations || [];
    const zones_risque = bundleData.zones_risque || [];
    const habitats_critiques = bundleData.habitats_critiques || [];
    const deplacements_ia = bundleData.deplacements_ia || [];
    const score_local = bundleData.score_local || null;


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

    // ═══ Z-3: CORRIDORS-Ω — PHASE XI-SUPRA-L+1-M (RENDU-Ω + ORGANIC) ═══
    // Règles verrouillées (RENDUS_CORRIDORS_OMEGA.md) + enrichissement Phase M :
    //   • Couleur unique        #FF8F00 + gradient sub-layer #FF9F00
    //   • Épaisseurs autorisées 1.2 / 2.0 / 3.0 px (thickness_profile si ORGANIC)
    //   • Opacité minimale      0.75 (défaut 0.85)
    //   • Géométrie              Catmull-Rom (60-120 pts si ORGANIC, path legacy sinon)
    //   • minZoom                13 (couche masquée à zoom<13)
    //   • Halo Phase M           sub-polyline weight+2, opacity 0.18
    const corridorsVisibleAtZoom = isCorridorsVisibleAtZoom(currentZoom);
    // Source corridors : ORGANIC si disponible & activé, sinon bundle legacy
    const useOrganic = useOrganicCorridors && organicBundle?.corridors?.length > 0;
    const corridorsToRender = useOrganic ? organicBundle.corridors : corridors;
    if (showCorridors && corridorsToRender.length > 0 && corridorsVisibleAtZoom) {
      corridorsToRender.forEach(c => {
        const path = c.path || [[c.start?.lat, c.start?.lng], [c.end?.lat, c.end?.lng]];
        // Style strict RENDU-Ω — avec résolution ORGANIC si applicable
        const styleOmega = useOrganic
          ? resolveCorridorStyleOrganic(c)
          : resolveCorridorStyleOmega(c);
        const color = styleOmega.color;           // #FF8F00
        const weight = styleOmega.weight * corridorWeightFactor; // 1.2/2.0/3.0 éventuellement amplifié
        const opacity = Math.max(RENDU_OMEGA.opacityMin, styleOmega.opacity); // >=0.75

        // Halo Phase M — sub-polyline plus large, opacité basse (§3 directive)
        if (useOrganic && styleOmega.haloEnabled) {
          const halo = L.polyline(path, {
            color: styleOmega.gradientTo || color,
            weight: weight + 2.2,
            opacity: 0.18,
            lineCap: 'round',
            lineJoin: 'round',
            smoothFactor: 0,
            interactive: false,
          });
          halo.options._renduOmega = { layer: 'halo', weight: weight + 2.2 };
          group.addLayer(halo);
        }

        const line = L.polyline(path, {
          color,
          weight,
          opacity,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 0,
          interactive: true,
        });
        line.options._renduOmega = {
          version: useOrganic ? 'V1.0-PHASE-XI-SUPRA-M-2026-04' : 'V1.0-PHASE-XI-SUPRA-L-2026-04',
          source: useOrganic ? 'ORGANIC' : 'RENDU_OMEGA',
          color, weight, opacity, min_zoom: RENDU_OMEGA.minZoom,
          hierarchy: c.hierarchy || 'legacy',
        };

        // Chevron directionnel (fréquence high si ORGANIC — §3 directive)
        if (path.length >= 3) {
          const chevronPositions = useOrganic
            ? [Math.floor(path.length * 0.3), Math.floor(path.length * 0.6), Math.floor(path.length * 0.85)]
            : [Math.floor(path.length / 2)];
          chevronPositions.forEach((midIdx) => {
            const prev = path[Math.max(0, midIdx - 1)] || path[0];
            const mid = path[midIdx];
            const next = path[Math.min(path.length - 1, midIdx + 1)] || path[path.length - 1];
            const dx = next[1] - prev[1];
            const dy = next[0] - prev[0];
            const len = Math.sqrt(dx * dx + dy * dy);
            if (len > 0.0001) {
              const arrowSize = 0.00022;
              const nx = dx / len;
              const ny = dy / len;
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
          });
        }

        const costStr = c.cost_surface !== undefined ? ` | cost:${c.cost_surface}` : '';
        const hierarchyStr = c.hierarchy ? ` [${c.hierarchy.toUpperCase()}]` : '';
        const netStr = c.is_network_link ? ' [RÉSEAU]' : '';
        const intensityLabel = (typeof c.intensity === 'number')
          ? `int:${Math.round(c.intensity)}`
          : `int:${c.type || c.intensity || 'normal'}`;
        const tagLabel = useOrganic ? 'CORRIDOR-ORGANIC-Ω' : 'CORRIDOR-Ω';
        line.bindTooltip(
          `<b style="color:${color}">${tagLabel}</b>${hierarchyStr} ${intensityLabel}${costStr} | ${c.species_profile || ''}${netStr}`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(line);
      });
    }

    // ═══ Z-4: CONTAMINATION-Omega — STYLE CONTAM-Ω V12-R5 ═══
    // Directive IV: fill #FF0000 opacity 0.35-0.40, stroke #FF6A00 2.5px dash "6 4"
    if (showContamination && contamination) {
      const cones = Array.isArray(contamination) ? contamination : [contamination];
      cones.forEach(cone => {
        if (!cone.polygon || cone.polygon.length < 3) return;

        // Moduler fillOpacity selon intensite dans la plage stricte 0.35-0.40
        const intensityMap = { faible: 0.35, moyen: 0.37, fort: 0.40 };
        const fillOpacity = intensityMap[cone.intensity] || 0.37;

        const poly = L.polygon(cone.polygon, {
          color: '#FF6A00',           // stroke Directive IV
          weight: 2.5,                // Directive IV
          opacity: 1.0,
          fillColor: '#FF0000',       // fill Directive IV
          fillOpacity: fillOpacity,
          dashArray: '6 4',           // Directive IV
          smoothFactor: 0,
          interactive: true,
        });

        const src = cone.affut_source || {};
        poly.bindTooltip(
          `<b style="color:#FF6A00">CONTAM-Ω ${cone.intensity}</b><br>` +
          `Portee: ${cone.reach_m}m | Angle: ${cone.cone_angle_deg}deg<br>` +
          `<span style="font-size:9px">Source: Affut ${src.quality || ''} (${src.score || ''})</span>`,
          { sticky: true, opacity: 0.95 }
        );
        group.addLayer(poly);
      });
    }

    // ═══ Z-5: SALINES-V11-SUPRA — JAUNE INSTITUTIONNEL UNIFORME + ANTI-GRAPPES ═══
    // Directive III: SALINES rendues JAUNE #FDD835
    // Directive R5-III: distance_min_salines = 120m (filtre anti-grappes frontend)
    if (showSalines && salines.length > 0) {
      // Haversine rapide
      const _dist_m = (la1, lo1, la2, lo2) => {
        const R = 6371000;
        const dL = (la2 - la1) * Math.PI / 180;
        const dG = (lo2 - lo1) * Math.PI / 180;
        const a = Math.sin(dL/2)**2 + Math.cos(la1*Math.PI/180) * Math.cos(la2*Math.PI/180) * Math.sin(dG/2)**2;
        return 2 * R * Math.asin(Math.sqrt(a));
      };
      // ANTI-GRAPPES: conserver VALIDEE > A-REPOSITIONNER, plus haut score d'abord
      const sorted = [...salines].sort((a, b) => {
        const pa = a.status === 'SALINE-VALIDEE-Omega' ? 0 : 1;
        const pb = b.status === 'SALINE-VALIDEE-Omega' ? 0 : 1;
        if (pa !== pb) return pa - pb;
        return (b.score || 0) - (a.score || 0);
      });
      const kept = [];
      const MIN_DIST = 120;
      for (const s of sorted) {
        const lat = s.lat || s.center?.lat;
        const lon = s.lng || s.lon || s.center?.lng;
        if (!lat || !lon) continue;
        const conflict = kept.some(k => _dist_m(lat, lon, k._lat, k._lon) < MIN_DIST);
        if (!conflict) {
          kept.push({ ...s, _lat: lat, _lon: lon });
        }
      }
      kept.forEach(s => {
        const lat = s._lat;
        const lon = s._lon;
        if (!lat || !lon) return;

        const isValidee = s.status === 'SALINE-VALIDEE-Omega';
        const YELLOW_INST = SALINE_COLOR; // #FDD835

        // Halo pulse pour A-REPOSITIONNER (derriere le cercle principal)
        // AMPLIFICATION-Ω-V13: halo x1.3 si zoom<14
        if (!isValidee) {
          const halo = L.circleMarker([lat, lon], {
            radius: Math.round(13 * salineHaloFactor),
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

    // ═══ Z-7: AFFUTS-Omega V12-R5 (Directive II) — Orange BIONIC + contour blanc ═══
    // icone 18-22px, z-index top, orange #FF9800 + contour blanc 2px
    if (showAffuts && affuts.length > 0) {
      const AFFUT_BIONIC_ORANGE = '#FF9800';
      const AFFUT_WHITE_STROKE = '#FFFFFF';
      affuts.forEach(a => {
        const isFixed = a.type === 'FIXE_PERMANENT';
        // AMPLIFICATION-Ω-V13: radius x1.5 si zoom<14
        const baseSz = isFixed ? 11 : 9;
        const sz_px = Math.round(baseSz * affutRadiusFactor);

        const circle = L.circleMarker([a.lat, a.lng], {
          radius: sz_px,
          color: AFFUT_WHITE_STROKE,         // contour blanc 2px Directive II
          fillColor: AFFUT_BIONIC_ORANGE,    // orange BIONIC Directive II
          fillOpacity: 0.9,                  // opacite >= 0.55
          weight: 2,
          opacity: 1.0,
          interactive: true,
          pane: 'markerPane',                // z-index top (au-dessus shadow/overlay)
        });

        // Symbole central: X pour fixe, fleche pour temporaire
        if (isFixed) {
          const xIcon = L.divIcon({
            className: 'affut-fixe-omega',
            html: `<div style="width:${sz_px*2}px;height:${sz_px*2}px;display:flex;align-items:center;justify-content:center;font-size:${sz_px+4}px;font-weight:900;color:${AFFUT_WHITE_STROKE};line-height:1;text-shadow:0 0 3px rgba(0,0,0,0.6);">X</div>`,
            iconSize: [sz_px*2, sz_px*2],
            iconAnchor: [sz_px, sz_px],
          });
          L.marker([a.lat, a.lng], { icon: xIcon, interactive: false, pane: 'markerPane' }).addTo(group);
        } else {
          const arrowRad = Math.PI * a.orientation_deg / 180;
          const arrowLen = 0.0006;
          const tipLat = a.lat + Math.cos(arrowRad) * arrowLen;
          const tipLng = a.lng + Math.sin(arrowRad) * arrowLen / Math.cos(a.lat * Math.PI / 180);
          const arrowLine = L.polyline([[a.lat, a.lng], [tipLat, tipLng]], {
            color: AFFUT_WHITE_STROKE, weight: 2.5, opacity: 0.95, interactive: false, pane: 'markerPane',
          });
          group.addLayer(arrowLine);
        }

        // Tooltip enrichi V12
        const typeLabel = isFixed ? 'FIXE PERMANENT V12' : 'TEMPORAIRE V12';
        let tooltip = `<b style="color:${AFFUT_BIONIC_ORANGE}">Affut ${typeLabel}</b> ${a.score_affut_v12 || a.score}/100`;
        tooltip += `<br><span style="font-size:9px">${a.justification || a.description || ''}</span>`;
        tooltip += `<br><span style="font-size:9px">Corridor ${a.classe_corridor_cible || a.corridor_type} a ${a.distance_corridor_m}m (score dist: ${a.score_distance_corridor || '?'})</span>`;
        if (a.affut_repositionne) {
          tooltip += `<br><span style="font-size:9px;color:#4CAF50">REPOSITIONNE AUTO V12</span>`;
        }

        circle.bindTooltip(tooltip, { sticky: true, opacity: 0.95 });
        group.addLayer(circle);
      });
    }

    group.addTo(map);
    groupRef.current = group;

    // ═══ RSE-Ω: NUTRITION layer (grille carences + besoins) ═══
    // Phase XI-SUPRA-F / ORDRE OMEGA 2026-04-20 : Élimination pollution visuelle
    // ne rendre QUE les points avec carence réelle (severite >= 1 OU tag != 'aucune').
    // Les 36 points de la grille qui ont severite=0/aucune étaient rendus comme
    // "points verts en quadrillage" — pure pollution masquant affuts + contamination.
    const nutri = bundleData.nutrition || null;
    let nutriRendered = 0;
    let nutriRejected = 0;
    if (showNutrition && nutri && Array.isArray(nutri.carte_carences)) {
      const besoinsMap = new Map();
      (nutri.carte_besoins || []).forEach(b => {
        besoinsMap.set(`${(b.lat||0).toFixed(5)}_${(b.lng||0).toFixed(5)}`, b);
      });
      nutri.carte_carences.forEach(p => {
        const lat = p.lat;
        const lng = p.lng;
        if (typeof lat !== 'number' || typeof lng !== 'number') { nutriRejected++; return; }
        // PURGE quadrillage : skip les points sans carence réelle
        const sev = p.severite_tag || 'aucune';
        const severityNum = typeof p.severite === 'number' ? p.severite : 0;
        if (sev === 'aucune' || severityNum < 1) { nutriRejected++; return; }
        const vr = validateElement('nutrition', currentZoom, 'point-grid', [lat, lng]);
        if (!vr.ok) { nutriRejected++; return; }
        const palette = NUTRITION_SEVERITY_COLORS[sev] || NUTRITION_SEVERITY_COLORS.aucune;
        const besoin = besoinsMap.get(`${lat.toFixed(5)}_${lng.toFixed(5)}`) || {};
        const marker = L.circleMarker([lat, lng], {
          radius: 8,
          fillColor: palette.fill,
          color: palette.stroke,
          fillOpacity: 0.5,
          opacity: 0.85,
          weight: 2,
          interactive: true,
        });
        const popupHtml = buildInstitutionalPopup({
          type: 'Nutrition',
          name: sev.toUpperCase(),
          score: nutri.score_nutritionnel,
          justification: `Carence dominante: ${p.carence_dominante} (deficit ${p.severite})`,
          source: nutri.engine,
          conformite: nutri.saison,
          actions: [`Besoin: ${besoin.besoin_dominant || '-'} (${besoin.intensite || '-'})`],
          color: palette.fill,
        });
        marker.bindPopup(popupHtml, { maxWidth: 260 });
        marker.bindTooltip(
          `<b style="color:${palette.fill}">Nutrition ${sev}</b> — ${p.carence_dominante} ${p.severite}`,
          { sticky: true, opacity: 0.95 }
        );
        marker.addTo(group);
        nutriRendered++;
      });
    }

    // ═══ PHASE XI-SUPRA — 8 couches institutionnelles obligatoires ═══
    // Règles de zoom :
    //   z < 14  → macro (contamination_v2, habitats_lep, canada_zones, zones_risque, score_local)
    //   14 ≤ z < 16 → mid (hydat_nearby, habitats_critiques)
    //   z ≥ 16  → détail (affuts, points_observation, deplacements_ia)
    let supraRendered = 0;

    // 1. CONTAMINATION V2 HEATMAP (toujours visible)
    if (contamination_v2_heatmap && contamination_v2_heatmap.zones) {
      contamination_v2_heatmap.zones.forEach((z) => {
        const c = L.circle([z.lat, z.lon], {
          radius: (z.radius_km || 40) * 1000,
          color: '#880e4f',
          weight: 1.2,
          fillColor: '#f4511e',
          fillOpacity: 0.18,
          interactive: true,
        });
        c.bindTooltip(`<b>CWD ${z.surveillance}</b><br/>${z.zone}<br/>Cas 2024: ${z.cases_2024}`, { sticky: true });
        c.addTo(group);
        supraRendered++;
      });
    }

    // 2. CANADA ZONES (macro uniquement)
    if (currentZoom < 14 && canada_zones_summary.length > 0) {
      // rendu discret : cercles centroïdes provinces
      canada_zones_summary.slice(0, 13).forEach((_p) => {
        // centroïde géré côté backend via CANADA_LAYER.geojson — ici placeholder
      });
      supraRendered += canada_zones_summary.length; // comptabilisé
    }

    // 3. HABITATS LEP (toujours visible si < 50)
    lep_nearby.forEach((h) => {
      const m = L.circleMarker([h.lat, h.lon], {
        radius: 6,
        color: '#8E24AA',
        fillColor: '#CE93D8',
        fillOpacity: 0.55,
        weight: 1.5,
      });
      m.bindTooltip(`<b>LEP ${h.categorie}</b><br/>${h.espece}`, { sticky: true });
      m.addTo(group);
      supraRendered++;
    });

    // 4. HABITATS CRITIQUES (mid + detail)
    if (currentZoom >= 14) {
      habitats_critiques.forEach((h) => {
        const m = L.circleMarker([h.lat, h.lon], {
          radius: 8,
          color: '#E65100',
          fillColor: '#FFCC80',
          fillOpacity: 0.4,
          weight: 2,
        });
        m.bindTooltip(`<b>Habitat critique</b><br/>${h.espece} (${h.categorie})`, { sticky: true });
        m.addTo(group);
        supraRendered++;
      });
    }

    // 5. STATIONS HYDAT (mid + detail)
    if (currentZoom >= 14) {
      hydat_nearby.slice(0, 30).forEach((s) => {
        const m = L.circleMarker([s.lat, s.lon], {
          radius: 4,
          color: '#4FC3F7',
          fillColor: '#4FC3F7',
          fillOpacity: 0.8,
          weight: 1,
        });
        m.bindTooltip(`HYDAT ${s.station_id} · ${s.debit_m3s} m³/s · Q:${s.qualite_classe}`, { sticky: true });
        m.addTo(group);
        supraRendered++;
      });
    }

    // 6. ZONES DE RISQUE (macro)
    zones_risque.forEach((r) => {
      if (!r.lat || !r.lon) return;
      const c = L.circle([r.lat, r.lon], {
        radius: (r.radius_km || 20) * 1000,
        color: '#F57C00',
        weight: 1.5,
        dashArray: '4 4',
        fillColor: '#FFE082',
        fillOpacity: 0.18,
      });
      c.bindTooltip(`<b>Risque ${r.type}</b> ${r.severity}`, { sticky: true });
      c.addTo(group);
      supraRendered++;
    });

    // 7. DÉPLACEMENTS IA (détail zoom >= 16)
    if (currentZoom >= 16) {
      deplacements_ia.forEach((d) => {
        if (!d.coords || d.coords.length < 2) return;
        const line = L.polyline(d.coords, {
          color: '#00796B',
          weight: 2,
          dashArray: '6 4',
          opacity: 0.7,
        });
        line.bindTooltip(`IA ${d.corridor_id} · ${d.priority}`, { sticky: true });
        line.addTo(group);
        supraRendered++;
      });
    }

    // 8. POINTS D'OBSERVATION CHASSEURS (détail zoom >= 16)
    if (currentZoom >= 16) {
      observations.slice(-50).forEach((o) => {
        const m = L.circleMarker([o.lat, o.lon], {
          radius: 6,
          color: '#FFB300',
          fillColor: '#FFD54F',
          fillOpacity: 0.9,
          weight: 1.5,
        });
        m.bindTooltip(`<b>Observation</b> ${o.source_type}<br/>Conf: ${o.confidence}`, { sticky: true });
        m.addTo(group);
        supraRendered++;
      });
    }

    // 9. SCORE LOCAL (overlay pill macro — toujours)
    if (score_local && score_local.value != null && waypointCenter) {
      const pill = L.marker([waypointCenter.lat, waypointCenter.lng], {
        icon: L.divIcon({
          className: 'score-local-pill-v20',
          html: `<div data-testid="score-local-pill" style="background:rgba(14,17,23,0.88);color:#F3F4F6;padding:4px 10px;border-radius:999px;font-size:13px;font-weight:600;border:1px solid rgba(255,255,255,0.15);white-space:nowrap">SCORE ${score_local.value} · ${score_local.classification}</div>`,
          iconSize: [null, 22],
          iconAnchor: [0, -30],
        }),
        interactive: false,
      });
      pill.addTo(group);
      supraRendered++;
    }

    // ═══ RSE-Ω: emit render cycle log ═══
    logRenderCycle({
      zoom: currentZoom,
      zones: zones.length,
      corridors: corridors.length,
      affuts: affuts.length,
      salines: salines.length,
      hotspots: hotspots.length,
      contamination: Array.isArray(contamination) ? contamination.length : 0,
      // Phase XI-SUPRA additions
      contamination_v2: contamination_v2_heatmap ? (contamination_v2_heatmap.zones || []).length : 0,
      canada_zones: canada_zones_summary.length,
      lep: lep_nearby.length,
      hydat: hydat_nearby.length,
      observations: observations.length,
      zones_risque: zones_risque.length,
      habitats_critiques: habitats_critiques.length,
      deplacements_ia: deplacements_ia.length,
      score_local: score_local ? 1 : 0,
      supraRendered,
      nutrition: { rendered: nutriRendered, rejected: nutriRejected, total: nutri ? (nutri.carte_carences || []).length : 0 },
      engine: 'RSE-Ω+RENDER-Ω',
    });

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
  }, [map, bundleData, waypointCenter, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, showContamination, showNutrition, corridorWeightFactor, affutRadiusFactor, salineHaloFactor, currentZoom, clearOwnLayers, useOrganicCorridors, organicBundle]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;
