/**
 * speciesColorOmega.js — Palette différenciée par ESPÈCE
 * ============================================================
 * P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω · 2026-02-XX
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU
 *
 * 🔒 VERROU ABSOLU — PALETTE FIGÉE INVIOLABLE
 * ───────────────────────────────────────────────────────────────────
 * Toute modification de cette palette est INTERDITE sauf directive
 * explicite du COMMANDANT STEEVE-MAX. Cette palette a été doctrinalement
 * validée pour lisibilité sur fond vert (satellite forestier ESRI/Maxar)
 * en biorégion BSL/Québec.
 *
 * Doctrine : chaque espèce dispose d'une signature couleur strictement
 * distincte pour éliminer la perception d'identité visuelle inter-espèces.
 * La hiérarchie de la veine est encodée par épaisseur (weight) et opacité.
 *
 * COULEURS INSTITUTIONNELLES (BCE-4X · STEEVE-MAX) :
 *   chevreuil       → ORANGE AMBRÉ      (#FF8F00 / #FFB347)
 *   orignal         → BLEU PROFOND      (#1E5F8E / #5BA0D6)
 *   ours_noir       → VIOLET SOMBRE     (#5D2E8C / #8E6BC7)
 *   wapiti          → ROUGE BRIQUE      (#C0392B / #E57373)
 *   dindon_sauvage  → AMBRE DORÉ        (#D4A017 / #E8C547)
 *   coyote          → GRIS ACIER        (#6E6E6E / #A0A0A0)
 *
 * 🚫 COULEURS INTERDITES (anti-régression) :
 *   - #E65100 (orange foncé mono legacy)
 *   - #2D7A2D / #5BC68F (vert chevreuil ancien — illisible sur fond forêt)
 *   - #8B4513 / #C68B5B (brun orignal ancien — fusion visuelle avec sol)
 *
 * Compatibilité fallback : pour espèces inconnues, retour à la palette
 * `multi_aggregated` (violet neutre #7B3F99).
 */

// 🔒 Palette couleurs strictement institutionnelle Ω · VERROUILLÉE
export const SPECIES_COLOR_OMEGA = Object.freeze({
  chevreuil: Object.freeze({
    primary:   '#FF8F00', // veine_principale  — ORANGE AMBRÉ
    secondary: '#FFB347', // veine_secondaire
    capillary: '#FFCC80', // capillaire
    halo:      '#FFE0B2', // halo externe espèce
    label:     'CHEVREUIL',
  }),
  orignal: Object.freeze({
    primary:   '#1E5F8E', // veine_principale  — BLEU PROFOND
    secondary: '#5BA0D6',
    capillary: '#88BFE5',
    halo:      '#B0D4ED',
    label:     'ORIGNAL',
  }),
  ours_noir: Object.freeze({
    primary:   '#5D2E8C', // veine_principale  — VIOLET SOMBRE
    secondary: '#8E6BC7',
    capillary: '#B299D9',
    halo:      '#CCB8E8',
    label:     'OURS NOIR',
  }),
  wapiti: Object.freeze({
    primary:   '#C0392B', // veine_principale  — ROUGE BRIQUE
    secondary: '#E57373',
    capillary: '#EF9A9A',
    halo:      '#FFCDD2',
    label:     'WAPITI',
  }),
  dindon_sauvage: Object.freeze({
    primary:   '#D4A017', // veine_principale  — AMBRE DORÉ
    secondary: '#E8C547',
    capillary: '#F0D77A',
    halo:      '#F5E5A8',
    label:     'DINDON SAUVAGE',
  }),
  coyote: Object.freeze({
    primary:   '#6E6E6E', // veine_principale  — GRIS ACIER
    secondary: '#A0A0A0',
    capillary: '#BFBFBF',
    halo:      '#D8D8D8',
    label:     'COYOTE',
  }),
  // multi_aggregated : palette neutre violette pour la vue "TOUTES ESPÈCES"
  multi_aggregated: Object.freeze({
    primary:   '#7B3F99',
    secondary: '#B073D0',
    capillary: '#D4A8E8',
    halo:      '#E8C8F5',
    label:     'MULTI · ESPÈCES',
  }),
});

// 🚫 Liste explicite des couleurs INTERDITES (vérification anti-régression)
export const FORBIDDEN_COLORS_OMEGA = Object.freeze([
  '#E65100', // mono orange foncé legacy
  '#2D7A2D', // vert chevreuil ancien
  '#5BC68F',
  '#8FD9A8',
  '#A8E8C0',
  '#8B4513', // brun orignal ancien
  '#C68B5B',
  '#D9A582',
  '#E8BFA0',
]);

// Fallback palette historique (hiérarchie pure) — utilisée si espèce inconnue
export const FALLBACK_HIER_COLOR = Object.freeze({
  veine_principale: '#FF8F00',
  veine_secondaire: '#FFB347',
  capillaire:       '#FFCC80',
  connector:        '#FFE0B2',
});

// Alias d'espèces utilisés côté frontend pour normalisation
const SPECIES_ALIAS = Object.freeze({
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
});

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

/**
 * 🔒 Garde anti-régression : assert qu'une couleur n'est pas dans la liste
 * des couleurs interdites. Utilisé dans les tests doctrinaux.
 */
export const assertNotForbiddenColor = (color) => {
  if (!color) return true;
  const upper = String(color).toUpperCase();
  return !FORBIDDEN_COLORS_OMEGA.some((c) => c.toUpperCase() === upper);
};
