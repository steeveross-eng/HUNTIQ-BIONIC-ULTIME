/**
 * __tests__/inspectionBioFiltering.test.js
 * =========================================
 * PHASE_INSPECTION_BIO_FILTERING_Ω — ENFORCE_URBAN_EXCLUSION
 * Tests internes institutionnels des 4 filtres Ω.
 *
 * Directive : "INTERDIRE tout rendu brut non filtré dans les tests internes"
 *   → chaque test doit prouver qu'un bundle urbain/non-habitat produit 0 feature
 *     même avec mode inspection EXPERT actif.
 *
 * Exécution : npx jest inspectionBioFiltering --rootDir /app/frontend
 */

import {
  enableInspectionBiologiqueMode,
  disableInspectionBiologiqueMode,
  buildInspectionBioFeatures,
  OMEGA_FILTERS_SPEC,
} from '../renduOmegaStore';

const URBAN_ZONE = {
  type: 'alimentation',
  excluded: true,
  exclusion_reason: 'urbain_portuaire',
  polygon: [[46.81, -71.21], [46.82, -71.21], [46.82, -71.20], [46.81, -71.20]],
  terrain: { urban: true, impervious_pct: 85, pente_deg: 2, canopy: 0.10, distance_eau_m: 5 },
  score: 10,
};

const VITAL_ZONE_FOREST = {
  type: 'alimentation',
  excluded: false,
  polygon: [[46.90, -71.50], [46.91, -71.50], [46.91, -71.49], [46.90, -71.49]],
  terrain: { urban: false, impervious_pct: 5, pente_deg: 8, canopy: 0.72, distance_eau_m: 180 },
  score: 78,
};

const SALINE_URBAN = {
  lat: 46.815, lng: -71.205, id: 'S-URB-1', score: 20,
  terrain: { urban: true, impervious_pct: 90, distance_eau_m: 3 },
};

const SALINE_FOREST = {
  lat: 46.905, lng: -71.495, id: 'S-FOR-1', score: 80,
  terrain: { urban: false, impervious_pct: 2, pente_deg: 4, canopy: 0.75, distance_eau_m: 200 },
};

describe('PHASE_INSPECTION_BIO_FILTERING_Ω', () => {
  beforeEach(() => {
    // clean state
    disableInspectionBiologiqueMode();
  });

  test('OMEGA_FILTERS_SPEC contient les 4 filtres institutionnels', () => {
    const ids = Object.values(OMEGA_FILTERS_SPEC.filters).map(f => f.id);
    expect(ids).toEqual(
      expect.arrayContaining([
        'EXCLUSION_AWARE_Ω',
        'HABITAT_AWARE_Ω',
        'TERRAIN_AWARE_Ω_FILTER',
        'BIOLOGIE_AWARE_Ω_FILTER',
      ])
    );
    expect(OMEGA_FILTERS_SPEC.forbidRawRenderInInternalTests).toBe(true);
  });

  test('Bundle URBAIN pur → 0 feature rendue même en mode EXPERT', () => {
    enableInspectionBiologiqueMode('expert');
    const out = buildInspectionBioFeatures({
      zones: [URBAN_ZONE],
      salines: [SALINE_URBAN],
      corridors: [],
      scoreLocal: { value: 15, classification: 'FAIBLE' },
    });
    expect(out).not.toBeNull();
    expect(out.filtersActive).toBe(true);
    expect(out.attracteurs).toHaveLength(0);
    expect(out.pentes).toHaveLength(0);
    expect(out.couvert).toHaveLength(0);
    // Au moins un des filtres globaux a été déclenché
    const anyGlobal = out.rejections.HABITAT_AWARE_Ω === -1 || out.rejections.BIOLOGIE_AWARE_Ω_FILTER === -1;
    expect(anyGlobal).toBe(true);
  });

  test('Bundle URBAIN avec habitat OK mais score FAIBLE → rejet BIOLOGIE_AWARE_Ω', () => {
    enableInspectionBiologiqueMode('expert');
    const out = buildInspectionBioFeatures({
      zones: [URBAN_ZONE, VITAL_ZONE_FOREST], // 1 vital non-excluded OK → habitat OK
      salines: [SALINE_URBAN],
      corridors: [],
      scoreLocal: { value: 10, classification: 'NON_HABITAT' },
    });
    expect(out.rejections.BIOLOGIE_AWARE_Ω_FILTER).toBe(-1);
    expect(out.attracteurs).toHaveLength(0);
    expect(out.pentes).toHaveLength(0);
  });

  test('Bundle FORET + score MODERE → features correctement rendues', () => {
    enableInspectionBiologiqueMode('expert');
    const out = buildInspectionBioFeatures({
      zones: [VITAL_ZONE_FOREST],
      salines: [SALINE_FOREST],
      corridors: [],
      scoreLocal: { value: 72, classification: 'MODERE' },
    });
    expect(out).not.toBeNull();
    expect(out.attracteurs.length).toBeGreaterThanOrEqual(2); // saline + centroïde zone vitale
    expect(out.pentes.length).toBeGreaterThanOrEqual(1);
    expect(out.couvert.length).toBeGreaterThanOrEqual(1);
  });

  test('Filtre EXCLUSION_AWARE_Ω : saline urbaine rejetée dans bundle avec habitat valide', () => {
    enableInspectionBiologiqueMode('expert');
    const out = buildInspectionBioFeatures({
      zones: [VITAL_ZONE_FOREST, URBAN_ZONE],
      salines: [SALINE_URBAN, SALINE_FOREST],
      corridors: [],
      scoreLocal: { value: 68, classification: 'MODERE' },
    });
    // saline urbaine rejetée par TERRAIN_AWARE (impervious_pct=90 > 60)
    // saline forêt acceptée
    const salineIds = out.attracteurs.filter(a => a.meta.source === 'saline').map(a => a.meta.id);
    expect(salineIds).toContain('S-FOR-1');
    expect(salineIds).not.toContain('S-URB-1');
    // La saline urbaine tombe dans le polygone URBAN_ZONE → rejet EXCLUSION_AWARE_Ω
    // (le centroïde du polygone URBAN_ZONE contient S-URB-1 [46.815, -71.205]).
    // Si non, elle serait rejetée par TERRAIN_AWARE (impervious_pct=90 > 60).
    const anyUrbanRejection =
      out.rejections.EXCLUSION_AWARE_Ω > 0 ||
      out.rejections.TERRAIN_AWARE_Ω_FILTER > 0;
    expect(anyUrbanRejection).toBe(true);
  });

  test('Mode OFF → buildInspectionBioFeatures retourne null', () => {
    disableInspectionBiologiqueMode();
    const out = buildInspectionBioFeatures({
      zones: [VITAL_ZONE_FOREST], salines: [SALINE_FOREST], corridors: [],
      scoreLocal: { value: 80, classification: 'FORT' },
    });
    expect(out).toBeNull();
  });

  test('Bundle sans zones vitales → HABITAT_AWARE_Ω rejet global', () => {
    enableInspectionBiologiqueMode('pro');
    const out = buildInspectionBioFeatures({
      zones: [URBAN_ZONE], // seule excluded
      salines: [SALINE_FOREST],
      corridors: [],
      scoreLocal: { value: 60, classification: 'MODERE' },
    });
    expect(out.rejections.HABITAT_AWARE_Ω).toBe(-1);
    expect(out.attracteurs).toHaveLength(0);
  });
});
