"""
ENGINE-STRESS-ANTHROPIQUE-Ω — Moteur pression humaine institutionnel
=====================================================================
Inputs: terrain_v10 (cost_surface, connectivity) + proxies humains derives
Outputs: score 0-100 (0=tres stresse, 100=tres tranquille), disturbance_level, proximity_access
"""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-STRESS-ANTHROPIQUE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(
    name=ENGINE_NAME,
    version=ENGINE_VERSION,
    description="Pression humaine / stress anthropique (accessibilite, perturbation, tranquillite)",
    pillar="COMPORTEMENT-HUMAIN",
    dependencies=["LIDAR_WCS_1M", "OPEN_METEO"],
)


def compute_stress_anthropique(terrain_v10: dict, hour: int = 7, contamination_v2: dict | None = None) -> dict:
    """Score 0-100 : 100 = territoire tranquille, 0 = fort stress anthropique.

    Proxies utilises (donnees reelles terrain_v10):
      - cost_surface: haut = difficile acces humain = tranquille
      - connectivity: bas = zone isolee = tranquille
      - canopy: haut = couvert = moins visible humain = tranquille
      - heure: peak 6-9h + 16-19h = stress piegage amateur

    Phase X-C: contamination_v2 ajoute un stress sanitaire (perturbation
    institutionnelle MFFP) pénalisant la tranquillité.
    """
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    cost = terrain.get("cost_surface", 0.4)
    connectivity = terrain.get("connectivity", 0.5)
    canopy = terrain.get("canopy", 0.5)
    pente = terrain.get("pente_deg", 10)

    # Score d'inaccessibilite humaine (plus cost = plus pente = moins access)
    s_inaccess = min(100, cost * 60 + min(1, pente / 30) * 40)

    # Isolement ecologique (connectivity inverse)
    s_isolement = (1 - connectivity) * 100

    # Protection par couvert
    s_cover = canopy * 100

    # Penalite horaire (activite humaine)
    horaire_mult = 1.0
    if 6 <= hour <= 9 or 16 <= hour <= 19:
        horaire_mult = 0.85  # peak piegeage
    elif 10 <= hour <= 15:
        horaire_mult = 0.92  # moderate
    # 20-5: nuit = tranquille max

    # Score tranquillite (haut = peu de stress anthropique)
    tranquillite = (s_inaccess * 0.40 + s_isolement * 0.30 + s_cover * 0.30) * horaire_mult
    tranquillite = round(min(100, max(0, tranquillite)), 1)

    # Phase X-C : stress sanitaire additionnel selon contamination_v2
    cwd_impact = {}
    if contamination_v2:
        risk = (contamination_v2.get("cwd_risk") or "").upper()
        dist = contamination_v2.get("distance_nearest_cwd_km")
        sanitary_malus = 0.0
        if risk == "ELEVE":
            sanitary_malus = 15.0
        elif risk == "MODERE":
            sanitary_malus = 8.0
        elif risk == "FAIBLE":
            sanitary_malus = 3.0
        if sanitary_malus > 0:
            tranquillite = round(max(0.0, tranquillite - sanitary_malus), 1)
        cwd_impact = {
            "cwd_risk": risk or None,
            "distance_km": dist,
            "sanitary_malus": sanitary_malus,
        }

    # Disturbance level inverse
    if tranquillite > 75:
        disturbance = "faible"
    elif tranquillite > 50:
        disturbance = "moderee"
    elif tranquillite > 25:
        disturbance = "forte"
    else:
        disturbance = "tres-forte"

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "score": tranquillite,
        "tranquillite_score": tranquillite,
        "disturbance_level": disturbance,
        "inaccessibility_score": round(s_inaccess, 1),
        "isolation_score": round(s_isolement, 1),
        "cover_score": round(s_cover, 1),
        "hour_modifier": horaire_mult,
        "contamination_v2_impact": cwd_impact or None,
        "data_sources": ["LIDAR_WCS_1M", "OPEN_METEO"],
        "limites": [
            "Routes/batiments reels absents (pas d'OSM integration) — proxies cost_surface + connectivity",
            "Pression chasse historique non integree",
        ],
    }
