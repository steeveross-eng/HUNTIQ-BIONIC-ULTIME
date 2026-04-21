/**
 * __tests__/nutritionSalinesBinding.test.js
 * =========================================================
 * PHASE_NUTRITION_SALINES_BINDING_Ω — INTEGRATED_WITH_FILTERING
 * Tests institutionnels du binding exclusif nutrition↔saline
 * avec application stricte des 4 filtres Ω.
 */

import {
  enableInspectionBiologiqueMode,
  disableInspectionBiologiqueMode,
  bindNutritionToSaline,
  applyOmegaFiltersToSaline,
  assertNutritionBoundToSaline,
  NUTRITION_SALINES_SPEC,
} from '../renduOmegaStore';

const VITAL_ZONE_FOREST = {
  type: 'alimentation', excluded: false,
  polygon: [[46.90, -71.50], [46.91, -71.50], [46.91, -71.49], [46.90, -71.49]],
  terrain: { urban: false, impervious_pct: 5, pente_deg: 8, canopy: 0.72, distance_eau_m: 180 },
  score: 78,
};

const URBAN_ZONE = {
  type: 'alimentation', excluded: true,
  exclusion_reason: 'urbain_portuaire',
  polygon: [[46.81, -71.21], [46.82, -71.21], [46.82, -71.20], [46.81, -71.20]],
  terrain: { urban: true, impervious_pct: 85, distance_eau_m: 5 },
};

const SALINE_FOREST = {
  id: 'S-FOR-1', lat: 46.905, lng: -71.495,
  score: 76, score_bio_global: 74, score_nutrition: 80, score_terrain: 72,
  status: 'SALINE-VALIDEE-Omega',
  carences_zone: ['ca', 'mg'],
  recommandations: ['Maintenir bloc Ca-Mg', 'Visite bi-mensuelle avril-septembre'],
  terrain: { urban: false, impervious_pct: 3, pente_deg: 6, canopy: 0.70, distance_eau_m: 220 },
};

const SALINE_URBAN = {
  id: 'S-URB-1', lat: 46.815, lng: -71.205,
  score: 22, status: 'SALINE-A-REPOSITIONNER-Omega',
  terrain: { urban: true, impervious_pct: 92, distance_eau_m: 3 },
};

