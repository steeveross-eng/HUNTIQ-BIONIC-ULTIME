/**
 * speciesColorOmega.js — Palette différenciée par ESPÈCE
 * ============================================================
 * P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω
 * Doctrine : chaque espèce dispose d'une signature couleur strictement
 * distincte pour éliminer la perception d'identité visuelle inter-espèces.
 * La hiérarchie de la veine est encodée par épaisseur (weight) et opacité.
 *
 * COULEURS INSTITUTIONNELLES (BCE-4X · STEEVE-MAX) :
 *   chevreuil       → vert organique  (#2D7A2D / #5BC68F)
 *   orignal         → brun chaud      (#8B4513 / #C68B5B)
 *   ours_noir       → violet profond  (#5D2E8C / #8E6BC7)
 *   wapiti          → bleu ardoise    (#1E5F8E / #5BA0D6)
 *   dindon_sauvage  → ambre or        (#D4A017 / #E8C547)
 *   coyote          → gris graphite   (#555555 / #888888)
 *
 * Compatibilité fallback : pour espèces inconnues, retour à la palette
 * hiérarchique historique (orange-rouge / orange / pêche).
 */

// Palette couleurs strictement institutionnelle Ω
export const SPECIES_COLOR_OMEGA = {
  chevreuil: {
    primary:   '#2D7A2D', // veine_principale
    secondary: '#5BC68F', // veine_secondaire
    capillary: '#8FD9A8', // capillaire
    halo:      '#A8E8C0', // halo externe espèce
    label:     'CHEVREUIL',
  },
  orignal: {
    primary:   '#8B4513',
    secondary: '#C68B5B',
    capillary: '#D9A582',
    halo:      '#E8BFA0',
    label:     'ORIGNAL',
  },
  ours_noir: {
    primary:   '#5D2E8C',
    secondary: '#8E6BC7',
    capillary: '#B299D9',
    halo:      '#CCB8E8',
    label:     'OURS NOIR',
  },
  wapiti: {
    primary:   '#1E5F8E',
    secondary: '#5BA0D6',
    capillary: '#88BFE5',
    halo:      '#B0D4ED',
    label:     'WAPITI',
  },
  dindon_sauvage: {
    primary:   '#D4A017',
    secondary: '#E8C547',
    capillary: '#F0D77A',
    halo:      '#F5E5A8',
    label:     'DINDON SAUVAGE',
  },
  coyote: {
    primary:   '#555555',
    secondary: '#888888',
    capillary: '#AAAAAA',
    halo:      '#C8C8C8',
    label:     'COYOTE',
  },
  // multi_aggregated : palette neutre violette pour la vue "TOUTES ESPÈCES"
  multi_aggregated: {
    primary:   '#7B3F99',
    secondary: '#B073D0',
    capillary: '#D4A8E8',
    halo:      '#E8C8F5',
    label:     'MULTI · ESPÈCES',
  },
};

// Fallback palette historique (hiérarchie pure) — utilisée si espèce inconnue
export const FALLBACK_HIER_COLOR = {
  veine_principale: '#FF4500',
  veine_secondaire: '#FF8F00',
  capillaire:       '#FFB347',
  connector:        '#FFEE99',
};

// Alias d'espèces utilisés côté frontend pour normalisation
const SPECIES_ALIAS = {
  cerf: 'chevreuil',
  cerf_de_virginie: 'chevreuil',
  deer: 'chevreuil',
  ours: 'ours_noir',
  bear: 'ours_noir',
  moose: 'orignal',
  elk: 'wapiti',
  dindon: 'dindon_sauvage',
  wild_turkey: 'dindon_sauvage',
  canis_latrans: 'coyote',
};

/**
 * Normalise un nom d'espèce vers la clé canonique de la palette.
 */
export const normalizeSpeciesKey = (species) => {
  if (!species) return 'multi_aggregated';
  const lower = String(species).toLowerCase().trim();
  if (lower === 'tous' || lower === 'toutes' || lower === 'all') return 'multi_aggregated';
  return SPECIES_ALIAS[lower] || lower;
};

/**
 * Retourne la palette de couleurs pour une espèce donnée.
 * Fallback gracieux vers multi_aggregated si espèce inconnue.
 */
export const getSpeciesPaletteOmega = (species) => {
  const key = normalizeSpeciesKey(species);
  return SPECIES_COLOR_OMEGA[key] || SPECIES_COLOR_OMEGA.multi_aggregated;
};

/**
 * Résout la couleur d'un corridor donné selon ESPÈCE × HIÉRARCHIE.
 *  - veine_principale → palette.primary
 *  - veine_secondaire → palette.secondary
 *  - capillaire       → palette.capillary
 *  - connector / autre → palette.secondary (fallback)
 */
export const getCorridorColorBySpeciesAndHierarchy = (species, hierarchy) => {
  const palette = getSpeciesPaletteOmega(species);
  switch (hierarchy) {
    case 'veine_principale':
      return palette.primary;
    case 'veine_secondaire':
      return palette.secondary;
    case 'capillaire':
      return palette.capillary;
    default:
      return palette.secondary;
  }
};

/**
 * Résout le weight (épaisseur) d'un corridor selon hiérarchie.
 * Doctrine : §8 ENGINE CORRIDORS Ω — 4 niveaux 1.2/2.0/3.0/4.0
 */
export const getCorridorWeightByHierarchy = (hierarchy) => {
  switch (hierarchy) {
    case 'veine_principale':
      return 4.0;
    case 'veine_secondaire':
      return 2.5;
    case 'capillaire':
      return 1.5;
    default:
      return 2.0;
  }
};

/**
 * Résout l'opacité d'un corridor selon hiérarchie.
 * veine_principale = 1.0 (doctrine SUPRA-Ω-ART : OBLIGATOIRE)
 */
export const getCorridorOpacityByHierarchy = (hierarchy) => {
  switch (hierarchy) {
    case 'veine_principale':
      return 1.0;
    case 'veine_secondaire':
      return 0.78;
    case 'capillaire':
      return 0.55;
    default:
      return 0.70;
  }
};
