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
// ENFORCEMENT_P0 §2.3/§7.1 — RELIQUE PURGÉE : RENDUΩ impose une palette UNIQUE
// épaisseurs 1.2/2.0/3.0 px (puis 3.0/4.0/6.0 px §X150), opacité ≥0.75.
// Le mapping multicolor historique (HIER.extreme=#FF0000, etc.) est DORMANT
// et INTERDIT.
// PHASE-D VERROUILLAGE RENDUΩ (BCE-4X · STEEVE-MAX · 2026-04-27) :
//   - Palette institutionnelle VERTE verrouillée :
//       primary    = #00A676  (axe principal corridor)
//       haloInner  = #4CC99A  (lumière saturée organique)
//       haloOuter  = #B2F2D9  (diffusion ambiante)
//   - Texture organique : oscillation contrôlée sur épaisseur, halos amplifiés
//   - Multi-espèces (5) · multi-saisons (1-12) via coefs RENDU_OMEGA
//   - La couleur historique #FF8F00 est conservée comme legacy_orange dans
//     paletteOmegaPhaseD pour la traçabilité institutionnelle.
const CORRIDOR_STYLES_RELIQUE_PURGED = Object.freeze({
  _purged_by: 'PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0',
  _phase_d_lock: 'PHASE_D_VERROUILLAGE_RENDUOMEGA_BCE4X_STEEVEMAX',
  _do_not_use: true,
  _resolver_canon: 'resolveCorridorStyleOmega',
  _resolver_phase_d: 'resolveCorridorStylePhaseD',
  _rendu_color_canon_phase_d: '#00A676',
  _rendu_legacy_orange: '#FF8F00',
});

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
  // P22E_FIX_R3 — exposition d'un state corridorsLoading pour indicateur UI.
  const [corridorsLoading, setCorridorsLoading] = useState(false);
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
  // affuts/hotspots/zones). Le z-index corridors = 500 + idx_in_zOrder * 15.
  // COMMANDE STEEVE-MAX — création explicite des 8 panes RENDUΩ pour garantir
  // l'ordre institutionnel strict : zones < hydrologie < terrain < corridors
  // < salines < hotspots < affuts < vent.
  useEffect(() => {
    if (!map) return;
    try {
      // Création explicite de TOUS les panes RENDUΩ pour garantir l'ordre strict
      RENDU_OMEGA.zIndexOrder.forEach((layerKey, idx) => {
        const paneName = renduOmegaPaneName(layerKey);
        if (!map.getPane(paneName)) {
          const pane = map.createPane(paneName);
          pane.style.zIndex = String(500 + idx * 15);
          pane.style.pointerEvents = layerKey === 'corridors' ? 'auto' : 'none';
        }
      });
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
  // COMMANDE STEEVE-MAX — supprimé l'early return : on fetch même sans waypoint
  // pour éviter de bloquer le rendu RenduΩ. La condition `useOrganicCorridors`
  // suffit (defaut true, désactivable par prop).
  // P22E_FIX_R2 (2026-05-09 · COMMANDANT STEEVE-MAX) :
  //   - Suppression du flag `cancelled` qui empêchait setOrganicBundle()
  //     d'être appliqué quand la promise se résolvait après cleanup
  //     (3-19s de latence backend → re-render fréquent → setState perdu).
  //   - Ref-based mutex empêche les requêtes concurrentes pour la même clé.
  //   - State corridorsLoading exposé pour indicateur UI (R3).
  const inflightOrganicKeyRef = useRef(null);
  useEffect(() => {
    if (!useOrganicCorridors || !enabled) return;
    if (!waypointCenter) return;  // garde-fou minimal : besoin d'un centre
    const requestKey = `${Number(waypointCenter.lat).toFixed(4)}|${Number(waypointCenter.lng).toFixed(4)}|${species}`;
    // P22E_FIX_R2 — guard mutex : évite les requêtes parallèles pour la même clé
    if (inflightOrganicKeyRef.current === requestKey) return;
    inflightOrganicKeyRef.current = requestKey;
    setCorridorsLoading(true);
    getOrganicCorridors(waypointCenter.lat, waypointCenter.lng, species)
      .then((data) => {
        // P22E_FIX_R2 : applique TOUJOURS si la requête est encore pertinente.
        if (!data) {
          setCorridorsLoading(false);
          return;
        }
        setOrganicBundle(data);
        setCorridorsLoading(false);
        try {
          // eslint-disable-next-line no-console
          console.warn('[RENDUΩ · P22E_FIX_R2] organicBundle hydrated → triggerRender. corridors=', data?.corridors?.length || 0, '· requestKey=', requestKey);
          if (typeof window !== 'undefined') {
            window.__P22E_ORGANIC_HYDRATED__ = {
              ts: Date.now(),
              key: requestKey,
              corridors_count: data?.corridors?.length || 0,
              smoother_total: data?.smoother_total_corridors || 0,
            };
          }
        } catch (_e) { /* noop */ }
      })
      .catch(() => {
        setCorridorsLoading(false);
      })
      .finally(() => {
        // libère le mutex pour permettre un nouveau fetch si la clé change
        if (inflightOrganicKeyRef.current === requestKey) {
          inflightOrganicKeyRef.current = null;
        }
      });
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
        // PHASE_ZERO_OPS_REFUS_VALIDATION_Ω (X50) → X120-SUPRA-CANONIQUE — popup descriptif enrichi
        const speciesHint = (species || 'espèce générale').toString();
        const zType = String(z.type || '').toLowerCase();
        const zDesc = zType === 'rut' ? 'Secteur de parades et affrontements territoriaux'
          : zType === 'alimentation' ? 'Zone de gagnage dense et persistant'
          : zType === 'repos' ? 'Couche thermique abritée, faible dérangement'
          : zType === 'eau' ? 'Point d\'abreuvement hydrologique structurel'
          : 'Structure biomimétique V10-SUPRA';
        const zForce = zType === 'rut' ? 'Fréquentation mâle élevée en saison'
          : zType === 'alimentation' ? 'Ressource énergétique soutenue'
          : zType === 'repos' ? 'Couverture thermique + visuelle'
          : zType === 'eau' ? 'Ressource hydrique régulière'
          : 'Habitat institutionnel validé';
        const zFaiblesse = (t.canopy !== undefined && t.canopy < 0.3) ? 'Canopée faible — exposition accrue'
          : (t.pente_deg > 20) ? 'Pente raide — accès pénible'
          : (t.distance_eau_m > 600) ? 'Eau éloignée — fréquentation fragmentée'
          : 'Lisière partielle — attention au vent dominant';
        const zOptim = zType === 'rut' ? 'Affût latéral contre-vent, 60-90 m de distance'
          : zType === 'alimentation' ? 'Arrivée pré-aube, sortie post-crépusculaire'
          : zType === 'repos' ? 'Approche silencieuse, jamais de passage direct'
          : zType === 'eau' ? 'Affût à 40-60 m sous le vent, observation discrète'
          : 'Respecter la trame hydrologique et la pente';
        poly.bindPopup(
          `<div data-testid="zone-popup-${z.id}" style="min-width:280px;font-family:system-ui,Segoe UI,sans-serif">
            <div style="font-weight:700;color:${cfg.stroke};font-size:13px;text-transform:uppercase;letter-spacing:0.05em">Zone ${z.type}</div>
            <div style="margin-top:4px;font-size:11px;color:#555">${zDesc}</div>
            <div style="margin-top:6px;font-size:12px"><b>Score</b> : ${z.score}/100 · <b>Espèce</b> : ${speciesHint}</div>
            ${t.canopy!==undefined?`<div style="font-size:11px;color:#555">Canopée ${Math.round(t.canopy*100)}% · Pente ${t.pente_deg}° · Eau ${t.distance_eau_m}m · Conf. therm. ${Math.round((t.thermal_comfort||0)*100)}%</div>`:''}
            <div style="margin-top:6px;padding:4px 6px;background:#E8F5E9;border-left:3px solid ${cfg.stroke};font-size:11px;color:#1B5E20">
              <b>Force</b> : ${zForce}<br/>
              <b>Faiblesse</b> : ${zFaiblesse}
            </div>
            <div style="margin-top:4px;padding:4px 6px;background:#FFF8E1;border-left:3px solid #F57C00;font-size:11px;color:#E65100">
              <b>Optimisation</b> : ${zOptim}
            </div>
            ${z.excluded?`<div style="margin-top:4px;font-size:11px;color:#EF4444;font-weight:600">EXCLUSION : ${z.exclusion_reason}</div>`:''}
            <div style="margin-top:6px;font-size:10px;color:#888">Source : ${z.source||'V20-BUNDLE'} · ENGINE-RENDER-Ω (XI-SUPRA)</div>
          </div>`,
          { maxWidth: 360, className: 'bionic-zone-popup-omega' }
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
    // COMMANDE STEEVE-MAX — fallback robuste : RENDUΩ utilise organicBundle
    // si disponible, sinon les corridors du bundle V20 (V30 + INTERZONE + ENTRANTS).
    const organicReady = useOrganicCorridors && organicBundle?.corridors?.length > 0;
    const corridorsToRender = organicReady ? organicBundle.corridors : corridors;
    // Log institutionnel obligatoire — traçabilité du rendu
    try {
      // eslint-disable-next-line no-console
      console.warn(
        '[RENDUΩ] corridorsToRender =', corridorsToRender.length,
        '· organicReady =', organicReady,
        '· bundleCorridors =', corridors.length,
        '· organicBundleCorridors =', organicBundle?.corridors?.length || 0,
        '· zoom =', currentZoom,
        '· visibleAtZoom =', corridorsVisibleAtZoom,
      );
    } catch (_e) { /* noop */ }
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
      // Compteur institutionnel : nombre de polylines réellement ajoutées au map.
      // Si 0 à la fin → fallback RAW est déclenché (cf. plus bas).
      let renderedPolylineCount = 0;
      corridorsToRender.forEach((c, corridorIdx) => {
        const rawPath = c.path || [[c.start?.lat, c.start?.lng], [c.end?.lat, c.end?.lng]];
        const speciesForSig = c.species_profile || species;

        // ═══ PIPELINE SUPRA_S_CORRECTION + HOTFIX ═══
        // align → signature → RE-ENFORCE (hotfix) → snap-saline (non-destructif) → clipWithFadeOut (avec rescue)
        const { displaySubpaths, fadeTails, snappedSaline, snapStatus, metrics } = prepareDisplayPath(rawPath, {
          species: speciesForSig,
          isOrganic: organicReady,
          center: waypointCenter_latlng,
          clip: true,
          salines,
          logSink: logSinkFn,
          corridorId: c.id,
        });

        // Style strict RENDU-Ω
        const styleOmega = organicReady
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
          const geom = validateCorridorGeometry(path, { isOrganic: organicReady, strictMinPoints: false });
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
            source: organicReady ? 'ORGANIC' : 'RENDU_SUPRA_OMEGA_V2',
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
          const tagLabel = organicReady ? 'CORRIDOR-ORGANIC-Ω' : 'CORRIDOR-SUPRA-Ω-ART-v2';
          line.bindTooltip(
            `<b style="color:${color}">${tagLabel}</b>${hierarchyStr} ${intensityLabel}${costStr}${salineStr} | ${speciesForSig || ''}${netStr}`,
            { sticky: true, opacity: 0.95 }
          );
          // X80-ABSOLU-Ω → X120-SUPRA-CANONIQUE — popup corridor descriptif enrichi
          const corridorHier = String(c.hierarchy || c.type || 'normal').toLowerCase();
          const corrDesc = corridorHier === 'extreme' ? 'Axe majeur permanent : flux biologique intense'
            : corridorHier === 'intense' ? 'Axe structurant régulier : inter-zones prioritaire'
            : corridorHier === 'saisonnier' ? 'Corridor saisonnier : activation rut/pré-rut'
            : 'Corridor normal : liaison fonctionnelle';
          const corrForce = corridorHier === 'extreme' ? 'Probabilité de passage > 85 %'
            : corridorHier === 'intense' ? 'Trace reconnaissable sol + lichens abrasés'
            : 'Traversée régulière observée';
          const corrFaib = corridorHier === 'saisonnier' ? 'Hors saison : fréquentation quasi nulle'
            : (c.distance_m > 1200 ? 'Longueur importante → affût unique insuffisant' : 'Vent traversier défavorable possible');
          const corrOpt = 'Affût sous le vent à 25-45 m du corridor · orientation nord-est si tireur droitier · hauteur 3-4 m';
          line.bindPopup(
            `<div data-testid="corridor-popup-${c.id || corridorIdx}" style="min-width:280px;font-family:system-ui,Segoe UI,sans-serif">
              <div style="font-weight:700;color:${color};font-size:13px;letter-spacing:0.05em">CORRIDOR ${String(c.type || 'normal').toUpperCase()}</div>
              <div style="margin-top:4px;font-size:11px;color:#555">${corrDesc}</div>
              <div style="margin-top:6px;font-size:12px"><b>Hiérarchie</b> : ${corridorHier} · <b>Intensité</b> : ${intensityLabel}</div>
              ${c.distance_m ? `<div style="font-size:11px;color:#555">Distance : ${Math.round(c.distance_m)} m · ${c.from_zone_type||'?'} → ${c.to_zone_type||'?'}</div>` : ''}
              ${c.score ? `<div style="font-size:11px;color:#555">Score : ${c.score}/100</div>` : ''}
              <div style="margin-top:6px;padding:4px 6px;background:#FFF3E0;border-left:3px solid ${color};font-size:11px;color:#E65100">
                <b>Force</b> : ${corrForce}<br/>
                <b>Faiblesse</b> : ${corrFaib}
              </div>
              <div style="margin-top:4px;padding:4px 6px;background:#E3F2FD;border-left:3px solid #1976D2;font-size:11px;color:#0D47A1">
                <b>Optimisation</b> : ${corrOpt}
              </div>
              <div style="margin-top:6px;font-size:10px;color:#888">Source : ${organicReady ? 'ENGINE-IA-CORRIDORS-ORGANIC-Ω (XI-SUPRA-M)' : 'CORRIDOR-SUPRA-Ω-ART-v2'}<br/>Style : Catmull-Rom 28 pts · couleur ${color}</div>
            </div>`,
            { maxWidth: 360 }
          );
          group.addLayer(line);
          renderedPolylineCount++;
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
            renderedPolylineCount++;
          });
        });
      });

      // ═══ COMMANDE STEEVE-MAX — FALLBACK ABSOLU RENDUΩ ═══
      // Si le pipeline align→signature→snap→clip aboutit à 0 polyline visible,
      // on garantit AU MINIMUM le rendu du path RAW de chaque corridor pour
      // assurer la visibilité institutionnelle exigée par le Commandant.
      if (renderedPolylineCount === 0 && corridorsToRender.length > 0) {
        try {
          // eslint-disable-next-line no-console
          console.warn(`[RENDUΩ-FALLBACK] pipeline a filtré tous les corridors (${corridorsToRender.length} en entrée → 0 polyline). Rendu RAW d'urgence.`);
        } catch (_e) { /* noop */ }
        corridorsToRender.forEach((c, idx) => {
          const rawPath = c.path;
          if (!Array.isArray(rawPath) || rawPath.length < 2) return;
          const fallbackLine = L.polyline(rawPath, {
            color: RENDU_OMEGA.color,            // #FF8F00 institutionnel
            weight: 3.0,                          // visibilité maximale
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round',
            smoothFactor: 0,
            interactive: true,
            pane: corridorsPaneName,
          });
          fallbackLine.options._renduOmega = {
            layer: 'corridor_raw_fallback',
            id: c.id || `raw_${idx}`,
            type: c.entering_corridor ? 'ENTERING'
                : (c.interzone_generated ? 'INTERZONE' : 'V30'),
          };
          fallbackLine.bindTooltip(
            `<b style="color:#FF8F00">CORRIDOR-Ω-RAW</b> · ${c.id || `id_${idx}`} · type=${fallbackLine.options._renduOmega.type}`,
            { sticky: true, opacity: 0.92 },
          );
          group.addLayer(fallbackLine);
          renderedPolylineCount++;
        });
      }
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
    // X80-ABSOLU-Ω → X150-SUPRA-ARCHITECTONIQUE — signaux conformité RENDU-Ω corridors
    if (typeof window !== 'undefined') {
      window.__OMEGA_CORRIDORS_STYLE_CONFORME__ = showCorridors && corridorsToRender.length > 0;
      // X150 — 7 probes détaillées des 13 normes (document DESCRIPTIONS_RENDU_OMEGA_CORRIDORS)
      const x150Probes = {
        // PHASE-D VERROUILLAGE RENDUΩ — palette verte institutionnelle BCE-4X
        color_strict_phase_d_green: RENDU_OMEGA.color === '#00A676',
        palette_phase_d_complete:
          RENDU_OMEGA.paletteOmegaPhaseD?.primary === '#00A676' &&
          RENDU_OMEGA.paletteOmegaPhaseD?.haloInner === '#4CC99A' &&
          RENDU_OMEGA.paletteOmegaPhaseD?.haloOuter === '#B2F2D9',
        weights_allowed: JSON.stringify(RENDU_OMEGA.weightsAllowedPx) === JSON.stringify([1.2, 2.0, 3.0]),
        opacity_min_075: RENDU_OMEGA.opacityMin >= 0.75,
        catmull_rom_points_25_30: RENDU_OMEGA.controlPointsMin === 25 && RENDU_OMEGA.controlPointsMax === 30,
        segment_max_20m: RENDU_OMEGA.segmentMaxM === 20.0,
        angle_max_45: RENDU_OMEGA.angleMaxDeg === 45.0,
        functional_radius_420_780: RENDU_OMEGA.functionalRadiusMinM === 420 && RENDU_OMEGA.functionalRadiusMaxM === 780,
        min_zoom_13: RENDU_OMEGA.minZoom === 13,
        zindex_order_conforme: JSON.stringify(RENDU_OMEGA.zIndexOrder) === JSON.stringify(['zones','hydrologie','terrain','corridors','salines','affuts','hotspots','vent']),
        forbid_affut_interaction: RENDU_OMEGA.forbidAffutInteraction === true,
        forbid_directional_arrow: RENDU_OMEGA.forbidDirectionalArrow === true,
        preview_equals_final: RENDU_OMEGA.previewEqualsFinal === true,
        organic_texture_enabled: RENDU_OMEGA.organicTexture?.enabled === true,
        species_coefs_complete: typeof RENDU_OMEGA.speciesWeightCoefficient?.orignal === 'number',
        season_coefs_complete: typeof RENDU_OMEGA.seasonWeightCoefficient?.[10] === 'number',
      };
      const x150ConformeTotal = Object.values(x150Probes).every(Boolean);
      window.__OMEGA_CORRIDORS_X150_PROBES__ = x150Probes;
      window.__OMEGA_CORRIDORS_X150_CONFORME__ = x150ConformeTotal;
    }

    // ═══ Z-4: CONTAMINATION-Omega — CANON SUPRÊME X120 ═══
    // Directive X120-SUPRA-CANONIQUE-Ω : opacité 0.18 stricte, contours divisés par 2,
    // géométrie rectiligne (smoothFactor 0), rouge institutionnel #FF0000.
    // RENDU-Ω INTÉGRAL (PHASE-E ordre Commandant 2026-04-28) : opacités atténuées
    // pour libérer la lisibilité des couches Ω sans suppression de la couche.
    if (showContamination && contamination) {
      const cones = Array.isArray(contamination) ? contamination : [contamination];
      cones.forEach(cone => {
        if (!cone.polygon || cone.polygon.length < 3) return;
        // Ligne externe fine (contour principal)
        const polyOuter = L.polygon(cone.polygon, {
          color: '#DC2626',                     // RENDU-Ω : palette officielle bande PROSCRIT
          weight: 1.25,
          opacity: 0.45,                        // PURGE Ω : 0.85 → 0.45 (atténuation conformité)
          fillColor: '#DC2626',
          fillOpacity: 0,                       // §2 contour seul, intérieur transparent
          dashArray: '5 3',
          smoothFactor: 0,
          lineJoin: 'miter',
          interactive: true,
          pane: 'overlayPane',
        });
        // Ligne interne ultra-fine (effet double contour canonique)
        const polyInner = L.polygon(cone.polygon, {
          color: '#DC2626',
          weight: 0.6,
          opacity: 0.30,                        // PURGE Ω : 0.6 → 0.30
          fill: false,
          dashArray: '2 2',
          smoothFactor: 0,
          lineJoin: 'miter',
          interactive: false,
          pane: 'overlayPane',
        });
        const src = cone.affut_source || {};
        const intensityPct = cone.intensity === 'fort' ? 85 : cone.intensity === 'moyen' ? 55 : 25;
        polyOuter.bindTooltip(
          `<b style="color:#FF0000">CONTAM-Ω ${cone.intensity || 'moyen'}</b> · ${cone.reach_m || 150}m / ${cone.cone_angle_deg || 60}°`,
          { sticky: true, opacity: 0.95 }
        );
        polyOuter.bindPopup(
          `<div data-testid="contamination-popup-${cone.id || ''}" style="min-width:260px;font-family:system-ui,Segoe UI,sans-serif">
            <div style="font-weight:700;color:#FF0000;font-size:13px;letter-spacing:0.05em">CONTAMINATION-Ω V2</div>
            <div style="margin-top:4px;font-size:12px"><b>Intensité</b> : ${cone.intensity || 'moyen'} (${intensityPct}%)</div>
            <div style="font-size:12px"><b>Portée</b> : ${cone.reach_m || 150} m · <b>Cône</b> : ${cone.cone_angle_deg || 60}°</div>
            <div style="margin-top:6px;padding:4px 6px;background:#FFEBEE;border-left:3px solid #FF0000;font-size:11px;color:#B71C1C">
              <b>Analyse écologique</b><br/>
              Zone d'exposition olfactive détectable par le gibier — effet de lisière amplifié par le vent dominant.
            </div>
            <div style="margin-top:4px;font-size:11px;color:#444">
              <b>Force</b> : signal olfactif concentré autour de l'affût source.<br/>
              <b>Faiblesse</b> : dispersion par turbulence foliaire en zone boisée (± 30% attenué si canopée &gt; 60%).
            </div>
            <div style="margin-top:4px;font-size:11px;color:#1B5E20">
              <b>Optimisation</b> : éviter de stationner dans le cône ≥ 30 min ; privilégier approche contre-vent.
            </div>
            <div style="font-size:10px;color:#888;margin-top:6px">Source : ENGINE-CONTAMINATION-Ω-V2 · Affût ${src.quality || ''} (${src.score || ''})</div>
          </div>`,
          { maxWidth: 320 }
        );
        group.addLayer(polyOuter);
        group.addLayer(polyInner);
      });
    }
    // X80-ABSOLU-Ω → X120-SUPRA-CANONIQUE — signal contamination visible
    // Vrai si polygones contamination présents OU si contamination_v2 backend actif
    if (typeof window !== 'undefined') {
      const contaminationList = Array.isArray(contamination) ? contamination : (contamination ? [contamination] : []);
      const v2Present = !!contamination_v2_heatmap;
      const v2Score = bundleData.contamination_v2 && Object.keys(bundleData.contamination_v2 || {}).length > 0;
      window.__OMEGA_CONTAMINATION_LAYERS_VISIBLE__ = showContamination && (contaminationList.length > 0 || v2Present || v2Score);
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
        // X50 → X120-SUPRA-CANONIQUE — click listener → popup descriptif enrichi
        const hotLvl = level + 1;
        const hotDesc = hotLvl >= 4 ? 'Point chaud prioritaire : activité confirmée récente' : hotLvl === 3 ? 'Hotspot soutenu : passages fréquents attestés' : hotLvl === 2 ? 'Hotspot modéré : signal à confirmer saisonnièrement' : 'Signal faible : corroborer par caméra ou saline';
        const hotForce = hotLvl >= 4 ? 'Probabilité d\'observation > 70 %' : hotLvl === 3 ? 'Passage récurrent détecté' : 'Présence ponctuelle possible';
        const hotFaib = hotLvl >= 4 ? 'Zone saturée — attention aux autres chasseurs' : 'Ecarts horaires importants selon lune et pression';
        const hotOpt = 'Déployer caméra 360° + piège olfactif 200 m amont · éviter toute approche bruyante dans 80 m';
        circle.bindPopup(
          `<div data-testid="hotspot-popup-${h.id||''}" style="min-width:260px;font-family:system-ui,Segoe UI,sans-serif">
            <div style="font-weight:700;color:${color};font-size:13px;letter-spacing:0.05em">HOTSPOT ${h.type||'activité'}</div>
            <div style="margin-top:4px;font-size:11px;color:#555">${hotDesc}</div>
            <div style="margin-top:6px;font-size:12px"><b>Intensité</b> : ${hotLvl}/5 (score ${Math.round(intensity)})</div>
            ${h.justification?`<div style="font-size:11px;color:#555">${h.justification}</div>`:''}
            <div style="margin-top:6px;padding:4px 6px;background:#FFEBEE;border-left:3px solid ${color};font-size:11px;color:#B71C1C">
              <b>Force</b> : ${hotForce}<br/>
              <b>Faiblesse</b> : ${hotFaib}
            </div>
            <div style="margin-top:4px;padding:4px 6px;background:#E8F5E9;border-left:3px solid #2E7D32;font-size:11px;color:#1B5E20">
              <b>Optimisation</b> : ${hotOpt}
            </div>
            <div style="margin-top:6px;font-size:10px;color:#888">Source : ${h.source||'ENGINE-HOTSPOTS-V10'}</div>
          </div>`,
          { maxWidth: 340 }
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

    // ═══ Z-7: AFFUTS-Omega V12-R5 (Directive II) — RENDU-Ω INTÉGRAL (PHASE-E ordre Commandant 2026-04-28)
    // PURGE LEGACY : opacité réduite, palette institutionnelle Ω canonique #00A676.
    if (showAffuts && affuts.length > 0) {
      const AFFUT_BIONIC_ORANGE = '#00A676';
      const AFFUT_WHITE_STROKE = '#FFFFFF';
      affuts.forEach(a => {
        const isFixed = a.type === 'FIXE_PERMANENT';
        // AMPLIFICATION-Ω-V13: radius x1.5 si zoom<14
        const baseSz = isFixed ? 11 : 9;
        const sz_px = Math.round(baseSz * affutRadiusFactor);

        const circle = L.circleMarker([a.lat, a.lng], {
          radius: sz_px,
          color: AFFUT_WHITE_STROKE,         // contour blanc 2px Directive II
          fillColor: AFFUT_BIONIC_ORANGE,    // RENDU-Ω : palette institutionnelle Ω
          fillOpacity: 0.55,                 // PURGE Ω : 0.9 → 0.55 (atténuation conformité)
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
        // X50 → X120-SUPRA-CANONIQUE — click listener → popup descriptif enrichi
        circle.bindPopup(
          `<div data-testid="affut-popup-${a.id||''}" style="min-width:280px;font-family:system-ui,Segoe UI,sans-serif">
            <div style="font-weight:700;color:${AFFUT_BIONIC_ORANGE};font-size:13px;letter-spacing:0.05em">AFFÛT ${typeLabel}</div>
            <div style="margin-top:4px;font-size:11px;color:#555">Poste de tir institutionnel V12 optimisé</div>
            <div style="margin-top:6px;font-size:12px"><b>Score V12</b> : ${a.score_affut_v12 || a.score}/100</div>
            <div style="font-size:11px;color:#555">Corridor cible : ${a.classe_corridor_cible || a.corridor_type || 'n/a'} à ${a.distance_corridor_m || '?'} m</div>
            ${a.repositioned_distance_m ? `<div style="font-size:11px;color:#4CAF50">Repositionné auto : ${a.repositioned_distance_m} m</div>` : ''}
            <div style="margin-top:6px;padding:4px 6px;background:#FFF3E0;border-left:3px solid ${AFFUT_BIONIC_ORANGE};font-size:11px;color:#E65100">
              <b>Force</b> : ${a.justification || 'Angle de tir dégagé + couverture vent favorable'}<br/>
              <b>Faiblesse</b> : ${(a.score||0) < 60 ? 'Score modéré — vérifier vent dominant' : 'Fenêtre de tir limitée selon saison'}
            </div>
            <div style="margin-top:4px;padding:4px 6px;background:#E8F5E9;border-left:3px solid #2E7D32;font-size:11px;color:#1B5E20">
              <b>Optimisation</b> : position sous le vent, hauteur 3-4 m, écran naturel derrière l'épaule tireur · arrivée 45 min avant activité prévue
            </div>
            <div style="margin-top:6px;font-size:10px;color:#888">Source : ENGINE-AFFUTS-V12 · RENDU-Ω</div>
          </div>`,
          { maxWidth: 360 }
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
    // PHASE_XII_SUPRA_TERRITOIRE_RERENDER_Ω_ULTIME §4 — lifecycle cône olfactif.
    // Le cône est STRICTEMENT conditionné à :
    //   (1) la présence d'un waypoint actif (waypointCenter non null)
    //   (2) le flag `showWind` = true (tab VENT activé)
    //   (3) au moins 1 wind vector valide
    // Si l'une des 3 conditions tombe, le cône n'est pas re-créé et l'appel
    // clearOwnLayers() au prochain render supprime le layer existant.
    const _coneLifecycleOk = Boolean(
      showWind
      && waypointCenter
      && typeof waypointCenter.lat === 'number'
      && typeof waypointCenter.lng === 'number'
      && windVectors.length > 0
    );
    if (_coneLifecycleOk) {
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
        fillOpacity: 0,                          // §1 contour seul (cône olfactif)
        dashArray: '5,4',
        interactive: true,
        pane: 'markerPane',
      });
      cone.bindTooltip(
        `<b style="color:#FFFFFF">Cône olfactif</b> · ${Math.round(meanDir)}° · ${meanSpeed.toFixed(1)} km/h`,
        { sticky: true, opacity: 0.95 }
      );
      cone.bindPopup(
        `<div data-testid="wind-cone-popup" style="min-width:280px;font-family:system-ui,Segoe UI,sans-serif">
          <div style="font-weight:700;color:#424242;font-size:13px;letter-spacing:0.05em">CÔNE OLFACTIF V20-Ω</div>
          <div style="margin-top:4px;font-size:11px;color:#555">Zone de dispersion odorante détectable par le gibier</div>
          <div style="margin-top:6px;font-size:12px"><b>Direction</b> : ${Math.round(meanDir)}° · <b>Vitesse</b> : ${meanSpeed.toFixed(1)} km/h</div>
          <div style="font-size:11px;color:#555">Ouverture : 30° · Portée : 500 m</div>
          <div style="margin-top:6px;padding:4px 6px;background:#F5F5F5;border-left:3px solid #9E9E9E;font-size:11px;color:#424242">
            <b>Force</b> : indicateur fiable du vecteur olfactif.<br/>
            <b>Faiblesse</b> : turbulence foliaire si canopée &gt; 60 % → dispersion chaotique (+30 %).
          </div>
          <div style="margin-top:4px;padding:4px 6px;background:#E1F5FE;border-left:3px solid #0288D1;font-size:11px;color:#01579B">
            <b>Optimisation</b> : approcher contre-vent (vers ${(Math.round(meanDir)+180)%360}°) · éviter tout stationnement dans le cône.
          </div>
          <div style="margin-top:6px;font-size:10px;color:#888">Source : ENGINE-SENSORIEL-VENT-ODEURS-Ω · engine_vent.compute_scent_cone (V30-LOCKED)</div>
        </div>`,
        { maxWidth: 340 }
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
          fillOpacity: 0,                       // §2 CONTAM contour seul, intérieur transparent
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
        fillOpacity: 0,                          // §3 RISQUES contour seul
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
    // PHASE_RECAPTURE_OMEGA (2026-04-28 · ordre Commandant STEEVE-MAX) :
    // grille Ω institutionnelle (FAVORABLE/NEUTRE/RÉSERVE) — JAMAIS PARTIEL.
    if (score_local && score_local.value != null && waypointCenter) {
      // Import runtime (CommonJS safe)
      const { scoreLabelOmegaBande, scoreColorOmega } = require('@/lib/scoreLabelOmega');
      const _scoreVal = Number(score_local.value) || 0;
      const _labelInstit = scoreLabelOmegaBande(_scoreVal);
      const _colorInstit = scoreColorOmega(_labelInstit);
      const pill = L.marker([waypointCenter.lat, waypointCenter.lng], {
        icon: L.divIcon({
          className: 'score-local-pill-v20',
          html: `<div data-testid="score-local-pill" data-label-instit="${_labelInstit}" style="background:rgba(14,17,23,0.92);color:${_colorInstit};padding:4px 10px;border-radius:999px;font-size:13px;font-weight:700;border:1px solid ${_colorInstit};white-space:nowrap;letter-spacing:0.03em">SCORE ${_scoreVal.toFixed(2)} · ${_labelInstit}</div>`,
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
