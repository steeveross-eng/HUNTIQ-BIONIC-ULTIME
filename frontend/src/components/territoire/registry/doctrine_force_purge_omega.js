/**
 * doctrine_force_purge_omega.js — P20_PHASE3 force purge guard.
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Source UNIQUE de vérité pour les flags doctrinaux V30. Tout panneau
 * legacy/debug doit être conditionné à `IS_LEGACY_PANEL_ENABLED`.
 * Par défaut : tous les flags legacy/debug = FALSE (FORCE_DISABLE).
 *
 * V30_LOCK : INVIOLÉ.
 * ═══════════════════════════════════════════════════════════════
 */

export const BCE_4X_FORCE_PURGE_VERSION =
  'P20_PHASE3_FORCE_PURGE_2026_05_08_2147';

// Lecture optionnelle de override URL (ex: ?legacyPanels=on pour debug
// strictement local). En production, ces flags restent FALSE.
const _readUrlFlag = (key) => {
  try {
    const params = new URLSearchParams(window.location.search);
    return params.get(key) === 'on';
  } catch (e) {
    return false;
  }
};

export const IS_LEGACY_PANEL_ENABLED = _readUrlFlag('legacyPanels');
export const IS_ANALYSIS_V6_ENABLED = _readUrlFlag('analysisV6');
export const IS_DEBUG_PANEL_ENABLED = _readUrlFlag('debugPanels');
export const IS_DEV_INSPECTOR_ENABLED = _readUrlFlag('devInspector');

// Garantie doctrinal : on log uniquement quand l'utilisateur active
// volontairement un override (anti-générique : pas de fake activation).
if (IS_LEGACY_PANEL_ENABLED || IS_ANALYSIS_V6_ENABLED
    || IS_DEBUG_PANEL_ENABLED || IS_DEV_INSPECTOR_ENABLED) {
  // eslint-disable-next-line no-console
  console.warn(
    '[BCE-4X · DOCTRINE] override URL flag actif :',
    {
      legacyPanels: IS_LEGACY_PANEL_ENABLED,
      analysisV6: IS_ANALYSIS_V6_ENABLED,
      debugPanels: IS_DEBUG_PANEL_ENABLED,
      devInspector: IS_DEV_INSPECTOR_ENABLED,
    },
    'V30_LOCK : INVIOLÉ',
  );
}

// Doctrinal status check (utilisé par l'admin premium status rail)
export const getForcePurgeStatus = () => ({
  version: BCE_4X_FORCE_PURGE_VERSION,
  legacy_panels_enabled: IS_LEGACY_PANEL_ENABLED,
  analysis_v6_enabled: IS_ANALYSIS_V6_ENABLED,
  debug_panels_enabled: IS_DEBUG_PANEL_ENABLED,
  dev_inspector_enabled: IS_DEV_INSPECTOR_ENABLED,
  doctrine: 'BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT',
  v30_lock: 'INVIOLÉ',
});

export default getForcePurgeStatus;
