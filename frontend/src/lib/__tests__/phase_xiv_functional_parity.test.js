/**
 * __tests__/phase_xiv_functional_parity.test.js
 * =========================================================
 * PHASE_XIV_CRITICAL_FUNCTIONAL_PARITY_Ω — Tests sentinelles BLOQUANTS
 * VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
 *
 * Tout échec de ce fichier = phase XIV invalidée = merge TERRITOIRE refusé.
 */

import {
  bindNutritionToSaline,
  applyOmegaFiltersToSaline,
  NUTRITION_SALINES_SPEC,
  enableInspectionBiologiqueMode,
  disableInspectionBiologiqueMode,
  INSPECTION_BIO_SPEC,
  buildInspectionBioFeatures,
} from '../renduOmegaStore';

const SALINE_FOREST = {
  id: 'S-FOR-PARITY', lat: 46.905, lng: -71.495,
  score: 76, score_bio_global: 74, score_nutrition: 80,
  status: 'SALINE-VALIDEE-Omega',
  carences_zone: ['ca', 'mg'],
  recommandations: ['Maintenir bloc Ca-Mg'],
  terrain: { urban: false, impervious_pct: 3, pente_deg: 6, canopy: 0.70, distance_eau_m: 220 },
};

const ZONES_FOREST = [{
  type: 'alimentation', excluded: false,
  polygon: [[46.90, -71.50], [46.91, -71.50], [46.91, -71.49], [46.90, -71.49]],
  terrain: { urban: false, impervious_pct: 5, pente_deg: 8, canopy: 0.72, distance_eau_m: 180 },
  score: 78, recalcul_organic_omega: true,
}];

const ZONES_URBAN = [{
  type: 'alimentation', excluded: true,
  exclusion_reason: 'zone_urbaine_anthropique',
  polygon: [[46.81, -71.21], [46.82, -71.21], [46.82, -71.20], [46.81, -71.20]],
  terrain: { urban: true, impervious_pct: 85, pente_deg: 2, canopy: 0.10, distance_eau_m: 5 },
  score: 0, recalcul_organic_omega: true,
}];

