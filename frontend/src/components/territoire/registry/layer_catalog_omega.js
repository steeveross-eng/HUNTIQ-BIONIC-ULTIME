/**
 * layer_catalog_omega.js — P20 cleanup · 18 layers source unique
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Catalogue complet des 18 couches doctrinales (cf P18 manual back-end).
 * Ordre d'affichage = ordre du tableau (groupes A→E).
 * V30_LOCK : INVIOLÉ.
 * ═══════════════════════════════════════════════════════════════
 */
import { TERRITOIRE_OMEGA_PALETTE } from './territoire_palette_omega';
import { LAYER_ICON_REGISTRY_OMEGA } from './layer_icon_registry_omega';

const P = TERRITOIRE_OMEGA_PALETTE;
const I = LAYER_ICON_REGISTRY_OMEGA;

export const LAYER_GROUPS_OMEGA = Object.freeze({
  A: { id: 'A', label: 'BASE',          color: P.base.primary,         zBase: 100 },
  B: { id: 'B', label: 'BIO-Ω',         color: P.bio_omega.primary,    zBase: 200 },
  C: { id: 'C', label: 'ENVIRONNEMENT', color: P.environnement.primary,zBase: 300 },
  D: { id: 'D', label: 'HF SPÉCIALISÉ', color: P.hf.primary,           zBase: 400 },
  E: { id: 'E', label: 'INSPECTION',    color: P.inspection.primary,   zBase: 500 },
  F: { id: 'F', label: 'CRYPTO Ω',      color: P.doctrine.gold,        zBase: 600 },
});

