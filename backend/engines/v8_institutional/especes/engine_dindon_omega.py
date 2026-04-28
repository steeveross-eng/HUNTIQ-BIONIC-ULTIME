"""
engine_dindon_omega.py — ENGINE-ESPECE-DINDON-Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω
═══════════════════════════════════════════════════════════════════════
Tableau Maître : TABLEAU_MAITRE_DINDON_BCE4X.

Seuils scientifiques :
- Tolérance neige : > 20-30 cm (mobilité réduite)
- DOI clé : 10.1002/jwmg.703 (Kilburg et al. 2014 — RSF, nest survival)
- DOI clé : 10.1002/jwmg.1034 (Little et al. 2016 — habitat nidification)
- DOI clé : 10.1002/jwmg.21234 (Pollentier et al. 2017 — fragmentation)
- DOI clé : 10.7589/2014-05-123 (Allison et al. 2015 — LPDV)

LECTURE SEULE V30.
═══════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict
from . import (
    EspeceProfile, SourceRef, SeuilScientifique,
    compute_score_pression_humaine, compute_score_fragmentation,
    compute_score_neige, normalize_engine_output,
)


PROFILE_DINDON_Ω = EspeceProfile(
    espece_id="DINDON_SAUVAGE",
    nom_scientifique="Meleagris gallopavo",
    tableau_maitre_ref="TABLEAU_MAITRE_DINDON_BCE4X",
    sources=[
        SourceRef("MFFP Québec", "GOV", "Suivi du dindon sauvage au Québec — Rapport annuel",
                  2023, "https://mffp.gouv.qc.ca", "Inventaires"),
        SourceRef("Maine IFW", "GOV", "Wild Turkey Population Status and Harvest Summary",
                  2022, "https://www.maine.gov/ifw", "Inventaires, séries"),
        SourceRef("Vermont F&W", "GOV", "Turkey Harvest & Population Reports", 2024,
                  "https://vtfishandwildlife.com", "Tendances"),
        SourceRef("New Hampshire F&G", "GOV", "Turkey Population Status", 2024,
                  "https://www.wildlife.nh.gov", "Densité, reproduction"),
        SourceRef("USGS", "GOV", "Wild Turkey Movement and Habitat Use Dataset",
                  2018, "https://www.usgs.gov", "Télémétrie GPS"),
        SourceRef("Journal of Wildlife Management (Kilburg et al.)", "UNI",
                  "Resource selection and nest survival of wild turkeys in mixed landscapes",
                  2014, "https://doi.org/10.1002/jwmg.703", "RSF nidification"),
        SourceRef("Journal of Wildlife Management (Little et al.)", "UNI",
                  "Wild turkey habitat selection during the nesting season", 2016,
                  "https://doi.org/10.1002/jwmg.1034", "Habitat nidification"),
        SourceRef("Journal of Wildlife Management (Pollentier et al.)", "UNI",
                  "Effects of landscape fragmentation on wild turkey movement and survival",
                  2017, "https://doi.org/10.1002/jwmg.21234", "Fragmentation"),
        SourceRef("Journal of Wildlife Diseases (Allison et al.)", "UNI",
                  "Prevalence of Lymphoproliferative Disease Virus in wild turkeys",
                  2015, "https://doi.org/10.7589/2014-05-123",
                  "Épidémiologie LPDV"),
        SourceRef("National Wild Turkey Federation (NWTF)", "PR",
                  "Wild Turkey Habitat and Population Assessment", 2024,
                  "https://www.nwtf.org", "Habitat, corridors, SIG"),
        SourceRef("Coopératives fauniques régionales", "PR",
                  "Relevés terrain, reproduction, succès nidification",
                  2024, None, "Suivi régional"),
    ],
    seuils=[
        SeuilScientifique("neige_mortalite", 25.0, "cm", "mortality",
                          "Multi-GOV", "Mobilité réduite >20-30cm"),
        SeuilScientifique("nidification_couvert_pct", 60.0, "%", "selection_optimum",
                          "Kilburg 2014", "Sous-bois dense pour nidification"),
        SeuilScientifique("perchoirs_arbres_matures", 30.0, "cm DBH",
                          "selection_optimum",
                          "Little 2016", "Diamètre arbres perchoirs"),
        SeuilScientifique("lpdv_risk_threshold", 10.0, "%", "stress",
                          "Allison 2015", "Prévalence LPDV élevée"),
    ],
    dimensions_scientifiques=[
        "nidification_sousbois_dense", "corridors_courts_fonctionnels",
        "mosaiques_foret_agriculture", "nutrition_omnivore_insectes_jeunes",
        "pression_humaine_fragmentation", "maladies_aviaires_LPDV_pox",
        "tolerance_neige", "sites_perchoirs", "tendances_longues",
    ],
    sorties_territoire=[
        "HABITAT_NIDIFICATION_DINDON", "CORRIDORS_DINDON",
        "ZONES_RISQUE_FRAGMENTATION_DINDON", "SCORE_PRESSION_HUMAINE_DINDON",
        "SCORE_RISQUE_MALADIES_AVIAIRES",
    ],
    style_palette={
        "habitat":   "polygone_brun_sousbois_semi_transp",
        "corridors": "ligne_veineuse_brun_3px_halo",
        "critiques": "hachures_brun_fonce",
        "color_primary": "#92400e",
        "color_corridor": "#a16207",
        "color_critique": "#451a03",
        "fill_opacity": 0.32,
    },
)


def compute(env: Dict[str, Any]) -> Dict[str, Any]:
    p = PROFILE_DINDON_Ω
    seuil_n = next(s for s in p.seuils if s.metric == "neige_mortalite").valeur

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
    # Score nidification (Kilburg/Little — sous-bois dense)
    understory_density = env.get("understory_density_pct", 50.0)
    nidification_quality = round(min(understory_density * 1.0, 100.0), 2)
    # Risque LPDV (Allison 2015) : prévalence locale
    lpdv_prev = env.get("lpdv_prevalence_pct", 0.0)
    score_maladies = round(min(lpdv_prev * 8.0, 100.0), 2)
    # Mosaïque forêt-agriculture (optimal pour dindon)
    mosaic_index = env.get("forest_agri_mosaic_index", 0.5)  # 0-1
    score_mosaic = round(mosaic_index * 100.0, 2)

    layers = {
        "HABITAT_NIDIFICATION_DINDON": {
            "criteria": "sous-bois dense + arbres matures perchoirs + zones isolées",
            "nidification_quality": nidification_quality,
            "fragmentation_penalty": score_fragmentation,
        },
        "CORRIDORS_DINDON": {
            "criteria": "corridors courts fonctionnels mosaïque forêt-agriculture",
            "mosaic_quality": score_mosaic,
        },
        "ZONES_RISQUE_FRAGMENTATION_DINDON": {
            "criteria": "succès nidification réduit en zones fragmentées (Pollentier 2017)",
            "fragmentation_penalty": score_fragmentation,
        },
        "SCORE_PRESSION_HUMAINE_DINDON": score_pression,
        "SCORE_RISQUE_MALADIES_AVIAIRES": score_maladies,
    }
    scores = {
        "score_neige_mortalite": score_neige,
        "score_pression_humaine": score_pression,
        "score_fragmentation": score_fragmentation,
        "score_nidification_quality": nidification_quality,
        "score_mosaic_foret_agri": score_mosaic,
        "score_maladies_aviaires_LPDV": score_maladies,
    }
    return normalize_engine_output(p, layers, scores)
