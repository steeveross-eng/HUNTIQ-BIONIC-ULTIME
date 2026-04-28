"""
engine_chevreuil_omega.py — ENGINE-ESPECE-CHEVREUIL-Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω
═══════════════════════════════════════════════════════════════════════
Sources triple validation (GOV+UNI+PR), DOI obligatoire.
Tableau Maître : TABLEAU_MAITRE_CHEVREUIL_BCE4X.

Seuils scientifiques :
- Stress thermique : 26-28°C (NOAA, UNI)
- Tolérance neige : > 40-50 cm (NOAA, GOV)
- DOI clé : 10.1371/journal.pone.0325656 (LaSharr et al. 2025, PLOS One)

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


PROFILE_CHEVREUIL_Ω = EspeceProfile(
    espece_id="CHEVREUIL",
    nom_scientifique="Odocoileus virginianus",
    tableau_maitre_ref="TABLEAU_MAITRE_CHEVREUIL_BCE4X",
    sources=[
        SourceRef("MFFP Québec", "GOV", "Plan de gestion du cerf de Virginie 2020-2027", 2023,
                  "https://mffp.gouv.qc.ca", "Inventaires aériens, analyses d'habitat"),
        SourceRef("Ontario MNRF", "GOV", "White-Tailed Deer Population and Harvest Summary", 2022,
                  "https://www.ontario.ca/page/ministry-natural-resources-and-forestry", "Inventaires, télémétrie"),
        SourceRef("Maine IFW", "GOV", "Maine White-Tailed Deer Assessment", 2021,
                  "https://www.maine.gov/ifw", "Inventaires, séries temporelles"),
        SourceRef("USGS", "GOV", "Movement Ecology (GPS) — White-Tailed Deer", 2024,
                  "https://www.usgs.gov", "GPS telemetry"),
        SourceRef("PLOS One (LaSharr et al.)", "UNI",
                  "Dispersal dynamics of white-tailed deer in human-altered landscapes and implications for disease risk",
                  2025, "https://doi.org/10.1371/journal.pone.0325656", "GPS, modèles de dispersion"),
        SourceRef("Springer Nature (Fulbright)", "UNI", "White-Tailed Deer (chapitre scientifique)", 2023,
                  "https://link.springer.com", "Synthèse scientifique"),
        SourceRef("Wiley Online Library", "UNI",
                  "Development of high-throughput genomic resources to inform white-tailed deer management",
                  2024, "https://onlinelibrary.wiley.com", "Génomique"),
        SourceRef("National Deer Association (NDA)", "PR", "Annual Deer Report", 2024,
                  "https://deerassociation.com", "Données terrain validées"),
    ],
    seuils=[
        SeuilScientifique("thermique_stress", 27.0, "°C", "stress",
                          "NOAA + UNI", "Stress thermique 26-28°C — NOAA + Springer 2023"),
        SeuilScientifique("neige_mortalite", 45.0, "cm", "mortality",
                          "NOAA + MFFP", "Mortalité accrue >40-50 cm — NOAA + GOV"),
        SeuilScientifique("rsf_optimum", 0.65, "ratio", "selection_optimum",
                          "PLOS One 2025", "RSF optima mosaïques feuillus/conifères"),
    ],
    dimensions_scientifiques=[
        "comportements_saisonniers", "corridors_deplacement", "zones_ecologiques",
        "nutrition_avancee", "interactions_inter_especes", "pression_humaine",
        "exigences_thermiques", "tolerance_neige", "sites_critiques", "tendances_longues",
    ],
    sorties_territoire=[
        "HABITAT_OPTIMAL_CHEVREUIL", "CORRIDORS_CHEVREUIL", "ZONES_CRITIQUES_CHEVREUIL",
        "SCORE_PRESSION_HUMAINE_CHEVREUIL", "SCORE_FRAGMENTATION_CHEVREUIL",
    ],
    style_palette={
        "habitat":   "polygone_vert_thermique_semi_transp",
        "corridors": "ligne_veineuse_vert_3px_halo",
        "critiques": "hachures_vert_fonce",
        "color_primary": "#16a34a",
        "color_corridor": "#16a34a",
        "color_critique": "#0f5132",
        "fill_opacity": 0.35,
    },
)


def compute(env: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule les couches Ω + scores pour le chevreuil sur l'environnement fourni.

    env attendu :
      - temperature_c (float)
      - snow_depth_cm (float)
      - routes_density (float, km/km²)
      - urbanisation_pct (float)
      - agriculture_pct (float)
      - forest_patches_count (int)
      - largest_patch_index (float, 0-100)
      - edge_density (float, m/ha)
    """
    p = PROFILE_CHEVREUIL_Ω
    seuil_t = next(s for s in p.seuils if s.metric == "thermique_stress").valeur
    seuil_n = next(s for s in p.seuils if s.metric == "neige_mortalite").valeur

    score_thermique = compute_score_thermique(env.get("temperature_c", 0.0), seuil_t)
    score_neige = compute_score_neige(env.get("snow_depth_cm", 0.0), seuil_n)
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
    score_cwd_risk = round(min((score_pression * 0.6 + score_fragmentation * 0.4), 100.0), 2)

    layers = {
        "HABITAT_OPTIMAL_CHEVREUIL": {
            "criteria": "mosaïques feuillus/conifères + clairières + forêts matures",
            "rsf_threshold": 0.55, "habitat_quality_score": round(100.0 - score_pression * 0.5, 2),
        },
        "CORRIDORS_CHEVREUIL": {
            "criteria": "stables repos↔alimentation, dispersion juvénile mâles",
            "fragmentation_penalty": score_fragmentation,
        },
        "ZONES_CRITIQUES_CHEVREUIL": {
            "criteria": "mise bas (zones isolées), rut (clairières), repos (forêts matures)",
            "thermal_refuge_required": score_thermique > 30.0,
        },
        "SCORE_PRESSION_HUMAINE_CHEVREUIL": score_pression,
        "SCORE_FRAGMENTATION_CHEVREUIL": score_fragmentation,
    }
    scores = {
        "score_thermique": score_thermique,
        "score_neige_mortalite": score_neige,
        "score_pression_humaine": score_pression,
        "score_fragmentation": score_fragmentation,
        "score_cwd_risk": score_cwd_risk,
    }
    return normalize_engine_output(p, layers, scores)
