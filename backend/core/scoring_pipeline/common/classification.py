"""
CORE Scoring Pipeline — Systeme de classification unifie
============================================================
Directive x3205. Modele unique de classification parametrable.
Chaque moteur definit sa propre configuration de niveaux,
mais utilise le meme framework de classification.

BCE-4X: Les seuils et labels de chaque moteur restent IDENTIQUES.
Aucune modification des valeurs originales.

SYSTEMES IDENTIFIES DANS x3204:
  1. ALIMENTATION-V1: OPTIMALE(80+), TRES_BONNE(60-79), UTILISABLE(40-59), FAIBLE(0-39)
  2. REPOS-V1:        OPTIMAL(80+), TRES_BON(60-79), UTILISABLE(40-59), FAIBLE(0-39)
  3. CORRIDORS-V10 (reseau): OPTIMAL(75+), FONCTIONNEL(50-74), DEGRADE(25-49), INUTILISABLE(0-24)
  4. CORRIDORS-V10 (corridor): CRITIQUE(85+), MAJEUR(70-84), FORT(50-69), MODERE(30-49), FAIBLE(0-29)
  5. score_consolide: OPTIMAL(80+), BON(60-79), MODERE(40-59), FAIBLE(0-39)
"""


# ══════════════════════════════════════════════════════════════════
# CONFIGURATIONS PAR MOTEUR (valeurs originales preservees)
# ══════════════════════════════════════════════════════════════════

CLASSIFICATION_CONFIGS = {
    "ALIMENTATION_V1": {
        "engine": "ALIMENTATION-V1",
        "levels": [
            {"name": "OPTIMALE", "min": 80, "max": 100, "color": "#1B5E20", "label_fr": "Optimale"},
            {"name": "TRES_BONNE", "min": 60, "max": 79, "color": "#4CAF50", "label_fr": "Tres bonne"},
            {"name": "UTILISABLE", "min": 40, "max": 59, "color": "#FF9800", "label_fr": "Utilisable"},
            {"name": "FAIBLE", "min": 0, "max": 39, "color": "#F44336", "label_fr": "Faible"},
        ],
    },
    "REPOS_V1": {
        "engine": "REPOS-V1",
        "levels": [
            {"name": "OPTIMAL", "min": 80, "max": 100, "color": "#1565C0", "label_fr": "Optimal"},
            {"name": "TRES_BON", "min": 60, "max": 79, "color": "#42A5F5", "label_fr": "Tres bon"},
            {"name": "UTILISABLE", "min": 40, "max": 59, "color": "#FF9800", "label_fr": "Utilisable"},
            {"name": "FAIBLE", "min": 0, "max": 39, "color": "#F44336", "label_fr": "Faible"},
        ],
    },
    "CORRIDORS_V10_NETWORK": {
        "engine": "CORRIDORS-V10",
        "scope": "reseau",
        "levels": [
            {"name": "OPTIMAL", "min": 75, "max": 100, "color": "#1B5E20", "label_fr": "Optimal"},
            {"name": "FONCTIONNEL", "min": 50, "max": 74, "color": "#4CAF50", "label_fr": "Fonctionnel"},
            {"name": "DEGRADE", "min": 25, "max": 49, "color": "#FF9800", "label_fr": "Degrade"},
            {"name": "INUTILISABLE", "min": 0, "max": 24, "color": "#F44336", "label_fr": "Inutilisable"},
        ],
    },
    "CORRIDORS_V10_CORRIDOR": {
        "engine": "CORRIDORS-V10",
        "scope": "corridor_individuel",
        "levels": [
            {"name": "CRITIQUE", "min": 85, "max": 100, "color": "#CC0000", "label_fr": "Critique",
             "pattern": "striped", "largeur_m": 4, "render_weight": 6, "dash_array": "10,4"},
            {"name": "MAJEUR", "min": 70, "max": 84, "color": "#FF0000", "label_fr": "Majeur",
             "pattern": None, "largeur_m": 6, "render_weight": 5, "dash_array": None},
            {"name": "FORT", "min": 50, "max": 69, "color": "#FF8C00", "label_fr": "Fort",
             "pattern": None, "largeur_m": 11, "render_weight": 4, "dash_array": None},
            {"name": "MODERE", "min": 30, "max": 49, "color": "#FFD700", "label_fr": "Modere",
             "pattern": None, "largeur_m": 17, "render_weight": 3, "dash_array": None},
            {"name": "FAIBLE", "min": 0, "max": 29, "color": "#BFBFBF", "label_fr": "Faible",
             "pattern": None, "largeur_m": 26, "render_weight": 2, "dash_array": None},
        ],
    },
    "SCORE_CONSOLIDE": {
        "engine": "SCORE-CONSOLIDE",
        "levels": [
            {"name": "OPTIMAL", "min": 80, "max": 100, "color": "#DC2626", "label_fr": "Optimal"},
            {"name": "BON", "min": 60, "max": 79, "color": "#F59E0B", "label_fr": "Bon"},
            {"name": "MODERE", "min": 40, "max": 59, "color": "#22C55E", "label_fr": "Modere"},
            {"name": "FAIBLE", "min": 0, "max": 39, "color": "#3B82F6", "label_fr": "Faible"},
        ],
    },
}


