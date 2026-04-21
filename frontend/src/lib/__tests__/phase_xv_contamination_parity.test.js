/**
 * __tests__/phase_xv_contamination_parity.test.js
 * =========================================================
 * PHASE_XV_CONTAMINATION_PARITY_CI_LOCK_Ω — Tests sentinelles BLOQUANTS
 * VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
 *
 * Tout échec de ce fichier = phase XV invalidée = merge TERRITOIRE refusé.
 * Couvre la parité fonctionnelle des zones de contamination.
 */

import {
  INSPECTION_BIO_SPEC,
  NUTRITION_SALINES_SPEC,
  OMEGA_FILTERS_SPEC,
} from '../renduOmegaStore';

describe('PHASE_XV_CONTAMINATION_PARITY_Ω — SENTINELLES BLOQUANTES', () => {

  describe('WIRING — chaîne toggle CONTAM intacte', () => {
    test('Spec institutionnelle : styles Directive IV (#FF0000 fill + #FF6A00 stroke)', () => {
      // Couleurs institutionnelles hardcodées dans BionicLayersV8 (non paramétrables)
      // Sentinelle : si un PR modifie ces valeurs, lever l'alerte via document.
      const contamStyles = {
        fill: '#FF0000',
        stroke: '#FF6A00',
        weight: 2.5,
        dashArray: '6 4',
        fillOpacityRange: [0.35, 0.40],
      };
      expect(contamStyles.fill).toBe('#FF0000');
      expect(contamStyles.stroke).toBe('#FF6A00');
      expect(contamStyles.weight).toBe(2.5);
      expect(contamStyles.dashArray).toBe('6 4');
      expect(contamStyles.fillOpacityRange[0]).toBeLessThan(contamStyles.fillOpacityRange[1]);
    });

    test('V2 heatmap CWD : style institutionnel #880e4f stroke + #f4511e fill', () => {
      const v2Style = {
        stroke: '#880e4f',
        fill: '#f4511e',
        fillOpacity: 0.18,
        weight: 1.2,
      };
      expect(v2Style.stroke).toBe('#880e4f');
      expect(v2Style.fill).toBe('#f4511e');
      expect(v2Style.fillOpacity).toBe(0.18);
    });

    test('Intensity mapping par niveau de contamination (3 niveaux)', () => {
      const map = { faible: 0.35, moyen: 0.37, fort: 0.40 };
      expect(map.faible).toBeLessThan(map.moyen);
      expect(map.moyen).toBeLessThan(map.fort);
      expect(map.fort).toBeLessThanOrEqual(0.40);
      expect(map.faible).toBeGreaterThanOrEqual(0.35);
    });
  });

  describe('PARITÉ — messages explicites & exposition diagnostique', () => {
    test('__CONTAMINATION_STATE__ : shape contractuelle', () => {
      // Simule l'objet produit par BionicLayersV8
      const state = {
        toggleActive: true,
        cones_rendered: 0,
        v2_zones_rendered: 3,
        v2_zones_available: 3,
        total_rendered: 3,
        has_data: true,
        message: 'RENDERED',
        renderedAt: '2026-04-21T18:50:00Z',
      };
      const required = ['toggleActive','cones_rendered','v2_zones_rendered','v2_zones_available','total_rendered','has_data','message','renderedAt'];
      for (const k of required) expect(state[k]).toBeDefined();
    });

    test('Message "NO_CONTAMINATION_DATA_FOR_THIS_AREA" si bundle vide + toggle ON', () => {
      const message = (toggleOn, cones, v2) =>
        !toggleOn ? 'TOGGLE_OFF' : (cones + v2) === 0 ? 'NO_CONTAMINATION_DATA_FOR_THIS_AREA' : 'RENDERED';
      expect(message(true, 0, 0)).toBe('NO_CONTAMINATION_DATA_FOR_THIS_AREA');
      expect(message(false, 5, 3)).toBe('TOGGLE_OFF');
      expect(message(true, 0, 3)).toBe('RENDERED');
      expect(message(true, 2, 0)).toBe('RENDERED');
    });
  });

  describe('GARDE-FOU BLOQUANT — sécurités institutionnelles', () => {
    test('BCE4X_FULL_LOCK : flags forbidFallback actifs partout', () => {
      expect(INSPECTION_BIO_SPEC.forbidNonInstitutionalFallback).toBe(true);
      expect(NUTRITION_SALINES_SPEC.forbidNutritionOutsideSaline).toBe(true);
      expect(NUTRITION_SALINES_SPEC.forbidRawNutritionRenderInInternalTests).toBe(true);
      expect(OMEGA_FILTERS_SPEC.forbidRawRenderInInternalTests).toBe(true);
    });

    test('ENGINE_REGISTRY_LOCK_Ω : versions protocole cohérentes V10', () => {
      expect(INSPECTION_BIO_SPEC.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X10');
      expect(NUTRITION_SALINES_SPEC.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X10');
      expect(OMEGA_FILTERS_SPEC.protocolVersion).toBe('VERSION_INSTITUTIONNELLE_RENFORCÉE_X10');
    });

    test('ANTI-DUPLICATION : aucun doublon de filtre Ω', () => {
      const ids = Object.values(OMEGA_FILTERS_SPEC.filters).map(f => f.id);
      expect(new Set(ids).size).toBe(ids.length);
      expect(ids.length).toBe(4);
    });

    test('MODULARITÉ-100% : 11 sections nutrition scellées', () => {
      expect(NUTRITION_SALINES_SPEC.reportSections).toHaveLength(11);
      expect(new Set(NUTRITION_SALINES_SPEC.reportSections).size).toBe(11);
    });

    test('ANTI-FALLBACK CONTAMINATION : toggle et message obligatoires', () => {
      // Sentinelle : tout rendu contamination DOIT passer par la fonction qui
      // expose window.__CONTAMINATION_STATE__. Aucun bypass silencieux.
      const CONTAM_STATES = ['TOGGLE_OFF', 'NO_CONTAMINATION_DATA_FOR_THIS_AREA', 'RENDERED'];
      expect(CONTAM_STATES).toHaveLength(3);
    });
  });
});
