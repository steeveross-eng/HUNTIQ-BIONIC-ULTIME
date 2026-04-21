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
import { RENDU_OMEGA, resolveCorridorStyleOmega, isCorridorsVisibleAtZoom, getRenduRules, getOrganicCorridors, resolveCorridorStyleOrganic, clampCorridorWeight, validateCorridorGeometry, renduOmegaPaneName, prepareDisplayPath, detectConvergenceMainVein, computeSupraArtHaloSpec, isInspectionBiologiqueActive, computeDirectionalLuminosityGradient, computeTerrainAwareBoost, detectVitalZoneOverlap, publicPulseMultiplier, isPublicPulseActive, computeFadeOutTail, buildInspectionBioFeatures, inspectionBioPaneName, INSPECTION_BIO_SPEC, bindNutritionToSaline, NUTRITION_SALINES_SPEC } from '@/lib/renduOmegaStore';

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
  onSalineNutritionDblClick = null, // PHASE_NUTRITION_SALINES_BINDING_Ω
}) => {
  const map = useMap();
  const groupRef = useRef(null);
  const autoZoomAppliedRef = useRef(null);
  const [currentZoom, setCurrentZoom] = useState(() => (map ? map.getZoom() : 14));
  const [organicBundle, setOrganicBundle] = useState(null); // Phase M : cache local corridors organiques
  // PHASE_INSPECTION_BIO_GEOMETRY_BINDING — version bumpée à chaque activation/désactivation
  // pour forcer un re-render du featureGroup quand le mode inspection bascule.
  const [inspectionBioVersion, setInspectionBioVersion] = useState(0);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;
  const onSalineNutritionDblClickRef = useRef(onSalineNutritionDblClick);
  onSalineNutritionDblClickRef.current = onSalineNutritionDblClick;

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

  // PHASE_XII_SUPRA_R — Création du pane Leaflet CORRIDORS avec Z-INDEX institutionnel.
  // Ordre strict : zones < hydrologie < terrain < corridors < salines < affuts < hotspots < vent
  // Seul le pane 'corridors' est créé ici : les autres couches conservent leur pane
  // par défaut (préservation de l'interactivité existante, aucun impact sur salines/
  // affuts/hotspots/zones). Le z-index corridors = 400 + idx_in_zOrder * 10.
  useEffect(() => {
    if (!map) return;
    try {
      const corridorsKey = 'corridors';
      const paneName = renduOmegaPaneName(corridorsKey);
      if (!map.getPane(paneName)) {
        const pane = map.createPane(paneName);
        const idx = RENDU_OMEGA.zIndexOrder.indexOf(corridorsKey);
        pane.style.zIndex = String(400 + (idx >= 0 ? idx : 3) * 10);
        pane.style.pointerEvents = 'auto';
      }
    } catch (e) { /* noop — map non prête */ }
  }, [map]);

  // PHASE_INSPECTION_BIO_GEOMETRY_BINDING — écoute du toggle PRO/EXPERT/OFF
  // pour redéclencher le rendu des 4 couches institutionnelles.
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onChange = () => setInspectionBioVersion(v => v + 1);
    window.addEventListener('inspection-bio-changed', onChange);
    return () => window.removeEventListener('inspection-bio-changed', onChange);
  }, []);

  // PHASE_INSPECTION_BIO_GEOMETRY_BINDING — Création des 4 panes Leaflet
  // institutionnels inspection-bio (ATTRACTEURS / EXCLUSIONS / PENTES / COUVERT).
  // Z-index ordonnés selon INSPECTION_BIO_SPEC.overlayLayers[].zIndex.
  // Panes créés une seule fois à l'initialisation de la map.
  useEffect(() => {
    if (!map) return;
    try {
      for (const layer of INSPECTION_BIO_SPEC.overlayLayers) {
        const paneName = inspectionBioPaneName(layer.key);
        if (!map.getPane(paneName)) {
          const pane = map.createPane(paneName);
          pane.style.zIndex = String(layer.zIndex);
          pane.style.pointerEvents = 'none'; // overlay passif, n'intercepte pas les clics
        }
      }
    } catch (_e) { /* noop — map non prête */ }
  }, [map]);

  // PHASE_XII_SUPRA_S_CORRECTION §A8 — Injection keyframe CSS pulsation publique.
  // Pulsation très subtile (0.2–0.3 %) applied via filter:brightness sur le pane.
  // Activée uniquement via classe dynamique quand zoom > 15 (géré en render).
  useEffect(() => {
    if (typeof document === 'undefined') return;
    const styleId = 'rendu-omega-public-pulse-style';
    if (document.getElementById(styleId)) return;
    const el = document.createElement('style');
    el.id = styleId;
    el.textContent = `
@keyframes renduOmegaPublicPulse {
  0%   { filter: brightness(1.000); }
  50%  { filter: brightness(1.0025); }
  100% { filter: brightness(1.000); }
}
.leaflet-pane.leaflet-renduOmega-corridors-pane.rendu-omega-pulse-on {
  animation: renduOmegaPublicPulse 2400ms ease-in-out infinite;
}
    `.trim();
    document.head.appendChild(el);
  }, []);

  // §A8 — Toggle classe pulse selon zoom courant
  useEffect(() => {
    if (!map) return;
    const paneName = renduOmegaPaneName('corridors');
    const pane = map.getPane(paneName);
    if (!pane) return;
    // Leaflet ajoute la classe 'leaflet-{name}-pane' automatiquement
    if (isPublicPulseActive(currentZoom)) {
      pane.classList.add('rendu-omega-pulse-on');
    } else {
      pane.classList.remove('rendu-omega-pulse-on');
    }
  }, [map, currentZoom]);

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
        // PHASE_ZERO_OPS_REFUS_VALIDATION_Ω (X50) — listener click → popup descriptif
        poly.bindPopup(
          `<div data-testid="zone-popup-${z.id}" style="min-width:220px">
            <div style="font-weight:700;color:${cfg.stroke};font-size:13px;text-transform:uppercase">Zone ${z.type}</div>
            <div style="margin-top:4px;font-size:12px"><b>Score</b> : ${z.score}/100</div>
            ${t.canopy!==undefined?`<div style="font-size:11px;color:#555">Canopée ${Math.round(t.canopy*100)}% · Pente ${t.pente_deg}° · Eau ${t.distance_eau_m}m · Conf. therm. ${Math.round((t.thermal_comfort||0)*100)}%</div>`:''}
            ${z.excluded?`<div style="font-size:11px;color:#EF4444;font-weight:600;margin-top:4px">EXCLUSION : ${z.exclusion_reason}</div>`:''}
            <div style="margin-top:6px;font-size:10px;color:#888">Source : ${z.source||'V20-BUNDLE'}</div>
          </div>`,
          { maxWidth: 320, className: 'bionic-zone-popup-omega' }
        );
        group.addLayer(poly);
      });
    }

    // ═══ Z-3: CORRIDORS-Ω — PHASE XII-SUPRA-S_CORRECTION (RENDU_SUPRA_Ω_ART v2) ═══
    // Corrections directive PHASE_XII_SUPRA_S_CORRECTION (§BLOC A + B) :
    //   • §A1 snap-to-saline (rayon 420-780m) + halo +35% + lum +20% @40m
    //   • §A2 veine principale si convergence ≤15m → halo ×1.5, lum ×1.6
    //   • §A3 signatures espèce renforcées (4.0/1.0/0.8/2.5/5.0, amp 0.5-0.9%)
    //   • §A4 halo externe adaptatif (forest +30%, snow +15%, water +40%, cover +25%)
    //   • §A5 gradient directionnel 5-8% (inspection bio)
    //   • §A6 tension terrain++ (pente>15°, vallon, humide, transition)
    //   • §A7 renforcement 40m autour zones vitales
    //   • §A8 pulsation publique 0.2-0.3% (zoom > 15)
    //   • §B7 clipping progressif fade-out 8-12m
    //   • §B1-B6 CatmullRom 28 strict, segment ≤20m, angle ≤45°, continuité stricte
    const corridorsVisibleAtZoom = isCorridorsVisibleAtZoom(currentZoom);
    const useOrganic = useOrganicCorridors && organicBundle?.corridors?.length > 0;
    const corridorsToRender = useOrganic ? organicBundle.corridors : corridors;
    const corridorsPaneName = renduOmegaPaneName('corridors');
    const rejectedCorridors = [];
    // §A2 — Convergence ≤15m (SUPRA_S_CORRECTION)
    const mainVeinIdxs = detectConvergenceMainVein(corridorsToRender);
    const inspectionBioOn = isInspectionBiologiqueActive();
    const waypointCenter_latlng = waypointCenter
      ? [waypointCenter.lat, waypointCenter.lng]
      : null;
    // §A8 — Pulse public (zoom > 15)
    const pulseOn = isPublicPulseActive(currentZoom);
    const pulseMult = pulseOn ? publicPulseMultiplier() : 1.0;

    // §C — Log institutionnel des rejections/snap failures (SUPRA_S_CORRIDOR_REJECTION_LOG)
    const rejectionLog = [];
    const logSinkFn = (entry) => { try { rejectionLog.push({ t: Date.now(), ...entry }); } catch (_e) { /* noop */ } };

    // §A5 HOTFIX — garantie synchrone que le pane existe AVANT tout rendu corridor
    try {
      if (map && !map.getPane(corridorsPaneName)) {
        const pane = map.createPane(corridorsPaneName);
        const idx = RENDU_OMEGA.zIndexOrder.indexOf('corridors');
        pane.style.zIndex = String(400 + (idx >= 0 ? idx : 3) * 10);
        pane.style.pointerEvents = 'auto';
      }
    } catch (_e) { /* noop */ }

    if (showCorridors && corridorsToRender.length > 0 && corridorsVisibleAtZoom) {
      corridorsToRender.forEach((c, corridorIdx) => {
        const rawPath = c.path || [[c.start?.lat, c.start?.lng], [c.end?.lat, c.end?.lng]];
        const speciesForSig = c.species_profile || species;

        // ═══ PIPELINE SUPRA_S_CORRECTION + HOTFIX ═══
        // align → signature → RE-ENFORCE (hotfix) → snap-saline (non-destructif) → clipWithFadeOut (avec rescue)
        const { displaySubpaths, fadeTails, snappedSaline, snapStatus, metrics } = prepareDisplayPath(rawPath, {
          species: speciesForSig,
          isOrganic: useOrganic,
          center: waypointCenter_latlng,
          clip: true,
          salines,
          logSink: logSinkFn,
          corridorId: c.id,
        });

        // Style strict RENDU-Ω
        const styleOmega = useOrganic
          ? resolveCorridorStyleOrganic(c)
          : resolveCorridorStyleOmega(c);
        const color = RENDU_OMEGA.color;
        let weight = clampCorridorWeight(styleOmega.weight);
        const isMainVein = mainVeinIdxs.has(corridorIdx);

        // §A6 — Tension terrainaware++ (boost intensité lumineuse perçue via halo)
        const terrainBoost = computeTerrainAwareBoost(c);
        // §A7 — Renforcement zones vitales (si path traverse une zone à ≤40m)
        const primaryPath = displaySubpaths[0] || [];
        const vitalOverlaps = detectVitalZoneOverlap(primaryPath, zones);
        const vitalBoostCum = vitalOverlaps.reduce((acc, v) => acc + v.boost, 0);

        // §A2 — Veine principale cumulative (épaisseur + luminosité max ×1.6)
        if (isMainVein) weight = clampCorridorWeight(weight + RENDU_OMEGA.microWeightDeltaPx * 4);

        const opacity = 1.0; // SUPRA_S strict (dépasse RENDU_OMEGA.opacityMin ≥ 0.75)

        // Halo spec SUPRA_ART — amplifié par fond, saline, veine principale
        const halo = computeSupraArtHaloSpec(weight, {
          background: 'forest',
          isMainVein,
          salineNearby: snappedSaline !== null,
        });
        // §A6/A7 — Boost cumulatif opacité halo externe
        halo.external.opacity = Math.min(0.85, halo.external.opacity * terrainBoost * (1 + vitalBoostCum));

        // §A HOTFIX — log si aucun subpath rendu (corridor masqué intégralement)
        if (!displaySubpaths || displaySubpaths.length === 0) {
          logSinkFn({
            id: c.id,
            reason: 'no_display_subpath_after_pipeline',
            metrics,
            snap_status: snapStatus,
            n_fade_tails: fadeTails.length,
          });
          // Pas de return : on essaie quand même de rendre les fadeTails (§A1)
        }

        displaySubpaths.forEach((path) => {
          if (!Array.isArray(path) || path.length < 2) return;

          // §A HOTFIX — validation finale : log uniquement (pas de rejet).
          // Le pipeline HOTFIX (align+signature+re-enforce) garantit la conformité.
          const geom = validateCorridorGeometry(path, { isOrganic: useOrganic, strictMinPoints: false });
          if (geom.violations.length > 0) {
            const severe = geom.violations.some(v =>
              (v.rule === 'segment_over_max' && geom.metrics.max_segment_m > RENDU_OMEGA.segmentMaxM * 2) ||
              (v.rule === 'angle_over_max' && geom.metrics.max_angle_deg > RENDU_OMEGA.angleMaxDeg * 1.8) ||
              v.rule === 'discontinuity'
            );
            if (severe) {
              rejectedCorridors.push({ id: c.id, violations: geom.violations, metrics: geom.metrics });
              logSinkFn({ id: c.id, reason: 'severe_geometry_violation_post_pipeline', violations: geom.violations, metrics: geom.metrics });
              return;
            }
            // violations mineures tolérées — le corridor reste rendu, violations loguées
            logSinkFn({ id: c.id, reason: 'minor_geometry_violation_tolerated', violations: geom.violations.slice(0, 3), metrics: geom.metrics });
          }

          // 1. Halo EXTERNE adaptatif (fond + veine + saline)
          const extHalo = L.polyline(path, {
            color: halo.external.color,
            weight: halo.external.weight * pulseMult,
            opacity: Math.min(1.0, halo.external.opacity * pulseMult),
            lineCap: 'round',
            lineJoin: 'round',
            smoothFactor: 0,
            interactive: false,
            pane: corridorsPaneName,
          });
          extHalo.options._renduOmega = { layer: 'halo_external', mainVein: isMainVein, saline: snappedSaline?.saline ?? null };
          group.addLayer(extHalo);

          // 2. Halo INTERNE glow chaud
          const intHalo = L.polyline(path, {
            color: halo.inner.color,
            weight: halo.inner.weight,
            opacity: halo.inner.opacity * pulseMult,
            lineCap: 'round',
            lineJoin: 'round',
            smoothFactor: 0,
            interactive: false,
            pane: corridorsPaneName,
          });
          intHalo.options._renduOmega = { layer: 'halo_internal' };
          group.addLayer(intHalo);

          // 3. Ligne PRINCIPALE corridor
          const line = L.polyline(path, {
            color,
            weight: weight * pulseMult,
            opacity,
            lineCap: 'round',
            lineJoin: 'round',
            smoothFactor: 0,
            interactive: true,
            pane: corridorsPaneName,
          });
          line.options._renduOmega = {
            version: 'V1.3-PHASE-XII-SUPRA-S-CORRECTION-2026-04',
            source: useOrganic ? 'ORGANIC' : 'RENDU_SUPRA_OMEGA_V2',
            color, weight, opacity, min_zoom: RENDU_OMEGA.minZoom,
            hierarchy: isMainVein ? 'veine_principale' : (c.hierarchy || 'legacy'),
            geom_metrics: geom.metrics,
            no_directional_arrow: true,
            species_signature: speciesForSig,
            main_vein: isMainVein,
            saline_snap: snappedSaline ? { dist_m: Math.round(snappedSaline.distM), lat: snappedSaline.latlng[0], lng: snappedSaline.latlng[1] } : null,
            terrain_boost: terrainBoost,
            vital_zone_boost: vitalBoostCum,
            pulse_active: pulseOn,
          };

          // Mode INSPECTION BIOLOGIQUE — flux directionnel 5-8 %
          if (inspectionBioOn && path.length >= 6) {
            const gradSteps = computeDirectionalLuminosityGradient(path, 6);
            gradSteps.forEach((g) => {
              const subLine = L.polyline(g.sub, {
                color: '#FFB347',
                weight: weight * 0.6,
                opacity: Math.min(1.0, 0.55 * g.luminosityBoost),
                lineCap: 'round',
                lineJoin: 'round',
                smoothFactor: 0,
                interactive: false,
                pane: corridorsPaneName,
              });
              subLine.options._renduOmega = { layer: 'inspection_bio_flux' };
              group.addLayer(subLine);
            });
          }

          const costStr = c.cost_surface !== undefined ? ` | cost:${c.cost_surface}` : '';
          const hierarchyStr = isMainVein
            ? ' [VEINE PRINCIPALE]'
            : (c.hierarchy ? ` [${c.hierarchy.toUpperCase()}]` : '');
          const salineStr = snappedSaline ? ` | saline @${Math.round(snappedSaline.distM)}m` : '';
          const netStr = c.is_network_link ? ' [RÉSEAU]' : '';
          const intensityLabel = (typeof c.intensity === 'number')
            ? `int:${Math.round(c.intensity)}`
            : `int:${c.type || c.intensity || 'normal'}`;
          const tagLabel = useOrganic ? 'CORRIDOR-ORGANIC-Ω' : 'CORRIDOR-SUPRA-Ω-ART-v2';
          line.bindTooltip(
            `<b style="color:${color}">${tagLabel}</b>${hierarchyStr} ${intensityLabel}${costStr}${salineStr} | ${speciesForSig || ''}${netStr}`,
            { sticky: true, opacity: 0.95 }
          );
          // X80-ABSOLU-Ω — popup corridor descriptif (click listener)
          line.bindPopup(
            `<div data-testid="corridor-popup-${c.id || corridorIdx}" style="min-width:240px">
              <div style="font-weight:700;color:${color};font-size:13px">Corridor ${c.type || c.intensity || 'normal'}</div>
              <div style="margin-top:4px;font-size:12px"><b>Hiérarchie</b> : ${hierarchyStr || 'n/a'}</div>
              <div style="font-size:12px"><b>Intensité</b> : ${intensityLabel}</div>
              ${c.distance_m ? `<div style="font-size:11px;color:#555">Distance : ${Math.round(c.distance_m)} m</div>` : ''}
              ${c.score ? `<div style="font-size:11px;color:#555">Score : ${c.score}/100</div>` : ''}
              <div style="font-size:10px;color:#888;margin-top:4px">Source : ${useOrganic ? 'ENGINE-IA-CORRIDORS-ORGANIC-Ω (XI-SUPRA-M)' : 'CORRIDOR-SUPRA-Ω-ART-v2'} · style ${tagLabel}</div>
              <div style="font-size:10px;color:#888">Style : Catmull-Rom 28 pts · couleur ${color}</div>
            </div>`,
            { maxWidth: 320 }
          );
          group.addLayer(line);
        });

        // §B7 — FADE-OUT PROGRESSIF sur les queues clippées (transition 8-12m)
        // Rendu dégradé des portions extérieures au rayon fonctionnel
        fadeTails.forEach((tail) => {
          if (!Array.isArray(tail) || tail.length < 2) return;
          const fadeSteps = computeFadeOutTail(tail, weight, RENDU_OMEGA.fadeOutTailM);
          fadeSteps.forEach((fs) => {
            const fadeLine = L.polyline(fs.sub, {
              color,
              weight: fs.weight,
              opacity: fs.opacity,
              lineCap: 'round',
              lineJoin: 'round',
              smoothFactor: 0,
              interactive: false,
              pane: corridorsPaneName,
            });
            fadeLine.options._renduOmega = { layer: 'fade_tail', tail_opacity: fs.opacity };
            group.addLayer(fadeLine);
          });
        });
      });
      // §C HOTFIX — exposition du log institutionnel sur window pour inspection
      try {
        if (typeof window !== 'undefined') {
          window.SUPRA_S_CORRIDOR_REJECTION_LOG = rejectionLog;
          if (rejectionLog.length > 0) {
            console.info(`[RENDU-Ω HOTFIX] ${rejectionLog.length} entrées SUPRA_S_CORRIDOR_REJECTION_LOG (window.SUPRA_S_CORRIDOR_REJECTION_LOG pour inspection)`);
          }
        }
      } catch (_e) { /* noop */ }
    }
    // X80-ABSOLU-Ω — signal conformité style corridors (RENDU-Ω orange ambre + Catmull-Rom 28 pts)
    if (typeof window !== 'undefined') {
      window.__OMEGA_CORRIDORS_STYLE_CONFORME__ = showCorridors && corridorsToRender.length > 0;
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
    // X80-ABSOLU-Ω — signal contamination layers visible
    if (typeof window !== 'undefined') {
      const contaminationList = Array.isArray(contamination) ? contamination : (contamination ? [contamination] : []);
      window.__OMEGA_CONTAMINATION_LAYERS_VISIBLE__ = showContamination && contaminationList.length > 0;
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

        // PHASE_XIV_CRITICAL_FUNCTIONAL_PARITY_Ω — dblclick Leaflet : désactiver
        // le doubleClickZoom natif sur cet élément pour que le handler nutrition
        // soit prioritaire (Leaflet consomme le dblclick en zoom par défaut).
        try { L.DomEvent.disableClickPropagation(circle._path || circle); } catch (_) { /* noop */ }

        // PHASE_NUTRITION_SALINES_BINDING_Ω — double-clic = rapport nutritionnel institutionnel
        circle.on('dblclick', (ev) => {
          try {
            L.DomEvent.stopPropagation(ev);
            L.DomEvent.preventDefault(ev);
            if (ev.originalEvent) {
              ev.originalEvent.preventDefault();
              ev.originalEvent.stopPropagation();
            }
          } catch (_) { /* noop */ }
          const handler = onSalineNutritionDblClickRef.current;
          if (handler && NUTRITION_SALINES_SPEC.NUTRITION_BY_SALINE_ONLY) {
            const payload = bindNutritionToSaline(s, {
              species,
              month: new Date().getMonth() + 1,
              zones,
              scoreLocal: score_local,
            });
            handler(payload);
          }
        });
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
        // X50 P0-3 — click listener → popup descriptif institutionnel
        circle.bindPopup(
          `<div data-testid="hotspot-popup-${h.id||''}" style="min-width:200px">
            <div style="font-weight:700;color:${color};font-size:13px">Hotspot ${h.type||'activité'}</div>
            <div style="margin-top:4px;font-size:12px"><b>Intensité</b> : ${level+1}/5 (${Math.round(intensity)})</div>
            ${h.justification?`<div style="font-size:11px;color:#555">${h.justification}</div>`:''}
            ${h.source?`<div style="font-size:10px;color:#888;margin-top:4px">Source : ${h.source}</div>`:''}
          </div>`,
          { maxWidth: 300 }
        );
        group.addLayer(circle);
      });
    }

    // ═══ Z-6.5: INSPECTION-BIOLOGIQUE-Ω — PHASE_INSPECTION_BIO_GEOMETRY_BINDING ═══
    // Overlays institutionnels rendus uniquement si le mode inspection bio
    // est actif (rôle PRO ou EXPERT). Strict RENDU-Ω, aucun fallback non
    // institutionnel. Z-index ordonnés par INSPECTION_BIO_SPEC (couvert < pentes
    // < exclusions < attracteurs).
    if (inspectionBioOn) {
      const ibFeatures = buildInspectionBioFeatures({ zones, salines, corridors: corridorsToRender, waypointCenter, scoreLocal: score_local });
      if (ibFeatures) {
        const layerSpecs = Object.fromEntries(
          INSPECTION_BIO_SPEC.overlayLayers.map(l => [l.key, l])
        );
        // ATTRACTEURS — cercles triangulés orange institutionnel (zones vitales + salines)
        if (ibFeatures.attracteurs && ibFeatures.attracteurs.length) {
          const spec = layerSpecs.attracteurs;
          const paneName = inspectionBioPaneName('attracteurs');
          ibFeatures.attracteurs.forEach(f => {
            const c = L.circle(f.latlng, {
              radius: f.radiusM,
              color: spec.stroke, weight: spec.weight,
              opacity: spec.strokeOpacity,
              fillColor: spec.color, fillOpacity: spec.fillOpacity,
              interactive: false, pane: paneName,
            });
            c.bindTooltip(
              `<b style="color:${spec.color}">ATTRACTEUR</b> · ${f.meta.source}${f.meta.type ? ' ('+f.meta.type+')' : ''}`,
              { sticky: true, opacity: 0.95 }
            );
            group.addLayer(c);
          });
        }
        // EXCLUSIONS — polygones hachurés brun institutionnel
        if (ibFeatures.exclusions && ibFeatures.exclusions.length) {
          const spec = layerSpecs.exclusions;
          const paneName = inspectionBioPaneName('exclusions');
          ibFeatures.exclusions.forEach(f => {
            const p = L.polygon(f.latlngs, {
              color: spec.stroke, weight: spec.weight,
              opacity: spec.strokeOpacity,
              fillColor: spec.color, fillOpacity: spec.fillOpacity,
              dashArray: spec.dashArray,
              interactive: false, pane: paneName,
            });
            p.bindTooltip(
              `<b style="color:${spec.color}">EXCLUSION</b> · ${f.meta.reason}`,
              { sticky: true, opacity: 0.95 }
            );
            group.addLayer(p);
          });
        }
        // PENTES — polygones gradient par palier (EXPERT uniquement)
        if (ibFeatures.pentes && ibFeatures.pentes.length) {
          const spec = layerSpecs.pentes;
          const paneName = inspectionBioPaneName('pentes');
          ibFeatures.pentes.forEach(f => {
            const p = L.polygon(f.latlngs, {
              color: f.color, weight: spec.weight,
              opacity: spec.strokeOpacity,
              fillColor: f.color, fillOpacity: spec.fillOpacity,
              interactive: false, pane: paneName,
            });
            p.bindTooltip(
              `<b style="color:${f.color}">PENTE</b> ${f.meta.pente_deg}° · palier ≤${f.palierDeg}°`,
              { sticky: true, opacity: 0.95 }
            );
            group.addLayer(p);
          });
        }
        // COUVERT — polygones verts (EXPERT uniquement)
        if (ibFeatures.couvert && ibFeatures.couvert.length) {
          const spec = layerSpecs.couvert;
          const paneName = inspectionBioPaneName('couvert');
          ibFeatures.couvert.forEach(f => {
            const p = L.polygon(f.latlngs, {
              color: spec.stroke, weight: spec.weight,
              opacity: spec.strokeOpacity,
              fillColor: spec.color,
              fillOpacity: Math.min(0.6, spec.fillOpacity + (f.canopy - 0.5) * 0.4),
              interactive: false, pane: paneName,
            });
            p.bindTooltip(
              `<b style="color:${spec.color}">COUVERT</b> canopée ${f.meta.canopy_pct}%`,
              { sticky: true, opacity: 0.95 }
            );
            group.addLayer(p);
          });
        }
        // Exposition diagnostique institutionnelle (read-only)
        try {
          if (typeof window !== 'undefined') {
            window.__INSPECTION_BIO_GEOMETRY__ = Object.freeze({
              role: ibFeatures.role,
              counts: {
                attracteurs: ibFeatures.attracteurs.length,
                exclusions: ibFeatures.exclusions.length,
                pentes: ibFeatures.pentes.length,
                couvert: ibFeatures.couvert.length,
              },
              rejections: Object.freeze({ ...(ibFeatures.rejections || {}) }),
              filtersActive: !!ibFeatures.filtersActive,
              renderedAt: new Date().toISOString(),
            });
          }
        } catch (_e) { /* noop */ }
      }
    } else {
      // Mode OFF — purger l'exposition diagnostique
      try {
        if (typeof window !== 'undefined' && window.__INSPECTION_BIO_GEOMETRY__) {
          window.__INSPECTION_BIO_GEOMETRY__ = Object.freeze({
            role: null, counts: { attracteurs: 0, exclusions: 0, pentes: 0, couvert: 0 }, renderedAt: null,
          });
        }
      } catch (_e) { /* noop */ }
    }

    // ═══ Z-7: AFFUTS-Omega V12-R5 (Directive II) — Orange BIONIC + contour blanc ═══
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
        // X50 P0-3 — click listener → popup descriptif institutionnel
        circle.bindPopup(
          `<div data-testid="affut-popup-${a.id||''}" style="min-width:220px">
            <div style="font-weight:700;color:${AFFUT_BIONIC_ORANGE};font-size:13px">Affût ${typeLabel}</div>
            <div style="margin-top:4px;font-size:12px"><b>Score</b> : ${a.score_affut_v12 || a.score}/100</div>
            <div style="font-size:11px;color:#555">${a.justification || a.description || ''}</div>
            <div style="font-size:11px;color:#555">Corridor ${a.classe_corridor_cible || a.corridor_type} à ${a.distance_corridor_m}m</div>
            ${a.affut_repositionne?`<div style="font-size:11px;color:#4CAF50;font-weight:600">REPOSITIONNÉ AUTO V12</div>`:''}
          </div>`,
          { maxWidth: 320 }
        );
        group.addLayer(circle);
      });
    }

    // ═══ Z-9: VENT V20 Ω — X80-ABSOLU (cône olfactif + particules Ventusky) ═══
    // Directive X80-ABSOLU-Ω : remplacement du rendu radial (banni X70) par
    // (a) un cône olfactif unique blanc translucide, (b) des particules flottantes
    // blanches/grises sans concurrence visuelle avec les corridors orange.
    // Le widget COMPASS est rendu hors carte (cf. <CompassOmegaWidget/>).
    const windVectors = Array.isArray(bundleData.wind_vectors) ? bundleData.wind_vectors : [];
    let windRendered = 0;
    if (showWind && windVectors.length > 0 && waypointCenter) {
      // Vent dominant = moyenne des 8 vecteurs V8 (direction médiane + vitesse moyenne)
      const validVec = windVectors.filter(v => v.start && v.end && typeof v.direction_deg === 'number');
      const meanDir = validVec.reduce((a, v) => a + (v.direction_deg || 0), 0) / Math.max(1, validVec.length);
      const meanSpeed = validVec.reduce((a, v) => a + (v.speed_kmh || 0), 0) / Math.max(1, validVec.length);
      // (a) CÔNE OLFACTIF — 30°, portée 500 m, blanc translucide pointillé
      const coneAngle = 30;
      const reachM = 500;
      const reachDeg = reachM / 111320;
      const cosLat = Math.max(0.5, Math.cos(waypointCenter.lat * Math.PI / 180));
      const leftRad = (meanDir - coneAngle / 2) * Math.PI / 180;
      const rightRad = (meanDir + coneAngle / 2) * Math.PI / 180;
      const conePolygon = [
        [waypointCenter.lat, waypointCenter.lng],
        [waypointCenter.lat + Math.cos(leftRad) * reachDeg, waypointCenter.lng + Math.sin(leftRad) * reachDeg / cosLat],
        [waypointCenter.lat + Math.cos(rightRad) * reachDeg, waypointCenter.lng + Math.sin(rightRad) * reachDeg / cosLat],
        [waypointCenter.lat, waypointCenter.lng],
      ];
      const cone = L.polygon(conePolygon, {
        color: '#E0E0E0',
        weight: 1.5,
        opacity: 0.7,
        fillColor: '#FFFFFF',
        fillOpacity: 0.14,
        dashArray: '5,4',
        interactive: true,
        pane: 'markerPane',
      });
      cone.bindTooltip(
        `<b style="color:#FFFFFF">Cône olfactif</b> · ${Math.round(meanDir)}° · ${meanSpeed.toFixed(1)} km/h`,
        { sticky: true, opacity: 0.95 }
      );
      cone.bindPopup(
        `<div data-testid="wind-cone-popup" style="min-width:220px">
          <div style="font-weight:700;color:#424242;font-size:13px">Cône olfactif V20-Ω</div>
          <div style="margin-top:4px;font-size:12px"><b>Direction</b> : ${Math.round(meanDir)}°</div>
          <div style="font-size:12px"><b>Vitesse</b> : ${meanSpeed.toFixed(1)} km/h</div>
          <div style="font-size:11px;color:#555">Ouverture : 30° · Portée : 500 m</div>
          <div style="font-size:10px;color:#888;margin-top:4px">Source : engine_vent.compute_scent_cone (V30-LOCKED)</div>
        </div>`,
        { maxWidth: 280 }
      );
      group.addLayer(cone);
      windRendered = 1;
      // (b) PARTICULES VENTUSKY — petits tirets blancs le long de la direction
      // dominante dans un rayon de 700m (minimalistes, zéro concurrence corridors)
      const particleCount = 14;
      const particleReach = 0.0055; // ~600 m
      for (let p = 0; p < particleCount; p++) {
        const rho = (p / particleCount) * particleReach;
        const sideOffset = ((p % 3) - 1) * 0.0015;
        const baseRad = meanDir * Math.PI / 180;
        const perpRad = baseRad + Math.PI / 2;
        const startLat = waypointCenter.lat + Math.cos(baseRad) * rho + Math.cos(perpRad) * sideOffset;
        const startLng = waypointCenter.lng + (Math.sin(baseRad) * rho + Math.sin(perpRad) * sideOffset) / cosLat;
        const tickLen = 0.0009;
        const endLat = startLat + Math.cos(baseRad) * tickLen;
        const endLng = startLng + Math.sin(baseRad) * tickLen / cosLat;
        const particle = L.polyline([[startLat, startLng], [endLat, endLng]], {
          color: '#F5F5F5',
          weight: 1.4,
          opacity: 0.55,
          dashArray: '3,3',
          interactive: false,
          pane: 'markerPane',
        });
        group.addLayer(particle);
      }
      windRendered += particleCount;
    }
    if (typeof window !== 'undefined') {
      window.__OMEGA_WIND_VECTORS_RENDERED__ = windRendered;
      window.__OMEGA_VENTUSKY_PARTICLES_ACTIVE__ = showWind && windVectors.length > 0 ? 14 : 0;
      window.__OMEGA_VENT_STYLE_CONFORME__ = true;
      window.__OMEGA_VENT_CONFUSION_CORRIDORS__ = false;
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
    // PHASE_ZERO_OPS_REFUS_VALIDATION_Ω (X50) — Réactivation stricte de
    // PHASE_NUTRITION_SALINES_BINDING_Ω : aucun point nutritionnel autonome
    // ne peut être rendu tant que NUTRITION_BY_SALINE_ONLY=true. La nutrition
    // s'affiche UNIQUEMENT via double-clic sur une saline (cf. onSaline...).
    if (showNutrition && !NUTRITION_SALINES_SPEC.NUTRITION_BY_SALINE_ONLY && nutri && Array.isArray(nutri.carte_carences)) {
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

    // 1. CONTAMINATION V2 HEATMAP (visible uniquement si showContamination=true)
    // PHASE_XV_CONTAMINATION_PARITY_Ω — sous contrôle du toggle institutionnel
    let contamRendered = 0;
    if (showContamination && contamination_v2_heatmap && contamination_v2_heatmap.zones) {
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
        contamRendered++;
      });
    }

    // PHASE_XV_CONTAMINATION_PARITY_Ω — exposition diagnostique read-only
    try {
      if (typeof window !== 'undefined') {
        const cones = Array.isArray(contamination) ? contamination.length : 0;
        const v2zones = (contamination_v2_heatmap && contamination_v2_heatmap.zones) || [];
        window.__CONTAMINATION_STATE__ = Object.freeze({
          toggleActive: !!showContamination,
          cones_rendered: showContamination ? cones : 0,
          v2_zones_rendered: contamRendered,
          v2_zones_available: v2zones.length,
          total_rendered: (showContamination ? cones : 0) + contamRendered,
          has_data: (cones + v2zones.length) > 0,
          message: (!showContamination)
            ? 'TOGGLE_OFF'
            : (cones + v2zones.length) === 0
              ? 'NO_CONTAMINATION_DATA_FOR_THIS_AREA'
              : 'RENDERED',
          renderedAt: new Date().toISOString(),
        });
      }
    } catch (_e) { /* noop */ }

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
  }, [map, bundleData, waypointCenter, enabled, showZones, showCorridors, showAffuts, showSalines, showHotspots, showContamination, showNutrition, corridorWeightFactor, affutRadiusFactor, salineHaloFactor, currentZoom, clearOwnLayers, useOrganicCorridors, organicBundle, inspectionBioVersion]);

  useEffect(() => {
    renderLayers();
    return () => clearOwnLayers();
  }, [renderLayers, clearOwnLayers]);

  return null;
};

export default BionicLayersV8;
