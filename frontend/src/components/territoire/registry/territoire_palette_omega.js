/**
 * territoire_palette_omega.js — P20 cleanup · doctrinal palette
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Source UNIQUE de vérité couleurs/halos pour TOUS les panels et
 * couches Ω. Remplace progressivement les palettes dispersées dans
 * TerritoireToolbar / HighFidelityMapsPanel / LayersOmegaSyncPanel.
 *
 * Tous accès via TERRITOIRE_OMEGA_PALETTE.<group>.<token>
 * V30_LOCK : INVIOLÉ — modifications additives uniquement.
 * ═══════════════════════════════════════════════════════════════
 */
export const TERRITOIRE_OMEGA_PALETTE = Object.freeze({
  // Groupe A · BASE
  base: {
    primary: '#64748B',
    surface: '#0F1419',
    text: '#E8E4D9',
    muted: '#94A3B8',
  },
  // Groupe B · BIO-Ω
  bio_omega: {
    zones:     '#00A676',
    corridors: '#FFD600',
    affuts:    '#33B787',
    salines:   '#A78BFA',
    hotspots:  '#F59E0B',
    primary:   '#00A676',
  },
  // Groupe C · ENVIRONNEMENT
  environnement: {
    vent:          '#90CAF9',
    contamination: '#DC2626',
    sensoriel:     '#06B6D4',
    primary:       '#06B6D4',
  },
  // Groupe D · HF SPECIALISÉ
  hf: {
    lidar_hd:     '#F59E0B',
    canopy:       '#22C55E',
    orthophoto:   '#3B82F6',
    hydrology:    '#06B6D4',
    forest_roads: '#A855F7',
    snow_ground:  '#E0F2FE',
    slope_dem:    '#EF4444',
    primary:      '#F59E0B',
  },
  // Groupe E · INSPECTION
  inspection: {
    cursor: '#4A7A2E',
    bio:    '#FF8F00',
    ndvi:   '#A78BFA',
    primary: '#A78BFA',
  },
  // Doctrinal accents
  doctrine: {
    gold:    '#D4A017',
    success: '#00A676',
    danger:  '#DC2626',
    warning: '#F59E0B',
    info:    '#06B6D4',
  },
});

export default TERRITOIRE_OMEGA_PALETTE;
