"""
engine_orignal_omega.py — ENGINE-ESPECE-ORIGNAL-Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω
═══════════════════════════════════════════════════════════════════════
Tableau Maître : TABLEAU_MAITRE_ORIGNAL_BCE4X.

Seuils scientifiques :
- Stress thermique : 14-17°C (Ecological Applications, Ericsson)
- Tolérance neige : > 60-70 cm (NOAA, Parcs Canada)
- DOI clé : 10.3389/fevo.2021.758374 (Frontiers — Tique d'hiver)
- DOI clé : 10.1002/ece3.10909 (Wiley — Pression humaine/routes)

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


PROFILE_ORIGNAL_Ω = EspeceProfile(
    espece_id="ORIGNAL",
    nom_scientifique="Alces alces / Alces americanus",
    tableau_maitre_ref="TABLEAU_MAITRE_ORIGNAL_BCE4X",
    sources=[
        SourceRef("MFFP Québec", "GOV", "Inventaires orignal, plans de gestion, rapports ravage", 2024,
                  "https://mffp.gouv.qc.ca", "Inventaires aériens, télémétrie"),
        SourceRef("Ontario MNRF", "GOV", "Moose Management Reports", 2024,
                  "https://www.ontario.ca", "Plans de gestion"),
        SourceRef("NB DNR", "GOV", "Moose Population & Harvest Reports", 2024,
                  "https://www2.gnb.ca", "Tendances, succès chasse"),
        SourceRef("USGS", "GOV", "Animal movement / Moose telemetry", 2024,
                  "https://www.usgs.gov", "GPS telemetry"),
        SourceRef("Parcs Canada", "GOV", "Monitoring orignal", 2024,
                  "https://parks.canada.ca", "Aires protégées"),
        SourceRef("Frontiers in Ecology and Evolution", "UNI",
                  "Winter tick (Dermacentor albipictus) effects on moose populations",
                  2021, "https://doi.org/10.3389/fevo.2021.758374",
                  "Étude sur impact tique d'hiver"),
        SourceRef("Ecology and Evolution (Wiley)", "UNI",
                  "Anthropogenic pressure and moose habitat",
                  2023, "https://doi.org/10.1002/ece3.10909",
                  "Routes, exploitation forestière"),
        SourceRef("Canadian Journal of Forest Research", "UNI",
                  "Habitat & forêt — gestion orignal", 2020,
                  "https://doi.org/10.1139/cjfr-2020", "Habitat, forêt"),
        SourceRef("ALCES Journal", "UNI", "Articles peer-reviewed habitat/déplacements/nutrition/climat",
                  2020, "https://alces.ca", "Articles spécialisés"),
        SourceRef("RMEF / partenaires régionaux", "PR", "Analyses habitat / corridors orignal-wapiti",
                  2024, "https://www.rmef.org", "Analyses connectivité"),
        SourceRef("Coopératives fauniques régionales", "PR", "Relevés terrain mortalité, condition corporelle",
                  2024, None, "Suivi terrain"),
    ],
    seuils=[
        SeuilScientifique("thermique_stress", 15.5, "°C", "stress",
                          "Ericsson UNI", "Stress thermique 14-17°C, ECO Applications"),
        SeuilScientifique("neige_mortalite", 65.0, "cm", "mortality",
                          "NOAA + Parcs Canada", "Mortalité hivers longs >60-70cm"),
        SeuilScientifique("tique_risque", 0.5, "ratio", "stress",
                          "Frontiers 2021", "Risque tique = f(été chaud, prédation)"),
    ],
    dimensions_scientifiques=[
        "thermoregulation", "corridors_continus", "zones_humides", "ravages_hivernaux",
        "pression_humaine", "maladies_parasites_tique_hiver", "tolerance_neige",
        "sites_mise_bas", "tendances_populationnelles",
    ],
    sorties_territoire=[
        "HABITAT_THERMIQUE_ORIGNAL", "CORRIDORS_ORIGNAL", "RAVAGES_ORIGNAL",
        "SCORE_RISQUE_TIQUE_ORIGNAL", "SCORE_FRAGMENTATION_ORIGNAL",
    ],
    style_palette={
        "habitat":   "polygone_bleu_froid_semi_transp",
        "corridors": "ligne_veineuse_bleu_3px_halo",
        "critiques": "hachures_bleu_fonce",
        "color_primary": "#1d4ed8",
        "color_corridor": "#2563eb",
        "color_critique": "#1e3a8a",
        "fill_opacity": 0.35,
    },
)


def compute(env: Dict[str, Any]) -> Dict[str, Any]:
    p = PROFILE_ORIGNAL_Ω
    seuil_t = next(s for s in p.seuils if s.metric == "thermique_stress").valeur
    seuil_n = next(s for s in p.seuils if s.metric == "neige_mortalite").valeur

    temperature_c = env.get("temperature_c", 0.0)
    score_thermique = compute_score_thermique(temperature_c, seuil_t)
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
    # Risque tique (Frontiers 2021) : été chaud + prédation faible = risque élevé
    summer_temp = env.get("summer_avg_temp_c", temperature_c)
    pred_index = env.get("predation_index", 0.5)  # 0-1 (1=fort)
    score_tique = round(min(max((summer_temp - 14.0) * 8.0 + (1.0 - pred_index) * 30.0, 0.0), 100.0), 2)

    layers = {
        "HABITAT_THERMIQUE_ORIGNAL": {
            "criteria": "forêts mixtes boréales, zones humides (été), forêts matures conifères (hiver)",
            "thermal_refuge_required": score_thermique > 25.0,
        },
        "CORRIDORS_ORIGNAL": {
            "criteria": "corridors continus stables (USGS GPS), évitement routes",
            "fragmentation_penalty": score_fragmentation,
        },
        "RAVAGES_ORIGNAL": {
            "criteria": "couverture conifères dense + neige < 65cm",
            "ravage_quality": round(100.0 - score_neige * 0.5, 2),
        },
        "SCORE_RISQUE_TIQUE_ORIGNAL": score_tique,
        "SCORE_FRAGMENTATION_ORIGNAL": score_fragmentation,
    }
    scores = {
        "score_thermique": score_thermique,
        "score_neige_mortalite": score_neige,
        "score_pression_humaine": score_pression,
        "score_fragmentation": score_fragmentation,
        "score_risque_tique": score_tique,
    }
    return normalize_engine_output(p, layers, scores)