export const LAYER_CATALOG_OMEGA = Object.freeze([
  // --- B · BIO-Ω (5)
  { id: 'zones',         code: 'B-ZON', label: 'Zones',         desc: 'Zones doctrinales V30', group: 'B', color: P.bio_omega.zones,         icon: I.zones,         opacityDefault: 80, zIndex: 210, source: 'BionicLayersV8' },
  { id: 'corridors',     code: 'B-COR', label: 'Corridors',     desc: 'Corridors Vitaux Ω',    group: 'B', color: P.bio_omega.corridors,     icon: I.corridors,     opacityDefault: 80, zIndex: 220, source: 'BionicLayersV8' },
  { id: 'affuts',        code: 'B-AFF', label: 'Affûts',        desc: 'Affûts qualifiés',      group: 'B', color: P.bio_omega.affuts,        icon: I.affuts,        opacityDefault: 90, zIndex: 230, source: 'StandsMapLayer' },
  { id: 'salines',       code: 'B-SAL', label: 'Salines',       desc: 'Salines BP135',         group: 'B', color: P.bio_omega.salines,       icon: I.salines,       opacityDefault: 80, zIndex: 240, source: 'PhaseALayerV8' },
  { id: 'hotspots',      code: 'B-HOT', label: 'Hotspots',      desc: 'Heatmap consolidée',    group: 'B', color: P.bio_omega.hotspots,      icon: I.hotspots,      opacityDefault: 70, zIndex: 250, source: 'ConsolidatedHeatmapLayer' },
  // --- C · ENVIRONNEMENT (3)
  { id: 'vent',          code: 'C-VEN', label: 'Vent',          desc: 'Flux vent V9',          group: 'C', color: P.environnement.vent,      icon: I.vent,          opacityDefault: 70, zIndex: 310, source: 'WindFlowLayer' },
  { id: 'contamination', code: 'C-CON', label: 'Contamination', desc: 'Contamination Ω V2',    group: 'C', color: P.environnement.contamination, icon: I.contamination, opacityDefault: 65, zIndex: 320, source: 'ContaminationOverlayLayer' },
  { id: 'sensoriel',     code: 'C-SEN', label: 'Sensoriel',     desc: 'Vent + odeurs',         group: 'C', color: P.environnement.sensoriel, icon: I.sensoriel,     opacityDefault: 70, zIndex: 330, source: 'BundleData' },
  // --- D · HF SPÉCIALISÉ (7)
  { id: 'hf_lidar_hd',     code: 'D-LID', label: 'LIDAR HD',     desc: 'MHC haute résolution',group: 'D', color: P.hf.lidar_hd,     icon: I.lidar_hd,     opacityDefault: 70, zIndex: 410, source: 'HighFidelityMapLayers' },
  { id: 'hf_canopy_density', code: 'D-CAN', label: 'Canopée',     desc: 'SCANFI 2020',         group: 'D', color: P.hf.canopy,       icon: I.canopy,       opacityDefault: 60, zIndex: 420, source: 'HighFidelityMapLayers' },
  { id: 'hf_orthophoto_hr', code: 'D-ORT', label: 'Orthophoto',   desc: 'ESRI World Imagery',  group: 'D', color: P.hf.orthophoto,   icon: I.orthophoto,   opacityDefault: 80, zIndex: 430, source: 'HighFidelityMapLayers' },
  { id: 'hf_hydrology',    code: 'D-HYD', label: 'Hydrologie',    desc: 'NFIS-QC',             group: 'D', color: P.hf.hydrology,    icon: I.hydrology,    opacityDefault: 70, zIndex: 440, source: 'HighFidelityMapLayers' },
  { id: 'hf_forest_roads', code: 'D-FRD', label: 'Chemins fôr.', desc: 'MERN Québec',         group: 'D', color: P.hf.forest_roads, icon: I.forest_roads, opacityDefault: 70, zIndex: 450, source: 'HighFidelityMapLayers' },
  { id: 'hf_snow_ground',  code: 'D-SNO', label: 'Neige/Sol',    desc: 'NFIS-QC dépôts',      group: 'D', color: P.hf.snow_ground,  icon: I.snow_ground,  opacityDefault: 60, zIndex: 460, source: 'HighFidelityMapLayers' },
  { id: 'hf_slope_dem',    code: 'D-DEM', label: 'Pente DEM',    desc: 'NFIS-QC pentes',      group: 'D', color: P.hf.slope_dem,    icon: I.slope_dem,    opacityDefault: 65, zIndex: 470, source: 'HighFidelityMapLayers' },
  // --- E · INSPECTION (3)
  { id: 'cursor_bionic',   code: 'E-CUR', label: 'Curseur Bionic', desc: 'Inspection ponctuelle',group: 'E', color: P.inspection.cursor, icon: I.cursor, opacityDefault: 100, zIndex: 510, source: 'CursorBionicLayer' },
  { id: 'inspection_bio',  code: 'E-BIO', label: 'Inspection PRO', desc: 'Mode PRO/EXPERT',     group: 'E', color: P.inspection.bio,    icon: I.bio,    opacityDefault: 100, zIndex: 520, source: 'InspectionBiologiquePanel' },
  { id: 'ndvi_overlay',    code: 'E-NDV', label: 'NDVI Overlay',   desc: 'NASA MOD13Q1',        group: 'E', color: P.inspection.ndvi,   icon: I.ndvi,   opacityDefault: 60, zIndex: 530, source: 'NdviOverlayLayer' },
]);

export const LAYER_CATALOG_BY_ID_OMEGA = Object.freeze(
  Object.fromEntries(LAYER_CATALOG_OMEGA.map((l) => [l.id, l])),
);

export const LAYER_CATALOG_BY_GROUP_OMEGA = Object.freeze(
  LAYER_CATALOG_OMEGA.reduce((acc, l) => {
    if (!acc[l.group]) acc[l.group] = [];
    acc[l.group].push(l);
    return acc;
  }, {}),
);

export const LAYER_CATALOG_DOCTRINE_META = Object.freeze({
  ordre: 'P20_TERRITOIRE_UI_UX_AUDIT_Ω',
  doctrine: 'BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT',
  v30_lock: 'INVIOLÉ',
  fusion_add_only: true,
  n_layers: 18,
  generated_at_iso: new Date().toISOString(),
});

export default LAYER_CATALOG_OMEGA;
