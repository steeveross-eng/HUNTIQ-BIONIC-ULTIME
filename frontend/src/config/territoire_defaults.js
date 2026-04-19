/**
 * TERRITOIRE DEFAULTS-Ω — POINT DE VÉRITÉ UNIQUE
 * ==================================================
 * Tous les defaults d'affichage institutionnels de TERRITOIRE-Ω.
 * ZERO duplication autorisee dans les composants.
 * Toute modification de defaults DOIT passer par ce fichier.
 *
 * FLAGS ALWAYS-ON institutionnels: defaults=true signifie ALWAYS-ON par defaut.
 * L'utilisateur peut desactiver via bouton presseur, mais le pipeline serveur
 * GENERE TOUJOURS les couches (zero filtrage anthropique bloquant).
 */

// ═══ ALWAYS-ON FLAGS (institutionnels) ═══
export const TERRITOIRE_DEFAULTS = Object.freeze({
  SALINES: true,
  CORRIDORS: true,
  ZONES: true,
  AFFUTS: true,
  HOTSPOTS: true,
  VENT: true,
  CONTAMINATION: true,
  CURSEUR: true,
  INTEL: true,
});

// ═══ FLAGS ALWAYS-ON (informatifs — verifies par test_defaults_omega) ═══
export const ALWAYS_ON_FLAGS = Object.freeze({
  CORRIDORS_ALWAYS_ON: true,
  SALINES_ALWAYS_ON: true,
  AFFUTS_ALWAYS_ON: true,
  ZONES_ALWAYS_ON: true,
  HOTSPOTS_ALWAYS_ON: true,
  VENT_ALWAYS_ON: true,
  CONTAM_ALWAYS_ON: true,
  CURSEUR_ALWAYS_ON: true,
  INTEL_ALWAYS_ON: true,
});

// ═══ STYLE HIERARCHISE CORRIDORS (Directive III) ═══
// Intensite = epaisseur + opacite (surbrillance) strictement croissantes.
// Minimums institutionnels: weight>=1.4, opacity>=0.55.
export const CORRIDOR_STYLE_HIERARCHY = Object.freeze({
  // Mapping backend types → palette V11-SUPRA hierarchisee
  extreme: Object.freeze({
    label: 'CRITIQUE',
    color: '#FF0000',
    weight: 4.0,
    opacity: 1.0,
    surbrillance: 1.0,
  }),
  intense: Object.freeze({
    label: 'MAJEUR',
    color: '#FF6A00',
    weight: 3.2,
    opacity: 0.85,
    surbrillance: 0.85,
  }),
  saisonnier: Object.freeze({
    label: 'FORT',
    color: '#FFC300',
    weight: 2.6,
    opacity: 0.75,
    surbrillance: 0.75,
  }),
  normal: Object.freeze({
    label: 'MODERE',
    color: '#00B050',
    weight: 2.0,
    opacity: 0.65,
    surbrillance: 0.65,
  }),
  // Reserve pour future extension backend
  faible: Object.freeze({
    label: 'FAIBLE',
    color: '#00B0F0',
    weight: 1.4,
    opacity: 0.55,
    surbrillance: 0.55,
  }),
});

// ═══ COULEURS INSTITUTIONNELLES (alignees avec Directive III) ═══
export const INSTITUTIONAL_COLORS = Object.freeze({
  SALINE_YELLOW: '#FDD835',
  SALINE_YELLOW_HALO: 'rgba(253, 216, 53, 0.45)',
  AFFUT_FIXE: '#9E9E9E',
  AFFUT_TEMP: '#1E88E5',
  AFFUT_SURBRILLANCE: 0.85,
  CONTAM_FAIBLE: '#FFCC80',
  CONTAM_MOYEN: '#FB8C00',
  CONTAM_FORT: '#D84315',
});

// ═══ RSE-Ω — RENDER-SPEC-OMEGA SUPRA-EXTENDED ═══
// Config centralisee par couche (minZoom/maxZoom/zIndex/halo/palette/espacement).
// Source unique pour BionicLayersV8 + RenderGuardOmega + tests.
export const RSE_LAYERS_CONFIG = Object.freeze({
  contamination: {
    minZoom: 12, maxZoom: 16, zIndex: 400,
    halo: '#FF7043', espacementMin: 0, geometry: 'polygon',
  },
  zones: {
    minZoom: 12, maxZoom: 16, zIndex: 500,
    halo: '#29B6F6', espacementMin: 0, geometry: 'polygon-organic',
  },
  corridors: {
    minZoom: 12, maxZoom: 16, zIndex: 600,
    halo: '#FFC300', espacementMin: 0, geometry: 'polyline-catmull',
  },
  nutrition: {
    minZoom: 13, maxZoom: 16, zIndex: 450,
    halo: '#4CAF50', espacementMin: 200, geometry: 'point-grid',
  },
  salines: {
    minZoom: 13, maxZoom: 16, zIndex: 700,
    halo: '#FDD835', espacementMin: 300, geometry: 'point-halo',
  },
  hotspots: {
    minZoom: 13, maxZoom: 16, zIndex: 750,
    halo: '#B84D9C', espacementMin: 200, geometry: 'point-halo',
  },
  affuts: {
    minZoom: 13, maxZoom: 16, zIndex: 800,
    halo: '#FF9800', espacementMin: 300, geometry: 'point-marker',
  },
  vent: {
    minZoom: 14, maxZoom: 16, zIndex: 850,
    halo: '#00E5FF', espacementMin: 0, geometry: 'line-flow',
  },
});

// ═══ NUTRITION-V12-SUPRA palette par severite carence ═══
export const NUTRITION_SEVERITY_COLORS = Object.freeze({
  aucune:  { fill: '#808080', stroke: '#555555' },
  legere:  { fill: '#22C55E', stroke: '#15803D' },
  moderee: { fill: '#F59E0B', stroke: '#B45309' },
  forte:   { fill: '#EF4444', stroke: '#991B1B' },
});

export default TERRITOIRE_DEFAULTS;
