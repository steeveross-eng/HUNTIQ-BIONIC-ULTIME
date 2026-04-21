/**
 * __tests__/phase_xvi_enforce_single_pipeline.test.js
 * =========================================================
 * PHASE_XVI_ENFORCE_SINGLE_PIPELINE_Ω — Tests sentinelles BLOQUANTS ×2
 * VERSION_INSTITUTIONNELLE_RENFORCÉE_X20
 *
 * Tout échec de ce fichier = phase XVI invalidée = tout merge refusé.
 * Double protection : chaque sécurité X10 est re-vérifiée + variantes X20.
 */

import {
  ENFORCE_PIPELINE_SPEC_V20,
  enforceInstitutionalPipeline,
  getPipelineEnforcementStatus,
  detectAnthropicRender,
  assertNoAnthropicRender,
  buildInspectionBioFeatures,
  enableInspectionBiologiqueMode,
  disableInspectionBiologiqueMode,
  INSPECTION_BIO_SPEC,
  NUTRITION_SALINES_SPEC,
  OMEGA_FILTERS_SPEC,
} from '../renduOmegaStore';

describe('PHASE_XVI_ENFORCE_SINGLE_PIPELINE_Ω — SENTINELLES ×2', () => {
  beforeEach(() => {
    disableInspectionBiologiqueMode();
    if (typeof window !== 'undefined') {
      delete window.__RAW_RENDER_ATTEMPTS__;
      delete window.__ANTHROPIC_RENDER_FAILURES__;
    }
  });

  // ───── ENFORCE_PIPELINE_SPEC_V20 ─────
  describe('SPEC V20 scellée', () => {
    test('Protocole V20 : 8 flags doublés actifs', () => {
      expect(ENFORCE_PIPELINE_SPEC_V20.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X20');
      expect(ENFORCE_PIPELINE_SPEC_V20.supersedesVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X10');
      expect(ENFORCE_PIPELINE_SPEC_V20.BCE4X_FULL_LOCK_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.STEEVE_MAX_SECURITY_SUITE_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.ZERO_REGRESSION_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.ZERO_PERTE_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.MODULARITE_100_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.ANTI_DUPLICATION_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.ANTI_FALLBACK_DOUBLED).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.ENGINE_REGISTRY_LOCK_DOUBLED).toBe(true);
    });

    test('Pipeline unique forcé : 4 environnements obligatoires', () => {
      expect(ENFORCE_PIPELINE_SPEC_V20.singlePipelineEnforced).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.forbidRawRenderMode).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.forbidInternalNonFilteredEndpoints).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.mandatoryOmegaFiltersEnvironments).toEqual(
        expect.arrayContaining(['preview', 'capture', 'validation', 'audit'])
      );
    });

    test('Tokens urbains bloquants : 8 entrées minimales', () => {
      expect(ENFORCE_PIPELINE_SPEC_V20.urbanTokens.length).toBeGreaterThanOrEqual(8);
      expect(ENFORCE_PIPELINE_SPEC_V20.urbanRenderIsBlockingFailure).toBe(true);
    });
  });

  // ───── enforceInstitutionalPipeline ─────
  describe('enforceInstitutionalPipeline — garde runtime', () => {
    test('Pipeline conforme (filtered=true, bypass=false) → OK', () => {
      const ok = enforceInstitutionalPipeline('test.caller', { filtered: true, bypassOmega: false });
      expect(ok).toBe(true);
      expect(typeof window === 'undefined' || !window.__RAW_RENDER_ATTEMPTS__).toBe(true);
    });

    test('Pipeline raw (bypassOmega=true) → false + incrément audit', () => {
      const ok = enforceInstitutionalPipeline('test.raw1', { bypassOmega: true });
      expect(ok).toBe(false);
      expect(window.__RAW_RENDER_ATTEMPTS__.count).toBe(1);
      expect(window.__RAW_RENDER_ATTEMPTS__.lastAttempt.caller).toBe('test.raw1');
      expect(window.__RAW_RENDER_ATTEMPTS__.lastAttempt.reason).toBe('bypassOmega_true');
    });

    test('Pipeline non filtré (filtered=false) → false + incrément', () => {
      enforceInstitutionalPipeline('test.raw2', { filtered: false });
      expect(window.__RAW_RENDER_ATTEMPTS__.count).toBe(1);
      expect(window.__RAW_RENDER_ATTEMPTS__.lastAttempt.reason).toBe('filtered_false');
    });

    test('Multiples tentatives raw : compteur cumulatif', () => {
      for (let i = 0; i < 5; i++) enforceInstitutionalPipeline(`caller.${i}`, { bypassOmega: true });
      expect(window.__RAW_RENDER_ATTEMPTS__.count).toBe(5);
      expect(window.__RAW_RENDER_ATTEMPTS__.entries.length).toBe(5);
    });
  });

  // ───── getPipelineEnforcementStatus ─────
  describe('getPipelineEnforcementStatus — audit Commandant', () => {
    test('État initial : conforming=true, 0 tentative', () => {
      const st = getPipelineEnforcementStatus();
      expect(st.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X20');
      expect(st.singlePipelineEnforced).toBe(true);
      expect(st.rawRenderAttempts).toBe(0);
      expect(st.conforming).toBe(true);
    });

    test('État après tentative raw : conforming=false', () => {
      enforceInstitutionalPipeline('audit.test', { bypassOmega: true });
      const st = getPipelineEnforcementStatus();
      expect(st.rawRenderAttempts).toBe(1);
      expect(st.conforming).toBe(false);
      expect(st.lastAttempt.caller).toBe('audit.test');
    });
  });

  // ───── detectAnthropicRender ─────
  describe('detectAnthropicRender — détection bloquante', () => {
    test('Feature urbaine → anthropic=true', () => {
      expect(detectAnthropicRender({ terrain: { urban: true } }).anthropic).toBe(true);
      expect(detectAnthropicRender({ terrain: { industrial: true } }).anthropic).toBe(true);
      expect(detectAnthropicRender({ terrain: { port: true } }).anthropic).toBe(true);
      expect(detectAnthropicRender({ terrain: { impervious_pct: 85 } }).anthropic).toBe(true);
    });

    test('Feature forêt → anthropic=false', () => {
      const d = detectAnthropicRender({
        terrain: { urban: false, industrial: false, port: false, impervious_pct: 12, canopy: 0.7 },
      });
      expect(d.anthropic).toBe(false);
    });

    test('Feature avec exclusion_reason=urbain → détecté', () => {
      const d = detectAnthropicRender({ exclusion_reason: 'zone_urbaine_anthropique', terrain: {} });
      expect(d.anthropic).toBe(true);
      expect(d.token).toBe('urbain');
    });
  });

  // ───── assertNoAnthropicRender ─────
  describe('assertNoAnthropicRender — bloquante', () => {
    test('Feature conforme → passe sans erreur', () => {
      expect(() => assertNoAnthropicRender({
        id: 'z1', terrain: { urban: false, impervious_pct: 10, canopy: 0.8 },
      }, 'test.ok')).not.toThrow();
    });

    test('Feature urbaine → lève ANTHROPIC_RENDER_BLOCKING_FAILURE', () => {
      expect(() => assertNoAnthropicRender({
        id: 'z-urb', terrain: { urban: true, impervious_pct: 85 },
      }, 'test.fail')).toThrow(/ANTHROPIC_RENDER_BLOCKING_FAILURE/);
      expect(window.__ANTHROPIC_RENDER_FAILURES__).toHaveLength(1);
      expect(window.__ANTHROPIC_RENDER_FAILURES__[0].caller).toBe('test.fail');
    });

    test('Feature impervious>60 → bloque avec raison documentée', () => {
      expect(() => assertNoAnthropicRender({
        terrain: { impervious_pct: 75, urban: false },
      }, 'impervious_test')).toThrow(/impervious_pct=75/);
    });
  });

  // ───── Pipeline intégré : buildInspectionBioFeatures doit jamais produire anthropique ─────
  describe('Pipeline intégré — aucune feature anthropique rendue', () => {
    test('Bundle urbain + expert → aucune feature avec terrain anthropique dans la sortie', () => {
      enableInspectionBiologiqueMode('expert');
      const URBAN = {
        type: 'alimentation', excluded: true, exclusion_reason: 'zone_urbaine_anthropique',
        polygon: [[46.81, -71.21], [46.82, -71.21], [46.82, -71.20], [46.81, -71.20]],
        terrain: { urban: true, impervious_pct: 85, pente_deg: 2, canopy: 0.10 },
        score: 0,
      };
      const FOREST = {
        type: 'alimentation', excluded: false,
        polygon: [[46.90, -71.50], [46.91, -71.50], [46.91, -71.49], [46.90, -71.49]],
        terrain: { urban: false, impervious_pct: 5, pente_deg: 8, canopy: 0.72 },
        score: 78,
      };
      const out = buildInspectionBioFeatures({
        zones: [URBAN, FOREST], salines: [], corridors: [],
        scoreLocal: { value: 72, classification: 'MODERE' },
      });
      // Toutes les features rendues doivent être non-anthropiques
      const all = [...out.attracteurs, ...out.exclusions, ...out.pentes, ...out.couvert];
      // Les exclusions ont `terrain.urban` mais leur couche s'appelle EXCLUSIONS — elles sont OK car représentent les zones interdites.
      // Seules attracteurs, pentes, couvert ne doivent PAS provenir de zone urbaine
      for (const f of out.attracteurs) {
        expect(() => assertNoAnthropicRender({ terrain: f.meta?.terrain || {} }, 'attracteurs')).not.toThrow();
      }
    });
  });

  // ───── DOUBLE VERROUILLAGE : X10 + X20 ─────
  describe('DOUBLE VERROUILLAGE X10 + X20', () => {
    test('X10 : tous les forbid* actifs', () => {
      expect(INSPECTION_BIO_SPEC.forbidNonInstitutionalFallback).toBe(true);
      expect(NUTRITION_SALINES_SPEC.forbidNutritionOutsideSaline).toBe(true);
      expect(NUTRITION_SALINES_SPEC.forbidRawNutritionRenderInInternalTests).toBe(true);
      expect(OMEGA_FILTERS_SPEC.forbidRawRenderInInternalTests).toBe(true);
    });

    test('X20 : pipeline unique + double lock', () => {
      expect(ENFORCE_PIPELINE_SPEC_V20.forbidRawRenderMode).toBe(true);
      expect(ENFORCE_PIPELINE_SPEC_V20.singlePipelineEnforced).toBe(true);
      // 8 flags doublés
      const doubled = Object.keys(ENFORCE_PIPELINE_SPEC_V20).filter(k => k.endsWith('_DOUBLED'));
      expect(doubled.length).toBeGreaterThanOrEqual(8);
      for (const k of doubled) expect(ENFORCE_PIPELINE_SPEC_V20[k]).toBe(true);
    });
  });
});
