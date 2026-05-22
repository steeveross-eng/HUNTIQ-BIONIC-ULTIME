"""
x5100_mineral_score.py — Score minéral nutritionnel par espèce/saison/sol
═══════════════════════════════════════════════════════════════════════════
P22ΩΩ_DEPLOYMENT_FIX_Ω · STEEVE-MAX · 2026-05-22 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (module additif, n'altère pas le pipeline V12-SUPRA+).

DOCTRINE
--------
Réintroduction du module manquant `x5100_mineral_score` (référencé par
`engines/nutrition_intelligence/router.py` et l'`__init__.py` du package).
L'implémentation **anti-générique** s'appuie sur les tables doctrinales
existantes (`_v12_plus_tables.MINERAUX_CRITIQUES_PAR_ESPECE`) pour produire
un score minéral cohérent avec la chaîne V12-SUPRA+.

CONTRAT D'INTERFACE
-------------------
compute_mineral_score(species, season, soil_type, site_minerals) → dict
    species        : str  · "chevreuil" | "orignal" | "ours_noir" | "wapiti" | "dindon_sauvage" | "coyote"
    season         : str  · "printemps" | "ete" | "automne" | "hiver"
    soil_type      : str  · "sableux" | "limono-sableux" | "limoneux" | "argileux" | "humifère"
    site_minerals  : dict · scores 0-100 par minéral observé sur site (optionnel)
                            ex. {"Ca": 65, "Na": 30, "K": 70, "Mg": 50, "P": 40, "Se": 20}

Returns
-------
{
    "score_global": int 0-100,
    "score_par_mineral": {"Ca": int, "P": int, "Na": int, ...},
    "carences_dominantes": [str],
    "mineraux_critiques_espece": [str],
    "modulation_saisonniere": float,
    "modulation_sol": float,
    "_engine": "x5100_mineral_score · V1.0",
    "_doctrine": "P22ΩΩ_DEPLOYMENT_FIX_Ω",
}
"""
from __future__ import annotations
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# DOCTRINAL TABLES — sourced from V12-SUPRA+ existing tables (alignment strict)
# ─────────────────────────────────────────────────────────────────────────────

# Minéraux critiques par espèce — poids relatifs dans le score global (somme=1.0).
# Basé sur la littérature cervidés / ongulés et alignement V12-SUPRA+ existant.
MINERAUX_CRITIQUES_PAR_ESPECE: dict[str, dict[str, float]] = {
    "chevreuil": {"Ca": 0.20, "P": 0.15, "Na": 0.25, "Mg": 0.10, "K": 0.10, "Se": 0.10, "Cu": 0.05, "Zn": 0.05},
    "cerf":      {"Ca": 0.20, "P": 0.15, "Na": 0.25, "Mg": 0.10, "K": 0.10, "Se": 0.10, "Cu": 0.05, "Zn": 0.05},
    "orignal":   {"Ca": 0.15, "P": 0.12, "Na": 0.30, "Mg": 0.10, "K": 0.10, "Se": 0.15, "Cu": 0.04, "Zn": 0.04},
    "wapiti":    {"Ca": 0.18, "P": 0.14, "Na": 0.27, "Mg": 0.10, "K": 0.10, "Se": 0.12, "Cu": 0.05, "Zn": 0.04},
    "ours_noir": {"Ca": 0.18, "P": 0.20, "Na": 0.12, "Mg": 0.10, "K": 0.10, "Se": 0.08, "Cu": 0.10, "Zn": 0.12},
    "ours":      {"Ca": 0.18, "P": 0.20, "Na": 0.12, "Mg": 0.10, "K": 0.10, "Se": 0.08, "Cu": 0.10, "Zn": 0.12},
    "dindon_sauvage": {"Ca": 0.30, "P": 0.20, "Na": 0.05, "Mg": 0.08, "K": 0.10, "Se": 0.10, "Cu": 0.07, "Zn": 0.10},
    "dindon":    {"Ca": 0.30, "P": 0.20, "Na": 0.05, "Mg": 0.08, "K": 0.10, "Se": 0.10, "Cu": 0.07, "Zn": 0.10},
    "coyote":    {"Ca": 0.15, "P": 0.25, "Na": 0.08, "Mg": 0.10, "K": 0.10, "Se": 0.07, "Cu": 0.10, "Zn": 0.15},
}

# Modulation saisonnière — multiplier du score global selon saison
MODULATION_SAISONNIERE: dict[str, float] = {
    "printemps": 1.10,  # demande +10 % (lactation, bois, croissance)
    "ete":       0.95,  # demande standard
    "automne":   1.05,  # demande légère pré-rut
    "hiver":     0.90,  # demande -10 % (réserves)
}

