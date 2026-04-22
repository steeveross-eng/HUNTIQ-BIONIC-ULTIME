"""
p1_preparation.py — Préparation P1 EN BROUILLON (FEATURE FLAGS = OFF)
=======================================================================
Phase : PHASE_X200_P1_PREVIEW_ET_PREPARATION_Ω
Commandant STEEVE-MAX

Contient la LOGIQUE BROUILLON des 3 comportements P1 futurs :
  1. Densité 5 niveaux vers smoother X180
     (branchement reseau_veineux_omega → organic_corridor_smoother)
  2. Enforce ≥2 zones vitales par corridor
  3. Scoring 8-facteurs appliqué en post-V30 (post-processing Ω)

AUCUN de ces comportements n'est exécuté tant que :
  - le flag correspondant est True
  - ET que `is_p1_activation_authorized()` renvoie True

La fonction d'autorisation requiert une commande explicite du Commandant
(variable d'environnement P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true + token).
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAGS P1 — TOUS OFF — ACTIVATION INTERDITE SANS ORDRE EXPLICITE
# ═══════════════════════════════════════════════════════════════════════
P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER: bool = False
P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES:    bool = False
P1_FLAG_POST_V30_SCORING_8_FACTORS:   bool = False


def is_p1_activation_authorized() -> Dict[str, Any]:
    """Double-vérification : aucun flag ON par défaut + env var + token."""
    env_authorized = os.environ.get(
        "P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_ok = os.environ.get("P1_COMMANDANT_TOKEN", "") == "STEEVE-MAX-P1-EXPLICIT"
    return {
        "authorized": env_authorized and token_ok,
        "env_authorized": env_authorized,
        "token_ok": token_ok,
        "flags_p1": {
            "density_5_levels_to_smoother": P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER,
            "enforce_min_2_vital_zones":    P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES,
            "post_v30_scoring_8_factors":   P1_FLAG_POST_V30_SCORING_8_FACTORS,
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE BROUILLON #1 — DENSITÉ 5 NIVEAUX VERS SMOOTHER X180
# ═══════════════════════════════════════════════════════════════════════
def draft_enrich_corridor_with_hierarchy(corridor: Dict[str, Any],
                                         bio_score_0_100: float) -> Dict[str, Any]:
    """BROUILLON : ajoute 5 niveaux V7 (level, weight_px, color_hex) au corridor.

    Cette fonction NE SERA APPELÉE par le smoother X180 que lorsque
    P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER passe à True ET autorisation OK.
    """
    if not (P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER and is_p1_activation_authorized()["authorized"]):
        return corridor  # No-op si non autorisé
    from engines.reseau_veineux_omega.router import classify_corridor
    lvl = classify_corridor(float(bio_score_0_100))
    enriched = dict(corridor)
    enriched["level_v7"] = lvl["level"]
    enriched["weight_px_v7"] = lvl["weight_px"]
    enriched["color_hex_v7"] = lvl["color"]
    enriched["largeur_m_v7"] = lvl["largeur_m"]
    enriched["dash_array_v7"] = lvl.get("dash_array")
    return enriched


# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE BROUILLON #2 — ENFORCE ≥ 2 ZONES VITALES
# ═══════════════════════════════════════════════════════════════════════
def draft_enforce_min_2_vital_zones(corridor: Dict[str, Any]) -> Dict[str, Any]:
    """BROUILLON : marque un corridor `rejected_by_p1` si < 2 zones vitales.

    Aucun rejet réel tant que le flag est OFF. Marqueur purement prévisionnel.
    """
    connections = corridor.get("vital_zone_connections") or []
    count = len(connections)
    out = dict(corridor)
    out["p1_preview_vital_zone_count"] = count
    if P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES and is_p1_activation_authorized()["authorized"]:
        out["rejected_by_p1"] = count < 2
        out["p1_rejection_reason"] = (
            "vital_zone_connections_insufficient" if count < 2 else None
        )
    else:
        out["rejected_by_p1"] = False
        out["p1_rejection_reason"] = None
    return out


# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE BROUILLON #3 — SCORING 8-FACTEURS POST-V30
# ═══════════════════════════════════════════════════════════════════════
def draft_apply_post_v30_scoring(corridor: Dict[str, Any],
                                 subscores: Optional[Dict[str, Any]] = None
                                 ) -> Dict[str, Any]:
    """BROUILLON : applique le scoring 8-facteurs V7 au corridor en post-V30.

    Ne fait rien si flag OFF. Conçu pour être injecté APRÈS le smoother X180
    sans modifier V30 scellé.
    """
    out = dict(corridor)
    if not (P1_FLAG_POST_V30_SCORING_8_FACTORS and is_p1_activation_authorized()["authorized"]):
        return out
    from engines.bio_scoring_omega.router import score_8_factors
    subs = subscores or corridor.get("subscores") or {}
    res = score_8_factors(subs)
    out["post_v30_bio_score_0_100"] = res["score_0_100"]
    out["post_v30_scoring_applied"] = True
    return out


# ═══════════════════════════════════════════════════════════════════════
# DIAGNOSTIC — ÉTAT P1
# ═══════════════════════════════════════════════════════════════════════
def p1_preparation_status() -> Dict[str, Any]:
    return {
        "phase": "X200-P1-PREPARATION",
        "mode": "BROUILLON",
        "flags_all_off": (
            not P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER
            and not P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES
            and not P1_FLAG_POST_V30_SCORING_8_FACTORS
        ),
        "authorization": is_p1_activation_authorized(),
        "behaviors_documented": [
            "density_5_levels_to_smoother",
            "enforce_min_2_vital_zones",
            "post_v30_scoring_8_factors",
        ],
        "smoother_touched": False,
        "rendu_modified": False,
    }