describe('PHASE_XIV_FUNCTIONAL_PARITY_Ω — SENTINELLES BLOQUANTES', () => {
  beforeEach(() => { disableInspectionBiologiqueMode(); });

  // ───── ESPÈCES & CORRIDORS ─────
  describe('ESPECES→CORRIDORS : binding nutrition respecte species', () => {
    test('orignal != chevreuil : recettes minérales différenciées', () => {
      const orignal = bindNutritionToSaline(SALINE_FOREST, {
        species: 'orignal', month: 10, zones: ZONES_FOREST,
      });
      const chevreuil = bindNutritionToSaline(SALINE_FOREST, {
        species: 'chevreuil', month: 10, zones: ZONES_FOREST,
      });
      expect(orignal.ok && chevreuil.ok).toBe(true);
      expect(orignal.species).toBe('orignal');
      expect(chevreuil.species).toBe('chevreuil');
      expect(orignal.report.recettes_minerales.formule_institutionnelle)
        .not.toBe(chevreuil.report.recettes_minerales.formule_institutionnelle);
      expect(orignal.report.besoins_journaliers.kg_par_jour)
        .not.toBe(chevreuil.report.besoins_journaliers.kg_par_jour);
    });

    test('5 espèces supportées produisent 5 rapports distincts', () => {
      const ESPECES = ['orignal', 'chevreuil', 'cerf', 'wapiti', 'caribou'];
      const rapports = ESPECES.map(sp => bindNutritionToSaline(SALINE_FOREST, {
        species: sp, month: 10, zones: ZONES_FOREST,
      }));
      for (const r of rapports) expect(r.ok).toBe(true);
      const formules = rapports.map(r => r.report.recettes_minerales.formule_institutionnelle);
      expect(new Set(formules).size).toBe(5); // 5 formules uniques
    });
  });

  // ───── AFFÛTS (indirect via filtres anthropiques) ─────
  describe('AFFUTS : exclusion anthropique active', () => {
    test('Bundle urbain → 0 feature (affûts exclus indirectement par pipeline)', () => {
      enableInspectionBiologiqueMode('expert');
      const out = buildInspectionBioFeatures({
        zones: ZONES_URBAN, salines: [], corridors: [],
        scoreLocal: { value: 15, classification: 'FAIBLE' },
      });
      // Bundle urbain → rejet global HABITAT ou BIOLOGIE → aucune couche rendue
      expect(out.attracteurs.length + out.pentes.length + out.couvert.length).toBe(0);
    });

    test('Bundle forêt → features rendues (affûts virtuels via ATTRACTEURS OK)', () => {
      enableInspectionBiologiqueMode('expert');
      const out = buildInspectionBioFeatures({
        zones: ZONES_FOREST, salines: [SALINE_FOREST], corridors: [],
        scoreLocal: { value: 72, classification: 'MODERE' },
      });
      expect(out.attracteurs.length).toBeGreaterThanOrEqual(1);
    });
  });

  // ───── SALINES & NUTRITION ─────
  describe('SALINES→NUTRITION : binding dblclick produit 11 sections conformes', () => {
    test('Saline forêt + species orignal → 11 sections + données cohérentes', () => {
      const out = bindNutritionToSaline(SALINE_FOREST, {
        species: 'orignal', month: 10, zones: ZONES_FOREST,
      });
      expect(out.ok).toBe(true);
      for (const section of NUTRITION_SALINES_SPEC.reportSections) {
        expect(out.report[section]).toBeDefined();
      }
      // Cohérence octobre (month=10) → saison automne (rut)
      expect(out.report.saisonnalite.saison_courante).toBe('automne');
      // Carences propagées depuis la saline
      expect(out.report.carences.detectees).toEqual(['ca', 'mg']);
      expect(out.report.carences.criticite).toBe('ACTIVE');
      // Score nutritionnel institutionnel
      expect(out.report.score_nutritionnel_institutionnel.valeur).toBe(80);
      expect(out.report.score_nutritionnel_institutionnel.classification).toBe('FORT');
      // Impact biologique dérivé
      expect(out.report.impact_biologique.niveau).toBe('FORT');
    });

    test('Saline urbaine → rejet avec filtre documenté', () => {
      const out = bindNutritionToSaline(
        { id: 'S-URB', lat: 46.815, lng: -71.205, terrain: { urban: true, impervious_pct: 90 } },
        { species: 'orignal', month: 10, zones: ZONES_URBAN }
      );
      expect(out.ok).toBe(false);
      expect(['EXCLUSION_AWARE_Ω', 'HABITAT_AWARE_Ω', 'TERRAIN_AWARE_Ω_FILTER']).toContain(out.filter);
    });

    test('NUTRITION_BY_SALINE_ONLY flag verrouillé true', () => {
      expect(NUTRITION_SALINES_SPEC.NUTRITION_BY_SALINE_ONLY).toBe(true);
      expect(NUTRITION_SALINES_SPEC.forbidNutritionOutsideSaline).toBe(true);
    });
  });

  // ───── CORRIDORS & DESIGN ─────
  describe('CORRIDORS DESIGN : spécifications RENDU-Ω intactes', () => {
    test('INSPECTION_BIO_SPEC orange institutionnel #FF8F00 sur ATTRACTEURS', () => {
      const attracteurs = INSPECTION_BIO_SPEC.overlayLayers.find(l => l.key === 'attracteurs');
      expect(attracteurs.color).toBe('#FF8F00');
      expect(attracteurs.stroke).toBe('#FF8F00');
    });

    test('PENTES gradient 4 paliers 5/10/15/max', () => {
      const pentes = INSPECTION_BIO_SPEC.overlayLayers.find(l => l.key === 'pentes');
      expect(pentes.gradient).toHaveLength(4);
      expect(pentes.gradient.map(g => g.upto)).toEqual([5, 10, 15, 999]);
    });

    test('Z-index ordonnés correctement (couvert < pentes < exclusions < attracteurs)', () => {
      const specs = INSPECTION_BIO_SPEC.overlayLayers;
      const zi = Object.fromEntries(specs.map(s => [s.key, s.zIndex]));
      expect(zi.couvert).toBeLessThan(zi.pentes);
      expect(zi.pentes).toBeLessThan(zi.exclusions);
      expect(zi.exclusions).toBeLessThan(zi.attracteurs);
    });
  });

  // ───── GARDE-FOU BLOQUANT ─────
  describe('GARDE-FOU PARITÉ', () => {
    test('PARITY_SENTINEL_Ω : tous les contrats scellés en place', () => {
      expect(INSPECTION_BIO_SPEC.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X10');
      expect(NUTRITION_SALINES_SPEC.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X10');
      expect(INSPECTION_BIO_SPEC.forbidNonInstitutionalFallback).toBe(true);
      expect(NUTRITION_SALINES_SPEC.forbidRawNutritionRenderInInternalTests).toBe(true);
    });
  });
});
