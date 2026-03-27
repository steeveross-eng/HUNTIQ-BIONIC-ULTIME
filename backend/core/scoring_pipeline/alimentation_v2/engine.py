"""
ALIMENTATION-V2 — Engine principal
=====================================
Analyse territoriale + Salines + Recommandations nutritionnelles.
100% algorithmique interne, zéro API externe.
Conforme BCE-4X: aucune modification des 16 zones ou 64 centres.
"""
from .terrain import analyze_terrain
from .salines import compute_salines
from .nutrition import get_nutrition, NUTRITION_DB

SPECIES_MAP = {
    "CERF": "CERF", "ORIGNAL": "ORIGNAL", "OURS": "OURS",
    "WAPITI": "WAPITI", "DINDON": "DINDON",
}

# Mapping IDs frontend → backend
FRONTEND_SPECIES_MAP = {
    "chevreuil": "CERF",
    "orignal": "ORIGNAL",
    "ours_noir": "OURS",
    "dindon_sauvage": "DINDON",
    "wapiti": "WAPITI",
    "tous": "CERF",
}

SPECIES_LIST = list(SPECIES_MAP.keys())

# Espèces qui n'utilisent PAS les salines (directive biologique STEEVE-MAX)
SPECIES_NO_SALINES = {"OURS", "DINDON"}
SPECIES_NO_SALINES_MESSAGES = {
    "OURS": "L'ours noir n'utilise pas les salines. Ce comportement est normal et conforme à la biologie de l'espèce.",
    "DINDON": "Le dindon n'utilise pas les salines. Ce comportement est normal et conforme à la biologie de l'espèce.",
}


def analyze_alimentation_v2(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    max_salines: int = 4,
) -> dict:
    """
    Analyse alimentaire complète V2.
    Retourne: terrain, salines, recommandations nutritionnelles.
    STEEVE-MAX: OURS et DINDON ne génèrent aucune saline.
    Diversification spatiale: min 300m entre salines.
    """
    # Résolution espèce: accepte IDs frontend ou backend
    species_resolved = FRONTEND_SPECIES_MAP.get(species.lower(), species.upper())
    if species_resolved not in SPECIES_LIST:
        species_resolved = "CERF"
    species = species_resolved

    max_salines = max(1, min(4, max_salines))

    # 1. Analyse territoriale
    terrain = analyze_terrain(center_lat, center_lng, side_m)

    # 2. Calcul salines optimales (OURS/DINDON: aucune saline)
    if species in SPECIES_NO_SALINES:
        salines = []
    else:
        salines = compute_salines(
            center_lat, center_lng, terrain, species, month, side_m,
            max_salines=max_salines, min_distance_m=300.0,
        )

    # BCE-4X-MAX: EXCLUSION ULTIME — filtrer salines en zone urbaine/eau
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            _circle_on_urban, _circle_on_water,
        )
        _pre_count = len(salines)
        salines = [s for s in salines if not _circle_on_urban(s["lat"], s["lng"]) and not _circle_on_water(s["lat"], s["lng"])]
        _excluded = _pre_count - len(salines)
        if _excluded > 0:
            import logging
            logging.getLogger("alimentation_v2").info(
                f"[BCE-4X-MAX] Salines exclusion: input={_pre_count}, excluded={_excluded}, kept={len(salines)}"
            )
        # Recalculer les ranks après exclusion
        for idx, s in enumerate(salines):
            if s.get("selected"):
                s["rank"] = idx + 1
    except ImportError:
        pass

    # 3. Recommandations nutritionnelles
    nutrition = get_nutrition(species)

    # 4. Score global alimentation V2
    selected_salines = [s for s in salines if s.get("selected")]
    terrain_score = (
        terrain["alimentaire"]["score_disponibilite"] * 40 +
        terrain["eau"]["score_hydrique"] * 20 +
        (terrain["foret"]["couvert_pct"] / 100) * 20 +
        (1 - terrain["relief"]["pente_moyenne_pct"] / 30) * 20
    )
    avg_saline_score = sum(s["score"] for s in selected_salines) / len(selected_salines) if selected_salines else 0
    score_global = round(terrain_score * 0.6 + avg_saline_score * 0.4)

    # 5. Carences détectées
    nutriments_sol = terrain["nutriments_sol"]
    carences_detectees = []
    seuils = {"selenium_ppm": (0.2, "Sélénium"), "cuivre_ppm": (3, "Cuivre"),
              "calcium_ppm": (500, "Calcium"), "phosphore_ppm": (10, "Phosphore"),
              "zinc_ppm": (5, "Zinc")}
    for key, (seuil, nom) in seuils.items():
        val = nutriments_sol.get(key, seuil)
        if val < seuil:
            carences_detectees.append({
                "element": nom,
                "valeur_sol": val,
                "seuil_minimum": seuil,
                "deficit_pct": round((1 - val / seuil) * 100),
            })

    result = {
        "version": "ALIMENTATION-V2",
        "species": species,
        "species_nom": nutrition["nom"],
        "month": month,
        "score_global": min(100, max(0, score_global)),
        "terrain": terrain,
        "salines": salines,
        "n_salines": len(selected_salines),
        "n_candidates": len(salines),
        "max_salines": max_salines,
        "salines_disabled": species in SPECIES_NO_SALINES,
        "salines_message": SPECIES_NO_SALINES_MESSAGES.get(species),
        "nutrition": {
            "aliments_recommandes": nutrition["aliments_recommandes"],
            "nutriments_essentiels": nutrition["nutriments_essentiels"],
            "proteines": nutrition["proteines"],
            "oligo_elements": nutrition["oligo_elements"],
            "carences_locales": nutrition["carences_locales_quebec"],
            "saline_composition": nutrition.get("saline_composition"),
        },
        "carences_detectees": carences_detectees,
        "conformite": {
            "bce4x": True,
            "steeve_max": True,
            "zones_modifiees": 0,
            "centres_modifies": 0,
        },
    }

    return result


# ═══════════════════════════════════════════════════════════════
# x3300: Fonction de scoring consolidé par point
# Logique relocalisée depuis modules/score_consolide.py (ex-PROXY)
# BCE-4X: Code IDENTIQUE, ZERO changement fonctionnel
# Hash: variante C (5 decimales) — preservee pour compatibilite
# ═══════════════════════════════════════════════════════════════

from core.scoring_pipeline.common.hash import deterministic_hash_c as _seed_c


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    """
    Score alimentaire V2 pour un point unique (scoring consolide).
    Logique d'origine: modules/score_consolide._alimentation_v2_score_for_point()
    Relocalisee dans le moteur CORE conformement a x3300.
    """
    if species.upper() in ("OURS", "DINDON"):
        return 30.0

    eau = _seed_c(lat, lng, "alim_eau") * 0.6 + 0.3
    couvert = _seed_c(lat, lng, "alim_couvert")
    nutriments = _seed_c(lat, lng, f"alim_nut_{species}")
    return max(0, min(100, eau * 30 + couvert * 35 + nutriments * 35))