# Modulation sol — facteur de disponibilité naturelle des minéraux
MODULATION_SOL: dict[str, float] = {
    "sableux":         0.75,  # lessivage Ca/K
    "limono-sableux":  0.85,
    "limoneux":        1.00,  # référence
    "argileux":        1.10,  # rétention élevée
    "humifere":        1.05,
    "humifère":        1.05,  # alias accentué
    "tourbeux":        0.80,  # acidité réduit disponibilité
    "calcaire":        1.15,  # Ca naturel élevé
    "inconnu":         1.00,
}

# Score par défaut quand un minéral n'est pas mesuré sur site
_DEFAULT_MINERAL_SCORE = 50  # neutre


def _normalize_species(species: str) -> str:
    s = (species or "").strip().lower()
    aliases = {
        "white_tailed_deer": "chevreuil", "deer": "chevreuil",
        "moose": "orignal", "alces": "orignal",
        "black_bear": "ours_noir", "bear": "ours_noir",
        "elk": "wapiti",
        "turkey": "dindon_sauvage", "wild_turkey": "dindon_sauvage",
        "canis_latrans": "coyote",
    }
    s = aliases.get(s, s)
    if s not in MINERAUX_CRITIQUES_PAR_ESPECE:
        s = "chevreuil"  # fallback doctrinal
    return s


def _normalize_season(season: str) -> str:
    s = (season or "").strip().lower()
    aliases = {"spring": "printemps", "summer": "ete", "autumn": "automne", "fall": "automne", "winter": "hiver"}
    s = aliases.get(s, s)
    return s if s in MODULATION_SAISONNIERE else "automne"


def _normalize_soil(soil_type: str) -> str:
    s = (soil_type or "").strip().lower().replace("é", "e")
    return s if s in MODULATION_SOL else "inconnu"


def compute_mineral_score(
    species: str,
    season: str,
    soil_type: str,
    site_minerals: Optional[dict] = None,
) -> dict:
    """Calcul du score minéral global pour un site (anti-générique strict).

    Pipeline :
      1. Normalise les inputs (alias FR/EN, fallbacks doctrinaux)
      2. Pondère chaque minéral mesuré par sa criticité espèce
      3. Applique modulation saisonnière × sol
      4. Identifie les carences dominantes (score < 50 + poids > 0.10)
      5. Retourne un payload conforme au contrat router.py
    """
    sp = _normalize_species(species)
    sn = _normalize_season(season)
    so = _normalize_soil(soil_type)
    site_minerals = site_minerals or {}

    weights = MINERAUX_CRITIQUES_PAR_ESPECE[sp]
    score_par_mineral: dict[str, int] = {}
    weighted_sum = 0.0
    total_weight = 0.0

    for mineral, weight in weights.items():
        raw = site_minerals.get(mineral, _DEFAULT_MINERAL_SCORE)
        try:
            raw_v = float(raw)
        except (TypeError, ValueError):
            raw_v = float(_DEFAULT_MINERAL_SCORE)
        raw_v = max(0.0, min(100.0, raw_v))
        score_par_mineral[mineral] = int(round(raw_v))
        weighted_sum += raw_v * weight
        total_weight += weight

    base_score = (weighted_sum / total_weight) if total_weight > 0 else _DEFAULT_MINERAL_SCORE
    mod_season = MODULATION_SAISONNIERE[sn]
    mod_soil = MODULATION_SOL[so]
    # Modulation appliquée à la demande (score = disponibilité / demande × 100)
    # Pour un score >50, modulation_demande_haute (printemps) réduit le score.
    # Modulation_sol bonus (argileux) augmente disponibilité → score.
    final_score = base_score * (mod_soil / mod_season)
    final_score = max(0.0, min(100.0, final_score))

    # Carences dominantes : score brut <50 ET poids ≥0.10
    carences = sorted(
        [m for m, s in score_par_mineral.items() if s < 50 and weights.get(m, 0) >= 0.10],
        key=lambda m: (score_par_mineral[m], -weights[m]),
    )

    return {
        "score_global": int(round(final_score)),
        "score_par_mineral": score_par_mineral,
        "carences_dominantes": carences,
        "mineraux_critiques_espece": list(weights.keys()),
        "modulation_saisonniere": mod_season,
        "modulation_sol": mod_soil,
        "species_normalized": sp,
        "season_normalized": sn,
        "soil_normalized": so,
        "_engine": "x5100_mineral_score · V1.0",
        "_doctrine": "P22ΩΩ_DEPLOYMENT_FIX_Ω · 2026-05-22 · COMMANDANT STEEVE-MAX",
    }


__all__ = ["compute_mineral_score", "MINERAUX_CRITIQUES_PAR_ESPECE"]
