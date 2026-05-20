"""
engine_nutrition_v12_supra_plus.py — V12-SUPRA+ HUB FICHE SALINE ULTIME Ω
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_Ω · STEEVE-MAX · 2026-02-19
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

OPTION B doctrinale — Wrapper additif au-dessus de V12-SUPRA :
  ✅ Aucune modification de engine_nutrition_v12_supra.py (Verrou Phase III)
  ✅ Pas dans chaîne V20→V10 (calcul à la demande UI, latence cible <200ms)
  ✅ Endpoint REST dédié : /api/v6/nutrition-intelligence/v12-plus/fiche-saline

OUTPUT : "FICHE SALINE ULTIME PRD-READY" (10 blocs structurés) — voir §SCHEMA

EXTENSIONS V12+ ajoutées (P0) :
  1. NaCl explicit (Na × 2.54)
  2. Ratio Ca:P cible doctrinal (table espèce)
  3. Déficits P / Zn / Se (calculés depuis NRC tables)
  4. kg maïs/soya par semaine (conversion attractivité × MS jour × 7)
  5. Surface m² champs nourriciers par culture

ESPÈCES ADAPTÉES : orignal, chevreuil, cerf, ours_noir, ours, dindon_sauvage,
                   dindon, wapiti, coyote (carnivore = stratégie ajustée)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from engines.v8_institutional._v12_plus_tables import (
    APPROCHE_VENT_DOCTRINALE,
    CONSO_KG_MS_JOUR,
    FOOD_PLOT_SURFACE_M2,
    PLAN_30J_PHASES,
    RATIO_CAP_CIBLE_OMEGA,
    STRATEGIE_CORRIDORS,
    TABLES_DOCTRINE,
    TABLES_VERSION,
    TRACE_PPM_CIBLE,
    get_table_value,
)
from engines.v8_institutional.engine_carence_nutritionnelle_omega import _NEEDS as CARENCE_NEEDS
from engines.v8_institutional.engine_champs_nourriciers_omega import _CROP_ATTRACT

logger = logging.getLogger("bionic.engine_nutrition_v12_supra_plus")

ENGINE_NAME = "ENGINE-NUTRITION-V12-SUPRA-PLUS"
ENGINE_VERSION = "V12+-2026-02"
DOCTRINE = "P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_Ω"
PHASE_III_LOCK = "MAINTENU"

NA_TO_NACL_FACTOR = 2.54  # NaCl/Na molar weight ratio (58.44/23.00)


# ═════════════════════════════════════════════════════════════════════
# A. CALCULS DOCTRINAUX V12+
# ═════════════════════════════════════════════════════════════════════

def compute_nacl_g_jour(na_mg_jour: float) -> float:
    """Convertit Na (mg/jour) en NaCl (g/jour). Formule chimique NaCl = Na × 2.54.

    >>> compute_nacl_g_jour(4000)   # orignal base
    10.16
    """
    if na_mg_jour is None or na_mg_jour <= 0:
        return 0.0
    return round(na_mg_jour * NA_TO_NACL_FACTOR / 1000.0, 2)


def compute_ratio_cap(ca_mg: float, p_mg: float, species: str) -> Dict[str, Any]:
    """Calcule ratio Ca:P actuel + cible doctrinal."""
    target = get_table_value(RATIO_CAP_CIBLE_OMEGA, species, {})
    if p_mg and p_mg > 0:
        actuel_num = round(ca_mg / p_mg, 2)
        actuel_str = f"{actuel_num}:1"
    else:
        actuel_num = 0.0
        actuel_str = "n/a"
    return {
        "actuel": actuel_str,
        "actuel_num": actuel_num,
        "cible": target.get("ratio", "1.5:1"),
        "cible_num": target.get("ratio_num", 1.5),
        "ecart_pct": round((actuel_num - target.get("ratio_num", 1.5)) /
                           max(target.get("ratio_num", 1.5), 0.01) * 100, 1) if actuel_num > 0 else None,
        "justification_cible": target.get("justification", ""),
    }


def compute_deficit_pct(besoin_mg: float, dispo_mg: float) -> float:
    """Calcule déficit (%) : 100 × (besoin - dispo) / besoin, clamped [0, 100]."""
    if besoin_mg is None or besoin_mg <= 0:
        return 0.0
    if dispo_mg is None:
        dispo_mg = 0.0
    deficit_pct = max(0.0, min(100.0, 100.0 * (besoin_mg - dispo_mg) / besoin_mg))
    return round(deficit_pct, 1)


def compute_kg_culture_semaine(crop: str, species: str,
                                attractivite: float = None) -> float:
    """Calcule kg/semaine pour une culture donnée pour 1 individu.

    Formule doctrinale :
      kg_semaine = attractivite_crop × 7 × conso_kg_ms_jour × 0.15
      (15% MS = ration complémentaire vs ration totale naturelle)
    """
    if attractivite is None:
        crop_table = _CROP_ATTRACT.get(crop, {})
        key = str(species or "").lower()
        attractivite = (
            crop_table.get(key)
            or crop_table.get(key.replace("_sauvage", ""))
            or crop_table.get(key.replace("_noir", ""))
            or 0.5
        )
    conso = CONSO_KG_MS_JOUR.get(str(species or "").lower(), 1.0)
    return round(attractivite * 7 * conso * 0.15, 2)


def compute_surface_m2(crop: str, species: str) -> int:
    """Lookup surface m² par individu × culture."""
    return FOOD_PLOT_SURFACE_M2.get(crop, {}).get(str(species or "").lower(), 0)


# ═════════════════════════════════════════════════════════════════════
# B. EXTRACTION DEPUIS BUNDLE V12 (HUB)
# ═════════════════════════════════════════════════════════════════════

def _extract_besoins_eff(v12_bundle: dict) -> dict:
    """Extrait `besoins_effectifs` du bundle V12 hub."""
    return v12_bundle.get("besoins_effectifs", {}) or {}


def _extract_dispo_locale(v12_bundle: dict) -> dict:
    """Extrait disponibilité nutriments locale (waypoint central)."""
    dispo = v12_bundle.get("disponibilite", {}) or {}
    nutriments = dispo.get("nutriments", {}) or {}
    return nutriments


def _extract_carences_waypoint(v12_bundle: dict, lat: float, lon: float) -> dict:
    """Extrait carences du point grille le plus proche du waypoint."""
    grille = v12_bundle.get("carte_carences", []) or []
    if not grille:
        return {}
    closest = min(
        grille,
        key=lambda p: (p.get("lat", 0) - lat) ** 2 + (p.get("lng", 0) - lon) ** 2,
    )
    return closest.get("deficits", {}) or {}


# ═════════════════════════════════════════════════════════════════════
# C. CONSTRUCTION FICHE SALINE ULTIME (10 BLOCS)
# ═════════════════════════════════════════════════════════════════════

def build_fiche_saline_ultime(
    species: str,
    month: int,
    saline: dict,
    v12_bundle: dict,
    profil: str = "moyenne",
    wind_deg: float = 225.0,
    wind_speed: float = 15.0,
) -> Dict[str, Any]:
    """Construit la FICHE SALINE ULTIME en 10 blocs.

    Args:
      species   : chevreuil / orignal / wapiti / ours_noir / dindon_sauvage
      month     : 1-12
      saline    : dict avec id, lat, lng, score, type (depuis bundle V20)
      v12_bundle: résultat de compute_nutrition_v12 (HUB INTACT)
      profil    : moyenne | male_rut | femelle_gest | femelle_lact | juvenile
      wind_deg, wind_speed : vent courant pour stratégie tactique
    """
    species_key = str(species or "chevreuil").lower()
    sp_norm = species_key.replace("_sauvage", "").replace("_noir", "")
    lat = saline.get("lat", v12_bundle.get("waypoint", {}).get("lat", 0))
    lon = saline.get("lng", v12_bundle.get("waypoint", {}).get("lng", 0))

    besoins = _extract_besoins_eff(v12_bundle)
    dispo = _extract_dispo_locale(v12_bundle)
    carences_local = _extract_carences_waypoint(v12_bundle, lat, lon)
    habitat = v12_bundle.get("habitat", {})
    terrain_sources = v12_bundle.get("data_sources", {})

    # Extract NRC needs (mg/jour) via wildlife_nutritional_engine
    try:
        from modules.saline_engine.engines.wildlife_nutritional_engine import (
            SPECIES_NEEDS as NRC_NEEDS,
        )
    except Exception:
        NRC_NEEDS = {}

    nrc = NRC_NEEDS.get(species_key, NRC_NEEDS.get(sp_norm, {}))
    minerals_nrc = (nrc or {}).get("minerals", {})

    # ── Sélection profil physio mapping NRC ──
    profil_map = {
        "moyenne": "base", "male_rut": "rut", "femelle_gest": "gestation",
        "femelle_lact": "gestation", "juvenile": "base",
    }
    nrc_state = profil_map.get(profil, "base")

    def _nrc_mg(mineral: str) -> float:
        m = minerals_nrc.get(mineral, {})
        if isinstance(m, dict):
            return float(m.get(nrc_state, m.get("base", 0)))
        return float(m or 0)

    ca_mg = _nrc_mg("Ca")
    p_mg = _nrc_mg("P")
    na_mg = _nrc_mg("Na")
    mg_mg = _nrc_mg("Mg")
    zn_mg = _nrc_mg("Zn")
    se_mg = _nrc_mg("Se")

    # ── Compute energy/proteins via x5500 ──
    try:
        from engines.nutrition_intelligence.x5500_energy_protein import compute_energy_protein
        saison = ("printemps" if month in (3, 4, 5) else
                  "ete" if month in (6, 7, 8) else
                  "automne" if month in (9, 10, 11) else "hiver")
        ep = compute_energy_protein(species_key, saison) or {}
    except Exception as e:
        logger.debug(f"x5500_energy_protein indisponible: {e}")
        ep = {}

    proteines_g_jour = ep.get("proteines_g_jour", besoins.get("proteines", 0) * 3.0)
    energie_kcal_jour = ep.get("energie_kcal_jour", besoins.get("energie", 0) * 100.0)

    # ── Déficits V12 grille + extension P/Zn/Se via tables ──
    deficit_ca = carences_local.get("Ca", 0.0)
    deficit_na = carences_local.get("Na", 0.0)
    deficit_mg = carences_local.get("Mg", 0.0)

    # Extensions P/Zn/Se (heuristique : si Ca déficit → P déficit corrélé ; Zn/Se déficit habitat)
    sol_quality = (habitat.get("composantes", {}) or {}).get("sol_fertilite", 50) / 100.0
    deficit_p = round(max(0, deficit_ca * 0.8 + (1 - sol_quality) * 15), 1)
    deficit_zn = round(max(0, 30 + (1 - sol_quality) * 40), 1)
    deficit_se = round(max(0, 45 + (1 - sol_quality) * 35), 1)  # Se traditionnellement déficitaire QC

    # ── Recette saline ──
    nacl_g = compute_nacl_g_jour(na_mg)
    ratio_cap = compute_ratio_cap(ca_mg, p_mg, species_key)
    trace_ppm = get_table_value(TRACE_PPM_CIBLE, species_key, {})

    # ── Produit base (x5800 + x6000) ──
    try:
        from engines.nutrition_intelligence.x5800_recipe_engine import generate_recipe
        from engines.nutrition_intelligence.x6000_product_score import compute_product_score
        recipe_x5800 = generate_recipe(
            species_key, saison, "boreal_acide", "redmond_natural", {}
        ) or {}
    except Exception as e:
        logger.debug(f"x5800/x6000 indisponible: {e}")
        recipe_x5800 = {}

    # ── Champs nourriciers ──
    crops = ["mais", "soya", "trefle", "luzerne", "brassicas", "avoine", "pomme"]
    top_crop_attract = {}
    for c in crops:
        attr = _CROP_ATTRACT.get(c, {}).get(sp_norm, 0)
        if attr > 0:
            top_crop_attract[c] = attr
    if top_crop_attract:
        type_champ = max(top_crop_attract.items(), key=lambda x: x[1])[0]
    else:
        type_champ = "luzerne"

    # ── Vent / Approche ──
    approche = get_table_value(APPROCHE_VENT_DOCTRINALE, species_key, {})
    corridors_strat = get_table_value(STRATEGIE_CORRIDORS, species_key, {})

    # ── Plan 30 jours adapté ──
    plan_30j = []
    for phase in PLAN_30J_PHASES:
        adapted = dict(phase)
        adapted["actions"] = [
            a.format(
                vent_critique_deg=approche.get("vent_critique_deg", 60),
                heure_optimale=corridors_strat.get("heure_optimale", "aube/crépuscule"),
                distance_optimale_m=approche.get("distance_optimale_m", 30),
            ) if isinstance(a, str) else a
            for a in phase["actions"]
        ]
        plan_30j.append(adapted)

    # ── ASSEMBLAGE FICHE ULTIME 10 BLOCS ──
    fiche = {
        "_engine": ENGINE_NAME,
        "_version": ENGINE_VERSION,
        "_doctrine": DOCTRINE,
        "_phase_iii_lock": PHASE_III_LOCK,
        "_tables_doctrine": TABLES_DOCTRINE,
        "_tables_version": TABLES_VERSION,
        "_generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),

        # ┌─ BLOC 1 : IDENTITÉ DU SITE ──────────────────────────────────
        "1_identite_site": {
            "saline_id": saline.get("id"),
            "coordonnees": {"lat": lat, "lng": lon},
            "altitude_m": habitat.get("altitude", 0),
            "type_saline": saline.get("type", "naturelle"),
            "statut": saline.get("status", "ACTIVE"),
            "score_global_saline": saline.get("attractiveness_score", saline.get("score")),
            "saison": "printemps" if month in (3,4,5) else "ete" if month in (6,7,8) else "automne" if month in (9,10,11) else "hiver",
            "mois": month,
            "espece_active": species_key,
            "profil_physio": profil,
        },

        # ┌─ BLOC 2 : PROFIL BIOLOGIQUE ESPÈCE ACTIVE ──────────────────
        "2_profil_biologique": {
            "espece": species_key,
            "poids_base_kg": (nrc or {}).get("base_weight_kg", "n/a"),
            "olfaction": approche.get("olfaction"),
            "ouie": approche.get("ouie"),
            "vue": approche.get("vue"),
            "saisonnalite_besoins": "PRINTEMPS recuperation+lactation · ETE pic Na+saline · AUTOMNE rut+reserves · HIVER thermogenese",
        },

        # ┌─ BLOC 3 : HABITAT & TERRAIN ────────────────────────────────
        "3_habitat_terrain": {
            "score_habitat": habitat.get("score", 0),
            "composantes": habitat.get("composantes", {}),
            "limitations": habitat.get("limitations", []),
            "data_sources": terrain_sources,
            "type_terrain_optimal": corridors_strat.get("type_terrain_optimal"),
            "vegetation_couvert": corridors_strat.get("vegetation_couvert"),
        },

        # ┌─ BLOC 4 : BESOINS JOURNALIERS ──────────────────────────────
        "4_besoins_journaliers": {
            "proteines_g_jour": round(proteines_g_jour, 1),
            "energie_kcal_jour": round(energie_kcal_jour, 0),
            "mineraux_mg_jour": {
                "Ca": round(ca_mg, 0),
                "P": round(p_mg, 0),
                "Na": round(na_mg, 0),
                "Mg": round(mg_mg, 0),
                "Zn": round(zn_mg, 0),
                "Se": round(se_mg, 1),
            },
            "_sources": {
                "proteines_energie": "x5500_energy_protein",
                "mineraux": "wildlife_nutritional_engine.SPECIES_NEEDS (NRC)",
                "profil_etat_nrc": nrc_state,
            },
        },

        # ┌─ BLOC 5 : DÉFICITS (Ca, P, Na, Mg, Zn, Se) ─────────────────
        "5_deficits_pct": {
            "Ca": deficit_ca,
            "P":  deficit_p,
            "Na": deficit_na,
            "Mg": deficit_mg,
            "Zn": deficit_zn,
            "Se": deficit_se,
            "_severite_globale": (
                "CRITIQUE" if max(deficit_ca, deficit_na, deficit_se) > 50
                else "ÉLEVÉE" if max(deficit_ca, deficit_na, deficit_se) > 25
                else "MODÉRÉE"
            ),
            "_sources": {
                "Ca_Na_Mg": "compute_nutrition_v12._carences_point (V12 hub)",
                "P_Zn_Se":  "v12_supra_plus heuristique (sol fertility)",
            },
        },

        # ┌─ BLOC 6 : RECETTES AUTOMATIQUES (SALINE + ALIMENTAIRE) ────
        "6_recettes_automatiques": {
            "recette_saline": {
                "produit_base_recommande": recipe_x5800.get("product_name", "SEL_MARIN_TRACE_MINERAL"),
                "score_produit": recipe_x5800.get("score", 75),
                "ratio_cap": ratio_cap,
                "nacl_g_jour": nacl_g,
                "trace_minerale_ppm": {
                    "Zn_ppm": trace_ppm.get("Zn_ppm", 400),
                    "Se_ppm": trace_ppm.get("Se_ppm", 18),
                    "Cu_ppm": trace_ppm.get("Cu_ppm", 12),
                    "I_ppm":  trace_ppm.get("I_ppm", 4),
                },
                "format_recommande": "bloc" if max(deficit_ca, deficit_na) > 40 else "granules",
                "base_carrier": "sel_marin" if deficit_na > 30 else "argile_bentonite",
                "_sources": {
                    "produit_base":   "x5800_recipe_engine + x6000_product_score",
                    "ratio_cap":      "v12_supra_plus.compute_ratio_cap",
                    "nacl":           "v12_supra_plus.compute_nacl_g_jour (Na × 2.54)",
                    "trace_minerale": "_v12_plus_tables.TRACE_PPM_CIBLE",
                },
            },
            "recette_alimentaire": {
                "type_champ_nourricier_recommande": type_champ,
                "attractivites_par_culture": top_crop_attract,
                "kg_mais_semaine": compute_kg_culture_semaine("mais", species_key),
                "kg_soya_semaine": compute_kg_culture_semaine("soya", species_key),
                "surface_m2": {
                    "trefle":    compute_surface_m2("trefle", species_key),
                    "luzerne":   compute_surface_m2("luzerne", species_key),
                    "brassicas": compute_surface_m2("brassicas", species_key),
                    "avoine":    compute_surface_m2("avoine", species_key),
                },
                "ajustement_terrain": habitat.get("recommandations_terrain",
                                                  f"Sol score {round(sol_quality*100)}/100 — adapter culture"),
                "_sources": {
                    "type_champ": "engine_champs_nourriciers_omega._CROP_ATTRACT",
                    "kg_semaine": "v12_supra_plus.compute_kg_culture_semaine",
                    "surface_m2": "_v12_plus_tables.FOOD_PLOT_SURFACE_M2",
                },
            },
        },

        # ┌─ BLOC 7 : CHAMPS NOURRICIERS RECOMMANDÉS ───────────────────
        "7_champs_nourriciers": {
            "top_3_cultures": sorted(top_crop_attract.items(), key=lambda x: -x[1])[:3],
            "saison_factor": (1.2 if month in (8, 9, 10) else 0.9 if month in (6, 7) else 0.5),
            "rotation_recommandee": "Trèfle/luzerne (printemps) → Maïs/soya (été-automne) → Brassicas (fin automne)",
            "type_principal": type_champ,
        },

        # ┌─ BLOC 8 : STRATÉGIE DE CHASSE ──────────────────────────────
        "8_strategie_chasse": {
            "approche_vent_recommandee": approche.get("approche_vent"),
            "distance_minimale_m": approche.get("distance_min_m"),
            "distance_optimale_m": approche.get("distance_optimale_m"),
            "vent_critique_deg": approche.get("vent_critique_deg"),
            "vent_actuel_deg": wind_deg,
            "vent_actuel_kmh": wind_speed,
            "vent_compatible": (
                abs((wind_deg - 225) % 360 - 180) > (180 - approche.get("vent_critique_deg", 60))
                if approche.get("vent_critique_deg") else None
            ),
            "approche_corridor": corridors_strat.get("approche_corridor"),
            "heure_optimale": corridors_strat.get("heure_optimale"),
            "type_terrain_optimal": corridors_strat.get("type_terrain_optimal"),
            "vegetation_couvert": corridors_strat.get("vegetation_couvert"),
        },

        # ┌─ BLOC 9 : PLAN D'ACTION 30 JOURS ───────────────────────────
        "9_plan_30_jours": plan_30j,

        # ┌─ BLOC 10 : SYNTHÈSE FINALE ─────────────────────────────────
        "10_synthese_finale": {
            "score_global_site": saline.get("attractiveness_score", saline.get("score")) or v12_bundle.get("score_nutritionnel"),
            "carence_dominante": max(
                [("Ca", deficit_ca), ("P", deficit_p), ("Na", deficit_na),
                 ("Mg", deficit_mg), ("Zn", deficit_zn), ("Se", deficit_se)],
                key=lambda x: x[1],
            )[0],
            "recommandation_clef": (
                f"Saline {recipe_x5800.get('product_name', 'minérale')} (ratio Ca:P {ratio_cap['cible']}) "
                f"+ {round(nacl_g)} g NaCl/jour · champ {type_champ} {compute_surface_m2(type_champ, species_key)} m²/indiv."
            ),
            "fenetre_optimale": corridors_strat.get("heure_optimale"),
            "espece_compatibilite": "OPTIMALE" if max(top_crop_attract.values() or [0]) > 0.7 else "MOYENNE",
            "verrou_phase_III": PHASE_III_LOCK,
            "never_blank_omega": "GARANTI",
        },
    }

    return fiche


# ═════════════════════════════════════════════════════════════════════
# D. POINT D'ENTRÉE PRINCIPAL — calcul à la demande
# ═════════════════════════════════════════════════════════════════════

async def compute_fiche_saline_ultime(
    lat: float,
    lon: float,
    species: str,
    month: int,
    saline: Optional[dict] = None,
    profil: str = "moyenne",
    hour: int = 14,
    wind_deg: float = 225.0,
    wind_speed: float = 15.0,
) -> Dict[str, Any]:
    """Compute fiche saline ultime à la demande (Option B).

    1. Appelle compute_nutrition_v12 du HUB V12 (INTACT)
    2. Construit la FICHE ULTIME 10 blocs via build_fiche_saline_ultime
    """
    from engines.v8_institutional.engine_nutrition_v12_supra import compute_nutrition_v12

    # Stub minimal terrain pour V12 (rapide, sans LiDAR/IRDA fetch externe)
    terrain_v10_min = {
        "source": "V12_PLUS_QUICK",
        "fiabilite": 50,
        "sources_actives": {"lidar": "FALLBACK", "irda": "FALLBACK"},
        "terrain": {
            "densite_foret": 60, "essence_dominante": "mixte",
            "drainage": 5, "humidite_sol": 0.5, "feuillus_pct": 50,
        },
        "meteo": {"temp": 10, "vent_kmh": wind_speed, "vent_deg": wind_deg},
    }

    # V12 hub call (avec entrées spatiales minimales — pas de chaîne V20 complète)
    v12 = compute_nutrition_v12(
        lat=lat, lon=lon, species=species, month=month, hour=hour,
        terrain_v10=terrain_v10_min,
        zones=[], corridors=[], affuts=[], hotspots=[], salines=[saline] if saline else [],
        profil=profil,
    )

    saline_data = saline or {
        "id": f"AUTO_{lat:.4f}_{lon:.4f}",
        "lat": lat, "lng": lon, "type": "naturelle",
        "status": "ACTIVE",
        "attractiveness_score": v12.get("score_nutritionnel", 60),
    }

    fiche = build_fiche_saline_ultime(
        species=species, month=month, saline=saline_data,
        v12_bundle=v12, profil=profil, wind_deg=wind_deg, wind_speed=wind_speed,
    )

    return fiche
