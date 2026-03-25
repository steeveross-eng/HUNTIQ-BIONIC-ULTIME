"""
CORE Scoring Pipeline — Gestion des saisons
===============================================
Directive x3205. Source unique pour le mapping mois → saison.
BCE-4X: Valeurs identiques a celles des 3 moteurs originaux.
"""

# ══════════════════════════════════════════════════════════════════
# MAPPING MOIS → SAISON
# ══════════════════════════════════════════════════════════════════
# Origine: alimentation_v1, repos_v1, corridors_v10 (identique dans les 3)
# Region: Quebec, Canada

MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}

VALID_SEASONS = {"printemps", "ete", "automne", "hiver"}


def get_season(month: int) -> str:
    """Retourne la saison pour un mois donne (1-12).
    Defaut: 'automne' si mois invalide."""
    return MONTH_TO_SEASON.get(month, "automne")
