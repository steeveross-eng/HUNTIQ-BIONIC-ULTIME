/**
 * scoreLabelOmega.js — PHASE_XII_SUPRA_TERRITOIRE_RERENDER_Ω_ULTIME §1
 * ═══════════════════════════════════════════════════════════════════════
 * Utilitaire CENTRAL pour labellisation institutionnelle de score.
 * Grille §6.1/§6.2 ENFORCEMENT_P0 :
 *
 *   score < 70  → 'PARTIEL'    · rouge  #ef4444
 *   score ≥ 70  → 'CONFORME'   · orange #f59e0b
 *   score ≥ 90  → 'CONFORME_Ω' · vert   #16a34a
 *
 * Les labels legacy ('BON', 'MODERE', 'FAIBLE', 'EXCELLENT', 'MOYEN',
 * 'ACCEPTABLE', 'EXCEPTIONNEL') sont STRICTEMENT INTERDITS.
 *
 * BCE-4X ULTIME ABSOLU — TOP-ABSOLU.
 * ═══════════════════════════════════════════════════════════════════════
 */

export const SCORE_LABEL_PARTIEL = 'PARTIEL';
export const SCORE_LABEL_CONFORME = 'CONFORME';
export const SCORE_LABEL_CONFORME_OMEGA = 'CONFORME_Ω';

export const FORBIDDEN_LABELS = Object.freeze([
  'BON', 'MODERE', 'FAIBLE', 'EXCELLENT', 'MOYEN', 'ACCEPTABLE', 'EXCEPTIONNEL',
]);

/**
 * Retourne le label institutionnel officiel à partir d'un score.
 * @param {number|string|null|undefined} score
 * @returns {'PARTIEL'|'CONFORME'|'CONFORME_Ω'}
 */
export function scoreLabelOmega(score) {
  const s = Number(score);
  if (!Number.isFinite(s)) return SCORE_LABEL_PARTIEL;
  if (s >= 90) return SCORE_LABEL_CONFORME_OMEGA;
  if (s >= 70) return SCORE_LABEL_CONFORME;
  return SCORE_LABEL_PARTIEL;
}

/**
 * Retourne la couleur RGB institutionnelle associée au label.
 * @param {string} label
 */
export function scoreColorOmega(label) {
  switch (label) {
    case SCORE_LABEL_CONFORME_OMEGA: return '#16a34a';
    case SCORE_LABEL_CONFORME:       return '#f59e0b';
    case SCORE_LABEL_PARTIEL:
    default:                          return '#ef4444';
  }
}

/**
 * Remplace TOUT label legacy (BON, EXCELLENT, etc.) par le label institutionnel
 * déduit du score. Utilisé pour migrer les call-sites qui reçoivent une
 * classification backend non conforme.
 * @param {string|undefined} legacyLabel
 * @param {number} score
 */
export function normalizeScoreLabel(legacyLabel, score) {
  if (FORBIDDEN_LABELS.includes(String(legacyLabel || '').toUpperCase())) {
    return scoreLabelOmega(score);
  }
  // Si déjà conforme à la grille institutionnelle, on garde
  if ([SCORE_LABEL_PARTIEL, SCORE_LABEL_CONFORME, SCORE_LABEL_CONFORME_OMEGA]
        .includes(legacyLabel)) {
    return legacyLabel;
  }
  return scoreLabelOmega(score);
}