def classify(score: float, config_name: str) -> dict:
    """
    Classifie un score (0-100) selon la configuration d'un moteur.

    Args:
        score: Score a classifier (0-100)
        config_name: Cle dans CLASSIFICATION_CONFIGS

    Returns:
        dict avec: classe, label_fr, color, score_range, [+ extras pour corridors]
    """
    config = CLASSIFICATION_CONFIGS.get(config_name)
    if not config:
        raise COREClassificationError(f"Configuration inconnue: {config_name}")

    for level in config["levels"]:
        if score >= level["min"]:
            result = {
                "classe": level["name"],
                "label_fr": level["label_fr"],
                "color": level["color"],
                "score_range": f"{level['min']}-{level['max']}",
            }
            # Extras pour corridors individuels
            for key in ("pattern", "largeur_m", "render_weight", "dash_array"):
                if key in level:
                    result[key] = level[key]
            return result

    # Fallback: dernier niveau
    last = config["levels"][-1]
    return {
        "classe": last["name"],
        "label_fr": last["label_fr"],
        "color": last["color"],
        "score_range": f"{last['min']}-{last['max']}",
    }


def classify_batch(scores: list, config_name: str) -> dict:
    """
    Classifie un batch de scores et retourne des statistiques.

    Args:
        scores: Liste de scores (0-100)
        config_name: Cle dans CLASSIFICATION_CONFIGS

    Returns:
        dict avec: total, distribution, avg_score, min_score, max_score
    """
    if not scores:
        return {"total": 0, "distribution": {}, "avg_score": 0, "min_score": 0, "max_score": 0}

    config = CLASSIFICATION_CONFIGS.get(config_name)
    if not config:
        raise COREClassificationError(f"Configuration inconnue: {config_name}")

    results = [classify(s, config_name) for s in scores]
    counts = {}
    for r in results:
        cls = r["classe"]
        counts[cls] = counts.get(cls, 0) + 1

    total = len(scores)
    distribution = {}
    for level in config["levels"]:
        name = level["name"]
        count = counts.get(name, 0)
        distribution[name] = {
            "count": count,
            "pct": round(100 * count / max(total, 1), 1),
            "label_fr": level["label_fr"],
            "color": level["color"],
        }

    return {
        "total": total,
        "distribution": distribution,
        "avg_score": round(sum(scores) / total, 1),
        "min_score": round(min(scores), 1),
        "max_score": round(max(scores), 1),
    }


class COREClassificationError(Exception):
    """Erreur de classification CORE."""
    pass
