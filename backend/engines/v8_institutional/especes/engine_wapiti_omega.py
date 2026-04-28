"""
engine_wapiti_omega.py — ENGINE-ESPECE-WAPITI-Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω
═══════════════════════════════════════════════════════════════════════
Tableau Maître : TABLEAU_MAITRE_WAPITI_BCE4X.

Seuils scientifiques :
- Stress thermique : 20-25°C (multi-sources)
- Tolérance neige : > 40-60 cm
- DOI clé : 10.1002/jwmg.1030 (Proffitt et al. 2016 — RSF, GPS, corridors)
- DOI clé : 10.1002/eap.1923 (Montgomery et al. 2019 — disturbance multi-échelles)
- DOI clé : 10.7589/2015-07-178 (Miller & Fischer 2016 — CWD)

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


PROFILE_WAPITI_Ω = EspeceProfile(
    espece_id="WAPITI",
    nom_scientifique="Cervus canadensis",
    tableau_maitre_ref="TABLEAU_MAITRE_WAPITI_BCE4X",
    sources=[
        SourceRef("Parcs Canada", "GOV", "Elk Population Monitoring Report — Mountain National Parks",
                  2022, "https://parks.canada.ca", "Inventaires aériens, télémétrie"),
        SourceRef("Alberta Environment & Parks", "GOV", "Elk Management and Harvest Summary", 2021,
                  "https://www.alberta.ca", "Inventaires séries temporelles"),
        SourceRef("Kentucky DFWR", "GOV", "Elk Restoration and Population Status Report", 2020,
                  "https://fw.ky.gov", "GPS, inventaires"),
        SourceRef("MFFP Québec", "GOV", "Suivi cervidés", 2024,
                  "https://mffp.gouv.qc.ca", "Inventaires"),
        SourceRef("Journal of Wildlife Management (Proffitt et al.)", "UNI",
                  "Elk resource selection and migration in a changing landscape", 2016,
                  "https://doi.org/10.1002/jwmg.1030", "RSF, GPS"),
        SourceRef("Ecological Applications (Montgomery et al.)", "UNI",
                  "Elk responses to human disturbance across multiple spatial scales", 2019,
                  "https://doi.org/10.1002/eap.1923", "GPS multi-échelles"),
        SourceRef("Journal of Wildlife Diseases (Miller & Fischer)", "UNI",
                  "The epidemiology of chronic wasting disease in North America", 2016,
                  "https://doi.org/10.7589/2015-07-178", "Épidémiologie CWD"),
        SourceRef("Rocky Mountain Elk Foundation (RMEF)", "PR",
                  "Elk Habitat and Migration Corridor Analysis", 2024,
                  "https://www.rmef.org", "GPS, SIG, analyses habitat"),
    ],
    seuils=[
        SeuilScientifique("thermique_stress", 22.5, "°C", "stress",
                          "Multi-UNI", "Stress thermique 20-25°C — pentes nord requises"),
        SeuilScientifique("neige_mortalite", 50.0, "cm", "mortality",
                          "NOAA + GOV", "Mortalité hivers rigoureux >40-60cm"),
        SeuilScientifique("cwd_threshold", 5.0, "%", "stress",
                          "JWD 2016", "Seuil prévalence CWD = risque élevé"),
        SeuilScientifique("connectivity_optimum", 0.7, "ratio", "selection_optimum",
                          "Proffitt 2016", "Connectivité optimale corridors migratoires"),
    ],
    dimensions_scientifiques=[
        "corridors_migratoires", "mosaiques_prairie_foret", "dynamique_populationnelle",
        "nutrition_saisonniere", "pression_humaine_multi_echelles", "maladies_CWD",
        "exigences_thermiques", "tolerance_neige", "sites_rut_mise_bas",
    ],
    sorties_territoire=[
        "CORRIDORS_MIGRATOIRES_WAPITI", "HABITAT_PRAIRIE_FORET_WAPITI",
        "ZONES_RISQUE_CWD_WAPITI", "SCORE_PRESSION_HUMAINE_WAPITI",
        "SCORE_CONNECTIVITE_WAPITI",
    ],
    style_palette={
        "habitat":   "polygone_or_prairie_semi_transp",
        "corridors": "ligne_veineuse_or_3px_halo",
        "critiques": "hachures_orange",
        "color_primary": "#d97706",
        "color_corridor": "#f59e0b",
        "color_critique": "#7c2d12",
        "fill_opacity": 0.35,
    },
)


def compute(env: Dict[str, Any]) -> Dict[str, Any]:
    p = PROFILE_WAPITI_Ω
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
    cwd_prevalence = env.get("cwd_prevalence_pct", 0.0)
    score_cwd = round(min(cwd_prevalence * 12.0, 100.0), 2)
    # Connectivité (Proffitt 2016)
    connectivity_idx = env.get("connectivity_index", 0.5)  # 0-1
    score_connectivite = round(connectivity_idx * 100.0, 2)
    score_pression_multi = round(min(score_pression * 0.5 + score_fragmentation * 0.5, 100.0), 2)

    layers = {
        "CORRIDORS_MIGRATOIRES_WAPITI": {
            "criteria": "corridors migratoires stables prairie-forêt-altitude",
            "connectivity_score": score_connectivite,
            "fragmentation_penalty": score_fragmentation,
        },
        "HABITAT_PRAIRIE_FORET_WAPITI": {
            "criteria": "mosaïques prairie/forêt + vallées fluviales + transition",
            "habitat_quality": round(100.0 - score_pression_multi * 0.5, 2),
        },
        "ZONES_RISQUE_CWD_WAPITI": {
            "criteria": "prévalence CWD locale + densité élevée + chevauchement cervidés",
            "cwd_risk_score": score_cwd,
        },
        "SCORE_PRESSION_HUMAINE_WAPITI": score_pression_multi,
        "SCORE_CONNECTIVITE_WAPITI": score_connectivite,
    }
    scores = {
        "score_thermique": score_thermique,
        "score_neige_mortalite": score_neige,
        "score_pression_humaine_multi_echelles": score_pression_multi,
        "score_fragmentation": score_fragmentation,
        "score_cwd": score_cwd,
        "score_connectivite": score_connectivite,
    }
    return normalize_engine_output(p, layers, scores)