describe('PHASE_NUTRITION_SALINES_BINDING_Ω', () => {
  beforeEach(() => { disableInspectionBiologiqueMode(); });

  test('NUTRITION_SALINES_SPEC scellée avec 11 sections', () => {
    expect(NUTRITION_SALINES_SPEC.NUTRITION_BY_SALINE_ONLY).toBe(true);
    expect(NUTRITION_SALINES_SPEC.forbidNutritionOutsideSaline).toBe(true);
    expect(NUTRITION_SALINES_SPEC.reportSections).toHaveLength(11);
  });

  test('applyOmegaFiltersToSaline : saline forêt acceptée', () => {
    const res = applyOmegaFiltersToSaline(SALINE_FOREST, {
      zones: [VITAL_ZONE_FOREST],
      scoreLocal: { value: 72, classification: 'MODERE' },
    });
    expect(res.ok).toBe(true);
  });

  test('applyOmegaFiltersToSaline : saline urbaine rejetée par TERRAIN_AWARE', () => {
    const res = applyOmegaFiltersToSaline(SALINE_URBAN, {
      zones: [VITAL_ZONE_FOREST],
      scoreLocal: { value: 72, classification: 'MODERE' },
    });
    expect(res.ok).toBe(false);
    expect(['EXCLUSION_AWARE_Ω', 'TERRAIN_AWARE_Ω_FILTER']).toContain(res.filter);
  });

  test('applyOmegaFiltersToSaline : bundle sans habitat → HABITAT_AWARE_Ω rejet', () => {
    const res = applyOmegaFiltersToSaline(SALINE_FOREST, {
      zones: [URBAN_ZONE], // pas de zone vitale non-excluded
      scoreLocal: { value: 72, classification: 'MODERE' },
    });
    expect(res.ok).toBe(false);
    expect(res.filter).toBe('HABITAT_AWARE_Ω');
  });

  test('applyOmegaFiltersToSaline : score local FAIBLE → BIOLOGIE_AWARE_Ω rejet', () => {
    const res = applyOmegaFiltersToSaline(SALINE_FOREST, {
      zones: [VITAL_ZONE_FOREST],
      scoreLocal: { value: 10, classification: 'NON_HABITAT' },
    });
    expect(res.ok).toBe(false);
    expect(res.filter).toBe('BIOLOGIE_AWARE_Ω_FILTER');
  });

  test('bindNutritionToSaline : saline forêt → rapport 11 sections complet', () => {
    const out = bindNutritionToSaline(SALINE_FOREST, {
      species: 'orignal', month: 10,
      zones: [VITAL_ZONE_FOREST],
      scoreLocal: { value: 72, classification: 'MODERE' },
    });
    expect(out.ok).toBe(true);
    expect(out.species).toBe('orignal');
    expect(out.saline.id).toBe('S-FOR-1');
    for (const section of NUTRITION_SALINES_SPEC.reportSections) {
      expect(out.report[section]).toBeDefined();
    }
    // Vérifications de contenu institutionnel
    expect(out.report.besoins_journaliers.kg_par_jour).toBeGreaterThan(0);
    expect(out.report.mineraux.ca_g).toBeGreaterThan(0);
    expect(out.report.mineraux.na_g).toBeGreaterThan(0);
    expect(out.report.carences.detectees).toEqual(['ca', 'mg']);
    expect(out.report.score_nutritionnel_institutionnel.valeur).toBe(80);
  });

  test('bindNutritionToSaline : saline urbaine rejetée → payload ok=false', () => {
    const out = bindNutritionToSaline(SALINE_URBAN, {
      species: 'cerf', month: 10,
      zones: [VITAL_ZONE_FOREST, URBAN_ZONE],
      scoreLocal: { value: 72, classification: 'MODERE' },
    });
    expect(out.ok).toBe(false);
    expect(['EXCLUSION_AWARE_Ω', 'TERRAIN_AWARE_Ω_FILTER']).toContain(out.filter);
    expect(out.report).toBeUndefined();
  });

  test('assertNutritionBoundToSaline : refuse contexte orphelin', () => {
    expect(assertNutritionBoundToSaline(null)).toBe(false);
    expect(assertNutritionBoundToSaline({})).toBe(false);
    expect(assertNutritionBoundToSaline({ saline: SALINE_FOREST })).toBe(true);
    expect(assertNutritionBoundToSaline({ saline_id: 'S-FOR-1' })).toBe(true);
  });

  test('Saisonnalité par mois : octobre → automne', () => {
    const out = bindNutritionToSaline(SALINE_FOREST, {
      species: 'cerf', month: 10,
      zones: [VITAL_ZONE_FOREST],
    });
    expect(out.ok).toBe(true);
    expect(out.report.saisonnalite.saison_courante).toBe('automne');
  });

  test('Saisonnalité par mois : juillet → ete', () => {
    const out = bindNutritionToSaline(SALINE_FOREST, {
      species: 'chevreuil', month: 7,
      zones: [VITAL_ZONE_FOREST],
    });
    expect(out.ok).toBe(true);
    expect(out.report.saisonnalite.saison_courante).toBe('ete');
  });

  test('Recette minérale différenciée par espèce', () => {
    const orignal = bindNutritionToSaline(SALINE_FOREST, {
      species: 'orignal', month: 10, zones: [VITAL_ZONE_FOREST],
    });
    const chevreuil = bindNutritionToSaline(SALINE_FOREST, {
      species: 'chevreuil', month: 10, zones: [VITAL_ZONE_FOREST],
    });
    expect(orignal.ok && chevreuil.ok).toBe(true);
    expect(orignal.report.recettes_minerales.formule_institutionnelle).not.toBe(
      chevreuil.report.recettes_minerales.formule_institutionnelle
    );
  });
});
