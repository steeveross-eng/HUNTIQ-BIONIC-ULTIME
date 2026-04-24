/**
 * Territory Module Components
 * ═══════════════════════════════════════════════════════════════════════
 * PHASE_XII_SUPRA_PURGE_PIPELINES_SECONDAIRES_Ω — 2026-04-24
 * COMMANDANT STEEVE-MAX — BCE-4X ULTIME ABSOLU
 *
 * PURGES APPLIQUÉES :
 *   - TerritoryAdvanced        (0 usage externe — ORPHELIN PUR)
 *   - TerritoryAnalysisModule  (fichier absent du disque depuis longtemps)
 *   - TerritoryInventory       (fichier absent du disque depuis longtemps)
 *   - TerritoryRankings        (fichier absent du disque depuis longtemps)
 *
 * Seul export conservé : TerritoryMap (22 usages actifs dans
 * TerritoryAdvanced → purgé / BionicPrecisionZonesLayer / pipeline
 * territoire actif — NON ORPHELIN).
 *
 * Toute réintroduction future exige directive explicite du COMMANDANT.
 * ═══════════════════════════════════════════════════════════════════════
 */

export { default as TerritoryMap } from '../../../components/TerritoryMap';
