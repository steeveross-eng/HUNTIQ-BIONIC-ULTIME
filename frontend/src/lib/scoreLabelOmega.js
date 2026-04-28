/**
 * scoreLabelOmega.js — PHASE_XII_SUPRA_TERRITOIRE_RERENDER_Ω_ULTIME §1
 * ═══════════════════════════════════════════════════════════════════════
 * Utilitaire CENTRAL pour labellisation institutionnelle de score.
 *
 * GRILLE LEGACY (V30 alignement, métrique secondaire) :
 *   score < 70  → 'PARTIEL'    · rouge  #ef4444
 *   score ≥ 70  → 'CONFORME'   · orange #f59e0b
 *   score ≥ 90  → 'CONFORME_Ω' · vert   #16a34a
 *
 * GRILLE Ω INSTITUTIONNELLE (PHASE-E FUSION TERRITOIRE_Ω) :
 *   score < 50   → 'RÉSERVE'         · rouge  #ef4444
 *   50 ≤ s < 70  → 'NEUTRE'          · orange #f59e0b
 *   70 ≤ s < 85  → 'FAVORABLE'       · vert   #16a34a
 *   score ≥ 85   → 'TRÈS_FAVORABLE'  · vert   #00A676
 *
 * PHASE_RECAPTURE_OMEGA (2026-04-28 · ordre Commandant STEEVE-MAX) :
 *   La pastille SCORE LOCAL doit utiliser la grille Ω (jamais PARTIEL).
 *   Les labels legacy ('BON', 'MODERE', 'FAIBLE', 'EXCELLENT', 'MOYEN',
 *   'ACCEPTABLE', 'EXCEPTIONNEL') sont STRICTEMENT INTERDITS.
 *
 * BCE-4X ULTIME ABSOLU — TOP-ABSOLU.
 * ═══════════════════════════════════════════════════════════════════════
 */

export const SCORE_LABEL_PARTIEL = 'PARTIEL';
export const SCORE_LABEL_CONFORME = 'CONFORME';
export const SCORE_LABEL_CONFORME_OMEGA = 'CONFORME_Ω';

// Grille Ω institutionnelle (alignée backend fusion_territoire_omega.py)
export const SCORE_LABEL_RESERVE = 'RÉSERVE';
export const SCORE_LABEL_NEUTRE = 'NEUTRE';
export const SCORE_LABEL_FAVORABLE = 'FAVORABLE';
export const SCORE_LABEL_TRES_FAVORABLE = 'TRÈS_FAVORABLE';

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
 * PHASE_RECAPTURE_OMEGA — Retourne la BANDE Ω institutionnelle d'un score.
 * Utilisée pour la pastille SCORE LOCAL et tout affichage en mode Ω.
 * Garantit qu'aucun "PARTIEL" n'apparaît.
 * @param {number|string|null|undefined} score
 * @returns {'RÉSERVE'|'NEUTRE'|'FAVORABLE'|'TRÈS_FAVORABLE'}
 */
export function scoreLabelOmegaBande(score) {
  const s = Number(score);
  if (!Number.isFinite(s)) return SCORE_LABEL_NEUTRE;
  if (s >= 85) return SCORE_LABEL_TRES_FAVORABLE;
  if (s >= 70) return SCORE_LABEL_FAVORABLE;
  if (s >= 50) return SCORE_LABEL_NEUTRE;
  return SCORE_LABEL_RESERVE;
}

/**
 * Retourne la couleur RGB institutionnelle associée au label.
 * @param {string} label
 */
export function scoreColorOmega(label) {
  switch (label) {
    case SCORE_LABEL_TRES_FAVORABLE: return '#00A676';
    case SCORE_LABEL_CONFORME_OMEGA: return '#16a34a';
    case SCORE_LABEL_FAVORABLE:      return '#16a34a';
    case SCORE_LABEL_CONFORME:       return '#f59e0b';
    case SCORE_LABEL_NEUTRE:         return '#f59e0b';
    case SCORE_LABEL_RESERVE:        return '#ef4444';
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
  if ([SCORE_LABEL_PARTIEL, SCORE_LABEL_CONFORME, SCORE_LABEL_CONFORME_OMEGA,
       SCORE_LABEL_RESERVE, SCORE_LABEL_NEUTRE, SCORE_LABEL_FAVORABLE,
       SCORE_LABEL_TRES_FAVORABLE]
        .includes(legacyLabel)) {
    return legacyLabel;
  }
  return scoreLabelOmega(score);
}
