"""
engine_ours_noir_omega.py — ENGINE-ESPECE-OURS-NOIR-Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω
═══════════════════════════════════════════════════════════════════════
Tableau Maître : TABLEAU_MAITRE_OURS_NOIR_BCE4X.

DOI clés :
- 10.1002/jwmg.1032 (JWM — habitat, déplacements, corridors)
- 10.1111/1365-2664.12279 (J. Applied Ecology — pression humaine, conflits)
- 10.1002/jwmg.890 (JWM — reproduction, dynamique populationnelle)

LECTURE SEULE V30.
═══════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict
from . import (
    EspeceProfile, SourceRef, SeuilScientifique,
    compute_score_pression_humaine, compute_score_fragmentation,
    compute_score_thermique, compute_score_neige, normalize_engine_output,
)


PROFILE_OURS_NOIR_Ω = EspeceProfile(
    espece_id="OURS_NOIR",
    nom_scientifique="Ursus americanus",
    tableau_maitre_ref="TABLEAU_MAITRE_OURS_NOIR_BCE4X",
    sources=[
        SourceRef("MFFP Québec", "GOV", "Suivi ours noir, densité, conflits", 2024,
                  "https://mffp.gouv.qc.ca", "Inventaires"),
        SourceRef("Ontario MNRF", "GOV", "Black Bear Management — quotas, mortalité", 2024,
                  "https://www.ontario.ca", "Plans gestion"),
        SourceRef("NB DNR", "GOV", "Black Bear Population Trends", 2024,
                  "https://www2.gnb.ca", "Tendances climat"),
        SourceRef("State Wildlife Agencies (ME, VT, NH)", "GOV", "Tendances, reproduction, conflits",
                  2024, None, "Inventaires multi-états"),
        SourceRef("USGS", "GOV", "Black bear movement/telemetry", 2024,
                  "https://www.usgs.gov", "GPS"),
        SourceRef("USFWS", "GOV", "Habitat & population assessments", 2024,
                  "https://www.fws.gov", "Statut conservation"),
        SourceRef("Journal of Wildlife Management", "UNI",
                  "Black bear habitat, movements, corridors", 2018,
                  "https://doi.org/10.1002/jwmg.1032", "RSF, SSF, GPS"),
        SourceRef("Journal of Applied Ecology", "UNI",
                  "Human-bear conflicts and anthropogenic resources", 2014,
                  "https://doi.org/10.1111/1365-2664.12279",
                  "Analyses statistiques conflits"),
        SourceRef("Journal of Wildlife Management", "UNI",
                  "Reproduction, survie, dynamique populationnelle Ursus americanus", 2015,
                  "https://doi.org/10.1002/jwmg.890", "Suivi long terme"),
        SourceRef("BearWise", "PR", "Habitat, conflits, prévention", 2024,
                  "https://bearwise.org", "Programmes prévention"),
        SourceRef("Programmes régionaux télémétrie", "PR", "Colliers GPS ours noir", 2024,
                  None, "GPS terrain"),
    ],
    seuils=[
        SeuilScientifique("attractifs_humains_min", 30.0, "%", "stress",
                          "JAE 2014", "Disponibilité alimentaire anthropogénique"),
        SeuilScientifique("hyperphagie_automnale", 70.0, "%", "selection_optimum",
                          "JWM 2015", "Hyperphagie pré-hibernation"),
        SeuilScientifique("denning_isolation", 500.0, "m", "selection_optimum",
                          "JWM 2018", "Distance min routes pour tanières"),
    ],
    dimensions_scientifiques=[
        "deplacements_saisonniers", "corridors_forestiers", "zones_regeneration",
        "nutrition_saisonniere_baies_mast", "conflits_ours_humains", "pression_humaine",
        "tanieres", "reproduction_survie_jeunes", "tendances_longues",
    ],
    sorties_territoire=[
        "HABITAT_OURS_NOIR", "CORRIDORS_OURS_NOIR", "ZONES_CONFLITS_OURS_HUMAINS",
        "SCORE_ATTRACTIFS_ANTHROPIQUES", "SCORE_FRAGMENTATION_OURS_NOIR",
    ],
    style_palette={
        "habitat":   "polygone_gris_foret_semi_transp",
        "corridors": "ligne_veineuse_gris_3px_halo",
        "critiques": "hachures_noir",
        "color_primary": "#475569",
        "color_corridor": "#64748b",
        "color_critique": "#0f172a",
        "fill_opacity": 0.32,
    },
)


def compute(env: Dict[str, Any]) -> Dict[str, Any]:
    p = PROFILE_OURS_NOIR_Ω
    score_pression = compute_score_pression_humaine(
        env.get("routes_density", 0.0),
        env.get("urbanisation_pct", 0.0),
        env.get("agriculture_pct", 0.0),
    )
    score_fragmentation = compute_score_fragmentation(
        env.get("forest_patches_count", 0),
        env.get("largest_patch_index", 100.0),
        env.get("edge_density", 0.0),
    )
    # Score attractifs anthropiques (DOI 10.1111/1365-2664.12279)
    waste_proximity_pct = env.get("waste_proximity_pct", 0.0)
    crops_attractive_pct = env.get("crops_attractive_pct", 0.0)
    score_attractifs = round(min(waste_proximity_pct * 0.6 + crops_attractive_pct * 0.4, 100.0), 2)
    score_conflits = round(min(score_attractifs * 0.7 + score_pression * 0.3, 100.0), 2)
    # Disponibilité mast/baies (hyperphagie automnale)
    mast_index = env.get("mast_availability_index", 50.0)  # 0-100
    score_nutrition_automne = round(min(mast_index, 100.0), 2)

    layers = {
        "HABITAT_OURS_NOIR": {
            "criteria": "forêts mixtes + régénération + milieux humides + pentes abritées",
            "habitat_quality": round(100.0 - score_pression * 0.4, 2),
            "denning_potential": round(100.0 - score_fragmentation * 0.5, 2),
        },
        "CORRIDORS_OURS_NOIR": {
            "criteria": "corridors forestiers stables, évitement urbanisation",
            "fragmentation_penalty": score_fragmentation,
        },
        "ZONES_CONFLITS_OURS_HUMAINS": {
            "criteria": "proximité résidences + attractifs alimentaires + agriculture",
            "conflict_risk_score": score_conflits,
        },
        "SCORE_ATTRACTIFS_ANTHROPIQUES": score_attractifs,
        "SCORE_FRAGMENTATION_OURS_NOIR": score_fragmentation,
    }
    scores = {
        "score_pression_humaine": score_pression,
        "score_fragmentation": score_fragmentation,
        "score_attractifs_anthropiques": score_attractifs,
        "score_conflits_humains": score_conflits,
        "score_nutrition_automne_mast": score_nutrition_automne,
    }
    return normalize_engine_output(p, layers, scores)
